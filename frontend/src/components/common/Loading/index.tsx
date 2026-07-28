import React from 'react'
import { Box, CircularProgress, Typography } from '@mui/material'

interface LoadingProps {
  message?: string
  fullPage?: boolean
}

export const Loading: React.FC<LoadingProps> = ({ message, fullPage = false }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: fullPage ? '100vh' : 300,
        gap: 2,
      }}
    >
      <CircularProgress size={40} />
      {message && (
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  )
}

export const LoadingSkeleton: React.FC<{ rows?: number; height?: number }> = ({
  rows = 3,
  height = 20,
}) => {
  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {Array.from({ length: rows }).map((_, i) => (
        <Box
          key={i}
          className="skeleton"
          sx={{
            height,
            width: `${60 + Math.random() * 40}%`,
            mb: 1.5,
            borderRadius: 1,
          }}
        />
      ))}
    </Box>
  )
}
