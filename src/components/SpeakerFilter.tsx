interface SpeakerFilterProps {
  value: string
  onChange: (speaker: string) => void
}

import { useState, useRef, useEffect } from 'react'

export default function SpeakerFilter({ value, onChange }: SpeakerFilterProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const speakers = [
    { value: '', label: 'All speakers', icon: '👥' },
    { value: 'ricky', label: 'Ricky', icon: '🎭' },
    { value: 'steve', label: 'Steve', icon: '🎬' },
    { value: 'karl', label: 'Karl', icon: '🧠' }
  ]

  const selectedSpeaker = speakers.find(s => s.value === value) || speakers[0]

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="flex items-center gap-3">
      <label className="text-sm font-medium text-slate-700">
        Filter by speaker:
      </label>
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 hover:border-slate-300 hover:bg-slate-50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 min-w-[140px]"
          aria-label="Filter by speaker"
        >
          <span className="text-base">{selectedSpeaker.icon}</span>
          <span className="flex-1 text-left">{selectedSpeaker.label}</span>
          <svg 
            className={`h-4 w-4 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-10 overflow-hidden">
            {speakers.map((speaker) => (
              <button
                key={speaker.value}
                onClick={() => {
                  onChange(speaker.value)
                  setIsOpen(false)
                }}
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm text-left hover:bg-slate-50 transition-colors ${
                  value === speaker.value ? 'bg-emerald-50 text-emerald-700 border-r-2 border-emerald-500' : 'text-slate-700'
                }`}
              >
                <span className="text-base">{speaker.icon}</span>
                <span className="flex-1">{speaker.label}</span>
                {value === speaker.value && (
                  <svg className="h-4 w-4 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
