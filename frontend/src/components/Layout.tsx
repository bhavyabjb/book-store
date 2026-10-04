import { Outlet } from 'react-router-dom'
import { Header } from '@/components/Header'
import { useCart } from '@/hooks/useCart'

export function Layout() {
  // Load the cart once at the app shell level so the header badge count
  // stays accurate across every page, not just the checkout page.
  useCart()

  return (
    <div className="min-h-screen bg-bg text-text">
      <Header />
      <main>
        <Outlet />
      </main>
    </div>
  )
}
