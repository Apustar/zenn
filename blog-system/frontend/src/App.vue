<template>
  <div id="app" class="app-container">
    <Header />
    <ReadingProgressBar />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <Footer />
    <BackToTop />
    <MusicPlayer />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import BackToTop from './components/BackToTop.vue'
import MusicPlayer from './components/MusicPlayer.vue'
import ReadingProgressBar from './components/ReadingProgressBar.vue'

onMounted(() => {
  // 初始化 SEO（延迟执行，避免影响页面渲染）
  import('./utils/seo')
    .then(({ resetSEO }) => resetSEO())
    .catch(() => {
      // SEO 工具不可用时静默失败
    })
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-bottom: 80px; /* 为音乐播放器展开时预留空间 */
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
