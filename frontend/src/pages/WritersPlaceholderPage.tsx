// "My Writers" is a header nav link shown in the wireframes, but no page or
// API endpoint for it is defined in the capstone's API contract or page
// spec. We render a minimal placeholder so the nav link doesn't 404.
export function WritersPlaceholderPage() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-16 text-center">
      <h1 className="mb-3 text-2xl font-semibold">My Writers</h1>
      <p className="text-text-muted">Coming soon.</p>
    </div>
  )
}
