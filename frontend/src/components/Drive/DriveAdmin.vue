<template>
  <div class="drive-admin">
    <h2>📁 Drive Administration</h2>
    
    <!-- Quota Management -->
    <div class="admin-section">
      <h3>User Quotas</h3>
      <div class="quota-controls">
        <div class="quota-form">
          <input 
            v-model="quotaForm.username" 
            placeholder="Username" 
            class="form-input"
          />
          <input 
            v-model="quotaForm.additional_quota_gb" 
            type="number" 
            placeholder="Additional GB" 
            class="form-input"
          />
          <button @click="allocateQuota" class="btn btn-primary">
            Allocate Quota
          </button>
        </div>
      </div>
      
      <div class="users-list">
        <div v-if="!users || users.length === 0" class="empty-state">
          <p>Loading user quotas...</p>
        </div>
        <div v-else>
          <div v-for="user in users" :key="user.id" class="user-item">
            <div class="user-info">
              <div class="user-name">{{ user.user.username }}</div>
            </div>
            <div class="quota-info">
              <div class="quota-bar">
                <div class="quota-used" :style="{ width: user.usage_percentage + '%' }"></div>
              </div>
              <div class="quota-text">
                {{ formatBytes(user.used_space) }} / {{ formatBytes(user.total_quota + user.additional_quota) }}
                ({{ user.usage_percentage.toFixed(1) }}%)
              </div>
              <div class="quota-details">
                Base: {{ formatBytes(user.total_quota) }} + 
                Additional: {{ formatBytes(user.additional_quota) }}
              </div>
            </div>
            <div class="user-actions">
              <button @click="viewUserFiles(user.user.username)" class="btn btn-sm btn-secondary">
                📁 View Files
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- User Files Modal -->
    <div v-if="showFilesModal" class="modal-overlay" @click="showFilesModal = false">
      <div class="modal large" @click.stop>
        <h3>Files for {{ selectedUser }}</h3>
        <div v-if="userFiles.length === 0" class="empty-state">
          <p>No files found for this user.</p>
        </div>
        <div v-else class="files-grid">
          <div v-for="file in userFiles" :key="file.id" class="file-card">
            <div class="file-icon">📄</div>
            <div class="file-name">{{ file.filename }}</div>
            <div class="file-size">{{ formatBytes(file.file_size) }}</div>
            <div class="file-date">{{ formatDate(file.created_at) }}</div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showFilesModal = false" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api.js'

export default {
  name: 'DriveAdmin',
  setup() {
    const users = ref([])
    const userFiles = ref([])
    const showFilesModal = ref(false)
    const selectedUser = ref('')
    const quotaForm = ref({
      username: '',
      additional_quota_gb: ''
    })

    const loadUserQuotas = async () => {
      try {
        const response = await apiGet('/drive/admin/users')
        users.value = response?.users || []
      } catch (error) {
        console.error('Failed to load user quotas:', error)
        users.value = []  // Set empty array on error
      }
    }

    const allocateQuota = async () => {
      if (!quotaForm.value.username || !quotaForm.value.additional_quota_gb) {
        alert('Please fill in all fields')
        return
      }

      try {
        await apiPost('/drive/admin/allocate-quota', {
          username: quotaForm.value.username,
          additional_quota_gb: parseInt(quotaForm.value.additional_quota_gb)
        })
        
        alert('Quota allocated successfully!')
        quotaForm.value.username = ''
        quotaForm.value.additional_quota_gb = ''
        loadUserQuotas()
      } catch (error) {
        console.error('Failed to allocate quota:', error)
        alert('Failed to allocate quota')
      }
    }

    const viewUserFiles = async (username) => {
      try {
        const response = await apiGet(`/drive/admin/user/${username}`)
        userFiles.value = response.files
        selectedUser.value = username
        showFilesModal.value = true
      } catch (error) {
        console.error('Failed to load user files:', error)
      }
    }

    const formatBytes = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      loadUserQuotas()
    })

    return {
      users,
      userFiles,
      showFilesModal,
      selectedUser,
      quotaForm,
      loadUserQuotas,
      allocateQuota,
      viewUserFiles,
      formatBytes,
      formatDate
    }
  }
}
</script>

<style scoped>
.drive-admin {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

.drive-admin h2 {
  margin: 0 0 2rem 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.admin-section {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.admin-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.admin-section h3 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.quota-controls {
  margin-bottom: 2rem;
}

.quota-form {
  display: flex;
  gap: 1rem;
  align-items: end;
  flex-wrap: wrap;
}

.form-input {
  flex: 1;
  min-width: 200px;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input::placeholder {
  color: var(--text-tertiary);
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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

.btn-primary {
  background: var(--primary-gradient);
  color: white;
  box-shadow: var(--glass-shadow-md);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-lg);
}

.btn-secondary {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-2px);
}

.users-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.user-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.user-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.user-card:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-lg);
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.user-name {
  font-weight: 600;
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.user-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
}

.user-quota {
  margin-bottom: 1rem;
}

.quota-bar {
  width: 100%;
  height: 8px;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.quota-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(16, 185, 129, 0.8), rgba(6, 182, 212, 0.8));
  transition: width 0.3s ease;
  border-radius: 3px;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.3);
}

.quota-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-xl);
  -webkit-backdrop-filter: var(--glass-blur-xl);
  border: 1px solid var(--glass-border);
  padding: 2rem;
  border-radius: 20px;
  min-width: 400px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--glass-shadow-xl);
  position: relative;
  overflow: hidden;
}

.modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.file-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  transition: all 0.3s ease;
}

.file-card:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-1px);
}

.file-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.file-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  word-break: break-word;
}

.file-size {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.file-date {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: #666;
}
</style>
