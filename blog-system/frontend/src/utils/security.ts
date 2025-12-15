/**
 * 前端安全工具函数
 */

/**
 * 转义HTML内容，防止XSS攻击
 */
export function escapeHtml(text: string): string {
  if (!text) return ''
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

/**
 * 验证URL是否安全
 */
export function isValidUrl(url: string): boolean {
  if (!url) return false
  
  try {
    const urlObj = new URL(url)
    // 只允许http和https协议
    return ['http:', 'https:'].includes(urlObj.protocol)
  } catch {
    return false
  }
}

/**
 * 清理用户输入，移除潜在的恶意内容
 */
export function sanitizeInput(input: string): string {
  if (!input) return ''
  
  // 移除潜在的脚本标签和事件处理器
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi, '')
    .replace(/<embed\b[^<]*>/gi, '')
    .replace(/<link\b[^<]*>/gi, '')
    .replace(/<meta\b[^<]*>/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/vbscript:/gi, '')
    .replace(/data:(?!image\/)/gi, '') // 允许data:image/，但阻止其他data:协议
    .replace(/expression\s*\(/gi, '')
    .replace(/@import/gi, '')
    .replace(/binding\s*:/gi, '')
    .trim()
}

/**
 * 验证密码强度
 */
export function validatePasswordStrength(password: string): {
  isValid: boolean
  errors: string[]
} {
  const errors: string[] = []
  
  if (!password) {
    errors.push('密码不能为空')
    return { isValid: false, errors }
  }
  
  if (password.length < 8) {
    errors.push('密码长度至少8位')
  }
  
  if (!/\d/.test(password)) {
    errors.push('密码必须包含至少一个数字')
  }
  
  if (!/[a-zA-Z]/.test(password)) {
    errors.push('密码必须包含至少一个字母')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * 安全的JSON解析
 */
export function safeJsonParse<T>(jsonString: string, fallback: T): T {
  try {
    return JSON.parse(jsonString)
  } catch {
    return fallback
  }
}

/**
 * 检查是否为安全的重定向URL
 */
export function isSafeRedirectUrl(url: string): boolean {
  if (!url) return false
  
  // 允许相对路径
  if (url.startsWith('/') && !url.startsWith('//')) {
    return true
  }
  
  // 检查是否为同源URL
  try {
    const currentOrigin = window.location.origin
    const urlObj = new URL(url, currentOrigin)
    return urlObj.origin === currentOrigin
  } catch {
    return false
  }
}

/**
 * 生成安全的随机字符串
 */
export function generateSecureRandomString(length: number = 32): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  
  if (window.crypto && window.crypto.getRandomValues) {
    const randomValues = new Uint32Array(length)
    window.crypto.getRandomValues(randomValues)
    
    for (let i = 0; i < length; i++) {
      result += chars[randomValues[i] % chars.length]
    }
  } else {
    // 降级方案（不推荐在生产环境使用）
    for (let i = 0; i < length; i++) {
      result += chars[Math.floor(Math.random() * chars.length)]
    }
  }
  
  return result
}

/**
 * 内容安全策略检查
 */
export class CSPValidator {
  private static allowedDomains: string[] = []
  private static allowedSchemes: string[] = ['http:', 'https:', 'data:', 'mailto:', 'tel:']
  
  static setAllowedDomains(domains: string[]) {
    this.allowedDomains = domains
  }
  
  static setAllowedSchemes(schemes: string[]) {
    this.allowedSchemes = schemes
  }
  
  static isAllowedDomain(url: string): boolean {
    if (!url) return false
    
    try {
      const urlObj = new URL(url)
      return this.allowedDomains.some(domain => 
        urlObj.hostname === domain || urlObj.hostname.endsWith(`.${domain}`)
      )
    } catch {
      return false
    }
  }
  
  static isAllowedScheme(url: string): boolean {
    if (!url) return false
    
    try {
      const urlObj = new URL(url)
      return this.allowedSchemes.includes(urlObj.protocol)
    } catch {
      return false
    }
  }
  
  static validateUrl(url: string): { isValid: boolean; reason?: string } {
    if (!url) {
      return { isValid: false, reason: 'URL不能为空' }
    }
    
    // 检查协议
    if (!this.isAllowedScheme(url)) {
      return { isValid: false, reason: '不允许的协议' }
    }
    
    // 检查域名
    if (url.startsWith('http') && !this.isAllowedDomain(url)) {
      return { isValid: false, reason: '不允许的域名' }
    }
    
    return { isValid: true }
  }
  
  /**
   * 清理HTML属性，确保符合CSP
   */
  static sanitizeAttributes(element: Element): void {
    // 移除危险的事件处理器
    const attributes = element.attributes
    const toRemove: string[] = []
    
    for (let i = 0; i < attributes.length; i++) {
      const attr = attributes[i]
      // 移除所有事件处理器
      if (attr.name.startsWith('on')) {
        toRemove.push(attr.name)
      }
      // 移除危险的样式
      if (attr.name === 'style' && attr.value.includes('expression')) {
        toRemove.push(attr.name)
      }
    }
    
    toRemove.forEach(attr => element.removeAttribute(attr))
  }
}

/**
 * 防止点击劫持
 */
export function preventClickjacking(): void {
  if (window.top !== window.self) {
    try {
      window.top.location = window.location
    } catch {
      // 如果无法访问父窗口，则关闭当前窗口
      window.close()
    }
  }
}

/**
 * 安全的本地存储操作
 */
export const secureStorage = {
  set(key: string, value: any): boolean {
    try {
      const serialized = JSON.stringify(value)
      localStorage.setItem(key, serialized)
      return true
    } catch {
      return false
    }
  },
  
  get<T>(key: string, fallback: T): T {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : fallback
    } catch {
      return fallback
    }
  },
  
  remove(key: string): boolean {
    try {
      localStorage.removeItem(key)
      return true
    } catch {
      return false
    }
  },
  
  clear(): boolean {
    try {
      localStorage.clear()
      return true
    } catch {
      return false
    }
  }
}

/**
 * 输入验证器
 */
export class InputValidator {
  static validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }
  
  static validateUsername(username: string): boolean {
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
    return usernameRegex.test(username)
  }
  
  static validateComment(content: string): { isValid: boolean; error?: string } {
    if (!content || !content.trim()) {
      return { isValid: false, error: '评论内容不能为空' }
    }
    
    if (content.length > 1000) {
      return { isValid: false, error: '评论内容不能超过1000字符' }
    }
    
    return { isValid: true }
  }
  
  static validatePostTitle(title: string): { isValid: boolean; error?: string } {
    if (!title || !title.trim()) {
      return { isValid: false, error: '文章标题不能为空' }
    }
    
    if (title.length > 200) {
      return { isValid: false, error: '文章标题不能超过200字符' }
    }
    
    return { isValid: true }
  }
}