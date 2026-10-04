import { Link } from 'react-router-dom'
import { useRemoveFromWishlist, useWishlist } from '@/hooks/useWishlist'
import { BookCover } from '@/components/BookCover'
import { HeartIcon } from '@/components/icons'
import { formatDeliveryDate, formatPrice } from '@/lib/format'

export function WishlistPage() {
  const { data: books, isLoading } = useWishlist()
  const removeFromWishlist = useRemoveFromWishlist()

  return (
    <div className="mx-auto max-w-[1536px] px-6 py-6">
      <h1 className="mb-6 text-2xl font-semibold">My Wishlist</h1>
      {isLoading && <p className="text-text-muted">Loading…</p>}
      {!isLoading && (books ?? []).length === 0 && <p className="text-text-muted">Your wishlist is empty.</p>}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {(books ?? []).map((book) => (
          <div key={book.id} className="relative flex flex-col gap-2 rounded-xl bg-surface p-3">
            <button
              type="button"
              aria-label={`Remove ${book.title} from wishlist`}
              onClick={() => removeFromWishlist.mutate(book.id)}
              className="absolute right-4 top-4 z-10 rounded-full bg-surface-2 p-1.5 text-accent-red hover:bg-surface"
            >
              <HeartIcon className="h-4 w-4 fill-current" />
            </button>
            <Link to={`/books/${book.slug}`} className="block aspect-[3/4] overflow-hidden rounded-lg">
              <BookCover title={book.title} authorName={book.author.name} imageUrl={book.coverImageUrl} />
            </Link>
            <Link to={`/books/${book.slug}`} className="font-semibold hover:underline">
              {book.title}
            </Link>
            <p className="text-sm text-text-muted">by {book.author.name}</p>
            <p className="font-bold">{formatPrice(book.price)}</p>
            <p className="text-sm text-text-muted">
              Delivery by <span className="font-bold text-text">{formatDeliveryDate(book.deliveryDate)}</span>
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
