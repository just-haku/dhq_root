<template>
  <div class="database">
    <div class="page-header">
      <h1>Database Management</h1>
      <p>Monitor and manage database performance and operations</p>
    </div>

    <!-- Database Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-database"></i>
          </div>
          <div class="card-content">
            <h3>{{ dbStats.totalDatabases }}</h3>
            <p>Total Databases</p>
            <span class="db-count">{{ dbStats.activeDatabases }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon size">
            <i class="fas fa-hdd"></i>
          </div>
          <div class="card-content">
            <h3>{{ dbStats.totalSize }}</h3>
            <p>Total Size</p>
            <span class="size-status">{{ dbStats.avgSize }} avg</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon connections">
            <i class="fas fa-link"></i>
          </div>
          <div class="card-content">
            <h3>{{ dbStats.totalConnections }}</h3>
            <p>Connections</p>
            <span class="connection-count">{{ dbStats.activeConnections }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon queries">
            <i class="fas fa-code"></i>
          </div>
          <div class="card-content">
            <h3>{{ dbStats.totalQueries }}</h3>
            <p>Queries Today</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="backup-btn" @click="showBackupModal = true">
          <i class="fas fa-save"></i>
          Create Backup
        </button>
        <button class="restore-btn" @click="showRestoreModal = true">
          <i class="fas fa-undo"></i>
          Restore Backup
        </button>
        <button class="optimize-btn" @click="optimizeDatabase">
          <i class="fas fa-tools"></i>
          Optimize
        </button>
        <button class="query-btn" @click="showQueryModal = true">
          <i class="fas fa-terminal"></i>
          Query Console
        </button>
      </div>
    </div>

    <!-- Database List -->
    <div class="databases-section">
      <div class="section-header">
        <h2>Database Instances</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterDatabases">
              <option value="">All Status</option>
              <option value="online">Online</option>
              <option value="offline">Offline</option>
              <option value="maintenance">Maintenance</option>
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
        <p>Loading databases...</p>
      </div>

      <div v-else-if="filteredDatabases.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-database"></i>
        </div>
        <h3>No databases found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="databases-grid">
          <div 
            v-for="database in filteredDatabases" 
            :key="database.id"
            class="database-card"
            :class="{ 'offline': database.status === 'offline', 'maintenance': database.status === 'maintenance' }"
          >
            <div class="database-header">
              <div class="database-icon">
                <i class="fas fa-database"></i>
              </div>
              <div class="database-status">
                <span :class="['status-badge', database.status]">{{ database.status }}</span>
              </div>
            </div>

            <div class="database-content">
              <h3>{{ database.name }}</h3>
              <p>{{ database.description }}</p>
              
              <div class="database-info">
                <span class="type">{{ database.type }}</span>
                <span class="version">{{ database.version }}</span>
                <span class="size">{{ database.size }}</span>
              </div>

              <div class="database-stats">
                <div class="stat-item">
                  <label>Connections:</label>
                  <span>{{ database.connections }} / {{ database.maxConnections }}</span>
                </div>
                <div class="stat-item">
                  <label>Queries:</label>
                  <span>{{ database.queries }} today</span>
                </div>
                <div class="stat-item">
                  <label>Uptime:</label>
                  <span>{{ database.uptime }}%</span>
                </div>
              </div>

              <div class="database-actions">
                <button class="action-btn connect" @click="connectDatabase(database)" v-if="database.status === 'offline'">
                  <i class="fas fa-plug"></i>
                  Connect
                </button>
                <button class="action-btn disconnect" @click="disconnectDatabase(database)" v-if="database.status === 'online'">
                  <i class="fas fa-unlink"></i>
                  Disconnect
                </button>
                <button class="action-btn backup" @click="backupDatabase(database)">
                  <i class="fas fa-save"></i>
                  Backup
                </button>
                <button class="action-btn manage" @click="manageDatabase(database)">
                  <i class="fas fa-cog"></i>
                  Manage
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="databases-list">
          <div 
            v-for="database in filteredDatabases" 
            :key="database.id"
            class="database-list-card"
            :class="{ 'offline': database.status === 'offline', 'maintenance': database.status === 'maintenance' }"
          >
            <div class="database-list-header">
              <div class="database-list-info">
                <div class="database-icon">
                  <i class="fas fa-database"></i>
                </div>
                <div class="database-details">
                  <h3>{{ database.name }}</h3>
                  <p>{{ database.description }}</p>
                  <div class="database-info">
                    <span class="type">{{ database.type }}</span>
                    <span class="version">{{ database.version }}</span>
                    <span :class="['status-badge', database.status]">{{ database.status }}</span>
                    <span class="size">{{ database.size }}</span>
                  </div>
                </div>
              </div>
              <div class="database-list-stats">
                <div class="stat-item">
                  <label>Connections:</label>
                  <span>{{ database.connections }} / {{ database.maxConnections }}</span>
                </div>
                <div class="stat-item">
                  <label>Queries:</label>
                  <span>{{ database.queries }} today</span>
                </div>
                <div class="stat-item">
                  <label>Uptime:</label>
                  <span>{{ database.uptime }}%</span>
                </div>
              </div>
              <div class="database-list-actions">
                <button class="action-btn connect" @click="connectDatabase(database)" v-if="database.status === 'offline'">
                  <i class="fas fa-plug"></i>
                </button>
                <button class="action-btn disconnect" @click="disconnectDatabase(database)" v-if="database.status === 'online'">
                  <i class="fas fa-unlink"></i>
                </button>
                <button class="action-btn backup" @click="backupDatabase(database)">
                  <i class="fas fa-save"></i>
                </button>
                <button class="action-btn manage" @click="manageDatabase(database)">
                  <i class="fas fa-cog"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Metrics -->
    <div class="performance-section">
      <div class="section-header">
        <h2>Performance Metrics</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="timeRange" @change="updateMetrics">
              <option value="1">Last Hour</option>
              <option value="6">Last 6 Hours</option>
              <option value="24">Last 24 Hours</option>
              <option value="168">Last Week</option>
            </select>
          </div>
          <button class="refresh-btn" @click="refreshMetrics">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-header">
            <h3>Query Performance</h3>
            <span class="metric-value">{{ performance.avgQueryTime }}ms</span>
          </div>
          <div class="metric-chart">
            <canvas ref="queryChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Slow Queries: {{ performance.slowQueries }}</span>
            <span class="detail-item">Failed: {{ performance.failedQueries }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Connection Pool</h3>
            <span class="metric-value">{{ performance.poolUtilization }}%</span>
          </div>
          <div class="metric-chart">
            <canvas ref="poolChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Active: {{ performance.activeConnections }}</span>
            <span class="detail-item">Idle: {{ performance.idleConnections }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Cache Hit Rate</h3>
            <span class="metric-value">{{ performance.cacheHitRate }}%</span>
          </div>
          <div class="metric-chart">
            <canvas ref="cacheChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Hits: {{ performance.cacheHits }}</span>
            <span class="detail-item">Misses: {{ performance.cacheMisses }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Index Usage</h3>
            <span class="metric-value">{{ performance.indexUsage }}%</span>
          </div>
          <div class="metric-chart">
            <canvas ref="indexChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Size: {{ performance.indexSize }}</span>
            <span class="detail-item">Fragments: {{ performance.indexFragments }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Backup Management -->
    <div class="backup-section">
      <div class="section-header">
        <h2>Backup Management</h2>
        <div class="header-actions">
          <button class="create-backup-btn" @click="showBackupModal = true">
            <i class="fas fa-plus"></i>
            Create Backup
          </button>
        </div>
      </div>

      <div class="backups-grid">
        <div 
          v-for="backup in backups" 
          :key="backup.id"
          class="backup-card"
        >
          <div class="backup-header">
            <div class="backup-icon">
              <i class="fas fa-archive"></i>
            </div>
            <div class="backup-info">
              <h3>{{ backup.name }}</h3>
              <p>{{ backup.description }}</p>
            </div>
            <div class="backup-status">
              <span :class="['status-badge', backup.status]">{{ backup.status }}</span>
            </div>
          </div>

          <div class="backup-details">
            <div class="backup-item">
              <label>Type:</label>
              <span>{{ backup.type }}</span>
            </div>
            <div class="backup-item">
              <label>Size:</label>
              <span>{{ backup.size }}</span>
            </div>
            <div class="backup-item">
              <label>Created:</label>
              <span>{{ formatDate(backup.createdAt) }}</span>
            </div>
            <div class="backup-item">
              <label>Expires:</label>
              <span>{{ formatDate(backup.expiresAt) }}</span>
            </div>
          </div>

          <div class="backup-actions">
            <button class="action-btn restore" @click="restoreBackup(backup)">
              <i class="fas fa-undo"></i>
              Restore
            </button>
            <button class="action-btn download" @click="downloadBackup(backup)">
              <i class="fas fa-download"></i>
              Download
            </button>
            <button class="action-btn delete" @click="deleteBackup(backup)">
              <i class="fas fa-trash"></i>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Backup Modal -->
    <div v-if="showBackupModal" class="modal-overlay" @click="closeBackupModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create Backup</h2>
          <button class="close-btn" @click="closeBackupModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="backup-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Backup Name *</label>
                <input 
                  v-model="backupForm.name" 
                  type="text" 
                  placeholder="Enter backup name"
                  required
                />
              </div>
              <div class="form-group">
                <label>Database *</label>
                <select v-model="backupForm.databaseId" required>
                  <option value="">Select database</option>
                  <option 
                    v-for="db in databases.value" 
                    :key="db.id"
                    :value="db.id"
                  >
                    {{ db.name }}
                  </option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="backupForm.description" 
                placeholder="Describe this backup"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Backup Type</label>
              <select v-model="backupForm.type">
                <option value="full">Full Backup</option>
                <option value="incremental">Incremental</option>
                <option value="differential">Differential</option>
              </select>
            </div>

            <div class="form-group">
              <label>Compression</label>
              <select v-model="backupForm.compression">
                <option value="gzip">Gzip</option>
                <option value="bzip2">Bzip2</option>
                <option value="none">None</option>
              </select>
            </div>

            <div class="form-group">
              <label>Schedule</label>
              <select v-model="backupForm.schedule">
                <option value="manual">Manual</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div class="form-group" v-if="backupForm.schedule !== 'manual'">
              <label>Retention Period</label>
              <select v-model="backupForm.retention">
                <option value="7">7 days</option>
                <option value="30">30 days</option>
                <option value="90">90 days</option>
                <option value="365">1 year</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeBackupModal">Cancel</button>
          <button class="btn-primary" @click="createBackup">Create Backup</button>
        </div>
      </div>
    </div>

    <!-- Query Console Modal -->
    <div v-if="showQueryModal" class="modal-overlay" @click="closeQueryModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Query Console</h2>
          <button class="close-btn" @click="closeQueryModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="query-console">
            <div class="query-editor">
              <textarea 
                v-model="queryText" 
                placeholder="Enter SQL query here..."
                class="query-textarea"
                @keydown.ctrl.enter="executeQuery"
              ></textarea>
            </div>
            <div class="query-actions">
              <button class="execute-btn" @click="executeQuery">
                <i class="fas fa-play"></i>
                Execute (Ctrl+Enter)
              </button>
              <button class="clear-btn" @click="clearQuery">
                <i class="fas fa-trash"></i>
                Clear
              </button>
              <button class="save-btn" @click="saveQuery">
                <i class="fas fa-save"></i>
                Save Query
              </button>
            </div>
          </div>

            <div class="query-results" v-if="queryResults.length > 0">
              <div class="results-header">
                <h3>Results ({{ queryResults.length }} rows)</h3>
                <button class="export-btn" @click="exportResults">
                  <i class="fas fa-download"></i>
                  Export
                </button>
              </div>
              <div class="results-table-container">
                <table class="results-table">
                  <thead>
                    <tr>
                      <th v-for="column in queryResults[0]" :key="column">{{ column }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="(row, index) in queryResults" 
                      :key="index"
                    >
                      <td v-for="(value, column) in row" :key="column">{{ value }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeQueryModal">Close</button>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Chart } from 'chart.js/auto'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const statusFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('24')
const showBackupModal = ref(false)
  const showRestoreModal = ref(false)
const showQueryModal = ref(false)

// Chart instances
const queryChart = ref(null)
const poolChart = ref(null)
const cacheChart = ref(null)
const indexChart = ref(null)

// Database stats
const dbStats = reactive({
  totalDatabases: 3,
  activeDatabases: 3,
  totalSize: '45.2GB',
  avgSize: '15.1GB',
  totalConnections: 150,
  activeConnections: 45,
  totalQueries: 12450
})

// Performance metrics
const performance = reactive({
  avgQueryTime: 145,
  slowQueries: 12,
  failedQueries: 3,
  poolUtilization: 67,
  activeConnections: 30,
  idleConnections: 15,
  cacheHitRate: 94,
  cacheHits: 45678,
  cacheMisses: 2912,
  indexUsage: 78,
  indexSize: '2.3GB',
  indexFragments: 156
})

// Backup form
const backupForm = reactive({
  name: '',
  description: '',
  databaseId: '',
  type: 'full',
  compression: 'gzip',
  schedule: 'daily',
  retention: '30'
})

// Query state
const queryText = ref('')
const queryResults = ref([])

// Mock data
const databases = ref([
  {
    id: 1,
    name: 'Primary Database',
    description: 'Main application database',
    type: 'PostgreSQL',
    version: '14.2',
    size: '23.4GB',
    status: 'online',
    connections: 25,
    maxConnections: 100,
    queries: 4567,
    uptime: 99.9
  },
  {
    id: 2,
    name: 'Analytics Database',
    description: 'Analytics and reporting database',
    type: 'MySQL',
    version: '8.0',
    size: '15.8GB',
    status: 'online',
    connections: 15,
    maxConnections: 50,
    queries: 2341,
    uptime: 99.8
  },
  {
    id: 3,
    name: 'Cache Database',
    description: 'Redis cache server',
    type: 'Redis',
    version: '6.2',
    size: '6.0GB',
    status: 'online',
    connections: 5,
    maxConnections: 20,
    queries: 5542,
    uptime: 100
  }
])

const backups = ref([
  {
    id: 1,
    name: 'Daily Backup - Primary',
    description: 'Automated daily backup of primary database',
    type: 'incremental',
    size: '2.3GB',
    status: 'completed',
    createdAt: '2024-01-21T02:00:00Z',
    expiresAt: '2024-02-21T02:00:00Z'
  },
  {
    id: 2,
    name: 'Weekly Full Backup',
    description: 'Weekly full backup of all databases',
    type: 'full',
    size: '45.2GB',
    status: 'in_progress',
    createdAt: '2024-01-21T01:00:00Z',
    expiresAt: '2024-02-21T01:00:00Z'
  },
  {
    id: 3,
    name: 'Analytics Backup',
    description: 'Backup of analytics database',
    type: 'differential',
    size: '1.2GB',
    status: 'completed',
    createdAt: '2024-01-20T23:00:00Z',
    expiresAt: '2024-01-27T23:00:00Z'
  }
])

// Computed properties
const filteredDatabases = computed(() => {
  let filtered = databases.value

  if (statusFilter.value) {
    filtered = filtered.filter(db => db.status === statusFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.updatedAt || 0) - new Date(a.updatedAt || 0))
})

// Methods
const loadDatabaseData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/database')
    // if (response.success) {
    //   databases.value = response.databases || []
    //   backups.value = response.backups || []
    //   Object.assign(dbStats, response.stats)
    //   Object.assign(performance, response.performance)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading database data:', error)
    showError('Failed to load database data')
  } finally {
    loading.value = false
  }
}

const filterDatabases = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value) {
    return 'No databases match your filter criteria'
  }
  return 'No databases found'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const connectDatabase = async (database) => {
  try {
    // const response = await apiPost(`/database/${database.id}/connect`)
    // if (response.success) {
    //   database.status = 'online'
    //   showSuccess('Database connected successfully')
    // }
    
    // For demo, simulate connection
    database.status = 'online'
    showSuccess('Database connected successfully')
  } catch (error) {
    console.error('Error connecting database:', error)
    showError('Failed to connect database')
  }
}

const disconnectDatabase = async (database) => {
  try {
    // const response = await apiPost(`/database/${database.id}/disconnect`)
    // if (response.success) {
    //   database.status = 'offline'
    //   showSuccess('Database disconnected successfully')
    // }
    
    // For demo, simulate disconnection
    database.status = 'offline'
    showSuccess('Database disconnected successfully')
  } catch (error) {
    console.error('Error disconnecting database:', error)
    showError('Failed to disconnect database')
  }
}

const backupDatabase = async (database) => {
  try {
    // const response = await apiPost(`/database/${database.id}/backup`)
    // if (response.success) {
    //   const newBackup = response.backup
    //   backups.value.unshift(newBackup)
    //   showSuccess('Backup created successfully')
    // }
    
    // For demo, simulate backup
    const newBackup = {
      id: Date.now(),
      name: `Manual Backup - ${database.name}`,
      description: `Manual backup of ${database.name}`,
      type: 'full',
      size: database.size,
      status: 'in_progress',
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
    }
    
    backups.value.unshift(newBackup)
    showSuccess('Backup created successfully')
  } catch (error) {
    console.error('Error creating backup:', error)
    showError('Failed to create backup')
  }
}

const restoreBackup = async (backup) => {
  const confirmed = await showConfirm(`Are you sure you want to restore backup "${backup.name}"? This will overwrite the current database.`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/backups/${backup.id}/restore`)
    // if (response.success) {
    //   showSuccess('Backup restored successfully')
    // }
    
    // For demo, simulate restore
    showSuccess('Backup restored successfully')
  } catch (error) {
    console.error('Error restoring backup:', error)
    showError('Failed to restore backup')
  }
}

const downloadBackup = async (backup) => {
  try {
    // const response = await apiGet(`/backups/${backup.id}/download`)
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `${backup.name}.sql`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Backup downloaded successfully')
    // }
    
    // For demo, simulate download
    showSuccess('Backup downloaded successfully')
  } catch (error) {
    console.error('Error downloading backup:', error)
    showError('Failed to download backup')
  }
}

const deleteBackup = async (backup) => {
  const confirmed = await showConfirm(`Are you sure you want to delete backup "${backup.name}"? This action cannot be undone.`)
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/backups/${backup.id}`)
    // if (response.success) {
    //   const index = backups.value.findIndex(b => b.id === backup.id)
    //   if (index > -1) {
    //     backups.value.splice(index, 1)
    //     showSuccess('Backup deleted successfully')
    //   }
    // }
    
    // For demo, simulate deletion
    const index = backups.value.findIndex(b => b.id === backup.id)
    if (index > -1) {
      backups.value.splice(index, 1)
      showSuccess('Backup deleted successfully')
    }
  } catch (error) {
    console.error('Error deleting backup:', error)
    showError('Failed to delete backup')
  }
}

const optimizeDatabase = async () => {
  try {
    // const response = await apiPost('/database/optimize')
    // if (response.success) {
    //   showSuccess('Database optimization completed')
    //   await loadDatabaseData()
    // }
    
    // For demo, simulate optimization
    showSuccess('Database optimization completed')
    await loadDatabaseData()
  } catch (error) {
    console.error('Error optimizing database:', error)
    showError('Failed to optimize database')
  }
}

const updateMetrics = async () => {
  try {
    // const response = await apiGet('/database/metrics', { timeRange: timeRange.value })
    // if (response.success) {
    //   Object.assign(performance, response.performance)
    //   updateCharts()
    // }
    
    // For demo, simulate metrics update
    updateCharts()
  } catch (error) {
    console.error('Error updating metrics:', error)
    showError('Failed to update metrics')
  }
}

const initCharts = () => {
  // Initialize Query Performance chart
  if (queryChart.value) queryChart.value.destroy()
  queryChart.value = new Chart(queryChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Query Time',
        data: Array.from({ length: 20 }, () => Math.random() * 500),
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
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Connection Pool chart
  if (poolChart.value) poolChart.value.destroy()
  poolChart.value = new Chart(poolChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Pool Utilization',
        data: Array.from({ length: 20 }, () => Math.random() * 100),
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
        y: { beginAtZero: true, max: 100 }
      }
    }
  })

  // Initialize Cache Hit Rate chart
  if (cacheChart.value) cacheChart.value.destroy()
  cacheChart.value = new Chart(cacheChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Hit Rate',
        data: Array.from({ length: 20 }, () => Math.random() * 100),
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
        y: { beginAtZero: true, max: 100 }
      }
    }
  })

  // Initialize Index Usage chart
  if (indexChart.value) indexChart.value.destroy()
  indexChart.value = new Chart(indexChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Index Usage',
        data: Array.from({ length: 20 }, () => Math.random() * 100),
        borderColor: 'rgb(6, 182, 212)',
        backgroundColor: 'rgba(6, 182, 212, 0.1)',
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
}

const updateCharts = () => {
  // Update charts with new data
  if (queryChart.value) {
    queryChart.value.data.datasets[0].data.shift()
    queryChart.value.data.datasets[0].push(performance.avgQueryTime)
    queryChart.value.update('none')
  }

  if (poolChart.value) {
    poolChart.value.data.datasets[0].data.shift()
    poolChart.value.data.datasets[0].push(performance.poolUtilization)
    poolChart.value.update('none')
  }

  if (cacheChart.value) {
    cacheChart.value.data.datasets[0].data.shift()
    cacheChart.value.data.datasets[0].push(performance.cacheHitRate)
    cacheChart.value.update('none')
  }

  if (indexChart.value) {
    indexChart.value.data.datasets[0].data.shift()
    indexChart.value.data.datasets[0].push(performance.indexUsage)
    indexChart.value.update('none')
  }
}

const executeQuery = async () => {
  if (!queryText.value.trim()) {
    showError('Please enter a SQL query')
    return
  }

  try {
    // const response = await apiPost('/database/query', { query: queryText.value })
    // if (response.success) {
    //   queryResults.value = response.results
    //   showSuccess('Query executed successfully')
    // }
    
    // For demo, simulate query results
    const mockResults = [
      { id: 1, name: 'John Doe', email: 'john@example.com', age: 30 },
      { id: 2, name: 'Jane Smith', email: 'jane@example.com', age: 25 },
      { id: 3, name: 'Bob Johnson', email: 'bob@example.com', age: 35 }
    ]
    
    queryResults.value = mockResults
    showSuccess('Query executed successfully')
  } catch (error) {
    console.error('Error executing query:', error)
    showError('Failed to execute query')
  }
}

const clearQuery = () => {
  queryText.value = ''
  queryResults.value = []
}

const saveQuery = () => {
  if (!queryText.value.trim()) {
    showError('No query to save')
    return
  }

  // In real app, this would save the query to user's saved queries
  showSuccess('Query saved successfully')
}

const exportResults = () => {
  if (queryResults.value.length === 0) {
    showError('No results to export')
    return
  }

  try {
    // const response = await apiPost('/database/export', { 
    //   data: queryResults.value,
    //   format: 'csv'
    // })
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `query-results-${new Date().toISOString().split('T')[0]}.csv`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Results exported successfully')
    // }
    
    // For demo, simulate export
    showSuccess('Results exported successfully')
  } catch (error) {
    console.error('Error exporting results:', error)
    showError('Failed to export results')
  }
}

const closeBackupModal = () => {
  showBackupModal.value = false
  resetBackupForm()
}

const resetBackupForm = () => {
  Object.assign(backupForm, {
    name: '',
    description: '',
    databaseId: '',
    type: 'full',
    compression: 'gzip',
    schedule: 'daily',
    retention: '30'
  })
}

const closeQueryModal = () => {
  showQueryModal.value = false
  queryText.value = ''
  queryResults.value = []
}

// Lifecycle
onMounted(() => {
  loadDatabaseData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (queryChart.value) queryChart.value.destroy()
  if (poolChart.value) poolChart.value.destroy()
  if (cacheChart.value) cacheChart.value.destroy()
  if (indexChart.value) indexChart.value.destroy()
})
</script>

<style scoped>
.database {
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

.card-icon.size {
  background: var(--success-color);
}

.card-icon.connections {
  background: var(--warning-color);
}

.card-icon.queries {
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

.db-count,
.size-status,
.connection-count,
.query-count {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.db-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.size-status,
.connection-count,
.query-count {
  color: var(--text-secondary);
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

.backup-btn,
.restore-btn,
.optimize-btn,
.query-btn {
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

.backup-btn:hover,
.restore-btn:hover,
.optimize-btn:hover,
.query-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.restore-btn {
  background: var(--success-color);
}

.restore-btn:hover {
  background: var(--success-hover);
}

.optimize-btn {
  background: var(--warning-color);
}

.optimize-btn:hover {
  background: var(--warning-hover);
}

.query-btn {
  background: var(--info-color);
}

.query-btn:hover {
  background: var(--info-hover);
}

.databases-section,
.performance-section,
.backup-section {
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
  color: (var(--text-primary));
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

.create-backup-btn {
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

.create-backup-btn:hover {
  background: var(--primary-hover);
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

.databases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.database-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.database-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.database-card.offline {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.database-card.maintenance {
  opacity: 0.7;
  border-color: var(--info-color);
}

.database-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.database-icon {
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

.status-badge.online {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.offline {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.maintenance {
  background: rgba(6, 182, 212, 0.1);
  color: #06b6d4;
}

.database-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.database-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.database-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.version,
.size {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.database-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.database-actions {
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

.action-btn.connect:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.disconnect:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.backup:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.manage:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.databases-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.database-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.database-list-card:hover {
  background: var(--glass-bg-hover);
}

.database-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.database-list-info {
  flex: 1;
}

.database-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.database-list-actions {
  display: flex;
  gap: 0.5rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.metric-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.metric-chart {
  height: 150px;
  margin-bottom: 1rem;
}

.metric-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-secondary);
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

.backups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.backup-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.backup-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.backup-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.backup-icon {
  width: 50px;
  height: 50px;
  background: var(--info-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.backup-info {
  flex: 1;
}

.backup-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.backup-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.backup-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.in_progress {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.backup-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.backup-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.backup-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.backup-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.backup-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn.restore:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.download:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
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

.backup-form {
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

.query-console {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
}

.query-editor {
  margin-bottom: 1rem;
}

.query-textarea {
  width: 100%;
  min-height: 200px;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  resize: vertical;
  min-height: 200px;
}

.query-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.execute-btn {
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

.execute-btn:hover {
  background: var(--primary-hover);
}

.clear-btn,
.save-btn {
  padding: 0.75rem 1.25rem;
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.clear-btn:hover,
.save-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.query-results {
  margin-top: 1rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.results-table-container {
  overflow-x: auto;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.results-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.results-table tr:hover {
  background: var(--glass-bg-hover);
}

.export-btn {
  padding: 0.5rem 1rem;
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
}

.export-btn:hover {
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
  .database {
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
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .databases-grid {
    grid-template-columns: 1fr;
  }
  
  .database-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .database-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .metric-card {
    margin-bottom: 1rem;
  }
  
  .metric-details {
    grid-template-columns: 1fr;
  }
  
  .backups-grid {
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
