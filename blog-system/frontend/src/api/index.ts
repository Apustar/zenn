import axios from 'axios'
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios'

// 最大重试次数
const MAX_RETRIES = 2
// 重试延迟（毫秒）
const RETRY_DELAY = 1000

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true, // 允许发送cookies（用于session）
  headers: {
    'Content-Type': 'application/json',
  },
}) as AxiosInstance & {
  get<T = any>(url: string, config?: any): Promise<T>
  post<T = any>(url: string, data?: any, config?: any): Promise<T>
  put<T = any>(url: string, data?: any, config?: any): Promise<T>
  patch<T = any>(url: string, data?: any, config?: any): Promise<T>
  delete<T = any>(url: string, config?: any): Promise<T>
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加请求时间戳，用于防止缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 延迟函数
const delay = (ms: number): Promise<void> => new Promise(resolve => setTimeout(resolve, ms))

// 判断是否应该重试的错误
const shouldRetry = (error: AxiosError): boolean => {
  const code = error.code
  const status = error.response?.status
  
  // 网络错误或5xx服务器错误可以重试
  return (
    code === 'ECONNABORTED' || // 请求超时
    code === 'ENETDOWN' ||     // 网络断开
    code === 'ENETUNREACH' ||  // 网络不可达
    code === 'ECONNRESET' ||   // 连接重置
    status === 500 ||          // 服务器内部错误
    status === 502 ||          // 网关错误
    status === 503 ||          // 服务不可用
    status === 504             // 网关超时
  )
}

// 响应拦截器 - 返回 data 部分
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data as any
  },
  async (error: AxiosError) => {
    const config = error.config as any
    
    // 如果配置中没有重试次数，初始化为0
    if (!config._retryCount) {
      config._retryCount = 0
    }
    
    // 处理401未授权
    if (error.response?.status === 401 && !config._isRefreshing) {
      config._isRefreshing = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post('/api/auth/refresh/', {
            refresh: refreshToken,
          })
          localStorage.setItem('access_token', response.data.access)
          config.headers.Authorization = `Bearer ${response.data.access}`
          config._isRefreshing = false
          return api.request(config)
        } catch (refreshError) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          config._isRefreshing = false
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // 没有刷新token，直接跳转登录
        window.location.href = '/login'
      }
    }
    
    // 处理可重试的错误
    if (shouldRetry(error) && config._retryCount < MAX_RETRIES) {
      config._retryCount += 1
      await delay(RETRY_DELAY * config._retryCount) // 指数退避
      return api.request(config)
    }
    
    return Promise.reject(error)
  }
)

export default api

