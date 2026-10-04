import { describe, expect, it, vi } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { PaymentModal } from '@/components/PaymentModal'
import { renderWithProviders } from '@/test/utils'

describe('PaymentModal', () => {
  it('calls onSuccess when the payment succeeds', async () => {
    const onSuccess = vi.fn()
    renderWithProviders(<PaymentModal orderId={201} amount={470} onSuccess={onSuccess} onClose={vi.fn()} />)

    expect(screen.getByText('Payable Amount: ₹470')).toBeInTheDocument()

    fireEvent.change(screen.getByPlaceholderText('XXXX-XXXX-XXXX-XXXX'), {
      target: { value: '1111222233334444' },
    })
    fireEvent.click(screen.getByRole('button', { name: /pay now/i }))

    await waitFor(() => expect(onSuccess).toHaveBeenCalled())
  })

  it('shows an inline error and allows retry when the payment is declined', async () => {
    const onSuccess = vi.fn()
    renderWithProviders(<PaymentModal orderId={201} amount={470} onSuccess={onSuccess} onClose={vi.fn()} />)

    fireEvent.change(screen.getByPlaceholderText('XXXX-XXXX-XXXX-XXXX'), {
      target: { value: '0000000000000000' },
    })
    fireEvent.click(screen.getByRole('button', { name: /pay now/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Your bank declined this transaction.')
    expect(onSuccess).not.toHaveBeenCalled()

    // Retry with a valid card succeeds
    fireEvent.change(screen.getByPlaceholderText('XXXX-XXXX-XXXX-XXXX'), {
      target: { value: '1111222233334444' },
    })
    fireEvent.click(screen.getByRole('button', { name: /pay now/i }))

    await waitFor(() => expect(onSuccess).toHaveBeenCalled())
  })
})
