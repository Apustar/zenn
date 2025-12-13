<template>
  <div class="music-player" :class="{ 
    'is-expanded': isPlayerExpanded, 
    'has-music': playlist.length > 0,
    'show-playlist': showPlaylist 
  }">
    <!-- 音频元素 -->
    <audio
      ref="audioRef"
      :src="currentMusic?.audio_url"
      @timeupdate="handleTimeUpdate"
      @loadedmetadata="handleLoadedMetadata"
      @ended="handleEnded"
      @error="handleError"
      @play="isPlaying = true"
      @pause="isPlaying = false"
    />

    <!-- 空状态提示 -->
    <div v-if="playlist.length === 0" class="player-empty">
      <div class="empty-content">
        <Icon icon="mdi:music-off" class="empty-icon" />
        <span class="empty-text">暂无音乐，请在后台添加音乐</span>
      </div>
    </div>

    <!-- 折叠状态：圆形图标 -->
    <div v-else-if="!isPlayerExpanded" class="player-mini" @click="musicStore.togglePlayerExpanded">
      <div class="mini-icon-wrapper">
        <img
          v-if="currentMusic?.cover_url"
          :src="currentMusic.cover_url"
          :alt="currentMusic.title"
          class="mini-cover"
        />
        <div v-else class="mini-icon">
          <Icon icon="mdi:music" />
        </div>
        <div v-if="isPlaying" class="mini-playing-indicator">
          <Icon icon="mdi:equalizer" />
        </div>
      </div>
    </div>

    <!-- 展开状态：完整播放器 -->
    <div v-else class="player-main">
      <!-- 收起按钮 -->
      <button class="collapse-btn" @click="musicStore.togglePlayerExpanded" title="收起播放器">
        <Icon icon="mdi:chevron-down" />
      </button>
      <!-- 左侧：封面和歌曲信息 -->
      <div class="player-info">
        <div class="cover-wrapper" @click="musicStore.togglePlaylist">
          <img
            v-if="currentMusic?.cover_url"
            :src="currentMusic.cover_url"
            :alt="currentMusic.title"
            class="cover"
          />
          <div v-else class="cover-placeholder">
            <Icon icon="mdi:music" />
          </div>
          <div class="cover-overlay">
            <Icon :icon="showPlaylist ? 'mdi:playlist-remove' : 'mdi:playlist-music'" />
          </div>
        </div>
        <div class="song-info">
          <div class="song-title">{{ currentMusic?.title || '未知歌曲' }}</div>
          <div class="song-artist">{{ currentMusic?.artist || '未知艺术家' }}</div>
        </div>
      </div>

      <!-- 中间：播放控制 -->
      <div class="player-controls">
        <div class="control-buttons">
          <button class="control-btn" @click="musicStore.togglePlayMode" :title="playModeText">
            <Icon :icon="playModeIcon" />
          </button>
          <button class="control-btn" @click="musicStore.prevMusic" :disabled="!hasPrev">
            <Icon icon="mdi:skip-previous" />
          </button>
          <button class="control-btn play-btn" @click="togglePlay">
            <Icon :icon="isPlaying ? 'mdi:pause' : 'mdi:play'" />
          </button>
          <button class="control-btn" @click="musicStore.nextMusic" :disabled="!hasNext">
            <Icon icon="mdi:skip-next" />
          </button>
          <button class="control-btn" @click="musicStore.togglePlaylist" :title="showPlaylist ? '隐藏播放列表' : '显示播放列表'">
            <Icon icon="mdi:playlist-music" />
          </button>
        </div>
        <div class="progress-wrapper">
          <span class="time-text">{{ formatTime(currentTime) }}</span>
          <div class="progress-bar" @click="handleProgressClick">
            <div class="progress-track" :style="{ width: progressPercent + '%' }"></div>
            <div class="progress-thumb" :style="{ left: progressPercent + '%' }"></div>
          </div>
          <span class="time-text">{{ formatTime(duration) }}</span>
        </div>
      </div>

      <!-- 右侧：音量控制 -->
      <div class="player-volume">
        <button class="control-btn" @click="toggleMute" :title="isMuted ? '取消静音' : '静音'">
          <Icon :icon="isMuted ? 'mdi:volume-off' : volume > 0.5 ? 'mdi:volume-high' : 'mdi:volume-low'" />
        </button>
        <div class="volume-bar" @click="handleVolumeClick">
          <div class="volume-track" :style="{ width: (isMuted ? 0 : volume * 100) + '%' }"></div>
          <div class="volume-thumb" :style="{ left: (isMuted ? 0 : volume * 100) + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 播放列表 - 只在播放器展开时显示 -->
    <transition name="slide-up">
      <div v-if="showPlaylist && isPlayerExpanded" class="playlist-panel">
        <div class="playlist-header">
          <span class="playlist-title">播放列表 ({{ playlist.length }})</span>
          <button class="close-btn" @click="musicStore.togglePlaylist">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <div class="playlist-content">
          <div
            v-for="(music, index) in playlist"
            :key="music.id"
            class="playlist-item"
            :class="{ active: index === currentIndex }"
            @click="handlePlaylistItemClick(index)"
          >
            <div class="item-cover">
              <img
                v-if="music.cover_url"
                :src="music.cover_url"
                :alt="music.title"
              />
              <div v-else class="cover-placeholder-small">
                <Icon icon="mdi:music" />
              </div>
              <div v-if="index === currentIndex && isPlaying" class="playing-indicator">
                <Icon icon="mdi:equalizer" />
              </div>
            </div>
            <div class="item-info">
              <div class="item-title">{{ music.title }}</div>
              <div class="item-artist">{{ music.artist || '未知艺术家' }}</div>
            </div>
            <div class="item-duration">{{ formatTime(music.duration || 0) }}</div>
            <button
              class="item-remove"
              @click.stop="musicStore.removeFromPlaylist(index)"
              title="从播放列表移除"
            >
              <Icon icon="mdi:close" />
            </button>
          </div>
          <div v-if="playlist.length === 0" class="playlist-empty">
            播放列表为空
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { Icon } from '@iconify/vue'
import { useMusicStore } from '../stores/music'

const musicStore = useMusicStore()

// 使用storeToRefs保持响应式
const {
  playlist,
  currentIndex,
  isPlaying,
  currentTime,
  volume,
  isMuted,
  playMode,
  showPlaylist,
  isPlayerExpanded,
  currentMusic,
  hasNext,
  hasPrev,
} = storeToRefs(musicStore)

// 音频元素引用
const audioRef = ref<HTMLAudioElement | null>(null)
const duration = ref<number>(0)
const isSwitchingMusic = ref<boolean>(false) // 标记是否正在切换音乐

// 计算属性
const progressPercent = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

const playModeText = computed(() => {
  const texts = {
    sequence: '顺序播放',
    loop: '列表循环',
    random: '随机播放',
  }
  return texts[playMode]
})

const playModeIcon = computed(() => {
  const icons = {
    sequence: 'mdi:repeat',
    loop: 'mdi:repeat-once',
    random: 'mdi:shuffle',
  }
  return icons[playMode]
})

// 格式化时间
const formatTime = (seconds: number): string => {
  if (!seconds || isNaN(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 播放/暂停
const togglePlay = () => {
  musicStore.togglePlay()
}

// 监听播放状态，控制音频元素
watch(() => musicStore.isPlaying, (playing) => {
  if (!audioRef.value || isSwitchingMusic.value) return // 正在切换音乐时，不响应播放状态变化
  if (playing) {
    audioRef.value.play().catch((error) => {
      if (import.meta.env.DEV) {
        console.error('Play failed:', error)
      }
      musicStore.isPlaying = false
    })
  } else {
    audioRef.value.pause()
  }
})

// 监听当前音乐变化
watch(currentMusic, (music, oldMusic) => {
  if (!music || !audioRef.value) return
  
  // 标记正在切换音乐
  isSwitchingMusic.value = true
  
  // 如果之前有音乐在播放，先暂停
  if (oldMusic) {
    audioRef.value.pause()
  }
  
  // 保存是否应该自动播放
  const shouldAutoPlay = isPlaying.value
  
  // 如果应该自动播放，先设置为暂停状态（图标显示暂停）
  if (shouldAutoPlay) {
    isPlaying.value = false
  }
  
  // 加载新音频
  audioRef.value.load()
  
  // 播放新音频的函数
  const playNewMusic = () => {
    if (!audioRef.value || musicStore.currentMusic?.id !== music.id) {
      isSwitchingMusic.value = false
      return
    }
    
    audioRef.value.play()
      .then(() => {
        // 播放成功后设置为播放状态
        if (audioRef.value && musicStore.currentMusic?.id === music.id) {
          isPlaying.value = true
          isSwitchingMusic.value = false
        }
      })
      .catch((error) => {
        if (import.meta.env.DEV) {
          console.error('Auto play failed:', error)
        }
        // 播放失败，保持暂停状态
        isPlaying.value = false
        isSwitchingMusic.value = false
      })
  }
  
  // 如果应该自动播放，等待音频加载完成后自动播放
  if (shouldAutoPlay) {
    // 如果音频已经加载完成，直接播放
    if (audioRef.value.readyState >= 2) {
      setTimeout(playNewMusic, 150)
    } else {
      // 等待音频元数据加载完成后再播放
      const handleLoaded = () => {
        setTimeout(playNewMusic, 150)
      }
      audioRef.value.addEventListener('loadeddata', handleLoaded, { once: true })
      // 备用：如果 loadeddata 事件没有触发，使用 canplay 事件
      audioRef.value.addEventListener('canplay', handleLoaded, { once: true })
    }
  } else {
    // 不需要自动播放，直接重置标记
    isSwitchingMusic.value = false
  }
})

// 监听音量变化
watch(volume, (vol) => {
  if (audioRef.value) {
    audioRef.value.volume = isMuted.value ? 0 : vol
  }
})

watch(isMuted, (muted) => {
  if (audioRef.value) {
    audioRef.value.volume = muted ? 0 : volume.value
  }
})

// 监听播放器展开状态，折叠时自动关闭播放列表
watch(isPlayerExpanded, (expanded) => {
  if (!expanded && showPlaylist.value) {
    musicStore.togglePlaylist()
  }
})

// 音频事件处理
const handleTimeUpdate = (e: Event) => {
  const audio = e.target as HTMLAudioElement
  musicStore.setCurrentTime(audio.currentTime)
}

const handleLoadedMetadata = (e: Event) => {
  const audio = e.target as HTMLAudioElement
  duration.value = audio.duration
  // 如果音乐模型中没有duration，可以在这里更新（需要API支持）
}

const handleEnded = () => {
  // 播放结束，自动播放下一首
  musicStore.nextMusic()
}

const handleError = (e: Event) => {
  if (import.meta.env.DEV) {
    console.error('Audio error:', e)
  }
  // 播放出错，尝试下一首
  if (musicStore.hasNext) {
    setTimeout(() => {
      musicStore.nextMusic()
    }, 1000)
  }
}

// 进度条点击
const handleProgressClick = (e: MouseEvent) => {
  if (!audioRef.value || duration.value === 0) return
  const progressBar = e.currentTarget as HTMLElement
  const rect = progressBar.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  const newTime = percent * duration.value
  audioRef.value.currentTime = newTime
  musicStore.setCurrentTime(newTime)
}

// 音量条点击
const handleVolumeClick = (e: MouseEvent) => {
  const volumeBar = e.currentTarget as HTMLElement
  const rect = volumeBar.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  musicStore.setVolume(percent)
}

// 播放列表项点击处理
const handlePlaylistItemClick = (index: number) => {
  // 保存当前的播放状态
  const wasPlaying = isPlaying.value
  // 切换歌曲时保持之前的播放状态
  musicStore.playMusic(index, wasPlaying)
}

// 初始化
onMounted(async () => {
  await musicStore.initPlaylist()
  // 设置初始音量
  if (audioRef.value) {
    audioRef.value.volume = musicStore.isMuted ? 0 : musicStore.volume
  }
})

// 清理
onUnmounted(() => {
  if (audioRef.value) {
    audioRef.value.pause()
    audioRef.value.src = ''
  }
})
</script>

<style scoped>
.music-player {
  position: fixed;
  z-index: 999; /* 在导航栏下方 */
  transition: all 0.3s ease;
}

.music-player:not(.has-music) {
  min-height: 60px;
}

/* 折叠状态：圆形图标 - 右上角 */
.player-mini {
  position: fixed;
  top: 70px; /* 导航栏高度60px + 10px间距 */
  right: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 999;
}

.mini-icon-wrapper {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--primary-color, #007bff);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-icon-wrapper:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 123, 255, 0.5);
}

.mini-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mini-icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.mini-playing-indicator {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color, #007bff);
  font-size: 10px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

/* 展开状态：完整播放器 - 从底部弹出 */
.music-player.is-expanded {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--player-bg, rgba(255, 255, 255, 0.95));
  backdrop-filter: blur(10px);
  border-top: 1px solid var(--border-color, #e5e5e5);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.dark .music-player.is-expanded {
  background: var(--player-bg, rgba(30, 30, 30, 0.95));
  border-top-color: var(--border-color, #444);
}

.collapse-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-secondary, #666);
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 20px;
  z-index: 10;
}

.collapse-btn:hover {
  background: var(--bg-hover, rgba(0, 0, 0, 0.05));
  color: var(--text-primary, #333);
}

.player-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 20px;
  min-height: 60px;
}

.empty-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary, #666);
  font-size: 14px;
}

.empty-icon {
  font-size: 20px;
}

.empty-text {
  font-size: 14px;
}

.player-main {
  position: relative;
  display: flex;
  align-items: center;
  padding: 12px 20px;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.player-info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  flex: 0 0 auto;
}

.cover-wrapper {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
  background: var(--bg-secondary, #f5f5f5);
}

.cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-secondary, #999);
  font-size: 24px;
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  color: white;
  font-size: 20px;
}

.cover-wrapper:hover .cover-overlay {
  opacity: 1;
}

.song-info {
  min-width: 0;
  flex: 1;
}

.song-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #333);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.song-artist {
  font-size: 12px;
  color: var(--text-secondary, #666);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.control-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--text-primary, #333);
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.2s;
  font-size: 20px;
}

.control-btn:hover:not(:disabled) {
  background: var(--bg-hover, rgba(0, 0, 0, 0.05));
}

.control-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.play-btn {
  width: 44px;
  height: 44px;
  background: var(--primary-color, #007bff);
  color: white;
  font-size: 24px;
}

.play-btn:hover {
  background: var(--primary-hover, #0056b3);
  transform: scale(1.05);
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-text {
  font-size: 12px;
  color: var(--text-secondary, #666);
  min-width: 40px;
  text-align: center;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--bg-secondary, #e5e5e5);
  border-radius: 2px;
  cursor: pointer;
  position: relative;
}

.progress-track {
  height: 100%;
  background: var(--primary-color, #007bff);
  border-radius: 2px;
  transition: width 0.1s;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  width: 12px;
  height: 12px;
  background: var(--primary-color, #007bff);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.2s;
}

.progress-bar:hover .progress-thumb {
  opacity: 1;
}

.player-volume {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
}

.volume-bar {
  width: 80px;
  height: 4px;
  background: var(--bg-secondary, #e5e5e5);
  border-radius: 2px;
  cursor: pointer;
  position: relative;
}

.volume-track {
  height: 100%;
  background: var(--primary-color, #007bff);
  border-radius: 2px;
}

.volume-thumb {
  position: absolute;
  top: 50%;
  width: 12px;
  height: 12px;
  background: var(--primary-color, #007bff);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.2s;
}

.volume-bar:hover .volume-thumb {
  opacity: 1;
}

/* 播放列表 */
.playlist-panel {
  max-height: 400px;
  overflow-y: auto;
  border-top: 1px solid var(--border-color, #e5e5e5);
  background: var(--bg-primary, #fff);
}

.playlist-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-color, #e5e5e5);
}

.playlist-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-secondary, #666);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-hover, rgba(0, 0, 0, 0.05));
}

.playlist-content {
  padding: 8px 0;
}

.playlist-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.playlist-item:hover {
  background: var(--bg-hover, rgba(0, 0, 0, 0.05));
}

.playlist-item.active {
  background: var(--bg-active, rgba(0, 123, 255, 0.1));
}

.item-cover {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--bg-secondary, #f5f5f5);
}

.item-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder-small {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #999);
  font-size: 18px;
}

.playing-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  color: var(--text-primary, #333);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.item-artist {
  font-size: 12px;
  color: var(--text-secondary, #666);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-duration {
  font-size: 12px;
  color: var(--text-secondary, #666);
  min-width: 40px;
  text-align: right;
}

.item-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-secondary, #666);
  cursor: pointer;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.2s;
}

.playlist-item:hover .item-remove {
  opacity: 1;
}

.item-remove:hover {
  background: var(--bg-hover, rgba(0, 0, 0, 0.05));
  color: var(--error-color, #dc3545);
}

.playlist-empty {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-secondary, #666);
  font-size: 14px;
}

/* 动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

/* 响应式 */
@media (max-width: 768px) {
  .player-mini {
    top: 70px;
    right: 12px;
  }

  .mini-icon-wrapper {
    width: 44px;
    height: 44px;
  }

  .mini-icon {
    font-size: 20px;
  }

  .player-main {
    padding: 10px 12px;
    gap: 12px;
  }

  .song-info {
    display: none;
  }

  .player-volume {
    display: none;
  }

  .control-buttons {
    gap: 4px;
  }

  .control-btn {
    width: 32px;
    height: 32px;
    font-size: 18px;
  }

  .play-btn {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}
</style>

