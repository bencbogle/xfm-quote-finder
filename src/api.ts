import { SearchResponse } from './types'

export async function searchQuotes(
  query: string, 
  speaker?: string, 
  baseUrl: string = 'http://localhost:8000'
): Promise<SearchResponse> {
  const url = new URL('/search', baseUrl)
  url.searchParams.set('q', query)
  
  if (speaker) {
    url.searchParams.set('speaker', speaker)
  }

  const response = await fetch(url.toString())
  
  if (!response.ok) {
    throw new Error(`Search failed: ${response.status}`)
  }

  return response.json()
}

export function copySpotifyLink(url: string): Promise<void> {
  return navigator.clipboard.writeText(url)
}
