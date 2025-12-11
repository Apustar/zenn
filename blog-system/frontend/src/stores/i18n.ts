import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import i18n from '@/i18n'

export const useI18nStore = defineStore('i18n', () => {
  const getInitialLocale = (): 'zh-CN' | 'en-US' => {
    try {
      const locale = (i18n.global.locale as any).value
      if (locale === 'zh-CN' || locale === 'en-US') {
        return locale
      }
    } catch {
      // ignore
    }
    return 'zh-CN'
  }
  
  const currentLocale = ref<'zh-CN' | 'en-US'>(getInitialLocale())

  const setLocale = (lang: 'zh-CN' | 'en-US') => {
    try {
      (i18n.global.locale as any).value = lang
    } catch {
      // ignore
    }
    currentLocale.value = lang
    if (typeof window !== 'undefined') {
      localStorage.setItem('locale', lang)
      document.documentElement.lang = lang
    }
  }

  const toggleLocale = () => {
    const newLocale = currentLocale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
    setLocale(newLocale)
  }

  // 监听语言变化
  watch(currentLocale, (newLocale) => {
    if (typeof window !== 'undefined') {
      document.documentElement.lang = newLocale
    }
  })

  // 初始化时设置 HTML lang 属性
  if (typeof window !== 'undefined') {
    document.documentElement.lang = currentLocale.value
  }

  return {
    currentLocale,
    setLocale,
    toggleLocale,
  }
})

