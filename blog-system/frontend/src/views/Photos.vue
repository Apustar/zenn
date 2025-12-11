<template>
  <div class="photos-page">
    <div class="container">
      <h1 class="page-title">
        <Icon icon="mdi:image-multiple" />
        相册
      </h1>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="albums.length" class="albums-grid">
        <AlbumCard
          v-for="album in albums"
          :key="album.id"
          :album="album"
        />
      </div>
      <div v-else class="empty">暂无相册</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { photosApi, type Album } from '@/api/photos'
import AlbumCard from '@/components/AlbumCard.vue'

const albums = ref<Album[]>([])
const loading = ref(false)

const fetchAlbums = async () => {
  loading.value = true
  try {
    const response = await photosApi.getAlbums()
    albums.value = response.results
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch albums:', error)
    }
    albums.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAlbums()
})
</script>

<style scoped>
.photos-page {
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
  margin-bottom: 40px;
  color: var(--text-color, #333);
}

.albums-grid {
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

