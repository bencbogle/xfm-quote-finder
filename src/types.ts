export type SearchState = 'idle' | 'loading' | 'success' | 'empty' | 'error'

export interface SearchResult {
  episode_id: string
  episode_name: string
  timestamp_sec: number
  timestamp_hms: string
  speaker: string
  text: string
  spotify_url: string
}

export interface SearchResponse {
  query: string
  count: number
  results: SearchResult[]
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
