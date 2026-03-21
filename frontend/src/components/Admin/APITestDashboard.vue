<template>
  <div class="api-test-dashboard">
    <div class="dashboard-header">
      <h2>API Test Dashboard</h2>
      <p class="subtitle">Manage test API endpoints and monitor activity</p>
    </div>

    <!-- Configuration Section -->
    <div class="config-section">
      <div class="section-header">
        <h3>Test API Configuration</h3>
        <button 
          @click="showCreateModal = true" 
          class="btn btn-primary"
          :disabled="loading"
        >
          <i class="fas fa-plus"></i> New Configuration
        </button>
      </div>

      <div v-if="configs.length === 0 && !loading" class="empty-state">
        <i class="fas fa-cog"></i>
        <p>No test API configurations found</p>
        <button @click="showCreateModal = true" class="btn btn-outline">
          Create First Configuration
        </button>
      </div>

      <div v-else class="configs-grid">
        <div 
          v-for="config in configs" 
          :key="config.id"
          class="config-card"
          :class="{ 'active': config.is_enabled }"
        >
          <div class="config-header">
            <h4>{{ config.name }}</h4>
            <div class="config-status">
              <span 
                class="status-badge"
                :class="config.is_enabled ? 'enabled' : 'disabled'"
              >
                {{ config.is_enabled ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
          </div>
          
          <p class="config-description">{{ config.description || 'No description' }}</p>
          
          <div class="config-details">
            <div class="detail-item">
              <label>Mode:</label>
              <span>{{ config.mock_responses ? 'Mock Responses' : 'Real API' }}</span>
            </div>
            <div class="detail-item">
              <label>Growth Orders:</label>
              <span>{{ config.intercept_growth_orders ? 'Intercepted' : 'Normal' }}</span>
            </div>
            <div class="detail-item">
              <label>Response Delay:</label>
              <span>{{ config.response_delay_ms }}ms</span>
            </div>
            <div class="detail-item">
              <label>Failure Rate:</label>
              <span>{{ config.failure_rate_percent }}%</span>
            </div>
            <div class="detail-item">
              <label>Logging:</label>
              <span>{{ config.log_requests ? 'Enabled' : 'Disabled' }}</span>
            </div>
          </div>

          <div class="config-actions">
            <button 
              @click="toggleConfig(config)"
              class="btn btn-sm"
              :class="config.is_enabled ? 'btn-warning' : 'btn-success'"
              :disabled="loading"
            >
              {{ config.is_enabled ? 'Disable' : 'Enable' }}
            </button>
            <button 
              @click="editConfig(config)"
              class="btn btn-sm btn-outline"
              :disabled="loading"
            >
              <i class="fas fa-edit"></i> Edit
            </button>
            <button 
              @click="deleteConfig(config)"
              class="btn btn-sm btn-danger"
              :disabled="loading"
            >
              <i class="fas fa-trash"></i> Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Section -->
    <div class="stats-section">
      <h3>API Statistics</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_requests }}</div>
          <div class="stat-label">Total Requests</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.test_requests }}</div>
          <div class="stat-label">Test Requests</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.recent_requests_24h }}</div>
          <div class="stat-label">Last 24 Hours</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.success_rate_percent }}%</div>
          <div class="stat-label">Success Rate</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.avg_response_time_ms }}ms</div>
          <div class="stat-label">Avg Response Time</div>
        </div>
      </div>
    </div>

    <!-- Logs Section -->
    <div class="logs-section">
      <div class="section-header">
        <h3>API Logs</h3>
        <div class="logs-controls">
          <select v-model="logFilters.endpoint_name" class="filter-select">
            <option value="">All Endpoints</option>
            <option v-for="config in configs" :key="config.id" :value="config.name">
              {{ config.name }}
            </option>
          </select>
          <button @click="refreshLogs" class="btn btn-outline" :disabled="loading">
            <i class="fas fa-refresh"></i> Refresh
          </button>
          <button @click="clearLogs" class="btn btn-danger" :disabled="loading">
            <i class="fas fa-trash"></i> Clear Old Logs
          </button>
        </div>
      </div>

      <div class="logs-table">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Endpoint</th>
              <th>User</th>
              <th>Action</th>
              <th>Status</th>
              <th>Duration</th>
              <th>Test Mode</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td>{{ formatTimestamp(log.request_timestamp) }}</td>
              <td>{{ log.endpoint_name }}</td>
              <td>{{ log.user_id ? 'User ' + log.user_id.slice(-8) : 'System' }}</td>
              <td>{{ log.request_body?.action || 'Unknown' }}</td>
              <td>
                <span 
                  class="status-badge"
                  :class="log.response_status === 200 ? 'success' : 'error'"
                >
                  {{ log.response_status }}
                </span>
              </td>
              <td>{{ Math.round(log.duration_ms || 0) }}ms</td>
              <td>
                <span class="badge" :class="log.is_test_mode ? 'badge-test' : 'badge-real'">
                  {{ log.is_test_mode ? 'Test' : 'Real' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="logs.length === 0 && !loading" class="empty-state">
          <i class="fas fa-clipboard-list"></i>
          <p>No API logs found</p>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingConfig" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingConfig ? 'Edit Configuration' : 'Create Configuration' }}</h3>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="saveConfig" class="config-form">
          <div class="form-group">
            <label>Name *</label>
            <input 
              v-model="formData.name" 
              type="text" 
              required 
              class="form-control"
              placeholder="e.g., SMM API Test"
            />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="formData.description" 
              class="form-control"
              rows="3"
              placeholder="Describe this test configuration"
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>
                <input 
                  v-model="formData.is_enabled" 
                  type="checkbox"
                />
                Enable Configuration
              </label>
            </div>
            <div class="form-group">
              <label>
                <input 
                  v-model="formData.mock_responses" 
                  type="checkbox"
                />
                Use Mock Responses
              </label>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>
                <input 
                  v-model="formData.intercept_growth_orders" 
                  type="checkbox"
                />
                Intercept Channel Growth Orders
              </label>
            </div>
            <div class="form-group">
              <small class="text-muted">
                When enabled, all Channel Growth API calls will be routed through this test endpoint
              </small>
            </div>
          </div>

          <div v-if="!formData.mock_responses" class="form-group">
            <label>Real API URL</label>
            <input 
              v-model="formData.real_api_url" 
              type="url" 
              class="form-control"
              placeholder="https://api.example.com/v2"
            />
          </div>

          <div v-if="!formData.mock_responses" class="form-group">
            <label>Real API Key</label>
            <input 
              v-model="formData.real_api_key" 
              type="password" 
              class="form-control"
              placeholder="API key for real endpoint"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Response Delay (ms)</label>
              <input 
                v-model.number="formData.response_delay_ms" 
                type="number" 
                min="0"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>Failure Rate (%)</label>
              <input 
                v-model.number="formData.failure_rate_percent" 
                type="number" 
                min="0" 
                max="100"
                class="form-control"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>
                <input 
                  v-model="formData.log_requests" 
                  type="checkbox"
                />
                Log Requests
              </label>
            </div>
            <div class="form-group">
              <label>
                <input 
                  v-model="formData.log_responses" 
                  type="checkbox"
                />
                Log Responses
              </label>
            </div>
          </div>

          <!-- Advanced Templates -->
          <div class="form-section">
            <h4>Response Templates</h4>
            
            <div class="form-group">
              <label>Success Response (JSON)</label>
              <textarea 
                v-model="jsonSuccessResponse" 
                class="form-control code-editor"
                rows="3"
                placeholder='{"order": 99999}'
              ></textarea>
            </div>

            <div class="form-group">
              <label>Error Response (JSON)</label>
              <textarea 
                v-model="jsonErrorResponse" 
                class="form-control code-editor"
                rows="3"
                placeholder='{"error": "Test error message"}'
              ></textarea>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-outline">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ editingConfig ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '../../utils/api.js'

export default {
  name: 'APITestDashboard',
  setup() {
    // State
    const configs = ref([])
    const logs = ref([])
    const stats = ref({})
    const loading = ref(false)
    const showCreateModal = ref(false)
    const editingConfig = ref(null)
    
    // Form data
    const formData = reactive({
      name: '',
      description: '',
      is_enabled: false,
      mock_responses: true,
      intercept_growth_orders: false,
      real_api_url: '',
      real_api_key: '',
      success_response: { order: 99999 },
      error_response: { error: 'Test error message' },
      response_delay_ms: 1000,
      failure_rate_percent: 0,
      log_requests: true,
      log_responses: true
    })

    const logFilters = reactive({
      endpoint_name: ''
    })

    // Computed
    const jsonSuccessResponse = computed({
      get: () => JSON.stringify(formData.success_response, null, 2),
      set: (value) => {
        try {
          formData.success_response = JSON.parse(value)
        } catch (e) {
          console.error('Invalid JSON:', e)
        }
      }
    })

    const jsonErrorResponse = computed({
      get: () => JSON.stringify(formData.error_response, null, 2),
      set: (value) => {
        try {
          formData.error_response = JSON.parse(value)
        } catch (e) {
          console.error('Invalid JSON:', e)
        }
      }
    })

    // Methods
    const fetchConfigs = async () => {
      try {
        loading.value = true
        const data = await apiGet('/api/test-configs')
        configs.value = data.configs
      } catch (error) {
        console.error('Error fetching configs:', error)
      } finally {
        loading.value = false
      }
    }

    const fetchLogs = async () => {
      try {
        loading.value = true
        const params = new URLSearchParams()
        if (logFilters.endpoint_name) {
          params.append('endpoint_name', logFilters.endpoint_name)
        }
        params.append('limit', '50')
        
        const data = await apiGet(`/api/logs?${params}`)
        logs.value = data.logs
      } catch (error) {
        console.error('Error fetching logs:', error)
      } finally {
        loading.value = false
      }
    }

    const fetchStats = async () => {
      try {
        const data = await apiGet('/api/logs/stats')
        stats.value = data
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    }

    const saveConfig = async () => {
      try {
        loading.value = true
        
        const url = editingConfig.value 
          ? `/api/test-configs/${editingConfig.value.id}`
          : '/api/test-configs'
        
        if (editingConfig.value) {
          await apiPut(url, formData)
        } else {
          await apiPost(url, formData)
        }
        
        await fetchConfigs()
        closeModal()
      } catch (error) {
        console.error('Error saving config:', error)
      } finally {
        loading.value = false
      }
    }

    const toggleConfig = async (config) => {
      try {
        loading.value = true
        await apiPut(`/api/test-configs/${config.id}`, { is_enabled: !config.is_enabled })
        await fetchConfigs()
      } catch (error) {
        console.error('Error toggling config:', error)
      } finally {
        loading.value = false
      }
    }

    const editConfig = (config) => {
      editingConfig.value = config
      Object.assign(formData, {
        ...config,
        success_response: config.success_response || { order: 99999 },
        error_response: config.error_response || { error: 'Test error message' }
      })
    }

    const deleteConfig = async (config) => {
      if (!confirm(`Are you sure you want to delete "${config.name}"?`)) {
        return
      }
      
      try {
        loading.value = true
        await apiDelete(`/api/test-configs/${config.id}`)
        await fetchConfigs()
      } catch (error) {
        console.error('Error deleting config:', error)
      } finally {
        loading.value = false
      }
    }

    const clearLogs = async () => {
      if (!confirm('Clear logs older than 24 hours?')) {
        return
      }
      
      try {
        loading.value = true
        await apiDelete('/api/logs/clear?older_than_hours=24')
        await fetchLogs()
        await fetchStats()
      } catch (error) {
        console.error('Error clearing logs:', error)
      } finally {
        loading.value = false
      }
    }

    const refreshLogs = () => {
      fetchLogs()
      fetchStats()
    }

    const closeModal = () => {
      showCreateModal.value = false
      editingConfig.value = null
      
      // Reset form
      Object.assign(formData, {
        name: '',
        description: '',
        is_enabled: false,
        mock_responses: true,
        intercept_growth_orders: false,
        real_api_url: '',
        real_api_key: '',
        success_response: { order: 99999 },
        error_response: { error: 'Test error message' },
        response_delay_ms: 1000,
        failure_rate_percent: 0,
        log_requests: true,
        log_responses: true
      })
    }

    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }

    // Lifecycle
    onMounted(() => {
      fetchConfigs()
      fetchLogs()
      fetchStats()
    })

    return {
      configs,
      logs,
      stats,
      loading,
      showCreateModal,
      editingConfig,
      formData,
      logFilters,
      jsonSuccessResponse,
      jsonErrorResponse,
      saveConfig,
      toggleConfig,
      editConfig,
      deleteConfig,
      clearLogs,
      refreshLogs,
      closeModal,
      formatTimestamp
    }
  }
}
</script>

<style scoped>
.api-test-dashboard {
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

.section-header {
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #34495e;
}

.configs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.config-card {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s ease;
}

.config-card.active {
  border-color: #27ae60;
  box-shadow: 0 0 0 2px rgba(39, 174, 96, 0.1);
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.config-header h4 {
  margin: 0;
  color: #2c3e50;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.enabled {
  background: #d4edda;
  color: #155724;
}

.status-badge.disabled {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.success {
  background: #d4edda;
  color: #155724;
}

.status-badge.error {
  background: #f8d7da;
  color: #721c24;
}

.config-description {
  color: #7f8c8d;
  margin-bottom: 16px;
  font-size: 14px;
}

.config-details {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item label {
  font-weight: 600;
  color: #34495e;
}

.config-actions {
  display: flex;
  gap: 8px;
}

.stats-section {
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 8px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 14px;
}

.logs-section {
  margin-bottom: 30px;
}

.logs-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.logs-table {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  overflow: hidden;
}

.logs-table table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th,
.logs-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e1e8ed;
}

.logs-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #34495e;
}

.logs-table tr:hover {
  background: #f8f9fa;
}

.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-test {
  background: #fff3cd;
  color: #856404;
}

.badge-real {
  background: #d1ecf1;
  color: #0c5460;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
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
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
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

.config-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group label {
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

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.code-editor {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
}

.form-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e1e8ed;
}

.form-section h4 {
  margin: 0 0 20px 0;
  color: #34495e;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e1e8ed;
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

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #229954;
}

.btn-warning {
  background: #f39c12;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #e67e22;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
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
  .configs-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .logs-controls {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
