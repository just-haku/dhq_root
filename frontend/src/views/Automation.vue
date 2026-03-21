<template>
  <div class="automation">
    <div class="page-header">
      <h1>Automation</h1>
      <p>Streamline workflows with automated processes</p>
    </div>

    <!-- Automation Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-robot"></i>
          </div>
          <div class="card-content">
            <h3>{{ automationStats.totalAutomations }}</h3>
            <p>Total Automations</p>
            <span class="automation-count">{{ automationStats.activeAutomations }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon runs">
            <i class="fas fa-play-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ automationStats.totalRuns }}</h3>
            <p>Total Runs</p>
            <span class="run-count">{{ automationStats.todayRuns }} today</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon success">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ automationStats.successRate }}%</h3>
            <p>Success Rate</p>
            <span class="success-status" :class="getSuccessClass(automationStats.successRate)">
              {{ getSuccessStatus(automationStats.successRate) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon time">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ automationStats.timeSaved }}h</h3>
            <p>Time Saved</p>
            <span class="time-saved">{{ automationStats.thisMonth }}h this month</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="create-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Automation
        </button>
        <button class="import-btn" @click="showImportModal = true">
          <i class="fas fa-upload"></i>
          Import Workflow
        </button>
        <button class="templates-btn" @click="showTemplatesModal = true">
          <i class="fas fa-file-alt"></i>
          Browse Templates
        </button>
        <button class="logs-btn" @click="showLogsModal = true">
          <i class="fas fa-history"></i>
          View Logs
        </button>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="search-section">
      <div class="search-controls">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search automations..."
            @input="filterAutomations"
          />
        </div>
        <div class="filter-dropdown">
          <select v-model="statusFilter" @change="filterAutomations">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="draft">Draft</option>
            <option value="error">Error</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="triggerFilter" @change="filterAutomations">
            <option value="">All Triggers</option>
            <option value="schedule">Schedule</option>
            <option value="webhook">Webhook</option>
            <option value="event">Event</option>
            <option value="manual">Manual</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="categoryFilter" @change="filterAutomations">
            <option value="">All Categories</option>
            <option value="data">Data Processing</option>
            <option value="notification">Notifications</option>
            <option value="integration">Integrations</option>
            <option value="backup">Backup</option>
            <option value="cleanup">Cleanup</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Automations Grid -->
    <div class="automations-section">
      <div class="section-header">
        <h2>My Automations</h2>
        <div class="header-actions">
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
        <p>Loading automations...</p>
      </div>

      <div v-else-if="filteredAutomations.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-robot"></i>
        </div>
        <h3>No automations found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Automation
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="automations-grid">
          <div 
            v-for="automation in filteredAutomations" 
            :key="automation.id"
            class="automation-card"
            :class="{ 'paused': automation.status === 'paused', 'error': automation.status === 'error' }"
          >
            <div class="automation-header">
              <div class="automation-icon">
                <i :class="getAutomationIcon(automation.category)"></i>
              </div>
              <div class="automation-status">
                <span :class="['status-badge', automation.status]">{{ automation.status }}</span>
              </div>
            </div>

            <div class="automation-content">
              <h3>{{ automation.name }}</h3>
              <p>{{ automation.description }}</p>
              
              <div class="automation-meta">
                <span class="category">{{ automation.category }}</span>
                <span class="trigger">{{ automation.trigger }}</span>
                <span class="runs">{{ automation.runs }} runs</span>
              </div>

              <div class="automation-stats">
                <div class="stat-item">
                  <label>Success Rate:</label>
                  <span :class="getSuccessClass(automation.successRate)">
                    {{ automation.successRate }}%
                  </span>
                </div>
                <div class="stat-item">
                  <label>Last Run:</label>
                  <span>{{ formatDate(automation.lastRun) }}</span>
                </div>
                <div class="stat-item">
                  <label>Next Run:</label>
                  <span>{{ formatDate(automation.nextRun) }}</span>
                </div>
              </div>

              <div class="automation-actions">
                <button 
                  class="action-btn play"
                  @click="runAutomation(automation)"
                  :disabled="automation.status === 'running'"
                >
                  <i :class="automation.status === 'running' ? 'fas fa-spinner fa-spin' : 'fas fa-play'"></i>
                  {{ automation.status === 'running' ? 'Running' : 'Run' }}
                </button>
                <button 
                  class="action-btn pause"
                  @click="toggleAutomation(automation)"
                  v-if="automation.status === 'active'"
                >
                  <i class="fas fa-pause"></i>
                  Pause
                </button>
                <button 
                  class="action-btn resume"
                  @click="toggleAutomation(automation)"
                  v-if="automation.status === 'paused'"
                >
                  <i class="fas fa-play"></i>
                  Resume
                </button>
                <button 
                  class="action-btn edit"
                  @click="editAutomation(automation)"
                >
                  <i class="fas fa-edit"></i>
                  Edit
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="automations-list">
          <div 
            v-for="automation in filteredAutomations" 
            :key="automation.id"
            class="automation-list-card"
            :class="{ 'paused': automation.status === 'paused', 'error': automation.status === 'error' }"
          >
            <div class="automation-list-header">
              <div class="automation-list-info">
                <div class="automation-icon">
                  <i :class="getAutomationIcon(automation.category)"></i>
                </div>
                <div class="automation-details">
                  <h3>{{ automation.name }}</h3>
                  <p>{{ automation.description }}</p>
                  <div class="automation-meta">
                    <span class="category">{{ automation.category }}</span>
                    <span class="trigger">{{ automation.trigger }}</span>
                    <span :class="['status-badge', automation.status]">{{ automation.status }}</span>
                    <span class="runs">{{ automation.runs }} runs</span>
                  </div>
                </div>
              </div>
              <div class="automation-list-stats">
                <div class="stat-item">
                  <label>Success Rate:</label>
                  <span :class="getSuccessClass(automation.successRate)">
                    {{ automation.successRate }}%
                  </span>
                </div>
                <div class="stat-item">
                  <label>Last Run:</label>
                  <span>{{ formatDate(automation.lastRun) }}</span>
                </div>
                <div class="stat-item">
                  <label>Next Run:</label>
                  <span>{{ formatDate(automation.nextRun) }}</span>
                </div>
              </div>
              <div class="automation-list-actions">
                <button 
                  class="action-btn play"
                  @click="runAutomation(automation)"
                  :disabled="automation.status === 'running'"
                >
                  <i :class="automation.status === 'running' ? 'fas fa-spinner fa-spin' : 'fas fa-play'"></i>
                </button>
                <button 
                  class="action-btn pause"
                  @click="toggleAutomation(automation)"
                  v-if="automation.status === 'active'"
                >
                  <i class="fas fa-pause"></i>
                </button>
                <button 
                  class="action-btn resume"
                  @click="toggleAutomation(automation)"
                  v-if="automation.status === 'paused'"
                >
                  <i class="fas fa-play"></i>
                </button>
                <button 
                  class="action-btn edit"
                  @click="editAutomation(automation)"
                >
                  <i class="fas fa-edit"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Automation Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Create Automation</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="automation-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Automation Name *</label>
                <input 
                  v-model="automationForm.name" 
                  type="text" 
                  placeholder="Enter automation name"
                  required
                />
              </div>

              <div class="form-group">
                <label>Category *</label>
                <select v-model="automationForm.category" required>
                  <option value="">Select category</option>
                  <option value="data">Data Processing</option>
                  <option value="notification">Notifications</option>
                  <option value="integration">Integrations</option>
                  <option value="backup">Backup</option>
                  <option value="cleanup">Cleanup</option>
                </select>
              </div>

              <div class="form-group">
                <label>Trigger Type *</label>
                <select v-model="automationForm.trigger" required>
                  <option value="">Select trigger</option>
                  <option value="schedule">Schedule</option>
                  <option value="webhook">Webhook</option>
                  <option value="event">Event</option>
                  <option value="manual">Manual</option>
                </select>
              </div>

              <div class="form-group">
                <label>Priority</label>
                <select v-model="automationForm.priority">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            <div class="form-group full-width">
              <label>Description</label>
              <textarea 
                v-model="automationForm.description" 
                placeholder="Describe what this automation does"
                rows="3"
              ></textarea>
            </div>

            <!-- Trigger Configuration -->
            <div class="form-section">
              <h4>Trigger Configuration</h4>
              <div v-if="automationForm.trigger === 'schedule'" class="trigger-config">
                <div class="form-group">
                  <label>Schedule Type</label>
                  <select v-model="automationForm.scheduleType">
                    <option value="interval">Interval</option>
                    <option value="cron">Cron Expression</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                <div v-if="automationForm.scheduleType === 'interval'" class="form-group">
                  <label>Interval (minutes)</label>
                  <input 
                    v-model.number="automationForm.interval" 
                    type="number" 
                    min="1"
                    placeholder="60"
                  />
                </div>
                <div v-if="automationForm.scheduleType === 'cron'" class="form-group">
                  <label>Cron Expression</label>
                  <input 
                    v-model="automationForm.cronExpression" 
                    type="text" 
                    placeholder="0 0 * * *"
                  />
                </div>
              </div>
              <div v-if="automationForm.trigger === 'webhook'" class="trigger-config">
                <div class="form-group">
                  <label>Webhook URL</label>
                  <input 
                    v-model="automationForm.webhookUrl" 
                    type="text" 
                    placeholder="https://example.com/webhook"
                    readonly
                  />
                  <small>Webhook URL will be generated automatically</small>
                </div>
              </div>
              <div v-if="automationForm.trigger === 'event'" class="trigger-config">
                <div class="form-group">
                  <label>Event Type</label>
                  <select v-model="automationForm.eventType">
                    <option value="user.created">User Created</option>
                    <option value="user.updated">User Updated</option>
                    <option value="order.created">Order Created</option>
                    <option value="order.completed">Order Completed</option>
                    <option value="file.uploaded">File Uploaded</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Actions Configuration -->
            <div class="form-section">
              <h4>Actions</h4>
              <div class="actions-container">
                <div 
                  v-for="(action, index) in automationForm.actions" 
                  :key="index"
                  class="action-item"
                >
                  <div class="action-header">
                    <select v-model="action.type" class="action-type">
                      <option value="">Select action</option>
                      <option value="send_email">Send Email</option>
                      <option value="create_task">Create Task</option>
                      <option value="update_database">Update Database</option>
                      <option value="call_api">Call API</option>
                      <option value="create_file">Create File</option>
                    </select>
                    <button 
                      class="remove-btn"
                      @click="removeAction(index)"
                    >
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                  <div class="action-config">
                    <div v-if="action.type === 'send_email'" class="action-fields">
                      <input 
                        v-model="action.to" 
                        type="email" 
                        placeholder="To"
                      />
                      <input 
                        v-model="action.subject" 
                        type="text" 
                        placeholder="Subject"
                      />
                      <textarea 
                        v-model="action.message" 
                        placeholder="Message"
                        rows="3"
                      ></textarea>
                    </div>
                    <div v-if="action.type === 'create_task'" class="action-fields">
                      <input 
                        v-model="action.title" 
                        type="text" 
                        placeholder="Task title"
                      />
                      <textarea 
                        v-model="action.description" 
                        placeholder="Task description"
                        rows="2"
                      ></textarea>
                      <select v-model="action.priority">
                        <option value="low">Low Priority</option>
                        <option value="medium">Medium Priority</option>
                        <option value="high">High Priority</option>
                      </select>
                    </div>
                    <div v-if="action.type === 'call_api'" class="action-fields">
                      <input 
                        v-model="action.url" 
                        type="text" 
                        placeholder="API URL"
                      />
                      <select v-model="action.method">
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="PUT">PUT</option>
                        <option value="DELETE">DELETE</option>
                      </select>
                      <textarea 
                        v-model="action.payload" 
                        placeholder="JSON payload"
                        rows="3"
                      ></textarea>
                    </div>
                  </div>
                </div>
                <button class="add-action-btn" @click="addAction">
                  <i class="fas fa-plus"></i>
                  Add Action
                </button>
              </div>
            </div>

            <!-- Error Handling -->
            <div class="form-section">
              <h4>Error Handling</h4>
              <div class="error-handling">
                <div class="form-group">
                  <label>Retry Attempts</label>
                  <input 
                    v-model.number="automationForm.retryAttempts" 
                    type="number" 
                    min="0"
                    max="10"
                  />
                </div>
                <div class="form-group">
                  <label>Retry Delay (seconds)</label>
                  <input 
                    v-model.number="automationForm.retryDelay" 
                    type="number" 
                    min="0"
                  />
                </div>
                <div class="form-group">
                  <label>On Error</label>
                  <select v-model="automationForm.onError">
                    <option value="stop">Stop Execution</option>
                    <option value="continue">Continue on Error</option>
                    <option value="retry">Retry Only</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button 
            class="btn-primary" 
            @click="createAutomation"
            :disabled="creating"
          >
            <span v-if="!creating">Create Automation</span>
            <span v-else>Creating...</span>
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
const creating = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const triggerFilter = ref('')
const categoryFilter = ref('')
const viewMode = ref('grid')
const showCreateModal = ref(false)
const showImportModal = ref(false)
const showTemplatesModal = ref(false)
const showLogsModal = ref(false)

// Automation stats
const automationStats = reactive({
  totalAutomations: 12,
  activeAutomations: 8,
  totalRuns: 1247,
  todayRuns: 23,
  successRate: 94,
  timeSaved: 156,
  thisMonth: 45
})

// Automation form
const automationForm = reactive({
  name: '',
  description: '',
  category: '',
  trigger: '',
  priority: 'medium',
  scheduleType: 'interval',
  interval: 60,
  cronExpression: '',
  webhookUrl: '',
  eventType: '',
  actions: [],
  retryAttempts: 3,
  retryDelay: 60,
  onError: 'stop'
})

// Mock data
const automations = ref([
  {
    id: 1,
    name: 'Daily Backup',
    description: 'Automated daily backup of critical data',
    category: 'backup',
    trigger: 'schedule',
    status: 'active',
    runs: 234,
    successRate: 98,
    lastRun: '2024-01-21T02:00:00Z',
    nextRun: '2024-01-22T02:00:00Z',
    priority: 'high'
  },
  {
    id: 2,
    name: 'User Welcome Email',
    description: 'Send welcome email to new users',
    category: 'notification',
    trigger: 'event',
    status: 'active',
    runs: 156,
    successRate: 95,
    lastRun: '2024-01-21T10:30:00Z',
    nextRun: '2024-01-21T11:00:00Z',
    priority: 'medium'
  },
  {
    id: 3,
    name: 'Data Cleanup',
    description: 'Clean up old temporary files',
    category: 'cleanup',
    trigger: 'schedule',
    status: 'paused',
    runs: 89,
    successRate: 92,
    lastRun: '2024-01-20T03:00:00Z',
    nextRun: '2024-01-22T03:00:00Z',
    priority: 'low'
  },
  {
    id: 4,
    name: 'Order Processing',
    description: 'Process new orders and send notifications',
    category: 'integration',
    trigger: 'webhook',
    status: 'active',
    runs: 456,
    successRate: 96,
    lastRun: '2024-01-21T14:15:00Z',
    nextRun: '2024-01-21T15:00:00Z',
    priority: 'high'
  },
  {
    id: 5,
    name: 'Report Generation',
    description: 'Generate weekly performance reports',
    category: 'data',
    trigger: 'schedule',
    status: 'error',
    runs: 23,
    successRate: 78,
    lastRun: '2024-01-20T09:00:00Z',
    nextRun: '2024-01-27T09:00:00Z',
    priority: 'medium'
  }
])

// Computed properties
const filteredAutomations = computed(() => {
  let filtered = automations.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(automation => 
      automation.name.toLowerCase().includes(query) ||
      automation.description.toLowerCase().includes(query)
    )
  }

  // Apply status filter
  if (statusFilter.value) {
    filtered = filtered.filter(automation => automation.status === statusFilter.value)
  }

  // Apply trigger filter
  if (triggerFilter.value) {
    filtered = filtered.filter(automation => automation.trigger === triggerFilter.value)
  }

  // Apply category filter
  if (categoryFilter.value) {
    filtered = filtered.filter(automation => automation.category === categoryFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.lastRun) - new Date(a.lastRun))
})

// Methods
const loadAutomations = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/automation')
    // if (response.success) {
    //   automations.value = response.automations || []
    //   Object.assign(automationStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading automations:', error)
    showError('Failed to load automations')
  } finally {
    loading.value = false
  }
}

const filterAutomations = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (searchQuery.value || statusFilter.value || triggerFilter.value || categoryFilter.value) {
    return 'No automations match your search criteria'
  }
  return 'No automations found'
}

const getAutomationIcon = (category) => {
  const icons = {
    'data': 'fas fa-database',
    'notification': 'fas fa-bell',
    'integration': 'fas fa-plug',
    'backup': 'fas fa-save',
    'cleanup': 'fas fa-broom'
  }
  return icons[category] || 'fas fa-robot'
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

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const runAutomation = async (automation) => {
  if (automation.status === 'running') return

  try {
    // const response = await apiPost(`/automation/${automation.id}/run`)
    // if (response.success) {
    //   automation.status = 'running'
    //   showSuccess('Automation started successfully')
    // }
    
    // For demo, simulate run
    automation.status = 'running'
    showSuccess('Automation started successfully')
    
    // Simulate completion after 3 seconds
    setTimeout(() => {
      automation.status = 'active'
      automation.runs++
      automation.lastRun = new Date().toISOString()
    }, 3000)
  } catch (error) {
    console.error('Error running automation:', error)
    showError('Failed to run automation')
  }
}

const toggleAutomation = async (automation) => {
  try {
    // const response = await apiPut(`/automation/${automation.id}/toggle`)
    // if (response.success) {
    //   automation.status = automation.status === 'active' ? 'paused' : 'active'
    //   showSuccess(`Automation ${automation.status === 'active' ? 'resumed' : 'paused'}`)
    // }
    
    // For demo, simulate toggle
    automation.status = automation.status === 'active' ? 'paused' : 'active'
    showSuccess(`Automation ${automation.status === 'active' ? 'resumed' : 'paused'}`)
  } catch (error) {
    console.error('Error toggling automation:', error)
    showError('Failed to toggle automation')
  }
}

const editAutomation = (automation) => {
  // Populate form with automation data
  Object.assign(automationForm, {
    name: automation.name,
    description: automation.description,
    category: automation.category,
    trigger: automation.trigger,
    priority: automation.priority
  })
  
  showCreateModal.value = true
}

const addAction = () => {
  automationForm.actions.push({
    type: '',
    to: '',
    subject: '',
    message: '',
    title: '',
    description: '',
    priority: 'medium',
    url: '',
    method: 'GET',
    payload: ''
  })
}

const removeAction = (index) => {
  automationForm.actions.splice(index, 1)
}

const createAutomation = async () => {
  if (!automationForm.name || !automationForm.category || !automationForm.trigger) {
    showError('Please fill in all required fields')
    return
  }

  if (automationForm.actions.length === 0) {
    showError('Please add at least one action')
    return
  }

  creating.value = true
  try {
    // const response = await apiPost('/automation', automationForm)
    // if (response.success) {
    //   automations.value.unshift(response.automation)
    //   showSuccess('Automation created successfully')
    //   closeCreateModal()
    // }
    
    // For demo, simulate creation
    const newAutomation = {
      id: Date.now(),
      ...automationForm,
      status: 'active',
      runs: 0,
      successRate: 100,
      lastRun: null,
      nextRun: new Date(Date.now() + 60 * 60 * 1000).toISOString()
    }
    
    automations.value.unshift(newAutomation)
    showSuccess('Automation created successfully')
    closeCreateModal()
  } catch (error) {
    console.error('Error creating automation:', error)
    showError('Failed to create automation')
  } finally {
    creating.value = false
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetAutomationForm()
}

const resetAutomationForm = () => {
  Object.assign(automationForm, {
    name: '',
    description: '',
    category: '',
    trigger: '',
    priority: 'medium',
    scheduleType: 'interval',
    interval: 60,
    cronExpression: '',
    webhookUrl: '',
    eventType: '',
    actions: [],
    retryAttempts: 3,
    retryDelay: 60,
    onError: 'stop'
  })
}

// Lifecycle
onMounted(() => {
  loadAutomations()
})
</script>

<style scoped>
.automation {
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

.automation-count,
.run-count,
.success-status,
.time-saved {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.automation-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.run-count {
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

.time-saved {
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
.templates-btn,
.logs-btn {
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
.templates-btn:hover,
.logs-btn:hover {
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

.logs-btn {
  background: var(--warning-color);
}

.logs-btn:hover {
  background: var(--warning-hover);
}

.search-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.search-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  font-size: 1.1rem;
}

.search-box input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
}

.filter-dropdown select {
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
  cursor: pointer;
  min-width: 150px;
}

.automations-section {
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

.automations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.automation-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.automation-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.automation-card.paused {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.automation-card.error {
  border-color: var(--danger-color);
}

.automation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.automation-icon {
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

.status-badge.paused {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.draft {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.automation-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.automation-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.automation-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.category,
.trigger,
.runs {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.automation-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-item span {
  font-size: 0.8rem;
  color: var(--text-primary);
  font-weight: 600;
}

.excellent {
  color: #10b981;
}

.good {
  color: #3b82f6;
}

.fair {
  color: #f59e0b;
}

.poor {
  color: #ef4444;
}

.automation-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.action-btn:hover:not(:disabled) {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.play:hover:not(:disabled) {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.pause:hover:not(:disabled) {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.resume:hover:not(:disabled) {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.edit:hover:not(:disabled) {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.automations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.automation-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.automation-list-card:hover {
  background: var(--glass-bg-hover);
}

.automation-list-card.paused {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.automation-list-card.error {
  border-color: var(--danger-color);
}

.automation-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.automation-list-info {
  flex: 1;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.automation-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.automation-details p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
}

.automation-list-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.automation-list-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.automation-list-actions {
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
  max-width: 1200px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1400px;
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

.automation-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
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

.form-group.full-width {
  grid-column: 1 / -1;
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

.form-group small {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.form-section {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.form-section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.trigger-config {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.actions-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.action-item {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
}

.action-header {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.action-type {
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

.action-config {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-fields {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-fields input,
.action-fields select,
.action-fields textarea {
  padding: 0.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.add-action-btn {
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

.add-action-btn:hover {
  background: var(--primary-hover);
}

.error-handling {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
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
  .automation {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-box {
    min-width: 100%;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .automations-grid {
    grid-template-columns: 1fr;
  }
  
  .automation-stats {
    grid-template-columns: 1fr;
  }
  
  .automation-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .automation-list-stats {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .error-handling {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
