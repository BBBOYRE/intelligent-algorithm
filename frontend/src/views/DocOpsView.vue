<template>
  <div class="doc-ops-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">文档智能操作</h2>
      <p class="section-subtitle">自然语言指令操作文档，或对比两个文档的差异。</p>
      <div class="tab-bar">
        <button class="tab-btn" :class="{ active: activeTab === 'ops' }" @click="activeTab = 'ops'">文档操作</button>
        <button class="tab-btn" :class="{ active: activeTab === 'compare' }" @click="activeTab = 'compare'">文档对比</button>
      </div>
    </div>
    <div class="card-static content-layout" v-if="activeTab === 'ops'">
      <div class="left-panel">
        <h3 class="panel-title">1. 选择文档</h3>
        <div
          class="drop-zone"
          :class="{ 'dragover': isDragging, 'has-file': docFile }"
          @dragover.prevent="onDragOver"
          @dragleave="onDragLeave"
          @drop.prevent="onDrop"
          @click="triggerFileInput"
        >
          <div v-if="!docFile">
            <div class="upload-icon">📂</div>
            <h4 class="upload-title">上传文档文件</h4>
            <p class="upload-hint">支持 .docx, .xlsx, .md, .txt</p>
          </div>
          <div v-else class="selected-file">
            <span class="file-icon">📄</span>
            <div class="file-info">
              <span class="file-name">{{ docFile.name }}</span>
              <span class="file-size">{{ formatSize(docFile.size) }}</span>
            </div>
            <button class="change-btn" @click.stop="triggerFileInput">更换</button>
          </div>
          <input
            type="file"
            ref="fileInput"
            accept=".docx,.xlsx,.md,.txt"
            style="display: none"
            @change="onFileSelected"
          />
        </div>

        <div class="instruction-section">
          <h3 class="panel-title">2. 操作指令</h3>
          <div class="quick-actions">
            <button
              v-for="action in quickActions"
              :key="action"
              class="quick-btn"
              :disabled="isProcessing"
              @click="instruction = action"
            >{{ action }}</button>
          </div>
          <textarea
            v-model="instruction"
            class="instruction-input"
            placeholder="请输入操作指令，如：提取文档中所有人名和联系方式..."
            rows="4"
            :disabled="isProcessing"
          ></textarea>
        </div>

        <div class="action-box">
          <button
            class="btn btn-primary btn-lg w-full"
            @click="startExecute"
            :disabled="!docFile || !instruction.trim() || isProcessing"
          >
            <span class="icon" v-if="!isProcessing">✨</span>
            <span class="spinner" v-else></span>
            {{ isProcessing ? '正在处理中，请稍候...' : '执行操作' }}
          </button>
        </div>
      </div>

      <div class="right-panel">
        <h3 class="panel-title">执行结果</h3>
        <div class="result-box" v-if="!result">
          <div class="empty-state">
            <div class="empty-icon">⏳</div>
            <p v-if="!isProcessing">尚未开始处理</p>
            <p v-else class="pulsing">AI 正在分析文档并执行操作...</p>
          </div>
        </div>
        <div class="result-box result-success animate-slide-in" v-else-if="result.status === 'success'">
          <div class="result-header">
            <span class="success-badge">操作完成</span>
            <div class="result-actions">
              <button class="copy-btn" @click="copyResult">复制结果</button>
              <button v-if="result.output_path" class="download-btn" @click="downloadFile">下载修改后文档</button>
            </div>
          </div>
          <div class="result-meta">
            <span>源文件: {{ result.original_file }}</span>
            <span>指令: {{ result.instruction }}</span>
            <span v-if="result.ops_applied">已执行 {{ result.ops_applied }} 项操作</span>
          </div>
          <div class="result-content">
            <pre>{{ result.result }}</pre>
          </div>
        </div>
        <div class="result-box result-error animate-slide-in" v-else>
          <div class="error-icon">❌</div>
          <h3>处理失败</h3>
          <p class="result-detail">{{ result.error || '发生了未知错误' }}</p>
        </div>
      </div>
    </div>

    <!-- 文档对比 -->
    <div class="card-static compare-layout" v-if="activeTab === 'compare'">
      <div class="compare-uploads">
        <div class="compare-file-box">
          <h4>文档 A</h4>
          <div class="drop-zone mini-drop" @click="$refs.compareInputA.click()">
            <span v-if="!compareFileA">点击选择文件</span>
            <span v-else class="file-name">{{ compareFileA.name }}</span>
          </div>
          <input type="file" ref="compareInputA" accept=".docx,.xlsx,.md,.txt,.pdf" style="display:none" @change="compareFileA = $event.target.files[0]" />
        </div>
        <div class="compare-file-box">
          <h4>文档 B</h4>
          <div class="drop-zone mini-drop" @click="$refs.compareInputB.click()">
            <span v-if="!compareFileB">点击选择文件</span>
            <span v-else class="file-name">{{ compareFileB.name }}</span>
          </div>
          <input type="file" ref="compareInputB" accept=".docx,.xlsx,.md,.txt,.pdf" style="display:none" @change="compareFileB = $event.target.files[0]" />
        </div>
      </div>
      <div class="action-box" style="margin-top:1rem">
        <button class="btn btn-primary btn-lg w-full" @click="startCompare" :disabled="!compareFileA || !compareFileB || isComparing">
          <span class="spinner" v-if="isComparing"></span>
          {{ isComparing ? 'AI 正在对比分析...' : '开始对比' }}
        </button>
      </div>
      <div class="compare-result" v-if="compareReport">
        <div class="result-header" style="margin-bottom:0.75rem">
          <span class="success-badge">对比完成</span>
          <button class="copy-btn" @click="navigator.clipboard.writeText(compareReport); toast.success('已复制')">复制报告</button>
        </div>
        <div class="result-content compare-report-content" v-html="renderMarkdown(compareReport)"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToast } from '../composables/useToast'
import api from '../api/index.js'

const fileInput = ref(null)
const docFile = ref(null)
const isDragging = ref(false)
const isProcessing = ref(false)
const result = ref(null)
const instruction = ref('')
const toast = useToast()
const activeTab = ref('ops')

const compareFileA = ref(null)
const compareFileB = ref(null)
const isComparing = ref(false)
const compareReport = ref('')

const downloadHref = computed(() => {
  if (result.value && result.value.output_path) {
    return api.getDownloadUrl(result.value.output_path)
  }
  return '#'
})

const downloadFile = () => {
  if (!result.value?.output_path) return
  const url = api.getDownloadUrl(result.value.output_path)
  const token = localStorage.getItem('token')
  const xhr = new XMLHttpRequest()
  xhr.open('GET', url, true)
  xhr.responseType = 'blob'
  if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)
  xhr.onload = () => {
    if (xhr.status === 200) {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(xhr.response)
      a.download = result.value.output_path.split(/[/\\]/).pop() || 'download'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(a.href)
    } else {
      toast.error('下载失败')
    }
  }
  xhr.onerror = () => toast.error('下载失败')
  xhr.send()
}

const quickActions = [
  '提取所有人名',
  '提取关键数据和数字',
  '总结文档要点',
  '提取日期信息',
  '把标题加粗居中',
  '将所有日期统一为YYYY-MM-DD格式',
]

const triggerFileInput = () => {
  if (!isProcessing.value) fileInput.value.click()
}

const onDragOver = () => {
  if (!isProcessing.value) isDragging.value = true
}

const onDragLeave = () => {
  isDragging.value = false
}

const onDrop = (event) => {
  isDragging.value = false
  if (isProcessing.value) return
  const file = event.dataTransfer.files[0]
  handleSelection(file)
}

const onFileSelected = (event) => {
  const file = event.target.files[0]
  handleSelection(file)
  fileInput.value.value = ''
}

const handleSelection = (file) => {
  if (!file) return
  const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
  if (!['.docx', '.xlsx', '.md', '.txt'].includes(ext)) {
    toast.error('仅支持 docx, xlsx, md, txt 格式')
    return
  }
  docFile.value = file
  result.value = null
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const copyResult = () => {
  if (result.value && result.value.result) {
    navigator.clipboard.writeText(result.value.result)
    toast.success('已复制到剪贴板')
  }
}

const startExecute = async () => {
  if (!docFile.value || !instruction.value.trim()) return
  isProcessing.value = true
  result.value = null
  try {
    const formData = new FormData()
    formData.append('file', docFile.value)
    formData.append('instruction', instruction.value)
    const res = await api.executeDocOp(formData)
    result.value = res
    toast.success('操作执行完成！')
  } catch (error) {
    toast.error('执行失败: ' + error.message)
    result.value = { status: 'error', error: error.message }
  } finally {
    isProcessing.value = false
  }
}

const startCompare = async () => {
  if (!compareFileA.value || !compareFileB.value) return
  isComparing.value = true
  compareReport.value = ''
  try {
    const formData = new FormData()
    formData.append('file_a', compareFileA.value)
    formData.append('file_b', compareFileB.value)
    const res = await api.compareDocuments(formData)
    compareReport.value = res.report || '未生成对比报告'
    toast.success('对比完成')
  } catch (error) {
    toast.error('对比失败: ' + error.message)
  } finally {
    isComparing.value = false
  }
}

const renderMarkdown = (text) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.doc-ops-view {
  max-width: 1000px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 2rem;
}
.content-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  min-height: 480px;
}
.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.panel-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 0.75rem;
}
.w-full {
  width: 100%;
}
.drop-zone {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 140px;
}
.drop-zone.has-file {
  border-style: solid;
  background: var(--bg-input);
}
.selected-file {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
}
.file-icon {
  font-size: 2.5rem;
}
.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: left;
}
.file-name {
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-all;
}
.file-size {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}
.change-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.change-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}
.instruction-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.quick-btn {
  padding: 0.35rem 0.75rem;
  font-size: var(--font-size-sm, 13px);
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: var(--accent-blue);
  border-radius: var(--radius-sm, 4px);
  cursor: pointer;
  transition: all var(--transition-fast, 0.2s);
}
.quick-btn:hover {
  background: rgba(59, 130, 246, 0.2);
}
.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.instruction-input {
  width: 100%;
  resize: vertical;
  padding: 0.75rem 1rem;
  font-size: var(--font-size-md, 14px);
  color: var(--text-primary);
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md, 6px);
  outline: none;
  transition: border-color var(--transition-fast, 0.2s);
  font-family: inherit;
  box-sizing: border-box;
}
.instruction-input:focus {
  border-color: var(--accent-blue);
}
.instruction-input::placeholder {
  color: var(--text-muted);
}
.action-box {
  margin-top: auto;
}
.result-box {
  flex: 1;
  background: var(--bg-input);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  gap: 1rem;
  overflow: hidden;
}
.result-box:not(.result-success):not(.result-error) {
  align-items: center;
  justify-content: center;
  text-align: center;
}
.empty-state {
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}
.empty-icon {
  font-size: 3rem;
  opacity: 0.5;
}
.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.success-badge {
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-emerald);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm, 4px);
  font-size: var(--font-size-sm, 13px);
  font-weight: 600;
}
.result-actions {
  display: flex;
  gap: 0.5rem;
}
.copy-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-sm, 4px);
  font-size: var(--font-size-sm, 13px);
  cursor: pointer;
  transition: all var(--transition-fast, 0.2s);
}
.copy-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
}
.download-btn {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: var(--accent-emerald);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-sm, 4px);
  font-size: var(--font-size-sm, 13px);
  cursor: pointer;
  text-decoration: none;
  transition: all var(--transition-fast, 0.2s);
}
.download-btn:hover {
  background: rgba(16, 185, 129, 0.25);
}
.result-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: var(--font-size-sm, 13px);
  color: var(--text-muted);
}
.result-content {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
}
.result-content pre {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: var(--font-size-md, 14px);
  color: var(--text-primary);
  line-height: 1.7;
  margin: 0;
  font-family: inherit;
}
.error-icon {
  font-size: 4rem;
  color: var(--accent-rose);
  text-align: center;
}
.result-box.result-error {
  align-items: center;
  justify-content: center;
  text-align: center;
}
.result-box.result-error h3 {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
}
.result-detail {
  color: var(--text-secondary);
  font-size: var(--font-size-md);
  line-height: 1.6;
}
.pulsing {
  animation: pulse-glow 2s infinite;
  color: var(--accent-blue);
}
.tab-bar {
  display: flex;
  gap: 0;
  margin-top: 1rem;
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  overflow: hidden;
  width: fit-content;
}
.tab-btn {
  padding: 0.6rem 1.5rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: var(--font-size-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.tab-btn:not(:last-child) {
  border-right: 1px solid var(--border-subtle);
}
.tab-btn.active {
  background: var(--accent-blue);
  color: #fff;
  font-weight: 600;
}
.compare-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
}
.compare-uploads {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.compare-file-box h4 {
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  font-weight: 600;
}
.mini-drop {
  min-height: 80px;
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}
.compare-report-content {
  max-height: 500px;
  overflow-y: auto;
  line-height: 1.8;
}
</style>
