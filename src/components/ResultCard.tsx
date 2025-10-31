import { useState } from 'react'
import { SearchResult } from '../types'

interface ResultCardProps {
  result: SearchResult
}

const getSpeakerImage = (speaker: string) => {
  switch (speaker.toLowerCase()) {
    case 'ricky':
      return '/ricky.png'
    case 'steve':
      return '/steve.png'
    case 'karl':
      return '/karl2.png'
    default:
      return null
  }
}

const formatEpisodeDisplay = (episodeId: string, episodeName: string): string => {
  // Parse episode_id format: xfm-s2e32, podcast-s1e1, guide-s1e1
  const match = episodeId.match(/^(\w+)-s(\d+)e(\d+)$/)
  
  if (!match) {
    // Fallback for unexpected format
    return episodeName || episodeId
  }
  
  const [, publication, series, episode] = match
  
  // Determine display name based on publication type
  let displayPrefix: string
  switch (publication) {
    case 'xfm':
      displayPrefix = 'XFM'
      break
    case 'podcast':
      displayPrefix = 'Podcast'
      break
    case 'guide':
      displayPrefix = 'Podcast'
      break
    default:
      displayPrefix = publication.charAt(0).toUpperCase() + publication.slice(1)
  }
  
  // Format series and episode
  const seriesDisplay = `Series ${series} Episode ${episode}`
  
  // For guide episodes, just show the episode name without series/episode numbers
  if (publication === 'guide' && episodeName && episodeName.trim() !== '') {
    // Shorten "The Ricky Gervais Guide to:" to just "Guide to:"
    const shortenedName = episodeName.replace(/^The Ricky Gervais /, '')
    return `${displayPrefix} | ${shortenedName}`
  }
  
  // For podcast episodes with episode names starting with "The Ricky Gervais Guide to:"
  if (publication === 'podcast' && episodeName && episodeName.trim() !== '' && 
      episodeName.startsWith('The Ricky Gervais Guide to:')) {
    // Shorten "The Ricky Gervais Guide to:" to just "Guide to:"
    const shortenedName = episodeName.replace(/^The Ricky Gervais /, '')
    return `${displayPrefix} | ${shortenedName}`
  }
  
  // For XFM episodes, always show just series/episode (no episode name)
  if (publication === 'xfm') {
    return `${displayPrefix} | ${seriesDisplay}`
  }
  
  // For other cases (podcast), just show series/episode without episode name
  return `${displayPrefix} | ${seriesDisplay}`
}

// SVG Icons
const LinkIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
  </svg>
)

const CheckIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
)

const SpotifyIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z" />
  </svg>
)

export default function ResultCard({ result }: ResultCardProps) {
  const [copied, setCopied] = useState(false)

  const handleSpotifyClick = () => {
    if (result.spotify_url) {
      window.open(result.spotify_url, '_blank')
    }
  }

  const handleCopyUrl = async () => {
    if (result.spotify_url) {
      try {
        await navigator.clipboard.writeText(result.spotify_url)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Failed to copy URL:', err)
      }
    }
  }

  const speakerImage = getSpeakerImage(result.speaker)

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 md:p-6 hover:shadow-md transition-shadow">
      <div className="flex flex-col md:flex-row md:justify-between md:items-start mb-4 gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-slate-900 mb-1 truncate">
            {formatEpisodeDisplay(result.episode_id, result.episode_name)}
          </h3>
          <p className="text-sm text-slate-500">
            {result.timestamp_hms} • {result.speaker.charAt(0).toUpperCase() + result.speaker.slice(1).toLowerCase()}
          </p>
        </div>
        <div className="flex items-center gap-2 md:gap-3 flex-shrink-0">
          {speakerImage && (
            <img 
              src={speakerImage} 
              alt={result.speaker}
              className="w-8 h-8 rounded-full object-cover"
            />
          )}
          {result.spotify_url && (
            <>
              <button
                onClick={handleSpotifyClick}
                className="bg-green-600 text-white px-3 py-1.5 rounded text-sm hover:bg-green-700 transition-colors flex-1 md:flex-none whitespace-nowrap flex items-center justify-center gap-1.5 font-medium"
              >
                <SpotifyIcon />
                <span className="hidden sm:inline">Listen on Spotify</span>
                <span className="sm:hidden">Spotify</span>
              </button>
              <button
                onClick={handleCopyUrl}
                className={`px-3 py-1.5 rounded text-sm transition-colors flex-1 md:flex-none whitespace-nowrap flex items-center justify-center gap-1.5 font-medium ${
                  copied
                    ? 'bg-green-100 text-green-700 border border-green-300'
                    : 'border border-green-600 text-green-600 hover:bg-green-50'
                }`}
              >
                {copied ? (
                  <>
                    <CheckIcon />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <LinkIcon />
                    <span>Copy Link</span>
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>
      
      <blockquote className="text-slate-700 leading-relaxed">
        "{result.text}"
      </blockquote>
    </div>
  )
}
