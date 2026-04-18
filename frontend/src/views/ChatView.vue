<template>
  <div class="chat-view animate-fade-in stagger-children">
    <div class="chat-page">
      <aside class="chat-sidebar card-static">
        <div class="sidebar-header">
          <h3>会话</h3>
          <button class="btn btn-primary" @click="newSession">新建</button>
        </div>
        <div class="session-list">
          <button
            v-for="s in chatStore.sessions"
            :key="s.id"
            class="session-item"
            :class="{ active: s.id === chatStore.activeSessionId }"
            @click="chatStore.setActiveSession(s.id)"
          >
            <div class="session-title">{{ s.title || '新对话' }}</div>
            <div class="session-meta">
              <span>{{ formatTime(s.updated_at) }}</span>
              <span v-if="chatStore.isSessionWaiting(s.id)">处理中</span>
            </div>
            <span
              class="session-delete"
              @click.stop="deleteSession(s.id)"
              v-if="chatStore.sessions.length > 1"
            >x</span>
          </button>
        </div>
      </aside>

      <div class="chat-main">
        <div class="page-header">
          <h2 class="section-title">智能问答</h2>
          <p class="section-subtitle">支持多会话与历史管理，切换页面时任务继续执行</p>
        </div>

        <div class="chat-container card-static">
          <div class="chat-messages" ref="messagesContainer">
            <div v-if="messages.length === 0" class="empty-state">
              <div class="empty-icon">?</div>
              <h3>开始对话</h3>
              <p>示例：请总结近期上传文档核心结论；提取关键数据指标。</p>
              <div class="suggested-questions">
                <button class="badge badge-cyan" @click="suggestQuestion('请总结近期上传文档核心结论')">
                  总结核心结论
                </button>
                <button class="badge badge-blue" @click="suggestQuestion('提取关键数据指标')">
                  提取关键指标
                </button>
                <button class="badge badge-purple" @click="suggestQuestion('最新业务进展如何？')">
                  业务进展查询
                </button>
              </div>
            </div>

            <div
              v-for="msg in messages"
              :key="msg.id"
              class="message-wrapper"
              :class="msg.role === 'user' ? 'message-user' : 'message-assistant'"
            >
              <div class="avatar">{{ msg.role === 'user' ? 'U' : 'AI' }}</div>
              <div class="message-content">
                <div class="message-meta">{{ msg.role === 'user' ? '用户' : '智能助手' }}</div>
                <div class="message-text" v-html="formatMessage(msg.content)"></div>
              </div>
            </div>

            <div v-if="isTyping" class="message-wrapper message-assistant">
              <div class="avatar">AI</div>
              <div class="message-content typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>

          <div v-if="uploadStatus" class="upload-status" :class="uploadStatus.type">
            {{ uploadStatus.text }}
          </div>
          <div class="chat-input-area">
            <input type="file" ref="fileInput" multiple accept=".pdf,.doc,.docx,.txt,.md,.csv,.xlsx,.xls,.pptx" style="display:none" @change="handleFileUpload" />
            <button class="btn btn-ghost upload-btn" @click="$refs.fileInput.click()" :disabled="uploading" :title="'上传文档到知识库'">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
            </button>
            <textarea
              class="input chat-textarea"
              v-model="inputQuery"
              placeholder="请输入您的问题... (Shift+Enter 换行, Enter 发送)"
              @keydown.enter="handleEnter"
              rows="1"
            ></textarea>
            <button class="btn btn-primary send-btn" @click="sendMessage" :disabled="!inputQuery.trim()">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, nextTick, onMounted, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import api from '../api/index.js'

const inputQuery = ref('')
const messagesContainer = ref(null)
const fileInput = ref(null)
const uploading = ref(false)
const uploadStatus = ref(null)
const chatStore = useChatStore()

const messages = computed(() => chatStore.activeSession?.messages || [])
const isTyping = computed(() => chatStore.isSessionWaiting(chatStore.activeSessionId))

const formatMessage = (text) => {
  if (!text) return ''
  return text.replace(/\n/g, '<br/>')
}

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  const hh = `${d.getHours()}`.padStart(2, '0')
  const mm = `${d.getMinutes()}`.padStart(2, '0')
  return `${hh}:${mm}`
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const suggestQuestion = (q) => {
  inputQuery.value = q
}

const handleEnter = (e) => {
  if (!e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const sendMessage = async () => {
  const text = inputQuery.value.trim()
  if (!text) return
  inputQuery.value = ''
  await chatStore.sendMessage(text)
  scrollToBottom()
}

const handleFileUpload = async (e) => {
  const files = e.target.files
  if (!files || !files.length) return
  uploading.value = true
  uploadStatus.value = { type: 'info', text: `正在上传 ${files.length} 个文件到知识库...` }
  try {
    const formData = new FormData()
    for (const f of files) {
      formData.append('files', f)
    }
    const res = await api.uploadFiles(formData)
    uploadStatus.value = { type: 'success', text: `上传成功 ${res.success_count}/${res.total} 个文件` }
  } catch (err) {
    uploadStatus.value = { type: 'error', text: `上传失败: ${err?.message || '未知错误'}` }
  } finally {
    uploading.value = false
    e.target.value = ''
    setTimeout(() => { uploadStatus.value = null }, 4000)
  }
}

const newSession = () => {
  chatStore.createSession()
}

const deleteSession = (id) => {
  chatStore.deleteSession(id)
}

onMounted(() => {
  chatStore.init()
  scrollToBottom()
})

watch(
  messages,
  async () => {
    await nextTick()
    scrollToBottom()
  },
  { deep: true }
)
</script>

<style scoped>
.chat-view {
  max-width: 1200px;
  margin: 0 auto;
  height: calc(100vh - 120px);
}

.chat-page {
  height: 100%;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1rem;
}

.chat-sidebar {
  padding: 0.8rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.8rem;
  flex-shrink: 0;
}

.session-list {
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.session-item {
  text-align: left;
  border: 1px solid var(--border-subtle);
  background: var(--bg-input);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
  padding: 0.6rem 0.7rem;
  position: relative;
  cursor: pointer;
}

.session-item.active {
  border-color: var(--accent-blue);
  box-shadow: inset 0 0 0 1px var(--accent-blue);
}

.session-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  margin-bottom: 0.2rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.session-delete {
  position: absolute;
  right: 6px;
  top: 6px;
  font-size: 14px;
  color: var(--text-muted);
}

.chat-main {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.page-header {
  flex-shrink: 0;
  margin-bottom: 1rem;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  text-align: center;
  gap: 1rem;
}

.empty-icon {
  font-size: 3rem;
  opacity: 0.5;
}

.empty-state h3 {
  color: var(--text-primary);
  font-size: var(--font-size-xl);
}

.suggested-questions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.suggested-questions button {
  cursor: pointer;
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.suggested-questions button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.message-wrapper {
  display: flex;
  gap: 1rem;
  max-width: 85%;
  animation: slideInLeft 0.3s ease-out both;
}

.message-user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-assistant {
  align-self: flex-start;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: inset 0 0 0 1px var(--border-subtle);
}

.message-content {
  background: var(--bg-input);
  padding: 1rem 1.25rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  position: relative;
}

.message-user .message-content {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.2);
  border-top-right-radius: 0;
}

.message-assistant .message-content {
  background: rgba(17, 24, 39, 0.8);
  border-top-left-radius: 0;
}

.message-meta {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.message-user .message-meta {
  text-align: right;
}

.message-text {
  color: var(--text-primary);
  line-height: 1.6;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 1.25rem !important;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input-area {
  padding: 1.5rem;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  gap: 1rem;
  background: var(--bg-secondary);
}

.chat-textarea {
  flex: 1;
  resize: none;
  min-height: 48px;
  max-height: 200px;
  border-radius: var(--radius-md);
  padding-top: 0.75rem;
}

.send-btn {
  width: 48px;
  height: 48px;
  padding: 0;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.upload-btn {
  width: 48px;
  height: 48px;
  padding: 0;
  border-radius: var(--radius-md);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
  background: var(--bg-input);
}

.upload-btn:hover {
  color: var(--accent-blue);
  border-color: var(--accent-blue);
}

.upload-status {
  padding: 0.5rem 1.5rem;
  font-size: var(--font-size-sm);
  border-top: 1px solid var(--border-subtle);
}

.upload-status.info { color: var(--accent-blue); }
.upload-status.success { color: var(--accent-green, #22c55e); }
.upload-status.error { color: var(--accent-red, #ef4444); }

@media (max-width: 960px) {
  .chat-page {
    grid-template-columns: 1fr;
  }

  .chat-sidebar {
    max-height: 180px;
  }
}
</style>
