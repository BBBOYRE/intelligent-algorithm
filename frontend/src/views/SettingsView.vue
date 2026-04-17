<template>
  <div class="settings-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">系统设置</h2>
      <p class="section-subtitle">管理个人信息、密码和知识库</p>
    </div>

    <div class="settings-grid">
      <!-- 个人信息 -->
      <div class="card-static settings-card">
        <h3 class="card-title">个人信息</h3>
        <div class="info-row">
          <span class="info-label">用户名</span>
          <span class="info-value">{{ authStore.user?.username || '-' }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">邮箱</span>
          <span class="info-value">{{ authStore.user?.email || '-' }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">角色</span>
          <n-tag :type="authStore.user?.role === 'admin' ? 'warning' : 'info'" size="small">
            {{ authStore.user?.role === 'admin' ? '管理员' : '成员' }}
          </n-tag>
        </div>
      </div>

      <!-- 修改密码 -->
      <div class="card-static settings-card">
        <h3 class="card-title">修改密码</h3>
        <n-form :model="pwdForm" class="pwd-form">
          <n-form-item label="新密码">
            <n-input v-model:value="pwdForm.password" type="password" show-password-on="click" placeholder="输入新密码（至少6位）" />
          </n-form-item>
          <n-form-item label="确认密码">
            <n-input v-model:value="pwdForm.confirm" type="password" show-password-on="click" placeholder="再次输入新密码" />
          </n-form-item>
          <n-button type="primary" :disabled="!pwdForm.password || pwdForm.password.length < 6 || pwdForm.password !== pwdForm.confirm">
            更新密码
          </n-button>
        </n-form>
      </div>

      <!-- 知识库管理 -->
      <div class="card-static settings-card kb-card">
        <div class="card-title-row">
          <h3 class="card-title">知识库管理</h3>
          <n-button size="small" type="primary" @click="showCreateKB = true">新建知识库</n-button>
        </div>

        <div class="kb-list" v-if="knowledgeBases.length > 0">
          <div class="kb-item" v-for="kb in knowledgeBases" :key="kb.id">
            <div class="kb-item-info">
              <span class="kb-name">{{ kb.name }}</span>
              <span class="kb-meta">{{ kb.total_chunks }} 分块 / {{ kb.documents.length }} 文档</span>
            </div>
            <n-button size="tiny" type="error" quaternary @click="handleDeleteKB(kb)">删除</n-button>
          </div>
        </div>
        <div class="empty-kb" v-else>
          <p>暂无自定义知识库，使用默认知识库</p>
        </div>
      </div>

      <!-- API Key 管理 -->
      <div class="card-static settings-card">
        <div class="card-title-row">
          <h3 class="card-title">API Key 管理</h3>
          <n-button size="small" type="primary" @click="showCreateKey = true">生成新 Key</n-button>
        </div>

        <div class="kb-list" v-if="apiKeys.length > 0">
          <div class="kb-item" v-for="k in apiKeys" :key="k.id">
            <div class="kb-item-info">
              <span class="kb-name">{{ k.name }}</span>
              <span class="kb-meta">{{ k.prefix }}... · 创建于 {{ k.created_at?.replace('T',' ').slice(0,16) }}{{ k.last_used_at ? ' · 最近使用 ' + k.last_used_at.replace('T',' ').slice(0,16) : '' }}</span>
            </div>
            <n-button size="tiny" type="error" quaternary @click="handleDeleteKey(k)">删除</n-button>
          </div>
        </div>
        <div class="empty-kb" v-else>
          <p>暂无 API Key，生成一个用于外部系统集成</p>
        </div>
      </div>

      <!-- Webhook 管理 -->
      <div class="card-static settings-card">
        <div class="card-title-row">
          <h3 class="card-title">Webhook 管理</h3>
          <n-button size="small" type="primary" @click="showCreateHook = true">添加 Webhook</n-button>
        </div>

        <div class="kb-list" v-if="webhooks.length > 0">
          <div class="kb-item" v-for="h in webhooks" :key="h.id">
            <div class="kb-item-info">
              <span class="kb-name">{{ h.url }}</span>
              <span class="kb-meta">事件: {{ h.events || '全部' }} · {{ h.created_at?.replace('T',' ').slice(0,16) }}</span>
            </div>
            <n-button size="tiny" type="error" quaternary @click="handleDeleteHook(h)">删除</n-button>
          </div>
        </div>
        <div class="empty-kb" v-else>
          <p>暂无 Webhook，添加一个接收系统事件通知</p>
        </div>
      </div>
    </div>

    <!-- 新建知识库弹窗 -->
    <n-modal v-model:show="showCreateKB" preset="dialog" title="新建知识库" positive-text="创建" negative-text="取消" @positive-click="handleCreateKB">
      <n-form :model="newKBForm">
        <n-form-item label="名称">
          <n-input v-model:value="newKBForm.name" placeholder="如：项目A资料库" />
        </n-form-item>
        <n-form-item label="描述（选填）">
          <n-input v-model:value="newKBForm.description" type="textarea" placeholder="简要描述知识库用途" :rows="2" />
        </n-form-item>
      </n-form>
    </n-modal>

    <!-- 生成 API Key 弹窗 -->
    <n-modal v-model:show="showCreateKey" preset="dialog" title="生成 API Key" positive-text="生成" negative-text="取消" @positive-click="handleCreateKey">
      <n-form :model="newKeyForm">
        <n-form-item label="Key 名称">
          <n-input v-model:value="newKeyForm.name" placeholder="如：测试环境、CI/CD" />
        </n-form-item>
      </n-form>
    </n-modal>

    <!-- 显示新生成的 Key -->
    <n-modal v-model:show="showKeyResult" preset="card" title="API Key 已生成" style="width:520px">
      <n-alert type="warning" style="margin-bottom:1rem">请立即复制保存，此 Key 只显示一次，关闭后无法再查看。</n-alert>
      <n-input :value="generatedKey" readonly type="textarea" :rows="2" style="font-family:monospace" />
      <template #footer>
        <n-button type="primary" @click="copyKey">复制 Key</n-button>
      </template>
    </n-modal>

    <!-- 添加 Webhook 弹窗 -->
    <n-modal v-model:show="showCreateHook" preset="dialog" title="添加 Webhook" positive-text="添加" negative-text="取消" @positive-click="handleCreateHook">
      <n-form :model="newHookForm">
        <n-form-item label="回调 URL">
          <n-input v-model:value="newHookForm.url" placeholder="https://your-server.com/webhook" />
        </n-form-item>
        <n-form-item label="订阅事件（逗号分隔，留空=全部）">
          <n-input v-model:value="newHookForm.events" placeholder="document.uploaded, table.filled" />
        </n-form-item>
      </n-form>
    </n-modal>

    <!-- 显示 Webhook Secret -->
    <n-modal v-model:show="showHookSecret" preset="card" title="Webhook 已创建" style="width:520px">
      <n-alert type="info" style="margin-bottom:1rem">请保存 Secret，用于验证 Webhook 签名（X-Webhook-Signature 头）。</n-alert>
      <n-input :value="hookSecret" readonly style="font-family:monospace" />
      <template #footer>
        <n-button type="primary" @click="navigator.clipboard.writeText(hookSecret); message.success('已复制')">复制 Secret</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import api from '../api/index.js'

const authStore = useAuthStore()
const message = useMessage()
const knowledgeBases = ref([])
const showCreateKB = ref(false)
const newKBForm = ref({ name: '', description: '' })
const pwdForm = ref({ password: '', confirm: '' })

const apiKeys = ref([])
const showCreateKey = ref(false)
const showKeyResult = ref(false)
const newKeyForm = ref({ name: '' })
const generatedKey = ref('')

const webhooks = ref([])
const showCreateHook = ref(false)
const showHookSecret = ref(false)
const newHookForm = ref({ url: '', events: '' })
const hookSecret = ref('')

const loadKBs = async () => {
  try {
    const res = await api.listKBs()
    knowledgeBases.value = res.knowledge_bases || []
  } catch { /* ignore */ }
}

const handleCreateKB = async () => {
  if (!newKBForm.value.name.trim()) {
    message.warning('请输入知识库名称')
    return false
  }
  try {
    await api.createKB({ name: newKBForm.value.name, description: newKBForm.value.description })
    message.success('知识库创建成功')
    newKBForm.value = { name: '', description: '' }
    await loadKBs()
  } catch (e) {
    message.error('创建失败: ' + (e.response?.data?.detail || e.message))
  }
}

const handleDeleteKB = async (kb) => {
  if (!confirm(`确定删除知识库「${kb.name}」？所有数据将被清除。`)) return
  try {
    await api.deleteKB(kb.id)
    message.success('已删除')
    await loadKBs()
  } catch (e) {
    message.error('删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

const loadApiKeys = async () => {
  try {
    apiKeys.value = await api.listApiKeys()
  } catch { /* ignore */ }
}

const handleCreateKey = async () => {
  if (!newKeyForm.value.name.trim()) {
    message.warning('请输入 Key 名称')
    return false
  }
  try {
    const res = await api.createApiKey({ name: newKeyForm.value.name })
    generatedKey.value = res.key
    showKeyResult.value = true
    newKeyForm.value = { name: '' }
    await loadApiKeys()
  } catch (e) {
    message.error('生成失败: ' + (e.response?.data?.detail || e.message))
  }
}

const handleDeleteKey = async (k) => {
  if (!confirm(`确定删除 API Key「${k.name}」？使用此 Key 的外部集成将立即失效。`)) return
  try {
    await api.deleteApiKey(k.id)
    message.success('已删除')
    await loadApiKeys()
  } catch (e) {
    message.error('删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

const copyKey = () => {
  navigator.clipboard.writeText(generatedKey.value).then(() => {
    message.success('已复制到剪贴板')
  }).catch(() => {
    message.info('请手动复制')
  })
}

const loadWebhooks = async () => {
  try {
    webhooks.value = await api.listWebhooks()
  } catch { /* ignore */ }
}

const handleCreateHook = async () => {
  if (!newHookForm.value.url.trim()) {
    message.warning('请输入 URL')
    return false
  }
  try {
    const res = await api.createWebhook(newHookForm.value)
    hookSecret.value = res.secret
    showHookSecret.value = true
    newHookForm.value = { url: '', events: '' }
    await loadWebhooks()
  } catch (e) {
    message.error('创建失败: ' + (e.response?.data?.detail || e.message))
  }
}

const handleDeleteHook = async (h) => {
  if (!confirm(`确定删除此 Webhook？`)) return
  try {
    await api.deleteWebhook(h.id)
    message.success('已删除')
    await loadWebhooks()
  } catch (e) {
    message.error('删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

onMounted(() => {
  loadKBs()
  loadApiKeys()
  loadWebhooks()
})
</script>

<style scoped>
.settings-view {
  max-width: 900px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 2rem;
}
.settings-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.settings-card {
  padding: 1.5rem;
}
.card-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-subtle);
}
.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-subtle);
}
.card-title-row .card-title {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}
.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.info-row:last-child {
  border-bottom: none;
}
.info-label {
  color: var(--text-muted);
  font-size: var(--font-size-md);
}
.info-value {
  color: var(--text-primary);
  font-weight: 500;
}
.pwd-form {
  max-width: 400px;
}
.kb-card {
  min-height: 200px;
}
.kb-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.kb-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}
.kb-item-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.kb-name {
  font-weight: 600;
  color: var(--text-primary);
}
.kb-meta {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}
.empty-kb {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}
</style>
