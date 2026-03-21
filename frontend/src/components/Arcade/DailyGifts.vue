<template>
  <div class="daily-gifts glass-panel animate-fade">
    <header class="gifts-header">
      <div class="streak-badge">
        <i class="fas fa-fire"></i>
        <span>{{ streak }} DAY STREAK</span>
      </div>
      <h1>Daily Treasure</h1>
      <p>Log in every day to claim your KPI rewards and maintain your streak!</p>
    </header>

    <div class="milestones-container">
      <h3>Your Progress</h3>
      <div class="milestones-track">
        <div v-for="day in 7" :key="day" 
             class="milestone-node" 
             :class="{ completed: day < streak, current: day === streak, locked: day > streak }">
          <div class="node-icon">
            <i :class="day % 7 === 0 ? 'fas fa-gem' : 'fas fa-coins'"></i>
          </div>
          <div class="node-label">Day {{ day }}</div>
          <div v-if="day < streak" class="check-mark"><i class="fas fa-check"></i></div>
        </div>
      </div>
    </div>

    <div class="claim-section">
      <div v-if="!alreadyClaimed" class="claim-card glass-panel animate-pop">
        <div class="reward-preview">
          <span class="label">TODAY'S REWARD</span>
          <span class="value">{{ todayReward }} KPI</span>
        </div>
        <button @click="claimReward" class="claim-btn glow-btn" :disabled="isClaiming">
          <i class="fas fa-gift" :class="{ 'fa-spin': isClaiming }"></i>
          {{ isClaiming ? 'Claiming...' : 'Claim Daily Bonus' }}
        </button>
      </div>
      <div v-else class="claimed-card glass-panel">
        <i class="fas fa-check-circle text-success pulse"></i>
        <h3>Already Claimed!</h3>
        <p>Come back tomorrow to keep your {{ streak }} day streak alive.</p>
        <div class="next-reward">
          <span>Next: <strong>{{ tomorrowReward }} KPI</strong></span>
        </div>
      </div>
    </div>

    <footer class="gifts-footer">
      <div class="pro-tip">
        <i class="fas fa-lightbulb"></i>
        <span>Maintaining a streak increases your bonus multiplier up to 2x!</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { apiGet, apiPost, kpiBalance } from '../../utils/api.js'

const streak = ref(0)
const alreadyClaimed = ref(false)
const isClaiming = ref(false)
const baseBonus = ref(30)
const multipliers = ref([])
const lastClaimDate = ref(null)

const loadGiftsData = async () => {
  try {
    const profile = await apiGet('/gifts/profile')
    streak.value = profile.login_streak || 0
    lastClaimDate.value = profile.last_login
    
    const today = new Date().toDateString()
    alreadyClaimed.value = lastClaimDate.value && new Date(lastClaimDate.value).toDateString() === today

    const config = await apiGet('/gifts/config')
    baseBonus.value = config.base_bonus || 30
    multipliers.value = config.percentages || []
  } catch (err) {
    console.error('Failed to load gifts data:', err)
  }
}

const todayReward = computed(() => {
  const idx = Math.min(streak.value, 29)
  const mult = multipliers.value[idx] || 0
  return Math.floor(baseBonus.value * (1 + mult))
})

const tomorrowReward = computed(() => {
  const idx = Math.min(streak.value + 1, 29)
  const mult = multipliers.value[idx] || 0
  return Math.floor(baseBonus.value * (1 + mult))
})

const claimReward = async () => {
  isClaiming.value = true
  try {
    const res = await apiPost('/gifts/claim')
    streak.value = res.login_streak
    alreadyClaimed.value = true
    alert(`Congratulations! You claimed ${res.kpi_awarded} KPI.`)
    // The kpiBalance is updated via apiPost middleware
  } catch (err) {
    alert(err.message || 'Failed to claim reward')
  } finally {
    isClaiming.value = false
  }
}

onMounted(() => {
  loadGiftsData()
})
</script>

<style scoped>
.daily-gifts {
  max-width: 800px;
  margin: 2rem auto;
  padding: 3rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.gifts-header h1 {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0.5rem 0;
}

.streak-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-weight: 800;
  font-size: 0.9rem;
}

.milestones-container {
  padding: 2rem;
}

.milestones-track {
  display: flex;
  justify-content: space-between;
  position: relative;
  margin-top: 2rem;
}

.milestones-track::before {
  content: '';
  position: absolute;
  top: 25px;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--glass-border);
  z-index: 1;
}

.milestone-node {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  width: 60px;
}

.node-icon {
  width: 50px;
  height: 50px;
  background: var(--glass-bg-secondary);
  border: 4px solid var(--glass-border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  transition: all 0.3s;
}

.milestone-node.completed .node-icon {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.milestone-node.current .node-icon {
  background: var(--primary-color);
  border-color: #fff;
  color: white;
  transform: scale(1.2);
  box-shadow: 0 0 20px var(--primary-color);
}

.node-label {
  font-size: 0.75rem;
  font-weight: 700;
}

.check-mark {
  position: absolute;
  top: -5px;
  right: -5px;
  background: white;
  color: #10b981;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.claim-section {
  display: flex;
  justify-content: center;
}

.claim-card, .claimed-card {
  padding: 3rem;
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.reward-preview {
  display: flex;
  flex-direction: column;
}

.reward-preview .label { font-size: 0.8rem; font-weight: 800; color: var(--text-muted); }
.reward-preview .value { font-size: 3rem; font-weight: 900; color: var(--primary-color); }

.glow-btn {
  width: 100%;
  padding: 1.2rem;
  font-size: 1.1rem;
  font-weight: 800;
  border-radius: 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.pulse { animation: pulseAnim 2s infinite; }
@keyframes pulseAnim { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }

.animate-pop { animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes popIn { from { transform: scale(0.8); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.pro-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-style: italic;
}
</style>
