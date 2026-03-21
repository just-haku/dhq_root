<template>
  <div class="op-config-dashboard">
    <div class="dashboard-header">
      <h2>🔧 OP Configuration Center</h2>
      <p class="subtitle">Manage all system configurations and settings</p>
      
      <!-- Test Mode Toggle -->
      <div class="test-mode-toggle">
        <label class="toggle-switch">
          <input 
            type="checkbox" 
            v-model="testModeEnabled" 
            @change="toggleTestMode"
          >
          <span class="slider"></span>
        </label>
        <span class="toggle-label">
          {{ testModeEnabled ? '🧪 Test Mode ON' : '🔧 Production Mode' }}
        </span>
        <small v-if="testModeEnabled" class="test-mode-hint">
          API calls route to local backend (haku.io.vn:8000)
        </small>
      </div>
    </div>

    <!-- Configuration Tabs -->
    <div class="config-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab-button"
        :class="{ 'active': activeTab === tab.id }"
      >
        <i :class="tab.icon"></i>
        {{ tab.name }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- API Endpoints Configuration -->
      <div v-if="activeTab === 'api-endpoints'" class="config-section">
        <APIEndpointsConfig />
      </div>

      <!-- Test API Configuration -->
      <div v-if="activeTab === 'test-api'" class="config-section">
        <APITestConfig />
      </div>

      <!-- User Management Configuration -->
      <div v-if="activeTab === 'users'" class="config-section">
        <UserManagementConfig />
      </div>

      <!-- System Configuration -->
      <div v-if="activeTab === 'system'" class="config-section">
        <SystemConfig />
      </div>

      <!-- Monitoring Configuration -->
      <div v-if="activeTab === 'monitoring'" class="config-section">
        <MonitoringConfig />
      </div>

      <!-- Ordering Configuration -->
      <div v-if="activeTab === 'ordering'" class="config-section">
        <OrderingConfig />
      </div>

      <!-- Timezone Configuration -->
      <div v-if="activeTab === 'timezone'" class="config-section">
        <TimezoneConfig />
      </div>
    </div>
  </div>
</template>

<style scoped>
.op-config-dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h2 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.subtitle {
  color: #7f8c8d;
  margin: 0;
}

.test-mode-toggle {
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #2196F3;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.toggle-label {
  font-weight: 600;
  color: #2c3e50;
}

.test-mode-hint {
  color: #7f8c8d;
  font-size: 12px;
  margin-left: auto;
}

.config-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 30px;
  border-bottom: 2px solid #e1e8ed;
  overflow-x: auto;
}

.tab-button {
  padding: 12px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #7f8c8d;
  transition: all 0.2s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-button:hover {
  color: #3498db;
}

.tab-button.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.tab-button i {
  font-size: 16px;
}

.tab-content {
  min-height: 600px;
}

.config-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e1e8ed;
}

@media (max-width: 768px) {
  .config-tabs {
    flex-wrap: nowrap;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .tab-button {
    padding: 10px 16px;
    font-size: 12px;
  }
}
</style>

<script>
import { ref, onMounted } from 'vue'
import { apiGet, apiPost, apiPut } from '../../utils/api.js'
import APIEndpointsConfig from './config/APIEndpointsConfig.vue'
import APITestConfig from './config/APITestConfig.vue'
import UserManagementConfig from './config/UserManagementConfig.vue'
import SystemConfig from './config/SystemConfig.vue'
import MonitoringConfig from './config/MonitoringConfig.vue'
import OrderingConfig from './config/OrderingConfig.vue'
import TimezoneConfig from './config/TimezoneConfig.vue'

export default {
  name: 'OPConfigDashboard',
  components: {
    APIEndpointsConfig,
    APITestConfig,
    UserManagementConfig,
    SystemConfig,
    MonitoringConfig,
    OrderingConfig,
    TimezoneConfig
  },
  
  setup() {
    const activeTab = ref('api-endpoints')
    const testModeEnabled = ref(false)
    const loading = ref(false)
    
    const tabs = [
      { id: 'api-endpoints', name: 'API Endpoints', icon: 'fas fa-plug' },
      { id: 'test-api', name: 'Test API', icon: 'fas fa-flask' },
      { id: 'users', name: 'Users', icon: 'fas fa-users' },
      { id: 'system', name: 'System', icon: 'fas fa-server' },
      { id: 'monitoring', name: 'Monitoring', icon: 'fas fa-chart-line' },
      { id: 'ordering', name: 'Ordering', icon: 'fas fa-shopping-cart' },
      { id: 'timezone', name: 'Timezone', icon: 'fas fa-globe' }
    ]
    
    const toggleTestMode = async () => {
      // Temporarily disabled - backend endpoint not implemented
      console.log('Test mode toggle temporarily disabled')
      return
    }
    
    onMounted(() => {
      // Load initial configuration
    })
    
    return {
      activeTab,
      testModeEnabled,
      loading,
      tabs,
      toggleTestMode
    }
  }
}
</script>
