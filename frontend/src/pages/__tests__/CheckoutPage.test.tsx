import { describe, expect, it } from 'vitest'
import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { App } from '@/App'
import { renderWithProviders, loginTestUser } from '@/test/utils'
import { server } from '@/test/server'
import { API_BASE_URL } from '@/api/client'
import { cartWithItems } from '@/test/fixtures'

describe('CheckoutPage', () => {
  it('renders order totals computed from the mocked cart response', async () => {
    server.use(http.get(`${API_BASE_URL}/cart`, () => HttpResponse.json(cartWithItems)))
    loginTestUser()

    renderWithProviders(<App />, { route: '/checkout' })

    expect(await screen.findByRole('heading', { name: 'Shopping Cart' })).toBeInTheDocument()
    expect((await screen.findAllByText('Joy of Minimalism')).length).toBeGreaterThan(0)
    expect(screen.getAllByText('The Path to Success').length).toBeGreaterThan(0)

    expect(screen.getByText('Price (2 items)')).toBeInTheDocument()
    expect(screen.getByText('₹508')).toBeInTheDocument()
    expect(screen.getByText('₹62')).toBeInTheDocument()
    expect(screen.getByText('Free')).toBeInTheDocument()
    expect(screen.getByText('₹470')).toBeInTheDocument()
  })
})
