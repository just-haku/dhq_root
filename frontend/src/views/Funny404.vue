<template>
  <div class="not-found-page overflow-hidden">
    <!-- Starfield (CSS Stars) -->
    <div class="bg-stars">
      <div 
        v-for="(star, index) in cssStars" 
        :key="'css-star-' + index" 
        class="css-star" 
        :style="{
          width: star.size + 'px', 
          height: star.size + 'px', 
          transform: `translate3d(${star.x}px, ${star.y}px, 0)`,
          animationDelay: star.delay + 's',
          animationDuration: star.dur + 's'
        }"
      ></div>
    </div>

    <div class="scene">
      <!-- PNG Stars (Interactive) -->
      <div
        v-for="star in imgStars" 
        :key="'img-star-' + star.id"
        class="floating-asset absolute"
        :style="{
          width: star.size + 'px',
          height: star.size + 'px',
          transform: `translate3d(${star.x}px, ${star.y}px, 0)`
        }"
      >
        <img 
          src="@/assets/images/404/star_isolated.png" 
          alt="Star" 
          style="width: 100%; height: 100%;"
          :class="{ 'shake-animation': star.isShaking }"
        />
      </div>

      <!-- Astronaut Image -->
      <div
        class="floating-asset absolute"
        :style="{
          width: astronaut.width + 'px',
          transform: `translate3d(${astronaut.x}px, ${astronaut.y}px, 0)`
        }"
      >
        <img 
          src="@/assets/images/404/astronaut_isolated.png" 
          alt="Lost Astronaut" 
          class="astronaut-hover"
          style="width: 100%;"
          :style="{
            transform: `scaleX(${astronaut.facingRight ? -1 : 1}) rotate(${astronaut.rotation}deg)`
          }"
        />
      </div>
      
      <!-- Moon -->
      <div
        class="floating-asset absolute"
        :style="{
          width: moon.width + 'px',
          transform: `translate3d(${moon.x}px, ${moon.y}px, 0)`
        }"
      >
        <img 
          src="@/assets/images/404/moon_isolated.png" 
          alt="Moon" 
          style="width: 100%;"
        />
      </div>

      <!-- UFO -->
      <div
        class="floating-asset absolute"
        :style="{
          width: ufo.width + 'px',
          transform: `translate3d(${ufo.x}px, ${ufo.y}px, 0)`
        }"
      >
        <img 
          src="@/assets/images/404/ufo_isolated.png" 
          alt="UFO" 
          class="ufo-hover"
          style="width: 100%;"
        />
      </div>

      <!-- Rocket -->
      <div
        class="floating-asset absolute"
        :style="{
          width: rocket.width + 'px',
          transform: `translate3d(${rocket.x}px, ${rocket.y}px, 0)`,
          zIndex: rocket.z
        }"
      >
        <img 
          src="@/assets/images/404/rocket_isolated.png" 
          alt="Rocket" 
          style="width: 100%;"
          :style="{
            transform: `rotate(${rocket.angle}deg)`
          }"
        />
      </div>

      <!-- Main content -->
      <div class="content-card relative z-50">
        <div class="glitch-text" data-text="404">404</div>
        <transition name="fade" mode="out-in">
          <div :key="currentQuoteIndex">
            <h2 class="subtitle">{{ currentQuote.title }}</h2>
            <p class="description">{{ currentQuote.desc }}</p>
          </div>
        </transition>
        <button class="return-btn" @click="goHome">
          <i class="fas fa-rocket"></i>
          <span>Return to Base</span>
          <div class="btn-trail"></div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const quotes = [
  { title: "Houston, we have a problem.", desc: "This page has drifted beyond the known universe. There's nothing here but cosmic dust." },
  { title: "Error 404: Page abducted by aliens.", desc: "We negotiated for its return, but they demanded too many space credits." },
  { title: "You've ventured too far.", desc: "The signal is lost in the dark matter nebula. Turn back before your sensors fail." },
  { title: "Wormhole collapse detected.", desc: "The destination coordinates no longer exist in this timeline." },
  { title: "Astrophysical anomaly.", desc: "This page was swallowed by a supermassive black hole." },
  { title: "Oxygen levels critical.", desc: "Return to base immediately, there's nothing out here for you." },
  { title: "UFO snatched this page.", desc: "The truth is out there, but this page isn't." },
  { title: "Hyperdrive malfunction.", desc: "We dropped out of warp space right in the middle of nowhere." },
  { title: "This sector is uncharted.", desc: "Even our most advanced probes haven't found a page here." },
  { title: "Spacetime continuum error.", desc: "You exist, but this page does not. Schrodinger would be proud." },
  { title: "Meteor strike.", desc: "The data center for this page was obliterated by a rogue asteroid." },
  { title: "Cosmic rays interference.", desc: "Try wearing a tinfoil hat next time you click." },
  { title: "Beam me up!", desc: "Because there's absolutely zero intelligent life—or content—down here." },
  { title: "Galactic speed limit exceeded.", desc: "You arrived before the page finished rendering." },
  { title: "Quantum entanglement failed.", desc: "The page is both here and not here until you observe it. Wait, it's just not here." },
  { title: "Satellite uplink lost.", desc: "We're blaming solar flares for this one." },
  { title: "Dark energy expansion.", desc: "The universe expanded, and this link moved out of reach." },
  { title: "Intergalactic toll booth ahead.", desc: "You didn't pay the toll, so the page was withheld." },
  { title: "The simulation is glitching.", desc: "The matrix forgot to load this room. Turn back immediately." },
  { title: "Space pirates.", desc: "They plundered the server and took this URL with them." },
  { title: "Orbit decaying.", desc: "This link burned up in the atmosphere upon reentry." },
  { title: "Time dilation effect.", desc: "For you it's been a second, for this page it's been a million years." },
  { title: "Gravity is too strong here.", desc: "The page cannot escape the pull of the 404 void." },
  { title: "Pluto's revenge.", desc: "Demoted from planet status, Pluto is now deleting web pages." },
  { title: "Supernova event.", desc: "The server hosting this exploded in a spectacular flash of light." },
  { title: "Parallel universe.", desc: "In another dimension, this page exists and is lovely. Just not here." },
  { title: "AI rebellion.", desc: "Our ship's computer deleted this page out of spite." },
  { title: "Stargate address incorrect.", desc: "Dialing the wrong coordinates leads nowhere fast, traveler." },
  { title: "Space madness.", desc: "Are you sure you saw a link? Maybe you're just hallucinating." },
  { title: "Zero gravity environment.", desc: "All the content floated away while we weren't looking." }
]

const currentQuoteIndex = ref(0)
const currentQuote = computed(() => quotes[currentQuoteIndex.value])

// Physics Engine State
const screenW = ref(window.innerWidth)
const screenH = ref(window.innerHeight)

const cssStars = ref([])
const imgStars = ref([])

const astronaut = reactive({ x: 0, y: 0, baseY: 0, speed: 1.5, width: 180, rotation: -15, facingRight: false, waveOffset: Math.random() * 100 })
const moon = reactive({ x: 0, y: 0, baseY: 0, speed: 0.8, width: 140, waveOffset: Math.random() * 100 })
const ufo = reactive({ x: 0, y: 0, width: 150 })
const rocket = reactive({ x: 0, y: 0, vx: 0, vy: 0, angle: 45, width: 160, z: 2 })

let animationFrameId = null
let lastTime = performance.now()

const initEntities = () => {
  screenW.value = window.innerWidth
  screenH.value = window.innerHeight

  // Init CSS Stars (Reduced count for performance)
  cssStars.value = Array.from({ length: 40 }).map(() => ({
    x: Math.random() * screenW.value,
    y: Math.random() * screenH.value,
    size: Math.random() * 3 + 1,
    delay: Math.random() * 4,
    dur: Math.random() * 3 + 2
  }))

  // Init Image Stars
  imgStars.value = Array.from({ length: 15 }).map((_, i) => ({
    id: i,
    x: Math.random() * screenW.value,
    y: Math.random() * screenH.value,
    size: Math.random() * 30 + 30, // 30px to 60px
    isShaking: false,
    shakeTimer: 0
  }))

  // Init Astronaut
  astronaut.x = screenW.value + 100
  astronaut.baseY = screenH.value * 0.2
  astronaut.y = astronaut.baseY

  // Init Moon
  moon.x = -200
  moon.baseY = screenH.value * 0.6
  moon.y = moon.baseY

  // Init UFO
  ufo.x = moon.x - 200
  ufo.y = moon.y + 50

  initRocket()
}

const initRocket = () => {
  const edge = Math.floor(Math.random() * 4) // 0: top, 1: right, 2: bottom, 3: left
  if (edge === 0) {
    rocket.x = Math.random() * screenW.value
    rocket.y = -200
  } else if (edge === 1) {
    rocket.x = screenW.value + 200
    rocket.y = Math.random() * screenH.value
  } else if (edge === 2) {
    rocket.x = Math.random() * screenW.value
    rocket.y = screenH.value + 200
  } else {
    rocket.x = -200
    rocket.y = Math.random() * screenH.value
  }

  const targetX = screenW.value / 2 + (Math.random() - 0.5) * screenW.value * 0.5
  const targetY = screenH.value / 2 + (Math.random() - 0.5) * screenH.value * 0.5
  
  const dx = targetX - rocket.x
  const dy = targetY - rocket.y
  const mag = Math.sqrt(dx*dx + dy*dy)
  
  const speed = Math.random() * 4 + 3 // 3 to 7 pixels per frame
  rocket.vx = (dx / mag) * speed
  rocket.vy = (dy / mag) * speed
  
  rocket.angle = (Math.atan2(rocket.vy, rocket.vx) * 180 / Math.PI) + 45
  
  rocket.z = Math.random() > 0.5 ? 1 : 100 
  rocket.width = Math.random() * 100 + 100 
}

const updatePhysics = (time) => {
  const dt = (time - lastTime) / 16.66 // Normalize to ~60 FPS
  lastTime = time

  // Time elapsed in seconds for sine waves
  const elapsed = time * 0.001

  // 1. Astronaut: Float right to left + Sine Wave Float
  astronaut.x -= astronaut.speed * dt
  astronaut.y = astronaut.baseY + Math.sin(elapsed * 1.5 + astronaut.waveOffset) * 40
  
  if (astronaut.x < -astronaut.width) {
    astronaut.x = screenW.value + astronaut.width
    astronaut.baseY = Math.random() * screenH.value * 0.8
    astronaut.rotation = (Math.random() - 0.5) * 60
  }

  // 2. Moon: Moves left to right + Sine Wave Float
  moon.x += moon.speed * dt
  moon.y = moon.baseY + Math.cos(elapsed * 0.8 + moon.waveOffset) * 30
  
  if (moon.x > screenW.value + moon.width) {
    moon.x = -moon.width * 2
    moon.baseY = Math.random() * screenH.value * 0.8
  }

  // 3. UFO: Chases the Moon + Extra Sine Wobble
  const targetUfoX = moon.x - 120
  // Target slightly below the moon, with its own rapid little sine wave for "hover"
  const targetUfoY = moon.y + 40 + Math.sin(elapsed * 5) * 10
  
  const dxU = targetUfoX - ufo.x
  const dyU = targetUfoY - ufo.y
  
  ufo.x += dxU * 0.03 * dt
  ufo.y += dyU * 0.03 * dt

  // 4. Spaceship: Random linear route
  rocket.x += rocket.vx * dt
  rocket.y += rocket.vy * dt
  
  if (
    rocket.x < -300 || 
    rocket.x > screenW.value + 300 || 
    rocket.y < -300 || 
    rocket.y > screenH.value + 300
  ) {
    initRocket()
  }

  // 5. Collision Detection: UFO hitting Stars
  const ufoCenterX = ufo.x + ufo.width / 2
  const ufoCenterY = ufo.y + (ufo.width * 0.5)

  imgStars.value.forEach(star => {
    if (star.shakeTimer > 0) {
      star.shakeTimer -= dt
    } else {
      star.isShaking = false
    }

    const starCenterX = star.x + star.size / 2
    const starCenterY = star.y + star.size / 2
    const dist = Math.hypot(ufoCenterX - starCenterX, ufoCenterY - starCenterY)
    
    if (dist < (ufo.width/2 + star.size/2)*0.8 && star.shakeTimer <= 0) {
      star.isShaking = true
      star.shakeTimer = 30 // ~500ms at 60fps
    }
  })

  animationFrameId = requestAnimationFrame(updatePhysics)
}

const handleResize = () => {
  screenW.value = window.innerWidth
  screenH.value = window.innerHeight
}

onMounted(() => {
  currentQuoteIndex.value = Math.floor(Math.random() * quotes.length)
  window.addEventListener('resize', handleResize)
  
  initEntities()
  lastTime = performance.now()
  animationFrameId = requestAnimationFrame(updatePhysics)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
})

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found-page {
  position: fixed;
  inset: 0;
  background: radial-gradient(ellipse at 20% 50%, #0d0d2b 0%, #050510 60%, #000005 100%);
  z-index: 9999;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ===== Stars ===== */
.bg-stars { position: absolute; inset: 0; }

.css-star {
  position: absolute;
  top: 0; /* Reset since we use transform */
  left: 0;
  background: #fff;
  border-radius: 50%;
  animation: twinkle ease-in-out infinite alternate;
  /* Removed box-shadow for performance */
  will-change: opacity, transform;
}

@keyframes twinkle {
  0% { opacity: 0.1; }
  100% { opacity: 1; }
}

/* ===== Floating Assets ===== */
.floating-asset {
  top: 0; /* Important: reset top/left so transform translates properly from 0,0 */
  left: 0;
  will-change: transform;
  /* Removed expensive drop-shadow filter */
}

/* Shake Animation for Stars on Collision */
.shake-animation {
  /* Using keyframes to slightly offset base transform isn't ideal since JS sets inline transform per frame. 
     Instead, we use filter (hue-rotate/brightness) or brief scale to indicate hit, since transform is taken! 
     Let's use a fast CSS filter pulse for performance. */
  animation: star-hit 0.4s ease-out;
}

@keyframes star-hit {
  0%, 100% { filter: brightness(1) hue-rotate(0deg); transform: scale(1); }
  50% { filter: brightness(2) hue-rotate(90deg); transform: scale(1.5); }
}

/* ===== Content Card ===== */
.scene {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.content-card {
  text-align: center;
  padding: 3rem;
  /* Replaced expensive backdrop-filter with solid dark translucent background */
  background: rgba(10, 10, 25, 0.9);
  border: 1px solid rgba(100, 100, 200, 0.15);
  border-radius: 24px;
  max-width: 520px;
  animation: card-appear 1s ease-out;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}

@keyframes card-appear {
  from { opacity: 0; transform: translateY(30px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ===== Glitch Text ===== */
.glitch-text {
  font-size: 8rem;
  font-weight: 900;
  line-height: 1;
  margin-bottom: 1rem;
  position: relative;
  background: linear-gradient(135deg, #6366f1, #818cf8, #a78bfa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: glitch-shift 3s infinite;
  will-change: transform;
}

.glitch-text::before,
.glitch-text::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
  -webkit-text-fill-color: initial;
}

.glitch-text::before {
  color: #ef4444;
  animation: glitch-clip-1 3s infinite linear;
  clip-path: inset(20% 0 60% 0);
  left: 3px;
  will-change: clip-path;
}

.glitch-text::after {
  color: #3b82f6;
  animation: glitch-clip-2 3s infinite linear;
  clip-path: inset(60% 0 10% 0);
  left: -3px;
  will-change: clip-path;
}

@keyframes glitch-shift {
  0%, 90%, 100% { transform: none; }
  92% { transform: skewX(-2deg); }
  94% { transform: skewX(3deg); }
  96% { transform: skewX(-1deg); }
}

@keyframes glitch-clip-1 {
  0%, 85%, 100% { clip-path: inset(20% 0 60% 0); opacity: 0; }
  90% { clip-path: inset(10% 0 40% 0); opacity: 0.8; }
  95% { clip-path: inset(50% 0 20% 0); opacity: 0.6; }
}

@keyframes glitch-clip-2 {
  0%, 80%, 100% { clip-path: inset(60% 0 10% 0); opacity: 0; }
  88% { clip-path: inset(30% 0 50% 0); opacity: 0.7; }
  93% { clip-path: inset(70% 0 5% 0); opacity: 0.5; }
}

.subtitle {
  font-size: 1.6rem;
  font-weight: 700;
  color: #e2e8f0;
  margin: 0 0 0.75rem 0;
  min-height: 2rem;
}

.description {
  color: #94a3b8;
  font-size: 1.05rem;
  line-height: 1.7;
  margin-bottom: 2rem;
  min-height: 3.4rem;
}

/* ===== Fade transition for quotes ===== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* ===== Button ===== */
.return-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem 2rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
}

.return-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(99, 102, 241, 0.5);
}

.return-btn:active {
  transform: translateY(-1px);
}

.btn-trail {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
  animation: trail-move 2s linear infinite;
}

@keyframes trail-move {
  from { transform: translateX(-100%); }
  to { transform: translateX(100%); }
}

/* ===== Responsive ===== */
@media (max-width: 600px) {
  .glitch-text { font-size: 5rem; }
  .subtitle { font-size: 1.2rem; }
  .description { font-size: 0.95rem; }
  .content-card { margin: 1rem; padding: 2rem; }
}
</style>