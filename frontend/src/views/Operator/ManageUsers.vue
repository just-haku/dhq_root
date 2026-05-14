<template>
  <div class="manage-users p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-white flex items-center gap-3">
        <i class="fas fa-users-cog text-danger"></i>
        User & Access Management
      </h1>
    </div>

    <!-- Tabs -->
    <div class="flex gap-4 mb-6">
      <button 
        v-for="tab in ['Active Users', 'Pending Approvals']" 
        :key="tab"
        class="filter-tab"
        :class="{ active: currentTab === tab }"
        @click="currentTab = tab"
      >
        {{ tab }}
        <span v-if="tab === 'Pending Approvals' && pendingCount > 0" class="pending-badge">
          {{ pendingCount }}
        </span>
      </button>
    </div>

    <!-- User Table -->
    <div class="glass-panel overflow-hidden">
      <table class="dhq-table w-full">
        <thead>
          <tr>
            <th>Username</th>
            <th>Role</th>
            <th>Status</th>
            <th>Joined</th>
            <th>Quota</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="text-center py-8"><div class="spinner"></div></td></tr>
          <tr v-else-if="users.length === 0"><td colspan="6" class="text-center py-8 text-muted">No users found.</td></tr>
          <tr v-for="user in users" :key="user.id">
            <td>
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center font-bold">
                  {{ user.username[0].toUpperCase() }}
                </div>
                {{ user.username }}
              </div>
            </td>
            <td>
              <select v-model="user.role" class="dhq-select-small" @change="updateRole(user)">
                <option value="USER">USER</option>
                <option value="AD">AD</option>
                <option value="OP">OP</option>
              </select>
            </td>
            <td>
              <span class="status-badge" :class="'status-' + user.status.toLowerCase()">{{ user.status }}</span>
            </td>
            <td class="text-xs text-muted">{{ formatDate(user.created_at) }}</td>
            <td>
              <button class="btn-xs btn-secondary" @click="openQuotaModal(user)">
                <i class="fas fa-database mr-1"></i> Manage
              </button>
            </td>
            <td>
              <div class="flex gap-2">
                <button v-if="user.status === 'PENDING'" class="btn-icon text-success" @click="approveUser(user.id)" title="Approve">
                  <i class="fas fa-user-check"></i>
                </button>
                <button v-if="user.status === 'PENDING'" class="btn-icon text-danger" @click="rejectUser(user.id)" title="Reject">
                  <i class="fas fa-user-times"></i>
                </button>
                <button v-if="user.username !== 'haku'" class="btn-icon text-danger" @click="deleteUser(user.id)" title="Delete">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Quota Modal -->
    <div v-if="showQuotaModal" class="modal-overlay" @click.self="showQuotaModal = false">
      <div class="modal-content glass-panel p-6 w-[400px]">
        <h2 class="text-2xl font-bold mb-4 text-white">Manage Quota: {{ selectedUser?.username }}</h2>
        <div v-if="quotaLoading" class="py-8 text-center"><div class="spinner"></div></div>
        <div v-else class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Total Quota (GB)</label>
            <input type="number" v-model="userQuota.total" class="dhq-input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Additional Quota (GB)</label>
            <input type="number" v-model="userQuota.additional" class="dhq-input w-full" />
          </div>
          <div class="p-3 bg-slate-800 rounded-lg text-sm">
            <div class="flex justify-between mb-1">
              <span>Current Usage:</span>
              <span>{{ formatSize(userQuota.used) }}</span>
            </div>
            <div class="usage-bar">
              <div class="usage-fill" :style="{ width: userQuota.percent + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button class="btn btn-secondary" @click="showQuotaModal = false">Close</button>
          <button class="btn btn-primary" @click="saveQuota">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { apiGet, apiPut, apiDelete, showAlert } from '@/utils/api'

const currentTab = ref('Active Users')
const users = ref([])
const loading = ref(true)
const pendingCount = ref(0)
const showQuotaModal = ref(false)
const selectedUser = ref(null)
const userQuota = ref({ total: 30, additional: 0, used: 0, percent: 0 })
const quotaLoading = ref(false)

const fetchUsers = async () => {
  loading.value = true
  try {
    const endpoint = currentTab.value === 'Pending Approvals' ? '/admin/users/pending' : '/admin/users'
    const data = await apiGet(endpoint)
    users.value = data
    
    // Update pending count
    if (currentTab.value === 'Active Users') {
      const pendingData = await apiGet('/admin/users/pending')
      pendingCount.value = pendingData.length
    } else {
      pendingCount.value = data.length
    }
  } catch (error) {
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
}

watch(currentTab, fetchUsers)

const approveUser = async (id) => {
  try {
    await apiPut(`/admin/users/${id}`, { status: 'ACTIVE' })
    fetchUsers()
    showAlert('Approved', 'User account activated', 'success')
  } catch (error) {}
}

const rejectUser = async (id) => {
  if (!confirm('Reject this registration?')) return
  try {
    await apiPut(`/admin/users/${id}`, { status: 'DECLINED' })
    fetchUsers()
  } catch (error) {}
}

const updateRole = async (user) => {
  try {
    await apiPut(`/admin/users/${user.id}`, { role: user.role })
    showAlert('Updated', `Role for ${user.username} updated`, 'success')
  } catch (error) {}
}

const deleteUser = async (id) => {
  if (!confirm('Are you sure? This will permanently delete the user account.')) return
  try {
    await apiDelete(`/admin/users/${id}`)
    fetchUsers()
  } catch (error) {}
}

const openQuotaModal = async (user) => {
  selectedUser.value = user
  showQuotaModal.value = true
  quotaLoading.value = true
  try {
    const data = await apiGet(`/admin/users/${user.id}/quota`)
    userQuota.value = {
      total: data.total_quota / (1024*1024*1024),
      additional: data.additional_quota / (1024*1024*1024),
      used: data.used_space,
      percent: data.usage_percentage
    }
  } catch (error) {}
  finally { quotaLoading.value = false }
}

const saveQuota = async () => {
  try {
    await apiPut(`/admin/users/${selectedUser.value.id}/quota`, {
      total_quota: userQuota.value.total,
      additional_quota: userQuota.value.additional
    })
    showQuotaModal.value = false
    showAlert('Success', 'Quota updated', 'success')
  } catch (error) {}
}

const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString()

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(fetchUsers)
</script>

<style scoped>
.manage-users {
  max-width: 1200px;
  margin: 0 auto;
}

.dhq-table th {
  text-align: left;
  padding: 1rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  text-transform: uppercase;
}

.dhq-table td {
  padding: 1rem;
  border-top: 1px solid var(--glass-border);
}

.dhq-select-small {
  background: var(--bg-primary);
  border: 1px solid var(--glass-border);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.filter-tab {
  position: relative;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-muted);
  font-weight: 600;
  cursor: pointer;
}

.filter-tab.active {
  background: var(--glass-bg-hover);
  color: white;
  border-color: var(--danger-color);
}

.pending-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ef4444;
  color: white;
  font-size: 0.6rem;
  padding: 2px 6px;
  border-radius: 10px;
}

.usage-bar {
  width: 100%;
  height: 6px;
  background: #334155;
  border-radius: 3px;
  overflow: hidden;
}

.usage-fill {
  height: 100%;
  background: var(--primary-color);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.spinner {
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid var(--danger-color);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.status-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 800;
}
.status-active { color: #10b981; }
.status-pending { color: #f59e0b; }
.status-declined { color: #ef4444; }

@media (max-width: 768px) {
  .dhq-table {
    display: block;
    overflow-x: auto;
  }
}
</style>
