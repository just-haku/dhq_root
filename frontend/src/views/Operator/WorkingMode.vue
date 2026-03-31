<template>
  <div class="working-mode-container">
    <div class="header">
      <h1 class="title"><i class="fas fa-bolt text-yellow-400"></i> Working Mode</h1>
      <p class="subtitle">Configure system-wide power saver mode constraints and behavior</p>
    </div>

    <div class="content-grid">
      <!-- Master Toggle -->
      <div class="glass-panel main-panel">
        <div class="panel-header">
          <h2><i class="fas fa-power-off"></i> Master Power Switch</h2>
        </div>
        <div class="panel-body flex-center">
          <div class="master-toggle" :class="{ 'power-saver': systemStore.powerMode === 'power_saver' }">
            <div class="status-indicator">
              <i v-if="systemStore.powerMode === 'normal'" class="fas fa-check-circle text-green-400 text-4xl"></i>
              <i v-else class="fas fa-exclamation-triangle text-yellow-400 text-4xl"></i>
            </div>
            <div class="status-details">
              <h3>{{ systemStore.powerMode === 'normal' ? 'Normal Operations' : 'Power Saver Active' }}</h3>
              <p>{{ systemStore.powerMode === 'normal' ? 'All systems nominal.' : 'The system is currently running under power restrictions.' }}</p>
            </div>
            <button 
              class="btn-primary" 
              @click="toggleMasterMode"
              :disabled="isSaving"
            >
              {{ systemStore.powerMode === 'normal' ? 'Engage Power Saver' : 'Restore Normal Mode' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Granular Settings -->
      <div class="glass-panel settings-panel">
        <div class="panel-header">
          <h2><i class="fas fa-sliders-h"></i> Power Saver Constraints</h2>
          <p class="text-xs text-gray-400 mt-1">These settings dictate which features are suspended when Power Saver is active.</p>
        </div>
        <div class="panel-body">
          <div class="setting-row">
            <div class="setting-info">
              <h4><i class="fas fa-brain text-purple-400"></i> Disable Heavy AI Models</h4>
              <p>Force local LLMs to fallback to DeepSeek-R1:1.5B inside the Convo Hub.</p>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.ps_disable_ai" @change="saveSettings" :disabled="isSaving">
              <span class="slider round"></span>
            </label>
          </div>

          <div class="setting-row">
            <div class="setting-info">
              <h4><i class="fas fa-hdd text-blue-400"></i> Disable Drive Uploads</h4>
              <p>Prevent users from uploading new files to the storage cluster. Active uploads will finish.</p>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.ps_disable_uploads" @change="saveSettings" :disabled="isSaving">
              <span class="slider round"></span>
            </label>
          </div>

          <div class="setting-row">
            <div class="setting-info">
              <h4><i class="fas fa-drafting-compass text-orange-400"></i> Disable G-Code Generator</h4>
              <p>Suspend the computational processes powering the SVG to G-Code generator utility.</p>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.ps_disable_gcode" @change="saveSettings" :disabled="isSaving">
              <span class="slider round"></span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useSystemStore } from '@/stores/systemStore'
import { showSuccess, showError } from '@/utils/notification'

const systemStore = useSystemStore()
const isSaving = ref(false)

const settings = ref({
  ps_disable_ai: true,
  ps_disable_uploads: true,
  ps_disable_gcode: true
})

onMounted(() => {
  // Sync local ref with store
  settings.value.ps_disable_ai = systemStore.psDisableAi
  settings.value.ps_disable_uploads = systemStore.psDisableUploads
  settings.value.ps_disable_gcode = systemStore.psDisableGcode
})

// Listen to external store updates
watch(() => [systemStore.psDisableAi, systemStore.psDisableUploads, systemStore.psDisableGcode], ([ai, up, gc]) => {
  settings.value.ps_disable_ai = ai
  settings.value.ps_disable_uploads = up
  settings.value.ps_disable_gcode = gc
})

const toggleMasterMode = async () => {
  try {
    isSaving.value = true
    const newMode = systemStore.powerMode === 'normal' ? 'power_saver' : 'normal'
    await systemStore.setPowerMode(newMode)
    showSuccess(`System is now operating in ${newMode} mode.`)
  } catch (err) {
    showError('Failed to change master power mode.')
  } finally {
    isSaving.value = false
  }
}

const saveSettings = async () => {
  try {
    isSaving.value = true
    await systemStore.updateFeatures(settings.value)
    showSuccess('Power constraints updated successfully.')
  } catch (err) {
    showError('Failed to save power constraints.')
    // Revert local state visually
    settings.value.ps_disable_ai = systemStore.psDisableAi
    settings.value.ps_disable_uploads = systemStore.psDisableUploads
    settings.value.ps_disable_gcode = systemStore.psDisableGcode
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.working-mode-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.title {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.subtitle {
  color: #94a3b8;
  margin-bottom: 2rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.glass-panel {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.panel-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
}

.panel-header h2 {
  font-size: 1.25rem;
  margin: 0;
}

.master-toggle {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1.5rem;
  padding: 2rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 12px;
  width: 100%;
}

.master-toggle.power-saver {
  border: 1px solid rgba(250, 204, 21, 0.3);
  background: rgba(250, 204, 21, 0.05);
}

.status-details h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.status-details p {
  color: #94a3b8;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.setting-row:last-child {
  margin-bottom: 0;
}

.setting-info h4 {
  margin: 0 0 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.setting-info p {
  margin: 0;
  font-size: 0.875rem;
  color: #94a3b8;
}

/* Custom Switch CSS */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input { 
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #334155;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}

input:checked + .slider {
  background-color: #3b82f6;
}

input:focus + .slider {
  box-shadow: 0 0 1px #3b82f6;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
