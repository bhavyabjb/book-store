import { SearchIcon } from '@/components/icons'
import type { ListBooksParams } from '@/types'

export interface Filters {
  q: string
  language: string
  format: string
  priceRange: string
  deliveryBy: string
  sort: NonNullable<ListBooksParams['sort']>
}

export const PRICE_RANGES: Record<string, { minPrice?: number; maxPrice?: number }> = {
  All: {},
  'Under ₹200': { maxPrice: 200 },
  '₹200 - ₹400': { minPrice: 200, maxPrice: 400 },
  '₹400 - ₹600': { minPrice: 400, maxPrice: 600 },
  'Above ₹600': { minPrice: 600 },
}

// Days-from-today for each "Delivery by" option; resolved to an actual date
// at filter time (not module load) so a long-lived tab doesn't go stale.
const DELIVERY_OPTIONS: Record<string, number | undefined> = {
  'Any time': undefined,
  Tomorrow: 1,
  'Within 3 days': 3,
  'Within 5 days': 5,
  'Within a week': 7,
}

export function resolveDeliveryBy(option: string): { maxDeliveryDate?: string } {
  const days = DELIVERY_OPTIONS[option]
  if (days === undefined) return {}
  const date = new Date()
  date.setDate(date.getDate() + days)
  return { maxDeliveryDate: date.toISOString().slice(0, 10) }
}

const LANGUAGES = ['All', 'English', 'Hindi', 'Spanish', 'French']
const FORMATS = ['All', 'Paperback', 'Hardcover', 'eBook']
const SORTS: { value: NonNullable<ListBooksParams['sort']>; label: string }[] = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
  { value: 'rating', label: 'Rating' },
  { value: 'newest', label: 'Newest' },
]

interface FiltersBarProps {
  filters: Filters
  onChange: (filters: Filters) => void
}

export function FiltersBar({ filters, onChange }: FiltersBarProps) {
  return (
    <div className="mb-8 flex flex-wrap gap-3">
      <div className="relative min-w-[220px] flex-1">
        <input
          type="search"
          placeholder="Search you want to read here"
          aria-label="Search"
          value={filters.q}
          onChange={(e) => onChange({ ...filters, q: e.target.value })}
          className="w-full rounded-lg border border-border bg-surface px-4 py-2.5 pr-10 text-sm text-text placeholder:text-text-muted focus:border-primary focus:outline-none"
        />
        <SearchIcon className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
      </div>

      <select
        aria-label="Language"
        value={filters.language}
        onChange={(e) => onChange({ ...filters, language: e.target.value })}
        className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text focus:border-primary focus:outline-none"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang} value={lang}>
            {lang === 'All' ? 'Language: All' : lang}
          </option>
        ))}
      </select>

      <select
        aria-label="Format"
        value={filters.format}
        onChange={(e) => onChange({ ...filters, format: e.target.value })}
        className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text focus:border-primary focus:outline-none"
      >
        {FORMATS.map((format) => (
          <option key={format} value={format}>
            {format === 'All' ? 'Format: All' : format}
          </option>
        ))}
      </select>

      <select
        aria-label="Price Range"
        value={filters.priceRange}
        onChange={(e) => onChange({ ...filters, priceRange: e.target.value })}
        className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text focus:border-primary focus:outline-none"
      >
        {Object.keys(PRICE_RANGES).map((range) => (
          <option key={range} value={range}>
            {range === 'All' ? 'Price Range: All' : range}
          </option>
        ))}
      </select>

      <select
        aria-label="Delivery by"
        value={filters.deliveryBy}
        onChange={(e) => onChange({ ...filters, deliveryBy: e.target.value })}
        className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text focus:border-primary focus:outline-none"
      >
        {Object.keys(DELIVERY_OPTIONS).map((option) => (
          <option key={option} value={option}>
            {option === 'Any time' ? 'Delivery: Any time' : `Delivery by: ${option}`}
          </option>
        ))}
      </select>

      <select
        aria-label="Sort by"
        value={filters.sort}
        onChange={(e) => onChange({ ...filters, sort: e.target.value as Filters['sort'] })}
        className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text focus:border-primary focus:outline-none"
      >
        {SORTS.map((s) => (
          <option key={s.value} value={s.value}>
            {s.label}
          </option>
        ))}
      </select>
    </div>
  )
}
