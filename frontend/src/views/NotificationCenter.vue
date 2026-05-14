<template>
  <div class="notification-center p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-white flex items-center gap-3">
        <i class="fas fa-bell text-primary"></i>
        {{ t('sidebar.notification_center') }}
      </h1>
      <button v-if="notifications.length > 0" class="btn btn-secondary" @click="clearAll">
        Clear All
      </button>
    </div>

    <!-- Notification List -->
    <div class="grid gap-3">
      <div v-if="loading" class="text-center py-12">
        <div class="spinner"></div>
      </div>
      
      <div v-else-if="notifications.length === 0" class="glass-panel p-12 text-center text-muted">
        <i class="fas fa-bell-slash text-5xl mb-4 opacity-20"></i>
        <p>No new notifications.</p>
      </div>

      <div v-for="notif in notifications" :key="notif.id" 
           class="notif-card glass-panel p-4 flex gap-4"
           :class="{ 'is-read': notif.is_read }">
        <div class="notif-icon-box" :class="'type-' + notif.type.toLowerCase()">
          <i :class="getIcon(notif.type)"></i>
        </div>
        
        <div class="flex-1">
          <div class="flex justify-between items-start">
            <p class="text-white font-medium">{{ notif.message }}</p>
            <span class="text-xs text-muted">{{ timeAgo(notif.created_at) }}</span>
          </div>
          <div class="flex gap-3 mt-2">
            <a v-if="notif.link" class="text-xs text-primary hover:underline cursor-pointer" @click="navigate(notif)">
              View Details
            </a>
            <button v-if="!notif.is_read" class="text-xs text-muted hover:text-white" @click="markRead(notif.id)">
              Mark as Read
            </button>
          </div>
        </div>
        
        <button class="notif-close" @click="deleteNotif(notif.id)">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { apiGet, apiPut, apiDelete, showAlert } from '@/utils/api'

const { t } = useI18n()
const router = useRouter()
const notifications = ref([])
const loading = ref(true)

const fetchNotifications = async () => {
  loading.value = true
  try {
    notifications.value = await apiGet('/notifications')
  } catch (error) {
    console.error('Failed to fetch notifications:', error)
  } finally {
    loading.value = false
  }
}

const markRead = async (id) => {
  try {
    await apiPut(`/notifications/${id}/read`)
    const n = notifications.value.find(notif => notif.id === id)
    if (n) n.is_read = true
  } catch (error) {}
}

const deleteNotif = async (id) => {
  try {
    await apiDelete(`/notifications/${id}`)
    notifications.value = notifications.value.filter(n => n.id !== id)
  } catch (error) {}
}

const getIcon = (type) => {
  switch (type.toUpperCase()) {
    case 'TASK': return 'fas fa-tasks'
    case 'ORDER': return 'fas fa-shopping-bag'
    case 'SYSTEM': return 'fas fa-cog'
    case 'COLLAB': return 'fas fa-users'
    default: return 'fas fa-info-circle'
  }
}

const navigate = (notif) => {
  markRead(notif.id)
  if (notif.link) {
    router.push(notif.link)
  }
}

const timeAgo = (dateStr) => {
  const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000)
  if (seconds < 60) return 'Just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notification-center {
  max-width: 800px;
  margin: 0 auto;
}

.notif-card {
  position: relative;
  transition: all 0.2s;
  border-left: 4px solid #3b82f6;
}

.notif-card.is-read {
  opacity: 0.7;
  border-left-color: transparent;
}

.notif-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.05);
}

.type-task { color: #f59e0b; background: rgba(245, 158, 11, 0.1); }
.type-order { color: #10b981; background: rgba(16, 185, 129, 0.1); }
.type-system { color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
.type-collab { color: #8b5cf6; background: rgba(139, 92, 246, 0.1); }

.notif-close {
  opacity: 0;
  cursor: pointer;
  color: var(--text-muted);
  transition: opacity 0.2s;
}

.notif-card:hover .notif-close {
  opacity: 1;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
