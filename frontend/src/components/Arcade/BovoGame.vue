<template>
  <div class="bovo-game" @contextmenu.prevent @mousedown="handleMouseDown" @mousemove="handleMouseMove" @mouseup="handleMouseUp" @wheel="handleWheel">
    <div class="game-controls glass-panel">
      <div class="stats">
         <span class="label">STONES:</span> <span class="value">{{ stones.length }}</span>
         <span class="label">TURN:</span> <span class="value" :class="currentTurn">{{ currentTurn.toUpperCase() }}</span>
      </div>
      <div class="actions">
        <select v-model="difficulty" class="difficulty-select">
          <option value="EASY">Easy</option>
          <option value="MEDIUM">Medium</option>
          <option value="HARD">Hard</option>
        </select>
        <button @click="undoMove" :disabled="stones.length < 2 || gameOver" class="control-btn"><i class="fas fa-undo"></i> Undo</button>
        <button @click="resetGame" class="control-btn"><i class="fas fa-redo"></i> New Game</button>
      </div>
    </div>

    <div class="board-viewport" ref="viewport">
      <div class="board-container" :style="containerStyle">
        <!-- The Grid -->
        <div class="grid-layer">
          <div v-for="i in size + 1" :key="'h'+i" class="grid-line horizontal" :style="{ top: (i-1) * cellSize + 'px', width: size * cellSize + 'px' }"></div>
          <div v-for="i in size + 1" :key="'v'+i" class="grid-line vertical" :style="{ left: (i-1) * cellSize + 'px', height: size * cellSize + 'px' }"></div>
        </div>
        
        <!-- Stones -->
        <div class="stones-layer">
          <div v-for="(stone, index) in stones" :key="index" 
               class="stone" 
               :class="stone[2]"
               :style="{ left: (stone[0] * cellSize) + 'px', top: (stone[1] * cellSize) + 'px', width: cellSize + 'px', height: cellSize + 'px' }">
          </div>
        </div>

        <!-- Ghost Stone for placement -->
        <div v-if="!gameOver && currentTurn === 'black'" 
             class="stone ghost black" 
             :style="ghostStoneStyle">
        </div>
      </div>
    </div>

    <div v-if="gameOver" class="game-over-modal glass-panel">
      <h2>{{ winner === 'black' ? 'YOU WIN!' : 'AI WINS!' }}</h2>
      <div v-if="winner === 'black'" class="reward"><i class="fas fa-coins"></i> +100 KPI</div>
      <button @click="resetGame" class="reset-btn">Play Again</button>
    </div>

    <div class="instructions glass-panel">
      <span><i class="fas fa-mouse"></i> Right-click to Pan</span>
      <span><i class="fas fa-mouse-pointer"></i> Middle-click to Zoom</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiPost } from '../../utils/api.js'

const emit = defineEmits(['gameOver'])

const size = 50
const cellSize = 30
const stones = ref([]) // [x, y, color]
const currentTurn = ref('black')
const difficulty = ref('MEDIUM')
const gameOver = ref(false)
const winner = ref(null)

// Pan & Zoom state
const scale = ref(1.0)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const lastMousePos = ref({ x: 0, y: 0 })
const viewport = ref(null)

const containerStyle = computed(() => ({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${scale.value})`,
  width: (size * cellSize) + 'px',
  height: (size * cellSize) + 'px'
}))

// Ghost stone logic
const mousePos = ref({ x: 0, y: 0 })
const ghostStoneStyle = computed(() => {
  const x = Math.round((mousePos.value.x - panX.value) / (cellSize * scale.value))
  const y = Math.round((mousePos.value.y - panY.value) / (cellSize * scale.value))
  
  if (x < 0 || x >= size || y < 0 || y >= size) return { display: 'none' }
  
  return {
    left: (x * cellSize) + 'px',
    top: (y * cellSize) + 'px',
    width: cellSize + 'px',
    height: cellSize + 'px',
    opacity: 0.5
  }
})

const handleMouseDown = (e) => {
  if (e.button === 2) { // Right click for pan
    isPanning.value = true
    lastMousePos.value = { x: e.clientX, y: e.clientY }
  } else if (e.button === 0 && !gameOver.value && currentTurn.value === 'black') {
    placeStone(e)
  }
}

const handleMouseMove = (e) => {
  mousePos.value = { x: e.clientX - viewport.value.getBoundingClientRect().left, y: e.clientY - viewport.value.getBoundingClientRect().top }
  
  if (isPanning.value) {
    panX.value += e.clientX - lastMousePos.value.x
    panY.value += e.clientY - lastMousePos.value.y
    lastMousePos.value = { x: e.clientX, y: e.clientY }
  }
}

const handleMouseUp = () => {
  isPanning.value = false
}

const handleWheel = (e) => {
  e.preventDefault()
  const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1
  const newScale = Math.max(0.2, Math.min(3, scale.value * zoomFactor))
  
  // Optional: zoom centered at mouse position
  scale.value = newScale
}

const placeStone = (e) => {
  const rect = viewport.value.getBoundingClientRect()
  const x = Math.round((e.clientX - rect.left - panX.value) / (cellSize * scale.value))
  const y = Math.round((e.clientY - rect.top - panY.value) / (cellSize * scale.value))
  
  if (x >= 0 && x < size && y >= 0 && y < size) {
    if (!stones.value.find(s => s[0] === x && s[1] === y)) {
      stones.value.push([x, y, 'black'])
      if (checkWin(x, y, 'black')) {
        onUserWin()
      } else {
        currentTurn.value = 'white'
        setTimeout(getAIMove, 500)
      }
    }
  }
}

const getAIMove = async () => {
  try {
    const data = await apiPost('/games/bovo/move', {
      board_size: size,
      stones: stones.value,
      difficulty: difficulty.value
    })
    
    const [x, y] = data.move
    stones.value.push([x, y, 'white'])
    if (checkWin(x, y, 'white')) {
      gameOver.value = true
      winner.value = 'white'
    } else {
      currentTurn.value = 'black'
    }
  } catch (err) {
    console.error('AI move error:', err)
  }
}

const checkWin = (x, y, color) => {
    const directions = [[1, 0], [0, 1], [1, 1], [1, -1]]
    const board = {}
    stones.value.forEach(s => board[`${s[0]},${s[1]}`] = s[2])
    
    for (const [dx, dy] of directions) {
        let count = 1
        for (let i = 1; i < 5; i++) {
            if (board[`${x + dx*i},${y + dy*i}`] === color) count++
            else break
        }
        for (let i = 1; i < 5; i++) {
            if (board[`${x - dx*i},${y - dy*i}`] === color) count++
            else break
        }
        if (count >= 5) return true
    }
    return false
}

const onUserWin = () => {
  gameOver.value = true
  winner.value = 'black'
  emit('gameOver', { kpi: 100 })
}

const undoMove = () => {
  if (stones.value.length >= 2) {
    stones.value.pop() // remove AI move
    stones.value.pop() // remove user move
  }
}

const resetGame = () => {
  stones.value = []
  gameOver.value = false
  winner.value = null
  currentTurn.value = 'black'
  panX.value = 0
  panY.value = 0
  scale.value = 1.0
}

const centerBoard = () => {
  if (viewport.value) {
    const vWidth = viewport.value.clientWidth
    const vHeight = viewport.value.clientHeight
    panX.value = (vWidth - size * cellSize) / 2
    panY.value = (vHeight - size * cellSize) / 2
  }
}

onMounted(() => {
  centerBoard()
})
</script>

<style scoped>
.bovo-game {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.game-controls {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
  margin: 1rem;
}

.stats .label { font-size: 0.8rem; font-weight: 800; color: var(--text-muted); margin-right: 0.5rem; }
.stats .value { font-weight: 900; margin-right: 1.5rem; }
.stats .value.black { color: #000; }
.stats .value.white { color: #fff; text-shadow: 0 0 2px #000; }

.difficulty-select {
  padding: 0.4rem;
  border-radius: 8px;
  background: var(--glass-bg-secondary);
  color: var(--text-primary);
  margin-right: 1rem;
}

.control-btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: none;
  background: var(--primary-color);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  margin-left: 0.5rem;
}

.board-viewport {
  flex: 1;
  cursor: crosshair;
  background: #deb887; /* Board wood color */
  box-shadow: inset 0 0 50px rgba(0,0,0,0.2);
  margin: 1rem;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.board-container {
  position: absolute;
  transform-origin: 0 0;
  transition: transform 0.05s linear;
}

.grid-line {
  position: absolute;
  background: rgba(0,0,0,0.3);
}

.grid-line.horizontal { height: 1px; }
.grid-line.vertical { width: 1px; }

.stones-layer {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none;
}

.stone {
  position: absolute;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
}

.stone.black { background: radial-gradient(circle at 30% 30%, #444, #000); }
.stone.white { background: radial-gradient(circle at 30% 30%, #fff, #ddd); }

.game-over-modal {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 3rem;
  text-align: center;
  z-index: 100;
  width: 90%;
  max-width: 400px;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  border-radius: 20px;
}

.reward { font-size: 2rem; font-weight: 900; color: #10b981; margin: 1rem 0; }
.reset-btn { background: var(--primary-color); color: white; padding: 1rem 2rem; border-radius: 8px; border: none; font-weight: 700; cursor: pointer; }

.instructions {
  position: absolute;
  bottom: 2rem;
  right: 2rem;
  padding: 0.8rem 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.8rem;
  font-weight: 700;
}
</style>
