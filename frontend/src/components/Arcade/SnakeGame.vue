<template>
  <div class="snake-game-container glass-panel" :class="{ 'game-over': state === 'OVER' }">
    <div class="game-header">
      <div class="score-card glass-panel">
        <span class="label">LENGTH</span>
        <span class="value">{{ score }}</span>
      </div>
      <div class="score-card glass-panel best">
        <span class="label">RECORD</span>
        <span class="value">{{ highScore }}</span>
      </div>
    </div>

    <div class="canvas-wrapper">
      <canvas ref="canvasRef" width="400" height="400"></canvas>
      
      <transition name="fade">
        <div v-if="state !== 'PLAYING'" class="overlay glass-panel" @click="startGame">
          <div class="overlay-content">
            <div class="snake-icon"><i class="fas fa-worm"></i></div>
            <h2>{{ state === 'START' ? 'NEON SNAKE' : 'SYSTEM CRASHED' }}</h2>
            <p>{{ state === 'START' ? 'INITIALIZE LINK' : 'REBOOT SYSTEM' }}</p>
            <div v-if="state === 'OVER'" class="final-stats">
              <div class="stat">SCORE: {{ score }}</div>
              <div class="stat">KPI: {{ Math.floor(score * 2) }}</div>
            </div>
            <button class="premium-btn">{{ state === 'START' ? 'START' : 'RETRY' }}</button>
            <div class="hints">WASD or ARROWS</div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiPost } from '../../utils/api.js'

const canvasRef = ref(null)
const score = ref(0)
const highScore = ref(localStorage.getItem('snake_high_score') || 0)
const state = ref('START')

let ctx, animationFrame
let snake = []
let food = { x: 0, y: 0 }
let direction = 'RIGHT'
let nextDirection = 'RIGHT'
const gridSize = 20
const tileCount = 20
let gameSpeed = 100
let lastUpdate = 0

const startGame = () => {
  score.value = 0
  state.value = 'PLAYING'
  snake = [
    { x: 10, y: 10 },
    { x: 9, y: 10 },
    { x: 8, y: 10 }
  ]
  direction = 'RIGHT'
  nextDirection = 'RIGHT'
  spawnFood()
  gameLoop(0)
}

const spawnFood = () => {
  food = {
    x: Math.floor(Math.random() * tileCount),
    y: Math.floor(Math.random() * tileCount)
  }
  // Don't spawn on snake
  if (snake.some(s => s.x === food.x && s.y === food.y)) {
    spawnFood()
  }
}

const update = () => {
  direction = nextDirection
  const head = { ...snake[0] }

  if (direction === 'RIGHT') head.x++
  if (direction === 'LEFT') head.x--
  if (direction === 'UP') head.y--
  if (direction === 'DOWN') head.y++

  // Edge collision
  if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
    return endGame()
  }

  // Self collision
  if (snake.some(s => s.x === head.x && s.y === head.y)) {
    return endGame()
  }

  snake.unshift(head)

  // Eat food
  if (head.x === food.x && head.y === food.y) {
    score.value++
    spawnFood()
    // Speed up slightly
    gameSpeed = Math.max(60, 100 - score.value)
  } else {
    snake.pop()
  }
}

const draw = () => {
  if (!ctx) return
  ctx.fillStyle = '#0a0a0f'
  ctx.fillRect(0, 0, 400, 400)

  // Draw Grid lines (Subtle)
  ctx.strokeStyle = 'rgba(255,255,255,0.03)'
  ctx.lineWidth = 1
  for(let i=0; i<=tileCount; i++) {
    ctx.beginPath(); ctx.moveTo(i*gridSize, 0); ctx.lineTo(i*gridSize, 400); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(0, i*gridSize); ctx.lineTo(400, i*gridSize); ctx.stroke()
  }

  // Draw Food
  ctx.shadowBlur = 15
  ctx.shadowColor = '#f43f5e'
  ctx.fillStyle = '#f43f5e'
  ctx.beginPath()
  ctx.arc(food.x * gridSize + gridSize/2, food.y * gridSize + gridSize/2, gridSize/3, 0, Math.PI*2)
  ctx.fill()

  // Draw Snake
  snake.forEach((part, index) => {
    const isHead = index === 0
    ctx.shadowBlur = isHead ? 20 : 10
    ctx.shadowColor = isHead ? '#3b82f6' : '#60a5fa'
    
    // Gradient based on position
    const alpha = 1 - (index / snake.length) * 0.5
    ctx.fillStyle = isHead ? '#3b82f6' : `rgba(96, 165, 250, ${alpha})`
    
    const x = part.x * gridSize + 2
    const y = part.y * gridSize + 2
    const s = gridSize - 4
    
    roundRect(ctx, x, y, s, s, isHead ? 6 : 4)
    ctx.fill()
  })
  ctx.shadowBlur = 0
}

function roundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
  ctx.lineTo(x + radius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
}

const gameLoop = (timestamp) => {
  if (state.value !== 'PLAYING') return

  const elapsed = timestamp - lastUpdate
  if (elapsed > gameSpeed) {
    update()
    lastUpdate = timestamp
  }
  
  draw()
  animationFrame = requestAnimationFrame(gameLoop)
}

const handleKey = (e) => {
  if (state.value !== 'PLAYING') return
  
  if ((e.key === 'ArrowUp' || e.key === 'w') && direction !== 'DOWN') nextDirection = 'UP'
  if ((e.key === 'ArrowDown' || e.key === 's') && direction !== 'UP') nextDirection = 'DOWN'
  if ((e.key === 'ArrowLeft' || e.key === 'a') && direction !== 'RIGHT') nextDirection = 'LEFT'
  if ((e.key === 'ArrowRight' || e.key === 'd') && direction !== 'LEFT') nextDirection = 'RIGHT'
}

const endGame = async () => {
  state.value = 'OVER'
  if (score.value > highScore.value) {
    highScore.value = score.value
    localStorage.setItem('snake_high_score', score.value.toString())
  }
  
  try {
    const kpi = Math.floor(score.value * 2)
    await apiPost('/games/scores/submit', {
      game_type: 'snake',
      score: score.value,
      kpi: kpi
    })
  } catch (err) {
    console.error('Score submission error:', err)
  }
}

onMounted(() => {
  ctx = canvasRef.value.getContext('2d')
  window.addEventListener('keydown', handleKey)
  draw()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKey)
  if (animationFrame) cancelAnimationFrame(animationFrame)
})
</script>

<style scoped>
.snake-game-container {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  min-width: 450px;
}

.game-header {
  display: flex;
  justify-content: center;
  gap: 2rem;
  width: 100%;
}

.score-card {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 1.5rem;
  border-radius: 12px;
  min-width: 100px;
  text-align: center;
}

.score-card .label {
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--text-muted);
}

.score-card .value {
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--primary-color);
}

.canvas-wrapper {
  position: relative;
  width: 400px;
  height: 400px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 0 40px rgba(59, 130, 246, 0.2);
  border: 4px solid rgba(255,255,255,0.05);
}

canvas {
  display: block;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(12px);
  z-index: 10;
  cursor: pointer;
}

.overlay-content {
  text-align: center;
}

.snake-icon {
  font-size: 3rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
  filter: drop-shadow(0 0 10px var(--primary-color));
}

.overlay h2 {
  font-size: 2rem;
  font-weight: 900;
  color: white;
  margin-bottom: 0.5rem;
}

.overlay p {
  font-size: 1rem;
  color: var(--primary-color);
  font-weight: 600;
  letter-spacing: 2px;
}

.final-stats {
  margin: 1.5rem 0;
}

.stat {
  font-size: 1.2rem;
  font-weight: 800;
  color: #fbbf24;
}

.premium-btn {
  margin-top: 1rem;
  padding: 0.8rem 2.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 900;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(0,0,0,0.3);
}

.hints {
  margin-top: 2rem;
  font-size: 0.8rem;
  color: rgba(255,255,255,0.3);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.4s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
