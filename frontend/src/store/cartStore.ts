import { create } from 'zustand'
import type { Cart } from '@/types'

const EMPTY_CART: Cart = {
  items: [],
  subtotal: 0,
  tax: 0,
  deliveryCharge: 0,
  total: 0,
}

interface CartState {
  cart: Cart
  itemCount: number
  setCart: (cart: Cart) => void
  clearCart: () => void
}

function countItems(cart: Cart): number {
  return cart.items.reduce((sum, item) => sum + item.quantity, 0)
}

export const useCartStore = create<CartState>()((set) => ({
  cart: EMPTY_CART,
  itemCount: 0,
  setCart: (cart) => set({ cart, itemCount: countItems(cart) }),
  clearCart: () => set({ cart: EMPTY_CART, itemCount: 0 }),
}))
