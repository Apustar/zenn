import api from './index'

export interface Photo {
  id: number
  title: string
  image: string
  description?: string
  order: number
  created_at: string
}

export interface Album {
  id: number
  name: string
  slug: string
  description?: string
  cover?: string
  author: {
    id: number
    username: string
    avatar?: string
  }
  photos: Photo[]
  photos_count: number
  is_encrypted?: boolean
  is_password_verified?: boolean
  order: number
  created_at: string
  updated_at: string
}

export interface AlbumListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Album[]
}

export const photosApi = {
  // 获取相册列表
  getAlbums: async (params?: { page?: number }): Promise<AlbumListResponse> => {
    return api.get<AlbumListResponse>('/albums/', { params })
  },

  // 获取相册详情
  getAlbum: async (slug: string): Promise<Album> => {
    return api.get<Album>(`/albums/${slug}/`)
  },

  // 创建相册
  createAlbum: (data: {
    name: string
    slug?: string
    description?: string
    cover?: string
    order?: number
  }) => {
    return api.post<Album>('/albums/', data)
  },

  // 验证相册密码
  verifyPassword: async (slug: string, password: string): Promise<{ success: boolean; message: string }> => {
    return api.post(`/albums/${slug}/verify_password/`, { password })
  },
}

