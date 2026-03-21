<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>Manage Orders</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>Monitor and control all your active orders</p>
    
</div>

    <div class="page-actions">

      <button class="btn btn-primary" @click="$router.push('/orders/create')">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M12 8 L12 16 M8 12 L16 12" stroke="currentColor" stroke-width="2"/>
        </svg>
        New Order
      </button>
      <button class="btn btn-secondary" @click="refreshOrders">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M12 6 L12 12 L16 16" stroke="currentColor" stroke-width="2"/>
        </svg>
        Refresh
      </button>
    
</div>

    <div class="orders-manage-content">
      <div class="orders-filters">
        <div class="filter-group">
          <label>Status:</label>
          <select v-model="selectedStatus" class="filter-select">
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Search:</label>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search orders..."
            class="search-input"
          />
        </div>
      </div>

      <div class="orders-table-container">
        <table class="orders-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Name</th>
              <th>Type</th>
              <th>Budget</th>
              <th>Progress</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in filteredOrders" :key="order.id">
              <td>
                <span class="order-id">#{{ order.id }}</span>
              </td>
              <td>
                <div class="order-name">{{ order.name }}</div>
              </td>
              <td>
                <span class="order-type">{{ order.type }}</span>
              </td>
              <td>
                <span class="order-budget">{{ order.budget }} KPI</span>
              </td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: order.progress + '%' }"></div>
                  </div>
                  <span class="progress-text">{{ order.progress }}%</span>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="order.status">
                  {{ order.status }}
                </span>
              </td>
              <td>
                <span class="order-date">{{ formatDate(order.created) }}</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn-icon" @click="viewOrder(order)" title="View">
                    <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                      <circle cx="12" cy="12" r="3" fill="currentColor"/>
                    </svg>
                  </button>
                  <button 
                    class="btn-icon" 
                    @click="toggleOrder(order)"
                    :title="order.status === 'active' ? 'Pause' : 'Resume'"
                    v-if="order.status === 'active' || order.status === 'paused'"
                  >
                    <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="6" y="4" width="4" height="16" fill="currentColor" v-if="order.status === 'active'"/>
                      <rect x="14" y="4" width="4" height="16" fill="currentColor" v-if="order.status === 'active'"/>
                      <polygon points="5,4 19,12 5,20" fill="currentColor" v-if="order.status === 'paused'"/>
                    </svg>
                  </button>
                  <button class="btn-icon danger" @click="cancelOrder(order)" title="Cancel" v-if="order.status === 'active' || order.status === 'paused'">
                    <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M18 6 L6 18 M6 6 L18 18" stroke="currentColor" stroke-width="2" fill="none"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <button class="btn btn-outline" :disabled="currentPage === 1" @click="currentPage--">
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15 18 L9 12 L15 6" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          Previous
        </button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button class="btn btn-outline" :disabled="currentPage === totalPages" @click="currentPage++">
          Next
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 18 L15 12 L9 6" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const selectedStatus = ref('all')
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

const orders = ref([
  {
    id: 1234,
    name: 'Summer Campaign 2024',
    type: 'Growth',
    budget: 5000,
    progress: 75,
    status: 'active',
    created: new Date('2024-01-15')
  },
  {
    id: 1235,
    name: 'Product Launch Boost',
    type: 'Marketing',
    budget: 3000,
    progress: 45,
    status: 'active',
    created: new Date('2024-01-14')
  },
  {
    id: 1236,
    name: 'Brand Awareness Q2',
    type: 'Engagement',
    budget: 2000,
    progress: 100,
    status: 'completed',
    created: new Date('2024-01-10')
  },
  {
    id: 1237,
    name: 'Retention Campaign',
    type: 'Retention',
    budget: 1500,
    progress: 30,
    status: 'paused',
    created: new Date('2024-01-12')
  },
  {
    id: 1238,
    name: 'New User Onboarding',
    type: 'Growth',
    budget: 4000,
    progress: 0,
    status: 'pending',
    created: new Date('2024-01-16')
  }
])

const filteredOrders = computed(() => {
  let filtered = orders.value

  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(order => order.status === selectedStatus.value)
  }

  if (searchQuery.value) {
    filtered = filtered.filter(order => 
      order.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      order.id.toString().includes(searchQuery.value)
    )
  }

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredOrders.value.length / itemsPerPage)
})

const paginatedOrders = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredOrders.value.slice(start, end)
})

const refreshOrders = () => {
  console.log('Refreshing orders...')
}

const viewOrder = (order) => {
  console.log('Viewing order:', order.id)
}

const toggleOrder = (order) => {
  if (order.status === 'active') {
    order.status = 'paused'
    console.log('Paused order:', order.id)
  } else if (order.status === 'paused') {
    order.status = 'active'
    console.log('Resumed order:', order.id)
  }
}

const cancelOrder = (order) => {
  if (confirm(`Are you sure you want to cancel order #${order.id}?`)) {
    order.status = 'cancelled'
    console.log('Cancelled order:', order.id)
  }
}

const formatDate = (date) => {
  return date.toLocaleDateString()
}

onMounted(() => {
  console.log('Orders Manage component mounted')
})
</script>

<style scoped>
.orders-manage-content {
  max-width: 1200px;
  margin: 0 auto;
}

.orders-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 60px;
}

.filter-select,
.search-input {
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #f1f5f9;
  font-size: 0.875rem;
}

.search-input {
  min-width: 200px;
}

.orders-table-container {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 2rem;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th {
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  text-align: left;
  color: #f1f5f9;
  font-weight: 600;
  font-size: 0.875rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.orders-table td {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
  font-size: 0.875rem;
}

.orders-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.order-id {
  font-family: monospace;
  color: #94a3b8;
}

.order-name {
  font-weight: 500;
  color: #f1f5f9;
}

.order-type {
  padding: 0.25rem 0.5rem;
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.order-budget {
  color: #f59e0b;
  font-weight: 600;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar {
  width: 60px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #3b82f6);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: #94a3b8;
  min-width: 35px;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.pending {
  background: rgba(156, 163, 175, 0.2);
  color: #9ca3af;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.status-badge.paused {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.status-badge.completed {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.status-badge.cancelled {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

.btn-icon.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.btn-icon .icon {
  width: 1rem;
  height: 1rem;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #94a3b8;
  font-size: 0.875rem;
}

.icon {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 768px) {
  .orders-filters {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-select,
  .search-input {
    flex: 1;
  }
  
  .orders-table-container {
    overflow-x: auto;
  }
  
  .orders-table {
    min-width: 800px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 0.75rem;
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
