<template>
  <div class="api-endpoints-config">
    <div class="section-header">
      <h3>🔌 API Endpoints Configuration</h3>
      <button @click="showCreateModal = true" class="btn btn-primary" :disabled="loading">
        <i class="fas fa-plus"></i> New Endpoint
      </button>
    </div>

    <div v-if="endpoints.length === 0 && !loading" class="empty-state">
      <i class="fas fa-plug"></i>
      <p>No API endpoints configured</p>
      <button @click="showCreateModal = true" class="btn btn-outline">
        Create First Endpoint
      </button>
    </div>

    <div v-else class="endpoints-grid">
      <div 
        v-for="endpoint in endpoints" 
        :key="endpoint.id"
        class="endpoint-card"
        :class="{ 'active': endpoint.is_active, 'public': endpoint.is_public }"
      >
        <div class="endpoint-header">
          <h4>{{ endpoint.name }}</h4>
          <div class="endpoint-status">
            <span class="status-badge" :class="endpoint.is_active ? 'active' : 'inactive'">
              {{ endpoint.is_active ? 'Active' : 'Inactive' }}
            </span>
            <span v-if="endpoint.is_public" class="badge badge-public">Public</span>
          </div>
        </div>
        
        <p class="endpoint-description">{{ endpoint.description || 'No description' }}</p>
        
        <div class="endpoint-details">
          <div class="detail-item">
            <label>URL:</label>
            <span class="url-text">{{ endpoint.endpoint_url }}</span>
          </div>
          <div class="detail-item">
            <label>Method:</label>
            <span class="method-badge" :class="endpoint.method.toLowerCase()">
              {{ endpoint.method }}
            </span>
          </div>
          <div class="detail-item">
            <label>Auth:</label>
            <span>{{ endpoint.auth_type }}</span>
          </div>
          <div class="detail-item">
            <label>Cost:</label>
            <span>{{ endpoint.cost_kpi }} KPI / ${{ endpoint.cost_currency }}</span>
          </div>
        </div>

        <div class="endpoint-actions">
          <button 
            @click="toggleEndpoint(endpoint)"
            class="btn btn-sm"
            :class="endpoint.is_active ? 'btn-warning' : 'btn-success'"
            :disabled="loading"
          >
            {{ endpoint.is_active ? 'Disable' : 'Enable' }}
          </button>
          <button 
            @click="editEndpoint(endpoint)"
            class="btn btn-sm btn-outline"
            :disabled="loading"
          >
            <i class="fas fa-edit"></i> Edit
          </button>
          <button 
            @click="deleteEndpoint(endpoint)"
            class="btn btn-sm btn-danger"
            :disabled="loading"
          >
            <i class="fas fa-trash"></i> Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingEndpoint" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingEndpoint ? 'Edit API Endpoint' : 'Create API Endpoint' }}</h3>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="saveEndpoint" class="endpoint-form">
          <div class="form-group">
            <label>Name *</label>
            <input 
              v-model="formData.name" 
              type="text" 
              required 
              class="form-control"
              placeholder="e.g., SMM API Service"
            />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="formData.description" 
              class="form-control"
              rows="3"
              placeholder="Describe this API endpoint"
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Endpoint URL *</label>
              <input 
                v-model="formData.endpoint_url" 
                type="url" 
                required
                class="form-control"
                placeholder="https://api.example.com/v2"
              />
            </div>
            <div class="form-group">
              <label>Method</label>
              <select v-model="formData.method" class="form-control">
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Auth Type</label>
              <select v-model="formData.auth_type" class="form-control">
                <option value="NONE">None</option>
                <option value="API_KEY">API Key</option>
                <option value="BEARER_TOKEN">Bearer Token</option>
                <option value="BASIC_AUTH">Basic Auth</option>
              </select>
            </div>
            <div class="form-group">
              <label>API Key</label>
              <input 
                v-model="formData.api_key" 
                type="password" 
                class="form-control"
                placeholder="API key for authentication"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>KPI Cost</label>
              <input 
                v-model.number="formData.cost_kpi" 
                type="number" 
                min="0"
                class="form-control"
                placeholder="0"
              />
            </div>
            <div class="form-group">
              <label>Currency Cost</label>
              <input 
                v-model.number="formData.cost_currency" 
                type="number" 
                min="0" 
                step="0.01"
                class="form-control"
                placeholder="0.00"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>
                <input v-model="formData.is_active" type="checkbox" />
                Active
              </label>
            </div>
            <div class="form-group">
              <label>
                <input v-model="formData.is_public" type="checkbox" />
                Public (Available to all users)
              </label>
            </div>
          </div>

          <!-- Advanced Configuration -->
          <div class="form-section">
            <h4>Advanced Configuration</h4>
            
            <div class="form-group">
              <label>Custom Headers (JSON)</label>
              <textarea 
                v-model="jsonHeaders" 
                class="form-control code-editor"
                rows="3"
                placeholder='{"Authorization": "Bearer token"}'
              ></textarea>
            </div>

            <div class="form-group">
              <label>Request Template (JSON)</label>
              <textarea 
                v-model="jsonRequestTemplate" 
                class="form-control code-editor"
                rows="4"
                placeholder='{"key": "{api_key}", "action": "add"}'
              ></textarea>
            </div>

            <div class="form-group">
              <label>Success Criteria (JSON)</label>
              <textarea 
                v-model="jsonSuccessCriteria" 
                class="form-control code-editor"
                rows="3"
                placeholder='{"status_code": [200, 201]}'
              ></textarea>
            </div>

            <div class="form-group">
              <label>Response Mapping (JSON)</label>
              <textarea 
                v-model="jsonResponseMapping" 
                class="form-control code-editor"
                rows="3"
                placeholder='{"order_id": "response.order"}'
              ></textarea>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-outline">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ editingEndpoint ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '../../../utils/api.js'

export default {
  name: 'APIEndpointsConfig',
  setup() {
    // State
    const endpoints = ref([])
    const loading = ref(false)
    const showCreateModal = ref(false)
    const editingEndpoint = ref(null)
    
    // Form data
    const formData = reactive({
      name: '',
      description: '',
      endpoint_url: '',
      method: 'POST',
      auth_type: 'API_KEY',
      api_key: '',
      headers: {},
      request_template: {},
      success_criteria: {},
      response_mapping: {},
      cost_kpi: 0,
      cost_currency: 0.0,
      is_active: true,
      is_public: false
    })

    // Computed
    const jsonHeaders = computed({
      get: () => JSON.stringify(formData.headers, null, 2),
      set: (value) => {
        try {
          formData.headers = JSON.parse(value)
        } catch (e) {
          console.error('Invalid JSON:', e)
        }
      }
    })

    const jsonRequestTemplate = computed({
      get: () => JSON.stringify(formData.request_template, null, 2),
      set: (value) => {
        try {
          formData.request_template = JSON.parse(value)
        } catch (e) {
          console.error('Invalid JSON:', e)
        }
      }
    })

    const jsonSuccessCriteria = computed({
      get: () => JSON.stringify(formData.success_criteria, null, 2),
      set: (value) => {
        try {
          formData.success_criteria = JSON.parse(value)
        } catch (e) {
          console.error('Invalid JSON:', e)
        }
      }
    })

    const jsonResponseMapping = computed({
      get: () => JSON.stringify(formData.response_mapping, null, 2),
      set: (value) => {
        try {
          formData.response_mapping = JSON.parse(value)
        } catch (e) {
          console.error('Invalid JSON:', e)
        }
      }
    })

    // Methods
    const fetchEndpoints = async () => {
      try {
        loading.value = true
        const data = await apiGet('/api/ordering/endpoints')
        endpoints.value = data.endpoints
      } catch (error) {
        console.error('Error fetching endpoints:', error)
      } finally {
        loading.value = false
      }
    }

    const saveEndpoint = async () => {
      try {
        loading.value = true
        
        const url = editingEndpoint.value 
          ? `/api/ordering/endpoints/${editingEndpoint.value.id}`
          : '/api/ordering/endpoints'
        
        if (editingEndpoint.value) {
          await apiPut(url, formData)
        } else {
          await apiPost(url, formData)
        }
        
        await fetchEndpoints()
        closeModal()
      } catch (error) {
        console.error('Error saving endpoint:', error)
      } finally {
        loading.value = false
      }
    }

    const toggleEndpoint = async (endpoint) => {
      try {
        loading.value = true
        await apiPut(`/api/ordering/endpoints/${endpoint.id}`, { is_active: !endpoint.is_active })
        await fetchEndpoints()
      } catch (error) {
        console.error('Error toggling endpoint:', error)
      } finally {
        loading.value = false
      }
    }

    const editEndpoint = (endpoint) => {
      editingEndpoint.value = endpoint
      Object.assign(formData, {
        ...endpoint,
        headers: endpoint.headers || {},
        request_template: endpoint.request_template || {},
        success_criteria: endpoint.success_criteria || {},
        response_mapping: endpoint.response_mapping || {}
      })
    }

    const deleteEndpoint = async (endpoint) => {
      if (!confirm(`Are you sure you want to delete "${endpoint.name}"?`)) {
        return
      }
      
      try {
        loading.value = true
        await apiDelete(`/api/ordering/endpoints/${endpoint.id}`)
        await fetchEndpoints()
      } catch (error) {
        console.error('Error deleting endpoint:', error)
      } finally {
        loading.value = false
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      editingEndpoint.value = null
      
      // Reset form
      Object.assign(formData, {
        name: '',
        description: '',
        endpoint_url: '',
        method: 'POST',
        auth_type: 'API_KEY',
        api_key: '',
        headers: {},
        request_template: {},
        success_criteria: {},
        response_mapping: {},
        cost_kpi: 0,
        cost_currency: 0.0,
        is_active: true,
        is_public: false
      })
    }

    // Lifecycle
    onMounted(() => {
      fetchEndpoints()
    })

    return {
      endpoints,
      loading,
      showCreateModal,
      editingEndpoint,
      formData,
      jsonHeaders,
      jsonRequestTemplate,
      jsonSuccessCriteria,
      jsonResponseMapping,
      saveEndpoint,
      toggleEndpoint,
      editEndpoint,
      deleteEndpoint,
      closeModal
    }
  }
}
</script>

<style scoped>
.api-endpoints-config {
  width: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #34495e;
}

.endpoints-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 20px;
}

.endpoint-card {
  background: #f8f9fa;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s ease;
}

.endpoint-card.active {
  border-color: #27ae60;
  background: #d4edda;
}

.endpoint-card.public {
  border-left: 4px solid #3498db;
}

.endpoint-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.endpoint-header h4 {
  margin: 0;
  color: #2c3e50;
}

.endpoint-status {
  display: flex;
  gap: 8px;
  align-items: center;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-public {
  background: #d1ecf1;
  color: #0c5460;
}

.endpoint-description {
  color: #7f8c8d;
  margin-bottom: 16px;
  font-size: 14px;
}

.endpoint-details {
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
  min-width: 80px;
}

.url-text {
  font-family: monospace;
  font-size: 12px;
  word-break: break-all;
}

.method-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.method-badge.get {
  background: #e3f2fd;
  color: #1976d2;
}

.method-badge.post {
  background: #e8f5e8;
  color: #388e3c;
}

.method-badge.put {
  background: #fff3e0;
  color: #f57c00;
}

.method-badge.delete {
  background: #ffebee;
  color: #d32f2f;
}

.endpoint-actions {
  display: flex;
  gap: 8px;
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
  max-width: 700px;
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

.endpoint-form {
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
  .endpoints-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .endpoint-actions {
    flex-direction: column;
  }
}
</style>
