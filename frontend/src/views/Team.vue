<template>
  <div class="team">
    <div class="page-header">
      <h1>Team Management</h1>
      <p>Manage your team members, roles, and permissions</p>
    </div>

    <!-- Team Controls -->
    <div class="team-controls">
      <div class="control-section">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search team members..."
            @input="filterTeamMembers"
          />
        </div>
      </div>

      <div class="control-section">
        <div class="filter-dropdown">
          <select v-model="roleFilter" @change="filterTeamMembers">
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
            <option value="developer">Developer</option>
            <option value="designer">Designer</option>
            <option value="support">Support</option>
            <option value="viewer">Viewer</option>
          </select>
        </div>
      </div>

      <div class="control-section">
        <div class="filter-dropdown">
          <select v-model="statusFilter" @change="filterTeamMembers">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="pending">Pending</option>
          </select>
        </div>
      </div>

      <div class="control-section">
        <button class="add-member-btn" @click="showAddMemberModal = true">
          <i class="fas fa-plus"></i>
          Add Team Member
        </button>
      </div>
    </div>

    <!-- Team Statistics -->
    <div class="team-stats">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-content">
          <h3>{{ teamStats.total }}</h3>
          <p>Total Members</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon active">
          <i class="fas fa-user-check"></i>
        </div>
        <div class="stat-content">
          <h3>{{ teamStats.active }}</h3>
          <p>Active</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon pending">
          <i class="fas fa-user-clock"></i>
        </div>
        <div class="stat-content">
          <h3>{{ teamStats.pending }}</h3>
          <p>Pending</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon inactive">
          <i class="fas fa-user-times"></i>
        </div>
        <div class="stat-content">
          <h3>{{ teamStats.inactive }}</h3>
          <p>Inactive</p>
        </div>
      </div>
    </div>

    <!-- Team Members List -->
    <div class="team-members">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading team members...</p>
      </div>

      <div v-else-if="filteredTeamMembers.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-users-slash"></i>
        </div>
        <h3>No team members found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="members-grid">
        <div 
          v-for="member in filteredTeamMembers" 
          :key="member.id"
          class="member-card"
        >
          <div class="member-header">
            <div class="member-avatar">
              <img v-if="member.avatar" :src="member.avatar" :alt="member.name" />
              <div v-else class="avatar-placeholder">
                {{ getInitials(member.name) }}
              </div>
              <div :class="['status-indicator', member.status]"></div>
            </div>
            <div class="member-info">
              <h4>{{ member.name }}</h4>
              <p>{{ member.email }}</p>
              <span :class="['role-badge', member.role]">{{ member.role }}</span>
            </div>
          </div>

          <div class="member-details">
            <div class="detail-item">
              <i class="fas fa-calendar"></i>
              <span>Joined {{ formatDate(member.created_at) }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-clock"></i>
              <span>Last active {{ formatLastActive(member.last_active) }}</span>
            </div>
            <div v-if="member.department" class="detail-item">
              <i class="fas fa-building"></i>
              <span>{{ member.department }}</span>
            </div>
          </div>

          <div class="member-actions">
            <button 
              class="action-btn view"
              @click="viewMember(member)"
              title="View Details"
            >
              <i class="fas fa-eye"></i>
            </button>
            <button 
              class="action-btn edit"
              @click="editMember(member)"
              title="Edit Member"
            >
              <i class="fas fa-edit"></i>
            </button>
            <button 
              class="action-btn permissions"
              @click="managePermissions(member)"
              title="Manage Permissions"
            >
              <i class="fas fa-key"></i>
            </button>
            <button 
              :class="['action-btn', member.status === 'active' ? 'deactivate' : 'activate']"
              @click="toggleMemberStatus(member)"
              :title="member.status === 'active' ? 'Deactivate' : 'Activate'"
            >
              <i :class="member.status === 'active' ? 'fas fa-ban' : 'fas fa-check'"></i>
            </button>
            <button 
              class="action-btn delete"
              @click="deleteMember(member)"
              title="Remove Member"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Member Modal -->
    <div v-if="showAddMemberModal || showEditMemberModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ showEditMemberModal ? 'Edit Team Member' : 'Add Team Member' }}</h2>
          <button class="close-btn" @click="closeModals">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label>Full Name *</label>
              <input 
                v-model="memberForm.name" 
                type="text" 
                placeholder="John Doe"
                required
              />
            </div>

            <div class="form-group">
              <label>Email Address *</label>
              <input 
                v-model="memberForm.email" 
                type="email" 
                placeholder="john@example.com"
                required
              />
            </div>

            <div class="form-group">
              <label>Role *</label>
              <select v-model="memberForm.role" required>
                <option value="">Select Role</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="developer">Developer</option>
                <option value="designer">Designer</option>
                <option value="support">Support</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>

            <div class="form-group">
              <label>Department</label>
              <input 
                v-model="memberForm.department" 
                type="text" 
                placeholder="Engineering"
              />
            </div>

            <div class="form-group">
              <label>Phone Number</label>
              <input 
                v-model="memberForm.phone" 
                type="tel" 
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div class="form-group">
              <label>Status</label>
              <select v-model="memberForm.status">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="pending">Pending</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Notes</label>
            <textarea 
              v-model="memberForm.notes" 
              placeholder="Additional notes about this team member..."
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModals">Cancel</button>
          <button 
            class="btn-primary" 
            @click="saveMember"
            :disabled="saving"
          >
            {{ saving ? 'Saving...' : (showEditMemberModal ? 'Update Member' : 'Add Member') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Permissions Modal -->
    <div v-if="showPermissionsModal" class="modal-overlay" @click="closePermissionsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Manage Permissions - {{ selectedMember?.name }}</h2>
          <button class="close-btn" @click="closePermissionsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="permissions-grid">
            <div 
              v-for="category in permissionCategories" 
              :key="category.name"
              class="permission-category"
            >
              <h3>{{ category.label }}</h3>
              <div class="permission-items">
                <label 
                  v-for="permission in category.permissions" 
                  :key="permission.key"
                  class="permission-item"
                >
                  <input 
                    type="checkbox" 
                    :checked="memberPermissions[permission.key]"
                    @change="updatePermission(permission.key, $event.target.checked)"
                  />
                  <div class="permission-info">
                    <span class="permission-name">{{ permission.name }}</span>
                    <span class="permission-description">{{ permission.description }}</span>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closePermissionsModal">Cancel</button>
          <button 
            class="btn-primary" 
            @click="savePermissions"
            :disabled="saving"
          >
            {{ saving ? 'Saving...' : 'Save Permissions' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const saving = ref(false)
const teamMembers = ref([])
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

// Modal states
const showAddMemberModal = ref(false)
const showEditMemberModal = ref(false)
const showPermissionsModal = ref(false)
const selectedMember = ref(null)

// Forms
const memberForm = reactive({
  name: '',
  email: '',
  role: '',
  department: '',
  phone: '',
  status: 'active',
  notes: ''
})

const memberPermissions = reactive({})

// Permission categories
const permissionCategories = [
  {
    name: 'dashboard',
    label: 'Dashboard',
    permissions: [
      { key: 'view_dashboard', name: 'View Dashboard', description: 'Access main dashboard' },
      { key: 'view_analytics', name: 'View Analytics', description: 'See analytics data' },
      { key: 'export_reports', name: 'Export Reports', description: 'Download reports' }
    ]
  },
  {
    name: 'orders',
    label: 'Orders',
    permissions: [
      { key: 'view_orders', name: 'View Orders', description: 'See all orders' },
      { key: 'create_orders', name: 'Create Orders', description: 'Create new orders' },
      { key: 'edit_orders', name: 'Edit Orders', description: 'Modify existing orders' },
      { key: 'delete_orders', name: 'Delete Orders', description: 'Remove orders' }
    ]
  },
  {
    name: 'users',
    label: 'Users',
    permissions: [
      { key: 'view_users', name: 'View Users', description: 'See user list' },
      { key: 'create_users', name: 'Create Users', description: 'Add new users' },
      { key: 'edit_users', name: 'Edit Users', description: 'Modify user accounts' },
      { key: 'delete_users', name: 'Delete Users', description: 'Remove users' }
    ]
  },
  {
    name: 'team',
    label: 'Team Management',
    permissions: [
      { key: 'view_team', name: 'View Team', description: 'See team members' },
      { key: 'add_members', name: 'Add Members', description: 'Add team members' },
      { key: 'edit_members', name: 'Edit Members', description: 'Modify team members' },
      { key: 'manage_permissions', name: 'Manage Permissions', description: 'Change member permissions' }
    ]
  },
  {
    name: 'system',
    label: 'System',
    permissions: [
      { key: 'view_settings', name: 'View Settings', description: 'Access system settings' },
      { key: 'edit_settings', name: 'Edit Settings', description: 'Modify system settings' },
      { key: 'view_logs', name: 'View Logs', description: 'Access system logs' }
    ]
  }
]

// Computed properties
const filteredTeamMembers = computed(() => {
  let filtered = teamMembers.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(member => 
      member.name.toLowerCase().includes(query) ||
      member.email.toLowerCase().includes(query) ||
      member.department?.toLowerCase().includes(query)
    )
  }

  // Apply role filter
  if (roleFilter.value) {
    filtered = filtered.filter(member => member.role === roleFilter.value)
  }

  // Apply status filter
  if (statusFilter.value) {
    filtered = filtered.filter(member => member.status === statusFilter.value)
  }

  return filtered
})

const teamStats = computed(() => {
  const stats = {
    total: teamMembers.value.length,
    active: teamMembers.value.filter(m => m.status === 'active').length,
    inactive: teamMembers.value.filter(m => m.status === 'inactive').length,
    pending: teamMembers.value.filter(m => m.status === 'pending').length
  }
  return stats
})

// Methods
const loadTeamMembers = async () => {
  loading.value = true
  try {
    const response = await apiGet('/team/members')
    if (response.success) {
      teamMembers.value = response.members || []
    }
  } catch (error) {
    console.error('Error loading team members:', error)
    showError('Failed to load team members')
  } finally {
    loading.value = false
  }
}

const filterTeamMembers = () => {
  // This is reactive, no additional action needed
}

const getInitials = (name) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const formatLastActive = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return 'just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} days ago`
  
  return formatDate(dateString)
}

const getEmptyMessage = () => {
  if (searchQuery.value || roleFilter.value || statusFilter.value) {
    return 'No team members match your search criteria'
  }
  return 'Start by adding your first team member'
}

const viewMember = (member) => {
  // Navigate to member details or show details modal
  console.log('View member:', member)
}

const editMember = (member) => {
  selectedMember.value = member
  Object.assign(memberForm, {
    ...member,
    notes: member.notes || ''
  })
  showEditMemberModal.value = true
}

const managePermissions = async (member) => {
  selectedMember.value = member
  
  // Load member permissions
  try {
    const response = await apiGet(`/team/members/${member.id}/permissions`)
    if (response.success) {
      Object.assign(memberPermissions, response.permissions || {})
      showPermissionsModal.value = true
    }
  } catch (error) {
    console.error('Error loading permissions:', error)
    showError('Failed to load permissions')
  }
}

const toggleMemberStatus = async (member) => {
  const newStatus = member.status === 'active' ? 'inactive' : 'active'
  const action = newStatus === 'active' ? 'activate' : 'deactivate'
  
  const confirmed = await showConfirm(`Are you sure you want to ${action} ${member.name}?`)
  if (!confirmed) return

  try {
    const response = await apiPut(`/team/members/${member.id}/status`, {
      status: newStatus
    })
    
    if (response.success) {
      member.status = newStatus
      showSuccess(`Member ${action}d successfully`)
    }
  } catch (error) {
    console.error('Error updating member status:', error)
    showError(`Failed to ${action} member`)
  }
}

const deleteMember = async (member) => {
  const confirmed = await showConfirm(`Are you sure you want to remove ${member.name} from the team?`)
  if (!confirmed) return

  try {
    const response = await apiDelete(`/team/members/${member.id}`)
    if (response.success) {
      const index = teamMembers.value.findIndex(m => m.id === member.id)
      if (index > -1) {
        teamMembers.value.splice(index, 1)
        showSuccess('Member removed successfully')
      }
    }
  } catch (error) {
    console.error('Error deleting member:', error)
    showError('Failed to remove member')
  }
}

const saveMember = async () => {
  if (!memberForm.name || !memberForm.email || !memberForm.role) {
    showError('Please fill in all required fields')
    return
  }

  saving.value = true
  try {
    const isEdit = showEditMemberModal.value
    const endpoint = isEdit ? `/team/members/${selectedMember.value.id}` : '/team/members'
    const method = isEdit ? apiPut : apiPost

    const response = await method(endpoint, memberForm)
    
    if (response.success) {
      if (isEdit) {
        Object.assign(selectedMember.value, memberForm)
        showSuccess('Member updated successfully')
      } else {
        teamMembers.value.push(response.member)
        showSuccess('Member added successfully')
      }
      closeModals()
    }
  } catch (error) {
    console.error('Error saving member:', error)
    showError('Failed to save member')
  } finally {
    saving.value = false
  }
}

const updatePermission = (key, value) => {
  memberPermissions[key] = value
}

const savePermissions = async () => {
  saving.value = true
  try {
    const response = await apiPut(`/team/members/${selectedMember.value.id}/permissions`, {
      permissions: memberPermissions
    })
    
    if (response.success) {
      showSuccess('Permissions updated successfully')
      closePermissionsModal()
    }
  } catch (error) {
    console.error('Error saving permissions:', error)
    showError('Failed to save permissions')
  } finally {
    saving.value = false
  }
}

const closeModals = () => {
  showAddMemberModal.value = false
  showEditMemberModal.value = false
  resetMemberForm()
}

const closePermissionsModal = () => {
  showPermissionsModal.value = false
  selectedMember.value = null
  Object.keys(memberPermissions).forEach(key => delete memberPermissions[key])
}

const resetMemberForm = () => {
  Object.assign(memberForm, {
    name: '',
    email: '',
    role: '',
    department: '',
    phone: '',
    status: 'active',
    notes: ''
  })
  selectedMember.value = null
}

// Lifecycle
onMounted(() => {
  loadTeamMembers()
})
</script>

<style scoped>
.team {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.team-controls {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: center;
}

.search-box {
  position: relative;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.filter-dropdown select {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.add-member-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add-member-btn:hover {
  background: var(--primary-hover);
}

.team-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 50px;
  height: 50px;
  background: var(--primary-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.stat-icon.active {
  background: var(--success-color);
}

.stat-icon.pending {
  background: var(--warning-color);
}

.stat-icon.inactive {
  background: var(--danger-color);
}

.stat-content h3 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.9rem;
}

.team-members {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 3px solid var(--glass-border);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 3rem;
  color: var(--text-tertiary);
  margin-bottom: 1rem;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.member-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.member-card:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.member-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.member-avatar {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.2rem;
}

.status-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
}

.status-indicator.active {
  background: var(--success-color);
}

.status-indicator.inactive {
  background: var(--danger-color);
}

.status-indicator.pending {
  background: var(--warning-color);
}

.member-info {
  flex: 1;
}

.member-info h4 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.member-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.role-badge.admin {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.role-badge.manager {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.role-badge.developer {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.role-badge.designer {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.role-badge.support {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.role-badge.viewer {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.member-details {
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.detail-item i {
  width: 16px;
  color: var(--text-tertiary);
}

.member-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  background: var(--glass-bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.view:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.edit:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.permissions:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.activate:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.deactivate:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.permission-category h3 {
  margin-bottom: 1rem;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.permission-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.permission-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background 0.3s ease;
}

.permission-item:hover {
  background: var(--glass-bg-hover);
}

.permission-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
  margin-top: 0.125rem;
}

.permission-info {
  flex: 1;
}

.permission-name {
  display: block;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.permission-description {
  display: block;
  color: var(--text-tertiary);
  font-size: 0.8rem;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .team {
    padding: 1rem;
  }
  
  .team-controls {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .team-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .members-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .permissions-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
