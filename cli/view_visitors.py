#!/usr/bin/env python3
"""
CLI tool to view unique visitor statistics.
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app.search_core import get_visitor_stats
from app.database import init_database

def main():
    """Display visitor statistics."""
    import argparse
    
    parser = argparse.ArgumentParser(description="View unique visitor statistics")
    parser.add_argument(
        "--days",
        type=int,
        help="Number of days to look back (default: all time)"
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Show daily breakdown for last 30 days"
    )
    
    args = parser.parse_args()
    
    # Initialize database connection
    try:
        init_database()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Get statistics
    try:
        stats = get_visitor_stats(days=args.days)
        
        if args.days:
            print(f"\n📊 Visitor Statistics (Last {args.days} days)")
        else:
            print("\n📊 Visitor Statistics (All Time)")
        
        print(f"{'='*50}")
        print(f"Unique Visitors: {stats['unique_visitors']:,}")
        print(f"Total Visits: {stats['total_visits']:,}")
        
        if stats['first_visit']:
            print(f"First Visit: {stats['first_visit']}")
        if stats['last_visit']:
            print(f"Last Visit: {stats['last_visit']}")
        
        if args.daily and stats['daily_breakdown']:
            print(f"\n📅 Daily Breakdown (Last 30 days)")
            print(f"{'='*50}")
            print(f"{'Date':<12} {'Unique Visitors':<18} {'Total Visits':<15}")
            print(f"{'-'*50}")
            for day in stats['daily_breakdown']:
                print(f"{day['date']:<12} {day['unique_visitors']:<18} {day['total_visits']:<15}")
        
        print()
        
    except Exception as e:
        print(f"❌ Failed to get visitor stats: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

