<template>
  <div class="td-game-wrapper glass-panel">
    <div class="td-sidebar glass-panel">
      <div class="user-info">
        <div class="stat gold">
          <i class="fas fa-coins"></i>
          <span>{{ Math.floor(money) }}</span>
        </div>
        <div class="stat health">
          <i class="fas fa-heart"></i>
          <span>{{ lives }}</span>
        </div>
        <div class="stat wave">
          <span class="label">WAVE</span>
          <span>{{ currentWave }}/5</span>
        </div>
      </div>

      <div class="tower-shop">
        <h3>TOWERS</h3>
        <div class="shop-grid">
          <div 
            v-for="type in towerTypes" 
            :key="type.id"
            class="shop-item glass-panel"
            :class="{ 'selected': selectedType === type.id, 'disabled': money < type.cost }"
            @click="selectTowerType(type)"
          >
            <div class="icon-box" :style="{ background: type.color }">
              <i :class="type.icon"></i>
            </div>
            <div class="info">
              <span class="name">{{ type.name }}</span>
              <span class="cost">${{ type.cost }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="global-upgrades">
        <h3>UPGRADES</h3>
        <div class="upgrade-list">
          <div 
            v-for="(val, key) in globalStats" 
            :key="key"
            class="upgrade-item glass-panel"
            @click="upgradeStat(key)"
            :class="{ 'disabled': money < upgradeCosts[key] }"
          >
            <span class="label">{{ upgradeLabels[key] }}</span>
            <span class="cost">{{ upgradeCosts[key] }} KPI</span>
          </div>
        </div>
      </div>
    </div>

    <div class="td-main">
      <div class="canvas-container" @click="handleCanvasClick" @mousemove="handleCanvasMove">
        <canvas ref="bgCanvas" width="800" height="600" class="bg-canvas"></canvas>
        <canvas ref="gameCanvas" width="800" height="600" class="game-canvas"></canvas>
        
        <!-- Selection Ghost -->
        <div 
          v-if="selectedType && ghostPos"
          class="tower-ghost"
          :style="{ left: ghostPos.x + 'px', top: ghostPos.y + 'px', width: gridSize+'px', height: gridSize+'px' }"
        >
           <div class="range-circle" :style="{ width: getSelectedRange()*2+'px', height: getSelectedRange()*2+'px', left: -getSelectedRange()+gridSize/2+'px', top: -getSelectedRange()+gridSize/2+'px' }"></div>
        </div>

        <div v-if="gameState === 'START'" class="td-overlay glass-panel">
           <h2>BATTLE FOR THE ROOT</h2>
           <p>DEPLOY TOWERS TO PROTECT THE SERVER CORE</p>
           <button class="premium-btn" @click="startWaves">INITIALIZE DEFENSE</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { apiPost } from '../../utils/api.js'
import { drawSprite, loadImage } from '../../utils/assets.js'

const gameCanvas = ref(null)
const bgCanvas = ref(null)
const money = ref(500)
const lives = ref(20)
const currentWave = ref(0)
const gameState = ref('START') // START, PLAYING, OVER
const selectedType = ref(null)
const ghostPos = ref(null)
const gridSize = 40

let ctx, bgCtx, animationFrame
let enemies = []
let towers = []
let projectiles = []
let lastFrameTime = 0

// Stats & Upgrades
const globalStats = ref({
  critRate: 0.05,
  critDmg: 1.5,
  recharge: 1.0,
  dmgBonus: 1.0,
  moneyBonus: 1.0,
  discount: 1.0,
  towerHealth: 1.0
})

const upgradeCosts = ref({
  critRate: 100,
  critDmg: 150,
  recharge: 200,
  dmgBonus: 250,
  moneyBonus: 300,
  discount: 100,
  towerHealth: 50
})

const upgradeLabels = {
  critRate: 'CRIT RATE',
  critDmg: 'CRIT DMG',
  recharge: 'COOLDOWN',
  dmgBonus: 'POWER',
  moneyBonus: 'INCOME',
  discount: 'DISCOUNT',
  towerHealth: 'DURABILITY'
}

const towerTypes = [
  { id: 'slasher', name: 'Slasher', cost: 100, range: 80, dmg: 15, rate: 40, icon: 'fas fa-sword', color: '#6366f1', frame: 0 },
  { id: 'archer', name: 'Archer', cost: 180, range: 150, dmg: 30, rate: 30, icon: 'fas fa-bow-arrow', color: '#10b981', frame: 1 },
  { id: 'mage', name: 'Mage', cost: 350, range: 200, dmg: 80, rate: 60, icon: 'fas fa-magic', color: '#8b5cf6', frame: 2 },
  { id: 'cannon', name: 'Cannon', cost: 250, range: 180, dmg: 100, rate: 120, icon: 'fas fa-bomb', color: '#f97316', frame: 3 },
  { id: 'xcannon', name: 'X-Cannon', cost: 800, range: 100, dmg: 200, rate: 15, icon: 'fas fa-crosshairs', color: '#a855f7', frame: 5 }
]

// Assets
const mapImg = new Image(); mapImg.src = '/assets/arcade/td_map_1.png'
const towerImg = new Image(); towerImg.src = '/assets/arcade/td_towers.png'
const enemyImg = new Image(); enemyImg.src = '/assets/arcade/td_enemies.png'

// Map Nodes (Grass Map)
const nodes = [
  { x: 0, y: 50 }, { x: 235, y: 215 }, { x: 500, y: 115 }, { x: 745, y: 255 },
  { x: 135, y: 590 }, { x: 500, y: 500 }, { x: 700, y: 550 }, { x: 800, y: 550 }
]

const selectTowerType = (type) => {
  if (money.value < type.cost) return
  selectedType.value = type.id === selectedType.value ? null : type.id
}

const getSelectedRange = () => {
  const t = towerTypes.find(t => t.id === selectedType.value)
  return t ? t.range : 0
}

const handleCanvasMove = (e) => {
  const rect = gameCanvas.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  ghostPos.value = { 
    x: Math.floor(x / gridSize) * gridSize, 
    y: Math.floor(y / gridSize) * gridSize 
  }
}

const handleCanvasClick = (e) => {
  if (!selectedType.value) return
  const type = towerTypes.find(t => t.id === selectedType.value)
  if (money.value < type.cost) return

  // Check collision with path or other towers
  // Simplified for now: just place
  towers.push({
    x: ghostPos.value.x + gridSize/2,
    y: ghostPos.value.y + gridSize/2,
    type: type,
    cooldown: 0,
    level: 1
  })
  money.value -= type.cost
  selectedType.value = null
}

const upgradeStat = (key) => {
  if (money.value < upgradeCosts.value[key]) return
  money.value -= upgradeCosts.value[key]
  
  if (key === 'critRate') globalStats.value.critRate += 0.02
  if (key === 'critDmg') globalStats.value.critDmg += 0.2
  if (key === 'dmgBonus') globalStats.value.dmgBonus *= 1.1
  if (key === 'recharge') globalStats.value.recharge *= 0.95
  
  upgradeCosts.value[key] = Math.floor(upgradeCosts.value[key] * 1.5)
}

const startWaves = () => {
  gameState.value = 'PLAYING'
  currentWave.value = 1
  spawnWave()
  gameLoop()
}

const spawnWave = () => {
  const count = 5 + currentWave.value * 3
  for (let i = 0; i < count; i++) {
    setTimeout(() => {
      if (gameState.value !== 'PLAYING') return
      enemies.push({
        x: nodes[0].x,
        y: nodes[0].y,
        health: 50 + currentWave.value * 50,
        maxHealth: 50 + currentWave.value * 50,
        speed: 1.5 + Math.random() * 0.5,
        targetNode: 1,
        frame: 0,
        dead: false
      })
    }, i * 800)
  }
}

const update = (dt) => {
  if (gameState.value !== 'PLAYING') return

  // Update Enemies
  enemies.forEach(e => {
    const target = nodes[e.targetNode]
    const dx = target.x - e.x
    const dy = target.y - e.y
    const dist = Math.sqrt(dx*dx + dy*dy)
    
    if (dist < 5) {
      e.targetNode++
      if (e.targetNode >= nodes.length) {
        lives.value--
        e.dead = true
        if (lives.value <= 0) endGame()
      }
    } else {
      e.x += (dx/dist) * e.speed
      e.y += (dy/dist) * e.speed
    }
  })
  enemies = enemies.filter(e => !e.dead && e.health > 0)

  // Update Towers
  towers.forEach(t => {
    if (t.cooldown > 0) t.cooldown--
    else {
      // Find target
      const target = enemies.find(e => {
        const dist = Math.sqrt((t.x - e.x)**2 + (t.y - e.y)**2)
        return dist < t.type.range
      })
      if (target) {
        shoot(t, target)
        t.cooldown = t.type.rate * globalStats.value.recharge
      }
    }
  })

  // Update Projectiles
  projectiles.forEach(p => {
    const dx = p.target.x - p.x
    const dy = p.target.y - p.y
    const dist = Math.sqrt(dx*dx + dy*dy)
    
    if (dist < 10) {
      p.hit = true
      // Damage calculation
      let damage = p.dmg * globalStats.value.dmgBonus
      if (Math.random() < globalStats.value.critRate) damage *= globalStats.value.critDmg
      p.target.health -= damage
      if (p.target.health <= 0 && !p.target.dead) {
        money.value += (10 * globalStats.value.moneyBonus)
      }
    } else {
      p.x += (dx/dist) * 10
      p.y += (dy/dist) * 10
    }
  })
  projectiles = projectiles.filter(p => !p.hit)

  // Check wave end
  if (enemies.length === 0 && currentWave.value < 5) {
     currentWave.value++
     spawnWave()
  } else if (enemies.length === 0 && currentWave.value >= 5) {
     endGame(true)
  }
}

const shoot = (tower, target) => {
  projectiles.push({
    x: tower.x,
    y: tower.y,
    target: target,
    dmg: tower.type.dmg,
    hit: false,
    color: tower.type.color
  })
}

const draw = () => {
  if (!ctx) return
  ctx.clearRect(0,0,800,600)

  // Draw Enemies
  enemies.forEach(e => {
    ctx.fillStyle = '#f00'
    ctx.fillRect(e.x-10, e.y-10, 20, 20)
    // Health bar
    ctx.fillStyle = '#333'; ctx.fillRect(e.x-15, e.y-20, 30, 4)
    ctx.fillStyle = '#0f0'; ctx.fillRect(e.x-15, e.y-20, (e.health/e.maxHealth)*30, 4)
  })

  // Draw Towers
  towers.forEach(t => {
    if (towerImg.complete) {
      // grid 3x2?
      const sw = towerImg.width / 3
      const sh = towerImg.height / 2
      drawSprite(ctx, towerImg, t.x-20, t.y-20, 40, 40, t.type.frame, sw, sh, 3)
    } else {
      ctx.fillStyle = t.type.color
      ctx.fillRect(t.x-15, t.y-15, 30, 30)
    }
  })

  // Draw Projectiles
  projectiles.forEach(p => {
    ctx.fillStyle = p.color
    ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI*2); ctx.fill()
  })
}

const gameLoop = (timestamp) => {
  const dt = timestamp - lastFrameTime
  lastFrameTime = timestamp
  update(dt)
  draw()
  if (gameState.value === 'PLAYING') {
    animationFrame = requestAnimationFrame(gameLoop)
  }
}

const endGame = async (won) => {
  gameState.value = 'OVER'
  const kpiReward = won ? 200 + currentWave.value * 50 : currentWave.value * 20
  
  try {
    await apiPost('/games/scores/submit', {
      game_type: 'towerdefense',
      score: currentWave.value,
      kpi: kpiReward
    })
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  ctx = gameCanvas.value.getContext('2d')
  bgCtx = bgCanvas.value.getContext('2d')
  
  mapImg.onload = () => {
    bgCtx.drawImage(mapImg, 0, 0, 800, 600)
  }
  if (mapImg.complete) bgCtx.drawImage(mapImg, 0, 0, 800, 600)
  
  draw()
})

onUnmounted(() => {
  cancelAnimationFrame(animationFrame)
})
</script>

<style scoped>
.td-game-wrapper {
  display: flex;
  width: 1080px;
  height: 600px;
  overflow: hidden;
  position: relative;
}

.td-sidebar {
  width: 280px;
  height: 100%;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  border-right: 1px solid rgba(255,255,255,0.1);
  background: rgba(0,0,0,0.2);
}

.user-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 8px;
  background: rgba(255,255,255,0.05);
  font-weight: 800;
}

.stat.gold { color: #fbbf24; }
.stat.health { color: #f43f5e; }
.stat.wave { grid-column: span 2; display: flex; justify-content: space-between; }

.tower-shop h3, .global-upgrades h3 {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  letter-spacing: 1px;
}

.shop-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
}

.shop-item {
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 12px;
}

.shop-item.selected {
  border-color: var(--primary-color);
  background: rgba(59, 130, 246, 0.1);
}

.shop-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.shop-item .icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.info {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 0.7rem;
}

.info .name { font-weight: 700; }
.info .cost { color: #fbbf24; font-weight: 800; }

.upgrade-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.upgrade-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0.8rem;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
}

.upgrade-item.disabled { opacity: 0.4; pointer-events: none; }
.upgrade-item .cost { color: #10b981; }

.td-main {
  flex: 1;
  position: relative;
  background: #111;
}

.canvas-container {
  position: relative;
  width: 800px;
  height: 600px;
}

canvas {
  position: absolute;
  top: 0;
  left: 0;
}

.game-canvas { z-index: 2; }
.bg-canvas { z-index: 1; }

.tower-ghost {
  position: absolute;
  pointer-events: none;
  background: rgba(59, 130, 246, 0.3);
  border: 1px dashed #3b82f6;
  z-index: 5;
}

.range-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.td-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 3rem;
  text-align: center;
  z-index: 100;
  border-radius: 20px;
}

.td-overlay h2 { font-size: 2.2rem; margin-bottom: 1rem; }

.premium-btn {
  padding: 0.8rem 2rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50px;
  font-weight: 800;
  cursor: pointer;
  margin-top: 1.5rem;
}
</style>
