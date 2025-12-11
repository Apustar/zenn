import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export interface Theme {
  name: string
  bgUrl?: string
  bgStrategy: 'none' | 'no-repeat' | 'repeat' | 'cover'
  icon: string
  isDark: boolean
}

export const useThemeStore = defineStore('theme', () => {
  const getInitialTheme = (): string => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') || 'sakura'
    }
    return 'sakura'
  }
  
  const getInitialIsDark = (): boolean => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('isDark') === 'true'
    }
    return false
  }
  
  const currentTheme = ref<string>(getInitialTheme())
  const isDark = ref<boolean>(getInitialIsDark())

  const themes: Record<string, Theme> = {
    white: {
      name: 'white',
      bgStrategy: 'none',
      icon: 'mdi:white-balance-sunny',
      isDark: false,
    },
    sakura: {
      name: 'sakura',
      bgUrl: '/themes/sakura.png',
      bgStrategy: 'none',
      icon: 'mdi:flower',
      isDark: false,
    },
    dark: {
      name: 'dark',
      bgStrategy: 'cover',
      icon: 'mdi:weather-night',
      isDark: true,
    },
  }

  const setTheme = (themeName: string) => {
    currentTheme.value = themeName
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', themeName)
    }
    applyTheme()
  }

  const toggleDark = () => {
    isDark.value = !isDark.value
    if (typeof window !== 'undefined') {
      localStorage.setItem('isDark', String(isDark.value))
    }
    applyTheme()
  }

  const applyTheme = () => {
    if (typeof window === 'undefined') return
    
    const theme = themes[currentTheme.value] || themes.sakura
    if (!theme) return
    
    const root = document.documentElement

    try {
      if (theme.bgUrl) {
        root.style.setProperty('--theme-bg-url', `url(${theme.bgUrl})`)
        root.style.setProperty('--theme-bg-strategy', theme.bgStrategy)
      } else {
        root.style.removeProperty('--theme-bg-url')
      }

      if (theme.isDark || isDark.value) {
        root.classList.add('dark')
      } else {
        root.classList.remove('dark')
      }
    } catch (e) {
      if (import.meta.env.DEV) {
        console.warn('Theme apply failed:', e)
      }
    }
  }

  // 监听主题变化
  watch([currentTheme, isDark], () => {
    if (typeof window !== 'undefined') {
      applyTheme()
    }
  })

  // 初始化应用主题（延迟执行，确保 DOM 已加载）
  if (typeof window !== 'undefined') {
    setTimeout(() => {
      applyTheme()
    }, 100)
  }

  return {
    currentTheme,
    isDark,
    themes,
    setTheme,
    toggleDark,
    applyTheme,
  }
})
