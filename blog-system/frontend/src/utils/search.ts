/**
 * 搜索相关工具函数
 */

const SEARCH_HISTORY_KEY = 'search_history'
const MAX_HISTORY_LENGTH = 10

/**
 * 保存搜索历史
 */
export function saveSearchHistory(keyword: string): void {
  if (!keyword.trim()) return
  
  try {
    const history = getSearchHistory()
    // 移除重复项
    const filtered = history.filter(item => item !== keyword)
    // 添加到开头
    filtered.unshift(keyword)
    // 限制长度
    const limited = filtered.slice(0, MAX_HISTORY_LENGTH)
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(limited))
  } catch (error) {
    console.error('Failed to save search history:', error)
  }
}

/**
 * 获取搜索历史
 */
export function getSearchHistory(): string[] {
  try {
    const stored = localStorage.getItem(SEARCH_HISTORY_KEY)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('Failed to get search history:', error)
    return []
  }
}

/**
 * 清空搜索历史
 */
export function clearSearchHistory(): void {
  try {
    localStorage.removeItem(SEARCH_HISTORY_KEY)
  } catch (error) {
    console.error('Failed to clear search history:', error)
  }
}

/**
 * 高亮搜索关键词
 */
export function highlightKeyword(text: string, keyword: string): string {
  if (!keyword || !text) return text
  
  const regex = new RegExp(`(${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

