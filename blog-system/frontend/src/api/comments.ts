import api from './index'

export interface Comment {
  id: number
  author: {
    id: number
    username: string
    avatar?: string
  }
  content: string
  parent?: number
  replies?: Comment[]
  likes_count: number
  is_liked: boolean
  created_at: string
  updated_at: string
}

export interface CommentListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Comment[]
}

export const commentsApi = {
  // 获取评论列表
  getComments: async (contentTypeId: string, objectId: number): Promise<Comment[]> => {
    const response = await api.get<CommentListResponse | Comment[]>('/comments/', {
      params: {
        content_type: contentTypeId,
        object_id: objectId,
      },
    })
    // 处理分页响应，返回 results 数组
    if (response && typeof response === 'object' && 'results' in response) {
      return (response as CommentListResponse).results || []
    }
    // 如果不是分页格式，直接返回数组
    return Array.isArray(response) ? response : []
  },

  // 创建评论
  createComment: async (data: {
    content: string
    parent?: number
    content_type: number
    object_id: number
  }): Promise<Comment> => {
    return api.post<Comment>('/comments/', data)
  },

  // 点赞评论
  likeComment: async (id: number): Promise<void> => {
    return api.post<void>(`/comments/${id}/like/`)
  },
}

