<template>
  <header class="header">
    <div class="header-content">
      <div class="breadcrumb animate-slide-in">
        <span class="route-title">{{ currentRouteTitle }}</span>
      </div>
      <div class="header-actions">
        <n-button quaternary class="inbox-btn" @click="router.push('/inbox')">
          <template #icon>
            <n-icon><mail-outline /></n-icon>
          </template>
          <n-badge :value="unreadCount" :max="99" v-if="unreadCount > 0" />
        </n-button>
        <n-dropdown :options="userMenuOptions" @select="handleUserMenu">
          <n-button quaternary>
            <template #icon>
              <n-icon><person-circle-outline /></n-icon>
            </template>
            {{ authStore.user?.username || '用户' }}
          </n-button>
        </n-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, h, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import { PersonCircleOutline, SettingsOutline, LogOutOutline, MailOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth'
import api from '../api/index.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const unreadCount = ref(0)

const currentRouteTitle = computed(() => route.meta.title || '系统概览')

const renderIcon = (icon) => () => h(NIcon, null, { default: () => h(icon) })

const userMenuOptions = [
  { label: '个人信息', key: 'profile', icon: renderIcon(SettingsOutline) },
  { type: 'divider' },
  { label: '退出登录', key: 'logout', icon: renderIcon(LogOutOutline) },
]

const handleUserMenu = (key) => {
  if (key === 'profile') {
    router.push('/settings')
  } else if (key === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

const pollUnread = async () => {
  try {
    const res = await api.getUnreadCount()
    unreadCount.value = res.count || 0
  } catch {}
}

onMounted(() => {
  pollUnread()
  setInterval(pollUnread, 30000)
})
</script>

<style scoped>
.header {
  height: var(--header-height);
  border-bottom: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  z-index: 90;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  background: rgba(10, 15, 30, 0.85);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 2rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.inbox-btn {
  position: relative;
}

.route-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.route-title::before {
  content: '';
  display: block;
  width: 4px;
  height: 16px;
  background: var(--accent-yellow);
  border-radius: 2px;
}
</style>
