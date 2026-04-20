<template>
  <div class="home-view">
    <div class="home-layout">
      <!-- Left: Projects sidebar -->
      <aside class="projects-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">我的项目</span>
          <n-button size="tiny" type="primary" @click="showCreateProject = true">新建</n-button>
        </div>
        <n-input v-model:value="projectSearch" placeholder="搜索项目..." size="small" clearable style="margin-bottom:0.75rem" />
        <div class="project-list">
          <router-link v-for="p in filteredProjects" :key="p.id" :to="`/project/${p.id}`" class="project-item">
            <span class="project-icon">{{ p.is_personal ? '📁' : '👥' }}</span>
            <span class="project-name">{{ p.name }}</span>
          </router-link>
          <div v-if="filteredProjects.length === 0" class="empty-hint">暂无项目</div>
        </div>
      </aside>

      <!-- Center: Feed -->
      <main class="feed-section">
        <h1 class="home-title">Home</h1>
        <div class="feed-list">
          <div v-if="feed.length === 0" class="empty-hint" style="padding:3rem">暂无动态</div>
          <div v-for="(item, idx) in feed" :key="idx" class="feed-item">
            <div class="feed-type-dot" :class="item.type"></div>
            <div class="feed-content">
              <div class="feed-title">{{ item.title }}</div>
              <div class="feed-detail" v-if="item.detail">{{ item.detail }}</div>
              <div class="feed-time">{{ formatTime(item.created_at) }}</div>
            </div>
          </div>
        </div>
      </main>

      <!-- Right: Stats panel -->
      <aside class="stats-sidebar">
        <div class="stats-card">
          <div class="stats-card-title">快速统计</div>
          <div class="stat-row"><span>项目数</span><strong>{{ projects.length }}</strong></div>
          <div class="stat-row"><span>知识库分块</span><strong>{{ kbStats.total_chunks || 0 }}</strong></div>
          <div class="stat-row"><span>已入库文档</span><strong>{{ kbStats.documents?.length || 0 }}</strong></div>
        </div>
        <div class="stats-card" v-if="pendingTasks.length > 0">
          <div class="stats-card-title">待办任务</div>
          <div v-for="t in pendingTasks.slice(0, 5)" :key="t.id" class="task-item">
            <span class="task-title">{{ t.title }}</span>
            <span class="task-deadline" v-if="t.deadline">{{ t.deadline.slice(0, 10) }}</span>
          </div>
        </div>
      </aside>
    </div>
    <!-- Create project modal -->
    <n-modal v-model:show="showCreateProject" preset="dialog" title="新建项目" positive-text="创建" negative-text="取消" @positive-click="doCreateProject">
      <n-form :model="createForm">
        <n-form-item label="项目名称">
          <n-input v-model:value="createForm.name" placeholder="输入项目名称" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="createForm.description" type="textarea" :rows="2" placeholder="可选" />
        </n-form-item>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '../api/index.js'

const message = useMessage()
const projects = ref([])
const feed = ref([])
const kbStats = ref({ total_chunks: 0, documents: [] })
const pendingTasks = ref([])
const projectSearch = ref('')
const showCreateProject = ref(false)
const createForm = ref({ name: '', description: '' })

const filteredProjects = computed(() => {
  if (!projectSearch.value) return projects.value
  const q = projectSearch.value.toLowerCase()
  return projects.value.filter(p => p.name.toLowerCase().includes(q))
})

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  return iso.replace('T', ' ').slice(0, 16)
}
const doCreateProject = async () => {
  if (!createForm.value.name.trim()) { message.warning('请输入项目名称'); return false }
  try {
    await api.createProject(createForm.value)
    message.success('项目已创建')
    createForm.value = { name: '', description: '' }
    await loadProjects()
  } catch (e) { message.error(e?.response?.data?.detail || '创建失败') }
}

const loadProjects = async () => {
  try { projects.value = await api.listProjects() } catch { projects.value = [] }
}

onMounted(async () => {
  await loadProjects()
  try { feed.value = await api.getFeed(30) } catch { feed.value = [] }
  try { kbStats.value = await api.getKBStats() } catch {}
  try {
    const allTeams = await api.listTeams()
    let tasks = []
    for (const t of allTeams) {
      try {
        const teamTasks = await api.getTeamTasks(t.id)
        tasks = tasks.concat(teamTasks.filter(tk => tk.status !== 'completed'))
      } catch {}
    }
    pendingTasks.value = tasks
  } catch {}
})
</script>

<style scoped>
.home-view { max-width: 1280px; margin: 0 auto; }
.home-layout {
  display: grid;
  grid-template-columns: 240px 1fr 280px;
  gap: 2rem;
  min-height: calc(100vh - 120px);
}
.projects-sidebar { padding-top: 0.5rem; }
.sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 0.75rem;
}
.sidebar-title { font-weight: 600; font-size: var(--font-size-md); color: var(--text-primary); }
.project-list { display: flex; flex-direction: column; gap: 0.25rem; }
.project-item {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.4rem 0.5rem; border-radius: var(--radius-sm);
  color: var(--text-secondary); font-size: var(--font-size-sm);
  text-decoration: none; transition: background 0.15s;
}
.project-item:hover { background: rgba(0,0,0,0.04); color: var(--text-primary); }
.project-icon { font-size: 1rem; }
.project-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.feed-section { border-left: 1px solid var(--border-subtle); border-right: 1px solid var(--border-subtle); padding: 0 2rem; }
.home-title { font-size: var(--font-size-2xl); font-weight: 700; color: var(--text-primary); margin-bottom: 1.5rem; }
.feed-list { display: flex; flex-direction: column; }
.feed-item {
  display: flex; gap: 0.75rem; padding: 0.75rem 0;
  border-bottom: 1px solid var(--border-subtle);
}
.feed-type-dot {
  width: 10px; height: 10px; border-radius: 50%; margin-top: 0.35rem; flex-shrink: 0;
}
.feed-type-dot.activity { background: var(--accent-blue); }
.feed-type-dot.announcement { background: var(--accent-amber); }
.feed-type-dot.task { background: var(--accent-green); }
.feed-content { flex: 1; min-width: 0; }
.feed-title { font-weight: 500; color: var(--text-primary); font-size: var(--font-size-sm); }
.feed-detail { color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: 0.2rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.feed-time { color: var(--text-muted); font-size: var(--font-size-xs); margin-top: 0.25rem; }
.stats-sidebar { padding-top: 0.5rem; }
.stats-card {
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg); padding: 1rem; margin-bottom: 1rem;
}
.stats-card-title { font-weight: 600; font-size: var(--font-size-sm); color: var(--text-primary); margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-subtle); }
.stat-row { display: flex; justify-content: space-between; padding: 0.3rem 0; font-size: var(--font-size-sm); color: var(--text-secondary); }
.stat-row strong { color: var(--text-primary); }
.task-item { padding: 0.3rem 0; font-size: var(--font-size-sm); display: flex; justify-content: space-between; }
.task-title { color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.task-deadline { color: var(--text-muted); font-size: var(--font-size-xs); flex-shrink: 0; }
.empty-hint { color: var(--text-muted); font-size: var(--font-size-sm); text-align: center; padding: 1rem; }
@media (max-width: 960px) {
  .home-layout { grid-template-columns: 1fr; }
  .projects-sidebar { display: none; }
  .stats-sidebar { display: none; }
  .feed-section { border: none; padding: 0; }
}
</style>
