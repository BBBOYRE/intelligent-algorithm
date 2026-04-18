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

    <div class="docs-section" v-if="kbStats.documents && kbStats.documents.length > 0">
      <h3 class="section-title">已入库文档</h3>
      <div class="doc-tags">
        <span class="doc-tag" v-for="doc in kbStats.documents" :key="doc.file_name">
          {{ doc.file_name }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../api/index.js'

const authStore = useAuthStore()
const kbStats = ref({ total_chunks: 0, documents: [] })
const knowledgeBases = ref([])

onMounted(async () => {
  try {
    kbStats.value = await api.getKBStats()
  } catch { /* ignore */ }
  try {
    const res = await api.listKBs()
    knowledgeBases.value = res.knowledge_bases || []
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
