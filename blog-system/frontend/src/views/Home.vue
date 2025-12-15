<template>
  <div class="home">
    <!-- 首屏 -->
    <section v-if="showHero" class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">{{ heroTitle }}</h1>
        <p v-if="heroSubtitle" class="hero-subtitle">{{ heroSubtitle }}</p>
        <div class="hero-socials" v-if="socialLinks.length">
          <a
            v-for="link in socialLinks"
            :key="link.name"
            :href="link.url"
            target="_blank"
            class="social-link"
          >
            <Icon :icon="link.icon" />
          </a>
        </div>
      </div>
    </section>

    <!-- 热门文章 -->
    <section v-if="hotPosts.length > 0" class="hot-posts-section">
      <div class="container">
        <h2 class="section-title">
          <Icon icon="mdi:fire" />
          <span>热门文章</span>
        </h2>
        <div class="hot-posts-grid">
          <PostCard v-for="post in hotPosts" :key="post.id" :post="post" />
        </div>
      </div>
    </section>

    <!-- 文章列表 -->
    <section class="posts-section">
      <div class="container">
        <h2 class="section-title">
          <Icon icon="mdi:book-open-variant" />
          <span>{{ getTranslation('home.title', '最新文章') }}</span>
        </h2>
        <div v-if="loading" class="loading">{{ getTranslation('common.loading', '加载中...') }}</div>
        <div v-else-if="posts.length" class="posts-grid">
          <PostCard v-for="post in posts" :key="post.id" :post="post" />
        </div>
        <div v-else class="empty">{{ getTranslation('common.empty', '暂无文章') }}</div>
        <Pagination
          v-if="totalPages > 1"
          :current="currentPage"
          :total="totalPages"
          @change="handlePageChange"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import { postsApi, type Post } from '@/api/posts'
import PostCard from '@/components/PostCard.vue'
import Pagination from '@/components/Pagination.vue'

const { t } = useI18n()
const showHero = ref(true)

// 安全获取翻译，失败时使用默认值
const getTranslation = (key: string, defaultValue: string) => {
  try {
    const result = t(key)
    return result && result !== key ? result : defaultValue
  } catch {
    return defaultValue
  }
}

const heroTitle = ref(getTranslation('home.hero.title', 'Hi, Friend'))
const heroSubtitle = ref(getTranslation('home.hero.subtitle', '欢迎来到我的博客'))
const socialLinks = ref<Array<{ name: string; url: string; icon: string }>>([])

const posts = ref<Post[]>([])
const hotPosts = ref<Post[]>([])
const loading = ref(false)
const hotLoading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

const fetchPosts = async (page = 1) => {
  loading.value = true
  try {
    const response = await postsApi.getPosts({ page })
    posts.value = response.results || []
    totalPages.value = response.count ? Math.ceil(response.count / 10) : 1
    currentPage.value = page
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch posts:', error)
    }
    posts.value = []
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page: number) => {
  fetchPosts(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const fetchHotPosts = async () => {
  hotLoading.value = true
  try {
    hotPosts.value = await postsApi.getHotPosts()
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch hot posts:', error)
    }
    hotPosts.value = []
  } finally {
    hotLoading.value = false
  }
}

onMounted(() => {
  fetchPosts()
  fetchHotPosts()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.hero-section {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--hero-bg, linear-gradient(135deg, #667eea 0%, #764ba2 100%));
  color: white;
  text-align: center;
  padding: 60px 20px;
}

.hero-content {
  max-width: 800px;
}

.hero-title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 20px;
}

.hero-subtitle {
  font-size: 20px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.hero-socials {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.social-link {
  color: white;
  font-size: 24px;
  transition: transform 0.3s;
}

.social-link:hover {
  transform: scale(1.2);
}

.hot-posts-section {
  padding: 60px 0;
  background: var(--bg-secondary, #f5f5f5);
}

.hot-posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.posts-section {
  padding: 60px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 40px;
  color: var(--text-color, #333);
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.loading,
.empty {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}
</style>
