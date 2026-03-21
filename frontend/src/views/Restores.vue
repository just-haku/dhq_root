<template>
  <div class="restores">
    <div class="page-header">
      <h1>Restore Management</h1>
      <p>Manage system restores, recovery points, and rollback operations</p>
    </div>

    <!-- Restore Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-undo"></i>
          </div>
          <div class="card-content">
            <h3>{{ restoreStats.totalRestores }}</h3>
            <p>Total Restores</p>
            <span class="restore-count">{{ restoreStats.successfulRestores }} successful</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon points">
            <i class="fas fa-map-marker-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ restoreStats.recoveryPoints }}</h3>
            <p>Recovery Points</p>
            <span class="points-count">{{ restoreStats.availablePoints }} available</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon active">
            <i class="fas fa-play-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ restoreStats.activeRestores }}</h3>
            <p>Active Restores</p>
            <span class="active-count">{{ restoreStats.pendingRestores }} pending</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon health">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <h3>{{ restoreStats.healthScore }}%</h3>
            <p>Health Score</p>
            <span class="health-status" :class="getHealthClass(restoreStats.healthScore)">
              {{ getHealthStatus(restoreStats.healthScore) }}
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
          Create Restore
        </button>
        <button class="rollback-btn" @click="showRollbackModal = true">
          <i class="fas fa-history"></i>
          Rollback
        </button>
        <button class="verify-btn" @click="verifyAllRestores">
          <i class="fas fa-check-circle"></i>
          Verify All
        </button>
        <button class="cleanup-btn" @click="showCleanupModal = true">
          <i class="fas fa-broom"></i>
          Cleanup
        </button>
      </div>
    </div>

    <!-- Restore History -->
    <div class="restores-section">
      <div class="section-header">
        <h2>Restore History</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterRestores">
              <option value="">All Status</option>
              <option value="completed">Completed</option>
              <option value="running">Running</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
              <option value="pending">Pending</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="typeFilter" @change="filterRestores">
              <option value="">All Types</option>
              <option value="full">Full</option>
              <option value="selective">Selective</option>
              <option value="file">File</option>
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
        <p>Loading restores...</p>
      </div>

      <div v-else-if="filteredRestores.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-undo"></i>
        </div>
        <h3>No restores found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Restore
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="restores-grid">
          <div 
            v-for="restore in filteredRestores" 
            :key="restore.id"
            class="restore-card"
            :class="{ 'running': restore.status === 'running', 'failed': restore.status === 'failed', 'cancelled': restore.status === 'cancelled', 'pending': restore.status === 'pending' }"
          >
            <div class="restore-header">
              <div class="restore-icon">
                <i :class="getRestoreIcon(restore.type)"></i>
              </div>
              <div class="restore-status">
                <span :class="['status-badge', restore.status]">{{ restore.status }}</span>
              </div>
            </div>

            <div class="restore-content">
              <h3>{{ restore.name }}</h3>
              <p>{{ restore.description }}</p>
              
              <div class="restore-info">
                <span class="type">{{ restore.type }}</span>
                <span class="source">{{ restore.source }}</span>
                <span class="duration">{{ restore.duration }}</span>
              </div>

              <div class="restore-details">
                <div class="detail-item">
                  <label>Started:</label>
                  <span>{{ formatDateTime(restore.startedAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Files:</label>
                  <span>{{ restore.fileCount }}</span>
                </div>
                <div class="detail-item">
                  <label>Size:</label>
                  <span>{{ restore.size }}</span>
                </div>
              </div>

              <div class="restore-progress" v-if="restore.status === 'running'">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: restore.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ restore.progress }}%</span>
              </div>

              <div class="restore-actions">
                <button class="action-btn pause" @click="pauseRestore(restore)" v-if="restore.status === 'running'">
                  <i class="fas fa-pause"></i>
                  Pause
                </button>
                <button class="action-btn resume" @click="resumeRestore(restore)" v-if="restore.status === 'pending'">
                  <i class="fas fa-play"></i>
                  Resume
                </button>
                <button class="action-btn cancel" @click="cancelRestore(restore)" v-if="['running', 'pending'].includes(restore.status)">
                  <i class="fas fa-times"></i>
                  Cancel
                </button>
                <button class="action-btn retry" @click="retryRestore(restore)" v-if="restore.status === 'failed'">
                  <i class="fas fa-redo"></i>
                  Retry
                </button>
                <button class="action-btn view" @click="viewRestore(restore)" v-if="restore.status === 'completed'">
                  <i class="fas fa-eye"></i>
                  View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="restores-list">
          <div 
            v-for="restore in filteredRestores" 
            :key="restore.id"
            class="restore-list-card"
            :class="{ 'running': restore.status === 'running', 'failed': restore.status === 'failed', 'cancelled': restore.status === 'cancelled', 'pending': restore.status === 'pending' }"
          >
            <div class="restore-list-header">
              <div class="restore-list-info">
                <div class="restore-icon">
                  <i :class="getRestoreIcon(restore.type)"></i>
                </div>
                <div class="restore-details">
                  <h3>{{ restore.name }}</h3>
                  <p>{{ restore.description }}</p>
                  <div class="restore-info">
                    <span class="type">{{ restore.type }}</span>
                    <span class="source">{{ restore.source }}</span>
                    <span :class="['status-badge', restore.status]">{{ restore.status }}</span>
                    <span class="duration">{{ restore.duration }}</span>
                  </div>
                </div>
              </div>
              <div class="restore-list-stats">
                <div class="detail-item">
                  <label>Started:</label>
                  <span>{{ formatDateTime(restore.startedAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Files:</label>
                  <span>{{ restore.fileCount }}</span>
                </div>
                <div class="detail-item">
                  <label>Size:</label>
                  <span>{{ restore.size }}</span>
                </div>
              </div>
              <div class="restore-list-actions">
                <button class="action-btn pause" @click="pauseRestore(restore)" v-if="restore.status === 'running'">
                  <i class="fas fa-pause"></i>
                </button>
                <button class="action-btn resume" @click="resumeRestore(restore)" v-if="restore.status === 'pending'">
                  <i class="fas fa-play"></i>
                </button>
                <button class="action-btn cancel" @click="cancelRestore(restore)" v-if="['running', 'pending'].includes(restore.status)">
                  <i class="fas fa-times"></i>
                </button>
                <button class="action-btn retry" @click="retryRestore(restore)" v-if="restore.status === 'failed'">
                  <i class="fas fa-redo"></i>
                </button>
                <button class="action-btn view" @click="viewRestore(restore)" v-if="restore.status === 'completed'">
                  <i class="fas fa-eye"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recovery Points -->
    <div class="recovery-points-section">
      <div class="section-header">
        <h2>Recovery Points</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="pointFilter" @change="filterRecoveryPoints">
              <option value="">All Points</option>
              <option value="manual">Manual</option>
              <option value="automatic">Automatic</option>
              <option value="scheduled">Scheduled</option>
            </select>
          </div>
          <button class="create-point-btn" @click="showCreatePointModal = true">
            <i class="fas fa-plus"></i>
            Create Point
          </button>
        </div>
      </div>

      <div class="recovery-points-grid">
        <div 
          v-for="point in filteredRecoveryPoints" 
          :key="point.id"
          class="recovery-point-card"
          :class="{ 'corrupted': point.status === 'corrupted', 'expired': point.status === 'expired' }"
        >
          <div class="recovery-point-header">
            <div class="recovery-point-icon">
              <i class="fas fa-map-marker-alt"></i>
            </div>
            <div class="recovery-point-status">
              <span :class="['status-badge', point.status]">{{ point.status }}</span>
            </div>
          </div>

          <div class="recovery-point-content">
            <h3>{{ point.name }}</h3>
            <p>{{ point.description }}</p>
            
            <div class="recovery-point-info">
              <span class="type">{{ point.type }}</span>
              <span class="created">{{ formatDate(point.createdAt) }}</span>
              <span class="size">{{ point.size }}</span>
            </div>

            <div class="recovery-point-details">
              <div class="detail-item">
                <label>Created By:</label>
                <span>{{ point.createdBy }}</span>
              </div>
              <div class="detail-item">
                <label>Version:</label>
                <span>{{ point.version }}</span>
              </div>
              <div class="detail-item">
                <label>Expires:</label>
                <span>{{ formatDate(point.expiresAt) }}</span>
              </div>
            </div>

            <div class="recovery-point-actions">
              <button class="action-btn restore" @click="restoreFromPoint(point)">
                <i class="fas fa-undo"></i>
                Restore
              </button>
              <button class="action-btn verify" @click="verifyRecoveryPoint(point)">
                <i class="fas fa-check-circle"></i>
                Verify
              </button>
              <button class="action-btn delete" @click="deleteRecoveryPoint(point)">
                <i class="fas fa-trash"></i>
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Restore Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Restore Analytics</h2>
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
            <h3>Restore Success Rate</h3>
            <span class="analytics-value">{{ analytics.successRate }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="successChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Successful: {{ analytics.successfulRestores }}</span>
            <span class="detail-item">Failed: {{ analytics.failedRestores }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Restore Frequency</h3>
            <span class="analytics-value">{{ analytics.restoresPerDay }}/day</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="frequencyChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">This week: {{ analytics.weeklyRestores }}</span>
            <span class="detail-item">This month: {{ analytics.monthlyRestores }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Average Restore Time</h3>
            <span class="analytics-value">{{ analytics.avgRestoreTime }}</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="timeChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Fastest: {{ analytics.fastestRestore }}</span>
            <span class="detail-item">Slowest: {{ analytics.slowestRestore }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Restore Types</h3>
            <span class="analytics-value">{{ analytics.restoreTypes.length }}</span>
          </div>
          <div class="restore-types-chart">
            <canvas ref="typesChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Full: {{ analytics.restoreTypes.full }}</span>
            <span class="detail-item">Selective: {{ analytics.restoreTypes.selective }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Restore Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Create Restore</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="restore-form">
            <div class="form-group">
              <label>Restore Name *</label>
              <input 
                v-model="restoreForm.name" 
                type="text" 
                placeholder="Enter restore name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="restoreForm.description" 
                placeholder="Describe this restore"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Restore Type *</label>
                <select v-model="restoreForm.type" required>
                  <option value="full">Full Restore</option>
                  <option value="selective">Selective Restore</option>
                  <option value="file">File Restore</option>
                  <option value="database">Database Restore</option>
                </select>
              </div>

              <div class="form-group">
                <label>Source Backup *</label>
                <select v-model="restoreForm.sourceBackupId" required>
                  <option value="">Select backup</option>
                  <option 
                    v-for="backup in availableBackups" 
                    :key="backup.id"
                    :value="backup.id"
                  >
                    {{ backup.name }} - {{ formatDate(backup.createdAt) }}
                  </option>
                </select>
              </div>
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

            <div class="form-group">
              <label>Notifications</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="restoreForm.notifyOnStart"
                  />
                  <span>Notify on start</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="restoreForm.notifyOnComplete"
                  />
                  <span>Notify on completion</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="restoreForm.notifyOnFailure"
                  />
                  <span>Notify on failure</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button class="btn-primary" @click="createRestore">
            <i class="fas fa-undo"></i>
            Create Restore
          </button>
        </div>
      </div>
    </div>

    <!-- Rollback Modal -->
    <div v-if="showRollbackModal" class="modal-overlay" @click="closeRollbackModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>System Rollback</h2>
          <button class="close-btn" @click="closeRollbackModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="rollback-form">
            <div class="form-group">
              <label>Rollback Point *</label>
              <select v-model="rollbackForm.rollbackPointId" required>
                <option value="">Select rollback point</option>
                <option 
                  v-for="point in rollbackPoints" 
                  :key="point.id"
                  :value="point.id"
                >
                  {{ point.name }} - {{ formatDate(point.createdAt) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Rollback Type</label>
              <select v-model="rollbackForm.type">
                <option value="full">Full Rollback</option>
                <option value="partial">Partial Rollback</option>
                <option value="preview">Preview Only</option>
              </select>
            </div>

            <div class="form-group">
              <label>Confirmation Required</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="rollbackForm.confirmRequired"
                  />
                  <span>Require confirmation before rollback</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Backup Current State</label>
              <select v-model="rollbackForm.backupCurrent">
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeRollbackModal">Cancel</button>
          <button class="btn-primary danger" @click="executeRollback">
            <i class="fas fa-history"></i>
            Execute Rollback
          </button>
        </div>
      </div>
    </div>

    <!-- Create Recovery Point Modal -->
    <div v-if="showCreatePointModal" class="modal-overlay" @click="closeCreatePointModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create Recovery Point</h2>
          <button class="close-btn" @click="closeCreatePointModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="recovery-point-form">
            <div class="form-group">
              <label>Point Name *</label>
              <input 
                v-model="pointForm.name" 
                type="text" 
                placeholder="Enter recovery point name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="pointForm.description" 
                placeholder="Describe this recovery point"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Point Type</label>
                <select v-model="pointForm.type">
                  <option value="manual">Manual</option>
                  <option value="automatic">Automatic</option>
                  <option value="scheduled">Scheduled</option>
                </select>
              </div>

              <div class="form-group">
                <label>Retention Period</label>
                <select v-model="pointForm.retention">
                  <option value="7">7 days</option>
                  <option value="30">30 days</option>
                  <option value="90">90 days</option>
                  <option value="365">1 year</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Include System State</label>
              <select v-model="pointForm.includeSystemState">
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>

            <div class="form-group">
              <label>Compression</label>
              <select v-model="pointForm.compression">
                <option value="gzip">Gzip</option>
                <option value="zip">Zip</option>
                <option value="none">None</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreatePointModal">Cancel</button>
          <button class="btn-primary" @click="createRecoveryPoint">
            <i class="fas fa-map-marker-alt"></i>
            Create Point
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
const pointFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('30')
const showCreateModal = ref(false)
const showRollbackModal = ref(false)
const showCreatePointModal = ref(false)
const showCleanupModal = ref(false)

// Chart instances
const successChart = ref(null)
const frequencyChart = ref(null)
const timeChart = ref(null)
const typesChart = ref(null)

// Restore stats
const restoreStats = reactive({
  totalRestores: 89,
  successfulRestores: 78,
  recoveryPoints: 156,
  availablePoints: 142,
  activeRestores: 3,
  pendingRestores: 2,
  healthScore: 91
})

// Analytics
const analytics = reactive({
  successRate: 88,
  successfulRestores: 78,
  failedRestores: 11,
  restoresPerDay: 2.1,
  weeklyRestores: 15,
  monthlyRestores: 63,
  avgRestoreTime: '45 min',
  fastestRestore: '12 min',
  slowestRestore: '2h 15min',
  restoreTypes: { full: 34, selective: 55 }
})

// Restore form
const restoreForm = reactive({
  name: '',
  description: '',
  type: 'full',
  sourceBackupId: '',
  selectedFiles: [],
  restoreLocation: '',
  overwrite: 'prompt',
  verify: 'yes',
  notifyOnStart: true,
  notifyOnComplete: true,
  notifyOnFailure: true
})

// Rollback form
const rollbackForm = reactive({
  rollbackPointId: '',
  type: 'full',
  confirmRequired: true,
  backupCurrent: 'yes'
})

// Recovery point form
const pointForm = reactive({
  name: '',
  description: '',
  type: 'manual',
  retention: '30',
  includeSystemState: 'yes',
  compression: 'gzip'
})

// Mock data
const restores = ref([
  {
    id: 1,
    name: 'System Restore - 2024-01-21',
    description: 'Full system restore from backup',
    type: 'full',
    status: 'completed',
    source: 'System Backup - 2024-01-20',
    duration: '45 min',
    startedAt: '2024-01-21T10:30:00Z',
    fileCount: 1234,
    size: '2.4GB',
    progress: 100
  },
  {
    id: 2,
    name: 'Database Restore - 2024-01-21',
    description: 'Database restore from latest backup',
    type: 'database',
    status: 'running',
    source: 'Database Backup - 2024-01-21',
    duration: 'In progress',
    startedAt: '2024-01-21T11:00:00Z',
    fileCount: 234,
    size: '456MB',
    progress: 67
  },
  {
    id: 3,
    name: 'File Restore - 2024-01-20',
    description: 'Selective file restore',
    type: 'selective',
    status: 'failed',
    source: 'User Files Backup - 2024-01-20',
    duration: 'Failed',
    startedAt: '2024-01-20T15:30:00Z',
    fileCount: 56,
    size: '123MB',
    progress: 0
  },
  {
    id: 4,
    name: 'Quick Restore - 2024-01-20',
    description: 'Quick restore of configuration files',
    type: 'file',
    status: 'pending',
    source: 'Config Backup - 2024-01-20',
    duration: 'Pending',
    startedAt: '2024-01-20T23:45:00Z',
    fileCount: 12,
    size: '23MB',
    progress: 0
  }
])

const recoveryPoints = ref([
  {
    id: 1,
    name: 'Pre-Update Point',
    description: 'System state before major update',
    type: 'manual',
    status: 'available',
    createdAt: '2024-01-21T09:00:00Z',
    createdBy: 'admin',
    version: 'v2.1.0',
    expiresAt: '2024-02-21T09:00:00Z',
    size: '1.2GB'
  },
  {
    id: 2,
    name: 'Daily Auto Point',
    description: 'Automatic daily recovery point',
    type: 'automatic',
    status: 'available',
    createdAt: '2024-01-21T02:00:00Z',
    createdBy: 'system',
    version: 'v2.1.0',
    expiresAt: '2024-02-20T02:00:00Z',
    size: '2.1GB'
  },
  {
    id: 3,
    name: 'Weekly Point',
    description: 'Scheduled weekly recovery point',
    type: 'scheduled',
    status: 'corrupted',
    createdAt: '2024-01-14T02:00:00Z',
    createdBy: 'system',
    version: 'v2.0.5',
    expiresAt: '2024-02-14T02:00:00Z',
    size: '1.8GB'
  }
])

const availableBackups = ref([
  {
    id: 1,
    name: 'System Backup - 2024-01-20',
    createdAt: '2024-01-20T23:45:00Z'
  },
  {
    id: 2,
    name: 'Database Backup - 2024-01-21',
    createdAt: '2024-01-21T10:15:00Z'
  },
  {
    id: 3,
    name: 'User Files Backup - 2024-01-20',
    createdAt: '2024-01-20T15:30:00Z'
  }
])

const rollbackPoints = ref([
  {
    id: 1,
    name: 'Pre-Update Point',
    createdAt: '2024-01-21T09:00:00Z'
  },
  {
    id: 2,
    name: 'Daily Auto Point',
    createdAt: '2024-01-21T02:00:00Z'
  },
  {
    id: 3,
    name: 'Weekly Point',
    createdAt: '2024-01-14T02:00:00Z'
  }
])

// Computed properties
const filteredRestores = computed(() => {
  let filtered = restores.value

  if (statusFilter.value) {
    filtered = filtered.filter(restore => restore.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(restore => restore.type === typeFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.startedAt) - new Date(a.startedAt))
})

const filteredRecoveryPoints = computed(() => {
  let filtered = recoveryPoints.value

  if (pointFilter.value) {
    filtered = filtered.filter(point => point.type === pointFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

// Methods
const loadRestoreData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/restores')
    // if (response.success) {
    //   restores.value = response.restores || []
    //   recoveryPoints.value = response.recoveryPoints || []
    //   availableBackups.value = response.availableBackups || []
    //   rollbackPoints.value = response.rollbackPoints || []
    //   Object.assign(restoreStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading restore data:', error)
    showError('Failed to load restore data')
  } finally {
    loading.value = false
  }
}

const filterRestores = () => {
  // This is reactive, no additional action needed
}

const filterRecoveryPoints = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || typeFilter.value) {
    return 'No restores match your filter criteria'
  }
  return 'No restores found'
}

const getRestoreIcon = (type) => {
  const icons = {
    'full': 'fas fa-undo',
    'selective': 'fas fa-list',
    'file': 'fas fa-file',
    'database': 'fas fa-database'
  }
  return icons[type] || 'fas fa-undo'
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

const pauseRestore = async (restore) => {
  try {
    // const response = await apiPost(`/restores/${restore.id}/pause`)
    // if (response.success) {
    //   restore.status = 'pending'
    //   showSuccess('Restore paused successfully')
    // }
    
    // For demo, simulate pause
    restore.status = 'pending'
    showSuccess('Restore paused successfully')
  } catch (error) {
    console.error('Error pausing restore:', error)
    showError('Failed to pause restore')
  }
}

const resumeRestore = async (restore) => {
  try {
    // const response = await apiPost(`/restores/${restore.id}/resume`)
    // if (response.success) {
    //   restore.status = 'running'
    //   showSuccess('Restore resumed successfully')
    // }
    
    // For demo, simulate resume
    restore.status = 'running'
    showSuccess('Restore resumed successfully')
  } catch (error) {
    console.error('Error resuming restore:', error)
    showError('Failed to resume restore')
  }
}

const cancelRestore = async (restore) => {
  const confirmed = await showConfirm(`Are you sure you want to cancel restore "${restore.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/restores/${restore.id}/cancel`)
    // if (response.success) {
    //   restore.status = 'cancelled'
    //   showSuccess('Restore cancelled successfully')
    // }
    
    // For demo, simulate cancellation
    restore.status = 'cancelled'
    showSuccess('Restore cancelled successfully')
  } catch (error) {
    console.error('Error cancelling restore:', error)
    showError('Failed to cancel restore')
  }
}

const retryRestore = async (restore) => {
  try {
    // const response = await apiPost(`/restores/${restore.id}/retry`)
    // if (response.success) {
    //   restore.status = 'pending'
    //   showSuccess('Restore retry initiated')
    // }
    
    // For demo, simulate retry
    restore.status = 'pending'
    showSuccess('Restore retry initiated')
  } catch (error) {
    console.error('Error retrying restore:', error)
    showError('Failed to retry restore')
  }
}

const viewRestore = (restore) => {
  // Open restore details modal or navigate to detailed view
  showSuccess(`Viewing restore details: ${restore.name}`)
}

const verifyAllRestores = async () => {
  try {
    // const response = await apiPost('/restores/verify-all')
    // if (response.success) {
    //   showSuccess('All restores verified successfully')
    // }
    
    // For demo, simulate verification
    showSuccess('All restores verified successfully')
  } catch (error) {
    console.error('Error verifying restores:', error)
    showError('Failed to verify restores')
  }
}

const restoreFromPoint = async (point) => {
  const confirmed = await showConfirm(`Are you sure you want to restore from recovery point "${point.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/recovery-points/${point.id}/restore`)
    // if (response.success) {
    //   showSuccess('Restore from recovery point started successfully')
    // }
    
    // For demo, simulate restore
    showSuccess('Restore from recovery point started successfully')
  } catch (error) {
    console.error('Error restoring from point:', error)
    showError('Failed to restore from recovery point')
  }
}

const verifyRecoveryPoint = async (point) => {
  try {
    // const response = await apiPost(`/recovery-points/${point.id}/verify`)
    // if (response.success) {
    //   showSuccess('Recovery point verified successfully')
    // }
    
    // For demo, simulate verification
    showSuccess('Recovery point verified successfully')
  } catch (error) {
    console.error('Error verifying recovery point:', error)
    showError('Failed to verify recovery point')
  }
}

const deleteRecoveryPoint = async (point) => {
  const confirmed = await showConfirm(`Are you sure you want to delete recovery point "${point.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/recovery-points/${point.id}`)
    // if (response.success) {
    //   const index = recoveryPoints.value.findIndex(p => p.id === point.id)
    //   if (index > -1) {
    //     recoveryPoints.value.splice(index, 1)
    //     showSuccess('Recovery point deleted successfully')
    //   }
    // }
    
    // For demo, simulate deletion
    const index = recoveryPoints.value.findIndex(p => p.id === point.id)
    if (index > -1) {
      recoveryPoints.value.splice(index, 1)
      showSuccess('Recovery point deleted successfully')
    }
  } catch (error) {
    console.error('Error deleting recovery point:', error)
    showError('Failed to delete recovery point')
  }
}

const createRestore = async () => {
  if (!restoreForm.name || !restoreForm.sourceBackupId) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/restores', restoreForm)
    // if (response.success) {
    //   restores.value.unshift(response.restore)
    //   showSuccess('Restore created successfully')
    //   closeCreateModal()
    //   resetRestoreForm()
    // }
    
    // For demo, simulate creation
    const newRestore = {
      id: Date.now(),
      ...restoreForm,
      status: 'pending',
      source: availableBackups.value.find(b => b.id === restoreForm.sourceBackupId)?.name || 'Unknown',
      duration: 'Pending',
      startedAt: new Date().toISOString(),
      fileCount: 0,
      size: 'Calculating...',
      progress: 0
    }
    
    restores.value.unshift(newRestore)
    showSuccess('Restore created successfully')
    closeCreateModal()
    resetRestoreForm()
  } catch (error) {
    console.error('Error creating restore:', error)
    showError('Failed to create restore')
  }
}

const executeRollback = async () => {
  if (!rollbackForm.rollbackPointId) {
    showError('Please select a rollback point')
    return
  }

  const confirmed = await showConfirm('Are you sure you want to execute this rollback? This action cannot be undone.')
  if (!confirmed) return

  try {
    // const response = await apiPost('/system/rollback', rollbackForm)
    // if (response.success) {
    //   showSuccess('Rollback executed successfully')
    //   closeRollbackModal()
    //   resetRollbackForm()
    // }
    
    // For demo, simulate rollback
    showSuccess('Rollback executed successfully')
    closeRollbackModal()
    resetRollbackForm()
  } catch (error) {
    console.error('Error executing rollback:', error)
    showError('Failed to execute rollback')
  }
}

const createRecoveryPoint = async () => {
  if (!pointForm.name) {
    showError('Please enter a recovery point name')
    return
  }

  try {
    // const response = await apiPost('/recovery-points', pointForm)
    // if (response.success) {
    //   recoveryPoints.value.unshift(response.point)
    //   showSuccess('Recovery point created successfully')
    //   closeCreatePointModal()
    //   resetPointForm()
    // }
    
    // For demo, simulate creation
    const newPoint = {
      id: Date.now(),
      ...pointForm,
      status: 'available',
      createdAt: new Date().toISOString(),
      createdBy: 'admin',
      version: 'v2.1.0',
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      size: 'Calculating...'
    }
    
    recoveryPoints.value.unshift(newPoint)
    showSuccess('Recovery point created successfully')
    closeCreatePointModal()
    resetPointForm()
  } catch (error) {
    console.error('Error creating recovery point:', error)
    showError('Failed to create recovery point')
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetRestoreForm()
}

const closeRollbackModal = () => {
  showRollbackModal.value = false
  resetRollbackForm()
}

const closeCreatePointModal = () => {
  showCreatePointModal.value = false
  resetPointForm()
}

const resetRestoreForm = () => {
  Object.assign(restoreForm, {
    name: '',
    description: '',
    type: 'full',
    sourceBackupId: '',
    selectedFiles: [],
    restoreLocation: '',
    overwrite: 'prompt',
    verify: 'yes',
    notifyOnStart: true,
    notifyOnComplete: true,
    notifyOnFailure: true
  })
}

const resetRollbackForm = () => {
  Object.assign(rollbackForm, {
    rollbackPointId: '',
    type: 'full',
    confirmRequired: true,
    backupCurrent: 'yes'
  })
}

const resetPointForm = () => {
  Object.assign(pointForm, {
    name: '',
    description: '',
    type: 'manual',
    retention: '30',
    includeSystemState: 'yes',
    compression: 'gzip'
  })
}

const updateAnalytics = async () => {
  try {
    // const response = await apiGet('/restores/analytics', { timeRange: timeRange.value })
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
    // const response = await apiGet('/restores/analytics/refresh')
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
  // Initialize Success Rate chart
  if (successChart.value) successChart.value.destroy()
  successChart.value = new Chart(successChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Successful', 'Failed'],
      datasets: [{
        data: [analytics.successfulRestores, analytics.failedRestores],
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
        label: 'Restores',
        data: Array.from({ length: 7 }, () => Math.floor(Math.random() * 5)),
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

  // Initialize Time chart
  if (timeChart.value) timeChart.value.destroy()
  timeChart.value = new Chart(timeChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Restore Time (min)',
        data: [45, 32, 67, 23, 45, 12, 34],
        backgroundColor: 'rgba(245, 158, 11, 0.8)'
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
      labels: ['Full', 'Selective', 'File', 'Database'],
      datasets: [{
        data: [analytics.restoreTypes.full, analytics.restoreTypes.selective, 12, 23],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)'
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
  if (successChart.value) {
    successChart.value.data.datasets[0].data = [analytics.successfulRestores, analytics.failedRestores]
    successChart.value.update('none')
  }

  if (frequencyChart.value) {
    frequencyChart.value.data.datasets[0].data = Array.from({ length: 7 }, () => Math.floor(Math.random() * 5))
    frequencyChart.value.update('none')
  }

  if (timeChart.value) {
    timeChart.value.data.datasets[0].data = [45, 32, 67, 23, 45, 12, 34]
    timeChart.value.update('none')
  }

  if (typesChart.value) {
    typesChart.value.data.datasets[0].data = [analytics.restoreTypes.full, analytics.restoreTypes.selective, 12, 23]
    typesChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadRestoreData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (successChart.value) successChart.value.destroy()
  if (frequencyChart.value) frequencyChart.value.destroy()
  if (timeChart.value) timeChart.value.destroy()
  if (typesChart.value) typesChart.value.destroy()
})
</script>

<style scoped>
.restores {
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

.card-icon.points {
  background: var(--warning-color);
}

.card-icon.active {
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

.restore-count,
.points-count,
.active-count,
.health-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.restore-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.points-count {
  color: var(--text-secondary);
}

.active-count {
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
.rollback-btn,
.verify-btn,
.cleanup-btn {
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
.rollback-btn:hover,
.verify-btn:hover,
.cleanup-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.rollback-btn {
  background: var(--warning-color);
}

.rollback-btn:hover {
  background: var(--warning-hover);
}

.verify-btn {
  background: var(--success-color);
}

.verify-btn:hover {
  background: var(--success-hover);
}

.cleanup-btn {
  background: var(--info-color);
}

.cleanup-btn:hover {
  background: var(--info-hover);
}

.restores-section,
.recovery-points-section,
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

.create-point-btn {
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

.create-point-btn:hover {
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

.restores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.restore-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.restore-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.restore-card.running {
  border-color: var(--warning-color);
}

.restore-card.failed {
  border-color: var(--danger-color);
}

.restore-card.cancelled {
  border-color: var(--warning-color);
  opacity: 0.7;
}

.restore-card.pending {
  border-color: var(--info-color);
}

.restore-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.restore-icon {
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

.status-badge.pending {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.restore-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.restore-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.restore-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.source,
.duration {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.restore-details {
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

.restore-progress {
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

.restore-actions {
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

.action-btn.cancel:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.action-btn.retry:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.view:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.restores-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.restore-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.restore-list-card:hover {
  background: var(--glass-bg-hover);
}

.restore-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.restore-list-info {
  flex: 1;
}

.restore-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.restore-list-actions {
  display: flex;
  gap: 0.5rem;
}

.recovery-points-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.recovery-point-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.recovery-point-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.recovery-point-card.corrupted {
  border-color: var(--danger-color);
  opacity: 0.7;
}

.recovery-point-card.expired {
  border-color: var(--warning-color);
  opacity: 0.7;
}

.recovery-point-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.recovery-point-icon {
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

.recovery-point-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.recovery-point-status.available {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.recovery-point-status.corrupted {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.recovery-point-status.expired {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.recovery-point-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.recovery-point-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.recovery-point-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.recovery-point-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn.restore:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.verify:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
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
.restore-types-chart {
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

.restore-form,
.rollback-form,
.recovery-point-form {
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

.btn-primary.danger {
  background: var(--danger-color);
}

.btn-primary.danger:hover {
  background: var(--danger-hover);
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
  .restores {
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
  
  .restores-grid {
    grid-template-columns: 1fr;
  }
  
  .restore-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .restore-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .recovery-points-grid {
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
