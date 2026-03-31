<template>
  <div class="side-menu-wrapper">
    <!-- Menu Trigger Icon -->
    <div class="menu-trigger glass-panel" @click="isOpen = !isOpen">
      <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
      </svg>
    </div>

    <!-- Overlay and Side Menu -->
    <Teleport to="body">
      <transition name="fade">
        <div v-if="isOpen" 
             class="menu-overlay" 
             @mousedown="onOverlayMouseDown"
             @mouseup="onOverlayMouseUp"></div>
      </transition>

      <div class="side-menu glass-panel" :class="{ 'is-open': isOpen }">
        <!-- User Card -->
        <div class="user-card relative overflow-hidden">
        <div class="user-card-bg cursor-pointer" @click="navigate('/profile')">
          <div class="user-banner" :style="{ background: bannerUrl ? `url(${bannerUrl}) center/cover no-repeat` : 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))' }"></div>
        </div>
        
        <div class="user-card-content cursor-pointer" @click="navigate('/profile')">
          <div class="user-avatar-wrapper">
            <div class="avatar-circle flex items-center justify-center overflow-hidden">
              <img v-if="avatarUrl" :src="avatarUrl" class="avatar-img" />
              <span v-else class="text-white text-xl font-bold">{{ initials }}</span>
            </div>
          </div>
          
          <div class="user-details">
            <h3 class="display-name">{{ displayName || 'Guest User' }}</h3>
            <div class="user-badges">
              <span class="role-badge" :class="roleClass">{{ user?.role || 'USER' }}</span>
              <span class="currency-badges flex gap-2">
                <span class="kpi-badge-small" title="KPI Balance">
                  <i class="fas fa-coins text-[10px] mr-1"></i>
                  {{ kpiBalance }}
                </span>
                <span class="chips-badge-small" title="Chips Balance">
                  <i class="fas fa-gamepad text-[10px] mr-1"></i>
                  {{ formatNumber(user?.chip_balance || 0) }}
                </span>
                <span class="api-dollar-badge-small" title="API$ Balance">
                  <i class="fas fa-file-invoice-dollar text-[10px] mr-1"></i>
                  {{ (user?.api_dollar_balance || 0).toFixed(2) }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Routes -->
      <div class="nav-routes-container custom-scrollbar" :class="[`layout-${sideMenuLayout}`]">
        <!-- USER Routes -->
        <div class="route-section">
          <h4 class="section-title">User Portal</h4>
          <div class="route-list">
            <a class="nav-link" v-for="route in userRoutes" :key="route.name" @click.prevent="navigate(route.path)">
              <i :class="route.icon"></i>
              {{ route.name }}
            </a>
          </div>
        </div>
        
        <!-- AD Routes -->
        <div class="route-section" v-if="['AD', 'OP'].includes(user?.role)">
          <h4 class="section-title">Admin Portal</h4>
          <div class="route-list">
            <a class="nav-link" v-for="route in adRoutes" :key="route.name" @click.prevent="navigate(route.path)">
              <i :class="route.icon" class="text-secondary"></i>
              {{ route.name }}
            </a>
          </div>
        </div>
        
        <!-- OP Routes -->
        <div class="route-section" v-if="user?.role === 'OP'">
          <h4 class="section-title">Operator Portal</h4>
          <div class="route-list">
            <a class="nav-link" v-for="route in opRoutes" :key="route.name" @click.prevent="navigate(route.path)">
              <i :class="route.icon" class="text-danger"></i>
              {{ route.name }}
            </a>
          </div>
        </div>
      </div>
      
      <!-- Logout -->
      <div class="logout-section">
        <button class="btn btn-danger w-full" @click="logout">
          <i class="fas fa-sign-out-alt"></i> Log Out
        </button>
      </div>
    </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { kpiBalance } from '@/utils/api.js'
import { useUserStore } from '@/stores/userStore.js'

const { t } = useI18n()

const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

// Debug watcher
watch(kpiBalance, (newVal) => {
  console.log(`%c🏠 SideMenu: kpiBalance updated to ${newVal}`, 'color: #8b5cf6; font-weight: bold')
})

const router = useRouter()
const userStore = useUserStore()
const isOpen = ref(false)

const user = computed(() => userStore.user)
const displayName = computed(() => userStore.displayName)
const avatarUrl = computed(() => userStore.avatarUrl)
const bannerUrl = computed(() => userStore.bannerUrl)
const username = computed(() => userStore.username)
const sideMenuLayout = computed(() => userStore.sideMenuLayout)

let overlayMouseDownPos = { x: 0, y: 0 }

const onOverlayMouseDown = (e) => {
  overlayMouseDownPos = { x: e.clientX, y: e.clientY }
}

const onOverlayMouseUp = (e) => {
  const dx = e.clientX - overlayMouseDownPos.x
  const dy = e.clientY - overlayMouseDownPos.y
  const distance = Math.sqrt(dx*dx + dy*dy)
  if (distance < 5) { // 5px threshold for drag vs click
    isOpen.value = false
  }
}

const handleKeyDown = (e) => {
  if (e.key === 'Escape' && isOpen.value) {
    isOpen.value = false
  }
}

onMounted(() => {
  userStore.init()
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})

const initials = computed(() => {
  return (displayName.value || username.value)?.charAt(0).toUpperCase() || '?'
})

const roleClass = computed(() => {
  if (user.value?.role === 'OP') return 'role-op'
  if (user.value?.role === 'AD') return 'role-ad'
  return 'role-user'
})

const navigate = (path) => {
  isOpen.value = false
  if (path) {
    router.push(path)
  }
}

const logout = () => {
  userStore.clearUser()
  router.push('/')
}

// Route Placeholders Mapping
const userRoutes = computed(() => [
  { name: t('sidebar.drive'), icon: 'fas fa-hdd', path: '/drive' },
  { name: t('sidebar.collaboration'), icon: 'fas fa-users-cog', path: '/collaboration' },
  { name: t('sidebar.order_center'), icon: 'fas fa-box', path: '/order-center' },
  { name: t('sidebar.cnc'), icon: 'fas fa-drafting-compass', path: '/gcode-generator' },
  { name: t('sidebar.task_center'), icon: 'fas fa-tasks', path: '#' },
  { name: t('sidebar.email'), icon: 'fas fa-envelope-open-text', path: '/email-hub' },
  { name: t('sidebar.chat'), icon: 'fas fa-comments', path: '/convo-hub' },
  { name: t('sidebar.shop'), icon: 'fas fa-shopping-cart', path: '/shop' },
  { name: t('sidebar.arcade'), icon: 'fas fa-gamepad', path: '/arcade' },
  { name: t('sidebar.notification_center'), icon: 'fas fa-bell', path: '#' },
  { name: t('sidebar.settings'), icon: 'fas fa-user-cog', path: '/settings' },
  { name: t('sidebar.personalize'), icon: 'fas fa-paint-brush', path: '#' },
  { name: t('sidebar.scan_virus'), icon: 'fas fa-shield-virus', path: '/virus-scan' },
  { name: t('sidebar.daily_gift'), icon: 'fas fa-gift', path: '/daily-gifts' }
])

const adRoutes = computed(() => [
  { name: t('sidebar.users'), icon: 'fas fa-users', path: '/admin/users' },
  { name: t('sidebar.performance'), icon: 'fas fa-server', path: '/performance' },
  { name: t('sidebar.panic_mode'), icon: 'fas fa-exclamation-triangle', path: '/admin/panic' }
])

const opRoutes = computed(() => [
  { name: t('sidebar.manage_role'), icon: 'fas fa-user-shield', path: '#' },
  { name: t('sidebar.vault'), icon: 'fas fa-shield-halved', path: '/vault' },
  { name: t('sidebar.manage_quotas'), icon: 'fas fa-database', path: '#' },
  { name: t('sidebar.nuke_data'), icon: 'fas fa-bomb', path: '/nuke-data' },
  { name: t('sidebar.manage_shop'), icon: 'fas fa-store-alt', path: '#' },
  { name: t('sidebar.working_mode'), icon: 'fas fa-bolt', path: '/operator/working-mode' },
  { name: t('sidebar.admin_config'), icon: 'fas fa-cogs', path: '/operator/server-settings' },
  { name: t('sidebar.manage_gifts'), icon: 'fas fa-box-open', path: '/manage-gifts' },
])
</script>

<style scoped>
.menu-trigger {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  box-shadow: var(--glass-shadow);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-trigger:hover {
  transform: scale(1.1);
}

.menu-icon {
  font-size: 1.5rem;
}

.menu-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 998;
}

.side-menu {
  position: fixed;
  top: 0;
  left: -610px;
  width: 600px;
  height: 100vh;
  z-index: 999;
  display: flex;
  flex-direction: column;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 0 1rem 1rem 0;
  border-left: none;
  background: var(--bg-primary);
  box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5);
}

.side-menu.is-open {
  transform: translateX(610px);
}

/* User Card Styles */
.user-card {
  position: relative;
  height: 350px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--glass-border);
}

.user-card-bg {
  position: relative;
  width: 100%;
  height: 100%;
}

.user-banner {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-card-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.4) 50%, transparent 100%);
  padding: 1.5rem;
  display: flex;
  align-items: flex-end;
  gap: 1rem;
}

.user-avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--primary-color);
}

.avatar-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--primary-color);
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: 2px solid var(--primary-color);
}

.user-details {
  flex: 1;
}

.display-name {
  font-size: 2.2rem;
  font-weight: 800;
  color: white;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.8);
  margin: 0 0 0.5rem 0;
  line-height: 1.1;
}

.user-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.role-badge {
  font-size: 0.75rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 12px;
  color: white;
}
.role-op { background: #ef4444; }
.role-ad { background: #f59e0b; }
.role-user { background: #3b82f6; }

.kpi-badge-small {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.chips-badge-small {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.api-dollar-badge-small {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

/* Navigation Routes */
.nav-routes-container {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
}

.route-section {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  padding-left: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 0.95rem;
  font-weight: 500;
}

.nav-link i {
  width: 20px;
  text-align: center;
  font-size: 1.1rem;
}

.nav-link:hover {
  background: var(--glass-bg-hover);
  transform: translateX(5px);
  color: var(--primary-color);
}

/* Grid Layout Styles */
.nav-routes-container.layout-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.nav-routes-container.layout-grid .route-section {
  margin-bottom: 0.5rem;
}

.nav-routes-container.layout-grid .route-section .route-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.nav-routes-container.layout-grid .nav-link {
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 1rem 0.5rem;
  aspect-ratio: 1;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  gap: 0.5rem;
  font-size: 0.75rem;
}

.nav-routes-container.layout-grid .nav-link i {
  font-size: 1.5rem;
  width: auto;
}

.nav-routes-container.layout-grid .nav-link:hover {
  transform: scale(1.05);
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
}

/* Logout Section */
.logout-section {
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
  flex-shrink: 0;
}

.w-full {
  width: 100%;
}

/* Custom Scrollbar for side menu */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--glass-border);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--glass-border-hover);
}
</style>