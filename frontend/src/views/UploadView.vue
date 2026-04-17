<template>
  <div class="upload-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">文档上传与解析</h2>
      <p class="section-subtitle">支持 docx, xlsx, md, txt, csv, html, pdf, 图片(jpg/png/bmp/tiff) 格式，系统将自动进行解析、分块，并存入知识库。</p>
    </div>

    <div class="upload-section card-static">
      <!-- 知识库选择器 -->
      <div class="kb-selector-bar" v-if="kbOptions.length > 1">
        <span style="color:var(--text-secondary);font-size:var(--font-size-sm)">上传到：</span>
        <n-select v-model:value="selectedKBId" :options="kbOptions" style="width:280px" size="small" />
      </div>

      <!-- 知识库状态栏 -->
      <div class="kb-status-bar">
        <div class="kb-info">
          <span class="kb-label">知识库状态</span>
          <span class="kb-chunks">已入库 <strong>{{ kbStats.total_chunks || 0 }}</strong> 个分块</span>
          <span class="kb-docs" v-if="kbStats.documents">，<strong>{{ kbStats.documents.length }}</strong> 个文档</span>
        </div>
        <div class="kb-doc-list" v-if="kbStats.documents && kbStats.documents.length > 0">
          <span class="doc-tag" v-for="doc in kbStats.documents" :key="doc.file_name">{{ doc.file_name }}</span>
        </div>
        <button class="btn btn-danger-sm" @click="handleClearKB" :disabled="isUploading || isClearing">
          {{ isClearing ? '清空中...' : '清空知识库' }}
        </button>
      </div>

      <div 
        class="drop-zone" 
        :class="{ 'dragover': isDragging }"
        @dragover.prevent="onDragOver"
        @dragleave="onDragLeave"
        @drop.prevent="onDrop"
        @click="triggerFileInput"
      >
        <div class="upload-icon">📁</div>
        <h3 class="upload-title">点击或拖拽文件到此处传</h3>
        <p class="upload-hint">支持多个文件同时上传 (最多 20 个)</p>
        <input 
          type="file" 
          ref="fileInput" 
          multiple 
          accept=".docx,.xlsx,.md,.txt,.csv,.html,.pdf,.jpg,.jpeg,.png,.bmp,.tiff" 
          style="display: none" 
          @change="onFileSelected" 
        />
      </div>

      <div class="file-list" v-if="files.length > 0">
        <h4 class="list-title">待处理文件 ({{ files.length }})</h4>
        <div class="file-items">
          <div v-for="(file, index) in files" :key="index" class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatSize(file.size) }}</span>
            <button class="remove-btn" @click="removeFile(index)" :disabled="isUploading" title="移除">×</button>
          </div>
        </div>

        <div class="upload-actions">
          <button class="btn btn-secondary" @click="clearFiles" :disabled="isUploading">清空列表</button>
          <button class="btn btn-primary" @click="uploadFiles" :disabled="isUploading || files.length === 0">
            <span class="icon" v-if="!isUploading">🚀</span>
            <span class="spinner" v-else></span>
            {{ isUploading ? '正在解析并入库...' : '开始解析并入库' }}
          </button>
        </div>
      </div>
      
      <!-- Progress Section -->
      <div class="progress-section" v-if="isUploading">
        <div class="progress-header">
          <span>处理进度: {{ uploadStatus }}</span>
          <span>{{ Math.round(uploadProgress * 100) }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-bar-fill" :style="{ width: `${uploadProgress * 100}%` }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '../composables/useToast'
import { useAppStore } from '../stores/app'
import api from '../api/index.js'

const fileInput = ref(null)
const files = ref([])
const isDragging = ref(false)
const isUploading = ref(false)
const isClearing = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const toast = useToast()
const store = useAppStore()
const kbStats = ref({ total_chunks: 0, documents: [] })
const selectedKBId = ref('default')
const kbOptions = ref([{ label: '个人默认知识库', value: 'default' }])
const selectedKBTeamId = ref('')

const loadKBOptions = async () => {
  try {
    const res = await api.listKBs()
    const opts = [{ label: '个人默认知识库', value: 'default' }]
    for (const kb of (res.knowledge_bases || [])) {
      const prefix = kb.team_name ? `[${kb.team_name}] ` : ''
      opts.push({ label: prefix + kb.name, value: kb.id, teamId: kb.team_id || '' })
    }
    kbOptions.value = opts
  } catch {}
}

const loadKBStats = async () => {
  try {
    kbStats.value = await api.getKBStats(selectedKBId.value)
  } catch (e) {
    kbStats.value = { total_chunks: 0, documents: [] }
  }
}

const handleClearKB = async () => {
  if (!confirm('确定要清空知识库吗？所有已入库的文档数据将被删除。')) return
  isClearing.value = true
  try {
    await api.clearKB()
    toast.success('知识库已清空')
    await loadKBStats()
    await store.refreshKBStats()
  } catch (e) {
    toast.error('清空失败: ' + e.message)
  } finally {
    isClearing.value = false
  }
}

onMounted(() => {
  loadKBStats()
  loadKBOptions()
})

const triggerFileInput = () => {
  if (!isUploading.value) fileInput.value.click()
}

const onDragOver = () => {
  if (!isUploading.value) isDragging.value = true
}

const onDragLeave = () => {
  isDragging.value = false
}

const onDrop = (event) => {
  isDragging.value = false
  if (isUploading.value) return
  
  const droppedFiles = Array.from(event.dataTransfer.files)
  addFiles(droppedFiles)
}

const onFileSelected = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
  fileInput.value.value = '' // reset input
}

const addFiles = (newFiles) => {
  const allowedExtensions = ['.docx', '.xlsx', '.md', '.txt', '.csv', '.html', '.htm', '.pdf']
  const validFiles = newFiles.filter(file => {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
    return allowedExtensions.includes(ext)
  })

  if (validFiles.length < newFiles.length) {
    toast.error('某些文件格式不支持，支持 docx, xlsx, md, txt, csv, html, pdf')
  }

  files.value = [...files.value, ...validFiles]
}

const removeFile = (index) => {
  files.value.splice(index, 1)
}

const clearFiles = () => {
  files.value = []
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const uploadFiles = async () => {
  if (files.value.length === 0) return

  isUploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = `准备上传 ${files.value.length} 个文件...`

  try {
    const formData = new FormData()
    files.value.forEach(file => {
      formData.append('files', file)
    })
    formData.append('kb_id', selectedKBId.value)
    const opt = kbOptions.value.find(o => o.value === selectedKBId.value)
    if (opt?.teamId) formData.append('team_id', opt.teamId)

    // 5个以上文件用异步模式
    if (files.value.length > 5) {
      uploadStatus.value = '正在上传文件...'
      const asyncRes = await api.uploadFilesAsync(formData)
      const taskId = asyncRes.task_id

      // 轮询进度
      uploadStatus.value = '后台解析中...'
      let done = false
      while (!done) {
        await new Promise(r => setTimeout(r, 1000))
        const task = await api.getTask(taskId)
        uploadProgress.value = task.progress
        uploadStatus.value = `正在解析: ${task.completed_count}/${task.total}`
        if (task.status === 'completed' || task.status === 'failed') {
          done = true
          if (task.result) {
            toast.success(`成功解析并入库 ${task.result.success_count} 个文件`)
          }
        }
      }
    } else {
      uploadStatus.value = '正在上传并解析...'
      uploadProgress.value = 0.3
      const res = await api.uploadFiles(formData)
      toast.success(`成功解析并入库 ${res.success_count} 个文件`)
    }

    uploadProgress.value = 1.0
    uploadStatus.value = '处理完成！'
    clearFiles()
    await store.refreshKBStats()
    await loadKBStats()
  } catch (error) {
    toast.error(`上传失败: ${error.message}`)
    uploadStatus.value = `处理出错`
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.upload-view {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.upload-hint {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
}

.file-list {
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  padding: 1.5rem;
}

.list-title {
  font-size: var(--font-size-md);
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.file-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 1.5rem;
  padding-right: 0.5rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.file-item:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-active);
}

.file-icon {
  font-size: 1.25rem;
}

.file-name {
  flex: 1;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
}

.remove-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
  transition: color var(--transition-fast);
}
.remove-btn:hover {
  color: var(--accent-rose);
}

.upload-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.kb-status-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}
.kb-info {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}
.kb-info strong {
  color: var(--accent-cyan);
  font-weight: 700;
}
.kb-label {
  font-weight: 600;
  color: var(--text-primary);
  margin-right: 0.75rem;
}
.kb-doc-list {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.doc-tag {
  padding: 0.2rem 0.6rem;
  font-size: var(--font-size-xs, 12px);
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.25);
  color: var(--accent-blue);
  border-radius: var(--radius-sm, 4px);
}
.btn-danger-sm {
  padding: 0.35rem 0.85rem;
  font-size: var(--font-size-sm, 13px);
  background: rgba(244, 63, 94, 0.15);
  border: 1px solid rgba(244, 63, 94, 0.3);
  color: var(--accent-rose);
  border-radius: var(--radius-sm, 4px);
  cursor: pointer;
  transition: all var(--transition-fast, 0.2s);
  white-space: nowrap;
}
.btn-danger-sm:hover {
  background: rgba(244, 63, 94, 0.25);
}
.btn-danger-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
