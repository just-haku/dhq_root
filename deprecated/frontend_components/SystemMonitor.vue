<template>
  <div class="system-monitor">
    <div class="monitor-header">
      <h3>🖥️ System Monitor</h3>
      <div class="monitor-controls">
        <button @click="refreshMetrics" class="refresh-btn" :disabled="loading">
          🔄 Refresh
        </button>
        <select v-model="autoRefresh" @change="toggleAutoRefresh" class="refresh-select">
          <option :value="false">Manual</option>
          <option :value="5000">5s</option>
          <option :value="10000">10s</option>
          <option :value="30000">30s</option>
        </select>
      </div>
    </div>
    
    <!-- System Health Overview -->
    <div class="health-overview">
      <div class="health-card" :class="systemHealth.status">
        <div class="health-icon">
          {{ getHealthIcon(systemHealth.status) }}
        </div>
        <div class="health-info">
          <div class="health-title">System Health</div>
          <div class="health-status">{{ systemHealth.status.toUpperCase() }}</div>
          <div class="health-uptime">Uptime: {{ formatUptime(systemHealth.uptime_seconds) }}</div>
        </div>
      </div>
      
      <div class="alerts-card">
        <div class="alerts-header">
          <span class="alerts-title">🚨 Alerts</span>
          <span class="alerts-count" :class="{ 'has-alerts': systemAlerts.total_count > 0 }">
            {{ systemAlerts.total_count }}
          </span>
        </div>
        <div class="alerts-breakdown">
          <span class="alert-critical">{{ systemAlerts.critical_count }} Critical</span>
          <span class="alert-warning">{{ systemAlerts.warning_count }} Warning</span>
        </div>
      </div>
    </div>
    
    <!-- Resource Metrics -->
    <div class="metrics-grid">
      <div class="metric-card cpu">
        <div class="metric-header">
          <span class="metric-title">💻 CPU</span>
          <span class="metric-value">{{ systemMetrics.cpu?.usage_percent || 0 }}%</span>
        </div>
        <div class="metric-bar">
          <div class="metric-fill cpu-fill" :style="{ width: (systemMetrics.cpu?.usage_percent || 0) + '%' }"></div>
        </div>
        <div class="metric-details">
          <span>Cores: {{ systemMetrics.cpu?.core_count || 0 }}</span>
          <span>Load: {{ systemMetrics.cpu?.load_average?.['1min']?.toFixed(2) || 0 }}</span>
          <span v-if="systemMetrics.cpu?.frequency_mhz">Freq: {{ Math.round(systemMetrics.cpu.frequency_mhz) }}MHz</span>
        </div>
      </div>
      
      <div class="metric-card memory">
        <div class="metric-header">
          <span class="metric-title">🧠 Memory</span>
          <span class="metric-value">{{ systemMetrics.memory?.usage_percent || 0 }}%</span>
        </div>
        <div class="metric-bar">
          <div class="metric-fill memory-fill" :style="{ width: (systemMetrics.memory?.usage_percent || 0) + '%' }"></div>
        </div>
        <div class="metric-details">
          <span>Used: {{ formatBytes(systemMetrics.memory?.used_gb * 1024**3) }}</span>
          <span>Total: {{ formatBytes(systemMetrics.memory?.total_gb * 1024**3) }}</span>
          <span>Available: {{ formatBytes(systemMetrics.memory?.available_gb * 1024**3) }}</span>
        </div>
      </div>
      
      <div class="metric-card disk">
        <div class="metric-header">
          <span class="metric-title">💾 Disk</span>
          <span class="metric-value">{{ systemMetrics.disk?.usage_percent || 0 }}%</span>
        </div>
        <div class="metric-bar">
          <div class="metric-fill disk-fill" :style="{ width: (systemMetrics.disk?.usage_percent || 0) + '%' }"></div>
        </div>
        <div class="metric-details">
          <span>Used: {{ formatBytes(systemMetrics.disk?.used_gb * 1024**3) }}</span>
          <span>Total: {{ formatBytes(systemMetrics.disk?.total_gb * 1024**3) }}</span>
          <span>Free: {{ formatBytes(systemMetrics.disk?.free_gb * 1024**3) }}</span>
        </div>
      </div>
      
      <div class="metric-card network">
        <div class="metric-header">
          <span class="metric-title">🌐 Network</span>
          <span class="metric-value">Active</span>
        </div>
        <div class="metric-details">
          <span>Sent: {{ formatBytes(systemMetrics.network?.bytes_sent || 0) }}</span>
          <span>Received: {{ formatBytes(systemMetrics.network?.bytes_recv || 0) }}</span>
          <span>Packets: {{ ((systemMetrics.network?.packets_sent || 0) + (systemMetrics.network?.packets_recv || 0)).toLocaleString() }}</span>
        </div>
      </div>
    </div>
    
    <!-- Additional System Info -->
    <div class="info-grid">
      <div class="info-card">
        <div class="info-header">
          <span class="info-title">⏱️ System Uptime</span>
        </div>
        <div class="info-content">
          <div class="info-value">{{ formatUptime(systemHealth.uptime_seconds) }}</div>
          <div class="info-subtitle">Since last boot</div>
        </div>
      </div>
      
      <div class="info-card">
        <div class="info-header">
          <span class="info-title">🔄 Load Average</span>
        </div>
        <div class="info-content">
          <div class="load-averages">
            <span>1m: {{ systemMetrics.cpu?.load_average?.['1min']?.toFixed(2) || 0 }}</span>
            <span>5m: {{ systemMetrics.cpu?.load_average?.['5min']?.toFixed(2) || 0 }}</span>
            <span>15m: {{ systemMetrics.cpu?.load_average?.['15min']?.toFixed(2) || 0 }}</span>
          </div>
        </div>
      </div>
      
      <div class="info-card">
        <div class="info-header">
          <span class="info-title">💾 Swap Memory</span>
        </div>
        <div class="info-content">
          <div class="swap-info">
            <span>Used: {{ formatBytes((systemMetrics.memory?.swap?.used_gb || 0) * 1024**3) }}</span>
            <span>Total: {{ formatBytes((systemMetrics.memory?.swap?.total_gb || 0) * 1024**3) }}</span>
            <span>{{ systemMetrics.memory?.swap?.usage_percent || 0 }}%</span>
          </div>
        </div>
      </div>
      
      <div class="info-card">
        <div class="info-header">
          <span class="info-title">💿 Disk I/O</span>
        </div>
        <div class="info-content">
          <div class="disk-io">
            <span>Read: {{ (systemMetrics.disk?.read_mb_s || 0).toFixed(2) }} MB/s</span>
            <span>Write: {{ (systemMetrics.disk?.write_mb_s || 0).toFixed(2) }} MB/s</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Service Status -->
    <div class="services-section">
      <h4>🔧 Service Status</h4>
      <div class="services-grid">
        <div 
          v-for="(service, name) in serviceStatus" 
          :key="name"
          class="service-card"
          :class="service.status"
        >
          <div class="service-icon">
            {{ getServiceIcon(name) }}
          </div>
          <div class="service-info">
            <div class="service-name">{{ formatServiceName(name) }}</div>
            <div class="service-status">{{ service.status.toUpperCase() }}</div>
            <div v-if="service.port" class="service-port">Port: {{ service.port }}</div>
            <div v-if="service.error" class="service-error">{{ service.error }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Active Processes -->
    <div class="processes-section">
      <h4>⚡ Active Processes</h4>
      <div class="processes-list">
        <div 
          v-for="process in systemMetrics.processes" 
          :key="process.pid"
          class="process-item"
        >
          <div class="process-name">{{ process.name }}</div>
          <div class="process-metrics">
            <span class="process-cpu">{{ process.cpu_percent?.toFixed(1) || 0 }}% CPU</span>
            <span class="process-memory">{{ process.memory_mb?.toFixed(1) || 0 }} MB</span>
          </div>
          <div class="process-pid">PID: {{ process.pid }}</div>
        </div>
      </div>
    </div>
    
    <!-- Performance Trends -->
    <div class="trends-section">
      <h4>📈 Performance Trends</h4>
      <div class="trends-container">
        <canvas ref="trendsChart" width="800" height="300"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { apiGet } from '../../utils/api.js'

export default {
  name: 'SystemMonitor',
  setup() {
    const loading = ref(false)
    const autoRefresh = ref(false)
    const refreshInterval = ref(null)
    const systemMetrics = ref({})
    const systemHealth = ref({ status: 'unknown', uptime_seconds: 0 })
    const systemAlerts = ref({ total_count: 0, critical_count: 0, warning_count: 0 })
    const serviceStatus = ref({})
    const trendsChart = ref(null)
    
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token')
      return token ? { 'Authorization': `Bearer ${token}` } : {}
    }
    
    const loadSystemMetrics = async () => {
      try {
        const data = await apiGet('/monitoring/system-health')
        systemMetrics.value = data
        
        // Calculate system health based on metrics
        const alerts = data.alerts || []
        systemHealth.value = {
          status: alerts.length > 0 ? 'warning' : 'healthy',
          uptime_seconds: data.uptime_seconds || 0
        }
        
        // Update system alerts
        systemAlerts.value = {
          total_count: alerts.length,
          critical_count: alerts.filter(a => a.severity === 'critical').length,
          warning_count: alerts.filter(a => a.severity === 'warning').length
        }
      } catch (error) {
        console.error('Error loading system metrics:', error)
        systemHealth.value = { status: 'error', uptime_seconds: 0 }
        systemMetrics.value = {}
      }
    }
    
    const loadServiceStatus = async () => {
      try {
        const data = await apiGet('/monitoring/service-status')
        serviceStatus.value = data
      } catch (error) {
        console.error('Error loading service status:', error)
        serviceStatus.value = {}
      }
    }
    
    const loadSystemAlerts = async () => {
      try {
        // Alerts are now loaded as part of system metrics
        // This function can be used for additional alert data if needed
      } catch (error) {
        console.error('Error loading system alerts:', error)
      }
    }
    
    const refreshMetrics = async () => {
      loading.value = true
      await Promise.all([
        loadSystemMetrics(),
        loadServiceStatus(),
        loadSystemAlerts()
      ])
      await nextTick()
      renderTrendsChart()
      loading.value = false
    }
    
    const toggleAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
      
      if (autoRefresh.value) {
        refreshInterval.value = setInterval(refreshMetrics, autoRefresh.value)
      }
    }
    
    const formatUptime = (seconds) => {
      const days = Math.floor(seconds / 86400)
      const hours = Math.floor((seconds % 86400) / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      if (days > 0) {
        return `${days}d ${hours}h ${minutes}m`
      } else if (hours > 0) {
        return `${hours}h ${minutes}m`
      } else {
        return `${minutes}m`
      }
    }
    
    const formatBytes = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const getHealthIcon = (status) => {
      const icons = {
        'healthy': '✅',
        'warning': '⚠️',
        'error': '❌',
        'unknown': '❓'
      }
      return icons[status] || '❓'
    }
    
    const getServiceIcon = (serviceName) => {
      const icons = {
        'backend': '🔧',
        'socketio': '🔌',
        'frontend': '🖥️',
        'mongodb': '🗄️',
        'redis': '⚡',
        'nginx': '🌐'
      }
      return icons[serviceName] || '📦'
    }
    
    const formatServiceName = (serviceName) => {
      return serviceName.charAt(0).toUpperCase() + serviceName.slice(1).replace(/([A-Z])/g, ' $1')
    }
    
    const renderTrendsChart = () => {
      if (!trendsChart.value) return
      
      const ctx = trendsChart.value.getContext('2d')
      const width = trendsChart.value.width
      const height = trendsChart.value.height
      
      // Clear canvas
      ctx.clearRect(0, 0, width, height)
      
      // Draw grid
      ctx.strokeStyle = '#e5e7eb'
      ctx.lineWidth = 1
      
      // Horizontal lines
      for (let i = 0; i <= 4; i++) {
        const y = (height - 40) * (i / 4) + 20
        ctx.beginPath()
        ctx.moveTo(40, y)
        ctx.lineTo(width - 20, y)
        ctx.stroke()
      }
      
      // Draw sample data lines
      const datasets = [
        { color: '#3b82f6', label: 'CPU' },
        { color: '#10b981', label: 'Memory' },
        { color: '#f59e0b', label: 'Disk' }
      ]
      
      datasets.forEach(dataset => {
        ctx.strokeStyle = dataset.color
        ctx.lineWidth = 2
        ctx.beginPath()
        
        for (let i = 0; i < 20; i++) {
          const x = 40 + (i / 19) * (width - 60)
          const y = height - 40 - Math.random() * (height - 60)
          
          if (i === 0) {
            ctx.moveTo(x, y)
          } else {
            ctx.lineTo(x, y)
          }
        }
        
        ctx.stroke()
      })
      
      // Draw labels
      ctx.fillStyle = '#6b7280'
      ctx.font = '12px sans-serif'
      ctx.fillText('0%', 10, height - 20)
      ctx.fillText('100%', 5, 20)
      ctx.fillText('Time', width / 2, height - 5)
    }
    
    onMounted(() => {
      refreshMetrics()
    })
    
    onUnmounted(() => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
    })
    
    return {
      loading,
      autoRefresh,
      systemMetrics,
      systemHealth,
      systemAlerts,
      serviceStatus,
      trendsChart,
      refreshMetrics,
      toggleAutoRefresh,
      formatUptime,
      formatBytes,
      getHealthIcon,
      getServiceIcon,
      formatServiceName
    }
  }
}
</script>

<style scoped>
.system-monitor {
  background: var(--bg-primary);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.monitor-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.monitor-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.refresh-btn {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.refresh-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.refresh-btn:hover::before {
  left: 100%;
}

.refresh-btn:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-1px);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-select {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  padding: 0.5rem;
  transition: all 0.3s ease;
}

.refresh-select:focus {
  outline: none;
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.health-overview {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.health-card {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  padding: 1.5rem;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--glass-shadow-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.health-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.health-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-xl);
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.health-card.healthy {
  border-left: 4px solid rgba(34, 197, 94, 0.6);
}

.health-card.warning {
  border-left: 4px solid rgba(245, 158, 11, 0.6);
}

.health-card.error {
  border-left: 4px solid rgba(239, 68, 68, 0.6);
}

.health-icon {
  font-size: 2rem;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.health-info {
  flex: 1;
}

.health-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.health-status {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 1.2rem;
  margin-bottom: 0.25rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.health-uptime {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.alerts-card {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  padding: 1.5rem;
  border-radius: 20px;
  box-shadow: var(--glass-shadow-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.alerts-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.alerts-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-xl);
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.alerts-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.alerts-count {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.alerts-count.has-alerts {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
  color: #ef4444;
}

.alerts-breakdown {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
}

.alert-critical {
  color: #ef4444;
  font-weight: 500;
}

.alert-warning {
  color: #f59e0b;
  font-weight: 500;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: var(--glass-shadow-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--glass-shadow-xl);
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.metric-card.cpu {
  border-left: 4px solid rgba(59, 130, 246, 0.6);
}

.metric-card.memory {
  border-left: 4px solid rgba(16, 185, 129, 0.6);
}

.metric-card.disk {
  border-left: 4px solid rgba(245, 158, 11, 0.6);
}

.metric-card.network {
  border-left: 4px solid rgba(139, 92, 246, 0.6);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-primary);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metric-bar {
  height: 8px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1rem;
  border: 1px solid var(--glass-border);
}

.metric-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 3px;
}

.metric-fill.cpu-fill {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.8), rgba(96, 165, 250, 0.8));
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
}

.metric-fill.memory-fill {
  background: linear-gradient(90deg, rgba(16, 185, 129, 0.8), rgba(52, 211, 153, 0.8));
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.3);
}

.metric-fill.disk-fill {
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.8), rgba(251, 191, 36, 0.8));
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.3);
}

.metric-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* Info Grid Styles */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.info-card {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  padding: 1.5rem;
  border-radius: 20px;
  box-shadow: var(--glass-shadow-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.info-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-xl);
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.info-header {
  margin-bottom: 1rem;
}

.info-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-value {
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--text-primary);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.info-subtitle {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.load-averages,
.swap-info,
.disk-io {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.9rem;
}

.load-averages span,
.swap-info span,
.disk-io span {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  font-family: monospace;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.load-averages span:hover,
.swap-info span:hover,
.disk-io span:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
}

.services-section,
.processes-section,
.trends-section {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  padding: 1.5rem;
  border-radius: 20px;
  margin-bottom: 2rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.services-section::before,
.processes-section::before,
.trends-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.services-section h4,
.processes-section h4,
.trends-section h4 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.service-card {
  background: var(--bg-primary);
  padding: 1rem;
  border-radius: 0.5rem;
  border-left: 4px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.service-card.running {
  border-left-color: #10b981;
}

.service-card.stopped {
  border-left-color: #ef4444;
}

.service-card.error {
  border-left-color: #f59e0b;
}

.service-icon {
  font-size: 1.5rem;
}

.service-info {
  flex: 1;
}

.service-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.service-status {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}

.service-port,
.service-error {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.processes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.process-item {
  background: var(--bg-primary);
  padding: 1rem;
  border-radius: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.process-name {
  font-weight: 600;
  color: var(--text-primary);
}

.process-metrics {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.process-pid {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.trends-container {
  background: var(--bg-primary);
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

@media (max-width: 768px) {
  .health-overview {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
}
</style>
