<template>
  <div class="debug">
    <div class="page-header">
      <h1>Debug Center</h1>
      <p>Debug applications, analyze issues, and troubleshoot problems</p>
    </div>

    <!-- Debug Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-bug"></i>
          </div>
          <div class="card-content">
            <h3>{{ debugStats.activeDebugSessions }}</h3>
            <p>Active Sessions</p>
            <span class="session-count">{{ debugStats.totalDebugSessions }} total</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon issues">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="card-content">
            <h3>{{ debugStats.openIssues }}</h3>
            <p>Open Issues</p>
            <span class="issue-count">{{ debugStats.criticalIssues }} critical</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon performance">
            <i class="fas fa-tachometer-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ debugStats.performanceScore }}%</h3>
            <p>Performance Score</p>
            <span class="performance-status" :class="getPerformanceClass(debugStats.performanceScore)">
              {{ getPerformanceStatus(debugStats.performanceScore) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon logs">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ debugStats.logEntries }}</h3>
            <p>Log Entries</p>
            <span class="log-count">{{ debugStats.errorLogs }} errors</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="session-btn" @click="showSessionModal = true">
          <i class="fas fa-play"></i>
          New Session
        </button>
        <button class="analyze-btn" @click="showAnalyzeModal = true">
          <i class="fas fa-search"></i>
          Analyze
        </button>
        <button class="profile-btn" @click="showProfileModal = true">
          <i class="fas fa-chart-line"></i>
          Profile
        </button>
        <button class="logs-btn" @click="showLogsModal = true">
          <i class="fas fa-file-alt"></i>
          Logs
        </button>
      </div>
    </div>

    <!-- Debug Sessions -->
    <div class="sessions-section">
      <div class="section-header">
        <h2>Debug Sessions</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterSessions">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="applicationFilter" @change="filterSessions">
              <option value="">All Applications</option>
              <option value="frontend">Frontend</option>
              <option value="backend">Backend</option>
              <option value="api">API</option>
              <option value="database">Database</option>
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
        <p>Loading debug sessions...</p>
      </div>

      <div v-else-if="filteredSessions.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-bug"></i>
        </div>
        <h3>No debug sessions found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showSessionModal = true">
          <i class="fas fa-play"></i>
          Start Your First Session
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="sessions-grid">
          <div 
            v-for="session in filteredSessions" 
            :key="session.id"
            class="session-card"
            :class="{ 'active': session.status === 'active', 'paused': session.status === 'paused', 'failed': session.status === 'failed' }"
          >
            <div class="session-header">
              <div class="session-icon">
                <i :class="getApplicationIcon(session.application)"></i>
              </div>
              <div class="session-status">
                <span :class="['status-badge', session.status]">{{ session.status }}</span>
              </div>
            </div>

            <div class="session-content">
              <h3>{{ session.name }}</h3>
              <p>{{ session.description }}</p>
              
              <div class="session-info">
                <span class="application">{{ session.application }}</span>
                <span class="environment">{{ session.environment }}</span>
                <span class="duration">{{ session.duration }}</span>
              </div>

              <div class="session-details">
                <div class="detail-item">
                  <label>Started:</label>
                  <span>{{ formatDateTime(session.startedAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Breakpoints:</label>
                  <span>{{ session.breakpoints }}</span>
                </div>
                <div class="detail-item">
                  <label>Memory:</label>
                  <span>{{ session.memoryUsage }}</span>
                </div>
              </div>

              <div class="session-progress" v-if="session.status === 'active'">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: session.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ session.progress }}%</span>
              </div>

              <div class="session-actions">
                <button class="action-btn view" @click="viewSession(session)">
                  <i class="fas fa-eye"></i>
                  View
                </button>
                <button class="action-btn pause" @click="pauseSession(session)" v-if="session.status === 'active'">
                  <i class="fas fa-pause"></i>
                  Pause
                </button>
                <button class="action-btn resume" @click="resumeSession(session)" v-if="session.status === 'paused'">
                  <i class="fas fa-play"></i>
                  Resume
                </button>
                <button class="action-btn stop" @click="stopSession(session)" v-if="['active', 'paused'].includes(session.status)">
                  <i class="fas fa-stop"></i>
                  Stop
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="sessions-list">
          <div 
            v-for="session in filteredSessions" 
            :key="session.id"
            class="session-list-card"
            :class="{ 'active': session.status === 'active', 'paused': session.status === 'paused', 'failed': session.status === 'failed' }"
          >
            <div class="session-list-header">
              <div class="session-list-info">
                <div class="session-icon">
                  <i :class="getApplicationIcon(session.application)"></i>
                </div>
                <div class="session-details">
                  <h3>{{ session.name }}</h3>
                  <p>{{ session.description }}</p>
                  <div class="session-info">
                    <span class="application">{{ session.application }}</span>
                    <span class="environment">{{ session.environment }}</span>
                    <span :class="['status-badge', session.status]">{{ session.status }}</span>
                    <span class="duration">{{ session.duration }}</span>
                  </div>
                </div>
              </div>
              <div class="session-list-stats">
                <div class="detail-item">
                  <label>Started:</label>
                  <span>{{ formatDateTime(session.startedAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Breakpoints:</label>
                  <span>{{ session.breakpoints }}</span>
                </div>
                <div class="detail-item">
                  <label>Memory:</label>
                  <span>{{ session.memoryUsage }}</span>
                </div>
              </div>
              <div class="session-list-actions">
                <button class="action-btn view" @click="viewSession(session)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn pause" @click="pauseSession(session)" v-if="session.status === 'active'">
                  <i class="fas fa-pause"></i>
                </button>
                <button class="action-btn resume" @click="resumeSession(session)" v-if="session.status === 'paused'">
                  <i class="fas fa-play"></i>
                </button>
                <button class="action-btn stop" @click="stopSession(session)" v-if="['active', 'paused'].includes(session.status)">
                  <i class="fas fa-stop"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Issues Tracker -->
    <div class="issues-section">
      <div class="section-header">
        <h2>Issues Tracker</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="issueFilter" @change="filterIssues">
              <option value="">All Issues</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <button class="create-issue-btn" @click="showIssueModal = true">
            <i class="fas fa-plus"></i>
            Report Issue
          </button>
        </div>
      </div>

      <div class="issues-list">
        <div 
          v-for="issue in filteredIssues" 
          :key="issue.id"
          class="issue-card"
          :class="{ 'critical': issue.severity === 'critical', 'high': issue.severity === 'high', 'medium': issue.severity === 'medium', 'low': issue.severity === 'low' }"
        >
          <div class="issue-header">
            <div class="issue-icon">
              <i :class="getIssueIcon(issue.type)"></i>
            </div>
            <div class="issue-severity">
              <span :class="['severity-badge', issue.severity]">{{ issue.severity }}</span>
            </div>
          </div>

          <div class="issue-content">
            <h3>{{ issue.title }}</h3>
            <p>{{ issue.description }}</p>
            
            <div class="issue-info">
              <span class="type">{{ issue.type }}</span>
              <span class="status">{{ issue.status }}</span>
              <span class="date">{{ formatDate(issue.createdAt) }}</span>
            </div>

            <div class="issue-details">
              <div class="detail-item">
                <label>Application:</label>
                <span>{{ issue.application }}</span>
              </div>
              <div class="detail-item">
                <label>Environment:</label>
                <span>{{ issue.environment }}</span>
              </div>
              <div class="detail-item">
                <label>Assigned:</label>
                <span>{{ issue.assignedTo }}</span>
              </div>
            </div>

            <div class="issue-actions">
              <button class="action-btn view" @click="viewIssue(issue)">
                <i class="fas fa-eye"></i>
                View
              </button>
              <button class="action-btn fix" @click="fixIssue(issue)" v-if="issue.status === 'open'">
                <i class="fas fa-wrench"></i>
                Fix
              </button>
              <button class="action-btn close" @click="closeIssue(issue)" v-if="issue.status === 'open'">
                <i class="fas fa-check"></i>
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Analysis -->
    <div class="performance-section">
      <div class="section-header">
        <h2>Performance Analysis</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="timeRange" @change="updatePerformance">
              <option value="1">Last hour</option>
              <option value="24">Last 24 hours</option>
              <option value="168">Last week</option>
              <option value="720">Last month</option>
            </select>
          </div>
          <button class="refresh-btn" @click="refreshPerformance">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="performance-grid">
        <div class="performance-card">
          <div class="performance-header">
            <h3>CPU Usage</h3>
            <span class="performance-value">{{ performance.cpuUsage }}%</span>
          </div>
          <div class="performance-chart">
            <canvas ref="cpuChart"></canvas>
          </div>
          <div class="performance-details">
            <span class="detail-item">Average: {{ performance.avgCpu }}%</span>
            <span class="detail-item">Peak: {{ performance.peakCpu }}%</span>
          </div>
        </div>

        <div class="performance-card">
          <div class="performance-header">
            <h3>Memory Usage</h3>
            <span class="performance-value">{{ performance.memoryUsage }}MB</span>
          </div>
          <div class="performance-chart">
            <canvas ref="memoryChart"></canvas>
          </div>
          <div class="performance-details">
            <span class="detail-item">Average: {{ performance.avgMemory }}MB</span>
            <span class="detail-item">Peak: {{ performance.peakMemory }}MB</span>
          </div>
        </div>

        <div class="performance-card">
          <div class="performance-header">
            <h3>Response Time</h3>
            <span class="performance-value">{{ performance.responseTime }}ms</span>
          </div>
          <div class="performance-chart">
            <canvas ref="responseChart"></canvas>
          </div>
          <div class="performance-details">
            <span class="detail-item">Average: {{ performance.avgResponse }}ms</span>
            <span class="detail-item">95th: {{ performance.p95Response }}ms</span>
          </div>
        </div>

        <div class="performance-card">
          <div class="performance-header">
            <h3>Error Rate</h3>
            <span class="performance-value">{{ performance.errorRate }}%</span>
          </div>
          <div class="performance-chart">
            <canvas ref="errorChart"></canvas>
          </div>
          <div class="performance-details">
            <span class="detail-item">Total: {{ performance.totalErrors }}</span>
            <span class="detail-item">Critical: {{ performance.criticalErrors }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- New Debug Session Modal -->
    <div v-if="showSessionModal" class="modal-overlay" @click="closeSessionModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>New Debug Session</h2>
          <button class="close-btn" @click="closeSessionModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="session-form">
            <div class="form-group">
              <label>Session Name *</label>
              <input 
                v-model="sessionForm.name" 
                type="text" 
                placeholder="Enter session name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="sessionForm.description" 
                placeholder="Describe what you're debugging"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Application *</label>
                <select v-model="sessionForm.application" required>
                  <option value="frontend">Frontend</option>
                  <option value="backend">Backend</option>
                  <option value="api">API</option>
                  <option value="database">Database</option>
                </select>
              </div>

              <div class="form-group">
                <label>Environment *</label>
                <select v-model="sessionForm.environment" required>
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                  <option value="testing">Testing</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Debug Configuration</label>
              <div class="debug-config">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sessionForm.config.enableBreakpoints"
                  />
                  <span>Enable breakpoints</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sessionForm.config.enableLogging"
                  />
                  <span>Enable logging</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sessionForm.config.enableProfiling"
                  />
                  <span>Enable profiling</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sessionForm.config.enableMemoryTracking"
                  />
                  <span>Enable memory tracking</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Breakpoints</label>
              <div class="breakpoints-container">
                <div 
                  v-for="(breakpoint, index) in sessionForm.breakpoints" 
                  :key="index"
                  class="breakpoint-item"
                >
                  <input 
                    v-model="breakpoint.file" 
                    type="text" 
                    placeholder="File path"
                  />
                  <input 
                    v-model="breakpoint.line" 
                    type="number" 
                    placeholder="Line number"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeBreakpoint(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-breakpoint-btn" @click="addBreakpoint">
                  <i class="fas fa-plus"></i>
                  Add Breakpoint
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>Options</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sessionForm.autoStart"
                  />
                  <span>Auto start session</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sessionForm.saveSession"
                  />
                  <span>Save session data</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sessionForm.notifyOnComplete"
                  />
                  <span>Notify on completion</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeSessionModal">Cancel</button>
          <button class="btn-primary" @click="createSession">
            <i class="fas fa-play"></i>
            Start Session
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Chart } from 'chart.js/auto'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const statusFilter = ref('')
const applicationFilter = ref('')
const issueFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('24')
const showSessionModal = ref(false)
const showAnalyzeModal = ref(false)
const showProfileModal = ref(false)
const showLogsModal = ref(false)
const showIssueModal = ref(false)

// Chart instances
const cpuChart = ref(null)
const memoryChart = ref(null)
const responseChart = ref(null)
const errorChart = ref(null)

// Debug stats
const debugStats = reactive({
  activeDebugSessions: 3,
  totalDebugSessions: 45,
  openIssues: 12,
  criticalIssues: 2,
  performanceScore: 78,
  logEntries: 1234,
  errorLogs: 23
})

// Performance data
const performance = reactive({
  cpuUsage: 45,
  avgCpu: 42,
  peakCpu: 78,
  memoryUsage: 512,
  avgMemory: 485,
  peakMemory: 1024,
  responseTime: 125,
  avgResponse: 118,
  p95Response: 250,
  errorRate: 2.3,
  totalErrors: 23,
  criticalErrors: 2
})

// Session form
const sessionForm = reactive({
  name: '',
  description: '',
  application: 'frontend',
  environment: 'development',
  config: {
    enableBreakpoints: true,
    enableLogging: true,
    enableProfiling: false,
    enableMemoryTracking: false
  },
  breakpoints: [],
  autoStart: true,
  saveSession: true,
  notifyOnComplete: true
})

// Mock data
const sessions = ref([
  {
    id: 1,
    name: 'Frontend Performance Debug',
    description: 'Debugging frontend performance issues in dashboard',
    status: 'active',
    application: 'frontend',
    environment: 'development',
    duration: '15 min 30 sec',
    startedAt: '2024-01-21T10:30:00Z',
    breakpoints: 5,
    memoryUsage: '256MB',
    progress: 67
  },
  {
    id: 2,
    name: 'API Response Time Issue',
    description: 'Investigating slow API response times',
    status: 'paused',
    application: 'api',
    environment: 'staging',
    duration: '8 min 45 sec',
    startedAt: '2024-01-21T09:45:00Z',
    breakpoints: 3,
    memoryUsage: '128MB',
    progress: 45
  },
  {
    id: 3,
    name: 'Database Connection Debug',
    description: 'Debugging database connection pool issues',
    status: 'completed',
    application: 'database',
    environment: 'testing',
    duration: '25 min 15 sec',
    startedAt: '2024-01-21T08:00:00Z',
    breakpoints: 8,
    memoryUsage: '512MB',
    progress: 100
  },
  {
    id: 4,
    name: 'Backend Memory Leak',
    description: 'Investigating memory leak in backend service',
    status: 'failed',
    application: 'backend',
    environment: 'production',
    duration: 'Failed',
    startedAt: '2024-01-20T16:30:00Z',
    breakpoints: 12,
    memoryUsage: '1024MB',
    progress: 0
  }
])

const issues = ref([
  {
    id: 1,
    title: 'Frontend Memory Leak',
    description: 'Memory usage increases continuously in dashboard component',
    type: 'memory',
    severity: 'critical',
    status: 'open',
    application: 'frontend',
    environment: 'production',
    assignedTo: 'John Doe',
    createdAt: '2024-01-21T09:00:00Z'
  },
  {
    id: 2,
    title: 'API Timeout Issues',
    description: 'API endpoints timing out after 30 seconds',
    type: 'performance',
    severity: 'high',
    status: 'open',
    application: 'api',
    environment: 'staging',
    assignedTo: 'Jane Smith',
    createdAt: '2024-01-20T14:30:00Z'
  },
  {
    id: 3,
    title: 'Database Connection Pool Exhaustion',
    description: 'Database connection pool running out of connections',
    type: 'database',
    severity: 'medium',
    status: 'open',
    application: 'database',
    environment: 'production',
    assignedTo: 'Bob Johnson',
    createdAt: '2024-01-19T11:15:00Z'
  }
])

// Computed properties
const filteredSessions = computed(() => {
  let filtered = sessions.value

  if (statusFilter.value) {
    filtered = filtered.filter(session => session.status === statusFilter.value)
  }

  if (applicationFilter.value) {
    filtered = filtered.filter(session => session.application === applicationFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.startedAt) - new Date(a.startedAt))
})

const filteredIssues = computed(() => {
  let filtered = issues.value

  if (issueFilter.value) {
    filtered = filtered.filter(issue => issue.severity === issueFilter.value)
  }

  return filtered.sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
    return severityOrder[a.severity] - severityOrder[b.severity]
  })
})

// Methods
const loadDebugData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/debug')
    // if (response.success) {
    //   sessions.value = response.sessions || []
    //   issues.value = response.issues || []
    //   Object.assign(debugStats, response.stats)
    //   Object.assign(performance, response.performance)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading debug data:', error)
    showError('Failed to load debug data')
  } finally {
    loading.value = false
  }
}

const filterSessions = () => {
  // This is reactive, no additional action needed
}

const filterIssues = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || applicationFilter.value) {
    return 'No debug sessions match your filter criteria'
  }
  return 'No debug sessions found'
}

const getApplicationIcon = (application) => {
  const icons = {
    'frontend': 'fas fa-desktop',
    'backend': 'fas fa-server',
    'api': 'fas fa-plug',
    'database': 'fas fa-database'
  }
  return icons[application] || 'fas fa-bug'
}

const getIssueIcon = (type) => {
  const icons = {
    'memory': 'fas fa-memory',
    'performance': 'fas fa-tachometer-alt',
    'database': 'fas fa-database',
    'network': 'fas fa-network-wired',
    'security': 'fas fa-shield-alt'
  }
  return icons[type] || 'fas fa-exclamation-triangle'
}

const getPerformanceClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 75) return 'good'
  if (score >= 60) return 'fair'
  return 'poor'
}

const getPerformanceStatus = (score) => {
  if (score >= 90) return 'Excellent'
  if (score >= 75) return 'Good'
  if (score >= 60) return 'Fair'
  return 'Needs Improvement'
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const viewSession = (session) => {
  // Open session details modal or navigate to detailed view
  showSuccess(`Viewing debug session: ${session.name}`)
}

const pauseSession = async (session) => {
  try {
    // const response = await apiPost(`/debug/sessions/${session.id}/pause`)
    // if (response.success) {
    //   session.status = 'paused'
    //   showSuccess('Session paused successfully')
    // }
    
    // For demo, simulate pause
    session.status = 'paused'
    showSuccess('Session paused successfully')
  } catch (error) {
    console.error('Error pausing session:', error)
    showError('Failed to pause session')
  }
}

const resumeSession = async (session) => {
  try {
    // const response = await apiPost(`/debug/sessions/${session.id}/resume`)
    // if (response.success) {
    //   session.status = 'active'
    //   showSuccess('Session resumed successfully')
    // }
    
    // For demo, simulate resume
    session.status = 'active'
    showSuccess('Session resumed successfully')
  } catch (error) {
    console.error('Error resuming session:', error)
    showError('Failed to resume session')
  }
}

const stopSession = async (session) => {
  const confirmed = await showConfirm(`Are you sure you want to stop debug session "${session.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/debug/sessions/${session.id}/stop`)
    // if (response.success) {
    //   session.status = 'completed'
    //   session.progress = 100
    //   showSuccess('Session stopped successfully')
    // }
    
    // For demo, simulate stop
    session.status = 'completed'
    session.progress = 100
    showSuccess('Session stopped successfully')
  } catch (error) {
    console.error('Error stopping session:', error)
    showError('Failed to stop session')
  }
}

const viewIssue = (issue) => {
  // Open issue details modal or navigate to detailed view
  showSuccess(`Viewing issue: ${issue.title}`)
}

const fixIssue = async (issue) => {
  try {
    // const response = await apiPost(`/debug/issues/${issue.id}/fix`)
    // if (response.success) {
    //   issue.status = 'in-progress'
    //   showSuccess('Issue fix initiated')
    // }
    
    // For demo, simulate fix
    issue.status = 'in-progress'
    showSuccess('Issue fix initiated')
  } catch (error) {
    console.error('Error fixing issue:', error)
    showError('Failed to fix issue')
  }
}

const closeIssue = async (issue) => {
  const confirmed = await showConfirm(`Are you sure you want to close issue "${issue.title}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/debug/issues/${issue.id}/close`)
    // if (response.success) {
    //   issue.status = 'closed'
    //   showSuccess('Issue closed successfully')
    // }
    
    // For demo, simulate close
    issue.status = 'closed'
    showSuccess('Issue closed successfully')
  } catch (error) {
    console.error('Error closing issue:', error)
    showError('Failed to close issue')
  }
}

const addBreakpoint = () => {
  sessionForm.breakpoints.push({ file: '', line: '' })
}

const removeBreakpoint = (index) => {
  sessionForm.breakpoints.splice(index, 1)
}

const createSession = async () => {
  if (!sessionForm.name || !sessionForm.application || !sessionForm.environment) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/debug/sessions', sessionForm)
    // if (response.success) {
    //   sessions.value.unshift(response.session)
    //   showSuccess('Debug session created successfully')
    //   closeSessionModal()
    //   resetSessionForm()
    // }
    
    // For demo, simulate creation
    const newSession = {
      id: Date.now(),
      ...sessionForm,
      status: sessionForm.autoStart ? 'active' : 'paused',
      duration: sessionForm.autoStart ? '0 sec' : 'Pending',
      startedAt: sessionForm.autoStart ? new Date().toISOString() : null,
      breakpoints: sessionForm.breakpoints.length,
      memoryUsage: '0MB',
      progress: 0
    }
    
    sessions.value.unshift(newSession)
    showSuccess('Debug session created successfully')
    closeSessionModal()
    resetSessionForm()
  } catch (error) {
    console.error('Error creating session:', error)
    showError('Failed to create debug session')
  }
}

const closeSessionModal = () => {
  showSessionModal.value = false
  resetSessionForm()
}

const resetSessionForm = () => {
  Object.assign(sessionForm, {
    name: '',
    description: '',
    application: 'frontend',
    environment: 'development',
    config: {
      enableBreakpoints: true,
      enableLogging: true,
      enableProfiling: false,
      enableMemoryTracking: false
    },
    breakpoints: [],
    autoStart: true,
    saveSession: true,
    notifyOnComplete: true
  })
}

const updatePerformance = async () => {
  try {
    // const response = await apiGet('/debug/performance', { timeRange: timeRange.value })
    // if (response.success) {
    //   Object.assign(performance, response.performance)
    //   updateCharts()
    // }
    
    // For demo, simulate update
    updateCharts()
  } catch (error) {
    console.error('Error updating performance:', error)
    showError('Failed to update performance data')
  }
}

const refreshPerformance = async () => {
  try {
    // const response = await apiGet('/debug/performance/refresh')
    // if (response.success) {
    //   Object.assign(performance, response.performance)
    //   updateCharts()
    // }
    
    // For demo, simulate refresh
    updateCharts()
    showSuccess('Performance data refreshed successfully')
  } catch (error) {
    console.error('Error refreshing performance:', error)
    showError('Failed to refresh performance data')
  }
}

const initCharts = () => {
  // Initialize CPU chart
  if (cpuChart.value) cpuChart.value.destroy()
  cpuChart.value = new Chart(cpuChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 60 }, (_, i) => `${i}s`),
      datasets: [{
        label: 'CPU Usage %',
        data: Array.from({ length: 60 }, () => Math.random() * 100),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  })

  // Initialize Memory chart
  if (memoryChart.value) memoryChart.value.destroy()
  memoryChart.value = new Chart(memoryChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 60 }, (_, i) => `${i}s`),
      datasets: [{
        label: 'Memory Usage MB',
        data: Array.from({ length: 60 }, () => Math.random() * 1024),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Response Time chart
  if (responseChart.value) responseChart.value.destroy()
  responseChart.value = new Chart(responseChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 60 }, (_, i) => `${i}s`),
      datasets: [{
        label: 'Response Time ms',
        data: Array.from({ length: 60 }, () => Math.random() * 500),
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Error Rate chart
  if (errorChart.value) errorChart.value.destroy()
  errorChart.value = new Chart(errorChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 60 }, (_, i) => `${i}s`),
      datasets: [{
        label: 'Error Rate %',
        data: Array.from({ length: 60 }, () => Math.random() * 10),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })
}

const updateCharts = () => {
  // Update charts with new data
  if (cpuChart.value) {
    cpuChart.value.data.datasets[0].data = Array.from({ length: 60 }, () => Math.random() * 100)
    cpuChart.value.update('none')
  }

  if (memoryChart.value) {
    memoryChart.value.data.datasets[0].data = Array.from({ length: 60 }, () => Math.random() * 1024)
    memoryChart.value.update('none')
  }

  if (responseChart.value) {
    responseChart.value.data.datasets[0].data = Array.from({ length: 60 }, () => Math.random() * 500)
    responseChart.value.update('none')
  }

  if (errorChart.value) {
    errorChart.value.data.datasets[0].data = Array.from({ length: 60 }, () => Math.random() * 10)
    errorChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadDebugData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (cpuChart.value) cpuChart.value.destroy()
  if (memoryChart.value) memoryChart.value.destroy()
  if (responseChart.value) responseChart.value.destroy()
  if (errorChart.value) errorChart.value.destroy()
})
</script>

<style scoped>
.debug {
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

.card-icon.issues {
  background: var(--danger-color);
}

.card-icon.performance {
  background: var(--warning-color);
}

.card-icon.logs {
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

.session-count,
.issue-count,
.performance-status,
.log-count {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.session-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.issue-count {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.performance-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.performance-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.performance-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.performance-status.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.log-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
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

.session-btn,
.analyze-btn,
.profile-btn,
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

.session-btn:hover,
.analyze-btn:hover,
.profile-btn:hover,
.logs-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.analyze-btn {
  background: var(--info-color);
}

.analyze-btn:hover {
  background: var(--info-hover);
}

.profile-btn {
  background: var(--warning-color);
}

.profile-btn:hover {
  background: var(--warning-hover);
}

.logs-btn {
  background: var(--success-color);
}

.logs-btn:hover {
  background: var(--success-hover);
}

.sessions-section,
.issues-section,
.performance-section {
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

.create-issue-btn,
.refresh-btn {
  padding: 0.75rem 1.25rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.create-issue-btn:hover,
.refresh-btn:hover {
  background: var(--primary-hover);
}

.time-range select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
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

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.session-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.session-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.session-card.active {
  border-color: var(--success-color);
}

.session-card.paused {
  border-color: var(--warning-color);
}

.session-card.failed {
  border-color: var(--danger-color);
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.session-icon {
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

.status-badge.completed {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.session-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.session-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.session-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.application,
.environment,
.duration {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.session-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.detail-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.session-progress {
  margin-bottom: 1rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.session-actions {
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

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.view:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.pause:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.resume:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.stop:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.session-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.session-list-card:hover {
  background: var(--glass-bg-hover);
}

.session-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.session-list-info {
  flex: 1;
}

.session-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.session-list-actions {
  display: flex;
  gap: 0.5rem;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.issue-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.issue-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.issue-card.critical {
  border-color: var(--danger-color);
}

.issue-card.high {
  border-color: var(--warning-color);
}

.issue-card.medium {
  border-color: var(--info-color);
}

.issue-card.low {
  border-color: var(--text-tertiary);
}

.issue-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.issue-icon {
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

.severity-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.severity-badge.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.severity-badge.high {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.severity-badge.medium {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.severity-badge.low {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.issue-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.issue-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.issue-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.status,
.date {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.issue-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.issue-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn.fix:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.close:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.performance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.performance-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.performance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.performance-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.performance-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.performance-chart {
  height: 150px;
  margin-bottom: 1rem;
}

.performance-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-secondary);
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

.session-form {
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

.debug-config,
.options-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
}

.breakpoints-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.breakpoint-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.breakpoint-item input {
  flex: 1;
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
}

.breakpoint-item input[type="number"] {
  width: 100px;
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
  font-size: 0.9rem;
}

.remove-btn:hover {
  background: var(--danger-hover);
}

.add-breakpoint-btn {
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

.add-breakpoint-btn:hover {
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
  display: flex;
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

@media (max-width: 768px) {
  .debug {
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
  
  .sessions-grid {
    grid-template-columns: 1fr;
  }
  
  .session-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .session-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .performance-grid {
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
