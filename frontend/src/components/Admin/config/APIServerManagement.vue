<template>
  <div class="api-server-management">
    <div class="section-header">
      <h2>🌐 API Server Management</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        ➕ Add Server
      </button>
    </div>

    <!-- API Servers List -->
    <div class="servers-list">
      <div v-for="server in servers" :key="server.id" class="server-card">
        <div class="server-header">
          <h3>{{ server.display_name }}</h3>
          <div class="server-badges">
            <span v-if="server.is_default" class="badge badge-primary">Default</span>
            <span :class="['badge', server.is_active ? 'badge-success' : 'badge-secondary']">
              {{ server.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
        
        <div class="server-info">
          <div class="info-row">
            <label>Name:</label>
            <span>{{ server.name }}</span>
          </div>
          <div class="info-row">
            <label>Base URL:</label>
            <span class="url">{{ server.base_url }}</span>
          </div>
          <div class="info-row">
            <label>API Version:</label>
            <span>{{ server.api_version }}</span>
          </div>
          <div class="info-row">
            <label>Services:</label>
            <span>{{ server.supports_services.join(', ') }}</span>
          </div>
          <div class="info-row">
            <label>Priority:</label>
            <span>{{ server.priority }}</span>
          </div>
          <div v-if="server.description" class="info-row">
            <label>Description:</label>
            <span>{{ server.description }}</span>
          </div>
        </div>
        
        <div class="server-actions">
          <button @click="editServer(server)" class="btn btn-secondary">
            ✏️ Edit
          </button>
          <button @click="deleteServer(server)" class="btn btn-danger">
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingServer" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingServer ? 'Edit API Server' : 'Add API Server' }}</h3>
          <button @click="closeModal" class="btn-close">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Server Name *</label>
            <input v-model="serverForm.name" type="text" class="form-control" 
                   placeholder="e.g., primary_api" required>
          </div>
          
          <div class="form-group">
            <label>Display Name *</label>
            <input v-model="serverForm.display_name" type="text" class="form-control" 
                   placeholder="e.g., Primary API Server" required>
          </div>
          
          <div class="form-group">
            <label>Base URL *</label>
            <input v-model="serverForm.base_url" type="url" class="form-control" 
                   placeholder="https://api.example.com" required>
          </div>
          
          <div class="form-group">
            <label>API Version</label>
            <select v-model="serverForm.api_version" class="form-control">
              <option value="v1">v1</option>
              <option value="v2">v2</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Supported Services</label>
            <input v-model="serverForm.supports_services" type="text" class="form-control" 
                   placeholder="views,likes,comments">
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="serverForm.description" class="form-control" 
                      placeholder="Optional description"></textarea>
          </div>
          
          <div class="form-group">
            <label>Priority</label>
            <input v-model="serverForm.priority" type="number" class="form-control" 
                   min="1" max="100">
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="serverForm.is_active" type="checkbox">
              Active
            </label>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="serverForm.is_default" type="checkbox">
              Default Server
            </label>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button @click="saveServer" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.api-server-management {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.section-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.section-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
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

.btn-danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.8), rgba(220, 53, 69, 0.8));
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-lg);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.servers-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.server-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.server-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.server-card:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-lg);
}

.server-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.server-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.server-badges {
  display: flex;
  gap: 0.5rem;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-primary {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.badge-success {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.badge-secondary {
  background: rgba(107, 114, 128, 0.2);
  color: #6b7280;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.server-info {
  margin-bottom: 1.5rem;
}

.info-row {
  display: flex;
  margin-bottom: 0.75rem;
  align-items: center;
}

.info-row label {
  font-weight: 600;
  min-width: 120px;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.info-row span {
  color: var(--text-primary);
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.info-row span.url {
  font-family: monospace;
  background: var(--glass-bg-tertiary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  word-break: break-all;
}

.server-actions {
  display: flex;
  gap: 0.75rem;
}

/* Modal styles */
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
  z-index: 9999;
  padding: 1rem;
}

.modal-content {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-xl);
  -webkit-backdrop-filter: var(--glass-blur-xl);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--glass-shadow-xl);
  position: relative;
}

.modal-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.3rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.btn-close {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.btn-close:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: scale(1.1);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-control::placeholder {
  color: var(--text-tertiary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.form-control option {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  padding: 0.5rem;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

<script>
import { ref, reactive, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '../../../utils/api.js'
import { showSuccess, showError, showConfirm } from '../../../utils/notifications.js'

export default {
  name: 'APIServerManagement',
  
  setup() {
    const servers = ref([])
    const loading = ref(false)
    const showCreateModal = ref(false)
    const editingServer = ref(null)
    const saving = ref(false)
    
    const serverForm = reactive({
      name: '',
      display_name: '',
      base_url: '',
      api_version: 'v2',
      supports_services: 'views,likes,comments',
      description: '',
      priority: 1,
      is_active: true,
      is_default: false
    })
    
    const loadServers = async () => {
      loading.value = true
      try {
        const response = await apiGet('/api-management/servers')
        servers.value = response.servers || []
      } catch (error) {
        showError('Failed to load API servers: ' + error.message)
      } finally {
        loading.value = false
      }
    }
    
    const editServer = (server) => {
      editingServer.value = server
      Object.assign(serverForm, {
        name: server.name,
        display_name: server.display_name,
        base_url: server.base_url,
        api_version: server.api_version,
        supports_services: server.supports_services.join(','),
        description: server.description || '',
        priority: server.priority,
        is_active: server.is_active,
        is_default: server.is_default
      })
    }
    
    const saveServer = async () => {
      saving.value = true
      try {
        if (editingServer.value) {
          await apiPut(`/api-management/servers/${editingServer.value.id}`, serverForm)
          showSuccess('API server updated successfully!')
        } else {
          await apiPost('/api-management/servers', serverForm)
          showSuccess('API server created successfully!')
        }
        
        closeModal()
        await loadServers()
      } catch (error) {
        showError('Failed to save API server: ' + error.message)
      } finally {
        saving.value = false
      }
    }
    
    const deleteServer = async (server) => {
      const confirmed = await showConfirm(
        `Are you sure you want to delete "${server.display_name}"?`,
        'Delete Server',
        'Cancel'
      )
      
      if (!confirmed) return
      
      try {
        await apiDelete(`/api-management/servers/${server.id}`)
        showSuccess('API server deleted successfully!')
        await loadServers()
      } catch (error) {
        showError('Failed to delete API server: ' + error.message)
      }
    }
    
    const closeModal = () => {
      showCreateModal.value = false
      editingServer.value = null
      
      // Reset form
      Object.assign(serverForm, {
        name: '',
        display_name: '',
        base_url: '',
        api_version: 'v2',
        supports_services: 'views,likes,comments',
        description: '',
        priority: 1,
        is_active: true,
        is_default: false
      })
    }
    
    onMounted(() => {
      loadServers()
    })
    
    return {
      servers,
      loading,
      showCreateModal,
      editingServer,
      saving,
      serverForm,
      loadServers,
      editServer,
      saveServer,
      deleteServer,
      closeModal
    }
  }
}
</script>
