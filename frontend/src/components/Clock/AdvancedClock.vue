<template>
  <div class="advanced-clock-container" :data-theme="theme">
    <!-- Background Layer -->
    <div id="background-layer" :style="backgroundStyle"></div>
    
    <!-- Alignment Grid -->
    <div id="alignment-grid" v-show="showGrid">
      <div class="grid-line v-mid"></div>
      <div class="grid-line h-mid"></div>
    </div>

    <!-- Clock Container -->
    <div id="clock-container" :style="clockStyle" @mousedown="startDrag">
      <div class="chunk" id="hours" :style="digitStyle('hours')">{{ displayHours }}</div>
      <div class="chunk sep" id="sep1" :style="digitStyle('separator')">:</div>
      <div class="chunk" id="minutes" :style="digitStyle('minutes')">{{ displayMinutes }}</div>
      <div class="chunk sep" id="sep2" :style="digitStyle('separator')">:</div>
      <div class="chunk" id="seconds" :style="digitStyle('seconds')">{{ displaySeconds }}</div>
    </div>

    <!-- Date Display -->
    <div id="date-display" class="draggable-ui" :style="dateStyle" v-show="showDate">
      {{ currentDate }}
    </div>

    <!-- Control Buttons -->
    <div class="top-controls" v-show="showControls">
      <button @click="toggleTimer" :title="timerMode ? 'Start Timer' : 'Start Stopwatch'" class="control-btn">
        <i :class="timerMode ? 'fas fa-play' : 'fas fa-stopwatch'"></i>
      </button>
      <button @click="pauseTimer" title="Pause" class="control-btn">
        <i class="fas fa-pause"></i>
      </button>
      <button @click="resetTimer" title="Reset" class="control-btn">
        <i class="fas fa-undo"></i>
      </button>
    </div>
    
    <!-- Settings Button -->
    <button id="settings-button" @click="toggleSettings" title="Settings" class="settings-btn">
      <i class="fas fa-cog"></i>
    </button>

    <!-- Settings Panel -->
    <div id="settings-panel" v-show="showSettings" class="settings-panel">
      <div class="settings-tabs main-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="['tab-button', { active: activeTab === tab.id }]"
          :title="tab.name"
        >
          <i :class="tab.icon"></i>
        </button>
      </div>

      <!-- Mode Tab -->
      <div class="tab-content" v-show="activeTab === 'mode-tab'">
        <h3>Mode & Timing</h3>
        <label>Mode</label>
        <select v-model="clockMode" @change="onModeChange" class="form-control">
          <option value="clock">Clock (Realtime)</option>
          <option value="timer">Timer</option>
          <option value="stopwatch">Stopwatch</option>
        </select>

        <div v-show="clockMode === 'timer'" class="timer-settings">
          <label>Duration (Seconds)</label>
          <div class="d-flex gap-2">
            <input type="number" v-model="timerDuration" min="0" class="form-control">
            <button @click="setTimer" class="btn btn-secondary">Set</button>
          </div>
        </div>

        <label>Speed Multiplier (x)</label>
        <input type="number" v-model="speedMultiplier" min="0.1" step="0.1" class="form-control">

        <div class="form-check mt-2">
          <input type="checkbox" v-model="showDate" id="date-display-toggle" class="form-check-input">
          <label for="date-display-toggle" class="form-check-label">Show Date</label>
        </div>
        
        <div class="controls mt-3 d-flex gap-2">
          <button @click="startClock" class="btn btn-primary w-100">Start</button>
          <button @click="pauseClock" class="btn btn-secondary w-100">Pause</button>
          <button @click="resetClock" class="btn btn-danger w-100">Reset</button>
        </div>
      </div>

      <!-- Background Tab -->
      <div class="tab-content" v-show="activeTab === 'background-tab'">
        <h3>Background</h3>
        <label>Solid Color</label>
        <div class="d-flex gap-2 mb-3">
          <input type="color" v-model="backgroundColor" class="form-control">
          <button @click="applyBackground('solid')" class="btn btn-secondary">Apply</button>
        </div>
        
        <label>Gradient (Deg, Start, End)</label>
        <div class="d-flex gap-2 mb-2">
          <input type="number" v-model="gradientDegree" style="width: 60px" class="form-control">
          <input type="color" v-model="gradientStart" class="form-control">
          <input type="color" v-model="gradientEnd" class="form-control">
        </div>
        <button @click="applyBackground('gradient')" class="btn btn-secondary w-100 mb-3">Apply Gradient</button>

        <label>Image URL</label>
        <input type="text" v-model="backgroundImageUrl" placeholder="https://..." class="form-control mb-2">
        <button @click="applyBackground('image')" class="btn btn-secondary w-100">Apply Image</button>
      </div>

      <!-- Digits Tab -->
      <div class="tab-content" v-show="activeTab === 'digits-tab'">
        <h3>Digits Style</h3>
        <div class="settings-tabs nested-tabs mb-3">
          <button 
            v-for="digitTab in digitTabs" 
            :key="digitTab.id"
            @click="activeDigitTab = digitTab.id"
            :class="['tab-button', 'nested', { active: activeDigitTab === digitTab.id }]"
          >
            {{ digitTab.name }}
          </button>
        </div>

        <!-- Global Digit Settings -->
        <div v-show="activeDigitTab === 'digits-global-tab'">
          <label>Font Family</label>
          <select v-model="globalFont" @change="applyGlobalFont" class="form-control">
            <option value="'Orbitron', sans-serif">Orbitron</option>
            <option value="'Roboto Mono', monospace">Roboto Mono</option>
            <option value="'Poppins', sans-serif">Poppins</option>
            <option value="custom">Custom Font...</option>
          </select>
          
          <hr>
          
          <label>Texture / Gradient</label>
          <div class="d-flex gap-2 mb-2">
            <input type="color" v-model="digitSolidColor" class="form-control">
            <input type="color" v-model="digitGradientStart" class="form-control">
            <input type="color" v-model="digitGradientEnd" class="form-control">
          </div>
          <div class="d-flex gap-2 mb-2">
            <button @click="applyDigitStyle('solid')" class="btn btn-secondary btn-small w-100">Solid</button>
            <button @click="applyDigitStyle('gradient')" class="btn btn-secondary btn-small w-100">Gradient</button>
          </div>

          <label>Image Texture URL</label>
          <input type="text" v-model="digitImageUrl" placeholder="https://..." class="form-control mb-2">
          <button @click="applyDigitStyle('image')" class="btn btn-secondary btn-small w-100">Apply Texture</button>
        </div>
        
        <!-- Individual Digit Settings -->
        <div v-for="digit in ['hours', 'minutes', 'seconds']" :key="digit" v-show="activeDigitTab === `digits-${digit}-tab`">
          <button @click="resetDigitToGlobal(digit)" class="btn btn-secondary w-100 mb-2">Reset to Global</button>
          <label>Specific Color</label>
          <input type="color" v-model="digitColors[digit]" class="form-control mb-2">
          <button @click="applyDigitColor(digit)" class="btn btn-secondary w-100">Apply Color</button>
        </div>
      </div>

      <!-- Layout Tab -->
      <div class="tab-content" v-show="activeTab === 'layout-tab'">
        <h3>Layout</h3>
        <label>Size (VW)</label>
        <input type="range" v-model="clockSize" min="5" max="50" class="form-range">
        
        <label>Timezone Offset (Hours)</label>
        <input type="number" v-model="timezoneOffset" step="0.5" class="form-control">
        
        <hr>
        
        <button @click="toggleGrid" class="btn btn-secondary w-100 mb-2">Toggle Grid</button>
        <button @click="resetPositions" class="btn btn-secondary w-100 mb-2">Reset Positions</button>
        <button @click="resetAll" class="btn btn-danger w-100">Reset All & Reload</button>
      </div>

      <!-- Style Tab -->
      <div class="tab-content" v-show="activeTab === 'style-tab'">
        <h3>Effects</h3>
        <label>Opacity (BG / Digits)</label>
        <div class="d-flex gap-2">
          <input type="range" v-model="bgOpacity" max="1" step="0.1" class="form-range">
          <input type="range" v-model="digitsOpacity" max="1" step="0.1" class="form-range">
        </div>
        
        <label>Blur (BG / Digits)</label>
        <div class="d-flex gap-2">
          <input type="range" v-model="bgBlur" max="20" class="form-range">
          <input type="range" v-model="digitsBlur" max="20" class="form-range">
        </div>
        
        <div class="form-check mt-2">
          <input type="checkbox" v-model="glowEnabled" id="glow-toggle" class="form-check-input">
          <label for="glow-toggle" class="form-check-label">Neon Glow</label>
        </div>
        <input type="color" v-model="glowColor" class="form-control mt-2">
      </div>

      <!-- Audio Tab -->
      <div class="tab-content" v-show="activeTab === 'audio-tab'">
        <h3>Audio</h3>
        <div class="form-check mb-2">
          <input type="checkbox" v-model="soundEnabled" id="sound-toggle" class="form-check-input">
          <label for="sound-toggle" class="form-check-label">Enable Ticking</label>
        </div>
        <select v-model="soundType" class="form-select">
          <option value="none">None</option>
          <option value="click">Click</option>
          <option value="beep">Beep</option>
        </select>
        <label>Volume</label>
        <input type="range" v-model="soundVolume" max="1" step="0.1" class="form-range">
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

export default {
  name: 'AdvancedClock',
  setup() {
    // Clock state
    const currentTime = ref(new Date())
    const clockMode = ref('clock')
    const isRunning = ref(true)
    const speedMultiplier = ref(1)
    const timezoneOffset = ref(0)
    
    // Timer state
    const timerDuration = ref(60)
    const timerTime = ref(0)
    const timerMode = ref(false)
    
    // Display state
    const showDate = ref(false)
    const showControls = ref(false)
    const showGrid = ref(false)
    const showSettings = ref(false)
    
    // UI state
    const activeTab = ref('mode-tab')
    const activeDigitTab = ref('digits-global-tab')
    const theme = ref('dark')
    
    // Background settings
    const backgroundType = ref('solid')
    const backgroundColor = ref('#000000')
    const gradientDegree = ref(90)
    const gradientStart = ref('#000000')
    const gradientEnd = ref('#1e1e24')
    const backgroundImageUrl = ref('')
    
    // Digit settings
    const globalFont = ref("'Orbitron', sans-serif")
    const digitSolidColor = ref('#ffffff')
    const digitGradientStart = ref('#ffffff')
    const digitGradientEnd = ref('#3b82f6')
    const digitImageUrl = ref('')
    const digitColors = ref({
      hours: '#ffffff',
      minutes: '#ffffff',
      seconds: '#ffffff'
    })
    
    // Style settings
    const clockSize = ref(15)
    const bgOpacity = ref(1)
    const digitsOpacity = ref(1)
    const bgBlur = ref(0)
    const digitsBlur = ref(0)
    const glowEnabled = ref(false)
    const glowColor = ref('#ffffff')
    
    // Audio settings
    const soundEnabled = ref(false)
    const soundType = ref('click')
    const soundVolume = ref(0.7)
    
    // Drag state
    const isDragging = ref(false)
    const dragOffset = ref({ x: 0, y: 0 })
    const clockPosition = ref({ x: 50, y: 50 })
    
    // Tab definitions
    const tabs = ref([
      { id: 'mode-tab', name: 'Mode', icon: 'fas fa-clock' },
      { id: 'background-tab', name: 'Background', icon: 'fas fa-image' },
      { id: 'digits-tab', name: 'Digits', icon: 'fas fa-font' },
      { id: 'layout-tab', name: 'Layout', icon: 'fas fa-th' },
      { id: 'style-tab', name: 'Style', icon: 'fas fa-magic' },
      { id: 'audio-tab', name: 'Audio', icon: 'fas fa-volume-up' }
    ])
    
    const digitTabs = ref([
      { id: 'digits-global-tab', name: 'Global' },
      { id: 'digits-hours-tab', name: 'Hr' },
      { id: 'digits-minutes-tab', name: 'Min' },
      { id: 'digits-seconds-tab', name: 'Sec' }
    ])
    
    let interval = null
    
    // Computed properties
    const displayHours = computed(() => {
      if (clockMode.value === 'timer' || clockMode.value === 'stopwatch') {
        return Math.floor(timerTime.value / 3600).toString().padStart(2, '0')
      }
      const hours = currentTime.value.getHours()
      return hours.toString().padStart(2, '0')
    })
    
    const displayMinutes = computed(() => {
      if (clockMode.value === 'timer' || clockMode.value === 'stopwatch') {
        return Math.floor((timerTime.value % 3600) / 60).toString().padStart(2, '0')
      }
      return currentTime.value.getMinutes().toString().padStart(2, '0')
    })
    
    const displaySeconds = computed(() => {
      if (clockMode.value === 'timer' || clockMode.value === 'stopwatch') {
        return (timerTime.value % 60).toString().padStart(2, '0')
      }
      return currentTime.value.getSeconds().toString().padStart(2, '0')
    })
    
    const currentDate = computed(() => {
      return currentTime.value.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    })
    
    const backgroundStyle = computed(() => {
      let style = {
        opacity: bgOpacity.value,
        filter: `blur(${bgBlur.value}px)`
      }
      
      if (backgroundType.value === 'solid') {
        style.backgroundColor = backgroundColor.value
      } else if (backgroundType.value === 'gradient') {
        style.background = `linear-gradient(${gradientDegree.value}deg, ${gradientStart.value}, ${gradientEnd.value})`
      } else if (backgroundType.value === 'image' && backgroundImageUrl.value) {
        style.backgroundImage = `url(${backgroundImageUrl.value})`
        style.backgroundSize = 'cover'
        style.backgroundPosition = 'center'
      }
      
      return style
    })
    
    const clockStyle = computed(() => {
      return {
        fontSize: `${clockSize.value}vw`,
        left: `${clockPosition.value.x}%`,
        top: `${clockPosition.value.y}%`,
        transform: 'translate(-50%, -50%)',
        opacity: digitsOpacity.value,
        filter: `blur(${digitsBlur.value}px)`,
        textShadow: glowEnabled.value ? `0 0 10px ${glowColor.value}` : 'none'
      }
    })
    
    const dateStyle = computed(() => {
      return {
        left: `${clockPosition.value.x}%`,
        top: `${clockPosition.value.y + 10}%`,
        transform: 'translateX(-50%)'
      }
    })
    
    // Methods
    const updateClock = () => {
      if (clockMode.value === 'clock') {
        const now = new Date()
        const offset = timezoneOffset.value * 60 * 60 * 1000
        currentTime.value = new Date(now.getTime() + offset)
      } else if ((clockMode.value === 'timer' || clockMode.value === 'stopwatch') && isRunning.value) {
        if (clockMode.value === 'timer' && timerTime.value > 0) {
          timerTime.value -= speedMultiplier.value
          if (timerTime.value <= 0) {
            timerTime.value = 0
            isRunning.value = false
            playSound('complete')
          }
        } else if (clockMode.value === 'stopwatch') {
          timerTime.value += speedMultiplier.value
        }
      }
      
      if (soundEnabled.value && soundType.value !== 'none') {
        playSound('tick')
      }
    }
    
    const startClock = () => {
      isRunning.value = true
    }
    
    const pauseClock = () => {
      isRunning.value = false
    }
    
    const resetClock = () => {
      if (clockMode.value === 'clock') {
        currentTime.value = new Date()
      } else {
        timerTime.value = clockMode.value === 'timer' ? timerDuration.value : 0
      }
      isRunning.value = false
    }
    
    const toggleTimer = () => {
      if (clockMode.value === 'clock') {
        clockMode.value = 'timer'
        timerTime.value = timerDuration.value
      }
      isRunning.value = !isRunning.value
    }
    
    const pauseTimer = () => {
      isRunning.value = false
    }
    
    const resetTimer = () => {
      timerTime.value = clockMode.value === 'timer' ? timerDuration.value : 0
      isRunning.value = false
    }
    
    const setTimer = () => {
      timerTime.value = timerDuration.value
    }
    
    const onModeChange = () => {
      resetClock()
      if (clockMode.value === 'timer') {
        timerTime.value = timerDuration.value
      } else if (clockMode.value === 'stopwatch') {
        timerTime.value = 0
      }
    }
    
    const toggleSettings = () => {
      showSettings.value = !showSettings.value
    }
    
    const applyBackground = (type) => {
      backgroundType.value = type
      saveSettings()
    }
    
    const applyGlobalFont = () => {
      saveSettings()
    }
    
    const applyDigitStyle = (style) => {
      saveSettings()
    }
    
    const applyDigitColor = (digit) => {
      saveSettings()
    }
    
    const resetDigitToGlobal = (digit) => {
      digitColors.value[digit] = digitSolidColor.value
      saveSettings()
    }
    
    const toggleGrid = () => {
      showGrid.value = !showGrid.value
    }
    
    const resetPositions = () => {
      clockPosition.value = { x: 50, y: 50 }
      saveSettings()
    }
    
    const resetAll = () => {
      localStorage.removeItem('advancedClockSettings')
      location.reload()
    }
    
    const saveSettings = () => {
      const settings = {
        clockMode: clockMode.value,
        speedMultiplier: speedMultiplier.value,
        timezoneOffset: timezoneOffset.value,
        showDate: showDate.value,
        showControls: showControls.value,
        backgroundType: backgroundType.value,
        backgroundColor: backgroundColor.value,
        gradientDegree: gradientDegree.value,
        gradientStart: gradientStart.value,
        gradientEnd: gradientEnd.value,
        backgroundImageUrl: backgroundImageUrl.value,
        globalFont: globalFont.value,
        digitColors: digitColors.value,
        clockSize: clockSize.value,
        bgOpacity: bgOpacity.value,
        digitsOpacity: digitsOpacity.value,
        bgBlur: bgBlur.value,
        digitsBlur: digitsBlur.value,
        glowEnabled: glowEnabled.value,
        glowColor: glowColor.value,
        soundEnabled: soundEnabled.value,
        soundType: soundType.value,
        soundVolume: soundVolume.value,
        clockPosition: clockPosition.value
      }
      localStorage.setItem('advancedClockSettings', JSON.stringify(settings))
    }
    
    const loadSettings = () => {
      const saved = localStorage.getItem('advancedClockSettings')
      if (saved) {
        const settings = JSON.parse(saved)
        Object.assign(settings, settings)
      }
    }
    
    const digitStyle = (digit) => {
      const baseStyle = {
        fontFamily: globalFont.value
      }
      
      if (digit === 'separator') {
        return baseStyle
      }
      
      if (digitColors.value[digit] !== digitSolidColor.value) {
        baseStyle.color = digitColors.value[digit]
      }
      
      return baseStyle
    }
    
    const playSound = (type) => {
      if (!soundEnabled.value || soundType.value === 'none') return
      
      // Simple sound implementation - can be enhanced with actual audio files
      const audio = new Audio()
      audio.volume = soundVolume.value
      
      if (type === 'tick') {
        // Create a simple tick sound
        const oscillator = new (window.AudioContext || window.webkitAudioContext)()
        const gainNode = oscillator.createGain()
        const osc = oscillator.createOscillator()
        
        osc.connect(gainNode)
        gainNode.connect(oscillator.destination)
        
        osc.frequency.value = soundType.value === 'click' ? 1000 : 800
        gainNode.gain.value = 0.1
        gainNode.gain.exponentialRampToValueAtTime(0.01, oscillator.currentTime + 0.1)
        
        osc.start()
        osc.stop(oscillator.currentTime + 0.1)
      }
    }
    
    const startDrag = (e) => {
      isDragging.value = true
      const rect = e.target.getBoundingClientRect()
      dragOffset.value = {
        x: e.clientX - rect.left - rect.width / 2,
        y: e.clientY - rect.top - rect.height / 2
      }
      
      document.addEventListener('mousemove', onDrag)
      document.addEventListener('mouseup', stopDrag)
    }
    
    const onDrag = (e) => {
      if (!isDragging.value) return
      
      const x = ((e.clientX - dragOffset.value.x) / window.innerWidth) * 100
      const y = ((e.clientY - dragOffset.value.y) / window.innerHeight) * 100
      
      clockPosition.value = {
        x: Math.max(10, Math.min(90, x)),
        y: Math.max(10, Math.min(90, y))
      }
    }
    
    const stopDrag = () => {
      isDragging.value = false
      document.removeEventListener('mousemove', onDrag)
      document.removeEventListener('mouseup', stopDrag)
      saveSettings()
    }
    
    // Lifecycle
    onMounted(() => {
      loadSettings()
      interval = setInterval(updateClock, 1000 / speedMultiplier.value)
    })
    
    onUnmounted(() => {
      if (interval) {
        clearInterval(interval)
      }
    })
    
    watch(speedMultiplier, (newSpeed) => {
      if (interval) {
        clearInterval(interval)
        interval = setInterval(updateClock, 1000 / newSpeed)
      }
    })
    
    return {
      // State
      currentTime,
      clockMode,
      isRunning,
      speedMultiplier,
      timezoneOffset,
      timerDuration,
      timerTime,
      timerMode,
      showDate,
      showControls,
      showGrid,
      showSettings,
      activeTab,
      activeDigitTab,
      theme,
      backgroundType,
      backgroundColor,
      gradientDegree,
      gradientStart,
      gradientEnd,
      backgroundImageUrl,
      globalFont,
      digitSolidColor,
      digitGradientStart,
      digitGradientEnd,
      digitImageUrl,
      digitColors,
      clockSize,
      bgOpacity,
      digitsOpacity,
      bgBlur,
      digitsBlur,
      glowEnabled,
      glowColor,
      soundEnabled,
      soundType,
      soundVolume,
      clockPosition,
      tabs,
      digitTabs,
      
      // Computed
      displayHours,
      displayMinutes,
      displaySeconds,
      currentDate,
      backgroundStyle,
      clockStyle,
      dateStyle,
      
      // Methods
      startClock,
      pauseClock,
      resetClock,
      toggleTimer,
      pauseTimer,
      resetTimer,
      setTimer,
      onModeChange,
      toggleSettings,
      applyBackground,
      applyGlobalFont,
      applyDigitStyle,
      applyDigitColor,
      resetDigitToGlobal,
      toggleGrid,
      resetPositions,
      resetAll,
      digitStyle,
      startDrag
    }
  }
}
</script>

<style scoped>
.advanced-clock-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #000;
  z-index: 1;
}

#background-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

#alignment-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}

.grid-line {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
}

.grid-line.v-mid {
  left: 50%;
  width: 1px;
  height: 100%;
  transform: translateX(-50%);
}

.grid-line.h-mid {
  top: 50%;
  width: 100%;
  height: 1px;
  transform: translateY(-50%);
}

#clock-container {
  position: absolute;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  color: #fff;
  cursor: move;
  user-select: none;
}

.chunk {
  display: inline-block;
  min-width: 1.2em;
  text-align: center;
  line-height: 1;
}

.sep {
  margin: 0 0.1em;
  opacity: 0.7;
}

#date-display {
  position: absolute;
  z-index: 11;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8em;
  font-family: 'Inter', sans-serif;
  text-align: center;
  white-space: nowrap;
}

.top-controls {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  gap: 10px;
}

.control-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.settings-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 20;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.settings-panel {
  position: absolute;
  top: 70px;
  right: 20px;
  width: 350px;
  max-height: 80vh;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 20px;
  z-index: 30;
  overflow-y: auto;
  backdrop-filter: blur(10px);
}

.settings-tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9em;
}

.tab-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.tab-button.active {
  background: rgba(59, 130, 246, 0.5);
  border-color: #3b82f6;
}

.tab-content {
  color: #fff;
}

.tab-content h3 {
  margin-bottom: 15px;
  color: #3b82f6;
  font-size: 1.1em;
}

.tab-content label {
  display: block;
  margin-bottom: 5px;
  font-size: 0.9em;
  color: rgba(255, 255, 255, 0.8);
}

.tab-content input,
.tab-content select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  border-radius: 5px;
  padding: 8px;
  margin-bottom: 10px;
  width: 100%;
}

.tab-content input[type="color"] {
  height: 40px;
  cursor: pointer;
}

.tab-content input[type="range"] {
  cursor: pointer;
}

.tab-content button {
  background: #3b82f6;
  border: none;
  color: #fff;
  padding: 10px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-content button:hover {
  background: #2563eb;
}

.tab-content button.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.tab-content button.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.tab-content button.btn-danger {
  background: #ef4444;
}

.tab-content button.btn-danger:hover {
  background: #dc2626;
}

.nested-tabs {
  margin-bottom: 15px;
}

.nested {
  font-size: 0.8em;
  padding: 5px 8px;
}

.form-check {
  margin-bottom: 10px;
}

.form-check-input {
  margin-right: 8px;
}

.d-flex {
  display: flex;
}

.gap-2 {
  gap: 8px;
}

.w-100 {
  width: 100%;
}

.mt-2 {
  margin-top: 8px;
}

.mt-3 {
  margin-top: 12px;
}

.mb-2 {
  margin-bottom: 8px;
}

.mb-3 {
  margin-bottom: 12px;
}

.text-center {
  text-align: center;
}

.btn-small {
  padding: 5px 8px;
  font-size: 0.8em;
}

hr {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 15px 0;
}

/* Dark theme */
[data-theme="dark"] {
  background: #000;
  color: #fff;
}

/* Light theme */
[data-theme="light"] {
  background: #fff;
  color: #000;
}

[data-theme="light"] .settings-panel {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(0, 0, 0, 0.2);
}

[data-theme="light"] .tab-content label {
  color: rgba(0, 0, 0, 0.8);
}

[data-theme="light"] .tab-content input,
[data-theme="light"] .tab-content select {
  background: rgba(0, 0, 0, 0.1);
  border-color: rgba(0, 0, 0, 0.2);
  color: #000;
}

[data-theme="light"] #clock-container {
  color: #000;
}

[data-theme="light"] #date-display {
  color: rgba(0, 0, 0, 0.7);
}
</style>
