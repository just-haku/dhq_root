<template>
  <div id="app" :data-theme="currentTheme">
    <!-- Liquid Glass Vector Background Elements -->
    <div class="vector-bg">
      <div class="vector-shape"></div>
      <div class="vector-shape"></div>
      <div class="vector-shape"></div>
    </div>
    
    <!-- Global Theme Toggle -->
    <button class="theme-toggle-btn glass-panel" @click="toggleTheme" title="Toggle Theme">
      <i :class="currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon'"></i>
    </button>
    
    <!-- Main Content routing -->
    <router-view v-slot="{ Component }">
      <transition name="page-fade" mode="out-in">
        <component :is="Component" v-if="Component" />
      </transition>
    </router-view>

    <!-- Global Notification Singleton -->
    <LiquidGlassNotification 
      :show="notificationState.show"
      :type="notificationState.type"
      :title="notificationState.title"
      :message="notificationState.message"
      :icon="notificationState.icon"
      :duration="notificationState.duration"
      @close="closeNotification"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { notificationState } from './utils/api.js'
import LiquidGlassNotification from './components/UI/LiquidGlassNotification.vue'
import { useUserStore } from '@/stores/userStore.js'

const userStore = useUserStore()
const currentTheme = computed(() => userStore.activeTheme)

const closeNotification = () => {
  notificationState.value.show = false
}

const setTheme = async (theme) => {
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('dhq-theme', theme)
  
  if (userStore.user) {
    try {
      const { apiPatch } = await import('@/utils/api')
      await apiPatch('/user/appearance', { active_theme: theme })
      userStore.setUser({ active_theme: theme })
    } catch (e) {
      console.error('Failed to save theme to backend:', e)
    }
  }
}

const toggleTheme = () => {
  const themes = ['dark', 'light'] // only toggle between defaults for the quick button
  const currentIndex = themes.indexOf(currentTheme.value)
  if (currentIndex === -1) {
     setTheme('dark')
     return
  }
  const nextIndex = (currentIndex + 1) % themes.length
  setTheme(themes[nextIndex])
}

onMounted(() => {
  userStore.init()
  const savedTheme = localStorage.getItem('dhq-theme')
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme)
  }
})
</script>

<style>
/* App specific styles */
.theme-toggle-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: var(--text-primary);
  z-index: 1000;
  cursor: pointer;
  border: 1px solid var(--glass-border);
}

.theme-toggle-btn:hover {
  transform: scale(1.1) rotate(15deg);
}

/* Page transitions */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Mobile responsive padding */
@media (max-width: 768px) {
  .theme-toggle-btn {
    bottom: 1rem;
    right: 1rem;
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
}
</style>
