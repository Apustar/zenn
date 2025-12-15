<template>
  <div class="admin-comments">
    <div class="page-header">
      <h1 class="page-title">评论管理</h1>
      <div class="header-filters">
        <select v-model="approvalFilter" @change="fetchComments" class="filter-select">
          <option value="">全部</option>
          <option value="true">已审核</option>
          <option value="false">待审核</option>
        </select>
        <input
          v-model="searchKeyword"
          @input="handleSearch"
          type="text"
          placeholder="搜索评论内容..."
          class="search-input"
        />
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="comments.length" class="comments-list">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="comment-item"
        :class="{ 'not-approved': !comment.is_approved }"
      >
        <div class="comment-header">
          <div class="comment-author">
            <img
              v-if="comment.author.avatar"
              :src="comment.author.avatar"
              :alt="comment.author.username"
              class="avatar"
            />
            <div v-else class="avatar-placeholder">
              {{ comment.author.username.charAt(0).toUpperCase() }}
            </div>
            <div class="author-info">
              <span class="username">{{ comment.author.username }}</span>
              <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
            </div>
          </div>
          <div class="comment-status">
            <span
              v-if="!comment.is_approved"
              class="status-badge pending"
            >
              待审核
            </span>
            <span v-else class="status-badge approved">已审核</span>
          </div>
        </div>
        <div class="comment-content">
          {{ comment.content }}
        </div>
        <div class="comment-actions">
          <button
            v-if="!comment.is_approved"
            @click="handleApprove(comment, true)"
            class="btn btn-sm btn-success"
          >
            通过审核
          </button>
          <button
            v-else
            @click="handleApprove(comment, false)"
            class="btn btn-sm btn-warning"
          >
            取消审核
          </button>
          <button
            @click="handleDelete(comment)"
            class="btn btn-sm btn-danger"
          >
            删除
          </button>
        </div>
      </div>
    </div>
    <div v-else class="empty">暂无评论</div>

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
import { commentsApi, type Comment } from '@/api/comments'

const loading = ref(false)
const comments = ref<Comment[]>([])
const currentPage = ref(1)
const totalPages = ref(1)
const approvalFilter = ref('')
const searchKeyword = ref('')

const fetchComments = async (page = 1) => {
  loading.value = true
  try {
    const params: any = { page }
    if (approvalFilter.value) {
      params.is_approved = approvalFilter.value === 'true'
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    const response = await commentsApi.getAllComments(params)
    comments.value = response.results || []
    totalPages.value = response.count ? Math.ceil(response.count / 10) : 1
    currentPage.value = page
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch comments:', error)
    }
    alert('加载评论失败，请稍后重试')
    comments.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  clearTimeout((window as any).commentSearchTimer)
  ;(window as any).commentSearchTimer = setTimeout(() => {
    fetchComments(1)
  }, 300)
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchComments(page)
  }
}

const handleApprove = async (comment: Comment, approved: boolean) => {
  try {
    await commentsApi.approveComment(comment.id, approved)
    alert(approved ? '审核通过' : '已取消审核')
    await fetchComments(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '操作失败'
    alert(`操作失败: ${message}`)
  }
}

const handleDelete = async (comment: Comment) => {
  if (!confirm(`确定要删除这条评论吗？此操作不可恢复。`)) {
    return
  }
  
  try {
    await commentsApi.deleteComment(comment.id)
    alert('删除成功')
    await fetchComments(currentPage.value)
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '删除失败'
    alert(`删除失败: ${message}`)
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped>
.admin-comments {
  max-width: 1200px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: var(--text-color, #333);
}

.header-filters {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select,
.search-input {
  padding: 8px 12px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  font-size: 14px;
}

.search-input {
  min-width: 200px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comment-item.not-approved {
  border-left: 4px solid #ff9800;
  background: #fff9e6;
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar,
.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color, #FE9600);
  color: white;
  font-weight: bold;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-weight: 600;
  color: var(--text-color, #333);
}

.comment-time {
  font-size: 12px;
  color: var(--text-secondary, #999);
}

.comment-status {
  display: flex;
  gap: 8px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.approved {
  background: #d4edda;
  color: #155724;
}

.comment-content {
  margin-bottom: 12px;
  line-height: 1.6;
  color: var(--text-color, #333);
  white-space: pre-wrap;
  word-break: break-word;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #218838;
}

.btn-warning {
  background: #ffc107;
  color: #333;
}

.btn-warning:hover {
  background: #e0a800;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.loading,
.empty {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary, #666);
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
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: var(--bg-secondary, #f5f5f5);
  border-color: var(--primary-color, #FE9600);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-secondary, #666);
  font-size: 14px;
}
</style>
