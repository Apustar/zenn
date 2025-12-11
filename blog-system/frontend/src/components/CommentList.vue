<template>
  <div class="comment-list">
    <h3 class="comment-title">评论 ({{ comments.length }})</h3>
    
    <!-- 评论表单 -->
    <div v-if="authStore.isAuthenticated" class="comment-form">
      <textarea
        v-model="newComment.content"
        placeholder="写下你的评论..."
        class="comment-input"
        rows="4"
      />
      <button @click="handleSubmit" :disabled="!newComment.content.trim()" class="submit-btn">
        发表评论
      </button>
    </div>
    <div v-else class="comment-login">
      请 <router-link :to="{ path: '/login', query: { redirect: $route.fullPath } }">登录</router-link> 后发表评论
    </div>

    <!-- 评论列表 -->
    <div v-if="comments.length" class="comments">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        @like="handleLike"
        @reply="handleReply"
      />
    </div>
    <div v-else class="empty">暂无评论</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { commentsApi, type Comment } from '@/api/comments'
import { useAuthStore } from '@/stores/auth'
import CommentItem from './CommentItem.vue'

const props = defineProps<{
  contentType: string
  objectId: number
}>()

const route = useRoute()
const authStore = useAuthStore()
const comments = ref<Comment[]>([])
const loading = ref(false)

const newComment = ref({
  content: '',
  parent: undefined as number | undefined,
})

/**
 * 获取 content_type_id
 * 根据 contentType 字符串返回对应的 ContentType ID
 * posts.post -> 6 (Post 模型)
 */
const getContentTypeId = (contentType: string): number => {
  // 根据 contentType 字符串映射到 ContentType ID
  const contentTypeMap: Record<string, number> = {
    'posts.post': 6,  // Post 模型的 ContentType ID
    // 可以添加其他模型的映射
  }
  return contentTypeMap[contentType] || 6  // 默认返回 Post 的 ID
}

const fetchComments = async () => {
  loading.value = true
  try {
    const contentTypeId = getContentTypeId(props.contentType)
    const result = await commentsApi.getComments(contentTypeId.toString(), props.objectId)
    comments.value = Array.isArray(result) ? result : []
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch comments:', error)
    }
    comments.value = []
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!newComment.value.content.trim()) return
  
  try {
    const contentTypeId = getContentTypeId(props.contentType)
    const commentData: {
      content: string
      parent?: number
      content_type: number
      object_id: number
    } = {
      content: newComment.value.content,
      content_type: contentTypeId,
      object_id: props.objectId,
    }
    // 只有当 parent 有值时才添加 parent 字段
    if (newComment.value.parent !== undefined) {
      commentData.parent = newComment.value.parent
    }
    await commentsApi.createComment(commentData)
    newComment.value.content = ''
    newComment.value.parent = undefined
    fetchComments()
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to create comment:', error)
    }
  }
}

const handleLike = async (commentId: number) => {
  try {
    await commentsApi.likeComment(commentId)
    fetchComments()
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to like comment:', error)
    }
  }
}

const handleReply = async (data: { parentId: number; content: string }) => {
  try {
    const contentTypeId = getContentTypeId(props.contentType)
    await commentsApi.createComment({
      content: data.content,
      parent: data.parentId,
      content_type: contentTypeId,
      object_id: props.objectId,
    })
    fetchComments()
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to create reply:', error)
    }
  }
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped>
.comment-list {
  margin-top: 40px;
}

.comment-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 24px;
  color: var(--text-color, #333);
}

.comment-form {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.reply-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  margin-bottom: 12px;
  background: var(--bg-color, #f5f5f5);
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.cancel-reply-btn {
  padding: 4px 12px;
  background: none;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary, #666);
  transition: all 0.3s;
}

.cancel-reply-btn:hover {
  background: var(--border-color, #e5e5e5);
}

.comment-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  background: var(--bg-color, white);
  color: var(--text-color, #333);
  margin-bottom: 12px;
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

.comment-login {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary, #666);
}

.comments {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-secondary, #666);
}
</style>

