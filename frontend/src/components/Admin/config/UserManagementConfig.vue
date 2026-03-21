<template>
  <div class="user-management-config">
    <div class="section-header">
      <h3>👥 User Management Configuration</h3>
      <button @click="showCreateModal = true" class="btn btn-primary" :disabled="loading">
        <i class="fas fa-plus"></i> Create User
      </button>
    </div>

    <div class="user-controls">
      <button @click="loadUsers" class="btn btn-secondary" :disabled="loading">
        <i class="fas fa-refresh"></i> Refresh
      </button>
      <div class="filter-controls">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search users..." 
          class="search-input"
        />
        <select v-model="roleFilter" class="filter-select">
          <option value="">All Roles</option>
          <option value="OP">OP</option>
          <option value="ADMIN">Admin</option>
          <option value="USER">User</option>
        </select>
      </div>
    </div>
    
    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Display Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>KPI</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.display_name || 'N/A' }}</td>
            <td>{{ user.email || 'N/A' }}</td>
            <td>
              <span class="role-badge" :class="user.role.toLowerCase()">
                {{ user.role }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="user.status.toLowerCase()">
                {{ user.status }}
              </span>
            </td>
            <td>{{ user.kpi_current || 0 }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <button @click="editUser(user)" class="btn btn-sm btn-secondary">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="adjustKPI(user)" class="btn btn-sm btn-outline">
                <i class="fas fa-coins"></i>
              </button>
              <button 
                v-if="user.role !== 'OP'" 
                @click="deleteUser(user)" 
                class="btn btn-sm btn-danger"
              >
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="filteredUsers.length === 0 && !loading" class="empty-state">
        <i class="fas fa-users"></i>
        <p>No users found</p>
      </div>
    </div>

    <!-- Create/Edit User Modal -->
    <div v-if="showCreateModal || editingUser" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingUser ? 'Edit User' : 'Create User' }}</h3>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="saveUser" class="user-form">
          <div class="form-row">
            <div class="form-group">
              <label>Username *</label>
              <input 
                v-model="formData.username" 
                type="text" 
                required 
                class="form-control"
                :disabled="!!editingUser"
              />
            </div>
            <div class="form-group">
              <label>Display Name</label>
              <input 
                v-model="formData.display_name" 
                type="text" 
                class="form-control"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Email</label>
              <input 
                v-model="formData.email" 
                type="email" 
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>Role *</label>
              <select v-model="formData.role" class="form-control" required>
                <option value="USER">User</option>
                <option value="ADMIN">Admin</option>
                <option value="OP">OP</option>
              </select>
            </div>
          </div>

          <div v-if="!editingUser" class="form-row">
            <div class="form-group">
              <label>Password *</label>
              <input 
                v-model="formData.password" 
                type="password" 
                required
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>Confirm Password *</label>
              <input 
                v-model="formData.confirmPassword" 
                type="password" 
                required
                class="form-control"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Initial KPI</label>
              <input 
                v-model.number="formData.kpi_current" 
                type="number" 
                min="0"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="formData.status" class="form-control">
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
                <option value="SUSPENDED">Suspended</option>
              </select>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-outline">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ editingUser ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- KPI Adjustment Modal -->
    <div v-if="showKPIModal" class="modal-overlay" @click="closeKPI">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Adjust KPI for {{ kpiUser?.display_name || kpiUser?.username }}</h3>
          <button @click="closeKPI" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="saveKPI" class="kpi-form">
          <div class="form-group">
            <label>Current KPI</label>
            <input 
              :value="kpiUser?.kpi_current || 0" 
              type="number" 
              readonly
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label>Adjustment Type</label>
            <select v-model="kpiData.type" class="form-control">
              <option value="add">Add KPI</option>
              <option value="subtract">Subtract KPI</option>
              <option value="set">Set KPI</option>
            </select>
          </div>

          <div class="form-group">
            <label>Amount</label>
            <input 
              v-model.number="kpiData.amount" 
              type="number" 
              required
              class="form-control"
              placeholder="Enter amount"
            />
          </div>

          <div class="form-group">
            <label>Reason</label>
            <textarea 
              v-model="kpiData.reason" 
              class="form-control"
              rows="3"
              placeholder="Reason for KPI adjustment"
            ></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeKPI" class="btn btn-outline">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              Adjust KPI
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '../../../utils/api.js'

export default {
  name: 'UserManagementConfig',
  setup() {
    // State
    const users = ref([])
    const loading = ref(false)
    const showCreateModal = ref(false)
    const editingUser = ref(null)
    const showKPIModal = ref(false)
    const kpiUser = ref(null)
    const searchQuery = ref('')
    const roleFilter = ref('')
    
    // Form data
    const formData = reactive({
      username: '',
      display_name: '',
      email: '',
      role: 'USER',
      password: '',
      confirmPassword: '',
      kpi_current: 0,
      status: 'ACTIVE'
    })

    const kpiData = reactive({
      type: 'add',
      amount: 0,
      reason: ''
    })

    // Computed
    const filteredUsers = computed(() => {
      return users.value.filter(user => {
        const matchesSearch = !searchQuery.value || 
          user.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          (user.display_name && user.display_name.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
          (user.email && user.email.toLowerCase().includes(searchQuery.value.toLowerCase()))
        
        const matchesRole = !roleFilter.value || user.role === roleFilter.value
        
        return matchesSearch && matchesRole
      })
    })

    // Methods
    const loadUsers = async () => {
      try {
        loading.value = true
        users.value = await apiGet('/admin/users')
      } catch (error) {
        console.error('Error loading users:', error)
      } finally {
        loading.value = false
      }
    }

    const saveUser = async () => {
      if (!editingUser.value && formData.password !== formData.confirmPassword) {
        alert('Passwords do not match')
        return
      }
      
      try {
        loading.value = true
        
        const url = editingUser.value 
          ? `/admin/users/${editingUser.value.id}`
          : '/admin/users'
        
        const payload = { ...formData }
        if (!editingUser.value) {
          delete payload.confirmPassword
        } else {
          delete payload.password
          delete payload.confirmPassword
        }
        
        if (editingUser.value) {
          await apiPut(url, payload)
        } else {
          await apiPost(url, payload)
        }
        
        await loadUsers()
        closeModal()
      } catch (error) {
        console.error('Error saving user:', error)
      } finally {
        loading.value = false
      }
    }

    const editUser = (user) => {
      editingUser.value = user
      Object.assign(formData, {
        ...user,
        password: '',
        confirmPassword: ''
      })
    }

    const deleteUser = async (user) => {
      if (!confirm(`Are you sure you want to delete user "${user.username}"?`)) {
        return
      }
      
      try {
        loading.value = true
        await apiDelete(`/admin/users/${user.id}`)
        await loadUsers()
      } catch (error) {
        console.error('Error deleting user:', error)
      } finally {
        loading.value = false
      }
    }

    const adjustKPI = (user) => {
      kpiUser.value = user
      kpiData.type = 'add'
      kpiData.amount = 0
      kpiData.reason = ''
      showKPIModal.value = true
    }

    const saveKPI = async () => {
      try {
        loading.value = true
        await apiPost(`/admin/users/${kpiUser.value.id}/kpi`, kpiData)
        await loadUsers()
        closeKPI()
      } catch (error) {
        console.error('Error adjusting KPI:', error)
      } finally {
        loading.value = false
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      editingUser.value = null
      
      // Reset form
      Object.assign(formData, {
        username: '',
        display_name: '',
        email: '',
        role: 'USER',
        password: '',
        confirmPassword: '',
        kpi_current: 0,
        status: 'ACTIVE'
      })
    }

    const closeKPI = () => {
      showKPIModal.value = false
      kpiUser.value = null
      Object.assign(kpiData, {
        type: 'add',
        amount: 0,
        reason: ''
      })
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    // Lifecycle
    onMounted(() => {
      loadUsers()
    })

    return {
      users,
      loading,
      showCreateModal,
      editingUser,
      showKPIModal,
      kpiUser,
      searchQuery,
      roleFilter,
      formData,
      kpiData,
      filteredUsers,
      loadUsers,
      saveUser,
      editUser,
      deleteUser,
      adjustKPI,
      saveKPI,
      closeModal,
      closeKPI,
      formatDate
    }
  }
}
</script>

<style scoped>
.user-management-config {
  width: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #34495e;
}

.user-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.filter-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 200px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.users-table {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  overflow: hidden;
}

.users-table table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e1e8ed;
}

.users-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #34495e;
}

.users-table tr:hover {
  background: #f8f9fa;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.role-badge.op {
  background: #fff3cd;
  color: #856404;
}

.role-badge.admin {
  background: #d1ecf1;
  color: #0c5460;
}

.role-badge.user {
  background: #d4edda;
  color: #155724;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.suspended {
  background: #fff3cd;
  color: #856404;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
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
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
}

.user-form,
.kpi-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #34495e;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e1e8ed;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-outline {
  background: transparent;
  border: 1px solid #3498db;
  color: #3498db;
}

.btn-outline:hover:not(:disabled) {
  background: #3498db;
  color: white;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .user-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-controls {
    flex-direction: column;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .users-table {
    overflow-x: auto;
  }
}
</style>
