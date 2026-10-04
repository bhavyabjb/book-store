import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useRegister } from '@/hooks/useAuthActions'
import { ApiError } from '@/api/client'

export function RegisterPage() {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const register = useRegister()
  const navigate = useNavigate()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await register.mutateAsync({ firstName, lastName, email, password })
      navigate('/')
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Could not create your account. Please try again.')
    }
  }

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-6 py-16">
      <h1 className="text-center text-2xl font-semibold">Create your Book Worm account</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 rounded-xl bg-surface p-6">
        <div className="grid grid-cols-2 gap-4">
          <label className="text-sm">
            First Name
            <input
              required
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text focus:border-primary focus:outline-none"
            />
          </label>
          <label className="text-sm">
            Last Name
            <input
              required
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text focus:border-primary focus:outline-none"
            />
          </label>
        </div>
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
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-text focus:border-primary focus:outline-none"
          />
        </label>
        {error && <p className="text-sm text-accent-red">{error}</p>}
        <button
          type="submit"
          disabled={register.isPending}
          className="rounded-lg bg-primary px-5 py-2.5 font-semibold text-white hover:bg-primary-hover disabled:opacity-60"
        >
          {register.isPending ? 'Creating account…' : 'Create Account'}
        </button>
        <p className="text-center text-sm text-text-muted">
          Already have an account?{' '}
          <Link to="/login" className="text-primary hover:underline">
            Log in
          </Link>
        </p>
      </form>
    </div>
  )
}
