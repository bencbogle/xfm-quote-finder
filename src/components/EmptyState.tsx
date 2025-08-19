interface EmptyStateProps {
  query: string
}

export default function EmptyState({ query }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <div className="text-6xl mb-4">🔍</div>
      <h2 className="text-xl font-semibold text-slate-900 mb-2">
        No results found for "{query}"
      </h2>
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
