<template>
  <div class="cache">
    <div class="page-header">
      <h1>Cache Management</h1>
      <p>Monitor and manage system cache performance</p>
    </div>

    <!-- Cache Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-memory"></i>
          </div>
          <div class="card-content">
            <h3>{{ cacheStats.totalSize }}</h3>
            <p>Total Cache Size</p>
            <span class="cache-size">{{ cacheStats.avgSize }} avg</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon hits">
            <i class="fas fa-bullseye"></i>
          </div>
          <div class="card-content">
            <h3>{{ cacheStats.hitRate }}%</h3>
            <p>Hit Rate</p>
            <span class="hit-status" :class="getHitRateClass(cacheStats.hitRate)">
              {{ getHitRateStatus(cacheStats.hitRate) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon entries">
            <i class="fas fa-database"></i>
          </div>
          <div class="card-content">
            <h3>{{ cacheStats.totalEntries }}</h3>
            <p>Total Entries</p>
            <span class="entry-count">{{ cacheStats.activeEntries }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon operations">
            <i class="fas fa-exchange-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ cacheStats.totalOps }}</h3>
            <p>Operations/sec</p>
            <span class="ops-status">{{ cacheStats.currentOps }} current</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="clear-btn" @click="showClearModal = true">
          <i class="fas fa-trash"></i>
          Clear Cache
        </button>
        <button class="optimize-btn" @click="optimizeCache">
          <i class="fas fa-tools"></i>
          Optimize
        </button>
        <button class="refresh-btn" @click="refreshCache">
          <i class="fas fa-sync"></i>
          Refresh
        </button>
        <button class="settings-btn" @click="showSettingsModal = true">
          <i class="fas fa-cog"></i>
          Settings
        </button>
      </div>
    </div>

    <!-- Cache Instances -->
    <div class="cache-section">
      <div class="section-header">
        <h2>Cache Instances</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterCaches">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
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
        <p>Loading cache instances...</p>
      </div>

      <div v-else-if="filteredCaches.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-memory"></i>
        </div>
        <h3>No cache instances found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="cache-grid">
          <div 
            v-for="cache in filteredCaches" 
            :key="cache.id"
            class="cache-card"
            :class="{ 'inactive': cache.status === 'inactive', 'error': cache.status === 'error' }"
          >
            <div class="cache-header">
              <div class="cache-icon">
                <i :class="getCacheIcon(cache.type)"></i>
              </div>
              <div class="cache-status">
                <span :class="['status-badge', cache.status]">{{ cache.status }}</span>
              </div>
            </div>

            <div class="cache-content">
              <h3>{{ cache.name }}</h3>
              <p>{{ cache.description }}</p>
              
              <div class="cache-info">
                <span class="type">{{ cache.type }}</span>
                <span class="size">{{ cache.size }}</span>
                <span class="entries">{{ cache.entries }} entries</span>
              </div>

              <div class="cache-stats">
                <div class="stat-item">
                  <label>Hit Rate:</label>
                  <span :class="getHitRateClass(cache.hitRate)">{{ cache.hitRate }}%</span>
                </div>
                <div class="stat-item">
                  <label>Memory:</label>
                  <span>{{ cache.memoryUsage }}</span>
                </div>
                <div class="stat-item">
                  <label>TTL:</label>
                  <span>{{ cache.ttl }}</span>
                </div>
              </div>

              <div class="cache-actions">
                <button class="action-btn view" @click="viewCacheDetails(cache)">
                  <i class="fas fa-eye"></i>
                  View
                </button>
                <button class="action-btn clear" @click="clearCacheInstance(cache)">
                  <i class="fas fa-trash"></i>
                  Clear
                </button>
                <button class="action-btn manage" @click="manageCache(cache)">
                  <i class="fas fa-cog"></i>
                  Manage
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="cache-list">
          <div 
            v-for="cache in filteredCaches" 
            :key="cache.id"
            class="cache-list-card"
            :class="{ 'inactive': cache.status === 'inactive', 'error': cache.status === 'error' }"
          >
            <div class="cache-list-header">
              <div class="cache-list-info">
                <div class="cache-icon">
                  <i :class="getCacheIcon(cache.type)"></i>
                </div>
                <div class="cache-details">
                  <h3>{{ cache.name }}</h3>
                  <p>{{ cache.description }}</p>
                  <div class="cache-info">
                    <span class="type">{{ cache.type }}</span>
                    <span class="size">{{ cache.size }}</span>
                    <span :class="['status-badge', cache.status]">{{ cache.status }}</span>
                    <span class="entries">{{ cache.entries }} entries</span>
                  </div>
                </div>
              </div>
              <div class="cache-list-stats">
                <div class="stat-item">
                  <label>Hit Rate:</label>
                  <span :class="getHitRateClass(cache.hitRate)">{{ cache.hitRate }}%</span>
                </div>
                <div class="stat-item">
                  <label>Memory:</label>
                  <span>{{ cache.memoryUsage }}</span>
                </div>
                <div class="stat-item">
                  <label>TTL:</label>
                  <span>{{ cache.ttl }}</span>
                </div>
              </div>
              <div class="cache-list-actions">
                <button class="action-btn view" @click="viewCacheDetails(cache)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn clear" @click="clearCacheInstance(cache)">
                  <i class="fas fa-trash"></i>
                </button>
                <button class="action-btn manage" @click="manageCache(cache)">
                  <i class="fas fa-cog"></i>
                </button>
              </div>
            </div>
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
            <h3>Hit Rate</h3>
            <span class="metric-value">{{ metrics.hitRate }}%</span>
          </div>
          <div class="metric-chart">
            <canvas ref="hitRateChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Hits: {{ metrics.hits }}</span>
            <span class="detail-item">Misses: {{ metrics.misses }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Memory Usage</h3>
            <span class="metric-value">{{ metrics.memoryUsage }}%</span>
          </div>
          <div class="metric-chart">
            <canvas ref="memoryChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Used: {{ metrics.memoryUsed }}</span>
            <span class="detail-item">Total: {{ metrics.memoryTotal }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Operations</h3>
            <span class="metric-value">{{ metrics.opsPerSecond }}</span>
          </div>
          <div class="metric-chart">
            <canvas ref="opsChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Read: {{ metrics.readOps }}</span>
            <span class="detail-item">Write: {{ metrics.writeOps }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Evictions</h3>
            <span class="metric-value">{{ metrics.evictions }}</span>
          </div>
          <div class="metric-chart">
            <canvas ref="evictionChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">LRU: {{ metrics.lruEvictions }}</span>
            <span class="detail-item">TTL: {{ metrics.ttlEvictions }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cache Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Cache Details</h2>
          <button class="close-btn" @click="closeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="cache-details">
            <div class="detail-section">
              <h3>Basic Information</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Name:</label>
                  <span>{{ selectedCache?.name }}</span>
                </div>
                <div class="detail-item">
                  <label>Type:</label>
                  <span>{{ selectedCache?.type }}</span>
                </div>
                <div class="detail-item">
                  <label>Status:</label>
                  <span :class="['status-badge', selectedCache?.status]">{{ selectedCache?.status }}</span>
                </div>
                <div class="detail-item">
                  <label>Description:</label>
                  <span>{{ selectedCache?.description }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Performance Metrics</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Hit Rate:</label>
                  <span :class="getHitRateClass(selectedCache?.hitRate)">{{ selectedCache?.hitRate }}%</span>
                </div>
                <div class="detail-item">
                  <label>Entries:</label>
                  <span>{{ selectedCache?.entries }}</span>
                </div>
                <div class="detail-item">
                  <label>Memory Usage:</label>
                  <span>{{ selectedCache?.memoryUsage }}</span>
                </div>
                <div class="detail-item">
                  <label>TTL:</label>
                  <span>{{ selectedCache?.ttl }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Configuration</h3>
              <div class="config-grid">
                <div class="config-item">
                  <label>Max Size:</label>
                  <span>{{ selectedCache?.maxSize }}</span>
                </div>
                <div class="config-item">
                  <label>Eviction Policy:</label>
                  <span>{{ selectedCache?.evictionPolicy }}</span>
                </div>
                <div class="config-item">
                  <label>Default TTL:</label>
                  <span>{{ selectedCache?.defaultTtl }}</span>
                </div>
                <div class="config-item">
                  <label>Compression:</label>
                  <span>{{ selectedCache?.compression ? 'Enabled' : 'Disabled' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeDetailsModal">Close</button>
          <button class="btn-primary" @click="clearCacheInstance(selectedCache)">
            <i class="fas fa-trash"></i>
            Clear Cache
          </button>
        </div>
      </div>
    </div>

    <!-- Clear Cache Modal -->
    <div v-if="showClearModal" class="modal-overlay" @click="closeClearModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Clear Cache</h2>
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
                    v-model="clearOptions.expired"
                  />
                  <span>Expired entries only</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="clearOptions.all"
                  />
                  <span>All entries</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Cache Instances</label>
              <div class="cache-select">
                <div 
                  v-for="cache in caches.value" 
                  :key="cache.id"
                  class="cache-checkbox"
                >
                  <label class="checkbox-item">
                    <input 
                      type="checkbox" 
                      v-model="clearOptions.selectedCaches"
                      :value="cache.id"
                    />
                    <span>{{ cache.name }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeClearModal">Cancel</button>
          <button class="btn-danger" @click="clearSelectedCaches">
            <i class="fas fa-trash"></i>
            Clear Cache
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Chart } from 'chart.js/auto'
import { apiGet, apiPost, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const statusFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('24')
const showDetailsModal = ref(false)
const showClearModal = ref(false)
const showSettingsModal = ref(false)
const selectedCache = ref(null)

// Chart instances
const hitRateChart = ref(null)
const memoryChart = ref(null)
const opsChart = ref(null)
const evictionChart = ref(null)

// Cache stats
const cacheStats = reactive({
  totalSize: '2.4GB',
  avgSize: '800MB',
  hitRate: 94,
  totalEntries: 15678,
  activeEntries: 12456,
  totalOps: 1250,
  currentOps: 892
})

// Performance metrics
const metrics = reactive({
  hitRate: 94,
  hits: 45678,
  misses: 2912,
  memoryUsage: 67,
  memoryUsed: '1.6GB',
  memoryTotal: '2.4GB',
  opsPerSecond: 892,
  readOps: 567,
  writeOps: 325,
  evictions: 234,
  lruEvictions: 189,
  ttlEvictions: 45
})

// Clear options
const clearOptions = reactive({
  expired: true,
  all: false,
  selectedCaches: []
})

// Mock data
const caches = ref([
  {
    id: 1,
    name: 'Application Cache',
    description: 'Main application cache for frequently accessed data',
    type: 'Redis',
    status: 'active',
    size: '1.2GB',
    entries: 8456,
    hitRate: 96,
    memoryUsage: '1.2GB',
    ttl: '1 hour',
    maxSize: '2GB',
    evictionPolicy: 'LRU',
    defaultTtl: '1 hour',
    compression: true
  },
  {
    id: 2,
    name: 'Session Cache',
    description: 'User session data cache',
    type: 'Redis',
    status: 'active',
    size: '800MB',
    entries: 3234,
    hitRate: 92,
    memoryUsage: '800MB',
    ttl: '30 minutes',
    maxSize: '1GB',
    evictionPolicy: 'LRU',
    defaultTtl: '30 minutes',
    compression: false
  },
  {
    id: 3,
    name: 'Query Cache',
    description: 'Database query result cache',
    type: 'Memcached',
    status: 'active',
    size: '400MB',
    entries: 2988,
    hitRate: 89,
    memoryUsage: '400MB',
    ttl: '5 minutes',
    maxSize: '500MB',
    evictionPolicy: 'LRU',
    defaultTtl: '5 minutes',
    compression: true
  },
  {
    id: 4,
    name: 'File Cache',
    description: 'Static file cache',
    type: 'File',
    status: 'inactive',
    size: '200MB',
    entries: 1000,
    hitRate: 78,
    memoryUsage: '200MB',
    ttl: '1 day',
    maxSize: '500MB',
    evictionPolicy: 'TTL',
    defaultTtl: '1 day',
    compression: false
  }
])

// Computed properties
const filteredCaches = computed(() => {
  let filtered = caches.value

  if (statusFilter.value) {
    filtered = filtered.filter(cache => cache.status === statusFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.updatedAt || 0) - new Date(a.updatedAt || 0))
})

// Methods
const loadCacheData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/cache')
    // if (response.success) {
    //   caches.value = response.caches || []
    //   Object.assign(cacheStats, response.stats)
    //   Object.assign(metrics, response.metrics)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading cache data:', error)
    showError('Failed to load cache data')
  } finally {
    loading.value = false
  }
}

const filterCaches = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value) {
    return 'No cache instances match your filter criteria'
  }
  return 'No cache instances found'
}

const getCacheIcon = (type) => {
  const icons = {
    'Redis': 'fas fa-database',
    'Memcached': 'fas fa-memory',
    'File': 'fas fa-file-alt',
    'In-Memory': 'fas fa-microchip'
  }
  return icons[type] || 'fas fa-database'
}

const getHitRateClass = (rate) => {
  if (rate >= 95) return 'excellent'
  if (rate >= 90) return 'good'
  if (rate >= 80) return 'fair'
  return 'poor'
}

const getHitRateStatus = (rate) => {
  if (rate >= 95) return 'Excellent'
  if (rate >= 90) return 'Good'
  if (rate >= 80) return 'Fair'
  return 'Needs Improvement'
}

const viewCacheDetails = (cache) => {
  selectedCache.value = cache
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedCache.value = null
}

const clearCacheInstance = async (cache) => {
  const confirmed = await showConfirm(`Are you sure you want to clear cache "${cache.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/cache/${cache.id}/clear`)
    // if (response.success) {
    //   cache.entries = 0
    //   cache.memoryUsage = '0MB'
    //   showSuccess('Cache cleared successfully')
    // }
    
    // For demo, simulate clear
    cache.entries = 0
    cache.memoryUsage = '0MB'
    showSuccess('Cache cleared successfully')
  } catch (error) {
    console.error('Error clearing cache:', error)
    showError('Failed to clear cache')
  }
}

const manageCache = (cache) => {
  // Open cache management modal or navigate to detailed view
  showSuccess(`Opening management for ${cache.name}`)
}

const optimizeCache = async () => {
  try {
    // const response = await apiPost('/cache/optimize')
    // if (response.success) {
    //   showSuccess('Cache optimization completed')
    //   await loadCacheData()
    // }
    
    // For demo, simulate optimization
    showSuccess('Cache optimization completed')
    await loadCacheData()
  } catch (error) {
    console.error('Error optimizing cache:', error)
    showError('Failed to optimize cache')
  }
}

const refreshCache = async () => {
  await loadCacheData()
  updateCharts()
  showSuccess('Cache data refreshed successfully')
}

const updateMetrics = async () => {
  try {
    // const response = await apiGet('/cache/metrics', { timeRange: timeRange.value })
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

const clearSelectedCaches = async () => {
  if (clearOptions.selectedCaches.length === 0) {
    showError('Please select at least one cache instance')
    return
  }

  const confirmed = await showConfirm(`Are you sure you want to clear the selected cache instances?`)
  if (!confirmed) return

  try {
    // const response = await apiDelete('/cache/clear', {
    //   cacheIds: clearOptions.selectedCaches,
    //   options: {
    //     expired: clearOptions.expired,
    //     all: clearOptions.all
    //   }
    // })
    // if (response.success) {
    //   showSuccess('Cache instances cleared successfully')
    //   closeClearModal()
    //   await loadCacheData()
    // }
    
    // For demo, simulate clear
    showSuccess('Cache instances cleared successfully')
    closeClearModal()
    await loadCacheData()
  } catch (error) {
    console.error('Error clearing cache instances:', error)
    showError('Failed to clear cache instances')
  }
}

const closeClearModal = () => {
  showClearModal.value = false
  resetClearOptions()
}

const resetClearOptions = () => {
  Object.assign(clearOptions, {
    expired: true,
    all: false,
    selectedCaches: []
  })
}

const initCharts = () => {
  // Initialize Hit Rate chart
  if (hitRateChart.value) hitRateChart.value.destroy()
  hitRateChart.value = new Chart(hitRateChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Hit Rate',
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

  // Initialize Memory Usage chart
  if (memoryChart.value) memoryChart.value.destroy()
  memoryChart.value = new Chart(memoryChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Memory Usage',
        data: Array.from({ length: 20 }, () => Math.random() * 100),
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

  // Initialize Operations chart
  if (opsChart.value) opsChart.value.destroy()
  opsChart.value = new Chart(opsChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Operations',
        data: Array.from({ length: 20 }, () => Math.random() * 2000),
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

  // Initialize Evictions chart
  if (evictionChart.value) evictionChart.value.destroy()
  evictionChart.value = new Chart(evictionChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Evictions',
        data: Array.from({ length: 20 }, () => Math.random() * 100),
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
  if (hitRateChart.value) {
    hitRateChart.value.data.datasets[0].data.shift()
    hitRateChart.value.data.datasets[0].push(metrics.hitRate)
    hitRateChart.value.update('none')
  }

  if (memoryChart.value) {
    memoryChart.value.data.datasets[0].data.shift()
    memoryChart.value.data.datasets[0].push(metrics.memoryUsage)
    memoryChart.value.update('none')
  }

  if (opsChart.value) {
    opsChart.value.data.datasets[0].data.shift()
    opsChart.value.data.datasets[0].push(metrics.opsPerSecond)
    opsChart.value.update('none')
  }

  if (evictionChart.value) {
    evictionChart.value.data.datasets[0].data.shift()
    evictionChart.value.data.datasets[0].push(metrics.evictions)
    evictionChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadCacheData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (hitRateChart.value) hitRateChart.value.destroy()
  if (memoryChart.value) memoryChart.value.destroy()
  if (opsChart.value) opsChart.value.destroy()
  if (evictionChart.value) evictionChart.value.destroy()
})
</script>

<style scoped>
.cache {
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

.card-icon.hits {
  background: var(--success-color);
}

.card-icon.entries {
  background: var(--warning-color);
}

.card-icon.operations {
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

.cache-size,
.hit-status,
.entry-count,
.ops-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.cache-size {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.hit-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.hit-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.hit-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.hit-status.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.entry-count,
.ops-status {
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

.clear-btn,
.optimize-btn,
.refresh-btn,
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

.clear-btn:hover,
.optimize-btn:hover,
.refresh-btn:hover,
.settings-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.clear-btn {
  background: var(--danger-color);
}

.clear-btn:hover {
  background: var(--danger-hover);
}

.optimize-btn {
  background: var(--warning-color);
}

.optimize-btn:hover {
  background: var(--warning-hover);
}

.refresh-btn {
  background: var(--success-color);
}

.refresh-btn:hover {
  background: var(--success-hover);
}

.settings-btn {
  background: var(--info-color);
}

.settings-btn:hover {
  background: var(--info-hover);
}

.cache-section,
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

.time-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

.cache-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.cache-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.cache-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.cache-card.inactive {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.cache-card.error {
  border-color: var(--danger-color);
}

.cache-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.cache-icon {
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

.cache-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.cache-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.cache-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.size,
.entries {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.cache-stats {
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

.cache-actions {
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
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.clear:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.action-btn.manage:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.cache-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cache-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.cache-list-card:hover {
  background: var(--glass-bg-hover);
}

.cache-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.cache-list-info {
  flex: 1;
}

.cache-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.cache-list-actions {
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

.cache-details {
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

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.config-item label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.config-item span {
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

.cache-select {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.cache-checkbox {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
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
  .cache {
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
  
  .cache-grid {
    grid-template-columns: 1fr;
  }
  
  .cache-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .cache-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .detail-grid,
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
