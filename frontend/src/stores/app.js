import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index.js'

export const useAppStore = defineStore('app', () => {
  const kbStats = ref({ total_chunks: 0 })
  const isLoading = ref(false)
  const sidebarCollapsed = ref(false)

  async function refreshKBStats() {
    try {
      const data = await api.getKBStats()
      kbStats.value = data
    } catch (e) {
      console.error('Failed to refresh KB stats:', e)
    }
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return { kbStats, isLoading, sidebarCollapsed, refreshKBStats, toggleSidebar }
})
