<template>
  <div class="word-search-container glass-panel">
    <div class="game-header">
      <div class="header-info">
        <h1>Word Search</h1>
        <p>Find the words hidden in the grid!</p>
      </div>
      <div class="words-found">
        Found: {{ foundWords.length }} / {{ targetWords.length }}
      </div>
    </div>

    <div class="game-layout">
      <div class="grid-container" @mouseleave="handleMouseUp">
        <div v-for="(row, r) in grid" :key="r" class="grid-row">
          <div v-for="(cell, c) in row" :key="c" 
               class="grid-cell"
               :class="{ 
                 'highlighted': isHighlighted(r, c), 
                 'found': isCellFound(r, c) 
               }"
               @mousedown="handleMouseDown(r, c)"
               @mouseenter="handleMouseEnter(r, c)"
               @mouseup="handleMouseUp">
            {{ cell }}
          </div>
        </div>
      </div>

      <div class="word-list glass-panel">
        <h3>WORDS TO FIND</h3>
        <ul>
          <li v-for="word in targetWords" :key="word" 
              :class="{ 'found': foundWords.includes(word) }">
            {{ word }}
          </li>
        </ul>
      </div>
    </div>

    <div class="actions">
      <button @click="initGame" class="new-game-btn">New Puzzle</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiPost } from '../../utils/api.js'

const grid = ref([])
const gridSize = 12
const wordLibrary = [
  'VUE', 'JAVASCRIPT', 'ARCADE', 'DHQ', 'VITE', 'GAMING', 'REWARD', 'CHIPS', 'STREAK', 'LUCK', 'WINNER', 'PLAY', 'BLOCK', 'CHALLENGE', 'PUZZLE',
  'RETRO', 'JOYSTICK', 'CONSOLE', 'PIXEL', 'LEVEL', 'QUEST', 'SCORE', 'COINS', 'AVATAR', 'QUEST', 'STAGE', 'POWERUP', 'LEGEND', 'MASTER'
]
const targetWords = ref([])
const foundWords = ref([])
const selection = ref(null) 
const isDragging = ref(false)
const foundCells = ref(new Set()) // Store "r,c" strings

const directions = [
  [0, 1], [1, 0], [1, 1], [1, -1] // Right, Down, Down-Right, Down-Left
]

const initGame = () => {
  targetWords.value = shuffleArray([...wordLibrary]).slice(0, 8)
  foundWords.value = []
  foundCells.value = new Set()
  generateGrid()
}

const generateGrid = () => {
  grid.value = Array(gridSize).fill().map(() => Array(gridSize).fill(''))
  
  targetWords.value.forEach((word, wordIndex) => {
    let placed = false
    let attempts = 0
    
    // Attempt intersection for words after the first one
    if (wordIndex > 0) {
      const chars = word.split('')
      // Shuffle characters to try different intersection points
      shuffleArray(chars)
      
      for (const char of chars) {
        // Find all instances of this char in the grid
        const positions = []
        for (let r = 0; r < gridSize; r++) {
          for (let c = 0; c < gridSize; c++) {
            if (grid.value[r][c] === char) positions.push({ r, c })
          }
        }
        
        shuffleArray(positions)
        for (const pos of positions) {
          const charIndex = word.indexOf(char)
          const availableDirs = shuffleArray([...directions])
          
          for (const dir of availableDirs) {
            // Calculate start position if this char is at charIndex
            const startR = pos.r - charIndex * dir[0]
            const startC = pos.c - charIndex * dir[1]
            
            if (canPlace(word, startR, startC, dir)) {
              for (let i = 0; i < word.length; i++) {
                grid.value[startR + i * dir[0]][startC + i * dir[1]] = word[i]
              }
              placed = true
              break
            }
          }
          if (placed) break
        }
        if (placed) break
      }
    }
    
    // Fallback to random placement
    while (!placed && attempts < 100) {
      const dir = directions[Math.floor(Math.random() * directions.length)]
      const r = Math.floor(Math.random() * gridSize)
      const c = Math.floor(Math.random() * gridSize)
      
      if (canPlace(word, r, c, dir)) {
        for (let i = 0; i < word.length; i++) {
          grid.value[r + i * dir[0]][c + i * dir[1]] = word[i]
        }
        placed = true
      }
      attempts++
    }
  })
  
  for (let r = 0; r < gridSize; r++) {
    for (let c = 0; c < gridSize; c++) {
      if (!grid.value[r][c]) {
        grid.value[r][c] = String.fromCharCode(65 + Math.floor(Math.random() * 26))
      }
    }
  }
}

const canPlace = (word, r, c, dir) => {
  for (let i = 0; i < word.length; i++) {
    const nr = r + i * dir[0]
    const nc = c + i * dir[1]
    if (nr < 0 || nr >= gridSize || nc < 0 || nc >= gridSize) return false
    // Collision check allowing intersections
    if (grid.value[nr][nc] && grid.value[nr][nc] !== word[i]) return false
  }
  return true
}

const handleMouseDown = (r, c) => {
  isDragging.value = true
  selection.value = { start: { r, c }, end: { r, c } }
}

const handleMouseEnter = (r, c) => {
  if (isDragging.value) {
    selection.value.end = { r, c }
  }
}

const handleMouseUp = async () => {
  if (!isDragging.value) return
  isDragging.value = false
  
  const selectedWord = getSelectedWord()
  // REMOVED: reversedWord logic to fix user confusing.
  // Directional selection is now enforced.
  let match = targetWords.value.includes(selectedWord) ? selectedWord : null
  
  if (match && !foundWords.value.includes(match)) {
    foundWords.value.push(match)
    markCellsAsFound()
    if (foundWords.value.length === targetWords.value.length) {
      await submitScore()
    }
  }
  
  selection.value = null
}

const getSelectedWord = () => {
  if (!selection.value) return ''
  const { start, end } = selection.value
  
  const distR = Math.abs(end.r - start.r)
  const distC = Math.abs(end.c - start.c)
  
  if (distR !== 0 && distC !== 0 && distR !== distC) return ''
  
  const steps = Math.max(distR, distC)
  const sr = Math.sign(end.r - start.r) || 0
  const sc = Math.sign(end.c - start.c) || 0
  
  let word = ''
  for (let i = 0; i <= steps; i++) {
    word += grid.value[start.r + i * sr][start.c + i * sc]
  }
  return word
}

const markCellsAsFound = () => {
  if (!selection.value) return
  const { start, end } = selection.value
  const steps = Math.max(Math.abs(end.r - start.r), Math.abs(end.c - start.c))
  const sr = Math.sign(end.r - start.r) || 0
  const sc = Math.sign(end.c - start.c) || 0
  
  for (let i = 0; i <= steps; i++) {
    foundCells.value.add(`${start.r + i * sr},${start.c + i * sc}`)
  }
}

const isHighlighted = (r, c) => {
  if (!selection.value) return false
  const { start, end } = selection.value
  const distR = Math.abs(end.r - start.r)
  const distC = Math.abs(end.c - start.c)
  if (distR !== 0 && distC !== 0 && distR !== distC) return false
  
  const steps = Math.max(distR, distC)
  const sr = Math.sign(end.r - start.r) || 0
  const sc = Math.sign(end.c - start.c) || 0
  
  for (let i = 0; i <= steps; i++) {
    if (start.r + i * sr === r && start.c + i * sc === c) return true
  }
  return false
}

const isCellFound = (r, c) => foundCells.value.has(`${r},${c}`)

const submitScore = async () => {
  try {
    await apiPost('/games/scores/submit', { game_type: 'wordsearch', score: 100 })
  } catch (err) {
    console.error('Score submission error:', err)
  }
}

const shuffleArray = (arr) => arr.sort(() => Math.random() - 0.5)

onMounted(initGame)
</script>

<style scoped>
.word-search-container {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;
}

.game-header {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 800px;
}

.game-layout {
  display: flex;
  gap: 2rem;
}

.grid-container {
  background: var(--glass-bg-secondary);
  padding: 1rem;
  border-radius: 12px;
  user-select: none;
  cursor: crosshair;
}

.grid-row {
  display: flex;
}

.grid-cell {
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.grid-cell.highlighted {
  background: var(--primary-color);
  color: white;
  border-radius: 4px;
}

.grid-cell.found {
  color: var(--secondary-color);
}

.word-list {
  padding: 1.5rem;
  min-width: 150px;
}

.word-list ul {
  list-style: none;
  padding: 0;
  margin-top: 1rem;
}

.word-list li {
  padding: 0.3rem 0;
  font-weight: 700;
  color: var(--text-muted);
}

.word-list li.found {
  text-decoration: line-through;
  color: var(--secondary-color);
}

.new-game-btn {
  padding: 0.8rem 2rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
}
</style>
