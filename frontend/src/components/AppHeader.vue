<template>
  <header class="header">
    <div class="header-content">
      <div class="breadcrumb animate-slide-in">
        <span class="route-title">{{ currentRouteTitle }}</span>
      </div>
      <div class="header-actions">
        <!-- Add any global header actions here if needed -->
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const currentRouteTitle = computed(() => {
  return route.meta.title || '系统概览'
})
</script>

<style scoped>
.header {
  height: var(--header-height);
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  z-index: 90;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  background: rgba(10, 14, 26, 0.8);
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
  background: var(--gradient-primary);
  border-radius: 2px;
}
</style>
