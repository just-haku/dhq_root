<template>
  <div class="dashboard-container relative">
    <div class="main-content">
      <div class="dashboard-header text-center mb-10 mt-10">
        <h1 class="font-bold text-4xl mb-4 gradient-text">Dashboard</h1>
        <p class="text-secondary text-lg">Welcome to your Digital Headquarters central hub</p>
      </div>
      
      <div class="glass-card welcome-card mb-8 p-8 flex flex-col md:flex-row gap-6 items-center">
        <div class="welcome-text flex-grow">
          <h2 class="text-2xl font-bold mb-2">Hello, {{ displayName || 'User' }}!</h2>
          <p class="text-secondary">You are logged in as <span class="badge" :class="roleClass">{{ user?.role || 'USER' }}</span></p>
          <div class="mt-4">
            <p class="text-sm text-secondary mb-1">Current KPI Balance:</p>
            <h3 class="text-3xl font-bold text-warning"><i class="fas fa-coins text-yellow-400"></i> {{ kpiBalance }}</h3>
          </div>
        </div>
        <div class="welcome-action">
          <button class="btn btn-primary" @click="$router.push('/drive')">
            <i class="fas fa-folder-open"></i> Go to Drive
          </button>
        </div>
      </div>

      <div class="grid-layout">
        <div class="glass-card stat-card" v-for="(stat, idx) in dashboardStats" :key="idx">
          <div class="stat-icon" :style="{ color: stat.color }">
            <i :class="stat.icon"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
      
      <div class="glass-card mt-8 p-6 text-center text-muted">
        <i class="fas fa-magic text-3xl mb-4 opacity-50"></i>
        <h3 class="text-xl font-bold mb-2">Workspace Modules</h3>
        <p>Access your workspace modules by clicking the menu icon in the top left corner.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { kpiBalance } from '@/utils/api.js'

// Debug watcher
watch(kpiBalance, (newVal) => {
  console.log(`%c📊 Dashboard: kpiBalance updated to ${newVal}`, 'color: #8b5cf6; font-weight: bold')
})

import { useUserStore } from '@/stores/userStore'

const router = useRouter()
const userStore = useUserStore()

const user = computed(() => userStore.user)
const displayName = computed(() => userStore.displayName)

onMounted(() => {
  userStore.init()
  if (!userStore.user) {
    router.push('/')
  } else {
    userStore.fetchProfile()
  }
})

const roleClass = computed(() => {
  if (user.value?.role === 'OP') return 'role-op'
  if (user.value?.role === 'AD') return 'role-ad'
  return 'role-user'
})

// Fake placeholders for visual aesthetics
const dashboardStats = [
  { icon: 'fas fa-hdd', label: 'Storage Used', value: '45%', color: 'var(--primary-color)' },
  { icon: 'fas fa-users', label: 'Collaborations', value: '12', color: 'var(--secondary-color)' },
  { icon: 'fas fa-envelope-open-text', label: 'Unread Emails', value: '3', color: 'var(--success-color)' },
  { icon: 'fas fa-shield-alt', label: 'Security Status', value: 'Secure', color: 'var(--warning-color)' }
]
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.main-content {
  width: 100%;
}

.welcome-card {
  border-top: 4px solid var(--primary-color);
  background: linear-gradient(135deg, var(--glass-bg-primary) 0%, var(--glass-bg-secondary) 100%);
}

.badge {
  font-size: 0.75rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 12px;
  border: 1px currentColor solid;
}

.role-op { color: #ef4444; }
.role-ad { color: #f59e0b; }
.role-user { color: #3b82f6; }

.grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.8;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.gradient-text {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-warning {
  color: #fbbf24;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding-top: 1rem;
  }
}
</style>
