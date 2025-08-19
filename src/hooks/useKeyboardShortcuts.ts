import { useEffect, useRef } from 'react'

interface KeyboardShortcutsProps {
  onSearch: () => void
}

export function useKeyboardShortcuts({ onSearch }: KeyboardShortcutsProps) {
  const searchInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Focus search on '/' key (but not when already in an input)
      if (event.key === '/' && !event.target?.matches('input, textarea')) {
        event.preventDefault()
        searchInputRef.current?.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return { searchInputRef }
}
