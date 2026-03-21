<template>
  <div class="tictactoe-game">
    <div class="game-header-stats glass-panel">
      <div v-if="gameMode === 'AI'" class="ai-controls">
        <label>Difficulty:</label>
        <select v-model="difficulty" :disabled="moves.length > 0" class="difficulty-select">
          <option value="EASY">Easy</option>
          <option value="MEDIUM">Medium</option>
          <option value="HARD">Hard</option>
        </select>
      </div>
      <div v-else class="multiplayer-status">
        <span v-if="!opponent" class="waiting">Waiting for opponent...</span>
        <span v-else class="playing">Playing vs {{ opponent.username }}</span>
      </div>
      
      <div class="turn-indicator" :class="{ 'my-turn': isMyTurn }">
        {{ isMyTurn ? 'YOUR TURN' : 'OPPONENT TURN' }}
      </div>
    </div>

    <div class="ttt-board glass-panel">
      <div v-for="(cell, index) in board" :key="index" 
           @click="makeMove(index)"
           class="ttt-cell"
           :class="{ 'taken': cell, 'win-cell': winLine?.includes(index) }">
        <span v-if="cell" :class="cell.toLowerCase()">{{ cell }}</span>
      </div>
    </div>

    <!-- Mode Selector if game not started -->
    <div v-if="!gameStarted" class="mode-selector-modal glass-panel">
       <h2>Select Game Mode</h2>
       <div class="mode-buttons">
         <button @click="startAIMode" class="mode-btn"><i class="fas fa-robot"></i> VS AI</button>
         <button @click="startMultiplayerMode" class="mode-btn"><i class="fas fa-users"></i> Multiplayer</button>
       </div>
    </div>

    <div v-if="winner" class="game-over-modal glass-panel">
      <h2>{{ getGameOverMessage() }}</h2>
      <div v-if="winner === mySymbol" class="reward">
        <i class="fas fa-coins"></i> +{{ difficulty === 'HARD' ? 50 : difficulty === 'MEDIUM' ? 20 : 10 }} KPI
      </div>
      <button @click="resetGame" class="reset-btn">Play Again</button>
      <button @click="$emit('exit')" class="exit-btn">Exit to Arcade</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { apiPost } from '../../utils/api.js'
import { io } from 'socket.io-client'

const emit = defineEmits(['gameOver', 'exit'])

// Game State
const gameStarted = ref(false)
const gameMode = ref('AI') // 'AI' or 'MP'
const difficulty = ref('MEDIUM')
const board = ref(new Array(9).fill(null))
const mySymbol = ref('X')
const currentTurn = ref('X')
const winner = ref(null) // 'X', 'O', or 'TIE'
const winLine = ref(null)
const moves = ref([])

// Multiplayer State
const socket = ref(null)
const opponent = ref(null)
const roomId = ref(null)

const isMyTurn = computed(() => {
  if (winner.value) return false
  return currentTurn.value === mySymbol.value
})

const startAIMode = () => {
  gameMode.value = 'AI'
  gameStarted.value = true
  mySymbol.value = 'X'
  currentTurn.value = 'X'
}

const startMultiplayerMode = () => {
  gameMode.value = 'MP'
  gameStarted.value = true
  initSocket()
}

const initSocket = () => {
  const token = localStorage.getItem('token')
  socket.value = io(`${window.location.protocol}//${window.location.host}`, {
    auth: { token },
    query: { token }
  })

  socket.value.on('connect', () => {
    roomId.value = Math.random().toString(36).substring(7)
    socket.value.emit('join_game_room', {
      game_type: 'tictactoe',
      room_id: roomId.value,
      user_id: JSON.parse(localStorage.getItem('user')).id
    })
  })

  socket.value.on('player_joined', (data) => {
    // Basic matchmaking simulation
    if (!opponent.value && data.user_id !== JSON.parse(localStorage.getItem('user')).id) {
       opponent.value = { username: 'Player_' + data.user_id.slice(-4) }
       mySymbol.value = 'X' // First to join is X
    }
  })

  socket.value.on('new_move', (data) => {
    if (data.game_type === 'tictactoe') {
      executeMove(data.move, mySymbol.value === 'X' ? 'O' : 'X')
    }
  })
}

const makeMove = async (index) => {
  if (board.value[index] || winner.value || !isMyTurn.value) return
  
  executeMove(index, mySymbol.value)
  
  if (gameMode.value === 'AI' && !winner.value) {
    currentTurn.value = 'O'
    setTimeout(getAIMove, 500)
  } else if (gameMode.value === 'MP' && socket.value) {
    socket.value.emit('game_move', {
      game_type: 'tictactoe',
      room_id: roomId.value,
      move: index
    })
    currentTurn.value = mySymbol.value === 'X' ? 'O' : 'X'
  }
}

const executeMove = (index, symbol) => {
  board.value[index] = symbol
  moves.value.push(index)
  checkGameStatus()
  currentTurn.value = symbol === 'X' ? 'O' : 'X'
}

const getAIMove = async () => {
  try {
    const data = await apiPost('/games/tictactoe/move', {
      board: board.value,
      difficulty: difficulty.value
    })
    executeMove(data.move, 'O')
  } catch (err) {
    console.error('AI move error:', err)
  }
}

const checkGameStatus = () => {
  const lines = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6]
  ]
  
  for (const line of lines) {
    const [a, b, c] = line
    if (board.value[a] && board.value[a] === board.value[b] && board.value[a] === board.value[c]) {
      winner.value = board.value[a]
      winLine.value = line
      if (winner.value === mySymbol.value) {
        const kpi = difficulty.value === 'HARD' ? 50 : difficulty.value === 'MEDIUM' ? 20 : 10
        emit('gameOver', { kpi, difficulty: difficulty.value })
      }
      return
    }
  }
  
  if (!board.value.includes(null)) {
    winner.value = 'TIE'
  }
}

const getGameOverMessage = () => {
  if (winner.value === 'TIE') return "IT'S A TIE!"
  return winner.value === mySymbol.value ? "YOU WIN!" : "AI WINS!"
}

const resetGame = () => {
  board.value = new Array(9).fill(null)
  winner.value = null
  winLine.value = null
  moves.value = []
  currentTurn.value = 'X'
}

onUnmounted(() => {
  if (socket.value) socket.value.disconnect()
})
</script>

<style scoped>
.tictactoe-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  max-width: 400px;
}

.game-header-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 1rem 1.5rem;
}

.difficulty-select {
  margin-left: 0.5rem;
  padding: 0.3rem;
  border-radius: 4px;
  background: var(--glass-bg-secondary);
  color: var(--text-primary);
}

.turn-indicator {
  font-weight: 800;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  background: var(--glass-bg-secondary);
  color: var(--text-muted);
}

.turn-indicator.my-turn {
  background: var(--primary-color);
  color: #fff;
}

.ttt-board {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  padding: 15px;
  width: 320px;
  height: 320px;
}

.ttt-cell {
  background: var(--glass-bg-primary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.3s ease;
  aspect-ratio: 1;
}

.ttt-cell:hover:not(.taken) {
  background: var(--glass-bg-hover);
  transform: scale(1.05);
}

.ttt-cell.taken { cursor: default; }

.ttt-cell span.x { color: var(--primary-color); }
.ttt-cell span.o { color: var(--secondary-color); }

.ttt-cell.win-cell {
  background: #10b981;
  animation: pulse 1s infinite;
}

.mode-selector-modal {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 3rem;
  text-align: center;
  z-index: 20;
  width: 90%;
  max-width: 400px;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  border-radius: 20px;
}

.mode-buttons {
  display: flex;
  gap: 1.5rem;
  margin-top: 2rem;
}

.mode-btn {
  padding: 1rem 2rem;
  border-radius: 12px;
  border: none;
  background: var(--primary-color);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.mode-btn:hover { transform: translateY(-3px); box-shadow: 0 5px 15px var(--primary-color); }

.game-over-modal {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 2.5rem;
  text-align: center;
  z-index: 30;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 90%;
  max-width: 350px;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  border-radius: 20px;
}

.reward { font-size: 1.5rem; font-weight: 900; color: #10b981; }

.reset-btn, .exit-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  border: none;
  font-weight: 700;
  cursor: pointer;
}

.reset-btn { background: var(--primary-color); color: #fff; }
.exit-btn { background: var(--danger-color); color: #fff; }

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
</style>
