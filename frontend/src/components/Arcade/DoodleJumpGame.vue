<template>
  <div class="doodle-jump-container glass-panel" :class="{ 'game-over': gameOver }">
    <div class="game-header">
      <div class="score-card glass-panel">
        <span class="label">ALTITUDE</span>
        <span class="value">{{ Math.floor(currentScore) }}m</span>
      </div>
      <div class="score-card glass-panel best">
        <span class="label">RECORD</span>
        <span class="value">{{ bestScore }}m</span>
      </div>
    </div>
    
    <div class="canvas-wrapper">
      <canvas ref="gameCanvas" width="400" height="600"></canvas>
      
      <transition name="fade">
        <div v-if="!gameRunning" class="game-overlay glass-panel" @click="startGame">
          <div class="start-msg">
            <div class="character-preview" :style="previewStyle"></div>
            <h2>{{ gameOver ? 'MISSION FAILED' : 'DOODLE JUMP' }}</h2>
            <p>{{ gameOver ? 'RETRY MISSION' : 'START ASCENT' }}</p>
            <span v-if="gameOver" class="final-score">SCORE: {{ Math.floor(currentScore) }}</span>
            <div class="hints">
              <i class="fas fa-arrows-alt-h"></i> A / D or ARROWS
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { apiPost } from '../../utils/api.js'
import { drawSprite, loadImage } from '../../utils/assets.js'

const gameCanvas = ref(null)
const gameRunning = ref(false)
const gameOver = ref(false)
const currentScore = ref(0)
const bestScore = ref(parseInt(localStorage.getItem('doodle_high_score') || 0))

let ctx, animationFrame
let player = {
  x: 200,
  y: 400,
  width: 45,
  height: 45,
  vx: 0,
  vy: 0,
  jumpForce: -13.5,
  gravity: 0.42,
  frame: 0,
  rotation: 0
}

let platforms = []
const platformWidth = 70
const platformHeight = 16
const keys = {}

// Assets
const playerImg = new Image(); playerImg.src = '/assets/arcade/doodle_guy.png'

const previewStyle = computed(() => {
  return {
    backgroundImage: `url('/assets/arcade/doodle_guy.png')`,
    backgroundSize: '200% 200%', // 4 frames total probably
    backgroundPosition: '0 0'
  }
})

const initPlatforms = () => {
  platforms = []
  // Initial platform
  platforms.push({ x: 165, y: 550, type: 'normal' })
  
  for (let i = 1; i < 8; i++) {
    platforms.push({
      x: Math.random() * (400 - platformWidth),
      y: 600 - i * 85,
      type: Math.random() > 0.9 ? 'bonus' : 'normal'
    })
  }
}

const startGame = () => {
  gameRunning.value = true
  gameOver.value = false
  currentScore.value = 0
  player.x = 200
  player.y = 400
  player.vy = 0
  player.vx = 0
  initPlatforms()
  gameLoop()
}

const gameLoop = () => {
  if (!gameRunning.value) return
  update()
  draw()
  animationFrame = requestAnimationFrame(gameLoop)
}

const update = () => {
  if (keys['ArrowLeft'] || keys['a']) player.vx = -7
  else if (keys['ArrowRight'] || keys['d']) player.vx = 7
  else player.vx *= 0.85
  
  player.x += player.vx
  player.vy += player.gravity
  player.y += player.vy
  
  // Wrap screen
  if (player.x + player.width < 0) player.x = 400
  if (player.x > 400) player.x = -player.width
  
  // Animation/Frame determination
  if (player.vy < 0) player.frame = 1 // Jumping UP
  else player.frame = 2 // Falling DOWN

  // Rotation based on movement
  player.rotation = player.vx * 0.05

  // Platform collision
  if (player.vy > 0) {
    platforms.forEach(p => {
      if (
        player.x + player.width - 10 > p.x &&
        player.x + 10 < p.x + platformWidth &&
        player.y + player.height > p.y &&
        player.y + player.height < p.y + platformHeight + player.vy
      ) {
        player.vy = p.type === 'bonus' ? player.jumpForce * 1.5 : player.jumpForce
        player.y = p.y - player.height
      }
    })
  }
  
  // Camera scroll
  if (player.y < 280) {
    const diff = 280 - player.y
    player.y = 280
    platforms.forEach(p => {
      p.y += diff
      if (p.y > 600) {
        p.y = 0
        p.x = Math.random() * (400 - platformWidth)
        p.type = Math.random() > 0.92 ? 'bonus' : 'normal'
        currentScore.value += 10
      }
    })
  }
  
  if (player.y > 600) endGame()
}

const draw = () => {
  if (!ctx) return
  ctx.clearRect(0, 0, 400, 600)
  
  // Spacey/Gradient BG
  const bgGrad = ctx.createLinearGradient(0, 0, 0, 600)
  bgGrad.addColorStop(0, '#000428')
  bgGrad.addColorStop(1, '#004e92')
  ctx.fillStyle = bgGrad
  ctx.fillRect(0, 0, 400, 600)
  
  // Subtle stars
  ctx.fillStyle = '#fff'
  for(let i=0; i<30; i++) {
    const sx = Math.sin(i*123.4) * 200 + 200
    const sy = (Math.cos(i*567.8) * 300 + 300 + (currentScore.value * 0.5)) % 600
    ctx.globalAlpha = 0.3
    ctx.beginPath(); ctx.arc(sx, sy, 1, 0, Math.PI*2); ctx.fill()
  }
  ctx.globalAlpha = 1.0

  // Draw platforms
  platforms.forEach(p => {
    const isBonus = p.type === 'bonus'
    const color = isBonus ? '#fbbf24' : '#10b981'
    const shadowColor = isBonus ? 'rgba(251, 191, 36, 0.5)' : 'rgba(16, 185, 129, 0.4)'
    
    ctx.shadowBlur = 10
    ctx.shadowColor = shadowColor
    
    // Glassy platform
    const pGrad = ctx.createLinearGradient(p.x, p.y, p.x, p.y + platformHeight)
    pGrad.addColorStop(0, color)
    pGrad.addColorStop(1, '#064e3b')
    
    ctx.fillStyle = pGrad
    roundRect(ctx, p.x, p.y, platformWidth, platformHeight, 8)
    ctx.fill()
    ctx.strokeStyle = 'rgba(255,255,255,0.3)'
    ctx.lineWidth = 1
    ctx.stroke()
  })
  ctx.shadowBlur = 0
  
  // Draw player
  ctx.save()
  ctx.translate(player.x + player.width/2, player.y + player.height/2)
  ctx.rotate(player.rotation)
  
  if (playerImg.complete && playerImg.naturalWidth !== 0) {
    const sw = playerImg.width / 2
    const sh = playerImg.height / 2
    drawSprite(ctx, playerImg, -player.width/2, -player.height/2, player.width, player.height, player.frame, sw, sh, 2)
  } else {
    // Fallback
    ctx.fillStyle = '#3b82f6'; ctx.beginPath()
    ctx.arc(0, 0, player.width/2, 0, Math.PI*2); ctx.fill()
  }
  ctx.restore()
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

const endGame = async () => {
  gameRunning.value = false
  gameOver.value = true
  if (animationFrame) cancelAnimationFrame(animationFrame)
  
  const score = Math.floor(currentScore.value)
  if (score > bestScore.value) {
    bestScore.value = score
    localStorage.setItem('doodle_high_score', score.toString())
  }
  
  try {
    const kpi = Math.floor(score * 0.1)
    await apiPost('/games/scores/submit', {
      game_type: 'doodlejump',
      score: score,
      kpi: kpi
    })
  } catch (err) {
    console.error('Score submission error:', err)
  }
}

const handleKeyDown = (e) => { 
  keys[e.key] = true 
  if (e.key === ' ' && !gameRunning.value) startGame()
}
const handleKeyUp = (e) => { keys[e.key] = false }

onMounted(() => {
  ctx = gameCanvas.value.getContext('2d')
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
  draw()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)
  if (animationFrame) cancelAnimationFrame(animationFrame)
})
</script>

<style scoped>
.doodle-jump-container {
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
  min-width: 120px;
  text-align: center;
}

.score-card .label {
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--text-muted);
}

.score-card .value {
  font-size: 1.4rem;
  font-weight: 900;
  color: var(--primary-color);
}

.canvas-wrapper {
  position: relative;
  width: 400px;
  height: 600px;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 25px 70px rgba(0,0,0,0.6);
  border: 4px solid rgba(255,255,255,0.1);
  background: #000;
}

canvas {
  display: block;
}

.game-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(10px);
  z-index: 30;
  border: none;
}

.start-msg {
  text-align: center;
}

.character-preview {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  filter: drop-shadow(0 0 15px var(--primary-color));
  animation: float 2s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.start-msg h2 {
  font-size: 2.2rem;
  font-weight: 950;
  letter-spacing: 1px;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 0 20px rgba(0,0,0,0.5);
}

.start-msg p {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--primary-color);
}

.final-score {
  display: block;
  font-size: 2.5rem;
  color: #fbbf24;
  margin-top: 1rem;
  font-weight: 900;
}

.hints {
  margin-top: 3rem;
  font-size: 0.9rem;
  color: rgba(255,255,255,0.5);
  font-weight: 400;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.4s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.game-over canvas {
  filter: blur(4px) grayscale(0.5);
}
</style>
