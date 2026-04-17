<template>
  <div class="team-view animate-fade-in stagger-children">
    <div class="page-header">
      <h2 class="section-title">团队工作空间</h2>
      <p class="section-subtitle">管理团队成员与协作权限</p>
    </div>

    <!-- 团队列表 + 创建 -->
    <div class="top-bar">
      <n-select
        v-model:value="currentTeamId"
        :options="teamOptions"
        placeholder="选择团队"
        style="width: 220px"
        @update:value="onTeamChange"
      />
      <n-button type="primary" @click="showCreateModal = true">+ 创建团队</n-button>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" style="text-align:center;padding:4rem 0;color:var(--text-secondary)">
      <div class="spinner spinner-lg" style="margin:0 auto 1rem"></div>
      <p>加载中...</p>
    </div>

    <!-- 加载出错 -->
    <div v-else-if="loadError" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <p>{{ loadError }}</p>
      <n-button type="primary" size="small" style="margin-top:1rem" @click="loadTeams">重试</n-button>
    </div>

    <!-- 团队详情 -->
    <template v-else-if="currentTeam">
      <div class="card-static team-info">
        <div class="team-meta">
          <div class="team-name">{{ currentTeam.name }}</div>
          <div class="team-desc">{{ currentTeam.description || '暂无描述' }}</div>
        </div>
        <div class="team-actions" v-if="myRole === 'owner' || myRole === 'admin'">
          <n-button size="small" @click="openEditModal">编辑</n-button>
          <n-button size="small" type="error" @click="confirmDisband" v-if="myRole === 'owner'">解散团队</n-button>
        </div>
      </div>

      <!-- 成员列表 -->
      <div class="card-static members-section">
        <div class="members-header">
          <h3>成员列表 ({{ members.length }})</h3>
          <n-button
            v-if="myRole === 'owner' || myRole === 'admin'"
            size="small"
            type="primary"
            @click="showInviteModal = true"
          >邀请成员</n-button>
        </div>
        <n-data-table :columns="memberColumns" :data="members" :bordered="false" size="small" />
      </div>
    </template>

    <div v-else-if="teams.length === 0" class="empty-state">
      <div class="empty-icon">👥</div>
      <p>还没有团队，点击上方「创建团队」开始协作吧</p>
    </div>

    <!-- 创建团队弹窗 -->
    <n-modal v-model:show="showCreateModal" preset="card" title="创建团队" style="width: 420px">
      <n-form :model="createForm" label-placement="left" label-width="80">
        <n-form-item label="团队名称">
          <n-input v-model:value="createForm.name" placeholder="输入团队名称" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="createForm.description" type="textarea" :rows="2" placeholder="可选" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display:flex;justify-content:flex-end;gap:8px">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" :loading="creating" @click="doCreate">创建</n-button>
        </div>
      </template>
    </n-modal>

    <!-- 编辑团队弹窗 -->
    <n-modal v-model:show="showEditModal" preset="card" title="编辑团队" style="width: 420px">
      <n-form :model="editForm" label-placement="left" label-width="80">
        <n-form-item label="团队名称">
          <n-input v-model:value="editForm.name" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="editForm.description" type="textarea" :rows="2" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display:flex;justify-content:flex-end;gap:8px">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" :loading="editing" @click="doEdit">保存</n-button>
        </div>
      </template>
    </n-modal>

    <!-- 邀请成员弹窗 -->
    <n-modal v-model:show="showInviteModal" preset="card" title="邀请成员" style="width: 420px">
      <n-form :model="inviteForm" label-placement="left" label-width="80">
        <n-form-item label="邮箱">
          <n-input v-model:value="inviteForm.email" placeholder="被邀请人的注册邮箱" />
        </n-form-item>
        <n-form-item label="角色">
          <n-select v-model:value="inviteForm.role" :options="roleOptions" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display:flex;justify-content:flex-end;gap:8px">
          <n-button @click="showInviteModal = false">取消</n-button>
          <n-button type="primary" :loading="inviting" @click="doInvite">邀请</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { NTag, NButton, useMessage, useDialog } from 'naive-ui'
import api from '../api/index.js'

const message = useMessage()
const dialog = useDialog()

const teams = ref([])
const currentTeamId = ref(null)
const currentTeam = ref(null)
const members = ref([])
const myRole = ref('member')
const loading = ref(true)
const loadError = ref('')

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showInviteModal = ref(false)
const creating = ref(false)
const editing = ref(false)
const inviting = ref(false)

const createForm = ref({ name: '', description: '' })
const editForm = ref({ name: '', description: '' })
const inviteForm = ref({ email: '', role: 'member' })

const roleOptions = [
  { label: '成员', value: 'member' },
  { label: '管理员', value: 'admin' },
  { label: '观察者', value: 'viewer' },
]

const roleTagType = { owner: 'error', admin: 'warning', member: 'info', viewer: 'default' }
const roleLabel = { owner: '所有者', admin: '管理员', member: '成员', viewer: '观察者' }

const teamOptions = computed(() =>
  teams.value.map(t => ({ label: t.name, value: t.id }))
)

const memberColumns = computed(() => [
  { title: '用户名', key: 'username' },
  { title: '邮箱', key: 'email', ellipsis: { tooltip: true } },
  {
    title: '角色', key: 'role', width: 100,
    render(row) {
      return h(NTag, { size: 'small', type: roleTagType[row.role] || 'default' }, () => roleLabel[row.role] || row.role)
    },
  },
  { title: '加入时间', key: 'joined_at', width: 170, render(row) { return row.joined_at?.replace('T', ' ').slice(0, 19) } },
  {
    title: '操作', key: 'actions', width: 120,
    render(row) {
      if (row.role === 'owner') return null
      const canManage = myRole.value === 'owner' || myRole.value === 'admin'
      if (!canManage) return null
      return h(NButton, { size: 'tiny', type: 'error', onClick: () => removeMember(row.user_id) }, () => '移除')
    },
  },
])

const loadTeams = async () => {
  loading.value = true
  loadError.value = ''
  try {
    teams.value = await api.listTeams()
    if (teams.value.length && !currentTeamId.value) {
      currentTeamId.value = teams.value[0].id
      await loadTeamDetail(currentTeamId.value)
    }
  } catch (e) {
    console.error('loadTeams error:', e)
    loadError.value = e?.response?.data?.detail || e?.message || '加载团队列表失败'
  } finally {
    loading.value = false
  }
}

const loadTeamDetail = async (teamId) => {
  try {
    const detail = await api.getTeam(teamId)
    currentTeam.value = detail
    members.value = detail.members || []
    const me = teams.value.find(t => t.id === teamId)
    myRole.value = me?.my_role || 'member'
  } catch (e) {
    console.error('loadTeamDetail error:', e)
    message.error(e?.response?.data?.detail || '加载团队详情失败')
  }
}

const onTeamChange = (id) => {
  if (id) loadTeamDetail(id)
  else { currentTeam.value = null; members.value = [] }
}

const doCreate = async () => {
  if (!createForm.value.name.trim()) return message.warning('请输入团队名称')
  creating.value = true
  try {
    const team = await api.createTeam(createForm.value)
    message.success('团队创建成功')
    showCreateModal.value = false
    createForm.value = { name: '', description: '' }
    await loadTeams()
    currentTeamId.value = team.id
    await loadTeamDetail(team.id)
  } catch (e) {
    message.error(e?.response?.data?.detail || '创建失败')
  } finally { creating.value = false }
}

const openEditModal = () => {
  editForm.value = { name: currentTeam.value.name, description: currentTeam.value.description }
  showEditModal.value = true
}

const doEdit = async () => {
  editing.value = true
  try {
    await api.updateTeam(currentTeamId.value, editForm.value)
    message.success('已保存')
    showEditModal.value = false
    await loadTeams()
    await loadTeamDetail(currentTeamId.value)
  } catch (e) {
    message.error(e?.response?.data?.detail || '保存失败')
  } finally { editing.value = false }
}

const doInvite = async () => {
  if (!inviteForm.value.email.trim()) return message.warning('请输入邮箱')
  inviting.value = true
  try {
    await api.inviteTeamMember(currentTeamId.value, inviteForm.value)
    message.success('邀请成功')
    showInviteModal.value = false
    inviteForm.value = { email: '', role: 'member' }
    await loadTeamDetail(currentTeamId.value)
  } catch (e) {
    message.error(e?.response?.data?.detail || '邀请失败')
  } finally { inviting.value = false }
}

const removeMember = (userId) => {
  dialog.warning({
    title: '移除成员',
    content: '确定要移除该成员吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await api.removeTeamMember(currentTeamId.value, userId)
        message.success('已移除')
        await loadTeamDetail(currentTeamId.value)
      } catch (e) {
        message.error(e?.response?.data?.detail || '移除失败')
      }
    },
  })
}

const confirmDisband = () => {
  dialog.error({
    title: '解散团队',
    content: `确定要解散「${currentTeam.value.name}」吗？此操作不可恢复。`,
    positiveText: '解散',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await api.deleteTeam(currentTeamId.value)
        message.success('团队已解散')
        currentTeamId.value = null
        currentTeam.value = null
        members.value = []
        await loadTeams()
      } catch (e) {
        message.error(e?.response?.data?.detail || '操作失败')
      }
    },
  })
}

onMounted(loadTeams)
</script>

<style scoped>
.team-view {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.top-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.team-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
}
.team-name { font-size: var(--font-size-lg); font-weight: 600; color: var(--text-primary); }
.team-desc { font-size: var(--font-size-sm); color: var(--text-muted); margin-top: 0.25rem; }
.team-actions { display: flex; gap: 0.5rem; }
.members-section { padding: 1.5rem; }
.members-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1rem; padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-subtle);
}
.members-header h3 { font-size: var(--font-size-lg); font-weight: 600; color: var(--text-primary); }
.empty-state {
  text-align: center;
  padding: 4rem 0;
  color: var(--text-muted);
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
</style>
