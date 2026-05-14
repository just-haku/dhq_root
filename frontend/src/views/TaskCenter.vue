<template>
  <div class="task-center p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-white flex items-center gap-3">
        <i class="fas fa-tasks text-primary"></i>
        {{ t('sidebar.task_center') }}
      </h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="fas fa-plus mr-2"></i> Create Task
      </button>
    </div>

    <!-- Filters -->
    <div class="flex gap-4 mb-6">
      <button 
        v-for="status in ['ALL', 'PENDING', 'IN_PROGRESS', 'COMPLETED']" 
        :key="status"
        class="filter-tab"
        :class="{ active: currentFilter === status }"
        @click="currentFilter = status"
      >
        {{ status }}
      </button>
    </div>

    <!-- Task List -->
    <div class="grid gap-4">
      <div v-if="loading" class="text-center py-12">
        <div class="spinner"></div>
      </div>
      
      <div v-else-if="filteredTasks.length === 0" class="glass-panel p-12 text-center text-muted">
        <i class="fas fa-clipboard-list text-5xl mb-4 opacity-20"></i>
        <p>No tasks found for your selection.</p>
      </div>

      <div v-for="task in filteredTasks" :key="task.id" class="task-card glass-panel p-4 flex justify-between items-center">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-1">
            <span class="priority-indicator" :class="'priority-' + task.priority.toLowerCase()"></span>
            <h3 class="font-bold text-lg text-white">{{ task.title }}</h3>
            <span class="status-badge" :class="'status-' + task.status.toLowerCase()">{{ task.status }}</span>
          </div>
          <p class="text-muted text-sm line-clamp-2">{{ task.description }}</p>
          <div class="flex gap-4 mt-3 text-xs text-muted">
            <span><i class="fas fa-user-edit mr-1"></i> From: {{ task.creator }}</span>
            <span><i class="fas fa-user-tag mr-1"></i> To: {{ task.assignee || 'Self' }}</span>
            <span v-if="task.due_date"><i class="fas fa-calendar-alt mr-1"></i> Due: {{ formatDate(task.due_date) }}</span>
          </div>
        </div>
        
        <div class="flex gap-2">
          <button v-if="task.status !== 'COMPLETED'" class="btn-icon text-success" @click="updateStatus(task.id, 'COMPLETED')" title="Mark as Completed">
            <i class="fas fa-check"></i>
          </button>
          <button v-if="task.status === 'PENDING'" class="btn-icon text-primary" @click="updateStatus(task.id, 'IN_PROGRESS')" title="Start Task">
            <i class="fas fa-play"></i>
          </button>
          <button class="btn-icon text-danger" @click="deleteTask(task.id)" title="Delete Task">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Create Task Modal (Simple Placeholder) -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content glass-panel p-6 w-[500px]">
        <h2 class="text-2xl font-bold mb-4 text-white">Create New Task</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Title</label>
            <input v-model="newTask.title" class="dhq-input w-full" placeholder="What needs to be done?" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Description</label>
            <textarea v-model="newTask.description" class="dhq-input w-full h-24" placeholder="Details..."></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Assignee (Username)</label>
              <input v-model="newTask.assignee" class="dhq-input w-full" placeholder="Leave empty for self" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Priority</label>
              <select v-model="newTask.priority" class="dhq-input w-full">
                <option>LOW</option>
                <option>MEDIUM</option>
                <option>HIGH</option>
                <option>CRITICAL</option>
              </select>
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
          <button class="btn btn-primary" @click="handleCreate">Create Task</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiGet, apiPost, apiPut, apiDelete, showAlert } from '@/utils/api'

const { t } = useI18n()
const tasks = ref([])
const loading = ref(true)
const currentFilter = ref('ALL')
const showCreateModal = ref(false)

const newTask = ref({
  title: '',
  description: '',
  assignee: '',
  priority: 'MEDIUM'
})

const fetchTasks = async () => {
  loading.value = true
  try {
    tasks.value = await apiGet('/tasks')
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
  } finally {
    loading.value = false
  }
}

const filteredTasks = computed(() => {
  if (currentFilter.value === 'ALL') return tasks.value
  return tasks.value.filter(t => t.status === currentFilter.value)
})

const updateStatus = async (id, status) => {
  try {
    await apiPut(`/tasks/${id}`, { status })
    fetchTasks()
  } catch (error) {
    showAlert('Error', 'Failed to update task status', 'error')
  }
}

const handleCreate = async () => {
  if (!newTask.value.title) return
  try {
    await apiPost('/tasks', {
      title: newTask.value.title,
      description: newTask.value.description,
      assignee_username: newTask.value.assignee,
      priority: newTask.value.priority
    })
    showCreateModal.value = false
    newTask.value = { title: '', description: '', assignee: '', priority: 'MEDIUM' }
    fetchTasks()
    showAlert('Success', 'Task created successfully', 'success')
  } catch (error) {
    showAlert('Error', 'Failed to create task', 'error')
  }
}

const deleteTask = async (id) => {
  if (!confirm('Are you sure you want to delete this task?')) return
  try {
    await apiDelete(`/tasks/${id}`)
    fetchTasks()
  } catch (error) {
    showAlert('Error', 'Failed to delete task', 'error')
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.task-center {
  max-width: 1200px;
  margin: 0 auto;
}

.filter-tab {
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-muted);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
}

.task-card {
  transition: transform 0.2s, background 0.2s;
}

.task-card:hover {
  transform: translateX(5px);
  background: var(--glass-bg-hover);
}

.priority-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.priority-low { background: #10b981; }
.priority-medium { background: #3b82f6; }
.priority-high { background: #f59e0b; }
.priority-critical { background: #ef4444; }

.status-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  text-transform: uppercase;
  font-weight: 800;
}
.status-pending { color: #f59e0b; }
.status-in_progress { color: #3b82f6; }
.status-completed { color: #10b981; }

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.1);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

/* Spinner */
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

@media (max-width: 768px) {
  .task-center {
    padding: 1rem;
  }
  .filter-tab {
    padding: 0.4rem 1rem;
    font-size: 0.8rem;
  }
  .task-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  .flex.gap-2 {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
