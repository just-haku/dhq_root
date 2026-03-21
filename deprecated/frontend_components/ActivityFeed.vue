<template>
  <div class="activity-feed">
    <div class="feed-header">
      <h3>🔥 Live Activity Feed</h3>
      <div class="feed-controls">
        <select v-model="filterType" @change="loadActivities" class="filter-select">
          <option value="">All Activities</option>
          <option value="task">Tasks</option>
          <option value="file">Files</option>
          <option value="game">Games</option>
        </select>
        <button @click="loadActivities" class="refresh-btn">
          🔄 Refresh
        </button>
      </div>
    </div>
    
    <div class="feed-container">
      <div 
        v-for="activity in activities" 
        :key="activity.id"
        class="activity-item"
        :class="activity.type"
      >
        <div class="activity-icon">
          {{ getActivityIcon(activity.type) }}
        </div>
        <div class="activity-content">
          <div class="activity-header">
            <span class="activity-user">{{ activity.user.display_name || activity.user.username }}</span>
            <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
          </div>
          <div class="activity-title">{{ activity.title }}</div>
          <div class="activity-description">{{ activity.description }}</div>
          
          <!-- Task-specific metadata -->
          <div v-if="activity.type === 'task'" class="activity-metadata">
            <span class="metadata-item priority" :class="activity.metadata.priority.toLowerCase()">
              {{ activity.metadata.priority }}
            </span>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: activity.metadata.progress + '%' }"
              ></div>
            </div>
            <span class="progress-text">{{ activity.metadata.progress }}%</span>
          </div>
          
          <!-- File-specific metadata -->
          <div v-if="activity.type === 'file'" class="activity-metadata">
            <span class="metadata-item">
              📄 {{ formatFileSize(activity.metadata.file_size) }}
            </span>
            <span class="metadata-item">
              🔒 {{ activity.metadata.permission }}
            </span>
          </div>
          
          <!-- Game-specific metadata -->
          <div v-if="activity.type === 'game'" class="activity-metadata">
            <span class="metadata-item">
              🎮 {{ activity.metadata.game_type }}
            </span>
            <span class="metadata-item">
              ⚡ {{ activity.metadata.difficulty }}
            </span>
            <span class="metadata-item">
              ⏱️ {{ formatDuration(activity.metadata.duration) }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Loading state -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading activities...</p>
      </div>
      
      <!-- Empty state -->
      <div v-if="!loading && activities.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p>No recent activities</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiGet } from '../../utils/api.js'

export default {
  name: 'ActivityFeed',
  setup() {
    const activities = ref([])
    const loading = ref(false)
    const filterType = ref('')
    let refreshInterval = null
    
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token')
      return token ? { 'Authorization': `Bearer ${token}` } : {}
    }
    
    const loadActivities = async () => {
      loading.value = true
      
      try {
        const params = new URLSearchParams()
        if (filterType.value) {
          params.append('type', filterType.value)
        }
        
        const response = await apiGet(`/activity/feed?limit=20&${params}`)
        
        if (response.ok) {
          const data = await response.json()
          activities.value = data
        }
      } catch (error) {
        console.error('Error loading activities:', error)
      } finally {
        loading.value = false
      }
    }
    
    const getActivityIcon = (type) => {
      const icons = {
        'task': '✅',
        'file': '📄',
        'game': '🎮',
        'user': '👤',
        'project': '📋'
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
    
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const formatDuration = (seconds) => {
      if (!seconds) return '0s'
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      if (hours > 0) {
        return `${hours}h ${minutes}m`
      } else if (minutes > 0) {
        return `${minutes}m ${secs}s`
      } else {
        return `${secs}s`
      }
    }
    
    onMounted(() => {
      loadActivities()
      // Refresh every 30 seconds
      refreshInterval = setInterval(loadActivities, 30000)
    })
    
    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    })
    
    return {
      activities,
      loading,
      filterType,
      loadActivities,
      getActivityIcon,
      formatTime,
      formatFileSize,
      formatDuration
    }
  }
}
</script>

<style scoped>
.activity-feed {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.feed-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.feed-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.feed-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-select {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  padding: 0.5rem 1rem;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.refresh-btn {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.refresh-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.refresh-btn:hover::before {
  left: 100%;
}

.refresh-btn:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-1px);
}

.feed-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.activity-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.activity-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-xl);
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.activity-item.task {
  border-left: 4px solid rgba(59, 130, 246, 0.6);
}

.activity-item.file {
  border-left: 4px solid rgba(16, 185, 129, 0.6);
}

.activity-item.game {
  border-left: 4px solid rgba(236, 72, 153, 0.6);
}

.activity-icon {
  font-size: 1.5rem;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--glass-shadow-md);
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.activity-user {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.activity-time {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.activity-message {
  color: var(--text-primary);
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.activity-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.activity-type {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
}

.activity-type.task {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.activity-type.file {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.activity-type.game {
  background: rgba(236, 72, 153, 0.2);
  color: #ec4899;
}

.priority {
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  font-size: 0.75rem;
}

.priority.low {
  background: rgba(107, 114, 128, 0.2);
  color: #6b7280;
}

.priority.medium {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.priority.high {
  background: rgba(6, 182, 212, 0.2);
  color: #06b6d4;
}

.priority.urgent {
  background: rgba(236, 72, 153, 0.2);
  color: #ec4899;
}

.progress-bar {
  width: 60px;
  height: 6px;
  background: var(--glass-bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.8), rgba(16, 185, 129, 0.8));
  transition: width 0.3s ease;
  border-radius: 2px;
  box-shadow: 0 0 6px rgba(59, 130, 246, 0.3);
}

.progress-text {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.loading-state::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
  margin: 0 auto 1rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Custom scrollbar for feed container */
.feed-container::-webkit-scrollbar {
  width: 6px;
}

.feed-container::-webkit-scrollbar-track {
  background: var(--bg-tertiary);
  border-radius: 3px;
}

.feed-container::-webkit-scrollbar-thumb {
  background: var(--text-tertiary);
  border-radius: 3px;
}

.feed-container::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>
