import type { BookSummary } from '@/types'
import { BookCard } from '@/components/BookCard'

interface BookRailProps {
  title: string
  books: BookSummary[]
  isLoading?: boolean
  isError?: boolean
  error?: unknown
}

export function BookRail({ title, books, isLoading, isError, error }: BookRailProps) {
  return (
    <section className="mb-8">
      <h2 className="mb-4 text-xl font-semibold text-text">{title}</h2>
      {isLoading ? (
        <p className="text-text-muted">Loading…</p>
      ) : isError ? (
        <p className="text-accent-red">
          Could not load books{error instanceof Error ? `: ${error.message}` : ''}. Please try again.
        </p>
      ) : books.length === 0 ? (
        <p className="text-text-muted">No books found.</p>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-2">
          {books.map((book) => (
            <div key={book.id} className="w-64 shrink-0">
              <BookCard book={book} />
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
