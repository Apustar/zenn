<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <p>&copy; {{ currentYear }} {{ siteTitle }}. All rights reserved.</p>
        <p v-if="icpNumber" class="icp">
          <a href="https://beian.miit.gov.cn/" target="_blank">{{ icpNumber }}</a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const siteTitle = ref('我的博客')
const icpNumber = ref('')
const currentYear = new Date().getFullYear()
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

.icp {
  margin-top: 8px;
}

.icp a {
  color: var(--text-secondary, #666);
  text-decoration: none;
}
</style>

