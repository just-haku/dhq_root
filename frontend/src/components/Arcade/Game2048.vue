<template>
  <div class="game-2048-container glass-panel">
    <div class="game-header">
      <div class="score-container">
        <div class="score-box glass-panel">
          <span class="label">SCORE</span>
          <span class="value">{{ score }}</span>
        </div>
        <div class="score-box glass-panel">
          <span class="label">BEST</span>
          <span class="value">{{ bestScore }}</span>
        </div>
      </div>
      <button @click="initGame" class="reset-btn">New Game</button>
    </div>

    <div class="game-board-wrapper">
      <div class="grid-container" 
           @touchstart="handleTouchStart" 
           @touchend="handleTouchEnd"
           @mousedown="handleMouseDown"
           @mouseup="handleMouseUp">
        <!-- Background Grid -->
        <div v-for="i in 16" :key="'bg'+i" class="grid-cell-bg"></div>
        
        <!-- Animated Tiles -->
        <transition-group name="tile-move">
          <div v-for="tile in tiles" 
               :key="tile.id" 
               class="tile" 
               :class="['tile-' + tile.value, { 'tile-merged': tile.mergedFrom }]"
               :style="getTileStyle(tile)">
            <div class="tile-inner">{{ tile.value }}</div>
          </div>
        </transition-group>
      </div>
    </div>

    <div class="game-instructions">
      <p>Use <b>Arrow Keys</b>, <b>WASD</b> or <b>Swipe</b> to merge tiles!</p>
    </div>
    
    <div v-if="gameOver" class="game-over-overlay glass-panel">
      <h2>Game Over!</h2>
      <p>Final Score: {{ score }}</p>
      <button @click="initGame" class="reset-btn">Try Again</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { apiPost } from '../../utils/api.js'

const tiles = ref([])
const score = ref(0)
const bestScore = ref(0)
const gameOver = ref(false)
let nextId = 1

const initGame = () => {
  tiles.value = []
  score.value = 0
  gameOver.value = false
  addTile()
  addTile()
}

const addTile = () => {
  const occupied = new Set(tiles.value.map(t => `${t.r},${t.c}`))
  const empty = []
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      if (!occupied.has(`${r},${c}`)) empty.push({ r, c })
    }
  }
  
  if (empty.length > 0) {
    const { r, c } = empty[Math.floor(Math.random() * empty.length)]
    tiles.value.push({
      id: nextId++,
      r,
      c,
      value: Math.random() < 0.9 ? 2 : 4,
      mergedFrom: null
    })
  }
}

const getTileStyle = (tile) => {
  const size = 80 // Match CSS
  const gap = 10  // Match CSS
  return {
    transform: `translate(${tile.c * (size + gap)}px, ${tile.r * (size + gap)}px)`
  }
}

const move = async (dir) => {
  if (gameOver.value) return
  
  const oldTilesJson = JSON.stringify(tiles.value.map(t => ({ r: t.r, c: t.c, v: t.value })))
  
  // Clear merged states before moving
  tiles.value.forEach(t => t.mergedFrom = null)
  
  // Group tiles by row or column based on direction
  const isVertical = dir === 'up' || dir === 'down'
  const isReverse = dir === 'right' || dir === 'down'
  
  let moved = false
  
  for (let i = 0; i < 4; i++) {
    let line = tiles.value.filter(t => (isVertical ? t.c : t.r) === i)
    line.sort((a, b) => isVertical ? a.r - b.r : a.c - b.c)
    if (isReverse) line.reverse()
    
    let nextPos = isReverse ? 3 : 0
    for (let j = 0; j < line.length; j++) {
      const tile = line[j]
      const nextTile = line[j + 1]
      
      if (nextTile && tile.value === nextTile.value) {
        // Merge
        moved = true
        const targetPos = nextPos
        tile.r = isVertical ? targetPos : tile.r
        tile.c = isVertical ? tile.c : targetPos
        nextTile.r = isVertical ? targetPos : nextTile.r
        nextTile.c = isVertical ? nextTile.c : targetPos
        
        // Finalize merge after animation (simplified for now: just update values immediately)
        tile.value *= 2
        score.value += tile.value
        tile.mergedFrom = [nextTile.id]
        
        // Remove merged-in tile
        tiles.value = tiles.value.filter(t => t.id !== nextTile.id)
        j++ // Skip the next tile
      } else {
        // Just slide
        if ((isVertical ? tile.r : tile.c) !== nextPos) {
          moved = true
          tile.r = isVertical ? nextPos : tile.r
          tile.c = isVertical ? tile.c : nextPos
        }
      }
      nextPos = isReverse ? nextPos - 1 : nextPos + 1
    }
  }
  
  if (moved) {
    addTile()
    if (checkGameOver()) {
      gameOver.value = true
      submitScore()
    }
  }
}

const checkGameOver = () => {
  if (tiles.value.length < 16) return false
  
  // Check for possible merges
  for (const t of tiles.value) {
    const neighbors = tiles.value.filter(n => 
      (Math.abs(n.r - t.r) === 1 && n.c === t.c) ||
      (Math.abs(n.c - t.c) === 1 && n.r === t.r)
    )
    if (neighbors.some(n => n.value === t.value)) return false
  }
  return true
}

const submitScore = async () => {
  try {
    await apiPost('/games/scores/submit', {
      game_type: '2048',
      score: score.value
    })
  } catch (err) {
    console.error('Score submission error:', err)
  }
}

const handleKeyDown = (e) => {
  const key = e.key.toLowerCase()
  if (key === 'arrowup' || key === 'w') move('up')
  else if (key === 'arrowdown' || key === 's') move('down')
  else if (key === 'arrowleft' || key === 'a') move('left')
  else if (key === 'arrowright' || key === 'd') move('right')
  
  if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'w', 'a', 's', 'd'].includes(key)) {
    e.preventDefault()
  }
}

// Mouse Drag handling
let startX, startY
const handleMouseDown = (e) => {
  startX = e.clientX
  startY = e.clientY
}
const handleMouseUp = (e) => {
  if (!startX || !startY) return
  const dx = e.clientX - startX
  const dy = e.clientY - startY
  const absX = Math.abs(dx)
  const absY = Math.abs(dy)
  
  if (Math.max(absX, absY) > 30) {
    if (absX > absY) {
      move(dx > 0 ? 'right' : 'left')
    } else {
      move(dy > 0 ? 'down' : 'up')
    }
  }
  startX = null
  startY = null
}

// Touch Handling
const handleTouchStart = (e) => {
  startX = e.touches[0].clientX
  startY = e.touches[0].clientY
}
const handleTouchEnd = (e) => {
  if (!startX || !startY) return
  const dx = e.changedTouches[0].clientX - startX
  const dy = e.changedTouches[0].clientY - startY
  const absX = Math.abs(dx)
  const absY = Math.abs(dy)
  
  if (Math.max(absX, absY) > 30) {
    if (absX > absY) {
      move(dx > 0 ? 'right' : 'left')
    } else {
      move(dy > 0 ? 'down' : 'up')
    }
  }
  startX = null
  startY = null
}

onMounted(() => {
  initGame()
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('mousedown', handleMouseDown)
  window.addEventListener('mouseup', handleMouseUp)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('mousedown', handleMouseDown)
  window.removeEventListener('mouseup', handleMouseUp)
})
</script>

<style scoped>
.game-2048-container {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.game-header {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 400px;
}

.score-container {
  display: flex;
  gap: 1rem;
}

.score-box {
  padding: 0.5rem 1.5rem;
  text-align: center;
  border-radius: 8px;
  background: var(--glass-bg-secondary);
}

.score-box .label {
  font-size: 0.7rem;
  font-weight: 700;
  display: block;
}

.score-box .value {
  font-size: 1.2rem;
  font-weight: 900;
}

.reset-btn {
  background: var(--primary-color);
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

.grid-container {
  background: #bbada0;
  padding: 10px;
  border-radius: 10px;
  position: relative;
  width: 370px; /* 4*80 + 5*10 */
  height: 370px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.grid-cell-bg {
  width: 80px;
  height: 80px;
  background: rgba(238, 228, 218, 0.35);
  border-radius: 5px;
}

.tile-move-move {
  transition: transform 0.15s ease-in-out;
}

.tile {
  position: absolute;
  width: 80px;
  height: 80px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.2rem;
  font-weight: 800;
  transition: transform 0.15s ease-in-out;
  z-index: 10;
}

.tile-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: tile-appear 0.2s ease-out;
}

@keyframes tile-appear {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.tile-merged .tile-inner {
  animation: tile-merge 0.2s ease-in-out;
}

@keyframes tile-merge {
  0% { transform: scale(1); }
  50% { transform: scale(1.15); }
  100% { transform: scale(1); }
}

.tile-2 { background: #eee4da; color: #776e65; }
.tile-4 { background: #ede0c8; color: #776e65; }
.tile-8 { background: #f2b179; color: #f9f6f2; }
.tile-16 { background: #f59563; color: #f9f6f2; }
.tile-32 { background: #f67c5f; color: #f9f6f2; }
.tile-64 { background: #f65e3b; color: #f9f6f2; }
.tile-128 { background: #edcf72; color: #f9f6f2; font-size: 1.8rem; }
.tile-256 { background: #edcc61; color: #f9f6f2; font-size: 1.8rem; }
.tile-512 { background: #edc850; color: #f9f6f2; font-size: 1.8rem; }
.tile-1024 { background: #edc53f; color: #f9f6f2; font-size: 1.5rem; }
.tile-2048 { background: #edc22e; color: #f9f6f2; font-size: 1.5rem; }

.game-over-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(238, 228, 218, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border-radius: 10px;
}

.game-over-overlay h2 {
  font-size: 3rem;
  color: #776e65;
  margin-bottom: 1rem;
}

.game-instructions {
  text-align: center;
  color: var(--text-muted);
}
</style>
