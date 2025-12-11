<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <h1 class="login-title">登录</h1>
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              autocomplete="username"
              placeholder="请输入用户名"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              autocomplete="current-password"
              placeholder="请输入密码"
              class="form-input"
            />
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <button type="submit" :disabled="loading" class="login-btn">
            <span v-if="loading">登录中...</span>
            <span v-else>登录</span>
          </button>
        </form>
        <div class="login-footer">
          <p>还没有账号？请联系管理员注册</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!form.value.username.trim() || !form.value.password.trim()) {
    error.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const success = await authStore.login(form.value.username, form.value.password)
    if (success) {
      // 登录成功，跳转到之前的页面或首页
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
    } else {
      error.value = '用户名或密码错误'
    }
  } catch (err: any) {
    if (import.meta.env.DEV) {
      console.error('Login error:', err)
    }
    error.value = err.response?.data?.detail || err.message || '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 如果已经登录，直接跳转
onMounted(() => {
  if (authStore.isAuthenticated) {
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  }
})
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--bg-color, #f5f5f5);
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-card {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.login-title {
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
  color: var(--text-color, #333);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color, #333);
}

.form-input {
  padding: 12px 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 4px;
  font-size: 16px;
  background: var(--bg-color, white);
  color: var(--text-color, #333);
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color, #FE9600);
}

.error-message {
  padding: 12px;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  font-size: 14px;
  text-align: center;
}

.login-btn {
  padding: 12px 24px;
  background: var(--primary-color, #FE9600);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.3s;
  margin-top: 10px;
}

.login-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary, #666);
}
</style>

