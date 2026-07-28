
// BLACK VEIL V5 - Notification System Hook
import { useCallback } from 'react'
import { useDispatch } from 'react-redux'
import { addNotification } from '@/store/slices/notificationSlice'

export function useNotifications() {
  const dispatch = useDispatch()

  const showNotification = useCallback(
    (notification: {
      title: string
      message: string
      type: 'success' | 'error' | 'warning' | 'info'
      autoClose?: boolean
      duration?: number
    }) => {
      dispatch(addNotification(notification) as any)
    },
    [dispatch]
  )

  const showSuccess = useCallback(
    (message: string) => {
      showNotification({ title: 'Success', message, type: 'success' })
    },
    [showNotification]
  )

  const showError = useCallback(
    (message: string) => {
      showNotification({ title: 'Error', message, type: 'error' })
    },
    [showNotification]
  )

  const showWarning = useCallback(
    (message: string) => {
      showNotification({ title: 'Warning', message, type: 'warning' })
    },
    [showNotification]
  )

  const showInfo = useCallback(
    (message: string) => {
      showNotification({ title: 'Info', message, type: 'info' })
    },
    [showNotification]
  )

  return {
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  }
}
