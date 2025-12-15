<template>
  <div class="admin-moments">
    <div class="page-header">
      <h1 class="page-title">瞬间管理</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <Icon icon="mdi:plus" />
        新建瞬间
      </button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="moments.length" class="moments-list">
      <div
        v-for="moment in moments"
        :key="moment.id"
        class="moment-item"
      >
        <div class="moment-content">
          <div class="moment-text">{{ moment.content }}</div>
          <div v-if="moment.images && moment.images.length" class="moment-images">
            <img
              v-for="(img, idx) in moment.images"
              :key="idx"
              :src="img"
              :alt="`图片 ${idx + 1}`"
              class="moment-image"
            />
          </div>
          <div class="moment-meta">
            <span>{{ formatDate(moment.created_at) }}</span>
            <span v-if="moment.location" class="location">
              <Icon icon="mdi:map-marker" />
              {{ moment.location }}
            </span>
            <span class="visibility" :class="moment.visibility">
              {{ moment.visibility === 'public' ? '公开' : '私密' }}
            </span>
          </div>
        </div>
        <div class="moment-actions">
          <button @click="openEditModal(moment)" class="btn-icon">
            <Icon icon="mdi:pencil" />
          </button>
          <button @click="handleDelete(moment)" class="btn-icon btn-danger">
            <Icon icon="mdi:delete" />
          </button>
        </div>
      </div>
    </div>
    <div v-else class="empty">暂无瞬间</div>

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

    <!-- 创建/编辑模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingMoment ? '编辑瞬间' : '新建瞬间' }}</h2>
          <button @click="closeModal" class="btn-close">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-group">
            <label class="form-label">内容 *</label>
            <textarea
              v-model="form.content"
              required
              placeholder="分享你的瞬间..."
              class="form-textarea"
              rows="5"
            />
          </div>
          <div class="form-group">
            <label class="form-label">位置</label>
            <input
              v-model="form.location"
              type="text"
              placeholder="可选"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">可见性</label>
            <select v-model="form.visibility" class="form-input">
              <option value="public">公开</option>
              <option value="private">私密</option>
            </select>
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
import { momentsApi, type Moment } from '@/api/moments'

const loading = ref(false)
const saving = ref(false)
const moments = ref<Moment[]>([])
const currentPage = ref(1)
const totalPages = ref(1)
const showModal = ref(false)
const editingMoment = ref<Moment | null>(null)

const form = reactive({
  content: '',
  location: '',
  visibility: 'public' as 'public' | 'private',
})

const fetchMoments = async (page = 1) => {
  loading.value = true
  try {
    const response = await momentsApi.getMoments({ page })
    moments.value = response.results || []
    totalPages.value = response.count ? Math.ceil(response.count / 10) : 1
    currentPage.value = page
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch moments:', error)
    }
    alert('加载瞬间失败，请稍后重试')
    moments.value = []
  } finally {
    loading.value = false
  }
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchMoments(page)
  }
}

const openCreateModal = () => {
  editingMoment.value = null
  form.content = ''
  form.location = ''
  form.visibility = 'public'
  showModal.value = true
}

const openEditModal = (moment: Moment) => {
  editingMoment.value = moment
  form.content = moment.content
  form.location = moment.location || ''
  form.visibility = moment.visibility
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingMoment.value = null
}

const handleSubmit = async () => {
  saving.value = true
  try {
    if (editingMoment.value) {
      await momentsApi.updateMoment(editingMoment.value.id, form)
      alert('瞬间更新成功')
    } else {
      await momentsApi.createMoment(form)
      alert('瞬间创建成功')
    }
    closeModal()
    await fetchMoments(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (moment: Moment) => {
  if (!confirm(`确定要删除这条瞬间吗？`)) {
    return
  }
  
  try {
    await momentsApi.deleteMoment(moment.id)
    alert('删除成功')
    await fetchMoments(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchMoments()
})
</script>

<style scoped>
.admin-moments {
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

.moments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.moment-item {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.moment-content {
  flex: 1;
}

.moment-text {
  margin-bottom: 12px;
  line-height: 1.6;
  color: var(--text-color, #333);
  white-space: pre-wrap;
  word-break: break-word;
}

.moment-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.moment-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
}

.moment-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary, #666);
  align-items: center;
}

.location {
  display: flex;
  align-items: center;
  gap: 4px;
}

.visibility {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.visibility.public {
  background: #e8f5e9;
  color: #2e7d32;
}

.visibility.private {
  background: #fff3e0;
  color: #e65100;
}

.moment-actions {
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

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: var(--bg-secondary, #f5f5f5);
  border-color: var(--primary-color, #FE9600);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-secondary, #666);
  font-size: 14px;
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

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}
</style>
