<template>
  <div class="inbox-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">收件箱</h2>
      <p class="section-subtitle">查看消息和团队邀请</p>
    </div>

    <div class="inbox-actions">
      <n-button type="primary" size="small" @click="showCompose = true">发送消息</n-button>
    </div>

    <div class="inbox-list card-static" v-if="messages.length > 0">
      <div v-for="msg in messages" :key="msg.id" class="inbox-item" :class="{ unread: msg.status === 'unread' }">
        <div class="inbox-item-left">
          <div class="inbox-type-badge" :class="msg.type">{{ msg.type === 'team_invite' ? '邀请' : '消息' }}</div>
          <div class="inbox-item-info">
            <div class="inbox-title">{{ msg.title }}</div>
            <div class="inbox-meta">来自 {{ msg.sender_name }} · {{ formatTime(msg.created_at) }}</div>
            <div class="inbox-content" v-if="msg.content">{{ msg.content }}</div>
          </div>
        </div>
        <div class="inbox-item-actions">
          <template v-if="msg.type === 'team_invite' && msg.status === 'unread'">
            <n-button size="tiny" type="success" @click="handleAccept(msg)">接受</n-button>
            <n-button size="tiny" type="error" quaternary @click="handleReject(msg)">拒绝</n-button>
          </template>
          <n-tag v-else-if="msg.status === 'accepted'" type="success" size="small">已接受</n-tag>
          <n-tag v-else-if="msg.status === 'rejected'" type="error" size="small">已拒绝</n-tag>
          <n-button v-if="msg.status === 'unread' && msg.type === 'message'" size="tiny" quaternary @click="handleMarkRead(msg)">标记已读</n-button>
          <n-button size="tiny" quaternary type="error" @click="handleDelete(msg)">删除</n-button>
        </div>
      </div>
    </div>
    <div class="empty-state card-static" v-else>
      <p>收件箱为空</p>
    </div>

    <n-modal v-model:show="showCompose" preset="dialog" title="发送消息" positive-text="发送" negative-text="取消" @positive-click="handleSend">
      <n-form :model="composeForm">
        <n-form-item label="收件人邮箱">
          <n-input v-model:value="composeForm.recipient_email" placeholder="输入对方邮箱" />
        </n-form-item>
        <n-form-item label="标题">
          <n-input v-model:value="composeForm.title" placeholder="消息标题" />
        </n-form-item>
        <n-form-item label="内容">
          <n-input v-model:value="composeForm.content" type="textarea" placeholder="消息内容" :rows="4" />
        </n-form-item>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '../api/index.js'

const message = useMessage()
const messages = ref([])
const showCompose = ref(false)
const composeForm = ref({ recipient_email: '', title: '', content: '' })

const loadInbox = async () => {
  try {
    messages.value = await api.getInbox()
  } catch { messages.value = [] }
}

const formatTime = (iso) => {
  if (!iso) return ''
  return iso.replace('T', ' ').slice(0, 16)
}

const handleAccept = async (msg) => {
  try {
    await api.acceptInvite(msg.id)
    message.success('已接受邀请')
    await loadInbox()
  } catch (e) { message.error(e.response?.data?.detail || '操作失败') }
}

const handleReject = async (msg) => {
  try {
    await api.rejectInvite(msg.id)
    message.info('已拒绝邀请')
    await loadInbox()
  } catch (e) { message.error(e.response?.data?.detail || '操作失败') }
}

const handleMarkRead = async (msg) => {
  try {
    await api.markRead(msg.id)
    await loadInbox()
  } catch {}
}

const handleDelete = async (msg) => {
  try {
    await api.deleteInboxMessage(msg.id)
    await loadInbox()
  } catch {}
}

const handleSend = async () => {
  if (!composeForm.value.recipient_email || !composeForm.value.title) {
    message.warning('请填写收件人和标题')
    return false
  }
  try {
    await api.sendInboxMessage(composeForm.value)
    message.success('消息已发送')
    composeForm.value = { recipient_email: '', title: '', content: '' }
    showCompose.value = false
  } catch (e) { message.error(e.response?.data?.detail || '发送失败') }
}

onMounted(loadInbox)
</script>

<style scoped>
.inbox-view { max-width: 900px; margin: 0 auto; }
.page-header { margin-bottom: 1rem; }
.inbox-actions { margin-bottom: 1rem; }
.inbox-list { padding: 0; }
.inbox-item {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-subtle);
  gap: 1rem;
}
.inbox-item.unread { background: rgba(59, 130, 246, 0.05); }
.inbox-item:last-child { border-bottom: none; }
.inbox-item-left { display: flex; gap: 0.75rem; flex: 1; min-width: 0; }
.inbox-type-badge {
  padding: 0.2rem 0.5rem; border-radius: var(--radius-sm); font-size: var(--font-size-xs);
  font-weight: 600; flex-shrink: 0; height: fit-content; margin-top: 0.1rem;
}
.inbox-type-badge.team_invite { background: rgba(234, 179, 8, 0.15); color: #eab308; }
.inbox-type-badge.message { background: rgba(59, 130, 246, 0.15); color: var(--accent-blue); }
.inbox-item-info { min-width: 0; }
.inbox-title { font-weight: 600; color: var(--text-primary); }
.inbox-meta { font-size: var(--font-size-xs); color: var(--text-muted); margin-top: 0.2rem; }
.inbox-content { font-size: var(--font-size-sm); color: var(--text-secondary); margin-top: 0.3rem; }
.inbox-item-actions { display: flex; gap: 0.5rem; flex-shrink: 0; align-items: center; }
.empty-state { padding: 3rem; text-align: center; color: var(--text-muted); }
</style>
