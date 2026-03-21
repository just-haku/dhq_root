<template>
  <div class="operator-settings p-6 max-w-4xl mx-auto">
    <div class="mb-8 text-center">
      <h1 class="text-4xl font-bold gradient-text mb-2">Operator Control Center</h1>
      <p class="text-secondary">Global server configuration and resilient worker settings</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Server Configuration -->
      <div class="glass-card p-6">
        <h2 class="text-xl font-bold mb-6 flex items-center gap-2">
          <i class="fas fa-server text-primary"></i> Server Configuration
        </h2>
        
        <div class="space-y-6">
          <div class="form-group">
            <label>Server Timezone</label>
            <select v-model="settings.timezone" class="form-input">
              <option v-for="tz in timezones" :key="tz" :value="tz">{{ tz }}</option>
            </select>
            <p class="text-xs text-muted mt-1">All schedules will sync to this master clock.</p>
          </div>

          <div class="form-group">
            <label>Status Sync Interval (Minutes)</label>
            <div class="flex items-center gap-4">
              <input v-model.number="settings.status_sync_interval" type="number" min="1" max="60" class="form-input" />
              <span class="text-sm text-secondary whitespace-nowrap">Every {{ settings.status_sync_interval }}m</span>
            </div>
          </div>

          <div class="pt-4 border-t border-slate-700/50">
            <label class="text-xs font-bold text-primary uppercase mb-2 block">Quick Actions</label>
            <button class="btn btn-sm btn-outline-primary w-full flex items-center justify-center gap-2" @click="openServerModal()">
              <i class="fas fa-plus"></i> New API Provider
            </button>
          </div>
        </div>
      </div>

      <!-- Mock API & Resilience -->
      <div class="glass-card p-6">
        <h2 class="text-xl font-bold mb-6 flex items-center gap-2">
          <i class="fas fa-vial text-warning"></i> Resilience Testing
        </h2>
        
        <div class="space-y-6">
          <div class="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
            <div>
              <div class="font-bold">Internal Mock API</div>
              <div class="text-xs text-muted">Bypass external providers for testing</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="settings.mock_api_enabled" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          <div class="form-group" :class="{ 'opacity-50 pointer-events-none': !settings.mock_api_enabled }">
            <label>Simulated Success Rate (%)</label>
            <input v-model.number="settings.mock_success_rate" type="range" min="0" max="100" class="w-full accent-primary" />
            <div class="flex justify-between text-xs font-mono mt-1">
              <span class="text-danger">0% (Fail-safe Test)</span>
              <span class="text-primary font-bold">{{ settings.mock_success_rate }}%</span>
              <span class="text-success">100% (Reliable)</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- API Server Management -->
      <div class="glass-card col-span-1 md:col-span-2">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold flex items-center gap-2">
            <i class="fas fa-network-wired text-primary"></i> External API Providers
          </h2>
          <button class="btn btn-sm btn-primary" @click="openServerModal()">
            <i class="fas fa-plus"></i> Add Provider
          </button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="text-xs uppercase tracking-wider text-muted border-b border-slate-700/50">
                <th class="py-3 px-4">Display Name</th>
                <th class="py-3 px-4">Base URL</th>
                <th class="py-3 px-4">Status</th>
                <th class="py-3 px-4">Priority</th>
                <th class="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/30">
              <tr v-for="server in apiServers" :key="server.id" class="hover:bg-slate-800/20">
                <td class="py-3 px-4">
                  <div class="font-bold">{{ server.display_name }}</div>
                  <div class="text-[10px] opacity-40 font-mono">{{ server.name }}</div>
                </td>
                <td class="py-3 px-4 text-xs font-mono opacity-60">{{ server.base_url }}</td>
                <td class="py-3 px-4">
                  <span :class="server.is_active ? 'text-success' : 'text-danger'" class="flex items-center gap-1 text-xs">
                    <i class="fas" :class="server.is_active ? 'fa-check-circle' : 'fa-times-circle'"></i>
                    {{ server.is_active ? 'ACTIVE' : 'INACTIVE' }}
                  </span>
                </td>
                <td class="py-3 px-4 text-sm">{{ server.priority }}</td>
                <td class="py-3 px-4 text-right">
                  <div class="flex justify-end gap-1">
                    <button class="p-2 text-primary hover:bg-slate-700/50 rounded" @click="openServerModal(server)">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="p-2 text-danger hover:bg-red-900/20 rounded" @click="deleteServer(server.id)">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="apiServers.length === 0">
                <td colspan="6" class="py-12 text-center text-muted">
                  No external providers configured. Add one to enable multi-server distribution.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- API Server Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div class="glass-panel w-full max-w-lg p-8">
        <h2 class="text-2xl font-bold mb-6 gradient-text">
          {{ editingServer ? 'Edit API Provider' : 'Add New Provider' }}
        </h2>
        
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="form-group col-span-2">
            <label>Provider Name (Internal ID)</label>
            <input v-model="serverForm.name" type="text" placeholder="e.g. provider_high_speed" class="form-input" />
          </div>
          <div class="form-group col-span-2">
            <label>Display Name (User Visible)</label>
            <input v-model="serverForm.display_name" type="text" placeholder="e.g. Premium High-Speed Server" class="form-input" />
          </div>
          <div class="form-group col-span-2">
            <label>API Base URL</label>
            <input v-model="serverForm.base_url" type="url" placeholder="https://..." class="form-input" />
          </div>
          <div class="form-group col-span-2">
            <label>System-Wide API Key (Default Fallback)</label>
            <div class="relative">
              <input 
                v-model="serverForm.api_key" 
                :type="showModalKey ? 'text' : 'password'" 
                class="form-input pr-12" 
                placeholder="Key for all users without personal keys..." 
              />
              <button 
                @click="showModalKey = !showModalKey" 
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
              >
                <i class="fas" :class="showModalKey ? 'fa-eye-slash' : 'fa-eye'"></i>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label>Priority (Lower = First)</label>
            <input v-model.number="serverForm.priority" type="number" class="form-input" />
          </div>
          
          <div class="col-span-2 flex items-center gap-6 p-3 bg-slate-800/30 rounded-lg">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="serverForm.is_active" class="form-checkbox text-primary rounded border-slate-600 bg-slate-800">
              <span class="text-sm">Active & Enabled</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="serverForm.is_external" class="form-checkbox text-primary rounded border-slate-600 bg-slate-800">
              <span class="text-sm">External (Requires API Key)</span>
            </label>
          </div>
        </div>

        <div class="flex gap-4">
          <button class="btn btn-secondary flex-1" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary flex-1" @click="saveServer" :disabled="modalSaving">
            {{ modalSaving ? 'Saving...' : 'Save Provider' }}
          </button>
        </div>
      </div>
    </div>

    <div class="mt-8 flex justify-center">
      <button class="btn btn-primary px-12 py-3 text-lg font-bold shadow-lg shadow-primary/20" 
              @click="saveSettings" :disabled="saving">
        <span v-if="saving"><i class="fas fa-spinner fa-spin"></i> Saving...</span>
        <span v-else>Apply Global Changes</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiGet, apiPost, showAlert } from '@/utils/api'

const route = useRoute()

const saving = ref(false)
const timezones = ['GMT-12', 'GMT-11', 'GMT-10', 'GMT-9', 'GMT-8', 'GMT-7', 'GMT-6', 'GMT-5', 'GMT-4', 'GMT-3', 'GMT-2', 'GMT-1', 'GMT+0', 'GMT+1', 'GMT+2', 'GMT+3', 'GMT+4', 'GMT+5', 'GMT+6', 'GMT+7', 'GMT+8', 'GMT+9', 'GMT+10', 'GMT+11', 'GMT+12']

const settings = reactive({
  timezone: 'GMT+7',
  status_sync_interval: 5,
  mock_api_enabled: false,
  mock_success_rate: 100
})

const fetchSettings = async () => {
  try {
    const data = await apiGet('/order-center/operator/settings')
    Object.assign(settings, data)
  } catch (error) {}
}

const apiServers = ref([])
const fetchServers = async () => {
  try {
    apiServers.value = await apiGet('/order-center/operator/api-servers')
  } catch (error) {}
}

const showModal = ref(false)
const modalSaving = ref(false)
const editingServer = ref(null)
const showModalKey = ref(false)
const serverForm = reactive({
  name: '',
  display_name: '',
  base_url: '',
  api_key: '',
  is_active: true,
  is_external: true,
  rate_per_1000: 0.0,
  priority: 1
})

const openServerModal = (server = null) => {
  editingServer.value = server
  if (server) {
    Object.assign(serverForm, server)
  } else {
    Object.assign(serverForm, {
      name: '', display_name: '', base_url: '', api_key: '', 
      is_active: true, is_external: true, 
      rate_per_1000: 0.0, priority: 1
    })
  }
  showModal.value = true
}

const saveServer = async () => {
  modalSaving.value = true
  try {
    let url = '/order-center/operator/api-servers'
    if (editingServer.value) url += `?server_id=${editingServer.value.id}`
    await apiPost(url, serverForm)
    await fetchServers()
    showModal.value = false
    showAlert('Success', 'API Server updated', 'success', '🌐')
  } catch (error) {
    showAlert('Error', 'Failed to save server', 'danger', '❌')
  } finally {
    modalSaving.value = false
  }
}

const deleteServer = async (id) => {
  if (!confirm('Are you sure you want to remove this provider?')) return
  try {
    await apiPost(`/order-center/operator/api-servers/${id}/delete`) // We should probably use DELETE method if implemented
    // Backend implemented delete at router.delete("/operator/api-servers/{server_id}")
    // But our api utility might only support get/post. I'll use a hack or update api utility.
    // wait, I can use apiPost with a custom method or just use raw fetch if needed.
    // Actually, I'll just implemented it as POST /{id}/delete in backend too for safety.
    await fetchServers()
  } catch (error) {}
}

const saveSettings = async () => {
  saving.value = true
  try {
    await apiPost('/order-center/operator/settings', settings)
    showAlert('Success', 'Global settings updated', 'success', '⚙️')
  } catch (error) {
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchSettings()
  await fetchServers()
  
  if (route.query.add === 'true') {
    openServerModal()
  }
})
</script>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-input {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: white;
  width: 100%;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.gradient-text {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
