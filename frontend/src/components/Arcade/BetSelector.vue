<template>
  <div class="bet-selector glass-panel">
    <div class="bet-header">
      <span class="label">PLACE YOUR BET</span>
      <span class="chips-available">
        <i class="fas fa-coins"></i> {{ availableChips.toLocaleString() }}
      </span>
    </div>

    <div class="bet-input-zone">
      <div class="bet-display">
        <input 
          type="number" 
          v-model.number="currentBet" 
          :min="minBet" 
          :max="maxBet"
          @input="validateBet"
          class="bet-number-input"
        />
        <span class="suffix">CHIPS</span>
      </div>

      <div class="bet-slider-container">
        <input 
          type="range" 
          v-model.number="currentBet" 
          :min="minBet" 
          :max="maxBet"
          step="5000"
          class="bet-slider"
        />
        <div class="slider-labels">
          <span>5K</span>
          <span>5M</span>
          <span>10M</span>
        </div>
      </div>
    </div>

    <div class="bet-presets">
      <button 
        v-for="preset in presets" 
        :key="preset.value"
        @click="currentBet = preset.value"
        class="preset-btn"
        :class="{ active: currentBet === preset.value, 'disabled': preset.value > availableChips }"
      >
        {{ preset.label }}
      </button>
    </div>

    <div class="bet-footer">
      <button 
        @click="confirmBet" 
        class="confirm-btn"
        :disabled="currentBet > availableChips || currentBet < minBet"
      >
        CONFIRM BET ({{ currentBet.toLocaleString() }})
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  availableChips: {
    type: Number,
    required: true
  },
  minBet: {
    type: Number,
    default: 5000
  },
  maxBet: {
    type: Number,
    default: 10000000
  }
})

const emit = defineEmits(['confirm'])

const currentBet = ref(props.minBet)

const presets = [
  { label: '5K', value: 5000 },
  { label: '10K', value: 10000 },
  { label: '20K', value: 20000 },
  { label: '50K', value: 50000 },
  { label: '100K', value: 100000 },
  { label: '200K', value: 200000 },
  { label: '500K', value: 500000 },
  { label: '1M', value: 1000000 },
  { label: '2M', value: 2000000 },
  { label: '5M', value: 5000000 },
  { label: '10M', value: 10000000 }
]

const validateBet = () => {
  if (currentBet.value > props.maxBet) currentBet.value = props.maxBet
  if (currentBet.value < props.minBet) currentBet.value = props.minBet
}

const confirmBet = () => {
  emit('confirm', currentBet.value)
}

watch(() => props.availableChips, (newVal) => {
  if (currentBet.value > newVal) {
    currentBet.value = Math.max(props.minBet, newVal)
  }
})
</script>

<style scoped>
.bet-selector {
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: var(--glass-bg-secondary);
}

.bet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 800;
}

.label { color: var(--text-muted); font-size: 0.8rem; letter-spacing: 1px; }
.chips-available { color: var(--primary-color); font-size: 1.1rem; }

.bet-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(0,0,0,0.3);
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.bet-number-input {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 2rem;
  font-weight: 900;
  width: 200px;
  text-align: center;
}

.bet-number-input:focus { outline: none; }
.suffix { font-weight: 800; color: var(--text-muted); }

.bet-slider {
  width: 100%;
  height: 8px;
  -webkit-appearance: none;
  background: var(--glass-bg-primary);
  border-radius: 4px;
  margin: 1rem 0;
}

.bet-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  background: var(--primary-color);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px var(--primary-color);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 700;
}

.bet-presets {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.preset-btn {
  padding: 0.5rem;
  border-radius: 8px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover:not(.disabled) { background: var(--glass-bg-hover); transform: translateY(-2px); }
.preset-btn.active { background: var(--primary-color); color: #fff; border-color: var(--primary-color); }
.preset-btn.disabled { opacity: 0.3; cursor: not-allowed; }

.confirm-btn {
  width: 100%;
  padding: 1.2rem;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--primary-color), var(--text-secondary));
  color: #fff;
  font-weight: 900;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.confirm-btn:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
.confirm-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
