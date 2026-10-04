import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useCartStore } from '@/store/cartStore'
import { useAuthStore } from '@/store/authStore'
import { CartIcon, LogoIcon, UserIcon } from '@/components/icons'

export function Header() {
  const itemCount = useCartStore((s) => s.itemCount)
  const user = useAuthStore((s) => s.user)
  const clearSession = useAuthStore((s) => s.clearSession)
  const [menuOpen, setMenuOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <header className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-bg px-6 py-4">
      <div className="flex items-center gap-6">
        <Link to="/" className="flex items-center gap-2 text-lg font-semibold text-text">
          <LogoIcon className="h-5 w-5" />
          Book Worm
        </Link>
        <nav className="hidden items-center gap-6 border-l border-border pl-6 text-sm text-text-muted sm:flex">
          <Link to="/orders" className="hover:text-text">
            My Orders
          </Link>
          <Link to="/wishlist" className="hover:text-text">
            My Wishlist
          </Link>
          <Link to="/writers" className="hover:text-text">
            My Writers
          </Link>
        </nav>
      </div>
      <div className="flex items-center gap-5">
        <Link to="/checkout" aria-label="Cart" className="relative text-text">
          <CartIcon className="h-6 w-6" />
          {itemCount > 0 && (
            <span
              data-testid="cart-badge"
              className="absolute -right-2 -top-2 flex h-5 min-w-5 items-center justify-center rounded-full bg-accent-red px-1 text-xs font-semibold text-white"
            >
              {itemCount}
            </span>
          )}
        </Link>
        <div className="relative">
          <button
            type="button"
            aria-label="Account"
            className="text-text"
            onClick={() => setMenuOpen((v) => !v)}
          >
            <UserIcon className="h-6 w-6" />
          </button>
          {menuOpen && (
            <div
              className="absolute right-0 top-8 w-44 rounded-lg border border-border bg-surface py-2 text-sm shadow-lg"
              onMouseLeave={() => setMenuOpen(false)}
            >
              {user ? (
                <>
                  <div className="px-4 py-1.5 text-text-muted">{user.firstName}</div>
                  <button
                    type="button"
                    className="block w-full px-4 py-1.5 text-left hover:bg-surface-2"
                    onClick={() => {
                      clearSession()
                      setMenuOpen(false)
                      navigate('/')
                    }}
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="block px-4 py-1.5 hover:bg-surface-2"
                    onClick={() => setMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="block px-4 py-1.5 hover:bg-surface-2"
                    onClick={() => setMenuOpen(false)}
                  >
                    Register
                  </Link>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
