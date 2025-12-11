<template>
  <div class="search-page">
    <div class="container">
      <h1 class="page-title">搜索</h1>
      <div class="search-box">
        <input
          ref="searchInput"
          v-model="keyword"
          @keyup.enter="handleSearch"
          type="text"
          placeholder="输入关键词搜索..."
          class="search-input"
        />
        <button @click="handleSearch" class="search-btn">
          <Icon icon="mdi:magnify" />
        </button>
      </div>
      <div v-if="loading" class="loading">搜索中...</div>
      <div v-else-if="results.length" class="search-results">
        <PostCard v-for="post in results" :key="post.id" :post="post" />
      </div>
      <div v-else-if="searched" class="empty">未找到相关文章</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import { postsApi, type Post } from '@/api/posts'
import PostCard from '@/components/PostCard.vue'

const keyword = ref('')
const results = ref<Post[]>([])
const loading = ref(false)
const searched = ref(false)
const searchInput = ref<HTMLInputElement | null>(null)

const handleSearch = async () => {
  if (!keyword.value.trim()) return
  
  loading.value = true
  searched.value = true
  try {
    const response = await postsApi.getPosts({ search: keyword.value })
    results.value = response.results || []
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Search failed:', error)
    }
    results.value = []
  } finally {
    loading.value = false
  }
}

// 页面加载时自动聚焦搜索框
onMounted(async () => {
  await nextTick()
  if (searchInput.value) {
    searchInput.value.focus()
  }
})
</script>

<style scoped>
.search-page {
  padding: 40px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 40px;
  color: var(--text-color, #333);
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 40px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  font-size: 16px;
  background: var(--card-bg, white);
  color: var(--text-color, #333);
}

.search-btn {
  padding: 12px 24px;
  background: var(--primary-color, #FE9600);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 20px;
  transition: opacity 0.3s;
}

.search-btn:hover {
  opacity: 0.9;
}

.search-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.loading,
.empty {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}
</style>

