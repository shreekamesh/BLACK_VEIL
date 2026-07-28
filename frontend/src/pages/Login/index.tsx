import React, { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import {
  Box, Paper, TextField, Button, Typography, Alert, CircularProgress,
  InputAdornment, IconButton, Link,
} from '@mui/material'
import { Visibility, VisibilityOff } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { RootState, AppDispatch } from '@/store'
import { loginUser, clearError } from '@/store/slices/authSlice'
import { wsManager } from '@/api/websocket'
import { config } from '@/config'

const loginSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type LoginFormData = z.infer<typeof loginSchema>

const Login: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useDispatch<AppDispatch>()
  const { isLoading, error, isAuthenticated } = useSelector((state: RootState) => state.auth)
  const [showPassword, setShowPassword] = React.useState(false)

  const { control, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: '', password: '' },
  })

  const from = (location.state as any)?.from?.pathname || '/dashboard'

  useEffect(() => {
    if (isAuthenticated) {
      wsManager.connect()
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, from])

  useEffect(() => {
    return () => { dispatch(clearError()) }
  }, [dispatch])

  const onSubmit = async (data: LoginFormData) => {
    try {
      await dispatch(loginUser({ username: data.username, password: data.password })).unwrap()
    } catch {
      // Error handled by Redux slice
    }
  }

  return (
    <Box sx={{
      height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #0a0e17 0%, #121a28 50%, #1a2638 100%)',
      position: 'relative', overflow: 'hidden',
    }}>
      {/* Background grid effect */}
      <Box sx={{
        position: 'absolute', inset: 0,
        backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(0, 212, 255, 0.1) 1px, transparent 0)',
        backgroundSize: '40px 40px',
      }} />

      <Paper elevation={24} sx={{
        p: 4, maxWidth: 400, width: '100%', borderRadius: 2,
        position: 'relative', zIndex: 1,
      }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" sx={{
            fontWeight: 800,
            background: 'linear-gradient(135deg, #00d4ff, #7c3aed)',
            backgroundClip: 'text', WebkitBackgroundClip: 'text', color: 'transparent',
          }}>
            BLACK VEIL V5
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Cognitive Autonomous Cyber Defense Organism
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <Controller name="username" control={control}
            render={({ field }) => (
              <TextField {...field} fullWidth label="Username" margin="normal"
                error={!!errors.username} helperText={errors.username?.message}
                disabled={isLoading}
              />
            )}
          />
          <Controller name="password" control={control}
            render={({ field }) => (
              <TextField {...field} fullWidth label="Password"
                type={showPassword ? 'text' : 'password'} margin="normal"
                error={!!errors.password} helperText={errors.password?.message}
                disabled={isLoading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            )}
          />
          <Button type="submit" fullWidth variant="contained" size="large"
            disabled={isLoading} sx={{ mt: 3, mb: 2, py: 1.5 }}
          >
            {isLoading ? <CircularProgress size={24} sx={{ color: 'white' }} /> : 'Login'}
          </Button>

          <Box sx={{ textAlign: 'center' }}>
            <Link href="#" variant="body2" color="text.secondary" underline="hover">
              Forgot password?
            </Link>
          </Box>
        </form>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="caption" color="text.disabled">
            v{config.version} | {config.environment}
          </Typography>
        </Box>
      </Paper>
    </Box>
  )
}

export default Login
