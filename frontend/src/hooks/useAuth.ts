import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { loginUser, registerUser, clearAuth, clearError } from '@/store/slices/authSlice'
import { RootState, AppDispatch } from '@/store'
import { ROUTES } from '@/config/routes.config'
import { wsManager } from '@/api/websocket'

export function useAuth() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { user, isAuthenticated, isLoading, error } = useSelector(
    (state: RootState) => state.auth,
  )

  const handleLogin = useCallback(
    async (username: string, password: string) => {
      try {
        await dispatch(loginUser({ username, password })).unwrap()
        wsManager.connect()
        navigate(ROUTES.DASHBOARD)
        return true
      } catch {
        return false
      }
    },
    [dispatch, navigate],
  )

  const handleRegister = useCallback(
    async (data: { username: string; email: string; password: string; fullName: string }) => {
      try {
        await dispatch(registerUser(data)).unwrap()
        wsManager.connect()
        navigate(ROUTES.DASHBOARD)
        return true
      } catch {
        return false
      }
    },
    [dispatch, navigate],
  )

  const handleLogout = useCallback(() => {
    wsManager.disconnect()
    dispatch(clearAuth())
    navigate(ROUTES.LOGIN)
  }, [dispatch, navigate])

  const handleClearError = useCallback(() => {
    dispatch(clearError())
  }, [dispatch])

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    clearError: handleClearError,
  }
}

