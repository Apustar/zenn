<template>
  <div class="tag-page">
    <div class="container">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="tag">
        <h1 class="page-title" :style="{ color: tag.color }">
          <Icon icon="mdi:tag" />
          {{ tag.name }}
        </h1>
        <p v-if="tag.description" class="page-description">{{ tag.description }}</p>
        <div v-if="posts.length" class="posts-grid">
          <PostCard v-for="post in posts" :key="post.id" :post="post" />
        </div>
        <div v-else class="empty">该标签下暂无文章</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import { tagsApi, type Tag } from '@/api/tags'
import { postsApi, type Post } from '@/api/posts'
import PostCard from '@/components/PostCard.vue'

const route = useRoute()
const tag = ref<Tag | null>(null)
const posts = ref<Post[]>([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    tag.value = await tagsApi.getTag(route.params.slug as string)
    if (tag.value) {
      const response = await postsApi.getPosts({ tags: tag.value.id.toString() })
      posts.value = response?.results || []
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch tag:', error)
    }
    tag.value = null
    posts.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.tag-page {
  padding: 40px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 20px;
}

.page-description {
  font-size: 16px;
  color: var(--text-secondary, #666);
  margin-bottom: 40px;
}

.posts-grid {
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

