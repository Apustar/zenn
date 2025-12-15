import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { ThemeConfig } from '@/types/theme'
import { themes, getThemeById, getDefaultTheme } from '@/themes'
import { applyThemeToDOM, applyCursorStyle, initCursorFollow } from '@/utils/theme'

export const useThemeStore = defineStore('theme', () => {
  const getInitialTheme = (): string => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') || 'default'
    }
    return 'default'
  }
  
  const currentThemeId = ref<string>(getInitialTheme())
  const currentTheme = ref<ThemeConfig>(getThemeById(getInitialTheme()) || getDefaultTheme())
  
  /**
   * 设置主题
   */
  const setTheme = (themeId: string) => {
    const theme = getThemeById(themeId)
    if (!theme) {
      console.warn(`Theme ${themeId} not found, using default theme`)
      return
    }
    
    currentThemeId.value = themeId
    currentTheme.value = theme
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', themeId)
    }
    
    applyTheme()
  }
  
  /**
   * 应用主题
   */
  const applyTheme = () => {
    if (typeof window === 'undefined') return
    
    try {
      // 应用主题样式
      applyThemeToDOM(currentTheme.value)
      
      // 应用鼠标样式
      applyCursorStyle(currentTheme.value)
      
      // 初始化鼠标跟随效果
      if (currentTheme.value.cursor.followEffect?.enabled) {
        initCursorFollow()
      }
    } catch (e) {
      if (import.meta.env.DEV) {
        console.warn('Theme apply failed:', e)
      }
    }
  }
  
  /**
   * 获取所有可用主题
   */
  const getAvailableThemes = (): ThemeConfig[] => {
    return Object.values(themes)
  }
  
  /**
   * 获取当前主题
   */
  const getCurrentTheme = (): ThemeConfig => {
    return currentTheme.value
  }
  
  // 监听主题变化
  watch(currentThemeId, () => {
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
    currentThemeId,
    currentTheme,
    setTheme,
    applyTheme,
    getAvailableThemes,
    getCurrentTheme,
  }
})
