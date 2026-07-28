import React, { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { Provider as ReduxProvider } from 'react-redux'
// import { PersistGate } from 'redux-persist/integration/react'
import { ThemeProvider } from '@mui/material/styles'
import { CssBaseline, CircularProgress, Box } from '@mui/material'
import { Toaster } from 'react-hot-toast'

import { store } from '@/store'
import { queryClient } from '@/api'
import { theme } from '@/assets/styles/theme'
import { ProtectedRoute } from '@/components/common/ProtectedRoute'
import { Layout } from '@/components/common/Layout'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'

// Lazy load pages
const Login = lazy(() => import('@/pages/Login'))
const Dashboard = lazy(() => import('@/pages/Dashboard'))
const NotFound = lazy(() => import('@/pages/NotFound'))

// Placeholder pages - will be fully implemented
const PagePlaceholder = ({ title }: { title: string }) => (
  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
    <Box sx={{ textAlign: 'center' }}>
      <h2>{title}</h2>
      <p style={{ color: '#94a3b8' }}>Coming soon</p>
    </Box>
  </Box>
)

const LoadingFallback = () => (
  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
    <CircularProgress />
  </Box>
)

function App() {
  return (
    <ReduxProvider store={store}>
      <React.Fragment>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <Toaster
              position="bottom-right"
              toastOptions={{
                style: {
                  background: '#1a2638',
                  color: '#f1f5f9',
                  border: '1px solid rgba(148, 163, 184, 0.12)',
                  borderRadius: '8px',
                },
                success: { iconTheme: { primary: '#10b981', secondary: '#f1f5f9' } },
                error: { iconTheme: { primary: '#ef4444', secondary: '#f1f5f9' } },
              }}
            />
            <BrowserRouter>
              <ErrorBoundary>
                <Suspense fallback={<LoadingFallback />}>
                  <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />

                    <Route element={<ProtectedRoute />}>
                      <Route element={<Layout />}>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/dashboard/*" element={<Dashboard />} />

                        <Route path="/trust" element={<PagePlaceholder title="Trust Management" />} />
                        <Route path="/trust/*" element={<PagePlaceholder title="Trust Management" />} />

                        <Route path="/ai" element={<PagePlaceholder title="AI Predictions" />} />
                        <Route path="/ai/*" element={<PagePlaceholder title="AI Predictions" />} />

                        <Route path="/cognitive" element={<PagePlaceholder title="Cognitive State" />} />
                        <Route path="/cognitive/*" element={<PagePlaceholder title="Cognitive State" />} />

                        <Route path="/incidents" element={<PagePlaceholder title="Incident Management" />} />
                        <Route path="/incidents/*" element={<PagePlaceholder title="Incident Management" />} />

                        <Route path="/deception" element={<PagePlaceholder title="Deception Management" />} />
                        <Route path="/deception/*" element={<PagePlaceholder title="Deception Management" />} />

                        <Route path="/credentials" element={<PagePlaceholder title="Credential Management" />} />
                        <Route path="/credentials/*" element={<PagePlaceholder title="Credential Management" />} />

                        <Route path="/evolution" element={<PagePlaceholder title="Evolution Engine" />} />
                        <Route path="/evolution/*" element={<PagePlaceholder title="Evolution Engine" />} />

                        <Route path="/admin" element={<PagePlaceholder title="Administration" />} />
                        <Route path="/admin/*" element={<PagePlaceholder title="Administration" />} />

                        <Route path="/profile" element={<PagePlaceholder title="Profile" />} />
                        <Route path="/settings" element={<PagePlaceholder title="Settings" />} />
                      </Route>
                    </Route>

                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </Suspense>
              </ErrorBoundary>
            </BrowserRouter>
          </ThemeProvider>
        </QueryClientProvider>
      </React.Fragment>
    </ReduxProvider>
  )
}

export default App

