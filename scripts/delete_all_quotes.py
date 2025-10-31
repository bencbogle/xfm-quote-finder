#!/usr/bin/env python3
"""
Delete all quotes from the database and verify deletion.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def delete_all_quotes():
    """Delete all quotes and verify."""
    print("Delete All Quotes from Database")
    print("="*70)
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    try:
        from app.database import get_connection
    except Exception as e:
        print(f"❌ Error importing database module: {e}")
        sys.exit(1)
    
    # Get current count
    print("\nChecking current state...")
    try:
        with get_connection() as conn:
            from sqlalchemy import text
            
            result = conn.execute(text("SELECT COUNT(*) FROM quotes"))
            current_count = result.fetchone()[0]
            print(f"Current quotes in database: {current_count:,}")
            
            if current_count == 0:
                print("\n✅ Database is already empty. Nothing to delete.")
                return True
    except Exception as e:
        print(f"❌ Error checking current state: {e}")
        sys.exit(1)
    
    # Confirm deletion (skip if --yes flag provided)
    if "--yes" not in sys.argv:
        print(f"\n⚠️  WARNING: About to delete {current_count:,} quotes from the database")
        print("This action cannot be undone!")
        
        try:
            response = input("\nType 'DELETE' to confirm: ")
            if response != "DELETE":
                print("❌ Deletion cancelled")
                return False
        except EOFError:
            print("\n❌ Interactive input not available. Use --yes flag to skip confirmation.")
            print("   Example: uv run python3 scripts/delete_all_quotes.py --yes")
            return False
    else:
        print(f"\n⚠️  Deleting {current_count:,} quotes from the database (--yes flag provided)")
    
    # Delete all quotes
    print("\n🗑️  Deleting all quotes...")
    try:
        with get_connection() as conn:
            from sqlalchemy import text
            
            result = conn.execute(text("DELETE FROM quotes"))
            conn.commit()
            deleted_count = result.rowcount
            print(f"   Deleted {deleted_count:,} quotes")
    except Exception as e:
        print(f"❌ Error deleting quotes: {e}")
        sys.exit(1)
    
    # Verify deletion
    print("\nVerifying deletion...")
    try:
        with get_connection() as conn:
            from sqlalchemy import text
            
            result = conn.execute(text("SELECT COUNT(*) FROM quotes"))
            remaining_count = result.fetchone()[0]
            
            if remaining_count == 0:
                print(f"✅ Confirmed: Database is now empty ({remaining_count} quotes)")
                
                # Also check for any other data
                result = conn.execute(text("""
                    SELECT COUNT(DISTINCT episode_id) FROM quotes
                """))
                episode_count = result.fetchone()[0]
                print(f"   Unique episodes: {episode_count}")
                
                return True
            else:
                print(f"❌ ERROR: Expected 0 quotes, but found {remaining_count:,}")
                print("   Some quotes were not deleted!")
                return False
    except Exception as e:
        print(f"❌ Error verifying deletion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    success = delete_all_quotes()
    sys.exit(0 if success else 1)

