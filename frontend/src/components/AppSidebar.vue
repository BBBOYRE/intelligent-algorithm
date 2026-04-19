<template>
  <aside class="sidebar" :class="{ 'collapsed': store.sidebarCollapsed, 'drawer-open': store.drawerVisible }">
    <div class="sidebar-header">
      <div class="logo">
        <span class="logo-icon">📄</span>
        <span class="logo-text" v-show="!store.sidebarCollapsed">文档智能系统</span>
      </div>
      <div class="header-actions">
        <button class="toggle-btn desktop-only" @click="store.toggleSidebar()" title="Toggle Sidebar">
          <svg v-if="!store.sidebarCollapsed" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </button>
        <button class="toggle-btn mobile-only" @click="store.toggleDrawer()" title="Close Drawer">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
    </div>

    <nav class="sidebar-nav stagger-children">
      <router-link v-for="route in navRoutes" :key="route.name" :to="route.path" class="nav-item">
        <span class="nav-icon">{{ route.meta.icon }}</span>
        <span class="nav-text" v-show="!store.sidebarCollapsed">{{ route.meta.title }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer" v-show="!store.sidebarCollapsed">
      <div class="kb-card card-static animate-fade-in">
        <div class="kb-header">
          <span class="kb-title">📊 知识库状态</span>
          <button class="refresh-btn" @click="refreshStats" :disabled="isRefreshing" title="刷新统计">
            <svg :class="{'spinning': isRefreshing}" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
          </button>
        </div>
        <div class="kb-stat">
          <span class="stat-label">已入库分块</span>
          <span class="stat-value">{{ store.kbStats.total_chunks }}</span>
        </div>
        <div class="kb-stat" v-if="store.kbStats.documents">
          <span class="stat-label">文档数量</span>
          <span class="stat-value">{{ store.kbStats.documents.length }}</span>
        </div>
      </div>

      <div class="user-info">
        <span class="user-avatar">👤</span>
        <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const store = useAppStore()
const authStore = useAuthStore()
const isRefreshing = ref(false)

const navRoutes = computed(() => {
  const mainRoute = router.options.routes.find(r => r.path === '/')
  if (!mainRoute || !mainRoute.children) return []
  return mainRoute.children
    .filter(r => r.meta && r.meta.icon)
    .map(r => ({ ...r, path: r.path === '' ? '/' : `/${r.path}` }))
})

const refreshStats = async () => {
  isRefreshing.value = true
  await store.refreshKBStats()
  setTimeout(() => { isRefreshing.value = false }, 500)
}

onMounted(() => {
  store.refreshKBStats()
})
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  transition: width var(--transition-normal), transform var(--transition-normal);
  z-index: 100;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.mobile-only {
  display: none;
}
.sidebar.collapsed {
  width: 80px;
}
.sidebar-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
}
.collapsed .sidebar-header {
  justify-content: center;
  padding: 0;
}
.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.logo-icon {
  font-size: 1.5rem;
}
.logo-text {
  font-weight: 700;
  font-size: 1.125rem;
  color: var(--text-primary);
  white-space: nowrap;
}
.toggle-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}
.toggle-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-primary);
}
.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  overflow-y: auto;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.625rem 1rem;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  white-space: nowrap;
  text-decoration: none;
}
.collapsed .nav-item {
  justify-content: center;
  padding: 0.625rem 0;
}
.nav-item:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-primary);
}
.nav-item.router-link-active {
  background: rgba(51, 112, 255, 0.08);
  color: var(--accent-blue);
  font-weight: 600;
}
.nav-icon {
  font-size: 1.125rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sidebar-footer {
  padding: 0.75rem 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.kb-card {
  padding: 0.75rem;
  background: rgba(51, 112, 255, 0.04);
  border-color: var(--border-subtle);
}
.kb-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.kb-title {
  font-weight: 600;
  font-size: var(--font-size-xs);
  color: var(--accent-blue);
}
.refresh-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}
.refresh-btn:hover {
  color: var(--accent-blue);
  background: rgba(51, 112, 255, 0.08);
}
.spinning {
  animation: spin 1s linear infinite;
}
.kb-stat {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.2rem 0;
}
.stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}
.stat-value {
  font-family: monospace;
  font-size: var(--font-size-md);
  font-weight: 700;
  color: var(--accent-blue);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem;
  background: rgba(0, 0, 0, 0.02);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}
.user-avatar {
  font-size: 1.25rem;
}
.user-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar {
  transform: translateX(-100%);
  width: var(--sidebar-width) !important; /* Ignore collapsed state in drawer mode */
}
.sidebar.drawer-open {
  transform: translateX(0);
  box-shadow: var(--shadow-lg);
}
.desktop-only {
  display: none;
}
.mobile-only {
  display: flex;
}
</style>
