import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-16 text-center">
      <h1 className="mb-3 text-2xl font-semibold">Page not found</h1>
      <p className="mb-6 text-text-muted">The page you're looking for doesn't exist.</p>
      <Link to="/" className="text-primary hover:underline">
        Back to Home
      </Link>
    </div>
  )
}
