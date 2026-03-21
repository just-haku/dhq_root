<template>
  <div class="admin-panel">
    <!-- Header with Panic Button -->
    <div class="admin-header">
      <div class="header-content">
        <div class="header-title">
          <h2>⚙️ System Administration</h2>
          <p class="header-subtitle">Manage your DHQ Digital Headquarters</p>
        </div>
        <button @click="showPanicModal = true" class="panic-button">
          <span class="panic-icon">🚨</span>
          <span class="panic-text">PANIC BUTTON</span>
        </button>
      </div>
    </div>

    <!-- System Status -->
    <div class="admin-section status-section">
      <div class="section-header">
        <h3>📊 System Status</h3>
        <div class="status-indicator" :class="{ 'all-online': allSystemsOnline }">
          <span class="status-dot"></span>
          {{ allSystemsOnline ? 'All Systems Online' : 'Some Issues Detected' }}
        </div>
      </div>
      <div class="status-grid">
        <div class="status-card" :class="{ 'status-online': systemStatus.backend, 'status-offline': !systemStatus.backend }">
          <div class="status-icon">
            {{ systemStatus.backend ? '🟢' : '🔴' }}
          </div>
          <div class="status-content">
            <div class="status-label">Backend</div>
            <div class="status-value">{{ systemStatus.backend ? 'Online' : 'Offline' }}</div>
          </div>
        </div>
        <div class="status-card" :class="{ 'status-online': systemStatus.database, 'status-offline': !systemStatus.database }">
          <div class="status-icon">
            {{ systemStatus.database ? '🟢' : '🔴' }}
          </div>
          <div class="status-content">
            <div class="status-label">Database</div>
            <div class="status-value">{{ systemStatus.database ? 'Connected' : 'Disconnected' }}</div>
          </div>
        </div>
        <div class="status-card" :class="{ 'status-online': systemStatus.redis, 'status-offline': !systemStatus.redis }">
          <div class="status-icon">
            {{ systemStatus.redis ? '🟢' : '🔴' }}
          </div>
          <div class="status-content">
            <div class="status-label">Redis</div>
            <div class="status-value">{{ systemStatus.redis ? 'Connected' : 'Disconnected' }}</div>
          </div>
        </div>
        <div class="status-card" :class="{ 'status-online': systemStatus.socketio, 'status-offline': !systemStatus.socketio }">
          <div class="status-icon">
            {{ systemStatus.socketio ? '🟢' : '🔴' }}
          </div>
          <div class="status-content">
            <div class="status-label">Socket.IO</div>
            <div class="status-value">{{ systemStatus.socketio ? 'Running' : 'Stopped' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Management Sections -->
    <div class="management-grid">
      <!-- OP Configuration Dashboard -->
      <div class="admin-section management-card">
        <div class="card-header">
          <div class="card-icon">🔧</div>
          <div class="card-title">
            <h3>OP Configuration</h3>
            <p>System settings and configurations</p>
          </div>
        </div>
        <OPConfigDashboard />
      </div>

      <!-- API Server Management -->
      <div class="admin-section management-card">
        <div class="card-header">
          <div class="card-icon">🌐</div>
          <div class="card-title">
            <h3>API Server Management</h3>
            <p>Configure external API servers</p>
          </div>
        </div>
        <APIServerManagement />
      </div>

      <!-- User Profile -->
      <div class="admin-section management-card">
        <div class="card-header">
          <div class="card-icon">👤</div>
          <div class="card-title">
            <h3>User Profile & API Keys</h3>
            <p>Manage your API keys and settings</p>
          </div>
        </div>
        <UserProfile />
      </div>

      <!-- Drive Administration -->
      <div class="admin-section management-card">
        <div class="card-header">
          <div class="card-icon">📁</div>
          <div class="card-title">
            <h3>Drive Administration</h3>
            <p>File and storage management</p>
          </div>
        </div>
        <DriveAdmin />
      </div>
    </div>

    <!-- System Analytics -->
    <div class="admin-section analytics-section">
      <div class="section-header">
        <h3>📈 System Analytics</h3>
        <div class="analytics-refresh">
          <button @click="refreshAnalytics" class="refresh-button" :disabled="analyticsLoading">
            <span class="refresh-icon" :class="{ 'spinning': analyticsLoading }">🔄</span>
            Refresh
          </button>
        </div>
      </div>
      <div class="analytics-grid">
        <div class="analytics-card users-card">
          <div class="analytics-icon">👥</div>
          <div class="analytics-content">
            <div class="analytics-label">Total Users</div>
            <div class="analytics-value">{{ analytics.totalUsers }}</div>
            <div class="analytics-trend">+12% this month</div>
          </div>
        </div>
        <div class="analytics-card active-users-card">
          <div class="analytics-icon">✨</div>
          <div class="analytics-content">
            <div class="analytics-label">Active Users</div>
            <div class="analytics-value">{{ analytics.activeUsers }}</div>
            <div class="analytics-trend">+8% this week</div>
          </div>
        </div>
        <div class="analytics-card files-card">
          <div class="analytics-icon">📄</div>
          <div class="analytics-content">
            <div class="analytics-label">Total Files</div>
            <div class="analytics-value">{{ analytics.totalFiles }}</div>
            <div class="analytics-trend">+25% this month</div>
          </div>
        </div>
        <div class="analytics-card projects-card">
          <div class="analytics-icon">🚀</div>
          <div class="analytics-content">
            <div class="analytics-label">Total Projects</div>
            <div class="analytics-value">{{ analytics.totalProjects }}</div>
            <div class="analytics-trend">+5% this month</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Nuke Protocol Section -->
    <div class="admin-section danger-zone">
      <h3>☢️ DANGER ZONE</h3>
      <div class="nuke-controls">
        <div class="nuke-warning">
          <p>⚠️ The Nuke Protocol will IRREVERSIBLY delete all DHQ data except OP users.</p>
          <p>This action cannot be undone and requires multiple verification steps.</p>
        </div>
        <button @click="initiateNuke" class="nuke-button">
          💀 INITIATE NUKE PROTOCOL
        </button>
      </div>
    </div>

    <!-- Panic Modal -->
    <div v-if="showPanicModal" class="modal-overlay" @click="showPanicModal = false">
      <div class="modal-content panic-modal" @click.stop>
        <div class="modal-header">
          <h3>🚨 PANIC BUTTON ACTIVATED</h3>
        </div>
        <div class="modal-body">
          <p><strong>Emergency containment protocol initiated!</strong></p>
          <p>This will immediately:</p>
          <ul>
            <li>🔐 Invalidate ALL active sessions</li>
            <li>🔒 Enable maintenance mode (OP only)</li>
            <li>🔗 Disable all public file links</li>
          </ul>
          <p><strong>Are you sure you want to proceed?</strong></p>
        </div>
        <div class="modal-footer">
          <button @click="executePanicProtocol" class="btn btn-danger">
            🚨 EXECUTE PANIC PROTOCOL
          </button>
          <button @click="showPanicModal = false" class="btn btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateUser" class="modal-overlay" @click="showCreateUser = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New User</h3>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Username:</label>
            <input v-model="createUserForm.username" type="text" placeholder="Enter username" />
          </div>
          <div class="form-group">
            <label>Email:</label>
            <input v-model="createUserForm.email" type="email" placeholder="Enter email" />
          </div>
          <div class="form-group">
            <label>Password:</label>
            <input v-model="createUserForm.password" type="password" placeholder="Enter password" />
          </div>
          <div class="form-group">
            <label>Display Name:</label>
            <input v-model="createUserForm.display_name" type="text" placeholder="Enter display name" />
          </div>
          <div class="form-group">
            <label>Role:</label>
            <select v-model="createUserForm.role">
              <option value="USER">User</option>
              <option value="ADMIN">Admin</option>
              <option value="OP">OP</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="createUser" class="btn btn-primary">Create User</button>
          <button @click="showCreateUser = false" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditUser" class="modal-overlay" @click="showEditUser = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit User</h3>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Username:</label>
            <input v-model="selectedUser.username" type="text" disabled />
          </div>
          <div class="form-group">
            <label>Email:</label>
            <input v-model="selectedUser.email" type="email" placeholder="Enter email" />
          </div>
          <div class="form-group">
            <label>Display Name:</label>
            <input v-model="selectedUser.display_name" type="text" placeholder="Enter display name" />
          </div>
          <div class="form-group">
            <label>Role:</label>
            <select v-model="selectedUser.role">
              <option value="USER">User</option>
              <option value="ADMIN">Admin</option>
              <option value="OP">OP</option>
            </select>
          </div>
          <div class="form-group">
            <label>Status:</label>
            <select v-model="selectedUser.status">
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
              <option value="SUSPENDED">Suspended</option>
            </select>
          </div>
          <div class="form-group">
            <label>KPI Balance:</label>
            <input v-model="selectedUser.kpi_current" type="number" placeholder="Enter KPI balance" />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="updateUser" class="btn btn-primary">Update User</button>
          <button @click="showEditUser = false" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Nuke Modal -->
    <div v-if="showNukeModal" class="modal-overlay" @click="showNukeModal = false">
      <div class="modal-content nuke-modal" @click.stop>
        <div class="modal-header">
          <h3>☢️ NUKE PROTOCOL</h3>
        </div>
        <div class="modal-body">
          <div class="nuke-step" :class="{ completed: nukeStep >= 1 }">
            <div class="step-number">1</div>
            <div class="step-content">
              <h4>Warning Acknowledgment</h4>
              <p>Type "TOTAL DATA WIPE" to acknowledge you understand this will delete everything.</p>
              <input v-model="nukeConfirmation1" type="text" placeholder="TOTAL DATA WIPE" />
            </div>
          </div>
          
          <div class="nuke-step" :class="{ completed: nukeStep >= 2 }">
            <div class="step-number">2</div>
            <div class="step-content">
              <h4>Password Verification</h4>
              <p>Re-enter your OP password to verify identity.</p>
              <input v-model="nukePassword" type="password" placeholder="OP Password" />
            </div>
          </div>
          
          <div class="nuke-step" :class="{ completed: nukeStep >= 3 }">
            <div class="step-number">3</div>
            <div class="step-content">
              <h4>Email OTP Verification</h4>
              <p>Check your email for the 8-digit verification code.</p>
              <input v-model="nukeOTP" type="text" placeholder="8-digit code" maxlength="8" />
              <button @click="sendNukeOTP" class="btn btn-secondary" :disabled="nukeOTPSent">
                {{ nukeOTPSent ? 'OTP Sent' : 'Send OTP' }}
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button 
            @click="executeNuke" 
            class="btn btn-danger" 
            :disabled="!canExecuteNuke"
          >
            💀 EXECUTE NUKE
          </button>
          <button @click="cancelNuke" class="btn btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '../../utils/api.js'
import DriveAdmin from '../Drive/DriveAdmin.vue'
import OPConfigDashboard from './OPConfigDashboard.vue'
import APIServerManagement from './config/APIServerManagement.vue'
import UserProfile from '../UserProfile.vue'

export default {
  name: 'AdminPanel',
  components: {
    DriveAdmin,
    OPConfigDashboard,
    APIServerManagement,
    UserProfile
  },
  setup() {
    // State
    const systemStatus = ref({
      backend: false,
      database: false,
      redis: false,
      socketio: false
    })
    
    const users = ref([])
    const analytics = ref({
      totalUsers: 0,
      activeUsers: 0,
      totalFiles: 0,
      totalProjects: 0
    })
    
    // Modals
    const showPanicModal = ref(false)
    const showNukeModal = ref(false)
    const showCreateUser = ref(false)
    const showEditUser = ref(false)
    
    // User forms
    const selectedUser = ref(null)
    const createUserForm = ref({
      username: '',
      email: '',
      password: '',
      display_name: '',
      role: 'USER'
    })
    
    // Nuke protocol
    const nukeStep = ref(0)
    const nukeConfirmation1 = ref('')
    const nukePassword = ref('')
    const nukeOTP = ref('')
    const nukeOTPSent = ref(false)
    
    // Get auth headers
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token')
      return token ? { 'Authorization': `Bearer ${token}` } : {}
    }
    
    // Check system status
    const checkSystemStatus = async () => {
      try {
        // Backend
        try {
          // Heatlh check is a special case, but we can use fetch here since it's public.
          // However, for consistency let's use a try/catch.
          const res = await apiGet('/health')
          systemStatus.value.backend = !!res
        } catch {
          systemStatus.value.backend = false
        }
        
        // Database
        try {
          const dbResponse = await apiGet('/admin/status/database')
          systemStatus.value.database = dbResponse.ok
        } catch { systemStatus.value.database = false }
        
        // Redis
        try {
          const redisResponse = await apiGet('/admin/status/redis')
          systemStatus.value.redis = redisResponse.ok
        } catch { systemStatus.value.redis = false }
        
        // Socket.IO - public check
        try {
          const socketUrl = window.location.origin === 'https://haku.io.vn' 
            ? 'https://haku.io.vn' 
            : 'http://localhost:8001'
          const socketioResponse = await fetch(socketUrl)
          systemStatus.value.socketio = socketioResponse.ok
        } catch { systemStatus.value.socketio = false }
        
      } catch (error) {
        console.error('Error checking system status:', error)
      }
    }
    
    // Load users
    const loadUsers = async () => {
      try {
        const data = await apiGet('/admin/users')
        users.value = data
      } catch (error) {
        console.error('Error loading users:', error)
      }
    }
    
    // Edit user
    const editUser = (user) => {
      selectedUser.value = { ...user }
      showEditUser.value = true
    }
    
    // Create user
    const createUser = async () => {
      try {
        await apiPost('/admin/users', createUserForm.value)
        alert('User created successfully!')
        showCreateUser.value = false
        createUserForm.value = {
          username: '',
          email: '',
          password: '',
          display_name: '',
          role: 'USER'
        }
        loadUsers()
      } catch (error) {
        console.error('Error creating user:', error)
        alert(`Failed to create user: ${error.message}`)
      }
    }
    
    // Update user
    const updateUser = async () => {
      try {
        await apiPut(`/admin/users/${selectedUser.value.id}`, selectedUser.value)
        alert('User updated successfully!')
        showEditUser.value = false
        selectedUser.value = null
        loadUsers()
      } catch (error) {
        console.error('Error updating user:', error)
        alert(`Failed to update user: ${error.message}`)
      }
    }
    
    // Delete user
    const deleteUser = async (user) => {
      if (!confirm(`Are you sure you want to delete user "${user.username}"?`)) {
        return
      }
      
      try {
        await apiDelete(`/admin/users/${user.id}`)
        alert('User deleted successfully!')
        loadUsers()
      } catch (error) {
        console.error('Error deleting user:', error)
        alert(`Failed to delete user: ${error.message}`)
      }
    }
    
    // Load analytics
    const loadAnalytics = async () => {
      try {
        const data = await apiGet('/admin/analytics')
        analytics.value = data
      } catch (error) {
        console.error('Error loading analytics:', error)
      }
    }
    
    // Execute panic protocol
    const executePanicProtocol = async () => {
      try {
        await apiPost('/admin/panic', {})
        alert('Panic protocol executed! All sessions invalidated.')
        showPanicModal.value = false
      } catch (error) {
        console.error('Error executing panic protocol:', error)
        alert(`Failed to execute panic protocol: ${error.message}`)
      }
    }
    
    // Initiate nuke
    const initiateNuke = () => {
      showNukeModal.value = true
      nukeStep.value = 0
      nukeConfirmation1.value = ''
      nukePassword.value = ''
      nukeOTP.value = ''
      nukeOTPSent.value = false
    }
    
    // Send nuke OTP
    const sendNukeOTP = async () => {
      try {
        await apiPost('/admin/nuke/otp', {})
        nukeOTPSent.value = true
        alert('OTP sent to your email!')
      } catch (error) {
        console.error('Error sending OTP:', error)
        alert(`Failed to send OTP: ${error.message}`)
      }
    }
    
    // Execute nuke
    const executeNuke = async () => {
      try {
        await apiPost('/admin/nuke', {
          confirmation: nukeConfirmation1.value,
          password: nukePassword.value,
          otp: nukeOTP.value
        })
        
        alert('Nuke protocol executed! System will be sanitized.')
        showNukeModal.value = false
        // Reload page after delay
        setTimeout(() => {
          window.location.reload()
        }, 3000)
      } catch (error) {
        console.error('Error executing nuke:', error)
        alert(`Nuke failed: ${error.message}`)
      }
    }
    
    // Cancel nuke
    const cancelNuke = () => {
      showNukeModal.value = false
      nukeStep.value = 0
    }
    
    // Computed
    const canExecuteNuke = computed(() => {
      return nukeConfirmation1.value === 'TOTAL DATA WIPE' &&
             nukePassword.value &&
             nukeOTP.value.length === 8
    })
    
    const allSystemsOnline = computed(() => {
      return systemStatus.value.backend && 
             systemStatus.value.database && 
             systemStatus.value.redis && 
             systemStatus.value.socketio
    })
    
    const analyticsLoading = ref(false)
    
    // Methods
    const refreshAnalytics = async () => {
      analyticsLoading.value = true
      try {
        // Simulate API call to refresh analytics
        await new Promise(resolve => setTimeout(resolve, 1000))
        // In real implementation, this would fetch fresh data
        analytics.value = {
          totalUsers: Math.floor(Math.random() * 1000) + 100,
          activeUsers: Math.floor(Math.random() * 500) + 50,
          totalFiles: Math.floor(Math.random() * 10000) + 1000,
          totalProjects: Math.floor(Math.random() * 100) + 10
        }
      } catch (error) {
        console.error('Failed to refresh analytics:', error)
      } finally {
        analyticsLoading.value = false
      }
    }
    
    // Watch nuke confirmation steps
    watch(nukeConfirmation1, (value) => {
      if (value === 'TOTAL DATA WIPE') {
        nukeStep.value = Math.max(nukeStep.value, 1)
      }
    })
    
    watch(nukePassword, (value) => {
      if (value) {
        nukeStep.value = Math.max(nukeStep.value, 2)
      }
    })
    
    watch(nukeOTP, (value) => {
      if (value.length === 8) {
        nukeStep.value = Math.max(nukeStep.value, 3)
      }
    })
    
    onMounted(() => {
      checkSystemStatus()
      loadUsers()
      loadAnalytics()
      
      // Check status periodically
      setInterval(checkSystemStatus, 30000) // Every 30 seconds
    })
    
    return {
      systemStatus,
      users,
      analytics,
      selectedUser,
      createUserForm,
      showPanicModal,
      showNukeModal,
      showCreateUser,
      showEditUser,
      nukeStep,
      nukeConfirmation1,
      nukePassword,
      nukeOTP,
      nukeOTPSent,
      canExecuteNuke,
      allSystemsOnline,
      analyticsLoading,
      loadUsers,
      editUser,
      createUser,
      updateUser,
      refreshAnalytics,
      deleteUser,
      executePanicProtocol,
      initiateNuke,
      sendNukeOTP,
      executeNuke,
      cancelNuke
    }
  }
}
</script>

<style scoped>
.admin-panel {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  box-shadow: var(--glass-shadow-xl);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.admin-header {
  margin-bottom: 3rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: var(--glass-shadow-xl);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.header-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.header-title h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 1rem;
}

.panic-button {
  background: linear-gradient(135deg, rgba(220, 38, 38, 0.8), rgba(239, 68, 68, 0.8), rgba(248, 113, 113, 0.8));
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 1rem 2rem;
  border-radius: 16px;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  animation: pulse 2s infinite;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: var(--glass-shadow-lg);
  position: relative;
  overflow: hidden;
}

.panic-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.panic-button:hover::before {
  left: 100%;
}

.panic-icon {
  font-size: 1.2rem;
  animation: blink 1s infinite;
}

.panic-button:hover {
  transform: scale(1.05);
  box-shadow: 0 16px 64px rgba(220, 38, 38, 0.4);
  border-color: rgba(255, 255, 255, 0.3);
}

.admin-section {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--glass-shadow-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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

.admin-section:hover {
  transform: translateY(-5px);
  box-shadow: var(--glass-shadow-xl);
  border-color: var(--glass-border-hover);
  background: var(--glass-bg-hover);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-section {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  backdrop-filter: var(--glass-blur-xl);
  -webkit-backdrop-filter: var(--glass-blur-xl);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.status-section .section-header h3 {
  color: var(--text-primary);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.status-indicator.all-online {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  animation: pulse 2s infinite;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.status-card:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-lg);
  border-color: var(--glass-border-hover);
}

.status-card.status-online {
  border-left: 4px solid #22c55e;
}

.status-card.status-offline {
  border-left: 4px solid #ef4444;
}

.status-icon {
  font-size: 1.5rem;
}

.status-content {
  flex: 1;
}

.status-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}

.status-value {
  font-weight: 600;
  font-size: 1rem;
  color: var(--text-primary);
}

.users-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--glass-border);
}

.users-table th {
  background: var(--glass-bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.management-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.management-card {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: var(--glass-shadow-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  flex: 1;
  min-width: 300px;
  max-width: 400px;
}

.management-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.management-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--glass-shadow-xl);
  border-color: var(--glass-border-hover);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border-bottom: 1px solid var(--glass-border);
  position: relative;
}

.card-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.card-icon {
  font-size: 2rem;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--glass-shadow-md);
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.card-title h3 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-title p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.analytics-section {
  background: linear-gradient(135deg, rgba(240, 147, 251, 0.2), rgba(245, 87, 108, 0.2));
  backdrop-filter: var(--glass-blur-xl);
  -webkit-backdrop-filter: var(--glass-blur-xl);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.analytics-section .section-header h3 {
  color: var(--text-primary);
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.9rem;
  position: relative;
  overflow: hidden;
}

.refresh-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.refresh-button:hover::before {
  left: 100%;
}

.refresh-button:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-1px);
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

.analytics-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.analytics-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.analytics-card:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-lg);
  border-color: var(--glass-border-hover);
}

.analytics-icon {
  font-size: 2rem;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--glass-shadow-md);
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.analytics-content {
  flex: 1;
}

.analytics-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}

.analytics-value {
  font-weight: 700;
  font-size: 1.5rem;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.analytics-trend {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.danger-zone {
  background: linear-gradient(135deg, rgba(220, 38, 38, 0.2), rgba(239, 68, 68, 0.2));
  backdrop-filter: var(--glass-blur-xl);
  -webkit-backdrop-filter: var(--glass-blur-xl);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.danger-zone::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s ease-in-out infinite;
}

.danger-zone h3 {
  color: var(--text-primary);
  text-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);
}

.nuke-controls {
  text-align: center;
}

.nuke-warning {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.nuke-warning::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.nuke-warning p {
  margin: 0.5rem 0;
  font-weight: 500;
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.nuke-button {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  padding: 1rem 2rem;
  border-radius: 16px;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.nuke-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.nuke-button:hover::before {
  left: 100%;
}

.nuke-button:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: scale(1.05);
  box-shadow: var(--glass-shadow-lg);
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0.3;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@media (max-width: 768px) {
  .admin-panel {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .management-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .analytics-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style>
