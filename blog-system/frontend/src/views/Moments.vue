<template>
  <div class="moments-page">
    <div class="container">
      <h1 class="page-title">
        <Icon icon="mdi:lightning-bolt" />
        瞬间
      </h1>
      
      <!-- 发布瞬间表单 -->
      <div v-if="authStore.isAuthenticated" class="moment-form">
        <textarea
          v-model="newMoment.content"
          placeholder="分享你的想法..."
          class="moment-input"
          rows="3"
        />
        <div class="form-actions">
          <button @click="handleSubmit" :disabled="!newMoment.content.trim()" class="submit-btn">
            发布
          </button>
        </div>
      </div>

      <!-- 瞬间列表 -->
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="moments.length" class="moments-list">
        <MomentCard
          v-for="moment in moments"
          :key="moment.id"
          :moment="moment"
          @like="handleLike"
        />
      </div>
      <div v-else class="empty">暂无瞬间</div>

      <Pagination
        v-if="totalPages > 1"
        :current="currentPage"
        :total="totalPages"
        @change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { momentsApi, type Moment } from '@/api/moments'
import { useAuthStore } from '@/stores/auth'
import MomentCard from '@/components/MomentCard.vue'
import Pagination from '@/components/Pagination.vue'

const authStore = useAuthStore()
const moments = ref<Moment[]>([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

const newMoment = ref({
  content: '',
  images: [] as string[],
  location: '',
  visibility: 'public' as 'public' | 'private',
})

const fetchMoments = async (page = 1) => {
  loading.value = true
  try {
    const response = await momentsApi.getMoments({ page })
    moments.value = response?.results || []
    totalPages.value = response?.count ? Math.ceil(response.count / 10) : 1
    currentPage.value = page
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch moments:', error)
    }
    moments.value = []
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!newMoment.value.content.trim()) return
  
  try {
    await momentsApi.createMoment(newMoment.value)
    newMoment.value.content = ''
    newMoment.value.images = []
    fetchMoments()
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to create moment:', error)
    }
  }
}

const handleLike = async (momentId: number) => {
  try {
    const result = await momentsApi.likeMoment(momentId)
    const moment = moments.value.find(m => m.id === momentId)
    if (moment && result) {
      moment.is_liked = result.liked
      moment.likes_count = result.likes
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to like moment:', error)
    }
  }
}

const handlePageChange = (page: number) => {
  fetchMoments(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  fetchMoments()
})
</script>

<style scoped>
.moments-page {
  padding: 40px 0;
}

.container {
  max-width: 800px;
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

.moment-form {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.moment-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
  resize: vertical;
  background: var(--bg-color, white);
  color: var(--text-color, #333);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.submit-btn {
  padding: 8px 24px;
  background: var(--primary-color, #FE9600);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.3s;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.moments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading,
.empty {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}
</style>

