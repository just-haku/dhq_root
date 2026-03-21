<template>
  <div class="performance">
    <div class="page-header">
      <h1><i class="fas fa-server"></i> Server Performance</h1>
      <p>Real-time system health, storage &amp; power monitoring</p>
      <div class="header-meta">
        <span class="uptime-badge" v-if="serverUptime">
          <i class="fas fa-clock"></i> Uptime: {{ serverUptime }}
        </span>
        <button class="refresh-btn-sm" @click="loadPerformanceData" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
        </button>
      </div>
    </div>

    <!-- Vitals Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card" :class="getCardClass(performanceStats.cpuUsage)">
          <div class="card-icon"><i class="fas fa-microchip"></i></div>
          <div class="card-content">
            <h3>{{ performanceStats.cpuUsage.toFixed(1) }}%</h3>
            <p>CPU</p>
          </div>
        </div>
        <div class="overview-card" :class="getCardClass(performanceStats.memoryUsage)">
          <div class="card-icon"><i class="fas fa-memory"></i></div>
          <div class="card-content">
            <h3>{{ performanceStats.memoryUsage.toFixed(1) }}%</h3>
            <p>Memory</p>
          </div>
        </div>
        <div class="overview-card" :class="getCardClass(performanceStats.diskUsage)">
          <div class="card-icon"><i class="fas fa-hdd"></i></div>
          <div class="card-content">
            <h3>{{ performanceStats.diskUsage.toFixed(1) }}%</h3>
            <p>Root Disk</p>
          </div>
        </div>
        <div class="overview-card" :class="upsStatusClass">
          <div class="card-icon"><i class="fas fa-car-battery"></i></div>
          <div class="card-content">
            <h3>{{ systemResources.ups.battery_capacity || '—' }}</h3>
            <p>UPS Battery</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Dashboard Grid -->
    <div class="dashboard-grid">

      <!-- CPU Cores -->
      <div class="dash-card cpu-card">
        <div class="dash-card-header">
          <h3><i class="fas fa-microchip"></i> CPU Cores</h3>
          <span class="badge">{{ systemResources.cpu.cores }} cores @ {{ systemResources.cpu.frequency }} GHz</span>
        </div>
        <div class="load-avg">
          Load Average: {{ systemResources.cpu.loadAverage }}
        </div>
        <div class="cores-grid">
          <div v-for="(usage, index) in systemResources.cpu.coresUsage" :key="index" class="core-item">
            <div class="core-header">
              <span class="core-label">{{ index }}</span>
              <span class="core-value" :class="getUsageClass(usage)">{{ usage.toFixed(0) }}%</span>
            </div>
            <div class="core-bar">
              <div class="core-fill" :style="{ width: usage + '%' }" :class="getUsageClass(usage)"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Memory -->
      <div class="dash-card">
        <div class="dash-card-header">
          <h3><i class="fas fa-memory"></i> Memory</h3>
          <span class="badge">{{ systemResources.memory.usage_percent?.toFixed(1) || 0 }}%</span>
        </div>
        <div class="mem-visual">
          <div class="mem-ring">
            <svg viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="12"/>
              <circle cx="60" cy="60" r="50" fill="none" :stroke="getMemColor()" stroke-width="12"
                :stroke-dasharray="memCircle" stroke-dashoffset="0" stroke-linecap="round"
                transform="rotate(-90 60 60)"/>
            </svg>
            <div class="mem-center">
              <span class="mem-used">{{ systemResources.memory.used_gb?.toFixed(1) || 0 }}</span>
              <span class="mem-unit">GB used</span>
            </div>
          </div>
          <div class="mem-details">
            <div class="mem-row"><span class="dot used"></span><label>Used</label><span>{{ systemResources.memory.used_gb?.toFixed(1) || 0 }} GB</span></div>
            <div class="mem-row"><span class="dot available"></span><label>Available</label><span>{{ systemResources.memory.available_gb?.toFixed(1) || 0 }} GB</span></div>
            <div class="mem-row"><span class="dot total"></span><label>Total</label><span>{{ systemResources.memory.total_gb?.toFixed(1) || 0 }} GB</span></div>
            <div class="mem-row"><span class="dot swap"></span><label>Swap</label><span>{{ systemResources.memory.swap?.usage_percent || 0 }}%</span></div>
          </div>
        </div>
      </div>

      <!-- Disk Space -->
      <div class="dash-card storage-card">
        <div class="dash-card-header">
          <h3><i class="fas fa-database"></i> Disk Space</h3>
        </div>
        <div class="storage-list">
          <div v-for="mount in systemResources.storage.mounts" :key="mount.mount" class="storage-item">
            <div class="storage-meta">
              <div class="storage-left">
                <i :class="getDiskIcon(mount.mount)" class="storage-icon"></i>
                <div>
                  <div class="storage-mount">{{ mount.mount }}</div>
                  <div class="storage-fs">{{ mount.fs }}</div>
                </div>
              </div>
              <div class="storage-right">
                <span class="storage-size">{{ mount.used }} / {{ mount.size }}</span>
                <span class="storage-pct" :class="getUsageClass(parseInt(mount.percent))">{{ mount.percent }}</span>
              </div>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: mount.percent }" :class="getUsageClass(parseInt(mount.percent))"></div>
            </div>
          </div>
          <div v-if="!systemResources.storage.mounts?.length" class="no-data">No disk partitions found</div>
        </div>
      </div>

      <!-- UPS Status -->
      <div class="dash-card ups-detail-card">
        <div class="dash-card-header">
          <h3><i class="fas fa-car-battery"></i> CyberPower UPS</h3>
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <button class="refresh-btn-sm" @click="loadPerformanceData" :disabled="loading" title="Fetch UPS Stats">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            </button>
            <span class="badge" :class="systemResources.ups.state === 'Normal' ? 'badge-success' : 'badge-warning'">
              {{ systemResources.ups.state || systemResources.ups.status }}
            </span>
          </div>
        </div>

        <div v-if="systemResources.ups.status === 'Connected'" class="ups-content">
          <div class="ups-gauge-row">
            <div class="ups-gauge">
              <div class="battery-icon">
                <div class="battery-body">
                  <div class="battery-fill" :style="{ width: parseBatteryPct() + '%' }" :class="getBatteryClass()"></div>
                </div>
                <div class="battery-tip"></div>
              </div>
              <span class="battery-label">{{ systemResources.ups.battery_capacity }}</span>
            </div>
            <div class="ups-runtime">
              <i class="fas fa-hourglass-half"></i>
              <span>{{ systemResources.ups.remaining_runtime }}</span>
            </div>
          </div>

          <div class="ups-grid">
            <div class="ups-stat"><label>Model</label><span>{{ systemResources.ups.model || '—' }}</span></div>
            <div class="ups-stat"><label>Rated Power</label><span>{{ systemResources.ups.rating_power || '—' }}</span></div>
            <div class="ups-stat"><label>Supply</label><span>{{ systemResources.ups.power_supply || '—' }}</span></div>
            <div class="ups-stat"><label>Load</label><span>{{ systemResources.ups.load || '0 Watt' }}</span></div>
            <div class="ups-stat"><label>Utility</label><span>{{ systemResources.ups.utility_voltage || '—' }}</span></div>
            <div class="ups-stat"><label>Output</label><span>{{ systemResources.ups.output_voltage || '—' }}</span></div>
            <div class="ups-stat"><label>Frequency</label><span>{{ systemResources.ups.utility_frequency || '—' }}</span></div>
            <div class="ups-stat"><label>Interaction</label><span>{{ systemResources.ups.line_interaction || 'None' }}</span></div>
          </div>

          <div class="ups-event" v-if="systemResources.ups.last_power_event">
            <i class="fas fa-bolt"></i>
            <span>Last Event: {{ systemResources.ups.last_power_event }}</span>
          </div>
        </div>

        <div class="ups-error" v-else>
          <i class="fas fa-plug"></i>
          <p>{{ systemResources.ups.raw_error || 'UPS data unavailable' }}</p>
        </div>
      </div>

      <!-- Processes -->
      <div class="dash-card processes-card">
        <div class="dash-card-header">
          <h3><i class="fas fa-cogs"></i> DHQ Processes</h3>
          <span class="badge">{{ systemResources.processes?.length || 0 }}</span>
        </div>
        <div class="process-list">
          <div v-for="proc in systemResources.processes" :key="proc.pid" class="process-item">
            <span class="proc-name">{{ proc.name }}</span>
            <span class="proc-pid">PID {{ proc.pid }}</span>
            <span class="proc-cpu" :class="getUsageClass(proc.cpu_percent)">{{ proc.cpu_percent?.toFixed(1) }}%</span>
            <span class="proc-mem">{{ proc.memory_mb?.toFixed(0) }} MB</span>
          </div>
          <div v-if="!systemResources.processes?.length" class="no-data">No tracked processes</div>
        </div>
      </div>
    </div>

    <!-- Alerts -->
    <div class="alerts-section" v-if="performanceAlerts.length">
      <div class="section-header">
        <h2><i class="fas fa-bell"></i> Active Alerts</h2>
      </div>
      <div class="alerts-list">
        <div v-for="alert in performanceAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
          <i :class="getAlertIcon(alert.severity)"></i>
          <span class="alert-msg">{{ alert.message }}</span>
          <button class="dismiss-btn" @click="dismissAlert(alert)"><i class="fas fa-times"></i></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { apiGet } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'

const loading = ref(false)
const serverUptime = ref('')

const performanceStats = reactive({
  cpuUsage: 0,
  memoryUsage: 0,
  diskUsage: 0,
})

const systemResources = reactive({
  cpu: { usage: 0, cores: 0, coresUsage: [], frequency: 0, loadAverage: '0, 0, 0' },
  memory: { usage_percent: 0, total_gb: 0, used_gb: 0, available_gb: 0, swap: { usage_percent: 0 } },
  storage: { mounts: [] },
  ups: { status: 'Loading...', state: 'N/A', battery_capacity: '—' },
  processes: []
})

const performanceAlerts = ref([])

let refreshInterval = null

// Computed
const upsStatusClass = computed(() => {
  if (systemResources.ups.status !== 'Connected') return 'card-offline'
  const pct = parseBatteryPct()
  if (pct >= 80) return 'card-ok'
  if (pct >= 30) return 'card-warn'
  return 'card-crit'
})

const memCircle = computed(() => {
  const pct = systemResources.memory.usage_percent || 0
  const circumference = 2 * Math.PI * 50
  const filled = (pct / 100) * circumference
  return `${filled} ${circumference - filled}`
})

// Methods
const loadPerformanceData = async () => {
  loading.value = true
  try {
    const r = await apiGet('/monitoring/system-health')
    if (r) {
      // Uptime
      serverUptime.value = r.uptime_formatted

      // CPU
      systemResources.cpu.usage = r.cpu.usage_percent
      systemResources.cpu.cores = r.cpu.core_count
      systemResources.cpu.coresUsage = r.cpu.cores_percent || []
      systemResources.cpu.frequency = r.cpu.frequency_mhz ? (r.cpu.frequency_mhz / 1000).toFixed(2) : '0'
      systemResources.cpu.loadAverage = `${r.cpu.load_average['1min'].toFixed(2)}, ${r.cpu.load_average['5min'].toFixed(2)}, ${r.cpu.load_average['15min'].toFixed(2)}`

      // Memory
      Object.assign(systemResources.memory, r.memory)

      // Storage & UPS
      systemResources.storage = r.storage || { mounts: [] }
      Object.assign(systemResources.ups, r.ups)

      // Processes
      systemResources.processes = r.processes || []

      // Overview stats
      performanceStats.cpuUsage = r.cpu.usage_percent
      performanceStats.memoryUsage = r.memory.usage_percent
      performanceStats.diskUsage = r.disk?.usage_percent || 0

      // Alerts
      performanceAlerts.value = (r.alerts || []).map((a, i) => ({
        id: i, message: a.message, severity: a.type, timestamp: r.timestamp
      }))
    }
  } catch (e) {
    console.error('Performance data error:', e)
  } finally {
    loading.value = false
  }
}

const parseBatteryPct = () => {
  const cap = systemResources.ups.battery_capacity || '0'
  return parseInt(cap) || 0
}

const getBatteryClass = () => {
  const p = parseBatteryPct()
  if (p >= 80) return 'battery-high'
  if (p >= 30) return 'battery-mid'
  return 'battery-low'
}

const getUsageClass = (usage) => {
  if (usage >= 80) return 'critical'
  if (usage >= 60) return 'warning'
  return 'normal'
}

const getCardClass = (usage) => {
  if (usage >= 80) return 'card-crit'
  if (usage >= 60) return 'card-warn'
  return 'card-ok'
}

const getMemColor = () => {
  const p = systemResources.memory.usage_percent || 0
  if (p >= 80) return '#ef4444'
  if (p >= 60) return '#f59e0b'
  return '#10b981'
}

const getDiskIcon = (mount) => {
  if (mount.includes('storage') || mount.includes('hdd')) return 'fas fa-hdd'
  if (mount === '/') return 'fas fa-laptop'
  if (mount.includes('boot')) return 'fas fa-microchip'
  return 'fas fa-folder'
}

const getAlertIcon = (severity) => {
  return severity === 'critical' ? 'fas fa-exclamation-circle' : 'fas fa-exclamation-triangle'
}

const formatDateTime = (d) => d ? new Date(d).toLocaleString() : ''

const dismissAlert = (alert) => {
  performanceAlerts.value = performanceAlerts.value.filter(a => a.id !== alert.id)
}

onMounted(() => {
  loadPerformanceData()
  refreshInterval = setInterval(loadPerformanceData, 10000) // every 10s
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<style scoped>
.performance {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}
.page-header h1 i { margin-right: 0.5rem; opacity: 0.6; }

.page-header p {
  color: var(--text-secondary);
  font-size: 1rem;
  margin-bottom: 0.75rem;
}

.header-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.uptime-badge {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}
.uptime-badge i { margin-right: 0.4rem; }

.refresh-btn-sm {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}
.refresh-btn-sm:hover { color: var(--primary-color); background: var(--glass-bg-hover); }

/* Overview Cards */
.overview-section { margin-bottom: 2rem; }

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

.overview-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s;
  border-left: 4px solid transparent;
}

.card-ok { border-left-color: #10b981; }
.card-warn { border-left-color: #f59e0b; }
.card-crit { border-left-color: #ef4444; }
.card-offline { border-left-color: #6b7280; }

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  background: rgba(59, 130, 246, 0.12);
  color: #3b82f6;
}

.card-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}
.card-content p { color: var(--text-secondary); margin: 0; font-size: 0.85rem; }

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.dash-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
}

.dash-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.dash-card-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1rem;
}
.dash-card-header h3 i { margin-right: 0.5rem; opacity: 0.6; }

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.77rem;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.12);
  color: #3b82f6;
}
.badge-success { background: rgba(16, 185, 129, 0.12); color: #10b981; }
.badge-warning { background: rgba(245, 158, 11, 0.12); color: #f59e0b; }

/* CPU */
.cpu-card { grid-column: span 2; }

.load-avg {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
  padding: 0.5rem 0.75rem;
  background: var(--glass-bg-primary);
  border-radius: 8px;
  display: inline-block;
}

.cores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
}

.core-item {
  background: var(--glass-bg-primary);
  padding: 0.6rem;
  border-radius: 8px;
}

.core-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
}

.core-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.core-value {
  font-size: 0.8rem;
  font-weight: 700;
}
.core-value.normal { color: #10b981; }
.core-value.warning { color: #f59e0b; }
.core-value.critical { color: #ef4444; }

.core-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
}

.core-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}
.core-fill.normal { background: #10b981; }
.core-fill.warning { background: #f59e0b; }
.core-fill.critical { background: #ef4444; }

/* Memory */
.mem-visual {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.mem-ring {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}
.mem-ring svg { width: 100%; height: 100%; }

.mem-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
.mem-used { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); display: block; }
.mem-unit { font-size: 0.7rem; color: var(--text-secondary); }

.mem-details { flex: 1; }

.mem-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0;
  font-size: 0.85rem;
}
.mem-row label { flex: 1; color: var(--text-secondary); }
.mem-row span:last-child { font-weight: 600; color: var(--text-primary); }

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot.used { background: #3b82f6; }
.dot.available { background: #10b981; }
.dot.total { background: #6b7280; }
.dot.swap { background: #f59e0b; }

/* Storage */
.storage-card { grid-column: span 1; }

.storage-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 300px;
  overflow-y: auto;
}

.storage-item {
  background: var(--glass-bg-primary);
  padding: 1rem;
  border-radius: 10px;
}

.storage-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.storage-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.storage-icon {
  font-size: 1.1rem;
  color: var(--text-secondary);
  width: 24px;
  text-align: center;
}

.storage-mount {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
}
.storage-fs {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.storage-right {
  text-align: right;
}

.storage-size {
  font-size: 0.82rem;
  color: var(--text-secondary);
  display: block;
}

.storage-pct {
  font-weight: 700;
  font-size: 0.9rem;
}
.storage-pct.normal { color: #10b981; }
.storage-pct.warning { color: #f59e0b; }
.storage-pct.critical { color: #ef4444; }

/* Progress bar */
.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}
.progress-fill.normal { background: linear-gradient(90deg, #10b981, #34d399); }
.progress-fill.warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.progress-fill.critical { background: linear-gradient(90deg, #ef4444, #f87171); }

/* UPS */
.ups-content { display: flex; flex-direction: column; gap: 1rem; }

.ups-gauge-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border-radius: 10px;
}

.ups-gauge {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.battery-icon {
  display: flex;
  align-items: center;
}

.battery-body {
  width: 60px;
  height: 24px;
  border: 2px solid var(--text-secondary);
  border-radius: 4px;
  padding: 2px;
  overflow: hidden;
}

.battery-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}
.battery-fill.battery-high { background: #10b981; }
.battery-fill.battery-mid { background: #f59e0b; }
.battery-fill.battery-low { background: #ef4444; }

.battery-tip {
  width: 4px;
  height: 10px;
  background: var(--text-secondary);
  border-radius: 0 2px 2px 0;
}

.battery-label {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.ups-runtime {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: var(--text-secondary);
}
.ups-runtime i { color: #f59e0b; }

.ups-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.ups-stat {
  background: var(--glass-bg-primary);
  padding: 0.6rem;
  border-radius: 8px;
  text-align: center;
}
.ups-stat label {
  display: block;
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-bottom: 0.2rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.ups-stat span {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.82rem;
}

.ups-event {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  background: rgba(245, 158, 11, 0.08);
  border-radius: 8px;
  font-size: 0.82rem;
  color: var(--text-secondary);
}
.ups-event i { color: #f59e0b; }

.ups-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  text-align: center;
  gap: 0.75rem;
}
.ups-error i { font-size: 2rem; color: #6b7280; }
.ups-error p { color: var(--text-secondary); font-size: 0.85rem; margin: 0; }
.ups-error code {
  font-size: 0.75rem;
  background: var(--glass-bg-primary);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  color: var(--text-tertiary);
  word-break: break-all;
}

/* Processes */
.processes-card { grid-column: span 1; }

.process-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 250px;
  overflow-y: auto;
}

.process-item {
  display: grid;
  grid-template-columns: 1fr auto auto auto;
  gap: 1rem;
  align-items: center;
  padding: 0.55rem 0.75rem;
  background: var(--glass-bg-primary);
  border-radius: 8px;
  font-size: 0.82rem;
}

.proc-name { font-weight: 600; color: var(--text-primary); }
.proc-pid { color: var(--text-tertiary); font-size: 0.75rem; }
.proc-cpu { font-weight: 600; }
.proc-cpu.normal { color: #10b981; }
.proc-cpu.warning { color: #f59e0b; }
.proc-cpu.critical { color: #ef4444; }
.proc-mem { color: var(--text-secondary); }

.no-data {
  text-align: center;
  padding: 2rem;
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

/* Alerts */
.alerts-section {
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.section-header {
  margin-bottom: 1rem;
}
.section-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1rem;
}
.section-header h2 i { margin-right: 0.5rem; opacity: 0.6; }

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.85rem;
}
.alert-item.warning { background: rgba(245, 158, 11, 0.08); color: #f59e0b; }
.alert-item.critical { background: rgba(239, 68, 68, 0.08); color: #ef4444; }

.alert-msg { flex: 1; color: var(--text-primary); }

.dismiss-btn {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}
.dismiss-btn:hover { color: var(--text-primary); }

/* Responsive */
@media (max-width: 1024px) {
  .overview-cards { grid-template-columns: repeat(2, 1fr); }
  .dashboard-grid { grid-template-columns: 1fr; }
  .cpu-card { grid-column: span 1; }
  .ups-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 640px) {
  .performance { padding: 1rem; }
  .overview-cards { grid-template-columns: 1fr 1fr; }
  .cores-grid { grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); }
  .mem-visual { flex-direction: column; }
  .ups-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
