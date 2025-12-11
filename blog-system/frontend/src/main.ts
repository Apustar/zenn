import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import i18n from './i18n'
import './styles/main.css'
import App from './App.vue'

// 全局错误处理
const errorHandler = (err: unknown, instance: any, info: string) => {
  if (import.meta.env.DEV) {
    console.error('Vue Error:', err)
    console.error('Component:', instance)
    console.error('Info:', info)
  }
}

try {
  const app = createApp(App)
  const pinia = createPinia()

  app.config.errorHandler = errorHandler

  app.use(pinia)
  app.use(router)
  app.use(i18n)

  app.mount('#app')
} catch (error) {
  if (import.meta.env.DEV) {
    console.error('Failed to initialize app:', error)
  }
  // 显示错误信息
  const appElement = document.getElementById('app')
  if (appElement) {
    appElement.innerHTML = `
      <div style="padding: 40px; text-align: center; color: black; background: white;">
        <h1 style="color: red;">应用初始化失败</h1>
        <p>请查看浏览器控制台获取详细错误信息</p>
        <pre style="text-align: left; background: #f5f5f5; padding: 20px; border-radius: 4px; margin-top: 20px; overflow: auto;">${String(error)}</pre>
      </div>
    `
  }
}
