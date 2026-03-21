<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>Task Manager</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>Manage system tasks and background jobs</p>
    
</div>

    <div class="page-actions">

      <button class="btn btn-primary" @click="createTask">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M12 8 L12 16 M8 12 L16 12" stroke="currentColor" stroke-width="2"/>
        </svg>
        New Task
      </button>
      <button class="btn btn-secondary" @click="refreshTasks">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M12 6 L12 12 L16 16" stroke="currentColor" stroke-width="2"/>
        </svg>
        Refresh
      </button>
    
</div>

    <div class="tasks-content">
      <div class="tasks-stats">
        <div class="stat-card">
          <div class="stat-icon running">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <polygon points="10,8 16,12 10,16" fill="currentColor"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ runningTasks }}</div>
            <div class="stat-label">Running</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon completed">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M8 12 L11 15 L16 9" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ completedTasks }}</div>
            <div class="stat-label">Completed</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon failed">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M15 9 L9 15 M9 9 L15 15" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ failedTasks }}</div>
            <div class="stat-label">Failed</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon pending">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="12" cy="12" r="3" fill="currentColor"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ pendingTasks }}</div>
            <div class="stat-label">Pending</div>
          </div>
        </div>
      </div>

      <div class="tasks-filters">
        <div class="filter-group">
          <label>Status:</label>
          <select v-model="selectedStatus" class="filter-select">
            <option value="all">All Tasks</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="pending">Pending</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Priority:</label>
          <select v-model="selectedPriority" class="filter-select">
            <option value="all">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      <div class="tasks-grid">
        <div 
          v-for="task in filteredTasks" 
          :key="task.id"
          class="task-card"
          :class="task.status"
        >
          <div class="task-header">
            <div class="task-info">
              <h3>{{ task.name }}</h3>
              <span class="task-id">#{{ task.id }}</span>
            </div>
            <div class="task-status" :class="task.status">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <!-- Running -->
                <circle v-if="task.status === 'running'" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <polygon v-if="task.status === 'running'" points="10,8 16,12 10,16" fill="currentColor"/>
                
                <!-- Completed -->
                <circle v-if="task.status === 'completed'" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <path v-if="task.status === 'completed'" d="M8 12 L11 15 L16 9" stroke="currentColor" stroke-width="2" fill="none"/>
                
                <!-- Failed -->
                <circle v-if="task.status === 'failed'" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <path v-if="task.status === 'failed'" d="M15 9 L9 15 M9 9 L15 15" stroke="currentColor" stroke-width="2" fill="none"/>
                
                <!-- Pending -->
                <circle v-if="task.status === 'pending'" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle v-if="task.status === 'pending'" cx="12" cy="12" r="3" fill="currentColor"/>
              </svg>
              {{ task.status }}
            </div>
          </div>
          
          <div class="task-description">{{ task.description }}</div>
          
          <div class="task-meta">
            <div class="meta-item">
              <span class="meta-label">Priority:</span>
              <span class="priority-badge" :class="task.priority">{{ task.priority }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Progress:</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ task.progress }}%</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Created:</span>
              <span class="meta-value">{{ formatDate(task.created) }}</span>
            </div>
          </div>
          
          <div class="task-actions">
            <button class="btn btn-sm btn-outline" @click="viewTask(task)">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
              </svg>
              View
            </button>
            <button 
              class="btn btn-sm btn-outline" 
              @click="pauseTask(task)"
              v-if="task.status === 'running'"
            >
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="4" width="4" height="16" fill="currentColor"/>
                <rect x="14" y="4" width="4" height="16" fill="currentColor"/>
              </svg>
              Pause
            </button>
            <button 
              class="btn btn-sm btn-outline" 
              @click="resumeTask(task)"
              v-if="task.status === 'failed'"
            >
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5,4 19,12 5,20" fill="currentColor"/>
              </svg>
              Retry
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const selectedStatus = ref('all')
const selectedPriority = ref('all')

const tasks = ref([
  {
    id: 1001,
    name: 'Database Backup',
    description: 'Scheduled daily backup of production database',
    status: 'running',
    priority: 'high',
    progress: 65,
    created: new Date('2024-01-16T10:00:00')
  },
  {
    id: 1002,
    name: 'Email Campaign',
    description: 'Send promotional emails to subscribed users',
    status: 'completed',
    priority: 'medium',
    progress: 100,
    created: new Date('2024-01-15T14:30:00')
  },
  {
    id: 1003,
    name: 'Data Cleanup',
    description: 'Remove expired user sessions and cache',
    status: 'failed',
    priority: 'low',
    progress: 25,
    created: new Date('2024-01-16T09:15:00')
  },
  {
    id: 1004,
    name: 'Report Generation',
    description: 'Generate monthly analytics report',
    status: 'pending',
    priority: 'medium',
    progress: 0,
    created: new Date('2024-01-16T16:45:00')
  }
])

const runningTasks = computed(() => tasks.value.filter(t => t.status === 'running').length)
const completedTasks = computed(() => tasks.value.filter(t => t.status === 'completed').length)
const failedTasks = computed(() => tasks.value.filter(t => t.status === 'failed').length)
const pendingTasks = computed(() => tasks.value.filter(t => t.status === 'pending').length)

const filteredTasks = computed(() => {
  let filtered = tasks.value

  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(task => task.status === selectedStatus.value)
  }

  if (selectedPriority.value !== 'all') {
    filtered = filtered.filter(task => task.priority === selectedPriority.value)
  }

  return filtered
})

const createTask = () => {
  console.log('Creating new task...')
}

const refreshTasks = () => {
  console.log('Refreshing tasks...')
}

const viewTask = (task) => {
  console.log('Viewing task:', task.id)
}

const pauseTask = (task) => {
  task.status = 'pending'
  console.log('Paused task:', task.id)
}

const resumeTask = (task) => {
  task.status = 'running'
  console.log('Resumed task:', task.id)
}

const formatDate = (date) => {
  return date.toLocaleString()
}

onMounted(() => {
  console.log('Admin Tasks component mounted')
})
</script>

<style scoped>
.tasks-content {
  max-width: 1200px;
  margin: 0 auto;
}

.tasks-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-icon.running {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.stat-icon.completed {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.stat-icon.failed {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.stat-icon.pending {
  background: rgba(156, 163, 175, 0.2);
  color: #9ca3af;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.tasks-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #f1f5f9;
  font-size: 0.875rem;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.task-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.task-card:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.task-card.running {
  border-left: 4px solid #10b981;
}

.task-card.completed {
  border-left: 4px solid #3b82f6;
}

.task-card.failed {
  border-left: 4px solid #ef4444;
}

.task-card.pending {
  border-left: 4px solid #9ca3af;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.task-info h3 {
  margin: 0 0 0.25rem 0;
  color: #f1f5f9;
  font-size: 1.125rem;
  font-weight: 600;
}

.task-id {
  color: #94a3b8;
  font-size: 0.75rem;
  font-family: monospace;
}

.task-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.task-status.running {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.task-status.completed {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.task-status.failed {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.task-status.pending {
  background: rgba(156, 163, 175, 0.2);
  color: #9ca3af;
}

.task-description {
  color: #cbd5e1;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.meta-label {
  color: #94a3b8;
  font-size: 0.75rem;
  min-width: 70px;
}

.priority-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-badge.high {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.priority-badge.medium {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.priority-badge.low {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  max-width: 100px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #3b82f6);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: #94a3b8;
  min-width: 35px;
}

.meta-value {
  color: #f1f5f9;
  font-size: 0.75rem;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
}

.btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-sm {
  padding: 0.375rem 0.5rem;
  font-size: 0.625rem;
}

.icon {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 768px) {
  .tasks-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tasks-filters {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-select {
    flex: 1;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<style scoped>
.legacy-page-container {
  padding: 1rem;
}
.page-title { margin-bottom: 0.5rem; }
.page-subtitle { color: var(--text-secondary); margin-bottom: 1rem; }
.page-actions { margin-bottom: 1.5rem; }
</style>
