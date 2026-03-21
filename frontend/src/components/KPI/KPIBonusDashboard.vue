<template>
  <div class="kpi-bonus-dashboard">
    <div class="bonus-header">
      <h2>
        <i class="fas fa-gift"></i>
        Daily KPI Bonus
      </h2>
      <p class="subtitle">Claim your daily KPI rewards and track your progress</p>
    </div>

    <!-- Today's Bonus Card -->
    <div class="today-bonus-card">
      <div class="bonus-content">
        <div class="bonus-main">
          <div class="bonus-amount">
            <span class="amount">{{ todayBonus?.final_amount || 0 }}</span>
            <span class="currency">KPI</span>
          </div>
          <div class="bonus-details">
            <div class="day-info">Day {{ todayBonus?.day_number || 1 }} of 30</div>
            <div class="multiplier-info" v-if="todayBonus?.bonus_multiplier > 1">
              <i class="fas fa-times-circle"></i>
              {{ todayBonus?.bonus_multiplier }}x Multiplier
            </div>
            <div class="special-badges">
              <span v-if="todayBonus?.is_wednesday" class="badge wednesday">
                <i class="fas fa-calendar-day"></i>
                Wednesday Bonus
              </span>
              <span v-if="todayBonus?.is_special_day" class="badge special">
                <i class="fas fa-star"></i>
                Special Day
              </span>
            </div>
          </div>
        </div>
        
        <div class="bonus-actions">
          <button 
            v-if="canClaimBonus" 
            @click="claimBonus" 
            class="btn btn-primary btn-large"
            :disabled="claiming"
          >
            <i v-if="!claiming" class="fas fa-gift"></i>
            <i v-else class="fas fa-spinner fa-spin"></i>
            {{ claiming ? 'Claiming...' : 'Claim Bonus' }}
          </button>
          
          <div v-else-if="todayBonus?.is_claimed" class="claimed-status">
            <i class="fas fa-check-circle"></i>
            Already Claimed
          </div>
          
          <div v-else-if="todayBonus?.is_expired" class="expired-status">
            <i class="fas fa-clock"></i>
            Expired
          </div>
        </div>
      </div>
      
      <div class="bonus-progress">
        <div class="progress-info">
          <span>Cycle Progress</span>
          <span>{{ cycleInfo?.current_day || 1 }}/30 days</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: (cycleInfo?.current_day / 30 * 100 || 3.33) + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-fire"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ cycleInfo?.current_streak || 0 }}</div>
          <div class="stat-label">Current Streak</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-trophy"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ cycleInfo?.longest_streak || 0 }}</div>
          <div class="stat-label">Longest Streak</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-coins"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(cycleInfo?.total_claimed_this_cycle || 0) }}</div>
          <div class="stat-label">This Cycle</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-gem"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(cycleInfo?.total_lifetime_claimed || 0) }}</div>
          <div class="stat-label">Lifetime</div>
        </div>
      </div>
    </div>

    <!-- 30-Day Graph -->
    <div class="graph-section">
      <h3>30-Day Bonus History</h3>
      
      <div class="graph-controls">
        <button 
          @click="refreshGraph" 
          class="btn btn-outline"
          :disabled="loading"
        >
          <i class="fas fa-sync-alt"></i>
          Refresh
        </button>
      </div>
      
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        Loading bonus history...
      </div>
      
      <div v-else class="graph-container">
        <div class="graph-grid">
          <div 
            v-for="(day, index) in graphData" 
            :key="index"
            class="day-bar"
            :class="{
              'claimed': day.claimed,
              'available': day.available && !day.claimed && !day.expired,
              'expired': day.expired,
              'wednesday': day.is_wednesday,
              'special': day.is_special_day
            }"
            :title="getDayTooltip(day)"
          >
            <div class="bar-container">
              <div 
                class="bar-fill" 
                :style="{ height: getBarHeight(day.amount) + '%' }"
              ></div>
            </div>
            <div class="day-label">{{ day.day_number }}</div>
          </div>
        </div>
        
        <div class="graph-legend">
          <div class="legend-item claimed">
            <div class="legend-color"></div>
            <span>Claimed</span>
          </div>
          <div class="legend-item available">
            <div class="legend-color"></div>
            <span>Available</span>
          </div>
          <div class="legend-item expired">
            <div class="legend-color"></div>
            <span>Expired</span>
          </div>
          <div class="legend-item wednesday">
            <div class="legend-color"></div>
            <span>Wednesday</span>
          </div>
          <div class="legend-item special">
            <div class="legend-color"></div>
            <span>Special</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Upcoming Bonuses -->
    <div class="upcoming-section">
      <h3>Upcoming Bonuses</h3>
      
      <div class="upcoming-grid">
        <div 
          v-for="bonus in upcomingBonuses" 
          :key="bonus.day_number"
          class="upcoming-card"
          :class="{ 'wednesday': bonus.is_wednesday, 'special': bonus.is_special_day }"
        >
          <div class="upcoming-header">
            <span class="day-number">Day {{ bonus.day_number }}</span>
            <span class="date">{{ formatDate(bonus.date) }}</span>
          </div>
          
          <div class="upcoming-amount">
            <span class="amount">{{ bonus.amount }}</span>
            <span class="currency">KPI</span>
          </div>
          
          <div class="upcoming-multiplier" v-if="bonus.multiplier > 1">
            <i class="fas fa-times-circle"></i>
            {{ bonus.multiplier }}x
          </div>
          
          <div class="upcoming-badges">
            <span v-if="bonus.is_wednesday" class="badge wednesday">
              <i class="fas fa-calendar-day"></i>
            </span>
            <span v-if="bonus.is_special_day" class="badge special">
              <i class="fas fa-star"></i>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- System Info -->
    <div class="system-info">
      <h3>System Information</h3>
      
      <div class="info-grid">
        <div class="info-item">
          <span class="label">Base Daily Amount:</span>
          <span class="value">{{ systemConfig?.base_daily_amount || 30 }} KPI</span>
        </div>
        
        <div class="info-item">
          <span class="label">Daily Increment:</span>
          <span class="value">+{{ systemConfig?.daily_increment || 2 }} KPI</span>
        </div>
        
        <div class="info-item">
          <span class="label">Wednesday Bonus:</span>
          <span class="value">{{ systemConfig?.wednesday_multiplier || 1.5 }}x</span>
        </div>
        
        <div class="info-item">
          <span class="label">Bonus Expires In:</span>
          <span class="value">{{ systemConfig?.expiry_hours || 24 }} hours</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost } from '../../utils/api.js'

export default {
  name: 'KPIBonusDashboard',
  
  setup() {
    const loading = ref(false)
    const claiming = ref(false)
    const todayBonus = ref(null)
    const cycleInfo = ref(null)
    const graphData = ref([])
    const upcomingBonuses = ref([])
    const systemConfig = ref(null)
    
    const canClaimBonus = computed(() => {
      return todayBonus.value && 
             !todayBonus.value.is_claimed && 
             !todayBonus.value.is_expired
    })
    
    const loadTodayBonus = async () => {
      try {
        const response = await apiGet('/kpi-bonus/daily-bonus')
        todayBonus.value = response.daily_bonus
        cycleInfo.value = response.cycle
      } catch (error) {
        console.error('Failed to load daily bonus:', error)
      }
    }
    
    const claimBonus = async () => {
      claiming.value = true
      try {
        const response = await apiPost('/kpi-bonus/claim-bonus')
        
        if (response.success) {
          alert(response.message)
          await loadTodayBonus()
          await loadGraphData()
          await loadCycleInfo()
        } else {
          alert(response.message)
        }
      } catch (error) {
        console.error('Failed to claim bonus:', error)
        alert('Failed to claim bonus: ' + (error.response?.data?.detail || error.message))
      } finally {
        claiming.value = false
      }
    }
    
    const loadGraphData = async () => {
      try {
        const response = await apiGet('/kpi-bonus/bonus-history?days=30')
        graphData.value = response.graph_data
      } catch (error) {
        console.error('Failed to load graph data:', error)
      }
    }
    
    const loadCycleInfo = async () => {
      try {
        const response = await apiGet('/kpi-bonus/cycle-info')
        cycleInfo.value = response.cycle
        upcomingBonuses.value = response.upcoming_bonuses
      } catch (error) {
        console.error('Failed to load cycle info:', error)
      }
    }
    
    const loadSystemConfig = async () => {
      try {
        const response = await apiGet('/kpi-bonus/system-config')
        systemConfig.value = response
      } catch (error) {
        console.error('Failed to load system config:', error)
      }
    }
    
    const refreshGraph = async () => {
      loading.value = true
      try {
        await loadGraphData()
        await loadTodayBonus()
        await loadCycleInfo()
      } finally {
        loading.value = false
      }
    }
    
    const getBarHeight = (amount) => {
      const maxAmount = Math.max(...graphData.value.map(d => d.amount))
      return maxAmount > 0 ? (amount / maxAmount) * 100 : 0
    }
    
    const getDayTooltip = (day) => {
      if (!day.available) return `Day ${day.day_number}: Not available`
      
      let status = day.claimed ? 'Claimed' : (day.expired ? 'Expired' : 'Available')
      let multiplier = day.multiplier > 1 ? ` (${day.multiplier}x)` : ''
      
      return `Day ${day.day_number}: ${day.amount} KPI${multiplier} - ${status}`
    }
    
    const formatNumber = (num) => {
      return new Intl.NumberFormat().format(num)
    }
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }
    
    onMounted(async () => {
      await Promise.all([
        loadTodayBonus(),
        loadGraphData(),
        loadCycleInfo(),
        loadSystemConfig()
      ])
    })
    
    return {
      loading,
      claiming,
      todayBonus,
      cycleInfo,
      graphData,
      upcomingBonuses,
      systemConfig,
      canClaimBonus,
      claimBonus,
      refreshGraph,
      getBarHeight,
      getDayTooltip,
      formatNumber,
      formatDate
    }
  }
}
</script>

<style scoped>
.kpi-bonus-dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

.bonus-header {
  text-align: center;
  margin-bottom: 2rem;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.bonus-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.bonus-header h2 {
  color: var(--text-primary);
  margin-bottom: 1rem;
  font-size: 1.8rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.today-bonus-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 2rem;
  color: var(--text-primary);
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
  box-shadow: var(--glass-shadow-lg);
}

.today-bonus-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.bonus-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.bonus-main {
  flex: 1;
}

.bonus-amount {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.amount {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.currency {
  font-size: 1.2rem;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.bonus-details {
  text-align: right;
}

.day-info {
  font-size: 1rem;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.multiplier-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-tertiary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.special-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.badge.wednesday {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.badge.special {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.bonus-actions {
  text-align: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.btn-primary {
  background: #27ae60;
  color: white;
  border: 2px solid #27ae60;
}

.btn-primary:hover:not(:disabled) {
  background: #229954;
  border-color: #229954;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.btn-large {
  padding: 16px 32px;
  font-size: 16px;
}

.btn-outline {
  background: transparent;
  color: #3498db;
  border: 2px solid #3498db;
}

.btn-outline:hover {
  background: #3498db;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.claimed-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  color: #2ecc71;
}

.expired-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  color: #e74c3c;
}

.bonus-progress {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #2ecc71;
  transition: width 0.3s ease;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
  border-left: 4px solid #3498db;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.stat-card:nth-child(1) .stat-icon { background: #e74c3c; }
.stat-card:nth-child(2) .stat-icon { background: #f39c12; }
.stat-card:nth-child(3) .stat-icon { background: #27ae60; }
.stat-card:nth-child(4) .stat-icon { background: #9b59b6; }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
}

.graph-section, .upcoming-section, .system-info {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.graph-section h3, .upcoming-section h3, .system-info h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.graph-controls {
  margin-bottom: 20px;
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.graph-container {
  margin-bottom: 20px;
}

.graph-grid {
  display: grid;
  grid-template-columns: repeat(30, 1fr);
  gap: 4px;
  margin-bottom: 20px;
  height: 200px;
  align-items: flex-end;
}

.day-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  cursor: pointer;
  position: relative;
}

.bar-container {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  margin-bottom: 4px;
}

.bar-fill {
  width: 100%;
  background: #ecf0f1;
  border-radius: 2px 2px 0 0;
  transition: all 0.3s;
}

.day-bar.claimed .bar-fill { background: #27ae60; }
.day-bar.available .bar-fill { background: #3498db; }
.day-bar.expired .bar-fill { background: #e74c3c; }
.day-bar.wednesday .bar-fill { background: #f39c12; }
.day-bar.special .bar-fill { background: #9b59b6; }

.day-label {
  font-size: 10px;
  color: #7f8c8d;
}

.graph-legend {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-item.claimed .legend-color { background: #27ae60; }
.legend-item.available .legend-color { background: #3498db; }
.legend-item.expired .legend-color { background: #e74c3c; }
.legend-item.wednesday .legend-color { background: #f39c12; }
.legend-item.special .legend-color { background: #9b59b6; }

.upcoming-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.upcoming-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #3498db;
  transition: all 0.3s;
}

.upcoming-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.upcoming-card.wednesday {
  border-left-color: #f39c12;
}

.upcoming-card.special {
  border-left-color: #9b59b6;
}

.upcoming-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.day-number {
  font-weight: 600;
  color: #2c3e50;
}

.date {
  font-size: 12px;
  color: #7f8c8d;
}

.upcoming-amount {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;
}

.upcoming-amount .amount {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.upcoming-amount .currency {
  font-size: 14px;
  color: #7f8c8d;
}

.upcoming-multiplier {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #3498db;
  margin-bottom: 8px;
}

.upcoming-badges {
  display: flex;
  gap: 4px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.info-item .label {
  font-weight: 500;
  color: #7f8c8d;
}

.info-item .value {
  font-weight: 600;
  color: #2c3e50;
}
</style>
