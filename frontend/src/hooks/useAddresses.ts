import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createAddress, listAddresses } from '@/api/client'
import type { AddressCreate } from '@/types'

export const ADDRESSES_QUERY_KEY = ['addresses'] as const

export function useAddresses() {
  return useQuery({ queryKey: ADDRESSES_QUERY_KEY, queryFn: listAddresses })
}

export function useCreateAddress() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: AddressCreate) => createAddress(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ADDRESSES_QUERY_KEY }),
  })
}
