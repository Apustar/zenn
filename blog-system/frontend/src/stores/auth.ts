import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type User } from '@/api/auth'
import { safeAsync } from '@/utils/async'

export const useAuthStore = defineStore('auth', () => {
  const getInitialToken = (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token')
    }
    return null
  }
  
  const user = ref<User | null>(null)
  const token = ref<string | null>(getInitialToken())

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = async (username: string, password: string) => {
    const [result, error] = await safeAsync(async () => {
      await authApi.login({ username, password })
      token.value = localStorage.getItem('access_token')
      await fetchUser()
      return true
    })
    
    if (error) {
      throw error
    }
    return result
  }

  const logout = () => {
    authApi.logout()
    user.value = null
    token.value = null
  }

  const fetchUser = async () => {
    if (!token.value) return
    
    const [result, error] = await safeAsync(async () => {
      return await authApi.getCurrentUser()
    })
    
    if (error) {
      logout()
    } else {
      user.value = result || null
    }
  }

  // 初始化时获取用户信息（延迟执行，避免阻塞渲染）
  if (token.value && typeof window !== 'undefined') {
    setTimeout(() => {
      fetchUser()
    }, 200)
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    fetchUser,
  }
})
