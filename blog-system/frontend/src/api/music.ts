import api from './index'

export interface Music {
  id: number
  title: string
  artist: string
  album: string
  audio_file: string
  audio_url: string
  cover: string
  cover_url: string | null
  lyrics: string
  duration: number | null
  order: number
  is_published: boolean
  author: {
    id: number
    username: string
  }
  created_at: string
  updated_at: string
}

export const musicApi = {
  // 获取音乐列表
  getMusicList: async (): Promise<Music[]> => {
    return api.get<Music[]>('/music/')
  },

  // 获取音乐详情
  getMusicDetail: async (id: number): Promise<Music> => {
    return api.get<Music>(`/music/${id}/`)
  },

  // 创建音乐（需要认证）
  createMusic: async (data: FormData): Promise<Music> => {
    return api.post<Music>('/music/', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 更新音乐（需要认证）
  updateMusic: async (id: number, data: FormData): Promise<Music> => {
    return api.patch<Music>(`/music/${id}/`, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 删除音乐（需要认证）
  deleteMusic: async (id: number): Promise<void> => {
    await api.delete(`/music/${id}/`)
  },
}

