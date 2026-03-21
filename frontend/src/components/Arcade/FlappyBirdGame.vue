<template>
  <div class="flappy-bird-container glass-panel" :class="{ 'game-over': gameState === 'OVER' }">
    <div class="game-header">
      <div class="score-card glass-panel">
        <span class="label">SCORE</span>
        <span class="value">{{ score }}</span>
      </div>
      <div class="score-card glass-panel high-score">
        <span class="label">BEST</span>
        <span class="value">{{ highScore }}</span>
      </div>
    </div>
    
    <div class="canvas-wrapper">
      <canvas 
        ref="canvasRef" 
        width="400" 
        height="600" 
        @mousedown="jump" 
        @touchstart.prevent="jump"
        :class="{ 'shake': screenShake > 0 }"
      ></canvas>
      
      <div v-if="gameState === 'START'" class="overlay glass-panel">
        <div class="bird-preview"></div>
        <h2>FLAPPY BIRD</h2>
        <p>TAP TO FLAP</p>
        <button @click="startGame" class="start-btn premium-btn">START MISSION</button>
      </div>
      
      <div v-if="gameState === 'OVER'" class="overlay glass-panel">
        <h2>MISSION FAILED</h2>
        <div class="final-score">{{ score }}</div>
        <p>REWARD: {{ Math.floor(score * 1.5) }} KPI</p>
        <button @click="startGame" class="start-btn premium-btn">REDEPLOY</button>
      </div>
    </div>

    <!-- Instructions -->
    <div class="controls-hint">
       <span><i class="fas fa-mouse"></i> CLICK</span>
       <span class="divider">|</span>
       <span><i class="fas fa-keyboard"></i> SPACE</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiPost } from '../../utils/api.js'
import { drawSprite } from '../../utils/assets.js'

const canvasRef = ref(null)
const score = ref(0)
const highScore = ref(localStorage.getItem('flappy_high_score') || 0)
const gameState = ref('START') // START, PLAYING, OVER
const screenShake = ref(0)

let ctx, animationFrame
let bird = { 
  x: 50, 
  y: 300, 
  velocity: 0, 
  radius: 18, 
  rotation: 0,
  frame: 0,
  frameCounter: 0
}

let pipes = []
const gravity = 0.25
const jumpStrength = -4.8
const pipeWidth = 65
const pipeGap = 160
const pipeSpeed = 2.5

// Assets
const birdImg = new Image(); birdImg.src = '/assets/arcade/bird.png'
const bgImg = new Image(); bgImg.src = '/assets/arcade/flappy_bg.png'

// Parallax offsets
let bgOffset1 = 0 // Distant
let bgOffset2 = 0 // Mid
let bgOffset3 = 0 // Ground

const startGame = () => {
  score.value = 0
  gameState.value = 'PLAYING'
  bird = { 
    x: 50, 
    y: 300, 
    velocity: 0, 
    radius: 18, 
    rotation: 0,
    frame: 0,
    frameCounter: 0
  }
  pipes = []
  generatePipe(450)
  generatePipe(700)
  gameLoop()
}

const generatePipe = (x) => {
  const minHeight = 80
  const maxHeight = 350
  const height = Math.floor(Math.random() * (maxHeight - minHeight + 1)) + minHeight
  pipes.push({ x, top: height, passed: false })
}

const jump = () => {
  if (gameState.value === 'PLAYING') {
    bird.velocity = jumpStrength
    // Pulse effect
  } else if (gameState.value === 'START' || gameState.value === 'OVER') {
    // Prevent accidental double start
  }
}

const handleKey = (e) => {
  if (e.code === 'Space') {
    e.preventDefault()
    if (gameState.value === 'PLAYING') jump()
    else if (gameState.value === 'START' || gameState.value === 'OVER') startGame()
  }
}

const update = () => {
  if (gameState.value !== 'PLAYING') return

  bird.velocity += gravity
  bird.y += bird.velocity
  
  // Rotation logic
  if (bird.velocity < 0) {
    bird.rotation = Math.max(-0.5, bird.rotation - 0.1)
  } else {
    bird.rotation = Math.min(Math.PI / 2.5, bird.rotation + 0.05)
  }

  // Animation logic
  bird.frameCounter++
  if (bird.frameCounter % 5 === 0) {
    bird.frame = (bird.frame + 1) % 4 // Use top 4 frames
  }

  // Parallax update
  bgOffset1 -= 0.5
  bgOffset2 -= 1.2
  bgOffset3 -= 2.5
  if (bgOffset1 <= -400) bgOffset1 = 0
  if (bgOffset2 <= -400) bgOffset2 = 0
  if (bgOffset3 <= -400) bgOffset3 = 0

  // Floor/Ceiling collision
  if (bird.y + bird.radius > 560 || bird.y - bird.radius < 0) {
    triggerCollision()
  }

  // Pipe update
  if (pipes.length > 0 && pipes[0].x < -pipeWidth) {
    pipes.shift()
  }
  
  if (pipes.length > 0 && pipes[pipes.length - 1].x < 250) {
    generatePipe(450)
  }

  pipes.forEach(pipe => {
    pipe.x -= pipeSpeed
    
    // Score
    if (!pipe.passed && pipe.x + pipeWidth < bird.x) {
      pipe.passed = true
      score.value++
    }

    // Collision Detection
    const bottomY = pipe.top + pipeGap
    if (
      bird.x + bird.radius - 5 > pipe.x && 
      bird.x - bird.radius + 5 < pipe.x + pipeWidth &&
      (bird.y - bird.radius + 5 < pipe.top || bird.y + bird.radius - 5 > bottomY)
    ) {
      triggerCollision()
    }
  })

  if (screenShake > 0) screenShake.value--
}

const triggerCollision = () => {
  screenShake.value = 15
  endGame()
}

const draw = () => {
  if (!ctx) return
  const w = 400
  const h = 600
  ctx.clearRect(0,0,w,h)

  // Draw Parallax BG
  // Background layer (Mountains)
  if (bgImg.complete) {
    // We assume the generated image has layers vertically? Or we just draw it 3 times with different speeds
    // Actually our prompt asked for layers in one. Let's assume it's one big beautiful scene for now
    // and we just scroll it.
    ctx.drawImage(bgImg, bgOffset1, 0, 1024, 600)
    ctx.drawImage(bgImg, bgOffset1 + 1024, 0, 1024, 600)
    
    // Midground (City) - slightly darker overlay or scroll again
    ctx.globalAlpha = 0.5
    ctx.drawImage(bgImg, bgOffset2, 50, 1024, 600)
    ctx.globalAlpha = 1.0
  } else {
    // Fallback gradient
    const grad = ctx.createLinearGradient(0,0,0,h)
    grad.addColorStop(0, '#4facfe')
    grad.addColorStop(1, '#00f2fe')
    ctx.fillStyle = grad
    ctx.fillRect(0,0,w,h)
  }

  // Draw Pipes
  pipes.forEach(pipe => {
    const grad = ctx.createLinearGradient(pipe.x, 0, pipe.x + pipeWidth, 0)
    grad.addColorStop(0, '#2ecc71')
    grad.addColorStop(0.5, '#27ae60')
    grad.addColorStop(1, '#2ecc71')
    
    ctx.fillStyle = grad
    ctx.strokeStyle = '#1b5e20'
    ctx.lineWidth = 3
    
    // Top Pipe
    roundRect(ctx, pipe.x, 0, pipeWidth, pipe.top, 8)
    ctx.fill()
    ctx.stroke()
    
    // Top Lip
    ctx.fillRect(pipe.x - 5, pipe.top - 20, pipeWidth + 10, 20)
    ctx.strokeRect(pipe.x - 5, pipe.top - 20, pipeWidth + 10, 20)

    // Bottom Pipe
    const bottomY = pipe.top + pipeGap
    const bottomHeight = h - bottomY - 40 // Ground offset
    roundRect(ctx, pipe.x, bottomY, pipeWidth, bottomHeight, 8)
    ctx.fill()
    ctx.stroke()
    
    // Bottom Lip
    ctx.fillRect(pipe.x - 5, bottomY, pipeWidth + 10, 20)
    ctx.strokeRect(pipe.x - 5, bottomY, pipeWidth + 10, 20)
  })

  // Draw Ground
  const groundGrad = ctx.createLinearGradient(0, 560, 0, 600)
  groundGrad.addColorStop(0, '#8d6e63')
  groundGrad.addColorStop(1, '#4e342e')
  ctx.fillStyle = groundGrad
  ctx.fillRect(0, 560, w, 40)
  ctx.fillStyle = '#43a047'
  ctx.fillRect(0, 560, w, 5)

  // Draw Bird
  ctx.save()
  ctx.translate(bird.x, bird.y)
  ctx.rotate(bird.rotation)
  
  if (birdImg.complete) {
    // spritesheet has 4x4 grid probably, let's assume 4 cols
    const sw = birdImg.width / 4
    const sh = birdImg.height / 4
    drawSprite(ctx, birdImg, -bird.radius * 1.5, -bird.radius * 1.5, bird.radius * 3, bird.radius * 3, bird.frame, sw, sh, 4)
  } else {
    // Stylized Fallback
    ctx.fillStyle = '#f1c40f'
    ctx.beginPath(); ctx.arc(0,0,bird.radius,0,Math.PI*2); ctx.fill()
    ctx.strokeStyle = '#000'; ctx.lineWidth = 2; ctx.stroke()
  }
  ctx.restore()
}

// Helper for rounded rectangles (Canvas 2D)
function roundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height)
  ctx.lineTo(x, y + height)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
}

const gameLoop = () => {
  update()
  draw()
  if (gameState.value === 'PLAYING') {
    animationFrame = requestAnimationFrame(gameLoop)
  }
}

const endGame = async () => {
  gameState.value = 'OVER'
  if (score.value > highScore.value) {
    highScore.value = score.value
    localStorage.setItem('flappy_high_score', score.value.toString())
  }
  
  try {
    const kpi = Math.floor(score.value * 1.5)
    await apiPost('/games/scores/submit', {
      game_type: 'flappybird',
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
  cancelAnimationFrame(animationFrame)
})
</script>

<style scoped>
.flappy-bird-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  position: relative;
  min-width: 450px;
}

.canvas-wrapper {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  border: 4px solid rgba(255,255,255,0.1);
  background: #000;
}

canvas {
  display: block;
  cursor: pointer;
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

.overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  padding: 2.5rem;
  border-radius: 20px;
  text-align: center;
  color: white;
  z-index: 20;
  border: 1px solid rgba(255,255,255,0.2);
}

.overlay h2 {
  font-size: 2rem;
  font-weight: 900;
  letter-spacing: 2px;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #fff, #aaa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.final-score {
  font-size: 4rem;
  font-weight: 950;
  color: #fbbf24;
  text-shadow: 0 0 20px rgba(251, 191, 36, 0.4);
  margin: 1rem 0;
}

.premium-btn {
  margin-top: 1.5rem;
  padding: 1rem 2.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 800;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.premium-btn:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 15px 30px rgba(0,0,0,0.3);
  filter: brightness(1.1);
}

.controls-hint {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.divider { opacity: 0.3; }

/* Shake Animation */
.shake {
  animation: shake 0.1s infinite;
}

@keyframes shake {
  0% { transform: translate(1px, 1px) rotate(0deg); }
  20% { transform: translate(-1px, -2px) rotate(-1deg); }
  40% { transform: translate(-3px, 0px) rotate(1deg); }
  60% { transform: translate(3px, 2px) rotate(0deg); }
  80% { transform: translate(1px, -1px) rotate(1deg); }
  100% { transform: translate(-1px, 2px) rotate(-1deg); }
}

.game-over canvas {
  filter: grayscale(0.5) contrast(1.2);
}
</style>
