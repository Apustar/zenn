# 文章草稿自动保存使用指南

## 功能概述

文章草稿自动保存功能提供了以下特性：

1. **本地自动保存**：使用 `localStorage` 实时保存编辑内容（1秒防抖）
2. **后端自动保存**：每30秒自动保存到服务器
3. **草稿恢复**：页面加载时检测并提示恢复未保存的草稿
4. **手动保存**：支持手动触发保存

## 使用方法

### 1. 在文章编辑页面中使用

```vue
<template>
  <div class="post-editor">
    <!-- 草稿恢复提示弹窗 -->
    <DraftRestoreModal
      :visible="showRestoreModal"
      :draft-data="draftData"
      @restore="handleRestoreDraft"
      @discard="handleDiscardDraft"
      @cancel="showRestoreModal = false"
    />

    <!-- 保存状态提示 -->
    <div v-if="isSaving" class="save-status">
      <Icon icon="mdi:loading" class="spinning" />
      正在保存...
    </div>
    <div v-else-if="lastSavedAt" class="save-status saved">
      <Icon icon="mdi:check-circle" />
      已保存 {{ formatTime(lastSavedAt) }}
    </div>

    <!-- 编辑表单 -->
    <form @submit.prevent="handleSubmit">
      <input
        v-model="formData.title"
        @input="handleInput"
        placeholder="文章标题"
      />
      <textarea
        v-model="formData.content"
        @input="handleInput"
        placeholder="文章内容"
      />
      <!-- 其他表单字段... -->
      
      <button type="submit">发布</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import DraftRestoreModal from '@/components/DraftRestoreModal.vue'
import { useAutosave, type DraftData } from '@/composables/useAutosave'
import { postsApi } from '@/api/posts'

const route = useRoute()
const postId = ref<number | undefined>(undefined)

// 表单数据
const formData = ref({
  title: '',
  content: '',
  excerpt: '',
  category: undefined,
  tags: [],
  // ... 其他字段
})

// 使用自动保存
const {
  initAutosave,
  updateDraft,
  restoreDraft,
  discardDraft,
  manualSave,
  isSaving,
  lastSavedAt,
  showRestoreModal,
  draftData,
  cleanup,
} = useAutosave(postId.value)

// 处理输入变化
const handleInput = () => {
  updateDraft({
    ...formData.value,
    id: postId.value,
  })
}

// 恢复草稿
const handleRestoreDraft = (data: DraftData) => {
  const restored = restoreDraft(data)
  if (restored) {
    formData.value = {
      title: restored.title || '',
      content: restored.content || '',
      excerpt: restored.excerpt || '',
      category: restored.category,
      tags: restored.tags || [],
      // ... 恢复其他字段
    }
    if (restored.id) {
      postId.value = restored.id
    }
  }
}

// 丢弃草稿
const handleDiscardDraft = () => {
  discardDraft(postId.value)
}

// 提交表单
const handleSubmit = async () => {
  try {
    // 手动保存（发布前确保保存）
    await manualSave({
      ...formData.value,
      id: postId.value,
      status: 'published', // 发布状态
    })
    
    // 然后调用发布 API
    if (postId.value) {
      await postsApi.updatePost(route.params.slug as string, {
        ...formData.value,
        status: 'published',
      })
    } else {
      await postsApi.createPost({
        ...formData.value,
        status: 'published',
      })
    }
    
    // 清除本地草稿
    cleanup()
    
    // 跳转到文章页面
    // router.push(...)
  } catch (error) {
    console.error('Failed to publish:', error)
  }
}

// 格式化时间
const formatTime = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const seconds = Math.floor(diff / 1000)
  
  if (seconds < 60) {
    return '刚刚'
  } else if (seconds < 3600) {
    return `${Math.floor(seconds / 60)}分钟前`
  } else {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
}

// 初始化
onMounted(async () => {
  // 如果是编辑现有文章，加载文章数据
  if (route.params.slug) {
    try {
      const post = await postsApi.getPost(route.params.slug as string)
      postId.value = post.id
      formData.value = {
        title: post.title,
        content: post.content || '',
        excerpt: post.excerpt,
        category: post.category?.id,
        tags: post.tags.map(t => t.id),
        // ... 其他字段
      }
    } catch (error) {
      console.error('Failed to load post:', error)
    }
  }
  
  // 初始化自动保存
  initAutosave(formData.value)
})

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.save-status {
  position: fixed;
  top: 80px;
  right: 20px;
  padding: 8px 16px;
  background: var(--bg-color, #fff);
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary, #666);
  display: flex;
  align-items: center;
  gap: 6px;
  z-index: 1000;
}

.save-status.saved {
  color: #28a745;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
```

## API 说明

### 后端 API

#### 自动保存现有文章
```
POST /api/posts/{slug}/autosave/
```

请求体：
```json
{
  "title": "文章标题",
  "content": "文章内容",
  "excerpt": "摘要",
  "category": 1,
  "tags": [1, 2, 3],
  ...
}
```

响应：
```json
{
  "code": 200,
  "message": "自动保存成功",
  "data": {
    "id": 1,
    "slug": "article-slug",
    "title": "文章标题",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

#### 创建新草稿
```
POST /api/posts/autosave_create/
```

请求体和响应格式同上。

### 前端工具函数

#### `AutosaveManager` 类

```typescript
const manager = new AutosaveManager(postId, async (data) => {
  // 保存到后端的回调函数
  await postsApi.autosavePost(slug, data)
})

// 更新数据（自动触发本地保存和防抖保存到后端）
manager.update(draftData)

// 立即保存到后端
await manager.saveToBackend()

// 清理资源
manager.destroy()
```

#### `useAutosave` Composable

```typescript
const {
  initAutosave,      // 初始化自动保存
  updateDraft,       // 更新草稿数据
  restoreDraft,      // 恢复草稿
  discardDraft,      // 丢弃草稿
  manualSave,        // 手动保存
  isSaving,          // 是否正在保存
  lastSavedAt,       // 最后保存时间
  showRestoreModal,  // 是否显示恢复弹窗
  draftData,         // 草稿数据
  cleanup,           // 清理资源
} = useAutosave(postId)
```

## 配置说明

### 自动保存间隔

在 `src/utils/autosave.ts` 中可以修改：

```typescript
const AUTOSAVE_INTERVAL = 30000 // 30秒（毫秒）
const DEBOUNCE_DELAY = 1000     // 1秒防抖延迟（毫秒）
```

### 存储键名

本地存储使用以下键名格式：
- 新文章：`post_draft_new`
- 现有文章：`post_draft_{postId}`

## 注意事项

1. **权限要求**：自动保存需要用户登录，只有文章作者可以保存自己的文章
2. **数据格式**：确保传递给 `updateDraft` 的数据格式正确
3. **清理资源**：组件卸载时记得调用 `cleanup()` 清理定时器
4. **错误处理**：自动保存失败不会影响用户编辑，但会在控制台输出错误信息
5. **草稿状态**：自动保存的文章状态始终为 `draft`，发布时需要手动设置状态

## 最佳实践

1. **页面加载时检查草稿**：使用 `useAutosave` 的 `initAutosave` 会自动检查
2. **用户输入时更新**：在 `@input` 事件中调用 `updateDraft`
3. **发布前手动保存**：确保发布前数据已保存到服务器
4. **发布成功后清理**：发布成功后调用 `cleanup()` 清除本地草稿

