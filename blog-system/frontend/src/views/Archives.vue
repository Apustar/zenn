<template>
  <div class="archives-page">
    <div class="container">
      <h1 class="page-title">归档</h1>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="archives">
        <div v-for="(posts, date) in archives" :key="date" class="archive-group">
          <h2 class="archive-date">{{ formatDate(date) }}</h2>
          <div class="archive-posts">
            <router-link
              v-for="post in posts"
              :key="post.id"
              :to="`/post/${post.slug}`"
              class="archive-post"
            >
              <span class="post-date">{{ formatPostDate(post.published_at || post.created_at) }}</span>
              <span class="post-title">{{ post.title }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { postsApi, type Post } from '@/api/posts'

const archives = ref<Record<string, Post[]>>({})
const loading = ref(false)

const fetchArchives = async () => {
  loading.value = true
  try {
    archives.value = await postsApi.getArchives()
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch archives:', error)
    }
    archives.value = {}
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr: string) => {
  const parts = dateStr.split('-')
  if (parts.length >= 2) {
    const [year, month] = parts
    return `${year}年${parseInt(month)}月`
  }
  return dateStr
}

const formatPostDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
  })
}

onMounted(() => {
  fetchArchives()
})
</script>

<style scoped>
.archives-page {
  padding: 40px 0;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 40px;
  color: var(--text-color, #333);
}

.archive-group {
  margin-bottom: 40px;
}

.archive-date {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--text-color, #333);
  padding-bottom: 10px;
  border-bottom: 2px solid var(--border-color, #e5e5e5);
}

.archive-posts {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.archive-post {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px;
  border-radius: 4px;
  transition: background 0.3s;
  text-decoration: none;
  color: var(--text-color, #333);
}

.archive-post:hover {
  background: var(--bg-color, #f5f5f5);
}

.post-date {
  font-size: 14px;
  color: var(--text-secondary, #666);
  min-width: 60px;
}

.post-title {
  flex: 1;
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}
</style>

