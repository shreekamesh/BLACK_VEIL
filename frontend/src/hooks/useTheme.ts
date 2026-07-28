import { useState, useCallback, useEffect } from 'react'
import { config } from '@/config'

type ThemeMode = 'dark' | 'light'

export function useTheme() {
  const [mode, setMode] = useState<ThemeMode>(
    () => (localStorage.getItem('themeMode') as ThemeMode) || (config.theme.darkMode ? 'dark' : 'light'),
  )

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', mode)
    localStorage.setItem('themeMode', mode)
  }, [mode])

  const toggleTheme = useCallback(() => {
    setMode((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }, [])

  const setTheme = useCallback((newMode: ThemeMode) => {
    setMode(newMode)
  }, [])

  return {
    mode,
    isDark: mode === 'dark',
    toggleTheme,
    setTheme,
  }
}

