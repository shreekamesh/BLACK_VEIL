import React from 'react'
import { IconButton, Tooltip } from '@mui/material'
import { DarkMode, LightMode } from '@mui/icons-material'
import { useTheme } from '@/hooks/useTheme'

export const ThemeToggle: React.FC = () => {
  const { mode, toggleTheme } = useTheme()

  return (
    <Tooltip title={mode === 'dark' ? 'Light Mode' : 'Dark Mode'}>
      <IconButton onClick={toggleTheme} color="inherit">
        {mode === 'dark' ? <LightMode /> : <DarkMode />}
      </IconButton>
    </Tooltip>
  )
}
