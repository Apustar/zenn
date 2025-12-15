/**
 * 通用错误处理和加载状态管理
 */
import { ref, computed } from 'vue'

export interface LoadingState {
  loading: boolean
  error: string | null
}

export function useAsyncState<T = any>() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const data = ref<T | null>(null)

  const isLoading = computed(() => loading.value)
  const hasError = computed(() => !!error.value)
  const hasData = computed(() => data.value !== null)

  const execute = async (asyncFn: () => Promise<T>): Promise<T | null> => {
    loading.value = true
    error.value = null
    
    try {
      const result = await asyncFn()
      data.value = result
      return result
    } catch (err: any) {
      error.value = err.message || '操作失败'
      if (import.meta.env.DEV) {
        console.error('Async operation failed:', err)
      }
      return null
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    loading.value = false
    error.value = null
    data.value = null
  }

  return {
    loading: isLoading,
    error: hasError,
    data,
    hasData,
    execute,
    reset
  }
}

/**
 * 通用API错误处理
 */
export class APIError extends Error {
  constructor(
    message: string,
    public code?: number,
    public details?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

/**
 * 安全的异步操作包装器
 */
export async function safeAsync<T>(
  asyncFn: () => Promise<T>,
  errorHandler?: (error: any) => void
): Promise<[T | null, any | null]> {
  try {
    const result = await asyncFn()
    return [result, null]
  } catch (error) {
    if (errorHandler) {
      errorHandler(error)
    } else if (import.meta.env.DEV) {
      console.error('Safe async failed:', error)
    }
    return [null, error]
  }
}

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout)
    }
    
    timeout = setTimeout(() => {
      func(...args)
    }, wait)
  }
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}