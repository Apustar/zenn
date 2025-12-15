<template>
  <div v-if="visible" class="draft-restore-modal-overlay" @click.self="handleCancel">
    <div class="draft-restore-modal">
      <div class="modal-header">
        <Icon icon="mdi:file-document-edit" class="header-icon" />
        <h3>发现未保存的草稿</h3>
      </div>
      <div class="modal-content">
        <p>检测到您有未保存的草稿，是否要恢复？</p>
        <div v-if="draftData" class="draft-info">
          <div class="draft-item">
            <span class="label">标题：</span>
            <span class="value">{{ draftData.title || '(无标题)' }}</span>
          </div>
          <div v-if="draftData.updated_at" class="draft-item">
            <span class="label">保存时间：</span>
            <span class="value">{{ formatDate(draftData.updated_at) }}</span>
          </div>
        </div>
      </div>
      <div class="modal-actions">
        <button class="btn btn-secondary" @click="handleCancel">取消</button>
        <button class="btn btn-danger" @click="handleDiscard">丢弃草稿</button>
        <button class="btn btn-primary" @click="handleRestore">恢复草稿</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import type { DraftData } from '@/utils/autosave'

interface Props {
  visible: boolean
  draftData: DraftData | null
}

interface Emits {
  (e: 'restore', data: DraftData): void
  (e: 'discard'): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handleRestore = () => {
  if (props.draftData) {
    emit('restore', props.draftData)
  }
}

const handleDiscard = () => {
  emit('discard')
}

const handleCancel = () => {
  emit('cancel')
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.draft-restore-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.draft-restore-modal {
  background: var(--bg-color, #fff);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #e5e5e5);
}

.header-icon {
  font-size: 24px;
  color: var(--primary-color, #FE9600);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #333);
}

.modal-content {
  padding: 24px;
}

.modal-content p {
  margin: 0 0 16px 0;
  color: var(--text-color, #333);
  line-height: 1.6;
}

.draft-info {
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.draft-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.draft-item:last-child {
  margin-bottom: 0;
}

.draft-item .label {
  color: var(--text-secondary, #666);
  font-size: 14px;
  min-width: 80px;
}

.draft-item .value {
  color: var(--text-color, #333);
  font-size: 14px;
  font-weight: 500;
  flex: 1;
  word-break: break-word;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color, #e5e5e5);
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary-color, #FE9600);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-color, #333);
}

.btn-secondary:hover {
  background: var(--border-color, #e5e5e5);
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .draft-restore-modal {
    width: 95%;
    margin: 20px;
  }

  .modal-header,
  .modal-content,
  .modal-actions {
    padding: 16px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>

