import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Music } from '../api/music'
import { musicApi } from '../api/music'

export const useMusicStore = defineStore('music', () => {
  // 状态
  const playlist = ref<Music[]>([])
  const currentIndex = ref<number>(-1)
  const isPlaying = ref<boolean>(false)
  const currentTime = ref<number>(0)
  const volume = ref<number>(1)
  const isMuted = ref<boolean>(false)
  const playMode = ref<'sequence' | 'loop' | 'random'>(() => {
    // 从localStorage读取播放模式
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('music_play_mode')
      return (saved as 'sequence' | 'loop' | 'random') || 'sequence'
    }
    return 'sequence'
  })
  const isLoading = ref<boolean>(false)
  const showPlaylist = ref<boolean>(false)
  const isPlayerExpanded = ref<boolean>(false) // 播放器是否展开

  // 计算属性
  const currentMusic = computed(() => {
    if (currentIndex.value >= 0 && currentIndex.value < playlist.value.length) {
      return playlist.value[currentIndex.value]
    }
    return null
  })

  const hasNext = computed(() => {
    if (playlist.value.length === 0) return false
    if (playMode.value === 'loop') return true
    if (playMode.value === 'random') return true
    return currentIndex.value < playlist.value.length - 1
  })

  const hasPrev = computed(() => {
    if (playlist.value.length === 0) return false
    if (playMode.value === 'loop') return true
    if (playMode.value === 'random') return true
    return currentIndex.value > 0
  })

  // 初始化播放列表
  const initPlaylist = async () => {
    try {
      isLoading.value = true
      const response = await musicApi.getMusicList()
      // 处理可能的分页格式或直接数组格式
      let musicList: Music[] = []
      if (Array.isArray(response)) {
        musicList = response
      } else if (response && typeof response === 'object' && 'results' in response) {
        // 如果是分页格式，提取 results
        musicList = (response as any).results || []
      }
      
      playlist.value = musicList || []
      // 如果有音乐且当前没有播放，自动播放第一首
      if (musicList.length > 0 && currentIndex.value === -1) {
        currentIndex.value = 0
      }
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('Failed to load music list:', error)
      }
      playlist.value = []
    } finally {
      isLoading.value = false
    }
  }

  // 播放指定音乐
  const playMusic = (index: number, shouldPlay: boolean = true) => {
    if (index >= 0 && index < playlist.value.length) {
      // 保存之前的播放状态
      const wasPlaying = isPlaying.value
      currentIndex.value = index
      // 如果指定了 shouldPlay，使用指定值；否则保持之前的播放状态
      isPlaying.value = shouldPlay !== undefined ? shouldPlay : wasPlaying
    }
  }

  // 播放指定音乐（通过ID）
  const playMusicById = (id: number) => {
    const index = playlist.value.findIndex(m => m.id === id)
    if (index !== -1) {
      playMusic(index)
    }
  }

  // 下一首
  const nextMusic = () => {
    if (playlist.value.length === 0) return

    // 保存当前的播放状态
    const wasPlaying = isPlaying.value

    let nextIndex: number
    if (playMode.value === 'random') {
      // 随机播放
      nextIndex = Math.floor(Math.random() * playlist.value.length)
      // 避免连续播放同一首
      if (nextIndex === currentIndex.value && playlist.value.length > 1) {
        nextIndex = (nextIndex + 1) % playlist.value.length
      }
    } else if (playMode.value === 'loop') {
      // 循环播放
      nextIndex = (currentIndex.value + 1) % playlist.value.length
    } else {
      // 顺序播放
      if (currentIndex.value < playlist.value.length - 1) {
        nextIndex = currentIndex.value + 1
      } else {
        return // 没有下一首
      }
    }

    // 切换歌曲时保持之前的播放状态
    playMusic(nextIndex, wasPlaying)
  }

  // 上一首
  const prevMusic = () => {
    if (playlist.value.length === 0) return

    // 保存当前的播放状态
    const wasPlaying = isPlaying.value

    let prevIndex: number
    if (playMode.value === 'random') {
      // 随机播放
      prevIndex = Math.floor(Math.random() * playlist.value.length)
      // 避免连续播放同一首
      if (prevIndex === currentIndex.value && playlist.value.length > 1) {
        prevIndex = (prevIndex + playlist.value.length - 1) % playlist.value.length
      }
    } else if (playMode.value === 'loop') {
      // 循环播放
      prevIndex = (currentIndex.value - 1 + playlist.value.length) % playlist.value.length
    } else {
      // 顺序播放
      if (currentIndex.value > 0) {
        prevIndex = currentIndex.value - 1
      } else {
        return // 没有上一首
      }
    }

    // 切换歌曲时保持之前的播放状态
    playMusic(prevIndex, wasPlaying)
  }

  // 播放/暂停
  const togglePlay = () => {
    if (currentMusic.value) {
      isPlaying.value = !isPlaying.value
    } else if (playlist.value.length > 0) {
      // 如果没有当前音乐，播放第一首
      playMusic(0)
    }
  }

  // 设置播放模式
  const setPlayMode = (mode: 'sequence' | 'loop' | 'random') => {
    playMode.value = mode
    if (typeof window !== 'undefined') {
      localStorage.setItem('music_play_mode', mode)
    }
  }

  // 切换播放模式
  const togglePlayMode = () => {
    const modes: ('sequence' | 'loop' | 'random')[] = ['sequence', 'loop', 'random']
    const currentModeIndex = modes.indexOf(playMode.value)
    const nextModeIndex = (currentModeIndex + 1) % modes.length
    setPlayMode(modes[nextModeIndex])
  }

  // 设置音量
  const setVolume = (value: number) => {
    volume.value = Math.max(0, Math.min(1, value))
    isMuted.value = volume.value === 0
  }

  // 切换静音
  const toggleMute = () => {
    if (isMuted.value) {
      // 取消静音，恢复之前的音量
      volume.value = volume.value || 0.5
      isMuted.value = false
    } else {
      // 静音
      isMuted.value = true
    }
  }

  // 设置当前播放时间
  const setCurrentTime = (time: number) => {
    currentTime.value = time
  }

  // 切换播放列表显示
  const togglePlaylist = () => {
    showPlaylist.value = !showPlaylist.value
  }

  // 从播放列表移除
  const removeFromPlaylist = (index: number) => {
    if (index < 0 || index >= playlist.value.length) return

    playlist.value.splice(index, 1)

    // 如果移除的是当前播放的音乐
    if (index === currentIndex.value) {
      if (playlist.value.length > 0) {
        // 如果还有音乐，播放下一首（或第一首）
        currentIndex.value = Math.min(index, playlist.value.length - 1)
      } else {
        // 如果没有音乐了，重置状态
        currentIndex.value = -1
        isPlaying.value = false
      }
    } else if (index < currentIndex.value) {
      // 如果移除的是当前播放之前的音乐，调整索引
      currentIndex.value--
    }
  }

  // 清空播放列表
  const clearPlaylist = () => {
    playlist.value = []
    currentIndex.value = -1
    isPlaying.value = false
    currentTime.value = 0
  }

  // 切换播放器展开/收起
  const togglePlayerExpanded = () => {
    isPlayerExpanded.value = !isPlayerExpanded.value
  }

  return {
    // 状态
    playlist,
    currentIndex,
    isPlaying,
    currentTime,
    volume,
    isMuted,
    playMode,
    isLoading,
    showPlaylist,
    isPlayerExpanded,
    // 计算属性
    currentMusic,
    hasNext,
    hasPrev,
    // 方法
    initPlaylist,
    playMusic,
    playMusicById,
    nextMusic,
    prevMusic,
    togglePlay,
    setPlayMode,
    togglePlayMode,
    setVolume,
    toggleMute,
    setCurrentTime,
    togglePlaylist,
    togglePlayerExpanded,
    removeFromPlaylist,
    clearPlaylist,
  }
})


