<template>
  <div class="project-detail">
    <div class="project-3col">
      <!-- 左侧：项目列表（与主页一致） -->
      <aside class="projects-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">我的项目</span>
        </div>
        <div class="project-list">
          <router-link v-for="p in personalProjects" :key="p.id" :to="`/project/${p.id}`" class="project-link" :class="{ active: p.id === route.params.id }">
            <span>📁</span> {{ p.name }}
          </router-link>
          <div v-if="personalProjects.length === 0" class="empty-hint">暂无</div>
        </div>
        <div class="sidebar-header" style="margin-top:1rem">
          <span class="sidebar-title">团队空间</span>
        </div>
        <div class="project-list">
          <router-link v-for="t in teams" :key="t.id" to="/team" class="project-link">
            <span>👥</span> {{ t.name }}
          </router-link>
          <div v-if="teams.length === 0" class="empty-hint">暂无</div>
        </div>
      </aside>

      <!-- 中间+右侧：项目内容 -->
      <div class="project-content">
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
                <div class="kb-actions" v-if="project.kb_id">
                  <n-button size="tiny" @click="goUpload">上传文档</n-button>
                  <n-button size="tiny" @click="goManageKB">管理知识库</n-button>
                </div>
              </div>
              <div class="kb-file-list">
                <div v-if="!project.knowledge_bases?.length" class="empty-hint">暂无关联知识库</div>
                <template v-else>
                  <div v-for="kb in project.knowledge_bases" :key="kb.id" class="kb-summary">
                    <div class="kb-summary-row">
                      <span class="kb-file-icon">📚</span>
                      <span class="kb-file-name">{{ kb.name }}</span>
                      <span class="kb-meta">{{ kb.total_chunks }} 个分块 · {{ kb.doc_count }} 个文档</span>
                    </div>
                  </div>
                  <div class="doc-list" v-if="documents.length">
                    <div v-for="doc in documents" :key="doc.file_name" class="doc-row">
                      <span class="doc-icon">📄</span>
                      <span class="doc-name">{{ doc.file_name }}</span>
                      <span class="doc-format">{{ doc.format }}</span>
                    </div>
                  </div>
                  <div v-else-if="project.kb_id" class="empty-hint">暂无文档，点击上方"上传文档"添加</div>
                </template>
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
      </div>
    </div>

    <n-modal v-model:show="showEdit" preset="dialog" title="编辑项目" positive-text="保存" negative-text="取消" @positive-click="doEdit">
      <n-form :model="editForm">
        <n-form-item label="项目名称"><n-input v-model:value="editForm.name" /></n-form-item>
        <n-form-item label="描述"><n-input v-model:value="editForm.description" type="textarea" :rows="3" /></n-form-item>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { useAppStore } from '../stores/app.js'
import api from '../api/index.js'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const appStore = useAppStore()
const project = ref(null)
const documents = ref([])
const showEdit = ref(false)
const editForm = ref({ name: '', description: '' })
const allProjects = ref([])
const teams = ref([])

const personalProjects = computed(() => allProjects.value.filter(p => p.is_personal))

const loadProject = async () => {
  try {
    project.value = await api.getProject(route.params.id)
    if (project.value.kb_id) {
      await loadDocuments(project.value.kb_id)
    }
  } catch (e) {
    message.error('项目不存在')
    router.push('/')
  }
}

const loadDocuments = async (kbId) => {
  try {
    const res = await api.listKBDocuments(kbId)
    documents.value = res.documents || []
  } catch { documents.value = [] }
}

const goUpload = () => {
  if (project.value?.kb_id) {
    appStore.switchKb(project.value.kb_id)
    router.push('/upload')
  }
}

const goManageKB = () => {
  if (project.value?.kb_id) {
    appStore.switchKb(project.value.kb_id)
    router.push('/knowledge-base')
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

watch(() => route.params.id, (newId) => {
  if (newId) loadProject()
})

onMounted(async () => {
  await loadProject()
  try { allProjects.value = await api.listProjects() } catch {}
  try { teams.value = await api.listTeams() } catch {}
})
</script>

<style scoped>
.project-detail { max-width: 1280px; margin: 0 auto; }
.project-3col {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 2rem;
  min-height: calc(100vh - 120px);
}
.projects-sidebar { padding-top: 0.5rem; }
.sidebar-header { margin-bottom: 0.5rem; }
.sidebar-title { font-weight: 600; font-size: var(--font-size-sm); color: var(--text-primary); }
.project-list { display: flex; flex-direction: column; gap: 0.2rem; }
.project-link {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.35rem 0.5rem; border-radius: var(--radius-sm);
  color: var(--text-secondary); font-size: var(--font-size-sm);
  text-decoration: none; transition: background 0.15s;
}
.project-link:hover { background: rgba(0,0,0,0.04); color: var(--text-primary); }
.project-link.active { background: rgba(51, 112, 255, 0.08); color: var(--accent-blue); font-weight: 600; }
.project-content { min-width: 0; }
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
.project-layout { display: grid; grid-template-columns: 1fr 280px; gap: 2rem; }
.project-desc { color: var(--text-secondary); font-size: var(--font-size-md); margin-bottom: 1.5rem; line-height: 1.6; }
.kb-list-section { border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); overflow: hidden; }
.kb-list-header { padding: 0.75rem 1rem; background: var(--bg-secondary); border-bottom: 1px solid var(--border-subtle); font-weight: 600; font-size: var(--font-size-sm); color: var(--text-primary); display: flex; align-items: center; justify-content: space-between; }
.kb-actions { display: flex; gap: 0.5rem; }
.kb-summary { padding: 0.6rem 1rem; border-bottom: 1px solid var(--border-subtle); }
.kb-summary-row { display: flex; align-items: center; gap: 0.75rem; font-size: var(--font-size-sm); }
.kb-meta { color: var(--text-muted); margin-left: auto; font-size: 0.8rem; }
.doc-list { }
.doc-row { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 1rem 0.5rem 2rem; border-bottom: 1px solid var(--border-subtle); font-size: var(--font-size-sm); transition: background 0.15s; }
.doc-row:last-child { border-bottom: none; }
.doc-row:hover { background: rgba(0,0,0,0.02); }
.doc-icon { font-size: 0.9rem; }
.doc-name { font-weight: 500; color: var(--text-primary); }
.doc-format { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; }
.kb-file-icon { font-size: 1rem; }
.kb-file-name { font-weight: 500; color: var(--accent-blue); }
.about-card { border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 1.25rem; }
.about-title { font-weight: 700; font-size: var(--font-size-lg); color: var(--text-primary); margin-bottom: 0.75rem; }
.about-desc { color: var(--text-secondary); font-size: var(--font-size-sm); margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-subtle); }
.about-meta { display: flex; flex-direction: column; gap: 0.5rem; }
.meta-row { display: flex; justify-content: space-between; font-size: var(--font-size-sm); color: var(--text-secondary); }
.meta-row strong { color: var(--text-primary); }
.empty-hint { color: var(--text-muted); text-align: center; padding: 1.5rem; font-size: var(--font-size-sm); }
@media (max-width: 960px) {
  .project-3col { grid-template-columns: 1fr; }
  .projects-sidebar { display: none; }
  .project-layout { grid-template-columns: 1fr; }
}
</style>
