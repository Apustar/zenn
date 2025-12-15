<template>
  <div class="admin-settings">
    <div class="settings-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab-button"
        :class="{ active: activeTab === tab.id }"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 站点设置 -->
    <div v-if="activeTab === 'site'" class="settings-content">
      <h2 class="section-title">站点设置</h2>
      <form @submit.prevent="handleSaveSiteSettings" class="settings-form">
        <div class="form-group">
          <label class="form-label">站点名称 *</label>
          <input
            v-model="siteForm.site_name"
            type="text"
            required
            placeholder="请输入站点名称"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">站点描述</label>
          <textarea
            v-model="siteForm.site_description"
            placeholder="请输入站点描述"
            class="form-textarea"
            rows="3"
          />
        </div>

        <div class="form-group">
          <label class="form-label">站点关键词</label>
          <input
            v-model="siteForm.site_keywords"
            type="text"
            placeholder="关键词之间用逗号分隔"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">站点图标</label>
          <div class="icon-upload">
            <img
              v-if="siteForm.site_icon_url || siteIconPreview"
              :src="siteIconPreview || siteForm.site_icon_url"
              alt="站点图标"
              class="icon-preview"
            />
            <div v-else class="icon-placeholder">
              <Icon icon="mdi:image" />
              <span>点击上传图标</span>
            </div>
            <input
              ref="iconInput"
              type="file"
              accept="image/*"
              @change="handleIconChange"
              class="file-input"
            />
            <button
              type="button"
              @click="() => (iconInput as any)?.click()"
              class="btn btn-secondary"
            >
              选择图标
            </button>
            <button
              v-if="siteForm.site_icon_url || siteIconPreview"
              type="button"
              @click="removeIcon"
              class="btn btn-danger"
            >
              移除
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">关于页面内容</label>
          <textarea
            v-model="siteForm.about_content"
            placeholder="支持 Markdown 格式"
            class="form-textarea"
            rows="10"
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? '保存中...' : '保存设置' }}
          </button>
        </div>
      </form>
    </div>

    <!-- 导航菜单设置 -->
    <div v-if="activeTab === 'navigation'" class="settings-content">
      <div class="section-header">
        <h2 class="section-title">导航菜单</h2>
        <button @click="openNavigationModal" class="btn btn-primary">
          <Icon icon="mdi:plus" />
          添加菜单项
        </button>
      </div>

      <div v-if="loadingNav" class="loading">加载中...</div>
      <div v-else-if="navigationItems.length" class="navigation-list">
        <div
          v-for="item in navigationItems"
          :key="item.id"
          class="navigation-item"
        >
          <div class="item-info">
            <span class="item-name">{{ item.name }}</span>
            <span class="item-url">{{ item.url }}</span>
            <div class="item-badges">
              <span v-if="item.is_builtin" class="badge badge-builtin">系统内置</span>
              <span v-if="!item.is_visible" class="badge badge-hidden">隐藏</span>
              <span v-if="!item.is_accessible" class="badge badge-inaccessible">不可访问</span>
            </div>
          </div>
          <div class="item-actions">
            <button
              @click="openNavigationModal(item)"
              class="btn-icon"
              :disabled="item.is_builtin"
            >
              <Icon icon="mdi:pencil" />
            </button>
            <button
              @click="handleDeleteNavigation(item)"
              class="btn-icon btn-danger"
              :disabled="item.is_builtin"
            >
              <Icon icon="mdi:delete" />
            </button>
          </div>
        </div>
      </div>
      <div v-else class="empty">暂无导航菜单</div>

      <!-- 导航菜单编辑模态框 -->
      <div v-if="showNavModal" class="modal-overlay" @click="closeNavModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2>{{ editingNavItem ? '编辑菜单项' : '添加菜单项' }}</h2>
            <button @click="closeNavModal" class="btn-close">
              <Icon icon="mdi:close" />
            </button>
          </div>
          <form @submit.prevent="handleSaveNavigation" class="modal-form">
            <div class="form-group">
              <label class="form-label">菜单名称 *</label>
              <input
                v-model="navForm.name"
                type="text"
                required
                placeholder="请输入菜单名称"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="form-label">链接地址 *</label>
              <input
                v-model="navForm.url"
                type="text"
                required
                placeholder="/page/about"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="form-label">排序</label>
              <input
                v-model.number="navForm.order"
                type="number"
                placeholder="数字越小越靠前"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="navForm.is_visible"
                  type="checkbox"
                />
                <span>在导航栏显示</span>
              </label>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="navForm.is_accessible"
                  type="checkbox"
                />
                <span>允许访问（设为否时访问会显示404）</span>
              </label>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeNavModal" class="btn btn-secondary">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="savingNav">
                {{ savingNav ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Icon } from '@iconify/vue'
import { settingsApi, navigationApi, type SiteSettings, type NavigationItem } from '@/api/settings'

const activeTab = ref<'site' | 'navigation'>('site')
const tabs = [
  { id: 'site', label: '站点设置' },
  { id: 'navigation', label: '导航菜单' },
]

const loading = ref(false)
const saving = ref(false)
const loadingNav = ref(false)
const savingNav = ref(false)
const siteForm = reactive<Partial<SiteSettings> & { site_icon?: File }>({
  site_name: '',
  site_description: '',
  site_keywords: '',
  about_content: '',
})
const siteIconPreview = ref<string | null>(null)
const iconInput = ref<HTMLInputElement | null>(null)

const navigationItems = ref<NavigationItem[]>([])
const showNavModal = ref(false)
const editingNavItem = ref<NavigationItem | null>(null)
const navForm = reactive({
  name: '',
  url: '',
  order: 0,
  is_visible: true,
  is_accessible: true,
})

const fetchSiteSettings = async () => {
  loading.value = true
  try {
    const settings = await settingsApi.getSettings()
    siteForm.site_name = settings.site_name
    siteForm.site_description = settings.site_description || ''
    siteForm.site_keywords = settings.site_keywords || ''
    siteForm.about_content = settings.about_content || ''
    siteForm.site_icon_url = settings.site_icon_url
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch site settings:', error)
    }
    alert('加载站点设置失败')
  } finally {
    loading.value = false
  }
}

const handleIconChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    siteForm.site_icon = file
    const reader = new FileReader()
    reader.onload = (e) => {
      siteIconPreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const removeIcon = () => {
  siteForm.site_icon = undefined
  siteIconPreview.value = null
  if (iconInput.value) {
    iconInput.value.value = ''
  }
}

const handleSaveSiteSettings = async () => {
  saving.value = true
  try {
    await settingsApi.updateSettings(siteForm)
    alert('设置保存成功')
    await fetchSiteSettings()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '保存失败'
    alert(`保存失败: ${message}`)
  } finally {
    saving.value = false
  }
}

const fetchNavigationItems = async () => {
  loadingNav.value = true
  try {
    // 管理员需要查看所有菜单项（包括隐藏的）
    // 这里需要调用一个管理员专用的 API，或者修改现有 API
    const items = await navigationApi.getNavigationItems()
    navigationItems.value = items
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch navigation items:', error)
    }
    alert('加载导航菜单失败')
    navigationItems.value = []
  } finally {
    loadingNav.value = false
  }
}

const openNavigationModal = (item?: NavigationItem) => {
  editingNavItem.value = item || null
  if (item) {
    navForm.name = item.name
    navForm.url = item.url
    navForm.order = item.order
    navForm.is_visible = item.is_visible
    navForm.is_accessible = item.is_accessible
  } else {
    navForm.name = ''
    navForm.url = ''
    navForm.order = 0
    navForm.is_visible = true
    navForm.is_accessible = true
  }
  showNavModal.value = true
}

const closeNavModal = () => {
  showNavModal.value = false
  editingNavItem.value = null
}

const handleSaveNavigation = async () => {
  savingNav.value = true
  try {
    if (editingNavItem.value) {
      await navigationApi.updateNavigationItem(editingNavItem.value.id, navForm)
      alert('菜单项更新成功')
    } else {
      await navigationApi.createNavigationItem(navForm)
      alert('菜单项创建成功')
    }
    closeNavModal()
    await fetchNavigationItems()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  } finally {
    savingNav.value = false
  }
}

const handleDeleteNavigation = async (item: NavigationItem) => {
  if (!confirm(`确定要删除菜单项《${item.name}》吗？`)) {
    return
  }
  
  try {
    await navigationApi.deleteNavigationItem(item.id)
    alert('删除成功')
    await fetchNavigationItems()
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

onMounted(() => {
  fetchSiteSettings()
  fetchNavigationItems()
})
</script>

<style scoped>
.admin-settings {
  max-width: 1200px;
}

.settings-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--border-color, #e5e5e5);
}

.tab-button {
  padding: 12px 24px;
  border: none;
  background: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary, #666);
  transition: all 0.3s;
}

.tab-button:hover {
  color: var(--primary-color, #FE9600);
}

.tab-button.active {
  color: var(--primary-color, #FE9600);
  border-bottom-color: var(--primary-color, #FE9600);
}

.settings-content {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 24px 0;
  color: var(--text-color, #333);
}

.settings-form {
  max-width: 800px;
}

.form-group {
  margin-bottom: 24px;
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

.icon-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-preview,
.icon-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  border: 2px dashed var(--border-color, #e5e5e5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #666);
}

.icon-preview {
  border: none;
  object-fit: cover;
}

.file-input {
  display: none;
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
  margin-top: 32px;
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

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.navigation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.navigation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-name {
  font-weight: 600;
  color: var(--text-color, #333);
}

.item-url {
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.item-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge-builtin {
  background: #e3f2fd;
  color: #1976d2;
}

.badge-hidden {
  background: #fff3e0;
  color: #e65100;
}

.badge-inaccessible {
  background: #ffebee;
  color: #c62828;
}

.item-actions {
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

.btn-icon:hover:not(:disabled) {
  background: var(--bg-secondary, #f5f5f5);
  border-color: var(--primary-color, #FE9600);
  color: var(--primary-color, #FE9600);
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon.btn-danger:hover:not(:disabled) {
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
</style>
