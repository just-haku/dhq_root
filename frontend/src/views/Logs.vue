<template>
  <div class="logs">
    <div class="page-header">
      <h1>System Logs</h1>
      <p>View and manage system logs and events</p>
    </div>

    <!-- Log Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ logStats.totalLogs }}</h3>
            <p>Total Logs</p>
            <span class="log-count">{{ logStats.todayLogs }} today</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon errors">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="card-content">
            <h3>{{ logStats.errorCount }}</h3>
            <p>Errors</p>
            <span class="error-status" :class="getErrorClass(logStats.errorCount)">
              {{ getErrorStatus(logStats.errorCount) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon warnings">
            <i class="fas fa-exclamation-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ logStats.warningCount }}</h3>
            <p>Warnings</p>
            <span class="warning-count">{{ logStats.recentWarnings }} recent</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon size">
            <i class="fas fa-database"></i>
          </div>
          <div class="card-content">
            <h3>{{ logStats.totalSize }}</h3>
            <p>Total Size</p>
            <span class="size-status">{{ logStats.avgSize }} avg</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="refresh-btn" @click="refreshLogs">
          <i class="fas fa-sync"></i>
          Refresh Logs
        </button>
        <button class="export-btn" @click="exportLogs">
          <i class="fas fa-download"></i>
          Export Logs
        </button>
        <button class="clear-btn" @click="showClearModal = true">
          <i class="fas fa-trash"></i>
          Clear Logs
        </button>
        <button class="settings-btn" @click="showSettingsModal = true">
          <i class="fas fa-cog"></i>
          Settings
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
            placeholder="Search logs..."
            @input="filterLogs"
          />
        </div>
        <div class="filter-dropdown">
          <select v-model="levelFilter" @change="filterLogs">
            <option value="">All Levels</option>
            <option value="debug">Debug</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="sourceFilter" @change="filterLogs">
            <option value="">All Sources</option>
            <option value="application">Application</option>
            <option value="database">Database</option>
            <option value="auth">Authentication</option>
            <option value="api">API</option>
            <option value="system">System</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="timeFilter" @change="filterLogs">
            <option value="">All Time</option>
            <option value="1">Last Hour</option>
            <option value="6">Last 6 Hours</option>
            <option value="24">Last 24 Hours</option>
            <option value="168">Last Week</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="logs-section">
      <div class="section-header">
        <h2>Log Entries</h2>
        <div class="header-actions">
          <div class="auto-refresh">
            <label class="switch">
              <input 
                type="checkbox" 
                v-model="autoRefresh"
                @change="toggleAutoRefresh"
              />
              <span class="slider"></span>
            </label>
            <span>Auto Refresh</span>
          </div>
          <div class="view-toggle">
            <button 
              :class="['view-btn', { active: viewMode === 'table' }]"
              @click="viewMode = 'table'"
            >
              <i class="fas fa-table"></i>
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'json' }]"
              @click="viewMode = 'json'"
            >
              <i class="fas fa-code"></i>
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading logs...</p>
      </div>

      <div v-else-if="filteredLogs.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-file-alt"></i>
        </div>
        <h3>No logs found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else>
        <!-- Table View -->
        <div v-if="viewMode === 'table'" class="logs-table-container">
          <table class="logs-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Level</th>
                <th>Source</th>
                <th>Message</th>
                <th>Context</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="log in paginatedLogs" 
                :key="log.id"
                :class="['log-row', log.level]"
              >
                <td class="timestamp">{{ formatDateTime(log.timestamp) }}</td>
                <td>
                  <span :class="['level-badge', log.level]">{{ log.level }}</span>
                </td>
                <td>{{ log.source }}</td>
                <td class="message">{{ log.message }}</td>
                <td class="context">
                  <button 
                    class="context-btn"
                    @click="viewLogDetails(log)"
                  >
                    <i class="fas fa-eye"></i>
                    View
                  </button>
                </td>
                <td>
                  <button 
                    class="action-btn copy"
                    @click="copyLog(log)"
                    title="Copy log"
                  >
                    <i class="fas fa-copy"></i>
                  </button>
                  <button 
                    class="action-btn delete"
                    @click="deleteLog(log)"
                    title="Delete log"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- JSON View -->
        <div v-else class="logs-json-container">
          <div 
            v-for="log in paginatedLogs" 
            :key="log.id"
            :class="['log-json', log.level]"
          >
            <div class="log-json-header">
              <span class="timestamp">{{ formatDateTime(log.timestamp) }}</span>
              <span :class="['level-badge', log.level]">{{ log.level }}</span>
              <span class="source">{{ log.source }}</span>
              <div class="log-actions">
                <button 
                  class="action-btn copy"
                  @click="copyLog(log)"
                  title="Copy log"
                >
                  <i class="fas fa-copy"></i>
                </button>
                <button 
                  class="action-btn delete"
                  @click="deleteLog(log)"
                  title="Delete log"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
            <pre class="log-json-content">{{ JSON.stringify(log, null, 2) }}</pre>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination">
          <div class="pagination-info">
            <span>Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredLogs.length }} logs</span>
          </div>
          <div class="pagination-controls">
            <button 
              class="pagination-btn"
              @click="previousPage"
              :disabled="currentPage === 1"
            >
              <i class="fas fa-chevron-left"></i>
            </button>
            <span class="page-number">Page {{ currentPage }}</span>
            <button 
              class="pagination-btn"
              @click="nextPage"
              :disabled="currentPage === totalPages"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Log Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Log Details</h2>
          <button class="close-btn" @click="closeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="log-details">
            <div class="detail-section">
              <h3>Basic Information</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Timestamp:</label>
                  <span>{{ formatDateTime(selectedLog?.timestamp) }}</span>
                </div>
                <div class="detail-item">
                  <label>Level:</label>
                  <span :class="['level-badge', selectedLog?.level]">{{ selectedLog?.level }}</span>
                </div>
                <div class="detail-item">
                  <label>Source:</label>
                  <span>{{ selectedLog?.source }}</span>
                </div>
                <div class="detail-item">
                  <label>Message:</label>
                  <span>{{ selectedLog?.message }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section" v-if="selectedLog?.context">
              <h3>Context</h3>
              <pre class="context-json">{{ JSON.stringify(selectedLog.context, null, 2) }}</pre>
            </div>

            <div class="detail-section" v-if="selectedLog?.stackTrace">
              <h3>Stack Trace</h3>
              <pre class="stack-trace">{{ selectedLog.stackTrace }}</pre>
            </div>

            <div class="detail-section" v-if="selectedLog?.metadata">
              <h3>Metadata</h3>
              <div class="metadata-grid">
                <div 
                  v-for="(value, key) in selectedLog.metadata" 
                  :key="key"
                  class="metadata-item"
                >
                  <label>{{ key }}:</label>
                  <span>{{ value }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeDetailsModal">Close</button>
          <button class="btn-primary" @click="copyLog(selectedLog)">
            <i class="fas fa-copy"></i>
            Copy Log
          </button>
        </div>
      </div>
    </div>

    <!-- Clear Logs Modal -->
    <div v-if="showClearModal" class="modal-overlay" @click="closeClearModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Clear Logs</h2>
          <button class="close-btn" @click="closeClearModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="clear-options">
            <div class="form-group">
              <label>Clear Options</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="clearOptions.debug"
                  />
                  <span>Debug logs</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="clearOptions.info"
                  />
                  <span>Info logs</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="clearOptions.warning"
                  />
                  <span>Warning logs</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="clearOptions.error"
                  />
                  <span>Error logs</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="clearOptions.critical"
                  />
                  <span>Critical logs</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Time Range</label>
              <select v-model="clearOptions.timeRange">
                <option value="1">Last Hour</option>
                <option value="6">Last 6 Hours</option>
                <option value="24">Last 24 Hours</option>
                <option value="168">Last Week</option>
                <option value="720">Last Month</option>
                <option value="all">All Time</option>
              </select>
            </div>

            <div class="form-group">
              <label>Source</label>
              <select v-model="clearOptions.source">
                <option value="">All Sources</option>
                <option value="application">Application</option>
                <option value="database">Database</option>
                <option value="auth">Authentication</option>
                <option value="api">API</option>
                <option value="system">System</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeClearModal">Cancel</button>
          <button class="btn-danger" @click="clearLogs">
            <i class="fas fa-trash"></i>
            Clear Logs
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { apiGet, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const searchQuery = ref('')
const levelFilter = ref('')
const sourceFilter = ref('')
const timeFilter = ref('')
const viewMode = ref('table')
const autoRefresh = ref(false)
const refreshInterval = ref(null)
const currentPage = ref(1)
const pageSize = ref(50)
const showDetailsModal = ref(false)
const showClearModal = ref(false)
const showSettingsModal = ref(false)
const selectedLog = ref(null)

// Log stats
const logStats = reactive({
  totalLogs: 15420,
  todayLogs: 342,
  errorCount: 23,
  warningCount: 156,
  recentWarnings: 12,
  totalSize: '2.4GB',
  avgSize: '156KB'
})

// Clear options
const clearOptions = reactive({
  debug: true,
  info: false,
  warning: true,
  error: false,
  critical: false,
  timeRange: '24',
  source: ''
})

// Mock data
const logs = ref([
  {
    id: 1,
    timestamp: '2024-01-21T10:30:00Z',
    level: 'info',
    source: 'application',
    message: 'User login successful',
    context: { userId: '12345', ip: '192.168.1.1' },
    metadata: { sessionId: 'abc123', userAgent: 'Mozilla/5.0' }
  },
  {
    id: 2,
    timestamp: '2024-01-21T10:25:00Z',
    level: 'warning',
    source: 'database',
    message: 'Database connection slow',
    context: { query: 'SELECT * FROM users', duration: 2500 },
    metadata: { connectionId: 'conn_456', database: 'main' }
  },
  {
    id: 3,
    timestamp: '2024-01-21T10:20:00Z',
    level: 'error',
    source: 'api',
    message: 'API request failed',
    context: { endpoint: '/api/users', status: 500 },
    stackTrace: 'Error: Internal Server Error\n    at APIHandler.handle (/app/api/handler.js:45:15)',
    metadata: { requestId: 'req_789', method: 'GET' }
  },
  {
    id: 4,
    timestamp: '2024-01-21T10:15:00Z',
    level: 'debug',
    source: 'auth',
    message: 'Token validation successful',
    context: { tokenId: 'token_123', userId: '12345' },
    metadata: { expiresAt: '2024-01-21T12:15:00Z' }
  },
  {
    id: 5,
    timestamp: '2024-01-21T10:10:00Z',
    level: 'critical',
    source: 'system',
    message: 'System memory usage critical',
    context: { usage: '95%', available: '512MB' },
    metadata: { server: 'web-01', pid: 1234 }
  }
])

// Computed properties
const filteredLogs = computed(() => {
  let filtered = logs.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(log => 
      log.message.toLowerCase().includes(query) ||
      log.source.toLowerCase().includes(query)
    )
  }

  // Apply level filter
  if (levelFilter.value) {
    filtered = filtered.filter(log => log.level === levelFilter.value)
  }

  // Apply source filter
  if (sourceFilter.value) {
    filtered = filtered.filter(log => log.source === sourceFilter.value)
  }

  // Apply time filter
  if (timeFilter.value) {
    const hours = parseInt(timeFilter.value)
    const cutoffDate = new Date(Date.now() - hours * 60 * 60 * 1000)
    filtered = filtered.filter(log => new Date(log.timestamp) >= cutoffDate)
  }

  return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLogs.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredLogs.value.length / pageSize.value)
})

const startIndex = computed(() => {
  return (currentPage.value - 1) * pageSize.value
})

const endIndex = computed(() => {
  const end = startIndex.value + pageSize.value
  return Math.min(end, filteredLogs.value.length)
})

// Methods
const loadLogs = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/logs')
    // if (response.success) {
    //   logs.value = response.logs || []
    //   Object.assign(logStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading logs:', error)
    showError('Failed to load logs')
  } finally {
    loading.value = false
  }
}

const filterLogs = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (searchQuery.value || levelFilter.value || sourceFilter.value || timeFilter.value) {
    return 'No logs match your search criteria'
  }
  return 'No logs found'
}

const getErrorClass = (count) => {
  if (count === 0) return 'none'
  if (count <= 5) return 'low'
  if (count <= 20) return 'medium'
  return 'high'
}

const getErrorStatus = (count) => {
  if (count === 0) return 'None'
  if (count <= 5) return 'Low'
  if (count <= 20) return 'Medium'
  return 'High'
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const viewLogDetails = (log) => {
  selectedLog.value = log
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedLog.value = null
}

const copyLog = async (log) => {
  try {
    const logText = JSON.stringify(log, null, 2)
    await navigator.clipboard.writeText(logText)
    showSuccess('Log copied to clipboard')
  } catch (error) {
    showError('Failed to copy log')
  }
}

const deleteLog = async (log) => {
  const confirmed = await showConfirm('Are you sure you want to delete this log?')
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/logs/${log.id}`)
    // if (response.success) {
    //   const index = logs.value.findIndex(l => l.id === log.id)
    //   if (index > -1) {
    //     logs.value.splice(index, 1)
    //     showSuccess('Log deleted successfully')
    //   }
    // }
    
    // For demo, simulate deletion
    const index = logs.value.findIndex(l => l.id === log.id)
    if (index > -1) {
      logs.value.splice(index, 1)
      showSuccess('Log deleted successfully')
    }
  } catch (error) {
    console.error('Error deleting log:', error)
    showError('Failed to delete log')
  }
}

const refreshLogs = async () => {
  await loadLogs()
  showSuccess('Logs refreshed successfully')
}

const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  refreshInterval.value = setInterval(() => {
    loadLogs()
  }, 30000) // Refresh every 30 seconds
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

const exportLogs = async () => {
  try {
    // const response = await apiPost('/logs/export', {
    //   filters: { level: levelFilter.value, source: sourceFilter.value, time: timeFilter.value }
    // })
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `logs-${new Date().toISOString().split('T')[0]}.json`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Logs exported successfully')
    // }
    
    // For demo, simulate export
    showSuccess('Logs exported successfully')
  } catch (error) {
    console.error('Error exporting logs:', error)
    showError('Failed to export logs')
  }
}

const clearLogs = async () => {
  const confirmed = await showConfirm('Are you sure you want to clear the selected logs? This action cannot be undone.')
  if (!confirmed) return

  try {
    // const response = await apiDelete('/logs/clear', clearOptions)
    // if (response.success) {
    //   await loadLogs()
    //   showSuccess('Logs cleared successfully')
    //   closeClearModal()
    // }
    
    // For demo, simulate clear
    showSuccess('Logs cleared successfully')
    closeClearModal()
  } catch (error) {
    console.error('Error clearing logs:', error)
    showError('Failed to clear logs')
  }
}

const closeClearModal = () => {
  showClearModal.value = false
  resetClearOptions()
}

const resetClearOptions = () => {
  Object.assign(clearOptions, {
    debug: true,
    info: false,
    warning: true,
    error: false,
    critical: false,
    timeRange: '24',
    source: ''
  })
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

// Lifecycle
onMounted(() => {
  loadLogs()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.logs {
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

.card-icon.errors {
  background: var(--danger-color);
}

.card-icon.warnings {
  background: var(--warning-color);
}

.card-icon.size {
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

.log-count,
.error-status,
.warning-count,
.size-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.log-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.error-status.none {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.error-status.low {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.error-status.medium {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.error-status.high {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.warning-count {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.size-status {
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

.refresh-btn,
.export-btn,
.clear-btn,
.settings-btn {
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

.refresh-btn:hover,
.export-btn:hover,
.clear-btn:hover,
.settings-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.export-btn {
  background: var(--success-color);
}

.export-btn:hover {
  background: var(--success-hover);
}

.clear-btn {
  background: var(--danger-color);
}

.clear-btn:hover {
  background: var(--danger-hover);
}

.settings-btn {
  background: var(--info-color);
}

.settings-btn:hover {
  background: var(--info-hover);
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

.logs-section {
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

.auto-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch .slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--text-tertiary);
  transition: 0.4s;
  border-radius: 24px;
}

.switch .slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

.switch input:checked + .slider {
  background-color: var(--primary-color);
}

.switch input:checked + .slider:before {
  transform: translateX(26px);
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

.logs-table-container {
  overflow-x: auto;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.logs-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.log-row {
  transition: background 0.3s ease;
}

.log-row:hover {
  background: var(--glass-bg-hover);
}

.log-row.debug {
  border-left: 4px solid var(--info-color);
}

.log-row.info {
  border-left: 4px solid var(--primary-color);
}

.log-row.warning {
  border-left: 4px solid var(--warning-color);
}

.log-row.error {
  border-left: 4px solid var(--danger-color);
}

.log-row.critical {
  border-left: 4px solid var(--danger-color);
  background: rgba(239, 68, 68, 0.05);
}

.timestamp {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.level-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.level-badge.debug {
  background: rgba(6, 182, 212, 0.1);
  color: #06b6d4;
}

.level-badge.info {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.level-badge.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.level-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.level-badge.critical {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.message {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.context-btn {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.context-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
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

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.logs-json-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.log-json {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
}

.log-json.debug {
  border-left: 4px solid var(--info-color);
}

.log-json.info {
  border-left: 4px solid var(--primary-color);
}

.log-json.warning {
  border-left: 4px solid var(--warning-color);
}

.log-json.error {
  border-left: 4px solid var(--danger-color);
}

.log-json.critical {
  border-left: 4px solid var(--danger-color);
  background: rgba(239, 68, 68, 0.05);
}

.log-json-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}

.log-json-content {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: var(--text-primary);
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--glass-border);
}

.pagination-info {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number {
  color: var(--text-primary);
  font-weight: 600;
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

.log-details {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.detail-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.detail-item span {
  color: var(--text-primary);
  font-weight: 500;
}

.context-json,
.stack-trace {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--text-primary);
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metadata-item label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.metadata-item span {
  color: var(--text-primary);
  font-weight: 500;
}

.clear-options {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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

.form-group select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary, .btn-danger {
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

.btn-danger {
  background: var(--danger-color);
  color: white;
}

.btn-danger:hover {
  background: var(--danger-hover);
}

@media (max-width: 768px) {
  .logs {
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
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
