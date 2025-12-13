<template>
  <div class="share-button-wrapper">
    <button
      @click="toggleShareMenu"
      class="share-btn"
      :class="{ 'copied': copied }"
      :title="copied ? '已复制' : '分享文章'"
    >
      <Icon :icon="copied ? 'mdi:check-circle' : 'mdi:share-variant'" />
      <span v-if="showLabel">{{ copied ? '已复制' : '分享' }}</span>
    </button>

    <!-- 分享菜单 -->
    <transition name="fade">
      <div v-if="showMenu" class="share-menu" @click.stop>
        <div class="share-menu-header">
          <span>分享到</span>
          <button class="close-btn" @click="closeMenu">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <div class="share-options">
          <button
            class="share-option"
            @click="handleCopyLink"
            :disabled="copying"
          >
            <Icon icon="mdi:link-variant" />
            <span>复制链接</span>
          </button>
          <button
            class="share-option"
            @click="shareToWeibo"
            v-if="showSocialShare"
          >
            <Icon icon="mdi:weibo" />
            <span>微博</span>
          </button>
          <button
            class="share-option"
            @click="shareToTwitter"
            v-if="showSocialShare"
          >
            <Icon icon="mdi:twitter" />
            <span>Twitter</span>
          </button>
          <button
            class="share-option"
            @click="shareToQQ"
            v-if="showSocialShare"
          >
            <Icon icon="mdi:qqchat" />
            <span>QQ</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- 点击外部关闭菜单 -->
    <div v-if="showMenu" class="share-overlay" @click="closeMenu"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { copyToClipboard, getCurrentUrl } from '@/utils/clipboard'

interface Props {
  url?: string
  title?: string
  description?: string
  showLabel?: boolean
  showSocialShare?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  url: '',
  title: '',
  description: '',
  showLabel: false,
  showSocialShare: true,
})

const showMenu = ref(false)
const copied = ref(false)
const copying = ref(false)
const copyTimeout = ref<number | null>(null)

const shareUrl = ref('')

onMounted(() => {
  shareUrl.value = props.url || getCurrentUrl()
})

onUnmounted(() => {
  if (copyTimeout.value) {
    clearTimeout(copyTimeout.value)
  }
})

// 监听 url prop 变化
watch(() => props.url, (newUrl) => {
  if (newUrl) {
    shareUrl.value = newUrl
  } else {
    shareUrl.value = getCurrentUrl()
  }
})

const toggleShareMenu = () => {
  if (showMenu.value) {
    closeMenu()
  } else {
    showMenu.value = true
  }
}

const closeMenu = () => {
  showMenu.value = false
}

const handleCopyLink = async () => {
  if (copying.value) return

  copying.value = true
  const success = await copyToClipboard(shareUrl.value)

  if (success) {
    copied.value = true
    // 2秒后重置状态
    if (copyTimeout.value) {
      clearTimeout(copyTimeout.value)
    }
    copyTimeout.value = window.setTimeout(() => {
      copied.value = false
    }, 2000)
    
    // 关闭菜单
    setTimeout(() => {
      closeMenu()
    }, 300)
  } else {
    // 复制失败，显示提示
    alert('复制失败，请手动复制链接')
  }

  copying.value = false
}

// 通用分享函数
const openShareWindow = (url: string) => {
  try {
    window.open(url, '_blank', 'width=600,height=400')
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to open share window:', error)
    }
  }
  closeMenu()
}

const shareToWeibo = () => {
  const url = encodeURIComponent(shareUrl.value)
  const title = encodeURIComponent(props.title || '')
  openShareWindow(`https://service.weibo.com/share/share.php?url=${url}&title=${title}`)
}

const shareToTwitter = () => {
  const url = encodeURIComponent(shareUrl.value)
  const text = encodeURIComponent(props.title || '')
  openShareWindow(`https://twitter.com/intent/tweet?url=${url}&text=${text}`)
}

const shareToQQ = () => {
  const url = encodeURIComponent(shareUrl.value)
  const title = encodeURIComponent(props.title || '')
  openShareWindow(`https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${title}`)
}

// 点击外部关闭菜单通过 overlay 处理，不需要额外的事件监听
</script>

<style scoped>
.share-button-wrapper {
  position: relative;
  display: inline-block;
}

.share-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: var(--text-secondary, #666);
  transition: color 0.3s;
  font-size: 14px;
}

.share-btn:hover {
  color: var(--primary-color, #FE9600);
}

.share-btn.copied {
  color: #52c41a;
}

.share-btn.copied:hover {
  color: #73d13d;
}

.share-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.share-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 998;
}

.share-menu {
  position: absolute;
  bottom: 100%;
  right: 0;
  margin-bottom: 8px;
  background: var(--card-bg, white);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 999;
  min-width: 200px;
  overflow: hidden;
}

.dark .share-menu {
  background: var(--card-bg, #2a2a2a);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.share-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, #e5e5e5);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-secondary, #666);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: var(--bg-hover, rgba(0, 0, 0, 0.05));
}

.share-options {
  padding: 8px;
}

.share-option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
  color: var(--text-primary, #333);
  font-size: 14px;
  text-align: left;
}

.share-option:hover:not(:disabled) {
  background: var(--bg-hover, rgba(0, 0, 0, 0.05));
}

.share-option:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.share-option .iconify {
  font-size: 20px;
  color: var(--primary-color, #FE9600);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>

