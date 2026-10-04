import type { BookSummary } from '@/types'

// The OpenAPI contract only exposes GET /books/{bookId} with an integer id,
// but the wireframes use pretty `/books/:slug` URLs. We keep a small
// slug -> id map (seeded whenever a BookSummary is rendered anywhere in the
// app, and persisted to sessionStorage for hard refreshes/direct links)
// so the product page can resolve a slug to the numeric id the API needs.
const STORAGE_KEY = 'bookworm-slug-map'

function loadMap(): Record<string, number> {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as Record<string, number>) : {}
  } catch {
    return {}
  }
}

function saveMap(map: Record<string, number>) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(map))
  } catch {
    // ignore storage errors (e.g. private browsing)
  }
}

export function rememberBook(book: Pick<BookSummary, 'id' | 'slug'>) {
  const map = loadMap()
  if (map[book.slug] !== book.id) {
    map[book.slug] = book.id
    saveMap(map)
  }
}

export function rememberBooks(books: Pick<BookSummary, 'id' | 'slug'>[]) {
  books.forEach(rememberBook)
}

export function getCachedId(slug: string): number | undefined {
  return loadMap()[slug]
}
