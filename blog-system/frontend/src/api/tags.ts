import api from './index'

export interface Tag {
  id: number
  name: string
  slug: string
  description?: string
  color: string
  post_count: number
  created_at: string
}

export const tagsApi = {
  // 获取标签列表
  getTags: async (): Promise<Tag[]> => {
    return api.get<Tag[]>('/tags/')
  },

  // 获取标签详情
  getTag: async (slug: string): Promise<Tag> => {
    return api.get<Tag>(`/tags/${slug}/`)
  },

  // 创建标签
  createTag: async (data: Partial<Tag>): Promise<Tag> => {
    return api.post<Tag>('/tags/', data)
  },

  // 更新标签
  updateTag: async (slug: string, data: Partial<Tag>): Promise<Tag> => {
    return api.patch<Tag>(`/tags/${slug}/`, data)
  },

  // 删除标签
  deleteTag: async (slug: string): Promise<void> => {
    return api.delete(`/tags/${slug}/`)
  },
}

