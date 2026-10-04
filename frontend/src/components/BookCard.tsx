import { Link } from 'react-router-dom'
import type { BookSummary } from '@/types'
import { formatDeliveryDate, formatPrice } from '@/lib/format'
import { BookCover } from '@/components/BookCover'
import { rememberBook } from '@/lib/slugCache'

interface BookCardProps {
  book: BookSummary
}

export function BookCard({ book }: BookCardProps) {
  rememberBook(book)

  return (
    <article className="flex w-full flex-col gap-3 rounded-xl bg-surface p-3" data-testid="book-card">
      <Link to={`/books/${book.slug}`} className="block aspect-[3/4] overflow-hidden rounded-lg">
        <BookCover title={book.title} authorName={book.author.name} imageUrl={book.coverImageUrl} />
      </Link>
      <div className="flex flex-1 flex-col gap-1">
        <Link to={`/books/${book.slug}`} className="font-semibold text-text hover:underline">
          {book.title}
        </Link>
        <p className="text-sm text-text-muted">
          by{' '}
          <Link to={`/books?author=${encodeURIComponent(book.author.name)}`} className="text-primary hover:underline">
            {book.author.name}
          </Link>
        </p>
        {book.description && (
          <p className="line-clamp-2 text-sm text-text-muted">{book.description}</p>
        )}
        <p className="mt-1 text-sm text-text-muted">{book.format}</p>
        <p className="text-sm">
          {book.tags.map((tag, i) => (
            <span key={tag}>
              {i > 0 && ', '}
              <span className="text-primary">{tag}</span>
            </span>
          ))}
        </p>
        <p className="mt-2 text-lg font-bold">{formatPrice(book.price)}</p>
        <p className="text-sm text-text-muted">
          Delivery by <span className="font-bold text-text">{formatDeliveryDate(book.deliveryDate)}</span>
        </p>
      </div>
    </article>
  )
}
