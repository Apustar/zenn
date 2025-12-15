<template>
  <div class="admin-posts">
    <div class="page-header">
      <h1 class="page-title">文章管理</h1>
      <router-link to="/admin/posts/new" class="btn btn-primary">
        <Icon icon="mdi:plus" />
        新建文章
      </router-link>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filters">
      <input
        v-model="searchKeyword"
        @input="handleSearch"
        type="text"
        placeholder="搜索文章标题..."
        class="search-input"
      />
      <select v-model="statusFilter" @change="fetchPosts" class="filter-select">
        <option value="">全部状态</option>
        <option value="published">已发布</option>
        <option value="draft">草稿</option>
        <option value="archived">已归档</option>
      </select>
    </div>

    <!-- 文章列表 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="posts.length" class="posts-table">
      <table>
        <thead>
          <tr>
            <th>标题</th>
            <th>分类</th>
            <th>状态</th>
            <th>浏览量</th>
            <th>点赞</th>
            <th>发布时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in posts" :key="post.id">
            <td>
              <div class="post-title-cell">
                <span class="title-text">{{ post.title }}</span>
                <span v-if="post.is_top" class="badge badge-top">置顶</span>
                <span v-if="post.is_encrypted" class="badge badge-encrypted">加密</span>
              </div>
            </td>
            <td>{{ post.category?.name || '-' }}</td>
            <td>
              <span class="status-badge" :class="post.status">
                {{ getStatusText(post.status) }}
              </span>
            </td>
            <td>{{ post.views }}</td>
            <td>{{ post.likes }}</td>
            <td>{{ formatDate(post.published_at || post.created_at) }}</td>
            <td>
              <div class="actions">
                <button
                  @click="$router.push(`/admin/posts/${post.id}`)"
                  class="btn-icon"
                  title="编辑"
                >
                  <Icon icon="mdi:pencil" />
                </button>
                <button
                  @click="handleDelete(post)"
                  class="btn-icon btn-danger"
                  title="删除"
                >
                  <Icon icon="mdi:delete" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="empty">暂无文章</div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="page-btn"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} / {{ totalPages }} 页
      </span>
      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { postsApi, type Post } from '@/api/posts'

const router = useRouter()

const posts = ref<Post[]>([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const searchKeyword = ref('')
const statusFilter = ref('')

const fetchPosts = async (page = 1) => {
  loading.value = true
  try {
    const params: any = { page }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    const response = await postsApi.getPosts(params)
    posts.value = response.results || []
    totalPages.value = response.count ? Math.ceil(response.count / 10) : 1
    currentPage.value = page
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch posts:', error)
    }
    alert('加载文章失败，请稍后重试')
    posts.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 防抖搜索
  clearTimeout((window as any).searchTimer)
  ;(window as any).searchTimer = setTimeout(() => {
    fetchPosts(1)
  }, 300)
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchPosts(page)
  }
}

const handleDelete = async (post: Post) => {
  if (!confirm(`确定要删除文章《${post.title}》吗？此操作不可恢复。`)) {
    return
  }
  
  try {
    await postsApi.deletePost(post.slug)
    alert('删除成功')
    await fetchPosts(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
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
  fetchPosts()
})
</script>

<style scoped>
.admin-posts {
  max-width: 1400px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: var(--text-color, #333);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
}

.btn-primary {
  background: var(--primary-color, #FE9600);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-input {
  flex: 1;
  max-width: 400px;
  padding: 10px 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
  font-size: 14px;
}

.filter-select {
  padding: 10px 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
  font-size: 14px;
  background: var(--card-bg, white);
  cursor: pointer;
}

.posts-table {
  background: var(--card-bg, white);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--bg-secondary, #f5f5f5);
}

th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-color, #333);
  border-bottom: 2px solid var(--border-color, #e5e5e5);
}

td {
  padding: 16px;
  border-bottom: 1px solid var(--border-color, #e5e5e5);
  font-size: 14px;
  color: var(--text-color, #333);
}

tbody tr:hover {
  background: var(--bg-secondary, #f5f5f5);
}

.post-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-text {
  font-weight: 500;
}

.badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-top {
  background: #fff3e0;
  color: #e65100;
}

.badge-encrypted {
  background: #f3e5f5;
  color: #6a1b9a;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.published {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.draft {
  background: #fff3e0;
  color: #e65100;
}

.status-badge.archived {
  background: #f3e5f5;
  color: #6a1b9a;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  padding: 6px;
  background: none;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  color: var(--text-color, #333);
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
}

.btn-icon:hover {
  background: var(--bg-secondary, #f5f5f5);
  border-color: var(--primary-color, #FE9600);
  color: var(--primary-color, #FE9600);
}

.btn-icon.btn-danger:hover {
  background: #fee;
  border-color: #c33;
  color: #c33;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
  background: var(--card-bg, white);
  color: var(--text-color, #333);
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: var(--primary-color, #FE9600);
  color: white;
  border-color: var(--primary-color, #FE9600);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.loading,
.empty {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary, #666);
}
</style>

