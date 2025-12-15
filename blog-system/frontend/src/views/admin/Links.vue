<template>
  <div class="admin-links">
    <div class="page-header">
      <h1 class="page-title">友链管理</h1>
      <div class="header-actions">
        <button @click="openCategoryModal" class="btn btn-secondary">
          <Icon icon="mdi:folder-plus" />
          添加分类
        </button>
        <button @click="openLinkModal" class="btn btn-primary">
          <Icon icon="mdi:plus" />
          添加友链
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="categories.length" class="categories-list">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-section"
      >
        <div class="category-header">
          <h2 class="category-name">{{ category.name }}</h2>
          <div class="category-actions">
            <button @click="openCategoryModal(category)" class="btn-icon">
              <Icon icon="mdi:pencil" />
            </button>
            <button @click="handleDeleteCategory(category)" class="btn-icon btn-danger">
              <Icon icon="mdi:delete" />
            </button>
          </div>
        </div>
        <div v-if="category.links && category.links.length" class="links-grid">
          <div
            v-for="link in category.links"
            :key="link.id"
            class="link-item"
          >
            <div class="link-logo">
              <img
                v-if="link.logo"
                :src="link.logo"
                :alt="link.name"
                class="logo-image"
              />
              <div v-else class="logo-placeholder">
                <Icon icon="mdi:link" />
              </div>
            </div>
            <div class="link-info">
              <h3 class="link-name">{{ link.name }}</h3>
              <a :href="link.url" target="_blank" class="link-url" @click.stop>
                {{ link.url }}
              </a>
              <p v-if="link.description" class="link-description">
                {{ link.description }}
              </p>
              <div class="link-meta">
                <span class="order">排序: {{ link.order }}</span>
                <span v-if="link.is_visible === false" class="badge badge-hidden">隐藏</span>
              </div>
            </div>
            <div class="link-actions">
              <button @click="openLinkModal(link, category)" class="btn-icon">
                <Icon icon="mdi:pencil" />
              </button>
              <button @click="handleDeleteLink(link)" class="btn-icon btn-danger">
                <Icon icon="mdi:delete" />
              </button>
            </div>
          </div>
        </div>
        <div v-else class="empty-category">该分类下暂无友链</div>
      </div>
    </div>
    <div v-else class="empty">暂无友链分类</div>

    <!-- 分类编辑模态框 -->
    <div v-if="showCategoryModal" class="modal-overlay" @click="closeCategoryModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingCategory ? '编辑分类' : '添加分类' }}</h2>
          <button @click="closeCategoryModal" class="btn-close">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <form @submit.prevent="handleSaveCategory" class="modal-form">
          <div class="form-group">
            <label class="form-label">分类名称 *</label>
            <input
              v-model="categoryForm.name"
              type="text"
              required
              placeholder="请输入分类名称"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">排序</label>
            <input
              v-model.number="categoryForm.order"
              type="number"
              placeholder="数字越小越靠前"
              class="form-input"
            />
          </div>
          <div class="form-actions">
            <button type="button" @click="closeCategoryModal" class="btn btn-secondary">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="savingCategory">
              {{ savingCategory ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 友链编辑模态框 -->
    <div v-if="showLinkModal" class="modal-overlay" @click="closeLinkModal">
      <div class="modal-content modal-large" @click.stop>
        <div class="modal-header">
          <h2>{{ editingLink ? '编辑友链' : '添加友链' }}</h2>
          <button @click="closeLinkModal" class="btn-close">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <form @submit.prevent="handleSaveLink" class="modal-form">
          <div class="form-group">
            <label class="form-label">友链名称 *</label>
            <input
              v-model="linkForm.name"
              type="text"
              required
              placeholder="请输入友链名称"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">链接地址 *</label>
            <input
              v-model="linkForm.url"
              type="url"
              required
              placeholder="https://example.com"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">分类 *</label>
            <select v-model.number="linkForm.category" required class="form-input">
              <option value="">请选择分类</option>
              <option
                v-for="cat in categories"
                :key="cat.id"
                :value="cat.id"
              >
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea
              v-model="linkForm.description"
              placeholder="请输入友链描述（可选）"
              class="form-textarea"
              rows="3"
            />
          </div>
          <div class="form-group">
            <label class="form-label">Logo</label>
            <div class="logo-upload">
              <img
                v-if="logoPreview || editingLink?.logo"
                :src="logoPreview || editingLink?.logo"
                alt="Logo预览"
                class="logo-preview"
              />
              <div v-else class="logo-placeholder-small">
                <Icon icon="mdi:image" />
              </div>
              <div class="logo-actions">
                <input
                  ref="logoInput"
                  type="file"
                  accept="image/*"
                  @change="handleLogoChange"
                  class="file-input"
                />
                <button
                  type="button"
                  @click="() => (logoInput as any)?.click()"
                  class="btn btn-secondary btn-sm"
                >
                  选择Logo
                </button>
                <button
                  v-if="logoPreview || editingLink?.logo"
                  type="button"
                  @click="removeLogo"
                  class="btn btn-danger btn-sm"
                >
                  移除
                </button>
              </div>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">排序</label>
              <input
                v-model.number="linkForm.order"
                type="number"
                placeholder="数字越小越靠前"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="linkForm.is_visible"
                  type="checkbox"
                />
                <span>显示</span>
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeLinkModal" class="btn btn-secondary">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="savingLink">
              {{ savingLink ? '保存中...' : '保存' }}
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
import { linksApi, type LinkCategory, type Link } from '@/api/links'

const loading = ref(false)
const savingCategory = ref(false)
const savingLink = ref(false)
const categories = ref<LinkCategory[]>([])
const showCategoryModal = ref(false)
const showLinkModal = ref(false)
const editingCategory = ref<LinkCategory | null>(null)
const editingLink = ref<Link | null>(null)
const linkCategory = ref<LinkCategory | null>(null)
const logoInput = ref<HTMLInputElement | null>(null)
const logoPreview = ref<string | null>(null)

const categoryForm = reactive({
  name: '',
  order: 0,
})

const linkForm = reactive({
  name: '',
  url: '',
  category: null as number | null,
  description: '',
  logo: null as File | null,
  order: 0,
  is_visible: true,
})

const fetchCategories = async () => {
  loading.value = true
  try {
    const cats = await linksApi.getLinkCategories()
    categories.value = Array.isArray(cats) ? cats : []
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch link categories:', error)
    }
    alert('加载友链分类失败，请稍后重试')
    categories.value = []
  } finally {
    loading.value = false
  }
}

const openCategoryModal = (category?: LinkCategory) => {
  editingCategory.value = category || null
  if (category) {
    categoryForm.name = category.name
    categoryForm.order = category.order
  } else {
    categoryForm.name = ''
    categoryForm.order = 0
  }
  showCategoryModal.value = true
}

const closeCategoryModal = () => {
  showCategoryModal.value = false
  editingCategory.value = null
}

const handleSaveCategory = async () => {
  savingCategory.value = true
  try {
    if (editingCategory.value) {
      await linksApi.updateLinkCategory(editingCategory.value.id, categoryForm)
      alert('分类更新成功')
    } else {
      await linksApi.createLinkCategory(categoryForm)
      alert('分类创建成功')
    }
    closeCategoryModal()
    await fetchCategories()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  } finally {
    savingCategory.value = false
  }
}

const handleDeleteCategory = async (category: LinkCategory) => {
  if (!confirm(`确定要删除分类《${category.name}》吗？\n该分类下的所有友链也将被删除。`)) {
    return
  }
  
  try {
    await linksApi.deleteLinkCategory(category.id)
    alert('删除成功')
    await fetchCategories()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

const openLinkModal = (link?: Link, category?: LinkCategory) => {
  editingLink.value = link || null
  linkCategory.value = category || null
  
  if (link) {
    linkForm.name = link.name
    linkForm.url = link.url
    linkForm.category = link.category || null
    linkForm.description = link.description || ''
    linkForm.order = link.order
    linkForm.is_visible = link.is_visible !== false
    linkForm.logo = null
  } else {
    linkForm.name = ''
    linkForm.url = ''
    linkForm.category = category?.id || null
    linkForm.description = ''
    linkForm.order = 0
    linkForm.is_visible = true
    linkForm.logo = null
  }
  logoPreview.value = null
  showLinkModal.value = true
}

const closeLinkModal = () => {
  showLinkModal.value = false
  editingLink.value = null
  linkCategory.value = null
  linkForm.logo = null
  logoPreview.value = null
  if (logoInput.value) logoInput.value.value = ''
}

const handleLogoChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    linkForm.logo = file
    const reader = new FileReader()
    reader.onload = (e) => {
      logoPreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const removeLogo = () => {
  linkForm.logo = null
  logoPreview.value = null
  if (logoInput.value) logoInput.value.value = ''
}

const handleSaveLink = async () => {
  savingLink.value = true
  try {
    const formData = new FormData()
    formData.append('name', linkForm.name)
    formData.append('url', linkForm.url)
    if (linkForm.category) {
      formData.append('category', linkForm.category.toString())
    }
    if (linkForm.description) {
      formData.append('description', linkForm.description)
    }
    if (linkForm.logo) {
      formData.append('logo', linkForm.logo)
    }
    formData.append('order', linkForm.order.toString())
    formData.append('is_visible', linkForm.is_visible.toString())

    if (editingLink.value) {
      await linksApi.updateLink(editingLink.value.id, formData)
      alert('友链更新成功')
    } else {
      await linksApi.createLink(formData)
      alert('友链创建成功')
    }
    closeLinkModal()
    await fetchCategories()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  } finally {
    savingLink.value = false
  }
}

const handleDeleteLink = async (link: Link) => {
  if (!confirm(`确定要删除友链《${link.name}》吗？`)) {
    return
  }
  
  try {
    await linksApi.deleteLink(link.id)
    alert('删除成功')
    await fetchCategories()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.admin-links {
  max-width: 1200px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: var(--text-color, #333);
}

.header-actions {
  display: flex;
  gap: 12px;
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

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.category-section {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border-color, #e5e5e5);
}

.category-name {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: var(--text-color, #333);
}

.category-actions {
  display: flex;
  gap: 8px;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.link-item {
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  gap: 12px;
  transition: all 0.3s;
}

.link-item:hover {
  background: var(--border-color, #e5e5e5);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.link-logo {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.logo-placeholder {
  width: 100%;
  height: 100%;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #999);
  font-size: 24px;
}

.link-info {
  flex: 1;
  min-width: 0;
}

.link-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: var(--text-color, #333);
}

.link-url {
  display: block;
  font-size: 12px;
  color: var(--primary-color, #FE9600);
  text-decoration: none;
  margin-bottom: 8px;
  word-break: break-all;
}

.link-url:hover {
  text-decoration: underline;
}

.link-description {
  font-size: 13px;
  color: var(--text-secondary, #666);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.link-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 12px;
  color: var(--text-secondary, #999);
}

.badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.badge-hidden {
  background: #fff3e0;
  color: #e65100;
}

.link-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.btn-icon {
  padding: 6px;
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

.empty-category {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary, #666);
  font-size: 14px;
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

.logo-upload {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.logo-preview {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid var(--border-color, #e5e5e5);
}

.logo-placeholder-small {
  width: 100px;
  height: 100px;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #999);
  font-size: 32px;
  border: 1px solid var(--border-color, #e5e5e5);
}

.logo-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-input {
  display: none;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding-top: 28px;
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
