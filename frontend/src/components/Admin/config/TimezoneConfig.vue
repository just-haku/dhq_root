<template>
  <div class="timezone-config">
    <div class="config-header">
      <h3>🌍 Timezone Configuration</h3>
      <p>Set the default timezone for all scheduling and time-based operations</p>
    </div>

    <div class="config-content">
      <!-- Current Timezone Display -->
      <div class="current-timezone">
        <div class="info-card">
          <h4>Current Timezone</h4>
          <div class="timezone-display">
            <span class="timezone-name">{{ currentTimezone }}</span>
            <span class="timezone-offset">{{ currentTimezoneOffset }}</span>
          </div>
          <div class="current-time">
            Current Server Time: {{ formatDateTime(currentServerTime) }}
          </div>
        </div>
      </div>

      <!-- Timezone Selection -->
      <div class="timezone-selection">
        <div class="form-group">
          <label for="timezone-select">Select Timezone:</label>
          <select 
            id="timezone-select"
            v-model="selectedTimezone"
            @change="updateTimezone"
            class="timezone-select"
          >
            <option value="">Select timezone...</option>
            <option 
              v-for="tz in availableTimezones" 
              :key="tz.value"
              :value="tz.value"
              :selected="tz.value === selectedTimezone"
            >
              {{ tz.label }} ({{ tz.value }})
            </option>
          </select>
        </div>

        <div class="timezone-info">
          <div class="info-item">
            <strong>GMT+7</strong> - Southeast Asia (Bangkok, Hanoi, Jakarta)
          </div>
          <div class="info-item">
            <strong>UTC</strong> - Coordinated Universal Time
          </div>
          <div class="info-item">
            <strong>GMT-5</strong> - Eastern Time (New York, Toronto)
          </div>
        </div>
      </div>

      <!-- Auto Sub-order Placement -->
      <div class="auto-order-section">
        <div class="form-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="autoOrderEnabled"
              @change="toggleAutoOrder"
            />
            <span class="checkmark"></span>
            Enable Auto Sub-order Placement
          </label>
          <p class="description">
            Automatically places sub-orders when their scheduled time arrives.
            This ensures orders start exactly on time without manual intervention.
          </p>
        </div>

        <div v-if="autoOrderEnabled" class="auto-order-status">
          <div class="status-indicator" :class="{ 'active': autoOrderActive }">
            <span class="status-dot"></span>
            {{ autoOrderActive ? 'Auto-placement Active' : 'Auto-placement Idle' }}
          </div>
          <div class="last-check">
            Last check: {{ formatDateTime(lastAutoCheck) }}
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="saveTimezone" class="btn btn-primary" :disabled="saving">
          <i class="fas fa-save"></i>
          {{ saving ? 'Saving...' : 'Save Timezone' }}
        </button>
        <button @click="testTimezone" class="btn btn-secondary">
          <i class="fas fa-clock"></i>
          Test Current Time
        </button>
        <button @click="resetToDefault" class="btn btn-outline">
          <i class="fas fa-undo"></i>
          Reset to GMT+7
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiGet, apiPost } from '../../../utils/api.js'

export default {
  name: 'TimezoneConfig',
  setup() {
    const selectedTimezone = ref('UTC')
    const currentTimezone = ref('UTC')
    const currentTimezoneOffset = ref('+00:00')
    const currentServerTime = ref(new Date())
    const autoOrderEnabled = ref(false)
    const autoOrderActive = ref(false)
    const lastAutoCheck = ref(new Date())
    const saving = ref(false)

    const availableTimezones = [
      { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
      { value: 'GMT+7', label: 'GMT+7 (Southeast Asia)' },
      { value: 'GMT+8', label: 'GMT+8 (China, Taiwan)' },
      { value: 'GMT+5', label: 'GMT+5 (Eastern Time)' },
      { value: 'GMT-8', label: 'GMT-8 (Pacific Time)' },
      { value: 'GMT+0', label: 'GMT+0 (London, Lisbon)' },
      { value: 'GMT+1', label: 'GMT+1 (Central European)' },
      { value: 'GMT+2', label: 'GMT+2 (Eastern European)' },
      { value: 'GMT-5', label: 'GMT-5 (Eastern Standard)' },
      { value: 'GMT+3', label: 'GMT+3 (Moscow, Istanbul)' },
      { value: 'GMT+9', label: 'GMT+9 (Japan, Korea)' },
      { value: 'GMT+10', label: 'GMT+10 (Australia East)' }
    ]

    let autoOrderInterval = null

    const formatDateTime = (date) => {
      return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: selectedTimezone.value === 'UTC' ? 'UTC' : undefined
      })
    }

    const updateTimezoneDisplay = () => {
      const tz = selectedTimezone.value
      currentTimezone.value = tz
      currentTimezoneOffset.value = tz.replace('GMT', '')
      
      // Update current server time with selected timezone
      const now = new Date()
      if (tz !== 'UTC') {
        // Simple offset calculation for display
        const offset = parseInt(tz.replace('GMT', ''))
        const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000)
        currentServerTime.value = new Date(utcTime + (offset * 3600000))
      } else {
        currentServerTime.value = now
      }
    }

    const loadTimezoneConfig = async () => {
      try {
        const response = await apiGet('/admin/timezone-config')
        if (response.success) {
          selectedTimezone.value = response.config.timezone || 'GMT+7'
          autoOrderEnabled.value = response.config.auto_order_enabled || false
          updateTimezoneDisplay()
        }
      } catch (error) {
        console.error('Failed to load timezone config:', error)
      }
    }

    const saveTimezone = async () => {
      saving.value = true
      try {
        const response = await apiPost('/admin/timezone-config', {
          timezone: selectedTimezone.value,
          auto_order_enabled: autoOrderEnabled.value
        })

        if (response.success) {
          updateTimezoneDisplay()
          // Show success message
          alert('Timezone configuration saved successfully!')
        } else {
          alert('Failed to save timezone configuration')
        }
      } catch (error) {
        console.error('Failed to save timezone config:', error)
        alert('Error saving timezone configuration')
      } finally {
        saving.value = false
      }
    }

    const updateTimezone = () => {
      updateTimezoneDisplay()
    }

    const toggleAutoOrder = async () => {
      try {
        const response = await apiPost('/admin/auto-order-toggle', {
          enabled: autoOrderEnabled.value
        })

        if (response.success) {
          autoOrderActive.value = response.active
          lastAutoCheck.value = new Date()
        }
      } catch (error) {
        console.error('Failed to toggle auto-order:', error)
        autoOrderEnabled.value = !autoOrderEnabled.value // Revert on error
      }
    }

    const testTimezone = () => {
      const testTime = new Date()
      alert(`Current server time: ${formatDateTime(testTime)}\nSelected timezone: ${currentTimezone.value}`)
    }

    const resetToDefault = () => {
      selectedTimezone.value = 'GMT+7'
      updateTimezoneDisplay()
    }

    // Auto-order checker
    const startAutoOrderChecker = () => {
      if (autoOrderEnabled.value) {
        autoOrderInterval = setInterval(async () => {
          try {
            const response = await apiGet('/admin/auto-order-status')
            if (response.success) {
              autoOrderActive.value = response.active
              lastAutoCheck.value = new Date()
            }
          } catch (error) {
            console.error('Auto-order check failed:', error)
          }
        }, 30000) // Check every 30 seconds
      }
    }

    const stopAutoOrderChecker = () => {
      if (autoOrderInterval) {
        clearInterval(autoOrderInterval)
        autoOrderInterval = null
      }
    }

    onMounted(async () => {
      await loadTimezoneConfig()
      updateTimezoneDisplay()
      startAutoOrderChecker()
    })

    onUnmounted(() => {
      stopAutoOrderChecker()
    })

    return {
      selectedTimezone,
      currentTimezone,
      currentTimezoneOffset,
      currentServerTime,
      autoOrderEnabled,
      autoOrderActive,
      lastAutoCheck,
      saving,
      availableTimezones,
      formatDateTime,
      updateTimezone,
      saveTimezone,
      toggleAutoOrder,
      testTimezone,
      resetToDefault
    }
  }
}
</script>

<style scoped>
.timezone-config {
  padding: 20px;
}

.config-header {
  margin-bottom: 30px;
}

.config-header h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.config-header p {
  margin: 0 0 20px 0;
  color: #7f8c8d;
  line-height: 1.5;
}

.config-content {
  display: grid;
  gap: 30px;
}

.current-timezone {
  grid-column: 1;
}

.info-card {
  background: #f8f9fa;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
}

.info-card h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.timezone-display {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.timezone-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #3498db;
  padding: 8px 12px;
  background: #e3f2fd;
  border-radius: 6px;
}

.timezone-offset {
  font-size: 0.9rem;
  color: #7f8c8d;
  font-family: monospace;
}

.current-time {
  font-size: 0.9rem;
  color: #28a745;
}

.timezone-selection {
  grid-column: 1;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.timezone-select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e8ed;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
}

.timezone-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.timezone-info {
  margin-top: 20px;
  padding: 15px;
  background: #fff3cd;
  border-radius: 6px;
  border-left: 4px solid #ffc107;
}

.info-item {
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.info-item strong {
  color: #2c3e50;
}

.auto-order-section {
  grid-column: 1;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
}

.checkmark {
  position: relative;
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #ccc;
  border-radius: 4px;
  margin-right: 10px;
}

.checkbox-label input:checked + .checkmark {
  background-color: #3498db;
  border-color: #3498db;
}

.checkbox-label input:checked + .checkmark:after {
  content: "";
  position: absolute;
  display: block;
  left: 6px;
  top: 2px;
  width: 6px;
  height: 12px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.description {
  margin: 0;
  padding: 10px 0 0 30px;
  color: #7f8c8d;
  font-size: 0.9rem;
  line-height: 1.4;
}

.auto-order-status {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e1e8ed;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #dc3545;
}

.status-indicator.active .status-dot {
  background: #28a745;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.last-check {
  font-size: 0.8rem;
  color: #7f8c8d;
  font-style: italic;
}

.action-buttons {
  grid-column: 1 / -1;
  grid-row: 1 / -1;
  display: flex;
  gap: 15px;
  justify-content: flex-start;
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: #3498db;
  border: 2px solid #3498db;
}

.btn-outline:hover:not(:disabled) {
  background: #3498db;
  color: white;
  transform: translateY(-2px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .config-content {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-column: 1;
    grid-row: auto;
    flex-wrap: wrap;
  }
}
</style>
