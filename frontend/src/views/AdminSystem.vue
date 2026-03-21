<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>System Admin</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>System configuration and maintenance</p>
    
</div>

    <div class="page-actions">

      <button class="btn btn-primary" @click="runDiagnostics">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2 L12 6 M12 18 L12 22 M4.93 4.93 L7.76 7.76 M16.24 16.24 L19.07 19.07 M2 12 L6 12 M18 12 L22 12 M4.93 19.07 L7.76 16.24 M16.24 7.76 L19.07 4.93" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        Diagnostics
      </button>
      <button class="btn btn-secondary" @click="refreshSystem">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M12 6 L12 12 L16 16" stroke="currentColor" stroke-width="2"/>
        </svg>
        Refresh
      </button>
    
</div>

    <div class="system-content">
      <!-- System Status Overview -->
      <div class="system-overview">
        <h2>System Status</h2>
        <div class="status-grid">
          <div class="status-card">
            <div class="status-icon online">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
              </svg>
            </div>
            <div class="status-info">
              <h3>System Health</h3>
              <span class="status-text">Online</span>
              <div class="status-details">All systems operational</div>
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-icon warning">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2 L2 20 L22 20 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M12 8 L12 12 M12 16 L12 16.5" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="status-info">
              <h3>Database</h3>
              <span class="status-text">Warning</span>
              <div class="status-details">High memory usage</div>
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-icon online">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
              </svg>
            </div>
            <div class="status-info">
              <h3>API Server</h3>
              <span class="status-text">Online</span>
              <div class="status-details">Response time: 45ms</div>
            </div>
          </div>
          
          <div class="status-card">
            <div class="status-icon online">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
              </svg>
            </div>
            <div class="status-info">
              <h3>Cache</h3>
              <span class="status-text">Online</span>
              <div class="status-details">Hit rate: 94%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- System Metrics -->
      <div class="metrics-section">
        <h2>System Metrics</h2>
        <div class="metrics-grid">
          <div class="metric-card">
            <h3>CPU Usage</h3>
            <div class="metric-chart">
              <div class="circular-progress" :style="{ '--progress': systemMetrics.cpu + '%' }">
                <div class="progress-value">{{ systemMetrics.cpu }}%</div>
              </div>
            </div>
          </div>
          
          <div class="metric-card">
            <h3>Memory Usage</h3>
            <div class="metric-chart">
              <div class="circular-progress" :style="{ '--progress': systemMetrics.memory + '%' }">
                <div class="progress-value">{{ systemMetrics.memory }}%</div>
              </div>
            </div>
          </div>
          
          <div class="metric-card">
            <h3>Disk Usage</h3>
            <div class="metric-chart">
              <div class="circular-progress" :style="{ '--progress': systemMetrics.disk + '%' }">
                <div class="progress-value">{{ systemMetrics.disk }}%</div>
              </div>
            </div>
          </div>
          
          <div class="metric-card">
            <h3>Network I/O</h3>
            <div class="metric-chart">
              <div class="circular-progress" :style="{ '--progress': systemMetrics.network + '%' }">
                <div class="progress-value">{{ systemMetrics.network }}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- System Actions -->
      <div class="actions-section">
        <h2>System Actions</h2>
        <div class="actions-grid">
          <div class="action-card">
            <div class="action-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 12 L5 12 M19 12 L21 12 M12 3 L12 5 M12 19 L12 21" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
            </div>
            <h3>Restart Services</h3>
            <p>Safely restart all system services</p>
            <button class="btn btn-outline" @click="restartServices">Restart</button>
          </div>
          
          <div class="action-card">
            <div class="action-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2 L12 6 M12 18 L12 22 M4.93 4.93 L7.76 7.76 M16.24 16.24 L19.07 19.07 M2 12 L6 12 M18 12 L22 12 M4.93 19.07 L7.76 16.24 M16.24 7.76 L19.07 4.93" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
            </div>
            <h3>Clear Cache</h3>
            <p>Clear system and application cache</p>
            <button class="btn btn-outline" @click="clearCache">Clear</button>
          </div>
          
          <div class="action-card">
            <div class="action-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M14 2 L6 2 C4.9 2 4 2.9 4 4 L4 20 C4 21.1 4.9 22 6 22 L18 22 C19.1 22 20 21.1 20 20 L20 8 L14 2 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M14 2 L14 8 L20 8" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
            </div>
            <h3>Generate Report</h3>
            <p>Create system health report</p>
            <button class="btn btn-outline" @click="generateReport">Generate</button>
          </div>
          
          <div class="action-card danger">
            <div class="action-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2 L12 7 M12 17 L12 22 M2 12 L7 12 M17 12 L22 12" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
            </div>
            <h3>System Reset</h3>
            <p>⚠️ Reset system to factory defaults</p>
            <button class="btn btn-danger" @click="systemReset">Reset</button>
          </div>
        </div>
      </div>

      <!-- Recent Logs -->
      <div class="logs-section">
        <h2>Recent System Logs</h2>
        <div class="logs-container">
          <div 
            v-for="log in recentLogs" 
            :key="log.id"
            class="log-entry"
            :class="log.level"
          >
            <div class="log-time">{{ formatTime(log.timestamp) }}</div>
            <div class="log-level">{{ log.level }}</div>
            <div class="log-message">{{ log.message }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const systemMetrics = ref({
  cpu: 45,
  memory: 78,
  disk: 62,
  network: 23
})

const recentLogs = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    level: 'INFO',
    message: 'System health check completed successfully'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    level: 'WARNING',
    message: 'Database memory usage above threshold (85%)'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    level: 'INFO',
    message: 'Cache cleared successfully'
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 1000 * 60 * 45),
    level: 'ERROR',
    message: 'Failed to connect to external API service'
  }
])

let metricsInterval = null

const runDiagnostics = () => {
  console.log('Running system diagnostics...')
  // Simulate diagnostic check
  setTimeout(() => {
    console.log('Diagnostics completed')
  }, 2000)
}

const refreshSystem = () => {
  console.log('Refreshing system data...')
  updateMetrics()
}

const restartServices = () => {
  if (confirm('Are you sure you want to restart all services? This may cause temporary downtime.')) {
    console.log('Restarting services...')
  }
}

const clearCache = () => {
  if (confirm('Clear cache? This may temporarily slow down the system.')) {
    console.log('Clearing cache...')
  }
}

const generateReport = () => {
  console.log('Generating system report...')
}

const systemReset = () => {
  const confirmation = prompt('This will reset the entire system. Type "RESET" to confirm:')
  if (confirmation === 'RESET') {
    console.log('System reset initiated...')
  }
}

const updateMetrics = () => {
  // Simulate real-time metrics updates
  systemMetrics.value.cpu = Math.floor(Math.random() * 30) + 30
  systemMetrics.value.memory = Math.floor(Math.random() * 40) + 50
  systemMetrics.value.disk = Math.floor(Math.random() * 20) + 55
  systemMetrics.value.network = Math.floor(Math.random() * 50) + 10
}

const formatTime = (timestamp) => {
  return timestamp.toLocaleTimeString()
}

onMounted(() => {
  console.log('Admin System component mounted')
  // Update metrics every 5 seconds
  metricsInterval = setInterval(updateMetrics, 5000)
})

onUnmounted(() => {
  if (metricsInterval) {
    clearInterval(metricsInterval)
  }
})
</script>

<style scoped>
.system-content {
  max-width: 1200px;
  margin: 0 auto;
}

.system-overview,
.metrics-section,
.actions-section,
.logs-section {
  margin-bottom: 3rem;
}

.system-overview h2,
.metrics-section h2,
.actions-section h2,
.logs-section h2 {
  margin: 0 0 1.5rem 0;
  color: #f1f5f9;
  font-size: 1.5rem;
  font-weight: 600;
}

.status-grid,
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.status-card,
.metric-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.status-card:hover,
.metric-card:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.status-icon.online {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.status-icon.warning {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.status-icon.error {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.status-info {
  flex: 1;
}

.status-info h3 {
  margin: 0 0 0.25rem 0;
  color: #f1f5f9;
  font-size: 1.125rem;
  font-weight: 600;
}

.status-text {
  color: #10b981;
  font-weight: 600;
  font-size: 0.875rem;
}

.status-text.warning {
  color: #f59e0b;
}

.status-text.error {
  color: #ef4444;
}

.status-details {
  color: #94a3b8;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.metric-card {
  flex-direction: column;
  text-align: center;
}

.metric-card h3 {
  margin: 0 0 1rem 0;
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 600;
}

.metric-chart {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.circular-progress {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    #10b981 0deg,
    #10b981 calc(var(--progress) * 3.6deg),
    rgba(255, 255, 255, 0.1) calc(var(--progress) * 3.6deg)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.circular-progress::before {
  content: '';
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.8);
}

.progress-value {
  position: relative;
  z-index: 1;
  color: #f1f5f9;
  font-weight: 700;
  font-size: 1rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.action-card:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.action-card.danger {
  border-color: rgba(239, 68, 68, 0.3);
}

.action-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1.5rem;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
  font-size: 1.5rem;
}

.action-card.danger .action-icon {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.action-card h3 {
  margin: 0 0 0.75rem 0;
  color: #f1f5f9;
  font-size: 1.25rem;
  font-weight: 600;
}

.action-card p {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0 0 1.5rem 0;
  line-height: 1.4;
}

.logs-container {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.log-entry {
  display: grid;
  grid-template-columns: 80px 80px 1fr;
  gap: 1rem;
  padding: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-family: monospace;
  font-size: 0.875rem;
}

.log-entry:last-child {
  border-bottom: none;
}

.log-time {
  color: #94a3b8;
}

.log-level {
  font-weight: 600;
  text-transform: uppercase;
}

.log-entry.info .log-level {
  color: #3b82f6;
}

.log-entry.warning .log-level {
  color: #f59e0b;
}

.log-entry.error .log-level {
  color: #ef4444;
}

.log-message {
  color: #cbd5e1;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-outline {
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.3);
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
}

@media (max-width: 768px) {
  .status-grid,
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .log-entry {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .log-entry::before {
    content: attr(data-time);
    color: #94a3b8;
    font-size: 0.75rem;
  }
}
</style>

<style scoped>
.legacy-page-container {
  padding: 1rem;
}
.page-title { margin-bottom: 0.5rem; }
.page-subtitle { color: var(--text-secondary); margin-bottom: 1rem; }
.page-actions { margin-bottom: 1.5rem; }
</style>
