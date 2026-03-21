<template>
  <div class="arcade-dashboard-container glass-panel">
    <!-- Sidebar Navigation -->
    <aside class="arcade-sidebar">
      <div class="arcade-logo">
        <i class="fas fa-gamepad"></i>
        <span>DHQ ARCADE</span>
      </div>
      
      <nav class="arcade-nav">
        <button v-for="tab in availableTabs" 
                :key="tab.id" 
                @click="activeTab = tab.id"
                :class="{ active: activeTab === tab.id }"
                class="nav-item">
          <i :class="tab.icon"></i>
          <span>{{ tab.label }}</span>
        </button>
        
        <!-- Admin Only Tabs -->
        <template v-if="isOP">
          <div class="nav-divider">Admin</div>
          <button @click="$router.push('/arcade/manage')"
                  class="nav-item admin-item">
            <i class="fas fa-tools"></i>
            <span>Management</span>
          </button>
        </template>
      </nav>
      
      <div class="theme-selector-section">
        <label>Theme</label>
        <select v-model="currentTheme" @change="updateTheme" class="theme-select">
          <option v-for="t in themes" :key="t" :value="t">{{ capitalize(t) }}</option>
        </select>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="arcade-content">
      <header class="content-header">
        <div class="user-stats-bar glass-panel">
          <div class="stat">
            <span class="label">KPI BALANCE</span>
            <span class="value">{{ kpiBalance }}</span>
          </div>
          <div class="stat chips">
            <span class="label">CHIPS</span>
            <span class="value">{{ formatNumber(profile?.chip_balance || 0) }}</span>
          </div>
          <div class="stat api-dollar">
            <span class="label">API$</span>
            <span class="value">{{ (profile?.api_dollar_balance || 0).toFixed(2) }}</span>
          </div>
          <div class="stat link" @click="$router.push('/daily-gifts')">
            <span class="label">DAILY TREASURE</span>
            <span class="value"><i class="fas fa-gift"></i> CLAIM</span>
          </div>
          <div class="stat">
            <span class="label">LEVEL</span>
            <span class="value">{{ profile?.level || 1 }}</span>
          </div>
        </div>
      </header>

      <div class="tab-view-container">
        <!-- Games View -->
        <div v-if="activeTab === 'games'" class="games-view">
          <div class="games-grid">
            <div v-for="game in allGames" :key="game.id" class="game-card glass-panel" @click="startGame(game)">
              <div class="game-preview" :style="{ backgroundColor: game.color }">
                <img v-if="game.imageLoaded" 
                     :src="`/assets/arcade/previews/${game.id}.png`" 
                     @error="onImageError(game)"
                     class="preview-img">
                <i v-else :class="game.icon"></i>
              </div>
              <div class="game-info">
                <h3>{{ game.name }}</h3>
                <p>{{ game.description }}</p>
                <div class="game-meta">
                  <span class="difficulty" :class="game.difficulty.toLowerCase()">{{ game.difficulty }}</span>
                  <span class="reward"><i class="fas fa-coins"></i> {{ game.reward }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        
        <!-- Placeholder for other tabs -->
        <div v-if="['shop', 'leaderboard', 'achievements', 'history'].includes(activeTab)" class="placeholder-view glass-panel">
           <i class="fas fa-tools"></i>
           <h2>{{ activeTab.toUpperCase() }} Coming Soon</h2>
           <p>We are polishing this section to match the new pastel premium theme.</p>
        </div>
      </div>
    </main>

    <!-- Game Overlay -->
    <transition name="fade">
      <div v-if="activeGame" class="game-overlay">
        <div class="game-header">
           <button @click="activeGame = null" class="exit-btn"><i class="fas fa-times"></i> Exit Game</button>
           <span class="game-title">{{ activeGame.name }}</span>
        </div>
        <div class="game-container glass-panel">
           <component :is="activeGame.component" @gameOver="onGameOver" @exit="activeGame = null" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, markRaw, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet, apiPost, kpiBalance, showAlert } from '../../utils/api.js'

// Game Components
import WordleGame from './WordleGame.vue'
import TicTacToeGame from './TicTacToeGame.vue'
import BovoGame from './BovoGame.vue'
import BlackjackGame from './BlackjackGame.vue'
import BigTwoGame from './BigTwoGame.vue'
import WordSearchGame from './WordSearchGame.vue'
import Game2048 from './Game2048.vue'
import DoodleJumpGame from './DoodleJumpGame.vue'
import FlappyBirdGame from './FlappyBirdGame.vue'

const router = useRouter()

// Navigation & Tabs
const activeTab = ref('games')
const availableTabs = [
  { id: 'games', label: 'Play Games', icon: 'fas fa-gamepad' },
  { id: 'shop', label: 'Arcade Shop', icon: 'fas fa-shopping-bag' },
  { id: 'leaderboard', label: 'Leaderboard', icon: 'fas fa-trophy' },
  { id: 'achievements', label: 'Achievements', icon: 'fas fa-medal' },
  { id: 'history', label: 'KPI History', icon: 'fas fa-history' }
]

const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

// Watch for Shop tab to redirect
watch(activeTab, (newTab) => {
  if (newTab === 'shop') {
    router.push('/shop')
    activeTab.value = 'games' // Reset
  }
})

// Auth & Profile
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const profile = ref(null)
const isOP = computed(() => user.value.role === 'OP' || user.value.is_op)

// Themes
const themes = ['dark', 'light', 'blue', 'pink', 'red', 'gold', 'silver', 'gray', 'purple', 'brown', 'glass']
const currentTheme = ref(localStorage.getItem('dhq-theme') || 'dark')

const updateTheme = () => {
  document.documentElement.setAttribute('data-theme', currentTheme.value)
  localStorage.setItem('dhq-theme', currentTheme.value)
}

// Games Data
const allGames = ref([
  { id: 'wordle', name: 'Wordle', description: 'Guess the hidden 5-letter word in 6 tries.', icon: 'fas fa-font', component: markRaw(WordleGame), difficulty: 'Medium', reward: '25-125 KPI', color: '#6aaa64', imageLoaded: true },
  { id: 'tictactoe', name: 'Tic Tac Toe', description: 'Classic 3x3 grid game against AI.', icon: 'fas fa-times', component: markRaw(TicTacToeGame), difficulty: 'Easy', reward: '10-50 KPI', color: '#3b82f6', imageLoaded: true },
  { id: 'bovo', name: 'Bovo (Five in a Row)', description: 'Connect five stones in a row to win.', icon: 'fas fa-circle', component: markRaw(BovoGame), difficulty: 'Hard', reward: '100 KPI', color: '#8b5cf6', imageLoaded: true },
  { id: 'blackjack', name: 'Blackjack', description: 'Beat the dealer without going over 21.', icon: 'fas fa-spade', component: markRaw(BlackjackGame), difficulty: 'Medium', reward: 'CHIPS', color: '#ef4444', imageLoaded: true },
  { id: 'bigtwo', name: 'Big Two', description: 'Be the first to empty your hand.', icon: 'fas fa-cards', component: markRaw(BigTwoGame), difficulty: 'Hard', reward: 'CHIPS', color: '#f59e0b', imageLoaded: true },
  { id: '2048', name: '2048', description: 'Merge tiles to reach the 2048 tile.', icon: 'fas fa-th-large', component: markRaw(Game2048), difficulty: 'Medium', reward: '80 KPI', color: '#edc22e', imageLoaded: true },
  { id: 'wordsearch', name: 'Word Search', description: 'Find hidden words in the grid.', icon: 'fas fa-search', component: markRaw(WordSearchGame), difficulty: 'Medium', reward: '40 KPI', color: '#10b981', imageLoaded: true },
  { id: 'doodlejump', name: 'Doodle Jump', description: 'Jump as high as you can!', icon: 'fas fa-arrow-up', component: markRaw(DoodleJumpGame), difficulty: 'Medium', reward: '70 KPI', color: '#ec4899', imageLoaded: true },
  { id: 'flappybird', name: 'Flappy Bird', description: 'Tap to fly through pipes!', icon: 'fas fa-dove', component: markRaw(FlappyBirdGame), difficulty: 'Hard', reward: '90 KPI', color: '#7dd3fc', imageLoaded: true },
  { id: 'snake', name: 'Neon Snake', description: 'Classic snake with a neon twist.', icon: 'fas fa-worm', component: markRaw(defineAsyncComponent(() => import('./SnakeGame.vue'))), difficulty: 'Medium', reward: '20-100 KPI', color: '#3b82f6', imageLoaded: false },
  { id: 'minesweeper', name: 'Minesweeper', description: 'Clear the grid without hitting mines.', icon: 'fas fa-bomb', component: markRaw(defineAsyncComponent(() => import('./MinesweeperGame.vue'))), difficulty: 'Hard', reward: '50-150 KPI', color: '#f43f5e', imageLoaded: false },
  { id: 'colorsorter', name: 'Color Sorter', description: 'Sort the colored liquids into tubes.', icon: 'fas fa-vial', component: markRaw(defineAsyncComponent(() => import('./ColorSorterGame.vue'))), difficulty: 'Medium', reward: '50 KPI', color: '#10b981', imageLoaded: false },
  { id: 'towerdefense', name: 'Tower Defense', description: 'Protect your base from waves of enemies.', icon: 'fa-fort-awesome', component: markRaw(defineAsyncComponent(() => import('./TowerDefenseGame.vue'))), difficulty: 'Extreme', reward: '100-500 KPI', color: '#fbbf24', imageLoaded: false },
  { id: 'platformer', name: 'Platformer Arena', description: 'Action-packed platformer wave survival.', icon: 'fas fa-gamepad', component: markRaw(defineAsyncComponent(() => import('./PlatformerGame.vue'))), difficulty: 'Hard', reward: '200 KPI', color: '#a855f7', imageLoaded: false },
])

const activeGame = ref(null)
const dailyClaimed = ref(false)

// Methods
const loadProfile = async () => {
  try {
    profile.value = await apiGet('/arcade/profile')
    dailyClaimed.value = new Date(profile.value.last_login).toDateString() === new Date().toDateString()
  } catch (err) {
    console.error('Profile load error:', err)
  }
}

const claimDailyBonus = () => {
  router.push('/daily-gifts')
}

const startGame = (game) => {
  if (game.placeholder) {
    alert('This game is coming soon!')
    return
  }
  activeGame.value = game
}

const onGameOver = (data) => {
  if (data.kpi > 0) {
    showAlert('Game Over', `Congratulations! You earned ${data.kpi} KPI!`, 'success', '🏆')
  } else if (data.chips !== undefined) {
    // Chips handled in game component
  } else {
    showAlert('Game Over', 'Better luck next time!', 'info')
  }
  loadProfile()
}

const onImageError = (game) => {
  game.imageLoaded = false
}

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1)

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.arcade-dashboard-container {
  display: flex;
  height: calc(100vh - 110px); /* Optimized height to fit layout nicely */
  overflow: hidden;
  margin: 0.5rem 1rem;
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border-radius: 24px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}

.arcade-sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  padding: 2rem 1.5rem;
  border-right: 1px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.03); /* Subtle backdrop for sidebar area */
}

.arcade-logo {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 3rem;
  background: linear-gradient(135deg, var(--primary-color), var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.arcade-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-item:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
  transform: translateX(5px);
}

.nav-item.active {
  background: var(--primary-color);
  color: #fff;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.nav-divider {
  margin: 1.5rem 0 0.5rem 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
}

.admin-item {
  color: var(--secondary-color);
}

.theme-selector-section {
  margin-top: 2rem;
  padding: 1rem;
  border-top: 1px solid var(--glass-border);
}

.theme-select {
  width: 100%;
  margin-top: 0.5rem;
}

.arcade-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.user-stats-bar {
  display: flex;
  gap: 2rem;
  padding: 0.75rem 2rem;
  border-radius: 50px;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 1.5rem;
  border-right: 1px solid var(--glass-border);
}

.stat.link {
  cursor: pointer;
  transition: all 0.3s;
}

.stat.link:hover {
  background: var(--glass-bg-hover);
  color: var(--primary-color);
}

.stat .label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted);
}

.stat .value {
  font-size: 1.2rem;
  font-weight: 800;
}

.claim-bonus-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 50px;
  background: var(--primary-color);
  color: #fff;
  border: none;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.3s ease;
}

.claim-bonus-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px var(--primary-color);
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.game-card {
  padding: 0;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.game-preview {
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  color: rgba(255,255,255,0.8);
  position: relative;
  overflow: hidden;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.game-card:hover .preview-img {
  transform: scale(1.1);
}

.game-info {
  padding: 1.5rem;
}

.game-info h3 {
  margin-bottom: 0.5rem;
}

.game-info p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  height: 2.7rem;
  overflow: hidden;
}

.game-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
}

.difficulty {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.difficulty.easy { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.difficulty.medium { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.difficulty.hard { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

.reward {
  font-weight: 700;
  color: var(--primary-color);
}

/* Admin Sections */
.admin-view h2 {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.gift-form, .bonus-grid {
  padding: 2rem;
}

.bonus-inputs-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.bonus-day-input {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.bonus-day-input input {
  width: 100%;
}

.bonus-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-top: 1px solid var(--glass-border);
  padding-top: 1.5rem;
}

.search-section {
  position: relative;
}

.search-input-group {
  position: relative;
  width: 100%;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.search-result {
  padding: 0.8rem 1rem;
  cursor: pointer;
}

.search-result:hover {
  background: var(--glass-bg-hover);
}

.gift-inputs {
  display: grid;
  grid-template-columns: 1fr 2fr auto;
  gap: 1.5rem;
  align-items: flex-end;
  margin-top: 1.5rem;
}

.send-btn, .save-btn {
  background: var(--primary-color);
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
}

/* Game Overlay */
.game-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--bg-gradient);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
}

.exit-btn {
  background: var(--danger-color);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.game-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem;
  text-align: center;
}

.placeholder-view i {
  font-size: 4rem;
  margin-bottom: 2rem;
  color: var(--text-muted);
}

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
