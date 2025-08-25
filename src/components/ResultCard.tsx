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

export default function ResultCard({ result }: ResultCardProps) {
  const handleSpotifyClick = () => {
    if (result.spotify_url) {
      window.open(result.spotify_url, '_blank')
    }
  }

  const speakerImage = getSpeakerImage(result.speaker)

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-medium text-slate-900 mb-1">
            {result.episode_name || result.episode_id}
          </h3>
          <p className="text-sm text-slate-500">
            {result.timestamp_hms} • {result.speaker}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {speakerImage && (
            <img 
              src={speakerImage} 
              alt={result.speaker}
              className="w-8 h-8 rounded-full object-cover"
            />
          )}
          {result.spotify_url && (
            <button
              onClick={handleSpotifyClick}
              className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
            >
              Listen on Spotify
            </button>
          )}
        </div>
      </div>
      
      <blockquote className="text-slate-700 leading-relaxed">
        "{result.text}"
      </blockquote>
    </div>
  )
}
