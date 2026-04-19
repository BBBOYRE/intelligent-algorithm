import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index.js'

export const useAppStore = defineStore('app', () => {
  const kbStats = ref({ total_chunks: 0 })
  const isLoading = ref(false)
  const sidebarCollapsed = ref(false)
  const drawerVisible = ref(false)

  // Knowledge Bases (Projects)
  const knowledgeBases = ref([])
  const currentKbId = ref('default')
  const currentTeamId = ref(null)

  async function refreshKBStats() {
    try {
      const data = await api.getKBStats(currentKbId.value)
      kbStats.value = data
    } catch (e) {
      console.error('Failed to refresh KB stats:', e)
    }
  }

  async function fetchKnowledgeBases() {
    try {
      const res = await api.listKBs()
      knowledgeBases.value = res.knowledge_bases || []
      
      // Select first personal KB if current is invalid
      if (!knowledgeBases.value.find(k => k.id === currentKbId.value)) {
        if (knowledgeBases.value.length > 0) {
          switchKb(knowledgeBases.value[0].id)
        }
      }
    } catch (e) {
      console.error('Failed to fetch KBs:', e)
    }
  }

  function switchKb(kbId) {
    const kb = knowledgeBases.value.find(k => k.id === kbId)
    if (kb) {
      currentKbId.value = kb.id
      currentTeamId.value = kb.team_id || null
      refreshKBStats()
    }
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function toggleDrawer() {
    drawerVisible.value = !drawerVisible.value
  }

  return { 
    kbStats, isLoading, sidebarCollapsed, drawerVisible, 
    knowledgeBases, currentKbId, currentTeamId,
    refreshKBStats, toggleSidebar, toggleDrawer, fetchKnowledgeBases, switchKb 
  }
})
