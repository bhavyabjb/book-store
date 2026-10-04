import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { CategorySidebar } from '@/components/CategorySidebar'
import { FiltersBar, PRICE_RANGES, type Filters } from '@/components/FiltersBar'
import { BookRail } from '@/components/BookRail'
import { useBooks, useCategories } from '@/hooks/useCatalog'
import type { ListBooksParams } from '@/types'

const DEFAULT_FILTERS: Filters = {
  q: '',
  language: 'All',
  format: 'All',
  priceRange: 'All',
  sort: 'relevance',
}

export function HomePage() {
  const [searchParams] = useSearchParams()
  const [category, setCategory] = useState<string | null>(null)
  const [filters, setFilters] = useState<Filters>({
    ...DEFAULT_FILTERS,
    q: searchParams.get('author') ?? '',
  })

  const { data: categories } = useCategories()

  const isFiltering =
    filters.q !== '' ||
    filters.language !== 'All' ||
    filters.format !== 'All' ||
    filters.priceRange !== 'All' ||
    filters.sort !== 'relevance'

  const baseParams: ListBooksParams = useMemo(() => {
    const range = PRICE_RANGES[filters.priceRange] ?? {}
    return {
      category: category ?? undefined,
      q: filters.q || undefined,
      language: filters.language !== 'All' ? filters.language : undefined,
      format: filters.format !== 'All' ? (filters.format as ListBooksParams['format']) : undefined,
      minPrice: range.minPrice,
      maxPrice: range.maxPrice,
      sort: filters.sort,
      pageSize: 12,
    }
  }, [category, filters])

  const searchResults = useBooks({ ...baseParams, section: undefined }, { enabled: isFiltering })
  const recommended = useBooks({ ...baseParams, section: 'recommended' }, { enabled: !isFiltering })
  const bestsellers = useBooks({ ...baseParams, section: 'bestsellers' }, { enabled: !isFiltering })
  const newLaunches = useBooks({ ...baseParams, section: 'new_launches' }, { enabled: !isFiltering })

  return (
    <div className="mx-auto flex max-w-[1536px] gap-8 px-6 py-6">
      <CategorySidebar
        categories={categories ?? []}
        selected={category}
        onSelect={setCategory}
      />
      <div className="min-w-0 flex-1">
        <FiltersBar filters={filters} onChange={setFilters} />

        {isFiltering ? (
          <BookRail
            title="Search Results"
            books={searchResults.data?.items ?? []}
            isLoading={searchResults.isLoading}
          />
        ) : (
          <>
            <BookRail
              title="Recommended for You"
              books={recommended.data?.items ?? []}
              isLoading={recommended.isLoading}
            />
            <BookRail
              title="Bestsellers this Month"
              books={bestsellers.data?.items ?? []}
              isLoading={bestsellers.isLoading}
            />
            <BookRail
              title="New Launches"
              books={newLaunches.data?.items ?? []}
              isLoading={newLaunches.isLoading}
            />
          </>
        )}
      </div>
    </div>
  )
}
