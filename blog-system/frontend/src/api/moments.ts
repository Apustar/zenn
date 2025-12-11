import api from './index'

export interface Moment {
  id: number
  content: string
  author: {
    id: number
    username: string
    avatar?: string
  }
  images: string[]
  location?: string
  visibility: 'public' | 'private'
  likes_count: number
  is_liked: boolean
  comments_count: number
  published_at: string
  created_at: string
  updated_at: string
}

export interface MomentListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Moment[]
}

export const momentsApi = {
  // 获取瞬间列表
  getMoments: async (params?: { page?: number }): Promise<MomentListResponse> => {
    return api.get<MomentListResponse>('/moments/', { params })
  },

  // 获取瞬间详情
  getMoment: async (id: number): Promise<Moment> => {
    return api.get<Moment>(`/moments/${id}/`)
  },

  // 创建瞬间
  createMoment: (data: {
    content: string
    images?: string[]
    location?: string
    visibility?: 'public' | 'private'
  }) => {
    return api.post<Moment>('/moments/', data)
  },

  // 更新瞬间
  updateMoment: (id: number, data: Partial<Moment>) => {
    return api.patch<Moment>(`/moments/${id}/`, data)
  },

  // 删除瞬间
  deleteMoment: (id: number) => {
    return api.delete(`/moments/${id}/`)
  },

  // 点赞瞬间
  likeMoment: async (id: number): Promise<{ liked: boolean; likes: number }> => {
    return api.post<{ liked: boolean; likes: number }>(`/moments/${id}/like/`)
  },
}

