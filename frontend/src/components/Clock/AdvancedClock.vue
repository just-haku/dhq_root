<template>
  <div class="advanced-clock-container" @mousemove="onDrag" @mouseup="stopDrag" @mouseleave="stopDrag">
    <!-- Background image overlay -->
    <div id="bg-overlay" :style="overlayStyle"></div>

    <!-- Clock Stage -->
    <div id="stage" :style="stageStyle">
      <!-- Top controls if timer mode -->
      <div class="top-controls" v-if="state.clockMode !== 'clock' && state.showControls">
        <button @click="toggleTimer" :title="state.isRunning ? 'Pause' : 'Start'" class="control-btn top-btn">
          <span v-if="state.isRunning">⏸️</span>
          <span v-else>▶️</span>
        </button>
        <button @click="resetTimer" title="Reset" class="control-btn top-btn">
          <span>🔄</span>
        </button>
      </div>

      <div id="clock-face" @mousedown="startDrag">
        <div class="digit-cell" :class="{ flip: flipState[0] }">
          <img v-if="state.useImgDigits && state.imgDigits[digits[0]]" :src="state.imgDigits[digits[0]]" />
          <span v-else :style="digitStyle">{{ digits[0] }}</span>
        </div>
        <div class="digit-cell" :class="{ flip: flipState[1] }">
          <img v-if="state.useImgDigits && state.imgDigits[digits[1]]" :src="state.imgDigits[digits[1]]" />
          <span v-else :style="digitStyle">{{ digits[1] }}</span>
        </div>
        <div class="colon" :style="digitStyle">:</div>
        <div class="digit-cell" :class="{ flip: flipState[2] }">
          <img v-if="state.useImgDigits && state.imgDigits[digits[2]]" :src="state.imgDigits[digits[2]]" />
          <span v-else :style="digitStyle">{{ digits[2] }}</span>
        </div>
        <div class="digit-cell" :class="{ flip: flipState[3] }">
          <img v-if="state.useImgDigits && state.imgDigits[digits[3]]" :src="state.imgDigits[digits[3]]" />
          <span v-else :style="digitStyle">{{ digits[3] }}</span>
        </div>
        <div class="colon" :style="digitStyle">:</div>
        <div class="digit-cell" :class="{ flip: flipState[4] }">
          <img v-if="state.useImgDigits && state.imgDigits[digits[4]]" :src="state.imgDigits[digits[4]]" />
          <span v-else :style="digitStyle">{{ digits[4] }}</span>
        </div>
        <div class="digit-cell" :class="{ flip: flipState[5] }">
          <img v-if="state.useImgDigits && state.imgDigits[digits[5]]" :src="state.imgDigits[digits[5]]" />
          <span v-else :style="digitStyle">{{ digits[5] }}</span>
        </div>
      </div>
      <div id="date-line" v-show="state.showDate">{{ currentDate }}</div>
    </div>

    <!-- Settings toggler -->
    <button id="settings-button" @click="toggleSettings" title="Settings" class="settings-btn" style="position: absolute; right: 20px; top: 20px; z-index: 100;">
      ⚙️
    </button>

    <!-- Controls Panel -->
    <div id="controls" v-show="showSettings">
      <!-- Tab Bar -->
      <div id="tab-bar">
        <button class="tab-btn" :class="{active: activeTab === 'tab-bg'}" @click="activeTab = 'tab-bg'">🎨 Background</button>
        <button class="tab-btn" :class="{active: activeTab === 'tab-digits'}" @click="activeTab = 'tab-digits'">🔢 Digits</button>
        <button class="tab-btn" :class="{active: activeTab === 'tab-img-digits'}" @click="activeTab = 'tab-img-digits'">🖼️ Custom</button>
        <button class="tab-btn" :class="{active: activeTab === 'tab-mode'}" @click="activeTab = 'tab-mode'">⚙️ Mode</button>
      </div>

      <!-- ── TAB: BACKGROUND ── -->
      <div class="tab-panel" :class="{active: activeTab === 'tab-bg'}">
        <div class="section-title">Gradient Presets</div>
        <div class="swatch-grid" id="gradient-swatches">
           <div v-for="(grad, i) in GRADIENTS" :key="i"
                class="swatch" :class="{active: state.bgMode === 'gradient' && state.bgGradient === grad.g}"
                :style="{background: grad.g}" :title="grad.label"
                @click="setGradient(grad)"></div>
        </div>

        <div class="section-title">Solid Color</div>
        <div class="color-row">
          <label>Pick any background color</label>
          <input type="color" v-model="state.bgColor" @input="state.bgMode = 'solid'" />
        </div>

        <div class="section-title">Background Image</div>
        <label class="upload-btn">
          📁 Upload Image
          <input type="file" accept="image/*" @change="handleBgUpload" style="display:none" />
        </label>
        <div class="slider-row">
          <label>Blur</label>
          <input type="range" v-model="state.bgBlur" min="0" max="20" step="0.5" />
          <span id="blur-val">{{state.bgBlur}}px</span>
        </div>
        <div class="slider-row">
          <label>Overlay</label>
          <input type="range" v-model="state.bgDarken" min="0" max="0.9" step="0.05" />
          <span id="opacity-val">{{Math.round(state.bgDarken*100)}}%</span>
        </div>
        <p class="info-row">Upload a photo as background. Use blur & overlay to keep the clock readable.</p>
      </div>

      <!-- ── TAB: DIGITS STYLE ── -->
      <div class="tab-panel" :class="{active: activeTab === 'tab-digits'}">
        <div class="section-title">Font Style</div>
        <div class="digit-grid">
           <div v-for="style in DIGIT_STYLES" :key="style.id" 
                class="digit-option" :class="{active: state.digitFont === style.id}"
                @click="state.digitFont = style.id">
              <div class="preview-num" :style="{fontFamily: style.fontFamily, fontWeight: style.fontWeight||'700', letterSpacing: style.letterSpacing||'inherit'}">12</div>
              <div class="opt-label">{{style.label}}</div>
           </div>
        </div>

        <div class="section-title">Digit Color</div>
        <div class="color-strip">
           <div v-for="(color, i) in DIGIT_COLORS" :key="i"
                class="color-chip" :class="{active: state.digitColor === color.c}"
                :style="{background: color.c}" :title="color.c"
                @click="setDigitColor(color)"></div>
        </div>
        <div class="color-row" style="margin-top:10px">
          <label>Custom digit color</label>
          <input type="color" v-model="state.digitColor" @input="updateCustomDigitColor" />
        </div>

        <div class="section-title">Glow Intensity</div>
        <div class="slider-row">
          <label>Glow</label>
          <input type="range" v-model="state.glowIntensity" min="0" max="100" step="5" />
          <span id="glow-val">{{state.glowIntensity}}</span>
        </div>
      </div>

      <!-- ── TAB: CUSTOM DIGIT IMAGES ── -->
      <div class="tab-panel" :class="{active: activeTab === 'tab-img-digits'}">
        <p class="info-row">Upload individual images for each digit (0–9). The clock will use your images instead of text.</p>
        <p class="info-row warn" v-show="state.useImgDigits" style="margin-top:6px;">✅ Now using your custom digit images!</p>

        <div class="section-title">Upload Digits 0–9</div>
        <div class="img-digit-grid">
           <div v-for="i in 10" :key="i-1" class="img-digit-slot" @click="triggerDigitUpload(i-1)">
              <span class="slot-num">DIGIT {{i-1}}</span>
              <img v-if="state.imgDigits[i-1]" :src="state.imgDigits[i-1]" :alt="i-1" />
              <span v-else class="slot-icon">➕</span>
              <input type="file" :ref="(el) => digitInputs[i-1] = el" accept="image/*" style="display:none" @change="(e) => handleDigitUpload(e, i-1)" />
           </div>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:16px">
          <button class="upload-btn" @click="state.useImgDigits = true" :style="{opacity: imgDigitsCount > 0 ? 1 : 0.4, pointerEvents: imgDigitsCount > 0 ? 'auto' : 'none'}">
            ✅ Use Images ({{imgDigitsCount}}/10)
          </button>
          <button class="upload-btn" @click="clearImgDigits" style="background:rgba(255,100,100,0.15);border-color:rgba(255,100,100,0.4);color:#ffaaaa">
            🗑️ Clear All
          </button>
        </div>
      </div>

      <!-- ── TAB: MODE & SETTINGS ── -->
      <div class="tab-panel" :class="{active: activeTab === 'tab-mode'}">
        <div class="section-title">Timers & Mode</div>
        <div class="slider-row mb-2">
          <label style="width:120px">Clock Mode</label>
          <select v-model="state.clockMode" class="form-control" @change="onModeChange" style="flex:1">
            <option value="clock">Realtime Clock</option>
            <option value="timer">Timer</option>
            <option value="stopwatch">Stopwatch</option>
          </select>
        </div>

        <div v-show="state.clockMode === 'timer'" class="slider-row mb-2">
          <label style="width:120px">Duration (s)</label>
          <input type="number" v-model.number="state.timerDuration" min="0" class="form-control" style="flex:1; width:auto;">
          <button @click="resetTimer" class="btn btn-secondary btn-small" style="padding: 6px 10px;">Set</button>
        </div>

        <div class="slider-row mb-2">
          <label style="width:120px">Timezone Offset</label>
          <input type="number" v-model.number="state.timezoneOffset" step="0.5" class="form-control" style="flex:1;">
        </div>
        
        <div class="section-title mt-3">Visuals & Audio</div>
        <div class="slider-row mb-2">
           <label style="width:120px"><input type="checkbox" v-model="state.showDate"> Show Date</label>
           <label style="width:120px"><input type="checkbox" v-model="state.showControls"> Show Controls</label>
        </div>

        <div class="slider-row mb-2">
           <label style="width:120px"><input type="checkbox" v-model="state.soundEnabled"> Tick Sound</label>
           <select v-model="state.soundType" :disabled="!state.soundEnabled" class="form-control" style="flex:1">
              <option value="none">None</option>
              <option value="click">Click</option>
              <option value="beep">Beep</option>
           </select>
        </div>
        
        <div class="section-title mt-3">Reset</div>
        <div class="slider-row" style="justify-content:center;">
           <button @click="resetPositions" class="btn btn-secondary w-100" style="padding: 10px;">Reset Position to Center</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

const showSettings = ref(false)
const activeTab = ref('tab-bg')
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const currentTime = ref(new Date())

const digits = ref(['0','0', '0','0', '0','0'])
const flipState = ref([false, false, false, false, false, false])

const digitInputs = ref([])

const GRADIENTS = [
  { label:'Deep Space', g:'linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%)', c:'#1a1a2e' },
  { label:'Aurora',     g:'linear-gradient(135deg,#0d0d0d 0%,#1a3a2a 40%,#0d2a1a 100%)', c:'#0d2a1a' },
  { label:'Sunset',     g:'linear-gradient(135deg,#1a0533 0%,#6b1a2a 50%,#ff4e00 100%)', c:'#6b1a2a' },
  { label:'Ocean',      g:'linear-gradient(135deg,#000428 0%,#004e92 100%)',               c:'#002a5c' },
  { label:'Forest',     g:'linear-gradient(135deg,#0f2027 0%,#203a43 50%,#2c5364 100%)', c:'#203a43' },
  { label:'Neon',       g:'linear-gradient(135deg,#0f0c29 0%,#302b63 50%,#24243e 100%)', c:'#302b63' },
  { label:'Gold',       g:'linear-gradient(135deg,#1a0a00 0%,#3d1f00 50%,#7a4400 100%)', c:'#3d1f00' },
  { label:'Rose',       g:'linear-gradient(135deg,#1a001a 0%,#3d0028 50%,#7a0050 100%)', c:'#3d0028' },
  { label:'Midnight',   g:'linear-gradient(135deg,#000000 0%,#0a0a23 50%,#111133 100%)', c:'#0a0a23' },
  { label:'Teal',       g:'linear-gradient(135deg,#001a22 0%,#003344 50%,#005566 100%)', c:'#003344' },
]

const DIGIT_STYLES = [
  { id:'mono',      label:'Mono',       fontFamily:"'Courier New', monospace",       sample:'12' },
  { id:'rounded',   label:'Rounded',    fontFamily:"'Nunito', 'Segoe UI', sans-serif", sample:'12' },
  { id:'thin',      label:'Ultra Thin', fontFamily:"'Segoe UI Light','Helvetica Neue',sans-serif", fontWeight:'200', sample:'12' },
  { id:'slab',      label:'Slab',       fontFamily:"Georgia, 'Times New Roman', serif", sample:'12' },
  { id:'lcd',       label:'LCD',        fontFamily:"'Lucida Console','Courier New',monospace", letterSpacing:'4px', sample:'12' },
  { id:'digital7',  label:'Digital',    fontFamily:"'Digital-7','Share Tech Mono','Courier New',monospace", sample:'12' },
]

const DIGIT_COLORS = [
  { c:'#ffffff', s:'rgba(255,255,255,0.5)' },
  { c:'#7c6fff', s:'rgba(124,111,255,0.9)' },
  { c:'#ff6fd8', s:'rgba(255,111,216,0.9)' },
  { c:'#43e8a8', s:'rgba(67,232,168,0.9)'  },
  { c:'#ffd700', s:'rgba(255,215,0,0.9)'   },
  { c:'#ff5f40', s:'rgba(255,95,64,0.9)'   },
  { c:'#40d0ff', s:'rgba(64,208,255,0.9)'  },
  { c:'#ff9940', s:'rgba(255,153,64,0.9)'  },
]

const state = reactive({
  bgMode: 'gradient',
  bgGradient: GRADIENTS[0].g,
  bgColor: GRADIENTS[0].c,
  bgImageUrl: null,
  bgBlur: 0,
  bgDarken: 0.25,
  digitFont: 'mono',
  digitColor: '#ffffff',
  digitShadowColor: 'rgba(255,255,255,0.5)',
  glowIntensity: 60,
  useImgDigits: false,
  imgDigits: Array(10).fill(null),
  
  clockMode: 'clock',
  isRunning: true,
  timerDuration: 60,
  timerTime: 0,
  timezoneOffset: 0,
  showDate: true,
  showControls: true,
  clockPosition: { x: 50, y: 50 },
  soundEnabled: false,
  soundType: 'none',
  soundVolume: 0.7
})

watch(() => state.bgMode, updateBodyBg, { immediate: true })
watch(() => state.bgGradient, updateBodyBg)
watch(() => state.bgColor, updateBodyBg)

function updateBodyBg() {
  const container = document.querySelector('.advanced-clock-container')
  if (!container) return
  if (state.bgMode === 'gradient') container.style.background = state.bgGradient
  else if (state.bgMode === 'solid') container.style.background = state.bgColor
  else container.style.background = '#000'
}

const overlayStyle = computed(() => {
  if (state.bgMode === 'image' && state.bgImageUrl) {
    return {
      backgroundImage: `url(${state.bgImageUrl})`,
      filter: `blur(${state.bgBlur}px)`,
      opacity: 1,
      background: `linear-gradient(rgba(0,0,0,${state.bgDarken}),rgba(0,0,0,${state.bgDarken}))`,
      backgroundBlendMode: 'darken'
    }
  }
  return { opacity: 0 }
})

const stageStyle = computed(() => {
  return {
    position: 'absolute',
    left: `${state.clockPosition.x}%`,
    top: `${state.clockPosition.y}%`,
    transform: 'translate(-50%, -50%)',
    zIndex: 1
  }
})

const digitStyle = computed(() => {
  const style = DIGIT_STYLES.find(s => s.id === state.digitFont) || DIGIT_STYLES[0]
  const g = state.glowIntensity
  const c = state.digitShadowColor
  const textShadow = g > 0 ? `0 0 ${g*0.4}px ${c}, 0 0 ${g}px ${c}` : 'none'
  return {
    color: state.digitColor,
    fontFamily: style.fontFamily,
    fontWeight: style.fontWeight || '700',
    letterSpacing: style.letterSpacing || '-2px',
    textShadow
  }
})

const displayValues = computed(() => {
  if (state.clockMode === 'timer' || state.clockMode === 'stopwatch') {
    const time = state.timerTime
    const h = Math.floor(time / 3600).toString().padStart(2, '0')
    const m = Math.floor((time % 3600) / 60).toString().padStart(2, '0')
    const s = Math.floor(time % 60).toString().padStart(2, '0')
    return [h[0], h[1], m[0], m[1], s[0], s[1]]
  }
  const h = currentTime.value.getHours().toString().padStart(2, '0')
  const m = currentTime.value.getMinutes().toString().padStart(2, '0')
  const s = currentTime.value.getSeconds().toString().padStart(2, '0')
  return [h[0], h[1], m[0], m[1], s[0], s[1]]
})

watch(displayValues, (newVals) => {
  newVals.forEach((val, i) => {
    if (val !== digits.value[i]) {
      // Trigger flip
      flipState.value[i] = false
      digits.value[i] = val
      nextTick(() => {
        flipState.value[i] = true
      })
    }
  })
}, { deep: true })

const DAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const currentDate = computed(() => {
  return `${DAYS[currentTime.value.getDay()]} · ${MONTHS[currentTime.value.getMonth()]} ${currentTime.value.getDate()}, ${currentTime.value.getFullYear()}`
})

let interval = null
const updateClock = () => {
  if (state.clockMode === 'clock') {
    const now = new Date()
    const offset = state.timezoneOffset * 60 * 60 * 1000
    currentTime.value = new Date(now.getTime() + offset)
  } else if ((state.clockMode === 'timer' || state.clockMode === 'stopwatch') && state.isRunning) {
    if (state.clockMode === 'timer' && state.timerTime > 0) {
      state.timerTime -= 1
      if (state.timerTime <= 0) {
        state.timerTime = 0
        state.isRunning = false
        playSound('complete')
      }
    } else if (state.clockMode === 'stopwatch') {
      state.timerTime += 1
    }
  }
  
  if (state.soundEnabled && state.soundType !== 'none') playSound('tick')
}

const handleVisibilityChange = () => {
  if (document.hidden) {
    if (interval) {
      clearInterval(interval)
      interval = null
    }
  } else {
    updateClock()
    interval = setInterval(updateClock, 1000)
  }
}

const toggleSettings = () => showSettings.value = !showSettings.value
const setGradient = (grad) => { state.bgMode = 'gradient'; state.bgGradient = grad.g; state.bgColor = grad.c }
const setDigitColor = (c) => { state.digitColor = c.c; state.digitShadowColor = c.s }
const updateCustomDigitColor = () => { state.digitShadowColor = state.digitColor + 'cc' }

const toggleTimer = () => {
  if (state.clockMode === 'clock') {
    state.clockMode = 'timer'
    state.timerTime = state.timerDuration
  }
  state.isRunning = !state.isRunning
}
const resetTimer = () => {
  if (state.clockMode === 'clock') currentTime.value = new Date()
  else state.timerTime = state.clockMode === 'timer' ? state.timerDuration : 0
  state.isRunning = false
}
const onModeChange = () => {
  resetTimer()
  if (state.clockMode === 'timer') state.timerTime = state.timerDuration
  else if (state.clockMode === 'stopwatch') state.timerTime = 0
}

const handleBgUpload = (e) => {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (evt) => {
    state.bgImageUrl = evt.target.result
    state.bgMode = 'image'
  }
  reader.readAsDataURL(file)
}

const triggerDigitUpload = (i) => {
  if (digitInputs.value[i]) digitInputs.value[i].click()
}
const handleDigitUpload = (e, i) => {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (evt) => {
    state.imgDigits[i] = evt.target.result
  }
  reader.readAsDataURL(file)
}
const clearImgDigits = () => {
  state.imgDigits = Array(10).fill(null)
  state.useImgDigits = false
}
const imgDigitsCount = computed(() => state.imgDigits.filter(Boolean).length)

// Dragging
const startDrag = (e) => {
  const stage = document.getElementById('stage')
  if (!stage) return
  isDragging.value = true
  const rect = stage.getBoundingClientRect()
  dragOffset.value = {
    x: e.clientX - rect.left - rect.width / 2,
    y: e.clientY - rect.top - rect.height / 2
  }
}
const onDrag = (e) => {
  if (!isDragging.value) return
  const x = ((e.clientX - dragOffset.value.x) / window.innerWidth) * 100
  const y = ((e.clientY - dragOffset.value.y) / window.innerHeight) * 100
  state.clockPosition = {
    x: Math.max(0, Math.min(100, x)),
    y: Math.max(0, Math.min(100, y))
  }
}
const stopDrag = () => {
  if (isDragging.value) saveSettings()
  isDragging.value = false
}
const resetPositions = () => {
  state.clockPosition = { x: 50, y: 50 }
  saveSettings()
}

// Sound
const playSound = (type) => {
  if (!state.soundEnabled || state.soundType === 'none') return
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const gainNode = audioCtx.createGain()
    const osc = audioCtx.createOscillator()
    osc.connect(gainNode)
    gainNode.connect(audioCtx.destination)
    if (type === 'tick') {
      osc.frequency.value = state.soundType === 'click' ? 1000 : 800
      gainNode.gain.value = state.soundVolume * 0.1
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1)
      osc.start()
      osc.stop(audioCtx.currentTime + 0.1)
    }
  } catch(e) {}
}

const saveSettings = () => {
  localStorage.setItem('advancedClockSettingsV3', JSON.stringify(state))
}
const loadSettings = () => {
  const saved = localStorage.getItem('advancedClockSettingsV3') // keep fresh logic apart from old v1/v2
  if (saved) {
    try { Object.assign(state, JSON.parse(saved)) } catch(e){}
  }
}

watch(state, saveSettings, { deep: true })

onMounted(() => {
  loadSettings()
  nextTick(() => {
    updateBodyBg()
  })
  updateClock()
  interval = setInterval(updateClock, 1000)

  // Pause rendering when tab is hidden to fix CPU/GPU spikes
  document.addEventListener("visibilitychange", handleVisibilityChange)
  
  // Set initial digit values
  const initVals = displayValues.value
  for (let i = 0; i < 6; i++) {
    digits.value[i] = initVals[i]
  }
})

onUnmounted(() => {
  document.removeEventListener("visibilitychange", handleVisibilityChange)
  if (interval) clearInterval(interval)
})
</script>

<style scoped>
/* ─── Reset & Base ─── */
*, *::before, *::after { box-sizing: border-box; }

.advanced-clock-container {
  position: absolute;
  top: 0; left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: 'Segoe UI', system-ui, sans-serif;
  transition: background 0.6s ease;
  z-index: 1;
}

/* ─── BG Image Overlay ─── */
#bg-overlay {
  position: absolute; inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  pointer-events: none;
  z-index: 0;
}

/* ─── Clock Stage ─── */
#stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  padding: 20px;
}

/* ─── Clock Face ─── */
#clock-face {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 28px 44px;
  border-radius: 28px;
  background: rgba(0,0,0,0.35);
  backdrop-filter: blur(18px);
  border: 1.5px solid rgba(255,255,255,0.12);
  box-shadow: 0 8px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.04);
  transition: background 0.4s, box-shadow 0.4s;
  cursor: move;
}

/* ─── Digit Cells ─── */
.digit-cell {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 88px; height: 110px;
}
.digit-cell span {
  font-size: 96px;
  line-height: 1;
  transition: color 0.4s, text-shadow 0.4s, font-family 0.3s, opacity 0.15s;
  user-select: none;
}
.digit-cell img {
  width: 100%; height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 0 12px rgba(255,255,255,0.5));
  transition: filter 0.4s;
}

.digit-cell.flip span, .digit-cell.flip img {
  animation: flipIn 0.18s ease-out;
}
@keyframes flipIn {
  0%   { transform: scaleY(0.3) translateY(-8px); opacity: 0.4; }
  100% { transform: scaleY(1)   translateY(0);    opacity: 1;   }
}

.colon {
  font-size: 84px;
  opacity: 0.85;
  margin: 0 2px;
  animation: colonBlink 1s step-end infinite;
  line-height: 1;
  user-select: none;
  transition: color 0.4s, text-shadow 0.4s;
}
@keyframes colonBlink {
  0%, 100% { opacity: 0.85; }
  50%       { opacity: 0.2;  }
}

#date-line {
  font-size: 16px;
  color: rgba(255,255,255,0.6);
  letter-spacing: 3px;
  text-transform: uppercase;
  text-shadow: 0 2px 8px rgba(0,0,0,0.5);
  user-select: none;
}

/* Top Controls */
.top-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
}
.top-btn {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  width: 40px; height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.settings-btn {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  width: 40px; height: 40px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
}
.settings-btn:hover, .top-btn:hover {
  background: rgba(255,255,255,0.2);
}

/* Settings Controls Panel */
#controls {
  position: absolute;
  top: 70px; right: 20px;
  z-index: 100;
  background: rgba(15,15,25,0.82);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  backdrop-filter: blur(24px);
  padding: 0;
  width: min(94vw, 420px);
  color: #fff;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  text-align: left;
}

#tab-bar {
  display: flex;
  border-bottom: 1px solid rgba(255,255,255,0.10);
}
.tab-btn {
  flex: 1;
  padding: 13px 8px;
  background: none; border: none;
  color: #8888aa;
  font-size: 13px; font-weight: 600;
  cursor: pointer; position: relative;
}
.tab-btn::after {
  content: ''; position: absolute;
  bottom: 0; left: 20%; right: 20%;
  height: 2px; background: #7c6fff;
  border-radius: 2px; transform: scaleX(0); transition: 0.25s;
}
.tab-btn:hover { color: #fff; }
.tab-btn.active { color: #fff; }
.tab-btn.active::after { transform: scaleX(1); }

.tab-panel { display: none; padding: 20px 24px; max-height: calc(100vh - 150px); overflow-y: auto;}
.tab-panel.active { display: block; }

.section-title {
  font-size: 11px; font-weight: 700;
  letter-spacing: 2px; text-transform: uppercase;
  color: #8888aa; margin-bottom: 12px; margin-top: 16px;
}
.section-title:first-child { margin-top: 0; }

.swatch-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.swatch {
  width: 36px; height: 36px; border-radius: 10px;
  cursor: pointer; border: 2px solid transparent; flex-shrink: 0;
}
.swatch:hover, .swatch.active { border-color: #fff; transform: scale(1.1); }

.color-row, .slider-row { display: flex; align-items: center; gap: 12px; margin-top: 12px; }
.color-row label, .slider-row label { font-size: 13px; color: #8888aa; flex: 1; flex-shrink: 0;}
input[type="color"] { width: 44px; height: 32px; border-radius: 8px; background: none; border:1px solid #555;}
input[type="range"] { flex: 1; accent-color: #7c6fff; }
.slider-row span { font-size: 12px; color: #8888aa; width: 36px; text-align: right; }

.upload-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 9px 18px; border-radius: 10px;
  background: rgba(124,111,255,0.18); border: 1.5px solid rgba(124,111,255,0.4);
  color: #c4baff; font-size: 13px; cursor: pointer; margin-top: 10px;
}

.digit-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.digit-option {
  padding: 10px; border-radius: 12px; border: 2px solid rgba(255,255,255,0.08);
  cursor: pointer; text-align: center; background: rgba(255,255,255,0.04);
}
.digit-option.active { border-color: #7c6fff; background: rgba(124,111,255,0.15); }
.preview-num { font-size: 28px; color: #fff; }
.opt-label { font-size: 10px; color: #8888aa; text-transform: uppercase; }

.color-strip { display: flex; gap: 8px; flex-wrap: wrap; }
.color-chip { width: 28px; height: 28px; border-radius: 50%; cursor: pointer; border: 2px solid transparent; }
.color-chip.active { border-color: #fff; }

.img-digit-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.img-digit-slot {
  border-radius: 10px; border: 1.5px dashed rgba(255,255,255,0.2);
  padding: 6px; display: flex; flex-direction: column; align-items: center;
  cursor: pointer; background: rgba(255,255,255,0.03); min-height: 50px;
}
.img-digit-slot .slot-num { font-size: 10px; color: #8888aa; }
.img-digit-slot img { width: 100%; height: auto; object-fit: contain; }

.btn { padding: 8px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer; }
.btn-secondary { background: rgba(255,255,255,0.2); }
.form-control { background: rgba(255,255,255,0.1); border: 1px solid #555; color: #fff; padding: 6px; border-radius: 4px; }

.info-row { font-size: 12px; color: #8888aa; margin-top: 8px; }
.info-row.warn { color: #ffb347; }

.mb-2 { margin-bottom: 8px; }
.mt-3 { margin-top: 12px; }
.w-100 { width: 100%; }

@media (max-width: 520px) {
  .digit-cell { width: 56px; height: 72px; }
  .digit-cell span { font-size: 62px; }
  .colon { font-size: 54px; }
  #clock-face { padding: 18px 20px; border-radius: 20px; }
}
</style>
