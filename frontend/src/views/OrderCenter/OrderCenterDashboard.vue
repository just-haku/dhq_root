<template>
  <div class="order-center-dashboard p-6">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold gradient-text">Order Center</h1>
        <p class="text-secondary">Manage and schedule your metric distributions</p>
      </div>
      <button class="btn btn-primary" @click="$router.push('/order-center/create')">
        <i class="fas fa-plus"></i> Create New Order
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="loader"></div>
    </div>

    <div v-else-if="orders.length === 0" class="glass-card p-12 text-center">
      <i class="fas fa-box-open text-6xl mb-4 opacity-20"></i>
      <h2 class="text-xl font-bold mb-2">No Orders Found</h2>
      <p class="text-secondary mb-6">You haven't created any orders yet.</p>
      <button class="btn btn-primary" @click="$router.push('/order-center/create')">
        Get Started
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="order in orders" :key="order.id" 
           class="glass-card order-card cursor-pointer hover-trigger" 
           @click="$router.push(`/order-center/${order.id}`)">
        <div class="order-type-badge" :class="order.status.toLowerCase()">
          {{ order.status }}
        </div>
        <div class="p-5">
          <h3 class="text-xl font-bold mb-1 truncate">{{ order.name }}</h3>
          <p class="text-sm text-secondary mb-4 truncate">{{ order.target_link }}</p>
          
          <div class="flex justify-between items-center text-sm mb-4">
            <span class="text-muted">Total Quantity</span>
            <span class="font-bold">{{ formatNumber(order.total_qty) }}</span>
          </div>

          <div class="border-t border-slate-700/50 pt-4 flex justify-between items-center">
            <span class="text-xs text-muted">Created {{ formatDate(order.created_at) }}</span>
            <i class="fas fa-chevron-right text-primary opacity-0 hover-visible transition-opacity"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiGet } from '@/utils/api'

const orders = ref([])
const loading = ref(true)

const fetchOrders = async () => {
  try {
    orders.value = await apiGet('/order-center/list')
  } catch (error) {
    console.error('Failed to fetch orders:', error)
  } finally {
    loading.value = false
  }
}

const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString()
}

onMounted(fetchOrders)
</script>

<style scoped>
.order-card {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.order-card:hover {
  transform: translateY(-5px);
  border-color: var(--primary-color);
  box-shadow: 0 10px 30px -10px rgba(56, 189, 248, 0.3);
}

.order-type-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
}

.active { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.paused { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.completed { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.cancelled { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

.gradient-text {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hover-visible {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.order-card:hover .hover-visible {
  opacity: 1;
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
