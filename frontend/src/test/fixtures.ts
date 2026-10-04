import type {
  Address,
  Author,
  BookDetail,
  BookSummary,
  Cart,
  Category,
  Order,
  OrderSummary,
  Review,
  UserProfile,
} from '@/types'

export const authorDanielReed: Author = {
  id: 1,
  name: 'Daniel Reed',
  bio: 'Daniel Reed is a writer, minimalist, and productivity coach based in San Francisco.',
  photoUrl: null,
}

export const authorJamesWright: Author = {
  id: 2,
  name: 'James Wright',
  bio: 'James Wright writes about goals and personal growth.',
  photoUrl: null,
}

export const categoryNonFiction: Category = {
  id: 1,
  name: 'Non-fiction',
  slug: 'non-fiction',
  parentId: null,
}

export const categorySelfHelp: Category = {
  id: 2,
  name: 'Self Help',
  slug: 'self-help',
  parentId: 1,
}

export const categories: Category[] = [categoryNonFiction, categorySelfHelp]

export const bookJoyOfMinimalism: BookSummary = {
  id: 101,
  slug: 'joy-of-minimalism',
  title: 'Joy of Minimalism',
  author: authorDanielReed,
  description: 'Declutter your life to uncover peace, clarity, and joy.',
  price: 149,
  format: 'Paperback',
  coverImageUrl: null,
  tags: ['Non-fiction', 'Self Help'],
  ratingAvg: 4.5,
  deliveryDate: '2026-07-21',
}

export const bookPathToSuccess: BookSummary = {
  id: 102,
  slug: 'path-to-success',
  title: 'The Path to Success',
  author: authorJamesWright,
  description: 'A practical guide to achieving goals with clarity and confidence.',
  price: 359,
  format: 'Paperback',
  coverImageUrl: null,
  tags: ['Non-fiction', 'Self Help'],
  ratingAvg: 4.2,
  deliveryDate: '2026-07-21',
}

export const bookSummaries: BookSummary[] = [bookJoyOfMinimalism, bookPathToSuccess]

export const bookJoyOfMinimalismDetail: BookDetail = {
  ...bookJoyOfMinimalism,
  publisher: 'ABC Publishers',
  language: 'English',
  isbn: '978-0-123456-78-9',
  backCoverImageUrl: null,
  unitsSold: 145,
  category: categorySelfHelp,
}

export const reviews: Review[] = [
  {
    id: 1,
    bookId: 101,
    reviewerName: 'John Smith',
    rating: 5,
    comment: 'Loved this book.',
    createdAt: '2026-06-01T10:00:00Z',
  },
]

export const emptyCart: Cart = {
  items: [],
  subtotal: 0,
  tax: 0,
  deliveryCharge: 0,
  total: 0,
}

export const cartWithItems: Cart = {
  items: [
    { book: bookJoyOfMinimalism, quantity: 1, lineTotal: 149 },
    { book: bookPathToSuccess, quantity: 1, lineTotal: 359 },
  ],
  subtotal: 508,
  tax: 62,
  deliveryCharge: 0,
  total: 470,
}

export const userProfile: UserProfile = {
  id: 1,
  email: 'jane@example.com',
  firstName: 'Jane',
  lastName: 'Doe',
  phone: null,
  giftPointsBalance: 0,
}

export const address: Address = {
  id: 1,
  firstName: 'Jane',
  lastName: 'Doe',
  line1: '221B Baker Street',
  city: 'Mumbai',
  state: 'Maharashtra',
  pin: '400001',
  country: 'India',
  phone: '+919999999999',
  email: 'jane@example.com',
  isDefault: true,
}

const now = Date.now()

export const orderWithinCancelWindow: OrderSummary = {
  id: 201,
  status: 'PAID',
  total: 470,
  placedAt: new Date(now - 60 * 60 * 1000).toISOString(),
  cancelBy: new Date(now + 47 * 60 * 60 * 1000).toISOString(),
  items: [{ book: bookJoyOfMinimalism, quantity: 1, unitPrice: 149 }],
}

export const orderPastCancelWindow: OrderSummary = {
  id: 202,
  status: 'PAID',
  total: 359,
  placedAt: new Date(now - 72 * 60 * 60 * 1000).toISOString(),
  cancelBy: new Date(now - 24 * 60 * 60 * 1000).toISOString(),
  items: [{ book: bookPathToSuccess, quantity: 1, unitPrice: 359 }],
}

export const orderDetail: Order = {
  ...orderWithinCancelWindow,
  address,
  subtotal: 149,
  tax: 0,
  deliveryCharge: 0,
  discount: 0,
  couponCode: null,
  giftPointsRedeemed: 0,
}
