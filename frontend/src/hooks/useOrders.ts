import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { cancelOrder, createOrder, getOrder, listOrders } from '@/api/client'
import type { OrderCreateRequest } from '@/types'

export const ORDERS_QUERY_KEY = ['orders'] as const

export function useOrders() {
  return useQuery({ queryKey: ORDERS_QUERY_KEY, queryFn: listOrders })
}

export function useOrder(orderId: string | number | undefined) {
  return useQuery({
    queryKey: ['order', orderId],
    queryFn: () => getOrder(orderId as string | number),
    enabled: orderId !== undefined,
  })
}

export function useCreateOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: OrderCreateRequest) => createOrder(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ORDERS_QUERY_KEY }),
  })
}

export function useCancelOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (orderId: number) => cancelOrder(orderId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ORDERS_QUERY_KEY }),
  })
}
