import api from './index'
import axios from 'axios'

export interface SiteSettings {
  site_name: string
  site_description?: string
  site_keywords?: string
  site_icon?: string
  site_icon_url?: string
  about_content?: string
  about_content_html?: string
  updated_at: string
}

export interface NavigationItem {
  id: number
  name: string
  url: string
  is_builtin: boolean
  is_visible: boolean
  is_accessible: boolean
  order: number
}

export const settingsApi = {
  // 获取站点设置
  getSettings: async (): Promise<SiteSettings> => {
    return api.get<SiteSettings>('/settings/')
  },

  // 更新站点设置（需要管理员权限）
  // 如果包含文件，会自动使用 FormData
  updateSettings: async (data: Partial<SiteSettings> & { site_icon?: File }): Promise<SiteSettings> => {
    const token = localStorage.getItem('access_token')
    const headers: Record<string, string> = {
      Authorization: token ? `Bearer ${token}` : '',
    }

    // 如果包含文件，使用 FormData
    if (data.site_icon instanceof File) {
      const formData = new FormData()
      if (data.site_name) formData.append('site_name', data.site_name)
      if (data.site_description) formData.append('site_description', data.site_description)
      if (data.site_keywords) formData.append('site_keywords', data.site_keywords)
      formData.append('site_icon', data.site_icon)
      
      const response = await axios.patch<SiteSettings>('/api/settings/1/', formData, { headers })
      return response.data
    } else {
      // 普通 JSON 数据
      return api.patch<SiteSettings>('/settings/1/', data)
    }
  },
}

export const navigationApi = {
  // 获取导航菜单列表（只返回可见的）
  getNavigationItems: async (): Promise<NavigationItem[]> => {
    return api.get<NavigationItem[]>('/navigation/')
  },

  // 创建导航菜单（需要管理员权限）
  createNavigationItem: async (data: {
    name: string
    url: string
    is_visible?: boolean
    order?: number
  }): Promise<NavigationItem> => {
    return api.post<NavigationItem>('/navigation/', data)
  },

  // 更新导航菜单（需要管理员权限）
  updateNavigationItem: async (id: number, data: Partial<NavigationItem>): Promise<NavigationItem> => {
    return api.patch<NavigationItem>(`/navigation/${id}/`, data)
  },

  // 删除导航菜单（需要管理员权限）
  deleteNavigationItem: async (id: number): Promise<void> => {
    return api.delete(`/navigation/${id}/`)
  },

  // 检查URL是否可以访问
  checkUrlAccess: async (url: string): Promise<{ url: string; accessible: boolean }> => {
    return api.get<{ url: string; accessible: boolean }>('/navigation/check_access/', {
      params: { url }
    })
  },
}
