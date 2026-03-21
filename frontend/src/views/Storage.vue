<template>
  <div class="storage">
    <div class="page-header">
      <h1>Storage Management</h1>
      <p>Monitor and manage system storage and file systems</p>
    </div>

    <!-- Storage Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-hdd"></i>
          </div>
          <div class="card-content">
            <h3>{{ storageStats.totalStorage }}</h3>
            <p>Total Storage</p>
            <span class="storage-size">{{ storageStats.usedStorage }} used</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon files">
            <i class="fas fa-file"></i>
          </div>
          <div class="card-content">
            <h3>{{ storageStats.totalFiles }}</h3>
            <p>Total Files</p>
            <span class="file-count">{{ storageStats.todayFiles }} today</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon performance">
            <i class="fas fa-tachometer-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ storageStats.avgSpeed }}MB/s</h3>
            <p>Avg Speed</p>
            <span class="speed-status">{{ storageStats.peakSpeed }}MB/s peak</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon health">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <h3>{{ storageStats.health }}%</h3>
            <p>Health Status</p>
            <span class="health-status" :class="getHealthClass(storageStats.health)">
              {{ getHealthStatus(storageStats.health) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="cleanup-btn" @click="showCleanupModal = true">
          <i class="fas fa-broom"></i>
          Cleanup
        </button>
        <button class="backup-btn" @click="showBackupModal = true">
          <i class="fas fa-save"></i>
          Backup
        </button>
        <button class="optimize-btn" @click="optimizeStorage">
          <i class="fas fa-tools"></i>
          Optimize
        </button>
        <button class="scan-btn" @click="scanStorage">
          <i class="fas fa-search"></i>
          Scan
        </button>
      </div>
    </div>

    <!-- Storage Volumes -->
    <div class="volumes-section">
      <div class="section-header">
        <h2>Storage Volumes</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterVolumes">
              <option value="">All Status</option>
              <option value="online">Online</option>
              <option value="offline">Offline</option>
              <option value="error">Error</option>
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
        <p>Loading storage volumes...</p>
      </div>

      <div v-else-if="filteredVolumes.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-hdd"></i>
        </div>
        <h3>No storage volumes found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="volumes-grid">
          <div 
            v-for="volume in filteredVolumes" 
            :key="volume.id"
            class="volume-card"
            :class="{ 'offline': volume.status === 'offline', 'error': volume.status === 'error' }"
          >
            <div class="volume-header">
              <div class="volume-icon">
                <i :class="getVolumeIcon(volume.type)"></i>
              </div>
              <div class="volume-status">
                <span :class="['status-badge', volume.status]">{{ volume.status }}</span>
              </div>
            </div>

            <div class="volume-content">
              <h3>{{ volume.name }}</h3>
              <p>{{ volume.description }}</p>
              
              <div class="volume-info">
                <span class="type">{{ volume.type }}</span>
                <span class="mount-point">{{ volume.mountPoint }}</span>
                <span class="size">{{ volume.size }}</span>
              </div>

              <div class="volume-stats">
                <div class="stat-item">
                  <label>Used:</label>
                  <span>{{ volume.used }}</span>
                </div>
                <div class="stat-item">
                  <label>Available:</label>
                  <span>{{ volume.available }}</span>
                </div>
                <div class="stat-item">
                  <label>Files:</label>
                  <span>{{ volume.fileCount }}</span>
                </div>
              </div>

              <div class="volume-actions">
                <button class="action-btn mount" @click="mountVolume(volume)" v-if="volume.status === 'offline'">
                  <i class="fas fa-plug"></i>
                  Mount
                </button>
                <button class="action-btn unmount" @click="unmountVolume(volume)" v-if="volume.status === 'online'">
                  <i class="fas fa-eject"></i>
                  Unmount
                </button>
                <button class="action-btn format" @click="formatVolume(volume)">
                  <i class="fas fa-eraser"></i>
                  Format
                </button>
                <button class="action-btn manage" @click="manageVolume(volume)">
                  <i class="fas fa-cog"></i>
                  Manage
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="volumes-list">
          <div 
            v-for="volume in filteredVolumes" 
            :key="volume.id"
            class="volume-list-card"
            :class="{ 'offline': volume.status === 'offline', 'error': volume.status === 'error' }"
          >
            <div class="volume-list-header">
              <div class="volume-list-info">
                <div class="volume-icon">
                  <i :class="getVolumeIcon(volume.type)"></i>
                </div>
                <div class="volume-details">
                  <h3>{{ volume.name }}</h3>
                  <p>{{ volume.description }}</p>
                  <div class="volume-info">
                    <span class="type">{{ volume.type }}</span>
                    <span class="mount-point">{{ volume.mountPoint }}</span>
                    <span :class="['status-badge', volume.status]">{{ volume.status }}</span>
                    <span class="size">{{ volume.size }}</span>
                  </div>
                </div>
              </div>
              <div class="volume-list-stats">
                <div class="stat-item">
                  <label>Used:</label>
                  <span>{{ volume.used }}</span>
                </div>
                <div class="stat-item">
                  <label>Available:</label>
                  <span>{{ volume.available }}</span>
                </div>
                <div class="stat-item">
                  <label>Files:</label>
                  <span>{{ volume.fileCount }}</span>
                </div>
              </div>
              <div class="volume-list-actions">
                <button class="action-btn mount" @click="mountVolume(volume)" v-if="volume.status === 'offline'">
                  <i class="fas fa-plug"></i>
                </button>
                <button class="action-btn unmount" @click="unmountVolume(volume)" v-if="volume.status === 'online'">
                  <i class="fas fa-eject"></i>
                </button>
                <button class="action-btn format" @click="formatVolume(volume)">
                  <i class="fas fa-eraser"></i>
                </button>
                <button class="action-btn manage" @click="manageVolume(volume)">
                  <i class="fas fa-cog"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- File Browser -->
    <div class="browser-section">
      <div class="section-header">
        <h2>File Browser</h2>
        <div class="header-actions">
          <div class="path-display">
            <input 
              v-model="currentPath" 
              type="text" 
              placeholder="Enter path to browse"
              @keyup.enter="navigateToPath"
            />
            <button class="browse-btn" @click="navigateToPath">
              <i class="fas fa-arrow-right"></i>
            </button>
          </div>
          <div class="filter-dropdown">
            <select v-model="fileFilter" @change="filterFiles">
              <option value="">All Files</option>
              <option value="image">Images</option>
              <option value="document">Documents</option>
              <option value="video">Videos</option>
              <option value="audio">Audio</option>
              <option value="archive">Archives</option>
            </select>
          </div>
          <div class="sort-dropdown">
            <select v-model="sortBy" @change="sortFiles">
              <option value="name">Name</option>
              <option value="size">Size</option>
              <option value="modified">Modified</option>
              <option value="type">Type</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading files...</p>
      </div>

      <div v-else-if="filteredFiles.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-folder-open"></i>
        </div>
        <h3>No files found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="files-container">
        <div class="files-header">
          <div class="files-breadcrumb">
            <span 
              v-for="(segment, index) in pathSegments" 
              :key="index"
              class="breadcrumb-segment"
              @click="navigateToPath(getPathTo(index))"
            >
              {{ segment }}
            </span>
          </div>
        </div>

        <div class="files-grid">
          <div 
            v-for="file in paginatedFiles" 
            :key="file.id"
            class="file-card"
            @click="selectFile(file)"
            @dblclick="openFile(file)"
          >
            <div class="file-icon">
              <i :class="getFileIcon(file.type)"></i>
            </div>
            <div class="file-info">
              <h4>{{ file.name }}</h4>
              <p>{{ formatFileSize(file.size) }}</p>
              <div class="file-meta">
                <span class="file-type">{{ file.type }}</span>
                <span class="file-modified">{{ formatDate(file.modified) }}</span>
              </div>
            </div>
            <div class="file-actions">
              <button class="action-btn download" @click.stop="downloadFile(file)">
                <i class="fas fa-download"></i>
              </button>
              <button class="action-btn delete" @click.stop="deleteFile(file)">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination">
          <div class="pagination-info">
            <span>Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredFiles.length }} files</span>
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

    <!-- Performance Metrics -->
    <div class="metrics-section">
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
            <h3>Storage Usage</h3>
            <span class="metric-value">{{ metrics.storageUsage }}%</span>
          </div>
          <div class="metric-chart">
            <canvas ref="storageChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Used: {{ metrics.storageUsed }}</span>
            <span class="detail-item">Total: {{ metrics.storageTotal }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>I/O Operations</h3>
            <span class="metric-value">{{ metrics.ioOps }}/s</span>
          </div>
          <div class="metric-chart">
            <canvas ref="ioChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Read: {{ metrics.readOps }}/s</span>
            <span class="detail-item">Write: {{ metrics.writeOps }}/s</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Network Speed</h3>
            <span class="metric-value">{{ metrics.networkSpeed }}MB/s</span>
          </div>
          <div class="metric-chart">
            <canvas ref="networkChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Upload: {{ metrics.uploadSpeed }}MB/s</span>
            <span class="detail-item">Download: {{ metrics.downloadSpeed }}MB/s</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Cache Hit Rate</h3>
            <span class="metric-value">{{ metrics.cacheHitRate }}%</span>
          </div>
          <div class="metric-chart">
            <canvas ref="cacheChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Hits: {{ metrics.cacheHits }}</span>
            <span class="detail-item">Misses: {{ metrics.cacheMisses }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cleanup Modal -->
    <div v-if="showCleanupModal" class="modal-overlay" @click="closeCleanupModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Storage Cleanup</h2>
          <button class="close-btn" @click="closeCleanupModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="cleanup-options">
            <div class="form-group">
              <label>Cleanup Options</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="cleanupOptions.tempFiles"
                  />
                  <span>Temporary files</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="cleanupOptions.duplicateFiles"
                  />
                  <span>Duplicate files</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="cleanupOptions.oldFiles"
                  />
                  <span>Old files (>30 days)</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="cleanupOptions.logFiles"
                  />
                  <span>Log files</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="cleanupOptions.cache"
                  />
                  <span>Cache files</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Target Volumes</label>
              <div class="volume-select">
                <div 
                  v-for="volume in volumes.value" 
                  :key="volume.id"
                  class="volume-checkbox"
                >
                  <label class="checkbox-item">
                    <input 
                      type="checkbox" 
                      v-model="cleanupOptions.selectedVolumes"
                      :value="volume.id"
                    />
                    <span>{{ volume.name }} ({{ volume.mountPoint }})</span>
                  </label>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>File Size Filter</label>
              <select v-model="cleanupOptions.minSize">
                <option value="">All sizes</option>
                <option value="1mb">>1MB+</option>
                <option value="10mb">10MB+</option>
                <option value="100mb">100MB+</option>
                <option value="1gb">1GB+</option>
              </select>
            </div>

            <div class="form-group">
              <label>Age Filter</label>
              <select v-model="cleanupOptions.age">
                <option value="">All ages</option>
                <option value="7">7 days</option>
                <option value="30">30 days</option>
                <option value="90">90 days</option>
                <option value="365">1 year</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCleanupModal">Cancel</button>
          <button class="btn-danger" @click="performCleanup">
            <i class="fas fa-broom"></i>
            Start Cleanup
          </button>
        </div>
      </div>
    </div>

    <!-- Backup Modal -->
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
            <div class="form-group">
              <label>Backup Type *</label>
              <select v-model="backupForm.type" required>
                <option value="full">Full Backup</option>
                <option value="incremental">Incremental</option>
                <option value="differential">Differential</option>
              </select>
            </div>

            <div class="form-group">
              <label>Target *</label>
              <select v-model="backupForm.targetId" required>
                <option value="">Select target</option>
                <option 
                  v-for="volume in volumes.value" 
                  :key="volume.id"
                  :value="volume.id"
                >
                  {{ volume.name }} ({{ volume.mountPoint }})
                </option>
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

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="backupForm.description" 
                placeholder="Describe this backup"
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeBackupModal">Cancel</button>
          <button class="btn-primary" @click="createBackup">
            <i class="fas fa-save"></i>
            Create Backup
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
const viewMode = ref('grid')
const timeRange = ref('24')
const showCleanupModal = ref(false)
const showBackupModal = ref(false)
const showTestModal = ref(false)
const showSettingsModal = ref(false)

// Chart instances
const storageChart = ref(null)
const ioChart = ref(null)
const networkChart = ref(null)
const cacheChart = ref(null)

// Storage stats
const storageStats = reactive({
  totalStorage: '500GB',
  usedStorage: '345GB',
  totalFiles: 124567,
  todayFiles: 234,
  avgSpeed: 125,
  peakSpeed: 450,
  health: 95
})

// Performance metrics
const metrics = reactive({
  storageUsage: 69,
  storageUsed: '345GB',
  storageTotal: '500GB',
  ioOps: 234,
  readOps: 156,
  writeOps: 78,
  networkSpeed: 125,
  uploadSpeed: 89,
  downloadSpeed: 156,
  cacheHitRate: 87,
  cacheHits: 45678,
  cacheMisses: 6789
})

// Cleanup options
const cleanupOptions = reactive({
  tempFiles: true,
  duplicateFiles: false,
  oldFiles: false,
  logFiles: false,
  cache: false,
  selectedVolumes: [],
  minSize: '',
  age: '',
  retention: '30'
})

// Backup form
const backupForm = reactive({
  type: 'full',
  targetId: '',
  compression: 'gzip',
  schedule: 'manual',
  retention: '30',
  description: ''
})

// Mock data
const volumes = ref([
  {
    id: 1,
    name: 'System Root',
    description: 'Main system partition',
    type: 'ext4',
    status: 'online',
    mountPoint: '/',
    size: '250GB',
    used: '180GB',
    available: '70GB',
    fileCount: 4567,
    lastModified: '2024-01-21T10:30:00Z'
  },
  {
    id: 2,
    name: 'Data Volume',
    description: 'Application data storage',
    type: 'ext4',
    status: 'online',
    mountPoint: '/data',
    size: '150GB',
    used: '120GB',
    available: '30GB',
    fileCount: 2345,
    lastModified: '2024-01-21T09:45:00Z'
  },
  {
    id: 3,
    name: 'Backup Volume',
    description: 'Backup storage volume',
    type: 'ext4',
    status: 'online',
    mountPoint: '/backup',
    size: '100GB',
    used: '45GB',
    available: '55GB',
    fileCount: 1234,
    lastModified: '2024-01-21T08:15:00Z'
  },
  {
    id: 4,
    name: 'Log Volume',
    description: 'System logs storage',
    type: 'ext4',
    status: 'online',
    mountPoint: '/var/log',
    size: '50GB',
    used: '35GB',
    available: '15GB',
    fileCount: 567,
    lastModified: '2024-01-21T07:30:00Z'
  },
  {
    id: 5,
    name: 'Cache Volume',
    description: 'Application cache storage',
    type: 'ext4',
    status: 'offline',
    mountPoint: '/cache',
    size: '25GB',
    used: '20GB',
    available: '5GB',
    fileCount: 234,
    lastModified: '2024-01-20T15:30:00Z'
  }
])

// File system state
const currentPath = ref('/')
const files = ref([])
const fileFilter = ref('')
const sortBy = ref('name')
const pageSize = ref(50)
const currentPage = ref(1)

// Computed properties
const filteredVolumes = computed(() => {
  let filtered = volumes.value

  if (statusFilter.value) {
    filtered = filtered.filter(volume => volume.status === statusFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.lastModified) - new Date(a.lastModified))
})

const filteredFiles = computed(() => {
  let filtered = files.value

  // Apply file filter
  if (fileFilter.value) {
    filtered = filtered.filter(file => file.type === fileFilter.value)
  }

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(file => 
      file.name.toLowerCase().includes(query) ||
      file.path.toLowerCase().includes(query)
    )
  }

  // Apply sorting
  if (sortBy.value === 'size') {
    filtered.sort((a, b) => b.size - a.size)
  } else if (sortBy.value === 'modified') {
    filtered.sort((a, b) => new Date(b.lastModified) - new Date(a.lastModified))
  } else if (sortBy.value === 'type') {
    filtered.sort((a, b) => a.type.localeCompare(b.type))
  }

  return filtered
})

const paginatedFiles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFiles.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredFiles.value.length / pageSize.value)
})

const startIndex = computed(() => {
  return (currentPage.value - 1) * pageSize.value
})

const endIndex = computed(() => {
  const end = startIndex.value + pageSize.value
  return Math.min(end, filteredFiles.value.length)
})

const pathSegments = computed(() => {
  return currentPath.value.split('/').filter(segment => segment !== '')
})

const getPathTo = (index) => {
  return pathSegments.value.slice(0, index + 1).join('/')
}

// Methods
const loadStorageData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/storage')
    // if (response.success) {
    //   volumes.value = response.volumes || []
    //   files.value = response.files || []
    //   Object.assign(storageStats, response.stats)
    //   Object.assign(metrics, response.metrics)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading storage data:', error)
    showError('Failed to load storage data')
  } finally {
    loading.value = false
  }
}

const filterVolumes = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value) {
    return 'No storage volumes match your filter criteria'
  }
  return 'No storage volumes found'
}

const getVolumeIcon = (type) => {
  const icons = {
    'ext4': 'fas fa-hdd',
    'ext3': 'fas fa-hdd',
    'ext2': 'fas fa-hdd',
    'ntfs': 'fas fa-hdd',
    'fat32': 'fas fa-hdd'
  }
  return icons[type] || 'fas fa-hdd'
}

const getHealthClass = (health) => {
  if (health >= 95) return 'excellent'
  if (health >= 90) return 'good'
  if (health >= 80) return 'fair'
  return 'poor'
}

const getHealthStatus = (health) => {
  if (health >= 95) return 'Excellent'
  if (health >= 90) return 'Good'
  if (health >= 80) return 'Fair'
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

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  const unitIndex = Math.floor(Math.log(size) / Math.log(1024))
  return `${(+(size / Math.pow(1024, unitIndex)).toFixed(2))} ${units[unitIndex]}`
}

const mountVolume = async (volume) => {
  try {
    // const response = await apiPost(`/storage/volumes/${volume.id}/mount`)
    // if (response.success) {
    //   volume.status = 'online'
    //   showSuccess('Volume mounted successfully')
    // }
    
    // For demo, simulate mount
    volume.status = 'online'
    showSuccess('Volume mounted successfully')
  } catch (error) {
    console.error('Error mounting volume:', error)
    showError('Failed to mount volume')
  }
}

const unmountVolume = async (volume) => {
  try {
    // const response = await apiPost(`/storage/volumes/${volume.id}/unmount`)
    // if (response.success) {
    //   volume.status = 'offline'
    //   showSuccess('Volume unmounted successfully')
    // }
    
    // For demo, simulate unmount
    volume.status = 'offline'
    showSuccess('Volume unmounted successfully')
  } catch (error) {
    console.error('Error unmounting volume:', error)
    showError('Failed to unmount volume')
  }
}

const formatVolume = async (volume) => {
  try {
    // const response = await apiPost(`/storage/volumes/${volume.id}/format`)
    // if (response.success) {
    //   showSuccess('Volume formatted successfully')
    // }
    
    // For demo, simulate format
    showSuccess('Volume formatted successfully')
  } catch (error) {
    console.error('Error formatting volume:', error)
    showError('Failed to format volume')
  }
}

const manageVolume = (volume) => {
  // Open volume management modal or navigate to detailed view
  showSuccess(`Opening management for ${volume.name}`)
}

const scanStorage = async () => {
  try {
    // const response = await apiPost('/storage/scan')
    // if (response.success) {
    //   files.value = response.files || []
    //   showSuccess('Storage scan completed')
    // }
    
    // For demo, simulate scan
    const mockFiles = [
      { id: 1, name: 'document.pdf', type: 'document', size: 2048000, path: '/documents/document.pdf', modified: '2024-01-21T10:30:00Z' },
      { id: 2, name: 'image.jpg', type: 'image', size: 1024000, path: '/images/image.jpg', modified: '2024-01-21T10:15:00Z' },
      { id: 3, name: 'video.mp4', type: 'video', size: 5242880, path: '/videos/video.mp4', modified: '2024-01-21T10:00:00Z' },
      { id: 4, name: 'audio.mp3', type: 'audio', size: 314572, path: '/audio/audio.mp3', modified: '2024-01-21T10:00:00Z' },
      { id: 5, name: 'archive.zip', type: 'archive', size: 10485760, path: '/archive.zip', modified: '2024-01-21T09:00:00Z' }
    ]
    files.value = mockFiles
    showSuccess('Storage scan completed')
  } catch (error) {
    console.error('Error scanning storage:', error)
    showError('Failed to scan storage')
  }
}

const navigateToPath = (path) => {
  currentPath.value = path
}

const selectFile = (file) => {
  // Handle file selection
  showSuccess(`Selected: ${file.name}`)
}

const openFile = (file) => {
  // Open file in default application
  showSuccess(`Opening ${file.name}`)
}

const downloadFile = async (file) => {
  // In real app, this would trigger file download
  const downloadUrl = `/api/files/${file.id}/download`
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showSuccess(`Downloading ${file.name}`)
}

const deleteFile = async (file) => {
  const confirmed = await showConfirm(`Are you sure you want to delete "${file.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/files/${file.id}`)
    // if (response.success) {
    //   const index = files.value.findIndex(f => f.id === file.id)
    //   if (index > -1) {
    //     files.value.splice(index, 1)
    //     showSuccess('File deleted successfully')
    //   }
    // }
    
    // For demo, simulate deletion
    const index = files.value.findIndex(f => f.id === file.id)
    if (index > -1) {
      files.value.splice(index, 1)
      showSuccess('File deleted successfully')
    }
  } catch (error) {
    console.error('Error deleting file:', error)
    showError('Failed to delete file')
  }
}

const refreshMetrics = async () => {
  try {
    // const response = await apiGet('/storage/metrics', { timeRange: timeRange.value })
    // if (response.success) {
    //   Object.assign(metrics, response.metrics)
    //   updateCharts()
    // }
    
    // For demo, simulate metrics update
    updateCharts()
  } catch (error) {
    console.error('Error updating metrics:', error)
    showError('Failed to update metrics')
  }
}

const updateCharts = () => {
  // Update charts with new data
  if (storageChart.value) {
    storageChart.value.data.datasets[0].data.shift()
    storageChart.value.data.datasets[0].push(metrics.storageUsage)
    storageChart.value.update('none')
  }

  if (ioChart.value) {
    ioChart.value.data.datasets[0].data.shift()
    ioChart.value.data.datasets[0].push(metrics.ioOps)
    ioChart.value.update('none')
  }

  if (networkChart.value) {
    networkChart.value.data.datasets[0].data.shift()
    networkChart.value.data.datasets[0].push(metrics.networkSpeed)
    networkChart.value.update('none')
  }

  if (cacheChart.value) {
    cacheChart.value.data.datasets[0].data.shift()
    cacheChart.value.data.datasets[0].push(metrics.cacheHitRate)
    cacheChart.value.update('none')
  }
}

const performCleanup = async () => {
  if (cleanupOptions.selectedVolumes.length === 0 && !cleanupOptions.tempFiles && !cleanupOptions.duplicateFiles && !cleanupOptions.oldFiles && !cleanupOptions.logFiles && !cleanupOptions.cache) {
    showError('Please select at least one cleanup option')
    return
  }

  const confirmed = await showConfirm('Are you sure you want to start the cleanup process? This action cannot be undone.')
  if (!confirmed) return

  try {
    // const response = await apiPost('/storage/cleanup', cleanupOptions)
    // if (response.success) {
    //   showSuccess('Cleanup completed successfully')
    //   closeCleanupModal()
    //   await loadStorageData()
    // }
    
    // For demo, simulate cleanup
    showSuccess('Cleanup completed successfully')
    closeCleanupModal()
    await loadStorageData()
  } catch (error) {
    console.error('Error performing cleanup:', error)
    showError('Failed to perform cleanup')
  }
}

const createBackup = async () => {
  if (!backupForm.targetId) {
    showError('Please select a target volume')
    return
  }

  if (!backupForm.type) {
    showError('Please select a backup type')
    return
  }

  try {
    // const response = await apiPost('/storage/backup', backupForm)
    // if (response.success) {
    //   showSuccess('Backup created successfully')
    //   closeBackupModal()
    //   resetBackupForm()
    //   await loadStorageData()
    // }
    
    // For demo, simulate backup creation
    showSuccess('Backup created successfully')
    closeBackupModal()
    resetBackupForm()
  } catch (error) {
    console.error('Error creating backup:', error)
    showError('Failed to create backup')
  }
}

const closeCleanupModal = () => {
  showCleanupModal.value = false
  resetCleanupOptions()
}

const closeBackupModal = () => {
  showBackupModal.value = false
  resetBackupForm()
}

const resetCleanupOptions = () => {
  Object.assign(cleanupOptions, {
    tempFiles: true,
    duplicateFiles: false,
    oldFiles: false,
    logFiles: false,
    cache: false,
    selectedVolumes: [],
    minSize: '',
    age: '',
    retention: '30'
  })
}

const resetBackupForm = () => {
  Object.assign(backupForm, {
    type: 'full',
    targetId: '',
    compression: 'gzip',
    schedule: 'manual',
    retention: '30',
    description: ''
  })
}

// Lifecycle
onMounted(() => {
  loadStorageData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (storageChart.value) storageChart.value.destroy()
  if (ioChart.value) ioChart.value.destroy()
  if (networkChart.value) networkChart.value.destroy()
  if (cacheChart.value) cacheChart.value.destroy()
})
</script>

<style scoped>
.storage {
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

.card-icon.files {
  background: var(--success-color);
}

.card-icon.performance {
  background: var(--warning-color);
}

.card-icon.health {
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

.storage-size,
.file-count,
.delivery-status,
.queue-status,
.speed-status,
.health-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.storage-size {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.file-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.delivery-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.delivery-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.delivery-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.delivery-status.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.queue-status {
  color: var(--text-secondary);
}

.speed-status {
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

.cleanup-btn,
.backup-btn,
.optimize-btn,
.scan-btn,
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

.cleanup-btn:hover,
.backup-btn:hover,
.optimize-btn:hover,
.scan-btn:hover,
.settings-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.cleanup-btn {
  background: var(--danger-color);
}

.cleanup-btn:hover {
  background: var(--danger-hover);
}

.backup-btn {
  background: var(--success-color);
}

.backup-btn:hover {
  background: var(--success-hover);
}

.optimize-btn {
  background: var(--warning-color);
}

.optimize-btn:hover {
  background: var(--warning-hover);
}

.scan-btn {
  background: var(--info-color);
}

.scan-btn:hover {
  background: var(--info-hover);
}

.settings-btn {
  background: var(--info-color);
}

.settings-btn:hover {
  background: var(--info-hover);
}

.volumes-section,
.templates-section,
.browser-section,
.metrics-section {
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

.volumes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.volume-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.volume-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.volume-card.inactive {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.volume-card.error {
  border-color: var(--danger-color);
}

.volume-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.volume-icon {
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

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.volume-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.volume-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.volume-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.mount-point,
.size {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.volume-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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

.volume-actions {
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

.action-btn.mount:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.unmount:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.format:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.manage:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.volumes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.volume-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.volume-list-card:hover {
  background: var(--glass-bg-hover);
}

.volume-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.volume-list-info {
  flex: 1;
}

.volume-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.volume-list-actions {
  display: flex;
  gap: 0.5rem;
}

.files-container {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.files-breadcrumb {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.breadcrumb-segment {
  color: var(--text-primary);
  cursor: pointer;
  transition: color 0.3s ease;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.breadcrumb-segment:hover {
  color: var(--primary-color);
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.file-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.file-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.file-icon {
  width: 40px;
  height: 40px;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: 1.2rem;
}

.file-icon img {
  width: 24px;
  height: 24px;
  object-fit: contain;
  border-radius: 4px;
}

.file-info {
  flex: 1;
}

.file-info h4 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.file-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  line-height: 1.4;
}

.file-meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.file-type {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.file-modified {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.file-actions {
  display: flex;
  gap: 0.5rem;
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

.cleanup-options,
.backup-form {
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

.checkbox-group {
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

.volume-select {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.volume-checkbox {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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
  .storage {
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
  
  .search-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .filter-dropdown select {
    width: 100%;
  }
  
  .view-toggle {
    flex-direction: row;
    justify-content: center;
    gap: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .service-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .service-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .template-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .template-details {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
