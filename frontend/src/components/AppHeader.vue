<template>
  <header class="header">
    <div class="header-content">
      <div class="breadcrumb animate-slide-in">
        <span class="route-title">{{ currentRouteTitle }}</span>
      </div>
      <div class="header-actions">
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
import { computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import { PersonCircleOutline, SettingsOutline, LogOutOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const currentRouteTitle = computed(() => route.meta.title || '系统概览')

const renderIcon = (icon) => () => h(NIcon, null, { default: () => h(icon) })

const userMenuOptions = [
  { label: '个人信息', key: 'profile', icon: renderIcon(SettingsOutline) },
  { type: 'divider' },
  { label: '退出登录', key: 'logout', icon: renderIcon(LogOutOutline) },
]

const handleUserMenu = (key) => {
  if (key === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
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
