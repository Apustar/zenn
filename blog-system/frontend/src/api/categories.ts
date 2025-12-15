import api from './index'

export interface Category {
  id: number
  name: string
  slug: string
  description?: string
  cover?: string
  parent?: number
  order: number
  post_count: number
  children?: Category[]
  created_at: string
}

export const categoriesApi = {
  // 获取分类列表
  getCategories: async (): Promise<Category[]> => {
    return api.get<Category[]>('/categories/')
  },

  // 获取分类详情
  getCategory: async (slug: string): Promise<Category> => {
    return api.get<Category>(`/categories/${slug}/`)
  },

  // 创建分类
  createCategory: async (data: Partial<Category>): Promise<Category> => {
    return api.post<Category>('/categories/', data)
  },

  // 更新分类
  updateCategory: async (slug: string, data: Partial<Category>): Promise<Category> => {
    return api.patch<Category>(`/categories/${slug}/`, data)
  },

  // 删除分类
  deleteCategory: async (slug: string): Promise<void> => {
    return api.delete(`/categories/${slug}/`)
  },
}

