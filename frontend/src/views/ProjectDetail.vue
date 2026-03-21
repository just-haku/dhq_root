<template>
  <div class="project-detail">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading project details...</p>
    </div>

    <div v-else-if="!project" class="error-state">
      <div class="error-icon">
        <i class="fas fa-exclamation-triangle"></i>
      </div>
      <h3>Project not found</h3>
      <p>The project you're looking for doesn't exist or you don't have permission to view it.</p>
      <button class="btn-primary" @click="$router.push('/projects')">
        <i class="fas fa-arrow-left"></i>
        Back to Projects
      </button>
    </div>

    <div v-else class="project-content">
      <!-- Project Header -->
      <div class="project-header">
        <div class="header-left">
          <button class="back-btn" @click="$router.push('/projects')">
            <i class="fas fa-arrow-left"></i>
            Back to Projects
          </button>
          <div class="project-title">
            <h1>{{ project.name }}</h1>
            <div class="project-badges">
              <span :class="['status-badge', project.status]">{{ project.status }}</span>
              <span :class="['priority-badge', project.priority]">{{ project.priority }}</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <div class="project-actions">
            <button class="action-btn" @click="editProject" title="Edit Project">
              <i class="fas fa-edit"></i>
              Edit
            </button>
            <button class="action-btn" @click="deleteProject" title="Delete Project">
              <i class="fas fa-trash"></i>
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Project Overview -->
      <div class="project-overview">
        <div class="overview-cards">
          <div class="overview-card">
            <div class="card-icon">
              <i class="fas fa-tasks"></i>
            </div>
            <div class="card-content">
              <h3>{{ project.task_count || 0 }}</h3>
              <p>Total Tasks</p>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon completed">
              <i class="fas fa-check-circle"></i>
            </div>
            <div class="card-content">
              <h3>{{ project.completed_tasks || 0 }}</h3>
              <p>Completed</p>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon">
              <i class="fas fa-users"></i>
            </div>
            <div class="card-content">
              <h3>{{ project.team_count || 0 }}</h3>
              <p>Team Members</p>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon">
              <i class="fas fa-calendar"></i>
            </div>
            <div class="card-content">
              <h3>{{ formatDate(project.due_date) }}</h3>
              <p>Due Date</p>
            </div>
          </div>
        </div>

        <!-- Progress Overview -->
        <div class="progress-overview">
          <h3>Project Progress</h3>
          <div class="progress-bar-large">
            <div 
              class="progress-fill" 
              :style="{ width: project.progress + '%' }"
            ></div>
          </div>
          <div class="progress-stats">
            <span>{{ project.progress }}% Complete</span>
            <span>{{ project.completed_tasks || 0 }} of {{ project.task_count || 0 }} tasks</span>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="content-grid">
        <!-- Project Details -->
        <div class="content-section">
          <div class="section-header">
            <h2>Project Details</h2>
            <button class="edit-btn" @click="editProject">
              <i class="fas fa-edit"></i>
            </button>
          </div>
          <div class="details-content">
            <div class="detail-item">
              <label>Description</label>
              <p>{{ project.description || 'No description provided' }}</p>
            </div>
            <div class="detail-row">
              <div class="detail-item">
                <label>Start Date</label>
                <p>{{ formatDate(project.start_date) || 'Not set' }}</p>
              </div>
              <div class="detail-item">
                <label>Due Date</label>
                <p>{{ formatDate(project.due_date) || 'Not set' }}</p>
              </div>
            </div>
            <div class="detail-row">
              <div class="detail-item">
                <label>Budget</label>
                <p>{{ formatCurrency(project.budget) || 'Not set' }}</p>
              </div>
              <div class="detail-item">
                <label>Created</label>
                <p>{{ formatDateTime(project.created_at) }}</p>
              </div>
            </div>
            <div class="detail-item">
              <label>Tags</label>
              <div class="tags-container">
                <span 
                  v-for="tag in project.tags" 
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
                <span v-if="!project.tags || project.tags.length === 0" class="no-tags">
                  No tags assigned
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Team Members -->
        <div class="content-section">
          <div class="section-header">
            <h2>Team Members</h2>
            <button class="add-btn" @click="addTeamMember">
              <i class="fas fa-plus"></i>
            </button>
          </div>
          <div class="team-list">
            <div 
              v-for="member in project.team" 
              :key="member.id"
              class="team-member"
            >
              <img 
                :src="member.avatar || getDefaultAvatar(member.name)" 
                :alt="member.name"
                class="member-avatar"
              />
              <div class="member-info">
                <h4>{{ member.name }}</h4>
                <p>{{ member.role || 'Team Member' }}</p>
              </div>
              <div class="member-actions">
                <button class="action-btn small" @click="removeTeamMember(member)">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            <div v-if="!project.team || project.team.length === 0" class="empty-team">
              <p>No team members assigned</p>
              <button class="btn-primary" @click="addTeamMember">
                <i class="fas fa-plus"></i>
                Add Team Member
              </button>
            </div>
          </div>
        </div>

        <!-- Tasks Section -->
        <div class="content-section full-width">
          <div class="section-header">
            <h2>Tasks</h2>
            <div class="header-actions">
              <div class="view-toggle">
                <button 
                  v-for="view in taskViews" 
                  :key="view.value"
                  :class="['view-btn', { active: currentTaskView === view.value }]"
                  @click="currentTaskView = view.value"
                >
                  <i :class="view.icon"></i>
                  {{ view.label }}
                </button>
              </div>
              <button class="add-btn" @click="addTask">
                <i class="fas fa-plus"></i>
                Add Task
              </button>
            </div>
          </div>

          <!-- Task List View -->
          <div v-if="currentTaskView === 'list'" class="tasks-list">
            <div 
              v-for="task in project.tasks" 
              :key="task.id"
              class="task-item"
            >
              <div class="task-checkbox">
                <input 
                  type="checkbox" 
                  :checked="task.completed"
                  @change="toggleTaskComplete(task)"
                />
              </div>
              <div class="task-content">
                <h4 :class="{ completed: task.completed }">{{ task.title }}</h4>
                <p>{{ task.description }}</p>
                <div class="task-meta">
                  <span :class="['priority-badge', task.priority]">{{ task.priority }}</span>
                  <span class="task-assignee">
                    <img 
                      :src="task.assignee?.avatar || getDefaultAvatar(task.assignee?.name)" 
                      :alt="task.assignee?.name"
                    />
                    {{ task.assignee?.name || 'Unassigned' }}
                  </span>
                  <span class="task-due">{{ formatDate(task.due_date) }}</span>
                </div>
              </div>
              <div class="task-actions">
                <button class="action-btn small" @click="editTask(task)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn small" @click="deleteTask(task)">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
            <div v-if="!project.tasks || project.tasks.length === 0" class="empty-tasks">
              <p>No tasks created yet</p>
              <button class="btn-primary" @click="addTask">
                <i class="fas fa-plus"></i>
                Create First Task
              </button>
            </div>
          </div>

          <!-- Task Board View -->
          <div v-else-if="currentTaskView === 'board'" class="tasks-board">
            <div 
              v-for="column in taskColumns" 
              :key="column.status"
              class="task-column"
            >
              <div class="column-header">
                <h3>{{ column.title }}</h3>
                <span class="column-count">{{ column.tasks.length }}</span>
              </div>
              <div class="column-tasks">
                <div 
                  v-for="task in column.tasks" 
                  :key="task.id"
                  class="task-card"
                >
                  <div class="task-card-header">
                    <span :class="['priority-badge', task.priority]">{{ task.priority }}</span>
                    <button class="action-btn small" @click="deleteTask(task)">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                  <h4>{{ task.title }}</h4>
                  <p>{{ task.description }}</p>
                  <div class="task-card-meta">
                    <span class="task-assignee">
                      <img 
                        :src="task.assignee?.avatar || getDefaultAvatar(task.assignee?.name)" 
                        :alt="task.assignee?.name"
                      />
                    </span>
                    <span class="task-due">{{ formatDate(task.due_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Timeline -->
        <div class="content-section full-width">
          <div class="section-header">
            <h2>Activity Timeline</h2>
            <button class="refresh-btn" @click="loadActivities">
              <i class="fas fa-sync"></i>
            </button>
          </div>
          <div class="timeline">
            <div 
              v-for="activity in project.activities" 
              :key="activity.id"
              class="timeline-item"
            >
              <div class="timeline-icon">
                <i :class="getActivityIcon(activity.type)"></i>
              </div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <h4>{{ activity.title }}</h4>
                  <span class="timeline-time">{{ formatDateTime(activity.created_at) }}</span>
                </div>
                <p>{{ activity.description }}</p>
                <div v-if="activity.user" class="activity-user">
                  <img 
                    :src="activity.user.avatar || getDefaultAvatar(activity.user.name)" 
                    :alt="activity.user.name"
                  />
                  <span>{{ activity.user.name }}</span>
                </div>
              </div>
            </div>
            <div v-if="!project.activities || project.activities.length === 0" class="empty-timeline">
              <p>No activity recorded yet</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Project Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Edit Project</h2>
          <button class="close-btn" @click="closeEditModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group full-width">
              <label>Project Name</label>
              <input v-model="editForm.name" type="text" />
            </div>
            <div class="form-group full-width">
              <label>Description</label>
              <textarea v-model="editForm.description" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="editForm.status">
                <option value="planning">Planning</option>
                <option value="active">Active</option>
                <option value="on-hold">On Hold</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div class="form-group">
              <label>Priority</label>
              <select v-model="editForm.priority">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div class="form-group">
              <label>Start Date</label>
              <input v-model="editForm.start_date" type="date" />
            </div>
            <div class="form-group">
              <label>Due Date</label>
              <input v-model="editForm.due_date" type="date" />
            </div>
            <div class="form-group">
              <label>Budget</label>
              <input v-model.number="editForm.budget" type="number" step="0.01" />
            </div>
            <div class="form-group">
              <label>Progress (%)</label>
              <input v-model.number="editForm.progress" type="number" min="0" max="100" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeEditModal">Cancel</button>
          <button class="btn-primary" @click="saveProject">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiGet, apiPut, apiDelete, apiPost } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

const route = useRoute()
const router = useRouter()

// Reactive state
const loading = ref(false)
const project = ref(null)
const showEditModal = ref(false)
const currentTaskView = ref('list')

const taskViews = [
  { label: 'List', value: 'list', icon: 'fas fa-list' },
  { label: 'Board', value: 'board', icon: 'fas fa-columns' }
]

const editForm = reactive({
  name: '',
  description: '',
  status: '',
  priority: '',
  start_date: '',
  due_date: '',
  budget: 0,
  progress: 0
})

// Computed properties
const taskColumns = computed(() => {
  const columns = [
    { title: 'To Do', status: 'todo', tasks: [] },
    { title: 'In Progress', status: 'in-progress', tasks: [] },
    { title: 'Review', status: 'review', tasks: [] },
    { title: 'Done', status: 'done', tasks: [] }
  ]

  if (project.value?.tasks) {
    project.value.tasks.forEach(task => {
      const column = columns.find(col => col.status === task.status)
      if (column) {
        column.tasks.push(task)
      }
    })
  }

  return columns
})

// Methods
const loadProject = async () => {
  loading.value = true
  try {
    const response = await apiGet(`/projects/${route.params.id}`)
    if (response.success) {
      project.value = response.project
    } else {
      project.value = null
    }
  } catch (error) {
    console.error('Error loading project:', error)
    project.value = null
  } finally {
    loading.value = false
  }
}

const loadActivities = async () => {
  if (!project.value) return
  
  try {
    const response = await apiGet(`/projects/${project.value.id}/activities`)
    if (response.success) {
      project.value.activities = response.activities || []
    }
  } catch (error) {
    console.error('Error loading activities:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not set'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Not set'
  return new Date(dateString).toLocaleString()
}

const formatCurrency = (amount) => {
  if (!amount) return 'Not set'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const getDefaultAvatar = (name) => {
  if (!name) return ''
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3b82f6&color=fff&size=40`
}

const getActivityIcon = (type) => {
  const icons = {
    'project_created': 'fas fa-plus-circle',
    'project_updated': 'fas fa-edit',
    'task_created': 'fas fa-plus',
    'task_completed': 'fas fa-check',
    'member_added': 'fas fa-user-plus',
    'member_removed': 'fas fa-user-minus',
    'status_changed': 'fas fa-exchange-alt'
  }
  return icons[type] || 'fas fa-circle'
}

const editProject = () => {
  if (!project.value) return
  
  Object.assign(editForm, {
    name: project.value.name,
    description: project.value.description,
    status: project.value.status,
    priority: project.value.priority,
    start_date: project.value.start_date,
    due_date: project.value.due_date,
    budget: project.value.budget,
    progress: project.value.progress
  })
  
  showEditModal.value = true
}

const saveProject = async () => {
  if (!project.value) return
  
  try {
    const response = await apiPut(`/projects/${project.value.id}`, editForm)
    if (response.success) {
      Object.assign(project.value, response.project)
      showSuccess('Project updated successfully')
      closeEditModal()
    }
  } catch (error) {
    console.error('Error saving project:', error)
    showError('Failed to save project')
  }
}

const deleteProject = async () => {
  if (!project.value) return
  
  const confirmed = await showConfirm(`Are you sure you want to delete "${project.value.name}"?`)
  if (!confirmed) return
  
  try {
    const response = await apiDelete(`/projects/${project.value.id}`)
    if (response.success) {
      showSuccess('Project deleted successfully')
      router.push('/projects')
    }
  } catch (error) {
    console.error('Error deleting project:', error)
    showError('Failed to delete project')
  }
}

const addTeamMember = () => {
  // Open team member selection modal
  console.log('Add team member')
}

const removeTeamMember = async (member) => {
  if (!project.value) return
  
  const confirmed = await showConfirm(`Remove ${member.name} from the project?`)
  if (!confirmed) return
  
  try {
    const response = await apiDelete(`/projects/${project.value.id}/team/${member.id}`)
    if (response.success) {
      const index = project.value.team.findIndex(m => m.id === member.id)
      if (index > -1) {
        project.value.team.splice(index, 1)
        showSuccess('Team member removed')
      }
    }
  } catch (error) {
    console.error('Error removing team member:', error)
    showError('Failed to remove team member')
  }
}

const addTask = () => {
  // Open task creation modal
  console.log('Add task')
}

const editTask = (task) => {
  // Open task edit modal
  console.log('Edit task:', task)
}

const deleteTask = async (task) => {
  if (!project.value) return
  
  const confirmed = await showConfirm(`Delete task "${task.title}"?`)
  if (!confirmed) return
  
  try {
    const response = await apiDelete(`/projects/${project.value.id}/tasks/${task.id}`)
    if (response.success) {
      const index = project.value.tasks.findIndex(t => t.id === task.id)
      if (index > -1) {
        project.value.tasks.splice(index, 1)
        showSuccess('Task deleted')
      }
    }
  } catch (error) {
    console.error('Error deleting task:', error)
    showError('Failed to delete task')
  }
}

const toggleTaskComplete = async (task) => {
  if (!project.value) return
  
  try {
    const response = await apiPut(`/projects/${project.value.id}/tasks/${task.id}`, {
      completed: !task.completed
    })
    
    if (response.success) {
      task.completed = !task.completed
      showSuccess(task.completed ? 'Task completed' : 'Task marked as incomplete')
    }
  } catch (error) {
    console.error('Error updating task:', error)
    showError('Failed to update task')
  }
}

const closeEditModal = () => {
  showEditModal.value = false
}

// Lifecycle
onMounted(() => {
  loadProject()
})
</script>

<style scoped>
.project-detail {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.loading-state, .error-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 3px solid var(--glass-border);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  color: var(--danger-color);
  margin-bottom: 1rem;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
}

.header-left {
  flex: 1;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
  font-weight: 500;
}

.back-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.project-title h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.75rem 0;
}

.project-badges {
  display: flex;
  gap: 0.75rem;
}

.status-badge, .priority-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.planning {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.on-hold {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.completed {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.cancelled {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.priority-badge.low {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.priority-badge.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.priority-badge.high {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.priority-badge.critical {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.project-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  padding: 0.625rem 1.25rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.small {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.project-overview {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.overview-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-icon {
  width: 50px;
  height: 50px;
  background: var(--primary-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.card-icon.completed {
  background: var(--success-color);
}

.card-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.card-content p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.9rem;
}

.progress-overview {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.progress-overview h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.progress-bar-large {
  width: 100%;
  height: 12px;
  background: var(--glass-bg-tertiary);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
  border-radius: 6px;
  transition: width 0.3s ease;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.content-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
}

.content-section.full-width {
  grid-column: 1 / -1;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.section-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.edit-btn, .add-btn, .refresh-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  background: var(--glass-bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-btn:hover, .add-btn:hover, .refresh-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.add-btn:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 0.25rem;
}

.view-btn {
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
}

.view-btn:hover {
  background: var(--glass-bg-hover);
}

.view-btn.active {
  background: var(--primary-color);
  color: white;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-primary);
}

.detail-item p {
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.detail-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.no-tags {
  color: var(--text-tertiary);
  font-style: italic;
}

.team-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.member-info {
  flex: 1;
}

.member-info h4 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.member-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.member-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-team, .empty-tasks, .empty-timeline {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-secondary {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.task-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.task-checkbox input {
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
  margin-top: 0.125rem;
}

.task-content {
  flex: 1;
}

.task-content h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.task-content h4.completed {
  text-decoration: line-through;
  color: var(--text-tertiary);
}

.task-content p {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.task-assignee {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.task-assignee img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.task-due {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
}

.tasks-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.task-column {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--glass-border);
}

.column-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.column-count {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.column-tasks {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 200px;
}

.task-card {
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.task-card:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-1px);
}

.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.task-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.task-card p {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.4;
}

.task-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
}

.timeline-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.timeline-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.timeline-time {
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

.timeline-content p {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.activity-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.activity-user img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

@media (max-width: 768px) {
  .project-detail {
    padding: 1rem;
  }
  
  .project-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .project-overview {
    grid-template-columns: 1fr;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-row {
    grid-template-columns: 1fr;
  }
  
  .tasks-board {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
