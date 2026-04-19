<template>
  <div class="dashboard-view animate-fade-in stagger-children">
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎回来，{{ authStore.user?.username || '用户' }}</h1>
      <p class="welcome-subtitle">基于大语言模型的文档理解与多源数据融合系统</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon icon-blue">📄</div>
        <div class="stat-info">
          <span class="stat-value">{{ kbStats.total_chunks || 0 }}</span>
          <span class="stat-label">知识库分块</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon icon-emerald">📁</div>
        <div class="stat-info">
          <span class="stat-value">{{ kbStats.documents?.length || 0 }}</span>
          <span class="stat-label">已入库文档</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon icon-purple">🧠</div>
        <div class="stat-info">
          <span class="stat-value">{{ knowledgeBases.length }}</span>
          <span class="stat-label">知识库数量</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon icon-amber">
          <span class="status-dot"></span>
        </div>
        <div class="stat-info">
          <span class="stat-value status-online">在线</span>
          <span class="stat-label">系统状态</span>
        </div>
      </div>
    </div>

    <div class="features-grid">
      <router-link to="/upload" class="card feature-card clickable">
        <div class="feature-icon icon-blue">📄</div>
        <h3>文档上传与解析</h3>
        <p>上传多格式文档，自动解析并入库到向量知识库</p>
        <span class="feature-link">去上传 →</span>
      </router-link>

      <router-link to="/doc-ops" class="card feature-card clickable">
        <div class="feature-icon icon-purple">✏️</div>
        <h3>文档智能操作</h3>
        <p>自然语言指令编辑文档格式和内容，支持 docx 回写</p>
        <span class="feature-link">去操作 →</span>
      </router-link>

      <router-link to="/chat" class="card feature-card clickable">
        <div class="feature-icon icon-cyan">💬</div>
        <h3>智能问答</h3>
        <p>基于知识库的 RAG 检索问答，精准回答您的问题</p>
        <span class="feature-link">去提问 →</span>
      </router-link>

      <router-link to="/table-fill" class="card feature-card clickable">
        <div class="feature-icon icon-emerald">📊</div>
        <h3>模板表格填写</h3>
        <p>上传模板，自动从知识库检索数据精准填入表格</p>
        <span class="feature-link">去填写 →</span>
      </router-link>
    </div>

    <div class="dashboard-widgets">
      <!-- Memos Section -->
      <div class="memos-section" v-if="sortedMemos.length > 0">
        <div class="section-header">
          <h3 class="section-title">我的备忘录</h3>
          <router-link to="/memos" class="view-all">查看全部 →</router-link>
        </div>
        <div class="memos-list">
          <div v-for="memo in sortedMemos.slice(0, 5)" :key="memo.id" class="dashboard-memo-card card-static">
            <div class="memo-title-row">
              <div class="memo-title">
                <span v-if="memo.is_starred" class="star-icon">⭐</span>
                {{ memo.title || '无标题' }}
              </div>
              <div class="memo-date" :class="{ 'overdue': isOverdue(memo.due_date), 'close': isClose(memo.due_date) }" v-if="memo.due_date">
                {{ formatRelativeDate(memo.due_date) }}
              </div>
            </div>
            <div class="memo-content-preview">{{ truncate(memo.content, 60) }}</div>
          </div>
        </div>
      </div>

      <!-- Docs Section -->
      <div class="docs-section" v-if="kbStats.documents && kbStats.documents.length > 0">
        <h3 class="section-title">已入库文档</h3>
        <div class="doc-tags">
          <span class="doc-tag" v-for="doc in kbStats.documents" :key="doc.file_name">
            {{ doc.file_name }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../api/index.js'

const authStore = useAuthStore()
const kbStats = ref({ total_chunks: 0, documents: [] })
const knowledgeBases = ref([])
const memos = ref([])

// 优先级：收藏+时间临近>收藏>时间临近>无关注+无时间临近
const sortedMemos = computed(() => {
  return [...memos.value].sort((a, b) => {
    const aClose = isClose(a.due_date) || isOverdue(a.due_date)
    const bClose = isClose(b.due_date) || isOverdue(b.due_date)

    const getPriority = (m, close) => {
      if (m.is_starred && close) return 1
      if (m.is_starred && !close) return 2
      if (!m.is_starred && close) return 3
      return 4
    }

    const pA = getPriority(a, aClose)
    const pB = getPriority(b, bClose)

    if (pA !== pB) {
      return pA - pB
    }

    // 同优先级下，有截至日期优先按截止日期升序，无截止日期按更新时间倒序
    if (a.due_date && b.due_date) {
      return new Date(a.due_date) - new Date(b.due_date)
    }
    if (a.due_date) return -1
    if (b.due_date) return 1
    return new Date(b.updated_at) - new Date(a.updated_at)
  })
})

const isOverdue = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const isClose = (dateStr) => {
  if (!dateStr) return false
  const diffTime = new Date(dateStr) - new Date()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays >= 0 && diffDays <= 3
}

const formatRelativeDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffTime = date - now
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return '已过期'
  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '明天'
  if (diffDays === 2) return '后天'
  return `${diffDays}天后`
}

const truncate = (text, len) => {
  if (!text) return ''
  return text.length > len ? text.substring(0, len) + '...' : text
}

onMounted(async () => {
  try {
    kbStats.value = await api.getKBStats()
  } catch { /* ignore */ }
  try {
    const res = await api.listKBs()
    knowledgeBases.value = res.knowledge_bases || []
  } catch { /* ignore */ }
  try {
    memos.value = await api.listMemos()
  } catch { /* ignore */ }
})
</script>

<style scoped>
.dashboard-view {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}
.welcome-section {
  margin-top: 1rem;
}
.welcome-title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}
.welcome-subtitle {
  color: var(--text-muted);
  font-size: var(--font-size-lg);
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  backdrop-filter: blur(12px);
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}
.icon-blue { background: rgba(51, 112, 255, 0.08); }
.icon-purple { background: rgba(124, 58, 237, 0.08); }
.icon-emerald { background: rgba(52, 199, 89, 0.08); }
.icon-amber { background: rgba(255, 149, 0, 0.08); }
.icon-cyan { background: rgba(51, 112, 255, 0.08); color: var(--accent-blue); }
.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.stat-value {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
}
.stat-label {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}
.status-online {
  color: var(--accent-emerald) !important;
}
.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--accent-emerald);
  box-shadow: 0 0 12px var(--accent-emerald);
  display: inline-block;
  animation: pulse-glow 2s infinite;
}
.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}
.feature-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  text-decoration: none;
  color: inherit;
  padding: 1.5rem;
}
.feature-card.clickable {
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s;
}
.feature-card.clickable:hover {
  transform: translateY(-2px);
  border-color: var(--accent-blue);
}
.feature-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
}
.feature-card h3 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}
.feature-card p {
  color: var(--text-secondary);
  font-size: var(--font-size-md);
  line-height: 1.5;
}
.feature-link {
  font-size: var(--font-size-sm);
  color: var(--accent-blue);
  font-weight: 500;
  margin-top: auto;
}
.section-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.dashboard-widgets {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .dashboard-widgets {
    grid-template-columns: 1fr;
  }
}

/* Memos specific styles */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header .section-title {
  margin-bottom: 0;
}

.view-all {
  font-size: var(--font-size-sm);
  color: var(--accent-blue);
  text-decoration: none;
  font-weight: 500;
}

.view-all:hover {
  text-decoration: underline;
}

.memos-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dashboard-memo-card {
  padding: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.memo-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.memo-title {
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.star-icon {
  font-size: 0.9rem;
}

.memo-date {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.memo-date.overdue {
  color: var(--accent-red);
  font-weight: 600;
}

.memo-date.close {
  color: var(--accent-amber);
  font-weight: 600;
}

.memo-content-preview {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.doc-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.doc-tag {
  padding: 0.3rem 0.75rem;
  font-size: var(--font-size-sm);
  background: rgba(51, 112, 255, 0.06);
  border: 1px solid rgba(51, 112, 255, 0.15);
  color: var(--accent-blue);
  border-radius: var(--radius-sm);
}
</style>
