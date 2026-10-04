import { http, HttpResponse } from 'msw'
import { API_BASE_URL } from '@/api/client'
import {
  address,
  bookJoyOfMinimalismDetail,
  bookPathToSuccess,
  bookSummaries,
  categories,
  emptyCart,
  orderDetail,
  orderPastCancelWindow,
  orderWithinCancelWindow,
  reviews,
  userProfile,
} from '@/test/fixtures'
import type { Cart, PaymentRequest, PaymentResult } from '@/types'

let cartState: Cart = emptyCart

export function resetMockCart() {
  cartState = emptyCart
}

export const lastListBooksQuery = { value: null as URLSearchParams | null }

export const handlers = [
  http.get(`${API_BASE_URL}/categories`, () => HttpResponse.json(categories)),

  http.get(`${API_BASE_URL}/books`, ({ request }) => {
    const url = new URL(request.url)
    lastListBooksQuery.value = url.searchParams
    return HttpResponse.json({
      items: bookSummaries,
      total: bookSummaries.length,
      page: 1,
      pageSize: 12,
    })
  }),

  http.get(`${API_BASE_URL}/books/:bookId`, ({ params }) => {
    if (String(params.bookId) === String(bookJoyOfMinimalismDetail.id)) {
      return HttpResponse.json(bookJoyOfMinimalismDetail)
    }
    return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
  }),

  http.get(`${API_BASE_URL}/books/:bookId/related`, () => HttpResponse.json([bookPathToSuccess])),

  http.get(`${API_BASE_URL}/books/:bookId/reviews`, () => HttpResponse.json(reviews)),

  http.post(`${API_BASE_URL}/books/:bookId/reviews`, async ({ request }) => {
    const body = (await request.json()) as { rating: number; comment?: string }
    return HttpResponse.json(
      {
        id: 99,
        bookId: 101,
        reviewerName: 'You',
        rating: body.rating,
        comment: body.comment ?? null,
        createdAt: new Date().toISOString(),
      },
      { status: 201 },
    )
  }),

  http.get(`${API_BASE_URL}/cart`, () => HttpResponse.json(cartState)),

  http.post(`${API_BASE_URL}/cart/items`, async ({ request }) => {
    const body = (await request.json()) as { bookId: number; quantity?: number }
    const book = bookSummaries.find((b) => b.id === body.bookId)
    if (!book) return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
    const existing = cartState.items.find((i) => i.book.id === body.bookId)
    const quantity = (existing?.quantity ?? 0) + (body.quantity ?? 1)
    const items = [
      ...cartState.items.filter((i) => i.book.id !== body.bookId),
      { book, quantity, lineTotal: book.price * quantity },
    ]
    const subtotal = items.reduce((sum, i) => sum + i.lineTotal, 0)
    cartState = { items, subtotal, tax: 0, deliveryCharge: 0, total: subtotal }
    return HttpResponse.json(cartState)
  }),

  http.patch(`${API_BASE_URL}/cart/items/:bookId`, async ({ params, request }) => {
    const body = (await request.json()) as { quantity: number }
    const bookId = Number(params.bookId)
    let items = cartState.items
    if (body.quantity <= 0) {
      items = items.filter((i) => i.book.id !== bookId)
    } else {
      items = items.map((i) =>
        i.book.id === bookId ? { ...i, quantity: body.quantity, lineTotal: i.book.price * body.quantity } : i,
      )
    }
    const subtotal = items.reduce((sum, i) => sum + i.lineTotal, 0)
    cartState = { items, subtotal, tax: 0, deliveryCharge: 0, total: subtotal }
    return HttpResponse.json(cartState)
  }),

  http.delete(`${API_BASE_URL}/cart/items/:bookId`, ({ params }) => {
    const bookId = Number(params.bookId)
    const items = cartState.items.filter((i) => i.book.id !== bookId)
    const subtotal = items.reduce((sum, i) => sum + i.lineTotal, 0)
    cartState = { items, subtotal, tax: 0, deliveryCharge: 0, total: subtotal }
    return HttpResponse.json(cartState)
  }),

  http.get(`${API_BASE_URL}/addresses`, () => HttpResponse.json([address])),
  http.post(`${API_BASE_URL}/addresses`, () => HttpResponse.json(address, { status: 201 })),

  http.post(`${API_BASE_URL}/coupons/apply`, async ({ request }) => {
    const body = (await request.json()) as { code: string }
    if (body.code === 'SAVE100') {
      return HttpResponse.json({ code: 'SAVE100', discount: 100, newTotal: 370 })
    }
    return HttpResponse.json({ detail: 'Invalid or inactive coupon' }, { status: 404 })
  }),

  http.get(`${API_BASE_URL}/orders`, () => HttpResponse.json([orderWithinCancelWindow, orderPastCancelWindow])),
  http.post(`${API_BASE_URL}/orders`, () => HttpResponse.json(orderDetail, { status: 201 })),
  http.get(`${API_BASE_URL}/orders/:orderId`, () => HttpResponse.json(orderDetail)),

  http.post(`${API_BASE_URL}/orders/:orderId/cancel`, ({ params }) => {
    if (String(params.orderId) === String(orderPastCancelWindow.id)) {
      return HttpResponse.json({ detail: 'Cancellation window has expired' }, { status: 422 })
    }
    return HttpResponse.json({ ...orderDetail, status: 'CANCELLED' })
  }),

  http.post(`${API_BASE_URL}/orders/:orderId/payment`, async ({ request, params }) => {
    const body = (await request.json()) as PaymentRequest
    const declined = body.cardNumber === '0000000000000000' || body.upiId === 'decline@upi'
    const result: PaymentResult = declined
      ? {
          status: 'FAILED',
          orderId: Number(params.orderId),
          amount: orderDetail.total,
          transactionRef: null,
          failureReason: 'Your bank declined this transaction.',
        }
      : {
          status: 'SUCCESS',
          orderId: Number(params.orderId),
          amount: orderDetail.total,
          transactionRef: 'TXN123',
          failureReason: null,
        }
    return HttpResponse.json(result)
  }),

  http.post(`${API_BASE_URL}/auth/login`, () =>
    HttpResponse.json({ accessToken: 'mock-token', tokenType: 'bearer', user: userProfile }),
  ),
  http.post(`${API_BASE_URL}/auth/register`, () =>
    HttpResponse.json({ accessToken: 'mock-token', tokenType: 'bearer', user: userProfile }, { status: 201 }),
  ),
  http.get(`${API_BASE_URL}/auth/me`, () => HttpResponse.json(userProfile)),

  http.get(`${API_BASE_URL}/wishlist`, () => HttpResponse.json([bookJoyOfMinimalismDetail])),
  http.post(`${API_BASE_URL}/wishlist/:bookId`, () => new HttpResponse(null, { status: 204 })),
  http.delete(`${API_BASE_URL}/wishlist/:bookId`, () => new HttpResponse(null, { status: 204 })),
]
