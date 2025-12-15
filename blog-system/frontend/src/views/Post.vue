<template>
  <div class="post-page">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="post" class="post-wrapper" :class="{ 'has-toc': hasTOC, [postLayoutClass]: true }">
      <article class="post-article">
      <header class="post-header">
        <h1 class="post-title">{{ post.title }}</h1>
        <div class="post-meta">
          <span class="meta-item">
            <Icon icon="mdi:calendar" />
            {{ formatDate(post.published_at || post.created_at) }}
          </span>
          <span v-if="post.category" class="meta-item">
            <Icon icon="mdi:folder" />
            <router-link :to="`/category/${post.category.slug}`">
              {{ post.category.name }}
            </router-link>
          </span>
          <span class="meta-item">
            <Icon icon="mdi:eye" />
            {{ post.views }}
          </span>
          <button
            @click="handleLike"
            class="meta-item like-btn"
            :class="{ liked: isLiked }"
          >
            <Icon :icon="isLiked ? 'mdi:heart' : 'mdi:heart-outline'" />
            {{ post.likes }}
          </button>
          <ShareButton
            :url="shareUrl"
            :title="post.title"
            :description="post.excerpt"
            :show-social-share="true"
          />
        </div>
        <!-- 字数统计和阅读时间 -->
        <div v-if="post.word_count || post.read_time" class="post-stats">
          <span v-if="post.word_count" class="stat-item">
            <Icon icon="mdi:text" />
            <span class="stat-value">{{ formatWordCount(post.word_count) }}</span>
            <span class="stat-label">字</span>
          </span>
          <span v-if="post.read_time" class="stat-item">
            <Icon icon="mdi:clock-outline" />
            <span class="stat-value">{{ post.read_time }}</span>
            <span class="stat-label">分钟</span>
          </span>
        </div>
      </header>
      <div v-if="post.cover" class="post-cover">
        <LazyImage :src="post.cover" :alt="post.title" />
      </div>
      <!-- 加密文章预览 -->
      <div v-if="post.is_encrypted && !post.is_password_verified" class="post-content">
        <div v-if="post.preview_content_html" v-html="post.preview_content_html"></div>
        <div class="encrypted-notice">
          <Icon icon="mdi:lock" />
          <p>此文章已加密，请输入密码查看全文</p>
          <button class="btn-view-full" @click="showPasswordModal = true">
            查看全文
          </button>
        </div>
      </div>
      <!-- 完整内容 -->
      <div v-else class="post-content" v-html="post.content_html"></div>
      <footer class="post-footer">
        <div class="post-tags">
          <Icon icon="mdi:tag" />
          <router-link
            v-for="tag in post.tags"
            :key="tag.id"
            :to="`/tag/${tag.slug}`"
            class="tag-link"
            :style="{ color: tag.color }"
          >
            {{ tag.name }}
          </router-link>
        </div>
      </footer>
      <!-- 相关推荐 -->
      <div v-if="relatedPosts.length > 0 && post && (!post.is_encrypted || post.is_password_verified)" class="related-posts-section">
        <h3 class="related-title">
          <Icon icon="mdi:book-multiple" />
          <span>相关文章</span>
        </h3>
        <div class="related-posts-grid">
          <PostCard v-for="relatedPost in relatedPosts" :key="relatedPost.id" :post="relatedPost" />
        </div>
      </div>
      
      <!-- 评论区域 -->
      <div v-if="post && (!post.is_encrypted || post.is_password_verified)" class="comment-section">
        <CommentList
          content-type="posts.post"
          :object-id="post.id"
        />
      </div>
    </article>
      <!-- 目录（移动端显示在顶部，桌面端显示在右侧） -->
      <TableOfContents
        v-if="post.toc && post.toc.length > 0 && (!post.is_encrypted || post.is_password_verified)"
        :toc="post.toc"
        class="post-toc"
        @item-click="handleTOCClick"
      />
    </div>
    
    <!-- 密码输入弹窗 -->
    <PasswordModal
      ref="passwordModalRef"
      v-model:visible="showPasswordModal"
      title="文章已加密"
      message="此文章已加密，请输入密码查看全文"
      @submit="handlePasswordSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import LazyImage from '@/components/LazyImage.vue'
import CommentList from '@/components/CommentList.vue'
import PasswordModal from '@/components/PasswordModal.vue'
import ShareButton from '@/components/ShareButton.vue'
import TableOfContents from '@/components/TableOfContents.vue'
import PostCard from '@/components/PostCard.vue'
import { initHighlight } from '@/utils/highlight'
import { postsApi, type Post } from '@/api/posts'
import { getCurrentUrl } from '@/utils/clipboard'
import { useThemeStore } from '@/stores/theme'

const route = useRoute()
const themeStore = useThemeStore()

const postLayoutClass = computed(() => {
  const layout = themeStore.currentTheme.layout.postLayout || 'centered'
  return `post-${layout}`
})
const post = ref<Post | null>(null)
const relatedPosts = ref<Post[]>([])
const loading = ref(false)
const isLiked = ref(false)
const showPasswordModal = ref(false)
const passwordModalRef = ref<InstanceType<typeof PasswordModal> | null>(null)
const shareUrl = ref('')

const fetchPost = async () => {
  loading.value = true
  try {
    post.value = await postsApi.getPost(route.params.slug as string)
    if (post.value) {
      isLiked.value = (post.value as any).is_liked || false
      // 生成分享链接
      shareUrl.value = getCurrentUrl()
      // 更新 SEO（延迟执行）
      import('@/utils/seo').then(({ updatePostSEO }) => {
        updatePostSEO(post.value!)
      }).catch(() => {
        // SEO 工具不可用时忽略
      })
      // 获取相关文章
      fetchRelatedPosts()
    }
    await nextTick()
    initHighlight()
  } catch (error: any) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch post:', error)
      console.error('Error details:', {
        message: error?.message,
        response: error?.response?.data,
        status: error?.response?.status,
        slug: route.params.slug
      })
    }
    post.value = null
  } finally {
    loading.value = false
  }
}

const fetchRelatedPosts = async () => {
  if (!post.value) return
  try {
    relatedPosts.value = await postsApi.getRelatedPosts(post.value.slug)
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch related posts:', error)
    }
    relatedPosts.value = []
  }
}

const handleLike = async () => {
  if (!post.value) return
  try {
    const result = await postsApi.likePost(post.value.slug)
    if (post.value && result) {
      isLiked.value = result.liked
      post.value.likes = result.likes
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to like post:', error)
    }
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const formatWordCount = (count: number) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count.toLocaleString()
}

const handlePasswordSubmit = async (password: string) => {
  if (!post.value) return
  
  try {
    await postsApi.verifyPassword(post.value.slug, password)
    // 密码验证成功，重新获取文章
    await fetchPost()
    showPasswordModal.value = false
  } catch (error: any) {
    if (import.meta.env.DEV) {
      console.error('Password verification failed:', error)
    }
    // 显示错误信息
    const errorMsg = error.response?.data?.error || '密码错误，请重试'
    passwordModalRef.value?.setError(errorMsg)
  }
}

const handleTOCClick = (id: string) => {
  // TOC 点击事件已在组件内部处理，这里可以添加额外逻辑
}

// 计算是否有 TOC
const hasTOC = computed(() => {
  return post.value && 
         post.value.toc && 
         post.value.toc.length > 0 && 
         (!post.value.is_encrypted || post.value.is_password_verified)
})

onMounted(() => {
  fetchPost()
})

// 监听路由变化，当 slug 改变时重新获取文章
watch(() => route.params.slug, () => {
  if (route.name === 'Post') {
    fetchPost()
  }
})
</script>

<style scoped>
.post-page {
  max-width: var(--container-max-width, 1200px);
  margin: 0 auto;
  padding: 40px 20px;
  position: relative;
}

/* 文章布局变体 */
.post-centered {
  max-width: 800px;
  margin: 0 auto;
}

.post-wide {
  max-width: 1400px;
  margin: 0 auto;
}

.post-narrow {
  max-width: 700px;
  margin: 0 auto;
}

.post-magazine {
  max-width: 1200px;
  margin: 0 auto;
}

.post-magazine .post-header {
  text-align: center;
  margin-bottom: 40px;
}

.post-magazine .post-title {
  font-size: 48px;
  line-height: 1.2;
  margin-bottom: 20px;
}

.post-magazine .post-content {
  font-size: 18px;
  line-height: 1.9;
  column-count: 2;
  column-gap: 40px;
}

@media (max-width: 768px) {
  .post-magazine .post-content {
    column-count: 1;
  }
}

.post-wrapper {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
  align-items: start;
}

/* 有 TOC 时使用两列布局 */
.post-wrapper.has-toc {
  grid-template-columns: minmax(0, 1fr) 240px;
}

.post-toc {
  position: sticky;
  top: 100px;
  align-self: start;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  width: 240px;
}

.post-article {
  min-width: 0; /* 允许内容收缩 */
  width: 100%;
}

.comment-section {
  grid-column: 1; /* 只占用第一列（文章列） */
  margin: 60px 0 0 0;
  padding: 0;
  width: 100%;
}

/* 移动端适配 */
@media (max-width: 1024px) {
  .post-wrapper {
    display: flex;
    flex-direction: column;
    gap: 30px;
  }
  
  .post-toc {
    position: relative;
    top: 0;
    max-height: none;
    order: -1; /* 移动端 TOC 显示在顶部 */
    width: 100%;
  }
  
  .post-article {
    width: 100%;
  }
  
  .post-page {
    padding: 20px 15px;
  }

  .post-stats {
    gap: 16px;
    font-size: 12px;
  }

  .stat-value {
    font-size: 13px;
  }
}

.post-header {
  margin-bottom: 30px;
}

.post-stats {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  padding: 12px 0;
  font-size: 13px;
  color: var(--text-secondary, #999);
  border-top: 1px solid var(--border-color, #f0f0f0);
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

.stat-item :deep(svg) {
  font-size: 14px;
  color: var(--text-secondary, #999);
  opacity: 0.8;
}

.stat-value {
  font-weight: 500;
  color: var(--text-color, #666);
  font-size: 14px;
}

.stat-label {
  color: var(--text-secondary, #999);
  font-size: 13px;
  margin-left: 2px;
}

.post-title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--text-color, #333);
  line-height: 1.4;
}

.post-meta {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-item :deep(.share-button-wrapper) {
  display: flex;
  align-items: center;
}

.like-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: var(--text-secondary, #666);
  transition: color 0.3s;
}

.like-btn:hover {
  color: var(--primary-color, #FE9600);
}

.like-btn.liked {
  color: #e74c3c;
}

.post-cover {
  margin-bottom: 30px;
  border-radius: 8px;
  overflow: hidden;
}

.post-cover img {
  width: 100%;
  height: auto;
}

.post-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-color, #333);
}

.post-content :deep(h1),
.post-content :deep(h2),
.post-content :deep(h3) {
  margin-top: 30px;
  margin-bottom: 15px;
  font-weight: bold;
}

.post-content :deep(p) {
  margin-bottom: 15px;
}

.post-content :deep(code) {
  background: var(--bg-color, #f5f5f5);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.post-content :deep(pre) {
  background: var(--bg-color, #f5f5f5);
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 20px;
}

.post-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color, #e5e5e5);
}

.post-tags {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tag-link {
  padding: 4px 12px;
  border-radius: 4px;
  background: var(--bg-color, #f5f5f5);
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}

.error-message {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary, #666);
}

.error-message :deep(svg) {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
  color: var(--text-secondary, #999);
}

.error-message p {
  font-size: 18px;
  margin-bottom: 24px;
}

.back-link {
  display: inline-block;
  padding: 12px 24px;
  background: var(--primary-color, #FE9600);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: opacity 0.2s;
}

.back-link:hover {
  opacity: 0.9;
}

.encrypted-notice {
  margin-top: 40px;
  padding: 40px;
  text-align: center;
  background: var(--bg-color, #f5f5f5);
  border-radius: 8px;
  border: 2px dashed var(--border-color, #e5e5e5);
}

.encrypted-notice :deep(svg) {
  font-size: 48px;
  color: var(--text-secondary, #999);
  margin-bottom: 16px;
}

.encrypted-notice p {
  margin: 0 0 20px 0;
  color: var(--text-secondary, #666);
  font-size: 16px;
}

.btn-view-full {
  padding: 12px 24px;
  background: var(--primary-color, #FE9600);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-view-full:hover {
  opacity: 0.9;
}

.related-posts-section {
  grid-column: 1; /* 只占用第一列（文章列） */
  margin: 60px 0 0 0;
  padding: 40px 0;
  border-top: 1px solid var(--border-color, #e5e5e5);
}

.related-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: var(--text-color, #333);
}

.related-posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.comment-section {
  grid-column: 1; /* 只占用第一列（文章列），不与 TOC 重合 */
  max-width: 900px;
  margin: 60px auto 0;
  padding: 0;
  width: 100%;
}

/* 移动端适配 */
@media (max-width: 1024px) {
  .comment-section {
    margin-top: 40px;
  }
}
</style>

