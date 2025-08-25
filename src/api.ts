import { SearchResponse, StatsResponse } from './types'

// In development, use the proxy to localhost:8000
// In production, use relative paths
const API_BASE = (import.meta as any).env?.PROD ? '' : '/api';

export async function searchQuotes(query: string, limit: number = 10, speaker?: string): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    top_k: limit.toString(),
  });
  
  if (speaker) {
    params.append('speaker', speaker);
  }

  const response = await fetch(`${API_BASE}/search?${params}`);
  
  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE}/stats`);
  
  if (!response.ok) {
    throw new Error(`Failed to get stats: ${response.statusText}`);
  }
  
  return response.json();
}

export function copySpotifyLink(url: string): Promise<void> {
  return navigator.clipboard.writeText(url)
}
