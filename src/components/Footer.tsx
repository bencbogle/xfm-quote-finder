export default function Footer() {
  return (
    <footer className="mt-16 pt-8 border-t border-slate-200">
      <div className="text-center text-sm text-slate-600">
        <p>
          Transcripts from{' '}
          <a 
            href="https://scrimpton.com/search" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-emerald-600 hover:text-emerald-700 underline"
          >
            scrimpton.com
          </a>
          {' • '}
          Spotify uploads by{' '}
          <a 
            href="https://open.spotify.com/show/34mXWuUCEa2UzTft5vxxLp?si=9caac35d12284346" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-emerald-600 hover:text-emerald-700 underline"
          >
            RSK XFM Pilky01
          </a>
          {' • '}
          Thanks to{' '}
          <a 
            href="https://www.reddit.com/user/Rhondson/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-emerald-600 hover:text-emerald-700 underline"
          >
            Rhondson
          </a>
          {' '}for remastering the episodes.
        </p>
        <p className="mt-2">
          <a 
            href="#privacy"
            className="text-slate-500 hover:text-slate-700 underline"
          >
            Privacy Policy
          </a>
          {' • '}
          <a 
            href="https://github.com/bencbogle/xfm-quote-finder/issues" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-slate-500 hover:text-slate-700 underline"
          >
            Feedback & Suggestions
          </a>
          {' • '}
          <a 
            href="https://github.com/bencbogle/xfm-quote-finder" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-slate-500 hover:text-slate-700 underline"
          >
            View on GitHub
          </a>
        </p>
      </div>
    </footer>
  )
}
