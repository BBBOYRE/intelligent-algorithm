<template>
  <div class="project-detail animate-fade-in">
    <div class="project-header">
      <div class="project-breadcrumb">
        <router-link to="/" class="breadcrumb-link">主页</router-link>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">{{ project?.name || '...' }}</span>
      </div>
      <div class="project-actions" v-if="project">
        <n-button size="small" @click="openEdit">编辑</n-button>
        <n-button size="small" type="error" @click="confirmDelete">删除</n-button>
      </div>
    </div>

    <div class="project-layout" v-if="project">
      <main class="project-main">
        <div class="project-desc" v-if="project.description">{{ project.description }}</div>

        <div class="kb-list-section">
          <div class="kb-list-header">
            <span>知识库 ({{ project.knowledge_bases?.length || 0 }})</span>
          </div>
          <div class="kb-file-list">
            <div v-if="!project.knowledge_bases?.length" class="empty-hint">暂无关联知识库</div>
            <div v-for="kb in project.knowledge_bases" :key="kb.id" class="kb-file-row">
              <span class="kb-file-icon">📚</span>
              <span class="kb-file-name">{{ kb.name }}</span>
              <span class="kb-file-desc">{{ kb.description || '' }}</span>
            </div>
          </div>
        </div>
      </main>

      <aside class="project-sidebar">
        <div class="about-card">
          <div class="about-title">About</div>
          <div class="about-desc">{{ project.description || '暂无描述' }}</div>
          <div class="about-meta">
            <div class="meta-row"><span>创建者</span><strong>{{ project.owner_name }}</strong></div>
            <div class="meta-row"><span>类型</span><strong>{{ project.is_personal ? '个人项目' : '团队项目' }}</strong></div>
            <div class="meta-row"><span>知识库</span><strong>{{ project.knowledge_bases?.length || 0 }}</strong></div>
            <div class="meta-row"><span>创建时间</span><strong>{{ project.created_at?.replace('T',' ').slice(0,10) }}</strong></div>
          </div>
        </div>
      </aside>
    </div>

    <div v-else style="text-align:center;padding:4rem;color:var(--text-muted)">加载中...</div>

    <!-- Edit modal -->
    <n-modal v-model:show="showEdit" preset="dialog" title="编辑项目" positive-text="保存" negative-text="取消" @positive-click="doEdit">
      <n-form :model="editForm">
        <n-form-item label="项目名称"><n-input v-model:value="editForm.name" /></n-form-item>
        <n-form-item label="描述"><n-input v-model:value="editForm.description" type="textarea" :rows="3" /></n-form-item>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import api from '../api/index.js'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const project = ref(null)
const showEdit = ref(false)
const editForm = ref({ name: '', description: '' })

const loadProject = async () => {
  try {
    project.value = await api.getProject(route.params.id)
  } catch (e) {
    message.error('项目不存在')
    router.push('/')
  }
}

const openEdit = () => {
  editForm.value = { name: project.value.name, description: project.value.description || '' }
  showEdit.value = true
}

const doEdit = async () => {
  try {
    await api.updateProject(route.params.id, editForm.value)
    message.success('已保存')
    showEdit.value = false
    await loadProject()
  } catch (e) { message.error(e?.response?.data?.detail || '保存失败') }
}

const confirmDelete = () => {
  dialog.error({
    title: '删除项目',
    content: `确定删除「${project.value.name}」？此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await api.deleteProject(route.params.id)
        message.success('项目已删除')
        router.push('/')
      } catch (e) { message.error(e?.response?.data?.detail || '删除失败') }
    },
  })
}

onMounted(loadProject)
</script>

<style scoped>
.project-detail { max-width: 1200px; margin: 0 auto; }
.project-header {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 1rem; margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
}
.project-breadcrumb { display: flex; align-items: center; gap: 0.5rem; font-size: var(--font-size-lg); }
.breadcrumb-link { color: var(--accent-blue); text-decoration: none; font-weight: 600; }
.breadcrumb-link:hover { text-decoration: underline; }
.breadcrumb-sep { color: var(--text-muted); }
.breadcrumb-current { font-weight: 600; color: var(--text-primary); }
.project-actions { display: flex; gap: 0.5rem; }
.project-layout {
  display: grid; grid-template-columns: 1fr 300px; gap: 2rem;
}
.project-desc {
  color: var(--text-secondary); font-size: var(--font-size-md);
  margin-bottom: 1.5rem; line-height: 1.6;
}
.kb-list-section {
  border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); overflow: hidden;
}
.kb-list-header {
  padding: 0.75rem 1rem; background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  font-weight: 600; font-size: var(--font-size-sm); color: var(--text-primary);
}
.kb-file-row {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 1rem; border-bottom: 1px solid var(--border-subtle);
  font-size: var(--font-size-sm); transition: background 0.15s;
}
.kb-file-row:last-child { border-bottom: none; }
.kb-file-row:hover { background: rgba(0,0,0,0.02); }
.kb-file-icon { font-size: 1rem; }
.kb-file-name { font-weight: 500; color: var(--accent-blue); }
.kb-file-desc { color: var(--text-muted); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.about-card {
  border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 1.25rem;
}
.about-title { font-weight: 700; font-size: var(--font-size-lg); color: var(--text-primary); margin-bottom: 0.75rem; }
.about-desc { color: var(--text-secondary); font-size: var(--font-size-sm); margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-subtle); }
.about-meta { display: flex; flex-direction: column; gap: 0.5rem; }
.meta-row { display: flex; justify-content: space-between; font-size: var(--font-size-sm); color: var(--text-secondary); }
.meta-row strong { color: var(--text-primary); }
.empty-hint { color: var(--text-muted); text-align: center; padding: 2rem; font-size: var(--font-size-sm); }
@media (max-width: 768px) {
  .project-layout { grid-template-columns: 1fr; }
}
</style>
