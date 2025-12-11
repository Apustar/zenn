<template>
  <div class="album-page">
    <div class="container">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="album">
        <header class="album-header">
          <h1 class="album-title">{{ album.name }}</h1>
          <p v-if="album.description" class="album-description">{{ album.description }}</p>
          <div class="album-meta">
            <span>{{ album.photos_count }} 张照片</span>
          </div>
        </header>

        <div v-if="album.photos && album.photos.length > 0" class="photos-masonry">
          <div
            v-for="photo in album.photos"
            :key="photo.id"
            class="photo-item"
            @click="openLightbox(photo)"
          >
            <LazyImage :src="photo.image" :alt="photo.title || 'Photo'" />
            <div v-if="photo.title || photo.description" class="photo-overlay">
              <p v-if="photo.title" class="photo-title">{{ photo.title }}</p>
              <p v-if="photo.description" class="photo-description">{{ photo.description }}</p>
            </div>
          </div>
        </div>
        <div v-else class="empty-photos">
          <p>该相册暂无照片</p>
        </div>
      </div>
    </div>

    <!-- 图片预览模态框 -->
    <div v-if="selectedPhoto" class="lightbox" @click="closeLightbox">
      <img :src="selectedPhoto.image" :alt="selectedPhoto.title" class="lightbox-image" />
      <button @click="closeLightbox" class="lightbox-close">
        <Icon icon="mdi:close" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import LazyImage from '@/components/LazyImage.vue'
import { photosApi, type Album, type Photo } from '@/api/photos'

const route = useRoute()
const album = ref<Album | null>(null)
const loading = ref(false)
const selectedPhoto = ref<Photo | null>(null)

const fetchAlbum = async () => {
  loading.value = true
  try {
    const result = await photosApi.getAlbum(route.params.slug as string)
    album.value = result || null
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch album:', error)
    }
    album.value = null
  } finally {
    loading.value = false
  }
}

const openLightbox = (photo: Photo) => {
  selectedPhoto.value = photo
  document.body.style.overflow = 'hidden'
}

const closeLightbox = () => {
  selectedPhoto.value = null
  document.body.style.overflow = ''
}

onMounted(() => {
  fetchAlbum()
})
</script>

<style scoped>
.album-page {
  padding: 40px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.album-header {
  margin-bottom: 40px;
  text-align: center;
}

.album-title {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 16px;
  color: var(--text-color, #333);
}

.album-description {
  font-size: 16px;
  color: var(--text-secondary, #666);
  margin-bottom: 12px;
}

.album-meta {
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.photos-masonry {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.photo-item {
  position: relative;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 1;
}

.photo-item .photo-image,
.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
  display: block;
}

.photo-item:hover img {
  transform: scale(1.05);
}

.photo-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  padding: 20px;
  color: white;
  opacity: 0;
  transition: opacity 0.3s;
}

.photo-item:hover .photo-overlay {
  opacity: 1;
}

.photo-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.photo-description {
  font-size: 14px;
  opacity: 0.9;
}

.lightbox {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
}

.lightbox-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.lightbox-close {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: background 0.3s;
}

.lightbox-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}

.empty-photos {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}
</style>

