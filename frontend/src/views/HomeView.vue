<template>
  <div class="home-view animate-fade-in stagger-children">
    <div class="hero-section">
      <h1 class="hero-title">基于大语言模型的<br/>文档理解与多源数据融合系统</h1>
      <p class="hero-subtitle">智能解析多格式文档，构建专属知识库，支持自然语言检索与模板自动填写，提升企业办公效率。</p>

      <div class="hero-actions">
        <router-link to="/upload" class="btn btn-primary btn-lg">
          <span class="icon">🚀</span> 快速开始
        </router-link>
        <router-link to="/chat" class="btn btn-secondary btn-lg">
          <span class="icon">💬</span> 尝试问答
        </router-link>
      </div>
    </div>

    <div class="features-grid">
      <router-link to="/upload" class="card feature-card clickable">
        <div class="feature-icon icon-blue">📄</div>
        <h3>非结构化文档信息提取</h3>
        <p>支持 docx, xlsx, md, txt 等多种格式，自动识别并提取关键信息，结构化分块后存入本地向量知识库。</p>
        <span class="feature-link">上传文档 →</span>
      </router-link>

      <router-link to="/doc-ops" class="card feature-card clickable">
        <div class="feature-icon icon-purple">✏️</div>
        <h3>文档智能操作交互</h3>
        <p>通过自然语言指令对文档进行信息提取、内容编辑、格式转换、总结分析等智能操作，无需手动处理。</p>
        <span class="feature-link">开始操作 →</span>
      </router-link>

      <router-link to="/table-fill" class="card feature-card clickable">
        <div class="feature-icon icon-emerald">📊</div>
        <h3>表格自定义数据填写</h3>
        <p>上传空白模板表格，系统自动从知识库中检索匹配数据并精准填入，支持精细与粗略两种检索模式。</p>
        <span class="feature-link">填写表格 →</span>
      </router-link>
    </div>

    <div class="status-section">
      <div class="card-static status-panel">
        <div class="status-header">
          <h3>系统状态</h3>
          <span class="status-indicator"></span>
        </div>
        <div class="status-details">
          <div class="detail-item">
            <span class="detail-label">知识库引擎</span>
            <span class="badge badge-emerald">ChromaDB 在线</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">已入库分块</span>
            <span class="detail-value highlight">{{ store.kbStats.total_chunks }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'

const store = useAppStore()
</script>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.hero-section {
  text-align: center;
  margin-top: 2rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 1.5rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: var(--font-size-xl);
  color: var(--text-secondary);
  max-width: 800px;
  margin: 0 auto 2.5rem;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
}

.feature-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
  text-decoration: none;
  color: inherit;
}

.feature-card.clickable {
  cursor: pointer;
  transition: transform var(--transition-fast, 0.2s), border-color var(--transition-fast, 0.2s);
}
.feature-card.clickable:hover {
  transform: translateY(-2px);
  border-color: var(--accent-blue);
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.icon-blue {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent-blue);
}
.icon-purple {
  background: rgba(139, 92, 246, 0.15);
  color: var(--accent-purple);
}
.icon-emerald {
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-emerald);
}

.feature-card h3 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.feature-link {
  font-size: var(--font-size-sm);
  color: var(--accent-blue);
  font-weight: 500;
  margin-top: auto;
}

.status-section {
  display: flex;
  justify-content: center;
}

.status-panel {
  width: 100%;
  max-width: 600px;
}

.status-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-subtle);
}

.status-header h3 {
  font-size: var(--font-size-lg);
  font-weight: 600;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent-emerald);
  box-shadow: 0 0 12px var(--accent-emerald);
  animation: pulse-glow 2s infinite;
}

.status-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-label {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}

.detail-value {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
}

.detail-value.highlight {
  color: var(--accent-cyan);
}
</style>
