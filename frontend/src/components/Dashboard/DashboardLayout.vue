<template>
  <div class="dashboard-layout">
    <!-- Top Navigation Bar -->
    <nav class="top-navbar">
      <div class="navbar-content">
        <div class="navbar-left">
          <!-- Hamburger Menu Button -->
          <button 
            class="hamburger-btn" 
            @click="toggleSidebar"
            :class="{ 'active': sidebarOpen }"
          >
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
          </button>
          
          <!-- Logo/Brand -->
          <div class="navbar-brand">
            <div class="brand-logo">🏢</div>
            <span class="brand-text">Digital HQ</span>
          </div>
        </div>
        
        <div class="navbar-right">
          <!-- KPI Badge -->
          <div class="kpi-badge">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="12" cy="12" r="3" fill="currentColor"/>
              <path d="M12 2 L12 7 M12 17 L12 22 M2 12 L7 12 M17 12 L22 12" stroke="currentColor" stroke-width="2"/>
            </svg>
            <span>{{ userKPI }}</span> KPI
          </div>
          
          <!-- Notification Bell -->
          <button class="notification-btn">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2 C10.9 2 10 2.9 10 4 L10 10 C10 12.2 8.2 14 6 14 L6 16 L18 16 L18 14 C15.8 14 14 12.2 14 10 L14 4 C14 2.9 13.1 2 12 2 Z"/>
              <path d="M8 17 C8 18.1 8.9 19 10 19 L14 19 C15.1 19 16 18.1 16 17" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            <span v-if="unreadNotifications > 0" class="notification-badge">
              {{ unreadNotifications }}
            </span>
          </button>
          
          <!-- User Menu -->
          <div class="user-menu" @click="toggleUserMenu">
            <img :src="userAvatar" alt="User" class="user-avatar" />
            <div class="user-dropdown" v-if="userMenuOpen">
              <div class="dropdown-header">
                <img :src="userAvatar" alt="User" class="dropdown-avatar" />
                <div class="user-info">
                  <div class="user-name">{{ userName }}</div>
                  <div class="user-role">{{ userRole }}</div>
                </div>
              </div>
              <div class="dropdown-items">
                <a href="#" class="dropdown-item">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M3 8 L21 8 M8 3 L8 21" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  My Inventory
                </a>
                <a href="#" class="dropdown-item">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 3 L3 21 L21 21 L21 3 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M3 9 L21 9 M3 15 L21 15" stroke="currentColor" stroke-width="2"/>
                    <circle cx="7" cy="12" r="1" fill="currentColor"/>
                    <circle cx="12" cy="12" r="1" fill="currentColor"/>
                    <circle cx="17" cy="12" r="1" fill="currentColor"/>
                  </svg>
                  Item Shop
                </a>
                <a href="#" class="dropdown-item">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M12 8 L12 12 L15 15" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  Settings
                </a>
                <div class="dropdown-divider"></div>
                <a href="#" class="dropdown-item logout" @click.prevent="handleLogout">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 21 L9 3 M3 9 L9 3 L15 9" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M21 12 L13 12 M21 12 L17 8 M21 12 L17 16" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                  Logout
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Sidebar Navigation -->
    <aside class="sidebar" :class="{ 'open': sidebarOpen }">
      <div class="sidebar-header">
        <h6 class="sidebar-title">
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <rect x="2" y="4" width="20" height="16" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M6 8 L18 8 M6 12 L14 12 M6 16 L10 16" stroke="currentColor" stroke-width="2"/>
          </svg>
          SYSTEM TERMINAL
        </h6>
        <button class="sidebar-close" @click="toggleSidebar">
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 6 L18 18 M6 18 L18 6" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
      </div>
      
      <!-- User Profile Card -->
      <div class="user-card">
        <div class="user-card-bg">
          <div class="banner-bg-placeholder"></div>
        </div>
        <div class="user-card-content">
          <div class="user-avatar-wrapper">
            <img :src="userAvatar" alt="User" class="user-card-avatar" />
          </div>
          <div class="user-details">
            <div class="user-name">{{ userName }}</div>
            <div class="user-badges">
              <span class="role-badge">{{ userRole }}</span>
              <span class="kpi-badge-small">
                <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                  <circle cx="12" cy="12" r="3" fill="currentColor"/>
                  <path d="M12 2 L12 7 M12 17 L12 22 M2 12 L7 12 M17 12 L22 12" stroke="currentColor" stroke-width="2"/>
                </svg>
                {{ userKPI }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Links -->
      <nav class="sidebar-nav">
        <div class="nav-section">
          <div class="nav-section-label">Workspace</div>
          <router-link to="/dashboard" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 9 L12 2 L21 9 L21 21 L3 21 Z" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M9 21 L9 12 L15 12 L15 21" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            Dashboard
          </router-link>
          <router-link to="/growth-orders" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 17 L9 11 L13 15 L21 7" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="21" cy="7" r="2" fill="currentColor"/>
            </svg>
            Growth Orders
          </router-link>
          <router-link to="/media-gallery" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
              <path d="M21 15 L16 10 L5 21" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            Media Gallery
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-label">Economy</div>
          <router-link to="/shop" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 3 L3 21 L21 21 L21 3 Z" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M3 9 L21 9 M3 15 L21 15" stroke="currentColor" stroke-width="2"/>
              <circle cx="7" cy="12" r="1" fill="currentColor"/>
              <circle cx="12" cy="12" r="1" fill="currentColor"/>
              <circle cx="17" cy="12" r="1" fill="currentColor"/>
            </svg>
            Item Shop
          </router-link>
          <router-link to="/orders/create" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M12 8 L12 16 M8 12 L16 12" stroke="currentColor" stroke-width="2"/>
            </svg>
            Place Order
          </router-link>
          <router-link to="/orders/manage" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M7 8 L17 8 M7 12 L13 12 M7 16 L15 16" stroke="currentColor" stroke-width="2"/>
            </svg>
            Manage Orders
          </router-link>
        </div>

        <div class="nav-section" v-if="['AD', 'OP'].includes(userRole)">
          <div class="nav-section-label">Administration</div>
          <router-link to="/admin/tasks" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M7 8 L10 8 M14 8 L17 8 M7 12 L17 12 M7 16 L13 16" stroke="currentColor" stroke-width="2"/>
              <circle cx="12" cy="8" r="1" fill="currentColor"/>
            </svg>
            Task Manager
          </router-link>
          <router-link to="/admin/users" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M3 21 L3 17 C3 15 5 13 9 13 C13 13 15 15 15 17 L15 21" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="19" cy="8" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M16 21 L16 18 C16 16.5 17 15 19 15 C21 15 22 16.5 22 18 L22 21" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            Users & Groups
          </router-link>
          <router-link to="/admin/system" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="2" y="2" width="20" height="8" rx="1" stroke="currentColor" stroke-width="2" fill="none"/>
              <rect x="2" y="14" width="20" height="8" rx="1" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="6" cy="6" r="1" fill="currentColor"/>
              <circle cx="12" cy="6" r="1" fill="currentColor"/>
              <circle cx="18" cy="6" r="1" fill="currentColor"/>
              <circle cx="6" cy="18" r="1" fill="currentColor"/>
              <circle cx="12" cy="18" r="1" fill="currentColor"/>
              <circle cx="18" cy="18" r="1" fill="currentColor"/>
            </svg>
            System Admin
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-label">System</div>
          <router-link to="/settings" class="nav-link" active-class="active">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M12 8 L12 12 L15 15" stroke="currentColor" stroke-width="2"/>
            </svg>
            Settings
          </router-link>
            Logout
          </a>
        </div>
      </nav>

      <!-- System Wipe Button (Admin Only) -->
      <div class="system-actions" v-if="['AD', 'OP'].includes(userRole)">
        <button class="system-wipe-btn" @click="showSystemWipe = true">
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
            <circle cx="12" cy="12" r="3" fill="currentColor"/>
            <path d="M12 4 L12 2 M12 22 L12 20 M4 12 L2 12 M22 12 L20 12" stroke="currentColor" stroke-width="2"/>
            <path d="M6 6 L4.5 4.5 M19.5 19.5 L18 18 M18 6 L19.5 4.5 M4.5 19.5 L6 18" stroke="currentColor" stroke-width="2"/>
          </svg>
          SYSTEM WIPE
        </button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="content-wrapper">
        <!-- Page Header -->
        <header class="page-header">
          <div class="page-title">
            <h1>{{ pageTitle }}</h1>
            <p class="page-subtitle">{{ pageSubtitle }}</p>
          </div>
          <div class="page-actions">
            <slot name="page-actions"></slot>
          </div>
        </header>

        <!-- Page Content -->
        <div class="page-content">
          <slot></slot>
        </div>
      </div>
    </main>

    <!-- Overlay for mobile sidebar -->
    <div 
      class="sidebar-overlay" 
      :class="{ 'active': sidebarOpen }" 
      @click="toggleSidebar"
    ></div>

    <!-- System Wipe Modal -->
    <div v-if="showSystemWipe" class="modal-overlay" @click="showSystemWipe = false">
      <div class="modal-content danger-modal" @click.stop>
        <div class="modal-header danger">
          <h5><i class="fas fa-exclamation-triangle"></i> DANGER ZONE</h5>
          <button class="modal-close" @click="showSystemWipe = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p class="danger-title">FULL SYSTEM RESET</p>
          <input 
            type="text" 
            v-model="wipeConfirmation" 
            class="form-control" 
            placeholder="Type YES to confirm"
          />
          <input 
            type="password" 
            v-model="wipePassword" 
            class="form-control" 
            placeholder="Admin Password"
          />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showSystemWipe = false">
            Cancel
          </button>
          <button class="btn btn-danger" @click="executeSystemWipe">
            INITIATE WIPE
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/userStore.js'

// Reactive state
const sidebarOpen = ref(false)
const userMenuOpen = ref(false)
const showSystemWipe = ref(false)
const wipeConfirmation = ref('')
const wipePassword = ref('')

// User data
const userName = computed(() => userStore.displayName)
const userRole = computed(() => userStore.role)
const userKPI = ref(0)
const userAvatar = computed(() => {
  if (userStore.avatar) {
    return userStore.avatar
  }
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(userName.value)}&background=random`
})
const unreadNotifications = ref(0)

// Router
const router = useRouter()
const route = useRoute()

// Computed properties
const pageTitle = computed(() => {
  const titles = {
    '/dashboard': 'Dashboard',
    '/growth-orders': 'Growth Orders',
    '/admin/system': 'System Administration',
    '/admin/users': 'User Management',
    '/admin/tasks': 'Task Manager'
  }
  return titles[route.path] || 'Dashboard'
})

const pageSubtitle = computed(() => {
  const subtitles = {
    '/dashboard': 'Welcome back to your Digital HQ',
    '/growth-orders': 'Manage your automated growth campaigns',
    '/admin/system': 'System configuration and monitoring',
    '/admin/users': 'Manage users and permissions',
    '/admin/tasks': 'Monitor and manage system tasks'
  }
  return subtitles[route.path] || 'System Overview'
})

const userStore = useUserStore()

// Methods
const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
}

const executeSystemWipe = () => {
  if (wipeConfirmation.value === 'YES' && wipePassword.value) {
    // Implement system wipe logic
    console.log('System wipe initiated')
    showSystemWipe.value = false
    wipeConfirmation.value = ''
    wipePassword.value = ''
  }
}

const handleLogout = () => {
  userStore.clearUser()
  window.location.href = '/logout'
}

// Close dropdowns when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.user-menu')) {
    userMenuOpen.value = false
  }
}

// Close sidebar on escape key
const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    sidebarOpen.value = false
    userMenuOpen.value = false
  }
}

onMounted(() => {
  userStore.init()

  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* Dashboard Layout */
.dashboard-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #f1f5f9;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Top Navigation */
.top-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1000;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 1.5rem;
  max-width: 100%;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.hamburger-btn {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.hamburger-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.hamburger-line {
  width: 20px;
  height: 2px;
  background: #f1f5f9;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.hamburger-btn.active .hamburger-line:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.hamburger-btn.active .hamburger-line:nth-child(2) {
  opacity: 0;
}

.hamburger-btn.active .hamburger-line:nth-child(3) {
  transform: rotate(-45deg) translate(7px, -6px);
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: #f1f5f9;
}

.brand-logo {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: 700;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.kpi-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.875rem;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.notification-btn {
  position: relative;
  background: none;
  border: none;
  color: #f1f5f9;
  font-size: 1.25rem;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.notification-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #ef4444;
  color: white;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.user-menu {
  position: relative;
  cursor: pointer;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #3b82f6;
  object-fit: cover;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  min-width: 260px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.dropdown-header {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.dropdown-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #f1f5f9;
}

.user-role {
  font-size: 0.875rem;
  color: #94a3b8;
}

.dropdown-items {
  padding: 0.5rem;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  color: #cbd5e1;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.dropdown-item:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  transform: translateX(4px);
}

.dropdown-item.logout {
  color: #f87171;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0.5rem 0;
}

/* Sidebar */
.sidebar {
  position: fixed;
  top: 0;
  left: -550px;
  width: 550px;
  height: 100vh;
  background: rgba(15, 23, 42, 0.98);
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  transition: left 0.3s ease;
  z-index: 999;
  overflow-y: auto;
}

.sidebar.open {
  left: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-title {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar-close {
  background: none;
  border: none;
  color: #f1f5f9;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.sidebar-close:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* User Card */
.user-card {
  height: 240px;
  flex-shrink: 0;
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-card-bg {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 aspect ratio */
}

.banner-bg,
.banner-bg-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-bg-placeholder {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 3rem;
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
  width: 64px;
  height: 64px;
  flex-shrink: 0;
}

.user-card-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #3b82f6;
  object-fit: cover;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
  margin-bottom: 0.5rem;
}

.user-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.role-badge {
  background: #3b82f6;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

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

/* Navigation */
.sidebar-nav {
  padding: 1rem 1.5rem;
  flex: 1;
}

.nav-section {
  margin-bottom: 2rem;
}

.nav-section-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: #64748b;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #cbd5e1;
  text-decoration: none;
  border-radius: 8px;
  margin-bottom: 0.25rem;
  border-left: 4px solid transparent;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  transform: translateX(4px);
  border-left-color: #3b82f6;
}

.nav-link.active {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border-left-color: #3b82f6;
}

.nav-link i {
  width: 20px;
  text-align: center;
  transition: transform 0.3s ease;
}

.nav-link:hover i {
  transform: scale(1.2);
}

.logout-link {
  color: #f87171;
}

.logout-link:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border-left-color: #ef4444;
}

/* System Actions */
.system-actions {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.system-wipe-btn {
  width: 100%;
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.system-wipe-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
  transform: translateY(-1px);
}

/* Main Content */
.main-content {
  margin-left: 0;
  margin-top: 64px;
  min-height: calc(100vh - 64px);
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-open {
  margin-left: 550px;
}

.content-wrapper {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.page-title h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  color: #94a3b8;
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 1rem;
}

.page-content {
  min-height: calc(100vh - 200px);
}

/* Overlay */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.sidebar-overlay.active {
  opacity: 1;
  visibility: visible;
}

/* SVG Icons */
.icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.kpi-badge .icon,
.notification-btn .icon,
.nav-link .icon,
.dropdown-item .icon,
.sidebar-title .icon,
.sidebar-close .icon,
.system-wipe-btn .icon {
  color: currentColor;
}

/* Lightweight Icon Animations */
.nav-link:hover .icon {
  transform: scale(1.1) rotate(5deg);
}

.notification-btn:hover .icon {
  animation: bell-ring 0.5s ease-in-out;
}

.kpi-badge:hover .icon {
  animation: coin-pulse 0.6s ease-in-out;
}

.dropdown-item:hover .icon {
  transform: translateX(3px);
}

.system-wipe-btn:hover .icon {
  animation: radiation-pulse 1s ease-in-out infinite;
}

/* Performance-optimized animations */
@keyframes bell-ring {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(10deg); }
  75% { transform: rotate(-10deg); }
}

@keyframes coin-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

@keyframes radiation-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .icon {
    transition: transform 0.2s ease;
  }

  .nav-link:hover .icon {
    transform: scale(1.05);
  }

  .dropdown-item:hover .icon {
    transform: translateX(2px);
  }

  /* Disable heavy animations on mobile */
  .notification-btn:hover .icon,
  .kpi-badge:hover .icon,
  .system-wipe-btn:hover .icon {
    animation: none !important;
  }
}

/* Respect user's motion preferences */
@media (prefers-reduced-motion: reduce) {
  .icon {
    transition: none !important;
    animation: none !important;
  }
  
  .nav-link .icon,
  .notification-btn .icon,
  .kpi-badge .icon,
  .dropdown-item .icon,
  .system-wipe-btn .icon {
    animation: none !important;
  }
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: rgba(15, 23, 42, 0.98);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  max-width: 500px;
  width: 90%;
}

.danger-modal .modal-header {
  background: #dc2626;
  color: white;
  padding: 1rem 1.5rem;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h5 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
}

.modal-body {
  padding: 1.5rem;
}

.danger-title {
  text-align: center;
  color: #dc2626;
  font-weight: 700;
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #f1f5f9;
  margin-bottom: 1rem;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-danger {
  background: #dc2626;
  color: white;
}

.btn-danger:hover {
  background: #b91c1c;
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    left: -100%;
  }

  .main-content.sidebar-open {
    margin-left: 0;
  }

  .content-wrapper {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .navbar-content {
    padding: 0 1rem;
  }

  .brand-text {
    display: none;
  }

  .kpi-badge span {
    display: none;
  }
}
</style>
