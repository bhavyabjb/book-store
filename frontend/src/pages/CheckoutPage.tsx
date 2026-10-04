import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { CART_QUERY_KEY, useCart, useRemoveCartItem, useUpdateCartItem } from '@/hooks/useCart'
import { useAddresses } from '@/hooks/useAddresses'
import { useCreateOrder } from '@/hooks/useOrders'
import { useCartStore } from '@/store/cartStore'
import { Breadcrumb } from '@/components/Breadcrumb'
import { BookCover } from '@/components/BookCover'
import { QtyStepper } from '@/components/QtyStepper'
import { PaymentModal } from '@/components/PaymentModal'
import { applyCoupon, createAddress } from '@/api/client'
import { formatDeliveryDate, formatPrice } from '@/lib/format'
import type { AddressCreate, Cart } from '@/types'

const EMPTY_ADDRESS: AddressCreate = {
  firstName: '',
  lastName: '',
  line1: '',
  city: '',
  state: '',
  pin: '',
  country: 'India',
  phone: '',
  email: '',
  isDefault: false,
}

const EMPTY_CART: Cart = { items: [], subtotal: 0, tax: 0, deliveryCharge: 0, total: 0 }

export function CheckoutPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const clearCartStore = useCartStore((s) => s.clearCart)
  const { data: cart } = useCart()
  const { data: addresses } = useAddresses()
  const updateCartItem = useUpdateCartItem()
  const removeCartItem = useRemoveCartItem()
  const createOrder = useCreateOrder()

  function handlePaymentSuccess(orderId: number) {
    // The backend empties the cart once an order is placed; mirror that
    // locally so the header badge/cart page don't show stale items while
    // we navigate to the confirmation page.
    clearCartStore()
    queryClient.setQueryData(CART_QUERY_KEY, EMPTY_CART)
    navigate(`/orders/${orderId}/confirmation`)
  }

  const [useSaved, setUseSaved] = useState(false)
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null)
  const [form, setForm] = useState<AddressCreate>(EMPTY_ADDRESS)
  const [countryCode, setCountryCode] = useState('+91')
  const [couponCode, setCouponCode] = useState('')
  const [couponResult, setCouponResult] = useState<{ code: string; discount: number; newTotal: number } | null>(
    null,
  )
  const [couponError, setCouponError] = useState<string | null>(null)
  const [activeOrder, setActiveOrder] = useState<{ id: number; amount: number } | null>(null)
  const [checkoutError, setCheckoutError] = useState<string | null>(null)

  const applyCouponMutation = useMutation({
    mutationFn: () => applyCoupon({ code: couponCode }),
    onSuccess: (res) => {
      setCouponResult(res)
      setCouponError(null)
    },
    onError: () => {
      setCouponResult(null)
      setCouponError('Invalid or inactive coupon')
    },
  })

  const items = cart?.items ?? []
  const subtotal = cart?.subtotal ?? 0
  const tax = cart?.tax ?? 0
  const deliveryCharge = cart?.deliveryCharge ?? 0
  const total = couponResult?.newTotal ?? cart?.total ?? 0
  const discount = couponResult?.discount ?? 0

  const savedAddress = useMemo(
    () => addresses?.find((a) => a.id === selectedAddressId) ?? null,
    [addresses, selectedAddressId],
  )

  function updateField<K extends keyof AddressCreate>(key: K, value: AddressCreate[K]) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  async function handlePayNow() {
    setCheckoutError(null)
    let addressId = savedAddress?.id

    if (!addressId) {
      if (!form.firstName || !form.lastName || !form.line1 || !form.city || !form.pin || !form.state) {
        setCheckoutError('Please fill in all required address fields.')
        return
      }
      try {
        const created = await createAddress({ ...form, phone: `${countryCode}${form.phone}` })
        addressId = created.id
      } catch {
        setCheckoutError('Could not save address. Please try again.')
        return
      }
    }

    try {
      const order = await createOrder.mutateAsync({
        addressId,
        couponCode: couponResult?.code,
        giftPointsToRedeem: 0,
      })
      setActiveOrder({ id: order.id, amount: order.total })
    } catch {
      setCheckoutError('Could not place order. Please try again.')
    }
  }

  return (
    <div className="mx-auto max-w-[1536px] px-6 py-6">
      <Breadcrumb items={[{ label: 'Home', to: '/' }, { label: 'Checkout' }]} />
      <h1 className="mb-6 text-2xl font-semibold">Shopping Cart</h1>

      <div className="mb-8 grid grid-cols-1 gap-6 rounded-xl bg-surface p-6 sm:grid-cols-2">
        {items.length === 0 && <p className="text-text-muted">Your cart is empty.</p>}
        {items.map((item) => (
          <div key={item.book.id} className="flex gap-4">
            <div className="h-36 w-28 shrink-0">
              <BookCover
                title={item.book.title}
                authorName={item.book.author.name}
                imageUrl={item.book.coverImageUrl}
                compact
              />
            </div>
            <div className="flex flex-col gap-1">
              <p className="font-semibold">{item.book.title}</p>
              <p className="text-sm text-text-muted">by {item.book.author.name}</p>
              {item.book.description && (
                <p className="line-clamp-1 text-sm text-text-muted">{item.book.description}</p>
              )}
              <p className="text-sm text-text-muted">{item.book.format}</p>
              <p className="font-bold">{formatPrice(item.book.price)}</p>
              <p className="text-sm text-text-muted">
                Delivery by <span className="font-bold text-text">{formatDeliveryDate(item.book.deliveryDate)}</span>
              </p>
              <QtyStepper
                quantity={item.quantity}
                disabled={updateCartItem.isPending || removeCartItem.isPending}
                onIncrement={() =>
                  updateCartItem.mutate({ bookId: item.book.id, quantity: item.quantity + 1 })
                }
                onDecrement={() => {
                  if (item.quantity <= 1) {
                    removeCartItem.mutate(item.book.id)
                  } else {
                    updateCartItem.mutate({ bookId: item.book.id, quantity: item.quantity - 1 })
                  }
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
        <div className="rounded-xl bg-surface p-6">
          <h2 className="mb-4 text-xl font-semibold">Address</h2>
          <label className="mb-4 flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={useSaved}
              onChange={(e) => {
                setUseSaved(e.target.checked)
                if (e.target.checked) {
                  setSelectedAddressId(addresses?.find((a) => a.isDefault)?.id ?? addresses?.[0]?.id ?? null)
                } else {
                  setSelectedAddressId(null)
                }
              }}
            />
            Use Saved Address
          </label>

          {useSaved ? (
            <select
              aria-label="Saved address"
              value={selectedAddressId ?? ''}
              onChange={(e) => setSelectedAddressId(Number(e.target.value))}
              className="w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm text-text focus:border-primary focus:outline-none"
            >
              {(addresses ?? []).map((address) => (
                <option key={address.id} value={address.id}>
                  {address.firstName} {address.lastName}, {address.line1}, {address.city}
                </option>
              ))}
            </select>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <input
                placeholder="First Name"
                value={form.firstName}
                onChange={(e) => updateField('firstName', e.target.value)}
                className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none"
              />
              <input
                placeholder="Last Name"
                value={form.lastName}
                onChange={(e) => updateField('lastName', e.target.value)}
                className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none"
              />
              <input
                placeholder="Address Line 2"
                value={form.line1}
                onChange={(e) => updateField('line1', e.target.value)}
                className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none sm:col-span-2"
              />
              <input
                type="email"
                placeholder="e-mail"
                value={form.email ?? ''}
                onChange={(e) => updateField('email', e.target.value)}
                className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none"
              />
              <input
                placeholder="City"
                value={form.city}
                onChange={(e) => updateField('city', e.target.value)}
                className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none"
              />
              <input
                placeholder="000000"
                value={form.pin}
                onChange={(e) => updateField('pin', e.target.value)}
                className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none"
              />
              <div className="flex gap-2">
                <select
                  aria-label="Country code"
                  value={countryCode}
                  onChange={(e) => setCountryCode(e.target.value)}
                  className="rounded-lg border border-border bg-surface-2 px-2 py-2 text-sm focus:border-primary focus:outline-none"
                >
                  <option value="+91">+91</option>
                  <option value="+1">+1</option>
                  <option value="+44">+44</option>
                </select>
                <input
                  placeholder="Phone Number"
                  value={form.phone}
                  onChange={(e) => updateField('phone', e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none"
                />
              </div>
              <input
                placeholder="State"
                value={form.state}
                onChange={(e) => updateField('state', e.target.value)}
                className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none"
              />
              <input
                placeholder="Country"
                value={form.country}
                onChange={(e) => updateField('country', e.target.value)}
                className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none"
              />
            </div>
          )}
        </div>

        <div className="rounded-xl bg-surface p-6">
          <div
            aria-hidden
            className="mb-4 h-40 w-full rounded-lg"
            style={{
              background: 'linear-gradient(135deg, #1c3f73 0%, #2a5a9e 100%)',
            }}
          />
          <h2 className="mb-4 text-xl font-semibold">Grand Total</h2>
          <dl className="flex flex-col gap-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-text-muted">Price ({items.length} items)</dt>
              <dd>{formatPrice(subtotal)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-text-muted">Tax</dt>
              <dd>{formatPrice(tax)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-text-muted">Delivery Charges</dt>
              <dd>{deliveryCharge === 0 ? 'Free' : formatPrice(deliveryCharge)}</dd>
            </div>
            <div className="flex gap-2 py-2">
              <input
                placeholder="Apply Coupon"
                value={couponCode}
                onChange={(e) => setCouponCode(e.target.value)}
                className="w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm placeholder:text-text-muted focus:border-primary focus:outline-none"
              />
              <button
                type="button"
                onClick={() => applyCouponMutation.mutate()}
                disabled={!couponCode || applyCouponMutation.isPending}
                className="shrink-0 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary-hover disabled:opacity-60"
              >
                Apply
              </button>
            </div>
            {couponError && <p className="text-sm text-accent-red">{couponError}</p>}
            <div className="flex justify-between">
              <dt className="text-text-muted">Discount</dt>
              <dd>{formatPrice(discount)}</dd>
            </div>
            <div className="flex justify-between border-t border-border pt-3 text-base font-bold">
              <dt>Total Amount</dt>
              <dd>{formatPrice(total)}</dd>
            </div>
          </dl>
          {checkoutError && <p className="mt-3 text-sm text-accent-red">{checkoutError}</p>}
          <button
            type="button"
            data-testid="pay-now"
            onClick={handlePayNow}
            disabled={items.length === 0 || createOrder.isPending}
            className="mt-4 w-full rounded-lg bg-primary px-5 py-3 font-semibold text-white hover:bg-primary-hover disabled:opacity-60"
          >
            Pay Now
          </button>
        </div>
      </div>

      {activeOrder && (
        <PaymentModal
          orderId={activeOrder.id}
          amount={activeOrder.amount}
          onClose={() => setActiveOrder(null)}
          onSuccess={() => handlePaymentSuccess(activeOrder.id)}
        />
      )}
    </div>
  )
}
