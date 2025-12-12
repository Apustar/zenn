<template>
  <header class="header">
    <div class="header-container">
      <div class="header-brand">
        <router-link to="/" class="brand-link">
          <!-- 自定义图标 -->
          <img
            v-if="siteIconUrl"
            :src="siteIconUrl"
            alt="站点图标"
            class="brand-icon brand-icon-image"
          />
          <!-- 默认Z字形图标 -->
          <svg
            v-else
            class="brand-icon brand-icon-svg"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M4 4H20V8H8V12H20V16H8V20H4V4Z" fill="currentColor"/>
          </svg>
          <span class="brand-text">{{ siteTitle }}</span>
        </router-link>
      </div>
      <nav class="header-nav">
        <router-link
          v-for="item in navigationItems"
          :key="item.id"
          :to="item.is_accessible ? item.url : '/access-denied'"
          class="nav-link"
          @click="handleNavClick(item, $event)"
        >
          {{ item.name }}
        </router-link>
      </nav>
      <div class="header-actions">
        <button @click="toggleSearch" class="action-btn" :title="safeT('common.search', '搜索')">
          <Icon icon="mdi:magnify" />
        </button>
        <button @click="toggleLocale" class="action-btn" :title="safeT('common.language', '切换语言')">
          <Icon icon="mdi:translate" />
        </button>
        <button @click="toggleTheme" class="action-btn" :title="safeT('common.theme', '切换主题')">
          <Icon :icon="themeStore.isDark ? 'mdi:weather-sunny' : 'mdi:weather-night'" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import { useThemeStore } from '@/stores/theme'
import { useI18nStore } from '@/stores/i18n'
import { settingsApi } from '@/api/settings'
import { navigationApi, type NavigationItem } from '@/api/settings'

const { t } = useI18n()
const router = useRouter()
const themeStore = useThemeStore()
const i18nStore = useI18nStore()

const siteTitle = ref('我的博客')
const siteIconUrl = ref<string | null>(null)
const navigationItems = ref<NavigationItem[]>([])

// 获取站点设置
const fetchSettings = async () => {
  try {
    const settings = await settingsApi.getSettings()
    if (settings.site_name) {
      siteTitle.value = settings.site_name
    }
    // 优先使用 site_icon_url，如果没有则使用 site_icon
    if (settings.site_icon_url) {
      siteIconUrl.value = settings.site_icon_url
    } else if (settings.site_icon) {
      siteIconUrl.value = settings.site_icon
    } else {
      siteIconUrl.value = null
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch site settings:', error)
    }
    // 失败时使用默认值
  }
}

// 默认导航菜单
const defaultNavigationItems: NavigationItem[] = [
  { id: 1, name: '首页', url: '/', is_builtin: true, is_visible: true, is_accessible: true, order: 0 },
  { id: 2, name: '瞬间', url: '/moments', is_builtin: true, is_visible: true, is_accessible: true, order: 1 },
  { id: 3, name: '相册', url: '/photos', is_builtin: true, is_visible: true, is_accessible: true, order: 2 },
  { id: 4, name: '友链', url: '/links', is_builtin: true, is_visible: true, is_accessible: true, order: 3 },
  { id: 5, name: '归档', url: '/archives', is_builtin: true, is_visible: true, is_accessible: true, order: 4 },
  { id: 6, name: '关于', url: '/about', is_builtin: true, is_visible: true, is_accessible: true, order: 5 },
]

// 获取导航菜单
const fetchNavigationItems = async () => {
  try {
    const items = await navigationApi.getNavigationItems()
    
    if (import.meta.env.DEV) {
      console.log('Fetched navigation items:', items)
    }
    
    // 过滤掉不可见的菜单项（双重保险）
    const visibleItems = Array.isArray(items) 
      ? items.filter(item => {
          // 严格检查 is_visible 字段
          const isVisible = item.is_visible === true || item.is_visible === undefined
          if (import.meta.env.DEV && !isVisible) {
            console.log('Filtered out menu item:', item.name, 'is_visible:', item.is_visible)
          }
          return isVisible
        })
      : []
    
    if (import.meta.env.DEV) {
      console.log('Visible navigation items:', visibleItems)
    }
    
    // 如果返回的数组为空或没有数据，使用默认菜单
    if (visibleItems.length > 0) {
      navigationItems.value = visibleItems
    } else {
      if (import.meta.env.DEV) {
        console.log('No visible items, using default menu')
      }
      navigationItems.value = defaultNavigationItems
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch navigation items:', error)
    }
    // 失败时使用默认菜单
    navigationItems.value = defaultNavigationItems
  }
}

// 初始化时先设置默认菜单，避免空白
navigationItems.value = defaultNavigationItems

onMounted(() => {
  fetchSettings()
  fetchNavigationItems()
})

/**
 * 安全地使用 i18n 翻译函数
 * 如果翻译失败或不存在，返回默认值
 */
const safeT = (key: string, defaultValue: string) => {
  try {
    const result = t(key)
    return result && result !== key ? result : defaultValue
  } catch {
    return defaultValue
  }
}

const toggleSearch = () => {
  router.push('/search')
}

const toggleTheme = () => {
  themeStore.toggleDark()
}

const toggleLocale = () => {
  i18nStore.toggleLocale()
}

// 处理导航点击
const handleNavClick = (item: NavigationItem, event: MouseEvent) => {
  // 如果菜单项不可访问，跳转到受限页面
  if (!item.is_accessible) {
    event.preventDefault()
    router.push('/access-denied')
  }
}
</script>

<style scoped>
.header {
  background: var(--header-bg, rgba(255, 255, 255, 0.9));
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color, #e5e5e5);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text-color, #333);
  font-size: 20px;
  font-weight: bold;
}

.brand-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  object-fit: contain;
}

.brand-icon-svg {
  color: var(--primary-color, #FE9600);
}

.brand-icon-image {
  display: block;
}

.header-nav {
  display: flex;
  gap: 24px;
}

.nav-link {
  text-decoration: none;
  color: var(--text-color, #333);
  font-size: 16px;
  transition: color 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--primary-color, #FE9600);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  color: var(--text-color, #333);
  font-size: 20px;
  transition: color 0.3s;
}

.action-btn:hover {
  color: var(--primary-color, #FE9600);
}
</style>
