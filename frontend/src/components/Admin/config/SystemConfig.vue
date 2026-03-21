<template>
  <div class="system-config">
    <div class="section-header">
      <h3>⚙️ System Configuration</h3>
      <div class="system-actions">
        <button @click="checkSystemStatus" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-refresh"></i> Check Status
        </button>
        <button @click="showPanicModal = true" class="btn btn-danger">
          <i class="fas fa-exclamation-triangle"></i> Panic Button
        </button>
      </div>
    </div>

    <!-- System Status -->
    <div class="status-section">
      <h4>System Status</h4>
      <div class="status-grid">
        <div class="status-card" :class="systemStatus.backend ? 'online' : 'offline'">
          <div class="status-icon">
            <i :class="systemStatus.backend ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
          </div>
          <div class="status-info">
            <div class="status-label">Backend</div>
            <div class="status-value">{{ systemStatus.backend ? 'Online' : 'Offline' }}</div>
          </div>
        </div>
        
        <div class="status-card" :class="systemStatus.database ? 'online' : 'offline'">
          <div class="status-icon">
            <i :class="systemStatus.database ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
          </div>
          <div class="status-info">
            <div class="status-label">Database</div>
            <div class="status-value">{{ systemStatus.database ? 'Connected' : 'Disconnected' }}</div>
          </div>
        </div>
        
        <div class="status-card" :class="systemStatus.redis ? 'online' : 'offline'">
          <div class="status-icon">
            <i :class="systemStatus.redis ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
          </div>
          <div class="status-info">
            <div class="status-label">Redis</div>
            <div class="status-value">{{ systemStatus.redis ? 'Connected' : 'Disconnected' }}</div>
          </div>
        </div>
        
        <div class="status-card" :class="systemStatus.socketio ? 'online' : 'offline'">
          <div class="status-icon">
            <i :class="systemStatus.socketio ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
          </div>
          <div class="status-info">
            <div class="status-label">Socket.IO</div>
            <div class="status-value">{{ systemStatus.socketio ? 'Running' : 'Stopped' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Metrics -->
    <div class="metrics-section">
      <h4>System Metrics</h4>
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-value">{{ systemMetrics.cpu_usage }}%</div>
          <div class="metric-label">CPU Usage</div>
          <div class="metric-bar">
            <div class="metric-fill" :style="{ width: systemMetrics.cpu_usage + '%' }"></div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-value">{{ systemMetrics.memory_usage }}%</div>
          <div class="metric-label">Memory Usage</div>
          <div class="metric-bar">
            <div class="metric-fill" :style="{ width: systemMetrics.memory_usage + '%' }"></div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-value">{{ systemMetrics.disk_usage }}%</div>
          <div class="metric-label">Disk Usage</div>
          <div class="metric-bar">
            <div class="metric-fill" :style="{ width: systemMetrics.disk_usage + '%' }"></div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-value">{{ systemMetrics.uptime }}</div>
          <div class="metric-label">System Uptime</div>
        </div>
      </div>
    </div>

    <!-- Maintenance Controls -->
    <div class="maintenance-section">
      <h4>Maintenance Controls</h4>
      <div class="maintenance-controls">
        <div class="control-item">
          <label>
            <input 
              v-model="maintenanceMode" 
              type="checkbox"
              @change="toggleMaintenanceMode"
              :disabled="loading"
            />
            Maintenance Mode
          </label>
          <p class="control-description">
            Enable maintenance mode to prevent user access
          </p>
        </div>
        
        <div class="control-item">
          <label>
            <input 
              v-model="debugMode" 
              type="checkbox"
              @change="toggleDebugMode"
              :disabled="loading"
            />
            Debug Mode
          </label>
          <p class="control-description">
            Enable detailed logging and debug information
          </p>
        </div>
        
        <div class="control-item">
          <label>
            <input 
              v-model="apiRateLimit" 
              type="checkbox"
              @change="toggleRateLimit"
              :disabled="loading"
            />
            API Rate Limiting
          </label>
          <p class="control-description">
            Enable rate limiting for API endpoints
          </p>
        </div>
      </div>
    </div>

    <!-- System Actions -->
    <div class="actions-section">
      <h4>System Actions</h4>
      <div class="action-grid">
        <button @click="clearCache" class="btn btn-outline" :disabled="loading">
          <i class="fas fa-broom"></i> Clear Cache
        </button>
        <button @click="restartServices" class="btn btn-outline" :disabled="loading">
          <i class="fas fa-redo"></i> Restart Services
        </button>
        <button @click="backupDatabase" class="btn btn-outline" :disabled="loading">
          <i class="fas fa-download"></i> Backup Database
        </button>
        <button @click="cleanupLogs" class="btn btn-outline" :disabled="loading">
          <i class="fas fa-trash"></i> Cleanup Logs
        </button>
        <button @click="showNukeModal = true" class="btn btn-danger">
          <i class="fas fa-radiation"></i> Nuke Protocol
        </button>
      </div>
    </div>

    <!-- Panic Modal -->
    <div v-if="showPanicModal" class="modal-overlay" @click="closePanicModal">
      <div class="modal-content panic-modal" @click.stop>
        <div class="modal-header">
          <h3>🚨 PANIC BUTTON</h3>
          <button @click="closePanicModal" class="btn-close">&times;</button>
        </div>
        
        <div class="panic-content">
          <div class="panic-warning">
            <i class="fas fa-exclamation-triangle"></i>
            <p>This will immediately:</p>
            <ul>
              <li>Kill all user sessions</li>
              <li>Enable maintenance mode</li>
              <li>Disable all non-essential services</li>
              <li>Lock down the system</li>
            </ul>
          </div>
          
          <div class="panic-actions">
            <button @click="activatePanicMode" class="btn btn-danger" :disabled="loading">
              🚨 ACTIVATE PANIC MODE
            </button>
            <button @click="closePanicModal" class="btn btn-outline">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Nuke Modal -->
    <div v-if="showNukeModal" class="modal-overlay" @click="closeNukeModal">
      <div class="modal-content nuke-modal" @click.stop>
        <div class="modal-header">
          <h3>☢️ NUKE PROTOCOL</h3>
          <button @click="closeNukeModal" class="btn-close">&times;</button>
        </div>
        
        <div class="nuke-content">
          <div class="nuke-warning">
            <i class="fas fa-radiation"></i>
            <p>This will permanently delete ALL data including:</p>
            <ul>
              <li>All user accounts</li>
              <li>All orders and history</li>
              <li>All files and uploads</li>
              <li>All system logs</li>
              <li>Database contents</li>
            </ul>
            <p><strong>THIS ACTION CANNOT BE UNDONE!</strong></p>
          </div>
          
          <div class="nuke-verification">
            <label>Type "TOTAL DATA WIPE" to confirm:</label>
            <input 
              v-model="nukeConfirmation" 
              type="text" 
              class="form-control"
              placeholder="TOTAL DATA WIPE"
            />
          </div>
          
          <div class="nuke-actions">
            <button 
              @click="activateNukeProtocol" 
              class="btn btn-danger" 
              :disabled="loading || nukeConfirmation !== 'TOTAL DATA WIPE'"
            >
              ☢️ NUKE EVERYTHING
            </button>
            <button @click="closeNukeModal" class="btn btn-outline">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '../../../utils/api.js'

export default {
  name: 'SystemConfig',
  setup() {
    // State
    const loading = ref(false)
    const showPanicModal = ref(false)
    const showNukeModal = ref(false)
    const nukeConfirmation = ref('')
    
    const systemStatus = reactive({
      backend: false,
      database: false,
      redis: false,
      socketio: false
    })
    
    const systemMetrics = reactive({
      cpu_usage: 0,
      memory_usage: 0,
      disk_usage: 0,
      uptime: '0d 0h 0m'
    })
    
    const maintenanceMode = ref(false)
    const debugMode = ref(false)
    const apiRateLimit = ref(true)

    // Methods
    const checkSystemStatus = async () => {
      try {
        loading.value = true
        
        // Check backend (using direct fetch since it's a root endpoint and doesn't need auth)
        const backendResponse = await fetch('/health')
        systemStatus.backend = backendResponse.ok
        
        // Check database
        try {
          await apiGet('/admin/status/database')
          systemStatus.database = true
        } catch {
          systemStatus.database = false
        }
        
        // Check Redis
        try {
          await apiGet('/admin/status/redis')
          systemStatus.redis = true
        } catch {
          systemStatus.redis = false
        }
        
        // Check Socket.IO
        const socketUrl = window.location.origin === 'https://haku.io.vn' 
          ? 'https://haku.io.vn' 
          : 'http://localhost:8001'
        try {
          const socketioResponse = await fetch(socketUrl)
          systemStatus.socketio = socketioResponse.ok
        } catch {
          systemStatus.socketio = false
        }
        
        // Get system metrics
        try {
          const metrics = await apiGet('/monitoring/system-health')
          systemMetrics.cpu_usage = Math.round(metrics.cpu_percent || 0)
          systemMetrics.memory_usage = Math.round(metrics.memory_percent || 0)
          systemMetrics.disk_usage = Math.round(metrics.disk_percent || 0)
          systemMetrics.uptime = metrics.uptime || 'Unknown'
        } catch (error) {
          console.error('Error fetching metrics:', error)
        }
        
      } catch (error) {
        console.error('Error checking system status:', error)
      } finally {
        loading.value = false
      }
    }

    const toggleMaintenanceMode = async () => {
      try {
        loading.value = true
        
        const endpoint = maintenanceMode.value ? '/admin/maintenance-on' : '/admin/maintenance-off'
        await apiPost(endpoint)
      } catch (error) {
        console.error('Error toggling maintenance mode:', error)
        // Revert checkbox if request failed
        maintenanceMode.value = !maintenanceMode.value
      } finally {
        loading.value = false
      }
    }

    const toggleDebugMode = async () => {
      // Implementation would depend on your debug mode system
      console.log('Toggle debug mode:', debugMode.value)
    }

    const toggleRateLimit = async () => {
      // Implementation would depend on your rate limiting system
      console.log('Toggle rate limiting:', apiRateLimit.value)
    }

    const clearCache = async () => {
      try {
        loading.value = true
        await apiPost('/admin/clear-cache')
        alert('Cache cleared successfully')
      } catch (error) {
        console.error('Error clearing cache:', error)
      } finally {
        loading.value = false
      }
    }

    const restartServices = async () => {
      if (!confirm('Restart all services? This may cause temporary downtime.')) {
        return
      }
      
      try {
        loading.value = true
        await apiPost('/admin/restart-services')
        alert('Services restart initiated')
      } catch (error) {
        console.error('Error restarting services:', error)
      } finally {
        loading.value = false
      }
    }

    const backupDatabase = async () => {
      try {
        loading.value = true
        const data = await apiPost('/admin/backup-database')
        alert(`Database backup completed: ${data.backup_file}`)
      } catch (error) {
        console.error('Error backing up database:', error)
      } finally {
        loading.value = false
      }
    }

    const cleanupLogs = async () => {
      if (!confirm('Clean up old system logs?')) {
        return
      }
      
      try {
        loading.value = true
        await apiPost('/admin/cleanup-logs')
        alert('Log cleanup completed')
      } catch (error) {
        console.error('Error cleaning up logs:', error)
      } finally {
        loading.value = false
      }
    }

    const activatePanicMode = async () => {
      try {
        loading.value = true
        await apiPost('/admin/panic')
        alert('PANIC MODE ACTIVATED! System locked down.')
        closePanicModal()
      } catch (error) {
        console.error('Error activating panic mode:', error)
      } finally {
        loading.value = false
      }
    }

    const activateNukeProtocol = async () => {
      try {
        loading.value = true
        await apiPost('/admin/nuke', {
          confirmation: nukeConfirmation.value
        })
        alert('Nuke protocol activated. All data has been wiped.')
        closeNukeModal()
      } catch (error) {
        console.error('Error activating nuke protocol:', error)
      } finally {
        loading.value = false
      }
    }

    const closePanicModal = () => {
      showPanicModal.value = false
    }

    const closeNukeModal = () => {
      showNukeModal.value = false
      nukeConfirmation.value = ''
    }

    // Lifecycle
    onMounted(() => {
      checkSystemStatus()
    })

    return {
      loading,
      showPanicModal,
      showNukeModal,
      nukeConfirmation,
      systemStatus,
      systemMetrics,
      maintenanceMode,
      debugMode,
      apiRateLimit,
      checkSystemStatus,
      toggleMaintenanceMode,
      toggleDebugMode,
      toggleRateLimit,
      clearCache,
      restartServices,
      backupDatabase,
      cleanupLogs,
      activatePanicMode,
      activateNukeProtocol,
      closePanicModal,
      closeNukeModal
    }
  }
}
</script>

<style scoped>
.system-config {
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

.system-actions {
  display: flex;
  gap: 12px;
}

.status-section,
.metrics-section,
.maintenance-section,
.actions-section {
  margin-bottom: 30px;
}

.status-section h4,
.metrics-section h4,
.maintenance-section h4,
.actions-section h4 {
  margin: 0 0 16px 0;
  color: #34495e;
}

.status-grid,
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.status-card,
.metric-card {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-card.online {
  border-color: #27ae60;
  background: #d4edda;
}

.status-card.offline {
  border-color: #e74c3c;
  background: #f8d7da;
}

.status-icon {
  font-size: 24px;
}

.status-icon .fa-check-circle {
  color: #27ae60;
}

.status-icon .fa-times-circle {
  color: #e74c3c;
}

.status-info {
  flex: 1;
}

.status-label,
.metric-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.status-value,
.metric-value {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.metric-bar {
  width: 100%;
  height: 4px;
  background: #e1e8ed;
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: #3498db;
  transition: width 0.3s ease;
}

.maintenance-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.control-item {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
}

.control-item label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #34495e;
  margin-bottom: 8px;
}

.control-description {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.panic-modal {
  border: 2px solid #e74c3c;
}

.nuke-modal {
  border: 2px solid #8e44ad;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
}

.panic-content,
.nuke-content {
  padding: 20px;
}

.panic-warning,
.nuke-warning {
  text-align: center;
  margin-bottom: 30px;
}

.panic-warning i,
.nuke-warning i {
  font-size: 48px;
  color: #e74c3c;
  margin-bottom: 16px;
  display: block;
}

.nuke-warning i {
  color: #8e44ad;
}

.panic-warning p,
.nuke-warning p {
  font-weight: 600;
  margin-bottom: 16px;
}

.panic-warning ul,
.nuke-warning ul {
  text-align: left;
  margin: 0 0 16px 0;
  padding-left: 20px;
}

.panic-actions,
.nuke-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.nuke-verification {
  margin-bottom: 20px;
}

.nuke-verification label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #34495e;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
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

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-danger {
  background: #e74c3c;
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

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .system-actions {
    justify-content: center;
  }
  
  .status-grid,
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .maintenance-controls {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>
