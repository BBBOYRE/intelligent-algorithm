<template>
  <div class="kg-view animate-fade-in">
    <div class="page-header">
      <h2 class="section-title">知识图谱</h2>
      <p class="section-subtitle">从知识库文档中提取实体和关系，可视化展示知识网络。</p>
    </div>

    <div class="card-static kg-card">
      <div class="kg-toolbar">
        <n-button type="primary" :loading="loading" @click="generateGraph">
          {{ loading ? '正在生成图谱...' : '生成知识图谱' }}
        </n-button>
        <span class="kg-stats" v-if="graphData">
          {{ graphData.nodes.length }} 个实体 · {{ graphData.edges.length }} 条关系
        </span>
      </div>

      <div class="kg-container" ref="graphContainer">
        <div v-if="!graphData && !loading" class="kg-empty">
          <div class="empty-icon">🕸️</div>
          <p>点击上方按钮，AI 将从知识库中提取实体关系并生成图谱</p>
        </div>
      </div>

      <div class="kg-detail" v-if="selectedNode">
        <h4>{{ selectedNode.label }}</h4>
        <n-tag size="small" :type="typeColor[selectedNode.type] || 'default'">{{ typeLabel[selectedNode.type] || selectedNode.type }}</n-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '../api/index.js'

const message = useMessage()
const graphContainer = ref(null)
const loading = ref(false)
const graphData = ref(null)
const selectedNode = ref(null)
let network = null

const typeColor = { person: 'info', org: 'warning', location: 'success', date: 'default', event: 'error', concept: 'info' }
const typeLabel = { person: '人物', org: '组织', location: '地点', date: '日期', event: '事件', concept: '概念' }
const typeNodeColor = { person: '#3b82f6', org: '#f59e0b', location: '#10b981', date: '#94a3b8', event: '#f43f5e', concept: '#8b5cf6' }

const generateGraph = async () => {
  loading.value = true
  selectedNode.value = null
  try {
    const data = await api.getKnowledgeGraph()
    if (!data.nodes?.length) {
      message.warning(data.message || '未提取到实体')
      return
    }
    graphData.value = data
    renderGraph(data)
  } catch (e) {
    message.error(e?.response?.data?.detail || '生成失败')
  } finally {
    loading.value = false
  }
}

const renderGraph = (data) => {
  if (network) { network.destroy(); network = null }
  const { DataSet } = require('vis-data')
  const { Network } = require('vis-network')

  const nodes = new DataSet(data.nodes.map(n => ({
    id: n.id,
    label: n.label,
    color: { background: typeNodeColor[n.type] || '#64748b', border: 'transparent', highlight: { background: '#fff', border: typeNodeColor[n.type] || '#64748b' } },
    font: { color: '#f1f5f9', size: 14 },
    shape: 'dot',
    size: 20,
    _raw: n,
  })))

  const edges = new DataSet(data.edges.map((e, i) => ({
    id: `e${i}`,
    from: e.from,
    to: e.to,
    label: e.label,
    font: { color: '#94a3b8', size: 11, strokeWidth: 0 },
    color: { color: 'rgba(148,163,184,0.4)', highlight: '#3b82f6' },
    arrows: 'to',
    smooth: { type: 'curvedCW', roundness: 0.2 },
  })))

  const options = {
    physics: { solver: 'forceAtlas2Based', forceAtlas2Based: { gravitationalConstant: -50, springLength: 150 } },
    interaction: { hover: true, tooltipDelay: 200 },
    layout: { improvedLayout: true },
  }

  network = new Network(graphContainer.value, { nodes, edges }, options)
  network.on('click', (params) => {
    if (params.nodes.length) {
      const nodeData = nodes.get(params.nodes[0])
      selectedNode.value = nodeData._raw
    } else {
      selectedNode.value = null
    }
  })
}

onUnmounted(() => { if (network) network.destroy() })
</script>

<style scoped>
.kg-view { max-width: 1100px; margin: 0 auto; }
.kg-card { padding: 1.5rem; }
.kg-toolbar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
.kg-stats { color: var(--text-muted); font-size: var(--font-size-sm); }
.kg-container { width: 100%; height: 500px; border: 1px solid var(--border-subtle); border-radius: var(--radius-md); background: var(--bg-primary); position: relative; }
.kg-empty { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--text-muted); }
.kg-empty .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.kg-detail { margin-top: 1rem; padding: 1rem; background: var(--bg-input); border-radius: var(--radius-md); display: flex; align-items: center; gap: 1rem; }
.kg-detail h4 { color: var(--text-primary); font-weight: 600; }
</style>
