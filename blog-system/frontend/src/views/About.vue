<template>
  <div class="about-page">
    <div v-if="loading" class="loading">加载中...</div>
    <article v-else class="about-article">
      <header class="about-header">
        <h1 class="about-title">关于</h1>
      </header>
      <div v-if="aboutContentHtml" class="about-content" v-html="aboutContentHtml"></div>
      <div v-else class="empty-content">
        <p>暂无内容</p>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { settingsApi } from '@/api/settings'
import { initHighlight } from '@/utils/highlight'

const loading = ref(false)
const aboutContentHtml = ref<string | null>(null)

const fetchAboutContent = async () => {
  loading.value = true
  try {
    const settings = await settingsApi.getSettings()
    aboutContentHtml.value = settings.about_content_html || null
    await nextTick()
    initHighlight()
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch about content:', error)
    }
    aboutContentHtml.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAboutContent()
})
</script>

<style scoped>
.about-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.about-article {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.about-header {
  margin-bottom: 30px;
  border-bottom: 2px solid var(--border-color, #e5e5e5);
  padding-bottom: 20px;
}

.about-title {
  font-size: 32px;
  font-weight: bold;
  color: var(--text-color, #333);
  margin: 0;
}

.about-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-color, #333);
}

.about-content :deep(h1),
.about-content :deep(h2),
.about-content :deep(h3) {
  margin-top: 30px;
  margin-bottom: 15px;
  font-weight: bold;
}

.about-content :deep(h1) {
  font-size: 28px;
}

.about-content :deep(h2) {
  font-size: 24px;
}

.about-content :deep(h3) {
  font-size: 20px;
}

.about-content :deep(p) {
  margin-bottom: 15px;
}

.about-content :deep(ul),
.about-content :deep(ol) {
  margin-bottom: 15px;
  padding-left: 30px;
}

.about-content :deep(li) {
  margin-bottom: 8px;
}

.about-content :deep(code) {
  background: var(--bg-color, #f5f5f5);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.about-content :deep(pre) {
  background: var(--bg-color, #f5f5f5);
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 20px;
}

.about-content :deep(pre code) {
  background: none;
  padding: 0;
}

.about-content :deep(blockquote) {
  border-left: 4px solid var(--primary-color, #FE9600);
  padding-left: 20px;
  margin: 20px 0;
  color: var(--text-secondary, #666);
}

.about-content :deep(a) {
  color: var(--primary-color, #FE9600);
  text-decoration: none;
}

.about-content :deep(a:hover) {
  text-decoration: underline;
}

.about-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 20px 0;
}

.empty-content {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}
</style>

