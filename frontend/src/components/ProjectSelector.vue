<template>
  <div class="project-selector">
    <n-dropdown
      trigger="click"
      :options="dropdownOptions"
      @select="handleSelect"
      placement="bottom-start"
      class="project-dropdown"
    >
      <n-button class="project-btn" quaternary>
        <template #icon>
          <n-icon><FolderOpenOutline /></n-icon>
        </template>
        <span class="project-name">{{ currentProjectName }}</span>
        <n-icon class="chevron-icon"><ChevronDownOutline /></n-icon>
      </n-button>
    </n-dropdown>

    <!-- Create Project Modal -->
    <n-modal v-model:show="showCreateModal" preset="card" title="新建项目" style="width: 500px">
      <n-form ref="formRef" :model="form" :rules="rules">
        <n-form-item label="项目名称" path="name">
          <n-input v-model:value="form.name" placeholder="输入项目名称" />
        </n-form-item>
        <n-form-item label="项目描述" path="description">
          <n-input v-model:value="form.description" type="textarea" placeholder="选填，简短描述项目用途" />
        </n-form-item>
        <n-form-item label="归属团队 (可选)" path="team_id">
          <n-select v-model:value="form.team_id" :options="teamOptions" placeholder="选择归属团队（留空为个人项目）" clearable />
        </n-form-item>
        <div style="display: flex; justify-content: flex-end; gap: 8px;">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" :loading="creating" @click="handleCreate">创建</n-button>
        </div>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, h } from 'vue'
import { NIcon, useMessage } from 'naive-ui'
import { FolderOpenOutline, ChevronDownOutline, AddOutline, PersonOutline, PeopleOutline } from '@vicons/ionicons5'
import { useAppStore } from '../stores/app'
import api from '../api/index'

const message = useMessage()
const appStore = useAppStore()

const showCreateModal = ref(false)
const creating = ref(false)
const formRef = ref(null)
const form = ref({ name: '', description: '', team_id: null })

const rules = {
  name: { required: true, message: '请输入项目名称', trigger: 'blur' }
}

const renderIcon = (icon) => () => h(NIcon, null, { default: () => h(icon) })

const currentProjectName = computed(() => {
  const kb = appStore.knowledgeBases.find(k => k.id === appStore.currentKbId)
  return kb ? kb.name : '选择项目'
})

const dropdownOptions = computed(() => {
  const kbs = appStore.knowledgeBases || []
  
  // Group by personal and teams
  const personal = kbs.filter(k => !k.team_id)
  const teamsMap = new Map()
  
  kbs.filter(k => k.team_id).forEach(k => {
    if (!teamsMap.has(k.team_id)) {
      teamsMap.set(k.team_id, {
        type: 'group',
        label: `团队: ${k.team_name || '未命名团队'}`,
        key: `team-group-${k.team_id}`,
        children: []
      })
    }
    teamsMap.get(k.team_id).children.push({
      label: k.name,
      key: k.id,
      icon: renderIcon(PeopleOutline)
    })
  })

  const options = []
  
  if (personal.length > 0) {
    options.push({
      type: 'group',
      label: '个人项目',
      key: 'personal-group',
      children: personal.map(k => ({
        label: k.name,
        key: k.id,
        icon: renderIcon(PersonOutline)
      }))
    })
  }
  
  options.push(...Array.from(teamsMap.values()))
  
  options.push({ type: 'divider', key: 'd1' })
  options.push({
    label: '新建项目...',
    key: 'create_new',
    icon: renderIcon(AddOutline)
  })
  
  return options
})

const teamOptions = ref([])

const fetchTeams = async () => {
  try {
    const res = await api.listTeams()
    const teamsList = Array.isArray(res) ? res : (res.teams || [])
    teamOptions.value = teamsList.map(t => ({ label: t.name, value: t.id }))
  } catch (e) {
    console.error(e)
  }
}

const handleSelect = (key) => {
  if (key === 'create_new') {
    form.value = { name: '', description: '', team_id: null }
    fetchTeams()
    showCreateModal.value = true
  } else {
    appStore.switchKb(key)
    message.success(`已切换至: ${currentProjectName.value}`)
  }
}

const handleCreate = () => {
  formRef.value?.validate(async (errors) => {
    if (errors) return
    creating.value = true
    try {
      await api.createKB(form.value)
      message.success('创建成功')
      showCreateModal.value = false
      await appStore.fetchKnowledgeBases()
      // Optional: switch to the newly created one
      // But we don't have its ID returned directly easily if list changes concurrently,
      // it's fine to just stay or let user click. Actually API returns ID.
    } catch (e) {
      message.error('创建失败: ' + (e.response?.data?.detail || e.message))
    } finally {
      creating.value = false
    }
  })
}

onMounted(() => {
  appStore.fetchKnowledgeBases()
})
</script>

<style scoped>
.project-selector {
  display: inline-flex;
}
.project-btn {
  font-size: var(--font-size-md);
  font-weight: 600;
  padding: 0 12px;
  border-radius: var(--radius-md);
  height: 40px;
}
.project-name {
  margin: 0 8px;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chevron-icon {
  font-size: 14px;
  color: var(--text-muted);
}
</style>
