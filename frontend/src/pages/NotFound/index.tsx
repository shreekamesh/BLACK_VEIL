import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Typography, Button, Paper } from '@mui/material'
import { ErrorOutline as ErrorIcon } from '@mui/icons-material'

const NotFound: React.FC = () => {
  const navigate = useNavigate()

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <Paper sx={{ p: 6, textAlign: 'center', maxWidth: 500 }}>
        <ErrorIcon sx={{ fontSize: 80, color: 'warning.main', mb: 2 }} />
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>404</Typography>
        <Typography variant="h6" gutterBottom color="text.secondary">
          Page Not Found
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          The page you are looking for doesn't exist or has been moved.
        </Typography>
        <Button variant="contained" size="large" onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
      </Paper>
    </Box>
  )
}

export default NotFound
