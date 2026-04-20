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
          <router-link v-for="p in personalProjects" :key="p.id" :to="`/project/${p.id}`" class="project-item">
            <span class="project-icon">📁</span>
            <span class="project-name">{{ p.name }}</span>
          </router-link>
          <div v-if="personalProjects.length === 0" class="empty-hint">暂无个人项目</div>
        </div>

        <div class="sidebar-header" style="margin-top:1.5rem">
          <span class="sidebar-title">团队空间</span>
        </div>
        <div class="project-list">
          <router-link v-for="t in teams" :key="t.id" to="/team" class="project-item">
            <span class="project-icon">👥</span>
            <span class="project-name">{{ t.name }}</span>
          </router-link>
          <div v-if="teams.length === 0" class="empty-hint">暂无团队</div>
        </div>
      </aside>

      <!-- Center: Feed -->
      <main class="feed-section">
        <h1 class="home-title">Home</h1>

        <div class="charts-row">
          <div class="chart-card">
            <div class="donut-chart" :style="docChartStyle"></div>
            <div class="chart-label">
              <strong>{{ kbStats.documents?.length || 0 }}</strong>
              <span>文档数</span>
            </div>
          </div>
          <div class="chart-card">
            <div class="donut-chart" :style="taskChartStyle"></div>
            <div class="chart-label">
              <strong>{{ completedTaskCount }}/{{ allTaskCount }}</strong>
              <span>任务完成</span>
            </div>
          </div>
        </div>

        <div class="feed-header">最近动态</div>
        <div class="feed-scroll">
          <div v-if="feed.length === 0" class="empty-hint" style="padding:2rem">暂无动态</div>
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
          <div class="stats-card-title">任务</div>
          <div v-if="allTasks.length === 0" class="empty-hint">暂无任务</div>
          <div v-for="t in allTasks.slice(0, 8)" :key="t.id" class="task-card">
            <div class="task-card-header">
              <span class="task-title" :class="{ done: t.status === 'completed' }">{{ t.title }}</span>
              <n-button v-if="t.status !== 'completed'" size="tiny" type="success" @click="openTaskComplete(t)">完成</n-button>
              <n-tag v-else size="small" type="success">已完成</n-tag>
            </div>
            <div class="task-desc" v-if="t.description">{{ t.description }}</div>
            <div class="task-desc" v-if="t.status === 'completed' && t.completion_note" style="color:var(--accent-green)">{{ t.completion_note }}</div>
            <div class="task-meta-row">
              <span v-if="t.team_name">来自: {{ t.team_name }}</span>
              <span v-if="t.deadline" class="task-deadline">截止: {{ t.deadline.slice(0, 10) }}</span>
            </div>
          </div>
        </div>
        <div class="stats-card">
          <div class="stats-card-title">备忘录</div>
          <div v-if="memos.length === 0" class="empty-hint">暂无备忘录</div>
          <div v-for="m in memos.slice(0, 5)" :key="m.id" class="memo-card">
            <div class="memo-card-title">
              <span>{{ m.is_starred ? '⭐ ' : '' }}{{ m.title || '无标题' }}</span>
              <span class="memo-due" v-if="m.due_date" :class="{ overdue: isOverdue(m.due_date) }">{{ formatDue(m.due_date) }}</span>
            </div>
            <div class="memo-card-content" v-if="m.content">{{ m.content.slice(0, 100) }}{{ m.content.length > 100 ? '...' : '' }}</div>
          </div>
          <router-link v-if="memos.length > 0" to="/memos" style="font-size:var(--font-size-xs);color:var(--accent-blue);display:block;margin-top:0.5rem">查看全部 →</router-link>
        </div>
        <div class="stats-card">
          <div class="stats-card-title">快速统计</div>
          <div class="stat-row"><span>项目数</span><strong>{{ projects.length }}</strong></div>
          <div class="stat-row"><span>知识库分块</span><strong>{{ kbStats.total_chunks || 0 }}</strong></div>
          <div class="stat-row"><span>已入库文档</span><strong>{{ kbStats.documents?.length || 0 }}</strong></div>
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
    <!-- 完成任务弹窗 -->
    <n-modal v-model:show="showCompleteTask" preset="card" title="确认完成任务" style="width:460px">
      <div v-if="completingTask" style="margin-bottom:0.75rem;font-weight:600">{{ completingTask.title }}</div>
      <n-form label-placement="left" label-width="80">
        <n-form-item label="完成说明">
          <n-input v-model:value="completeNote" type="textarea" :rows="3" placeholder="描述完成情况（可选）" />
        </n-form-item>
        <n-form-item label="提交文件">
          <input type="file" ref="completeFileInput" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display:flex;justify-content:flex-end;gap:8px">
          <n-button @click="showCompleteTask = false">取消</n-button>
          <n-button type="primary" @click="doCompleteTask">确认完成</n-button>
        </div>
      </template>
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
const allTasks = ref([])
const memos = ref([])
const allTaskCount = ref(0)
const completedTaskCount = ref(0)
const projectSearch = ref('')
const showCreateProject = ref(false)
const createForm = ref({ name: '', description: '' })
const teams = ref([])
const showCompleteTask = ref(false)
const completingTask = ref(null)
const completeNote = ref('')
const completeFileInput = ref(null)

const filteredProjects = computed(() => {
  if (!projectSearch.value) return projects.value
  const q = projectSearch.value.toLowerCase()
  return projects.value.filter(p => p.name.toLowerCase().includes(q))
})

const personalProjects = computed(() => {
  const list = projectSearch.value
    ? filteredProjects.value.filter(p => p.is_personal)
    : projects.value.filter(p => p.is_personal)
  return list
})

const teamProjects = computed(() => {
  const list = projectSearch.value
    ? filteredProjects.value.filter(p => !p.is_personal)
    : projects.value.filter(p => !p.is_personal)
  return list
})

const docChartStyle = computed(() => {
  const docs = kbStats.value.documents?.length || 0
  const total = Math.max(kbStats.value.total_chunks || 1, docs)
  const pct = Math.round((docs / total) * 100)
  return { background: `conic-gradient(var(--accent-blue) ${pct}%, var(--bg-input) ${pct}%)` }
})

const taskChartStyle = computed(() => {
  const total = allTaskCount.value || 1
  const pct = Math.round((completedTaskCount.value / total) * 100)
  return { background: `conic-gradient(var(--accent-green) ${pct}%, var(--bg-input) ${pct}%)` }
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

const isOverdue = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const formatDue = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = Math.ceil((d - now) / 86400000)
  if (diff < 0) return '已过期'
  if (diff === 0) return '今天'
  if (diff === 1) return '明天'
  return `${diff}天后`
}

const openTaskComplete = (task) => {
  completingTask.value = task
  completeNote.value = ''
  showCompleteTask.value = true
}

const doCompleteTask = async () => {
  if (!completingTask.value?.team_id) return
  const formData = new FormData()
  formData.append('completion_note', completeNote.value)
  if (completeFileInput.value?.files?.[0]) {
    formData.append('file', completeFileInput.value.files[0])
  }
  try {
    await api.completeTeamTask(completingTask.value.team_id, completingTask.value.id, formData)
    message.success('任务已完成')
    showCompleteTask.value = false
    pendingTasks.value = pendingTasks.value.filter(t => t.id !== completingTask.value.id)
    completedTaskCount.value++
  } catch (e) { message.error(e?.response?.data?.detail || '操作失败') }
}

const loadProjects = async () => {
  try { projects.value = await api.listProjects() } catch { projects.value = [] }
}

onMounted(async () => {
  await loadProjects()
  try { feed.value = await api.getFeed(30) } catch { feed.value = [] }
  try { kbStats.value = await api.getKBStats() } catch {}
  try { memos.value = await api.listMemos() } catch {}
  try {
    const allTeams = await api.listTeams()
    teams.value = allTeams
    let tasks = []
    let allTasksList = []
    let completed = 0
    let total = 0
    for (const t of allTeams) {
      try {
        const teamTasks = await api.getTeamTasks(t.id)
        total += teamTasks.length
        completed += teamTasks.filter(tk => tk.status === 'completed').length
        tasks = tasks.concat(teamTasks.filter(tk => tk.status !== 'completed').map(tk => ({ ...tk, team_id: t.id })))
        allTasksList = allTasksList.concat(teamTasks.map(tk => ({ ...tk, team_id: t.id })))
      } catch {}
    }
    pendingTasks.value = tasks
    allTasks.value = allTasksList
    allTaskCount.value = total
    completedTaskCount.value = completed
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
.task-title.done { text-decoration: line-through; color: var(--text-muted); }
.task-deadline { color: var(--text-muted); font-size: var(--font-size-xs); flex-shrink: 0; }
.empty-hint { color: var(--text-muted); font-size: var(--font-size-sm); text-align: center; padding: 1rem; }
.charts-row { display: flex; gap: 1.5rem; margin-bottom: 1.5rem; }
.chart-card { flex: 1; display: flex; align-items: center; gap: 1rem; padding: 1rem; border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); }
.donut-chart { width: 60px; height: 60px; border-radius: 50%; flex-shrink: 0; }
.chart-label { display: flex; flex-direction: column; }
.chart-label strong { font-size: var(--font-size-xl); color: var(--text-primary); }
.chart-label span { font-size: var(--font-size-xs); color: var(--text-muted); }
.feed-header { font-weight: 600; font-size: var(--font-size-md); color: var(--text-primary); margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-subtle); }
.feed-scroll { max-height: 400px; overflow-y: auto; }
.task-source { font-size: var(--font-size-xs); color: var(--text-muted); }
.task-card {
  padding: 0.5rem 0; border-bottom: 1px solid var(--border-subtle);
}
.task-card:last-child { border-bottom: none; }
.task-card-header { display: flex; justify-content: space-between; align-items: center; }
.task-desc { font-size: var(--font-size-xs); color: var(--text-secondary); margin-top: 0.25rem; }
.task-meta-row { display: flex; gap: 0.75rem; font-size: var(--font-size-xs); color: var(--text-muted); margin-top: 0.25rem; }
.memo-card { padding: 0.5rem 0; border-bottom: 1px solid var(--border-subtle); }
.memo-card:last-child { border-bottom: none; }
.memo-card-title { display: flex; justify-content: space-between; align-items: center; font-size: var(--font-size-sm); font-weight: 500; color: var(--text-primary); }
.memo-due { font-size: var(--font-size-xs); color: var(--accent-amber); flex-shrink: 0; }
.memo-due.overdue { color: var(--accent-red); }
.memo-card-content { font-size: var(--font-size-xs); color: var(--text-secondary); margin-top: 0.25rem; line-height: 1.5; }
@media (max-width: 960px) {
  .home-layout { grid-template-columns: 1fr; }
  .projects-sidebar { display: none; }
  .stats-sidebar { display: none; }
  .feed-section { border: none; padding: 0; }
}
</style>
