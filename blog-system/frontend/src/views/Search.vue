<template>
  <div class="search-page">
    <div class="container">
      <h1 class="page-title">搜索</h1>
      
      <!-- 搜索框 -->
      <div class="search-box-wrapper">
        <div class="search-box">
          <div class="search-input-wrapper">
            <Icon icon="mdi:magnify" class="search-icon" />
            <input
              ref="searchInput"
              v-model="keyword"
              @input="handleInput"
              @focus="showSuggestions = true"
              @blur="handleBlur"
              @keyup.enter="handleSearch"
              @keyup.escape="showSuggestions = false"
              type="text"
              placeholder="输入关键词搜索..."
              class="search-input"
            />
            <button
              v-if="keyword"
              @click="clearSearch"
              class="clear-btn"
            >
              <Icon icon="mdi:close" />
            </button>
          </div>
          <button @click="handleSearch" class="search-btn">
            搜索
          </button>
        </div>
        
        <!-- 搜索建议和历史 -->
        <div v-if="showSuggestions && (suggestions.length > 0 || searchHistory.length > 0)" class="suggestions-box">
          <!-- 搜索建议 -->
          <div v-if="suggestions.length > 0" class="suggestions-section">
            <div class="suggestions-header">
              <Icon icon="mdi:lightbulb-on" />
              <span>搜索建议</span>
            </div>
            <div
              v-for="(suggestion, index) in suggestions"
              :key="`suggestion-${index}`"
              @mousedown="selectSuggestion(suggestion)"
              class="suggestion-item"
            >
              <Icon icon="mdi:magnify" />
              <span v-html="highlightKeyword(suggestion, keyword)"></span>
            </div>
          </div>
          
          <!-- 搜索历史 -->
          <div v-if="searchHistory.length > 0 && !keyword" class="suggestions-section">
            <div class="suggestions-header">
              <Icon icon="mdi:history" />
              <span>搜索历史</span>
              <button @click="clearHistory" class="clear-history-btn">
                <Icon icon="mdi:delete-outline" />
              </button>
            </div>
            <div
              v-for="(item, index) in searchHistory"
              :key="`history-${index}`"
              @mousedown="selectSuggestion(item)"
              class="suggestion-item"
            >
              <Icon icon="mdi:clock-outline" />
              <span>{{ item }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 筛选器 -->
      <div v-if="searched || results.length > 0" class="filters">
        <div class="filter-group">
          <label>分类：</label>
          <select v-model="selectedCategory" @change="handleFilterChange" class="filter-select">
            <option value="">全部</option>
            <option v-for="cat in categories" :key="cat?.id || cat" :value="cat?.id">
              {{ cat?.name }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label>标签：</label>
          <select v-model="selectedTag" @change="handleFilterChange" class="filter-select">
            <option value="">全部</option>
            <option v-for="tag in tags" :key="tag?.id || tag" :value="tag?.id">
              {{ tag?.name }}
            </option>
          </select>
        </div>
        <div v-if="selectedCategory || selectedTag" class="filter-actions">
          <button @click="clearFilters" class="clear-filters-btn">
            <Icon icon="mdi:close-circle" />
            清除筛选
          </button>
        </div>
      </div>
      
      <!-- 搜索结果 -->
      <div v-if="loading" class="loading">
        <Icon icon="mdi:loading" class="spinning" />
        搜索中...
      </div>
      <div v-else-if="results.length" class="search-results">
        <div class="results-header">
          <span>找到 {{ results.length }} 条结果</span>
        </div>
        <div class="results-grid">
          <PostCard
            v-for="post in results"
            :key="post.id"
            :post="post"
            :highlight-keyword="keyword"
          />
        </div>
      </div>
      <div v-else-if="searched" class="empty">
        <Icon icon="mdi:file-search-outline" />
        <p>未找到相关文章</p>
        <p class="empty-tip">试试其他关键词或清除筛选条件</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { postsApi, type Post } from '@/api/posts'
import { categoriesApi, type Category } from '@/api/categories'
import { tagsApi, type Tag } from '@/api/tags'
import PostCard from '@/components/PostCard.vue'
import { saveSearchHistory, getSearchHistory, clearSearchHistory, highlightKeyword } from '@/utils/search'

const keyword = ref('')
const results = ref<Post[]>([])
const loading = ref(false)
const searched = ref(false)
const searchInput = ref<HTMLInputElement | null>(null)
const suggestions = ref<string[]>([])
const showSuggestions = ref(false)
const searchHistory = ref<string[]>([])
const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const selectedCategory = ref<number | ''>('')
const selectedTag = ref<number | ''>('')

// 防抖获取搜索建议
let suggestionTimer: number | null = null
const fetchSuggestions = async () => {
  if (suggestionTimer) {
    clearTimeout(suggestionTimer)
  }
  
  suggestionTimer = window.setTimeout(async () => {
    if (keyword.value.trim().length >= 2) {
      try {
        suggestions.value = await postsApi.getSearchSuggestions(keyword.value)
      } catch (error) {
        if (import.meta.env.DEV) {
          console.error('Failed to fetch suggestions:', error)
        }
        suggestions.value = []
      }
    } else {
      suggestions.value = []
    }
  }, 300)
}

const handleInput = () => {
  fetchSuggestions()
  if (keyword.value.trim()) {
    showSuggestions.value = true
  }
}

const handleBlur = () => {
  // 延迟隐藏，允许点击建议项
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

const selectSuggestion = (text: string) => {
  keyword.value = text
  showSuggestions.value = false
  handleSearch()
}

const clearSearch = () => {
  keyword.value = ''
  suggestions.value = []
  showSuggestions.value = false
}

const handleSearch = async () => {
  if (!keyword.value.trim()) return
  
  // 保存搜索历史
  saveSearchHistory(keyword.value)
  searchHistory.value = getSearchHistory()
  
  loading.value = true
  searched.value = true
  showSuggestions.value = false
  
  try {
    const params: any = {}
    
    // 搜索关键词
    if (keyword.value.trim()) {
      params.search = keyword.value.trim()
    }
    
    // 分类筛选
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    
    // 标签筛选（ManyToMany 关系，使用标签 ID）
    if (selectedTag.value) {
      params.tags = selectedTag.value
    }
    
    const response = await postsApi.getPosts(params)
    results.value = response.results || []
    
    // 调试：检查搜索结果
    if (import.meta.env.DEV) {
      console.log('Search results:', results.value)
      console.log('First result:', results.value[0])
      if (results.value.length > 0 && !results.value[0].slug) {
        console.warn('Warning: Search result missing slug field:', results.value[0])
      }
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Search failed:', error)
    }
    results.value = []
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  if (searched.value) {
    handleSearch()
  }
}

const clearFilters = () => {
  selectedCategory.value = ''
  selectedTag.value = ''
  if (searched.value) {
    handleSearch()
  }
}

const clearHistory = () => {
  clearSearchHistory()
  searchHistory.value = []
}

// 加载分类和标签
const loadFilters = async () => {
  try {
    const cats = await categoriesApi.getCategories()
    const tgs = await tagsApi.getTags()
    
    // 处理分类数据：可能是数组或分页格式
    let categoriesList: Category[] = []
    if (Array.isArray(cats)) {
      categoriesList = cats
    } else if (cats && typeof cats === 'object' && 'results' in cats) {
      // 分页格式：{ count, next, previous, results }
      categoriesList = Array.isArray(cats.results) ? cats.results : []
    }
    categories.value = categoriesList.filter(cat => cat != null && cat.id != null)
    
    // 处理标签数据：可能是数组或分页格式
    let tagsList: Tag[] = []
    if (Array.isArray(tgs)) {
      tagsList = tgs
    } else if (tgs && typeof tgs === 'object' && 'results' in tgs) {
      // 分页格式：{ count, next, previous, results }
      tagsList = Array.isArray(tgs.results) ? tgs.results : []
    }
    tags.value = tagsList.filter(tag => tag != null && tag.id != null)
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to load filters:', error)
    }
    categories.value = []
    tags.value = []
  }
}

// 页面加载时自动聚焦搜索框
onMounted(async () => {
  await nextTick()
  if (searchInput.value) {
    searchInput.value.focus()
  }
  searchHistory.value = getSearchHistory()
  loadFilters()
})
</script>

<style scoped>
.search-page {
  padding: 40px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 40px;
  color: var(--text-color, #333);
}

.search-box-wrapper {
  position: relative;
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 16px;
  font-size: 20px;
  color: var(--text-secondary, #999);
  pointer-events: none;
}

.search-input {
  flex: 1;
  padding: 12px 16px 12px 48px;
  border: 2px solid var(--border-color, #e5e5e5);
  border-radius: 8px;
  font-size: 16px;
  background: var(--card-bg, white);
  color: var(--text-color, #333);
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color, #FE9600);
}

.clear-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: var(--text-secondary, #999);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.3s;
}

.clear-btn:hover {
  color: var(--text-color, #333);
}

.search-btn {
  padding: 12px 32px;
  background: var(--primary-color, #FE9600);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: opacity 0.3s;
}

.search-btn:hover {
  opacity: 0.9;
}

.suggestions-box {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--card-bg, white);
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  max-height: 400px;
  overflow-y: auto;
}

.suggestions-section {
  padding: 8px 0;
}

.suggestions-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #666);
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.clear-history-btn {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--text-secondary, #666);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.suggestion-item:hover {
  background: var(--bg-secondary, #f5f5f5);
}

.suggestion-item :deep(mark) {
  background: var(--primary-color, #FE9600);
  color: white;
  padding: 2px 4px;
  border-radius: 2px;
}

.filters {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 30px;
  padding: 16px;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 8px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  color: var(--text-color, #333);
  font-weight: 500;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
  background: var(--card-bg, white);
  color: var(--text-color, #333);
  font-size: 14px;
  cursor: pointer;
}

.filter-actions {
  margin-left: auto;
}

.clear-filters-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-color, white);
  border: 1px solid var(--border-color, #e5e5e5);
  border-radius: 6px;
  color: var(--text-secondary, #666);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-filters-btn:hover {
  background: var(--border-color, #e5e5e5);
  color: var(--text-color, #333);
}

.results-header {
  margin-bottom: 20px;
  color: var(--text-secondary, #666);
  font-size: 14px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
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

.empty {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary, #666);
}

.empty :deep(svg) {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-tip {
  margin-top: 8px;
  font-size: 14px;
  color: var(--text-secondary, #999);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
  }
  
  .search-btn {
    width: 100%;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-select {
    flex: 1;
  }
  
  .filter-actions {
    margin-left: 0;
    width: 100%;
  }
  
  .clear-filters-btn {
    width: 100%;
    justify-content: center;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
