<template>
  <div class="login-container relative overflow-hidden">
    <!-- Login form card -->
    <div class="glass-panel login-card animate-fade-in">
      <div class="header-section text-center mb-8">
        <div class="logo-wrapper mb-6 flex justify-center">
          <div class="logo-icon floating">
            <i class="fas fa-ghost text-4xl text-white"></i>
          </div>
        </div>
        <h1 class="gradient-text text-3xl font-bold tracking-tight mb-2">DHQ Terminal</h1>
        <p class="text-secondary text-sm">Secure Access Interface v2.0</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div class="form-group">
          <label for="username">Operator Identity</label>
          <div class="input-wrapper">
            <i class="fas fa-user input-icon"></i>
            <input
              id="username"
              v-model="credentials.username"
              type="text"
              required
              placeholder="Username"
              class="liquid-input"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">Security Cipher</label>
          <div class="input-wrapper">
            <i class="fas fa-lock input-icon"></i>
            <input
              id="password"
              v-model="credentials.password"
              type="password"
              required
              placeholder="••••••••"
              class="liquid-input"
            />
          </div>
        </div>
        
        <button
          type="submit"
          :disabled="isLoading"
          class="btn-login w-full py-3 rounded-xl font-bold transition-all duration-300 flex items-center justify-center gap-2"
        >
          <template v-if="isLoading">
            <i class="fas fa-circle-notch fa-spin"></i>
            Decrypting...
          </template>
          <template v-else>
            <i class="fas fa-sign-in-alt"></i>
            Initialize Session
          </template>
        </button>
      </form>

      <div class="mt-8 pt-6 border-t border-white/10 text-center text-sm">
        <span class="text-secondary opacity-70">Unauthorized access prohibited. </span>
        <router-link to="/shadow-garden/apply" class="apply-link font-semibold transition-colors">Request Access</router-link>
      </div>

      <transition name="status-fade">
        <div v-if="errorMessage" class="error-toast mt-4 p-3 rounded-lg flex items-center gap-3">
          <i class="fas fa-exclamation-triangle"></i>
          <span>{{ errorMessage }}</span>
        </div>
      </transition>
    </div>

    <!-- Background Decoration specific to login -->
    <div class="login-decoration">
       <div class="circle circle-1"></div>
       <div class="circle circle-2"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'

const router = useRouter()
const userStore = useUserStore()

const isLoading = ref(false)
const errorMessage = ref('')

const credentials = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    const response = await fetch('/shadow-garden/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: credentials.username,
        password: credentials.password
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      if (data.access_token) {
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        // Sync user store
        userStore.init()
        await userStore.fetchProfile()
        router.push('/dashboard')
      }
    } else {
      errorMessage.value = data.detail || 'Access Denied: Invalid Credentials'
    }
  } catch (error) {
    errorMessage.value = 'Communication failure. System unreachable.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  // Clear any old data
  if (localStorage.getItem('token')) {
    // Optional: auto-redirect if already logged in?
    // router.push('/dashboard')
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  z-index: 10;
}

.login-card {
  width: 100%;
  max-width: 440px;
  padding: 3rem 2.5rem;
  z-index: 20;
}

.logo-icon {
  width: 80px;
  height: 80px;
  border-radius: 24px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px -5px rgba(var(--primary-rgb), 0.5);
  transform: rotate(-5deg);
}

.floating {
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(-5deg); }
  50% { transform: translateY(-10px) rotate(2deg); }
}

.gradient-text {
  background: linear-gradient(135deg, var(--text-primary), var(--text-tertiary));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.form-group label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  margin-left: 0.25rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1.25rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.liquid-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: var(--text-primary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.liquid-input:focus {
  background: rgba(var(--primary-rgb), 0.05);
  border-color: var(--primary-color);
  box-shadow: 0 0 15px rgba(var(--primary-rgb), 0.1);
}

.liquid-input:focus + .input-icon {
  color: var(--primary-color);
}

.btn-login {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  border: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  filter: brightness(1.1);
}

.btn-login:active {
  transform: translateY(0);
}

.btn-login:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.apply-link {
  color: var(--primary-color);
  text-decoration: none;
}

.apply-link:hover {
  filter: brightness(1.2);
  text-shadow: 0 0 10px rgba(var(--primary-rgb), 0.3);
}

.error-toast {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #ef4444;
  font-size: 0.85rem;
  font-weight: 500;
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.status-fade-enter-active, .status-fade-leave-active {
  transition: all 0.3s ease;
}
.status-fade-enter-from, .status-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* Background elements unique to login */
.login-decoration .circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  z-index: 1;
  opacity: 0.5;
}

.circle-1 {
  width: 400px;
  height: 400px;
  background: var(--primary-color);
  top: -100px;
  right: -100px;
  animation: pulse 10s infinite alternate;
}

.circle-2 {
  width: 300px;
  height: 300px;
  background: var(--secondary-color);
  bottom: -50px;
  left: -50px;
  animation: pulse 8s infinite alternate-reverse;
}

@keyframes pulse {
  from { transform: scale(1); opacity: 0.3; }
  to { transform: scale(1.2); opacity: 0.6; }
}

@media (max-width: 480px) {
  .login-card {
    padding: 2rem 1.5rem;
  }
}
</style>
