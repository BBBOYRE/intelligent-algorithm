<template>
  <div class="memos-view animate-fade-in stagger-children">
    <div class="page-header">
      <div class="header-content">
        <h2 class="section-title">备忘录管理</h2>
        <p class="section-subtitle">记录和管理您的重要备忘、待办事项</p>
      </div>
      <n-button type="primary" @click="openCreateModal">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        新建备忘录
      </n-button>
    </div>

    <div class="memos-grid">
      <n-empty v-if="memos.length === 0 && !loading" description="暂无备忘录" />
      
      <div v-for="memo in memos" :key="memo.id" class="memo-card card-static">
        <div class="memo-header">
          <div class="memo-title">{{ memo.title || '无标题' }}</div>
          <div class="memo-actions">
            <n-button quaternary circle size="small" @click="toggleStar(memo)">
              <n-icon :class="{ 'starred': memo.is_starred }">
                <Star v-if="memo.is_starred" />
                <StarOutline v-else />
              </n-icon>
            </n-button>
            <n-button quaternary circle size="small" @click="openEditModal(memo)">
              <n-icon><CreateOutline /></n-icon>
            </n-button>
            <n-popconfirm @positive-click="deleteMemo(memo.id)" positive-text="删除" negative-text="取消">
              <template #trigger>
                <n-button quaternary circle size="small" type="error">
                  <n-icon><TrashOutline /></n-icon>
                </n-button>
              </template>
              确定删除此备忘录？
            </n-popconfirm>
          </div>
        </div>
        
        <div class="memo-content">{{ truncate(memo.content, 100) }}</div>
        
        <div class="memo-footer">
          <div class="memo-date" v-if="memo.due_date" :class="{ 'overdue': isOverdue(memo.due_date), 'close': isClose(memo.due_date) }">
            <n-icon><TimeOutline /></n-icon> 截止: {{ formatDate(memo.due_date) }}
          </div>
          <div class="memo-date" v-else>
            <n-icon><CalendarOutline /></n-icon> 创建: {{ formatDate(memo.created_at) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Edit/Create Modal -->
    <n-modal v-model:show="showModal" preset="card" :title="isEdit ? '编辑备忘录' : '新建备忘录'" style="width: 600px">
      <n-form ref="formRef" :model="form" :rules="rules">
        <n-form-item label="标题" path="title">
          <n-input v-model:value="form.title" placeholder="输入标题（可选）" />
        </n-form-item>
        <n-form-item label="内容" path="content">
          <n-input v-model:value="form.content" type="textarea" placeholder="输入备忘录内容..." :autosize="{ minRows: 4, maxRows: 10 }" />
        </n-form-item>
        <n-form-item label="截止日期" path="due_date">
          <n-date-picker v-model:value="form.due_date" type="datetime" clearable placeholder="选择截止日期（可选）" style="width: 100%" />
        </n-form-item>
        <n-form-item label="设为收藏">
          <n-switch v-model:value="form.is_starred" />
        </n-form-item>
      </n-form>
      <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 16px;">
        <n-button @click="showModal = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="saveMemo">保存</n-button>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { AddOutline, StarOutline, Star, CreateOutline, TrashOutline, TimeOutline, CalendarOutline } from '@vicons/ionicons5'
import { useMessage } from 'naive-ui'
import api from '../api/index'

const message = useMessage()
const memos = ref([])
const loading = ref(false)

const showModal = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref(null)

const form = ref({
  id: null,
  title: '',
  content: '',
  due_date: null,
  is_starred: false
})

const rules = {
  content: { required: true, message: '内容不能为空', trigger: 'blur' }
}

const fetchMemos = async () => {
  loading.value = true
  try {
    memos.value = await api.listMemos()
  } catch (err) {
    message.error('加载备忘录失败')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEdit.value = false
  form.value = { id: null, title: '', content: '', due_date: null, is_starred: false }
  showModal.value = true
}

const openEditModal = (memo) => {
  isEdit.value = true
  form.value = { 
    id: memo.id, 
    title: memo.title, 
    content: memo.content, 
    // naive ui date picker expects timestamp
    due_date: memo.due_date ? new Date(memo.due_date).getTime() : null, 
    is_starred: memo.is_starred 
  }
  showModal.value = true
}

const toggleStar = async (memo) => {
  try {
    await api.updateMemo(memo.id, { is_starred: !memo.is_starred })
    memo.is_starred = !memo.is_starred
  } catch (e) {
    message.error('操作失败')
  }
}

const saveMemo = () => {
  formRef.value?.validate(async (errors) => {
    if (errors) return
    saving.value = true
    try {
      const payload = { ...form.value }
      // Convert timestamp back to ISO string for backend
      if (payload.due_date) {
        payload.due_date = new Date(payload.due_date).toISOString()
      }
      
      if (isEdit.value) {
        await api.updateMemo(payload.id, payload)
        message.success('更新成功')
      } else {
        await api.createMemo(payload)
        message.success('创建成功')
      }
      showModal.value = false
      fetchMemos()
    } catch (e) {
      message.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      saving.value = false
    }
  })
}

const deleteMemo = async (id) => {
  try {
    await api.deleteMemo(id)
    message.success('删除成功')
    fetchMemos()
  } catch (e) {
    message.error('删除失败')
  }
}

// Utils
const truncate = (text, len) => {
  if (!text) return ''
  return text.length > len ? text.substring(0, len) + '...' : text
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const isOverdue = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const isClose = (dateStr) => {
  if (!dateStr) return false
  const diffTime = new Date(dateStr) - new Date()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays >= 0 && diffDays <= 3
}

onMounted(() => {
  fetchMemos()
})
</script>

<style scoped>
.memos-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1rem 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.section-subtitle {
  color: var(--text-muted);
}

.memos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.memo-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  transition: all 0.2s;
}

.memo-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--accent-blue);
}

.memo-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.memo-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--text-primary);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.memo-actions {
  display: flex;
  gap: 4px;
}

.starred {
  color: #f5a623;
}

.memo-content {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.5;
  flex: 1;
  margin-bottom: 1rem;
  white-space: pre-wrap;
  word-break: break-all;
}

.memo-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  border-top: 1px solid var(--border-subtle);
  padding-top: 0.75rem;
}

.memo-date {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 4px;
}

.memo-date.overdue {
  color: var(--accent-red);
  font-weight: 600;
}

.memo-date.close {
  color: var(--accent-amber);
  font-weight: 600;
}
</style>
