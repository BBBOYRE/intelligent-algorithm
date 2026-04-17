<template>
  <div class="app-container">
    <AppSidebar />
    <main class="main-content">
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
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: var(--sidebar-width);
  min-height: 100vh;
}
.page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}
</style>
