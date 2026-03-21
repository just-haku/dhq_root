<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>Analytics Dashboard</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>Comprehensive insights and performance metrics</p>
    
</div>

    <div class="page-actions">

      <button class="btn btn-outline" @click="refreshData">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 2 L13.5 9.5 L16.5 9.5 L16.5 12.5 L10.5 12.5 L10.5 6.5 L13.5 6.5 L21 14 L21 2 Z" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M3 22 L10.5 14.5 L7.5 14.5 L7.5 11.5 L13.5 11.5 L13.5 17.5 L10.5 17.5 L3 10 L3 22 Z" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        Refresh
      </button>
      <button class="btn btn-primary" @click="exportReport">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 15 L21 19 C21 20.1 20.1 21 19 21 L5 21 C3.9 21 3 20.1 3 19 L3 15" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M7 10 L12 15 L17 10" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M12 15 L12 3" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        Export Report
      </button>
    
</div>

    <div class="analytics-content">
      <!-- Date Range Selector -->
      <div class="date-range-selector">
        <div class="range-options">
          <button 
            v-for="range in dateRanges" 
            :key="range.value"
            class="range-btn"
            :class="{ active: selectedRange === range.value }"
            @click="selectedRange = range.value"
          >
            {{ range.label }}
          </button>
        </div>
        <div class="custom-range">
          <input type="date" v-model="customStartDate" class="date-input" />
          <span>to</span>
          <input type="date" v-model="customEndDate" class="date-input" />
        </div>
      </div>

      <!-- Key Metrics Overview -->
      <div class="metrics-overview">
        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 17 L9 11 L13 15 L21 7" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="21" cy="7" r="2" fill="currentColor"/>
              </svg>
            </div>
            <span class="metric-title">Total Revenue</span>
          </div>
          <div class="metric-value">${{ formatNumber(totalRevenue) }}</div>
          <div class="metric-change positive">+{{ revenueGrowth }}% vs last period</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M12 6 L12 12 L16 16" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <span class="metric-title">Active Users</span>
          </div>
          <div class="metric-value">{{ formatNumber(activeUsers) }}</div>
          <div class="metric-change positive">+{{ userGrowth }}% vs last period</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M3 9 L21 9 M3 15 L21 15" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <span class="metric-title">Conversion Rate</span>
          </div>
          <div class="metric-value">{{ conversionRate }}%</div>
          <div class="metric-change negative">-{{ conversionChange }}% vs last period</div>
        </div>

        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
                <path d="M12 2 L12 7 M12 17 L12 22 M2 12 L7 12 M17 12 L22 12" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <span class="metric-title">Avg. Session Duration</span>
          </div>
          <div class="metric-value">{{ avgSessionDuration }}m</div>
          <div class="metric-change positive">+{{ sessionChange }}% vs last period</div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-grid">
        <!-- Revenue Chart -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>Revenue Trend</h3>
            <div class="chart-controls">
              <select v-model="revenueChartType" class="chart-select">
                <option value="line">Line Chart</option>
                <option value="bar">Bar Chart</option>
                <option value="area">Area Chart</option>
              </select>
            </div>
          </div>
          <div class="chart-container">
            <div class="chart-placeholder">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 17 L9 11 L13 15 L21 7" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="21" cy="7" r="2" fill="currentColor"/>
              </svg>
              <p>Revenue chart visualization</p>
            </div>
          </div>
        </div>

        <!-- User Activity Chart -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>User Activity</h3>
            <div class="chart-controls">
              <select v-model="activityChartType" class="chart-select">
                <option value="heatmap">Heatmap</option>
                <option value="timeline">Timeline</option>
                <option value="distribution">Distribution</option>
              </select>
            </div>
          </div>
          <div class="chart-container">
            <div class="chart-placeholder">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M12 6 L12 12 L16 16" stroke="currentColor" stroke-width="2"/>
              </svg>
              <p>User activity visualization</p>
            </div>
          </div>
        </div>

        <!-- Traffic Sources -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>Traffic Sources</h3>
            <div class="chart-controls">
              <button class="btn btn-sm btn-outline">Details</button>
            </div>
          </div>
          <div class="chart-container">
            <div class="traffic-sources">
              <div v-for="source in trafficSources" :key="source.name" class="source-item">
                <div class="source-info">
                  <span class="source-name">{{ source.name }}</span>
                  <span class="source-percentage">{{ source.percentage }}%</span>
                </div>
                <div class="source-bar">
                  <div class="source-fill" :style="{ width: source.percentage + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Pages -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>Top Pages</h3>
            <div class="chart-controls">
              <button class="btn btn-sm btn-outline">View All</button>
            </div>
          </div>
          <div class="chart-container">
            <div class="top-pages">
              <div v-for="page in topPages" :key="page.path" class="page-item">
                <div class="page-info">
                  <span class="page-path">{{ page.path }}</span>
                  <span class="page-views">{{ formatNumber(page.views) }} views</span>
                </div>
                <div class="page-trend" :class="page.trend">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7 14 L12 9 L17 14" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                  {{ page.change }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Tables -->
      <div class="tables-section">
        <!-- Recent Transactions -->
        <div class="table-card">
          <div class="table-header">
            <h3>Recent Transactions</h3>
            <div class="table-controls">
              <input type="text" v-model="transactionSearch" placeholder="Search transactions..." class="search-input" />
              <button class="btn btn-sm btn-primary">Export</button>
            </div>
          </div>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Date</th>
                  <th>Customer</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="transaction in filteredTransactions" :key="transaction.id">
                  <td>{{ transaction.id }}</td>
                  <td>{{ formatDate(transaction.date) }}</td>
                  <td>{{ transaction.customer }}</td>
                  <td>${{ transaction.amount }}</td>
                  <td>
                    <span class="status-badge" :class="transaction.status">
                      {{ transaction.status }}
                    </span>
                  </td>
                  <td>
                    <button class="btn-icon" title="View Details">
                      <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                        <circle cx="12" cy="12" r="3" fill="currentColor"/>
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- User Segments -->
        <div class="table-card">
          <div class="table-header">
            <h3>User Segments</h3>
            <div class="table-controls">
              <button class="btn btn-sm btn-outline">Create Segment</button>
            </div>
          </div>
          <div class="table-container">
            <div class="segments-grid">
              <div v-for="segment in userSegments" :key="segment.name" class="segment-card">
                <div class="segment-header">
                  <h4>{{ segment.name }}</h4>
                  <span class="segment-size">{{ segment.size }} users</span>
                </div>
                <div class="segment-metrics">
                  <div class="segment-metric">
                    <span class="metric-label">Engagement</span>
                    <span class="metric-value">{{ segment.engagement }}%</span>
                  </div>
                  <div class="segment-metric">
                    <span class="metric-label">Revenue</span>
                    <span class="metric-value">${{ segment.revenue }}</span>
                  </div>
                </div>
                <div class="segment-actions">
                  <button class="btn btn-sm btn-outline">View</button>
                  <button class="btn btn-sm btn-outline">Edit</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Reactive state
const selectedRange = ref('30d')
const customStartDate = ref('')
const customEndDate = ref('')
const revenueChartType = ref('line')
const activityChartType = ref('heatmap')
const transactionSearch = ref('')

// Date ranges
const dateRanges = [
  { value: '7d', label: '7 Days' },
  { value: '30d', label: '30 Days' },
  { value: '90d', label: '90 Days' },
  { value: '1y', label: '1 Year' },
  { value: 'custom', label: 'Custom' }
]

// Mock data
const totalRevenue = ref(1250000)
const revenueGrowth = ref(23)
const activeUsers = ref(45678)
const userGrowth = ref(15)
const conversionRate = ref(3.2)
const conversionChange = ref(0.8)
const avgSessionDuration = ref(12)
const sessionChange = ref(5)

const trafficSources = ref([
  { name: 'Direct', percentage: 35 },
  { name: 'Organic Search', percentage: 28 },
  { name: 'Social Media', percentage: 20 },
  { name: 'Referral', percentage: 12 },
  { name: 'Email', percentage: 5 }
])

const topPages = ref([
  { path: '/dashboard', views: 45678, change: 12, trend: 'positive' },
  { path: '/growth-orders', views: 23456, change: 8, trend: 'positive' },
  { path: '/shop', views: 18923, change: -3, trend: 'negative' },
  { path: '/media-gallery', views: 15678, change: 15, trend: 'positive' },
  { path: '/analytics', views: 12345, change: 22, trend: 'positive' }
])

const transactions = ref([
  { id: 'TRX001', date: new Date('2024-01-20'), customer: 'John Doe', amount: 1250, status: 'completed' },
  { id: 'TRX002', date: new Date('2024-01-20'), customer: 'Jane Smith', amount: 890, status: 'pending' },
  { id: 'TRX003', date: new Date('2024-01-19'), customer: 'Bob Johnson', amount: 2100, status: 'completed' },
  { id: 'TRX004', date: new Date('2024-01-19'), customer: 'Alice Brown', amount: 450, status: 'failed' },
  { id: 'TRX005', date: new Date('2024-01-18'), customer: 'Charlie Wilson', amount: 3200, status: 'completed' }
])

const userSegments = ref([
  { name: 'New Users', size: 1234, engagement: 45, revenue: 12500 },
  { name: 'Active Users', size: 5678, engagement: 78, revenue: 89000 },
  { name: 'Premium Users', size: 345, engagement: 92, revenue: 156000 },
  { name: 'Inactive Users', size: 2345, engagement: 12, revenue: 3400 }
])

// Computed properties
const filteredTransactions = computed(() => {
  if (!transactionSearch.value) return transactions.value
  
  const query = transactionSearch.value.toLowerCase()
  return transactions.value.filter(t => 
    t.id.toLowerCase().includes(query) ||
    t.customer.toLowerCase().includes(query) ||
    t.status.toLowerCase().includes(query)
  )
})

// Methods
const formatNumber = (num) => {
  return num.toLocaleString()
}

const formatDate = (date) => {
  return date.toLocaleDateString()
}

const refreshData = () => {
  console.log('Refreshing analytics data...')
  // Simulate data refresh
  totalRevenue.value += Math.random() * 10000
  activeUsers.value += Math.floor(Math.random() * 100)
}

const exportReport = () => {
  console.log('Exporting analytics report...')
  // Simulate report export
}

onMounted(() => {
  console.log('Analytics component mounted')
})
</script>

<style scoped>
.analytics-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Date Range Selector */
.date-range-selector {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.range-options {
  display: flex;
  gap: 0.5rem;
}

.range-btn {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.3s ease;
}

.range-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

.range-btn.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
}

.custom-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-input {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 0.875rem;
}

/* Metrics Overview */
.metrics-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.metric-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.metric-card:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.metric-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.3));
  border: 1px solid rgba(96, 165, 250, 0.3);
  color: #60a5fa;
}

.metric-title {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
}

.metric-change {
  font-size: 0.875rem;
  font-weight: 600;
}

.metric-change.positive {
  color: #10b981;
}

.metric-change.negative {
  color: #ef4444;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.chart-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-header h3 {
  color: #f1f5f9;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.chart-select {
  padding: 0.375rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #f1f5f9;
  font-size: 0.75rem;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: #64748b;
}

.chart-placeholder .icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Traffic Sources */
.traffic-sources {
  width: 100%;
}

.source-item {
  margin-bottom: 1rem;
}

.source-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.source-name {
  color: #f1f5f9;
  font-size: 0.875rem;
}

.source-percentage {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 600;
}

.source-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.source-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* Top Pages */
.top-pages {
  width: 100%;
}

.page-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.page-item:last-child {
  border-bottom: none;
}

.page-info {
  flex: 1;
}

.page-path {
  display: block;
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 500;
}

.page-views {
  color: #94a3b8;
  font-size: 0.75rem;
}

.page-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.page-trend.positive {
  color: #10b981;
}

.page-trend.negative {
  color: #ef4444;
}

.page-trend .icon {
  width: 0.75rem;
  height: 0.75rem;
}

/* Tables Section */
.tables-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1.5rem;
}

.table-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.table-header h3 {
  color: #f1f5f9;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.table-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.search-input {
  padding: 0.375rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #f1f5f9;
  font-size: 0.75rem;
  width: 200px;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 0.75rem;
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table td {
  padding: 0.75rem;
  color: #f1f5f9;
  font-size: 0.875rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.btn-icon {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

.btn-icon .icon {
  width: 1rem;
  height: 1rem;
}

/* User Segments */
.segments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.segment-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
}

.segment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.segment-header h4 {
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
}

.segment-size {
  color: #94a3b8;
  font-size: 0.75rem;
}

.segment-metrics {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.segment-metric {
  display: flex;
  justify-content: space-between;
}

.metric-label {
  color: #94a3b8;
  font-size: 0.75rem;
}

.metric-value {
  color: #f1f5f9;
  font-size: 0.75rem;
  font-weight: 600;
}

.segment-actions {
  display: flex;
  gap: 0.5rem;
}

/* Buttons */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-outline {
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.icon {
  width: 1rem;
  height: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .date-range-selector {
    flex-direction: column;
    gap: 1rem;
  }
  
  .range-options {
    flex-wrap: wrap;
  }
  
  .metrics-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .tables-section {
    grid-template-columns: 1fr;
  }
  
  .segments-grid {
    grid-template-columns: 1fr;
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
