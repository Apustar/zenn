<template>
  <article class="post-card">
    <router-link :to="`/post/${post.slug}`" class="post-link">
      <div v-if="post.cover" class="post-cover">
        <LazyImage :src="post.cover" :alt="post.title" />
      </div>
      <div class="post-content">
        <h3 class="post-title">{{ post.title }}</h3>
        <p v-if="post.excerpt" class="post-excerpt">{{ post.excerpt }}</p>
        <div class="post-meta">
          <span class="meta-item">
            <Icon icon="mdi:calendar" />
            {{ formatDate(post.published_at || post.created_at) }}
          </span>
          <span v-if="post.category" class="meta-item">
            <Icon icon="mdi:folder" />
            {{ post.category.name }}
          </span>
          <span class="meta-item">
            <Icon icon="mdi:eye" />
            {{ post.views }}
          </span>
        </div>
      </div>
    </router-link>
  </article>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'
import LazyImage from './LazyImage.vue'
import type { Post } from '@/api/posts'

defineProps<{
  post: Post
}>()

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>

<style scoped>
.post-card {
  background: var(--card-bg, white);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.post-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.post-cover {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.post-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.post-card:hover .post-cover img {
  transform: scale(1.05);
}

.post-content {
  padding: 20px;
}

.post-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 12px;
  color: var(--text-color, #333);
  line-height: 1.4;
}

.post-excerpt {
  color: var(--text-secondary, #666);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--text-secondary, #999);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>

