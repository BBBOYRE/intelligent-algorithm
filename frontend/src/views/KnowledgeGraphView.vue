<template>
  <div class="kg-view animate-fade-in">
    <div class="page-header">
      <h2 class="section-title">知识图谱</h2>
      <p class="section-subtitle">从知识库文档中提取实体和关系，可视化展示知识网络。</p>
    </div>

    <div class="card-static kg-card">
      <div class="kg-toolbar">
        <n-select
          v-model:value="selectedFiles"
          :options="fileOptions"
          multiple
          placeholder="选择文档（留空=全部）"
          style="min-width:300px;flex:1"
          clearable
        />
        <n-button type="primary" :loading="loading" :disabled="loading" @click="startGenerate">
          {{ loading ? '后台生成中...' : '生成知识图谱' }}
        </n-button>
        <span class="kg-stats" v-if="graphData">
          {{ graphData.nodes.length }} 个实体 · {{ graphData.edges.length }} 条关系
        </span>
        <n-button v-if="graphData" size="small" @click="downloadGraph">导出图谱数据</n-button>
      </div>

      <div class="kg-container" ref="graphContainer">
        <div v-if="!graphData && !loading" class="kg-empty">
          <div class="empty-icon">🕸️</div>
          <p>选择文档后点击生成，AI 将在后台提取实体关系</p>
        </div>
        <div v-if="loading" class="kg-empty">
          <div class="spinner spinner-lg"></div>
          <p style="margin-top:1rem">AI 正在后台提取实体关系，请稍候...</p>
        </div>
      </div>

      <div class="kg-detail" v-if="selectedNode">
        <h4>{{ selectedNode.label }}</h4>
        <n-tag size="small" :type="typeColor[selectedNode.type] || 'default'">
          {{ typeLabel[selectedNode.type] || selectedNode.type }}
        </n-tag>
      </div>
      <div class="kg-error" v-if="errorMsg">{{ errorMsg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '../api/index.js'

const message = useMessage()
const graphContainer = ref(null)
const loading = ref(false)
const graphData = ref(null)
const selectedNode = ref(null)
const selectedFiles = ref([])
const fileOptions = ref([])
const errorMsg = ref('')
let network = null
let pollTimer = null

const typeColor = { person: 'info', org: 'warning', location: 'success', date: 'default', event: 'error', concept: 'info' }
const typeLabel = { person: '人物', org: '组织', location: '地点', date: '日期', event: '事件', concept: '概念' }
const typeNodeColor = { person: '#3b82f6', org: '#f59e0b', location: '#10b981', date: '#94a3b8', event: '#f43f5e', concept: '#8b5cf6' }

const loadFiles = async () => {
  try {
    const files = await api.getKGFiles()
    fileOptions.value = files.map(f => ({ label: f.name, value: f.name }))
  } catch {}
}

const startGenerate = async () => {
  loading.value = true
  errorMsg.value = ''
  graphData.value = null
  selectedNode.value = null
  try {
    const names = selectedFiles.value.length > 0 ? selectedFiles.value : null
    const { task_id } = await api.generateKG(names)
    pollForResult(task_id)
  } catch (e) {
    loading.value = false
    errorMsg.value = e?.response?.data?.detail || '启动失败'
  }
}

const pollForResult = (taskId) => {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const res = await api.getKGResult(taskId)
      if (res.status === 'done') {
        clearInterval(pollTimer); pollTimer = null; loading.value = false
        if (res.nodes?.length) {
          graphData.value = res
          setTimeout(() => renderGraph(res), 100)
          message.success(`提取到 ${res.nodes.length} 个实体`)
        } else {
          errorMsg.value = '未能从文档中提取到实体关系'
        }
      } else if (res.status === 'error') {
        clearInterval(pollTimer); pollTimer = null; loading.value = false
        errorMsg.value = res.detail || '生成失败'
      }
    } catch {
      clearInterval(pollTimer); pollTimer = null; loading.value = false
      errorMsg.value = '查询结果失败'
    }
  }, 2000)
}

const renderGraph = async (data) => {
  if (network) { network.destroy(); network = null }
  const { DataSet } = await import('vis-data')
  const { Network } = await import('vis-network')

  const nodes = new DataSet(data.nodes.map(n => ({
    id: n.id, label: n.label,
    color: { background: typeNodeColor[n.type] || '#64748b', border: 'transparent', highlight: { background: '#fff', border: typeNodeColor[n.type] || '#64748b' } },
    font: { color: '#f1f5f9', size: 14 }, shape: 'dot', size: 20, _raw: n,
  })))

  const edges = new DataSet(data.edges.map((e, i) => ({
    id: `e${i}`, from: e.from, to: e.to, label: e.label,
    font: { color: '#94a3b8', size: 11, strokeWidth: 0 },
    color: { color: 'rgba(148,163,184,0.4)', highlight: '#3b82f6' },
    arrows: 'to', smooth: { type: 'curvedCW', roundness: 0.2 },
  })))

  const options = {
    physics: { solver: 'forceAtlas2Based', forceAtlas2Based: { gravitationalConstant: -50, springLength: 150 } },
    interaction: { hover: true, tooltipDelay: 200 },
    layout: { improvedLayout: true },
  }

  network = new Network(graphContainer.value, { nodes, edges }, options)
  network.on('click', (params) => {
    if (params.nodes.length) {
      selectedNode.value = nodes.get(params.nodes[0])._raw
    } else {
      selectedNode.value = null
    }
  })
}

onMounted(loadFiles)
onUnmounted(() => {
  if (network) network.destroy()
  if (pollTimer) clearInterval(pollTimer)
})

const downloadGraph = () => {
  if (!graphData.value) return
  const json = JSON.stringify({ nodes: graphData.value.nodes, edges: graphData.value.edges }, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'knowledge_graph.json'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(a.href)
}
</script>

<style scoped>
.kg-view { max-width: 1100px; margin: 0 auto; }
.kg-card { padding: 1.5rem; }
.kg-toolbar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.kg-stats { color: var(--text-muted); font-size: var(--font-size-sm); }
.kg-container { width: 100%; height: 500px; border: 1px solid var(--border-subtle); border-radius: var(--radius-md); background: var(--bg-primary); position: relative; }
.kg-empty { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--text-muted); }
.kg-empty .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.kg-detail { margin-top: 1rem; padding: 1rem; background: var(--bg-input); border-radius: var(--radius-md); display: flex; align-items: center; gap: 1rem; }
.kg-detail h4 { color: var(--text-primary); font-weight: 600; }
.kg-error { margin-top: 0.75rem; padding: 0.75rem 1rem; background: rgba(244,63,94,0.1); border: 1px solid rgba(244,63,94,0.3); border-radius: var(--radius-md); color: var(--accent-rose); font-size: var(--font-size-sm); }
</style>
