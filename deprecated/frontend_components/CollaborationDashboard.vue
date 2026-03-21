<template>
  <div class="collaboration-dashboard">
    <div class="dashboard-header">
      <h2>🤝 Smart Collaboration Manager</h2>
      <p>Manage your content creator collaborations efficiently</p>
      
      <div class="header-actions">
        <button @click="showCreateModal = true" class="btn btn-primary">
          <i class="fas fa-plus"></i>
          New Collaboration
        </button>
        <button @click="refreshCollaborations" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-sync" :class="{ 'fa-spin': loading }"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Dashboard Stats -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <h3>Total</h3>
          <span class="stat-value">{{ stats.total_collaborations }}</span>
        </div>
        <div class="stat-card">
          <h3>Pending</h3>
          <span class="stat-value">{{ stats.pending }}</span>
        </div>
        <div class="stat-card">
          <h3>In Progress</h3>
          <span class="stat-value">{{ stats.in_progress }}</span>
        </div>
        <div class="stat-card">
          <h3>Completed</h3>
          <span class="stat-value">{{ stats.completed }}</span>
        </div>
      </div>
    </div>

    <!-- Collaborations List -->
    <div class="collaborations-section">
      <h3>Collaborations</h3>
      <div class="collaborations-grid">
        <div 
          v-for="collab in collaborations" 
          :key="collab.id"
          class="collab-card"
          @click="selectCollaboration(collab)"
        >
          <div class="collab-header">
            <h4>{{ collab.name }}</h4>
            <span class="collab-status" :class="collab.status">
              {{ formatStatus(collab.status) }}
            </span>
          </div>
          
          <div class="collab-info">
            <div class="info-row">
              <span class="label">Collaborator:</span>
              <span class="value">{{ collab.collaborator }}</span>
            </div>
            <div class="info-row">
              <span class="label">Platform:</span>
              <span class="value">{{ collab.platform }}</span>
            </div>
            <div class="info-row">
              <span class="label">Type:</span>
              <span class="value">{{ collab.type }}</span>
            </div>
            <div class="info-row">
              <span class="label">Videos:</span>
              <span class="value">{{ collab.completed_videos }}/{{ collab.total_videos }}</span>
            </div>
          </div>
          
          <div class="collab-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: collab.progress_percentage + '%' }"
              ></div>
            </div>
            <span class="progress-text">{{ collab.progress_percentage.toFixed(1) }}%</span>
          </div>
          
          <div class="collab-footer">
            <div class="deadline-info">
              <i class="fas fa-clock"></i>
              <span>{{ formatDate(collab.deadline) }}</span>
            </div>
            <div class="collab-actions">
              <button @click.stop="editCollaboration(collab)" class="btn btn-sm btn-outline">
                <i class="fas fa-edit"></i>
                Edit
              </button>
              <button @click.stop="deleteCollaboration(collab)" class="btn btn-sm btn-danger">
                <i class="fas fa-trash"></i>
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Collaboration Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New Collaboration</h3>
          <button @click="closeCreateModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Collaboration Name</label>
            <input type="text" v-model="createForm.name" class="form-control" placeholder="e.g., Summer Campaign 2024" />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Collaborator Name</label>
              <input type="text" v-model="createForm.collaborator_name" class="form-control" placeholder="Creator name" />
            </div>
            <div class="form-group">
              <label>Email</label>
              <input type="email" v-model="createForm.collaborator_email" class="form-control" placeholder="creator@example.com" />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Service Name</label>
              <input type="text" v-model="createForm.service_name" class="form-control" placeholder="e.g., YouTube Channel Review" />
            </div>
            <div class="form-group">
              <label>Type</label>
              <select v-model="createForm.type" class="form-control">
                <option value="Paid">Paid</option>
                <option value="Product">Product</option>
                <option value="Mixed">Mixed</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Platforms</label>
              <div class="platform-checkboxes">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="createForm.platforms" value="YouTube" class="form-check-input">
                  <span>YouTube</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="createForm.platforms" value="TikTok" class="form-check-input">
                  <span>TikTok</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="createForm.platforms" value="Instagram" class="form-check-input">
                  <span>Instagram</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="createForm.platforms" value="Twitter" class="form-check-input">
                  <span>Twitter</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="createForm.platforms" value="Twitch" class="form-check-input">
                  <span>Twitch</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="createForm.platforms" value="Facebook" class="form-check-input">
                  <span>Facebook</span>
                </label>
              </div>
            </div>
            <div class="form-group" v-if="createForm.type === 'Paid' || createForm.type === 'Mixed'">
              <label>Agreed Price ($)</label>
              <input type="number" v-model="createForm.agreed_price" min="0" step="0.01" class="form-control" />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Deadline</label>
              <input type="datetime-local" v-model="createForm.deadline" required class="form-control" />
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeCreateModal" class="btn btn-secondary">Cancel</button>
          <button @click="createCollaboration" class="btn btn-primary" :disabled="creating">
            <i class="fas fa-spinner fa-spin" v-if="creating"></i>
            {{ creating ? 'Creating...' : 'Create Collaboration' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { apiGet, apiPost } from '../../utils/api.js'

export default {
  name: 'CollaborationDashboard',
  setup() {
    const collaborations = ref([])
    const selectedCollaboration = ref(null)
    const stats = ref({
      total_collaborations: 0,
      pending: 0,
      in_progress: 0,
      completed: 0
    })
    const loading = ref(false)
    const showCreateModal = ref(false)
    const creating = ref(false)
    
    const createForm = ref({
      name: '',
      service_name: '',
      collaborator_name: '',
      collaborator_email: '',
      type: 'Paid',
      agreed_price: null,
      platforms: [],
      deadline: ''
    })
    
    const refreshCollaborations = async () => {
      loading.value = true
      try {
        const [collabsData, statsData] = await Promise.all([
          apiGet('/collaboration/collaborations'),
          apiGet('/collaboration/collaborations/dashboard/stats')
        ])
        
        if (collabsData && collabsData.collaborations) {
          collaborations.value = collabsData.collaborations
        }
        
        if (statsData) {
          stats.value = statsData
        }
      } catch (error) {
        console.error('Error fetching collaborations:', error)
      } finally {
        loading.value = false
      }
    }
    
    const createCollaboration = async () => {
      creating.value = true
      try {
        const formData = { ...createForm.value }
        if (formData.deadline) {
          formData.deadline = new Date(formData.deadline).toISOString()
        }
        
        const response = await apiPost('/collaboration/collaborations', formData)
        if (response) {
          alert('Collaboration created successfully!')
          closeCreateModal()
          refreshCollaborations()
        }
      } catch (error) {
        console.error('Error creating collaboration:', error)
        alert('Failed to create collaboration')
      } finally {
        creating.value = false
      }
    }
    
    const closeCreateModal = () => {
      showCreateModal.value = false
      createForm.value = {
        name: '',
        service_name: '',
        collaborator_name: '',
        collaborator_email: '',
        type: 'Paid',
        agreed_price: null,
        platforms: [],
        deadline: ''
      }
    }
    
    const formatStatus = (status) => {
      return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
    
    const deleteCollaboration = async (collab) => {
      if (!confirm(`Are you sure you want to delete "${collab.name}"?`)) {
        return
      }
      
      try {
        const response = await apiPost(`/collaboration/collaborations/${collab.id}/delete`)
        if (response) {
          alert('Collaboration deleted successfully!')
          refreshCollaborations()
        }
      } catch (error) {
        console.error('Error deleting collaboration:', error)
        alert('Failed to delete collaboration')
      }
    }
    
    const editCollaboration = (collab) => {
      // TODO: Implement edit modal
      alert('Edit functionality coming soon!')
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'Not set'
      return new Date(dateString).toLocaleDateString()
    }
    
    const selectCollaboration = (collab) => {
      selectedCollaboration.value = collab
    }
    
    onMounted(() => {
      refreshCollaborations()
    })
    
    return {
      collaborations,
      selectedCollaboration,
      stats,
      loading,
      showCreateModal,
      creating,
      createForm,
      refreshCollaborations,
      createCollaboration,
      closeCreateModal,
      formatDate,
      deleteCollaboration,
      editCollaboration,
      selectCollaboration
    }
  }
}
</script>

<style scoped>
.collaboration-dashboard {
  padding: 2rem;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h2 {
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.dashboard-header p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  border: 1px solid var(--border-color);
}

.stat-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
}

.collaborations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.collab-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.collab-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.collab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.collab-header h4 {
  margin: 0;
  color: var(--text-primary);
}

.collab-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.collab-status.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.collab-status.in_progress {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.collab-status.completed {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.info-row .label {
  color: var(--text-secondary);
}

.info-row .value {
  color: var(--text-primary);
  font-weight: 500;
}

.collab-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 45px;
}

.collab-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.deadline-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--text-secondary);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-primary);
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.platform-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.checkbox-label:hover {
  background: var(--bg-tertiary);
}

.form-check-input {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.checkbox-label span {
  color: var(--text-primary);
  font-size: 0.9rem;
}

:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --primary-color: #3b82f6;
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] {
  --bg-primary: #1e293b;
  --bg-secondary: #334155;
  --bg-tertiary: #475569;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --border-color: #475569;
  --primary-color: #3b82f6;
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
}
</style>
