import api from './index'

export interface Post {
  id: number
  title: string
  slug: string
  excerpt: string
  content?: string
  content_html?: string
  cover?: string
  author: {
    id: number
    username: string
    avatar?: string
  }
  category?: {
    id: number
    name: string
    slug: string
  }
  tags: Array<{
    id: number
    name: string
    slug: string
    color: string
  }>
  is_top: boolean
  views: number
  likes: number
  is_liked?: boolean
  word_count?: number
  read_time?: number
  is_encrypted?: boolean
  is_password_verified?: boolean
  preview_content_html?: string | null
  published_at?: string
  created_at: string
  updated_at?: string
}

export interface PostListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Post[]
}

export const postsApi = {
  // 获取文章列表
  getPosts: async (params?: {
    page?: number
    category?: string
    tags?: string
    search?: string
    ordering?: string
  }): Promise<PostListResponse> => {
    return api.get<PostListResponse>('/posts/', { params })
  },

  // 获取文章详情
  getPost: async (slug: string): Promise<Post> => {
    return api.get<Post>(`/posts/${slug}/`)
  },

  // 创建文章
  createPost: (data: Partial<Post>) => {
    return api.post<Post>('/posts/', data)
  },

  // 更新文章
  updatePost: (slug: string, data: Partial<Post>) => {
    return api.patch<Post>(`/posts/${slug}/`, data)
  },

  // 删除文章
  deletePost: (slug: string) => {
    return api.delete(`/posts/${slug}/`)
  },

  // 点赞文章
  likePost: (slug: string): Promise<{ liked: boolean; likes: number }> => {
    return api.post(`/posts/${slug}/like/`)
  },

  // 获取相关文章
  getRelatedPosts: (slug: string) => {
    return api.get<Post[]>(`/posts/${slug}/related/`)
  },

  // 获取归档
  getArchives: async (): Promise<Record<string, Post[]>> => {
    return api.get<Record<string, Post[]>>('/posts/archives/')
  },

  // 验证文章密码
  verifyPassword: async (slug: string, password: string): Promise<{ success: boolean; message: string }> => {
    return api.post(`/posts/${slug}/verify_password/`, { password })
  },
}

