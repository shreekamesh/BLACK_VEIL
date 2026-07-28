import { QueryClient } from '@tanstack/react-query'
import { config } from '@/config'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: config.api.retries,
      retryDelay: config.api.retryDelay,
      staleTime: 30000,
      cacheTime: 300000,
    },
    mutations: {
      retry: 1,
    },
  },
})

