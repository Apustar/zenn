<template>
  <div class="admin-photos">
    <div class="page-header">
      <h1 class="page-title">相册管理</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <Icon icon="mdi:plus" />
        新建相册
      </button>
    </div>

    <!-- 搜索 -->
    <div class="filters">
      <div class="search-wrapper">
        <Icon icon="mdi:magnify" class="search-icon" />
        <input
          v-model="searchKeyword"
          @input="handleSearch"
          type="text"
          placeholder="搜索相册名称或描述..."
          class="search-input"
        />
        <button
          v-if="searchKeyword"
          @click="clearSearch"
          class="search-clear"
          type="button"
        >
          <Icon icon="mdi:close-circle" />
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="albums.length" class="albums-grid">
      <div
        v-for="album in albums"
        :key="album.id"
        class="album-card"
      >
        <div class="album-cover" @click="openAlbumDetail(album)">
          <img
            v-if="album.cover"
            :src="album.cover"
            :alt="album.name"
            class="cover-image"
          />
          <div v-else class="cover-placeholder">
            <Icon icon="mdi:image-multiple" />
          </div>
          <div v-if="album.is_encrypted" class="encrypted-badge">
            <Icon icon="mdi:lock" />
          </div>
        </div>
        <div class="album-info">
          <h3 class="album-name">{{ album.name }}</h3>
          <p v-if="album.description" class="album-description">
            {{ album.description }}
          </p>
          <div class="album-meta">
            <span>{{ album.photos_count || 0 }} 张照片</span>
            <span>{{ formatDate(album.created_at) }}</span>
          </div>
        </div>
        <div class="album-actions">
          <button @click="openEditModal(album)" class="btn-icon">
            <Icon icon="mdi:pencil" />
          </button>
          <button @click="handleDelete(album)" class="btn-icon btn-danger">
            <Icon icon="mdi:delete" />
          </button>
        </div>
      </div>
    </div>
    <div v-else class="empty">暂无相册</div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="page-btn"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} / {{ totalPages }} 页
      </span>
      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        下一页
      </button>
    </div>

    <!-- 相册详情/编辑模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ editingAlbum ? '编辑相册' : '新建相册' }}</h2>
          <button @click="closeModal" class="btn-close">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-group">
            <label class="form-label">相册名称 *</label>
            <input
              v-model="form.name"
              type="text"
              required
              placeholder="请输入相册名称"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">URL 别名</label>
            <input
              v-model="form.slug"
              type="text"
              placeholder="自动生成"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea
              v-model="form.description"
              placeholder="相册描述"
              class="form-textarea"
              rows="3"
            />
          </div>
          <div class="form-group">
            <label class="form-label">封面图</label>
            <div class="image-upload">
              <img
                v-if="form.coverPreview || (editingAlbum && editingAlbum.cover)"
                :src="form.coverPreview || editingAlbum?.cover"
                alt="封面预览"
                class="image-preview"
                @click="() => coverInput?.click()"
                title="点击更换封面"
              />
              <div
                v-else
                class="image-placeholder"
                @click="() => coverInput?.click()"
              >
                <Icon icon="mdi:image" />
                <span>点击上传封面</span>
              </div>
              <input
                ref="coverInput"
                type="file"
                accept="image/*"
                @change="handleCoverChange"
                class="file-input"
              />
              <button
                type="button"
                @click="() => coverInput?.click()"
                class="btn btn-secondary"
              >
                选择封面
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">排序</label>
            <input
              v-model.number="form.order"
              type="number"
              placeholder="0"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="form.is_encrypted"
                type="checkbox"
              />
              <span>加密相册</span>
            </label>
          </div>
          <div v-if="form.is_encrypted" class="form-group">
            <label class="form-label">访问密码</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="设置访问密码"
              class="form-input"
            />
          </div>

          <!-- 照片管理 -->
          <div v-if="editingAlbum" class="photos-section">
            <div class="section-header">
              <h3>照片管理</h3>
              <div class="section-actions">
                <button
                  type="button"
                  @click="openBulkUploadModal"
                  class="btn btn-secondary btn-sm"
                >
                  <Icon icon="mdi:upload-multiple" />
                  批量上传
                </button>
                <button
                  type="button"
                  @click="openPhotoModal"
                  class="btn btn-secondary btn-sm"
                >
                  <Icon icon="mdi:plus" />
                  添加照片
                </button>
                <button
                  v-if="selectedPhotos.length > 0"
                  type="button"
                  @click="handleBulkDelete"
                  class="btn btn-danger btn-sm"
                >
                  <Icon icon="mdi:delete" />
                  删除选中 ({{ selectedPhotos.length }})
                </button>
              </div>
            </div>
            <div v-if="editingAlbum.photos && editingAlbum.photos.length" class="photos-grid">
              <div
                v-for="(photo, index) in editingAlbum.photos"
                :key="photo.id"
                class="photo-item"
                :class="{ 'selected': selectedPhotos.includes(photo.id) }"
                @click="togglePhotoSelection(photo.id)"
              >
                <div class="photo-checkbox">
                  <input
                    type="checkbox"
                    :checked="selectedPhotos.includes(photo.id)"
                    @click.stop="togglePhotoSelection(photo.id)"
                  />
                </div>
                <img :src="photo.image" :alt="photo.title" class="photo-thumb" />
                <div class="photo-order">{{ index + 1 }}</div>
                <div class="photo-actions" @click.stop>
                  <button
                    type="button"
                    @click="openPhotoEditModal(photo)"
                    class="btn-icon btn-sm"
                    title="编辑"
                  >
                    <Icon icon="mdi:pencil" />
                  </button>
                  <button
                    type="button"
                    @click="handleDeletePhoto(photo)"
                    class="btn-icon btn-sm btn-danger"
                    title="删除"
                  >
                    <Icon icon="mdi:delete" />
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="empty-photos">暂无照片</div>
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

    <!-- 批量上传模态框 -->
    <div v-if="showBulkUploadModal" class="modal-overlay" @click="closeBulkUploadModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>批量上传照片</h2>
          <button @click="closeBulkUploadModal" class="btn-close">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <div class="modal-form">
          <div class="form-group">
            <label class="form-label">选择照片 *</label>
            <input
              ref="bulkPhotoInput"
              type="file"
              accept="image/*"
              multiple
              @change="handleBulkPhotoChange"
              class="file-input"
            />
            <button
              type="button"
              @click="() => bulkPhotoInput?.click()"
              class="btn btn-secondary"
            >
              选择多张照片
            </button>
            <div v-if="bulkPhotos.length" class="bulk-photos-preview">
              <div
                v-for="(photo, index) in bulkPhotos"
                :key="index"
                class="bulk-photo-item"
              >
                <img :src="photo.preview" :alt="`Photo ${index + 1}`" class="bulk-photo-preview" />
                <button
                  type="button"
                  @click="removeBulkPhoto(index)"
                  class="btn-icon btn-sm btn-danger"
                >
                  <Icon icon="mdi:close" />
                </button>
              </div>
            </div>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeBulkUploadModal" class="btn btn-secondary">
              取消
            </button>
            <button type="button" @click="handleBulkUpload" class="btn btn-primary" :disabled="bulkUploading || bulkPhotos.length === 0">
              {{ bulkUploading ? '上传中...' : `上传 ${bulkPhotos.length} 张照片` }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 照片编辑模态框 -->
    <div v-if="showPhotoModal" class="modal-overlay" @click="closePhotoModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingPhoto ? '编辑照片' : '添加照片' }}</h2>
          <button @click="closePhotoModal" class="btn-close">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <form @submit.prevent="handlePhotoSubmit" class="modal-form">
          <div class="form-group">
            <label class="form-label">照片 *</label>
            <div class="image-upload">
              <img
                v-if="photoForm.imagePreview || (editingPhoto && editingPhoto.image)"
                :src="photoForm.imagePreview || editingPhoto?.image"
                alt="照片预览"
                class="image-preview"
                @click="() => photoInput?.click()"
                title="点击更换照片"
              />
              <div
                v-else
                class="image-placeholder"
                @click="() => photoInput?.click()"
              >
                <Icon icon="mdi:image" />
                <span>点击上传照片</span>
              </div>
              <input
                ref="photoInput"
                type="file"
                accept="image/*"
                @change="handlePhotoImageChange"
                class="file-input"
                :required="!editingPhoto"
              />
              <button
                type="button"
                @click="() => photoInput?.click()"
                class="btn btn-secondary"
              >
                选择照片
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">标题</label>
            <input
              v-model="photoForm.title"
              type="text"
              placeholder="可选"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea
              v-model="photoForm.description"
              placeholder="可选"
              class="form-textarea"
              rows="3"
            />
          </div>
          <div class="form-group">
            <label class="form-label">排序</label>
            <input
              v-model.number="photoForm.order"
              type="number"
              placeholder="0"
              class="form-input"
            />
          </div>
          <div class="form-actions">
            <button type="button" @click="closePhotoModal" class="btn btn-secondary">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="savingPhoto">
              {{ savingPhoto ? '保存中...' : '保存' }}
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
import { photosApi, type Album, type Photo } from '@/api/photos'

const loading = ref(false)
const saving = ref(false)
const savingPhoto = ref(false)
const bulkUploading = ref(false)
const albums = ref<Album[]>([])
const showModal = ref(false)
const showPhotoModal = ref(false)
const showBulkUploadModal = ref(false)
const editingAlbum = ref<Album | null>(null)
const editingPhoto = ref<Photo | null>(null)
const selectedPhotos = ref<number[]>([])
const coverInput = ref<HTMLInputElement | null>(null)
const photoInput = ref<HTMLInputElement | null>(null)
const bulkPhotoInput = ref<HTMLInputElement | null>(null)
const currentPage = ref(1)
const totalPages = ref(1)
const searchKeyword = ref('')
const bulkPhotos = ref<Array<{ file: File; preview: string }>>([])

const form = reactive({
  name: '',
  slug: '',
  description: '',
  cover: null as File | null,
  coverPreview: null as string | null,
  order: 0,
  is_encrypted: false,
  password: '',
})

const photoForm = reactive({
  image: null as File | null,
  imagePreview: null as string | null,
  title: '',
  description: '',
  order: 0,
})

const fetchAlbums = async (page = 1) => {
  loading.value = true
  try {
    const params: any = { page }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const response = await photosApi.getAlbums(params)
    albums.value = response.results || []
    totalPages.value = response.count ? Math.ceil(response.count / 10) : 1
    currentPage.value = page
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch albums:', error)
    }
    alert('加载相册失败，请稍后重试')
    albums.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  clearTimeout((window as any).albumSearchTimer)
  ;(window as any).albumSearchTimer = setTimeout(() => {
    fetchAlbums(1)
  }, 300)
}

const clearSearch = () => {
  searchKeyword.value = ''
  fetchAlbums(1)
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchAlbums(page)
  }
}

const openCreateModal = () => {
  editingAlbum.value = null
  form.name = ''
  form.slug = ''
  form.description = ''
  form.cover = null
  form.coverPreview = null
  form.order = 0
  form.is_encrypted = false
  form.password = ''
  showModal.value = true
}

const openAlbumDetail = async (album: Album) => {
  try {
    const fullAlbum = await photosApi.getAlbum(album.slug)
    editingAlbum.value = fullAlbum
    form.name = fullAlbum.name
    form.slug = fullAlbum.slug
    form.description = fullAlbum.description || ''
    form.order = fullAlbum.order
    form.is_encrypted = fullAlbum.is_encrypted || false
    form.password = ''
    selectedPhotos.value = []
    showModal.value = true
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch album:', error)
    }
    alert('加载相册详情失败')
  }
}

const openEditModal = (album: Album) => {
  openAlbumDetail(album)
}

const closeModal = () => {
  showModal.value = false
  editingAlbum.value = null
}

const handleCoverChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    form.cover = file
    const reader = new FileReader()
    reader.onload = (e) => {
      form.coverPreview = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const handleSubmit = async () => {
  saving.value = true
  try {
    const data: any = {
      name: form.name,
      slug: form.slug || undefined,
      description: form.description || undefined,
      order: form.order,
      is_encrypted: form.is_encrypted,
      password: form.is_encrypted && form.password ? form.password : undefined,
    }
    if (form.cover) {
      data.cover = form.cover
    }

    if (editingAlbum.value) {
      await photosApi.updateAlbum(editingAlbum.value.slug, data)
      alert('相册更新成功')
    } else {
      await photosApi.createAlbum(data)
      alert('相册创建成功')
    }
    closeModal()
    await fetchAlbums(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (album: Album) => {
  if (!confirm(`确定要删除相册《${album.name}》吗？此操作将删除相册中的所有照片，且不可恢复。`)) {
    return
  }
  
  try {
    await photosApi.deleteAlbum(album.slug)
    alert('删除成功')
    await fetchAlbums(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

const openPhotoModal = () => {
  editingPhoto.value = null
  photoForm.image = null
  photoForm.imagePreview = null
  photoForm.title = ''
  photoForm.description = ''
  photoForm.order = editingAlbum.value?.photos?.length || 0
  showPhotoModal.value = true
}

const openPhotoEditModal = (photo: Photo) => {
  editingPhoto.value = photo
  photoForm.image = null
  photoForm.imagePreview = null
  photoForm.title = photo.title || ''
  photoForm.description = photo.description || ''
  photoForm.order = photo.order
  showPhotoModal.value = true
}

const closePhotoModal = () => {
  showPhotoModal.value = false
  editingPhoto.value = null
}

const handlePhotoImageChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    photoForm.image = file
    const reader = new FileReader()
    reader.onload = (e) => {
      photoForm.imagePreview = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const handlePhotoSubmit = async () => {
  if (!editingAlbum.value) {
    alert('请先选择相册')
    return
  }

  savingPhoto.value = true
  try {
    const data: any = {
      album: editingAlbum.value.id,
      title: photoForm.title || undefined,
      description: photoForm.description || undefined,
      order: photoForm.order,
    }
    if (photoForm.image) {
      data.image = photoForm.image
    }

    if (editingPhoto.value) {
      await photosApi.updatePhoto(editingPhoto.value.id, data)
      alert('照片更新成功')
    } else {
      await photosApi.createPhoto(data)
      alert('照片添加成功')
    }
    closePhotoModal()
    // 重新加载相册详情
    if (editingAlbum.value) {
      const fullAlbum = await photosApi.getAlbum(editingAlbum.value.slug)
      editingAlbum.value = fullAlbum
    }
    await fetchAlbums(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  } finally {
    savingPhoto.value = false
  }
}

const togglePhotoSelection = (photoId: number) => {
  const index = selectedPhotos.value.indexOf(photoId)
  if (index > -1) {
    selectedPhotos.value.splice(index, 1)
  } else {
    selectedPhotos.value.push(photoId)
  }
}

const handleDeletePhoto = async (photo: Photo) => {
  if (!confirm('确定要删除这张照片吗？')) {
    return
  }
  
  try {
    await photosApi.deletePhoto(photo.id)
    alert('删除成功')
    // 重新加载相册详情
    if (editingAlbum.value) {
      const fullAlbum = await photosApi.getAlbum(editingAlbum.value.slug)
      editingAlbum.value = fullAlbum
    }
    await fetchAlbums(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

const handleBulkDelete = async () => {
  if (selectedPhotos.value.length === 0) {
    return
  }
  
  if (!confirm(`确定要删除选中的 ${selectedPhotos.value.length} 张照片吗？`)) {
    return
  }
  
  try {
    await photosApi.bulkDeletePhotos(selectedPhotos.value)
    alert('批量删除成功')
    selectedPhotos.value = []
    // 重新加载相册详情
    if (editingAlbum.value) {
      const fullAlbum = await photosApi.getAlbum(editingAlbum.value.slug)
      editingAlbum.value = fullAlbum
    }
    await fetchAlbums(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

const openBulkUploadModal = () => {
  bulkPhotos.value = []
  showBulkUploadModal.value = true
}

const closeBulkUploadModal = () => {
  showBulkUploadModal.value = false
  bulkPhotos.value = []
}

const handleBulkPhotoChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    Array.from(files).forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          bulkPhotos.value.push({
            file,
            preview: e.target?.result as string
          })
        }
        reader.readAsDataURL(file)
      }
    })
  }
}

const removeBulkPhoto = (index: number) => {
  bulkPhotos.value.splice(index, 1)
}

const handleBulkUpload = async () => {
  if (!editingAlbum.value || bulkPhotos.value.length === 0) {
    return
  }
  
  bulkUploading.value = true
  try {
    let order = editingAlbum.value.photos?.length || 0
    for (const photo of bulkPhotos.value) {
      await photosApi.createPhoto({
        album: editingAlbum.value.id,
        image: photo.file,
        order: order++
      })
    }
    alert(`成功上传 ${bulkPhotos.value.length} 张照片`)
    closeBulkUploadModal()
    // 重新加载相册详情
    if (editingAlbum.value) {
      const fullAlbum = await photosApi.getAlbum(editingAlbum.value.slug)
      editingAlbum.value = fullAlbum
    }
    await fetchAlbums(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '上传失败'
    alert(`上传失败: ${message}`)
  } finally {
    bulkUploading.value = false
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchAlbums(1)
})
</script>

<style scoped>
.admin-photos {
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
  font-size: 12px;
}

.albums-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.album-card {
  background: var(--card-bg, white);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.album-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.album-cover {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  cursor: pointer;
}

.cover-image {
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
  color: var(--text-secondary, #666);
  font-size: 48px;
}

.encrypted-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.album-info {
  padding: 16px;
}

.album-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-color, #333);
}

.album-description {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.album-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary, #666);
  margin-bottom: 12px;
}

.album-actions {
  display: flex;
  gap: 8px;
  padding: 0 16px 16px;
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

.btn-icon.btn-sm {
  padding: 4px;
  font-size: 12px;
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
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal-content.large {
  max-width: 900px;
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

.image-upload {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.image-preview,
.image-placeholder {
  width: 200px;
  height: 200px;
  border-radius: 8px;
  border: 2px dashed var(--border-color, #e5e5e5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #666);
  cursor: pointer;
  transition: all 0.3s;
}

.image-placeholder:hover {
  border-color: var(--primary-color, #FE9600);
  background: var(--bg-secondary, #f5f5f5);
  color: var(--primary-color, #FE9600);
}

.image-preview {
  border: 2px solid var(--border-color, #e5e5e5);
  object-fit: cover;
  position: relative;
}

.image-preview:hover {
  border-color: var(--primary-color, #FE9600);
  opacity: 0.9;
}

.image-preview::after {
  content: '点击更换';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.image-preview:hover::after {
  opacity: 1;
}

.file-input {
  display: none;
}

.photos-section {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid var(--border-color, #e5e5e5);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.photo-item {
  position: relative;
  border-radius: 4px;
  overflow: hidden;
}

.photo-thumb {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.photo-actions {
  position: absolute;
  top: 4px;
  right: 4px;
  display: flex;
  gap: 4px;
}

.empty-photos {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary, #666);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

/* 搜索和筛选 */
.filters {
  margin-bottom: 32px;
  margin-top: 8px;
}

.search-wrapper {
  position: relative;
  max-width: 500px;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 16px;
  color: var(--text-secondary, #999);
  font-size: 20px;
  pointer-events: none;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 48px;
  border: 2px solid var(--border-color, #e5e5e5);
  border-radius: 8px;
  font-size: 14px;
  background: var(--card-bg, white);
  color: var(--text-color, #333);
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.search-input::placeholder {
  color: var(--text-secondary, #999);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color, #FE9600);
  box-shadow: 0 0 0 3px rgba(254, 150, 0, 0.1);
}

.search-input:hover:not(:focus) {
  border-color: var(--primary-color, #FE9600);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.search-clear {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: var(--text-secondary, #999);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s;
  z-index: 1;
}

.search-clear:hover {
  color: var(--text-color, #333);
}

.search-clear :deep(svg) {
  font-size: 20px;
}
</style>
