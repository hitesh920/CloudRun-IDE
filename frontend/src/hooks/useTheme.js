/**
 * Custom React hook for theme management
 */

import { useState, useEffect } from 'react'

function getStoredTheme() {
  try {
    return localStorage.getItem('cloudrun-theme') || 'dark'
  } catch {
    return 'dark'
  }
}

function storeTheme(theme) {
  try {
    localStorage.setItem('cloudrun-theme', theme)
  } catch {
    // localStorage not available, ignore
  }
}

export function useTheme() {
  const [theme, setTheme] = useState(getStoredTheme)

  useEffect(() => {
    document.documentElement.classList.remove('light', 'dark')
    document.documentElement.classList.add(theme)
    storeTheme(theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark')
  }

  return {
    theme,
    toggleTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
  }
}
