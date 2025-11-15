export type SearchState = 'idle' | 'loading' | 'success' | 'empty' | 'error'

export interface SearchResult {
  episode_id: string
  episode_name: string
  timestamp_sec: number
  timestamp_hms: string
  speaker: string
  text: string
  spotify_url: string
  rank?: number
}

export type SearchType = 'exact' | 'fuzzy' | 'suggestion' | 'none'

export interface SearchResponse {
  query: string
  query_used: string
  original_query: string
  count: number
  results: SearchResult[]
  search_type: SearchType
  message?: string
  suggested_query?: string
  suggested_results?: SearchResult[]
  suggestion_confidence?: number
  auto_corrected?: boolean
}

export interface Stats {
  total_quotes: number
  unique_episodes: number
}

export interface StatsResponse {
  total_quotes: number
  unique_episodes: number
  episodes: string[]
}

export interface ToastProps {
  message: string
  type: 'error' | 'success'
  onClose: () => void
}
