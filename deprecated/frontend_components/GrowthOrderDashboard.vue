<template>
  <div class="growth-order-dashboard">
    <div class="dashboard-header">
      <h2>📈 Channel Growth Automation</h2>
      <p>Automated organic growth with intelligent scheduling</p>
      
      <div class="header-actions">
        <button @click="showCreateModal = true" class="btn btn-primary">
          <i class="fas fa-plus"></i>
          Create Growth Order
        </button>
        <button @click="refreshOrders" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-sync" :class="{ 'fa-spin': loading }"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Orders List -->
    <div class="orders-section">
      <h3>Active Growth Orders</h3>
      <div class="orders-grid" :class="{ 'mobile-grid': isMobile }">
        <div 
          v-for="order in orders" 
          :key="order.id"
          class="order-card"
          :class="{ 
            selected: selectedOrder?.id === order.id,
            'mobile-card': isMobile 
          }"
          :data-order-id="order.id"
          @click="selectOrder(order)"
        >
          <!-- Mobile optimized header -->
          <div class="order-header" :class="{ 'mobile-header': isMobile }">
            <div class="header-left">
              <h4>{{ order.name }}</h4>
              <span class="order-status" :class="order.status.toLowerCase()">
                {{ formatStatus(order.status) }}
              </span>
            </div>
            <div class="header-right" v-if="!isMobile">
              <span class="order-progress-badge">{{ order.progress.toFixed(1) }}%</span>
            </div>
          </div>
          
          <!-- Simplified details for mobile -->
          <div class="order-details" :class="{ 'mobile-details': isMobile }">
            <div class="detail" v-if="!isMobile">
              <span class="label">Service:</span>
              <span class="value">{{ order.service_type }}</span>
            </div>
            <div class="detail">
              <span class="label">Quantity:</span>
              <span class="value">{{ order.total_quantity.toLocaleString() }}</span>
            </div>
            <div class="detail" v-if="!isMobile">
              <span class="label">Progress:</span>
              <span class="value">{{ order.progress.toFixed(1) }}%</span>
            </div>
          </div>
          
          <!-- Progress bar -->
          <div class="order-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: order.progress + '%' }"
              ></div>
            </div>
            <div class="progress-text">
              {{ order.total_executed }}/{{ order.sub_orders_count }} completed
            </div>
          </div>
          
          <!-- Mini Chart - Only render when visible -->
          <div 
            class="mini-graph-container" 
            v-if="order.sub_orders && order.sub_orders.length > 0 && visibleOrders.has(order.id)"
          >
            <canvas 
              :ref="`miniChart-${order.id}`" 
              class="mini-chart"
              :width="isMobile ? 100 : 120" 
              :height="isMobile ? 50 : 60"
            ></canvas>
          </div>
          
          <!-- Order Preview - Simplified for mobile -->
          <div class="order-preview" :class="{ 'mobile-preview': isMobile }">
            <div class="preview-item">
              <span class="preview-label">Start:</span>
              <span class="preview-value">{{ formatDateTime(order.start_time) }}</span>
            </div>
            <div class="preview-item" v-if="!isMobile">
              <span class="preview-label">End:</span>
              <span class="preview-value">{{ formatDateTime(order.end_time) }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">Rate:</span>
              <span class="preview-value">{{ calculateRate(order).toLocaleString() }}/hr</span>
            </div>
          </div>
          
          <!-- Actions - Mobile optimized -->
          <div class="order-actions" :class="{ 'mobile-actions': isMobile }">
            <button @click.stop="viewOrder(order)" class="liquid-glass-btn primary-btn">
              <i class="fas fa-eye"></i>
              <span>View Details</span>
            </button>
            <button 
              v-if="order.status === 'Active'" 
              @click.stop="pauseOrder(order)" 
              class="liquid-glass-btn warning-btn"
            >
              <i class="fas fa-pause"></i>
              <span>Pause</span>
            </button>
            <button 
              v-if="order.status !== 'Active'" 
              @click.stop="resumeOrder(order)" 
              class="liquid-glass-btn success-btn"
            >
              <i class="fas fa-play"></i>
              <span>Resume</span>
            </button>
            <button @click.stop="deleteOrder(order)" class="liquid-glass-btn danger-btn">
              <i class="fas fa-trash"></i>
              <span>Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Order Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>Create Growth Order</h3>
          <button @click="showCreateModal = false" class="btn-close">×</button>
        </div>
        
        <div class="modal-body">
          <div class="form-grid">
            <!-- Basic Information -->
            <div class="form-section">
              <h4>Basic Information</h4>
              <div class="form-group">
                <label>Order Name *</label>
                <input v-model="createForm.name" type="text" placeholder="Enter order name" />
                <span v-if="validationErrors.includes('Order name is required')" class="error-message">
                  Order name is required
                </span>
              </div>
              <div class="form-group">
                <label>Target Link *</label>
                <input v-model="createForm.target_link" type="url" placeholder="https://example.com/video" />
                <span v-if="validationErrors.includes('Target link is required')" class="error-message">
                  Target link is required
                </span>
                <span v-if="validationErrors.includes('Invalid target link format')" class="error-message">
                  Invalid URL format
                </span>
              </div>
              <div class="form-group">
                <label>Service Type *</label>
                <select v-model="createForm.service_type">
                  <option value="Views">Views</option>
                  <option value="Likes">Likes</option>
                  <option value="Followers">Followers</option>
                </select>
              </div>
              <div class="form-group">
                <label>Service ID *</label>
                <input v-model="createForm.service_id" type="text" placeholder="Service ID from API" />
                <span v-if="validationErrors.includes('Service ID is required')" class="error-message">
                  Service ID is required
                </span>
              </div>
            </div>

            <!-- Order Specifications -->
            <div class="form-section">
              <h4>Order Specifications</h4>
              <div class="form-group">
                <label>Start Date *</label>
                <input v-model="createForm.start_date" type="date" :min="minStartDate" />
                <span v-if="validationErrors.includes('Start date is required')" class="error-message">
                  Start date is required
                </span>
              </div>
              <div class="form-group">
                <label>Start Time *</label>
                <input v-model="createForm.start_time" type="time" />
                <span v-if="validationErrors.includes('Start time is required')" class="error-message">
                  Start time is required
                </span>
              </div>
              <div class="form-group">
                <label>Total Quantity *</label>
                <input v-model.number="createForm.total_quantity" type="number" min="100" />
                <span v-if="validationErrors.includes('Total quantity must be at least 100')" class="error-message">
                  Total quantity must be at least 100
                </span>
              </div>
              <div class="form-group">
                <label>Duration (minutes) *</label>
                <input v-model.number="createForm.duration_minutes" type="number" min="60" />
                <span v-if="validationErrors.includes('Duration must be at least 60 minutes')" class="error-message">
                  Duration must be at least 60 minutes
                </span>
              </div>
              <div class="form-group">
                <label>Step Interval (minutes) *</label>
                <input v-model.number="createForm.step_interval" type="number" min="1" />
                <span v-if="validationErrors.includes('Step interval must be at least 1 minute')" class="error-message">
                  Step interval must be at least 1 minute
                </span>
              </div>
              <div class="form-group">
                <label>Tolerance (%)</label>
                <input v-model.number="createForm.tolerance_percent" type="number" min="0" max="50" />
                <span v-if="validationErrors.includes('Tolerance must be between 0 and 50 percent')" class="error-message">
                  Tolerance must be between 0 and 50 percent
                </span>
              </div>
              <div class="form-group">
                <span v-if="validationErrors.includes('Start time must be in the future')" class="error-message">
                  Start time must be in the future
                </span>
              </div>
            </div>

            <!-- Graph Configuration -->
            <div class="form-section">
              <h4>Graph Configuration</h4>
              <div class="form-group">
                <label>Graph Type *</label>
                <select v-model="createForm.graph_type" @change="updatePreview">
                  <option value="Organic">Organic (S-Curve)</option>
                  <option value="Viral">Viral (Exponential)</option>
                  <option value="Steady">Steady (Linear)</option>
                  <option value="Burst">Burst (Random)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Seed (Optional)</label>
                <input v-model="createForm.seed" type="text" placeholder="For reproducible results" autocomplete="off" />
              </div>
              <div class="form-group">
                <label>API Server *</label>
                <select v-model="createForm.api_server_id" @change="updateApiKeyDisplay" class="form-control">
                  <option value="">Select API Server</option>
                  <option v-for="server in apiServers" :key="server.id" :value="server.id">
                    {{ server.display_name }} ({{ server.base_url }})
                  </option>
                </select>
              </div>
              <div class="form-group" v-if="createForm.api_server_id">
                <label>API Key</label>
                <div class="api-key-display">
                  <input 
                    :value="getMaskedApiKey(createForm.api_server_id)" 
                    type="text" 
                    readonly 
                    class="form-control"
                    placeholder="No API key set for this server"
                  />
                  <small class="form-text">
                    API key configured in Settings. Only first 4 characters shown for security.
                  </small>
                </div>
              </div>
            </div>
          </div>

          <!-- Graph Preview -->
          <div class="preview-section">
            <h4>Graph Preview</h4>
            <div class="preview-controls">
              <button @click="updatePreview" class="btn btn-secondary">
                <i class="fas fa-chart-line"></i>
                Update Preview
              </button>
              <div v-if="previewData" class="preview-stats">
                <span>Steps: {{ previewData.total_steps }}</span>
                <span>Total: {{ previewData.total_quantity.toLocaleString() }}</span>
                <span>Start: {{ formatDateTime(previewData.start_time) }}</span>
                <span>End: {{ formatDateTime(previewData.end_time) }}</span>
              </div>
            </div>
            <div v-if="previewData" class="chart-container">
              <canvas ref="previewChart"></canvas>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="createOrder" class="btn btn-primary" :disabled="creating">
            <i class="fas fa-plus"></i>
            {{ creating ? 'Creating...' : 'Create Order' }}
          </button>
          <button @click="showCreateModal = false" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Order Detail Modal -->
    <div v-if="showDetailModal && selectedOrder" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedOrder.name }} - Sub Orders</h3>
          <button @click="closeDetailModal" class="btn-close">×</button>
        </div>
        
        <div class="modal-body">
          <div class="order-controls">
            <button @click="fetchOrderStatus" class="btn btn-secondary">
              <i class="fas fa-sync"></i>
              Fetch Status
            </button>
            <div class="bulk-actions">
              <button @click="selectAllSubOrders" class="btn btn-sm btn-secondary">
                Select All
              </button>
              <button @click="deselectAllSubOrders" class="btn btn-sm btn-secondary">
                Deselect All
              </button>
              <button @click="runSelectedSubOrders" class="btn btn-sm btn-primary" :disabled="selectedSubOrders.length === 0">
                Run Selected (NOW!!!)
              </button>
            </div>
          </div>
          
          <div class="sub-orders-table">
            <table>
              <thead>
                <tr>
                  <th>
                    <input 
                      type="checkbox" 
                      @change="toggleAllSubOrders"
                      :checked="allSubOrdersSelected"
                    />
                  </th>
                  <th>Scheduled Time</th>
                  <th>Quantity</th>
                  <th>Cumulative</th>
                  <th>Status</th>
                  <th>External ID</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(subOrder, index) in selectedOrder.sub_orders" :key="subOrder.id">
                  <td>
                    <input 
                      type="checkbox" 
                      :checked="selectedSubOrders.includes(subOrder.id)"
                      @change="toggleSubOrderSelection(subOrder.id)"
                    />
                  </td>
                  <td>{{ formatDateTime(subOrder.scheduled_time) }}</td>
                  <td>{{ subOrder.quantity.toLocaleString() }}</td>
                  <td>{{ calculateCumulative(index).toLocaleString() }}</td>
                  <td>
                    <span class="status-badge" :class="getStatusClass(subOrder.status)">
                      {{ formatStatus(subOrder.status) }}
                    </span>
                  </td>
                  <td>{{ subOrder.external_order_id || 'N/A' }}</td>
                  <td>
                    <button 
                      v-if="subOrder.status === 'Pending' || subOrder.status === 'Failed_Fatal' || subOrder.status === 'Retry_Pending'"
                      @click="runSubOrderNow(subOrder)" 
                      class="btn btn-sm btn-warning"
                    >
                      Run Now
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Sub-orders Progress Graph -->
          <div class="sub-orders-graph" v-if="selectedOrder.sub_orders && selectedOrder.sub_orders.length > 0">
            <h4>Sub-orders Progress</h4>
            <div class="sub-orders-chart-container">
              <canvas ref="subOrdersChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'
import Chart from 'chart.js/auto'

const orders = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const creating = ref(false)
const selectedOrder = ref(null)
const selectedSubOrders = ref([])
const previewChart = ref(null)
const chartInstance = ref(null)
const subOrdersChart = ref(null)
const subOrdersChartInstance = ref(null)

// Performance optimization refs
const visibleOrders = ref(new Set())
const chartRenderQueue = ref(new Set())
const intersectionObserver = ref(null)
const refreshDebounceTimer = ref(null)
const isMobile = ref(false)

// Security and performance improvements
const componentCharts = ref(new Set()) // Track component-specific charts
const ordersVersion = ref(0) // Version for efficient data comparison
const lastRefreshTime = ref(0) // Prevent excessive refreshes
const validationErrors = ref([]) // Form validation errors

// Check if mobile on mount and resize
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

// Lazy loading with Intersection Observer
const setupIntersectionObserver = () => {
  if (intersectionObserver.value) {
    intersectionObserver.value.disconnect()
  }
  
  intersectionObserver.value = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        const orderId = entry.target.dataset.orderId
        if (entry.isIntersecting) {
          visibleOrders.value.add(orderId)
          // Queue chart rendering for visible orders
          if (!chartRenderQueue.value.has(orderId)) {
            chartRenderQueue.value.add(orderId)
            // Defer chart rendering to next frame
            requestAnimationFrame(() => {
              renderMiniChart(orderId, orders.value.find(o => o.id === orderId)?.sub_orders || [])
              chartRenderQueue.value.delete(orderId)
            })
          }
        } else {
          visibleOrders.value.delete(orderId)
        }
      })
    },
    {
      root: null,
      rootMargin: '50px',
      threshold: 0.1
    }
  )
}

// Debounced refresh function
const debouncedRefresh = () => {
  if (refreshDebounceTimer.value) {
    clearTimeout(refreshDebounceTimer.value)
  }
  refreshDebounceTimer.value = setTimeout(() => {
    refreshOrders()
  }, 500)
}

const createForm = reactive({
  name: '',
  target_link: '',
  service_id: '',
  service_type: 'Views',
  start_date: new Date().toISOString().split('T')[0], // Today's date
  start_time: '09:00',
  total_quantity: 10000,
  duration_minutes: 1440,
  step_interval: 60,
  graph_type: 'Organic',
  tolerance_percent: 10,
  seed: null,
  api_server_id: '', // User's selected API server
  sequential_placement: false // Default to time-based placement
})

const previewData = ref(null)
const userAPIKeys = ref([])
const availableServers = ref([])

// Computed property for minimum start date (today)
const minStartDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

// Load user's API keys and available servers
const loadUserAPIKeys = async () => {
  try {
    const [keysResponse, serversResponse] = await Promise.all([
      apiGet('/api-management/user-keys'),
      apiGet('/api-management/servers')
    ])
    
    userAPIKeys.value = keysResponse.keys || []
    availableServers.value = serversResponse.servers || []
    
    // Set default API key if available
    if (userAPIKeys.value.length > 0) {
      const defaultKey = userAPIKeys.value.find(key => key.is_active) || userAPIKeys.value[0]
      if (defaultKey) {
        createForm.api_key = defaultKey.api_key
        createForm.selected_server = defaultKey.api_server_id
      }
    }
  } catch (error) {
    console.error('Failed to load API keys:', error)
  }
}

// Computed properties
const allSubOrdersSelected = computed(() => {
  return selectedOrder.value && 
         selectedSubOrders.value.length === selectedOrder.value.sub_orders.length
})

// Optimized refresh orders with performance improvements
const refreshOrders = async () => {
  // Prevent excessive refreshes
  const now = Date.now()
  if (now - lastRefreshTime.value < 1000) {
    console.log('Refresh throttled')
    return
  }
  lastRefreshTime.value = now
  
  loading.value = true
  try {
    console.log('Fetching orders...')
    const data = await apiGet('/growth/list')
    console.log('Orders response:', data)
    
    if (data && data.success) {
      const newOrders = data.orders || []
      console.log('Orders loaded:', newOrders.length, 'orders')
      
      // Efficient comparison using version and length check
      if (orders.value.length !== newOrders.length || 
          ordersVersion.value !== data.version) {
        orders.value = newOrders
        ordersVersion.value = data.version || Date.now()
        
        // Clear visible orders set to force re-observation
        visibleOrders.value.clear()
        
        // Re-observe all order cards after DOM update
        await nextTick()
        observeOrderCards()
      }
    } else {
      console.error('Failed to load orders:', data)
      orders.value = []
    }
  } catch (error) {
    console.error('Error fetching orders:', error)
    orders.value = []
  } finally {
    loading.value = false
  }
}

// Observe order cards for lazy loading
const observeOrderCards = () => {
  if (!intersectionObserver.value) return
  
  // Clear previous observations
  intersectionObserver.value.disconnect()
  
  // Observe all order cards
  const orderCards = document.querySelectorAll('.order-card')
  orderCards.forEach(card => {
    intersectionObserver.value.observe(card)
  })
}

const selectOrder = (order) => {
  // Direct to view order details instead of just selecting
  viewOrder(order)
}

const viewOrder = async (order) => {
  try {
    const data = await apiGet(`/growth/${order.id}`)
    if (data.success) {
      selectedOrder.value = data.order
      selectedSubOrders.value = []
      showDetailModal.value = true
      
      // Start auto-refresh for this order
      startOrderAutoRefresh(order.id)
      
      // Render sub-orders chart
      await nextTick()
      renderSubOrdersChart()
    }
  } catch (error) {
    console.error('Error fetching order details:', error)
  }
}

// Optimized mini chart rendering with performance improvements
const renderMiniChart = (orderId, subOrders) => {
  // Early return if no sub-orders
  if (!subOrders || subOrders.length === 0) return
  
  // Use requestAnimationFrame for smooth rendering
  requestAnimationFrame(() => {
    const canvas = document.querySelector(`[ref="miniChart-${orderId}"]`)
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // Destroy existing chart if it exists
    const existingChart = Chart.getChart(canvas)
    if (existingChart) {
      existingChart.destroy()
      componentCharts.value.delete(existingChart)
    }
    
    // Improved data sampling with peak detection
    const maxDataPoints = 20
    let processedSubOrders = subOrders
    
    if (subOrders.length > maxDataPoints) {
      // Smart sampling: include peaks and evenly distributed points
      processedSubOrders = smartSampleData(subOrders, maxDataPoints)
    }
    
    // Sort sub-orders by scheduled time
    const sortedSubOrders = processedSubOrders.sort((a, b) => new Date(a.scheduled_time) - new Date(b.scheduled_time))
    
    // Prepare simplified data for mini chart
    const labels = sortedSubOrders.map((_, index) => index + 1)
    const cumulativeData = []
    let runningTotal = 0
    
    sortedSubOrders.forEach(subOrder => {
      if (subOrder.status === 'Completed') {
        runningTotal += subOrder.quantity
      }
      cumulativeData.push(runningTotal)
    })
    
    const targetTotal = sortedSubOrders.reduce((sum, sub) => sum + sub.quantity, 0)
    
    // Create optimized chart configuration
    const chartConfig = {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Progress',
            data: cumulativeData,
            borderColor: 'rgba(34, 197, 94, 1)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            borderWidth: isMobile.value ? 1 : 2,
            fill: true,
            tension: 0.1,
            pointRadius: isMobile.value ? 0 : 1,
            pointHoverRadius: isMobile.value ? 2 : 3
          },
          {
            label: 'Target',
            data: new Array(labels.length).fill(targetTotal),
            borderColor: 'rgba(156, 163, 175, 0.5)',
            borderWidth: 1,
            borderDash: [2, 2],
            fill: false,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: false, // Disable responsive for better performance
        maintainAspectRatio: false,
        animation: {
          duration: isMobile.value ? 0 : 200 // Disable animation on mobile
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            enabled: !isMobile.value, // Disable tooltips on mobile for performance
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                if (context.datasetIndex === 0) {
                  return `Progress: ${context.parsed.y.toLocaleString()}`
                } else {
                  return `Target: ${context.parsed.y.toLocaleString()}`
                }
              }
            }
          }
        },
        scales: {
          x: {
            display: false
          },
          y: {
            display: false,
            beginAtZero: true
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    }
    
    // @ts-ignore - Chart.js auto-import doesn't provide proper types
    const chart = new Chart(ctx, chartConfig)
    componentCharts.value.add(chart)
  })
}

// Smart data sampling with peak detection
const smartSampleData = (data, maxPoints) => {
  if (data.length <= maxPoints) return data
  
  // Always include first and last points
  const sampled = [data[0], data[data.length - 1]]
  
  // Find peaks (high values)
  const peaks = []
  for (let i = 1; i < data.length - 1; i++) {
    if (data[i].quantity > data[i - 1].quantity && data[i].quantity > data[i + 1].quantity) {
      peaks.push(data[i])
    }
  }
  
  // Add peaks to sample
  sampled.push(...peaks.slice(0, Math.floor(maxPoints / 3)))
  
  // Fill remaining slots with evenly distributed points
  const remainingSlots = maxPoints - sampled.length
  if (remainingSlots > 0) {
    const step = Math.floor(data.length / remainingSlots)
    for (let i = 1; i < remainingSlots - 1; i++) {
      const index = i * step
      if (index < data.length - 1 && !sampled.includes(data[index])) {
        sampled.push(data[index])
      }
    }
  }
  
  // Sort by time and return
  return sampled.sort((a, b) => new Date(a.scheduled_time) - new Date(b.scheduled_time))
    .slice(0, maxPoints)
}

// Sub-orders chart rendering
const renderSubOrdersChart = () => {
  if (!subOrdersChart.value || !selectedOrder.value?.sub_orders) return
  
  // Destroy existing chart
  if (subOrdersChartInstance.value) {
    subOrdersChartInstance.value.destroy()
    subOrdersChartInstance.value = null
  }
  
  nextTick(() => {
    const ctx = subOrdersChart.value.getContext('2d')
    if (!ctx) return
    
    // Sort sub-orders by scheduled time
    const sortedSubOrders = [...selectedOrder.value.sub_orders].sort((a, b) => 
      new Date(a.scheduled_time) - new Date(b.scheduled_time)
    )
    
    // Prepare data for chart
    const labels = sortedSubOrders.map((sub, index) => {
      const time = new Date(sub.scheduled_time)
      return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })
    
    const progressData = []
    const targetData = []
    let runningTotal = 0
    
    sortedSubOrders.forEach(subOrder => {
      runningTotal += subOrder.quantity
      targetData.push(runningTotal)
      
      if (subOrder.status === 'Completed') {
        progressData.push(runningTotal)
      } else {
        progressData.push(null) // Show gap for incomplete orders
      }
    })
    
    // @ts-ignore - Chart.js auto-import doesn't provide proper types
    subOrdersChartInstance.value = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Completed Progress',
            data: progressData,
            borderColor: 'rgba(34, 197, 94, 1)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            borderWidth: 3,
            fill: false,
            tension: 0.1,
            pointRadius: 4,
            pointHoverRadius: 6
          },
          {
            label: 'Target Progress',
            data: targetData,
            borderColor: 'rgba(156, 163, 175, 0.8)',
            borderWidth: 2,
            borderDash: [5, 5],
            fill: false,
            pointRadius: 3,
            pointHoverRadius: 5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            enabled: true,
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                if (context.parsed.y !== null) {
                  return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`
                }
                return context.dataset.label + ': Pending'
              }
            }
          }
        },
        scales: {
          x: {
            display: true,
            title: {
              display: true,
              text: 'Scheduled Time'
            }
          },
          y: {
            display: true,
            beginAtZero: true,
            title: {
              display: true,
              text: 'Cumulative Quantity'
            },
            ticks: {
              callback: function(value) {
                return value.toLocaleString()
              }
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    })
  })
}

// Auto-refresh order details with optimized performance
const orderAutoRefreshIntervals = new Map()

const startOrderAutoRefresh = (orderId) => {
  // Clear existing interval for this order (prevent race conditions)
  stopOrderAutoRefresh(orderId)
  
  // Start new interval with longer delay for performance
  const interval = setInterval(async () => {
    if (selectedOrder.value && selectedOrder.value.id === orderId) {
      try {
        const response = await apiGet(`/growth/${orderId}`)
        if (response.success) {
          const newOrder = response.order
          // Efficient comparison using version or timestamp
          const currentVersion = selectedOrder.value.updated_at || selectedOrder.value.last_modified
          const newVersion = newOrder.updated_at || newOrder.last_modified
          
          if (currentVersion !== newVersion) {
            selectedOrder.value = newOrder
            console.log('Auto-refreshed order status')
            // Update sub-orders chart when data changes
            await nextTick()
            renderSubOrdersChart()
          }
        }
      } catch (error) {
        console.error('Auto-refresh error:', error)
      }
    }
  }, 15000) // Increased to 15 seconds for better performance
  
  orderAutoRefreshIntervals.set(orderId, interval)
}

const stopOrderAutoRefresh = (orderId) => {
  if (orderAutoRefreshIntervals.has(orderId)) {
    clearInterval(orderAutoRefreshIntervals.get(orderId))
    orderAutoRefreshIntervals.delete(orderId)
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  // Stop auto-refresh when modal is closed
  if (selectedOrder.value) {
    stopOrderAutoRefresh(selectedOrder.value.id)
  }
  selectedOrder.value = null
}

const toggleSubOrderSelection = (subOrderId) => {
  const index = selectedSubOrders.value.indexOf(subOrderId)
  if (index > -1) {
    selectedSubOrders.value.splice(index, 1)
  } else {
    selectedSubOrders.value.push(subOrderId)
  }
}

const updatePreview = async () => {
  try {
    console.log('Updating preview with form data:', createForm)
    
    // Proper ISO date formatting
    const startDateTime = createForm.start_date && createForm.start_time 
      ? new Date(`${createForm.start_date}T${createForm.start_time}:00`).toISOString()
      : new Date().toISOString()
    
    const requestData = {
      start_time: startDateTime,
      total_quantity: createForm.total_quantity,
      duration_minutes: createForm.duration_minutes,
      step_interval: createForm.step_interval,
      graph_type: createForm.graph_type,
      tolerance_percent: createForm.tolerance_percent,
      seed: createForm.seed || null
    }
    
    console.log('Sending preview request:', requestData)
    
    const response = await apiPost('/growth/preview', requestData)
    console.log('Preview response:', response)
    
    if (response.success) {
      previewData.value = response.preview
      console.log('Preview data set:', previewData.value)
      await nextTick()
      renderChart()
    } else {
      console.error('Preview failed:', response)
      showError('Failed to generate preview: ' + (response.detail || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error generating preview:', error)
    showError('Failed to generate preview: ' + error.message)
  }
}

const renderChart = () => {
  if (!previewChart.value || !previewData.value) return
  
  // Destroy existing chart
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
  
  // Wait for DOM to be ready
  nextTick(() => {
    // Check if canvas context is available
    const ctx = previewChart.value.getContext('2d')
    if (!ctx) {
      console.error('Canvas context not available')
      return
    }
    
    // Create proper date labels based on the input start time
    const startDateTime = new Date(`${createForm.start_date}T${createForm.start_time}:00`)
    const labels = previewData.value.timestamps.map((ts, index) => {
      const time = new Date(ts)
      const timeDiff = (time - startDateTime) / (1000 * 60) // Difference in minutes
      if (timeDiff < 60) {
        return `${Math.round(timeDiff)}m`
      } else if (timeDiff < 1440) { // Less than 24 hours
        return `${Math.round(timeDiff / 60)}h`
      } else {
        return `${Math.round(timeDiff / 1440)}d`
      }
    })
    
    // @ts-ignore - Chart.js auto-import doesn't provide proper types
    chartInstance.value = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Quantity per Step',
            data: previewData.value.quantities,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.1
          },
          {
            label: 'Cumulative Total',
            data: previewData.value.cumulative,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            tension: 0.1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `${createForm.graph_type} Growth Pattern (Starting: ${createForm.start_time})` 
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    })
  })
}

const createOrder = async () => {
  creating.value = true
  validationErrors.value = []
  
  try {
    console.log('Creating order with form data:', createForm)
    
    // Comprehensive validation
    const errors = validateCreateForm()
    if (errors.length > 0) {
      validationErrors.value = errors
      showError(errors.join(', '))
      creating.value = false
      return
    }
    
    // Proper ISO date formatting
    const startDateTime = createForm.start_date && createForm.start_time 
      ? new Date(`${createForm.start_date}T${createForm.start_time}:00`).toISOString()
      : new Date().toISOString()
    
    // SECURE: Remove API key from client-side data
    const requestData = {
      name: createForm.name,
      target_link: createForm.target_link,
      service_id: createForm.service_id,
      service_type: createForm.service_type,
      start_time: startDateTime,
      total_quantity: createForm.total_quantity,
      duration_minutes: createForm.duration_minutes,
      step_interval: createForm.step_interval,
      graph_type: createForm.graph_type,
      tolerance_percent: createForm.tolerance_percent,
      seed: createForm.seed || null,
      api_server_id: createForm.api_server_id, // Server-side only
      sequential_placement: createForm.sequential_placement
      // SECURITY: Never send API key from client
    }
    
    console.log('Sending create request:', requestData)
    
    const data = await apiPost('/growth/create', requestData)
    console.log('Create response:', data)
    
    if (data.success) {
      showSuccess('Growth order created successfully!')
      showCreateModal.value = false
      resetCreateForm()
      refreshOrders()
    } else {
      console.error('Create failed:', data)
      showError('Failed to create order: ' + (data.detail || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error creating order:', error)
    showError('Failed to create order: ' + error.message)
  } finally {
    creating.value = false
  }
}

// Comprehensive form validation
const validateCreateForm = () => {
  const errors = []
  
  // Required fields
  if (!createForm.name?.trim()) {
    errors.push('Order name is required')
  }
  
  if (!createForm.target_link?.trim()) {
    errors.push('Target link is required')
  } else if (!isValidUrl(createForm.target_link)) {
    errors.push('Invalid target link format')
  }
  
  if (!createForm.service_id?.trim()) {
    errors.push('Service ID is required')
  }
  
  if (!createForm.start_date) {
    errors.push('Start date is required')
  }
  
  if (!createForm.start_time) {
    errors.push('Start time is required')
  }
  
  // Numeric validations
  if (!createForm.total_quantity || createForm.total_quantity < 100) {
    errors.push('Total quantity must be at least 100')
  }
  
  if (!createForm.duration_minutes || createForm.duration_minutes < 60) {
    errors.push('Duration must be at least 60 minutes')
  }
  
  if (!createForm.step_interval || createForm.step_interval < 1) {
    errors.push('Step interval must be at least 1 minute')
  }
  
  if (createForm.tolerance_percent !== undefined && 
      (createForm.tolerance_percent < 0 || createForm.tolerance_percent > 50)) {
    errors.push('Tolerance must be between 0 and 50 percent')
  }
  
  // Date validation
  const startDateTime = new Date(`${createForm.start_date}T${createForm.start_time}:00`)
  if (startDateTime <= new Date()) {
    errors.push('Start time must be in the future')
  }
  
  return errors
}

// URL validation helper
const isValidUrl = (url) => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

const pauseOrder = async (order) => {
  try {
    const data = await apiPost(`/growth/${order.id}/pause`)
    if (data.success) {
      showSuccess('Order paused successfully!')
      refreshOrders()
    } else {
      showError('Failed to pause order: ' + (data.detail || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error pausing order:', error)
    showError('Failed to pause order: ' + error.message)
  }
}

const resumeOrder = async (order) => {
  try {
    const data = await apiPost(`/growth/${order.id}/resume`)
    if (data.success) {
      showSuccess('Order resumed successfully!')
      refreshOrders()
    } else {
      showError('Failed to resume order: ' + (data.detail || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error resuming order:', error)
    showError('Failed to resume order: ' + error.message)
  }
}

const deleteOrder = async (order) => {
  const confirmed = await showConfirm(
    `Are you sure you want to delete "${order.name}"?`,
    'Delete Order',
    'Cancel'
  )
  
  if (!confirmed) {
    return
  }
  
  try {
    const data = await apiPost(`/growth/${order.id}/delete`)
    if (data.success) {
      showSuccess('Order deleted successfully!')
      refreshOrders()
    } else {
      showError('Failed to delete order: ' + (data.detail || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error deleting order:', error)
    showError('Failed to delete order: ' + error.message)
  }
}

const fetchOrderStatus = async () => {
  if (!selectedOrder.value) return
  
  try {
    const data = await apiPost(`/growth/${selectedOrder.value.id}/fetch_status`)
    if (data.success) {
      showSuccess(data.message)
      // Refresh the order details
      await viewOrder(selectedOrder.value)
    } else {
      showError('Failed to fetch status: ' + (data.detail || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error fetching status:', error)
    showError('Failed to fetch status: ' + error.message)
  }
}

const toggleAllSubOrders = () => {
  if (allSubOrdersSelected.value) {
    selectedSubOrders.value = []
  } else {
    selectedSubOrders.value = selectedOrder.value.sub_orders.map(so => so.id)
  }
}

const selectAllSubOrders = () => {
  selectedSubOrders.value = selectedOrder.value.sub_orders.map(so => so.id)
}

const deselectAllSubOrders = () => {
  selectedSubOrders.value = []
}

const runSelectedSubOrders = async () => {
  if (selectedSubOrders.value.length === 0) return
  
  const confirmed = await showConfirm(
    `Run ${selectedSubOrders.value.length} sub-orders NOW?`,
    'Run Sub-orders',
    'Cancel'
  )
  
  if (!confirmed) {
    return
  }
  
  for (const subOrderId of selectedSubOrders.value) {
    try {
      await runSubOrderNow({ id: subOrderId })
    } catch (error) {
      console.error(`Error running sub-order ${subOrderId}:`, error)
    }
  }
  
  showSuccess(`Started execution of ${selectedSubOrders.value.length} sub-orders`)
  selectedSubOrders.value = []
}

const runSubOrderNow = async (subOrder) => {
  try {
    // SECURITY: Remove API key from client-side request
    const data = await apiPost(`/growth/${selectedOrder.value.id}/suborders/${subOrder.id}/run_now`, {
      api_server_id: createForm.api_server_id // Server-side only
      // SECURITY: Never send API key from client
    })
    if (data.success) {
      showSuccess('Sub-order execution started!')
    } else {
      showError('Failed to start sub-order: ' + (data.detail || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error running sub-order:', error)
    showError('Failed to start sub-order: ' + error.message)
  }
}

const calculateCumulative = (index) => {
  if (!selectedOrder.value) return 0
  let total = 0
  for (let i = 0; i <= index; i++) {
    total += selectedOrder.value.sub_orders[i].quantity
  }
  return total
}

const resetCreateForm = () => {
  Object.assign(createForm, {
    name: '',
    target_link: '',
    service_id: '',
    service_type: 'Views',
    start_date: new Date().toISOString().split('T')[0], // Today's date
    start_time: '09:00',
    total_quantity: 10000,
    duration_minutes: 1440,
    step_interval: 60,
    graph_type: 'Organic',
    tolerance_percent: 10,
    seed: null,
    api_server_id: '',
    sequential_placement: false
  })
  previewData.value = null
}

// API Server Management
const apiServers = ref([])
const userApiKeys = ref({})

const loadApiServers = async () => {
  try {
    const response = await apiGet('/api-management/servers')
    apiServers.value = response.servers || []
    
    // Load user's API keys
    const keysData = await apiGet('/api-management/user/api-keys')
    userApiKeys.value = keysData.api_keys || {}
  } catch (error) {
    console.error('Error loading API servers:', error)
  }
}

const getMaskedApiKey = (serverId) => {
  const key = userApiKeys.value[serverId]
  if (!key || key.length < 4) return ''
  return key.substring(0, 4) + '•'.repeat(Math.max(8, key.length - 4))
}

const updateApiKeyDisplay = () => {
  // This will trigger the computed display update
}

const formatStatus = (status) => {
  return status.replace(/_/g, ' ')
}

const getStatusClass = (status) => {
  const baseClass = 'status-badge'
  const statusClass = status.toLowerCase().replace(/_/g, '-')
  return `${baseClass} ${statusClass}`
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return 'N/A'
  return new Date(dateTimeString).toLocaleString()
}

const calculateRate = (order) => {
  if (!order.total_quantity || !order.duration_minutes) {
    return 0
  }
  
  // If duration is in minutes, convert to hours
  const durationInHours = order.duration_minutes / 60
  
  // Calculate rate per hour
  const rate = order.total_quantity / durationInHours
  
  // Round to nearest whole number
  return Math.round(rate)
}

onMounted(async () => {
  // Check if mobile and setup resize listener
  checkMobile()
  window.addEventListener('resize', checkMobile)
  
  // Setup intersection observer for lazy loading
  setupIntersectionObserver()
  
  // Load initial data
  await loadUserAPIKeys()
  await loadApiServers()
  refreshOrders()
})

onUnmounted(() => {
  // Cleanup
  window.removeEventListener('resize', checkMobile)
  
  // Clear intersection observer
  if (intersectionObserver.value) {
    intersectionObserver.value.disconnect()
  }
  
  // Clear refresh debounce timer
  if (refreshDebounceTimer.value) {
    clearTimeout(refreshDebounceTimer.value)
  }
  
  // Clear all auto-refresh intervals
  orderAutoRefreshIntervals.forEach(interval => clearInterval(interval))
  orderAutoRefreshIntervals.clear()
  
  // Destroy chart instances
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
  if (subOrdersChartInstance.value) {
    subOrdersChartInstance.value.destroy()
  }
  
  // SECURITY: Destroy only this component's charts
  componentCharts.value.forEach(chart => {
    try {
      chart.destroy()
    } catch (error) {
      console.error('Error destroying chart:', error)
    }
  })
  componentCharts.value.clear()
})
</script>

<style scoped>
.growth-order-dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

.dashboard-header {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.dashboard-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.dashboard-header h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.dashboard-header p {
  margin: 0 0 1.5rem 0;
  color: var(--text-secondary);
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.order-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}

/* Liquid Glass Button Styles */
.liquid-glass-btn {
  padding: 0.875rem 1.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 44px;
  min-width: 140px;
  justify-content: center;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 2px 8px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.liquid-glass-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 255, 255, 0.2), 
    transparent
  );
  transition: left 0.5s ease;
}

.liquid-glass-btn:hover::before {
  left: 100%;
}

.liquid-glass-btn:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 12px 40px rgba(0, 0, 0, 0.15),
    0 4px 12px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.liquid-glass-btn:active {
  transform: translateY(0);
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.1),
    0 2px 6px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* Button Variants */
.primary-btn {
  background: linear-gradient(135deg, 
    rgba(59, 130, 246, 0.15),
    rgba(37, 99, 235, 0.25)
  );
  color: #60a5fa;
  border-color: rgba(96, 165, 250, 0.2);
}

.primary-btn:hover {
  background: linear-gradient(135deg, 
    rgba(59, 130, 246, 0.25),
    rgba(37, 99, 235, 0.35)
  );
  border-color: rgba(96, 165, 250, 0.4);
  color: #93c5fd;
}

.warning-btn {
  background: linear-gradient(135deg, 
    rgba(245, 158, 11, 0.15),
    rgba(217, 119, 6, 0.25)
  );
  color: #fbbf24;
  border-color: rgba(251, 191, 36, 0.2);
}

.warning-btn:hover {
  background: linear-gradient(135deg, 
    rgba(245, 158, 11, 0.25),
    rgba(217, 119, 6, 0.35)
  );
  border-color: rgba(251, 191, 36, 0.4);
  color: #fcd34d;
}

.success-btn {
  background: linear-gradient(135deg, 
    rgba(34, 197, 94, 0.15),
    rgba(22, 163, 74, 0.25)
  );
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.2);
}

.success-btn:hover {
  background: linear-gradient(135deg, 
    rgba(34, 197, 94, 0.25),
    rgba(22, 163, 74, 0.35)
  );
  border-color: rgba(74, 222, 128, 0.4);
  color: #86efac;
}

.danger-btn {
  background: linear-gradient(135deg, 
    rgba(239, 68, 68, 0.15),
    rgba(220, 38, 38, 0.25)
  );
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.2);
}

.danger-btn:hover {
  background: linear-gradient(135deg, 
    rgba(239, 68, 68, 0.25),
    rgba(220, 38, 38, 0.35)
  );
  border-color: rgba(248, 113, 113, 0.4);
  color: #fca5a5;
}

.orders-section {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.orders-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.orders-section h3 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 1.5rem;
  transition: all 0.3s ease;
}

.mobile-grid {
  grid-template-columns: 1fr;
  gap: 1rem;
}

.order-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.order-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.order-card:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-4px);
  box-shadow: var(--glass-shadow-xl);
}

.order-card.selected {
  background: var(--glass-bg-hover);
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: var(--glass-shadow-lg);
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
  font-size: 1.1rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.order-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.order-status.active {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.order-status.paused {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.order-status.completed {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.order-status.failed {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.order-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-weight: 500;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.value {
  font-weight: 600;
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.order-progress {
  margin-bottom: 1rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(16, 185, 129, 0.8), rgba(6, 182, 212, 0.8));
  transition: width 0.3s ease;
  border-radius: 3px;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.3);
}

.progress-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.order-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-xl);
  -webkit-backdrop-filter: var(--glass-blur-xl);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: var(--glass-shadow-xl);
}

.modal-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Mini Chart Styles */
.mini-graph-container {
  margin-top: 1rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.mini-chart {
  width: 100%;
  height: 60px;
}

/* Order Preview Styles */
.order-preview {
  margin-top: 0.75rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.75rem;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.preview-value {
  color: var(--text-primary);
  font-weight: 600;
}

/* Sub-orders Chart Styles */
.sub-orders-graph {
  margin-top: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sub-orders-graph h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.sub-orders-chart-container {
  position: relative;
  height: 200px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  padding: 1rem;
}

.sub-orders-chart-container canvas {
  max-height: 100%;
}

@media (max-width: 768px) {
  .growth-order-dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    padding: 1rem;
    text-align: center;
  }
  
  .dashboard-header h2 {
    font-size: 1.2rem;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .orders-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .order-card {
    padding: 1rem;
  }
  
  .mobile-card {
    border-radius: 12px;
  }
  
  .mobile-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .header-left {
    width: 100%;
  }
  
  .header-left h4 {
    font-size: 1rem;
    margin-bottom: 0.25rem;
  }
  
  .mobile-details {
    gap: 0.5rem;
  }
  
  .mobile-details .detail {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .mobile-preview {
    font-size: 0.7rem;
  }
  
  .mobile-actions {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .mobile-actions .btn {
    flex: 1;
    min-width: 80px;
    padding: 0.5rem;
    font-size: 0.8rem;
  }
  
  .modal-content {
    margin: 1rem;
    max-width: calc(100vw - 2rem);
    max-height: calc(100vh - 2rem);
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .sub-orders-table {
    font-size: 0.8rem;
  }
  
  .sub-orders-chart-container {
    height: 150px;
  }
}

.large-modal {
  width: 1200px;
  max-width: 95vw;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.3rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.btn-close {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--text-primary);
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.btn-close:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: scale(1.1);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.form-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.form-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.form-section h4 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  font-size: 0.9rem;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:invalid {
  border-color: rgba(239, 68, 68, 0.5);
}

.form-group input:invalid:focus {
  border-color: rgba(239, 68, 68, 0.8);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

.error-message {
  display: block;
  margin-top: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #ef4444;
  font-size: 0.8rem;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  animation: errorShake 0.3s ease-in-out;
}

@keyframes errorShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.form-group input::placeholder,
.form-group select::placeholder {
  color: var(--text-tertiary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.form-group select {
  cursor: pointer;
}

.form-group select option {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  padding: 0.5rem;
}

.api-key-display {
  position: relative;
}

.api-key-display .form-control {
  background: var(--glass-bg-tertiary);
  cursor: not-allowed;
  opacity: 0.8;
}

.form-text {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-tertiary);
  font-style: italic;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.preview-section {
  border-top: 1px solid var(--glass-border);
  padding-top: 2rem;
}

.preview-section h4 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.preview-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
}

.preview-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9rem;
}

.preview-stats span {
  color: var(--text-primary);
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.preview-stats strong {
  color: var(--text-primary);
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.chart-container {
  height: 400px;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.chart-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.order-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.bulk-actions {
  display: flex;
  gap: 0.5rem;
}

.sub-orders-table {
  overflow-x: auto;
}

.sub-orders-table table {
  width: 100%;
  border-collapse: collapse;
}

.sub-orders-table th,
.sub-orders-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.sub-orders-table th {
  background-color: #f9fafb;
  font-weight: 500;
  color: #374151;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.pending {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.running {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.failed_fatal,
.status-badge.retry_pending {
  background-color: #fee2e2;
  color: #991b1b;
}

/* Button styles */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4b5563;
}

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #059669;
}

.btn-warning {
  background-color: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background-color: #d97706;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #dc2626;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

/* Checkbox styling */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.checkbox-label input[type="checkbox"] {
  width: 1.2rem;
  height: 1.2rem;
  accent-color: #3b82f6;
  cursor: pointer;
}

.form-text {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
  line-height: 1.4;
}

/* Mini chart styles */
.mini-graph-container {
  margin-top: 0.5rem;
  padding: 0.25rem;
  background: #f9fafb;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
}

.mini-chart {
  max-width: 100%;
  height: auto;
}
</style>
