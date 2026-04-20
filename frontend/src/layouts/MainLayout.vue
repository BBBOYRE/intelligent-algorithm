<template>
  <div class="app-container">
    <div class="sidebar-overlay" v-if="appStore.drawerVisible" @click="appStore.toggleDrawer()"></div>
    <AppSidebar />
    <main class="main-content" :style="{ marginLeft: appStore.sidebarCollapsed ? '0' : 'var(--sidebar-width)' }">
      <AppHeader />
      <div class="page-content">
        <router-view />
      </div>
    </main>
    <ToastNotification />
  </div>
</template>

<script setup>
import AppSidebar from '../components/AppSidebar.vue'
import AppHeader from '../components/AppHeader.vue'
import ToastNotification from '../components/ToastNotification.vue'
import { useAppStore } from '../stores/app'

const appStore = useAppStore()
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
  position: relative;
}
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 95; /* just below sidebar which is 100 */
  animation: fadeIn 0.2s ease-out;
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 0;
  min-height: 100vh;
  transition: margin-left var(--transition-normal);
  width: 100%;
}
.page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}
</style>
