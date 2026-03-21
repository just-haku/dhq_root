<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>Growth Orders</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>Manage and monitor your growth campaigns</p>
    
</div>

    <div class="page-actions">

      <button class="btn btn-primary" @click="createNewOrder">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M12 8 L12 16 M8 12 L16 12" stroke="currentColor" stroke-width="2"/>
        </svg>
        New Order
      </button>
      <button class="btn btn-secondary" @click="refreshData">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M12 6 L12 12 L16 16" stroke="currentColor" stroke-width="2"/>
        </svg>
        Refresh
      </button>
    
</div>

    <div class="growth-orders-content">
      <!-- Enhanced Stats Overview -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 17 L9 11 L13 15 L21 7" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="21" cy="7" r="2" fill="currentColor"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalOrders }}</div>
            <div class="stat-label">Total Orders</div>
            <div class="stat-change positive">+12% this month</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="12" cy="12" r="3" fill="currentColor"/>
              <path d="M12 2 L12 7 M12 17 L12 22 M2 12 L7 12 M17 12 L22 12" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalKPI }}</div>
            <div class="stat-label">Total KPI Spent</div>
            <div class="stat-change positive">+8% this month</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2 L2 20 L22 20 Z" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M12 8 L12 12 M12 16 L12 16.5" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ avgROI }}%</div>
            <div class="stat-label">Average ROI</div>
            <div class="stat-change positive">+5% improvement</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M12 6 L12 12 L15 15" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ completionRate }}%</div>
            <div class="stat-label">Completion Rate</div>
            <div class="stat-change negative">-2% this week</div>
          </div>
        </div>
      </div>

      <!-- Enhanced Filters and Search -->
      <div class="orders-controls">
        <div class="search-section">
          <div class="search-bar">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M21 21 L16.65 16.65" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search orders by name, ID, or type..."
              class="search-input"
            />
          </div>
        </div>
        
        <div class="filter-section">
          <div class="filter-group">
            <label>Status:</label>
            <select v-model="selectedStatus" class="filter-select">
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Type:</label>
            <select v-model="selectedType" class="filter-select">
              <option value="all">All Types</option>
              <option value="growth">Growth Campaign</option>
              <option value="marketing">Marketing Push</option>
              <option value="engagement">Engagement Boost</option>
              <option value="retention">Retention Campaign</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Sort:</label>
            <select v-model="sortBy" class="filter-select">
              <option value="created">Created Date</option>
              <option value="progress">Progress</option>
              <option value="roi">ROI</option>
              <option value="budget">Budget</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Enhanced Orders Grid -->
      <div class="orders-grid">
        <div 
          v-for="order in filteredOrders" 
          :key="order.id"
          class="order-card"
          :class="{ 'active': order.status === 'active', 'completed': order.status === 'completed' }"
        >
          <div class="order-header">
            <div class="order-info">
              <h3>{{ order.name }}</h3>
              <span class="order-id">#{{ order.id }}</span>
            </div>
            <div class="order-status" :class="order.status">
              {{ order.status }}
            </div>
          </div>
          
          <div class="order-metrics">
            <div class="metric">
              <span class="metric-label">Progress</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: order.progress + '%' }"></div>
              </div>
              <span class="metric-value">{{ order.progress }}%</span>
            </div>
            
            <div class="metric">
              <span class="metric-label">ROI</span>
              <span class="metric-value">{{ order.roi }}%</span>
            </div>
            
            <div class="metric">
              <span class="metric-label">Duration</span>
              <span class="metric-value">{{ order.duration }} days</span>
            </div>
          </div>
          
          <div class="order-actions">
            <button class="btn btn-sm btn-outline" @click="viewDetails(order)">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
              </svg>
              Details
            </button>
            <button class="btn btn-sm btn-outline" @click="pauseOrder(order)" v-if="order.status === 'active'">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="4" width="4" height="16" fill="currentColor"/>
                <rect x="14" y="4" width="4" height="16" fill="currentColor"/>
              </svg>
              Pause
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Reactive state
const searchQuery = ref('')
const selectedStatus = ref('all')
const selectedType = ref('all')
const sortBy = ref('created')

const orders = ref([
  {
    id: 1234,
    name: 'Summer Campaign 2024',
    status: 'active',
    progress: 75,
    roi: 145,
    duration: 30,
    type: 'growth',
    budget: 5000,
    created: new Date('2024-01-15'),
    targetAudience: 'all',
    targetRegion: 'global'
  },
  {
    id: 1235,
    name: 'Product Launch Boost',
    status: 'active',
    progress: 45,
    roi: 89,
    duration: 14,
    type: 'marketing',
    budget: 3000,
    created: new Date('2024-01-14'),
    targetAudience: 'new',
    targetRegion: 'north-america'
  },
  {
    id: 1236,
    name: 'Brand Awareness Q2',
    status: 'completed',
    progress: 100,
    roi: 234,
    duration: 21,
    type: 'engagement',
    budget: 2000,
    created: new Date('2024-01-13'),
    targetAudience: 'all',
    targetRegion: 'global'
  },
  {
    id: 1237,
    name: 'Retention Campaign',
    status: 'paused',
    progress: 30,
    roi: 56,
    duration: 30,
    type: 'retention',
    budget: 1500,
    created: new Date('2024-01-12'),
    targetAudience: 'active',
    targetRegion: 'europe'
  },
  {
    id: 1238,
    name: 'New User Onboarding',
    status: 'pending',
    progress: 0,
    roi: 0,
    duration: 7,
    type: 'growth',
    budget: 1000,
    created: new Date('2024-01-16'),
    targetAudience: 'new',
    targetRegion: 'global'
  }
])

// Computed properties
const filteredOrders = computed(() => {
  let filtered = orders.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(order => 
      order.name.toLowerCase().includes(query) ||
      order.id.toString().includes(query) ||
      order.type.toLowerCase().includes(query)
    )
  }

  // Apply status filter
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(order => order.status === selectedStatus.value)
  }

  // Apply type filter
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(order => order.type === selectedType.value)
  }

  // Apply sorting
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'created':
        return b.created - a.created
      case 'progress':
        return b.progress - a.progress
      case 'roi':
        return b.roi - a.roi
      case 'budget':
        return b.budget - a.budget
      default:
        return b.created - a.created
    }
  })

  return filtered
})

const totalOrders = computed(() => orders.value.length)
const totalKPI = computed(() => orders.value.reduce((sum, order) => sum + order.budget, 0))
const avgROI = computed(() => {
  const completedOrders = orders.value.filter(order => order.status === 'completed')
  if (completedOrders.length === 0) return 0
  return Math.round(completedOrders.reduce((sum, order) => sum + order.roi, 0) / completedOrders.length)
})
const completionRate = computed(() => {
  const completedOrders = orders.value.filter(order => order.status === 'completed').length
  return Math.round((completedOrders / orders.value.length) * 100)
})

// Methods
const createNewOrder = () => {
  console.log('Creating new order...')
}

const refreshData = () => {
  console.log('Refreshing data...')
}

const viewDetails = (order) => {
  console.log('Viewing details for order:', order.id)
}

const pauseOrder = (order) => {
  order.status = order.status === 'active' ? 'paused' : 'active'
  console.log('Toggled order status:', order.id)
}

const deleteOrder = (order) => {
  if (confirm(`Are you sure you want to delete order #${order.id}?`)) {
    const index = orders.value.findIndex(o => o.id === order.id)
    if (index > -1) {
      orders.value.splice(index, 1)
    }
    console.log('Deleted order:', order.id)
  }
}

const duplicateOrder = (order) => {
  const newOrder = {
    ...order,
    id: Math.max(...orders.value.map(o => o.id)) + 1,
    name: `${order.name} (Copy)`,
    status: 'pending',
    progress: 0,
    created: new Date()
  }
  orders.value.push(newOrder)
  console.log('Duplicated order:', order.id)
}

onMounted(() => {
  console.log('Growth Orders component mounted')
})
</script>

<style scoped>
.growth-orders-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* Stats Overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
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

.stat-card:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.3));
  border: 1px solid rgba(96, 165, 250, 0.3);
  color: #60a5fa;
  font-size: 1.25rem;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1;
}

.stat-label {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.stat-change {
  font-size: 0.75rem;
  font-weight: 600;
  margin-top: 0.5rem;
}

.stat-change.positive {
  color: #10b981;
}

.stat-change.negative {
  color: #ef4444;
}

/* Controls Section */
.orders-controls {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.search-section {
  display: flex;
  justify-content: center;
}

.search-bar {
  position: relative;
  max-width: 400px;
  width: 100%;
}

.search-bar .icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  width: 1.25rem;
  height: 1.25rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(255, 255, 255, 0.08);
}

.filter-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(255, 255, 255, 0.08);
}

/* Orders Grid */
.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.order-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
}

.order-card:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.order-id {
  color: #94a3b8;
  font-size: 0.875rem;
  font-family: monospace;
}

.order-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.order-status.active {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.order-status.completed {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.order-status.paused {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.order-status.pending {
  background: rgba(156, 163, 175, 0.2);
  color: #9ca3af;
}

.order-status.failed {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.order-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.metric-label {
  color: #94a3b8;
  font-size: 0.875rem;
  min-width: 80px;
}

.progress-bar {
  flex: 1;
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

.metric-value {
  color: #f1f5f9;
  font-weight: 600;
  min-width: 60px;
  text-align: right;
}

.order-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.btn-danger {
  border-color: rgba(239, 68, 68, 0.5);
  color: #ef4444;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

.btn-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
}

.icon {
  width: 1rem;
  height: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .filter-section {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .orders-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .order-card {
    padding: 1rem;
  }
  
  .order-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .metric {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .order-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}

/* Icon Animations */
.icon {
  transition: all 0.3s ease;
}

.order-card:hover .icon {
  transform: scale(1.1) rotate(5deg);
}

.btn:hover .icon {
  transform: scale(1.05);
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
