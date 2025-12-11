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
}

