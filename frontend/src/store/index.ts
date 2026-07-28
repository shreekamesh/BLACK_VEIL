// BLACK VEIL V5 - Redux Store Configuration
// Central state management with Redux Toolkit
import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query'
import { combineReducers } from 'redux'

import authReducer from './slices/authSlice'
import dashboardReducer from './slices/dashboardSlice'
import incidentReducer from './slices/incidentSlice'
import trustReducer from './slices/trustSlice'
import aiReducer from './slices/aiSlice'
import cognitiveReducer from './slices/cognitiveSlice'
import notificationReducer from './slices/notificationSlice'

const rootReducer = combineReducers({
  auth: authReducer,
  dashboard: dashboardReducer,
  incidents: incidentReducer,
  trust: trustReducer,
  ai: aiReducer,
  cognitive: cognitiveReducer,
  notifications: notificationReducer,
})

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
  devTools: import.meta.env.NODE_ENV !== 'production',
})

setupListeners(store.dispatch)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
