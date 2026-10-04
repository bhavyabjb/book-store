import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { addToWishlist, getWishlist, removeFromWishlist } from '@/api/client'

export const WISHLIST_QUERY_KEY = ['wishlist'] as const

export function useWishlist() {
  return useQuery({ queryKey: WISHLIST_QUERY_KEY, queryFn: getWishlist })
}

export function useAddToWishlist() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (bookId: number) => addToWishlist(bookId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: WISHLIST_QUERY_KEY }),
  })
}

export function useRemoveFromWishlist() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (bookId: number) => removeFromWishlist(bookId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: WISHLIST_QUERY_KEY }),
  })
}
