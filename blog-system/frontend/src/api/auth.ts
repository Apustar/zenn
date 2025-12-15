import api from './index'
import axios from 'axios'

export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthResponse {
  access: string
  refresh: string
}

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  avatar?: string
  bio?: string
  website?: string
  is_staff?: boolean
  is_superuser?: boolean
  date_joined: string
}

export const authApi = {
  // 登录
  login: async (credentials: LoginCredentials) => {
    try {
      const response = await axios.post<AuthResponse>('/api/auth/login/', credentials)
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      return response.data
    } catch (error: any) {
      // 重新抛出错误，让调用者可以处理
      throw error
    }
  },

  // 登出
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  // 获取当前用户
  getCurrentUser: async (): Promise<User> => {
    return api.get<User>('/users/me/')
  },

  // 刷新 Token
  refreshToken: (refresh: string) => {
    return axios.post<AuthResponse>('/api/auth/refresh/', { refresh })
  },
}

