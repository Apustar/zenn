<template>
  <div class="access-denied-page">
    <div class="container">
      <div class="illustration">
        <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#FE9600;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#ff6b6b;stop-opacity:1" />
            </linearGradient>
          </defs>
          <!-- Lock icon -->
          <rect x="150" y="100" width="100" height="120" rx="10" fill="url(#grad1)" opacity="0.2"/>
          <rect x="170" y="120" width="60" height="80" rx="5" fill="url(#grad1)"/>
          <rect x="185" y="80" width="30" height="50" rx="15" fill="none" stroke="url(#grad1)" stroke-width="8"/>
          <circle cx="200" cy="160" r="8" fill="#fff"/>
        </svg>
      </div>
      <h1 class="title">访问受限</h1>
      <p class="message">抱歉，该页面暂不支持访问</p>
      <p class="description">如果您认为这是一个错误，请联系网站管理员</p>
      <div class="actions">
        <router-link to="/" class="btn btn-primary">
          <Icon icon="mdi:home" />
          返回首页
        </router-link>
        <button @click="goBack" class="btn btn-secondary">
          <Icon icon="mdi:arrow-left" />
          返回上一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.access-denied-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.container {
  text-align: center;
  max-width: 600px;
  background: var(--card-bg, white);
  border-radius: 20px;
  padding: 60px 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
}

.illustration {
  margin-bottom: 40px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.illustration svg {
  width: 200px;
  height: 150px;
  margin: 0 auto;
}

.title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #FE9600 0%, #ff6b6b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.message {
  font-size: 24px;
  color: var(--text-color, #333);
  margin-bottom: 12px;
  font-weight: 500;
}

.description {
  font-size: 16px;
  color: var(--text-secondary, #666);
  margin-bottom: 40px;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #FE9600 0%, #ff6b6b 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(254, 150, 0, 0.3);
}

.btn-secondary {
  background: var(--bg-color, #f5f5f5);
  color: var(--text-color, #333);
  border: 2px solid var(--border-color, #e5e5e5);
}

.btn-secondary:hover {
  background: var(--border-color, #e5e5e5);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .container {
    padding: 40px 20px;
  }
  
  .title {
    font-size: 36px;
  }
  
  .message {
    font-size: 20px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>

