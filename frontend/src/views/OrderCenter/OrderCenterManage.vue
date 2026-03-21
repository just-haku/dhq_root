<template>
  <div class="order-center-manage p-6 max-w-7xl mx-auto" v-if="order">
    <!-- Header -->
    <div class="flex justify-between items-start mb-8">
      <div>
        <button class="text-primary hover:underline mb-2 flex items-center gap-2" @click="$router.push('/order-center')">
          <i class="fas fa-arrow-left"></i> All Orders
        </button>
        <h1 class="text-3xl font-bold">{{ order.name }}</h1>
        <p class="text-secondary truncate max-w-md">{{ order.target_link }}</p>
      </div>
      <div class="flex gap-3">
        <button v-if="order.status === 'Active'" class="btn btn-warning" @click="pauseOrder">
          <i class="fas fa-pause mr-2"></i> Pause Order
        </button>
        <button v-if="order.status === 'Paused'" class="btn btn-success" @click="resumeOrder">
          <i class="fas fa-play mr-2"></i> Resume Order
        </button>
        <button class="btn btn-secondary" @click="downloadPDF">
          <i class="fas fa-file-pdf mr-2"></i> Download PDF
        </button>
      </div>
    </div>

    <!-- Dashboard Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
      <div class="glass-card p-5 flex items-center gap-4">
        <div class="bg-primary/20 p-3 rounded-xl text-primary text-2xl">
          <i class="fas fa-tasks"></i>
        </div>
        <div>
          <div class="text-xs text-secondary uppercase font-bold">Progress</div>
          <div class="text-xl font-bold">{{ progress }}%</div>
        </div>
      </div>
      
      <div class="glass-card p-5 flex items-center gap-4">
        <div class="bg-warning/20 p-3 rounded-xl text-warning text-2xl">
          <i class="fas fa-dna"></i>
        </div>
        <div>
          <div class="text-xs text-secondary uppercase font-bold">Distribution</div>
          <div class="text-xl font-bold">{{ order.graph_type }}</div>
        </div>
      </div>

      <div class="glass-card p-5 flex items-center gap-4">
        <div class="bg-success/20 p-3 rounded-xl text-success text-2xl">
          <i class="fas fa-dollar-sign"></i>
        </div>
        <div>
          <div class="text-xs text-secondary uppercase font-bold">Spent / Est</div>
          <div class="text-xl font-bold">${{ order.actual_cost.toFixed(2) }} / ${{ order.est_cost.toFixed(2) }}</div>
        </div>
      </div>

      <div class="glass-card p-5">
        <div class="h-12">
            <canvas id="miniChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Sub-orders Table -->
    <div class="glass-card overflow-hidden">
      <div class="p-4 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/30">
        <h2 class="font-bold flex items-center gap-2">
          <i class="fas fa-list-ul text-primary"></i> Sub-Order Execution Queue
        </h2>
        <div class="text-xs text-secondary">
          Click "NOW!!!" to bypass schedule
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="bg-slate-900/50 text-secondary uppercase text-xs">
              <th class="p-4 w-10">#</th>
              <th class="p-4">Scheduled Time</th>
              <th class="p-4">Quantity</th>
              <th class="p-4">Internal Status</th>
              <th class="p-4">API Status</th>
              <th class="p-4 text-center">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-700/30">
            <tr v-for="sub in order.sub_orders" :key="sub.id" 
                class="hover:bg-primary/5 transition-colors"
                :class="{ 'opacity-50': sub.internal_status === 'Success' }">
              <td class="p-4 font-mono text-muted">{{ sub.ordinal }}</td>
              <td class="p-4">
                <div class="flex flex-col">
                  <span>{{ formatDate(sub.scheduled_time) }}</span>
                  <span class="text-xs text-muted">{{ formatTime(sub.scheduled_time) }}</span>
                </div>
              </td>
              <td class="p-4 font-bold">{{ formatNumber(sub.qty) }}</td>
              <td class="p-4">
                <span class="status-chip" :class="sub.internal_status.toLowerCase().replace(/ /g, '-')">
                  {{ sub.internal_status }}
                </span>
              </td>
              <td class="p-4">
                <span class="text-xs truncate max-w-xs block">{{ sub.api_status || '-' }}</span>
              </td>
              <td class="p-4 text-center">
                <button v-if="sub.internal_status === 'Pending'" 
                        class="btn-now" 
                        @click="forceExecution(sub.id)">
                  NOW!!!
                </button>
                <i v-else-if="sub.internal_status === 'Success'" class="fas fa-check-circle text-success text-lg"></i>
                <i v-else class="fas fa-clock text-muted"></i>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  
  <div v-else class="flex justify-center items-center h-64">
    <div class="loader"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, markRaw } from 'vue'
import { useRoute } from 'vue-router'
import { apiGet, apiPost, showAlert, getApiBaseUrl, getAuthHeaders } from '@/utils/api'
import Chart from 'chart.js/auto'

const route = useRoute()
const order = ref(null)
const chart = ref(null)
let pollInterval = null

const progress = computed(() => {
  if (!order.value || !order.value.sub_orders.length) return 0
  const completed = order.value.sub_orders.filter(s => s.internal_status === 'Success').length
  return Math.round((completed / order.value.sub_orders.length) * 100)
})

const fetchOrder = async () => {
  try {
    order.value = await apiGet(`/order-center/${route.params.id}`)
    setTimeout(initChart, 100)
  } catch (error) {
    console.error('Failed to fetch order:', error)
  }
}

const pauseOrder = async () => {
  try {
    await apiPost(`/order-center/${order.value.id}/pause`)
    showAlert('Paused', 'Order execution paused', 'warning', '⏸️')
    fetchOrder()
  } catch (error) {}
}

const resumeOrder = async () => {
  try {
    await apiPost(`/order-center/${order.value.id}/resume`)
    showAlert('Resumed', 'Order execution resumed. Schedule shifted forward.', 'success', '▶️')
    fetchOrder()
  } catch (error) {}
}

const forceExecution = async (subId) => {
  try {
    await apiPost(`/order-center/${order.value.id}/sub-order/${subId}/force`)
    showAlert('Forcing', 'Sub-order triggered immediately', 'info', '⚡')
    fetchOrder()
  } catch (error) {}
}

const downloadPDF = async () => {
  const url = `${getApiBaseUrl()}/order-center/${order.value.id}/report-pdf`
  const headers = getAuthHeaders()
  
  try {
      const response = await fetch(url, { headers })
      if (!response.ok) throw new Error('Download failed')
      
      const blob = await response.blob()
      const link = document.createElement('a')
      link.href = window.URL.createObjectURL(blob)
      link.download = `report_${order.value.id}.pdf`
      link.click()
  } catch (e) {
      showAlert('Error', 'Failed to download PDF', 'error', '❌')
  }
}

const initChart = () => {
  if (chart.value) chart.value.destroy()
  const ctx = document.getElementById('miniChart')
  if (!ctx || !order.value) return
  
  const data = order.value.sub_orders.map(s => s.qty)
  const labels = order.value.sub_orders.map(s => s.ordinal)
  
  chart.value = markRaw(new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: '#38bdf8',
        borderRadius: 4
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
}

const formatNumber = (num) => new Intl.NumberFormat().format(num)
const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString()
const formatTime = (dateStr) => new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

onMounted(() => {
  fetchOrder()
  pollInterval = setInterval(fetchOrder, 10000) // Poll every 10s
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.status-chip {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.pending { background: rgba(148, 163, 184, 0.1); color: #94a3b8; }
.sent { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.queued { background: rgba(168, 85, 247, 0.1); color: #a855f7; }
.success { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.tried-but-failed { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

.btn-now {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
  font-weight: 900;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  border: none;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3);
}

.btn-now:hover {
  transform: scale(1.1) rotate(-3deg);
}

.loader {
  width: 48px;
  height: 48px;
  border: 5px solid var(--glass-border);
  border-bottom-color: var(--primary-color);
  border-radius: 50%;
  box-sizing: border-box;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
