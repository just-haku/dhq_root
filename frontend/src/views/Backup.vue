<template>
  <div class="backup">
    <div class="page-header">
      <h1>Backup & Restore</h1>
      <p>Manage system backups and restore data</p>
    </div>

    <!-- Backup Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-database"></i>
          </div>
          <div class="card-content">
            <h3>{{ backupStats.totalBackups }}</h3>
            <p>Total Backups</p>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon success">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ backupStats.successfulBackups }}</h3>
            <p>Successful</p>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon storage">
            <i class="fas fa-hdd"></i>
          </div>
          <div class="card-content">
            <h3>{{ formatSize(backupStats.totalStorage) }}</h3>
            <p>Total Storage</p>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon recent">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ formatDate(backupStats.lastBackup) }}</h3>
            <p>Last Backup</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="create-backup-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Backup
        </button>
        <button class="restore-btn" @click="showRestoreModal = true">
          <i class="fas fa-history"></i>
          Restore Backup
        </button>
        <button class="schedule-btn" @click="showScheduleModal = true">
          <i class="fas fa-calendar-alt"></i>
          Schedule Backup
        </button>
        <button class="settings-btn" @click="showSettingsModal = true">
          <i class="fas fa-cog"></i>
          Settings
        </button>
      </div>
    </div>

    <!-- Backups List -->
    <div class="backups-section">
      <div class="section-header">
        <h2>Backup History</h2>
        <div class="header-controls">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterBackups">
              <option value="">All Status</option>
              <option value="completed">Completed</option>
              <option value="in-progress">In Progress</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="typeFilter" @change="filterBackups">
              <option value="">All Types</option>
              <option value="full">Full Backup</option>
              <option value="incremental">Incremental</option>
              <option value="differential">Differential</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading backups...</p>
      </div>

      <div v-else-if="filteredBackups.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-database"></i>
        </div>
        <h3>No backups found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="backups-table-container">
        <table class="backups-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Size</th>
              <th>Status</th>
              <th>Created</th>
              <th>Duration</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="backup in filteredBackups" 
              :key="backup.id"
              class="backup-row"
            >
              <td>
                <div class="backup-name">
                  <h4>{{ backup.name }}</h4>
                  <p>{{ backup.description || 'No description' }}</p>
                </div>
              </td>
              <td>
                <span :class="['type-badge', backup.type]">{{ backup.type }}</span>
              </td>
              <td>{{ formatSize(backup.size) }}</td>
              <td>
                <div class="status-info">
                  <span :class="['status-badge', backup.status]">{{ backup.status }}</span>
                  <div v-if="backup.status === 'in-progress'" class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: backup.progress + '%' }"
                    ></div>
                  </div>
                </div>
              </td>
              <td>{{ formatDateTime(backup.created_at) }}</td>
              <td>{{ backup.duration || '-' }}</td>
              <td>
                <div class="actions">
                  <button 
                    v-if="backup.status === 'completed'"
                    class="action-btn restore"
                    @click="restoreBackup(backup)"
                    title="Restore Backup"
                  >
                    <i class="fas fa-history"></i>
                  </button>
                  <button 
                    class="action-btn download"
                    @click="downloadBackup(backup)"
                    title="Download Backup"
                    :disabled="backup.status !== 'completed'"
                  >
                    <i class="fas fa-download"></i>
                  </button>
                  <button 
                    class="action-btn delete"
                    @click="deleteBackup(backup)"
                    title="Delete Backup"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Backup Schedule -->
    <div class="schedule-section">
      <div class="section-header">
        <h2>Backup Schedule</h2>
        <button class="edit-schedule-btn" @click="showScheduleModal = true">
          <i class="fas fa-edit"></i>
          Edit Schedule
        </button>
      </div>

      <div class="schedule-grid">
        <div class="schedule-card">
          <div class="schedule-header">
            <h3>Daily Backup</h3>
            <div class="schedule-status">
              <span :class="['status-badge', schedule.daily.enabled ? 'enabled' : 'disabled']">
                {{ schedule.daily.enabled ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
          </div>
          <div class="schedule-details">
            <p>Runs at {{ schedule.daily.time }} daily</p>
            <p>Next run: {{ formatDateTime(schedule.daily.nextRun) }}</p>
          </div>
        </div>

        <div class="schedule-card">
          <div class="schedule-header">
            <h3>Weekly Backup</h3>
            <div class="schedule-status">
              <span :class="['status-badge', schedule.weekly.enabled ? 'enabled' : 'disabled']">
                {{ schedule.weekly.enabled ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
          </div>
          <div class="schedule-details">
            <p>Runs on {{ schedule.weekly.day }} at {{ schedule.weekly.time }}</p>
            <p>Next run: {{ formatDateTime(schedule.weekly.nextRun) }}</p>
          </div>
        </div>

        <div class="schedule-card">
          <div class="schedule-header">
            <h3>Monthly Backup</h3>
            <div class="schedule-status">
              <span :class="['status-badge', schedule.monthly.enabled ? 'enabled' : 'disabled']">
                {{ schedule.monthly.enabled ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
          </div>
          <div class="schedule-details">
            <p>Runs on {{ schedule.monthly.day }} of each month</p>
            <p>Next run: {{ formatDateTime(schedule.monthly.nextRun) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Backup Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create New Backup</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label>Backup Name *</label>
              <input 
                v-model="backupForm.name" 
                type="text" 
                placeholder="My Backup"
                required
              />
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
              <label>Backup Type *</label>
              <select v-model="backupForm.type" required>
                <option value="full">Full Backup</option>
                <option value="incremental">Incremental Backup</option>
                <option value="differential">Differential Backup</option>
              </select>
            </div>

            <div class="form-group">
              <label>Compression</label>
              <select v-model="backupForm.compression">
                <option value="gzip">Gzip</option>
                <option value="zip">Zip</option>
                <option value="tar">Tar</option>
                <option value="none">No Compression</option>
              </select>
            </div>

            <div class="form-group">
              <label>Encryption</label>
              <select v-model="backupForm.encryption">
                <option value="aes256">AES-256</option>
                <option value="aes128">AES-128</option>
                <option value="none">No Encryption</option>
              </select>
            </div>

            <div class="form-group">
              <label>Retention (days)</label>
              <input 
                v-model.number="backupForm.retention" 
                type="number" 
                min="1"
                max="365"
                placeholder="30"
              />
            </div>
          </div>

          <div class="form-group">
            <label>Include</label>
            <div class="checkbox-grid">
              <label class="checkbox-item">
                <input 
                  type="checkbox" 
                  v-model="backupForm.include.database"
                />
                <span>Database</span>
              </label>
              <label class="checkbox-item">
                <input 
                  type="checkbox" 
                  v-model="backupForm.include.files"
                />
                <span>Files</span>
              </label>
              <label class="checkbox-item">
                <input 
                  type="checkbox" 
                  v-model="backupForm.include.config"
                />
                <span>Configuration</span>
              </label>
              <label class="checkbox-item">
                <input 
                  type="checkbox" 
                  v-model="backupForm.include.logs"
                />
                <span>Logs</span>
              </label>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button 
            class="btn-primary" 
            @click="createBackup"
            :disabled="creating"
          >
            <span v-if="!creating">Create Backup</span>
            <span v-else>Creating...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Restore Backup Modal -->
    <div v-if="showRestoreModal" class="modal-overlay" @click="closeRestoreModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Restore Backup</h2>
          <button class="close-btn" @click="closeRestoreModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="backup-selection">
            <label>Select Backup to Restore</label>
            <select v-model="selectedBackupId" @change="loadBackupDetails">
              <option value="">Choose a backup...</option>
              <option 
                v-for="backup in completedBackups" 
                :key="backup.id"
                :value="backup.id"
              >
                {{ backup.name }} - {{ formatDate(backup.created_at) }}
              </option>
            </select>
          </div>

          <div v-if="selectedBackup" class="backup-details">
            <h3>Backup Information</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <label>Name:</label>
                <span>{{ selectedBackup.name }}</span>
              </div>
              <div class="detail-item">
                <label>Type:</label>
                <span>{{ selectedBackup.type }}</span>
              </div>
              <div class="detail-item">
                <label>Size:</label>
                <span>{{ formatSize(selectedBackup.size) }}</span>
              </div>
              <div class="detail-item">
                <label>Created:</label>
                <span>{{ formatDateTime(selectedBackup.created_at) }}</span>
              </div>
            </div>

            <div class="restore-options">
              <h3>Restore Options</h3>
              <div class="checkbox-grid">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="restoreOptions.database"
                  />
                  <span>Database</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="restoreOptions.files"
                  />
                  <span>Files</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="restoreOptions.config"
                  />
                  <span>Configuration</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="restoreOptions.logs"
                  />
                  <span>Logs</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeRestoreModal">Cancel</button>
          <button 
            class="btn-primary" 
            @click="restoreBackup"
            :disabled="!selectedBackupId || restoring"
          >
            <span v-if="!restoring">Restore Backup</span>
            <span v-else>Restoring...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Schedule Modal -->
    <div v-if="showScheduleModal" class="modal-overlay" @click="closeScheduleModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Backup Schedule</h2>
          <button class="close-btn" @click="closeScheduleModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="schedule-form">
            <div class="schedule-item">
              <h3>Daily Backup</h3>
              <div class="schedule-controls">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="scheduleForm.daily.enabled"
                  />
                  <span class="slider"></span>
                </label>
                <input 
                  v-model="scheduleForm.daily.time" 
                  type="time"
                  :disabled="!scheduleForm.daily.enabled"
                />
              </div>
            </div>

            <div class="schedule-item">
              <h3>Weekly Backup</h3>
              <div class="schedule-controls">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="scheduleForm.weekly.enabled"
                  />
                  <span class="slider"></span>
                </label>
                <select 
                  v-model="scheduleForm.weekly.day"
                  :disabled="!scheduleForm.weekly.enabled"
                >
                  <option value="monday">Monday</option>
                  <option value="tuesday">Tuesday</option>
                  <option value="wednesday">Wednesday</option>
                  <option value="thursday">Thursday</option>
                  <option value="friday">Friday</option>
                  <option value="saturday">Saturday</option>
                  <option value="sunday">Sunday</option>
                </select>
                <input 
                  v-model="scheduleForm.weekly.time" 
                  type="time"
                  :disabled="!scheduleForm.weekly.enabled"
                />
              </div>
            </div>

            <div class="schedule-item">
              <h3>Monthly Backup</h3>
              <div class="schedule-controls">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="scheduleForm.monthly.enabled"
                  />
                  <span class="slider"></span>
                </label>
                <input 
                  v-model.number="scheduleForm.monthly.day" 
                  type="number"
                  min="1"
                  max="31"
                  :disabled="!scheduleForm.monthly.enabled"
                />
                <input 
                  v-model="scheduleForm.monthly.time" 
                  type="time"
                  :disabled="!scheduleForm.monthly.enabled"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeScheduleModal">Cancel</button>
          <button class="btn-primary" @click="saveSchedule">Save Schedule</button>
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
const restoring = ref(false)
const backups = ref([])
const statusFilter = ref('')
const typeFilter = ref('')
const selectedBackupId = ref(null)
const selectedBackup = ref(null)

// Modal states
const showCreateModal = ref(false)
const showRestoreModal = ref(false)
const showScheduleModal = ref(false)
const showSettingsModal = ref(false)

const backupForm = reactive({
  name: '',
  description: '',
  type: 'full',
  compression: 'gzip',
  encryption: 'aes256',
  retention: 30,
  include: {
    database: true,
    files: true,
    config: true,
    logs: false
  }
})

const restoreOptions = reactive({
  database: true,
  files: true,
  config: true,
  logs: false
})

const schedule = reactive({
  daily: {
    enabled: true,
    time: '02:00',
    nextRun: ''
  },
  weekly: {
    enabled: true,
    day: 'sunday',
    time: '03:00',
    nextRun: ''
  },
  monthly: {
    enabled: false,
    day: 1,
    time: '04:00',
    nextRun: ''
  }
})

const scheduleForm = reactive({
  daily: {
    enabled: schedule.daily.enabled,
    time: schedule.daily.time
  },
  weekly: {
    enabled: schedule.weekly.enabled,
    day: schedule.weekly.day,
    time: schedule.weekly.time
  },
  monthly: {
    enabled: schedule.monthly.enabled,
    day: schedule.monthly.day,
    time: schedule.monthly.time
  }
})

// Mock backups data (in real app, this would come from API)
const mockBackups = [
  {
    id: 1,
    name: 'Daily Backup - 2024-01-20',
    description: 'Automatic daily backup',
    type: 'incremental',
    size: 1024 * 1024 * 512, // 512MB
    status: 'completed',
    created_at: '2024-01-20T02:00:00Z',
    duration: '5m 23s',
    progress: 100,
    include: ['database', 'files', 'config']
  },
  {
    id: 2,
    name: 'Weekly Full Backup',
    description: 'Complete system backup',
    type: 'full',
    size: 1024 * 1024 * 2048, // 2GB
    status: 'completed',
    created_at: '2024-01-19T03:00:00Z',
    duration: '12m 45s',
    progress: 100,
    include: ['database', 'files', 'config', 'logs']
  },
  {
    id: 3,
    name: 'Emergency Backup',
    description: 'Emergency backup before update',
    type: 'differential',
    size: 1024 * 1024 * 256, // 256MB
    status: 'in-progress',
    created_at: '2024-01-21T10:30:00Z',
    duration: null,
    progress: 65,
    include: ['database', 'config']
  },
  {
    id: 4,
    name: 'Failed Backup',
    description: 'Failed backup attempt',
    type: 'full',
    size: 0,
    status: 'failed',
    created_at: '2024-01-18T15:45:00Z',
    duration: '2m 10s',
    progress: 0,
    include: ['database', 'files']
  }
]

// Computed properties
const filteredBackups = computed(() => {
  let filtered = backups.value

  // Apply status filter
  if (statusFilter.value) {
    filtered = filtered.filter(backup => backup.status === statusFilter.value)
  }

  // Apply type filter
  if (typeFilter.value) {
    filtered = filtered.filter(backup => backup.type === typeFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const completedBackups = computed(() => {
  return backups.value.filter(backup => backup.status === 'completed')
})

const backupStats = computed(() => {
  const stats = {
    totalBackups: backups.value.length,
    successfulBackups: backups.value.filter(b => b.status === 'completed').length,
    totalStorage: backups.value.reduce((sum, backup) => sum + backup.size, 0),
    lastBackup: backups.value.length > 0 ? backups.value[0].created_at : null
  }
  return stats
})

// Methods
const loadBackups = async () => {
  loading.value = true
  try {
    // In real app, this would be an API call
    // const response = await apiGet('/backups')
    // if (response.success) {
    //   backups.value = response.backups || []
    // }
    
    // For demo, use mock data
    backups.value = mockBackups
  } catch (error) {
    console.error('Error loading backups:', error)
    showError('Failed to load backups')
  } finally {
    loading.value = false
  }
}

const filterBackups = () => {
  // This is reactive, no additional action needed
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const getEmptyMessage = () => {
  if (statusFilter.value || typeFilter.value) {
    return 'No backups match your search criteria'
  }
  return 'No backups created yet'
}

const createBackup = async () => {
  if (!backupForm.name) {
    showError('Please provide a backup name')
    return
  }

  creating.value = true
  try {
    // const response = await apiPost('/backups', backupForm)
    // if (response.success) {
    //   backups.value.unshift(response.backup)
    //   showSuccess('Backup created successfully')
    //   closeCreateModal()
    // }
    
    // For demo, simulate creation
    const newBackup = {
      id: Date.now(),
      ...backupForm,
      status: 'in-progress',
      progress: 0,
      created_at: new Date().toISOString(),
      size: 0,
      duration: null,
      include: Object.keys(backupForm.include).filter(key => backupForm.include[key])
    }
    
    backups.value.unshift(newBackup)
    showSuccess('Backup creation started')
    closeCreateModal()
    
    // Simulate progress
    setTimeout(() => {
      newBackup.status = 'completed'
      newBackup.progress = 100
      newBackup.size = 1024 * 1024 * 512 // 512MB
      newBackup.duration = '5m 23s'
    }, 5000)
  } catch (error) {
    console.error('Error creating backup:', error)
    showError('Failed to create backup')
  } finally {
    creating.value = false
  }
}

const restoreBackup = async (backup) => {
  const confirmed = await showConfirm(`Are you sure you want to restore from "${backup.name}"? This will overwrite current data.`)
  if (!confirmed) return

  restoring.value = true
  try {
    // const response = await apiPost(`/backups/${backup.id}/restore`, restoreOptions)
    // if (response.success) {
    //   showSuccess('Backup restored successfully')
    // }
    
    // For demo, simulate restore
    showSuccess('Backup restored successfully')
  } catch (error) {
    console.error('Error restoring backup:', error)
    showError('Failed to restore backup')
  } finally {
    restoring.value = false
  }
}

const downloadBackup = async (backup) => {
  try {
    // const response = await apiGet(`/backups/${backup.id}/download`)
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `${backup.name}.zip`
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
  const confirmed = await showConfirm(`Are you sure you want to delete "${backup.name}"?`)
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

const loadBackupDetails = () => {
  selectedBackup.value = completedBackups.value.find(b => b.id === selectedBackupId.value)
}

const saveSchedule = async () => {
  try {
    // const response = await apiPost('/backup/schedule', scheduleForm)
    // if (response.success) {
    //   Object.assign(schedule, response.schedule)
    //   showSuccess('Backup schedule saved successfully')
    //   closeScheduleModal()
    // }
    
    // For demo, simulate save
    Object.assign(schedule, scheduleForm)
    showSuccess('Backup schedule saved successfully')
    closeScheduleModal()
  } catch (error) {
    console.error('Error saving schedule:', error)
    showError('Failed to save backup schedule')
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetBackupForm()
}

const closeRestoreModal = () => {
  showRestoreModal.value = false
  selectedBackupId.value = null
  selectedBackup.value = null
  Object.assign(restoreOptions, {
    database: true,
    files: true,
    config: true,
    logs: false
  })
}

const closeScheduleModal = () => {
  showScheduleModal.value = false
}

const closeSettingsModal = () => {
  showSettingsModal.value = false
}

const resetBackupForm = () => {
  Object.assign(backupForm, {
    name: '',
    description: '',
    type: 'full',
    compression: 'gzip',
    encryption: 'aes256',
    retention: 30,
    include: {
      database: true,
      files: true,
      config: true,
      logs: false
    }
  })
}

// Lifecycle
onMounted(() => {
  loadBackups()
})
</script>

<style scoped>
.backup {
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

.card-icon.success {
  background: var(--success-color);
}

.card-icon.storage {
  background: var(--warning-color);
}

.card-icon.recent {
  background: var(--info-color);
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

.actions-section {
  margin-bottom: 3rem;
}

.action-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.create-backup-btn,
.restore-btn,
.schedule-btn,
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

.create-backup-btn:hover,
.restore-btn:hover,
.schedule-btn:hover,
.settings-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.restore-btn {
  background: var(--warning-color);
}

.restore-btn:hover {
  background: var(--warning-hover);
}

.schedule-btn {
  background: var(--info-color);
}

.schedule-btn:hover {
  background: var(--info-hover);
}

.settings-btn {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.settings-btn:hover {
  background: var(--glass-bg-hover);
}

.backups-section {
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

.header-controls {
  display: flex;
  gap: 1rem;
}

.filter-dropdown select {
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
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

.backups-table-container {
  overflow-x: auto;
}

.backups-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--glass-bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.backups-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.backups-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.backup-row {
  transition: background 0.3s ease;
}

.backup-row:hover {
  background: var(--glass-bg-hover);
}

.backup-name h4 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.backup-name p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.type-badge.full {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.type-badge.incremental {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.type-badge.differential {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.status-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.in-progress {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: var(--glass-bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
  border-radius: 3px;
  transition: width 0.3s ease;
}

.actions {
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
  transition: all 0 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.action-btn:hover:not(:disabled) {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.restore:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.download:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.schedule-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.schedule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.schedule-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.schedule-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.schedule-status {
  display: flex;
  align-items: center;
}

.status-badge.enabled {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.disabled {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.schedule-details {
  color: var(--text-secondary);
  line-height: 1.5;
}

.schedule-details p {
  margin: 0.25rem 0;
}

.edit-schedule-btn {
  padding: 0.5rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-schedule-btn:hover {
  background: var(--primary-hover);
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

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
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

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
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

.backup-selection {
  margin-bottom: 2rem;
}

.backup-selection label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-weight: 500;
}

.backup-selection select {
  width: 100%;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.backup-details {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.backup-details h3 {
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
}

.detail-item label {
  font-weight: 600;
  color: var(--text-secondary);
}

.restore-options {
  margin-top: 2rem;
}

.restore-options h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.schedule-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.schedule-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.schedule-item h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.schedule-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
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
  .backup {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .checkbox-grid {
    grid-template-columns: 1fr;
  }
  
  .schedule-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .schedule-controls {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
