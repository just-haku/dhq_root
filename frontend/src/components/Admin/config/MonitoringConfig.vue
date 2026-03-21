<template>
  <div class="monitoring-config">
    <div class="section-header">
      <h3>📊 Monitoring Configuration</h3>
      <button @click="refreshMetrics" class="btn btn-secondary" :disabled="loading">
        <i class="fas fa-refresh"></i> Refresh
      </button>
    </div>

    <!-- System Health -->
    <div class="health-section">
      <h4>System Health</h4>
      <div class="health-grid">
        <div class="health-item">
          <div class="health-label">CPU Usage</div>
          <div class="health-bar">
            <div class="health-fill cpu" :style="{ width: systemHealth.cpu_percent + '%' }"></div>
          </div>
          <div class="health-value">{{ systemHealth.cpu_percent }}%</div>
        </div>
        
        <div class="health-item">
          <div class="health-label">Memory Usage</div>
          <div class="health-bar">
            <div class="health-fill memory" :style="{ width: systemHealth.memory_percent + '%' }"></div>
          </div>
          <div class="health-value">{{ systemHealth.memory_percent }}%</div>
        </div>
        
        <div class="health-item">
          <div class="health-label">Disk Usage</div>
          <div class="health-bar">
            <div class="health-fill disk" :style="{ width: systemHealth.disk_percent + '%' }"></div>
          </div>
          <div class="health-value">{{ systemHealth.disk_percent }}%</div>
        </div>
        
        <div class="health-item">
          <div class="health-label">Network I/O</div>
          <div class="health-bar">
            <div class="health-fill network" :style="{ width: systemHealth.network_usage + '%' }"></div>
          </div>
          <div class="health-value">{{ systemHealth.network_usage }}%</div>
        </div>
      </div>
    </div>

    <!-- Service Status -->
    <div class="services-section">
      <h4>Service Status</h4>
      <div class="services-grid">
        <div 
          v-for="(status, service) in serviceStatus" 
          :key="service"
          class="service-card"
          :class="status.status.toLowerCase()"
        >
          <div class="service-icon">
            <i :class="getServiceIcon(service)"></i>
          </div>
          <div class="service-info">
            <div class="service-name">{{ formatServiceName(service) }}</div>
            <div class="service-status">{{ status.status }}</div>
            <div v-if="status.uptime" class="service-uptime">Uptime: {{ status.uptime }}</div>
            <div v-if="status.error" class="service-error">{{ status.error }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Metrics -->
    <div class="performance-section">
      <h4>Performance Metrics</h4>
      <div class="metrics-controls">
        <select v-model="selectedTimeRange" @change="loadPerformanceMetrics" class="time-select">
          <option value="1">Last 1 Hour</option>
          <option value="6">Last 6 Hours</option>
          <option value="24">Last 24 Hours</option>
          <option value="168">Last 7 Days</option>
        </select>
        <select v-model="selectedMetric" @change="loadPerformanceMetrics" class="metric-select">
          <option value="response_time">Response Time</option>
          <option value="throughput">Throughput</option>
          <option value="error_rate">Error Rate</option>
          <option value="active_users">Active Users</option>
        </select>
      </div>
      
      <div class="metrics-chart">
        <canvas ref="chartCanvas"></canvas>
      </div>
      
      <div class="metrics-summary">
        <div class="summary-item">
          <div class="summary-label">Average</div>
          <div class="summary-value">{{ performanceMetrics.average }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">Peak</div>
          <div class="summary-value">{{ performanceMetrics.peak }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">Minimum</div>
          <div class="summary-value">{{ performanceMetrics.minimum }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">Current</div>
          <div class="summary-value">{{ performanceMetrics.current }}</div>
        </div>
      </div>
    </div>

    <!-- Alerts -->
    <div class="alerts-section">
      <h4>System Alerts</h4>
      <div class="alerts-controls">
        <button @click="clearAlerts" class="btn btn-outline btn-sm" :disabled="loading">
          Clear All Alerts
        </button>
        <div class="alert-filters">
          <label>
            <input v-model="alertFilters.critical" type="checkbox" />
            Critical
          </label>
          <label>
            <input v-model="alertFilters.warning" type="checkbox" />
            Warning
          </label>
          <label>
            <input v-model="alertFilters.info" type="checkbox" />
            Info
          </label>
        </div>
      </div>
      
      <div class="alerts-list">
        <div 
          v-for="alert in filteredAlerts" 
          :key="alert.id"
          class="alert-item"
          :class="alert.severity.toLowerCase()"
        >
          <div class="alert-icon">
            <i :class="getAlertIcon(alert.severity)"></i>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-message">{{ alert.message }}</div>
            <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
          </div>
          <button @click="dismissAlert(alert.id)" class="btn btn-sm btn-outline">
            Dismiss
          </button>
        </div>
        
        <div v-if="filteredAlerts.length === 0" class="no-alerts">
          <i class="fas fa-check-circle"></i>
          <p>No active alerts</p>
        </div>
      </div>
    </div>

    <!-- Monitoring Settings -->
    <div class="settings-section">
      <h4>Monitoring Settings</h4>
      <div class="settings-grid">
        <div class="setting-item">
          <label>
            <input 
              v-model="monitoringSettings.real_time_alerts" 
              type="checkbox"
              @change="updateSettings"
            />
            Real-time Alerts
          </label>
          <p class="setting-description">
            Enable immediate notifications for critical issues
          </p>
        </div>
        
        <div class="setting-item">
          <label>
            <input 
              v-model="monitoringSettings.performance_tracking" 
              type="checkbox"
              @change="updateSettings"
            />
            Performance Tracking
          </label>
          <p class="setting-description">
            Track detailed performance metrics
          </p>
        </div>
        
        <div class="setting-item">
          <label>
            <input 
              v-model="monitoringSettings.log_monitoring" 
              type="checkbox"
              @change="updateSettings"
            />
            Log Monitoring
          </label>
          <p class="setting-description">
            Monitor system logs for errors and warnings
          </p>
        </div>
        
        <div class="setting-item">
          <label>
            <input 
              v-model="monitoringSettings.resource_monitoring" 
              type="checkbox"
              @change="updateSettings"
            />
            Resource Monitoring
          </label>
          <p class="setting-description">
            Monitor CPU, memory, and disk usage
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '../../../utils/api.js'

export default {
  name: 'MonitoringConfig',
  setup() {
    // State
    const loading = ref(false)
    const selectedTimeRange = ref('24')
    const selectedMetric = ref('response_time')
    const chartCanvas = ref(null)
    
    const systemHealth = reactive({
      cpu_percent: 0,
      memory_percent: 0,
      disk_percent: 0,
      network_usage: 0
    })
    
    const serviceStatus = reactive({
      backend: { status: 'Unknown' },
      database: { status: 'Unknown' },
      redis: { status: 'Unknown' },
      socketio: { status: 'Unknown' },
      nginx: { status: 'Unknown' }
    })
    
    const performanceMetrics = reactive({
      average: 0,
      peak: 0,
      minimum: 0,
      current: 0,
      data: []
    })
    
    const alerts = ref([])
    
    const alertFilters = reactive({
      critical: true,
      warning: true,
      info: false
    })
    
    const monitoringSettings = reactive({
      real_time_alerts: true,
      performance_tracking: true,
      log_monitoring: true,
      resource_monitoring: true
    })

    // Computed
    const filteredAlerts = computed(() => {
      return alerts.value.filter(alert => {
        if (alert.severity === 'CRITICAL' && !alertFilters.critical) return false
        if (alert.severity === 'WARNING' && !alertFilters.warning) return false
        if (alert.severity === 'INFO' && !alertFilters.info) return false
        return true
      })
    })

    // Methods
    const refreshMetrics = async () => {
      await Promise.all([
        loadSystemHealth(),
        loadServiceStatus(),
        loadPerformanceMetrics(),
        loadAlerts()
      ])
    }

    const loadSystemHealth = async () => {
      try {
        const data = await apiGet('/api/monitoring/system-health')
        Object.assign(systemHealth, data)
      } catch (error) {
        console.error('Error loading system health:', error)
      }
    }

    const loadServiceStatus = async () => {
      try {
        const data = await apiGet('/api/monitoring/service-status')
        Object.assign(serviceStatus, data.services || {})
      } catch (error) {
        console.error('Error loading service status:', error)
      }
    }

    const loadPerformanceMetrics = async () => {
      try {
        const data = await apiGet(`/api/monitoring/performance-metrics?hours=${selectedTimeRange.value}`)
        Object.assign(performanceMetrics, data)
        
        // Update chart
        await nextTick()
        updateChart()
      } catch (error) {
        console.error('Error loading performance metrics:', error)
      }
    }

    const loadAlerts = async () => {
      try {
        const data = await apiGet('/api/monitoring/alerts')
        alerts.value = data.alerts || []
      } catch (error) {
        console.error('Error loading alerts:', error)
      }
    }

    const updateChart = () => {
      // Simple chart implementation - in production you'd use Chart.js or similar
      const canvas = chartCanvas.value
      if (!canvas) return
      
      const ctx = canvas.getContext('2d')
      const width = canvas.width
      const height = canvas.height
      
      // Clear canvas
      ctx.clearRect(0, 0, width, height)
      
      // Draw simple line chart
      if (performanceMetrics.data && performanceMetrics.data.length > 0) {
        const data = performanceMetrics.data
        const maxValue = Math.max(...data.map(d => d.value))
        const minValue = Math.min(...data.map(d => d.value))
        const range = maxValue - minValue || 1
        
        ctx.strokeStyle = '#3498db'
        ctx.lineWidth = 2
        ctx.beginPath()
        
        data.forEach((point, index) => {
          const x = (index / (data.length - 1)) * width
          const y = height - ((point.value - minValue) / range) * height
          
          if (index === 0) {
            ctx.moveTo(x, y)
          } else {
            ctx.lineTo(x, y)
          }
        })
        
        ctx.stroke()
      }
    }

    const clearAlerts = async () => {
      try {
        loading.value = true
        await apiPost('/api/monitoring/alerts/clear')
        alerts.value = []
      } catch (error) {
        console.error('Error clearing alerts:', error)
      } finally {
        loading.value = false
      }
    }

    const dismissAlert = async (alertId) => {
      try {
        await apiPost(`/api/monitoring/alerts/${alertId}/dismiss`)
        alerts.value = alerts.value.filter(alert => alert.id !== alertId)
      } catch (error) {
        console.error('Error dismissing alert:', error)
      }
    }

    const updateSettings = async () => {
      try {
        await apiPut('/api/monitoring/settings', monitoringSettings)
      } catch (error) {
        console.error('Error updating settings:', error)
      }
    }

    const getServiceIcon = (service) => {
      const icons = {
        backend: 'fas fa-server',
        database: 'fas fa-database',
        redis: 'fas fa-memory',
        socketio: 'fas fa-plug',
        nginx: 'fas fa-globe'
      }
      return icons[service] || 'fas fa-question-circle'
    }

    const getAlertIcon = (severity) => {
      const icons = {
        CRITICAL: 'fas fa-exclamation-triangle',
        WARNING: 'fas fa-exclamation-circle',
        INFO: 'fas fa-info-circle'
      }
      return icons[severity] || 'fas fa-info-circle'
    }

    const formatServiceName = (service) => {
      return service.charAt(0).toUpperCase() + service.slice(1)
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }

    // Lifecycle
    onMounted(() => {
      refreshMetrics()
      
      // Set up auto-refresh
      setInterval(() => {
        refreshMetrics()
      }, 30000) // Refresh every 30 seconds
    })

    return {
      loading,
      selectedTimeRange,
      selectedMetric,
      chartCanvas,
      systemHealth,
      serviceStatus,
      performanceMetrics,
      alerts,
      alertFilters,
      monitoringSettings,
      filteredAlerts,
      refreshMetrics,
      loadPerformanceMetrics,
      clearAlerts,
      dismissAlert,
      updateSettings,
      getServiceIcon,
      getAlertIcon,
      formatServiceName,
      formatTime
    }
  }
}
</script>

<style scoped>
.monitoring-config {
  width: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-header h3 {
  margin: 0;
  color: #34495e;
}

.health-section,
.services-section,
.performance-section,
.alerts-section,
.settings-section {
  margin-bottom: 30px;
}

.health-section h4,
.services-section h4,
.performance-section h4,
.alerts-section h4,
.settings-section h4 {
  margin: 0 0 16px 0;
  color: #34495e;
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.health-item {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
}

.health-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.health-bar {
  width: 100%;
  height: 8px;
  background: #e1e8ed;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.health-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.health-fill.cpu {
  background: linear-gradient(90deg, #3498db, #2980b9);
}

.health-fill.memory {
  background: linear-gradient(90deg, #9b59b6, #8e44ad);
}

.health-fill.disk {
  background: linear-gradient(90deg, #e67e22, #d35400);
}

.health-fill.network {
  background: linear-gradient(90deg, #1abc9c, #16a085);
}

.health-value {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.service-card {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.service-card.online {
  border-color: #27ae60;
  background: #d4edda;
}

.service-card.offline {
  border-color: #e74c3c;
  background: #f8d7da;
}

.service-card.warning {
  border-color: #f39c12;
  background: #fff3cd;
}

.service-icon {
  font-size: 24px;
  color: #3498db;
}

.service-info {
  flex: 1;
}

.service-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.service-status {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.service-uptime,
.service-error {
  font-size: 12px;
  color: #95a5a6;
}

.metrics-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.time-select,
.metric-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.metrics-chart {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  height: 300px;
}

.metrics-chart canvas {
  width: 100%;
  height: 100%;
}

.metrics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.summary-item {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.summary-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.alerts-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.alert-filters {
  display: flex;
  gap: 16px;
}

.alert-filters label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.alerts-list {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  overflow: hidden;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #e1e8ed;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-item.critical {
  border-left: 4px solid #e74c3c;
  background: #fdf2f2;
}

.alert-item.warning {
  border-left: 4px solid #f39c12;
  background: #fffbf0;
}

.alert-item.info {
  border-left: 4px solid #3498db;
  background: #f8f9fa;
}

.alert-icon {
  font-size: 20px;
}

.alert-item.critical .alert-icon {
  color: #e74c3c;
}

.alert-item.warning .alert-icon {
  color: #f39c12;
}

.alert-item.info .alert-icon {
  color: #3498db;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.alert-message {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.alert-time {
  font-size: 12px;
  color: #95a5a6;
}

.no-alerts {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.no-alerts i {
  font-size: 48px;
  color: #27ae60;
  margin-bottom: 16px;
  display: block;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.setting-item {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
}

.setting-item label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #34495e;
  margin-bottom: 8px;
}

.setting-description {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-outline {
  background: transparent;
  border: 1px solid #3498db;
  color: #3498db;
}

.btn-outline:hover:not(:disabled) {
  background: #3498db;
  color: white;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .health-grid,
  .services-grid,
  .metrics-summary,
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-controls {
    flex-direction: column;
  }
  
  .alerts-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
}
</style>
