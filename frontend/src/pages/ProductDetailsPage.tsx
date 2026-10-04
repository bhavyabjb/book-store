import { useState } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { useBook, useCategories, useRelatedBooks, useReviews } from '@/hooks/useCatalog'
import { useAddCartItem } from '@/hooks/useCart'
import { useAddToWishlist } from '@/hooks/useWishlist'
import { useAuthStore } from '@/store/authStore'
import { Breadcrumb } from '@/components/Breadcrumb'
import { BookCover } from '@/components/BookCover'
import { BookCard } from '@/components/BookCard'
import { StarRating } from '@/components/StarRating'
import { CartIcon, HeartIcon } from '@/components/icons'
import { formatDeliveryDate, formatPrice } from '@/lib/format'
import { buildCategoryChain } from '@/lib/breadcrumb'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createReview } from '@/api/client'

const REVIEW_MAX_LENGTH = 100

export function ProductDetailsPage() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const token = useAuthStore((s) => s.token)
  const { data: book, isLoading, isError } = useBook(slug)
  const { data: categories } = useCategories()
  const { data: related } = useRelatedBooks(book?.id)
  const { data: reviews } = useReviews(book?.id)
  const addCartItem = useAddCartItem()
  const addToWishlist = useAddToWishlist()
  const queryClient = useQueryClient()

  const [comment, setComment] = useState('')
  const [rating, setRating] = useState(0)

  const createReviewMutation = useMutation({
    mutationFn: () => createReview(book!.id, { rating, comment }),
    onSuccess: () => {
      setComment('')
      setRating(0)
      queryClient.invalidateQueries({ queryKey: ['book', book?.id, 'reviews'] })
    },
  })

  if (isLoading) {
    return <p className="px-6 py-10 text-text-muted">Loading…</p>
  }

  if (isError || !book) {
    return <p className="px-6 py-10 text-text-muted">Book not found.</p>
  }

  const chain = buildCategoryChain(categories ?? [], book.category.id)

  function handleSubmitReview() {
    if (!token) {
      navigate('/login', { state: { from: location } })
      return
    }
    if (rating === 0) return
    createReviewMutation.mutate()
  }

  return (
    <div className="mx-auto flex max-w-[1536px] gap-10 px-6 py-6">
      <div className="min-w-0 flex-1">
        <Breadcrumb
          items={[
            { label: 'Home', to: '/' },
            ...chain.map((c) => ({ label: c.name, to: `/?category=${c.slug}` })),
          ]}
        />

        <div className="mb-8 grid grid-cols-1 gap-8 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1.2fr)]">
          <div className="aspect-[3/4]">
            <BookCover title={book.title} authorName={book.author.name} imageUrl={book.coverImageUrl} />
          </div>
          <div className="aspect-[3/4]">
            <BookCover
              title={book.description ?? book.title}
              imageUrl={book.backCoverImageUrl}
              className="text-sm font-normal normal-case"
            />
          </div>

          <div className="flex flex-col gap-3">
            <h1 className="text-2xl font-semibold">{book.title}</h1>
            <p className="text-text-muted">
              by{' '}
              <Link to={`/?author=${encodeURIComponent(book.author.name)}`} className="text-primary hover:underline">
                {book.author.name}
              </Link>
            </p>
            {book.description && <p className="text-text-muted">{book.description}</p>}
            {book.publisher && (
              <p className="text-sm text-text-muted">Published by: {book.publisher}</p>
            )}
            <p className="text-sm text-text-muted">{book.format}</p>
            <p className="text-sm">
              {book.tags.map((tag, i) => (
                <span key={tag}>
                  {i > 0 && ', '}
                  <span className="text-primary">{tag}</span>
                </span>
              ))}
            </p>

            <p className="mt-2 text-2xl font-bold">{formatPrice(book.price)}</p>
            <p className="text-sm text-text-muted">
              Delivery by <span className="font-bold text-text">{formatDeliveryDate(book.deliveryDate)}</span>
            </p>

            <div className="mt-2 flex gap-3">
              <button
                type="button"
                data-testid="add-to-cart"
                onClick={() => addCartItem.mutate({ bookId: book.id, quantity: 1 })}
                className="flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 font-semibold text-white hover:bg-primary-hover"
              >
                Add to Cart <CartIcon className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={() => {
                  if (!token) {
                    navigate('/login', { state: { from: location } })
                    return
                  }
                  addToWishlist.mutate(book.id)
                }}
                className="flex items-center gap-2 rounded-lg border border-border px-5 py-2.5 font-semibold text-text hover:bg-surface-2"
              >
                Add to Wishlist <HeartIcon className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-4 flex gap-8 border-t border-border pt-4 text-sm">
              <div>
                <p className="text-text-muted">Language</p>
                <p className="font-semibold text-primary">{book.language}</p>
              </div>
              <div>
                <p className="text-text-muted">Rating</p>
                <StarRating value={book.ratingAvg ?? 0} />
              </div>
              <div>
                <p className="text-text-muted">Sells</p>
                <p className="font-semibold">{book.unitsSold} copies sold</p>
              </div>
            </div>
          </div>
        </div>

        <section className="mb-8">
          <h2 className="mb-4 text-xl font-semibold">About the writer</h2>
          <div className="flex gap-4 rounded-xl bg-surface p-4">
            {book.author.photoUrl ? (
              <img
                src={book.author.photoUrl}
                alt={book.author.name}
                className="h-20 w-20 rounded-full object-cover"
              />
            ) : (
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-surface-2 text-xl font-semibold">
                {book.author.name.charAt(0)}
              </div>
            )}
            <div>
              <h3 className="font-semibold">{book.author.name}</h3>
              <p className="whitespace-pre-line text-sm text-text-muted">
                {book.author.bio ?? 'No biography available.'}
              </p>
            </div>
          </div>
        </section>

        <section>
          <h2 className="mb-4 text-xl font-semibold">Reviews</h2>
          <div className="mb-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <div className="mb-1 flex justify-between text-sm text-text-muted">
                <span>Leave Your Review</span>
                <span>
                  {comment.length}/{REVIEW_MAX_LENGTH}
                </span>
              </div>
              <textarea
                value={comment}
                maxLength={REVIEW_MAX_LENGTH}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Placeholder text"
                rows={5}
                className="w-full rounded-lg border border-border bg-surface-2 p-3 text-sm text-text placeholder:text-text-muted focus:border-primary focus:outline-none"
              />
              <div className="mt-3 flex items-center justify-between">
                <StarRating value={rating} onChange={setRating} />
                <button
                  type="button"
                  onClick={handleSubmitReview}
                  disabled={createReviewMutation.isPending}
                  className="rounded-lg bg-primary px-6 py-2 font-semibold text-white hover:bg-primary-hover disabled:opacity-60"
                >
                  Submit
                </button>
              </div>
              {createReviewMutation.isError && (
                <p className="mt-2 text-sm text-accent-red">Could not submit your review. Try again.</p>
              )}
            </div>
            <div className="flex flex-col gap-4">
              {(reviews ?? []).length === 0 && <p className="text-text-muted">No reviews yet.</p>}
              {(reviews ?? []).map((review) => (
                <div key={review.id}>
                  <p className="font-semibold">{review.reviewerName}</p>
                  {review.comment && <p className="text-sm text-text-muted">{review.comment}</p>}
                  <StarRating value={review.rating} size={16} />
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <aside className="w-80 shrink-0">
        <h2 className="mb-4 text-xl font-semibold">Related Reads</h2>
        <div className="flex flex-col gap-4">
          {(related ?? []).map((item) => (
            <BookCard key={item.id} book={item} />
          ))}
        </div>
      </aside>
    </div>
  )
}
