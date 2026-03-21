<template>
  <div class="wordle-game">
    <div class="stats-panel glass-panel">
      <div class="stat">
        <span class="label">ATTEMPTS</span>
        <span class="value">{{ attempts.length }} / 6</span>
      </div>
      <div class="stat">
        <span class="label">SCORE</span>
        <span class="value">{{ score }}</span>
      </div>
    </div>

    <div class="board">
      <div v-for="(row, rIndex) in 6" :key="rIndex" class="row">
        <div v-for="(col, cIndex) in 5" :key="cIndex" 
             class="cell" 
             :class="getCellClass(rIndex, cIndex)">
          {{ getCellLetter(rIndex, cIndex) }}
        </div>
      </div>
    </div>

    <div class="keyboard">
      <div v-for="(row, rIndex) in keyboardRows" :key="rIndex" class="key-row">
        <button v-for="key in row" :key="key" 
                @click="onKeyClick(key)"
                class="key"
                :class="getKeyClass(key)">
          {{ key === 'BACKSPACE' ? '⌫' : key }}
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-overlay glass-panel">
      <i class="fas fa-spinner fa-spin"></i>
      <span>Initializing Wordle...</span>
    </div>

    <div v-if="errorMessage" class="error-overlay glass-panel">
      <i class="fas fa-exclamation-triangle"></i>
      <span>{{ errorMessage }}</span>
      <button @click="startNewGame" class="retry-btn">Retry</button>
    </div>

    <div v-if="gameOver" class="game-over-modal glass-panel">
      <h2>{{ gameWon ? 'CONGRATULATIONS!' : 'GAME OVER' }}</h2>
      <p v-if="gameWon">You guessed the word in {{ attempts.length }} tries!</p>
      <p v-else>The word was: <strong>{{ targetWord }}</strong></p>
      <div class="reward">
        <i class="fas fa-coins"></i> +{{ kpiEarned }} KPI
      </div>
      <button @click="handleContinue" class="continue-btn">Continue (Press Enter)</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiPost } from '../../utils/api.js'

const emit = defineEmits(['gameOver'])

// Game State
const targetWord = ref('')
const gameId = ref('')
const currentGuess = ref('')
const attempts = ref([]) // List of { word, result: [{letter, status}, ...] }
const gameOver = ref(false)
const gameWon = ref(false)
const score = ref(0)
const kpiEarned = ref(0)
const isLoading = ref(true)
const errorMessage = ref('')

const keyboardRows = [
  ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
  ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
  ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'BACKSPACE']
]

const letterStatuses = ref({}) // { 'A': 'correct', 'B': 'absent', ... }

// Initialization
const startNewGame = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const data = await apiPost('/games/wordle/new')
    gameId.value = data.game_id
    targetWord.value = data.word // In production, targetWord is masked
  } catch (err) {
    errorMessage.value = 'Network error. Please check your connection.'
  } finally {
    isLoading.value = false
  }
}

// Logic
const handleContinue = () => {
  emit('gameOver', { kpi: kpiEarned.value })
  // Reset for new game
  attempts.value = []
  letterStatuses.value = {}
  currentGuess.value = ''
  gameOver.value = false
  gameWon.value = false
  kpiEarned.value = 0
  startNewGame()
}

const onKeyClick = (key) => {
  if (isLoading.value) return
  
  if (gameOver.value) {
    if (key === 'ENTER') handleContinue()
    return
  }
  
  if (key === 'ENTER') {
    if (!gameId.value) return
    submitGuess()
  } else if (key === 'BACKSPACE') {
    currentGuess.value = currentGuess.value.slice(0, -1)
  } else if (currentGuess.value.length < 5) {
    currentGuess.value += key
  }
}

const submitGuess = async () => {
  if (currentGuess.value.length !== 5) return
  
  try {
    const data = await apiPost(`/games/wordle/guess?game_id=${gameId.value}`, {
      guess: currentGuess.value
    })
    
    attempts.value.push({
      word: currentGuess.value,
      result: data.result
    })
    
    // Update letter statuses for keyboard
    data.result.forEach(r => {
      const current = letterStatuses.value[r.letter]
      if (r.status === 'correct') {
        letterStatuses.value[r.letter] = 'correct'
      } else if (r.status === 'present' && current !== 'correct') {
        letterStatuses.value[r.letter] = 'present'
      } else if (!current) {
        letterStatuses.value[r.letter] = 'absent'
      }
    })

    if (data.is_win) {
      gameWon.value = true
      gameOver.value = true
      kpiEarned.value = 50
      score.value += 100
    } else if (attempts.value.length >= 6) {
      gameOver.value = true
      gameWon.value = false
      kpiEarned.value = 5
      score.value = 0
    }
    
    currentGuess.value = ''
  } catch (err) {
    // showAlert handled by apiRequest, but manual alert here for validation if needed
    console.error('Wordle guess error:', err)
  }
}

// UI Helpers
const getCellLetter = (r, c) => {
  if (r < attempts.value.length) {
    return attempts.value[r].word[c]
  }
  if (r === attempts.value.length) {
    return currentGuess.value[c] || ''
  }
  return ''
}

const getCellClass = (r, c) => {
  if (r < attempts.value.length) {
    return attempts.value[r].result[c].status
  }
  if (r === attempts.value.length && currentGuess.value[c]) {
    return 'active'
  }
  return ''
}

const getKeyClass = (key) => {
  return letterStatuses.value[key] || ''
}

// Physical Keyboard Support
const handleKeyDown = (e) => {
  const key = e.key.toUpperCase()
  if (key === 'ENTER') onKeyClick('ENTER')
  if (gameOver.value) return
  if (key === 'BACKSPACE') onKeyClick('BACKSPACE')
  if (/^[A-Z]$/.test(key)) onKeyClick(key)
}

onMounted(() => {
  startNewGame()
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.wordle-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  max-width: 500px;
}

.stats-panel {
  display: flex;
  gap: 3rem;
  padding: 1rem 2rem;
  width: 100%;
  justify-content: center;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat .label { font-size: 0.7rem; color: var(--text-muted); font-weight: 800; }
.stat .value { font-size: 1.5rem; font-weight: 900; color: var(--primary-color); }

.board {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.row {
  display: flex;
  gap: 8px;
}

.cell {
  width: 50px;
  height: 50px;
  border: 2px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 900;
  border-radius: 4px;
  text-transform: uppercase;
  transition: all 0.2s ease;
}

.cell.active { transform: scale(1.1); border-color: var(--text-primary); }
.cell.correct { background: #10b981; color: white; border-color: #10b981; }
.cell.present { background: #f59e0b; color: white; border-color: #f59e0b; }
.cell.absent { background: #64748b; color: white; border-color: #64748b; }

.keyboard {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.key-row {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.key {
  min-width: 32px;
  height: 45px;
  padding: 0 10px;
  border: none;
  background: var(--glass-bg-secondary);
  color: var(--text-primary);
  border-radius: 4px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.key:hover { background: var(--glass-bg-hover); }
.key.correct { background: #10b981; color: white; }
.key.present { background: #f59e0b; color: white; }
.key.absent { background: #334155; color: white; }

.key:nth-child(1), .key:nth-last-child(1) {
  min-width: 65px;
}

.game-over-modal {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 3rem;
  text-align: center;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  box-shadow: 0 0 50px rgba(0,0,0,0.5);
}

.reward {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--primary-color);
}

.continue-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

.loading-overlay, .error-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  z-index: 20;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.loading-overlay i { font-size: 2rem; color: var(--primary-color); }
.error-overlay i { font-size: 2rem; color: var(--danger-color); }
.retry-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
</style>
