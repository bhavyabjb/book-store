import { Link, useParams } from 'react-router-dom'
import { useOrder } from '@/hooks/useOrders'
import { BookCover } from '@/components/BookCover'
import { CheckCircleIcon, LogoIcon } from '@/components/icons'
import { formatDeliveryDate, formatPrice } from '@/lib/format'

export function OrderSuccessPage() {
  const { orderId } = useParams<{ orderId: string }>()
  const { data: order, isLoading } = useOrder(orderId)

  if (isLoading) {
    return <p className="px-6 py-10 text-center text-text-muted">Loading…</p>
  }

  if (!order) {
    return <p className="px-6 py-10 text-center text-text-muted">Order not found.</p>
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center gap-6 rounded-xl bg-surface px-8 py-10 text-center">
      <CheckCircleIcon className="h-16 w-16 text-green-500" />
      <p className="text-lg">Your purchase of the following reads is successful</p>

      <div className="flex w-full flex-col gap-4 text-left">
        {order.items.map((item) => (
          <div key={item.book.id} className="flex gap-4 rounded-lg bg-surface-2 p-4">
            <div className="h-28 w-20 shrink-0">
              <BookCover
                title={item.book.title}
                authorName={item.book.author.name}
                imageUrl={item.book.coverImageUrl}
                compact
              />
            </div>
            <div>
              <p className="font-semibold">{item.book.title}</p>
              <p className="text-sm text-text-muted">by {item.book.author.name}</p>
              {item.book.description && (
                <p className="line-clamp-1 text-sm text-text-muted">{item.book.description}</p>
              )}
              <p className="text-sm text-text-muted">{item.book.format}</p>
              <p className="font-bold">{formatPrice(item.unitPrice)}</p>
              <p className="text-sm text-text-muted">
                Delivery by <span className="font-bold text-text">{formatDeliveryDate(item.book.deliveryDate)}</span>
              </p>
            </div>
          </div>
        ))}
      </div>

      <Link
        to="/"
        className="flex items-center gap-2 rounded-lg bg-primary px-6 py-3 font-semibold text-white hover:bg-primary-hover"
      >
        Continue your Shopping <LogoIcon className="h-4 w-4" />
      </Link>
    </div>
  )
}
