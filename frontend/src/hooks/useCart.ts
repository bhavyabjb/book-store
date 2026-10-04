import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { addCartItem, getCart, removeCartItem, updateCartItem } from '@/api/client'
import { useCartStore } from '@/store/cartStore'
import { useEffect } from 'react'
import type { CartItemCreate } from '@/types'

export const CART_QUERY_KEY = ['cart'] as const

export function useCart() {
  const setCart = useCartStore((s) => s.setCart)
  const query = useQuery({
    queryKey: CART_QUERY_KEY,
    queryFn: getCart,
  })

  useEffect(() => {
    if (query.data) setCart(query.data)
  }, [query.data, setCart])

  return query
}

export function useAddCartItem() {
  const queryClient = useQueryClient()
  const setCart = useCartStore((s) => s.setCart)
  return useMutation({
    mutationFn: (body: CartItemCreate) => addCartItem(body),
    onSuccess: (cart) => {
      setCart(cart)
      queryClient.setQueryData(CART_QUERY_KEY, cart)
    },
  })
}

export function useUpdateCartItem() {
  const queryClient = useQueryClient()
  const setCart = useCartStore((s) => s.setCart)
  return useMutation({
    mutationFn: ({ bookId, quantity }: { bookId: number; quantity: number }) =>
      updateCartItem(bookId, { quantity }),
    onSuccess: (cart) => {
      setCart(cart)
      queryClient.setQueryData(CART_QUERY_KEY, cart)
    },
  })
}

export function useRemoveCartItem() {
  const queryClient = useQueryClient()
  const setCart = useCartStore((s) => s.setCart)
  return useMutation({
    mutationFn: (bookId: number) => removeCartItem(bookId),
    onSuccess: (cart) => {
      setCart(cart)
      queryClient.setQueryData(CART_QUERY_KEY, cart)
    },
  })
}
