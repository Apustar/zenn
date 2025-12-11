import { createI18n } from 'vue-i18n'
import zhCN from '../locales/zh-CN.json'
import enUS from '../locales/en-US.json'

const messages = {
  'zh-CN': zhCN,
  'en-US': enUS,
}

// 从 localStorage 获取语言设置，默认为浏览器语言
const getLocale = (): string => {
  if (typeof window === 'undefined') return 'zh-CN'
  
  try {
    const saved = localStorage.getItem('locale')
    if (saved && (saved === 'zh-CN' || saved === 'en-US')) return saved
  } catch {
    // localStorage 不可用时忽略
  }
  
  try {
    const browserLang = navigator.language || (navigator as any).userLanguage
    if (browserLang.startsWith('zh')) return 'zh-CN'
    return 'en-US'
  } catch {
    return 'zh-CN'
  }
}

let i18nInstance: ReturnType<typeof createI18n>

try {
  i18nInstance = createI18n({
    legacy: false,
    locale: getLocale(),
    fallbackLocale: 'zh-CN',
    messages,
    silentTranslationWarn: true,
    silentFallbackWarn: true,
  })
} catch {
  // 创建基本的 i18n 实例作为后备
  i18nInstance = createI18n({
    legacy: false,
    locale: 'zh-CN',
    fallbackLocale: 'zh-CN',
    messages: { 'zh-CN': {}, 'en-US': {} },
    silentTranslationWarn: true,
    silentFallbackWarn: true,
  })
}

export const i18n = i18nInstance
export default i18n
