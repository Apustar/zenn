<template>
  <li :class="['toc-item', `toc-level-${item.level}`, { active: activeId === item.id }]">
    <a
      :href="`#${item.id}`"
      @click.prevent="handleClick"
      class="toc-link"
    >
      {{ item.text }}
    </a>
    <ul v-if="item.children && item.children.length > 0" class="toc-children">
      <TOCItem
        v-for="child in item.children"
        :key="child.id"
        :item="child"
        :active-id="activeId"
        @click="$emit('click', $event)"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
import type { TOCItem } from '@/api/posts'

const props = defineProps<{
  item: TOCItem
  activeId: string
}>()

const emit = defineEmits<{
  (e: 'click', id: string): void
}>()

const handleClick = () => {
  emit('click', props.item.id)
}
</script>

<style scoped>
.toc-item {
  margin: 0;
  padding: 0;
}

.toc-link {
  display: block;
  padding: 5px 8px;
  color: var(--text-secondary, #666);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
  line-height: 1.5;
  word-break: break-word;
}

.toc-link:hover {
  color: var(--primary-color, #FE9600);
  background: var(--bg-color, #f5f5f5);
}

.toc-item.active > .toc-link {
  color: var(--primary-color, #FE9600);
  font-weight: 600;
  background: var(--bg-color, #f5f5f5);
}

/* 不同级别的缩进 - 优化为更紧凑的布局 */
.toc-level-1 > .toc-link {
  font-weight: 600;
  font-size: 14px;
  padding-left: 8px;
}

.toc-level-2 > .toc-link {
  padding-left: 16px;
  font-size: 13px;
}

.toc-level-3 > .toc-link {
  padding-left: 24px;
  font-size: 12px;
}

.toc-level-4 > .toc-link {
  padding-left: 32px;
  font-size: 12px;
}

.toc-level-5 > .toc-link {
  padding-left: 40px;
  font-size: 11px;
}

.toc-level-6 > .toc-link {
  padding-left: 48px;
  font-size: 11px;
}

.toc-children {
  list-style: none;
  padding: 0;
  margin: 0;
  margin-top: 4px;
}
</style>

