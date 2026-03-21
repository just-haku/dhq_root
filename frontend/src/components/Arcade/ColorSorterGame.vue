<template>
  <div class="color-sorter-container glass-panel" :class="{ 'won': gameWon }">
    <div class="game-header">
      <div class="stat-card glass-panel">
        <span class="label">TUBES</span>
        <span class="value">{{ tubes.length }}</span>
      </div>
      <div class="stat-card glass-panel moves">
        <span class="label">MOVES</span>
        <span class="value">{{ moves }}</span>
      </div>
    </div>

    <div class="tubes-grid">
      <div 
        v-for="(tube, tIdx) in tubes" 
        :key="tIdx"
        class="tube-wrapper"
        @click="selectTube(tIdx)"
        :class="{ 'selected': selectedTube === tIdx }"
      >
        <div class="tube glass-panel">
          <div 
            v-for="(color, cIdx) in tube" 
            :key="cIdx"
            class="liquid-segment"
            :style="{ 
              backgroundColor: color, 
              bottom: (cIdx * 25) + '%',
              height: '25%',
              boxShadow: `0 0 15px ${color}66`
            }"
          ></div>
        </div>
      </div>
    </div>

    <div class="controls">
      <button class="premium-btn" @click="resetLevel">RESET LEVEL</button>
    </div>

    <transition name="fade">
      <div v-if="gameWon" class="game-overlay glass-panel">
        <h2>PURITY RESTORED</h2>
        <div class="final-stats">
          <p>MOVES: {{ moves }}</p>
          <p class="kpi-win">+50 KPI</p>
        </div>
        <button class="premium-btn" @click="nextLevel">NEXT MISSION</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiPost } from '../../utils/api.js'

const tubes = ref([])
const selectedTube = ref(null)
const moves = ref(0)
const gameWon = ref(false)
const difficulty = ref(5) // Start with 5 tubes

const colors = [
  '#f43f5e', // Red
  '#3b82f6', // Blue
  '#10b981', // Green
  '#fbbf24', // Amber
  '#8b5cf6', // Violet
]

const initLevel = () => {
  gameWon.value = false
  moves.value = 0
  selectedTube.value = null
  
  const activeColors = colors.slice(0, difficulty.value - 2)
  const allLiquids = []
  activeColors.forEach(c => {
    for(let i=0; i<4; i++) allLiquids.push(c)
  })

  // Shuffle
  for (let i = allLiquids.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [allLiquids[i], allLiquids[j]] = [allLiquids[j], allLiquids[i]]
  }

  const newTubes = []
  for (let i = 0; i < activeColors.length; i++) {
    newTubes.push(allLiquids.slice(i * 4, (i + 1) * 4))
  }
  // Add 2 empty tubes
  newTubes.push([])
  newTubes.push([])
  
  tubes.value = newTubes
}

const selectTube = (index) => {
  if (gameWon.value) return

  if (selectedTube.value === null) {
    if (tubes.value[index].length > 0) {
      selectedTube.value = index
    }
  } else {
    if (selectedTube.value === index) {
      selectedTube.value = null
      return
    }

    const fromTube = tubes.value[selectedTube.value]
    const toTube = tubes.value[index]
    const colorToMove = fromTube[fromTube.length - 1]

    // Rules:
    // 1. Target not full
    // 2. Target empty OR top color matches
    if (toTube.length < 4 && (toTube.length === 0 || toTube[toTube.length - 1] === colorToMove)) {
      // Move all adjacent matching colors
      while (fromTube.length > 0 && fromTube[fromTube.length - 1] === colorToMove && toTube.length < 4) {
        toTube.push(fromTube.pop())
      }
      moves.value++
      checkWin()
    }
    selectedTube.value = null
  }
}

const checkWin = () => {
  const won = tubes.value.every(t => {
    if (t.length === 0) return true
    if (t.length === 4) {
      return t.every(c => c === t[0])
    }
    return false
  })

  if (won) {
    gameWon.value = true
    submitScore()
  }
}

const submitScore = async () => {
  try {
    await apiPost('/games/scores/submit', {
      game_type: 'colorsorter',
      score: moves.value,
      kpi: 50
    })
  } catch (err) {
    console.error(err)
  }
}

const resetLevel = () => initLevel()
const nextLevel = () => {
  difficulty.value = Math.min(7, difficulty.value + 0.5)
  initLevel()
}

onMounted(() => {
  initLevel()
})
</script>

<style scoped>
.color-sorter-container {
  padding: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  min-width: 600px;
  position: relative;
}

.game-header {
  display: flex;
  gap: 2rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  padding: 0.6rem 1.5rem;
  border-radius: 12px;
  text-align: center;
  min-width: 100px;
}

.stat-card .label {
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--text-muted);
}

.stat-card .value {
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--primary-color);
}

.tubes-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem;
  margin: 2rem 0;
}

.tube-wrapper {
  cursor: pointer;
  transition: all 0.3s;
}

.tube-wrapper.selected {
  transform: translateY(-20px);
}

.tube {
  width: 60px;
  height: 180px;
  border-radius: 0 0 30px 30px;
  overflow: hidden;
  position: relative;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.2);
  display: flex;
  flex-direction: column-reverse;
}

.liquid-segment {
  width: 100%;
  position: absolute;
  left: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-top: 2px solid rgba(255,255,255,0.2);
}

.controls {
  margin-top: 1rem;
}

.premium-btn {
  padding: 1rem 2.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s;
}

.premium-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

.game-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 3rem;
  border-radius: 24px;
  text-align: center;
  z-index: 50;
  border: 1px solid rgba(255,255,255,0.1);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
