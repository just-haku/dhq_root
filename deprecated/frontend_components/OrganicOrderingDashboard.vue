<template>
  <div class="organic-ordering-dashboard">
    <div class="ordering-header">
      <h2>📈 Organic Growth Simulation</h2>
      <p>Create natural-looking view growth patterns for your content</p>
      
      <div class="header-actions">
        <button @click="showCreateModal = true" class="btn btn-primary">
          <i class="fas fa-chart-line"></i>
          Create Growth Plan
        </button>
        <button @click="showExecuteModal = true" class="btn btn-success">
          <i class="fas fa-play"></i>
          Execute Order
        </button>
        <button @click="executeNow" class="btn btn-warning" :disabled="!selectedOrder">
          <i class="fas fa-bolt"></i>
          NOW!!!
        </button>
        <button @click="refreshOrders" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-sync" :class="{ 'fa-spin': loading }"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Growth Patterns Info -->
    <div class="patterns-info">
      <h3>Growth Patterns</h3>
      <div class="patterns-grid">
        <div class="pattern-card">
          <h4>🌱 Organic</h4>
          <p>Natural growth with random variations, mimicking real viral content</p>
        </div>
        <div class="pattern-card">
          <h4>🚀 Viral</h4>
          <p>Explosive initial growth, then gradual decline</p>
        </div>
        <div class="pattern-card">
          <h4>📊 Steady</h4>
          <p>Consistent delivery over time</p>
        </div>
        <div class="pattern-card">
          <h4>⚡ Burst</h4>
          <p>Random bursts of activity to simulate viral moments</p>
        </div>
      </div>
    </div>

    <!-- Orders List -->
    <div class="orders-section">
      <h3>Active Growth Orders</h3>
      <div class="orders-grid">
        <div 
          v-for="order in orders" 
          :key="order.id"
          class="order-card"
          @click="selectOrder(order)"
        >
          <div class="order-header">
            <h4>{{ order.order_name }}</h4>
            <span class="order-status" :class="order.status.toLowerCase()">
              {{ order.status }}
            </span>
          </div>
          
          <div class="order-details">
            <div class="detail">
              <span class="label">Target:</span>
              <span class="value">{{ order.target_url }}</span>
            </div>
            <div class="detail">
              <span class="label">Service:</span>
              <span class="value">{{ order.service_type }}</span>
            </div>
            <div class="detail">
              <span class="label">Pattern:</span>
              <span class="value">{{ order.growth_pattern }}</span>
            </div>
            <div class="detail">
              <span class="label">Duration:</span>
              <span class="value">{{ order.duration_days }} days</span>
            </div>
          </div>
          
          <div class="order-progress">
            <div class="progress-info">
              <span>Progress: {{ order.progress_percentage.toFixed(1) }}%</span>
              <span>{{ order.completed_hours }}/{{ order.total_hours }} hours</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: order.progress_percentage + '%' }"
              ></div>
            </div>
          </div>
          
          <div class="order-footer">
            <div class="kpi-cost">
              <i class="fas fa-coins"></i>
              <span>KPI Cost: {{ order.kpi_cost || 0 }}</span>
            </div>
            <div class="order-actions">
              <button @click.stop="deleteOrder(order)" class="btn btn-sm btn-danger">
                <i class="fas fa-trash"></i>
                Delete
              </button>
            </div>
          </div>
          
          <div class="order-footer">
            <small class="created-date">
              Created: {{ formatDate(order.created_at) }}
            </small>
            <small v-if="order.next_delivery" class="next-delivery">
              Next: {{ formatDate(order.next_delivery) }}
            </small>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Growth Plan Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create Growth Plan</h3>
          <button @click="closeCreateModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Order Name</label>
            <input 
              type="text" 
              v-model="createForm.order_name" 
              class="form-control"
              placeholder="e.g., Summer Campaign Growth"
            />
          </div>
          
          <div class="form-group">
            <label>Service Name</label>
            <input 
              type="text" 
              v-model="createForm.service_name" 
              class="form-control"
              placeholder="e.g., YouTube Views Boost"
            />
          </div>
          
          <div class="form-group">
            <label>Target URL</label>
            <input 
              type="url" 
              v-model="createForm.target_url" 
              class="form-control"
              placeholder="https://..."
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Service Type</label>
              <select v-model="createForm.service_type" class="form-control">
                <option value="views">Views</option>
                <option value="likes">Likes</option>
                <option value="followers">Followers</option>
                <option value="comments">Comments</option>
                <option value="shares">Shares</option>
              </select>
            </div>
            <div class="form-group">
              <label>Total Quantity</label>
              <input 
                type="number" 
                v-model="createForm.total_quantity" 
                min="100"
                class="form-control"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Duration (Days)</label>
              <input 
                type="number" 
                v-model="createForm.duration_days" 
                min="1"
                step="0.1"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>Growth Pattern</label>
              <select v-model="createForm.growth_pattern" class="form-control">
                <option value="organic">🌱 Organic</option>
                <option value="viral">🚀 Viral</option>
                <option value="steady">📊 Steady</option>
                <option value="burst">⚡ Burst</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Start Delay (Hours)</label>
              <input 
                type="number" 
                v-model="createForm.start_delay_hours" 
                min="0"
                step="0.1"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>Min Per Hour</label>
              <input 
                type="number" 
                v-model="createForm.min_per_hour" 
                min="0"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>Max Per Hour</label>
              <input 
                type="number" 
                v-model="createForm.max_per_hour" 
                min="0"
                class="form-control"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>Peak Hours (comma-separated, 0-23)</label>
            <input 
              type="text" 
              v-model="peakHoursText" 
              placeholder="9, 12, 15, 18, 21"
              class="form-control"
            />
            <small>Hours when activity should be higher (e.g., 9, 12, 15, 18, 21)</small>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeCreateModal" class="btn btn-secondary">
            Cancel
          </button>
          <button @click="createGrowthPlan" class="btn btn-primary" :disabled="creating">
            <i class="fas fa-spinner fa-spin" v-if="creating"></i>
            {{ creating ? 'Creating...' : 'Create Plan' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Execute Order Modal -->
    <div v-if="showExecuteModal" class="modal-overlay" @click="closeExecuteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Execute Organic Order</h3>
          <button @click="closeExecuteModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Order Name</label>
            <input 
              type="text" 
              v-model="executeForm.order_name" 
              class="form-control"
              placeholder="My Organic Growth Order"
            />
          </div>
          
          <div class="form-group">
            <label>Target URL</label>
            <input 
              type="url" 
              v-model="executeForm.target_url" 
              class="form-control"
              placeholder="https://..."
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Service Type</label>
              <select v-model="executeForm.service_type" class="form-control">
                <option value="views">Views</option>
                <option value="likes">Likes</option>
                <option value="followers">Followers</option>
                <option value="comments">Comments</option>
                <option value="shares">Shares</option>
              </select>
            </div>
            <div class="form-group">
              <label>Total Quantity</label>
              <input 
                type="number" 
                v-model="executeForm.total_quantity" 
                min="100"
                class="form-control"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Duration (Days)</label>
              <input 
                type="number" 
                v-model="executeForm.duration_days" 
                min="1"
                step="0.1"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>Growth Pattern</label>
              <select v-model="executeForm.growth_pattern" class="form-control">
                <option value="organic">🌱 Organic</option>
                <option value="viral">🚀 Viral</option>
                <option value="steady">📊 Steady</option>
                <option value="burst">⚡ Burst</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>API Key</label>
            <input 
              type="password" 
              v-model="executeForm.api_key" 
              class="form-control"
              placeholder="Your service API key"
            />
          </div>
          
          <div class="form-group">
            <label>Tolerance (%)</label>
            <input 
              type="number" 
              v-model="executeForm.tolerance_pct" 
              min="0"
              max="100"
              step="0.1"
              class="form-control"
            />
            <small>Acceptable deviation from target quantity</small>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeExecuteModal" class="btn btn-secondary">
            Cancel
          </button>
          <button @click="executeOrder" class="btn btn-success" :disabled="executing">
            <i class="fas fa-spinner fa-spin" v-if="executing"></i>
            {{ executing ? 'Executing...' : 'Execute Order' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <div v-if="selectedOrder" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedOrder.order_name }} - Details</h3>
          <button @click="closeDetailsModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="order-details">
            <div class="details-stats">
              <div class="stat-card">
                <h4>Total Hours</h4>
                <span class="stat-value">{{ selectedOrder.statistics.total_hours }}</span>
              </div>
              <div class="stat-card">
                <h4>Completed</h4>
                <span class="stat-value">{{ selectedOrder.statistics.completed_hours }}</span>
              </div>
              <div class="stat-card">
                <h4>Delivered</h4>
                <span class="stat-value">{{ selectedOrder.statistics.total_delivered }}</span>
              </div>
              <div class="stat-card">
                <h4>Success Rate</h4>
                <span class="stat-value">{{ selectedOrder.statistics.success_rate.toFixed(1) }}%</span>
              </div>
            </div>
            
            <div class="hourly-details">
              <h4>Hourly Delivery Plan</h4>
              <div class="hourly-list">
                <div 
                  v-for="(hour, index) in selectedOrder.hourly_plan.slice(0, 24)" 
                  :key="index"
                  class="hourly-item"
                  :class="hour.status.toLowerCase()"
                >
                  <span class="hour-time">Hour {{ hour.hour_index }}</span>
                  <span class="hour-quantity">{{ hour.quantity }}</span>
                  <span class="hour-status">{{ hour.status }}</span>
                  <span v-if="hour.delivered_quantity" class="hour-delivered">
                    Delivered: {{ hour.delivered_quantity }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost } from '../../utils/api.js'

export default {
  name: 'OrganicOrderingDashboard',
  setup() {
    const orders = ref([])
    const loading = ref(false)
    const showCreateModal = ref(false)
    const showExecuteModal = ref(false)
    const selectedOrder = ref(null)
    const creating = ref(false)
    const executing = ref(false)
    
    const createForm = ref({
      order_name: '',
      service_name: '',
      target_url: '',
      service_type: 'views',
      total_quantity: 1000,
      duration_days: 7,
      growth_pattern: 'organic',
      start_delay_hours: 0,
      peak_hours: [9, 12, 15, 18, 21],
      min_per_hour: 0,
      max_per_hour: 100
    })
    
    const executeForm = ref({
      order_name: '',
      target_url: '',
      service_type: 'views',
      total_quantity: 1000,
      duration_days: 7,
      growth_pattern: 'organic',
      api_key: '',
      tolerance_pct: 10
    })
    
    const peakHoursText = computed({
      get: () => createForm.value.peak_hours.join(', '),
      set: (value) => {
        createForm.value.peak_hours = value.split(',').map(h => parseInt(h.trim())).filter(h => !isNaN(h) && h >= 0 && h <= 23)
      }
    })
    
    const refreshOrders = async () => {
      loading.value = true
      try {
        const data = await apiGet('/organic-ordering/orders')
        orders.value = data.orders
      } catch (error) {
        console.error('Error fetching orders:', error)
      } finally {
        loading.value = false
      }
    }
    
    const selectOrder = (order) => {
      selectedOrder.value = order
      console.log('Selected order:', order)
    }
    
    const createGrowthPlan = async () => {
      creating.value = true
      try {
        const response = await apiPost('/organic-ordering/organic/growth-plan', createForm.value)
        if (response) {
          const data = response
          alert(`Growth plan created successfully! KPI cost: ${data.kpi_cost || 'N/A'}`)
          closeCreateModal()
          refreshOrders()
        } else {
          throw new Error('Failed to create growth plan')
        }
      } catch (error) {
        console.error('Error creating growth plan:', error)
        alert('Failed to create growth plan')
      } finally {
        creating.value = false
      }
    }
    
    const executeOrder = async () => {
      executing.value = true
      try {
        const data = await apiPost('/organic-ordering/organic/execute', executeForm.value)
        alert(`Order started successfully! KPI cost: ${data.kpi_cost}`)
        closeExecuteModal()
        refreshOrders()
      } catch (error) {
        console.error('Error executing order:', error)
        alert('Failed to execute order')
      } finally {
        executing.value = false
      }
    }
    
    const closeCreateModal = () => {
      showCreateModal.value = false
      createForm.value = {
        order_name: '',
        service_name: '',
        target_url: '',
        service_type: 'views',
        total_quantity: 1000,
        duration_days: 7,
        growth_pattern: 'organic',
        start_delay_hours: 0,
        peak_hours: [9, 12, 15, 18, 21],
        min_per_hour: 0,
        max_per_hour: 100
      }
    }
    
    const closeExecuteModal = () => {
      showExecuteModal.value = false
      executeForm.value = {
        order_name: '',
        target_url: '',
        service_type: 'views',
        total_quantity: 1000,
        duration_days: 7,
        growth_pattern: 'organic',
        api_key: '',
        tolerance_pct: 10
      }
    }
    
    const closeDetailsModal = () => {
      selectedOrder.value = null
    }
    
    const deleteOrder = async (order) => {
      if (!confirm(`Are you sure you want to delete "${order.order_name}"?`)) {
        return
      }
      
      try {
        const response = await apiPost(`/organic-ordering/orders/${order.id}/delete`)
        if (response) {
          alert('Order deleted successfully!')
          refreshOrders()
        }
      } catch (error) {
        console.error('Error deleting order:', error)
        alert('Failed to delete order')
      }
    }
    
    const executeNow = async () => {
      if (!selectedOrder.value) {
        alert('Please select an order first!')
        return
      }
      
      if (!confirm(`Execute "${selectedOrder.value.order_name}" NOW? This will start immediate execution!`)) {
        return
      }
      
      try {
        const response = await apiPost(`/organic-ordering/orders/${selectedOrder.value.id}/execute-now`)
        if (response) {
          alert('Order execution started immediately!')
          refreshOrders()
        }
      } catch (error) {
        console.error('Error executing order now:', error)
        alert('Failed to execute order')
      }
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    }
    
    onMounted(() => {
      refreshOrders()
    })
    
    return {
      orders,
      loading,
      showCreateModal,
      showExecuteModal,
      selectedOrder,
      creating,
      executing,
      createForm,
      executeForm,
      peakHoursText,
      refreshOrders,
      selectOrder,
      createGrowthPlan,
      executeOrder,
      closeCreateModal,
      closeExecuteModal,
      closeDetailsModal,
      deleteOrder,
      executeNow,
      formatDate
    }
  }
}
</script>

<style scoped>
.organic-ordering-dashboard {
  padding: 2rem;
}

.ordering-header {
  margin-bottom: 2rem;
}

.ordering-header h2 {
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.ordering-header p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.patterns-info {
  margin-bottom: 3rem;
}

.patterns-info h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.patterns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.pattern-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
}

.pattern-card h4 {
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.pattern-card p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.orders-section h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.order-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.order-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
}

.order-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.order-status.active {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.order-status.completed {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.order-status.planned {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.order-details {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.detail {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.detail .label {
  color: var(--text-secondary);
}

.detail .value {
  color: var(--text-primary);
  font-weight: 500;
}

.order-progress {
  margin-bottom: 1rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
  transition: width 0.3s ease;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-secondary);
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
  background: var(--bg-primary);
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
}

.modal-content.large {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--text-secondary);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-primary);
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-secondary);
}

.details-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.stat-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.hourly-details {
  margin-top: 2rem;
}

.hourly-list {
  display: grid;
  gap: 0.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.hourly-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border-radius: 6px;
  border-left: 4px solid var(--border-color);
}

.hourly-item.completed {
  border-left-color: #22c55e;
}

.hourly-item.failed {
  border-left-color: #ef4444;
}

.hourly-item.pending {
  border-left-color: #f59e0b;
}

.hourly-time {
  font-weight: 600;
  color: var(--text-primary);
}

.hourly-quantity {
  color: var(--text-primary);
}

.hourly-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.hourly-delivered {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* CSS Variables */
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --primary-color: #3b82f6;
  --primary-hover: #2563eb;
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] {
  --bg-primary: #1e293b;
  --bg-secondary: #334155;
  --bg-tertiary: #475569;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --border-color: #475569;
  --primary-color: #3b82f6;
  --primary-hover: #60a5fa;
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
}
</style>
