<template>
  <div class="admin-post-edit">
    <div class="page-header">
      <h1 class="page-title">{{ isNew ? '新建文章' : '编辑文章' }}</h1>
      <div class="header-actions">
        <button @click="handleSaveDraft" class="btn btn-secondary" :disabled="saving">
          {{ saving ? '保存中...' : '保存草稿' }}
        </button>
        <button @click="handlePublish" class="btn btn-primary" :disabled="saving">
          {{ saving ? '发布中...' : '发布文章' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <form v-else @submit.prevent="handleSubmit" class="post-form">
      <div class="form-section">
        <label class="form-label">标题 *</label>
        <input
          v-model="form.title"
          type="text"
          required
          placeholder="请输入文章标题"
          class="form-input"
        />
      </div>

      <div class="form-section">
        <label class="form-label">摘要</label>
        <textarea
          v-model="form.excerpt"
          rows="3"
          placeholder="请输入文章摘要"
          class="form-textarea"
        ></textarea>
      </div>

      <div class="form-section">
        <label class="form-label">内容 *</label>
        <textarea
          v-model="form.content"
          rows="20"
          required
          placeholder="请输入文章内容（支持 Markdown）"
          class="form-textarea form-textarea-large"
        ></textarea>
      </div>

      <div class="form-row">
        <div class="form-section">
          <label class="form-label">分类</label>
          <select v-model="form.category" class="form-select">
            <option :value="null">无分类</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <div class="form-section">
          <label class="form-label">标签</label>
          <div class="tags-input">
            <div v-if="selectedTags.length" class="selected-tags">
              <span
                v-for="tag in selectedTags"
                :key="tag.id"
                class="tag-item"
              >
                {{ tag.name }}
                <button
                  type="button"
                  @click="removeTag(tag.id)"
                  class="tag-remove"
                >
                  ×
                </button>
              </span>
            </div>
            <select @change="addTag" class="form-select">
              <option value="">选择标签...</option>
              <option
                v-for="tag in availableTags"
                :key="tag.id"
                :value="tag.id"
              >
                {{ tag.name }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-row">
        <div class="form-section">
          <label class="form-label">封面图</label>
          <input
            v-model="form.cover"
            type="url"
            placeholder="封面图 URL"
            class="form-input"
          />
        </div>

        <div class="form-section">
          <label class="form-label">发布时间</label>
          <input
            v-model="form.published_at"
            type="datetime-local"
            class="form-input"
          />
        </div>
      </div>

      <div class="form-section">
        <div class="form-checkboxes">
          <label class="checkbox-label">
            <input v-model="form.is_top" type="checkbox" />
            <span>置顶</span>
          </label>
          <label class="checkbox-label">
            <input v-model="form.is_original" type="checkbox" />
            <span>原创</span>
          </label>
          <label class="checkbox-label">
            <input v-model="form.allow_comment" type="checkbox" />
            <span>允许评论</span>
          </label>
          <label class="checkbox-label">
            <input v-model="form.is_encrypted" type="checkbox" />
            <span>加密文章</span>
          </label>
        </div>
      </div>

      <div v-if="form.is_encrypted" class="form-section">
        <label class="form-label">访问密码</label>
        <input
          v-model="form.password"
          type="password"
          placeholder="请输入访问密码"
          class="form-input"
        />
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { postsApi, type Post } from '@/api/posts'
import { categoriesApi, type Category } from '@/api/categories'
import { tagsApi, type Tag } from '@/api/tags'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const saving = ref(false)
const error = ref('')

const isNew = computed(() => route.name === 'AdminPostNew')
const postId = computed(() => {
  const id = route.params.id
  return id && id !== 'new' ? Number(id) : null
})

const form = ref({
  title: '',
  slug: '',
  excerpt: '',
  content: '',
  cover: '',
  category: null as number | null,
  tags: [] as number[],
  status: 'draft' as 'draft' | 'published',
  is_top: false,
  is_original: true,
  allow_comment: true,
  is_encrypted: false,
  password: '',
  published_at: '',
})

const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const selectedTags = ref<Tag[]>([])

const availableTags = computed(() => {
  return tags.value.filter(tag => !selectedTags.value.find(st => st.id === tag.id))
})

const fetchPost = async () => {
  if (!postId.value) return
  
  loading.value = true
  try {
    const post = await postsApi.getPostById(postId.value)
    form.value = {
      title: post.title,
      slug: post.slug,
      excerpt: post.excerpt,
      content: post.content || '',
      cover: post.cover || '',
      category: post.category?.id || null,
      tags: post.tags.map(t => t.id),
      status: post.status || 'draft',
      is_top: post.is_top,
      is_original: post.is_original ?? true,
      allow_comment: post.allow_comment ?? true,
      is_encrypted: post.is_encrypted || false,
      password: '',
      published_at: post.published_at ? new Date(post.published_at).toISOString().slice(0, 16) : '',
    }
    selectedTags.value = post.tags || []
  } catch (err: any) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch post:', err)
    }
    error.value = err.message || '加载文章失败'
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const cats = await categoriesApi.getCategories()
    categories.value = Array.isArray(cats) ? cats : (cats as any).results || []
  } catch (err) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch categories:', err)
    }
  }
}

const fetchTags = async () => {
  try {
    const tgs = await tagsApi.getTags()
    tags.value = Array.isArray(tgs) ? tgs : (tgs as any).results || []
  } catch (err) {
    if (import.meta.env.DEV) {
      console.error('Failed to fetch tags:', err)
    }
  }
}

const addTag = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const tagId = Number(target.value)
  if (tagId && !form.value.tags.includes(tagId)) {
    const tag = tags.value.find(t => t.id === tagId)
    if (tag) {
      form.value.tags.push(tagId)
      selectedTags.value.push(tag)
      target.value = ''
    }
  }
}

const removeTag = (tagId: number) => {
  form.value.tags = form.value.tags.filter(id => id !== tagId)
  selectedTags.value = selectedTags.value.filter(t => t.id !== tagId)
}

const handleSaveDraft = async () => {
  form.value.status = 'draft'
  await handleSubmit()
}

const handlePublish = async () => {
  form.value.status = 'published'
  if (!form.value.published_at) {
    form.value.published_at = new Date().toISOString().slice(0, 16)
  }
  await handleSubmit()
}

const handleSubmit = async () => {
  if (!form.value.title.trim() || !form.value.content.trim()) {
    error.value = '请填写标题和内容'
    return
  }

  saving.value = true
  error.value = ''

  try {
    const data: any = {
      title: form.value.title,
      excerpt: form.value.excerpt,
      content: form.value.content,
      status: form.value.status,
      is_top: form.value.is_top,
      is_original: form.value.is_original,
      allow_comment: form.value.allow_comment,
      is_encrypted: form.value.is_encrypted,
    }

    if (form.value.cover) {
      data.cover = form.value.cover
    }

    if (form.value.category) {
      data.category = form.value.category
    }

    if (form.value.tags.length > 0) {
      data.tags = form.value.tags
    }

    if (form.value.is_encrypted && form.value.password) {
      data.password = form.value.password
    }

    if (form.value.published_at) {
      data.published_at = new Date(form.value.published_at).toISOString()
    }

    let post: Post
    if (isNew.value) {
      post = await postsApi.createPost(data)
    } else {
      post = await postsApi.updatePost(form.value.slug, data)
    }

    router.push('/admin/posts')
  } catch (err: any) {
    if (import.meta.env.DEV) {
      console.error('Failed to save post:', err)
    }
    error.value = err.response?.data?.detail || err.message || '保存失败'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await Promise.all([fetchCategories(), fetchTags()])
  if (!isNew.value && postId.value) {
    await fetchPost()
  }
})
</script>

<style scoped>
.admin-post-edit {
  max-width: 1200px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: var(--text-color, #333);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: var(--primary-color, #FE9600);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-secondary {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-color, #333);
  border: 1px solid var(--border-color, #e5e5e5);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--border-color, #e5e5e5);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.post-form {
  background: var(--card-bg, white);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-color, #333);
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
  font-size: 14px;
  background: var(--bg-color, white);
  color: var(--text-color, #333);
  transition: border-color 0.3s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: var(--primary-color, #FE9600);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.form-textarea-large {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.tags-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 4px;
  font-size: 14px;
}

.tag-remove {
  background: none;
  border: none;
  color: var(--text-secondary, #666);
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  padding: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-remove:hover {
  color: var(--text-color, #333);
}

.form-checkboxes {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-color, #333);
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.error-message {
  padding: 12px;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 6px;
  color: #c33;
  font-size: 14px;
  margin-top: 16px;
}

.loading {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary, #666);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .btn {
    flex: 1;
  }
}
</style>

