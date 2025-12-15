<template>
  <div v-if="show" class="reading-progress-bar" :style="{ width: `${progress}%` }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const progress = ref(0)
const show = ref(false)

const updateProgress = () => {
  // 只在文章页面显示进度条
  if (route.name !== 'Post') {
    show.value = false
    return
  }

  const article = document.querySelector('.post-article')
  if (!article) {
    show.value = false
    return
  }

  show.value = true

  const articleTop = article.getBoundingClientRect().top + window.scrollY
  const articleHeight = article.offsetHeight
  const windowHeight = window.innerHeight
  const scrollTop = window.scrollY

  // 计算阅读进度
  // 当滚动位置超过文章顶部时开始计算
  if (scrollTop < articleTop) {
    progress.value = 0
    return
  }

  // 计算已滚动的内容高度
  const scrolled = scrollTop + windowHeight - articleTop
  const total = articleHeight
  const percentage = Math.min(100, Math.max(0, (scrolled / total) * 100))

  progress.value = percentage
}

const handleScroll = () => {
  requestAnimationFrame(updateProgress)
}

onMounted(() => {
  updateProgress()
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('resize', updateProgress)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('resize', updateProgress)
})
</script>

<style scoped>
.reading-progress-bar {
  position: fixed;
  top: 60px; /* Header 高度 */
  left: 0;
  height: 2px;
  background: linear-gradient(90deg, #FE9600 0%, #FFB84D 100%);
  z-index: 999;
  transition: width 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(254, 150, 0, 0.4);
  will-change: width;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .reading-progress-bar {
    top: 60px;
    height: 2px;
  }
}

/* 暗色模式适配 */
@media (prefers-color-scheme: dark) {
  .reading-progress-bar {
    background: linear-gradient(90deg, #FE9600 0%, #FFB84D 100%);
    box-shadow: 0 1px 3px rgba(254, 150, 0, 0.6);
  }
}
</style>

