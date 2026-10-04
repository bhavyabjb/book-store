import { useQuery } from '@tanstack/react-query'
import { getBook, getRelatedBooks, listBooks, listCategories, listReviews } from '@/api/client'
import type { BookDetail, ListBooksParams } from '@/types'
import { getCachedId, rememberBook, rememberBooks } from '@/lib/slugCache'

export function useCategories() {
  return useQuery({ queryKey: ['categories'], queryFn: listCategories })
}

export function useBooks(params: ListBooksParams, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ['books', params],
    queryFn: async () => {
      const page = await listBooks(params)
      rememberBooks(page.items)
      return page
    },
    placeholderData: (prev) => prev,
    enabled: options?.enabled ?? true,
  })
}

/**
 * Resolves a book's route slug to the numeric id the API requires and loads
 * its detail. The contract only exposes GET /books/{bookId} (integer), so we
 * first check the slug->id cache populated while browsing, and fall back to
 * scanning the catalog once (covers hard refresh / shared links) before
 * calling the detail endpoint.
 */
export function useBook(slug: string | undefined) {
  return useQuery<BookDetail>({
    queryKey: ['book', slug],
    queryFn: async () => {
      if (!slug) throw new Error('Missing book slug')
      if (/^\d+$/.test(slug)) {
        const book = await getBook(slug)
        rememberBook(book)
        return book
      }
      const cachedId = getCachedId(slug)
      if (cachedId !== undefined) {
        const book = await getBook(cachedId)
        rememberBook(book)
        return book
      }
      const page = await listBooks({ pageSize: 100 })
      rememberBooks(page.items)
      const match = page.items.find((b) => b.slug === slug)
      if (!match) throw new Error('Book not found')
      const book = await getBook(match.id)
      rememberBook(book)
      return book
    },
    enabled: slug !== undefined,
  })
}

export function useRelatedBooks(bookId: string | number | undefined, limit = 4) {
  return useQuery({
    queryKey: ['book', bookId, 'related', limit],
    queryFn: async () => {
      const related = await getRelatedBooks(bookId as string | number, limit)
      rememberBooks(related)
      return related
    },
    enabled: bookId !== undefined,
  })
}

export function useReviews(bookId: string | number | undefined) {
  return useQuery({
    queryKey: ['book', bookId, 'reviews'],
    queryFn: () => listReviews(bookId as string | number),
    enabled: bookId !== undefined,
  })
}
