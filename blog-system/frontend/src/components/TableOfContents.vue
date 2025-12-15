<template>
  <div v-if="toc && toc.length > 0" class="toc-container">
    <div class="toc-header">
      <Icon icon="mdi:format-list-bulleted" />
      <span>目录</span>
    </div>
    <nav class="toc-nav">
      <ul class="toc-list">
        <TOCItem
          v-for="item in toc"
          :key="item.id"
          :item="item"
          :active-id="activeId"
          @click="handleItemClick"
        />
      </ul>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'
import type { TOCItem as TOCItemType } from '@/api/posts'
import TOCItem from './TOCItem.vue'

const props = defineProps<{
  toc: TOCItemType[]
}>()

const emit = defineEmits<{
  (e: 'item-click', id: string): void
}>()

const activeId = ref<string>('')

const handleItemClick = (id: string) => {
  emit('item-click', id)
  
  // 滚动到目标位置
  const element = document.getElementById(id)
  if (element) {
    const headerOffset = 100 // 考虑固定头部的高度
    const elementPosition = element.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - headerOffset

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth',
    })

    // 更新 URL hash（不触发滚动）
    history.replaceState(null, '', `#${id}`)
  }
}

// 监听滚动，更新当前激活的标题
const handleScroll = () => {
  const headings = document.querySelectorAll('.post-content h1, .post-content h2, .post-content h3, .post-content h4, .post-content h5, .post-content h6')
  if (headings.length === 0) return
  
  const scrollPosition = window.scrollY + 120 // 偏移量

  let currentId = ''
  
  for (let i = headings.length - 1; i >= 0; i--) {
    const heading = headings[i] as HTMLElement
    const rect = heading.getBoundingClientRect()
    if (rect.top <= scrollPosition) {
      currentId = heading.id || ''
      break
    }
  }

  activeId.value = currentId
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  // 初始检查
  handleScroll()
  
  // 如果有 hash，滚动到对应位置
  if (window.location.hash) {
    const id = window.location.hash.substring(1)
    setTimeout(() => {
      const element = document.getElementById(id)
      if (element) {
        const headerOffset = 100
        const elementPosition = element.getBoundingClientRect().top
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth',
        })
      }
    }, 300)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>


<style scoped>
.toc-container {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  width: 100%;
  /* 滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: var(--border-color, #ccc) var(--bg-color, #f5f5f5);
}

.toc-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: bold;
  font-size: 15px;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--border-color, #e5e5e5);
  color: var(--text-color, #333);
}

.toc-nav {
  font-size: 13px;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}


/* 滚动条样式 */
.toc-container::-webkit-scrollbar {
  width: 6px;
}

.toc-container::-webkit-scrollbar-track {
  background: var(--bg-color, #f5f5f5);
  border-radius: 3px;
}

.toc-container::-webkit-scrollbar-thumb {
  background: var(--border-color, #ccc);
  border-radius: 3px;
}

.toc-container::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary, #999);
}

/* 移动端适配 */
@media (max-width: 1024px) {
  .toc-container {
    margin-bottom: 20px;
  }
}
</style>
