<template>
  <div class="panic-mode-container">
    <div class="glass-panel alert-panel">
      <div class="alert-header">
        <i class="fas fa-exclamation-triangle pulse-icon"></i>
        <h1>EMERGENCY LOCKDOWN PROTOCOL</h1>
      </div>
      
      <div class="alert-body">
        <p class="warning-text">
          <strong>WARNING:</strong> Engaging Panic Mode will:
        </p>
        <ul class="consequences-list">
          <li>Instantly terminate all active user sessions across the server.</li>
          <li>Engage a server-wide Maintenance Mode block for 24 hours.</li>
          <li>Revoke <strong>ALL</strong> public "Anyone with link" file sharing URLs.</li>
          <li>Force all shared Drive files to require a registered account ("Internal" access only).</li>
        </ul>
        
        <div class="action-section">
          <p>Please type <strong>LOCKDOWN</strong> below to confirm.</p>
          <input 
            type="text" 
            v-model="confirmationText" 
            placeholder="Type LOCKDOWN" 
            class="confirmation-input"
            :disabled="isProcessing"
          />
          
          <button 
            @click="triggerPanic" 
            class="btn-danger panic-button"
            :disabled="confirmationText !== 'LOCKDOWN' || isProcessing"
          >
            <span v-if="!isProcessing"><i class="fas fa-radiation"></i> INITIATE PANIC MODE</span>
            <span v-else><i class="fas fa-spinner fa-spin"></i> Executing Lockdown...</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { apiPost } from '@/utils/api'
import { showError, showSuccess } from '@/utils/notification'

const confirmationText = ref('')
const isProcessing = ref(false)

const triggerPanic = async () => {
  if (confirmationText.value !== 'LOCKDOWN') return
  
  try {
    isProcessing.value = true
    const res = await apiPost('/admin/panic', { password: "admin" }) // Placeholder struct, actual route doesn't require body
    showError('PANIC MODE ACTIVATED. All systems locked down.', {
      timeout: 10000,
      icon: 'fas fa-radiation'
    })
    confirmationText.value = ''
  } catch (err) {
    showError('Failed to initiate panic protocol: ' + (err.response?.data?.detail || err.message))
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.panic-mode-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 100px);
  padding: 2rem;
}

.alert-panel {
  background: rgba(30, 10, 10, 0.85); /* Deep red tint */
  border: 1px solid #ef4444;
  box-shadow: 0 0 30px rgba(239, 68, 68, 0.2);
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  overflow: hidden;
}

.alert-header {
  background: #ef4444;
  color: white;
  padding: 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.alert-header h1 {
  margin: 0;
  font-size: 1.5rem;
  letter-spacing: 2px;
  font-weight: 800;
}

.pulse-icon {
  font-size: 3rem;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}

.alert-body {
  padding: 2rem;
}

.warning-text {
  color: #fca5a5;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.consequences-list {
  color: white;
  margin-bottom: 2rem;
  padding-left: 1.5rem;
}

.consequences-list li {
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.action-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2rem;
  border-top: 1px solid rgba(239, 68, 68, 0.3);
  padding-top: 2rem;
}

.confirmation-input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #ef4444;
  color: white;
  padding: 0.75rem;
  border-radius: 6px;
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
  letter-spacing: 2px;
  outline: none;
}

.confirmation-input:focus {
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

.panic-button {
  background: #dc2626;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 6px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
}

.panic-button:disabled {
  background: #7f1d1d;
  color: #fca5a5;
  cursor: not-allowed;
  opacity: 0.7;
}

.panic-button:not(:disabled):hover {
  background: #ef4444;
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
  transform: translateY(-2px);
}
</style>
