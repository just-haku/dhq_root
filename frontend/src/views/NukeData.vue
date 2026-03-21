<template>
  <div class="nuke-data-view">
    <div class="glass-panel warning-container text-center p-12 mt-12 w-full max-w-3xl mx-auto border-2 border-danger-color">
      <div class="warning-icon mb-6">
        <i class="fas fa-biohazard text-6xl text-danger-color animate-pulse"></i>
      </div>
      
      <h2 class="text-4xl font-black text-danger-color mb-4 tracking-wider">CRITICAL OPERATIONS</h2>
      <p class="text-text-secondary text-lg mb-8 max-w-xl mx-auto">
        WARNING: Executing the Nuke Protocol will permanently wipe all system data.
        This includes all Drive Files, Tasks, Collaborations, Orders, and physically delete all target partitions. This action CANNOT be undone.
      </p>
      
      <div class="auth-box glass-panel-inner p-6 mb-8 mt-8 text-left bg-black/20">
        
        <label class="block text-sm font-bold mb-2 uppercase tracking-wide text-danger-color">Target Module</label>
        <select v-model="target" class="form-control w-full bg-black/40 border-danger-color hover:border-red-400 focus:border-red-500 text-white mb-4">
          <option value="ENTIRE_SERVER">ENTIRE SERVER (All Data & Users)</option>
          <option value="USERS">USERS ONLY</option>
          <option value="DRIVE">DRIVE ONLY</option>
          <option value="COLLABORATION">COLLABORATION ONLY</option>
          <option value="ORDER">ORDERS ONLY</option>
        </select>

        <div v-if="target === 'DRIVE'" class="mb-4">
          <label class="block text-sm font-bold mb-2 uppercase tracking-wide text-danger-color">Target User (Optional)</label>
          <input 
            v-model="targetUser" 
            type="text" 
            class="form-control w-full bg-black/40 border-danger-color hover:border-red-400 focus:border-red-500 text-white placeholder-gray-500" 
            placeholder="Username (leave blank for all users)"
          />
        </div>

        <label class="block text-sm font-bold mb-2 uppercase tracking-wide text-danger-color">Development Key Required</label>
        <input 
          v-model="nukeKey" 
          type="password" 
          class="form-control w-full bg-black/40 border-danger-color hover:border-red-400 focus:border-red-500 text-white placeholder-gray-500 mb-4" 
          placeholder="Enter DEV_KEY"
          @keyup.enter="triggerNuke"
        />
        <label class="block text-sm font-bold mb-2 uppercase tracking-wide text-danger-color">Confirmation Phrase</label>
        <input 
          v-model="confirmation" 
          type="text" 
          class="form-control w-full bg-black/40 border-danger-color hover:border-red-400 focus:border-red-500 text-white placeholder-gray-500" 
          placeholder="Type 'NUKE_SYSTEM' to confirm"
          @keyup.enter="triggerNuke"
        />
      </div>

      <button 
        @click="triggerNuke" 
        class="btn w-full py-4 text-xl font-bold rounded flex items-center justify-center gap-3 transition-all"
        :class="isFormValid ? 'btn-nuke bg-red-600 hover:bg-red-500 text-white shadow-[0_0_20px_rgba(220,38,38,0.7)]' : 'bg-gray-700 text-gray-400 cursor-not-allowed'"
        :disabled="!isFormValid || loading"
      >
        <i class="fas fa-bomb" :class="{ 'fa-spin': loading }"></i> 
        {{ loading ? 'INITIATING SYSTEM WIPE...' : 'EXECUTE NUKE PROTOCOL' }}
      </button>

      <div v-if="successMessage" class="mt-6 p-4 rounded bg-green-900/50 border border-green-500 text-green-300 font-bold">
        <i class="fas fa-check-circle mr-2"></i> {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="mt-6 p-4 rounded bg-red-900/50 border border-red-500 text-red-300 font-bold">
        <i class="fas fa-exclamation-triangle mr-2"></i> {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { apiPost } from '@/utils/api'

const nukeKey = ref('')
const confirmation = ref('')
const target = ref('ENTIRE_SERVER')
const targetUser = ref('')
const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const isFormValid = computed(() => {
  return nukeKey.value.length > 0 && confirmation.value === 'NUKE_SYSTEM'
})

const triggerNuke = async () => {
  if (!isFormValid.value) return
  
  const ok = confirm(`Are you ABSOLUTELY SURE you wish to wipe the ${target.value} data? This is irreversible.`)
  if (!ok) return

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const res = await apiPost('/admin/nuke-data', {
      dev_key: nukeKey.value,
      confirmation: confirmation.value,
      target: target.value,
      target_user: target.value === 'DRIVE' && targetUser.value ? targetUser.value : null
    })
    
    successMessage.value = res.message || "System wipe executed successfully."
    nukeKey.value = ''
    confirmation.value = ''
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      errorMessage.value = err.response.data.detail
    } else {
      errorMessage.value = err.message || "An error occurred executing the Nuke sequence."
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.nuke-data-view {
  min-height: calc(100vh - 120px);
  padding-bottom: 50px;
}
.border-danger-color {
  border-color: #ef4444;
}
.text-danger-color {
  color: #ef4444;
}
.btn-nuke {
  text-transform: uppercase;
  letter-spacing: 2px;
}
</style>
