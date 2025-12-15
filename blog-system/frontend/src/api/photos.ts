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
  createAlbum: async (data: FormData | {
    name: string
    slug?: string
    description?: string
    cover?: File | string
    order?: number
    is_encrypted?: boolean
    password?: string
  }): Promise<Album> => {
    if (data instanceof FormData) {
      return api.post<Album>('/albums/', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    } else {
      const formData = new FormData()
      formData.append('name', data.name)
      if (data.slug) formData.append('slug', data.slug)
      if (data.description) formData.append('description', data.description)
      if (data.cover instanceof File) formData.append('cover', data.cover)
      if (data.order !== undefined) formData.append('order', data.order.toString())
      if (data.is_encrypted !== undefined) formData.append('is_encrypted', data.is_encrypted.toString())
      if (data.password) formData.append('password', data.password)
      return api.post<Album>('/albums/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    }
  },

  // 更新相册
  updateAlbum: async (slug: string, data: FormData | Partial<{
    name: string
    slug: string
    description: string
    cover: File | string
    order: number
    is_encrypted: boolean
    password: string
  }>): Promise<Album> => {
    if (data instanceof FormData) {
      return api.patch<Album>(`/albums/${slug}/`, data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    } else {
      const formData = new FormData()
      if (data.name) formData.append('name', data.name)
      if (data.slug) formData.append('slug', data.slug)
      if (data.description !== undefined) formData.append('description', data.description)
      if (data.cover instanceof File) formData.append('cover', data.cover)
      if (data.order !== undefined) formData.append('order', data.order.toString())
      if (data.is_encrypted !== undefined) formData.append('is_encrypted', data.is_encrypted.toString())
      if (data.password !== undefined) formData.append('password', data.password)
      return api.patch<Album>(`/albums/${slug}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    }
  },

  // 删除相册
  deleteAlbum: async (slug: string): Promise<void> => {
    return api.delete(`/albums/${slug}/`)
  },

  // 创建照片
  createPhoto: async (data: FormData | {
    album: number
    title?: string
    image: File
    description?: string
    order?: number
  }): Promise<Photo> => {
    if (data instanceof FormData) {
      return api.post<Photo>('/photos/', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    } else {
      const formData = new FormData()
      formData.append('album', data.album.toString())
      if (data.title) formData.append('title', data.title)
      formData.append('image', data.image)
      if (data.description) formData.append('description', data.description)
      if (data.order !== undefined) formData.append('order', data.order.toString())
      return api.post<Photo>('/photos/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    }
  },

  // 更新照片
  updatePhoto: async (id: number, data: FormData | Partial<{
    title: string
    image: File
    description: string
    order: number
  }>): Promise<Photo> => {
    if (data instanceof FormData) {
      return api.patch<Photo>(`/photos/${id}/`, data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    } else {
      const formData = new FormData()
      if (data.title !== undefined) formData.append('title', data.title)
      if (data.image instanceof File) formData.append('image', data.image)
      if (data.description !== undefined) formData.append('description', data.description)
      if (data.order !== undefined) formData.append('order', data.order.toString())
      return api.patch<Photo>(`/photos/${id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    }
  },

  // 删除照片
  deletePhoto: async (id: number): Promise<void> => {
    return api.delete(`/photos/${id}/`)
  },

  // 验证相册密码
  verifyPassword: async (slug: string, password: string): Promise<{ success: boolean; message: string }> => {
    return api.post(`/albums/${slug}/verify_password/`, { password })
  },

  // 批量更新照片排序
  bulkUpdatePhotoOrder: async (orders: { id: number; order: number }[]): Promise<{ success: boolean; message: string }> => {
    return api.post('/photos/bulk_update_order/', { orders })
  },

  // 批量删除照片
  bulkDeletePhotos: async (ids: number[]): Promise<{ success: boolean; message: string }> => {
    return api.post('/photos/bulk_delete/', { ids })
  },
}

