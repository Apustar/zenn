<template>
  <article class="moment-card">
    <div class="moment-header">
      <div class="author-info">
        <img
          v-if="moment.author.avatar"
          :src="moment.author.avatar"
          :alt="moment.author.username"
          class="avatar"
        />
        <div class="author-details">
          <span class="author-name">{{ moment.author.username }}</span>
          <span v-if="moment.location" class="location">
            <Icon icon="mdi:map-marker" />
            {{ moment.location }}
          </span>
        </div>
      </div>
      <span class="moment-time">{{ formatTime(moment.published_at) }}</span>
    </div>
    
    <div class="moment-content">
      <p>{{ moment.content }}</p>
      <div v-if="moment.images && moment.images.length" class="moment-images">
        <LazyImage
          v-for="(image, index) in moment.images"
          :key="index"
          :src="image"
          :alt="`Image ${index + 1}`"
          class="moment-image"
        />
      </div>
    </div>
    
    <div class="moment-footer">
      <button
        @click="$emit('like', moment.id)"
        class="action-btn"
        :class="{ liked: moment.is_liked }"
      >
        <Icon :icon="moment.is_liked ? 'mdi:heart' : 'mdi:heart-outline'" />
        {{ moment.likes_count }}
      </button>
      <span class="comments-count">
        <Icon icon="mdi:comment-outline" />
        {{ moment.comments_count }}
      </span>
    </div>
  </article>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'
import LazyImage from './LazyImage.vue'
import type { Moment } from '@/api/moments'

defineProps<{
  moment: Moment
}>()

defineEmits<{
  like: [id: number]
}>()

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.moment-card {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.moment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.author-name {
  font-weight: bold;
  color: var(--text-color, #333);
}

.location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.moment-time {
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.moment-content {
  margin-bottom: 16px;
}

.moment-content p {
  line-height: 1.6;
  color: var(--text-color, #333);
  margin-bottom: 12px;
}

.moment-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.moment-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}

.moment-footer {
  display: flex;
  gap: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color, #e5e5e5);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary, #666);
  font-size: 14px;
  transition: color 0.3s;
}

.action-btn:hover {
  color: var(--primary-color, #FE9600);
}

.action-btn.liked {
  color: #e74c3c;
}

.comments-count {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary, #666);
  font-size: 14px;
}
</style>

