<template>
  <div class="dashboard-layout" :class="{ 'no-header': route.meta.hideHeader }">
    <!-- Header -->
    <header v-if="!route.meta.hideHeader" class="dashboard-header glass-panel">
      <div class="header-left">
        <SideMenu v-if="!route.meta.hideSideMenu" />
        
        <div class="logo-container" @click="router.push('/dashboard')">
          <svg width="40" height="40" viewBox="0 0 40 40" class="logo-svg">
            <defs>
              <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color: var(--primary-color); stop-opacity: 1" />
                <stop offset="100%" style="stop-color: var(--secondary-color); stop-opacity: 1" />
              </linearGradient>
            </defs>
            <circle cx="20" cy="20" r="18" fill="url(#logoGradient)"/>
            <text x="20" y="26" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="16" font-weight="bold">C</text>
          </svg>
          <span class="logo-text gradient-text">KURO_server</span>
        </div>
      </div>

      <div class="header-right">
        <div class="kpi-display-global" @click="router.push('/arcade')">
          <i class="fas fa-coins text-warning"></i>
          <span>{{ kpiBalance }}</span>
        </div>
        <div class="notification-bell">
          <i class="fas fa-bell"></i>
          <span class="notification-dot"></span>
        </div>
        <div class="user-profile-wrapper" ref="userDropdownRef">
          <div class="user-info" @click="toggleUserDropdown">
            <span class="user-display-name">{{ userDisplayName || 'User' }}</span>
            <div class="user-avatar-small">
              <div class="avatar-circle-small flex items-center justify-center overflow-hidden">
                <img v-if="avatarUrl" :src="avatarUrl" class="avatar-img-small" />
                <span v-else class="text-white font-bold">{{ initials }}</span>
              </div>
            </div>
          </div>
          
          <transition name="dropdown-fade">
            <div v-show="isUserDropdownOpen" class="user-dropdown glass-panel">
              <div class="dropdown-header">
                <span class="dropdown-role">{{ user?.role || 'USER' }}</span>
              </div>
              <ul class="dropdown-list">
                <li @click="navigateFromDropdown('/profile')">
                  <i class="fas fa-user"></i> {{ t('settings.profile') }}
                </li>
                <li @click="navigateFromDropdown('/inventory')">
                  <i class="fas fa-box-open"></i> Inventory
                </li>
                <li @click="navigateFromDropdown('/settings')">
                  <i class="fas fa-cog"></i> {{ t('sidebar.settings') }}
                </li>
                <li class="logout-item" @click="logout">
                  <i class="fas fa-sign-out-alt"></i> {{ t('settings.logout') }}
                </li>
              </ul>
            </div>
          </transition>
        </div>
      </div>
    </header>

    <!-- Global Power Saver Alert -->
    <transition name="banner-fade">
      <div v-if="systemStore.powerMode === 'power_saver'" class="power-saver-banner">
        <div class="banner-content">
          <i class="fas fa-bolt banner-icon pulse-alert"></i>
          <span class="banner-text"><strong>{{ t('power_saver.powersaver') }} {{ t('power_saver.active') }}:</strong> {{ t('power_saver.banner') }}</span>
        </div>
      </div>
    </transition>

    <!-- Main Content -->
    <main class="dashboard-main-content custom-scrollbar">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" v-if="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { kpiBalance } from '@/utils/api.js'
import SideMenu from '@/components/SideMenu.vue'
import { useUserStore } from '@/stores/userStore.js'
import { useSystemStore } from '@/stores/systemStore.js'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const systemStore = useSystemStore()

const isUserDropdownOpen = ref(false)
const userDropdownRef = ref(null)

const toggleUserDropdown = () => {
  isUserDropdownOpen.value = !isUserDropdownOpen.value
}

const handleClickOutside = (e) => {
  if (userDropdownRef.value && !userDropdownRef.value.contains(e.target)) {
    isUserDropdownOpen.value = false
  }
}

const navigateFromDropdown = (path) => {
  isUserDropdownOpen.value = false
  router.push(path)
}

const logout = () => {
  isUserDropdownOpen.value = false
  userStore.clearUser()
  router.push('/')
}

// User data from store
const user = computed(() => userStore.user)
const userName = computed(() => userStore.username)
const userDisplayName = computed(() => userStore.displayName)
const userRole = computed(() => userStore.role)
const avatarUrl = computed(() => userStore.avatarUrl)

onMounted(() => {
  userStore.init()
  systemStore.init()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const initials = computed(() => {
  return (userDisplayName.value || userName.value)?.charAt(0).toUpperCase() || '?'
})
</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  height: 70px;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 90;
  border-radius: 0 0 1rem 1rem;
  border-top: none;
  border-left: none;
  border-right: none;
  background: var(--glass-bg-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 4rem; /* to give space for the SideMenu trigger which sits absolute/fixed */
  margin-left: 60px; /* Offset for SideMenu trigger */
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.logo-container:hover {
  transform: scale(1.05);
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.gradient-text {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.kpi-display-global {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  background: var(--glass-bg-hover);
  border-radius: 20px;
  font-weight: 800;
  font-size: 0.9rem;
  color: #fbbf24;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.kpi-display-global:hover {
  background: rgba(251, 191, 36, 0.1);
  transform: translateY(-1px);
}

.notification-bell {
  position: relative;
  font-size: 1.2rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.2s;
  padding: 0.5rem;
  border-radius: 50%;
  background: var(--glass-bg-hover);
}

.notification-bell:hover {
  color: var(--primary-color);
}

.notification-dot {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--danger-color, #ef4444);
  border: 1px solid var(--glass-bg-primary);
}

.user-profile-wrapper {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  transition: background 0.2s;
}

.user-info:hover {
  background: var(--glass-bg-hover);
}

.user-display-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.user-avatar-small {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  padding: 2px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}

.avatar-circle-small {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--glass-bg-primary);
}

.avatar-img-small {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.user-dropdown {
  position: absolute;
  top: 120%;
  right: 0;
  width: 200px;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.dropdown-header {
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid var(--glass-border);
  text-align: right;
}

.dropdown-role {
  font-size: 0.7rem;
  font-weight: 800;
  background: var(--primary-color);
  padding: 2px 8px;
  border-radius: 12px;
  color: white;
}

.dropdown-list {
  list-style: none;
  margin: 0;
  padding: 0.5rem 0;
}

.dropdown-list li {
  padding: 0.85rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  color: var(--text-primary);
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.dropdown-list li:hover {
  background: var(--glass-bg-hover);
  color: var(--primary-color);
}

.dropdown-list li i {
  width: 16px;
  text-align: center;
}

.dropdown-list li.logout-item {
  border-top: 1px solid var(--glass-border);
  margin-top: 0.25rem;
  color: #ef4444;
}

.dropdown-list li.logout-item:hover {
  background: rgba(239, 68, 68, 0.1);
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
  transform-origin: top right;
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.dashboard-main-content {
  margin-top: 70px; /* Account for fixed header */
  flex-grow: 1;
  padding: 2rem;
  width: 100%;
  max-width: 1600px;
  margin-left: auto;
  margin-right: auto;
  overflow-y: auto;
}

.no-header .dashboard-main-content {
  margin-top: 0;
  padding: 0;
  max-width: none;
}

/* Page transitions */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 768px) {
  .dashboard-header {
    padding: 0 1rem;
    height: 60px;
  }
  
  .header-left {
    margin-left: 35px;
    gap: 0.5rem;
  }
  
  .header-right {
    gap: 0.75rem;
  }
  
  .kpi-display-global {
    padding: 0.3rem 0.5rem;
    font-size: 0.8rem;
  }
  
  .logo-text {
    display: none;
  }
  
  .user-display-name {
    display: none;
  }
  
  .dashboard-main-content {
    padding: 1rem;
  }
}

/* Power Saver Banner CSS */
.power-saver-banner {
  margin-top: 70px;
  width: 100%;
  background: linear-gradient(90deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  z-index: 85;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 0.95rem;
  letter-spacing: 0.5px;
}

.banner-icon {
  font-size: 1.25rem;
  color: #fffbeb;
}

.pulse-alert {
  animation: alert-pulse 2s infinite;
}

@keyframes alert-pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}

.banner-fade-enter-active,
.banner-fade-leave-active {
  transition: all 0.4s ease;
}
.banner-fade-enter-from,
.banner-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Adjust main content margin when banner is present */
.power-saver-banner + .dashboard-main-content {
  margin-top: 0 !important;
}
</style>
