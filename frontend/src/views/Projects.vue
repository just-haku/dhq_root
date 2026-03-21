<template>
  <div class="projects">
    <div class="page-header">
      <h1>Projects</h1>
      <p>Manage your projects, tasks, and team collaboration</p>
    </div>

    <!-- Project Controls -->
    <div class="project-controls">
      <div class="control-section">
        <div class="view-toggle">
          <button 
            v-for="view in viewOptions" 
            :key="view.value"
            :class="['view-btn', { active: currentView === view.value }]"
            @click="currentView = view.value"
          >
            <i :class="view.icon"></i>
            {{ view.label }}
          </button>
        </div>
      </div>

      <div class="control-section">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search projects..."
            @input="filterProjects"
          />
        </div>
      </div>

      <div class="control-section">
        <div class="filter-dropdown">
          <select v-model="statusFilter" @change="filterProjects">
            <option value="">All Status</option>
            <option value="planning">Planning</option>
            <option value="active">Active</option>
            <option value="on-hold">On Hold</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      <div class="control-section">
        <div class="filter-dropdown">
          <select v-model="priorityFilter" @change="filterProjects">
            <option value="">All Priority</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      <div class="control-section">
        <button class="add-project-btn" @click="showAddProjectModal = true">
          <i class="fas fa-plus"></i>
          New Project
        </button>
      </div>
    </div>

    <!-- Project Statistics -->
    <div class="project-stats">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-folder"></i>
        </div>
        <div class="stat-content">
          <h3>{{ projectStats.total }}</h3>
          <p>Total Projects</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon active">
          <i class="fas fa-play-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ projectStats.active }}</h3>
          <p>Active</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon completed">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ projectStats.completed }}</h3>
          <p>Completed</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon overdue">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ projectStats.overdue }}</h3>
          <p>Overdue</p>
        </div>
      </div>
    </div>

    <!-- Projects Display -->
    <div class="projects-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading projects...</p>
      </div>

      <div v-else-if="filteredProjects.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-folder-open"></i>
        </div>
        <h3>No projects found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <!-- Grid View -->
      <div v-else-if="currentView === 'grid'" class="projects-grid">
        <div 
          v-for="project in filteredProjects" 
          :key="project.id"
          class="project-card"
          @click="viewProject(project)"
        >
          <div class="project-header">
            <div class="project-status">
              <span :class="['status-badge', project.status]">{{ project.status }}</span>
              <span :class="['priority-badge', project.priority]">{{ project.priority }}</span>
            </div>
            <div class="project-actions">
              <button 
                class="action-btn"
                @click.stop="editProject(project)"
                title="Edit Project"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button 
                class="action-btn"
                @click.stop="deleteProject(project)"
                title="Delete Project"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>

          <div class="project-content">
            <h3>{{ project.name }}</h3>
            <p class="project-description">{{ project.description }}</p>
            
            <div class="project-meta">
              <div class="meta-item">
                <i class="fas fa-calendar"></i>
                <span>Due {{ formatDate(project.due_date) }}</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-tasks"></i>
                <span>{{ project.task_count }} tasks</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-users"></i>
                <span>{{ project.team_count }} members</span>
              </div>
            </div>

            <div class="project-progress">
              <div class="progress-header">
                <span>Progress</span>
                <span>{{ project.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: project.progress + '%' }"
                ></div>
              </div>
            </div>

            <div class="project-team">
              <div class="team-avatars">
                <img 
                  v-for="member in project.team.slice(0, 4)" 
                  :key="member.id"
                  :src="member.avatar || getDefaultAvatar(member.name)"
                  :alt="member.name"
                  :title="member.name"
                />
                <div 
                  v-if="project.team.length > 4" 
                  class="avatar-more"
                  :title="`${project.team.length - 4} more members`"
                >
                  +{{ project.team.length - 4 }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else-if="currentView === 'list'" class="projects-list">
        <table class="projects-table">
          <thead>
            <tr>
              <th>Project</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Progress</th>
              <th>Due Date</th>
              <th>Team</th>
              <th>Tasks</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="project in filteredProjects" 
              :key="project.id"
              class="project-row"
              @click="viewProject(project)"
            >
              <td>
                <div class="project-info">
                  <h4>{{ project.name }}</h4>
                  <p>{{ project.description }}</p>
                </div>
              </td>
              <td>
                <span :class="['status-badge', project.status]">{{ project.status }}</span>
              </td>
              <td>
                <span :class="['priority-badge', project.priority]">{{ project.priority }}</span>
              </td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar small">
                    <div 
                      class="progress-fill" 
                      :style="{ width: project.progress + '%' }"
                    ></div>
                  </div>
                  <span>{{ project.progress }}%</span>
                </div>
              </td>
              <td>{{ formatDate(project.due_date) }}</td>
              <td>
                <div class="team-cell">
                  <div class="team-avatars small">
                    <img 
                      v-for="member in project.team.slice(0, 3)" 
                      :key="member.id"
                      :src="member.avatar || getDefaultAvatar(member.name)"
                      :alt="member.name"
                      :title="member.name"
                    />
                    <span v-if="project.team.length > 3">+{{ project.team.length - 3 }}</span>
                  </div>
                </div>
              </td>
              <td>{{ project.task_count }}</td>
              <td>
                <div class="actions-cell">
                  <button 
                    class="action-btn small"
                    @click.stop="editProject(project)"
                    title="Edit Project"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button 
                    class="action-btn small"
                    @click.stop="deleteProject(project)"
                    title="Delete Project"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Kanban View -->
      <div v-else-if="currentView === 'kanban'" class="kanban-board">
        <div 
          v-for="column in kanbanColumns" 
          :key="column.status"
          class="kanban-column"
        >
          <div class="column-header">
            <h3>{{ column.title }}</h3>
            <span class="column-count">{{ column.projects.length }}</span>
          </div>
          <div class="column-projects">
            <div 
              v-for="project in column.projects" 
              :key="project.id"
              class="kanban-card"
              @click="viewProject(project)"
            >
              <div class="card-header">
                <span :class="['priority-badge', project.priority]">{{ project.priority }}</span>
                <button 
                  class="action-btn small"
                  @click.stop="editProject(project)"
                >
                  <i class="fas fa-edit"></i>
                </button>
              </div>
              <h4>{{ project.name }}</h4>
              <p>{{ project.description }}</p>
              <div class="card-meta">
                <div class="meta-item">
                  <i class="fas fa-calendar"></i>
                  <span>{{ formatDate(project.due_date) }}</span>
                </div>
                <div class="progress-bar small">
                  <div 
                    class="progress-fill" 
                    :style="{ width: project.progress + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Project Modal -->
    <div v-if="showAddProjectModal || showEditProjectModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ showEditProjectModal ? 'Edit Project' : 'Create New Project' }}</h2>
          <button class="close-btn" @click="closeModals">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group full-width">
              <label>Project Name *</label>
              <input 
                v-model="projectForm.name" 
                type="text" 
                placeholder="Enter project name"
                required
              />
            </div>

            <div class="form-group full-width">
              <label>Description</label>
              <textarea 
                v-model="projectForm.description" 
                placeholder="Describe your project..."
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Status *</label>
              <select v-model="projectForm.status" required>
                <option value="">Select Status</option>
                <option value="planning">Planning</option>
                <option value="active">Active</option>
                <option value="on-hold">On Hold</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div class="form-group">
              <label>Priority *</label>
              <select v-model="projectForm.priority" required>
                <option value="">Select Priority</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div class="form-group">
              <label>Start Date</label>
              <input 
                v-model="projectForm.start_date" 
                type="date"
              />
            </div>

            <div class="form-group">
              <label>Due Date *</label>
              <input 
                v-model="projectForm.due_date" 
                type="date"
                required
              />
            </div>

            <div class="form-group">
              <label>Budget</label>
              <input 
                v-model.number="projectForm.budget" 
                type="number"
                placeholder="0.00"
                step="0.01"
              />
            </div>

            <div class="form-group">
              <label>Progress (%)</label>
              <input 
                v-model.number="projectForm.progress" 
                type="number"
                min="0"
                max="100"
                placeholder="0"
              />
            </div>
          </div>

          <div class="form-group">
            <label>Team Members</label>
            <div class="team-selector">
              <div 
                v-for="member in availableTeamMembers" 
                :key="member.id"
                class="team-member-option"
              >
                <label>
                  <input 
                    type="checkbox" 
                    :value="member.id"
                    v-model="projectForm.team_members"
                  />
                  <img 
                    :src="member.avatar || getDefaultAvatar(member.name)" 
                    :alt="member.name"
                  />
                  <span>{{ member.name }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModals">Cancel</button>
          <button 
            class="btn-primary" 
            @click="saveProject"
            :disabled="saving"
          >
            {{ saving ? 'Saving...' : (showEditProjectModal ? 'Update Project' : 'Create Project') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const saving = ref(false)
const projects = ref([])
const availableTeamMembers = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const priorityFilter = ref('')
const currentView = ref('grid')

// Modal states
const showAddProjectModal = ref(false)
const showEditProjectModal = ref(false)
const selectedProject = ref(null)

// View options
const viewOptions = [
  { label: 'Grid', value: 'grid', icon: 'fas fa-th' },
  { label: 'List', value: 'list', icon: 'fas fa-list' },
  { label: 'Kanban', value: 'kanban', icon: 'fas fa-columns' }
]

// Form
const projectForm = reactive({
  name: '',
  description: '',
  status: '',
  priority: '',
  start_date: '',
  due_date: '',
  budget: 0,
  progress: 0,
  team_members: []
})

// Computed properties
const filteredProjects = computed(() => {
  let filtered = projects.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(project => 
      project.name.toLowerCase().includes(query) ||
      project.description.toLowerCase().includes(query)
    )
  }

  // Apply status filter
  if (statusFilter.value) {
    filtered = filtered.filter(project => project.status === statusFilter.value)
  }

  // Apply priority filter
  if (priorityFilter.value) {
    filtered = filtered.filter(project => project.priority === priorityFilter.value)
  }

  return filtered
})

const projectStats = computed(() => {
  const stats = {
    total: projects.value.length,
    active: projects.value.filter(p => p.status === 'active').length,
    completed: projects.value.filter(p => p.status === 'completed').length,
    overdue: projects.value.filter(p => new Date(p.due_date) < new Date() && p.status !== 'completed').length
  }
  return stats
})

const kanbanColumns = computed(() => {
  const columns = [
    { title: 'Planning', status: 'planning', projects: [] },
    { title: 'Active', status: 'active', projects: [] },
    { title: 'On Hold', status: 'on-hold', projects: [] },
    { title: 'Completed', status: 'completed', projects: [] }
  ]

  filteredProjects.value.forEach(project => {
    const column = columns.find(col => col.status === project.status)
    if (column) {
      column.projects.push(project)
    }
  })

  return columns
})

// Methods
const loadProjects = async () => {
  loading.value = true
  try {
    const response = await apiGet('/projects')
    if (response.success) {
      projects.value = response.projects || []
    }
  } catch (error) {
    console.error('Error loading projects:', error)
    showError('Failed to load projects')
  } finally {
    loading.value = false
  }
}

const loadTeamMembers = async () => {
  try {
    const response = await apiGet('/team/members')
    if (response.success) {
      availableTeamMembers.value = response.members || []
    }
  } catch (error) {
    console.error('Error loading team members:', error)
  }
}

const filterProjects = () => {
  // This is reactive, no additional action needed
}

const formatDate = (dateString) => {
  if (!dateString) return 'No date set'
  return new Date(dateString).toLocaleDateString()
}

const getDefaultAvatar = (name) => {
  const initials = name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
  
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3b82f6&color=fff&size=40`
}

const getEmptyMessage = () => {
  if (searchQuery.value || statusFilter.value || priorityFilter.value) {
    return 'No projects match your search criteria'
  }
  return 'Create your first project to get started'
}

const viewProject = (project) => {
  // Navigate to project details or show details modal
  console.log('View project:', project)
}

const editProject = (project) => {
  selectedProject.value = project
  Object.assign(projectForm, {
    ...project,
    team_members: project.team?.map(member => member.id) || []
  })
  showEditProjectModal.value = true
}

const deleteProject = async (project) => {
  const confirmed = await showConfirm(`Are you sure you want to delete "${project.name}"?`)
  if (!confirmed) return

  try {
    const response = await apiDelete(`/projects/${project.id}`)
    if (response.success) {
      const index = projects.value.findIndex(p => p.id === project.id)
      if (index > -1) {
        projects.value.splice(index, 1)
        showSuccess('Project deleted successfully')
      }
    }
  } catch (error) {
    console.error('Error deleting project:', error)
    showError('Failed to delete project')
  }
}

const saveProject = async () => {
  if (!projectForm.name || !projectForm.status || !projectForm.priority || !projectForm.due_date) {
    showError('Please fill in all required fields')
    return
  }

  saving.value = true
  try {
    const isEdit = showEditProjectModal.value
    const endpoint = isEdit ? `/projects/${selectedProject.value.id}` : '/projects'
    const method = isEdit ? apiPut : apiPost

    const response = await method(endpoint, projectForm)
    
    if (response.success) {
      if (isEdit) {
        Object.assign(selectedProject.value, response.project)
        showSuccess('Project updated successfully')
      } else {
        projects.value.push(response.project)
        showSuccess('Project created successfully')
      }
      closeModals()
    }
  } catch (error) {
    console.error('Error saving project:', error)
    showError('Failed to save project')
  } finally {
    saving.value = false
  }
}

const closeModals = () => {
  showAddProjectModal.value = false
  showEditProjectModal.value = false
  resetProjectForm()
}

const resetProjectForm = () => {
  Object.assign(projectForm, {
    name: '',
    description: '',
    status: '',
    priority: '',
    start_date: '',
    due_date: '',
    budget: 0,
    progress: 0,
    team_members: []
  })
  selectedProject.value = null
}

// Lifecycle
onMounted(() => {
  loadProjects()
  loadTeamMembers()
})
</script>

<style scoped>
.projects {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.project-controls {
  display: grid;
  grid-template-columns: auto 2fr 1fr 1fr auto;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: center;
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
  padding: 0.5rem 1rem;
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
}

.view-btn:hover {
  background: var(--glass-bg-hover);
}

.view-btn.active {
  background: var(--primary-color);
  color: white;
}

.search-box {
  position: relative;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.filter-dropdown select {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.add-project-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add-project-btn:hover {
  background: var(--primary-hover);
}

.project-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
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

.stat-icon.active {
  background: var(--success-color);
}

.stat-icon.completed {
  background: var(--info-color);
}

.stat-icon.overdue {
  background: var(--danger-color);
}

.stat-content h3 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.9rem;
}

.projects-container {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  min-height: 400px;
}

.loading-state, .empty-state {
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

.empty-icon {
  font-size: 3rem;
  color: var(--text-tertiary);
  margin-bottom: 1rem;
}

/* Grid View */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.project-card:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.project-status {
  display: flex;
  gap: 0.5rem;
}

.status-badge, .priority-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
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
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  background: var(--glass-bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.small {
  width: 28px;
  height: 28px;
  font-size: 0.8rem;
}

.project-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.project-description {
  color: var(--text-secondary);
  margin: 0 0 1rem 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  /* Fallback for browsers that don't support -webkit-line-clamp */
  display: -moz-box;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  box-orient: vertical;
}

.project-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.meta-item i {
  width: 16px;
  color: var(--text-tertiary);
}

.project-progress {
  margin-bottom: 1rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar.small {
  height: 6px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
  border-radius: 4px;
  transition: width 0.3s ease;
}

.project-team {
  margin-top: 1rem;
}

.team-avatars {
  display: flex;
  align-items: center;
  gap: -8px;
}

.team-avatars img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--glass-bg-primary);
  margin-right: -8px;
}

.team-avatars.small img {
  width: 28px;
  height: 28px;
}

.avatar-more {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--glass-bg-tertiary);
  border: 2px solid var(--glass-bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-left: -8px;
}

/* List View */
.projects-table {
  width: 100%;
  border-collapse: collapse;
}

.projects-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.projects-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.project-row {
  cursor: pointer;
  transition: background 0.3s ease;
}

.project-row:hover {
  background: var(--glass-bg-hover);
}

.project-info h4 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.project-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-cell .progress-bar {
  flex: 1;
  max-width: 100px;
}

.team-cell {
  display: flex;
  align-items: center;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

/* Kanban View */
.kanban-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.kanban-column {
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
  padding-bottom: 0.5rem;
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

.column-projects {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 200px;
}

.kanban-card {
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.kanban-card:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-1px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.kanban-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.kanban-card p {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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
  max-width: 800px;
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
  margin-bottom: 1rem;
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

.team-selector {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.team-member-option label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background 0.3s ease;
}

.team-member-option label:hover {
  background: var(--glass-bg-hover);
}

.team-member-option input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
}

.team-member-option img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
}

@media (max-width: 768px) {
  .projects {
    padding: 1rem;
  }
  
  .project-controls {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .view-toggle {
    justify-content: center;
  }
  
  .project-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .projects-grid {
    grid-template-columns: 1fr;
  }
  
  .kanban-board {
    grid-template-columns: 1fr;
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
