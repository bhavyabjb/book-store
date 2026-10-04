import { describe, expect, it } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { App } from '@/App'
import { renderWithProviders } from '@/test/utils'

describe('ProductDetailsPage', () => {
  it('renders book detail and adding to cart updates the header cart badge', async () => {
    renderWithProviders(<App />, { route: '/books/joy-of-minimalism' })

    expect(await screen.findByRole('heading', { name: 'Joy of Minimalism' })).toBeInTheDocument()
    expect(screen.getByText(/ABC Publishers/)).toBeInTheDocument()
    expect(screen.getByText('145 copies sold')).toBeInTheDocument()

    expect(screen.queryByTestId('cart-badge')).not.toBeInTheDocument()

    fireEvent.click(screen.getByTestId('add-to-cart'))

    await waitFor(() => {
      expect(screen.getByTestId('cart-badge')).toHaveTextContent('1')
    })
  })
})
