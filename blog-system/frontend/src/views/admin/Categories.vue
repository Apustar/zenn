<template>
  <div class="admin-categories">
    <div class="page-header">
      <h1 class="page-title">分类管理</h1>
      <button @click="openCreateModal" class="btn btn-primary">
        <Icon icon="mdi:plus" />
        新建分类
      </button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="categories.length" class="categories-list">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-item"
      >
        <div class="category-info">
          <h3 class="category-name">{{ category.name }}</h3>
          <p v-if="category.description" class="category-description">
            {{ category.description }}
          </p>
          <div class="category-meta">
            <span>文章数: {{ category.post_count || 0 }}</span>
            <span>创建时间: {{ formatDate(category.created_at) }}</span>
          </div>
        </div>
        <div class="category-actions">
          <button @click="openEditModal(category)" class="btn-icon">
            <Icon icon="mdi:pencil" />
          </button>
          <button @click="handleDelete(category)" class="btn-icon btn-danger">
            <Icon icon="mdi:delete" />
          </button>
        </div>
      </div>
    </div>
    <div v-else class="empty">暂无分类</div>

    <!-- 创建/编辑模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingCategory ? '编辑分类' : '新建分类' }}</h2>
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
              placeholder="请输入分类名称"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea
              v-model="form.description"
              placeholder="请输入分类描述"
              class="form-textarea"
              rows="3"
            />
          </div>
          <div class="form-group">
            <label class="form-label">排序</label>
            <input
              v-model.number="form.order"
              type="number"
              placeholder="数字越小越靠前"
              class="form-input"
            />
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
import { categoriesApi, type Category } from '@/api/categories'

const loading = ref(false)
const saving = ref(false)
const categories = ref<Category[]>([])
const showModal = ref(false)
const editingCategory = ref<Category | null>(null)

const form = reactive({
  name: '',
  description: '',
  order: 0,
})

const fetchCategories = async () => {
  loading.value = true
  try {
    const cats = await categoriesApi.getCategories()
    categories.value = Array.isArray(cats) ? cats : (cats as any).results || []
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch categories:', error)
    }
    alert('加载分类失败，请稍后重试')
    categories.value = []
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingCategory.value = null
  form.name = ''
  form.description = ''
  form.order = 0
  showModal.value = true
}

const openEditModal = (category: Category) => {
  editingCategory.value = category
  form.name = category.name
  form.description = category.description || ''
  form.order = category.order || 0
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingCategory.value = null
}

const handleSubmit = async () => {
  saving.value = true
  try {
    if (editingCategory.value) {
      await categoriesApi.updateCategory(editingCategory.value.slug, form)
      alert('分类更新成功')
    } else {
      await categoriesApi.createCategory(form)
      alert('分类创建成功')
    }
    closeModal()
    await fetchCategories()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (category: Category) => {
  if (!confirm(`确定要删除分类《${category.name}》吗？\n删除后该分类下的文章将不受影响。`)) {
    return
  }
  
  try {
    await categoriesApi.deleteCategory(category.slug)
    alert('删除成功')
    await fetchCategories()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.admin-categories {
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

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-item {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.category-info {
  flex: 1;
}

.category-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-color, #333);
}

.category-description {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin: 0 0 8px 0;
}

.category-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary, #999);
}

.category-actions {
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

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}
</style>
