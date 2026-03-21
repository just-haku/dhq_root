<template>
  <div class="notification-center">
    <!-- Notification Button -->
    <button @click="toggleNotifications" class="notification-btn" :class="{ 'has-notifications': unreadCount > 0 }">
      <span class="notification-icon">🔔</span>
      <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
    </button>
    
    <!-- Notification Panel -->
    <div v-if="showNotifications" class="notification-panel" :class="{ 'slide-in': showNotifications }">
      <div class="notification-header">
        <h4>🔔 Notifications</h4>
        <div class="notification-controls">
          <button @click="markAllAsRead" class="mark-all-btn" :disabled="unreadCount === 0">
            Mark all as read
          </button>
          <button @click="clearAllNotifications" class="clear-btn">
            Clear all
          </button>
        </div>
      </div>
      
      <div class="notification-list">
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="notification-item"
          :class="{ 'unread': !notification.read, [notification.type]: true }"
          @click="markAsRead(notification)"
        >
          <div class="notification-icon">
            {{ getNotificationIcon(notification.type) }}
          </div>
          <div class="notification-content">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
          </div>
          <button @click.stop="removeNotification(notification)" class="remove-btn">
            ✕
          </button>
        </div>
        
        <!-- Empty state -->
        <div v-if="notifications.length === 0" class="empty-notifications">
          <div class="empty-icon">📭</div>
          <p>No notifications</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'NotificationCenter',
  setup() {
    const showNotifications = ref(false)
    const notifications = ref([])
    const unreadCount = ref(0)
    let notificationInterval = null
    
    // Notification types and their icons
    const getNotificationIcon = (type) => {
      const icons = {
        'task': '✅',
        'file': '📄',
        'message': '💬',
        'achievement': '🏆',
        'kpi': '💎',
        'system': '⚙️',
        'warning': '⚠️',
        'error': '❌',
        'success': '✨'
      }
      return icons[type] || '📌'
    }
    
    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) { // Less than 1 minute
        return 'Just now'
      } else if (diff < 3600000) { // Less than 1 hour
        return `${Math.floor(diff / 60000)}m ago`
      } else if (diff < 86400000) { // Less than 1 day
        return `${Math.floor(diff / 3600000)}h ago`
      } else {
        return date.toLocaleDateString()
      }
    }
    
    const addNotification = (notification) => {
      const newNotification = {
        id: Date.now() + Math.random(),
        ...notification,
        read: false,
        timestamp: new Date()
      }
      
      notifications.value.unshift(newNotification)
      updateUnreadCount()
      
      // Auto-remove after 10 seconds for non-important notifications
      if (notification.type !== 'error' && notification.type !== 'warning') {
        setTimeout(() => {
          removeNotification(newNotification)
        }, 10000)
      }
    }
    
    const markAsRead = (notification) => {
      if (!notification.read) {
        notification.read = true
        updateUnreadCount()
      }
    }
    
    const markAllAsRead = () => {
      notifications.value.forEach(notification => {
        notification.read = true
      })
      updateUnreadCount()
    }
    
    const removeNotification = (notification) => {
      const index = notifications.value.findIndex(n => n.id === notification.id)
      if (index > -1) {
        notifications.value.splice(index, 1)
        updateUnreadCount()
      }
    }
    
    const clearAllNotifications = () => {
      notifications.value = []
      updateUnreadCount()
    }
    
    const updateUnreadCount = () => {
      unreadCount.value = notifications.value.filter(n => !n.read).length
    }
    
    const toggleNotifications = () => {
      showNotifications.value = !showNotifications.value
      if (showNotifications.value) {
        markAllAsRead()
      }
    }
    
    // Simulate real-time notifications
    const simulateNotifications = () => {
      const types = ['task', 'file', 'message', 'achievement', 'kpi']
      const messages = [
        'New task assigned to you',
        'File uploaded successfully',
        'New message in General Chat',
        'Achievement unlocked!',
        'KPI points earned',
        'Project milestone reached',
        'System update available'
      ]
      
      // Random notification (10% chance every 30 seconds)
      if (Math.random() < 0.1) {
        const type = types[Math.floor(Math.random() * types.length)]
        const message = messages[Math.floor(Math.random() * messages.length)]
        
        addNotification({
          type: type,
          title: type.charAt(0).toUpperCase() + type.slice(1),
          message: message
        })
      }
    }
    
    // Listen for custom events
    const handleCustomNotification = (event) => {
      addNotification(event.detail)
    }
    
    onMounted(() => {
      // Add some initial notifications
      addNotification({
        type: 'success',
        title: 'Welcome back!',
        message: 'Your DHQ dashboard is ready'
      })
      
      // Set up notification simulation
      notificationInterval = setInterval(simulateNotifications, 30000)
      
      // Listen for custom notification events
      window.addEventListener('notification', handleCustomNotification)
    })
    
    onUnmounted(() => {
      if (notificationInterval) {
        clearInterval(notificationInterval)
      }
      window.removeEventListener('notification', handleCustomNotification)
    })
    
    // Expose addNotification for global access
    window.addNotification = addNotification
    
    return {
      showNotifications,
      notifications,
      unreadCount,
      getNotificationIcon,
      formatTime,
      markAsRead,
      markAllAsRead,
      removeNotification,
      clearAllNotifications,
      toggleNotifications
    }
  }
}
</script>

<style scoped>
.notification-center {
  position: relative;
  z-index: 1000;
}

.notification-btn {
  position: relative;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-btn:hover {
  background: var(--bg-primary);
  transform: scale(1.05);
}

.notification-btn.has-notifications {
  background: var(--primary-gradient);
  border-color: transparent;
}

.notification-icon {
  font-size: 1.25rem;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
  animation: pulse 2s infinite;
}

.notification-panel {
  position: absolute;
  top: 100%;
  right: 0;
  width: 400px;
  max-height: 500px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  transform-origin: top right;
  transition: all 0.3s ease;
}

.notification-panel.slide-in {
  animation: slideIn 0.3s ease-out;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

.notification-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
}

.notification-controls {
  display: flex;
  gap: 0.5rem;
}

.mark-all-btn,
.clear-btn {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 0.25rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mark-all-btn:hover:not(:disabled) {
  background: var(--primary-gradient);
  color: white;
  border-color: transparent;
}

.clear-btn:hover {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}

.mark-all-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.notification-item:hover {
  background: var(--bg-tertiary);
}

.notification-item.unread {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.05), transparent);
  border-left: 3px solid #3b82f6;
}

.notification-item.unread::before {
  content: '';
  position: absolute;
  top: 1rem;
  left: 0.5rem;
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
}

.notification-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 50%;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.notification-message {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.notification-time {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.remove-btn {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: var(--bg-tertiary);
  color: #ef4444;
}

.empty-notifications {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Notification type colors */
.notification-item.task {
  border-left-color: #10b981;
}

.notification-item.file {
  border-left-color: #3b82f6;
}

.notification-item.message {
  border-left-color: #8b5cf6;
}

.notification-item.achievement {
  border-left-color: #f59e0b;
}

.notification-item.kpi {
  border-left-color: #ec4899;
}

.notification-item.system {
  border-left-color: #6b7280;
}

.notification-item.warning {
  border-left-color: #f59e0b;
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.05), transparent);
}

.notification-item.error {
  border-left-color: #ef4444;
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.05), transparent);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Custom scrollbar */
.notification-list::-webkit-scrollbar {
  width: 6px;
}

.notification-list::-webkit-scrollbar-track {
  background: var(--bg-tertiary);
}

.notification-list::-webkit-scrollbar-thumb {
  background: var(--text-tertiary);
  border-radius: 3px;
}

.notification-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>
