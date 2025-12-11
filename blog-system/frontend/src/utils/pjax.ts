import type { Router } from 'vue-router'

export class Pjax {
  private router: Router
  private container: string
  private isTransitioning = false

  constructor(router: Router, container: string = 'main') {
    this.router = router
    this.container = container
    this.init()
  }

  private init() {
    // 拦截所有链接点击
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement
      const link = target.closest('a')
      
      if (!link) return
      
      const href = link.getAttribute('href')
      if (!href || href.startsWith('#') || href.startsWith('javascript:')) return
      
      // 外部链接或特殊链接不拦截
      if (link.target === '_blank' || link.hasAttribute('download')) return
      
      // 检查是否是同域链接
      try {
        const url = new URL(href, window.location.origin)
        if (url.origin !== window.location.origin) return
      } catch {
        // 相对路径
      }
      
      e.preventDefault()
      this.navigate(href)
    })
  }

  async navigate(path: string) {
    if (this.isTransitioning) return
    
    this.isTransitioning = true
    
    try {
      // 添加加载状态
      const container = document.querySelector(this.container)
      if (container) {
        container.classList.add('pjax-loading')
      }
      
      // 使用 Vue Router 导航
      await this.router.push(path)
      
      // 滚动到顶部
      window.scrollTo({ top: 0, behavior: 'smooth' })
      
      // 触发自定义事件
      window.dispatchEvent(new CustomEvent('pjax:complete', { detail: { path } }))
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('Pjax navigation failed:', error)
      }
    } finally {
      this.isTransitioning = false
      const container = document.querySelector(this.container)
      if (container) {
        container.classList.remove('pjax-loading')
      }
    }
  }
}

