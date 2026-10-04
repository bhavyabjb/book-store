import { useMutation } from '@tanstack/react-query'
import { loginUser, registerUser } from '@/api/client'
import { useAuthStore } from '@/store/authStore'
import type { LoginRequest, RegisterRequest } from '@/types'

export function useLogin() {
  const setSession = useAuthStore((s) => s.setSession)
  return useMutation({
    mutationFn: (body: LoginRequest) => loginUser(body),
    onSuccess: (res) => setSession(res.accessToken, res.user),
  })
}

export function useRegister() {
  const setSession = useAuthStore((s) => s.setSession)
  return useMutation({
    mutationFn: (body: RegisterRequest) => registerUser(body),
    onSuccess: (res) => setSession(res.accessToken, res.user),
  })
}
