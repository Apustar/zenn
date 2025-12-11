<template>
  <header class="header">
    <div class="header-container">
      <div class="header-brand">
        <router-link to="/" class="brand-link">
          <span class="brand-icon">🌸</span>
          <span class="brand-text">{{ siteTitle }}</span>
        </router-link>
      </div>
      <nav class="header-nav">
        <router-link to="/" class="nav-link">{{ safeT('common.home', '首页') }}</router-link>
        <router-link to="/moments" class="nav-link">{{ safeT('common.moments', '瞬间') }}</router-link>
        <router-link to="/photos" class="nav-link">{{ safeT('common.photos', '相册') }}</router-link>
        <router-link to="/links" class="nav-link">{{ safeT('common.links', '友链') }}</router-link>
        <router-link to="/archives" class="nav-link">{{ safeT('common.archives', '归档') }}</router-link>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import { useThemeStore } from '@/stores/theme'
import { useI18nStore } from '@/stores/i18n'

const { t } = useI18n()
const router = useRouter()
const themeStore = useThemeStore()
const i18nStore = useI18nStore()

const siteTitle = ref('我的博客')

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
  font-size: 24px;
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
