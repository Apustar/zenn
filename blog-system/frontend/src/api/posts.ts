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
  status?: 'draft' | 'published' | 'archived'
  is_top: boolean
  views: number
  likes: number
  is_liked?: boolean
  word_count?: number
  read_time?: number
  is_encrypted?: boolean
  is_password_verified?: boolean
  preview_content_html?: string | null
  toc?: TOCItem[]
  published_at?: string
  created_at: string
  updated_at?: string
}

export interface TOCItem {
  level: number
  text: string
  id: string
  children: TOCItem[]
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
    category?: string | number
    tags?: string | number
    search?: string
    status?: 'draft' | 'published' | 'archived'
    ordering?: string
  }): Promise<PostListResponse> => {
    return api.get<PostListResponse>('/posts/', { params })
  },

  // 获取文章详情（通过 slug）
  getPost: async (slug: string): Promise<Post> => {
    return api.get<Post>(`/posts/${slug}/`)
  },

  // 获取文章详情（通过 ID，用于管理后台）
  // 注意：后端使用 slug 作为 lookup_field，所以需要通过列表 API 查找
  getPostById: async (id: number): Promise<Post> => {
    // 获取所有文章（包括草稿），找到对应的文章
    // 注意：需要管理员权限才能看到所有文章
    let page = 1
    let found = false
    let post: Post | undefined
    
    while (!found) {
      const response = await api.get<PostListResponse>(`/posts/`, { params: { page } })
      post = response.results.find(p => p.id === id)
      
      if (post) {
        found = true
        break
      }
      
      if (!response.next) {
        break
      }
      page++
    }
    
    if (!post) {
      throw new Error('文章不存在')
    }
    
    return api.get<Post>(`/posts/${post.slug}/`)
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

  // 自动保存文章（更新现有文章）
  autosavePost: async (slug: string, data: Partial<Post>) => {
    return api.post<{ id: number; slug: string; title: string; updated_at: string }>(
      `/posts/${slug}/autosave/`,
      data
    )
  },

  // 自动保存新文章（创建草稿）
  autosaveCreatePost: async (data: Partial<Post>) => {
    return api.post<{ id: number; slug: string; title: string; updated_at: string }>(
      '/posts/autosave_create/',
      data
    )
  },

  // 获取热门文章
  getHotPosts: async (): Promise<Post[]> => {
    return api.get<Post[]>('/posts/hot/')
  },

  // 获取搜索建议
  getSearchSuggestions: async (keyword: string): Promise<string[]> => {
    return api.get<string[]>('/posts/search_suggestions/', {
      params: { q: keyword }
    })
  },
}

