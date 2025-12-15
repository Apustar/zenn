/**
 * 主题工具函数
 */
import type { ThemeConfig } from '@/types/theme'

/**
 * 应用主题到DOM
 */
export function applyThemeToDOM(theme: ThemeConfig): void {
  if (typeof window === 'undefined') return
  
  const root = document.documentElement
  
  // 应用颜色变量
  root.style.setProperty('--primary-color', theme.colors.primary)
  if (theme.colors.secondary) {
    root.style.setProperty('--secondary-color', theme.colors.secondary)
  }
  root.style.setProperty('--text-color', theme.colors.text)
  root.style.setProperty('--text-secondary', theme.colors.textSecondary)
  root.style.setProperty('--bg-color', theme.colors.bg)
  root.style.setProperty('--card-bg', theme.colors.cardBg)
  root.style.setProperty('--border-color', theme.colors.border)
  root.style.setProperty('--header-bg', theme.colors.headerBg)
  root.style.setProperty('--footer-bg', theme.colors.footerBg)
  
  if (theme.colors.success) {
    root.style.setProperty('--success-color', theme.colors.success)
  }
  if (theme.colors.warning) {
    root.style.setProperty('--warning-color', theme.colors.warning)
  }
  if (theme.colors.error) {
    root.style.setProperty('--error-color', theme.colors.error)
  }
  if (theme.colors.info) {
    root.style.setProperty('--info-color', theme.colors.info)
  }
  
  // 应用布局变量
  root.style.setProperty('--container-max-width', theme.layout.containerMaxWidth)
  root.style.setProperty('--card-radius', theme.layout.cardRadius)
  root.style.setProperty('--button-radius', theme.layout.buttonRadius)
  root.style.setProperty('--input-radius', theme.layout.inputRadius)
  root.style.setProperty('--shadow', theme.layout.shadow)
  root.style.setProperty('--card-shadow', theme.layout.cardShadow)
  root.style.setProperty('--hover-shadow', theme.layout.hoverShadow)
  
  // 应用布局样式类
  root.classList.remove('menu-horizontal', 'menu-vertical', 'menu-centered', 'menu-minimal')
  root.classList.remove('header-default', 'header-minimal', 'header-glass', 'header-solid')
  root.classList.remove('post-card-card', 'post-card-list', 'post-card-magazine', 'post-card-minimal')
  root.classList.remove('post-centered', 'post-wide', 'post-narrow', 'post-magazine')
  root.classList.remove('content-single', 'content-two-column', 'content-three-column')
  
  if (theme.layout.menuStyle) {
    root.classList.add(`menu-${theme.layout.menuStyle}`)
  }
  if (theme.layout.headerStyle) {
    root.classList.add(`header-${theme.layout.headerStyle}`)
  }
  if (theme.layout.postCardLayout) {
    root.classList.add(`post-card-${theme.layout.postCardLayout}`)
  }
  if (theme.layout.postLayout) {
    root.classList.add(`post-${theme.layout.postLayout}`)
  }
  if (theme.layout.contentLayout) {
    root.classList.add(`content-${theme.layout.contentLayout}`)
  }
  
  // 应用字体变量
  root.style.setProperty('--font-family', theme.typography.fontFamily)
  if (theme.typography.headingFont) {
    root.style.setProperty('--heading-font', theme.typography.headingFont)
  }
  root.style.setProperty('--base-size', theme.typography.baseSize)
  root.style.setProperty('--line-height', theme.typography.lineHeight)
  
  // 应用背景
  if (theme.background.gradient) {
    root.style.setProperty('--bg-gradient', theme.background.gradient)
  }
  if (theme.background.image) {
    root.style.setProperty('--bg-image', `url(${theme.background.image})`)
    root.style.setProperty('--bg-strategy', theme.background.strategy)
  } else {
    root.style.removeProperty('--bg-image')
  }
  
  // 应用动画持续时间
  root.style.setProperty('--animation-duration', theme.animations.duration)
  
  // 应用主题类名
  root.classList.remove('theme-default', 'theme-dark', 'theme-minimal', 'theme-colorful')
  root.classList.add(`theme-${theme.id}`)
  
  // 应用动画类
  root.classList.remove('anim-fade', 'anim-slide', 'anim-zoom', 'anim-none')
  root.classList.add(`anim-${theme.animations.pageTransition}`)
}

/**
 * 应用鼠标样式
 */
export function applyCursorStyle(theme: ThemeConfig): void {
  if (typeof window === 'undefined') return
  
  const root = document.documentElement
  
  // 先清理旧的鼠标跟随效果
  if (root.classList.contains('cursor-follow-enabled')) {
    cleanupCursorFollow()
  }
  
  // 应用基础鼠标样式
  if (theme.cursor.custom) {
    root.style.setProperty('--cursor-default', theme.cursor.custom)
    root.style.setProperty('--cursor-pointer', theme.cursor.custom)
  } else {
    root.style.setProperty('--cursor-default', theme.cursor.default)
    root.style.setProperty('--cursor-pointer', theme.cursor.pointer)
  }
  root.style.setProperty('--cursor-text', theme.cursor.text)
  
  // 应用鼠标跟随效果
  if (theme.cursor.followEffect?.enabled) {
    root.classList.add('cursor-follow-enabled')
    root.setAttribute('data-cursor-type', theme.cursor.followEffect.type)
    if (theme.cursor.followEffect.color) {
      root.style.setProperty('--cursor-follow-color', theme.cursor.followEffect.color)
    }
    if (theme.cursor.followEffect.size) {
      root.style.setProperty('--cursor-follow-size', theme.cursor.followEffect.size)
    }
    // 延迟初始化，确保DOM已更新
    setTimeout(() => {
      initCursorFollow()
    }, 100)
  } else {
    root.classList.remove('cursor-follow-enabled')
    root.removeAttribute('data-cursor-type')
  }
}

/**
 * 鼠标跟随效果实例管理
 */
let cursorFollowInstance: {
  cleanup: () => void
} | null = null

/**
 * 清理鼠标跟随效果
 */
export function cleanupCursorFollow(): void {
  if (cursorFollowInstance) {
    cursorFollowInstance.cleanup()
    cursorFollowInstance = null
  }
  
  // 移除所有跟随元素
  const existingElements = document.querySelectorAll('.cursor-follow')
  existingElements.forEach(el => el.remove())
  
  // 移除类名
  document.documentElement.classList.remove('cursor-follow-enabled')
}

/**
 * 初始化鼠标跟随效果
 */
export function initCursorFollow(): void {
  if (typeof window === 'undefined') return
  
  // 先清理旧的实例
  cleanupCursorFollow()
  
  const root = document.documentElement
  if (!root.classList.contains('cursor-follow-enabled')) return
  
  let cursorElement: HTMLElement | null = null
  
  // 创建鼠标跟随元素
  const createCursorElement = () => {
    if (cursorElement) return cursorElement
    
    cursorElement = document.createElement('div')
    cursorElement.className = 'cursor-follow'
    document.body.appendChild(cursorElement)
    return cursorElement
  }
  
  const cursorType = root.getAttribute('data-cursor-type') || 'dot'
  
  // 根据类型设置样式
  const updateCursorStyle = () => {
    if (!cursorElement) return
    
    const size = getComputedStyle(root).getPropertyValue('--cursor-follow-size') || '8px'
    const color = getComputedStyle(root).getPropertyValue('--cursor-follow-color') || getComputedStyle(root).getPropertyValue('--primary-color') || '#FE9600'
    
    cursorElement.style.cssText = `
      position: fixed;
      pointer-events: none;
      z-index: 9999;
      transform: translate(-50%, -50%);
      transition: width 0.2s, height 0.2s, opacity 0.2s;
      opacity: 0;
    `
    
    switch (cursorType) {
      case 'circle':
        cursorElement.style.width = size
        cursorElement.style.height = size
        cursorElement.style.borderRadius = '50%'
        cursorElement.style.border = `2px solid ${color}`
        cursorElement.style.background = 'transparent'
        break
      case 'ring':
        cursorElement.style.width = '24px'
        cursorElement.style.height = '24px'
        cursorElement.style.borderRadius = '50%'
        cursorElement.style.border = `2px solid ${color}`
        cursorElement.style.background = 'transparent'
        break
      default:
        cursorElement.style.width = size
        cursorElement.style.height = size
        cursorElement.style.borderRadius = '50%'
        cursorElement.style.border = 'none'
        cursorElement.style.background = color
    }
  }
  
  let mouseX = 0
  let mouseY = 0
  let cursorX = 0
  let cursorY = 0
  let animationId: number | null = null
  
  // 鼠标移动事件
  const handleMouseMove = (e: MouseEvent) => {
    mouseX = e.clientX
    mouseY = e.clientY
    
    if (!cursorElement) {
      createCursorElement()
      updateCursorStyle()
    }
    
    if (cursorElement) {
      cursorElement.style.opacity = '1'
    }
  }
  
  // 鼠标离开窗口
  const handleMouseLeave = () => {
    if (cursorElement) {
      cursorElement.style.opacity = '0'
    }
  }
  
  // 鼠标进入可点击元素
  const handleMouseEnter = (e: MouseEvent) => {
    const target = e.target as HTMLElement
    if ((target.tagName === 'A' || target.tagName === 'BUTTON' || target.getAttribute('role') === 'button') && cursorElement && cursorType === 'ring') {
      cursorElement.style.width = '40px'
      cursorElement.style.height = '40px'
    }
  }
  
  // 鼠标离开可点击元素
  const handleMouseLeaveElement = () => {
    if (cursorElement && cursorType === 'ring') {
      cursorElement.style.width = '24px'
      cursorElement.style.height = '24px'
    }
  }
  
  // 动画循环
  const animate = () => {
    cursorX += (mouseX - cursorX) * 0.1
    cursorY += (mouseY - cursorY) * 0.1
    
    if (cursorElement) {
      cursorElement.style.left = `${cursorX}px`
      cursorElement.style.top = `${cursorY}px`
    }
    
    animationId = requestAnimationFrame(animate)
  }
  
  // 绑定事件
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseleave', handleMouseLeave)
  document.addEventListener('mouseenter', handleMouseEnter, true)
  document.addEventListener('mouseleave', handleMouseLeaveElement, true)
  
  // 启动动画
  animate()
  
  // 保存清理函数
  cursorFollowInstance = {
    cleanup: () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseleave', handleMouseLeave)
      document.removeEventListener('mouseenter', handleMouseEnter, true)
      document.removeEventListener('mouseleave', handleMouseLeaveElement, true)
      if (animationId !== null) {
        cancelAnimationFrame(animationId)
      }
      if (cursorElement) {
        cursorElement.remove()
        cursorElement = null
      }
    }
  }
}

