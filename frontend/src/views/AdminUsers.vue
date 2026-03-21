<template>
  <div class="admin-users-container p-6">
    <div class="header-section mb-8">
      <h1 class="text-3xl font-bold text-white mb-2">User Management</h1>
      <p class="text-secondary">Control access, approve registrations, and manage user profiles.</p>
    </div>

    <!-- Tabs -->
    <div class="tabs-container flex gap-4 mb-8">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="currentTab = tab.id"
        class="tab-btn px-6 py-2 rounded-lg transition-all"
        :class="currentTab === tab.id ? 'active-tab' : 'inactive-tab'"
      >
        {{ tab.label }}
        <span v-if="tab.id === 'pending' && pendingUsers.length > 0" class="badge-count ml-2">
          {{ pendingUsers.length }}
        </span>
      </button>
    </div>

    <!-- Search/Filter Bar -->
    <div class="filter-bar glass-panel p-4 mb-6 flex gap-4 items-center">
      <div class="search-input flex-grow relative">
        <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-muted"></i>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search by username..." 
          class="liquid-input w-full pl-12"
        />
      </div>
      <select v-model="roleFilter" class="liquid-input w-48">
        <option value="">All Roles</option>
        <option value="USER">USER</option>
        <option value="AD">AD</option>
        <option value="OP">OP</option>
      </select>
    </div>

    <!-- Users Table/List -->
    <div class="users-list-container space-y-4">
      <div v-if="isLoading" class="text-center py-20">
        <i class="fas fa-spinner fa-spin text-4xl text-primary"></i>
      </div>

      <div v-else-if="filteredUsers.length === 0" class="text-center py-20 glass-panel">
        <p class="text-secondary text-lg">No users found.</p>
      </div>

      <div v-else v-for="user in filteredUsers" :key="user.username" class="user-item-card glass-panel p-6 flex items-center justify-between hover:translate-x-1 transition-transform">
        <div class="user-info flex items-center gap-6">
          <div class="avatar-wrapper">
             <div class="avatar-placeholder flex items-center justify-center overflow-hidden rounded-full w-14 h-14 bg-gradient-to-br from-primary to-secondary">
                <img v-if="user.avatar_url" :src="user.avatar_url" class="w-full h-full object-cover" />
                <span v-else class="text-xl font-bold text-white">{{ user.display_name.charAt(0).toUpperCase() }}</span>
             </div>
          </div>
          <div class="details">
            <div class="flex items-center gap-3">
              <h3 class="text-xl font-bold text-white">{{ user.display_name }}</h3>
              <span class="text-muted text-sm">@{{ user.username }}</span>
              <span class="role-badge" :class="'role-' + user.role.toLowerCase()">{{ user.role }}</span>
              <span class="status-badge" :class="'status-' + user.status.toLowerCase()">{{ user.status }}</span>
            </div>
            <p class="text-muted text-xs mt-1">Joined: {{ new Date(user.created_at).toLocaleDateString() }}</p>
          </div>
        </div>

        <div class="actions flex gap-3">
          <template v-if="user.status === 'PENDING'">
            <button @click="approveUser(user.username)" class="btn btn-primary btn-sm">
              <i class="fas fa-check"></i> Approve
            </button>
            <button @click="openDeclineModal(user)" class="btn btn-danger btn-sm">
              <i class="fas fa-times"></i> Decline
            </button>
          </template>
          <template v-else>
            <button @click="openEditModal(user)" class="btn btn-secondary btn-sm">
              <i class="fas fa-edit"></i> Edit
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- Decline Modal -->
    <Teleport to="body">
      <div v-if="showDeclineModal" class="modal-overlay fixed inset-0 z-[1000] flex items-center justify-center p-4">
        <div class="modal-content glass-panel p-8 w-full max-w-md animate-pop">
          <h2 class="text-2xl font-bold text-white mb-6">Decline Application</h2>
          <div class="form-group mb-6 text-secondary">
             Are you sure you want to decline the registration for @{{ targetUser.username }}?
          </div>
          <div class="flex justify-end gap-4">
            <button @click="showDeclineModal = false" class="btn btn-ghost">Cancel</button>
            <button @click="confirmDecline" class="btn btn-danger">
              Confirm Decline
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Edit Modal -->
    <Teleport to="body">
      <div v-if="showEditModal" class="modal-overlay fixed inset-0 z-[1000] flex items-center justify-center p-4">
        <div class="modal-content glass-panel p-8 w-full max-w-md animate-pop">
          <h2 class="text-2xl font-bold text-white mb-6">Edit User Access: {{ editingUser.username }}</h2>
          
          <div class="space-y-6">
            <div class="form-group">
              <label class="text-secondary text-sm">Role</label>
              <select v-model="editForm.role" class="liquid-input w-full">
                <option value="USER">USER</option>
                <option value="AD">AD</option>
                <option value="OP">OP</option>
              </select>
            </div>
             <div class="form-group">
              <label class="text-secondary text-sm">Status</label>
              <select v-model="editForm.status" class="liquid-input w-full">
                <option value="PENDING">PENDING</option>
                <option value="ACTIVE">ACTIVE</option>
                <option value="DECLINED">DECLINED</option>
              </select>
            </div>
          </div>

          <div class="flex justify-end gap-4 mt-8">
            <button @click="showEditModal = false" class="btn btn-ghost">Cancel</button>
            <button @click="saveUserChanges" class="btn btn-primary" :disabled="isSaving">
              <i v-if="isSaving" class="fas fa-spinner fa-spin"></i>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const currentTab = ref('pending')
const searchQuery = ref('')
const roleFilter = ref('')
const isLoading = ref(false)
const isSaving = ref(false)
const users = ref([])

const tabs = [
  { id: 'pending', label: 'Pending Requests' },
  { id: 'active', label: 'Active Users' },
  { id: 'all', label: 'All Users' }
]

const pendingUsers = computed(() => users.value.filter(u => u.status === 'PENDING'))
const activeUsers = computed(() => users.value.filter(u => u.status === 'ACTIVE'))

const filteredUsers = computed(() => {
  let list = []
  if (currentTab.value === 'pending') list = pendingUsers.value
  else if (currentTab.value === 'active') list = activeUsers.value
  else list = users.value

  if (roleFilter.value) {
    list = list.filter(u => u.role === roleFilter.value)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(u => 
      u.username.toLowerCase().includes(q) || 
      (u.display_name && u.display_name.toLowerCase().includes(q))
    )
  }

  return list
})

const fetchUsers = async () => {
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/user/admin/users', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    if (response.ok) {
      users.value = data.users
    }
  } catch (err) {
    console.error('Failed to fetch users:', err)
  } finally {
    isLoading.value = false
  }
}

const approveUser = async (username) => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/user/admin/users/${username}/approve`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      // Find and update local state
      const user = users.value.find(u => u.username === username)
      if (user) user.status = 'ACTIVE'
    }
  } catch (err) {
    console.error('Failed to approve user:', err)
  }
}

// Decline Logic
const showDeclineModal = ref(false)
const targetUser = ref(null)

const openDeclineModal = (user) => {
  targetUser.value = user
  showDeclineModal.value = true
}

const confirmDecline = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/user/admin/users/${targetUser.value.username}/decline`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    if (response.ok) {
      const user = users.value.find(u => u.username === targetUser.value.username)
      if (user) {
        user.status = 'DECLINED'
      }
      showDeclineModal.value = false
    }
  } catch (err) {
    console.error('Failed to decline user:', err)
  }
}

// Edit Logic
const showEditModal = ref(false)
const editingUser = ref(null)
const editForm = reactive({
  role: '',
  status: ''
})

const openEditModal = (user) => {
  editingUser.value = user
  editForm.role = user.role
  editForm.status = user.status
  showEditModal.value = true
}

const saveUserChanges = async () => {
  isSaving.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/user/admin/users/${editingUser.value.username}`, {
      method: 'PATCH',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(editForm)
    })
    if (response.ok) {
      const updatedData = await response.json()
      // Refresh or merge changes
      const index = users.value.findIndex(u => u.username === editingUser.value.username)
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...editForm }
      }
      showEditModal.value = false
    }
  } catch (err) {
    console.error('Failed to update user:', err)
  } finally {
    isSaving.value = false
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.tab-btn {
  font-weight: 600;
  font-size: 0.95rem;
}

.active-tab {
  background: var(--primary-color);
  color: white;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
}

.inactive-tab {
  background: var(--glass-bg-secondary);
  color: var(--text-secondary);
}

.inactive-tab:hover {
  background: var(--glass-bg-hover);
}

.badge-count {
  background: #ef4444;
  color: white;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
}

.role-badge, .status-badge {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 2px 10px;
  border-radius: 20px;
  text-transform: uppercase;
}

.role-op { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.role-ad { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
.role-user { background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }

.status-active { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.status-pending { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.status-declined { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

.modal-overlay {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
}

.modal-content {
  border: 1px solid var(--glass-border);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.animate-pop {
  animation: pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes pop {
  0% { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.btn-ghost {
  color: var(--text-secondary);
}
.btn-ghost:hover {
  background: var(--glass-bg-hover);
}
</style>
