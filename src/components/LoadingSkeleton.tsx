export default function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-4 bg-slate-200 rounded w-32 animate-pulse"></div>
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white border border-slate-200 rounded-lg p-6">
            <div className="flex gap-4">
              {/* Left column skeleton */}
              <div className="flex-shrink-0 w-48 space-y-2">
                <div className="h-4 bg-slate-200 rounded w-16 animate-pulse"></div>
                <div className="h-3 bg-slate-200 rounded w-20 animate-pulse"></div>
                <div className="h-3 bg-slate-200 rounded w-32 animate-pulse"></div>
              </div>

              {/* Main content skeleton */}
              <div className="flex-1 space-y-3">
                <div className="space-y-2">
                  <div className="h-4 bg-slate-200 rounded w-full animate-pulse"></div>
                  <div className="h-4 bg-slate-200 rounded w-3/4 animate-pulse"></div>
                </div>
                <div className="h-8 bg-slate-200 rounded w-32 animate-pulse"></div>
              </div>

              {/* Right column skeleton */}
              <div className="flex-shrink-0">
                <div className="h-6 bg-slate-200 rounded w-8 animate-pulse"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
