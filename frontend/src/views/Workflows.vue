<template>
  <div class="workflows">
    <div class="page-header">
      <h1>Workflows</h1>
      <p>Design and manage automated workflows</p>
    </div>

    <!-- Workflow Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-project-diagram"></i>
          </div>
          <div class="card-content">
            <h3>{{ workflowStats.totalWorkflows }}</h3>
            <p>Total Workflows</p>
            <span class="workflow-count">{{ workflowStats.activeWorkflows }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon runs">
            <i class="fas fa-play-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ workflowStats.totalExecutions }}</h3>
            <p>Total Executions</p>
            <span class="execution-count">{{ workflowStats.todayExecutions }} today</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon success">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ workflowStats.successRate }}%</h3>
            <p>Success Rate</p>
            <span class="success-status" :class="getSuccessClass(workflowStats.successRate)">
              {{ getSuccessStatus(workflowStats.successRate) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon time">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ workflowStats.avgDuration }}s</h3>
            <p>Avg Duration</p>
            <span class="duration-status">{{ workflowStats.lastDuration }}s last</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="create-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Workflow
        </button>
        <button class="import-btn" @click="showImportModal = true">
          <i class="fas fa-upload"></i>
          Import Workflow
        </button>
        <button class="templates-btn" @click="showTemplatesModal = true">
          <i class="fas fa-file-alt"></i>
          Browse Templates
        </button>
      </div>
    </div>

    <!-- Workflows Grid -->
    <div class="workflows-section">
      <div class="section-header">
        <h2>My Workflows</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterWorkflows">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="draft">Draft</option>
            </select>
          </div>
          <div class="view-toggle">
            <button 
              :class="['view-btn', { active: viewMode === 'grid' }]"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'list' }]"
              @click="viewMode = 'list'"
            >
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading workflows...</p>
      </div>

      <div v-else-if="filteredWorkflows.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-project-diagram"></i>
        </div>
        <h3>No workflows found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Workflow
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="workflows-grid">
          <div 
            v-for="workflow in filteredWorkflows" 
            :key="workflow.id"
            class="workflow-card"
            :class="{ 'inactive': workflow.status === 'inactive', 'draft': workflow.status === 'draft' }"
          >
            <div class="workflow-header">
              <div class="workflow-icon">
                <i class="fas fa-project-diagram"></i>
              </div>
              <div class="workflow-status">
                <span :class="['status-badge', workflow.status]">{{ workflow.status }}</span>
              </div>
            </div>

            <div class="workflow-content">
              <h3>{{ workflow.name }}</h3>
              <p>{{ workflow.description }}</p>
              
              <div class="workflow-meta">
                <span class="nodes">{{ workflow.nodes }} nodes</span>
                <span class="executions">{{ workflow.executions }} runs</span>
                <span class="duration">{{ workflow.avgDuration }}s avg</span>
              </div>

              <div class="workflow-actions">
                <button class="action-btn run" @click="runWorkflow(workflow)">
                  <i class="fas fa-play"></i>
                  Run
                </button>
                <button class="action-btn edit" @click="editWorkflow(workflow)">
                  <i class="fas fa-edit"></i>
                  Edit
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="workflows-list">
          <div 
            v-for="workflow in filteredWorkflows" 
            :key="workflow.id"
            class="workflow-list-card"
            :class="{ 'inactive': workflow.status === 'inactive', 'draft': workflow.status === 'draft' }"
          >
            <div class="workflow-list-header">
              <div class="workflow-list-info">
                <div class="workflow-icon">
                  <i class="fas fa-project-diagram"></i>
                </div>
                <div class="workflow-details">
                  <h3>{{ workflow.name }}</h3>
                  <p>{{ workflow.description }}</p>
                  <div class="workflow-meta">
                    <span class="nodes">{{ workflow.nodes }} nodes</span>
                    <span :class="['status-badge', workflow.status]">{{ workflow.status }}</span>
                    <span class="executions">{{ workflow.executions }} runs</span>
                    <span class="duration">{{ workflow.avgDuration }}s avg</span>
                  </div>
                </div>
              </div>
              <div class="workflow-list-actions">
                <button class="action-btn run" @click="runWorkflow(workflow)">
                  <i class="fas fa-play"></i>
                </button>
                <button class="action-btn edit" @click="editWorkflow(workflow)">
                  <i class="fas fa-edit"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Workflow Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Create Workflow</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="workflow-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Workflow Name *</label>
                <input 
                  v-model="workflowForm.name" 
                  type="text" 
                  placeholder="Enter workflow name"
                  required
                />
              </div>
              <div class="form-group">
                <label>Category</label>
                <select v-model="workflowForm.category">
                  <option value="automation">Automation</option>
                  <option value="integration">Integration</option>
                  <option value="data">Data Processing</option>
                  <option value="notification">Notification</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="workflowForm.description" 
                placeholder="Describe your workflow"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Workflow Nodes</label>
              <div class="nodes-container">
                <div 
                  v-for="(node, index) in workflowForm.nodes" 
                  :key="index"
                  class="node-item"
                >
                  <div class="node-header">
                    <input 
                      v-model="node.name" 
                      type="text" 
                      placeholder="Node name"
                    />
                    <button 
                      class="remove-btn"
                      @click="removeNode(index)"
                    >
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                  <div class="node-config">
                    <select v-model="node.type">
                      <option value="trigger">Trigger</option>
                      <option value="action">Action</option>
                      <option value="condition">Condition</option>
                      <option value="transform">Transform</option>
                    </select>
                  </div>
                </div>
                <button class="add-node-btn" @click="addNode">
                  <i class="fas fa-plus"></i>
                  Add Node
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button class="btn-primary" @click="createWorkflow">Create Workflow</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const statusFilter = ref('')
const viewMode = ref('grid')
const showCreateModal = ref(false)
const showImportModal = ref(false)
const showTemplatesModal = ref(false)

// Workflow stats
const workflowStats = reactive({
  totalWorkflows: 8,
  activeWorkflows: 5,
  totalExecutions: 342,
  todayExecutions: 12,
  successRate: 92,
  avgDuration: 45,
  lastDuration: 38
})

// Workflow form
const workflowForm = reactive({
  name: '',
  description: '',
  category: 'automation',
  nodes: []
})

// Mock data
const workflows = ref([
  {
    id: 1,
    name: 'Data Sync Workflow',
    description: 'Sync data between multiple systems',
    status: 'active',
    nodes: 8,
    executions: 156,
    avgDuration: 45,
    category: 'integration'
  },
  {
    id: 2,
    name: 'Email Notification Flow',
    description: 'Send automated email notifications',
    status: 'active',
    nodes: 5,
    executions: 89,
    avgDuration: 12,
    category: 'notification'
  },
  {
    id: 3,
    name: 'Report Generation',
    description: 'Generate daily reports automatically',
    status: 'inactive',
    nodes: 12,
    executions: 67,
    avgDuration: 120,
    category: 'automation'
  },
  {
    id: 4,
    name: 'User Onboarding',
    description: 'Handle new user onboarding process',
    status: 'draft',
    nodes: 6,
    executions: 0,
    avgDuration: 0,
    category: 'automation'
  }
])

// Computed properties
const filteredWorkflows = computed(() => {
  let filtered = workflows.value

  if (statusFilter.value) {
    filtered = filtered.filter(workflow => workflow.status === statusFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
})

// Methods
const loadWorkflows = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/workflows')
    // if (response.success) {
    //   workflows.value = response.workflows || []
    //   Object.assign(workflowStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading workflows:', error)
    showError('Failed to load workflows')
  } finally {
    loading.value = false
  }
}

const filterWorkflows = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value) {
    return 'No workflows match your filter criteria'
  }
  return 'No workflows found'
}

const getSuccessClass = (rate) => {
  if (rate >= 95) return 'excellent'
  if (rate >= 90) return 'good'
  if (rate >= 80) return 'fair'
  return 'poor'
}

const getSuccessStatus = (rate) => {
  if (rate >= 95) return 'Excellent'
  if (rate >= 90) return 'Good'
  if (rate >= 80) return 'Fair'
  return 'Needs Improvement'
}

const runWorkflow = async (workflow) => {
  try {
    // const response = await apiPost(`/workflows/${workflow.id}/run`)
    // if (response.success) {
    //   workflow.executions++
    //   showSuccess('Workflow started successfully')
    // }
    
    // For demo, simulate run
    workflow.executions++
    showSuccess('Workflow started successfully')
  } catch (error) {
    console.error('Error running workflow:', error)
    showError('Failed to run workflow')
  }
}

const editWorkflow = (workflow) => {
  // Populate form with workflow data
  Object.assign(workflowForm, {
    name: workflow.name,
    description: workflow.description,
    category: workflow.category
  })
  
  showCreateModal.value = true
}

const addNode = () => {
  workflowForm.nodes.push({
    name: '',
    type: 'action'
  })
}

const removeNode = (index) => {
  workflowForm.nodes.splice(index, 1)
}

const createWorkflow = async () => {
  if (!workflowForm.name) {
    showError('Please enter a workflow name')
    return
  }

  try {
    // const response = await apiPost('/workflows', workflowForm)
    // if (response.success) {
    //   workflows.value.unshift(response.workflow)
    //   showSuccess('Workflow created successfully')
    //   closeCreateModal()
    // }
    
    // For demo, simulate creation
    const newWorkflow = {
      id: Date.now(),
      ...workflowForm,
      status: 'draft',
      nodes: workflowForm.nodes.length,
      executions: 0,
      avgDuration: 0
    }
    
    workflows.value.unshift(newWorkflow)
    showSuccess('Workflow created successfully')
    closeCreateModal()
  } catch (error) {
    console.error('Error creating workflow:', error)
    showError('Failed to create workflow')
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetWorkflowForm()
}

const resetWorkflowForm = () => {
  Object.assign(workflowForm, {
    name: '',
    description: '',
    category: 'automation',
    nodes: []
  })
}

// Lifecycle
onMounted(() => {
  loadWorkflows()
})
</script>

<style scoped>
.workflows {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
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

.overview-section {
  margin-bottom: 3rem;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.overview-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  text-align: center;
}

.card-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.card-icon.runs {
  background: var(--success-color);
}

.card-icon.success {
  background: var(--warning-color);
}

.card-icon.time {
  background: var(--info-color);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.card-content p {
  color: var(--text-secondary);
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.workflow-count,
.execution-count,
.success-status,
.duration-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.workflow-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.execution-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.success-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.success-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.success-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.success-status.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.duration-status {
  background: rgba(6, 182, 212, 0.1);
  color: #06b6d4;
}

.actions-section {
  margin-bottom: 3rem;
}

.action-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.create-btn,
.import-btn,
.templates-btn {
  padding: 1rem 2rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.create-btn:hover,
.import-btn:hover,
.templates-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.import-btn {
  background: var(--success-color);
}

.import-btn:hover {
  background: var(--success-hover);
}

.templates-btn {
  background: var(--info-color);
}

.templates-btn:hover {
  background: var(--info-hover);
}

.workflows-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-dropdown select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.loading-state,
.empty-state {
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

.create-first-btn {
  padding: 1rem 2rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 2rem;
}

.create-first-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.workflows-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.workflow-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.workflow-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.workflow-card.inactive {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.workflow-card.draft {
  opacity: 0.6;
  border-color: var(--glass-border);
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.workflow-icon {
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

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.inactive {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.draft {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.workflow-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.workflow-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.workflow-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.nodes,
.executions,
.duration {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.workflow-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.run:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.edit:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.workflows-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.workflow-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.workflow-list-card:hover {
  background: var(--glass-bg-hover);
}

.workflow-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.workflow-list-info {
  flex: 1;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.workflow-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.workflow-details p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
}

.workflow-list-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.workflow-list-actions {
  display: flex;
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

.modal-content.large {
  max-width: 1000px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.5rem;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 2rem;
}

.workflow-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
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

.nodes-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.node-item {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
}

.node-header {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.75rem;
}

.node-header input {
  flex: 1;
  padding: 0.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
}

.remove-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--danger-color);
  border-radius: 6px;
  background: var(--danger-color);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: var(--danger-hover);
}

.node-config select {
  width: 100%;
  padding: 0.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
}

.add-node-btn {
  padding: 0.75rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  align-self: flex-start;
}

.add-node-btn:hover {
  background: var(--primary-hover);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary {
  padding: 1rem 2rem;
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

@media (max-width: 768px) {
  .workflows {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .workflows-grid {
    grid-template-columns: 1fr;
  }
  
  .workflow-list-header {
    flex-direction: column;
    gap: 1rem;
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
