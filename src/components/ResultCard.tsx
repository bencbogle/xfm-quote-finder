import { SearchResult } from '../types'
import { copySpotifyLink } from '../api'
import { useState } from 'react'

interface ResultCardProps {
  result: SearchResult
  query: string
}

export default function ResultCard({ result, query }: ResultCardProps) {



  const handleSpotifyClick = () => {
    window.open(result.spotify_url, '_blank', 'noopener,noreferrer')
  }

  const capitalizedSpeaker = result.speaker.charAt(0).toUpperCase() + result.speaker.slice(1)

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex gap-4">
        {/* Left column */}
        <div className="flex-shrink-0 w-48">
          <div className="font-semibold text-slate-900">{capitalizedSpeaker}</div>
          <div className="font-mono text-sm text-slate-600">{result.timestamp_hms}</div>
          <div className="text-sm text-slate-500 mt-1">
            {result.episode_id}
            {result.episode_name && ` — ${result.episode_name}`}
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1">
          <div className="text-slate-900 leading-relaxed mb-4">
            {result.text}
          </div>
          
          {result.spotify_url && (
            <button
              onClick={handleSpotifyClick}
              className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
              aria-label="Open Spotify link in new tab"
            >
              🎵 Listen on Spotify
            </button>
          )}
        </div>


      </div>
    </div>
  )
}
