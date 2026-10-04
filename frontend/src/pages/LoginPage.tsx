import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useLogin } from '@/hooks/useAuthActions'
import { ApiError } from '@/api/client'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const login = useLogin()
  const navigate = useNavigate()
  const location = useLocation() as { state?: { from?: { pathname: string } } }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await login.mutateAsync({ email, password })
      navigate(location.state?.from?.pathname ?? '/')
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Could not log in. Please try again.')
    }
  }

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-6 py-16">
      <h1 className="text-center text-2xl font-semibold">Log in to Book Worm</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 rounded-xl bg-surface p-6">
        <label className="text-sm">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text focus:border-primary focus:outline-none"
          />
        </label>
        <label className="text-sm">
          Password
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text focus:border-primary focus:outline-none"
          />
        </label>
        {error && <p className="text-sm text-accent-red">{error}</p>}
        <button
          type="submit"
          disabled={login.isPending}
          className="rounded-lg bg-primary px-5 py-2.5 font-semibold text-white hover:bg-primary-hover disabled:opacity-60"
        >
          {login.isPending ? 'Logging in…' : 'Log In'}
        </button>
        <p className="text-center text-sm text-text-muted">
          New to Book Worm?{' '}
          <Link to="/register" className="text-primary hover:underline">
            Create an account
          </Link>
        </p>
      </form>
    </div>
  )
}
