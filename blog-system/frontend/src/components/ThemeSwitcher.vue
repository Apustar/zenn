<template>
  <div class="theme-switcher">
    <button @click="showModal = true" class="theme-switcher-btn" :title="'切换主题'">
      <Icon icon="mdi:palette" />
    </button>
    
    <!-- 主题选择模态框 -->
    <Teleport to="body">
      <div v-if="showModal" class="theme-modal-overlay" @click="showModal = false">
        <div class="theme-modal" @click.stop>
          <div class="theme-modal-header">
            <h2>选择主题</h2>
            <button @click="showModal = false" class="close-btn">
              <Icon icon="mdi:close" />
            </button>
          </div>
          <div class="theme-grid">
            <div
              v-for="theme in availableThemes"
              :key="theme.id"
              class="theme-card"
              :class="{ active: theme.id === currentThemeId }"
              @click="selectTheme(theme.id)"
            >
            <div class="theme-preview" :style="getPreviewStyle(theme)">
              <div class="theme-preview-content">
                <div 
                  class="preview-header" 
                  :style="getHeaderStyle(theme)"
                >
                  <div class="preview-primary-indicator" :style="{ background: theme.colors.primary }"></div>
                </div>
                <div 
                  class="preview-card" 
                  :style="getCardStyle(theme)"
                >
                  <div class="preview-card-content" :style="{ borderLeftColor: theme.colors.primary }"></div>
                </div>
                <div 
                  class="preview-card" 
                  :style="getCardStyle(theme)"
                ></div>
              </div>
            </div>
              <div class="theme-info">
                <h3 class="theme-name">{{ theme.name }}</h3>
                <p class="theme-description">{{ theme.description }}</p>
              </div>
              <div v-if="theme.id === currentThemeId" class="theme-check">
                <Icon icon="mdi:check-circle" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useThemeStore } from '@/stores/theme'
import type { ThemeConfig } from '@/types/theme'

const themeStore = useThemeStore()
const showModal = ref(false)

const currentThemeId = computed(() => themeStore.currentThemeId)
const availableThemes = computed(() => themeStore.getAvailableThemes())

const selectTheme = (themeId: string) => {
  themeStore.setTheme(themeId)
  showModal.value = false
}

const getPreviewStyle = (theme: ThemeConfig) => {
  const style: Record<string, string> = {
    backgroundColor: theme.colors.bg,
  }
  
  if (theme.background.gradient) {
    style.background = theme.background.gradient
    style.backgroundColor = 'transparent'
  } else if (theme.background.image) {
    style.backgroundImage = `url(${theme.background.image})`
    style.backgroundSize = theme.background.strategy === 'cover' ? 'cover' : 'contain'
    style.backgroundRepeat = theme.background.strategy === 'repeat' ? 'repeat' : 'no-repeat'
    style.backgroundPosition = 'center'
    style.backgroundColor = theme.colors.bg
  }
  
  // 对于白色背景，添加轻微边框以增加可见性
  if (theme.colors.bg === '#FFFFFF' && !theme.background.gradient && !theme.background.image) {
    style.border = '1px solid rgba(0, 0, 0, 0.05)'
  }
  
  return style
}

const getHeaderStyle = (theme: ThemeConfig) => {
  const style: Record<string, string> = {}
  
  if (theme.colors.headerBg) {
    // 如果 headerBg 是 rgba，直接使用
    if (theme.colors.headerBg.includes('rgba')) {
      style.background = theme.colors.headerBg
    } else {
      // 否则添加透明度
      style.background = theme.colors.headerBg
      style.opacity = '0.9'
    }
  } else {
    // 如果没有 headerBg，使用 cardBg 或 bg
    style.background = theme.colors.cardBg || theme.colors.bg
    style.opacity = '0.9'
  }
  
  // 确保有最小对比度
  if (theme.colors.bg === '#FFFFFF' && theme.colors.cardBg === '#FFFFFF') {
    style.boxShadow = 'inset 0 1px 2px rgba(0, 0, 0, 0.05)'
  }
  
  return style
}

const getCardStyle = (theme: ThemeConfig) => {
  const style: Record<string, string> = {
    background: theme.colors.cardBg || theme.colors.bg,
    borderColor: theme.colors.border,
    borderWidth: '1px',
    borderStyle: 'solid',
  }
  
  // 对于白色背景的主题，添加轻微阴影以增加可见性
  if (theme.colors.bg === '#FFFFFF' && theme.colors.cardBg === '#FFFFFF') {
    style.boxShadow = 'inset 0 1px 2px rgba(0, 0, 0, 0.03)'
  }
  
  return style
}
</script>

<style scoped>
.theme-switcher {
  position: relative;
}

.theme-switcher-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 50%;
  color: var(--text-color, #333);
  cursor: pointer;
  transition: all 0.3s;
}

.theme-switcher-btn:hover {
  background: var(--primary-color, #FE9600);
  color: white;
  transform: scale(1.1);
}

.theme-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  animation: fadeIn 0.3s;
  padding: 20px;
  overflow-y: auto;
}

.theme-modal {
  background: var(--card-bg, white);
  border-radius: 16px;
  width: 100%;
  max-width: 900px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s;
  margin: auto;
  position: relative;
  z-index: 100000;
}

.theme-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid var(--border-color, #e5e5e5);
}

.theme-modal-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color, #333);
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: var(--text-secondary, #666);
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.close-btn:hover {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-color, #333);
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 24px;
}

.theme-card {
  position: relative;
  background: var(--card-bg, white);
  border: 2px solid var(--border-color, #e5e5e5);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.theme-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--hover-shadow, 0 8px 16px rgba(0, 0, 0, 0.15));
  border-color: var(--primary-color, #FE9600);
}

.theme-card.active {
  border-color: var(--primary-color, #FE9600);
  border-width: 3px;
}

.theme-preview {
  width: 100%;
  height: 120px;
  position: relative;
  overflow: hidden;
}

.theme-preview-content {
  padding: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-header {
  height: 20px;
  border-radius: 4px;
  min-height: 20px;
  flex-shrink: 0;
  width: 100%;
  opacity: 0.9;
  position: relative;
  display: flex;
  align-items: center;
  padding: 0 8px;
}

.preview-primary-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.preview-card {
  flex: 1;
  border-radius: 4px;
  border: 1px solid;
  min-height: 20px;
  width: 100%;
  position: relative;
  padding: 4px;
}

.preview-card-content {
  width: 100%;
  height: 100%;
  border-left: 2px solid;
  border-radius: 2px;
}

.theme-info {
  padding: 16px;
}

.theme-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color, #333);
}

.theme-description {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary, #666);
  line-height: 1.4;
}

.theme-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: var(--primary-color, #FE9600);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .theme-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
    padding: 16px;
  }
  
  .theme-preview {
    height: 100px;
  }
}
</style>

