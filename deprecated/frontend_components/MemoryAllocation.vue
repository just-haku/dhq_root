<template>
  <div class="memory-allocation">
    <div class="allocation-header">
      <h2>
        <i class="fas fa-memory"></i>
        Memory Allocation Management
      </h2>
      <p class="subtitle">Manage user storage quotas and permissions</p>
    </div>

    <!-- Allocation Form -->
    <div class="allocation-form">
      <h3>Allocate Memory to User</h3>
      <form @submit.prevent="allocateMemory">
        <div class="form-grid">
          <div class="form-group">
            <label>Username</label>
            <input 
              v-model="allocationForm.username" 
              type="text" 
              placeholder="Enter username"
              required
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label>Drive Quota (GB)</label>
            <input 
              v-model.number="allocationForm.drive_quota_gb" 
              type="number" 
              min="0" 
              step="1"
              placeholder="5"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label>Vault Quota (GB)</label>
            <input 
              v-model.number="allocationForm.vault_quota_gb" 
              type="number" 
              min="0" 
              step="1"
              placeholder="0 (unlimited for OP)"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label>Max File Size (MB)</label>
            <input 
              v-model.number="allocationForm.max_file_size_mb" 
              type="number" 
              min="1" 
              step="1"
              placeholder="100"
              class="form-input"
            />
          </div>
        </div>
        
        <div class="permissions-grid">
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="allocationForm.can_upload_large_files" 
                type="checkbox"
              />
              Can upload large files (>100MB)
            </label>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="allocationForm.can_access_vault" 
                type="checkbox"
              />
              Can access Vault
            </label>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="allocationForm.can_manage_shop" 
                type="checkbox"
              />
              Can manage Shop
            </label>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="allocationForm.can_view_all_drives" 
                type="checkbox"
              />
              Can view all drives
            </label>
          </div>
        </div>
        
        <div class="form-group">
          <label>Notes</label>
          <textarea 
            v-model="allocationForm.notes" 
            placeholder="Reason for allocation..."
            rows="3"
            class="form-textarea"
          ></textarea>
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <i class="fas fa-save"></i>
          Allocate Memory
        </button>
      </form>
    </div>

    <!-- Current Allocations -->
    <div class="allocations-list">
      <h3>Current Allocations</h3>
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        Loading allocations...
      </div>
      
      <div v-else-if="allocations.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        No allocations found
      </div>
      
      <div v-else class="allocations-grid">
        <div 
          v-for="allocation in allocations" 
          :key="allocation.id"
          class="allocation-card"
        >
          <div class="allocation-header">
            <h4>{{ allocation.user.display_name || allocation.user.username }}</h4>
            <span class="username">@{{ allocation.user.username }}</span>
          </div>
          
          <div class="allocation-details">
            <div class="detail-item">
              <span class="label">Drive Quota:</span>
              <span class="value">{{ formatFileSize(allocation.drive_quota) }}</span>
            </div>
            
            <div class="detail-item">
              <span class="label">Vault Quota:</span>
              <span class="value">{{ allocation.vault_quota > 0 ? formatFileSize(allocation.vault_quota) : 'Unlimited' }}</span>
            </div>
            
            <div class="detail-item">
              <span class="label">Max File Size:</span>
              <span class="value">{{ formatFileSize(allocation.max_file_size) }}</span>
            </div>
            
            <div class="detail-item">
              <span class="label">Drive Usage:</span>
              <div class="usage-bar">
                <div 
                  class="usage-fill" 
                  :style="{ width: allocation.drive_usage_percentage + '%' }"
                ></div>
                <span class="usage-text">{{ allocation.drive_usage_percentage.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
          
          <div class="permissions">
            <span 
              v-if="allocation.can_upload_large_files" 
              class="permission-badge"
              title="Can upload large files"
            >
              <i class="fas fa-file-upload"></i>
            </span>
            <span 
              v-if="allocation.can_access_vault" 
              class="permission-badge"
              title="Can access Vault"
            >
              <i class="fas fa-shield-alt"></i>
            </span>
            <span 
              v-if="allocation.can_manage_shop" 
              class="permission-badge"
              title="Can manage Shop"
            >
              <i class="fas fa-store"></i>
            </span>
            <span 
              v-if="allocation.can_view_all_drives" 
              class="permission-badge"
              title="Can view all drives"
            >
              <i class="fas fa-eye"></i>
            </span>
          </div>
          
          <div class="allocation-footer">
            <small>Allocated by {{ allocation.allocated_by.username }}</small>
            <small>{{ formatDate(allocation.allocation_date) }}</small>
          </div>
          
          <button 
            @click="viewHistory(allocation.user.username)"
            class="btn btn-sm btn-outline"
          >
            <i class="fas fa-history"></i>
            History
          </button>
        </div>
      </div>
    </div>

    <!-- History Modal -->
    <div v-if="showHistoryModal" class="modal-overlay" @click="closeHistoryModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Allocation History - {{ historyUser }}</h3>
          <button @click="closeHistoryModal" class="btn btn-icon">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="historyLoading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            Loading history...
          </div>
          
          <div v-else-if="history.length === 0" class="empty-state">
            <i class="fas fa-history"></i>
            No history found
          </div>
          
          <div v-else class="history-list">
            <div 
              v-for="item in history" 
              :key="item.change_date"
              class="history-item"
            >
              <div class="history-header">
                <span class="field-name">{{ formatFieldName(item.field_name) }}</span>
                <span class="change-date">{{ formatDate(item.change_date) }}</span>
              </div>
              
              <div class="history-details">
                <div class="value-change">
                  <span class="old-value">{{ formatValue(item.field_name, item.old_value) }}</span>
                  <i class="fas fa-arrow-right"></i>
                  <span class="new-value">{{ formatValue(item.field_name, item.new_value) }}</span>
                </div>
                
                <div class="changed-by">
                  by {{ item.changed_by.display_name || item.changed_by.username }}
                </div>
                
                <div v-if="item.reason" class="reason">
                  {{ item.reason }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { apiGet, apiPost } from '../../utils/api.js'

export default {
  name: 'MemoryAllocation',
  
  setup() {
    const loading = ref(false)
    const allocations = ref([])
    const showHistoryModal = ref(false)
    const historyUser = ref('')
    const history = ref([])
    const historyLoading = ref(false)
    
    const allocationForm = ref({
      username: '',
      drive_quota_gb: null,
      vault_quota_gb: null,
      max_file_size_mb: null,
      can_upload_large_files: false,
      can_access_vault: false,
      can_manage_shop: false,
      can_view_all_drives: false,
      notes: ''
    })
    
    const loadAllocations = async () => {
      loading.value = true
      try {
        const response = await apiGet('/api-management/user-keys')
        allocations.value = response.keys || []
      } catch (error) {
        console.error('Failed to load allocations:', error)
      } finally {
        loading.value = false
      }
    }
    
    const allocateMemory = async () => {
      loading.value = true
      try {
        await apiPost('/user-management/memory-allocate', allocationForm.value)
        
        // Reset form
        allocationForm.value = {
          username: '',
          drive_quota_gb: null,
          vault_quota_gb: null,
          max_file_size_mb: null,
          can_upload_large_files: false,
          can_access_vault: false,
          can_manage_shop: false,
          can_view_all_drives: false,
          notes: ''
        }
        
        // Reload allocations
        await loadAllocations()
        
        alert('Memory allocated successfully!')
      } catch (error) {
        console.error('Failed to allocate memory:', error)
        alert('Failed to allocate memory: ' + (error.response?.data?.detail || error.message))
      } finally {
        loading.value = false
      }
    }
    
    const viewHistory = async (username) => {
      historyUser.value = username
      showHistoryModal.value = true
      historyLoading.value = true
      
      try {
        const response = await apiGet(`/user-management/memory-history/${username}`)
        history.value = response.history
      } catch (error) {
        console.error('Failed to load history:', error)
        history.value = []
      } finally {
        historyLoading.value = false
      }
    }
    
    const closeHistoryModal = () => {
      showHistoryModal.value = false
      historyUser.value = ''
      history.value = []
    }
    
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString() + ' ' + 
             new Date(dateString).toLocaleTimeString()
    }
    
    const formatFieldName = (fieldName) => {
      return fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
    
    const formatValue = (fieldName, value) => {
      if (fieldName.includes('quota') || fieldName.includes('file_size')) {
        return formatFileSize(value)
      }
      if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No'
      }
      return value
    }
    
    onMounted(() => {
      loadAllocations()
    })
    
    return {
      loading,
      allocations,
      allocationForm,
      showHistoryModal,
      historyUser,
      history,
      historyLoading,
      allocateMemory,
      viewHistory,
      closeHistoryModal,
      formatFileSize,
      formatDate,
      formatFieldName,
      formatValue
    }
  }
}
</script>

<style scoped>
.memory-allocation {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

.allocation-header {
  margin-bottom: 2rem;
  text-align: center;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.allocation-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.allocation-header h2 {
  color: var(--text-primary);
  margin-bottom: 1rem;
  font-size: 1.8rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.allocation-form {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.allocation-form::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.allocation-form h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  font-size: 1.3rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.checkbox-label {
  flex-direction: row;
  align-items: center;
  cursor: pointer;
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.checkbox-label input {
  margin-right: 0.5rem;
}

.form-input, .form-textarea {
  padding: 0.75rem 1rem;
  background: var(--glass-bg-tertiary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input::placeholder, .form-textarea::placeholder {
  color: var(--text-tertiary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-md);
}

.btn-primary {
  background: var(--primary-gradient);
  border-color: var(--primary-color);
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.btn-primary:hover {
  background: var(--primary-gradient);
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-lg);
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.btn-outline {
  background: transparent;
  color: #3498db;
  border: 1px solid #3498db;
  border-radius: 12px;
  border: 2px solid #3498db;
}

.btn-outline:hover {
  background: #3498db;
  color: white;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-icon {
  padding: 8px;
  background: transparent;
  border: none;
  color: #7f8c8d;
  cursor: pointer;
}

.btn-icon:hover {
  color: #2c3e50;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.allocations-list h3 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.allocations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.allocation-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e1e8ed;
}

.allocation-header h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.username {
  color: #7f8c8d;
  font-size: 12px;
}

.allocation-details {
  margin: 15px 0;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-item .label {
  font-weight: 500;
  color: #2c3e50;
}

.detail-item .value {
  color: #34495e;
}

.usage-bar {
  position: relative;
  width: 100px;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
}

.usage-fill {
  height: 100%;
  background: linear-gradient(90deg, #27ae60, #f39c12, #e74c3c);
  transition: width 0.3s;
}

.usage-text {
  position: absolute;
  top: -20px;
  right: 0;
  font-size: 10px;
  color: #7f8c8d;
}

.permissions {
  display: flex;
  gap: 8px;
  margin: 15px 0;
}

.permission-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #3498db;
  color: white;
  border-radius: 50%;
  font-size: 10px;
}

.allocation-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ecf0f1;
}

.allocation-footer small {
  color: #7f8c8d;
  font-size: 11px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #3498db;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.field-name {
  font-weight: 600;
  color: #2c3e50;
}

.change-date {
  font-size: 12px;
  color: #7f8c8d;
}

.history-details {
  font-size: 14px;
}

.value-change {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.old-value {
  color: #e74c3c;
}

.new-value {
  color: #27ae60;
}

.changed-by {
  color: #7f8c8d;
  font-size: 12px;
  margin-bottom: 5px;
}

.reason {
  color: #34495e;
  font-style: italic;
}
</style>
