<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="admin-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <h2 v-if="!sidebarCollapsed" class="sidebar-title">管理后台</h2>
        <button @click="toggleSidebar" class="sidebar-toggle">
          <Icon :icon="sidebarCollapsed ? 'mdi:menu' : 'mdi:menu-open'" />
        </button>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path.startsWith(item.path) }"
        >
          <Icon :icon="item.icon" />
          <span v-if="!sidebarCollapsed">{{ item.name }}</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <router-link to="/" class="back-site">
          <Icon icon="mdi:home" />
          <span v-if="!sidebarCollapsed">返回前台</span>
        </router-link>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="admin-main">
      <!-- 顶部导航栏 -->
      <header class="admin-header">
        <div class="header-left">
          <h1 class="page-title">{{ currentPageTitle }}</h1>
        </div>
        <div class="header-right">
          <div class="user-info">
            <span class="username">{{ userInfo?.username || '管理员' }}</span>
            <button @click="handleLogout" class="logout-btn">
              <Icon icon="mdi:logout" />
              退出
            </button>
          </div>
        </div>
      </header>

      <!-- 内容区域 -->
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const sidebarCollapsed = ref(false)

const userInfo = computed(() => authStore.user)

const menuItems = [
  { path: '/admin', name: '仪表盘', icon: 'mdi:view-dashboard' },
  { path: '/admin/posts', name: '文章管理', icon: 'mdi:file-document' },
  { path: '/admin/categories', name: '分类管理', icon: 'mdi:folder' },
  { path: '/admin/tags', name: '标签管理', icon: 'mdi:tag' },
  { path: '/admin/comments', name: '评论管理', icon: 'mdi:comment' },
  { path: '/admin/moments', name: '瞬间管理', icon: 'mdi:lightning-bolt' },
  { path: '/admin/photos', name: '相册管理', icon: 'mdi:image-multiple' },
  { path: '/admin/music', name: '音乐管理', icon: 'mdi:music' },
  { path: '/admin/links', name: '友链管理', icon: 'mdi:link' },
  { path: '/admin/settings', name: '系统设置', icon: 'mdi:cog' },
]

const currentPageTitle = computed(() => {
  const currentItem = menuItems.find(item => route.path.startsWith(item.path))
  return currentItem?.name || '管理后台'
})

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-color, #f5f5f5);
}

/* 侧边栏 */
.admin-sidebar {
  width: 250px;
  background: var(--card-bg, white);
  border-right: 1px solid var(--border-color, #e5e5e5);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  z-index: 1000;
}

.admin-sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color, #e5e5e5);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--text-color, #333);
  margin: 0;
}

.sidebar-toggle {
  background: none;
  border: none;
  color: var(--text-color, #333);
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  font-size: 20px;
  transition: color 0.3s;
}

.sidebar-toggle:hover {
  color: var(--primary-color, #FE9600);
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: var(--text-color, #333);
  text-decoration: none;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--primary-color, #FE9600);
}

.nav-item.active {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--primary-color, #FE9600);
  border-left-color: var(--primary-color, #FE9600);
}

.nav-item :deep(svg) {
  font-size: 20px;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color, #e5e5e5);
}

.back-site {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  color: var(--text-color, #333);
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.3s;
}

.back-site:hover {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--primary-color, #FE9600);
}

/* 主内容区 */
.admin-main {
  flex: 1;
  margin-left: 250px;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s;
}

.admin-sidebar.collapsed ~ .admin-main {
  margin-left: 64px;
}

/* 顶部导航栏 */
.admin-header {
  background: var(--card-bg, white);
  border-bottom: 1px solid var(--border-color, #e5e5e5);
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: var(--text-color, #333);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  color: var(--text-color, #333);
  font-size: 14px;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-secondary, #f5f5f5);
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
  color: var(--text-color, #333);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: var(--primary-color, #FE9600);
  color: white;
  border-color: var(--primary-color, #FE9600);
}

/* 内容区域 */
.admin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }

  .admin-sidebar.collapsed {
    transform: translateX(0);
    width: 250px;
  }

  .admin-main {
    margin-left: 0;
  }

  .admin-sidebar.collapsed ~ .admin-main {
    margin-left: 0;
  }
}
</style>

