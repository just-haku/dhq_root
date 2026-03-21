<template>
  <div class="order-center-create p-6 max-w-5xl mx-auto">
    <div class="mb-8">
      <button class="text-primary hover:underline mb-2 flex items-center gap-2" @click="$router.push('/order-center')">
        <i class="fas fa-arrow-left"></i> Back to Dashboard
      </button>
      <h1 class="text-3xl font-bold gradient-text">Create New Order</h1>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Form Section -->
      <div class="lg:col-span-2 flex flex-col gap-6">
        <div class="glass-card p-6 relative z-20">
          <h2 class="text-xl font-bold mb-6 flex items-center gap-2">
            <i class="fas fa-info-circle text-primary"></i> Basic Information
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="form-group">
              <label>Order Name</label>
              <input v-model="form.name" type="text" placeholder="e.g., Campaign Alpha Views" class="form-input" />
            </div>
            <div class="form-group">
              <label>Target Link</label>
              <input v-model="form.target_link" type="url" placeholder="https://..." class="form-input" />
            </div>
            
            <div class="form-group col-span-1 md:col-span-2">
              <label>Select Service</label>
              
              <div class="flex flex-col gap-4">
                <!-- Platform Tier -->
                <div class="custom-dropdown" v-click-outside="() => showPlatforms = false">
                  <div class="dropdown-trigger" @click="showPlatforms = !showPlatforms" :class="{ 'active': selectedPlatform }">
                    <div v-if="selectedPlatform" class="flex items-center gap-2">
                      <span v-html="getPlatformIcon(selectedPlatform)" class="text-lg"></span>
                      <span class="font-bold">{{ selectedPlatform }}</span>
                    </div>
                    <span v-else class="text-muted">Platform...</span>
                    <i class="fas fa-chevron-down ml-auto transition-transform" :class="{ 'rotate-180': showPlatforms }"></i>
                  </div>
                  <div v-if="showPlatforms" class="dropdown-menu">
                    <div v-for="platform in platforms" :key="platform" 
                         class="service-item" @click="selectPlatform(platform)">
                      <span v-html="getPlatformIcon(platform)" class="platform-icon-small"></span>
                      <span class="text-sm font-bold">{{ platform }}</span>
                    </div>
                  </div>
                </div>

                <!-- Category Tier -->
                <div class="custom-dropdown" v-click-outside="() => showCategories = false" :class="{ 'opacity-50 pointer-events-none': !selectedPlatform }">
                  <div class="dropdown-trigger" @click="showCategories = !showCategories" :class="{ 'active': selectedCategory }">
                    <span v-if="selectedCategory" class="font-bold truncate">{{ selectedCategory }}</span>
                    <span v-else class="text-muted">Category...</span>
                    <i class="fas fa-chevron-down ml-auto transition-transform" :class="{ 'rotate-180': showCategories }"></i>
                  </div>
                  <div v-if="showCategories" class="dropdown-menu">
                    <div v-for="cat in availableCategories" :key="cat" 
                         class="service-item" @click="selectCategory(cat)">
                      <span class="text-sm font-bold">{{ cat }}</span>
                    </div>
                  </div>
                </div>

                <!-- Specific Service Tier -->
                <div class="custom-dropdown" v-click-outside="() => showSpecificServices = false" :class="{ 'opacity-50 pointer-events-none': !selectedCategory }">
                  <div class="dropdown-trigger" @click="showSpecificServices = !showSpecificServices" :class="{ 'active': selectedService }">
                    <div v-if="selectedService" class="truncate">
                      <span class="font-bold">{{ selectedService.name }}</span>
                    </div>
                    <span v-else class="text-muted">Service...</span>
                    <i class="fas fa-chevron-down ml-auto transition-transform" :class="{ 'rotate-180': showSpecificServices }"></i>
                  </div>
                  <div v-if="showSpecificServices" class="dropdown-menu">
                    <div class="p-2 sticky top-0 bg-slate-900/80 backdrop-blur-md z-10 border-b border-slate-700">
                      <input v-model="serviceSearch" type="text" placeholder="Search in category..." class="form-input text-sm py-1" @click.stop />
                    </div>
                    <div v-for="service in filteredSpecificServices" :key="service.service" 
                         class="service-item relative" @click="selectService(service)">
                      <div class="flex-grow pr-16">
                        <div class="text-sm font-bold">{{ service.name }}</div>
                        <div class="text-[10px] text-secondary flex items-center gap-3">
                          <span>ID: {{ service.service }}</span>
                          <span class="text-primary font-mono font-bold">${{ service.rate }}/1k</span>
                        </div>
                      </div>
                      <div v-if="service.best_seller" class="absolute top-2 right-2 border border-red-500/50 text-[8px] px-1 rounded text-red-500 font-bold uppercase">
                        Best Seller
                      </div>
                    </div>
                  </div>
                </div>

              <!-- Service Rate Summary -->
              <div v-if="selectedService" class="mt-3 p-3 rounded-lg bg-primary/5 border border-primary/10 flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                    <i class="fas fa-calculator"></i>
                  </div>
                  <div>
                    <div class="text-[10px] text-secondary uppercase font-bold tracking-wider">Service Rate</div>
                    <div class="text-sm font-mono font-bold">${{ selectedService.rate }} <span class="text-xs text-secondary font-normal">/ 1,000 units</span></div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-[10px] text-secondary uppercase font-bold tracking-wider">Est. Sub-Order ({{ form.step_mins }}m)</div>
                  <div class="text-sm font-mono font-bold text-primary">~${{ ((form.total_qty / ( (form.total_time * (form.time_unit === 'Hours' ? 60 : form.time_unit === 'Days' ? 1440 : 1)) / form.step_mins )) / 1000 * selectedService.rate).toFixed(3) }}</div>
                </div>
              </div>
              </div>
            </div>

            <div class="form-group col-span-1 md:col-span-2">
              <div class="flex justify-between items-end mb-2">
                <label class="mb-0">Select API Provider (Server)</label>
                <div v-if="serverBalance" class="flex items-center gap-2">
                  <div v-if="serverBalanceError" class="text-[10px] text-red-500 flex items-center gap-1">
                    <i class="fas fa-exclamation-triangle"></i>
                    {{ serverBalanceError }}
                    <button @click="$router.push('/settings?tab=security&focus=api')" class="underline hover:text-red-400">Fix in Settings</button>
                  </div>
                  <div v-else class="text-xs font-mono text-primary flex items-center gap-2">
                    Balance: <span class="font-bold">${{ serverBalance }}</span>
                    <button @click="fetchBalance" class="hover:text-white transition-colors" :class="{ 'fa-spin': fetchingBalance }" title="Refresh Balance">
                      <i class="fas fa-sync-alt"></i>
                    </button>
                  </div>
                </div>
              </div>
              <div class="custom-dropdown" v-click-outside="() => showServers = false">
                <div class="dropdown-trigger" @click="showServers = !showServers">
                  <div v-if="selectedServerObj" class="flex items-center gap-3">
                    <i :class="selectedServerObj.name === 'internal_api_server' ? 'fas fa-shield-alt text-success' : 'fas fa-server text-primary'"></i>
                    <div>
                      <div class="font-bold">{{ selectedServerObj.display_name }}</div>
                    </div>
                  </div>
                  <div v-else class="flex items-center gap-3">
                    <i class="fas fa-server text-primary"></i>
                    <div>
                      <div class="font-bold text-muted">Select API Provider...</div>
                    </div>
                  </div>
                  <i class="fas fa-chevron-down ml-auto transition-transform" :class="{ 'rotate-180': showServers }"></i>
                </div>
                
                <div v-if="showServers" class="dropdown-menu">
                  <div class="category-title">Available Providers</div>
                  <div v-for="server in sortedActiveServers" :key="server.id" 
                       class="service-item" @click="selectServer(server)">
                    <i :class="server.name === 'internal_api_server' ? 'fas fa-shield-alt text-success' : 'fas fa-server text-primary'" class="w-6 text-center"></i>
                    <div class="flex-grow">
                      <div class="text-sm font-bold">{{ server.display_name }}</div>
                      <div v-if="server.name === 'internal_api_server'" class="text-[10px] text-secondary">
                        Authenticated via your DHQ password
                      </div>
                    </div>
                  </div>

                  <div v-if="isOP" class="p-3 border-t border-slate-700/50 mt-2">
                    <button class="btn btn-sm btn-primary w-full flex items-center justify-center gap-2" 
                            @click="$router.push('/operator/server-settings?add=true')">
                      <i class="fas fa-plus-circle"></i> Add API Server
                    </button>
                  </div>
                </div>

                <!-- Insufficient Balance Warning -->
                <div v-if="serverBalance && !serverBalanceError && estimatedCost > parseFloat(serverBalance)" 
                     class="mt-3 p-3 rounded-lg flex items-center justify-between animate-pulse"
                     :class="selectedServerObj?.is_external ? 'bg-amber-500/10 border border-amber-500/20' : 'bg-red-500/10 border border-red-500/20'">
                  <div class="flex items-center gap-3" :class="selectedServerObj?.is_external ? 'text-amber-500' : 'text-red-500'">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div class="text-xs">
                      <div class="font-bold">Insufficient Balance</div>
                      <div v-if="selectedServerObj?.is_external">Please top-up on the original provider's website.</div>
                      <div v-else>Your balance is lower than the total estimated cost.</div>
                    </div>
                  </div>
                  <button v-if="!selectedServerObj?.is_external" 
                          @click="$router.push('/shop?tab=api-dollar&focus=true')" 
                          class="btn btn-sm bg-red-500 hover:bg-red-600 border-none text-white px-4">
                    Recharge
                  </button>
                  <a v-else :href="selectedServerObj.base_url" target="_blank" 
                     class="btn btn-sm bg-amber-500 hover:bg-amber-600 border-none text-white px-4 flex items-center gap-2">
                    Visit Provider <i class="fas fa-external-link-alt text-[10px]"></i>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <h2 class="text-xl font-bold mb-6 flex items-center gap-2">
            <i class="fas fa-chart-line text-primary"></i> Scheduling & Distribution
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="form-group">
              <label>Total Quantity</label>
              <input v-model.number="form.total_qty" type="number" class="form-input" @input="updatePreview" />
            </div>
            <div class="form-group">
              <label>Distribution Period</label>
              <div class="flex gap-2">
                <input v-model.number="form.total_time" type="number" class="form-input" @input="updatePreview" />
                <select v-model="form.time_unit" class="form-input w-24" @change="updatePreview">
                  <option>Minutes</option>
                  <option>Hours</option>
                  <option>Days</option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label>Step Interval (Minutes)</label>
              <input v-model.number="form.step_mins" type="number" class="form-input" @input="updatePreview" />
            </div>
            <div class="form-group">
              <label>Graph Type</label>
              <select v-model="form.graph_type" class="form-input" @change="updatePreview">
                <option>Linear</option>
                <option>Exponential</option>
                <option>Viral Bell Curve</option>
                <option>Random</option>
              </select>
            </div>
            
            <div class="form-group col-span-1 md:col-span-2">
              <label>Tolerance / Noise (%)</label>
              <input v-model.number="form.tolerance_pct" type="range" min="0" max="50" class="w-full accent-primary" @input="updatePreview" />
              <div class="flex justify-between text-xs text-muted mt-1">
                <span>0% (Precise)</span>
                <span>Current: {{ form.tolerance_pct }}%</span>
                <span>50% (Chaotic)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Preview Section -->
      <div class="flex flex-col gap-6">
        <div class="glass-card p-6 sticky top-6">
          <h2 class="text-lg font-bold mb-4">Cost Summary</h2>
          <div class="space-y-3 mb-6">
            <div class="flex justify-between text-sm">
              <span class="text-secondary">Quantity</span>
              <span>{{ formatNumber(form.total_qty) }}</span>
            </div>
            <div class="border-t border-slate-700 pt-3 flex justify-between font-bold">
              <span>Estimated Total</span>
              <span class="text-primary text-xl">${{ estimatedCost.toFixed(2) }}</span>
            </div>
          </div>

          <div class="mb-6 h-40">
            <canvas id="previewChart"></canvas>
          </div>

          <button class="btn btn-primary w-full py-3 text-lg font-bold" 
                  :disabled="!isValid || submitting"
                  @click="submitOrder">
            <span v-if="submitting"><i class="fas fa-spinner fa-spin"></i> Submitting...</span>
            <span v-else>Launch Expansion <i class="fas fa-paper-plane ml-2"></i></span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet, apiPost, showAlert } from '@/utils/api'
import { useUserStore } from '@/stores/userStore'
import Chart from 'chart.js/auto'

const router = useRouter()
const submitting = ref(false)
const userStore = useUserStore()
const serviceSearch = ref('')
const cachedServices = ref([])
const activeServers = ref([])
const serverBalance = ref(null)
const serverBalanceError = ref(null)
const fetchingBalance = ref(false)
const chart = ref(null)

const showPlatforms = ref(false)
const showCategories = ref(false)
const showSpecificServices = ref(false)
const showServers = ref(false)

const selectedPlatform = ref(null)
const selectedCategory = ref(null)
const selectedService = ref(null)

const isOP = computed(() => userStore.role === 'OP')
const selectedServerObj = computed(() => activeServers.value.find(s => s.id === form.api_server_id))

const sortedActiveServers = computed(() => {
  return [...activeServers.value].sort((a, b) => (a.priority || 0) - (b.priority || 0))
})

const form = reactive({
  name: '',
  unit_label: 'Units',
  target_link: '',
  total_qty: 1000,
  total_time: 12,
  time_unit: 'Hours',
  step_mins: 60,
  tolerance_pct: 10,
  graph_type: 'Linear',
  api_service_id: '',
  api_server_id: ''
})

const handleOutsideClick = (event, el) => {
    if (el && !el.contains(event.target)) {
        showPlatforms.value = false;
        showCategories.value = false;
        showSpecificServices.value = false;
        showServers.value = false;
    }
}

const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event, el);
      }
    };
    document.addEventListener("click", el.clickOutsideEvent);
  },
  unmounted(el) {
    document.removeEventListener("click", el.clickOutsideEvent);
  },
};

const getPlatformIcon = (category) => {
  const cat = (category || '').toLowerCase()
  if (cat.includes('youtube')) return '<i class="fab fa-youtube text-red-500"></i>'
  if (cat.includes('facebook')) return '<i class="fab fa-facebook text-blue-500"></i>'
  if (cat.includes('instagram')) return '<i class="fab fa-instagram text-pink-500"></i>'
  if (cat.includes('tiktok')) return '<i class="fab fa-tiktok text-white"></i>'
  if (cat.includes('twitter') || cat.includes(' x ')) return '<i class="fab fa-twitter text-sky-400"></i>'
  return '<i class="fas fa-globe text-secondary"></i>'
}

const platforms = computed(() => {
  const p = new Set()
  cachedServices.value.forEach(s => {
    if (s.platform) p.add(s.platform)
    else {
      // Fallback platform detection
      const cat = s.category.toLowerCase()
      if (cat.includes('youtube')) p.add('YouTube')
      else if (cat.includes('facebook')) p.add('Facebook')
      else if (cat.includes('instagram')) p.add('Instagram')
      else if (cat.includes('tiktok')) p.add('TikTok')
      else if (cat.includes('twitter') || cat.includes(' x ')) p.add('Twitter')
      else p.add('Other')
    }
  })
  return Array.from(p).sort()
})

const availableCategories = computed(() => {
  if (!selectedPlatform.value) return []
  const cats = new Set()
  cachedServices.value.forEach(s => {
    const p = s.platform || (s.category.toLowerCase().includes(selectedPlatform.value.toLowerCase()) ? selectedPlatform.value : null)
    if (p === selectedPlatform.value) {
      cats.add(s.category)
    }
  })
  return Array.from(cats).sort()
})

const filteredSpecificServices = computed(() => {
  if (!selectedCategory.value) return []
  const search = serviceSearch.value.toLowerCase()
  return cachedServices.value.filter(s => 
    s.category === selectedCategory.value &&
    (s.name.toLowerCase().includes(search) || s.service.toString().includes(search))
  )
})

const selectPlatform = (platform) => {
  selectedPlatform.value = platform
  selectedCategory.value = null
  selectedService.value = null
  showPlatforms.value = false
  showCategories.value = true
}

const selectCategory = (category) => {
  selectedCategory.value = category
  selectedService.value = null
  showCategories.value = false
  showSpecificServices.value = true
}

const selectService = (service) => {
  selectedService.value = service
  form.api_service_id = service.service
  form.unit_label = service.category
  showSpecificServices.value = false
  updatePreview()
}

const selectServer = (server) => {
  form.api_server_id = server ? server.id : ''
  showServers.value = false
  if (form.api_server_id) {
    fetchBalance()
  } else {
    serverBalance.value = null
    serverBalanceError.value = null
  }
}

const estimatedCost = computed(() => {
  if (!selectedService.value) return 0
  return (form.total_qty / 1000) * parseFloat(selectedService.value.rate)
})

const isValid = computed(() => {
  return form.name && form.target_link && form.total_qty > 0 && form.api_service_id
})

const updatePreview = () => {
    if (!chart.value) return;
    
    // Simple math simulation for visual feedback
    const num_steps = 10;
    const labels = Array.from({length: num_steps}, (_, i) => i);
    let data = [];
    
    if (form.graph_type === 'Linear') data = labels.map(() => 10);
    else if (form.graph_type === 'Exponential') data = labels.map((_, i) => Math.pow(1.5, i));
    else if (form.graph_type === 'Viral Bell Curve') data = labels.map((_, i) => Math.exp(-Math.pow(i - 6, 2) / 4) * 20);
    else data = labels.map(() => Math.random() * 20);

    chart.value.data.labels = labels;
    chart.value.data.datasets[0].data = data;
    chart.value.update('none');
}

const initChart = () => {
  const ctx = document.getElementById('previewChart')
  if (!ctx) return
  
  chart.value = markRaw(new Chart(ctx, {
    type: 'line',
    data: {
      labels: Array.from({length: 10}, (_, i) => i),
      datasets: [{
        label: 'Relative Quantity',
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.1)',
        data: Array(10).fill(10),
        fill: true,
        tension: 0.4,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { display: false },
        y: { display: false }
      }
    }
  }))
  updatePreview()
}

const fetchServices = async () => {
  try {
    const data = await apiGet('/order-center/services/cached')
    cachedServices.value = data
  } catch (error) {
    console.error('Failed to fetch services:', error)
  }
}

const fetchServers = async () => {
  try {
    const data = await apiGet('/order-center/api-servers/active')
    activeServers.value = data
  } catch (error) {
    console.error('Failed to fetch servers:', error)
  }
}

const fetchBalance = async () => {
  if (fetchingBalance.value) return
  fetchingBalance.value = true
  serverBalanceError.value = null
  try {
    let url = '/order-center/balance'
    if (form.api_server_id) url += `?server_id=${form.api_server_id}`
    const data = await apiGet(url)
    
    if (data.error) {
        serverBalanceError.value = data.error
        serverBalance.value = data.balance || '0.00'
    } else {
        serverBalance.value = data.balance
        serverBalanceError.value = null
    }
  } catch (error) {
    console.error('Failed to fetch balance:', error)
    serverBalance.value = '0.00'
    serverBalanceError.value = 'Connection failed'
  } finally {
    fetchingBalance.value = false
  }
}

const submitOrder = async () => {
  submitting.value = true
  try {
    const payload = { ...form, est_cost: estimatedCost.value }
    const result = await apiPost('/order-center/create', payload)
    showAlert('Success', 'Expansion order launched successfully', 'success', '🚀')
    router.push(`/order-center/${result.order_id}`)
  } catch (error) {
    console.error('Submission failed:', error)
  } finally {
    submitting.value = false
  }
}

const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

onMounted(() => {
  fetchServices()
  fetchServers()
  fetchBalance()
  setTimeout(initChart, 100)
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

.custom-dropdown {
  position: relative;
}

.dropdown-trigger {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.5rem;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(30px) saturate(200%);
  -webkit-backdrop-filter: blur(30px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 999;
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5);
}

.category-title {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  font-size: 0.7rem;
  text-transform: uppercase;
  font-weight: 800;
  color: var(--text-muted);
}

.service-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: background 0.2s;
}

.service-item:hover {
  background: var(--glass-bg-hover);
}

.platform-icon { font-size: 1.5rem; }
.platform-icon-small { font-size: 1.1rem; width: 24px; text-align: center; }

.gradient-text {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
