import { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import SearchBar from './components/SearchBar'
import SpeakerFilter from './components/SpeakerFilter'
import ResultsList from './components/ResultsList'
import LoadingSkeleton from './components/LoadingSkeleton'
import EmptyState from './components/EmptyState'
import Toast from './components/Toast'
import Footer from './components/Footer'
import Privacy from './components/Privacy'
import { SearchResult, SearchResponse, SearchState } from './types'
import { searchQuotes, getStats } from './api'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'

function App() {
  const [showPrivacy, setShowPrivacy] = useState(false)
  const [searchState, setSearchState] = useState<SearchState>('idle')
  const [query, setQuery] = useState('')
  const [speakerFilter, setSpeakerFilter] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [lastResponse, setLastResponse] = useState<SearchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [clearSearchTrigger, setClearSearchTrigger] = useState(0)

  // Handle hash routing
  useEffect(() => {
    const handleHashChange = () => {
      setShowPrivacy(window.location.hash === '#privacy')
    }
    
    handleHashChange()
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  // Load stats on mount
  useEffect(() => {
    const loadStats = async () => {
      try {
        await getStats()
      } catch (err) {
        console.error('Failed to load stats:', err)
      }
    }
    loadStats()
  }, [])

  // Search function
  const handleSearch = useCallback(async (searchQuery: string, speaker?: string) => {
    if (!searchQuery.trim()) return

    setSearchState('loading')
    setError(null)
    setLastResponse(null)

    try {
      const data = await searchQuotes(searchQuery, 10, speaker)
      setLastResponse(data)
      if (data.search_type === 'fuzzy' && data.query_used && data.query_used !== searchQuery) {
        setQuery(data.query_used)
      }
      setResults(data.results)
      setSearchState(data.results.length > 0 ? 'success' : 'empty')
    } catch (err) {
      setLastResponse(null)
      setError(err instanceof Error ? err.message : 'Search failed')
      setSearchState('error')
    }
  }, [])

  // Keyboard shortcuts
  const { searchInputRef } = useKeyboardShortcuts()

  const handleSearchSubmit = (searchQuery: string) => {
    setQuery(searchQuery)
    handleSearch(searchQuery, speakerFilter)
  }

  const handleHomeClick = () => {
    setSearchState('idle')
    setQuery('')
    setSpeakerFilter('')
    setResults([])
    setError(null)
    setLastResponse(null)
    setClearSearchTrigger(prev => prev + 1)
  }

  const handleSpeakerChange = (speaker: string) => {
    setSpeakerFilter(speaker)
    if (query.trim()) {
      handleSearch(query, speaker)
    }
  }

  const handleSuggestionClick = (suggestedQuery: string) => {
    setQuery(suggestedQuery)
    handleSearch(suggestedQuery, speakerFilter)
  }

  const clearError = () => setError(null)

  if (showPrivacy) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Privacy />
        <Footer />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <Header onClick={handleHomeClick} />
        
        <div className="space-y-8">
          <div className="space-y-6">
            <SearchBar 
              ref={searchInputRef}
              onSearch={handleSearchSubmit}
              placeholder="Enter a quote to search for..."
              clearTrigger={clearSearchTrigger}
              presetQuery={query}
            />
            <SpeakerFilter 
              value={speakerFilter}
              onChange={handleSpeakerChange}
            />
          </div>



          <div aria-live="polite" aria-atomic="false">
            {searchState === 'loading' && <LoadingSkeleton />}
            {searchState === 'success' && lastResponse && (
              <div className="space-y-4">
                {lastResponse.message && (
                  <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                    <p>{lastResponse.message}</p>
                    {lastResponse.search_type === 'fuzzy' && lastResponse.query_used !== lastResponse.original_query && (
                      <p className="mt-1 text-amber-800">
                        Showing results for "<span className="font-medium">{lastResponse.query_used}</span>"
                      </p>
                    )}
                  </div>
                )}
                <ResultsList results={results} />
              </div>
            )}
            {searchState === 'empty' && (
              <EmptyState 
                query={query}
                message={lastResponse?.message}
                searchType={lastResponse?.search_type}
                suggestedQuery={lastResponse?.suggested_query}
                suggestedResults={lastResponse?.suggested_results}
                onSuggestionSelect={handleSuggestionClick}
              />
            )}
          </div>
        </div>
      </div>

      {error && (
        <Toast 
          message={error} 
          type="error" 
          onClose={clearError}
        />
      )}
      
      <Footer />
    </div>
  )
}

export default App
