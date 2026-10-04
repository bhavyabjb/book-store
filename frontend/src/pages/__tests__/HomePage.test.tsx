import { describe, expect, it, beforeEach } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { HomePage } from '@/pages/HomePage'
import { renderWithProviders } from '@/test/utils'
import { lastListBooksQuery } from '@/test/handlers'

describe('HomePage', () => {
  beforeEach(() => {
    lastListBooksQuery.value = null
  })

  it('renders category sidebar and book rails from the API', async () => {
    renderWithProviders(<HomePage />)

    expect(await screen.findByText('Recommended for You')).toBeInTheDocument()
    expect(screen.getByText('Bestsellers this Month')).toBeInTheDocument()
    expect(screen.getByText('New Launches')).toBeInTheDocument()

    // Category sidebar from GET /categories
    expect(await screen.findByRole('button', { name: 'Non-fiction' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'All' })).toBeInTheDocument()

    // Book cards from GET /books (one per rail, same fixture data)
    expect((await screen.findAllByText('Joy of Minimalism')).length).toBeGreaterThan(0)
  })

  it('refetches with the correct query params when filters change', async () => {
    renderWithProviders(<HomePage />)
    await screen.findByText('Recommended for You')

    const search = screen.getByLabelText('Search')
    fireEvent.change(search, { target: { value: 'minimalism' } })

    await waitFor(() => {
      expect(lastListBooksQuery.value?.get('q')).toBe('minimalism')
    })

    // Switches from curated rails to a single search-results rail
    expect(screen.getByText('Search Results')).toBeInTheDocument()
    expect(screen.queryByText('Recommended for You')).not.toBeInTheDocument()

    const formatSelect = screen.getByLabelText('Format')
    fireEvent.change(formatSelect, { target: { value: 'Paperback' } })

    await waitFor(() => {
      expect(lastListBooksQuery.value?.get('format')).toBe('Paperback')
      expect(lastListBooksQuery.value?.get('q')).toBe('minimalism')
    })

    const sortSelect = screen.getByLabelText('Sort by')
    fireEvent.change(sortSelect, { target: { value: 'price_asc' } })

    await waitFor(() => {
      expect(lastListBooksQuery.value?.get('sort')).toBe('price_asc')
    })
  })
})
