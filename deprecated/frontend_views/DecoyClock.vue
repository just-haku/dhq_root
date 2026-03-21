<template>
  <div class="decoy-clock-container">
    <div class="clock-wrapper">
      <div class="digital-clock">
        {{ formattedTime }}
      </div>
      <div class="date-display">
        {{ formattedDate }}
      </div>
      <div class="timezone-display">
        {{ timezone }}
      </div>
    </div>
    
    <!-- Modular feature sections -->
    <div class="features-container">
      <div class="feature-section" v-if="showSeconds">
        <div class="seconds-display">{{ seconds }}</div>
        <div class="feature-label">Seconds</div>
      </div>
      
      <div class="feature-section" v-if="showMilliseconds">
        <div class="milliseconds-display">{{ milliseconds }}</div>
        <div class="feature-label">Milliseconds</div>
      </div>
      
      <div class="feature-section" v-if="showAnalog">
        <div class="analog-clock">
          <div class="clock-face">
            <div class="hand hour-hand" :style="hourHandStyle"></div>
            <div class="hand minute-hand" :style="minuteHandStyle"></div>
            <div class="hand second-hand" :style="secondHandStyle"></div>
            <div class="center-dot"></div>
          </div>
        </div>
        <div class="feature-label">Analog</div>
      </div>
    </div>
    
    <!-- Settings panel (expandable) -->
    <div class="settings-panel" :class="{ expanded: showSettings }">
      <button @click="toggleSettings" class="settings-toggle">
        {{ showSettings ? '✕' : '⚙️' }}
      </button>
      <div v-if="showSettings" class="settings-content">
        <div class="setting-item">
          <label>
            <input type="checkbox" v-model="showSeconds">
            Show Seconds
          </label>
        </div>
        <div class="setting-item">
          <label>
            <input type="checkbox" v-model="showMilliseconds">
            Show Milliseconds
          </label>
        </div>
        <div class="setting-item">
          <label>
            <input type="checkbox" v-model="showAnalog">
            Show Analog Clock
          </label>
        </div>
        <div class="setting-item">
          <label>
            <input type="checkbox" v-model="use24Hour">
            24-Hour Format
          </label>
        </div>
        <div class="setting-item">
          <label>
            Timezone:
            <select v-model="selectedTimezone">
              <option value="local">Local</option>
              <option value="UTC">UTC</option>
              <option value="America/New_York">New York</option>
              <option value="Europe/London">London</option>
              <option value="Asia/Tokyo">Tokyo</option>
            </select>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'DecoyClock',
  setup() {
    const currentTime = ref(new Date())
    const showSettings = ref(false)
    const showSeconds = ref(true)
    const showMilliseconds = ref(false)
    const showAnalog = ref(false)
    const use24Hour = ref(false)
    const selectedTimezone = ref('local')
    
    let interval = null
    
    const updateTime = () => {
      currentTime.value = new Date()
    }
    
    onMounted(() => {
      interval = setInterval(updateTime, showMilliseconds.value ? 10 : 1000)
    })
    
    onUnmounted(() => {
      if (interval) {
        clearInterval(interval)
      }
    })
    
    const formattedTime = computed(() => {
      const time = currentTime.value
      let hours = time.getHours()
      const minutes = time.getMinutes().toString().padStart(2, '0')
      const seconds = time.getSeconds().toString().padStart(2, '0')
      
      if (!use24Hour.value) {
        hours = hours % 12 || 12
        const period = time.getHours() >= 12 ? 'PM' : 'AM'
        return `${hours}:${minutes}:${seconds} ${period}`
      }
      
      return `${hours.toString().padStart(2, '0')}:${minutes}:${seconds}`
    })
    
    const formattedDate = computed(() => {
      const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }
      return currentTime.value.toLocaleDateString(undefined, options)
    })
    
    const timezone = computed(() => {
      if (selectedTimezone.value === 'local') {
        return Intl.DateTimeFormat().resolvedOptions().timeZone
      }
      return selectedTimezone.value
    })
    
    const seconds = computed(() => {
      return currentTime.value.getSeconds().toString().padStart(2, '0')
    })
    
    const milliseconds = computed(() => {
      return currentTime.value.getMilliseconds().toString().padStart(3, '0')
    })
    
    const hourHandStyle = computed(() => {
      const hours = currentTime.value.getHours() % 12
      const minutes = currentTime.value.getMinutes()
      const degrees = (hours * 30) + (minutes * 0.5)
      return `transform: rotate(${degrees}deg)`
    })
    
    const minuteHandStyle = computed(() => {
      const minutes = currentTime.value.getMinutes()
      const seconds = currentTime.value.getSeconds()
      const degrees = (minutes * 6) + (seconds * 0.1)
      return `transform: rotate(${degrees}deg)`
    })
    
    const secondHandStyle = computed(() => {
      const seconds = currentTime.value.getSeconds()
      const milliseconds = currentTime.value.getMilliseconds()
      const degrees = (seconds * 6) + (milliseconds * 0.006)
      return `transform: rotate(${degrees}deg)`
    })
    
    const toggleSettings = () => {
      showSettings.value = !showSettings.value
    }
    
    return {
      currentTime,
      formattedTime,
      formattedDate,
      timezone,
      seconds,
      milliseconds,
      showSettings,
      showSeconds,
      showMilliseconds,
      showAnalog,
      use24Hour,
      selectedTimezone,
      hourHandStyle,
      minuteHandStyle,
      secondHandStyle,
      toggleSettings
    }
  }
}
</script>

<style scoped>
.decoy-clock-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: 'Courier New', monospace;
  color: white;
  position: relative;
}

.clock-wrapper {
  text-align: center;
  margin-bottom: 2rem;
}

.digital-clock {
  font-size: 4rem;
  font-weight: bold;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
  margin-bottom: 1rem;
  letter-spacing: 0.1em;
}

.date-display {
  font-size: 1.5rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
}

.timezone-display {
  font-size: 1rem;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.features-container {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  justify-content: center;
}

.feature-section {
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 10px;
  backdrop-filter: blur(10px);
  min-width: 120px;
}

.seconds-display,
.milliseconds-display {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.analog-clock {
  width: 100px;
  height: 100px;
  margin: 0 auto 0.5rem;
  position: relative;
}

.clock-face {
  width: 100%;
  height: 100%;
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  position: relative;
  background: rgba(255, 255, 255, 0.1);
}

.hand {
  position: absolute;
  background: white;
  transform-origin: bottom center;
  bottom: 50%;
  left: 50%;
  border-radius: 2px;
}

.hour-hand {
  width: 4px;
  height: 30px;
  margin-left: -2px;
}

.minute-hand {
  width: 3px;
  height: 40px;
  margin-left: -1.5px;
}

.second-hand {
  width: 2px;
  height: 45px;
  margin-left: -1px;
  background: #ff6b6b;
}

.center-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.feature-label {
  font-size: 0.9rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.settings-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.settings-toggle {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 10px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.settings-toggle:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.settings-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  padding: 1rem;
  margin-top: 10px;
  min-width: 200px;
}

.setting-item {
  margin-bottom: 0.8rem;
}

.setting-item label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.setting-item input[type="checkbox"] {
  margin: 0;
}

.setting-item select {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.25rem;
  border-radius: 4px;
  margin-left: 0.5rem;
}

.setting-item select option {
  background: #667eea;
  color: white;
}

@media (max-width: 768px) {
  .digital-clock {
    font-size: 3rem;
  }
  
  .features-container {
    gap: 1rem;
  }
  
  .feature-section {
    min-width: 100px;
    padding: 0.8rem;
  }
  
  .analog-clock {
    width: 80px;
    height: 80px;
  }
}
</style>
