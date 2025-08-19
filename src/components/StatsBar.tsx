import { Stats } from '../types'

interface StatsBarProps {
  stats: Stats
}

export default function StatsBar({ stats }: StatsBarProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6">
      <div className="flex items-center justify-center text-slate-600">
        <span className="text-lg">
          📊 <strong className="text-slate-900">{stats.total_quotes.toLocaleString()}</strong> quotes from{' '}
          <strong className="text-slate-900">{stats.unique_episodes}</strong> episodes
        </span>
      </div>
    </div>
  )
}
