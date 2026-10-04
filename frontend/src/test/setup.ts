import '@testing-library/jest-dom/vitest'
import { afterAll, afterEach, beforeAll } from 'vitest'
import { server } from '@/test/server'
import { resetMockCart } from '@/test/handlers'
import { useAuthStore } from '@/store/authStore'
import { useCartStore } from '@/store/cartStore'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  server.resetHandlers()
  resetMockCart()
  useAuthStore.getState().clearSession()
  useCartStore.getState().clearCart()
  window.sessionStorage.clear()
  window.localStorage.clear()
})
afterAll(() => server.close())
