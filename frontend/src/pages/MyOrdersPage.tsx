import { useState } from 'react'
import { useCancelOrder, useOrders } from '@/hooks/useOrders'
import { useAddCartItem } from '@/hooks/useCart'
import { formatDateTime, formatPrice, isCancellable } from '@/lib/format'
import { ApiError } from '@/api/client'
import type { OrderSummary } from '@/types'

function OrderCard({ order }: { order: OrderSummary }) {
  const cancelOrder = useCancelOrder()
  const addCartItem = useAddCartItem()
  const [cancelError, setCancelError] = useState<string | null>(null)
  const cancellable =
    order.status !== 'CANCELLED' && order.status !== 'DELIVERED' && isCancellable(order.cancelBy)

  async function handleCancel() {
    setCancelError(null)
    try {
      await cancelOrder.mutateAsync(order.id)
    } catch (err) {
      if (err instanceof ApiError && err.status === 422) {
        setCancelError('The cancellation window has closed for this order.')
      } else {
        setCancelError('Could not cancel this order. Please try again.')
      }
    }
  }

  async function handleBuyAgain() {
    for (const item of order.items) {
      await addCartItem.mutateAsync({ bookId: item.book.id, quantity: item.quantity })
    }
  }

  return (
    <div className="rounded-xl bg-surface p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="font-semibold">Order #{order.id}</p>
          <p className="text-sm text-text-muted">Placed on {formatDateTime(order.placedAt)}</p>
        </div>
        <span className="rounded-full bg-surface-2 px-3 py-1 text-xs font-semibold uppercase tracking-wide">
          {order.status}
        </span>
      </div>

      <div className="flex flex-col gap-2">
        {order.items.map((item) => (
          <div key={item.book.id} className="flex justify-between text-sm">
            <span>
              {item.book.title} &times; {item.quantity}
            </span>
            <span>{formatPrice(item.unitPrice * item.quantity)}</span>
          </div>
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
        <p className="font-bold">Total: {formatPrice(order.total)}</p>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleBuyAgain}
            disabled={addCartItem.isPending}
            className="rounded-lg border border-border px-4 py-2 text-sm font-semibold hover:bg-surface-2 disabled:opacity-60"
          >
            Buy It Again
          </button>
          {cancellable && (
            <button
              type="button"
              onClick={handleCancel}
              disabled={cancelOrder.isPending}
              className="rounded-lg border border-accent-red px-4 py-2 text-sm font-semibold text-accent-red hover:bg-accent-red/10 disabled:opacity-60"
            >
              Cancel Order
            </button>
          )}
        </div>
      </div>
      {cancelError && <p className="mt-2 text-sm text-accent-red">{cancelError}</p>}
    </div>
  )
}

export function MyOrdersPage() {
  const { data: orders, isLoading } = useOrders()

  return (
    <div className="mx-auto max-w-4xl px-6 py-6">
      <h1 className="mb-6 text-2xl font-semibold">My Orders</h1>
      {isLoading && <p className="text-text-muted">Loading…</p>}
      {!isLoading && (orders ?? []).length === 0 && <p className="text-text-muted">No orders yet.</p>}
      <div className="flex flex-col gap-4">
        {(orders ?? []).map((order) => (
          <OrderCard key={order.id} order={order} />
        ))}
      </div>
    </div>
  )
}
