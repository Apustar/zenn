/**
 * 文章自动保存 Composable
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { AutosaveManager, type DraftData, loadDraftFromLocal, removeDraftFromLocal, hasUnsavedDraft } from '@/utils/autosave'
import { postsApi } from '@/api/posts'

export function useAutosave(postId?: number) {
  const route = useRoute()
  const autosaveManager = ref<AutosaveManager | null>(null)
  const isSaving = ref(false)
  const lastSavedAt = ref<Date | null>(null)
  const showRestoreModal = ref(false)
  const draftData = ref<DraftData | null>(null)

  // 初始化自动保存管理器
  const initAutosave = (initialData?: DraftData) => {
    const currentPostId = postId || (route.params.id as string | undefined)
    const id = currentPostId ? parseInt(currentPostId) : undefined

    autosaveManager.value = new AutosaveManager(id, async (data: DraftData) => {
      await saveToBackend(data)
    })

    // 检查是否有未保存的草稿
    if (!initialData) {
      checkForDraft(id)
    }
  }

  // 检查是否有未保存的草稿
  const checkForDraft = (id?: number) => {
    if (hasUnsavedDraft(id)) {
      draftData.value = loadDraftFromLocal(id)
      showRestoreModal.value = true
    }
  }

  // 保存到后端
  const saveToBackend = async (data: DraftData) => {
    if (isSaving.value) return

    isSaving.value = true
    try {
      const currentPostId = postId || (route.params.id as string | undefined)
      
      if (currentPostId) {
        // 更新现有文章
        const slug = typeof currentPostId === 'string' ? currentPostId : data.slug || ''
        if (slug) {
          await postsApi.autosavePost(slug, data)
        }
      } else {
        // 创建新草稿
        const result = await postsApi.autosaveCreatePost(data)
        if (result && result.id) {
          // 更新 postId，后续保存将更新现有文章
          autosaveManager.value?.setPostId(result.id)
          postId = result.id
        }
      }
      
      lastSavedAt.value = new Date()
    } catch (error) {
      console.error('Autosave failed:', error)
      throw error
    } finally {
      isSaving.value = false
    }
  }

  // 更新文章数据
  const updateDraft = (data: DraftData) => {
    if (autosaveManager.value) {
      autosaveManager.value.update(data)
    }
  }

  // 恢复草稿
  const restoreDraft = (data: DraftData) => {
    showRestoreModal.value = false
    return data
  }

  // 丢弃草稿
  const discardDraft = (id?: number) => {
    removeDraftFromLocal(id)
    showRestoreModal.value = false
    draftData.value = null
  }

  // 手动保存
  const manualSave = async (data: DraftData) => {
    await saveToBackend(data)
    // 保存成功后清除本地草稿
    const currentPostId = postId || (route.params.id as string | undefined)
    const id = currentPostId ? parseInt(currentPostId) : undefined
    removeDraftFromLocal(id)
  }

  // 清理资源
  const cleanup = () => {
    if (autosaveManager.value) {
      autosaveManager.value.destroy()
      autosaveManager.value = null
    }
  }

  // 组件卸载时清理
  onUnmounted(() => {
    cleanup()
  })

  return {
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
  }
}

