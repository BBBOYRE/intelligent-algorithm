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

    <!-- 主页按钮独立 -->
    <router-link to="/" class="home-btn" :class="{ active: $route.path === '/' }">
      <span class="nav-icon">🏠</span>
      <span class="nav-text" v-show="!store.sidebarCollapsed">主页</span>
    </router-link>

    <nav class="sidebar-nav">
      <!-- 文档工具 -->
      <div class="nav-group" v-show="!store.sidebarCollapsed">
        <span class="nav-group-label">文档工具</span>
      </div>
      <router-link v-for="route in docRoutes" :key="route.name" :to="route.path" class="nav-item">
        <span class="nav-icon">{{ route.meta.icon }}</span>
        <span class="nav-text" v-show="!store.sidebarCollapsed">{{ route.meta.title }}</span>
      </router-link>

      <!-- AI & 知识库 -->
      <div class="nav-group" v-show="!store.sidebarCollapsed">
        <span class="nav-group-label">AI & 知识库</span>
      </div>
      <router-link v-for="route in aiRoutes" :key="route.name" :to="route.path" class="nav-item">
        <span class="nav-icon">{{ route.meta.icon }}</span>
        <span class="nav-text" v-show="!store.sidebarCollapsed">{{ route.meta.title }}</span>
      </router-link>

      <!-- 协作 -->
      <div class="nav-group" v-show="!store.sidebarCollapsed">
        <span class="nav-group-label">协作</span>
      </div>
      <router-link v-for="route in collabRoutes" :key="route.name" :to="route.path" class="nav-item">
        <span class="nav-icon">{{ route.meta.icon }}</span>
        <span class="nav-text" v-show="!store.sidebarCollapsed">{{ route.meta.title }}</span>
      </router-link>

      <!-- 个人 -->
      <div class="nav-group" v-show="!store.sidebarCollapsed">
        <span class="nav-group-label">个人</span>
      </div>
      <router-link v-for="route in personalRoutes" :key="route.name" :to="route.path" class="nav-item">
        <span class="nav-icon">{{ route.meta.icon }}</span>
        <span class="nav-text" v-show="!store.sidebarCollapsed">{{ route.meta.title }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer" v-show="!store.sidebarCollapsed">
      <div class="user-info">
        <span class="user-avatar">👤</span>
        <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const store = useAppStore()
const authStore = useAuthStore()

const getRoutesByGroup = (group) => {
  const mainRoute = router.options.routes.find(r => r.path === '/')
  if (!mainRoute || !mainRoute.children) return []
  return mainRoute.children
    .filter(r => r.meta && r.meta.icon && r.meta.group === group)
    .map(r => ({ ...r, path: `/${r.path}` }))
}

const docRoutes = computed(() => getRoutesByGroup('doc'))
const aiRoutes = computed(() => getRoutesByGroup('ai'))
const collabRoutes = computed(() => getRoutesByGroup('collab'))
const personalRoutes = computed(() => getRoutesByGroup('personal'))
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
  width: 0;
  overflow: hidden;
  border-right: none;
}
.sidebar-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
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
.home-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.625rem 1rem;
  margin: 0.5rem 0.75rem 0;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 600;
  text-decoration: none;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}
.home-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-primary);
}
.home-btn.active {
  background: rgba(51, 112, 255, 0.08);
  color: var(--accent-blue);
}
.sidebar-nav {
  flex: 1;
  padding: 0.5rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  overflow-y: auto;
}
.nav-group {
  padding: 0.75rem 1rem 0.25rem;
}
.nav-group-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  white-space: nowrap;
  text-decoration: none;
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
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sidebar-footer {
  padding: 0.75rem 1rem 1.25rem;
  flex-shrink: 0;
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
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    width: var(--sidebar-width) !important;
  }
  .sidebar.drawer-open {
    transform: translateX(0);
    box-shadow: var(--shadow-lg);
  }
  .desktop-only { display: none; }
  .mobile-only { display: flex; }
}
</style>
