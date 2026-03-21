<template>
  <div class="analytics-dashboard">
    <div class="analytics-header">
      <h3>📊 Analytics Dashboard</h3>
      <div class="time-range-selector">
        <button 
          v-for="range in timeRanges" 
          :key="range.value"
          @click="selectedTimeRange = range.value"
          :class="{ active: selectedTimeRange === range.value }"
          class="range-btn"
        >
          {{ range.label }}
        </button>
      </div>
    </div>
    
    <!-- Overview Cards -->
    <div class="overview-grid">
      <div 
        v-for="metric in overviewMetrics" 
        :key="metric.key"
        class="metric-card"
        :class="metric.type"
      >
        <div class="metric-icon">{{ metric.icon }}</div>
        <div class="metric-content">
          <div class="metric-value">{{ formatNumber(metric.value) }}</div>
          <div class="metric-label">{{ metric.label }}</div>
          <div v-if="metric.change" class="metric-change" :class="metric.changeType">
            {{ metric.change > 0 ? '+' : '' }}{{ metric.change }}%
          </div>
        </div>
      </div>
    </div>
    
    <!-- Charts Section -->
    <div class="charts-section">
      <div class="chart-container">
        <h4>📈 Activity Trends</h4>
        <div class="chart-placeholder">
          <canvas ref="trendsChart" width="400" height="200"></canvas>
        </div>
      </div>
      
      <div class="chart-container">
        <h4>👥 User Distribution</h4>
        <div class="chart-placeholder">
          <canvas ref="distributionChart" width="400" height="200"></canvas>
        </div>
      </div>
    </div>
    
    <!-- Top Performers -->
    <div class="performers-section">
      <div class="performers-header">
        <h4>🏆 Top Performers</h4>
        <LiquidGlassDropdown trigger-text="KPI Balance" @close="loadTopPerformers">
          <button 
            v-for="metric in performerMetrics" 
            :key="metric.value"
            @click="performerMetric = metric.value; loadTopPerformers()"
            class="dropdown-item"
          >
            {{ metric.label }}
          </button>
        </LiquidGlassDropdown>
      </div>
      
      <div class="performers-list">
        <div 
          v-for="(performer, index) in topPerformers" 
          :key="performer.user.id"
          class="performer-item"
          :class="{ 'top-three': index < 3 }"
        >
          <div class="rank">
            <span v-if="index === 0">🥇</span>
            <span v-else-if="index === 1">🥈</span>
            <span v-else-if="index === 2">🥉</span>
            <span v-else>#{{ index + 1 }}</span>
          </div>
          <div class="performer-info">
            <div class="performer-name">{{ performer.user.display_name || performer.user.username }}</div>
            <div class="performer-details">
              <span class="performer-value">{{ formatNumber(performer.value) }}</span>
              <span v-if="performer.metadata.level" class="performer-level">
                Level {{ performer.metadata.level }}
              </span>
            </div>
          </div>
          <div class="performer-avatar">
            {{ performer.user.display_name?.[0] || performer.user.username[0] || 'U' }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Engagement Metrics -->
    <div class="engagement-section">
      <h4>📊 Engagement Metrics</h4>
      <div class="engagement-grid">
        <div class="engagement-item">
          <div class="engagement-label">Daily Active Rate</div>
          <div class="engagement-value">{{ analytics.engagement?.daily_active_rate || 0 }}%</div>
          <div class="engagement-bar">
            <div 
              class="engagement-fill" 
              :style="{ width: (analytics.engagement?.daily_active_rate || 0) + '%' }"
            ></div>
          </div>
        </div>
        
        <div class="engagement-item">
          <div class="engagement-label">Weekly Active Rate</div>
          <div class="engagement-value">{{ analytics.engagement?.weekly_active_rate || 0 }}%</div>
          <div class="engagement-bar">
            <div 
              class="engagement-fill" 
              :style="{ width: (analytics.engagement?.weekly_active_rate || 0) + '%' }"
            ></div>
          </div>
        </div>
        
        <div class="engagement-item">
          <div class="engagement-label">Avg Tasks per User</div>
          <div class="engagement-value">{{ analytics.engagement?.avg_tasks_per_user || 0 }}</div>
          <div class="engagement-bar">
            <div 
              class="engagement-fill" 
              :style="{ width: Math.min((analytics.engagement?.avg_tasks_per_user || 0) * 10, 100) + '%' }"
            ></div>
          </div>
        </div>
        
        <div class="engagement-item">
          <div class="engagement-label">Avg Files per User</div>
          <div class="engagement-value">{{ analytics.engagement?.avg_files_per_user || 0 }}</div>
          <div class="engagement-bar">
            <div 
              class="engagement-fill" 
              :style="{ width: Math.min((analytics.engagement?.avg_files_per_user || 0) * 20, 100) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { apiGet } from '../../utils/api.js'
import LiquidGlassDropdown from '../UI/LiquidGlassDropdown.vue'

export default {
  name: 'AnalyticsDashboard',
  components: {
    LiquidGlassDropdown
  },
  setup() {
    const analytics = ref({})
    const topPerformers = ref([])
    const trends = ref([])
    const selectedTimeRange = ref(7)
    const performerMetric = ref('kpi')
    const trendsChart = ref(null)
    const distributionChart = ref(null)
    
    const performerMetrics = [
      { label: 'KPI Balance', value: 'kpi' },
      { label: 'Tasks Completed', value: 'tasks' },
      { label: 'Files Uploaded', value: 'files' }
    ]
    
    const timeRanges = [
      { label: '24h', value: 1 },
      { label: '7d', value: 7 },
      { label: '30d', value: 30 }
    ]
    
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token')
      return token ? { 'Authorization': `Bearer ${token}` } : {}
    }
    
    const loadAnalytics = async () => {
      try {
        const response = await apiGet('/activity/analytics/overview')
        
        if (response.ok) {
          analytics.value = await response.json()
        }
      } catch (error) {
        console.error('Error loading analytics:', error)
      }
    }
    
    const loadTrends = async () => {
      try {
        const response = await apiGet(`/activity/analytics/trends?days=${selectedTimeRange.value}`)
        
        if (response.ok) {
          trends.value = await response.json()
          await nextTick()
          renderTrendsChart()
        }
      } catch (error) {
        console.error('Error loading trends:', error)
      }
    }
    
    const loadTopPerformers = async () => {
      try {
        const response = await apiGet(`/activity/analytics/top-performers?metric=${performerMetric.value}&limit=10`)
        
        if (response.ok) {
          topPerformers.value = await response.json()
        }
      } catch (error) {
        console.error('Error loading top performers:', error)
      }
    }
    
    const renderTrendsChart = () => {
      if (!trendsChart.value || !trends.value.length) return
      
      const ctx = trendsChart.value.getContext('2d')
      
      // Simple line chart implementation
      const width = trendsChart.value.width
      const height = trendsChart.value.height
      const padding = 40
      
      // Clear canvas
      ctx.clearRect(0, 0, width, height)
      
      // Draw axes
      ctx.strokeStyle = '#e5e7eb'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(padding, padding)
      ctx.lineTo(padding, height - padding)
      ctx.lineTo(width - padding, height - padding)
      ctx.stroke()
      
      // Draw data lines
      const datasets = [
        { key: 'new_users', color: '#3b82f6', label: 'New Users' },
        { key: 'new_tasks', color: '#10b981', label: 'Tasks' },
        { key: 'new_files', color: '#f59e0b', label: 'Files' }
      ]
      
      datasets.forEach(dataset => {
        ctx.strokeStyle = dataset.color
        ctx.lineWidth = 2
        ctx.beginPath()
        
        trends.value.forEach((point, index) => {
          const x = padding + (index / (trends.value.length - 1)) * (width - 2 * padding)
          const y = height - padding - (point[dataset.key] / Math.max(...trends.value.map(p => p[dataset.key]))) * (height - 2 * padding)
          
          if (index === 0) {
            ctx.moveTo(x, y)
          } else {
            ctx.lineTo(x, y)
          }
        })
        
        ctx.stroke()
      })
    }
    
    const renderDistributionChart = () => {
      if (!distributionChart.value) return
      
      const ctx = distributionChart.value.getContext('2d')
      const width = distributionChart.value.width
      const height = distributionChart.value.height
      
      // Clear canvas
      ctx.clearRect(0, 0, width, height)
      
      // Simple pie chart for user roles
      const roles = [
        { name: 'OP', count: 1, color: '#ef4444' },
        { name: 'AD', count: analytics.value.users?.active_7d || 0, color: '#3b82f6' },
        { name: 'USER', count: (analytics.value.users?.total || 0) - 1 - (analytics.value.users?.active_7d || 0), color: '#10b981' }
      ]
      
      const total = roles.reduce((sum, role) => sum + role.count, 0)
      let currentAngle = 0
      
      roles.forEach(role => {
        const sliceAngle = (role.count / total) * 2 * Math.PI
        
        ctx.fillStyle = role.color
        ctx.beginPath()
        ctx.moveTo(width / 2, height / 2)
        ctx.arc(width / 2, height / 2, Math.min(width, height) / 3, currentAngle, currentAngle + sliceAngle)
        ctx.closePath()
        ctx.fill()
        
        currentAngle += sliceAngle
      })
    }
    
    const formatNumber = (num) => {
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toString()
    }
    
    const overviewMetrics = computed(() => {
      if (!analytics.value.users) return []
      
      return [
        {
          key: 'total_users',
          label: 'Total Users',
          value: analytics.value.users.total,
          icon: '👥',
          type: 'primary',
          change: analytics.value.users.growth_rate_7d,
          changeType: analytics.value.users.growth_rate_7d > 0 ? 'positive' : 'negative'
        },
        {
          key: 'active_users',
          label: 'Active Users',
          value: analytics.value.users.active_7d,
          icon: '✨',
          type: 'success',
          change: null,
          changeType: null
        },
        {
          key: 'total_projects',
          label: 'Projects',
          value: analytics.value.projects.total,
          icon: '📋',
          type: 'info',
          change: null,
          changeType: null
        },
        {
          key: 'total_files',
          label: 'Files',
          value: analytics.value.files.total,
          icon: '📄',
          type: 'warning',
          change: null,
          changeType: null
        },
        {
          key: 'total_kpi',
          label: 'Total KPI',
          value: analytics.value.arcade.total_kpi_earned,
          icon: '💎',
          type: 'special',
          change: null,
          changeType: null
        },
        {
          key: 'completion_rate',
          label: 'Task Completion',
          value: analytics.value.tasks.completion_rate,
          icon: '✅',
          type: 'success',
          change: null,
          changeType: null
        }
      ]
    })
    
    onMounted(async () => {
      await loadAnalytics()
      await loadTrends()
      await loadTopPerformers()
      await nextTick()
      renderTrendsChart()
      renderDistributionChart()
    })
    
    return {
      analytics,
      topPerformers,
      trends,
      selectedTimeRange,
      performerMetric,
      timeRanges,
      performerMetrics,
      overviewMetrics,
      trendsChart,
      distributionChart,
      loadAnalytics,
      loadTrends,
      loadTopPerformers,
      formatNumber
    }
  }
}
</script>

<style scoped>
.analytics-dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.analytics-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.analytics-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.time-range-selector {
  display: flex;
  gap: 0.5rem;
}

.range-btn {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.range-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.range-btn:hover::before {
  left: 100%;
}

.range-btn:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-1px);
}

.range-btn.active {
  background: var(--primary-gradient);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
  box-shadow: var(--glass-shadow-md);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--glass-shadow-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--glass-shadow-xl);
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.metric-card.revenue {
  border-left: 4px solid rgba(16, 185, 129, 0.6);
}

.metric-card.users {
  border-left: 4px solid rgba(59, 130, 246, 0.6);
}

.metric-card.orders {
  border-left: 4px solid rgba(236, 72, 153, 0.6);
}

.metric-card.conversion {
  border-left: 4px solid rgba(6, 182, 212, 0.6);
}

.metric-icon {
  font-size: 2rem;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--glass-shadow-md);
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metric-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.metric-change {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
}

.metric-change.positive {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.metric-change.negative {
  background: rgba(236, 72, 153, 0.2);
  color: #ec4899;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: var(--glass-shadow-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.chart-container:hover {
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-xl);
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.chart-container h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-placeholder {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1rem;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.chart-placeholder::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.top-products {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.top-products::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.top-products h4 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.product-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.product-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.product-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.product-item:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-1px);
}

.product-info {
  flex: 1;
}

.product-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.product-sales {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.product-revenue {
  font-weight: bold;
  color: var(--text-primary);
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.user-engagement {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.user-engagement::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.user-engagement h4 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.engagement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.engagement-item {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.engagement-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.engagement-item:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-1px);
}

.engagement-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.engagement-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.engagement-bar {
  height: 8px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
}

.engagement-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.8), rgba(16, 185, 129, 0.8));
  transition: width 0.3s ease;
  border-radius: 3px;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@media (max-width: 768px) {
  .analytics-dashboard {
    padding: 1rem;
  }
  
  .analytics-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .overview-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .engagement-grid {
    grid-template-columns: 1fr;
  }
}
</style>
