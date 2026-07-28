import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
// IDs generated inline
let _notificationId = 0
function nextId() { return `n-${++_notificationId}` }

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: string
  read: boolean
  autoClose?: boolean
  duration?: number
}

export interface NotificationState {
  notifications: Notification[]
  unreadCount: number
  isLoading: boolean
  error: string | null
}

const initialState: NotificationState = {
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  error: null,
}

export const addNotification = createAsyncThunk(
  'notifications/add',
  async (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    return {
      ...notification,
      id: nextId(),
      timestamp: new Date().toISOString(),
      read: false,
    }
  },
)

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    markAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find((n) => n.id === action.payload)
      if (notification && !notification.read) {
        notification.read = true
        state.unreadCount = Math.max(0, state.unreadCount - 1)
      }
    },
    markAllAsRead: (state) => {
      state.notifications.forEach((n) => (n.read = true))
      state.unreadCount = 0
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      const index = state.notifications.findIndex((n) => n.id === action.payload)
      if (index !== -1) {
        if (!state.notifications[index].read) {
          state.unreadCount = Math.max(0, state.unreadCount - 1)
        }
        state.notifications.splice(index, 1)
      }
    },
    clearNotifications: (state) => {
      state.notifications = []
      state.unreadCount = 0
    },
  },
  extraReducers: (builder) => {
    builder.addCase(addNotification.fulfilled, (state, action) => {
      state.notifications.unshift(action.payload)
      state.unreadCount += 1
      // Keep max 100 notifications
      if (state.notifications.length > 100) {
        state.notifications.pop()
      }
    })
  },
})

export const {
  markAsRead,
  markAllAsRead,
  removeNotification,
  clearNotifications,
} = notificationSlice.actions

export default notificationSlice.reducer

