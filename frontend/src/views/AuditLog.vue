<template>
  <div class="audit-log">
    <div class="page-header">
      <h1>Audit Log</h1>
      <p>Track system activities and security events</p>
    </div>

    <!-- Statistics Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-history"></i>
          </div>
          <div class="card-content">
            <h3>{{ auditStats.totalEvents }}</h3>
            <p>Total Events</p>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon today">
            <i class="fas fa-calendar-day"></i>
          </div>
          <div class="card-content">
            <h3>{{ auditStats.todayEvents }}</h3>
            <p>Today's Events</p>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon security">
            <i class="fas fa-shield-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ auditStats.securityEvents }}</h3>
            <p>Security Events</p>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon errors">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="card-content">
            <h3>{{ auditStats.errorEvents }}</h3>
            <p>Error Events</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section">
      <div class="filter-controls">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search audit events..."
            @input="filterEvents"
          />
        </div>
        <div class="filter-dropdown">
          <select v-model="categoryFilter" @change="filterEvents">
            <option value="">All Categories</option>
            <option value="authentication">Authentication</option>
            <option value="authorization">Authorization</option>
            <option value="data">Data Operations</option>
            <option value="system">System</option>
            <option value="security">Security</option>
            <option value="api">API</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="severityFilter" @change="filterEvents">
            <option value="">All Severities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <div class="date-filter">
          <input 
            v-model="dateFilter" 
            type="date" 
            @change="filterEvents"
          />
        </div>
        <button class="export-btn" @click="exportLogs">
          <i class="fas fa-download"></i>
          Export
        </button>
      </div>
    </div>

    <!-- Audit Events Table -->
    <div class="events-section">
      <div class="section-header">
        <h2>Audit Events</h2>
        <div class="header-actions">
          <button class="refresh-btn" @click="refreshEvents">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
          <button class="clear-btn" @click="clearFilters">
            <i class="fas fa-times"></i>
            Clear Filters
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading audit events...</p>
      </div>

      <div v-else-if="filteredEvents.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-history"></i>
        </div>
        <h3>No audit events found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="events-table-container">
        <table class="events-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>User</th>
              <th>Action</th>
              <th>Category</th>
              <th>Severity</th>
              <th>IP Address</th>
              <th>Status</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="event in filteredEvents" 
              :key="event.id"
              class="event-row"
              :class="{ 'high-severity': event.severity === 'high' || event.severity === 'critical' }"
            >
              <td>
                <div class="timestamp">
                  <span class="date">{{ formatDate(event.timestamp) }}</span>
                  <span class="time">{{ formatTime(event.timestamp) }}</span>
                </div>
              </td>
              <td>
                <div class="user-info">
                  <div class="user-avatar">
                    <img :src="event.user.avatar || getDefaultAvatar()" :alt="event.user.name" />
                  </div>
                  <div class="user-details">
                    <span class="user-name">{{ event.user.name }}</span>
                    <span class="user-email">{{ event.user.email }}</span>
                  </div>
                </div>
              </td>
              <td>
                <div class="action-info">
                  <span class="action-name">{{ event.action }}</span>
                  <span class="action-description">{{ event.description }}</span>
                </div>
              </td>
              <td>
                <span :class="['category-badge', event.category]">{{ event.category }}</span>
              </td>
              <td>
                <span :class="['severity-badge', event.severity]">{{ event.severity }}</span>
              </td>
              <td>
                <span class="ip-address">{{ event.ip_address }}</span>
              </td>
              <td>
                <span :class="['status-badge', event.status]">{{ event.status }}</span>
              </td>
              <td>
                <button 
                  class="details-btn"
                  @click="showEventDetails(event)"
                  title="View Details"
                >
                  <i class="fas fa-eye"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Event Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Event Details</h2>
          <button class="close-btn" @click="closeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="event-details">
            <div class="detail-section">
              <h3>Basic Information</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Event ID:</label>
                  <span>{{ selectedEvent?.id }}</span>
                </div>
                <div class="detail-item">
                  <label>Timestamp:</label>
                  <span>{{ formatDateTime(selectedEvent?.timestamp) }}</span>
                </div>
                <div class="detail-item">
                  <label>User:</label>
                  <span>{{ selectedEvent?.user?.name }} ({{ selectedEvent?.user?.email }})</span>
                </div>
                <div class="detail-item">
                  <label>IP Address:</label>
                  <span>{{ selectedEvent?.ip_address }}</span>
                </div>
                <div class="detail-item">
                  <label>User Agent:</label>
                  <span>{{ selectedEvent?.user_agent }}</span>
                </div>
                <div class="detail-item">
                  <label>Session ID:</label>
                  <span>{{ selectedEvent?.session_id }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Action Details</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Action:</label>
                  <span>{{ selectedEvent?.action }}</span>
                </div>
                <div class="detail-item">
                  <label>Category:</label>
                  <span :class="['category-badge', selectedEvent?.category]">{{ selectedEvent?.category }}</span>
                </div>
                <div class="detail-item">
                  <label>Severity:</label>
                  <span :class="['severity-badge', selectedEvent?.severity]">{{ selectedEvent?.severity }}</span>
                </div>
                <div class="detail-item">
                  <label>Status:</label>
                  <span :class="['status-badge', selectedEvent?.status]">{{ selectedEvent?.status }}</span>
                </div>
              </div>
              <div class="detail-item full-width">
                <label>Description:</label>
                <p>{{ selectedEvent?.description }}</p>
              </div>
            </div>

            <div class="detail-section" v-if="selectedEvent?.details">
              <h3>Additional Details</h3>
              <div class="details-content">
                <pre>{{ JSON.stringify(selectedEvent.details, null, 2) }}</pre>
              </div>
            </div>

            <div class="detail-section" v-if="selectedEvent?.changes">
              <h3>Changes Made</h3>
              <div class="changes-list">
                <div 
                  v-for="(change, key) in selectedEvent.changes" 
                  :key="key"
                  class="change-item"
                >
                  <div class="change-field">{{ key }}</div>
                  <div class="change-values">
                    <div class="change-old">
                      <label>Old:</label>
                      <span>{{ change.old || 'N/A' }}</span>
                    </div>
                    <div class="change-new">
                      <label>New:</label>
                      <span>{{ change.new || 'N/A' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeDetailsModal">Close</button>
          <button class="btn-primary" @click="exportEvent(selectedEvent)">
            <i class="fas fa-download"></i>
            Export Event
          </button>
        </div>
      </div>
    </div>

    <!-- Export Modal -->
    <div v-if="showExportModal" class="modal-overlay" @click="closeExportModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Export Audit Logs</h2>
          <button class="close-btn" @click="closeExportModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="export-form">
            <div class="form-group">
              <label>Export Format</label>
              <select v-model="exportForm.format">
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
                <option value="xml">XML</option>
                <option value="pdf">PDF</option>
              </select>
            </div>

            <div class="form-group">
              <label>Date Range</label>
              <div class="date-range">
                <input 
                  v-model="exportForm.startDate" 
                  type="date"
                  :max="exportForm.endDate"
                />
                <span>to</span>
                <input 
                  v-model="exportForm.endDate" 
                  type="date"
                  :min="exportForm.startDate"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Categories</label>
              <div class="checkbox-grid">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.categories"
                    value="authentication"
                  />
                  <span>Authentication</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.categories"
                    value="authorization"
                  />
                  <span>Authorization</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.categories"
                    value="data"
                  />
                  <span>Data Operations</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.categories"
                    value="system"
                  />
                  <span>System</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.categories"
                    value="security"
                  />
                  <span>Security</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.categories"
                    value="api"
                  />
                  <span>API</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Severity Levels</label>
              <div class="checkbox-grid">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.severities"
                    value="low"
                  />
                  <span>Low</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.severities"
                    value="medium"
                  />
                  <span>Medium</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.severities"
                    value="high"
                  />
                  <span>High</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="exportForm.severities"
                    value="critical"
                  />
                  <span>Critical</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeExportModal">Cancel</button>
          <button 
            class="btn-primary" 
            @click="performExport"
            :disabled="exporting"
          >
            <span v-if="!exporting">Export</span>
            <span v-else>Exporting...</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const exporting = ref(false)
const auditEvents = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')
const severityFilter = ref('')
const dateFilter = ref('')
const selectedEvent = ref(null)

// Modal states
const showDetailsModal = ref(false)
const showExportModal = ref(false)

const exportForm = reactive({
  format: 'csv',
  startDate: '',
  endDate: '',
  categories: ['authentication', 'authorization', 'data', 'system', 'security', 'api'],
  severities: ['low', 'medium', 'high', 'critical']
})

// Mock audit events data (in real app, this would come from API)
const mockAuditEvents = [
  {
    id: 1,
    timestamp: '2024-01-21T10:30:00Z',
    user: {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      avatar: 'https://via.placeholder.com/40x40?text=JD'
    },
    action: 'User Login',
    category: 'authentication',
    severity: 'low',
    status: 'success',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    session_id: 'sess_123456',
    description: 'User successfully logged in',
    details: {
      login_method: 'password',
      two_factor_enabled: false
    }
  },
  {
    id: 2,
    timestamp: '2024-01-21T10:25:00Z',
    user: {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@example.com',
      avatar: 'https://via.placeholder.com/40x40?text=JS'
    },
    action: 'Data Export',
    category: 'data',
    severity: 'medium',
    status: 'success',
    ip_address: '192.168.1.101',
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    session_id: 'sess_123457',
    description: 'User exported customer data',
    details: {
      export_format: 'csv',
      record_count: 1500,
      data_type: 'customers'
    }
  },
  {
    id: 3,
    timestamp: '2024-01-21T10:20:00Z',
    user: {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      avatar: 'https://via.placeholder.com/40x40?text=JD'
    },
    action: 'Failed Login Attempt',
    category: 'security',
    severity: 'high',
    status: 'failed',
    ip_address: '203.0.113.1',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    session_id: null,
    description: 'Multiple failed login attempts detected',
    details: {
      attempt_count: 5,
      reason: 'invalid_password',
      locked: true
    }
  },
  {
    id: 4,
    timestamp: '2024-01-21T10:15:00Z',
    user: {
      id: 3,
      name: 'Admin User',
      email: 'admin@example.com',
      avatar: 'https://via.placeholder.com/40x40?text=AU'
    },
    action: 'System Configuration Change',
    category: 'system',
    severity: 'high',
    status: 'success',
    ip_address: '192.168.1.1',
    user_agent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    session_id: 'sess_123458',
    description: 'Admin modified system configuration',
    details: {
      config_file: '/etc/system.conf',
      changes: {
        'max_connections': { old: 100, new: 200 },
        'timeout': { old: 30, new: 60 }
      }
    },
    changes: {
      'max_connections': { old: 100, new: 200 },
      'timeout': { old: 30, new: 60 }
    }
  },
  {
    id: 5,
    timestamp: '2024-01-21T10:10:00Z',
    user: {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@example.com',
      avatar: 'https://via.placeholder.com/40x40?text=JS'
    },
    action: 'API Key Generated',
    category: 'api',
    severity: 'medium',
    status: 'success',
    ip_address: '192.168.1.101',
    user_agent: 'PostmanRuntime/7.29.2',
    session_id: 'sess_123457',
    description: 'User generated new API key',
    details: {
      key_id: 'key_abc123',
      permissions: ['read', 'write'],
      expires_at: '2024-04-21T10:10:00Z'
    }
  },
  {
    id: 6,
    timestamp: '2024-01-21T10:05:00Z',
    user: {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      avatar: 'https://via.placeholder.com/40x40?text=JD'
    },
    action: 'File Upload',
    category: 'data',
    severity: 'low',
    status: 'success',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    session_id: 'sess_123456',
    description: 'User uploaded document file',
    details: {
      file_name: 'report.pdf',
      file_size: 2048576,
      file_type: 'application/pdf'
    }
  }
]

// Computed properties
const filteredEvents = computed(() => {
  let filtered = auditEvents.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(event => 
      event.action.toLowerCase().includes(query) ||
      event.description.toLowerCase().includes(query) ||
      event.user.name.toLowerCase().includes(query) ||
      event.user.email.toLowerCase().includes(query)
    )
  }

  // Apply category filter
  if (categoryFilter.value) {
    filtered = filtered.filter(event => event.category === categoryFilter.value)
  }

  // Apply severity filter
  if (severityFilter.value) {
    filtered = filtered.filter(event => event.severity === severityFilter.value)
  }

  // Apply date filter
  if (dateFilter.value) {
    const filterDate = new Date(dateFilter.value).toDateString()
    filtered = filtered.filter(event => 
      new Date(event.timestamp).toDateString() === filterDate
    )
  }

  return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const auditStats = computed(() => {
  const today = new Date().toDateString()
  const stats = {
    totalEvents: auditEvents.value.length,
    todayEvents: auditEvents.value.filter(event => 
      new Date(event.timestamp).toDateString() === today
    ).length,
    securityEvents: auditEvents.value.filter(event => 
      event.category === 'security'
    ).length,
    errorEvents: auditEvents.value.filter(event => 
      event.status === 'failed'
    ).length
  }
  return stats
})

// Methods
const loadAuditEvents = async () => {
  loading.value = true
  try {
    // In real app, this would be an API call
    // const response = await apiGet('/audit-log')
    // if (response.success) {
    //   auditEvents.value = response.events || []
    // }
    
    // For demo, use mock data
    auditEvents.value = mockAuditEvents
  } catch (error) {
    console.error('Error loading audit events:', error)
    showError('Failed to load audit events')
  } finally {
    loading.value = false
  }
}

const filterEvents = () => {
  // This is reactive, no additional action needed
}

const refreshEvents = async () => {
  await loadAuditEvents()
  showSuccess('Audit events refreshed')
}

const clearFilters = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  severityFilter.value = ''
  dateFilter.value = ''
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}

const getEmptyMessage = () => {
  if (searchQuery.value || categoryFilter.value || severityFilter.value || dateFilter.value) {
    return 'No audit events match your search criteria'
  }
  return 'No audit events found'
}

const getDefaultAvatar = () => {
  return 'https://via.placeholder.com/40x40?text=U'
}

const showEventDetails = (event) => {
  selectedEvent.value = event
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedEvent.value = null
}

const exportLogs = () => {
  showExportModal.value = true
}

const closeExportModal = () => {
  showExportModal.value = false
  resetExportForm()
}

const resetExportForm = () => {
  Object.assign(exportForm, {
    format: 'csv',
    startDate: '',
    endDate: '',
    categories: ['authentication', 'authorization', 'data', 'system', 'security', 'api'],
    severities: ['low', 'medium', 'high', 'critical']
  })
}

const performExport = async () => {
  exporting.value = true
  try {
    // const response = await apiPost('/audit-log/export', exportForm)
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `audit-log-${new Date().toISOString().split('T')[0]}.${exportForm.format}`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Audit log exported successfully')
    //   closeExportModal()
    // }
    
    // For demo, simulate export
    showSuccess('Audit log exported successfully')
    closeExportModal()
  } catch (error) {
    console.error('Error exporting audit log:', error)
    showError('Failed to export audit log')
  } finally {
    exporting.value = false
  }
}

const exportEvent = async (event) => {
  try {
    // const response = await apiPost(`/audit-log/${event.id}/export`, { format: 'json' })
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `audit-event-${event.id}.json`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Event exported successfully')
    // }
    
    // For demo, simulate export
    showSuccess('Event exported successfully')
  } catch (error) {
    console.error('Error exporting event:', error)
    showError('Failed to export event')
  }
}

// Lifecycle
onMounted(() => {
  loadAuditEvents()
})
</script>

<style scoped>
.audit-log {
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

.card-icon.today {
  background: var(--success-color);
}

.card-icon.security {
  background: var(--warning-color);
}

.card-icon.errors {
  background: var(--danger-color);
}

.card-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.card-content p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 1rem;
}

.filters-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
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

.filter-dropdown select,
.date-filter input {
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
  cursor: pointer;
  min-width: 150px;
}

.export-btn {
  padding: 1rem 1.5rem;
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

.export-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.events-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
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
}

.refresh-btn,
.clear-btn {
  padding: 0.75rem 1.25rem;
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

.refresh-btn:hover,
.clear-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
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

.events-table-container {
  overflow-x: auto;
}

.events-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--glass-bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.events-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.events-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.event-row {
  transition: background 0.3s ease;
}

.event-row:hover {
  background: var(--glass-bg-hover);
}

.event-row.high-severity {
  border-left: 4px solid var(--danger-color);
}

.timestamp {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.timestamp .date {
  font-weight: 600;
  color: var(--text-primary);
}

.timestamp .time {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  font-weight: 600;
  color: var(--text-primary);
}

.user-email {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.action-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.action-name {
  font-weight: 600;
  color: var(--text-primary);
}

.action-description {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.category-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.category-badge.authentication {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.category-badge.authorization {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.category-badge.data {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.category-badge.system {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.category-badge.security {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.category-badge.api {
  background: rgba(6, 182, 212, 0.1);
  color: #06b6d4;
}

.severity-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.severity-badge.low {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.severity-badge.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.severity-badge.high {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.severity-badge.critical {
  background: rgba(127, 29, 29, 0.1);
  color: #7f1d1d;
}

.ip-address {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.status-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.details-btn {
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

.details-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
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
  max-width: 900px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1200px;
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
  font-weight: 600;
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

.event-details {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.detail-section {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
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
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.detail-item.full-width {
  grid-column: 1 / -1;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-secondary);
}

.detail-item p {
  margin: 0;
  color: var(--text-primary);
  line-height: 1.5;
}

.details-content {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
}

.details-content pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--text-primary);
}

.changes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.change-item {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  padding: 1rem;
}

.change-field {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.change-values {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.change-old,
.change-new {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.change-old label,
.change-new label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.change-old span,
.change-new span {
  color: var(--text-primary);
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.export-form {
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

.form-group select,
.form-group input {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.date-range input {
  flex: 1;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  .audit-log {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filter-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-box {
    min-width: 100%;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .change-values {
    grid-template-columns: 1fr;
  }
  
  .checkbox-grid {
    grid-template-columns: 1fr;
  }
  
  .date-range {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
