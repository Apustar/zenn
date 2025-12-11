<template>
  <div class="comment-item">
    <div class="comment-header">
      <img
        v-if="comment.author.avatar"
        :src="comment.author.avatar"
        :alt="comment.author.username"
        class="comment-avatar"
      />
      <div class="comment-author">
        <span class="author-name">{{ comment.author.username }}</span>
        <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
      </div>
    </div>
    
    <div class="comment-content">
      <p>{{ comment.content }}</p>
    </div>
    
    <div class="comment-footer">
      <button
        @click="$emit('like', comment.id)"
        class="action-btn"
        :class="{ liked: comment.is_liked }"
      >
        <Icon :icon="comment.is_liked ? 'mdi:heart' : 'mdi:heart-outline'" />
        {{ comment.likes_count }}
      </button>
      <button
        v-if="authStore.isAuthenticated"
        @click="toggleReplyForm"
        class="action-btn"
      >
        <Icon icon="mdi:reply" />
        回复
      </button>
    </div>
    
    <!-- 回复表单 -->
    <div v-if="showReplyForm && authStore.isAuthenticated" class="reply-form">
      <textarea
        v-model="replyContent"
        placeholder="写下你的回复..."
        class="reply-input"
        rows="3"
      />
      <div class="reply-actions">
        <button @click="handleSubmit" :disabled="!replyContent.trim()" class="reply-submit-btn">
          发表回复
        </button>
        <button @click="cancelReply" class="reply-cancel-btn">取消</button>
      </div>
    </div>
    
    <!-- 回复列表 -->
    <div v-if="comment.replies && comment.replies.length" class="replies">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        @like="$emit('like', $event)"
        @reply="$emit('reply', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'
import type { Comment } from '@/api/comments'

const props = defineProps<{
  comment: Comment
}>()

const emit = defineEmits<{
  like: [id: number]
  reply: [data: { parentId: number; content: string }]
}>()

const authStore = useAuthStore()
const showReplyForm = ref(false)
const replyContent = ref('')

const toggleReplyForm = () => {
  showReplyForm.value = !showReplyForm.value
  if (showReplyForm.value) {
    replyContent.value = ''
  }
}

const cancelReply = () => {
  showReplyForm.value = false
  replyContent.value = ''
}

const handleSubmit = () => {
  if (!replyContent.value.trim()) return
  emit('reply', {
    parentId: props.comment.id,
    content: replyContent.value.trim(),
  })
  replyContent.value = ''
  showReplyForm.value = false
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.comment-item {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--border-color, #e5e5e5);
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.comment-author {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.author-name {
  font-weight: bold;
  color: var(--text-color, #333);
}

.comment-time {
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.comment-content {
  margin-bottom: 12px;
  line-height: 1.6;
  color: var(--text-color, #333);
}

.comment-footer {
  display: flex;
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary, #666);
  font-size: 14px;
  transition: color 0.3s;
}

.action-btn:hover {
  color: var(--primary-color, #FE9600);
}

.action-btn.liked {
  color: #e74c3c;
}

.reply-form {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-color, #f5f5f5);
  border-radius: 8px;
}

.reply-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  background: var(--card-bg, white);
  color: var(--text-color, #333);
  margin-bottom: 12px;
}

.reply-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.reply-submit-btn {
  padding: 8px 24px;
  background: var(--primary-color, #FE9600);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.3s;
}

.reply-submit-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.reply-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reply-cancel-btn {
  padding: 8px 24px;
  background: var(--card-bg, white);
  color: var(--text-color, #333);
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.reply-cancel-btn:hover {
  background: var(--bg-color, #f5f5f5);
}

.replies {
  margin-top: 16px;
  padding-left: 20px;
  border-left: 2px solid var(--border-color, #e5e5e5);
}
</style>

