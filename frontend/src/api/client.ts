import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios'
import { config } from '@/config'
import { store } from '@/store'
import { clearAuth, setTokens } from '@/store/slices/authSlice'

class ApiClient {
  private client: AxiosInstance
  private isRefreshing = false
  private refreshSubscribers: ((token: string) => void)[] = []

  constructor() {
    this.client = axios.create({
      baseURL: config.api.baseUrl,
      timeout: config.api.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    this.client.interceptors.request.use(
      (req: InternalAxiosRequestConfig) => {
        const state = store.getState()
        const token = state.auth.token
        if (token && req.headers) {
          req.headers.Authorization = `Bearer ${token}`
        }
        return req
      },
      (error) => Promise.reject(error),
    )

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          if (this.isRefreshing) {
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                originalRequest.headers.Authorization = `Bearer ${token}`
                resolve(this.client(originalRequest))
              })
            })
          }

          this.isRefreshing = true

          try {
            const state = store.getState()
            const refresh = state.auth.refreshToken

            if (!refresh) {
              throw new Error('No refresh token available')
            }

            const response = await this.client.post('/auth/refresh', {
              refreshToken: refresh,
            })

            const { token, refreshToken: newRefreshToken } = response.data

            store.dispatch(setTokens({ token, refreshToken: newRefreshToken }))

            this.isRefreshing = false

            this.refreshSubscribers.forEach((callback) => callback(token))
            this.refreshSubscribers = []

            originalRequest.headers.Authorization = `Bearer ${token}`
            return this.client(originalRequest)
          } catch (refreshError) {
            this.isRefreshing = false
            store.dispatch(clearAuth())
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      },
    )
  }

  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<T>(url, { params })
    return response.data
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data)
    return response.data
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(url, data)
    return response.data
  }

  async patch<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.patch<T>(url, data)
    return response.data
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url)
    return response.data
  }

  async upload<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await this.client.post<T>(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100
          onProgress(progress)
        }
      },
    })
    return response.data
  }
}

export const apiClient = new ApiClient()

