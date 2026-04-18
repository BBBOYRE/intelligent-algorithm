<template>
  <div class="analytics-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">数据分析</h2>
      <p class="section-subtitle">查看使用统计和操作日志</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon icon-blue">📄</div>
        <div class="stat-info">
          <span class="stat-value">{{ overview.total_uploads }}</span>
          <span class="stat-label">文档上传</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon icon-purple">💬</div>
        <div class="stat-info">
          <span class="stat-value">{{ overview.total_chats }}</span>
          <span class="stat-label">智能问答</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon icon-emerald">📊</div>
        <div class="stat-info">
          <span class="stat-value">{{ overview.total_fills }}</span>
          <span class="stat-label">表格填写</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon icon-cyan">✏️</div>
        <div class="stat-info">
          <span class="stat-value">{{ overview.total_doc_ops }}</span>
          <span class="stat-label">文档操作</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon icon-amber">⏱️</div>
        <div class="stat-info">
          <span class="stat-value">{{ overview.avg_fill_time_ms ? (overview.avg_fill_time_ms / 1000).toFixed(1) + 's' : '-' }}</span>
          <span class="stat-label">平均填表耗时</span>
        </div>
      </div>
    </div>

    <!-- 操作日志 -->
    <div class="card-static logs-section">
      <div class="logs-header">
        <h3>操作日志</h3>
        <n-select v-model:value="logFilter" :options="actionOptions" placeholder="筛选操作类型" clearable style="width: 180px" @update:value="loadLogs" />
      </div>
      <n-data-table :columns="logColumns" :data="logs" :bordered="false" size="small" />
      <div class="pagination" v-if="logTotal > logPageSize">
        <n-pagination v-model:page="logPage" :page-count="Math.ceil(logTotal / logPageSize)" @update:page="loadLogs" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { NTag } from 'naive-ui'
import api from '../api/index.js'

const overview = ref({
  total_uploads: 0, total_chats: 0, total_fills: 0, total_doc_ops: 0, avg_fill_time_ms: 0,
})
const logs = ref([])
const logPage = ref(1)
const logPageSize = 15
const logTotal = ref(0)
const logFilter = ref(null)

const actionOptions = [
  { label: '文档上传', value: 'upload' },
  { label: '智能问答', value: 'chat' },
  { label: '表格填写', value: 'table_fill' },
  { label: '文档操作', value: 'doc_ops' },
  { label: '登录', value: 'login' },
  { label: '注册', value: 'register' },
]

const actionLabelMap = {
  upload: '文档上传', upload_async: '批量上传', chat: '智能问答',
  table_fill: '表格填写', table_preview: '表格预览', doc_ops: '文档操作',
  kb_clear: '清空知识库', kb_create: '创建知识库', kb_delete: '删除知识库',
  doc_delete: '删除文档', login: '登录', register: '注册',
}

const actionTypeMap = {
  upload: 'info', chat: 'default', table_fill: 'success',
  doc_ops: 'warning', login: 'info', register: 'info',
}

const logColumns = [
  {
    title: '操作',
    key: 'action',
    width: 120,
    render(row) {
      return h(NTag, { size: 'small', type: actionTypeMap[row.action] || 'default' },
        () => actionLabelMap[row.action] || row.action)
    },
  },
  { title: '详情', key: 'detail', ellipsis: { tooltip: true } },
  { title: '耗时', key: 'duration_ms', width: 80, render(row) { return row.duration_ms + 'ms' } },
  { title: '状态', key: 'status_code', width: 60 },
  { title: '时间', key: 'created_at', width: 170, render(row) { return row.created_at?.replace('T', ' ').slice(0, 19) || '' } },
]

const loadOverview = async () => {
  try { overview.value = await api.getAnalyticsOverview() } catch { /* ignore */ }
}

const loadLogs = async () => {
  try {
    const res = await api.getAuditLogs(logPage.value, logPageSize, logFilter.value || '')
    logs.value = res.logs || []
    logTotal.value = res.total || 0
  } catch { /* ignore */ }
}

onMounted(() => {
  loadOverview()
  loadLogs()
})
</script>

<style scoped>
.analytics-view {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.page-header { margin-bottom: 0.5rem; }
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  backdrop-filter: blur(12px);
}
.stat-icon {
  width: 44px; height: 44px;
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem;
}
.icon-blue { background: rgba(51, 112, 255, 0.08); }
.icon-purple { background: rgba(124, 58, 237, 0.08); }
.icon-emerald { background: rgba(52, 199, 89, 0.08); }
.icon-cyan { background: rgba(51, 112, 255, 0.08); }
.icon-amber { background: rgba(255, 149, 0, 0.08); }
.stat-info { display: flex; flex-direction: column; gap: 0.2rem; }
.stat-value { font-size: var(--font-size-xl); font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: var(--font-size-sm); color: var(--text-muted); }
.logs-section { padding: 1.5rem; }
.logs-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1rem; padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-subtle);
}
.logs-header h3 { font-size: var(--font-size-lg); font-weight: 600; color: var(--text-primary); }
.pagination { margin-top: 1rem; display: flex; justify-content: center; }
</style>
