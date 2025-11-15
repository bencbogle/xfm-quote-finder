import { SearchResult, SearchType } from '../types'

interface EmptyStateProps {
  query: string
  message?: string
  searchType?: SearchType
  suggestedQuery?: string
  suggestedResults?: SearchResult[]
  onSuggestionSelect?: (query: string) => void
}

export default function EmptyState({ 
  query, 
  message, 
  searchType, 
  suggestedQuery, 
  suggestedResults, 
  onSuggestionSelect 
}: EmptyStateProps) {
  const showSuggestion = searchType === 'suggestion' && suggestedQuery
  const previewResults = suggestedResults?.slice(0, 3) ?? []

  return (
    <div className="text-center py-12">
      <div className="text-6xl mb-4">🔍</div>
      <h2 className="text-xl font-semibold text-slate-900 mb-2">
        No results found for "{query}"
      </h2>
      {message && (
        <p className="text-slate-700 mb-4">{message}</p>
      )}
      {showSuggestion && (
        <div className="mb-6 space-y-3">
          <button
            type="button"
            onClick={() => suggestedQuery && onSuggestionSelect?.(suggestedQuery)}
            className="inline-flex items-center rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
          >
            Search instead for "{suggestedQuery}"
          </button>
          {previewResults.length > 0 && (
            <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-left">
              <p className="text-sm font-medium text-slate-700 mb-2">What you'd see:</p>
              <ul className="space-y-2 text-sm text-slate-600">
                {previewResults.map((result) => (
                  <li key={`${result.episode_id}-${result.timestamp_sec}`}>
                    “{result.text}” — {result.speaker} @ {result.timestamp_hms}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      <p className="text-slate-600 mb-6 max-w-md mx-auto">
        Try adjusting your search terms or check your spelling. You can also try searching for partial quotes.
      </p>
      
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 max-w-md mx-auto">
        <h3 className="font-medium text-slate-900 mb-3">Search tips:</h3>
        <ul className="text-sm text-slate-600 space-y-2 text-left">
          <li>• Try shorter, more common phrases</li>
          <li>• Use partial quotes you remember</li>
          <li>• Filter by speaker (Ricky, Steve, Karl)</li>
          <li>• Check for typos or different spellings</li>
        </ul>
      </div>
    </div>
  )
}
