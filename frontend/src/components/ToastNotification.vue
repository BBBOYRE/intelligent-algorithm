<template>
  <div class="toast-container">
    <transition-group name="toast-list">
      <div v-for="toast in toasts" :key="toast.id" class="toast" :class="'toast-' + toast.type">
        <span class="icon" v-if="toast.type === 'success'">✅</span>
        <span class="icon" v-else-if="toast.type === 'error'">❌</span>
        <span class="icon" v-else>ℹ️</span>
        <span class="message">{{ toast.message }}</span>
        <button class="close-btn" @click="removeToast(toast.id)">×</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast'

const { toasts, removeToast } = useToast()
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 10000;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  color: white;
  pointer-events: auto;
  min-width: 300px;
  max-width: 450px;
}

.toast-success { background: var(--accent-emerald); }
.toast-error { background: var(--accent-rose); }
.toast-info { background: var(--accent-blue); }

.icon {
  font-size: 1.25rem;
}

.message {
  flex: 1;
  font-weight: 500;
  font-size: var(--font-size-sm);
  line-height: 1.4;
}

.close-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color var(--transition-fast);
}
.close-btn:hover {
  color: white;
}

/* Animations */
.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.3s ease;
}
.toast-list-enter-from {
  opacity: 0;
  transform: translateX(50px);
}
.toast-list-leave-to {
  opacity: 0;
  transform: translateX(50px) scale(0.9);
}
</style>
