<template>
  <div class="table-fill-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">模板表格自动填写</h2>
      <p class="section-subtitle">上传空白的 docx 或 xlsx 模板表格，系统将基于知识库内容自动推断并填入数据。</p>
    </div>

    <div class="card-static content-layout">
      <div class="left-panel">
        <h3 class="panel-title">1. 选择模板文件</h3>
        
        <div 
          class="drop-zone" 
          :class="{ 'dragover': isDragging, 'has-file': templateFile }"
          @dragover.prevent="onDragOver"
          @dragleave="onDragLeave"
          @drop.prevent="onDrop"
          @click="triggerFileInput"
        >
          <div v-if="!templateFile">
            <div class="upload-icon">📝</div>
            <h4 class="upload-title">上传 Word/Excel 模板</h4>
            <p class="upload-hint">支持 .docx, .xlsx</p>
          </div>
          <div v-else class="selected-file">
            <span class="file-icon">📄</span>
            <div class="file-info">
              <span class="file-name">{{ templateFile.name }}</span>
              <span class="file-size">{{ formatSize(templateFile.size) }}</span>
            </div>
            <button class="change-btn" @click.stop="triggerFileInput">更换</button>
          </div>
          
          <input 
            type="file" 
            ref="fileInput" 
            accept=".docx,.xlsx" 
            style="display: none" 
            @change="onFileSelected" 
          />
        </div>

        <div class="action-box">
          <button 
            class="btn btn-primary btn-lg w-full" 
            @click="startFill" 
            :disabled="!templateFile || isProcessing"
          >
            <span class="icon" v-if="!isProcessing">✨</span>
            <span class="spinner" v-else></span>
            {{ isProcessing ? '正在处理数据，请稍候...' : '开始智能填写' }}
          </button>
        </div>
      </div>

      <div class="right-panel">
        <h3 class="panel-title">2. 执行结果</h3>
        
        <div class="result-box" v-if="!result">
          <div class="empty-state">
            <div class="empty-icon">⏳</div>
            <p v-if="!isProcessing">尚未开始处理</p>
            <p v-else class="pulsing">AI 代理正在努力填表中...</p>
          </div>
        </div>

        <div class="result-box result-success animate-slide-in" v-else-if="result.status === 'success'">
          <div class="success-icon">✅</div>
          <h3>填写完成</h3>
          <p class="result-detail">系统成功在表格中填入了 <strong class="highlight">{{ result.filled_cells }}</strong> 个数据单元格！</p>
          
          <div class="download-section">
            <a :href="downloadHref" class="btn btn-success" download>
              <span class="icon">📥</span> 下载填写好的文档
            </a>
          </div>
        </div>

        <div class="result-box result-error animate-slide-in" v-else>
          <div class="error-icon">❌</div>
          <h3>处理失败</h3>
          <p class="result-detail">{{ result.error || '发生了未知错误' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToast } from '../composables/useToast'
import api from '../api/index.js'

const fileInput = ref(null)
const templateFile = ref(null)
const isDragging = ref(false)
const isProcessing = ref(false)
const result = ref(null)
const toast = useToast()

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
  if (ext !== '.docx' && ext !== '.xlsx') {
    toast.error('仅支持 docx 或 xlsx 模板')
    return
  }
  templateFile.value = file
  result.value = null // reset result when new file is picked
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const downloadHref = computed(() => {
  if (result.value && result.value.output_path) {
    return api.getDownloadUrl(result.value.output_path)
  }
  return '#'
})

const startFill = async () => {
  if (!templateFile.value) return
  isProcessing.value = true
  result.value = null
  
  try {
    const formData = new FormData()
    formData.append('file', templateFile.value)
    
    // Server will return JSON { status, filled_cells, output_path }
    const res = await api.fillTemplate(formData)
    result.value = res
    toast.success('表格填写完成！')
  } catch (error) {
    toast.error('执行失败: ' + error.message)
    result.value = { status: 'error', error: error.message }
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.table-fill-view {
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
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
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
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  gap: 1rem;
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

.success-icon {
  font-size: 4rem;
  color: var(--accent-emerald);
}

.error-icon {
  font-size: 4rem;
  color: var(--accent-rose);
}

.result-box h3 {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
}

.result-detail {
  color: var(--text-secondary);
  font-size: var(--font-size-md);
  line-height: 1.6;
}

.highlight {
  font-size: var(--font-size-xl);
  color: var(--accent-blue);
  font-weight: 700;
}

.download-section {
  margin-top: 2rem;
}

.pulsing {
  animation: pulse-glow 2s infinite;
  color: var(--accent-blue);
}
</style>
