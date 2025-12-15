<template>
  <div class="admin-tags">
    <div class="page-header">
      <h1 class="page-title">标签管理</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <Icon icon="mdi:plus" />
        新建标签
      </button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="tags.length" class="tags-grid">
      <div
        v-for="tag in tags"
        :key="tag.id"
        class="tag-item"
        :style="{ borderLeftColor: tag.color }"
      >
        <div class="tag-info">
          <h3 class="tag-name">{{ tag.name }}</h3>
          <p v-if="tag.description" class="tag-description">
            {{ tag.description }}
          </p>
          <div class="tag-meta">
            <span>文章数: {{ tag.post_count || 0 }}</span>
          </div>
        </div>
        <div class="tag-actions">
          <button @click="openEditModal(tag)" class="btn-icon">
            <Icon icon="mdi:pencil" />
          </button>
          <button @click="handleDelete(tag)" class="btn-icon btn-danger">
            <Icon icon="mdi:delete" />
          </button>
        </div>
      </div>
    </div>
    <div v-else class="empty">暂无标签</div>

    <!-- 创建/编辑模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingTag ? '编辑标签' : '新建标签' }}</h2>
          <button @click="closeModal" class="btn-close">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-group">
            <label class="form-label">名称 *</label>
            <input
              v-model="form.name"
              type="text"
              required
              placeholder="请输入标签名称"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea
              v-model="form.description"
              placeholder="请输入标签描述"
              class="form-textarea"
              rows="3"
            />
          </div>
          <div class="form-group">
            <label class="form-label">颜色</label>
            <div class="color-input-group">
              <input
                v-model="form.color"
                type="color"
                class="color-picker"
              />
              <input
                v-model="form.color"
                type="text"
                placeholder="#FE9600"
                class="form-input color-text"
                pattern="^#[0-9A-Fa-f]{6}$"
              />
            </div>
            <p class="form-hint">选择标签显示的颜色</p>
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
import { tagsApi, type Tag } from '@/api/tags'

const loading = ref(false)
const saving = ref(false)
const tags = ref<Tag[]>([])
const showModal = ref(false)
const editingTag = ref<Tag | null>(null)

const form = reactive({
  name: '',
  description: '',
  color: '#FE9600',
})

const fetchTags = async () => {
  loading.value = true
  try {
    const tgs = await tagsApi.getTags()
    tags.value = Array.isArray(tgs) ? tgs : (tgs as any).results || []
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch tags:', error)
    }
    alert('加载标签失败，请稍后重试')
    tags.value = []
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingTag.value = null
  form.name = ''
  form.description = ''
  form.color = '#FE9600'
  showModal.value = true
}

const openEditModal = (tag: Tag) => {
  editingTag.value = tag
  form.name = tag.name
  form.description = tag.description || ''
  form.color = tag.color || '#FE9600'
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingTag.value = null
}

const handleSubmit = async () => {
  saving.value = true
  try {
    if (editingTag.value) {
      await tagsApi.updateTag(editingTag.value.slug, form)
      alert('标签更新成功')
    } else {
      await tagsApi.createTag(form)
      alert('标签创建成功')
    }
    closeModal()
    await fetchTags()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (tag: Tag) => {
  if (!confirm(`确定要删除标签《${tag.name}》吗？\n删除后该标签将从所有文章中移除。`)) {
    return
  }
  
  try {
    await tagsApi.deleteTag(tag.slug)
    alert('删除成功')
    await fetchTags()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

onMounted(() => {
  fetchTags()
})
</script>

<style scoped>
.admin-tags {
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

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.tag-item {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tag-info {
  flex: 1;
}

.tag-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-color, #333);
}

.tag-description {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin: 0 0 8px 0;
}

.tag-meta {
  font-size: 12px;
  color: var(--text-secondary, #999);
}

.tag-actions {
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

.color-input-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

.color-picker {
  width: 60px;
  height: 40px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  cursor: pointer;
}

.color-text {
  flex: 1;
}

.form-hint {
  margin: 8px 0 0 0;
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}
</style>
