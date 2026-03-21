<template>
  <div class="register-container">
    <div class="glass-panel register-form">
      <div class="header-section text-center mb-8">
        <div class="logo-placeholder mb-4 flex justify-center">
            <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">
                <i class="fas fa-crown text-3xl text-white"></i>
            </div>
        </div>
        <h2 class="register-title font-bold text-white">Apply for Access</h2>
        <p class="text-secondary text-base">Join the Digital Headquarters Elite</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <div class="form-group w-full">
          <label for="username">Username</label>
          <input id="username" v-model="form.username" type="text" required class="liquid-input w-full" />
        </div>

        <div class="form-group w-full">
          <label for="password">Password</label>
          <input id="password" v-model="form.password" type="password" required class="liquid-input w-full" />
        </div>

        <div class="form-group w-full">
          <label for="confirmPassword">Confirm Password</label>
          <input id="confirmPassword" v-model="form.confirm_password" type="password" required class="liquid-input w-full" />
        </div>

        <button type="submit" :disabled="isLoading" class="btn btn-primary w-full mt-4">
          <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
          {{ isLoading ? 'Submitting...' : 'Apply' }}
        </button>
      </form>

      <div class="mt-4 text-center text-sm">
        <span class="text-secondary">Already applied? </span>
        <router-link to="/shadow-garden/login" class="text-primary hover:underline" style="color: var(--primary-color)">Log In</router-link>
      </div>

      <div v-if="errorMessage" class="mt-4 p-3 rounded glass-card" style="border-color: var(--danger-color); color: var(--danger-color)">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="mt-4 p-3 rounded glass-card" style="border-color: var(--success-color); color: var(--success-color)">
        {{ successMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const form = reactive({
  username: '',
  password: '',
  confirm_password: ''
})

const handleRegister = async () => {
  if (form.password !== form.confirm_password) {
    errorMessage.value = 'Passwords do not match.'
    return
  }
  
  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    const response = await fetch('/shadow-garden/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    
    const data = await response.json()
    
    if (response.ok) {
      successMessage.value = 'Application submitted successfully. Waiting for Admin approval.'
      setTimeout(() => {
        router.push('/shadow-garden/login')
      }, 3000)
    } else {
      errorMessage.value = data.detail || 'Registration failed'
    }
  } catch (error) {
    errorMessage.value = 'Network error. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 1rem;
}

.register-form {
  width: 100%;
  max-width: 480px;
  padding: 2.5rem;
}

.register-title {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

.liquid-input {
  width: 100%;
}

.w-full {
  width: 100%;
}
</style>
