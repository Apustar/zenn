<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <p>&copy; {{ currentYear }} {{ siteTitle }}. All rights reserved.</p>
        <div class="footer-links">
          <a :href="rssFeedUrl" class="rss-link" title="订阅 RSS" target="_blank" rel="noopener noreferrer">
            <Icon icon="mdi:rss" />
            RSS
          </a>
        </div>
        <p v-if="icpNumber" class="icp">
          <a href="https://beian.miit.gov.cn/" target="_blank">{{ icpNumber }}</a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'

const siteTitle = ref('我的博客')
const icpNumber = ref('')
const currentYear = new Date().getFullYear()

// RSS Feed URL（使用相对路径，与 API 配置保持一致）
// RSS Feed 不在 /api 路径下，直接使用 /feed/
const rssFeedUrl = computed(() => '/feed/')
</script>

<style scoped>
.footer {
  background: var(--footer-bg, #f5f5f5);
  border-top: 1px solid var(--border-color, #e5e5e5);
  padding: 40px 0;
  margin-top: 60px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content {
  text-align: center;
  color: var(--text-secondary, #666);
  font-size: 14px;
}

.footer-links {
  margin: 12px 0;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.rss-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary, #666);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
}

.rss-link:hover {
  color: var(--primary-color, #FE9600);
}

.rss-link :deep(svg) {
  font-size: 18px;
}

.icp {
  margin-top: 8px;
}

.icp a {
  color: var(--text-secondary, #666);
  text-decoration: none;
}
</style>

