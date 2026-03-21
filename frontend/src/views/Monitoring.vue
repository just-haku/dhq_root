<template>
  <div class="monitoring">
    <div class="page-header">
      <h1>System Monitoring</h1>
      <p>Real-time system performance and health monitoring</p>
    </div>

    <!-- System Status Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <h3>{{ systemStatus.health }}</h3>
            <p>System Health</p>
            <span class="health-status" :class="getHealthClass(systemStatus.health)">
              {{ getHealthStatus(systemStatus.health) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon uptime">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ systemStatus.uptime }}%</h3>
            <p>Uptime</p>
            <span class="uptime-status">{{ systemStatus.lastDowntime }} last downtime</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon response">
            <i class="fas fa-tachometer-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ systemStatus.responseTime }}ms</h3>
            <p>Avg Response</p>
            <span class="response-status">{{ systemStatus.peakResponse }}ms peak</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon errors">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="card-content">
            <h3>{{ systemStatus.errorRate }}%</h3>
            <p>Error Rate</p>
            <span class="error-status" :class="getErrorClass(systemStatus.errorRate)">
              {{ getErrorStatus(systemStatus.errorRate) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Real-time Metrics -->
    <div class="metrics-section">
      <div class="section-header">
        <h2>Real-time Metrics</h2>
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
          <button class="refresh-btn" @click="refreshMetrics">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-header">
            <h3>CPU Usage</h3>
            <span class="metric-value">{{ metrics.cpu }}%</span>
          </div>
          <div class="metric-chart">
            <canvas ref="cpuChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Cores: {{ metrics.cpuCores }}</span>
            <span class="detail-item">Load: {{ metrics.cpuLoad }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Memory Usage</h3>
            <span class="metric-value">{{ metrics.memory }}%</span>
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
            <h3>Disk Usage</h3>
            <span class="metric-value">{{ metrics.disk }}%</span>
          </div>
          <div class="metric-chart">
            <canvas ref="diskChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">Used: {{ metrics.diskUsed }}</span>
            <span class="detail-item">Total: {{ metrics.diskTotal }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <h3>Network</h3>
            <span class="metric-value">{{ metrics.network }}Mbps</span>
          </div>
          <div class="metric-chart">
            <canvas ref="networkChart"></canvas>
          </div>
          <div class="metric-details">
            <span class="detail-item">In: {{ metrics.networkIn }}</span>
            <span class="detail-item">Out: {{ metrics.networkOut }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Status -->
    <div class="services-section">
      <div class="section-header">
        <h2>Service Status</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="serviceFilter" @change="filterServices">
              <option value="">All Services</option>
              <option value="healthy">Healthy</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
              <option value="down">Down</option>
            </select>
          </div>
        </div>
      </div>

      <div class="services-grid">
        <div 
          v-for="service in filteredServices" 
          :key="service.id"
          class="service-card"
          :class="service.status"
        >
          <div class="service-header">
            <div class="service-icon">
              <i :class="getServiceIcon(service.type)"></i>
            </div>
            <div class="service-info">
              <h3>{{ service.name }}</h3>
              <p>{{ service.description }}</p>
            </div>
            <div class="service-status">
              <span :class="['status-badge', service.status]">{{ service.status }}</span>
            </div>
          </div>

          <div class="service-metrics">
            <div class="metric-item">
              <label>Response Time:</label>
              <span>{{ service.responseTime }}ms</span>
            </div>
            <div class="metric-item">
              <label>Uptime:</label>
              <span>{{ service.uptime }}%</span>
            </div>
            <div class="metric-item">
              <label>Last Check:</label>
              <span>{{ formatDateTime(service.lastCheck) }}</span>
            </div>
          </div>

          <div class="service-actions">
            <button class="action-btn check" @click="checkService(service)">
              <i class="fas fa-check"></i>
              Check
            </button>
            <button class="action-btn restart" @click="restartService(service)">
              <i class="fas fa-redo"></i>
              Restart
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerts -->
    <div class="alerts-section">
      <div class="section-header">
        <h2>Active Alerts</h2>
        <div class="header-actions">
          <button class="create-alert-btn" @click="showCreateAlertModal = true">
            <i class="fas fa-plus"></i>
            Create Alert
          </button>
        </div>
      </div>

      <div v-if="alerts.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-bell"></i>
        </div>
        <h3>No active alerts</h3>
        <p>System is running normally</p>
      </div>

      <div v-else class="alerts-list">
        <div 
          v-for="alert in alerts" 
          :key="alert.id"
          class="alert-item"
          :class="alert.severity"
        >
          <div class="alert-icon">
            <i :class="getAlertIcon(alert.severity)"></i>
          </div>
          <div class="alert-content">
            <div class="alert-header">
              <h4>{{ alert.title }}</h4>
              <span :class="['severity-badge', alert.severity]">{{ alert.severity }}</span>
            </div>
            <p>{{ alert.message }}</p>
            <div class="alert-meta">
              <span class="time">{{ formatDateTime(alert.createdAt) }}</span>
              <span class="source">{{ alert.source }}</span>
            </div>
          </div>
          <div class="alert-actions">
            <button class="action-btn acknowledge" @click="acknowledgeAlert(alert)">
              <i class="fas fa-check"></i>
              Acknowledge
            </button>
            <button class="action-btn dismiss" @click="dismissAlert(alert)">
              <i class="fas fa-times"></i>
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Alert Modal -->
    <div v-if="showCreateAlertModal" class="modal-overlay" @click="closeCreateAlertModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create Alert</h2>
          <button class="close-btn" @click="closeCreateAlertModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="alert-form">
            <div class="form-group">
              <label>Alert Title</label>
              <input 
                v-model="alertForm.title" 
                type="text" 
                placeholder="Enter alert title"
              />
            </div>

            <div class="form-group">
              <label>Message</label>
              <textarea 
                v-model="alertForm.message" 
                placeholder="Describe the alert"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Severity</label>
                <select v-model="alertForm.severity">
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div class="form-group">
                <label>Source</label>
                <select v-model="alertForm.source">
                  <option value="system">System</option>
                  <option value="application">Application</option>
                  <option value="database">Database</option>
                  <option value="network">Network</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Conditions</label>
              <div class="conditions-container">
                <div 
                  v-for="(condition, index) in alertForm.conditions" 
                  :key="index"
                  class="condition-item"
                >
                  <select v-model="condition.metric">
                    <option value="cpu">CPU Usage</option>
                    <option value="memory">Memory Usage</option>
                    <option value="disk">Disk Usage</option>
                    <option value="response_time">Response Time</option>
                    <option value="error_rate">Error Rate</option>
                  </select>
                  <select v-model="condition.operator">
                    <option value=">">Greater than</option>
                    <option value="<">Less than</option>
                    <option value="==">Equals</option>
                  </select>
                  <input 
                    v-model="condition.threshold" 
                    type="number" 
                    placeholder="Threshold"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeCondition(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-condition-btn" @click="addCondition">
                  <i class="fas fa-plus"></i>
                  Add Condition
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateAlertModal">Cancel</button>
          <button class="btn-primary" @click="createAlert">Create Alert</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Chart } from 'chart.js/auto'
import { apiGet, apiPost, apiPut } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const autoRefresh = ref(false)
const refreshInterval = ref(null)
const serviceFilter = ref('')
const showCreateAlertModal = ref(false)

// Chart instances
const cpuChart = ref(null)
const memoryChart = ref(null)
const diskChart = ref(null)
const networkChart = ref(null)

// System status
const systemStatus = reactive({
  health: 'Healthy',
  uptime: 99.9,
  lastDowntime: '2 days ago',
  responseTime: 145,
  peakResponse: 892,
  errorRate: 0.2
})

// Metrics
const metrics = reactive({
  cpu: 45,
  cpuCores: 8,
  cpuLoad: '2.3',
  memory: 67,
  memoryUsed: '8.4GB',
  memoryTotal: '16GB',
  disk: 78,
  diskUsed: '234GB',
  diskTotal: '500GB',
  network: 125,
  networkIn: '45Mbps',
  networkOut: '80Mbps'
})

// Alert form
const alertForm = reactive({
  title: '',
  message: '',
  severity: 'warning',
  source: 'system',
  conditions: []
})

// Mock data
const services = ref([
  {
    id: 1,
    name: 'Web Server',
    description: 'Main web application server',
    type: 'web',
    status: 'healthy',
    responseTime: 145,
    uptime: 99.9,
    lastCheck: '2024-01-21T10:30:00Z'
  },
  {
    id: 2,
    name: 'Database',
    description: 'Primary database server',
    type: 'database',
    status: 'healthy',
    responseTime: 23,
    uptime: 99.8,
    lastCheck: '2024-01-21T10:29:00Z'
  },
  {
    id: 3,
    name: 'API Gateway',
    description: 'API request gateway',
    type: 'api',
    status: 'warning',
    responseTime: 892,
    uptime: 98.5,
    lastCheck: '2024-01-21T10:28:00Z'
  },
  {
    id: 4,
    name: 'Cache Server',
    description: 'Redis cache server',
    type: 'cache',
    status: 'healthy',
    responseTime: 2,
    uptime: 100,
    lastCheck: '2024-01-21T10:30:00Z'
  },
  {
    id: 5,
    name: 'Load Balancer',
    description: 'Traffic load balancer',
    type: 'network',
    status: 'healthy',
    responseTime: 12,
    uptime: 99.9,
    lastCheck: '2024-01-21T10:30:00Z'
  }
])

const alerts = ref([
  {
    id: 1,
    title: 'High CPU Usage',
    message: 'CPU usage exceeded 80% threshold',
    severity: 'warning',
    source: 'system',
    createdAt: '2024-01-21T10:15:00Z'
  },
  {
    id: 2,
    title: 'Slow API Response',
    message: 'API Gateway response time is above 500ms',
    severity: 'critical',
    source: 'application',
    createdAt: '2024-01-21T09:45:00Z'
  }
])

// Computed properties
const filteredServices = computed(() => {
  let filtered = services.value

  if (serviceFilter.value) {
    filtered = filtered.filter(service => service.status === serviceFilter.value)
  }

  return filtered
})

// Methods
const loadMonitoringData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/monitoring')
    // if (response.success) {
    //   Object.assign(systemStatus, response.systemStatus)
    //   Object.assign(metrics, response.metrics)
    //   services.value = response.services || []
    //   alerts.value = response.alerts || []
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading monitoring data:', error)
    showError('Failed to load monitoring data')
  } finally {
    loading.value = false
  }
}

const filterServices = () => {
  // This is reactive, no additional action needed
}

const getHealthClass = (health) => {
  if (health === 'Healthy') return 'healthy'
  if (health === 'Warning') return 'warning'
  if (health === 'Critical') return 'critical'
  return 'unknown'
}

const getHealthStatus = (health) => {
  return health
}

const getErrorClass = (rate) => {
  if (rate < 1) return 'good'
  if (rate < 5) return 'warning'
  return 'critical'
}

const getErrorStatus = (rate) => {
  if (rate < 1) return 'Good'
  if (rate < 5) return 'Warning'
  return 'Critical'
}

const getServiceIcon = (type) => {
  const icons = {
    'web': 'fas fa-globe',
    'database': 'fas fa-database',
    'api': 'fas fa-code',
    'cache': 'fas fa-memory',
    'network': 'fas fa-network-wired'
  }
  return icons[type] || 'fas fa-server'
}

const getAlertIcon = (severity) => {
  const icons = {
    'info': 'fas fa-info-circle',
    'warning': 'fas fa-exclamation-triangle',
    'critical': 'fas fa-exclamation-circle'
  }
  return icons[severity] || 'fas fa-bell'
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const refreshMetrics = async () => {
  await loadMonitoringData()
  updateCharts()
  showSuccess('Metrics refreshed successfully')
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
    loadMonitoringData()
    updateCharts()
  }, 5000) // Refresh every 5 seconds
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

const checkService = async (service) => {
  try {
    // const response = await apiPost(`/monitoring/services/${service.id}/check`)
    // if (response.success) {
    //   Object.assign(service, response.service)
    //   showSuccess(`Service ${service.name} checked successfully`)
    // }
    
    // For demo, simulate check
    showSuccess(`Service ${service.name} checked successfully`)
  } catch (error) {
    console.error('Error checking service:', error)
    showError('Failed to check service')
  }
}

const restartService = async (service) => {
  try {
    // const response = await apiPost(`/monitoring/services/${service.id}/restart`)
    // if (response.success) {
    //   Object.assign(service, response.service)
    //   showSuccess(`Service ${service.name} restarted successfully`)
    // }
    
    // For demo, simulate restart
    showSuccess(`Service ${service.name} restarted successfully`)
  } catch (error) {
    console.error('Error restarting service:', error)
    showError('Failed to restart service')
  }
}

const addCondition = () => {
  alertForm.conditions.push({
    metric: 'cpu',
    operator: '>',
    threshold: 80
  })
}

const removeCondition = (index) => {
  alertForm.conditions.splice(index, 1)
}

const createAlert = async () => {
  if (!alertForm.title || !alertForm.message) {
    showError('Please fill in all required fields')
    return
  }

  if (alertForm.conditions.length === 0) {
    showError('Please add at least one condition')
    return
  }

  try {
    // const response = await apiPost('/monitoring/alerts', alertForm)
    // if (response.success) {
    //   alerts.value.unshift(response.alert)
    //   showSuccess('Alert created successfully')
    //   closeCreateAlertModal()
    // }
    
    // For demo, simulate creation
    const newAlert = {
      id: Date.now(),
      ...alertForm,
      createdAt: new Date().toISOString()
    }
    
    alerts.value.unshift(newAlert)
    showSuccess('Alert created successfully')
    closeCreateAlertModal()
  } catch (error) {
    console.error('Error creating alert:', error)
    showError('Failed to create alert')
  }
}

const closeCreateAlertModal = () => {
  showCreateAlertModal.value = false
  resetAlertForm()
}

const resetAlertForm = () => {
  Object.assign(alertForm, {
    title: '',
    message: '',
    severity: 'warning',
    source: 'system',
    conditions: []
  })
}

const acknowledgeAlert = async (alert) => {
  try {
    // const response = await apiPut(`/monitoring/alerts/${alert.id}/acknowledge`)
    // if (response.success) {
    //   alert.acknowledged = true
    //   showSuccess('Alert acknowledged')
    // }
    
    // For demo, simulate acknowledge
    showSuccess('Alert acknowledged')
  } catch (error) {
    console.error('Error acknowledging alert:', error)
    showError('Failed to acknowledge alert')
  }
}

const dismissAlert = async (alert) => {
  try {
    // const response = await apiDelete(`/monitoring/alerts/${alert.id}`)
    // if (response.success) {
    //   const index = alerts.value.findIndex(a => a.id === alert.id)
    //   if (index > -1) {
    //     alerts.value.splice(index, 1)
    //     showSuccess('Alert dismissed')
    //   }
    // }
    
    // For demo, simulate dismiss
    const index = alerts.value.findIndex(a => a.id === alert.id)
    if (index > -1) {
      alerts.value.splice(index, 1)
      showSuccess('Alert dismissed')
    }
  } catch (error) {
    console.error('Error dismissing alert:', error)
    showError('Failed to dismiss alert')
  }
}

const initCharts = () => {
  // Initialize CPU chart
  if (cpuChart.value) cpuChart.value.destroy()
  cpuChart.value = new Chart(cpuChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}s`),
      datasets: [{
        label: 'CPU Usage',
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

  // Initialize Memory chart
  if (memoryChart.value) memoryChart.value.destroy()
  memoryChart.value = new Chart(memoryChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}s`),
      datasets: [{
        label: 'Memory Usage',
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

  // Initialize Disk chart
  if (diskChart.value) diskChart.value.destroy()
  diskChart.value = new Chart(diskChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}s`),
      datasets: [{
        label: 'Disk Usage',
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

  // Initialize Network chart
  if (networkChart.value) networkChart.value.destroy()
  networkChart.value = new Chart(networkChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}s`),
      datasets: [{
        label: 'Network',
        data: Array.from({ length: 20 }, () => Math.random() * 200),
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
        y: { beginAtZero: true }
      }
    }
  })
}

const updateCharts = () => {
  // Update charts with new data
  if (cpuChart.value) {
    cpuChart.value.data.datasets[0].data.shift()
    cpuChart.value.data.datasets[0].data.push(metrics.cpu)
    cpuChart.value.update('none')
  }

  if (memoryChart.value) {
    memoryChart.value.data.datasets[0].data.shift()
    memoryChart.value.data.datasets[0].data.push(metrics.memory)
    memoryChart.value.update('none')
  }

  if (diskChart.value) {
    diskChart.value.data.datasets[0].data.shift()
    diskChart.value.data.datasets[0].data.push(metrics.disk)
    diskChart.value.update('none')
  }

  if (networkChart.value) {
    networkChart.value.data.datasets[0].data.shift()
    networkChart.value.data.datasets[0].data.push(metrics.network)
    networkChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadMonitoringData()
  initCharts()
})

onUnmounted(() => {
  stopAutoRefresh()
  // Destroy charts
  if (cpuChart.value) cpuChart.value.destroy()
  if (memoryChart.value) memoryChart.value.destroy()
  if (diskChart.value) diskChart.value.destroy()
  if (networkChart.value) networkChart.value.destroy()
})
</script>

<style scoped>
.monitoring {
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

.card-icon.uptime {
  background: var(--success-color);
}

.card-icon.response {
  background: var(--warning-color);
}

.card-icon.errors {
  background: var(--danger-color);
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

.health-status.healthy {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.health-status.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.health-status.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.uptime-status,
.response-status,
.error-status {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.metrics-section,
.services-section,
.alerts-section {
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

.refresh-btn:hover {
  background: var(--primary-hover);
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

.create-alert-btn {
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

.create-alert-btn:hover {
  background: var(--primary-hover);
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

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.service-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.service-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.service-card.warning {
  border-color: var(--warning-color);
}

.service-card.critical {
  border-color: var(--danger-color);
}

.service-card.down {
  border-color: var(--danger-color);
  opacity: 0.7;
}

.service-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.service-icon {
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

.service-info {
  flex: 1;
}

.service-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.service-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.healthy {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.down {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.service-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.metric-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.service-actions {
  display: flex;
  gap: 0.5rem;
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

.action-btn.check:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.restart:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 3rem;
  color: var(--text-tertiary);
  margin-bottom: 1rem;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.alert-item {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.alert-item:hover {
  background: var(--glass-bg-hover);
}

.alert-item.warning {
  border-left: 4px solid var(--warning-color);
}

.alert-item.critical {
  border-left: 4px solid var(--danger-color);
  background: rgba(239, 68, 68, 0.05);
}

.alert-icon {
  width: 40px;
  height: 40px;
  background: var(--glass-bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.alert-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.severity-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.severity-badge.info {
  background: rgba(6, 182, 212, 0.1);
  color: #06b6d4;
}

.severity-badge.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.severity-badge.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.alert-content p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.alert-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.alert-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.acknowledge:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.dismiss:hover {
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
  max-width: 600px;
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

.alert-form {
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

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.conditions-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.condition-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.condition-item select,
.condition-item input {
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
}

.remove-btn:hover {
  background: var(--danger-hover);
}

.add-condition-btn {
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

.add-condition-btn:hover {
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
  .monitoring {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .service-metrics {
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
