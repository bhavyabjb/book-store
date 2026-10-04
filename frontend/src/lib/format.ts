export function formatPrice(amount: number): string {
  return `₹${amount % 1 === 0 ? amount.toFixed(0) : amount.toFixed(2)}`
}

export function formatDeliveryDate(isoDate: string): string {
  const date = new Date(isoDate)
  if (Number.isNaN(date.getTime())) return isoDate
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
  })
}

export function formatDateTime(isoDate: string): string {
  const date = new Date(isoDate)
  if (Number.isNaN(date.getTime())) return isoDate
  return date.toLocaleDateString('en-US', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function isCancellable(cancelBy: string, now: Date = new Date()): boolean {
  const cancelByDate = new Date(cancelBy)
  if (Number.isNaN(cancelByDate.getTime())) return false
  return now.getTime() < cancelByDate.getTime()
}
