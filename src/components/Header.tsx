interface HeaderProps {
  onClick?: () => void
}

export default function Header({ onClick }: HeaderProps) {
  return (
    <header 
      className={`text-center py-8 ${onClick ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}`}
      onClick={onClick}
    >
      <h1 className="text-4xl font-bold text-slate-900 mb-2 flex items-center justify-center gap-3">
        <img src="/karl.png" alt="XFM Quote Finder" className="w-10 h-10" />
        XFM Quote Finder
      </h1>
      <p className="text-lg text-slate-600">
        Type a quote, get the Spotify link, no faff.
      </p>
    </header>
  )
}
