import { useState, forwardRef } from 'react'

interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
}

const SearchBar = forwardRef<HTMLInputElement, SearchBarProps>(
  ({ onSearch, placeholder = "Search quotes..." }, ref) => {
    const [query, setQuery] = useState('')

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault()
      if (query.trim()) {
        onSearch(query)
      }
    }

    return (
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg 
              className="h-5 w-5 text-slate-400" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" 
              />
            </svg>
          </div>
          <input
            ref={ref}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            className="block w-full pl-10 pr-3 py-3 border border-slate-300 rounded-lg leading-5 bg-white placeholder-slate-500 focus:outline-none focus:placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            aria-label="Search quotes"
          />
        </div>
        <div className="mt-2 text-sm text-slate-500">
          Press <kbd className="px-1 py-0.5 bg-slate-100 rounded text-xs">/</kbd> to focus, <kbd className="px-1 py-0.5 bg-slate-100 rounded text-xs">Enter</kbd> to search
        </div>
      </form>
    )
  }
)

SearchBar.displayName = 'SearchBar'

export default SearchBar
