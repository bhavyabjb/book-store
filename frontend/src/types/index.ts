import type { components } from '@/api/schema'

export type Schemas = components['schemas']

export type Error_ = Schemas['Error']
export type BookFormat = Schemas['BookFormat']
export type RegisterRequest = Schemas['RegisterRequest']
export type LoginRequest = Schemas['LoginRequest']
export type TokenResponse = Schemas['TokenResponse']
export type UserProfile = Schemas['UserProfile']
export type Category = Schemas['Category']
export type Author = Schemas['Author']
export type BookSummary = Schemas['BookSummary']
export type BookDetail = Schemas['BookDetail']
export type BookPage = Schemas['BookPage']
export type Review = Schemas['Review']
export type ReviewCreate = Schemas['ReviewCreate']
export type CartItem = Schemas['CartItem']
export type Cart = Schemas['Cart']
export type CartItemCreate = Schemas['CartItemCreate']
export type CartItemUpdate = Schemas['CartItemUpdate']
export type Address = Schemas['Address']
export type AddressCreate = Schemas['AddressCreate']
export type CouponApplyRequest = Schemas['CouponApplyRequest']
export type CouponApplyResponse = Schemas['CouponApplyResponse']
export type OrderCreateRequest = Schemas['OrderCreateRequest']
export type OrderItem = Schemas['OrderItem']
export type OrderStatus = Schemas['OrderStatus']
export type OrderSummary = Schemas['OrderSummary']
export type Order = Schemas['Order']
export type PaymentMethod = Schemas['PaymentMethod']
export type PaymentRequest = Schemas['PaymentRequest']
export type PaymentStatus = Schemas['PaymentStatus']
export type PaymentResult = Schemas['PaymentResult']

export interface ListBooksParams {
  q?: string
  category?: string
  author?: string
  language?: string
  format?: BookFormat
  minPrice?: number
  maxPrice?: number
  sort?: 'relevance' | 'price_asc' | 'price_desc' | 'rating' | 'newest'
  section?: 'recommended' | 'bestsellers' | 'new_launches'
  page?: number
  pageSize?: number
}
