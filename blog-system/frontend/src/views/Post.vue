<template>
  <div class="post-page">
    <div v-if="loading" class="loading">加载中...</div>
    <article v-else-if="post" class="post-article">
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
    </article>
    
    <!-- 评论区域 -->
    <CommentList
      v-if="post && (!post.is_encrypted || post.is_password_verified)"
      content-type="posts.post"
      :object-id="post.id"
    />
    
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
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import LazyImage from '@/components/LazyImage.vue'
import CommentList from '@/components/CommentList.vue'
import PasswordModal from '@/components/PasswordModal.vue'
import ShareButton from '@/components/ShareButton.vue'
import { initHighlight } from '@/utils/highlight'
import { postsApi, type Post } from '@/api/posts'
import { getCurrentUrl } from '@/utils/clipboard'

const route = useRoute()
const post = ref<Post | null>(null)
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
    }
    await nextTick()
    initHighlight()
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch post:', error)
    }
    post.value = null
  } finally {
    loading.value = false
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

onMounted(() => {
  fetchPost()
})
</script>

<style scoped>
.post-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.post-article {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.post-header {
  margin-bottom: 30px;
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
</style>

