import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../api/index.js'
import { useAppStore } from './app'

function nowIso() {
  return new Date().toISOString()
}

function uid(prefix = 'id') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

function getStorageKey() {
  try {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    const userId = user?.id || 'anonymous'
    return `chat_store_v2_${userId}`
  } catch {
    return 'chat_store_v2_anonymous'
  }
}

export const useChatStore = defineStore('chat', () => {
  const sessions = ref([])
  const activeSessionId = ref('')
  const pendingQueue = ref([])
  const processing = ref(false)
  const currentProcessingSessionId = ref('')
  const isInitialized = ref(false)

  const activeSession = computed(() => sessions.value.find(s => s.id === activeSessionId.value) || null)

  const saveState = () => {
    // We now rely on backend, but we can store activeSessionId in localStorage
    const payload = {
      activeSessionId: activeSessionId.value,
    }
    localStorage.setItem(getStorageKey(), JSON.stringify(payload))
  }

  const init = async () => {
    isInitialized.value = true
    try {
      const raw = localStorage.getItem(getStorageKey())
      if (raw) {
        const data = JSON.parse(raw)
        if (typeof data?.activeSessionId === 'string') activeSessionId.value = data.activeSessionId
      }
    } catch {}

    try {
      const res = await api.getChatSessions();
      sessions.value = res || [];
    } catch (err) {
      console.error('Failed to init chat sessions', err)
      sessions.value = []
    }

    if (!sessions.value.length) {
      try {
        const first = await api.createChatSession()
        sessions.value = [first]
        activeSessionId.value = first.id
        saveState()
      } catch (err) {}
      return
    }

    if (!sessions.value.some(s => s.id === activeSessionId.value)) {
      activeSessionId.value = sessions.value[0].id
      saveState()
    }
  }

  const ensureReady = async () => {
    if (!isInitialized.value) await init()
  }

  const setActiveSession = async (id) => {
    await ensureReady()
    if (sessions.value.some(s => s.id === id)) {
      activeSessionId.value = id
      saveState()
    }
  }

  const createSession = async () => {
    await ensureReady()
    try {
      const session = await api.createChatSession()
      sessions.value.unshift(session)
      activeSessionId.value = session.id
      saveState()
      return session.id
    } catch (err) {
      return null
    }
  }

  const deleteSession = async (id) => {
    await ensureReady()
    if (sessions.value.length <= 1) return
    try {
      await api.deleteChatSession(id)
      sessions.value = sessions.value.filter(s => s.id !== id)
      pendingQueue.value = pendingQueue.value.filter(item => item.sessionId !== id)
      if (activeSessionId.value === id) {
        activeSessionId.value = sessions.value[0]?.id || ''
      }
      saveState()
    } catch (err) {}
  }

  const updateSessionTitleIfNeeded = async (session, text) => {
    if (session.messages.length > 1) return
    const short = text.trim().slice(0, 20)
    if (short) {
      session.title = short
      try {
        await api.updateChatSession(session.id, short)
      } catch {}
    }
  }

  const enqueueMessage = (sessionId, messageId, text) => {
    pendingQueue.value.push({ sessionId, messageId, text })
    void processQueue()
  }

  const processQueue = async () => {
    if (processing.value) return
    processing.value = true
    try {
      while (pendingQueue.value.length) {
        const current = pendingQueue.value.shift()
        const session = sessions.value.find(s => s.id === current.sessionId)
        if (!session) continue
        currentProcessingSessionId.value = current.sessionId

        const msgIdx = session.messages.findIndex(m => m.id === current.messageId)
        if (msgIdx < 0) continue

        const historyPayload = session.messages
          .slice(0, msgIdx)
          .map(m => ({ role: m.role, content: m.content }))
        
        // Add placeholder message for streaming
        const assistMessageId = uid('msg')
        session.messages.push({
          id: assistMessageId,
          role: 'assistant',
          content: '',
          created_at: nowIso(),
        })
        
        try {
          const appStore = useAppStore()
          const res = await api.chatStream(
            current.text, 
            historyPayload, 
            { session_id: session.id, kb_id: appStore.currentKbId },
            (chunk, fullReply) => {
              const msg = session.messages.find(m => m.id === assistMessageId)
              if (msg) {
                msg.content = fullReply
              }
            }
          )
          
          // Verify final message content
          const finalMsg = session.messages.find(m => m.id === assistMessageId)
          if (finalMsg && !finalMsg.content) {
             finalMsg.content = res?.reply || "I don't have an answer."
          }
        } catch (err) {
          const errMsg = session.messages.find(m => m.id === assistMessageId)
          if (errMsg) {
            errMsg.content = `[请求出错] ${err?.message || '未知错误'}`
          }
        }
        session.updated_at = nowIso()
        // Instead of saveState full payload, we refetch to ensure consistency if desired, or skip
        // but backend saved it so we are good.
      }
    } finally {
      currentProcessingSessionId.value = ''
      processing.value = false
    }
  }

  const sendMessage = async (text, sessionId = activeSessionId.value) => {
    const content = String(text || '').trim()
    if (!content) return
    await ensureReady()
    const session = sessions.value.find(s => s.id === sessionId)
    if (!session) return

    const messageId = uid('msg')
    session.messages.push({
      id: messageId,
      role: 'user',
      content,
      created_at: nowIso(),
    })
    session.updated_at = nowIso()
    updateSessionTitleIfNeeded(session, content)
    
    enqueueMessage(sessionId, messageId, content)
  }

  const isSessionWaiting = (sessionId) => {
    const hasPending = pendingQueue.value.some(item => item.sessionId === sessionId)
    if (hasPending) return true
    if (processing.value && currentProcessingSessionId.value === sessionId) return true
    return false
  }

  return {
    sessions,
    activeSessionId,
    activeSession,
    pendingQueue,
    processing,
    init,
    setActiveSession,
    createSession,
    deleteSession,
    sendMessage,
    isSessionWaiting,
  }
})

