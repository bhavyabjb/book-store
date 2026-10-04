import { useAuthStore } from '@/store/authStore'
import type {
  Address,
  AddressCreate,
  BookDetail,
  BookPage,
  BookSummary,
  Cart,
  CartItemCreate,
  CartItemUpdate,
  Category,
  CouponApplyRequest,
  CouponApplyResponse,
  ListBooksParams,
  LoginRequest,
  Order,
  OrderCreateRequest,
  OrderSummary,
  PaymentRequest,
  PaymentResult,
  RegisterRequest,
  Review,
  ReviewCreate,
  TokenResponse,
  UserProfile,
} from '@/types'

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
    this.detail = detail
  }
}

function buildQuery(params?: Record<string, unknown>): string {
  if (!params) return ''
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue
    search.set(key, String(value))
  }
  const qs = search.toString()
  return qs ? `?${qs}` : ''
}

async function request<T>(
  path: string,
  options: {
    method?: string
    body?: unknown
    query?: Record<string, unknown>
    auth?: boolean
  } = {},
): Promise<T> {
  const { method = 'GET', body, query, auth = true } = options
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  if (auth) {
    const token = useAuthStore.getState().token
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE_URL}${path}${buildQuery(query)}`, {
    method,
    headers,
    credentials: 'include',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (res.status === 204) {
    return undefined as T
  }

  const text = await res.text()
  const data = text ? JSON.parse(text) : undefined

  if (!res.ok) {
    const detail =
      data && typeof data === 'object' && 'detail' in data
        ? String((data as { detail: unknown }).detail)
        : res.statusText
    throw new ApiError(res.status, detail)
  }

  return data as T
}

// ---- auth ----
export const registerUser = (body: RegisterRequest) =>
  request<TokenResponse>('/auth/register', { method: 'POST', body, auth: false })

export const loginUser = (body: LoginRequest) =>
  request<TokenResponse>('/auth/login', { method: 'POST', body, auth: false })

export const getCurrentUser = () => request<UserProfile>('/auth/me')

// ---- catalog ----
export const listCategories = () => request<Category[]>('/categories', { auth: false })

export const listBooks = (params?: ListBooksParams) =>
  request<BookPage>('/books', { query: params as Record<string, unknown>, auth: false })

export const getBook = (bookId: number | string) =>
  request<BookDetail>(`/books/${bookId}`, { auth: false })

export const getRelatedBooks = (bookId: number | string, limit = 4) =>
  request<BookSummary[]>(`/books/${bookId}/related`, { query: { limit }, auth: false })

// ---- reviews ----
export const listReviews = (bookId: number | string) =>
  request<Review[]>(`/books/${bookId}/reviews`, { auth: false })

export const createReview = (bookId: number | string, body: ReviewCreate) =>
  request<Review>(`/books/${bookId}/reviews`, { method: 'POST', body })

// ---- wishlist ----
export const getWishlist = () => request<BookSummary[]>('/wishlist')

export const addToWishlist = (bookId: number | string) =>
  request<void>(`/wishlist/${bookId}`, { method: 'POST' })

export const removeFromWishlist = (bookId: number | string) =>
  request<void>(`/wishlist/${bookId}`, { method: 'DELETE' })

// ---- cart ----
export const getCart = () => request<Cart>('/cart')

export const addCartItem = (body: CartItemCreate) =>
  request<Cart>('/cart/items', { method: 'POST', body })

export const updateCartItem = (bookId: number | string, body: CartItemUpdate) =>
  request<Cart>(`/cart/items/${bookId}`, { method: 'PATCH', body })

export const removeCartItem = (bookId: number | string) =>
  request<Cart>(`/cart/items/${bookId}`, { method: 'DELETE' })

// ---- addresses ----
export const listAddresses = () => request<Address[]>('/addresses')

export const createAddress = (body: AddressCreate) =>
  request<Address>('/addresses', { method: 'POST', body })

// ---- coupons ----
export const applyCoupon = (body: CouponApplyRequest) =>
  request<CouponApplyResponse>('/coupons/apply', { method: 'POST', body })

// ---- orders ----
export const listOrders = () => request<OrderSummary[]>('/orders')

export const createOrder = (body: OrderCreateRequest) =>
  request<Order>('/orders', { method: 'POST', body })

export const getOrder = (orderId: number | string) => request<Order>(`/orders/${orderId}`)

export const cancelOrder = (orderId: number | string) =>
  request<Order>(`/orders/${orderId}/cancel`, { method: 'POST' })

// ---- payments ----
export const payForOrder = (orderId: number | string, body: PaymentRequest) =>
  request<PaymentResult>(`/orders/${orderId}/payment`, { method: 'POST', body })
