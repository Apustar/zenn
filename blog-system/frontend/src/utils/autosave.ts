/**
 * 文章草稿自动保存工具
 */

export interface DraftData {
  id?: number
  slug?: string
  title: string
  content: string
  excerpt?: string
  category?: number
  tags?: number[]
  cover?: string
  is_top?: boolean
  is_original?: boolean
  allow_comment?: boolean
  is_encrypted?: boolean
  password?: string
  updated_at?: string
}

const STORAGE_KEY_PREFIX = 'post_draft_'
const AUTOSAVE_INTERVAL = 30000 // 30秒自动保存到后端
const DEBOUNCE_DELAY = 1000 // 1秒防抖延迟
const OFFLINE_QUEUE_KEY = 'autosave_offline_queue' // 离线队列存储键

/**
 * 网络状态检测
 */
export function isOnline(): boolean {
  return navigator.onLine
}

/**
 * 添加网络状态监听器
 */
export function addNetworkStatusListener(callback: (online: boolean) => void): () => void {
  const handleOnline = () => callback(true)
  const handleOffline = () => callback(false)
  
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
  
  // 返回清理函数
  return () => {
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
  }
}

/**
 * 获取离线队列
 */
function getOfflineQueue(): Array<{ postId?: number; data: DraftData; timestamp: number }> {
  try {
    const queue = localStorage.getItem(OFFLINE_QUEUE_KEY)
    return queue ? JSON.parse(queue) : []
  } catch {
    return []
  }
}

/**
 * 保存到离线队列
 */
function saveToOfflineQueue(postId: number | undefined, data: DraftData): void {
  try {
    const queue = getOfflineQueue()
    queue.push({
      postId,
      data,
      timestamp: Date.now()
    })
    localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue))
  } catch (error) {
    console.error('Failed to save to offline queue:', error)
  }
}

/**
 * 清空离线队列
 */
function clearOfflineQueue(): void {
  try {
    localStorage.removeItem(OFFLINE_QUEUE_KEY)
  } catch (error) {
    console.error('Failed to clear offline queue:', error)
  }
}

/**
 * 获取草稿的存储键
 */
function getStorageKey(postId?: number): string {
  if (postId) {
    return `${STORAGE_KEY_PREFIX}${postId}`
  }
  return `${STORAGE_KEY_PREFIX}new`
}

/**
 * 保存草稿到 localStorage
 */
export function saveDraftToLocal(postId: number | undefined, data: DraftData): void {
  try {
    const key = getStorageKey(postId)
    const draftData = {
      ...data,
      saved_at: new Date().toISOString(),
    }
    localStorage.setItem(key, JSON.stringify(draftData))
  } catch (error) {
    console.error('Failed to save draft to localStorage:', error)
  }
}

/**
 * 从 localStorage 加载草稿
 */
export function loadDraftFromLocal(postId?: number): DraftData | null {
  try {
    const key = getStorageKey(postId)
    const stored = localStorage.getItem(key)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (error) {
    console.error('Failed to load draft from localStorage:', error)
  }
  return null
}

/**
 * 删除本地草稿
 */
export function removeDraftFromLocal(postId?: number): void {
  try {
    const key = getStorageKey(postId)
    localStorage.removeItem(key)
  } catch (error) {
    console.error('Failed to remove draft from localStorage:', error)
  }
}

/**
 * 检查是否有未保存的草稿
 */
export function hasUnsavedDraft(postId?: number): boolean {
  return loadDraftFromLocal(postId) !== null
}

/**
 * 自动保存管理器
 */
export class AutosaveManager {
  private postId: number | undefined
  private saveTimer: number | null = null
  private debounceTimer: number | null = null
  private lastSavedData: DraftData | null = null
  private isSaving = false
  private autosaveCallback?: (data: DraftData) => Promise<void>
  private isOnline = true
  private removeNetworkListener?: () => void

  constructor(postId?: number, autosaveCallback?: (data: DraftData) => Promise<void>) {
    this.postId = postId
    this.autosaveCallback = autosaveCallback
    
    // 初始化网络状态监听
    this.isOnline = isOnline()
    this.removeNetworkListener = addNetworkStatusListener((online) => {
      this.isOnline = online
      if (online) {
        // 网络恢复时，尝试同步离线队列
        this.syncOfflineQueue()
      }
    })
  }

  /**
   * 更新文章数据（防抖保存到本地）
   */
  update(data: DraftData): void {
    // 立即保存到本地存储
    saveDraftToLocal(this.postId, data)

    // 防抖：延迟保存到后端
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer)
    }

    this.debounceTimer = window.setTimeout(() => {
      this.lastSavedData = data
      if (this.isOnline) {
        this.scheduleAutosave()
      } else {
        // 离线状态下，添加到离线队列
        saveToOfflineQueue(this.postId, data)
      }
    }, DEBOUNCE_DELAY)
  }

  /**
   * 安排自动保存到后端
   */
  private scheduleAutosave(): void {
    if (this.saveTimer) {
      clearTimeout(this.saveTimer)
    }

    this.saveTimer = window.setTimeout(() => {
      this.saveToBackend()
    }, AUTOSAVE_INTERVAL)
  }

  /**
   * 立即保存到后端
   */
  async saveToBackend(force = false): Promise<void> {
    if (this.isSaving && !force) {
      return
    }

    if (!this.lastSavedData || !this.autosaveCallback) {
      return
    }

    if (!this.isOnline && !force) {
      // 离线状态下，添加到离线队列
      saveToOfflineQueue(this.postId, this.lastSavedData)
      return
    }

    this.isSaving = true
    try {
      await this.autosaveCallback(this.lastSavedData)
      // 保存成功后清除定时器
      if (this.saveTimer) {
        clearTimeout(this.saveTimer)
        this.saveTimer = null
      }
    } catch (error) {
      console.error('Autosave failed:', error)
      // 保存失败时，添加到离线队列
      saveToOfflineQueue(this.postId, this.lastSavedData)
    } finally {
      this.isSaving = false
    }
  }

  /**
   * 同步离线队列
   */
  private async syncOfflineQueue(): Promise<void> {
    if (!this.autosaveCallback || this.isSaving) {
      return
    }

    const queue = getOfflineQueue()
    if (queue.length === 0) {
      return
    }

    this.isSaving = true
    try {
      // 按时间戳排序，先处理旧的
      queue.sort((a, b) => a.timestamp - b.timestamp)
      
      for (const item of queue) {
        try {
          await this.autosaveCallback(item.data)
        } catch (error) {
          console.error('Failed to sync offline draft:', error)
          // 如果某个同步失败，停止同步并保留队列
          break
        }
      }
      
      // 所有同步成功，清空队列
      clearOfflineQueue()
    } catch (error) {
      console.error('Sync offline queue failed:', error)
    } finally {
      this.isSaving = false
    }
  }

  /**
   * 清理资源
   */
  destroy(): void {
    if (this.saveTimer) {
      clearTimeout(this.saveTimer)
      this.saveTimer = null
    }
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer)
      this.debounceTimer = null
    }
    if (this.removeNetworkListener) {
      this.removeNetworkListener()
    }
  }

  /**
   * 设置文章 ID（用于更新现有文章）
   */
  setPostId(postId: number): void {
    this.postId = postId
  }

  /**
   * 获取网络状态
   */
  getNetworkStatus(): boolean {
    return this.isOnline
  }

  /**
   * 获取离线队列长度
   */
  getOfflineQueueLength(): number {
    return getOfflineQueue().length
  }
}

