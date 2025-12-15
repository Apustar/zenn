/**
 * 主题系统 - 主题注册中心
 */
import type { ThemeConfig } from '@/types/theme'
import { defaultTheme } from './default'
import { darkTheme } from './dark'
import { minimalTheme } from './minimal'
import { colorfulTheme } from './colorful'

/**
 * 所有可用主题
 */
export const themes: Record<string, ThemeConfig> = {
  default: defaultTheme,
  dark: darkTheme,
  minimal: minimalTheme,
  colorful: colorfulTheme,
}

/**
 * 获取主题列表
 */
export function getThemeList(): ThemeConfig[] {
  return Object.values(themes)
}

/**
 * 根据ID获取主题
 */
export function getThemeById(id: string): ThemeConfig | null {
  return themes[id] || null
}

/**
 * 获取默认主题
 */
export function getDefaultTheme(): ThemeConfig {
  return defaultTheme
}

