import api from './index'

export interface Link {
  id: number
  name: string
  url: string
  description?: string
  logo?: string
  category?: number
  order: number
  is_visible?: boolean
  created_at: string
}

export interface LinkCategory {
  id: number
  name: string
  order: number
  links: Link[]
  created_at: string
}

export interface LinkCategoryListResponse {
  count: number
  next: string | null
  previous: string | null
  results: LinkCategory[]
}

export const linksApi = {
  // 获取友链分类列表
  getLinkCategories: async (): Promise<LinkCategory[]> => {
    const response = await api.get<LinkCategoryListResponse | LinkCategory[]>('/link-categories/')
    // 处理分页响应，返回 results 数组
    if (response && typeof response === 'object' && 'results' in response) {
      return response.results || []
    }
    // 如果不是分页格式，直接返回数组
    return Array.isArray(response) ? response : []
  },

  // 创建友链分类
  createLinkCategory: async (data: {
    name: string
    order?: number
  }): Promise<LinkCategory> => {
    return api.post<LinkCategory>('/link-categories/', data)
  },

  // 更新友链分类
  updateLinkCategory: async (id: number, data: Partial<LinkCategory>): Promise<LinkCategory> => {
    return api.patch<LinkCategory>(`/link-categories/${id}/`, data)
  },

  // 删除友链分类
  deleteLinkCategory: async (id: number): Promise<void> => {
    return api.delete(`/link-categories/${id}/`)
  },

  // 获取友链列表
  getLinks: async (): Promise<Link[]> => {
    return api.get<Link[]>('/links/')
  },

  // 创建友链
  createLink: async (data: FormData | {
    name: string
    url: string
    description?: string
    logo?: File
    category?: number
    order?: number
    is_visible?: boolean
  }): Promise<Link> => {
    if (data instanceof FormData) {
      return api.post<Link>('/links/', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    } else {
      const formData = new FormData()
      formData.append('name', data.name)
      formData.append('url', data.url)
      if (data.description) formData.append('description', data.description)
      if (data.logo instanceof File) formData.append('logo', data.logo)
      if (data.category) formData.append('category', data.category.toString())
      if (data.order !== undefined) formData.append('order', data.order.toString())
      if (data.is_visible !== undefined) formData.append('is_visible', data.is_visible.toString())
      return api.post<Link>('/links/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    }
  },

  // 更新友链
  updateLink: async (id: number, data: FormData | Partial<{
    name: string
    url: string
    description: string
    logo: File
    category: number
    order: number
    is_visible: boolean
  }>): Promise<Link> => {
    if (data instanceof FormData) {
      return api.patch<Link>(`/links/${id}/`, data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    } else {
      const formData = new FormData()
      if (data.name) formData.append('name', data.name)
      if (data.url) formData.append('url', data.url)
      if (data.description !== undefined) formData.append('description', data.description)
      if (data.logo instanceof File) formData.append('logo', data.logo)
      if (data.category !== undefined) formData.append('category', data.category?.toString() || '')
      if (data.order !== undefined) formData.append('order', data.order.toString())
      if (data.is_visible !== undefined) formData.append('is_visible', data.is_visible.toString())
      return api.patch<Link>(`/links/${id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    }
  },

  // 删除友链
  deleteLink: async (id: number): Promise<void> => {
    return api.delete(`/links/${id}/`)
  },
}

