import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type User } from '@/api/auth'

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
    try {
      await authApi.login({ username, password })
      token.value = localStorage.getItem('access_token')
      await fetchUser()
      return true
    } catch (error: any) {
      if (import.meta.env.DEV) {
        console.error('Login failed:', error)
      }
      throw error
    }
  }

  const logout = () => {
    authApi.logout()
    user.value = null
    token.value = null
  }

  const fetchUser = async () => {
    try {
      if (token.value) {
        const result = await authApi.getCurrentUser()
        user.value = result || null
      }
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('Fetch user failed:', error)
      }
      logout()
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
