import { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import SearchBar from './components/SearchBar'
import SpeakerFilter from './components/SpeakerFilter'
import ResultsList from './components/ResultsList'
import LoadingSkeleton from './components/LoadingSkeleton'
import EmptyState from './components/EmptyState'
import Toast from './components/Toast'
import Footer from './components/Footer'
import { SearchResult, SearchState } from './types'
import { searchQuotes, getStats } from './api'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'

function App() {
  const [searchState, setSearchState] = useState<SearchState>('idle')
  const [query, setQuery] = useState('')
  const [speakerFilter, setSpeakerFilter] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [error, setError] = useState<string | null>(null)
  const [clearSearchTrigger, setClearSearchTrigger] = useState(0)

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

    try {
      const data = await searchQuotes(searchQuery, 10, speaker)
      setResults(data.results)
      setSearchState(data.results.length > 0 ? 'success' : 'empty')
    } catch (err) {
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
    setClearSearchTrigger(prev => prev + 1)
  }

  const handleSpeakerChange = (speaker: string) => {
    setSpeakerFilter(speaker)
    if (query.trim()) {
      handleSearch(query, speaker)
    }
  }

  const clearError = () => setError(null)

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
            />
            <SpeakerFilter 
              value={speakerFilter}
              onChange={handleSpeakerChange}
            />
          </div>



          <div aria-live="polite" aria-atomic="false">
            {searchState === 'loading' && <LoadingSkeleton />}
            {searchState === 'success' && (
              <ResultsList results={results} />
            )}
            {searchState === 'empty' && <EmptyState query={query} />}
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
