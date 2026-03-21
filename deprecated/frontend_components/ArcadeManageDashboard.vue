<template>
  <div class="arcade-manage-dashboard glass-panel">
    <!-- Sidebar -->
    <aside class="manage-sidebar">
      <div class="manage-logo">
        <i class="fas fa-tools text-secondary"></i>
        <span>ARCADE MGMT</span>
      </div>
      
      <nav class="manage-nav">
        <button @click="activeTab = 'gifts'" :class="{ active: activeTab === 'gifts' }" class="nav-item">
          <i class="fas fa-gift"></i>
          <span>Gifts & KPI</span>
        </button>
        <button @click="activeTab = 'bonus'" :class="{ active: activeTab === 'bonus' }" class="nav-item">
          <i class="fas fa-calendar-check"></i>
          <span>Bonus Config</span>
        </button>
        <button @click="$router.push('/arcade')" class="nav-item back-item">
          <i class="fas fa-arrow-left"></i>
          <span>Back to Arcade</span>
        </button>
      </nav>
    </aside>

    <!-- Content -->
    <main class="manage-content custom-scrollbar">
      <header class="manage-header">
        <h1>{{ activeTab === 'gifts' ? 'Gift KPI points to Users' : 'Daily Bonus Configuration' }}</h1>
        <p class="text-secondary">Operator access only. Manage the economy and rewards.</p>
      </header>

      <!-- Gifting View -->
      <div v-if="activeTab === 'gifts'" class="gifts-view animate-fade">
        <div class="glass-panel gift-card">
          <div class="search-box">
             <label><i class="fas fa-search"></i> Find User</label>
             <div class="search-input-wrapper">
               <input v-model="userSearchQuery" @input="searchUsers" placeholder="Full username or display name..." />
               <div v-if="searchResults.length" class="search-results glass-panel">
                 <div v-for="u in searchResults" :key="u.id" @click="selectUser(u)" class="result-item">
                   <div class="avatar"><i class="fas fa-user-circle"></i></div>
                   <div class="info">
                     <span class="uname">{{ u.username }}</span>
                     <span class="dname">{{ u.display_name }}</span>
                   </div>
                   <div class="role-pill">{{ u.role }}</div>
                 </div>
               </div>
             </div>
          </div>

          <div v-if="selectedUser" class="selected-summary animate-slide">
             <div class="target-indicator">Gifting to: <strong>{{ selectedUser.username }}</strong></div>
             <div class="input-grid">
                <div class="input-field">
                   <label>Amount (KPI)</label>
                   <input type="number" v-model="giftAmount" min="1" />
                </div>
                <div class="input-field">
                   <label>Description</label>
                   <input v-model="giftReason" placeholder="Reason for the gift..." />
                </div>
                <button @click="sendGift" class="send-btn glow-btn" :disabled="giftAmount <= 0">
                   <i class="fas fa-paper-plane"></i> Send Gift
                </button>
             </div>
          </div>
        </div>
      </div>

      <!-- Bonus Config View -->
      <div v-if="activeTab === 'bonus'" class="bonus-view animate-fade">
        <div class="glass-panel config-card">
           <div class="base-config">
              <label>Global Base Bonus (KPI)</label>
              <div class="base-input-wrapper">
                 <input type="number" v-model="baseBonus" min="0" />
                 <span class="hint">The initial amount before multipliers</span>
              </div>
           </div>

           <div class="bonus-grid-container">
              <h3>30-Day Streak Multipliers (%)</h3>
              <div class="bonus-grid">
                <div v-for="day in 30" :key="day" class="day-cell">
                   <div class="day-num">Day {{ day }}</div>
                   <input type="number" step="0.1" v-model="bonusConfigs[day-1]" />
                </div>
              </div>
           </div>

           <div class="action-footer">
              <button @click="saveBonusConfig" class="save-btn glow-btn">
                 <i class="fas fa-save"></i> Save All Multipliers
              </button>
           </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiGet, apiPost } from '../../utils/api.js'

const activeTab = ref('gifts')

// Gifting state
const userSearchQuery = ref('')
const searchResults = ref([])
const selectedUser = ref(null)
const giftAmount = ref(0)
const giftReason = ref('')

// Bonus config state
const baseBonus = ref(30)
const bonusConfigs = ref(new Array(30).fill(0))

const searchUsers = async () => {
  if (userSearchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  try {
    searchResults.value = await apiGet(`/arcade/manage/users/search?query=${userSearchQuery.value}`)
  } catch (err) {
    console.error('User search error:', err)
  }
}

const selectUser = (u) => {
  selectedUser.value = u
  searchResults.value = []
  userSearchQuery.value = u.username
}

const sendGift = async () => {
  try {
    const data = await apiPost('/arcade/manage/gift', {
      user_id: selectedUser.value.id,
      amount: giftAmount.value,
      description: giftReason.value
    })
    
    alert('Gift successfully delivered to ' + selectedUser.value.username)
    giftAmount.value = 0
    giftReason.value = ''
    selectedUser.value = null
  } catch (err) {
    alert('Failed to send gift. Check logs.')
    console.error('Gift error:', err)
  }
}

const saveBonusConfig = async () => {
  try {
    await apiPost('/arcade/manage/bonus-config', {
      base_bonus: baseBonus.value,
      percentages: bonusConfigs.value.map(v => v / 100)
    })
    alert('30-Day streak configuration updated!')
  } catch (err) {
    console.error('Save config error:', err)
    alert('Failed to save configuration.')
  }
}

const loadBonusConfig = async () => {
  try {
    const data = await apiGet('/arcade/manage/bonus-config')
    baseBonus.value = data.base_bonus
    bonusConfigs.value = data.percentages.map(v => v * 100)
  } catch (err) {
    console.error('Load config error:', err)
  }
}

onMounted(() => {
  loadBonusConfig()
})
</script>

<style scoped>
.arcade-manage-dashboard {
  display: flex;
  height: calc(100vh - 70px);
  width: 100%;
  border-radius: 0;
  overflow: hidden;
}

.manage-sidebar {
  width: 260px;
  display: flex;
  flex-direction: column;
  padding: 2rem 1rem;
  border-right: 1px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.03);
}

.manage-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 900;
  margin-bottom: 2.5rem;
  padding-left: 0.5rem;
}

.manage-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1.2rem;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.nav-item:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
  transform: translateX(4px);
}

.nav-item.active {
  background: var(--primary-color);
  color: #fff;
}

.back-item {
  margin-top: 2rem;
  border-top: 1px solid var(--glass-border);
  padding-top: 1.5rem;
  font-size: 0.9rem;
}

.manage-content {
  flex: 1;
  padding: 2.5rem;
  overflow-y: auto;
}

.manage-header h1 { font-size: 2rem; font-weight: 900; margin-bottom: 0.5rem; }

.gifts-view, .bonus-view {
  margin-top: 2rem;
}

.gift-card, .config-card {
  padding: 2.5rem;
}

.search-input-wrapper {
  position: relative;
  margin-top: 0.5rem;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  z-index: 50;
  max-height: 250px;
  overflow-y: auto;
  margin-top: 5px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
}

.result-item:hover { background: var(--glass-bg-hover); }

.info { display: flex; flex-direction: column; flex: 1; }
.uname { font-weight: 700; font-size: 0.95rem; }
.dname { font-size: 0.8rem; color: var(--text-secondary); }
.role-pill { font-size: 0.65rem; font-weight: 800; background: var(--secondary-color); color: white; padding: 2px 6px; border-radius: 10px; }

.selected-summary {
  margin-top: 2.5rem;
  padding-top: 2.5rem;
  border-top: 1px solid var(--glass-border);
}

.input-grid {
  display: grid;
  grid-template-columns: 1fr 2fr auto;
  gap: 1.5rem;
  align-items: flex-end;
  margin-top: 1.5rem;
}

.bonus-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.day-cell {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.day-num { font-size: 0.75rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; }

.action-footer {
  margin-top: 2.5rem;
  padding-top: 2rem;
  border-top: 1px solid var(--glass-border);
  display: flex;
  justify-content: flex-end;
}

.glow-btn {
  padding: 1rem 2rem;
  border-radius: 12px;
  border: none;
  background: var(--primary-color);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s;
}

.glow-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.2);
}

.animate-fade { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.animate-slide { animation: slideUp 0.4s ease; }
@keyframes slideUp { from { transform: translateY(10px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>
