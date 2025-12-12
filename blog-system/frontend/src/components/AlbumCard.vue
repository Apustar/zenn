<template>
  <article class="album-card">
    <router-link :to="`/album/${album.slug}`" class="album-link">
      <div class="album-cover">
        <LazyImage
          v-if="album.cover"
          :src="album.cover"
          :alt="album.name"
        />
        <div v-else class="album-placeholder">
          <Icon icon="mdi:image-multiple" />
        </div>
        <div v-if="album.is_encrypted" class="encrypted-badge">
          <Icon icon="mdi:lock" />
        </div>
        <div class="album-overlay">
          <span class="photo-count">{{ album.photos_count }} 张</span>
        </div>
      </div>
      <div class="album-content">
        <h3 class="album-title">
          {{ album.name }}
          <Icon v-if="album.is_encrypted" icon="mdi:lock" class="title-lock-icon" />
        </h3>
        <p v-if="album.description" class="album-description">{{ album.description }}</p>
      </div>
    </router-link>
  </article>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'
import LazyImage from './LazyImage.vue'
import type { Album } from '@/api/photos'

defineProps<{
  album: Album
}>()
</script>

<style scoped>
.album-card {
  background: var(--card-bg, white);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.album-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.album-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.album-cover {
  position: relative;
  width: 100%;
  height: 250px;
  overflow: hidden;
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.album-card:hover .album-cover img {
  transform: scale(1.05);
}

.album-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-color, #f5f5f5);
  color: var(--text-secondary, #999);
  font-size: 48px;
}

.album-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  padding: 12px;
  color: white;
  opacity: 0;
  transition: opacity 0.3s;
}

.album-card:hover .album-overlay {
  opacity: 1;
}

.photo-count {
  font-size: 14px;
}

.encrypted-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.encrypted-badge :deep(svg) {
  font-size: 20px;
}

.album-content {
  padding: 20px;
}

.album-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 8px;
  color: var(--text-color, #333);
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-lock-icon {
  font-size: 18px;
  color: var(--text-secondary, #666);
}

.album-description {
  font-size: 14px;
  color: var(--text-secondary, #666);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

