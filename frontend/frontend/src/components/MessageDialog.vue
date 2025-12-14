<template>
  <Teleport to="body">
    <div v-if="visible" class="message-overlay" @click="handleOverlayClick">
      <div class="message-dialog" :class="[`message-${type}`]" @click.stop>
        <div class="message-icon">
          <span v-if="type === 'success'">✓</span>
          <span v-else-if="type === 'error'">✕</span>
          <span v-else-if="type === 'warning'">⚠</span>
          <span v-else>ℹ</span>
        </div>
        <div class="message-content">
          <h4 v-if="title" class="message-title">{{ title }}</h4>
          <p class="message-text">{{ message }}</p>
        </div>
        <button v-if="showClose" @click="close" class="message-close">×</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

interface Props {
  type?: 'success' | 'error' | 'warning' | 'info'
  message: string
  title?: string
  duration?: number
  showClose?: boolean
  closeOnOverlay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  duration: 3000,
  showClose: true,
  closeOnOverlay: true
})

const emit = defineEmits<{
  close: []
}>()

const visible = ref(false)
let timer: number | null = null

const close = () => {
  visible.value = false
  if (timer) {
    clearTimeout(timer)
    timer = null
  }
  emit('close')
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    close()
  }
}

const startTimer = () => {
  if (props.duration > 0) {
    timer = window.setTimeout(() => {
      close()
    }, props.duration)
  }
}

watch(visible, (newVal) => {
  if (newVal) {
    startTimer()
  } else if (timer) {
    clearTimeout(timer)
    timer = null
  }
})

onMounted(() => {
  visible.value = true
})

onUnmounted(() => {
  if (timer) {
    clearTimeout(timer)
  }
})
</script>

<style scoped>
.message-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
  animation: fadeIn 0.2s ease-out;
}

.message-dialog {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
  animation: slideIn 0.3s ease-out;
  border: 1px solid #2a2a2a;
}

.message-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: white;
}

.message-success .message-icon {
  background-color: #10b981;
}

.message-error .message-icon {
  background-color: #ef4444;
}

.message-warning .message-icon {
  background-color: #f59e0b;
}

.message-info .message-icon {
  background-color: #3b82f6;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-title {
  margin: 0 0 8px 0;
  color: #e0e0e0;
  font-size: 16px;
  font-weight: 600;
}

.message-text {
  margin: 0;
  color: #b0b0b0;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: #888;
  font-size: 28px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.message-close:hover {
  background-color: #2a2a2a;
  color: #e0e0e0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .message-dialog {
    padding: 20px;
    max-width: 90%;
  }

  .message-title {
    font-size: 15px;
  }

  .message-text {
    font-size: 13px;
  }
}
</style>
