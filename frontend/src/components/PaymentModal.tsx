import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { payForOrder } from '@/api/client'
import { formatPrice } from '@/lib/format'
import type { PaymentMethod } from '@/types'

interface PaymentModalProps {
  orderId: number
  amount: number
  onSuccess: () => void
  onClose: () => void
}

const TABS: { value: PaymentMethod; label: string }[] = [
  { value: 'CARD', label: 'Credit Card' },
  { value: 'DEBIT_CARD', label: 'Debit card' },
  { value: 'UPI', label: 'UPI' },
  { value: 'WALLET', label: 'Wallet' },
]

export function PaymentModal({ orderId, amount, onSuccess, onClose }: PaymentModalProps) {
  const [method, setMethod] = useState<PaymentMethod>('CARD')
  const [cardNumber, setCardNumber] = useState('')
  const [nameOnCard, setNameOnCard] = useState('')
  const [cvv, setCvv] = useState('')
  const [expiry, setExpiry] = useState('')
  const [upiId, setUpiId] = useState('')
  const [walletProvider, setWalletProvider] = useState('Paytm')

  const paymentMutation = useMutation({
    mutationFn: () =>
      payForOrder(orderId, {
        method,
        cardNumber: method === 'CARD' || method === 'DEBIT_CARD' ? cardNumber : undefined,
        nameOnCard: method === 'CARD' || method === 'DEBIT_CARD' ? nameOnCard : undefined,
        cvv: method === 'CARD' || method === 'DEBIT_CARD' ? cvv : undefined,
        expiry: method === 'CARD' || method === 'DEBIT_CARD' ? expiry : undefined,
        upiId: method === 'UPI' ? upiId : undefined,
        walletProvider: method === 'WALLET' ? walletProvider : undefined,
      }),
    onSuccess: (result) => {
      if (result.status === 'SUCCESS') {
        onSuccess()
      }
    },
  })

  const result = paymentMutation.data
  const declined = result?.status === 'FAILED'

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Complete Payment"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4"
    >
      <div className="w-full max-w-2xl overflow-hidden rounded-xl bg-surface shadow-2xl">
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 className="text-lg font-semibold">Complete Payment</h2>
          <p className="font-semibold">Payable Amount: {formatPrice(amount)}</p>
        </div>

        <div className="flex">
          <div className="w-40 shrink-0 border-r border-border">
            {TABS.map((tab) => (
              <button
                key={tab.value}
                type="button"
                onClick={() => setMethod(tab.value)}
                className={`block w-full border-l-2 px-4 py-4 text-left text-sm ${
                  method === tab.value
                    ? 'border-primary bg-surface-2 font-semibold text-text'
                    : 'border-transparent text-text-muted hover:text-text'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex-1 p-6">
            {(method === 'CARD' || method === 'DEBIT_CARD') && (
              <div className="grid grid-cols-2 gap-4">
                <label className="col-span-2 text-sm">
                  Card Number
                  <input
                    value={cardNumber}
                    onChange={(e) => setCardNumber(e.target.value)}
                    placeholder="XXXX-XXXX-XXXX-XXXX"
                    className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text placeholder:text-text-muted focus:border-primary focus:outline-none"
                  />
                </label>
                <label className="text-sm">
                  Name on Card
                  <input
                    value={nameOnCard}
                    onChange={(e) => setNameOnCard(e.target.value)}
                    placeholder="Name"
                    className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text placeholder:text-text-muted focus:border-primary focus:outline-none"
                  />
                </label>
                <label className="text-sm">
                  CVV
                  <input
                    value={cvv}
                    onChange={(e) => setCvv(e.target.value)}
                    placeholder="XXX"
                    className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text placeholder:text-text-muted focus:border-primary focus:outline-none"
                  />
                </label>
                <label className="col-span-2 text-sm">
                  Date of Expiry
                  <input
                    value={expiry}
                    onChange={(e) => setExpiry(e.target.value)}
                    placeholder="MM/YYYY"
                    className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text placeholder:text-text-muted focus:border-primary focus:outline-none"
                  />
                </label>
              </div>
            )}

            {method === 'UPI' && (
              <label className="block text-sm">
                UPI ID
                <input
                  value={upiId}
                  onChange={(e) => setUpiId(e.target.value)}
                  placeholder="yourname@upi"
                  className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text placeholder:text-text-muted focus:border-primary focus:outline-none"
                />
              </label>
            )}

            {method === 'WALLET' && (
              <label className="block text-sm">
                Wallet Provider
                <select
                  value={walletProvider}
                  onChange={(e) => setWalletProvider(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text focus:border-primary focus:outline-none"
                >
                  <option>Paytm</option>
                  <option>PhonePe</option>
                  <option>Amazon Pay</option>
                </select>
              </label>
            )}

            {declined && (
              <p role="alert" className="mt-4 text-sm text-accent-red">
                {result?.failureReason ?? 'Payment declined. Please try again.'}
              </p>
            )}

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg border border-border px-5 py-2.5 text-sm text-text hover:bg-surface-2"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => paymentMutation.mutate()}
                disabled={paymentMutation.isPending}
                className="rounded-lg bg-primary px-6 py-2.5 font-semibold text-white hover:bg-primary-hover disabled:opacity-60"
              >
                {paymentMutation.isPending ? 'Processing…' : 'Pay Now'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
