<template>
  <div class="manage-gifts glass-panel">
    <!-- Sidebar -->
    <aside class="manage-sidebar glass-panel">
      <div class="manage-logo">
        <i class="fas fa-gift text-secondary"></i>
        <span>MANAGE GIFTS</span>
      </div>
      
      <nav class="manage-nav">
        <button @click="activeTab = 'gifts'" :class="{ active: activeTab === 'gifts' }" class="nav-item">
          <i class="fas fa-hand-holding-usd"></i>
          <span>Gift KPI</span>
        </button>
        <button @click="activeTab = 'bonus'" :class="{ active: activeTab === 'bonus' }" class="nav-item">
          <i class="fas fa-calendar-alt"></i>
          <span>Bonus Config</span>
        </button>
        <button @click="$router.push('/arcade')" class="nav-item back-item">
          <i class="fas fa-arrow-left"></i>
          <span>Back to Arcade</span>
        </button>
      </nav>

      <div class="my-balance-card glass-panel" v-if="adminBalance">
        <div class="balance-item">
          <span class="label">MY KPI</span>
          <span class="val">{{ adminBalance.kpi_balance.toLocaleString() }}</span>
        </div>
        <div class="balance-item">
          <span class="label">MY CHIPS</span>
          <span class="val">{{ adminBalance.chip_balance.toLocaleString() }}</span>
        </div>
      </div>
    </aside>

    <!-- Content -->
    <main class="manage-content custom-scrollbar">
      <header class="manage-header">
        <h1>{{ activeTab === 'gifts' ? 'Gift KPI points to Users' : 'Daily Bonus Configuration' }}</h1>
        <p class="text-secondary">Manage the economy and rewards. Send manual gifts or configure automated bonuses.</p>
      </header>

      <!-- Gifting View -->
      <div v-if="activeTab === 'gifts'" class="gifts-view animate-fade">
        <div class="glass-panel gift-card">
          <div class="search-box">
             <label><i class="fas fa-search"></i> Find User</label>
             <div class="search-input-wrapper">
               <input v-model="userSearchQuery" @input="searchUsers" placeholder="Search by username or display name..." />
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
             <div class="target-indicator">
               Gifting to: <strong>{{ selectedUser.username }}</strong>
               <div v-if="recipientBalance" class="recipient-stats">
                 Current: <span><i class="fas fa-star"></i> {{ recipientBalance.kpi_balance.toLocaleString() }} KPI</span> 
                 | <span><i class="fas fa-coins"></i> {{ recipientBalance.chip_balance.toLocaleString() }} Chips</span>
               </div>
             </div>
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
              <label>Global Base Daily Bonus (KPI)</label>
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
                 <i class="fas fa-save"></i> Save Multipliers
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

// Meta state
const adminBalance = ref(null)
const recipientBalance = ref(null)

// Bonus config state
const baseBonus = ref(30)
const bonusConfigs = ref(new Array(30).fill(0))

const loadAdminBalance = async () => {
  try {
    const profile = await apiGet('/arcade/profile')
    adminBalance.value = {
      kpi_balance: profile.kpi_balance,
      chip_balance: profile.chip_balance
    }
  } catch (err) {
    console.error('Failed to load admin balance:', err)
  }
}

const loadRecipientBalance = async (userId) => {
  try {
    recipientBalance.value = await apiGet(`/gifts/manage/user-balance/${userId}`)
  } catch (err) {
    console.error('Failed to load recipient balance:', err)
  }
}

const searchUsers = async () => {
  if (userSearchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  try {
    searchResults.value = await apiGet(`/gifts/manage/users/search?query=${userSearchQuery.value}`)
  } catch (err) {
    console.error('User search error:', err)
  }
}

const selectUser = async (u) => {
  selectedUser.value = u
  searchResults.value = []
  userSearchQuery.value = u.username
  await loadRecipientBalance(u.id)
}

const sendGift = async () => {
  try {
    await apiPost('/gifts/manage/gift', {
      user_id: selectedUser.value.id,
      amount: giftAmount.value,
      description: giftReason.value
    })
    
    alert('Gift successfully delivered to ' + selectedUser.value.username)
    await loadAdminBalance() // Refresh own balance
    await loadRecipientBalance(selectedUser.value.id) // Refresh recipient balance
    giftAmount.value = 0
    giftReason.value = ''
    // selectedUser.value = null // Keep it selected to show updated balance
  } catch (err) {
    alert('Failed to send gift. Check logs.')
    console.error('Gift error:', err)
  }
}

const saveBonusConfig = async () => {
  try {
    await apiPost('/gifts/manage/bonus-config', {
      base_bonus: baseBonus.value,
      percentages: bonusConfigs.value.map(v => v / 100)
    })
    alert('Bonus configuration updated!')
  } catch (err) {
    console.error('Save config error:', err)
    alert('Failed to save configuration.')
  }
}

const loadBonusConfig = async () => {
  try {
    const data = await apiGet('/gifts/manage/bonus-config')
    if (data) {
      baseBonus.value = data.base_bonus || 30
      if (data.percentages && Array.isArray(data.percentages)) {
        bonusConfigs.value = data.percentages.map(v => v * 100)
      } else {
        bonusConfigs.value = new Array(30).fill(0)
      }
    }
  } catch (err) {
    console.error('Load config error:', err)
  }
}

onMounted(() => {
  loadBonusConfig()
  loadAdminBalance()
})
</script>

<style scoped>
.manage-gifts {
  display: flex;
  height: calc(100vh - 100px);
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  background: var(--glass-bg-primary);
}

.manage-sidebar {
  width: 250px;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  margin: 1rem;
  border-radius: 12px;
}

.manage-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.1rem;
  font-weight: 800;
  margin-bottom: 2rem;
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
  padding: 0.8rem 1rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  text-align: left;
}

.nav-item:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--primary-color);
  color: #fff;
}

.back-item {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

.my-balance-card {
  margin-top: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--primary-color);
}

.balance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance-item .label { font-size: 0.6rem; font-weight: 800; color: var(--text-muted); }
.balance-item .val { font-size: 0.9rem; font-weight: 900; color: var(--primary-color); }

.manage-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.manage-header h1 { font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem; }

.gifts-view, .bonus-view {
  margin-top: 1.5rem;
}

.gift-card, .config-card {
  padding: 2rem;
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
  max-height: 200px;
  overflow-y: auto;
  margin-top: 5px;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
}

.result-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.6rem 1rem;
  cursor: pointer;
}

.result-item:hover { background: var(--glass-bg-hover); }

.info { display: flex; flex-direction: column; flex: 1; }
.uname { font-weight: 700; font-size: 0.9rem; }
.dname { font-size: 0.75rem; color: var(--text-secondary); }
.role-pill { font-size: 0.6rem; font-weight: 800; background: var(--secondary-color); color: white; padding: 2px 6px; border-radius: 8px; }

.target-indicator { font-size: 1.1rem; margin-bottom: 0.5rem; }
.target-indicator strong { color: var(--primary-color); }

.recipient-stats {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 4px;
  background: var(--glass-bg-secondary);
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
}

.recipient-stats span { font-weight: 700; color: var(--text-primary); }
.recipient-stats i { color: #ffd700; margin-right: 4px; }

.input-grid {
  display: grid;
  grid-template-columns: 1fr 2fr auto;
  gap: 1.5rem;
  align-items: flex-end;
  margin-top: 1rem;
}

.bonus-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.day-cell {
  background: var(--glass-bg-secondary);
  padding: 0.5rem;
  border-radius: 8px;
  border: 1px solid var(--glass-border);
}

.day-num { font-size: 0.65rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; }

.day-cell input {
  width: 100%;
  background: transparent;
  border: none;
  font-weight: 700;
  color: var(--primary-color);
  text-align: center;
}

.action-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  display: flex;
  justify-content: flex-end;
}

.glow-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  border: none;
  background: var(--primary-color);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}

.animate-fade { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.animate-slide { animation: slideUp 0.3s ease; }
@keyframes slideUp { from { transform: translateY(10px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>
