<template>
  <div class="chat-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">智能问答</h2>
      <p class="section-subtitle">基于您的知识库，使用大语言模型进行精准的内容查询与分析。</p>
    </div>

    <div class="chat-container card-static">
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">💬</div>
          <h3>开始对话</h3>
          <p>尝试提问关于您已上传的文档内容。例如："这篇文档总结了什么？" 或 "核心数据指标是多少？"</p>
          <div class="suggested-questions">
            <button class="badge badge-cyan" @click="suggestQuestion('请总结一下近期上传的文档核心内容')">
              请总结核心内容
            </button>
            <button class="badge badge-blue" @click="suggestQuestion('提取所有的关键数据指标')">
              提取关键指标
            </button>
            <button class="badge badge-purple" @click="suggestQuestion('最新的业务进展如何？')">
              业务进展查询
            </button>
          </div>
        </div>

        <div 
          v-for="(msg, index) in messages" 
          :key="index"
          class="message-wrapper"
          :class="msg.role === 'user' ? 'message-user' : 'message-assistant'"
        >
          <div class="avatar">{{ msg.role === 'user' ? '🧑' : '🤖' }}</div>
          <div class="message-content">
            <div class="message-meta">{{ msg.role === 'user' ? '用户' : '智能助手' }}</div>
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
          </div>
        </div>

        <div v-if="isTyping" class="message-wrapper message-assistant">
          <div class="avatar">🤖</div>
          <div class="message-content typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <textarea 
          class="input chat-textarea" 
          v-model="inputQuery" 
          placeholder="请输入您的问题... (Shift+Enter 换行, Enter 发送)"
          @keydown.enter="handleEnter"
          :disabled="isTyping"
          rows="1"
        ></textarea>
        <button class="btn btn-primary send-btn" @click="sendMessage" :disabled="!inputQuery.trim() || isTyping">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useToast } from '../composables/useToast'
import api from '../api/index.js'

const messages = ref([])
const inputQuery = ref('')
const isTyping = ref(false)
const messagesContainer = ref(null)
const toast = useToast()

const formatMessage = (text) => {
  // basic markdown to html mapping for newlines
  if (!text) return ''
  return text
    .replace(/\n/g, '<br/>')
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const suggestQuestion = (q) => {
  inputQuery.value = q
  // optional: auto send -> sendMessage()
}

const handleEnter = (e) => {
  if (!e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const sendMessage = async () => {
  const text = inputQuery.value.trim()
  if (!text || isTyping.value) return

  inputQuery.value = ''
  
  // Add user message
  messages.value.push({ role: 'user', content: text })
  scrollToBottom()
  
  isTyping.value = true

  try {
    // Send history (exclude last newly added user message to avoid duplicate inside API logic, if needed)
    // Actually the logic typically requires the full history minus the current one, or just the current.
    // Our agent.py takes `message` and `chat_history`.
    const historyPayload = messages.value.slice(0, -1) 
    
    const res = await api.chat(text, historyPayload)
    
    messages.value.push({ role: 'assistant', content: res.reply || res.answer || res || "I don't have an answer." })
  } catch (err) {
    toast.error('请求失败: ' + err.message)
    messages.value.push({ role: 'assistant', content: `[请求出错] ${err.message}` })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.chat-view {
  max-width: 1000px;
  margin: 0 auto;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
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
  font-size: 1.25rem;
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

/* Typing indicator */
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
</style>
