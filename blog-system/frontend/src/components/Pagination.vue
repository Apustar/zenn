<template>
  <div class="pagination">
    <button
      @click="$emit('change', current - 1)"
      :disabled="current === 1"
      class="pagination-btn"
    >
      上一页
    </button>
    <span class="pagination-info">
      第 {{ current }} / {{ total }} 页
    </span>
    <button
      @click="$emit('change', current + 1)"
      :disabled="current === total"
      class="pagination-btn"
    >
      下一页
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  current: number
  total: number
}>()

defineEmits<{
  change: [page: number]
}>()
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  background: var(--card-bg, white);
  color: var(--text-color, #333);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--primary-color, #FE9600);
  color: white;
  border-color: var(--primary-color, #FE9600);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: var(--text-secondary, #666);
  font-size: 14px;
}
</style>

