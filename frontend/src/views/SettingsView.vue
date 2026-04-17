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

onMounted(loadKBs)
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
