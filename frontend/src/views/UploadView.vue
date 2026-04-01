<template>
  <div class="upload-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">文档上传与解析</h2>
      <p class="section-subtitle">支持 docx, xlsx, md, txt 格式，系统将自动进行解析、分块，并存入 ChromaDB 知识库。</p>
    </div>

    <div class="upload-section card-static">
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
          accept=".docx,.xlsx,.md,.txt" 
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
import { ref } from 'vue'
import { useToast } from '../composables/useToast'
import { useAppStore } from '../stores/app'
import api from '../api/index.js'

const fileInput = ref(null)
const files = ref([])
const isDragging = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const toast = useToast()
const store = useAppStore()

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
  const allowedExtensions = ['.docx', '.xlsx', '.md', '.txt']
  const validFiles = newFiles.filter(file => {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
    return allowedExtensions.includes(ext)
  })

  if (validFiles.length < newFiles.length) {
    toast.error('某些文件格式不支持，仅支持 docx, xlsx, md, txt')
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

    uploadStatus.value = `正在上传并解析...这可能需要一些时间`
    uploadProgress.value = 0.5 // mock progress

    const res = await api.uploadFiles(formData)
    
    uploadProgress.value = 1.0
    uploadStatus.value = `处理完成！`
    
    toast.success(`成功解析并入库 ${res.success_count} 个文件`)
    
    clearFiles()
    await store.refreshKBStats()
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
</style>
