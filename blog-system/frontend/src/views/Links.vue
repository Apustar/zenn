<template>
  <div class="links-page">
    <div class="container">
      <h1 class="page-title">
        <Icon icon="mdi:link-variant" />
        友情链接
      </h1>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="categories.length" class="links-content">
        <div v-for="category in categories" :key="category.id" class="link-category">
          <h2 class="category-title">{{ category.name }}</h2>
          <div v-if="category.links && category.links.length > 0" class="links-grid">
            <a
              v-for="link in category.links"
              :key="link.id"
              :href="link.url"
              target="_blank"
              rel="noopener noreferrer"
              class="link-card"
            >
              <div v-if="link.logo" class="link-logo">
                <LazyImage :src="link.logo" :alt="link.name" />
              </div>
              <div class="link-info">
                <h3 class="link-name">{{ link.name }}</h3>
                <p v-if="link.description" class="link-description">{{ link.description }}</p>
              </div>
            </a>
          </div>
          <div v-else class="empty-category">该分类下暂无友链</div>
        </div>
      </div>
      <div v-else class="empty">暂无友链</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import LazyImage from '@/components/LazyImage.vue'
import { linksApi, type LinkCategory } from '@/api/links'

const categories = ref<LinkCategory[]>([])
const loading = ref(false)

const fetchLinks = async () => {
  loading.value = true
  try {
    const result = await linksApi.getLinkCategories()
    
    if (Array.isArray(result)) {
      // 过滤掉没有链接的分类
      categories.value = result.filter(
        cat => cat && cat.links && Array.isArray(cat.links) && cat.links.length > 0
      )
    } else {
      categories.value = []
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch links:', error)
    }
    categories.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLinks()
})
</script>

<style scoped>
.links-page {
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

.link-category {
  margin-bottom: 40px;
}

.category-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--text-color, #333);
  padding-bottom: 12px;
  border-bottom: 2px solid var(--border-color, #e5e5e5);
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.link-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--card-bg, white);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-decoration: none;
  color: inherit;
  transition: transform 0.3s, box-shadow 0.3s;
}

.link-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.link-logo {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.link-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.link-info {
  flex: 1;
  min-width: 0;
}

.link-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
  color: var(--text-color, #333);
}

.link-description {
  font-size: 14px;
  color: var(--text-secondary, #666);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.loading,
.empty {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}

.empty-category {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary, #666);
  font-size: 14px;
}
</style>

