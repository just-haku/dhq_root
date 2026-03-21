<template>
  <div class="ordering-config">
    <div class="section-header">
      <h3>🛒 Ordering Configuration</h3>
      <button @click="showCreateModal = true" class="btn btn-primary" :disabled="loading">
        <i class="fas fa-plus"></i> New Order Config
      </button>
    </div>

    <!-- Order Statistics -->
    <div class="stats-section">
      <h4>Order Statistics</h4>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ orderStats.total_orders }}</div>
          <div class="stat-label">Total Orders</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ orderStats.pending_orders }}</div>
          <div class="stat-label">Pending</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ orderStats.completed_orders }}</div>
          <div class="stat-label">Completed</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ orderStats.failed_orders }}</div>
          <div class="stat-label">Failed</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ orderStats.success_rate }}%</div>
          <div class="stat-label">Success Rate</div>
        </div>
      </div>
    </div>

    <!-- API Endpoints -->
    <div class="endpoints-section">
      <h4>API Endpoints</h4>
      <div class="endpoints-controls">
        <button @click="loadEndpoints" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-refresh"></i> Refresh
        </button>
        <select v-model="endpointFilter" class="filter-select">
          <option value="">All Endpoints</option>
          <option value="active">Active Only</option>
          <option value="public">Public Only</option>
          <option value="private">Private Only</option>
        </select>
      </div>
      
      <div class="endpoints-grid">
        <div 
          v-for="endpoint in filteredEndpoints" 
          :key="endpoint.id"
          class="endpoint-card"
          :class="{ 
            'active': endpoint.is_active, 
            'public': endpoint.is_public,
            'inactive': !endpoint.is_active 
          }"
        >
          <div class="endpoint-header">
            <h5>{{ endpoint.name }}</h5>
            <div class="endpoint-badges">
              <span class="status-badge" :class="endpoint.is_active ? 'active' : 'inactive'">
                {{ endpoint.is_active ? 'Active' : 'Inactive' }}
              </span>
              <span v-if="endpoint.is_public" class="badge badge-public">Public</span>
            </div>
          </div>
          
          <p class="endpoint-description">{{ endpoint.description || 'No description' }}</p>
          
          <div class="endpoint-details">
            <div class="detail-row">
              <span class="detail-label">URL:</span>
              <span class="detail-value">{{ endpoint.endpoint_url }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Method:</span>
              <span class="method-badge" :class="endpoint.method.toLowerCase()">
                {{ endpoint.method }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Cost:</span>
              <span>{{ endpoint.cost_kpi }} KPI / ${{ endpoint.cost_currency }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Auth:</span>
              <span>{{ endpoint.auth_type }}</span>
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
              <i class="fas fa-edit"></i>
            </button>
            <button 
              @click="viewOrders(endpoint)"
              class="btn btn-sm btn-outline"
              :disabled="loading"
            >
              <i class="fas fa-list"></i>
            </button>
            <button 
              @click="deleteEndpoint(endpoint)"
              class="btn btn-sm btn-danger"
              :disabled="loading"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Orders -->
    <div class="orders-section">
      <h4>Recent Orders</h4>
      <div class="orders-controls">
        <button @click="loadOrders" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-refresh"></i> Refresh
        </button>
        <select v-model="orderStatusFilter" class="filter-select">
          <option value="">All Status</option>
          <option value="PENDING">Pending</option>
          <option value="PROCESSING">Processing</option>
          <option value="COMPLETED">Completed</option>
          <option value="FAILED">Failed</option>
        </select>
      </div>
      
      <div class="orders-table">
        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Service</th>
              <th>User</th>
              <th>Status</th>
              <th>Cost</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in filteredOrders" :key="order.id">
              <td>
                <code>{{ order.id.slice(-8) }}</code>
              </td>
              <td>{{ order.service_name }}</td>
              <td>{{ order.user_id ? 'User ' + order.user_id.slice(-8) : 'System' }}</td>
              <td>
                <span class="status-badge" :class="order.status.toLowerCase()">
                  {{ order.status }}
                </span>
              </td>
              <td>{{ order.cost_kpi }} KPI</td>
              <td>{{ formatDate(order.created_at) }}</td>
              <td>
                <button 
                  @click="viewOrderDetails(order)"
                  class="btn btn-sm btn-outline"
                >
                  <i class="fas fa-eye"></i>
                </button>
                <button 
                  v-if="order.status === 'FAILED'"
                  @click="retryOrder(order)"
                  class="btn btn-sm btn-warning"
                >
                  <i class="fas fa-redo"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="filteredOrders.length === 0 && !loading" class="empty-state">
          <i class="fas fa-shopping-cart"></i>
          <p>No orders found</p>
        </div>
      </div>
    </div>

    <!-- Order Settings -->
    <div class="settings-section">
      <h4>Order Settings</h4>
      <div class="settings-grid">
        <div class="setting-item">
          <label>
            <input 
              v-model="orderSettings.auto_retry_failed" 
              type="checkbox"
              @change="updateOrderSettings"
            />
            Auto-retry Failed Orders
          </label>
          <p class="setting-description">
            Automatically retry orders that fail due to network errors
          </p>
        </div>
        
        <div class="setting-item">
          <label>
            <input 
              v-model="orderSettings.enable_order_queue" 
              type="checkbox"
              @change="updateOrderSettings"
            />
            Enable Order Queue
          </label>
          <p class="setting-description">
            Process orders in a queue to prevent API overload
          </p>
        </div>
        
        <div class="setting-item">
          <label>
            Max Concurrent Orders
          </label>
          <input 
            v-model.number="orderSettings.max_concurrent_orders" 
            type="number" 
            min="1" 
            max="100"
            class="form-control"
            @change="updateOrderSettings"
          />
          <p class="setting-description">
            Maximum number of orders to process simultaneously
          </p>
        </div>
        
        <div class="setting-item">
          <label>
            Order Timeout (minutes)
          </label>
          <input 
            v-model.number="orderSettings.order_timeout_minutes" 
            type="number" 
            min="1" 
            max="1440"
            class="form-control"
            @change="updateOrderSettings"
          />
          <p class="setting-description">
            Maximum time to wait for order completion
          </p>
        </div>
      </div>
    </div>

    <!-- Create/Edit Endpoint Modal -->
    <div v-if="showCreateModal || editingEndpoint" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingEndpoint ? 'Edit Endpoint' : 'Create Endpoint' }}</h3>
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
  name: 'OrderingConfig',
  setup() {
    // State
    const loading = ref(false)
    const showCreateModal = ref(false)
    const editingEndpoint = ref(null)
    const endpointFilter = ref('')
    const orderStatusFilter = ref('')
    
    const orderStats = reactive({
      total_orders: 0,
      pending_orders: 0,
      completed_orders: 0,
      failed_orders: 0,
      success_rate: 0
    })
    
    const endpoints = ref([])
    const orders = ref([])
    
    const orderSettings = reactive({
      auto_retry_failed: true,
      enable_order_queue: true,
      max_concurrent_orders: 10,
      order_timeout_minutes: 30
    })
    
    // Form data
    const formData = reactive({
      name: '',
      description: '',
      endpoint_url: '',
      method: 'POST',
      auth_type: 'API_KEY',
      api_key: '',
      cost_kpi: 0,
      cost_currency: 0.0,
      is_active: true,
      is_public: false
    })

    // Computed
    const filteredEndpoints = computed(() => {
      return endpoints.value.filter(endpoint => {
        if (endpointFilter.value === 'active' && !endpoint.is_active) return false
        if (endpointFilter.value === 'public' && !endpoint.is_public) return false
        if (endpointFilter.value === 'private' && endpoint.is_public) return false
        return true
      })
    })

    const filteredOrders = computed(() => {
      return orders.value.filter(order => {
        if (orderStatusFilter.value && order.status !== orderStatusFilter.value) return false
        return true
      })
    })

    // Methods
    const loadOrderStats = async () => {
      try {
        const data = await apiGet('/api/ordering/stats')
        Object.assign(orderStats, data)
      } catch (error) {
        console.error('Error loading order stats:', error)
      }
    }

    const loadEndpoints = async () => {
      try {
        loading.value = true
        const data = await apiGet('/api/ordering/endpoints')
        endpoints.value = data.endpoints
      } catch (error) {
        console.error('Error loading endpoints:', error)
      } finally {
        loading.value = false
      }
    }

    const loadOrders = async () => {
      try {
        loading.value = true
        const data = await apiGet('/api/ordering/orders/all?limit=50')
        orders.value = data.orders
      } catch (error) {
        console.error('Error loading orders:', error)
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
        
        await loadEndpoints()
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
        await loadEndpoints()
      } catch (error) {
        console.error('Error toggling endpoint:', error)
      } finally {
        loading.value = false
      }
    }

    const editEndpoint = (endpoint) => {
      editingEndpoint.value = endpoint
      Object.assign(formData, endpoint)
    }

    const deleteEndpoint = async (endpoint) => {
      if (!confirm(`Are you sure you want to delete "${endpoint.name}"?`)) {
        return
      }
      
      try {
        loading.value = true
        await apiDelete(`/api/ordering/endpoints/${endpoint.id}`)
        await loadEndpoints()
      } catch (error) {
        console.error('Error deleting endpoint:', error)
      } finally {
        loading.value = false
      }
    }

    const viewOrders = (endpoint) => {
      // Filter orders by endpoint
      orderStatusFilter.value = ''
      // Scroll to orders section
      document.querySelector('.orders-section').scrollIntoView({ behavior: 'smooth' })
    }

    const viewOrderDetails = (order) => {
      // Show order details modal or navigate to order details
      console.log('View order details:', order)
    }

    const retryOrder = async (order) => {
      try {
        await apiPost(`/api/ordering/orders/${order.id}/retry`)
        await loadOrders()
      } catch (error) {
        console.error('Error retrying order:', error)
      }
    }

    const updateOrderSettings = async () => {
      try {
        await apiPut('/api/ordering/settings', orderSettings)
      } catch (error) {
        console.error('Error updating order settings:', error)
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
        cost_kpi: 0,
        cost_currency: 0.0,
        is_active: true,
        is_public: false
      })
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    // Lifecycle
    onMounted(() => {
      loadOrderStats()
      loadEndpoints()
      loadOrders()
    })

    return {
      loading,
      showCreateModal,
      editingEndpoint,
      endpointFilter,
      orderStatusFilter,
      orderStats,
      endpoints,
      orders,
      orderSettings,
      formData,
      filteredEndpoints,
      filteredOrders,
      loadOrderStats,
      loadEndpoints,
      loadOrders,
      saveEndpoint,
      toggleEndpoint,
      editEndpoint,
      deleteEndpoint,
      viewOrders,
      viewOrderDetails,
      retryOrder,
      updateOrderSettings,
      closeModal,
      formatDate
    }
  }
}
</script>

<style scoped>
.ordering-config {
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

.stats-section,
.endpoints-section,
.orders-section,
.settings-section {
  margin-bottom: 30px;
}

.stats-section h4,
.endpoints-section h4,
.orders-section h4,
.settings-section h4 {
  margin: 0 0 16px 0;
  color: #34495e;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
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

.endpoints-controls,
.orders-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.endpoints-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.endpoint-card {
  background: white;
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

.endpoint-card.inactive {
  opacity: 0.7;
}

.endpoint-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.endpoint-header h5 {
  margin: 0;
  color: #2c3e50;
}

.endpoint-badges {
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

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.processing {
  background: #cce5ff;
  color: #004085;
}

.status-badge.completed {
  background: #d4edda;
  color: #155724;
}

.status-badge.failed {
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

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-label {
  font-weight: 600;
  color: #34495e;
  min-width: 80px;
}

.detail-value {
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

.orders-table {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.orders-table table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th,
.orders-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e1e8ed;
}

.orders-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #34495e;
}

.orders-table tr:hover {
  background: #f8f9fa;
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
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #34495e;
}

.setting-description {
  font-size: 14px;
  color: #7f8c8d;
  margin: 8px 0 0 0;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 8px;
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

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-warning {
  background: #f39c12;
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

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
  
  .endpoints-grid {
    grid-template-columns: 1fr;
  }
  
  .endpoints-controls,
  .orders-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
