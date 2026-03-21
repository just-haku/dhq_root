<template>
  <div class="dropdown-container" ref="dropdownRef">
    <button 
      @click="toggleDropdown" 
      class="dropdown-trigger"
      :class="{ active: isOpen }"
    >
      <span class="trigger-content">
        <slot name="trigger">{{ triggerText }}</slot>
      </span>
      <span class="dropdown-arrow" :class="{ rotated: isOpen }">▼</span>
    </button>
    
    <transition name="dropdown">
      <div v-if="isOpen" class="dropdown-menu">
        <div class="dropdown-content">
          <slot></slot>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'LiquidGlassDropdown',
  props: {
    triggerText: {
      type: String,
      default: 'Options'
    }
  },
  setup(props, { emit }) {
    const isOpen = ref(false)
    const dropdownRef = ref(null)

    const toggleDropdown = () => {
      isOpen.value = !isOpen.value
    }

    const closeDropdown = (event) => {
      if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
        isOpen.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', closeDropdown)
    })

    onUnmounted(() => {
      document.removeEventListener('click', closeDropdown)
    })

    return {
      isOpen,
      dropdownRef,
      toggleDropdown
    }
  }
}
</script>

<style scoped>
.dropdown-container {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  min-width: 150px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.dropdown-trigger::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.dropdown-trigger:hover::before {
  left: 100%;
}

.dropdown-trigger:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-1px);
  box-shadow: var(--glass-shadow-lg);
}

.dropdown-trigger.active {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  box-shadow: var(--glass-shadow-lg);
}

.trigger-content {
  color: var(--text-primary);
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.dropdown-arrow {
  color: var(--text-primary);
  font-size: 0.8rem;
  transition: transform 0.3s ease;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  z-index: 1000;
  min-width: 200px;
}

.dropdown-content {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-xl);
  -webkit-backdrop-filter: var(--glass-blur-xl);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--glass-shadow-xl);
  overflow: hidden;
  position: relative;
}

.dropdown-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

/* Dropdown transitions */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* Dropdown items styling */
:deep(.dropdown-item) {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  position: relative;
}

:deep(.dropdown-item:hover) {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

:deep(.dropdown-item.danger) {
  color: #ef4444;
}

:deep(.dropdown-item.danger:hover) {
  background: rgba(239, 68, 68, 0.1);
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}
</style>
