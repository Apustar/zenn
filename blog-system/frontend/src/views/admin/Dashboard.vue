<template>
  <div class="admin-dashboard">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #4CAF50;">
          <Icon icon="mdi:file-document" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.posts }}</div>
          <div class="stat-label">文章总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #2196F3;">
          <Icon icon="mdi:comment" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.comments }}</div>
          <div class="stat-label">评论总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #FF9800;">
          <Icon icon="mdi:eye" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.views }}</div>
          <div class="stat-label">总浏览量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #9C27B0;">
          <Icon icon="mdi:heart" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.likes }}</div>
          <div class="stat-label">总点赞数</div>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="content-section">
        <h2 class="section-title">最近文章</h2>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="recentPosts.length" class="posts-list">
          <div
            v-for="post in recentPosts"
            :key="post.id"
            class="post-item"
            @click="$router.push(`/admin/posts/${post.id}`)"
          >
            <div class="post-info">
              <h3 class="post-title">{{ post.title }}</h3>
              <div class="post-meta">
                <span>{{ formatDate(post.created_at) }}</span>
                <span class="post-status" :class="post.status">
                  {{ getStatusText(post.status) }}
                </span>
              </div>
            </div>
            <div class="post-actions">
              <Icon icon="mdi:chevron-right" />
            </div>
          </div>
        </div>
        <div v-else class="empty">暂无文章</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { postsApi, type Post } from '@/api/posts'
import { commentsApi } from '@/api/comments'

const loading = ref(false)
const stats = ref({
  posts: 0,
  comments: 0,
  views: 0,
  likes: 0,
})
const recentPosts = ref<Post[]>([])

const fetchStats = async () => {
  try {
    // 获取文章统计
    const postsResponse = await postsApi.getPosts({ page: 1 })
    stats.value.posts = postsResponse.count || 0
    recentPosts.value = postsResponse.results?.slice(0, 5) || []
    
    // 计算总浏览量和点赞数（从所有文章）
    let allPosts = [...postsResponse.results]
    let page = 2
    while (postsResponse.next && page <= 10) { // 最多获取10页数据
      try {
        const nextResponse = await postsApi.getPosts({ page })
        allPosts = [...allPosts, ...nextResponse.results]
        if (!nextResponse.next) break
        page++
      } catch {
        break
      }
    }
    stats.value.views = allPosts.reduce((sum, post) => sum + (post.views || 0), 0)
    stats.value.likes = allPosts.reduce((sum, post) => sum + (post.likes || 0), 0)
    
    // 获取评论统计（管理员可以查看所有评论）
    try {
      const commentsResponse = await commentsApi.getAllComments({ page: 1 })
      stats.value.comments = commentsResponse.count || 0
    } catch {
      // 如果获取评论失败，使用默认值
      stats.value.comments = 0
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch stats:', error)
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

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    published: '已发布',
    draft: '草稿',
    archived: '已归档',
  }
  return statusMap[status] || status
}

onMounted(() => {
  loading.value = true
  fetchStats().finally(() => {
    loading.value = false
  })
})
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--text-color, #333);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.dashboard-content {
  display: grid;
  gap: 24px;
}

.content-section {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 20px 0;
  color: var(--text-color, #333);
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.post-item:hover {
  background: var(--bg-secondary, #f5f5f5);
  border-color: var(--primary-color, #FE9600);
}

.post-info {
  flex: 1;
}

.post-title {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 8px 0;
  color: var(--text-color, #333);
}

.post-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.post-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.post-status.published {
  background: #e8f5e9;
  color: #2e7d32;
}

.post-status.draft {
  background: #fff3e0;
  color: #e65100;
}

.post-status.archived {
  background: #f3e5f5;
  color: #6a1b9a;
}

.post-actions {
  color: var(--text-secondary, #666);
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary, #666);
}
</style>

