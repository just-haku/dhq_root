<template>
  <div class="plat-game-wrapper glass-panel" :class="{ 'game-over': state === 'OVER' }">
    <div class="game-ui">
      <div class="stat-bar health-bar glass-panel">
        <div class="fill" :style="{ width: (player.hp/player.maxHp)*100 + '%' }"></div>
        <span class="label">INTEGRITY</span>
      </div>
      <div class="game-meta">
        <div class="score-card glass-panel">
          <span class="label">KILLS</span>
          <span class="value">{{ kills }}</span>
        </div>
        <div class="score-card glass-panel">
          <span class="label">WAVE</span>
          <span class="value">{{ wave }}</span>
        </div>
      </div>
    </div>

    <div class="canvas-container">
      <canvas ref="canvasRef" width="800" height="500"></canvas>
      
      <transition name="fade">
        <div v-if="state !== 'PLAYING'" class="overlay glass-panel" @click="startGame">
          <div class="content">
            <h2>{{ state === 'START' ? 'PLATFORMER ARENA' : 'CORE BREACHED' }}</h2>
            <p>{{ state === 'START' ? 'INITIALIZE DEFENDER' : 'REBOOT SYSTEM' }}</p>
            <div v-if="state === 'OVER'" class="stats">
              <span>ELIMINATIONS: {{ kills }}</span>
              <span>REWARD: {{ Math.floor(kills * 10) }} KPI</span>
            </div>
            <button class="premium-btn">DE-RE-PLOY</button>
            <div class="hint">WASD to Move | J to Attack | K to Jump</div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiPost } from '../../utils/api.js'
import { drawSprite } from '../../utils/assets.js'

const canvasRef = ref(null)
const state = ref('START')
const kills = ref(0)
const wave = ref(0)

let ctx, animationFrame
const keys = {}

const player = {
  x: 400,
  y: 300,
  w: 48,
  h: 48,
  vx: 0,
  vy: 0,
  speed: 5,
  jump: -12,
  gravity: 0.6,
  onGround: false,
  dir: 1, // 1 for right, -1 for left
  hp: 100,
  maxHp: 100,
  attacking: 0,
  frame: 0
}

let enemies = []
let particles = []
const platforms = [
  { x: 0, y: 450, w: 800, h: 50 }, // Ground
  { x: 100, y: 320, w: 150, h: 20 },
  { x: 550, y: 320, w: 150, h: 20 },
  { x: 300, y: 200, w: 200, h: 20 }
]

// Assets
const playerImg = new Image(); playerImg.src = '/assets/arcade/plat_player.png'
const enemyImg = new Image(); enemyImg.src = '/assets/arcade/plat_enemy.png'
const tilesetImg = new Image(); tilesetImg.src = '/assets/arcade/tileset.png'

const startGame = () => {
  state.value = 'PLAYING'
  kills.value = 0
  wave.value = 1
  player.hp = 100
  player.x = 400
  player.y = 300
  enemies = []
  spawnWave()
  gameLoop()
}

const spawnWave = () => {
  const count = 3 + wave.value * 2
  for(let i=0; i<count; i++) {
    setTimeout(() => {
      if (state.value !== 'PLAYING') return
      const side = Math.random() > 0.5 ? 0 : 750
      enemies.push({
        x: side,
        y: 300,
        w: 32,
        h: 32,
        vx: 0,
        hp: 30 + wave.value * 10,
        speed: 1.5 + Math.random(),
        dead: false,
        frame: 0,
        frameTimer: 0
      })
    }, i * 1500)
  }
}

const update = () => {
  if (state.value !== 'PLAYING') return

  // Player input
  if (keys['a'] || keys['ArrowLeft']) { player.vx = -player.speed; player.dir = -1; }
  else if (keys['d'] || keys['ArrowRight']) { player.vx = player.speed; player.dir = 1; }
  else player.vx = 0

  if ((keys['w'] || keys['k'] || keys[' ']) && player.onGround) {
    player.vy = player.jump
    player.onGround = false
  }

  if (keys['j'] && player.attacking <= 0) {
    player.attacking = 20
    checkAttack()
  }

  // Physics
  player.vy += player.gravity
  player.x += player.vx
  player.y += player.vy

  // Platform collision
  player.onGround = false
  platforms.forEach(p => {
    if (
      player.x + player.w > p.x &&
      player.x < p.x + p.w &&
      player.y + player.h > p.y &&
      player.y + player.h < p.y + p.h + player.vy
    ) {
       player.y = p.y - player.h
       player.vy = 0
       player.onGround = true
    }
  })

  // Boundaries
  if (player.x < 0) player.x = 0
  if (player.x > 800 - player.w) player.x = 800 - player.w

  // Enemies update
  enemies.forEach(e => {
    // Basic AI
    const dx = player.x - e.x
    e.vx = dx > 0 ? e.speed : -e.speed
    e.x += e.vx
    
    // Enemy gravity
    e.y += 5 // simplified
    platforms.forEach(p => {
       if (e.x + e.w > p.x && e.x < p.x + p.w && e.y + e.h > p.y && e.y + e.h < p.y + 10) {
          e.y = p.y - e.h
       }
    })

    // Player collision
    if (Math.abs(e.x - player.x) < 30 && Math.abs(e.y - player.y) < 30) {
       // Player is invincible during active attack frames
       if (player.attacking <= 0) {
         player.hp -= 0.5
         if (player.hp <= 0) endGame()
       }
    }
  })
  enemies = enemies.filter(e => !e.dead)

  if (enemies.length === 0 && state.value === 'PLAYING') {
    wave.value++
    spawnWave()
  }

  if (player.attacking > 0) player.attacking--
}

const checkAttack = () => {
  enemies.forEach(e => {
    // Extended slash hitbox
    const attackX = player.dir === 1 ? player.x + (player.w * 0.8) : player.x - 80
    if (Math.abs(e.x - attackX) < 100 && Math.abs(e.y - player.y) < 80) {
       e.hp -= 50
       if (e.hp <= 0) {
         e.dead = true
         kills.value++
         createExplosion(e.x, e.y)
       }
    }
  })
}

const createExplosion = (x, y) => {
  for(let i=0; i<8; i++) {
    particles.push({
      x, y,
      vx: (Math.random()-0.5)*10,
      vy: (Math.random()-0.5)*10,
      life: 20
    })
  }
}

const draw = () => {
  if (!ctx) return
  ctx.clearRect(0, 0, 800, 500)

  // Draw BG/Gradient
  const grad = ctx.createLinearGradient(0,0,0,500)
  grad.addColorStop(0, '#1e1b4b')
  grad.addColorStop(1, '#0f172a')
  ctx.fillStyle = grad
  ctx.fillRect(0,0,800,500)

  // Draw Platforms
  ctx.fillStyle = '#334155'
  platforms.forEach(p => {
    roundRect(ctx, p.x, p.y, p.w, p.h, 4)
    ctx.fill()
    // Tileset texture if loaded
    if (tilesetImg.complete) {
       // Draw grass top
       ctx.drawImage(tilesetImg, 0, 0, 64, 32, p.x, p.y, p.w, 10)
    }
  })

  // Draw Player
  ctx.save()
  if (player.dir === -1) {
    ctx.translate(player.x + player.w, player.y); ctx.scale(-1, 1)
  } else {
    ctx.translate(player.x, player.y)
  }
  
  if (playerImg.complete) {
    // 4x3 grid? 
    const sw = playerImg.width / 4; const sh = playerImg.height / 3;
    let frame = 0 // idle
    if (Math.abs(player.vx) > 0) frame = Math.floor(Date.now()/100 % 4) + 4 // run
    if (player.attacking > 0) frame = Math.floor(Date.now()/50 % 2) + 8 // attack
    drawSprite(ctx, playerImg, 0, 0, player.w, player.h, frame, sw, sh, 4)
  } else {
    ctx.fillStyle = '#3b82f6'; ctx.fillRect(0,0,player.w,player.h)
  }
  ctx.restore()

  // Draw Enemies
  enemies.forEach(e => {
    if (enemyImg.complete) {
       const sw = enemyImg.width / 4; const sh = enemyImg.height / 2;
       const frame = Math.floor(Date.now()/150 % 4)
       drawSprite(ctx, enemyImg, e.x, e.y, e.w, e.h, frame, sw, sh, 4)
    } else {
       ctx.fillStyle = '#f43f5e'; ctx.fillRect(e.x, e.y, e.w, e.h)
    }
  })

  // Draw Particles
  particles.forEach(p => {
    ctx.fillStyle = '#fbbf24'
    ctx.globalAlpha = p.life / 20
    ctx.fillRect(p.x, p.y, 4, 4)
    p.x += p.vx; p.y += p.vy; p.life--
  })
  particles = particles.filter(p => p.life > 0)
}

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
  if (state.value === 'PLAYING') {
    animationFrame = requestAnimationFrame(gameLoop)
  }
}

const endGame = async () => {
  state.value = 'OVER'
  try {
    const kpi = Math.floor(kills.value * 10)
    await apiPost('/games/scores/submit', {
      game_type: 'platformer',
      score: kills.value,
      kpi: kpi
    })
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  ctx = canvasRef.value.getContext('2d')
  window.addEventListener('keydown', (e) => keys[e.key.toLowerCase()] = true)
  window.addEventListener('keyup', (e) => keys[e.key.toLowerCase()] = false)
})

onUnmounted(() => {
  cancelAnimationFrame(animationFrame)
})
</script>

<style scoped>
.plat-game-wrapper {
  width: 800px;
  height: 500px;
  position: relative;
  overflow: hidden;
}

.game-ui {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  z-index: 10;
  pointer-events: none;
}

.health-bar {
  width: 200px;
  height: 24px;
  position: relative;
  overflow: hidden;
  background: rgba(0,0,0,0.4);
}

.health-bar .fill {
  height: 100%;
  background: linear-gradient(90deg, #f43f5e, #fb7185);
  transition: width 0.3s;
}

.health-bar .label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.6rem;
  font-weight: 900;
  color: white;
}

.game-meta {
  display: flex;
  gap: 1rem;
}

.score-card {
  padding: 0.4rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-card .label { font-size: 0.65rem; color: var(--text-muted); }
.score-card .value { font-size: 1.2rem; font-weight: 800; color: var(--primary-color); }

.canvas-container {
  position: relative;
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
  backdrop-filter: blur(10px);
  z-index: 20;
  cursor: pointer;
}

.content { text-align: center; }
.content h2 { font-size: 2.5rem; letter-spacing: 2px; }
.stats { margin: 1rem 0; display: flex; flex-direction: column; gap: 0.5rem; font-weight: 700; color: #fbbf24; }

.premium-btn {
  padding: 1rem 2.5rem;
  background: var(--primary-color);
  color: white;
  border-radius: 50px;
  border: none;
  font-weight: 800;
  margin-top: 2rem;
}

.hint { margin-top: 2rem; opacity: 0.5; font-size: 0.8rem; }
</style>
