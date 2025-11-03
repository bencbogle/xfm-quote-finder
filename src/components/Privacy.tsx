export default function Privacy() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Privacy Policy</h1>
      
      <div className="prose prose-slate max-w-none space-y-4 text-slate-700">
        <p>
          <strong>Data Collection:</strong> When you search, we log your search query, IP address, user agent, and timestamp for analytics purposes.
        </p>
        
        <p>
          <strong>Data Storage:</strong> This data is stored in our database and used only to understand usage patterns and improve the service.
        </p>
        
        <p>
          <strong>Data Sharing:</strong> We do not sell, rent, or share your data with third parties.
        </p>
        
        <p>
          <strong>No Cookies:</strong> This site does not use cookies.
        </p>
        
        <p>
          <strong>Third-Party Services:</strong> We use Railway for hosting. Spotify links are provided for episode playback.
        </p>
        
        <p className="text-sm text-slate-500 mt-6">
          Last updated: {new Date().toLocaleDateString()}
        </p>
      </div>
      
      <div className="mt-8">
        <a 
          href="#"
          onClick={(e) => {
            e.preventDefault()
            window.location.hash = ''
          }}
          className="text-emerald-600 hover:text-emerald-700 underline"
        >
          ← Back
        </a>
      </div>
    </div>
  )
}

