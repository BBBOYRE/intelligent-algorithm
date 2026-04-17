<template>
  <div class="kb-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">知识库管理</h2>
      <p class="section-subtitle">查看已入库文档，搜索、筛选或删除单个文档</p>
    </div>

    <div class="card-static toolbar">
      <div class="search-row">
        <n-input v-model:value="searchQuery" placeholder="搜索文档名称..." clearable @update:value="loadDocuments">
          <template #prefix>🔍</template>
        </n-input>
        <n-select v-model:value="filterFormat" :options="formatOptions" placeholder="格式筛选" clearable style="width: 160px" @update:value="loadDocuments" />
        <n-button @click="loadDocuments">刷新</n-button>
      </div>
      <div class="stats-row">
        <span class="stat-text">共 <strong>{{ documents.length }}</strong> 个文档</span>
      </div>
    </div>

    <div class="card-static doc-table" v-if="documents.length > 0">
      <n-data-table :columns="columns" :data="documents" :bordered="false" size="small" />
    </div>

    <div class="card-static empty-state" v-else>
      <div class="empty-icon">📭</div>
      <p>知识库中暂无文档</p>
      <router-link to="/upload" class="btn btn-primary">去上传文档</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, h, onMounted } from 'vue'
import { NButton, NTag, useMessage } from 'naive-ui'
import api from '../api/index.js'

const message = useMessage()
const documents = ref([])
const searchQuery = ref('')
const filterFormat = ref(null)

const formatOptions = [
  { label: 'Word (.docx)', value: '.docx' },
  { label: 'Excel (.xlsx)', value: '.xlsx' },
  { label: 'Markdown (.md)', value: '.md' },
  { label: 'Text (.txt)', value: '.txt' },
  { label: 'CSV (.csv)', value: '.csv' },
  { label: 'HTML (.html)', value: '.html' },
  { label: 'PDF (.pdf)', value: '.pdf' },
]

const columns = [
  {
    title: '文档名称',
    key: 'file_name',
    ellipsis: { tooltip: true },
  },
  {
    title: '格式',
    key: 'format',
    width: 100,
    render(row) {
      const typeMap = { '.docx': 'info', '.xlsx': 'success', '.md': 'warning', '.txt': 'default', '.csv': 'info', '.html': 'warning', '.pdf': 'error' }
      return h(NTag, { size: 'small', type: typeMap[row.format] || 'default' }, () => row.format)
    },
  },
  {
    title: '分块数',
    key: 'chunk_count',
    width: 80,
    align: 'center',
  },
  {
    title: '内容预览',
    key: 'preview',
    ellipsis: { tooltip: true },
  },
  {
    title: '操作',
    key: 'actions',
    width: 80,
    align: 'center',
    render(row) {
      return h(NButton, {
        size: 'tiny',
        type: 'error',
        quaternary: true,
        onClick: () => handleDelete(row.file_name),
      }, () => '删除')
    },
  },
]

const loadDocuments = async () => {
  try {
    const res = await api.listKBDocuments('default', searchQuery.value, filterFormat.value || '')
    documents.value = res.documents || []
  } catch { /* ignore */ }
}

const handleDelete = async (fileName) => {
  if (!confirm(`确定删除文档「${fileName}」？`)) return
  try {
    await api.deleteKBDocument(fileName)
    message.success('已删除')
    await loadDocuments()
  } catch (e) {
    message.error('删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

onMounted(loadDocuments)
</script>

<style scoped>
.kb-view {
  max-width: 1100px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 2rem;
}
.toolbar {
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}
.search-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}
.stats-row {
  margin-top: 0.75rem;
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}
.stats-row strong {
  color: var(--accent-cyan);
}
.doc-table {
  padding: 0.5rem;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  text-align: center;
  color: var(--text-muted);
}
.empty-icon {
  font-size: 3rem;
  opacity: 0.5;
}
</style>
