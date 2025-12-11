<template>
  <img
    :data-src="src"
    :alt="alt"
    :class="['lazyload', className]"
    :src="placeholder"
  />
</template>

<script setup lang="ts">
import 'lazysizes'

defineProps<{
  src: string
  alt?: string
  className?: string
  placeholder?: string
}>()

const placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"%3E%3C/svg%3E'
</script>

<style scoped>
.lazyload {
  opacity: 0;
  transition: opacity 0.3s;
}

.lazyloaded {
  opacity: 1;
}
</style>

