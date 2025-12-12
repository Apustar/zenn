<template>
  <Teleport to="body">
    <div v-if="visible" class="password-modal-overlay" @click="handleOverlayClick">
      <div class="password-modal" @click.stop>
        <div class="password-modal-header">
          <h3>{{ title }}</h3>
          <button class="close-btn" @click="handleClose">
            <Icon icon="mdi:close" />
          </button>
        </div>
        <div class="password-modal-body">
          <p class="password-modal-message">{{ message }}</p>
          <div class="password-input-group">
            <input
              ref="passwordInput"
              v-model="password"
              type="password"
              class="password-input"
              :class="{ 'has-error': error }"
              placeholder="请输入密码"
              @keyup.enter="handleSubmit"
              @input="error = ''"
            />
            <p v-if="error" class="error-message">{{ error }}</p>
          </div>
        </div>
        <div class="password-modal-footer">
          <button class="btn btn-secondary" @click="handleClose">取消</button>
          <button class="btn btn-primary" @click="handleSubmit" :disabled="loading || !password">
            {{ loading ? '验证中...' : '确认' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { Icon } from '@iconify/vue'

interface Props {
  visible: boolean
  title?: string
  message?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '输入密码',
  message: '此内容已加密，请输入密码查看'
})

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', password: string): void
  (e: 'close'): void
}>()

const password = ref('')
const error = ref('')
const loading = ref(false)
const passwordInput = ref<HTMLInputElement | null>(null)

watch(() => props.visible, (newVal) => {
  if (newVal) {
    password.value = ''
    error.value = ''
    nextTick(() => {
      passwordInput.value?.focus()
    })
  }
})

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleOverlayClick = () => {
  handleClose()
}

const handleSubmit = () => {
  if (!password.value) {
    error.value = '请输入密码'
    return
  }
  
  error.value = ''
  loading.value = true
  
  // 触发submit事件，让父组件处理验证
  emit('submit', password.value)
}

// 暴露方法供父组件调用
defineExpose({
  setError: (msg: string) => {
    error.value = msg
    loading.value = false
  },
  clearError: () => {
    error.value = ''
  },
  setLoading: (val: boolean) => {
    loading.value = val
  }
})
</script>

<style scoped>
.password-modal-overlay {
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
  animation: fadeIn 0.2s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.password-modal {
  background: var(--card-bg, white);
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.password-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #e5e5e5);
}

.password-modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-color, #333);
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-secondary, #666);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.close-btn:hover {
  color: var(--text-color, #333);
}

.password-modal-body {
  padding: 24px;
}

.password-modal-message {
  margin: 0 0 20px 0;
  color: var(--text-secondary, #666);
  font-size: 14px;
  line-height: 1.6;
}

.password-input-group {
  margin-bottom: 0;
}

.password-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.password-input:focus {
  outline: none;
  border-color: var(--primary-color, #FE9600);
}

.password-input.has-error {
  border-color: #e74c3c;
}

.error-message {
  margin: 8px 0 0 0;
  color: #e74c3c;
  font-size: 14px;
}

.password-modal-footer {
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
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: var(--bg-color, #f5f5f5);
  color: var(--text-color, #333);
}

.btn-secondary:hover {
  background: var(--border-color, #e5e5e5);
}

.btn-primary {
  background: var(--primary-color, #FE9600);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

