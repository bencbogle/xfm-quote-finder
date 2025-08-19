import { SearchResult } from '../types'
import ResultCard from './ResultCard'

interface ResultsListProps {
  results: SearchResult[]
  query: string
}

export default function ResultsList({ results, query }: ResultsListProps) {
  return (
    <div className="space-y-4">
      <div className="text-sm text-slate-600">
        Found {results.length} result{results.length !== 1 ? 's' : ''}
      </div>
      <div className="space-y-4">
        {results.map((result, index) => (
          <ResultCard 
            key={`${result.episode_id}-${result.timestamp_sec}-${index}`}
            result={result} 
            query={query}
          />
        ))}
      </div>
    </div>
  )
}
