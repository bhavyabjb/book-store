import { describe, expect, it } from 'vitest'
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { App } from '@/App'
import { renderWithProviders, loginTestUser } from '@/test/utils'
import { server } from '@/test/server'
import { API_BASE_URL } from '@/api/client'

describe('MyOrdersPage', () => {
  it('only shows Cancel Order while within the 48h cancellation window', async () => {
    loginTestUser()
    renderWithProviders(<App />, { route: '/orders' })

    const order201 = (await screen.findByText('Order #201')).closest('div.rounded-xl') as HTMLElement
    const order202 = screen.getByText('Order #202').closest('div.rounded-xl') as HTMLElement

    expect(within(order201).getByRole('button', { name: 'Cancel Order' })).toBeInTheDocument()
    expect(within(order202).queryByRole('button', { name: 'Cancel Order' })).not.toBeInTheDocument()
  })

  it('gracefully surfaces a 422 if the cancellation window closes before the click lands', async () => {
    server.use(
      http.post(`${API_BASE_URL}/orders/:orderId/cancel`, () =>
        HttpResponse.json({ detail: 'Cancellation window has expired' }, { status: 422 }),
      ),
    )
    loginTestUser()
    const user = userEvent.setup()
    renderWithProviders(<App />, { route: '/orders' })

    const order201 = (await screen.findByText('Order #201')).closest('div.rounded-xl') as HTMLElement
    await user.click(within(order201).getByRole('button', { name: 'Cancel Order' }))

    await waitFor(() => {
      expect(within(order201).getByText(/cancellation window has closed/i)).toBeInTheDocument()
    })
  })
})
