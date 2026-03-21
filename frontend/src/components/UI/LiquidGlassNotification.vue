<template>
  <transition name="notification" appear>
    <div v-if="show" class="notification-overlay" @click="closeNotification">
      <div class="notification" :class="[type, { 'has-icon': !!icon }]" @click.stop>
        <div v-if="icon" class="notification-icon">
          {{ icon }}
        </div>
        <div class="notification-content">
          <h4 v-if="title" class="notification-title">{{ title }}</h4>
          <p v-if="message" class="notification-message">{{ message }}</p>
        </div>
        <button @click="closeNotification" class="notification-close">
          ✕
        </button>
      </div>
    </div>
  </transition>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'LiquidGlassNotification',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
    },
    title: {
      type: String,
      default: ''
    },
    message: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      default: ''
    },
    duration: {
      type: Number,
      default: 5000
    },
    closable: {
      type: Boolean,
      default: true
    }
  },
  setup(props, { emit }) {
    let timeoutId = null

    const closeNotification = () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
      emit('close')
    }

    const startTimer = () => {
      if (props.duration > 0) {
        timeoutId = setTimeout(() => {
          closeNotification()
        }, props.duration)
      }
    }

    onMounted(() => {
      if (props.show) {
        startTimer()
      }
    })

    onUnmounted(() => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    })

    return {
      closeNotification
    }
  }
}
</script>

<style scoped>
.notification-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.notification {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-xl);
  -webkit-backdrop-filter: var(--glass-blur-xl);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: var(--glass-shadow-xl);
  max-width: 500px;
  width: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.notification::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.notification.success {
  border-left: 4px solid rgba(16, 185, 129, 0.8);
}

.notification.error {
  border-left: 4px solid rgba(239, 68, 68, 0.8);
}

.notification.warning {
  border-left: 4px solid rgba(245, 158, 11, 0.8);
}

.notification.info {
  border-left: 4px solid rgba(59, 130, 246, 0.8);
}

.notification-icon {
  font-size: 1.5rem;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  flex-shrink: 0;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.notification-content {
  flex: 1;
}

.notification-title {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.notification-message {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.4;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.notification-close {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
  font-size: 0.8rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.notification-close:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: scale(1.1);
}

/* Notification transitions */
.notification-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-enter-from {
  opacity: 0;
}

.notification-leave-to {
  opacity: 0;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@media (max-width: 768px) {
  .notification {
    flex-direction: column;
    text-align: center;
  }
  
  .notification-icon {
    align-self: center;
  }
  
  .notification-close {
    position: absolute;
    top: 1rem;
    right: 1rem;
  }
}
</style>
