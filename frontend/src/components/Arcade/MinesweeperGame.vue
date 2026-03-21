<template>
  <div class="minesweeper-container glass-panel" :class="{ 'game-over': state === 'LOST', 'game-won': state === 'WON' }">
    <div class="game-header">
      <div class="stat-card glass-panel">
        <i class="fas fa-bomb text-danger"></i>
        <span>{{ remainingMines }}</span>
      </div>
      <div class="stat-card glass-panel timer">
        <i class="fas fa-stopwatch"></i>
        <span>{{ formatTime(timer) }}</span>
      </div>
      <button class="reset-btn glass-panel" @click="initGame">
        <i class="fas" :class="stateIcon"></i>
      </button>
    </div>

    <div class="grid-wrapper glass-panel">
      <div 
        class="grid" 
        :style="{ gridTemplateColumns: `repeat(${cols}, 1fr)` }"
      >
        <div 
          v-for="(cell, index) in grid" 
          :key="index"
          class="cell glass-panel"
          :class="{ 
            'revealed': cell.revealed, 
            'flagged': cell.flagged,
            'mine': cell.revealed && cell.mine,
            'exploded': cell.exploded,
            [`count-${cell.neighborMines}`]: cell.revealed && !cell.mine && cell.neighborMines > 0
          }"
          @click="revealCell(index)"
          @contextmenu.prevent="flagCell(index)"
        >
          <template v-if="cell.revealed">
            <i v-if="cell.mine" class="fas fa-bomb"></i>
            <span v-else-if="cell.neighborMines > 0">{{ cell.neighborMines }}</span>
          </template>
          <template v-else-if="cell.flagged">
            <i class="fas fa-flag"></i>
          </template>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div v-if="state === 'WON' || state === 'LOST'" class="game-overlay glass-panel">
        <h2>{{ state === 'WON' ? 'GRID SECURED' : 'DETONATION' }}</h2>
        <div class="final-stats">
          <p>TIME: {{ formatTime(timer) }}</p>
          <p v-if="state === 'WON'" class="kpi-win">+{{ calculateKPI() }} KPI</p>
        </div>
        <button class="premium-btn" @click="initGame">NEW DEPLOYMENT</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { apiPost } from '../../utils/api.js'

const rows = 12
const cols = 12
const totalMines = 20

const grid = ref([])
const state = ref('IDLE') // IDLE, PLAYING, WON, LOST
const timer = ref(0)
const remainingMines = ref(totalMines)
let timerInterval

const stateIcon = computed(() => {
  if (state.value === 'WON') return 'fa-trophy'
  if (state.value === 'LOST') return 'fa-dizzy'
  return 'fa-smile'
})

const initGame = () => {
  state.value = 'IDLE'
  timer.value = 0
  remainingMines.value = totalMines
  clearInterval(timerInterval)
  
  const newGrid = []
  for (let i = 0; i < rows * cols; i++) {
    newGrid.push({
      mine: false,
      revealed: false,
      flagged: false,
      neighborMines: 0,
      exploded: false
    })
  }
  grid.value = newGrid
}

const placeMines = (safeIndex) => {
  let placed = 0
  while (placed < totalMines) {
    const idx = Math.floor(Math.random() * grid.value.length)
    if (!grid.value[idx].mine && idx !== safeIndex) {
      grid.value[idx].mine = true
      placed++
    }
  }

  // Calculate numbers
  for (let i = 0; i < grid.value.length; i++) {
    if (grid.value[i].mine) continue
    const neighbors = getNeighbors(i)
    grid.value[i].neighborMines = neighbors.filter(n => grid.value[n].mine).length
  }
}

const getNeighbors = (index) => {
  const r = Math.floor(index / cols)
  const c = index % cols
  const n = []
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (dr === 0 && dc === 0) continue
      const nr = r + dr
      const nc = c + dc
      if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
        n.push(nr * cols + nc)
      }
    }
  }
  return n
}

const revealCell = (index) => {
  if (state.value === 'WON' || state.value === 'LOST' || grid.value[index].flagged || grid.value[index].revealed) return

  if (state.value === 'IDLE') {
    state.value = 'PLAYING'
    placeMines(index)
    startTimer()
  }

  const cell = grid.value[index]
  cell.revealed = true

  if (cell.mine) {
    cell.exploded = true
    return gameOver(false)
  }

  if (cell.neighborMines === 0) {
    const neighbors = getNeighbors(index)
    neighbors.forEach(n => revealCell(n))
  }

  checkWin()
}

const flagCell = (index) => {
  if (state.value === 'WON' || state.value === 'LOST' || grid.value[index].revealed) return
  grid.value[index].flagged = !grid.value[index].flagged
  remainingMines.value += grid.value[index].flagged ? -1 : 1
}

const checkWin = () => {
  const won = grid.value.every(c => c.mine || c.revealed)
  if (won) gameOver(true)
}

const gameOver = async (won) => {
  state.value = won ? 'WON' : 'LOST'
  clearInterval(timerInterval)

  // Reveal all mines
  grid.value.forEach(c => {
    if (c.mine) c.revealed = true
  })

  if (won) {
    try {
      const kpi = calculateKPI()
      await apiPost('/games/scores/submit', {
        game_type: 'minesweeper',
        score: timer.value,
        kpi: kpi
      })
    } catch (err) {
      console.error(err)
    }
  }
}

const startTimer = () => {
  timerInterval = setInterval(() => {
    timer.value++
  }, 1000)
}

const calculateKPI = () => {
  // Faster = more KPI
  const base = 50
  const bonus = Math.max(0, 100 - timer.value)
  return base + bonus
}

const formatTime = (s) => {
  const m = Math.floor(s / 60)
  const rs = s % 60
  return `${m}:${rs.toString().padStart(2, '0')}`
}

onMounted(() => {
  initGame()
})

onUnmounted(() => {
  clearInterval(timerInterval)
})
</script>

<style scoped>
.minesweeper-container {
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  min-width: 500px;
  position: relative;
}

.game-header {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 0.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.6rem 1.2rem;
  border-radius: 12px;
  font-weight: 800;
  font-size: 1.2rem;
  color: var(--text-primary);
  min-width: 100px;
}

.reset-btn {
  padding: 0.6rem 1.2rem;
  border-radius: 12px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  color: var(--primary-color);
}

.reset-btn:hover {
  transform: scale(1.1);
  background: rgba(255,255,255,0.1);
}

.grid-wrapper {
  padding: 1rem;
  border-radius: 16px;
  background: rgba(0,0,0,0.2);
}

.grid {
  display: grid;
  gap: 6px;
  user-select: none;
}

.cell {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 950;
  font-size: 1.1rem;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
}

.cell:hover:not(.revealed) {
  background: rgba(255,255,255,0.1);
  transform: translateY(-2px);
  border-color: rgba(255,255,255,0.2);
}

.cell.revealed {
  background: rgba(0,0,0,0.2);
  border-color: rgba(255,255,255,0.03);
  cursor: default;
}

.cell.flagged { color: #f43f5e; }
.cell.mine { color: white; background: rgba(244, 63, 94, 0.4); }
.cell.exploded { background: #f43f5e; box-shadow: 0 0 20px #f43f5e; }

.count-1 { color: #60a5fa; }
.count-2 { color: #10b981; }
.count-3 { color: #f43f5e; }
.count-4 { color: #8b5cf6; }
.count-5 { color: #f59e0b; }

.game-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 3rem;
  border-radius: 24px;
  text-align: center;
  backdrop-filter: blur(15px);
  z-index: 50;
  border: 1px solid rgba(255,255,255,0.1);
}

.game-overlay h2 {
  font-size: 2.5rem;
  font-weight: 950;
  margin-bottom: 1.5rem;
  letter-spacing: 2px;
}

.final-stats {
  margin-bottom: 2rem;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-muted);
}

.kpi-win {
  color: #fbbf24;
  font-weight: 900;
  font-size: 1.5rem;
  margin-top: 0.5rem;
}

.premium-btn {
  padding: 1rem 2.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
}

.fade-enter-active, .fade-leave-active { transition: all 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translate(-50%, -40%) scale(0.9); }
</style>
