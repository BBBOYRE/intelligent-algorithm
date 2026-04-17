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

        <div class="precision-section">
          <h3 class="panel-title">2. 填写精度</h3>
          <div class="toggle-group">
            <button
              class="toggle-btn"
              :class="{ active: fillPrecision === 'fine' }"
              @click="fillPrecision = 'fine'"
              :disabled="isProcessing"
            >
              精细
            </button>
            <button
              class="toggle-btn"
              :class="{ active: fillPrecision === 'coarse' }"
              @click="fillPrecision = 'coarse'"
              :disabled="isProcessing"
            >
              粗略
            </button>
          </div>
        </div>

        <div class="custom-requirements-section">
          <h3 class="panel-title">3. 特殊需求 (选填)</h3>
          <textarea
            v-model="customRequirements"
            class="requirement-input"
            placeholder="请输入对本次填表的特殊要求，如：保留原模板样式、某列需留空等..."
            rows="4"
            :disabled="isProcessing"
          ></textarea>
        </div>
        <div class="action-box">
          <button
            class="btn btn-primary btn-lg w-full"
            @click="startPreview"
            :disabled="!templateFile || isProcessing"
          >
            <span class="icon" v-if="!isProcessing">🔍</span>
            <span class="spinner" v-else></span>
            {{ isProcessing ? '正在处理数据，请稍候...' : '预览填写结果' }}
          </button>
        </div>
      </div>
      <div class="right-panel">
        <h3 class="panel-title">{{ previewData ? '预览结果（可编辑）' : '执行结果' }}</h3>

        <!-- 预览表格 -->
        <div class="result-box preview-box" v-if="previewData" style="align-items:stretch;justify-content:flex-start;overflow:auto">
          <div v-for="(table, ti) in previewData.tables" :key="ti" class="preview-table-wrap">
            <table class="preview-table">
              <thead>
                <tr><th v-for="h in table.headers" :key="h">{{ h }}</th></tr>
              </thead>
              <tbody>
                <tr v-for="(row, ri) in table.rows" :key="ri">
                  <td v-for="h in table.headers" :key="h">
                    <input class="cell-input" v-model="row[h]" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="preview-actions">
            <button class="btn btn-secondary" @click="previewData = null">返回修改</button>
            <button class="btn btn-success" @click="confirmFill" :disabled="isProcessing">
              <span class="icon" v-if="!isProcessing">✨</span>
              <span class="spinner" v-else></span>
              确认并生成文件
            </button>
          </div>
        </div>

        <!-- 空状态 -->
        <div class="result-box" v-else-if="!result">
          <div class="empty-state">
            <div class="empty-icon">⏳</div>
            <p v-if="!isProcessing">尚未开始处理</p>
            <p v-else class="pulsing">AI 代理正在努力填表中...</p>
          </div>
        </div>

        <!-- 成功 -->
        <div class="result-box result-success animate-slide-in" v-else-if="result.status === 'success'">
          <div class="success-icon">✅</div>
          <h3>填写完成</h3>
          <p class="result-detail">系统成功在表格中填入了 <strong class="highlight">{{ result.filled_cells }}</strong> 个数据单元格！</p>
          <p class="result-time" v-if="elapsedTime">耗时 <strong>{{ elapsedTime }}</strong> 秒</p>
          <div class="download-section">
            <button class="btn btn-success" @click="downloadResult">
              <span class="icon">📥</span> 下载填写好的文档
            </button>
          </div>
        </div>

        <!-- 失败 -->
        <div class="result-box result-error animate-slide-in" v-else>
          <div class="error-icon">❌</div>
          <h3>处理失败</h3>
          <p class="result-detail">{{ result.error || '发生了未知错误' }}</p>
          <p class="result-time" v-if="elapsedTime">耗时 <strong>{{ elapsedTime }}</strong> 秒</p>
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
const customRequirements = ref('')
const fillPrecision = ref('fine')
const elapsedTime = ref(null)
const previewData = ref(null)

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
  result.value = null
  elapsedTime.value = null
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

const isDesktopRuntime = () => {
  const ua = (navigator.userAgent || '').toLowerCase()
  return ua.includes('pywebview') || (typeof window !== 'undefined' && !!window.pywebview)
}

const browserDownload = () => {
  if (!result.value?.output_path) return
  const url = api.getDownloadUrl(result.value.output_path)
  const token = localStorage.getItem('token')
  const xhr = new XMLHttpRequest()
  xhr.open('GET', url, true)
  xhr.responseType = 'blob'
  if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)
  xhr.onload = () => {
    if (xhr.status === 200) {
      const blob = xhr.response
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
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

const downloadResult = async () => {
  if (!result.value?.output_path) return
  try {
    toast.info('尝试准备下载...')
    const res = await api.saveFileAs(result.value.output_path)
    if (res?.status === 'success') {
      toast.success(`已保存到: ${res.saved_to}`)
      return
    }
    if (res?.status === 'cancelled') return
    if (res?.status === 'error') {
      toast.error('保存失败: ' + res.error)
      return
    }
  } catch (err) {
    if (err.response && err.response.status >= 400) {
      // 后端不支持，或者是 web 模式，降级到浏览器下载
      browserDownload()
    } else {
      toast.error('请求保存接口失败')
      browserDownload()
    }
  }
}

const startPreview = async () => {
  if (!templateFile.value) return
  isProcessing.value = true
  result.value = null
  previewData.value = null
  elapsedTime.value = null
  const startTime = Date.now()
  try {
    const formData = new FormData()
    formData.append('file', templateFile.value)
    formData.append('custom_requirements', customRequirements.value || '')
    formData.append('fill_precision', fillPrecision.value)

    const res = await api.previewTemplate(formData)
    elapsedTime.value = ((Date.now() - startTime) / 1000).toFixed(1)
    if (res.status === 'success' && res.tables?.length) {
      previewData.value = res
      toast.success(`预览完成，共 ${res.tables.length} 个表格`)
    } else {
      toast.error('未检测到可填写的表格')
    }
  } catch (error) {
    elapsedTime.value = ((Date.now() - startTime) / 1000).toFixed(1)
    toast.error('预览失败: ' + error.message)
  } finally {
    isProcessing.value = false
  }
}

const confirmFill = async () => {
  if (!templateFile.value) return
  isProcessing.value = true
  result.value = null
  elapsedTime.value = null
  const startTime = Date.now()
  try {
    const formData = new FormData()
    formData.append('file', templateFile.value)
    formData.append('custom_requirements', customRequirements.value || '')
    formData.append('fill_precision', fillPrecision.value)

    const res = await api.fillTemplate(formData)
    elapsedTime.value = ((Date.now() - startTime) / 1000).toFixed(1)
    result.value = res
    previewData.value = null
    toast.success(`表格填写完成！耗时 ${elapsedTime.value}s`)
  } catch (error) {
    elapsedTime.value = ((Date.now() - startTime) / 1000).toFixed(1)
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
.precision-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.toggle-group {
  display: flex;
  gap: 0;
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md, 6px);
  overflow: hidden;
}
.toggle-btn {
  flex: 1;
  padding: 0.6rem 1rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: var(--font-size-md, 14px);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast, 0.2s);
  outline: none;
}
.toggle-btn:not(:last-child) {
  border-right: 1px solid var(--border-subtle);
}
.toggle-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}
.toggle-btn.active {
  background: var(--accent-blue);
  color: #ffffff;
  font-weight: 600;
}
.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.custom-requirements-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.requirement-input {
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
.requirement-input:focus {
  border-color: var(--accent-blue);
}
.requirement-input::placeholder {
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
.result-time {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
}
.result-time strong {
  color: var(--accent-cyan);
  font-size: var(--font-size-lg);
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
.preview-box {
  padding: 1rem;
}
.preview-table-wrap {
  overflow-x: auto;
  margin-bottom: 1rem;
}
.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}
.preview-table th, .preview-table td {
  border: 1px solid var(--border-subtle);
  padding: 0.4rem 0.5rem;
  text-align: left;
}
.preview-table th {
  background: rgba(59, 130, 246, 0.1);
  color: var(--text-primary);
  font-weight: 600;
  white-space: nowrap;
}
.cell-input {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  outline: none;
  padding: 0.2rem 0;
}
.cell-input:focus {
  background: rgba(59, 130, 246, 0.05);
}
.preview-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 0.5rem;
}
</style>
