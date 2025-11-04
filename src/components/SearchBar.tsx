import { useState, forwardRef, useEffect } from 'react'

interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  clearTrigger?: number
}

const SearchBar = forwardRef<HTMLInputElement, SearchBarProps>(
  ({ onSearch, placeholder = "Search quotes...", clearTrigger }, ref) => {
    const [query, setQuery] = useState('')

    // Clear the search bar when clearTrigger changes
    useEffect(() => {
      if (clearTrigger !== undefined) {
        setQuery('')
      }
    }, [clearTrigger])

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault()
      if (query.trim()) {
        onSearch(query)
      }
    }

    const isInputEmpty = !query.trim()

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
            className="block w-full pl-10 pr-12 py-3 border border-slate-300 rounded-lg leading-5 bg-white placeholder-slate-500 focus:outline-none focus:placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-base"
            aria-label="Search quotes"
          />
          <button
            type="submit"
            disabled={isInputEmpty}
            className="absolute inset-y-0 right-0 pr-3 flex items-center transition-colors duration-200 disabled:pointer-events-none"
            aria-label="Search"
          >
            <div className="p-2 -mr-2">
              <svg 
                className={`h-5 w-5 transition-colors duration-200 ${isInputEmpty ? 'text-slate-300' : 'text-slate-400 hover:text-emerald-600'}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M13 7l5 5m0 0l-5 5m5-5H6" 
                />
              </svg>
            </div>
          </button>
        </div>
        <div className="mt-2 text-sm text-slate-500 hidden sm:block">
          Press <kbd className="px-1 py-0.5 bg-slate-100 rounded text-xs">/</kbd> to focus, <kbd className="px-1 py-0.5 bg-slate-100 rounded text-xs">Enter</kbd> to search
        </div>
      </form>
    )
  }
)

SearchBar.displayName = 'SearchBar'

export default SearchBar
