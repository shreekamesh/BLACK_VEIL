import { useState, useCallback } from 'react'
import { apiClient } from '@/api/client'
import toast from 'react-hot-toast'

interface UseApiState<T> {
  data: T | null
  isLoading: boolean
  error: string | null
}

export function useApi<T = any>() {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    isLoading: false,
    error: null,
  })

  const execute = useCallback(
    async (
      apiCall: () => Promise<T>,
      options?: { showSuccess?: boolean; successMessage?: string },
    ) => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }))

      try {
        const data = await apiCall()
        setState({ data, isLoading: false, error: null })

        if (options?.showSuccess) {
          toast.success(options.successMessage || 'Operation completed successfully')
        }

        return data
      } catch (err: any) {
        const message = err?.response?.data?.message || err?.message || 'An error occurred'
        setState((prev) => ({ ...prev, isLoading: false, error: message }))
        toast.error(message)
        throw err
      }
    },
    [],
  )

  const reset = useCallback(() => {
    setState({ data: null, isLoading: false, error: null })
  }, [])

  return {
    ...state,
    execute,
    reset,
    get: useCallback(
      (url: string, params?: any) => execute(() => apiClient.get<T>(url, params)),
      [execute],
    ),
    post: useCallback(
      (url: string, data?: any) => execute(() => apiClient.post<T>(url, data)),
      [execute],
    ),
    put: useCallback(
      (url: string, data?: any) => execute(() => apiClient.put<T>(url, data)),
      [execute],
    ),
    delete: useCallback(
      (url: string) => execute(() => apiClient.delete<T>(url)),
      [execute],
    ),
  }
}

