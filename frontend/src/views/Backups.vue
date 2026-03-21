<template>
  <div class="backups">
    <div class="page-header">
      <h1>Backup Management</h1>
      <p>Manage system backups, schedules, and recovery options</p>
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
            <span class="backup-count">{{ backupStats.successfulBackups }} successful</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon storage">
            <i class="fas fa-hdd"></i>
          </div>
          <div class="card-content">
            <h3>{{ backupStats.totalStorage }}</h3>
            <p>Total Storage</p>
            <span class="storage-status">{{ backupStats.usedStorage }} used</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon schedule">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ backupStats.activeSchedules }}</h3>
            <p>Active Schedules</p>
            <span class="schedule-status">{{ backupStats.nextBackup }} next</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon health">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <h3>{{ backupStats.healthScore }}%</h3>
            <p>Health Score</p>
            <span class="health-status" :class="getHealthClass(backupStats.healthScore)">
              {{ getHealthStatus(backupStats.healthScore) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="create-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Backup
        </button>
        <button class="restore-btn" @click="showRestoreModal = true">
          <i class="fas fa-undo"></i>
          Restore
        </button>
        <button class="schedule-btn" @click="showScheduleModal = true">
          <i class="fas fa-calendar"></i>
          Schedule
        </button>
        <button class="verify-btn" @click="verifyAllBackups">
          <i class="fas fa-check-circle"></i>
          Verify All
        </button>
      </div>
    </div>

    <!-- Backup List -->
    <div class="backups-section">
      <div class="section-header">
        <h2>Backup History</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterBackups">
              <option value="">All Status</option>
              <option value="completed">Completed</option>
              <option value="running">Running</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="typeFilter" @change="filterBackups">
              <option value="">All Types</option>
              <option value="full">Full</option>
              <option value="incremental">Incremental</option>
              <option value="differential">Differential</option>
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
        <p>Loading backups...</p>
      </div>

      <div v-else-if="filteredBackups.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-database"></i>
        </div>
        <h3>No backups found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Backup
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="backups-grid">
          <div 
            v-for="backup in filteredBackups" 
            :key="backup.id"
            class="backup-card"
            :class="{ 'running': backup.status === 'running', 'failed': backup.status === 'failed', 'cancelled': backup.status === 'cancelled' }"
          >
            <div class="backup-header">
              <div class="backup-icon">
                <i :class="getBackupIcon(backup.type)"></i>
              </div>
              <div class="backup-status">
                <span :class="['status-badge', backup.status]">{{ backup.status }}</span>
              </div>
            </div>

            <div class="backup-content">
              <h3>{{ backup.name }}</h3>
              <p>{{ backup.description }}</p>
              
              <div class="backup-info">
                <span class="type">{{ backup.type }}</span>
                <span class="size">{{ backup.size }}</span>
                <span class="duration">{{ backup.duration }}</span>
              </div>

              <div class="backup-details">
                <div class="detail-item">
                  <label>Created:</label>
                  <span>{{ formatDateTime(backup.createdAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Files:</label>
                  <span>{{ backup.fileCount }}</span>
                </div>
                <div class="detail-item">
                  <label>Location:</label>
                  <span>{{ backup.location }}</span>
                </div>
              </div>

              <div class="backup-progress" v-if="backup.status === 'running'">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: backup.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ backup.progress }}%</span>
              </div>

              <div class="backup-actions">
                <button class="action-btn download" @click="downloadBackup(backup)" v-if="backup.status === 'completed'">
                  <i class="fas fa-download"></i>
                  Download
                </button>
                <button class="action-btn restore" @click="restoreBackup(backup)" v-if="backup.status === 'completed'">
                  <i class="fas fa-undo"></i>
                  Restore
                </button>
                <button class="action-btn verify" @click="verifyBackup(backup)" v-if="backup.status === 'completed'">
                  <i class="fas fa-check-circle"></i>
                  Verify
                </button>
                <button 
                  class="action-btn cancel"
                  @click="cancelBackup(backup)"
                  v-if="backup.status === 'running'"
                >
                  <i class="fas fa-times"></i>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="backups-list">
          <div 
            v-for="backup in filteredBackups" 
            :key="backup.id"
            class="backup-list-card"
            :class="{ 'running': backup.status === 'running', 'failed': backup.status === 'failed', 'cancelled': backup.status === 'cancelled' }"
          >
            <div class="backup-list-header">
              <div class="backup-list-info">
                <div class="backup-icon">
                  <i :class="getBackupIcon(backup.type)"></i>
                </div>
                <div class="backup-details">
                  <h3>{{ backup.name }}</h3>
                  <p>{{ backup.description }}</p>
                  <div class="backup-info">
                    <span class="type">{{ backup.type }}</span>
                    <span class="size">{{ backup.size }}</span>
                    <span :class="['status-badge', backup.status]">{{ backup.status }}</span>
                    <span class="duration">{{ backup.duration }}</span>
                  </div>
                </div>
              </div>
              <div class="backup-list-stats">
                <div class="detail-item">
                  <label>Created:</label>
                  <span>{{ formatDateTime(backup.createdAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Files:</label>
                  <span>{{ backup.fileCount }}</span>
                </div>
                <div class="detail-item">
                  <label>Location:</label>
                  <span>{{ backup.location }}</span>
                </div>
              </div>
              <div class="backup-list-actions">
                <button class="action-btn download" @click="downloadBackup(backup)" v-if="backup.status === 'completed'">
                  <i class="fas fa-download"></i>
                </button>
                <button class="action-btn restore" @click="restoreBackup(backup)" v-if="backup.status === 'completed'">
                  <i class="fas fa-undo"></i>
                </button>
                <button class="action-btn verify" @click="verifyBackup(backup)" v-if="backup.status === 'completed'">
                  <i class="fas fa-check-circle"></i>
                </button>
                <button 
                  class="action-btn cancel"
                  @click="cancelBackup(backup)"
                  v-if="backup.status === 'running'"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Backup Schedules -->
    <div class="schedules-section">
      <div class="section-header">
        <h2>Backup Schedules</h2>
        <div class="header-actions">
          <button class="add-schedule-btn" @click="showScheduleModal = true">
            <i class="fas fa-plus"></i>
            Add Schedule
          </button>
        </div>
      </div>

      <div class="schedules-grid">
        <div 
          v-for="schedule in schedules" 
          :key="schedule.id"
          class="schedule-card"
          :class="{ 'inactive': !schedule.enabled, 'error': schedule.status === 'error' }"
        >
          <div class="schedule-header">
            <div class="schedule-icon">
              <i class="fas fa-calendar"></i>
            </div>
            <div class="schedule-status">
              <span :class="['status-badge', schedule.status]">{{ schedule.status }}</span>
            </div>
          </div>

          <div class="schedule-content">
            <h3>{{ schedule.name }}</h3>
            <p>{{ schedule.description }}</p>
            
            <div class="schedule-info">
              <span class="frequency">{{ schedule.frequency }}</span>
              <span class="next-run">{{ formatDate(schedule.nextRun) }}</span>
              <span class="enabled">{{ schedule.enabled ? 'Enabled' : 'Disabled' }}</span>
            </div>

            <div class="schedule-details">
              <div class="detail-item">
                <label>Type:</label>
                <span>{{ schedule.type }}</span>
              </div>
              <div class="detail-item">
                <label>Retention:</label>
                <span>{{ schedule.retention }}</span>
              </div>
              <div class="detail-item">
                <label>Last Run:</label>
                <span>{{ formatDateTime(schedule.lastRun) }}</span>
              </div>
            </div>

            <div class="schedule-actions">
              <button class="action-btn run" @click="runSchedule(schedule)">
                <i class="fas fa-play"></i>
                Run Now
              </button>
              <button class="action-btn edit" @click="editSchedule(schedule)">
                <i class="fas fa-edit"></i>
                Edit
              </button>
              <button 
                class="action-btn toggle"
                @click="toggleSchedule(schedule)"
                :class="schedule.enabled ? 'disable' : 'enable'"
              >
                <i :class="schedule.enabled ? 'fas fa-pause' : 'fas fa-play'"></i>
                {{ schedule.enabled ? 'Disable' : 'Enable' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Storage Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Storage Analytics</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="timeRange" @change="updateAnalytics">
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
            </select>
          </div>
          <button class="refresh-btn" @click="refreshAnalytics">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="analytics-grid">
        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Storage Usage</h3>
            <span class="analytics-value">{{ analytics.storageUsage }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="storageChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Used: {{ analytics.storageUsed }}</span>
            <span class="detail-item">Total: {{ analytics.storageTotal }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Backup Frequency</h3>
            <span class="analytics-value">{{ analytics.backupsPerDay }}/day</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="frequencyChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">This week: {{ analytics.weeklyBackups }}</span>
            <span class="detail-item">This month: {{ analytics.monthlyBackups }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Success Rate</h3>
            <span class="analytics-value">{{ analytics.successRate }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="successChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Successful: {{ analytics.successfulBackups }}</span>
            <span class="detail-item">Failed: {{ analytics.failedBackups }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Backup Types</h3>
            <span class="analytics-value">{{ analytics.backupTypes.length }}</span>
          </div>
          <div class="backup-types-chart">
            <canvas ref="typesChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Full: {{ analytics.backupTypes.full }}</span>
            <span class="detail-item">Incremental: {{ analytics.backupTypes.incremental }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Backup Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Create Backup</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="backup-form">
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
              <label>Description</label>
              <textarea 
                v-model="backupForm.description" 
                placeholder="Describe this backup"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Backup Type *</label>
                <select v-model="backupForm.type" required>
                  <option value="full">Full</option>
                  <option value="incremental">Incremental</option>
                  <option value="differential">Differential</option>
                </select>
              </div>

              <div class="form-group">
                <label>Compression</label>
                <select v-model="backupForm.compression">
                  <option value="gzip">Gzip</option>
                  <option value="zip">Zip</option>
                  <option value="tar">Tar</option>
                  <option value="none">None</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Source Directories</label>
              <div class="directories-container">
                <div 
                  v-for="(directory, index) in backupForm.directories" 
                  :key="index"
                  class="directory-item"
                >
                  <input 
                    v-model="directory.path" 
                    type="text" 
                    placeholder="/path/to/directory"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeDirectory(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-directory-btn" @click="addDirectory">
                  <i class="fas fa-plus"></i>
                  Add Directory
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>Backup Location</label>
              <select v-model="backupForm.location">
                <option value="local">Local Storage</option>
                <option value="s3">Amazon S3</option>
                <option value="google-drive">Google Drive</option>
                <option value="dropbox">Dropbox</option>
                <option value="ftp">FTP Server</option>
              </select>
            </div>

            <div class="form-group">
              <label>Encryption</label>
              <select v-model="backupForm.encryption">
                <option value="none">None</option>
                <option value="aes256">AES-256</option>
                <option value="aes128">AES-128</option>
              </select>
            </div>

            <div class="form-group" v-if="backupForm.encryption !== 'none'">
              <label>Encryption Key</label>
              <input 
                v-model="backupForm.encryptionKey" 
                type="password" 
                placeholder="Enter encryption key"
              />
            </div>

            <div class="form-group">
              <label>Notifications</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="backupForm.notifyOnStart"
                  />
                  <span>Notify on start</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="backupForm.notifyOnComplete"
                  />
                  <span>Notify on completion</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="backupForm.notifyOnFailure"
                  />
                  <span>Notify on failure</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button class="btn-primary" @click="createBackup">
            <i class="fas fa-database"></i>
            Create Backup
          </button>
        </div>
      </div>
    </div>

    <!-- Restore Modal -->
    <div v-if="showRestoreModal" class="modal-overlay" @click="closeRestoreModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Restore Backup</h2>
          <button class="close-btn" @click="closeRestoreModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="restore-form">
            <div class="form-group">
              <label>Select Backup *</label>
              <select v-model="restoreForm.backupId" required>
                <option value="">Select backup to restore</option>
                <option 
                  v-for="backup in completedBackups" 
                  :key="backup.id"
                  :value="backup.id"
                >
                  {{ backup.name }} - {{ formatDate(backup.createdAt) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Restore Type</label>
              <select v-model="restoreForm.type">
                <option value="full">Full Restore</option>
                <option value="selective">Selective Restore</option>
                <option value="preview">Preview Only</option>
              </select>
            </div>

            <div class="form-group" v-if="restoreForm.type === 'selective'">
              <label>Select Files/Directories</label>
              <div class="files-container">
                <div 
                  v-for="(file, index) in restoreForm.selectedFiles" 
                  :key="index"
                  class="file-item"
                >
                  <label class="checkbox-item">
                    <input 
                      type="checkbox" 
                      v-model="file.selected"
                    />
                    <span>{{ file.name }}</span>
                  </label>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Restore Location</label>
              <input 
                v-model="restoreForm.restoreLocation" 
                type="text" 
                placeholder="/path/to/restore/location"
              />
            </div>

            <div class="form-group">
              <label>Overwrite Existing Files</label>
              <select v-model="restoreForm.overwrite">
                <option value="yes">Yes</option>
                <option value="no">No</option>
                <option value="prompt">Prompt</option>
              </select>
            </div>

            <div class="form-group">
              <label>Verify After Restore</label>
              <select v-model="restoreForm.verify">
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeRestoreModal">Cancel</button>
          <button class="btn-primary" @click="restoreBackup">
            <i class="fas fa-undo"></i>
            Restore Backup
          </button>
        </div>
      </div>
    </div>

    <!-- Schedule Modal -->
    <div v-if="showScheduleModal" class="modal-overlay" @click="closeScheduleModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create Schedule</h2>
          <button class="close-btn" @click="closeScheduleModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="schedule-form">
            <div class="form-group">
              <label>Schedule Name *</label>
              <input 
                v-model="scheduleForm.name" 
                type="text" 
                placeholder="Enter schedule name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="scheduleForm.description" 
                placeholder="Describe this schedule"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Frequency *</label>
                <select v-model="scheduleForm.frequency" required>
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div class="form-group">
                <label>Backup Type</label>
                <select v-model="scheduleForm.type">
                  <option value="full">Full</option>
                  <option value="incremental">Incremental</option>
                  <option value="differential">Differential</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Schedule Time</label>
              <input 
                v-model="scheduleForm.scheduleTime" 
                type="time" 
                placeholder="00:00"
              />
            </div>

            <div class="form-group">
              <label>Retention Period</label>
              <select v-model="scheduleForm.retention">
                <option value="7">7 days</option>
                <option value="30">30 days</option>
                <option value="90">90 days</option>
                <option value="365">1 year</option>
              </select>
            </div>

            <div class="form-group">
              <label>Source Directories</label>
              <div class="directories-container">
                <div 
                  v-for="(directory, index) in scheduleForm.directories" 
                  :key="index"
                  class="directory-item"
                >
                  <input 
                    v-model="directory.path" 
                    type="text" 
                    placeholder="/path/to/directory"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeScheduleDirectory(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-directory-btn" @click="addScheduleDirectory">
                  <i class="fas fa-plus"></i>
                  Add Directory
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>Notifications</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="scheduleForm.notifyOnStart"
                  />
                  <span>Notify on start</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="scheduleForm.notifyOnComplete"
                  />
                  <span>Notify on completion</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="scheduleForm.notifyOnFailure"
                  />
                  <span>Notify on failure</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeScheduleModal">Cancel</button>
          <button class="btn-primary" @click="createSchedule">
            <i class="fas fa-calendar"></i>
            Create Schedule
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
const typeFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('30')
const showCreateModal = ref(false)
const showRestoreModal = ref(false)
const showScheduleModal = ref(false)

// Chart instances
const storageChart = ref(null)
const frequencyChart = ref(null)
const successChart = ref(null)
const typesChart = ref(null)

// Backup stats
const backupStats = reactive({
  totalBackups: 156,
  successfulBackups: 142,
  totalStorage: '2.4TB',
  usedStorage: '1.8TB',
  activeSchedules: 8,
  nextBackup: '2 hours',
  healthScore: 94
})

// Storage analytics
const analytics = reactive({
  storageUsage: 75,
  storageUsed: '1.8TB',
  storageTotal: '2.4TB',
  backupsPerDay: 2.3,
  weeklyBackups: 16,
  monthlyBackups: 69,
  successRate: 91,
  successfulBackups: 142,
  failedBackups: 14,
  backupTypes: { full: 45, incremental: 111 }
})

// Backup form
const backupForm = reactive({
  name: '',
  description: '',
  type: 'full',
  compression: 'gzip',
  directories: [],
  location: 'local',
  encryption: 'none',
  encryptionKey: '',
  notifyOnStart: true,
  notifyOnComplete: true,
  notifyOnFailure: true
})

// Restore form
const restoreForm = reactive({
  backupId: '',
  type: 'full',
  selectedFiles: [],
  restoreLocation: '',
  overwrite: 'prompt',
  verify: 'yes'
})

// Schedule form
const scheduleForm = reactive({
  name: '',
  description: '',
  frequency: 'daily',
  type: 'incremental',
  scheduleTime: '02:00',
  retention: '30',
  directories: [],
  notifyOnStart: true,
  notifyOnComplete: true,
  notifyOnFailure: true
})

// Mock data
const backups = ref([
  {
    id: 1,
    name: 'System Backup - 2024-01-21',
    description: 'Full system backup including all directories',
    type: 'full',
    status: 'completed',
    size: '2.4GB',
    duration: '45 min',
    createdAt: '2024-01-21T10:30:00Z',
    fileCount: 1234,
    location: 'Local Storage',
    progress: 100
  },
  {
    id: 2,
    name: 'Database Backup - 2024-01-21',
    description: 'Database backup with transaction logs',
    type: 'incremental',
    status: 'completed',
    size: '456MB',
    duration: '12 min',
    createdAt: '2024-01-21T09:15:00Z',
    fileCount: 234,
    location: 'Amazon S3',
    progress: 100
  },
  {
    id: 3,
    name: 'User Files Backup - 2024-01-21',
    description: 'User home directories backup',
    type: 'differential',
    status: 'running',
    size: '1.2GB',
    duration: 'In progress',
    createdAt: '2024-01-21T11:00:00Z',
    fileCount: 567,
    location: 'Google Drive',
    progress: 67
  },
  {
    id: 4,
    name: 'Configuration Backup - 2024-01-20',
    description: 'System configuration and settings backup',
    type: 'full',
    status: 'failed',
    size: '234MB',
    duration: 'Failed',
    createdAt: '2024-01-20T23:45:00Z',
    fileCount: 89,
    location: 'Local Storage',
    progress: 0
  }
])

const schedules = ref([
  {
    id: 1,
    name: 'Daily System Backup',
    description: 'Daily full backup of system directories',
    frequency: 'daily',
    type: 'full',
    status: 'active',
    enabled: true,
    nextRun: '2024-01-22T02:00:00Z',
    retention: '30 days',
    lastRun: '2024-01-21T02:00:00Z'
  },
  {
    id: 2,
    name: 'Hourly Database Backup',
    description: 'Hourly incremental database backup',
    frequency: 'hourly',
    type: 'incremental',
    status: 'active',
    enabled: true,
    nextRun: '2024-01-21T11:00:00Z',
    retention: '7 days',
    lastRun: '2024-01-21T10:00:00Z'
  },
  {
    id: 3,
    name: 'Weekly User Backup',
    description: 'Weekly backup of user home directories',
    frequency: 'weekly',
    type: 'differential',
    status: 'inactive',
    enabled: false,
    nextRun: '2024-01-28T02:00:00Z',
    retention: '90 days',
    lastRun: '2024-01-14T02:00:00Z'
  }
])

// Computed properties
const filteredBackups = computed(() => {
  let filtered = backups.value

  if (statusFilter.value) {
    filtered = filtered.filter(backup => backup.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(backup => backup.type === typeFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

const completedBackups = computed(() => {
  return backups.value.filter(backup => backup.status === 'completed')
})

// Methods
const loadBackupData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/backups')
    // if (response.success) {
    //   backups.value = response.backups || []
    //   schedules.value = response.schedules || []
    //   Object.assign(backupStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading backup data:', error)
    showError('Failed to load backup data')
  } finally {
    loading.value = false
  }
}

const filterBackups = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || typeFilter.value) {
    return 'No backups match your filter criteria'
  }
  return 'No backups found'
}

const getBackupIcon = (type) => {
  const icons = {
    'full': 'fas fa-database',
    'incremental': 'fas fa-plus',
    'differential': 'fas fa-layer-group'
  }
  return icons[type] || 'fas fa-database'
}

const getHealthClass = (score) => {
  if (score >= 95) return 'excellent'
  if (score >= 90) return 'good'
  if (score >= 80) return 'fair'
  return 'poor'
}

const getHealthStatus = (score) => {
  if (score >= 95) return 'Excellent'
  if (score >= 90) return 'Good'
  if (score >= 80) return 'Fair'
  return 'Needs Improvement'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
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

const restoreBackup = async (backup) => {
  const confirmed = await showConfirm(`Are you sure you want to restore backup "${backup.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/backups/${backup.id}/restore`)
    // if (response.success) {
    //   showSuccess('Backup restore started successfully')
    // }
    
    // For demo, simulate restore
    showSuccess('Backup restore started successfully')
  } catch (error) {
    console.error('Error restoring backup:', error)
    showError('Failed to restore backup')
  }
}

const verifyBackup = async (backup) => {
  try {
    // const response = await apiPost(`/backups/${backup.id}/verify`)
    // if (response.success) {
    //   showSuccess('Backup verification completed successfully')
    // }
    
    // For demo, simulate verification
    showSuccess('Backup verification completed successfully')
  } catch (error) {
    console.error('Error verifying backup:', error)
    showError('Failed to verify backup')
  }
}

const cancelBackup = async (backup) => {
  const confirmed = await showConfirm(`Are you sure you want to cancel backup "${backup.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/backups/${backup.id}/cancel`)
    // if (response.success) {
    //   backup.status = 'cancelled'
    //   showSuccess('Backup cancelled successfully')
    // }
    
    // For demo, simulate cancellation
    backup.status = 'cancelled'
    showSuccess('Backup cancelled successfully')
  } catch (error) {
    console.error('Error cancelling backup:', error)
    showError('Failed to cancel backup')
  }
}

const verifyAllBackups = async () => {
  try {
    // const response = await apiPost('/backups/verify-all')
    // if (response.success) {
    //   showSuccess('All backups verified successfully')
    // }
    
    // For demo, simulate verification
    showSuccess('All backups verified successfully')
  } catch (error) {
    console.error('Error verifying backups:', error)
    showError('Failed to verify backups')
  }
}

const addDirectory = () => {
  backupForm.directories.push({ path: '' })
}

const removeDirectory = (index) => {
  backupForm.directories.splice(index, 1)
}

const addScheduleDirectory = () => {
  scheduleForm.directories.push({ path: '' })
}

const removeScheduleDirectory = (index) => {
  scheduleForm.directories.splice(index, 1)
}

const createBackup = async () => {
  if (!backupForm.name || backupForm.directories.length === 0) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/backups', backupForm)
    // if (response.success) {
    //   backups.value.unshift(response.backup)
    //   showSuccess('Backup created successfully')
    //   closeCreateModal()
    //   resetBackupForm()
    // }
    
    // For demo, simulate creation
    const newBackup = {
      id: Date.now(),
      ...backupForm,
      status: 'running',
      size: 'Calculating...',
      duration: 'In progress',
      createdAt: new Date().toISOString(),
      fileCount: 0,
      location: backupForm.location,
      progress: 0
    }
    
    backups.value.unshift(newBackup)
    showSuccess('Backup created successfully')
    closeCreateModal()
    resetBackupForm()
  } catch (error) {
    console.error('Error creating backup:', error)
    showError('Failed to create backup')
  }
}

const createSchedule = async () => {
  if (!scheduleForm.name || scheduleForm.directories.length === 0) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/backups/schedules', scheduleForm)
    // if (response.success) {
    //   schedules.value.unshift(response.schedule)
    //   showSuccess('Schedule created successfully')
    //   closeScheduleModal()
    //   resetScheduleForm()
    // }
    
    // For demo, simulate creation
    const newSchedule = {
      id: Date.now(),
      ...scheduleForm,
      status: 'active',
      enabled: true,
      nextRun: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      lastRun: null
    }
    
    schedules.value.unshift(newSchedule)
    showSuccess('Schedule created successfully')
    closeScheduleModal()
    resetScheduleForm()
  } catch (error) {
    console.error('Error creating schedule:', error)
    showError('Failed to create schedule')
  }
}

const runSchedule = async (schedule) => {
  try {
    // const response = await apiPost(`/backups/schedules/${schedule.id}/run`)
    // if (response.success) {
    //   showSuccess('Schedule executed successfully')
    // }
    
    // For demo, simulate execution
    showSuccess('Schedule executed successfully')
  } catch (error) {
    console.error('Error running schedule:', error)
    showError('Failed to run schedule')
  }
}

const editSchedule = (schedule) => {
  // Open schedule edit modal or navigate to detailed view
  showSuccess(`Editing schedule: ${schedule.name}`)
}

const toggleSchedule = async (schedule) => {
  try {
    // const response = await apiPut(`/backups/schedules/${schedule.id}/toggle`)
    // if (response.success) {
    //   schedule.enabled = !schedule.enabled
    //   showSuccess(`Schedule ${schedule.enabled ? 'enabled' : 'disabled'}`)
    // }
    
    // For demo, simulate toggle
    schedule.enabled = !schedule.enabled
    showSuccess(`Schedule ${schedule.enabled ? 'enabled' : 'disabled'}`)
  } catch (error) {
    console.error('Error toggling schedule:', error)
    showError('Failed to toggle schedule')
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetBackupForm()
}

const closeRestoreModal = () => {
  showRestoreModal.value = false
  resetRestoreForm()
}

const closeScheduleModal = () => {
  showScheduleModal.value = false
  resetScheduleForm()
}

const resetBackupForm = () => {
  Object.assign(backupForm, {
    name: '',
    description: '',
    type: 'full',
    compression: 'gzip',
    directories: [],
    location: 'local',
    encryption: 'none',
    encryptionKey: '',
    notifyOnStart: true,
    notifyOnComplete: true,
    notifyOnFailure: true
  })
}

const resetRestoreForm = () => {
  Object.assign(restoreForm, {
    backupId: '',
    type: 'full',
    selectedFiles: [],
    restoreLocation: '',
    overwrite: 'prompt',
    verify: 'yes'
  })
}

const resetScheduleForm = () => {
  Object.assign(scheduleForm, {
    name: '',
    description: '',
    frequency: 'daily',
    type: 'incremental',
    scheduleTime: '02:00',
    retention: '30',
    directories: [],
    notifyOnStart: true,
    notifyOnComplete: true,
    notifyOnFailure: true
  })
}

const updateAnalytics = async () => {
  try {
    // const response = await apiGet('/backups/analytics', { timeRange: timeRange.value })
    // if (response.success) {
    //   Object.assign(analytics, response.analytics)
    //   updateCharts()
    // }
    
    // For demo, simulate update
    updateCharts()
  } catch (error) {
    console.error('Error updating analytics:', error)
    showError('Failed to update analytics')
  }
}

const refreshAnalytics = async () => {
  try {
    // const response = await apiGet('/backups/analytics/refresh')
    // if (response.success) {
    //   Object.assign(analytics, response.analytics)
    //   updateCharts()
    // }
    
    // For demo, simulate refresh
    updateCharts()
    showSuccess('Analytics refreshed successfully')
  } catch (error) {
    console.error('Error refreshing analytics:', error)
    showError('Failed to refresh analytics')
  }
}

const initCharts = () => {
  // Initialize Storage Usage chart
  if (storageChart.value) storageChart.value.destroy()
  storageChart.value = new Chart(storageChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Used', 'Available'],
      datasets: [{
        data: [analytics.storageUsage, 100 - analytics.storageUsage],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(156, 163, 175, 0.3)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      }
    }
  })

  // Initialize Frequency chart
  if (frequencyChart.value) frequencyChart.value.destroy()
  frequencyChart.value = new Chart(frequencyChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 7 }, (_, i) => `Day ${i + 1}`),
      datasets: [{
        label: 'Backups',
        data: Array.from({ length: 7 }, () => Math.floor(Math.random() * 5)),
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

  // Initialize Success Rate chart
  if (successChart.value) successChart.value.destroy()
  successChart.value = new Chart(successChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Successful', 'Failed'],
      datasets: [{
        data: [analytics.successfulBackups, analytics.failedBackups],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ]
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

  // Initialize Types chart
  if (typesChart.value) typesChart.value.destroy()
  typesChart.value = new Chart(typesChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Full', 'Incremental'],
      datasets: [{
        data: [analytics.backupTypes.full, analytics.backupTypes.incremental],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      }
    }
  })
}

const updateCharts = () => {
  // Update charts with new data
  if (storageChart.value) {
    storageChart.value.data.datasets[0].data = [analytics.storageUsage, 100 - analytics.storageUsage]
    storageChart.value.update('none')
  }

  if (frequencyChart.value) {
    frequencyChart.value.data.datasets[0].data = Array.from({ length: 7 }, () => Math.floor(Math.random() * 5))
    frequencyChart.value.update('none')
  }

  if (successChart.value) {
    successChart.value.data.datasets[0].data = [analytics.successfulBackups, analytics.failedBackups]
    successChart.value.update('none')
  }

  if (typesChart.value) {
    typesChart.value.data.datasets[0].data = [analytics.backupTypes.full, analytics.backupTypes.incremental]
    typesChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadBackupData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (storageChart.value) storageChart.value.destroy()
  if (frequencyChart.value) frequencyChart.value.destroy()
  if (successChart.value) successChart.value.destroy()
  if (typesChart.value) typesChart.value.destroy()
})
</script>

<style scoped>
.backups {
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

.card-icon.storage {
  background: var(--warning-color);
}

.card-icon.schedule {
  background: var(--info-color);
}

.card-icon.health {
  background: var(--success-color);
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

.backup-count,
.storage-status,
.schedule-status,
.health-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.backup-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.storage-status {
  color: var(--text-secondary);
}

.schedule-status {
  color: var(--text-secondary);
}

.health-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.health-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.health-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.health-status.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
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
.restore-btn,
.schedule-btn,
.verify-btn {
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
.restore-btn:hover,
.schedule-btn:hover,
.verify-btn:hover {
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

.verify-btn {
  background: var(--success-color);
}

.verify-btn:hover {
  background: var(--success-hover);
}

.backups-section,
.schedules-section,
.analytics-section {
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

.add-schedule-btn {
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

.add-schedule-btn:hover {
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

.backups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
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
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.backup-card.running {
  border-color: var(--warning-color);
}

.backup-card.failed {
  border-color: var(--danger-color);
}

.backup-card.cancelled {
  border-color: var(--warning-color);
  opacity: 0.7;
}

.backup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.backup-icon {
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

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.running {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.cancelled {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.backup-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.backup-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.backup-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.size,
.duration {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.backup-details {
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

.backup-progress {
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

.backup-actions {
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

.action-btn.download:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.restore:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.verify:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.cancel:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.backups-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.backup-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.backup-list-card:hover {
  background: var(--glass-bg-hover);
}

.backup-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.backup-list-info {
  flex: 1;
}

.backup-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.backup-list-actions {
  display: flex;
  gap: 0.5rem;
}

.schedules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.schedule-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.schedule-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.schedule-card.inactive {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.schedule-card.error {
  border-color: var(--danger-color);
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.schedule-icon {
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

.schedule-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.schedule-status.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.schedule-status.inactive {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.schedule-status.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.schedule-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.schedule-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.schedule-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.frequency,
.next-run,
.enabled {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.enabled {
  color: #10b981;
}

.disabled {
  color: #ef4444;
}

.schedule-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.schedule-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.action-btn.toggle.enable:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.toggle.disable:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.analytics-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.analytics-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.analytics-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.analytics-chart,
.backup-types-chart {
  height: 150px;
  margin-bottom: 1rem;
}

.analytics-details {
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

.backup-form,
.restore-form,
.schedule-form {
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

.directories-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.directory-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.directory-item input {
  flex: 1;
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
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
  font-size: 0.9rem;
}

.remove-btn:hover {
  background: var(--danger-hover);
}

.add-directory-btn {
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

.add-directory-btn:hover {
  background: var(--primary-hover);
}

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

.files-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.file-item {
  padding: 0.75rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
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
  .backups {
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
  
  .backups-grid {
    grid-template-columns: 1fr;
  }
  
  .backup-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .backup-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .schedules-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
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
