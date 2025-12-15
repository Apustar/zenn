<template>
  <div class="admin-music">
    <div class="page-header">
      <h1 class="page-title">音乐管理</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <Icon icon="mdi:plus" />
        添加音乐
      </button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="musicList.length" class="music-list">
      <div
        v-for="music in musicList"
        :key="music.id"
        class="music-item"
      >
        <div class="music-cover">
          <img
            v-if="music.cover_url"
            :src="music.cover_url"
            :alt="music.title"
            class="cover-image"
          />
          <div v-else class="cover-placeholder">
            <Icon icon="mdi:music" />
          </div>
        </div>
        <div class="music-info">
          <h3 class="music-title">{{ music.title }}</h3>
          <div class="music-meta">
            <span class="artist">{{ music.artist }}</span>
            <span class="album">{{ music.album }}</span>
            <span v-if="music.duration" class="duration">
              {{ formatDuration(music.duration) }}
            </span>
          </div>
          <div class="music-status">
            <span class="status-badge" :class="{ published: music.is_published }">
              {{ music.is_published ? '已发布' : '未发布' }}
            </span>
            <span class="order">排序: {{ music.order }}</span>
          </div>
        </div>
        <div class="music-actions">
          <button @click="openEditModal(music)" class="btn-icon">
            <Icon icon="mdi:pencil" />
          </button>
          <button @click="handleDelete(music)" class="btn-icon btn-danger">
            <Icon icon="mdi:delete" />
          </button>
        </div>
      </div>
    </div>
    <div v-else class="empty">暂无音乐</div>

    <!-- 创建/编辑模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content modal-large" @click.stop>
        <div class="modal-header">
          <h2>{{ editingMusic ? '编辑音乐' : '添加音乐' }}</h2>
          <button @click="closeModal" class="btn-close">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-group">
            <label class="form-label">歌曲名称 *</label>
            <input
              v-model="form.title"
              type="text"
              required
              placeholder="请输入歌曲名称"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">艺术家 *</label>
            <input
              v-model="form.artist"
              type="text"
              required
              placeholder="请输入艺术家名称"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">专辑名称 *</label>
            <input
              v-model="form.album"
              type="text"
              required
              placeholder="请输入专辑名称"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">音频文件 *</label>
            <div class="file-upload">
              <input
                ref="audioInput"
                type="file"
                accept="audio/*"
                @change="handleAudioChange"
                class="file-input"
              />
              <button
                type="button"
                @click="() => (audioInput as any)?.click()"
                class="btn btn-secondary"
              >
                选择音频文件
              </button>
              <span v-if="form.audio_file" class="file-name">
                {{ form.audio_file instanceof File ? form.audio_file.name : '已选择文件' }}
              </span>
              <span v-else-if="editingMusic?.audio_url" class="file-name">
                当前: {{ editingMusic.audio_url.split('/').pop() }}
              </span>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">封面图片</label>
            <div class="cover-upload">
              <img
                v-if="coverPreview || editingMusic?.cover_url"
                :src="coverPreview || editingMusic?.cover_url"
                alt="封面预览"
                class="cover-preview"
              />
              <div v-else class="cover-placeholder-small">
                <Icon icon="mdi:image" />
              </div>
              <div class="cover-actions">
                <input
                  ref="coverInput"
                  type="file"
                  accept="image/*"
                  @change="handleCoverChange"
                  class="file-input"
                />
                <button
                  type="button"
                  @click="() => (coverInput as any)?.click()"
                  class="btn btn-secondary btn-sm"
                >
                  选择封面
                </button>
                <button
                  v-if="coverPreview || editingMusic?.cover_url"
                  type="button"
                  @click="removeCover"
                  class="btn btn-danger btn-sm"
                >
                  移除
                </button>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">歌词</label>
            <textarea
              v-model="form.lyrics"
              placeholder="请输入歌词（可选）"
              class="form-textarea"
              rows="8"
            />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">排序</label>
              <input
                v-model.number="form.order"
                type="number"
                placeholder="数字越小越靠前"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="form.is_published"
                  type="checkbox"
                />
                <span>发布</span>
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Icon } from '@iconify/vue'
import { musicApi, type Music } from '@/api/music'

const loading = ref(false)
const saving = ref(false)
const musicList = ref<Music[]>([])
const showModal = ref(false)
const editingMusic = ref<Music | null>(null)
const audioInput = ref<HTMLInputElement | null>(null)
const coverInput = ref<HTMLInputElement | null>(null)
const coverPreview = ref<string | null>(null)

const form = reactive({
  title: '',
  artist: '',
  album: '',
  audio_file: null as File | null,
  cover: null as File | null,
  lyrics: '',
  order: 0,
  is_published: true,
})

const fetchMusicList = async () => {
  loading.value = true
  try {
    const list = await musicApi.getMusicList()
    musicList.value = Array.isArray(list) ? list : []
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch music list:', error)
    }
    alert('加载音乐列表失败，请稍后重试')
    musicList.value = []
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingMusic.value = null
  form.title = ''
  form.artist = ''
  form.album = ''
  form.audio_file = null
  form.cover = null
  form.lyrics = ''
  form.order = 0
  form.is_published = true
  coverPreview.value = null
  showModal.value = true
}

const openEditModal = (music: Music) => {
  editingMusic.value = music
  form.title = music.title
  form.artist = music.artist
  form.album = music.album
  form.audio_file = null
  form.cover = null
  form.lyrics = music.lyrics || ''
  form.order = music.order
  form.is_published = music.is_published
  coverPreview.value = null
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingMusic.value = null
  form.audio_file = null
  form.cover = null
  coverPreview.value = null
  if (audioInput.value) audioInput.value.value = ''
  if (coverInput.value) coverInput.value.value = ''
}

const handleAudioChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    form.audio_file = file
  }
}

const handleCoverChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    form.cover = file
    const reader = new FileReader()
    reader.onload = (e) => {
      coverPreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const removeCover = () => {
  form.cover = null
  coverPreview.value = null
  if (coverInput.value) coverInput.value.value = ''
}

const handleSubmit = async () => {
  if (!form.audio_file && !editingMusic) {
    alert('请选择音频文件')
    return
  }

  saving.value = true
  try {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('artist', form.artist)
    formData.append('album', form.album)
    if (form.audio_file) {
      formData.append('audio_file', form.audio_file)
    }
    if (form.cover) {
      formData.append('cover', form.cover)
    }
    if (form.lyrics) {
      formData.append('lyrics', form.lyrics)
    }
    formData.append('order', form.order.toString())
    formData.append('is_published', form.is_published.toString())

    if (editingMusic) {
      await musicApi.updateMusic(editingMusic.id, formData)
      alert('音乐更新成功')
    } else {
      await musicApi.createMusic(formData)
      alert('音乐添加成功')
    }
    closeModal()
    await fetchMusicList()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (music: Music) => {
  if (!confirm(`确定要删除《${music.title}》吗？`)) {
    return
  }
  
  try {
    await musicApi.deleteMusic(music.id)
    alert('删除成功')
    await fetchMusicList()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

const formatDuration = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

onMounted(() => {
  fetchMusicList()
})
</script>

<style scoped>
.admin-music {
  max-width: 1200px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: var(--text-color, #333);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: var(--primary-color, #FE9600);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-color, #333);
}

.btn-secondary:hover {
  background: var(--border-color, #e5e5e5);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.music-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.music-item {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.music-cover {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #999);
  font-size: 32px;
}

.music-info {
  flex: 1;
  min-width: 0;
}

.music-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-color, #333);
}

.music-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.music-status {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 12px;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-badge.published {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge:not(.published) {
  background: #fff3e0;
  color: #e65100;
}

.order {
  color: var(--text-secondary, #999);
}

.music-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  padding: 8px;
  background: none;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  color: var(--text-color, #333);
  cursor: pointer;
  transition: all 0.3s;
}

.btn-icon:hover {
  background: var(--bg-secondary, #f5f5f5);
  border-color: var(--primary-color, #FE9600);
  color: var(--primary-color, #FE9600);
}

.btn-icon.btn-danger:hover {
  background: #fee;
  border-color: #c33;
  color: #c33;
}

.loading,
.empty {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary, #666);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal-large {
  max-width: 700px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--border-color, #e5e5e5);
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.btn-close {
  padding: 4px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary, #666);
  transition: color 0.3s;
}

.btn-close:hover {
  color: var(--text-color, #333);
}

.modal-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-color, #333);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color, #FE9600);
}

.form-textarea {
  resize: vertical;
}

.file-upload {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-input {
  display: none;
}

.file-name {
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.cover-upload {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.cover-preview {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid var(--border-color, #e5e5e5);
}

.cover-placeholder-small {
  width: 120px;
  height: 120px;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #999);
  font-size: 32px;
  border: 1px solid var(--border-color, #e5e5e5);
}

.cover-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}
</style>
