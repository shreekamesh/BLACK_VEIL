import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { configureStore } from '@reduxjs/toolkit'
import Login from '../../pages/Login'
import authReducer from '../../store/slices/authSlice'

const createTestStore = () => {
  return configureStore({
    reducer: {
      auth: authReducer,
    },
    preloadedState: {
      auth: {
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      },
    },
  })
}

describe('Login Page', () => {
  it('renders login form correctly', () => {
    const store = createTestStore()
    render(
      <Provider store={store}>
        <BrowserRouter>
          <Login />
        </BrowserRouter>
      </Provider>,
    )

    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument()
  })

  it('shows BLACK VEIL branding', () => {
    const store = createTestStore()
    render(
      <Provider store={store}>
        <BrowserRouter>
          <Login />
        </BrowserRouter>
      </Provider>,
    )

    expect(screen.getByText('BLACK VEIL V5')).toBeInTheDocument()
    expect(
      screen.getByText('Cognitive Autonomous Cyber Defense Organism'),
    ).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    const store = createTestStore()
    render(
      <Provider store={store}>
        <BrowserRouter>
          <Login />
        </BrowserRouter>
      </Provider>,
    )

    const submitButton = screen.getByRole('button', { name: /Login/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(
        screen.getByText(/Username must be at least 3 characters/i),
      ).toBeInTheDocument()
      expect(
        screen.getByText(/Password must be at least 8 characters/i),
      ).toBeInTheDocument()
    })
  })

  it('toggles password visibility', async () => {
    const store = createTestStore()
    render(
      <Provider store={store}>
        <BrowserRouter>
          <Login />
        </BrowserRouter>
      </Provider>,
    )

    const passwordInput = screen.getByLabelText(/Password/i)
    const toggleButton = screen.getByRole('button', {
      name: /toggle password visibility/i,
    })

    expect(passwordInput).toHaveAttribute('type', 'password')

    await userEvent.click(toggleButton)
    expect(passwordInput).toHaveAttribute('type', 'text')

    await userEvent.click(toggleButton)
    expect(passwordInput).toHaveAttribute('type', 'password')
  })

  it('has forgot password link', () => {
    const store = createTestStore()
    render(
      <Provider store={store}>
        <BrowserRouter>
          <Login />
        </BrowserRouter>
      </Provider>,
    )

    expect(screen.getByText(/Forgot password/i)).toBeInTheDocument()
  })

  it('shows version number', () => {
    const store = createTestStore()
    render(
      <Provider store={store}>
        <BrowserRouter>
          <Login />
        </BrowserRouter>
      </Provider>,
    )

    expect(screen.getByText(/v5\.0\.0/i)).toBeInTheDocument()
  })
})

