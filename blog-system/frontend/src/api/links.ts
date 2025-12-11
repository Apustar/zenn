import api from './index'

export interface Link {
  id: number
  name: string
  url: string
  description?: string
  logo?: string
  category?: number
  order: number
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
    const response = await api.get<LinkCategoryListResponse>('/link-categories/')
    // 处理分页响应，返回 results 数组
    if (response && typeof response === 'object' && 'results' in response) {
      return response.results || []
    }
    // 如果不是分页格式，直接返回数组
    return Array.isArray(response) ? response : []
  },

  // 获取友链列表
  getLinks: async (): Promise<Link[]> => {
    return api.get<Link[]>('/links/')
  },
}

