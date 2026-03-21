<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>Create Order</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>Set up a new growth campaign order</p>
    
</div>

    <div class="page-actions">

      <button class="btn btn-secondary" @click="$router.go(-1)">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 12 L5 12 M12 19 L5 12 L12 5" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        Back
      </button>
    
</div>

    <div class="order-form-content">
      <form @submit.prevent="submitOrder" class="order-form">
        <div class="form-section">
          <h2>Order Details</h2>
          
          <div class="form-group">
            <label for="orderName">Order Name *</label>
            <input 
              id="orderName"
              v-model="order.name"
              type="text" 
              required
              placeholder="Enter order name"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="orderType">Order Type *</label>
            <select id="orderType" v-model="order.type" required class="form-select">
              <option value="">Select order type</option>
              <option value="growth">Growth Campaign</option>
              <option value="marketing">Marketing Push</option>
              <option value="engagement">Engagement Boost</option>
              <option value="retention">Retention Campaign</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="budget">Budget (KPI) *</label>
            <input 
              id="budget"
              v-model.number="order.budget"
              type="number" 
              required
              min="100"
              max="10000"
              placeholder="Enter budget amount"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="duration">Duration (days) *</label>
            <input 
              id="duration"
              v-model.number="order.duration"
              type="number" 
              required
              min="1"
              max="365"
              placeholder="Campaign duration"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-section">
          <h2>Target Settings</h2>
          
          <div class="form-group">
            <label for="targetAudience">Target Audience</label>
            <select id="targetAudience" v-model="order.targetAudience" class="form-select">
              <option value="all">All Users</option>
              <option value="new">New Users</option>
              <option value="active">Active Users</option>
              <option value="premium">Premium Users</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="targetRegion">Target Region</label>
            <select id="targetRegion" v-model="order.targetRegion" class="form-select">
              <option value="global">Global</option>
              <option value="north-america">North America</option>
              <option value="europe">Europe</option>
              <option value="asia">Asia</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Target Metrics</label>
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="order.metrics.impressions" />
                <span>Impressions</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="order.metrics.clicks" />
                <span>Clicks</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="order.metrics.conversions" />
                <span>Conversions</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="order.metrics.retention" />
                <span>Retention</span>
              </label>
            </div>
          </div>
        </div>

        <div class="form-section">
          <h2>Schedule</h2>
          
          <div class="form-group">
            <label for="startDate">Start Date *</label>
            <input 
              id="startDate"
              v-model="order.startDate"
              type="datetime-local" 
              required
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="endDate">End Date</label>
            <input 
              id="endDate"
              v-model="order.endDate"
              type="datetime-local" 
              class="form-input"
            />
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="saveDraft">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 21 L5 21 C3.9 21 3 20.1 3 19 L3 5 C3 3.9 3.9 3 5 3 L16 3 L21 8 L21 19 C21 20.1 20.1 21 19 21 Z" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M17 21 L17 13 L7 13 L7 21" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M7 3 L7 8 L15 8" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            Save Draft
          </button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 11 L12 14 L22 4" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M21 12 L21 19 C21 20.1 20.1 21 19 21 L5 21 C3.9 21 3 20.1 3 19 L3 5 C3 3.9 3.9 3 5 3 L16 3" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            {{ isSubmitting ? 'Creating...' : 'Create Order' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isSubmitting = ref(false)

const order = ref({
  name: '',
  type: '',
  budget: 1000,
  duration: 30,
  targetAudience: 'all',
  targetRegion: 'global',
  metrics: {
    impressions: true,
    clicks: true,
    conversions: false,
    retention: false
  },
  startDate: '',
  endDate: ''
})

const submitOrder = async () => {
  isSubmitting.value = true
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    console.log('Order created:', order.value)
    router.push('/growth-orders')
  } catch (error) {
    console.error('Error creating order:', error)
  } finally {
    isSubmitting.value = false
  }
}

const saveDraft = () => {
  console.log('Draft saved:', order.value)
}

onMounted(() => {
  // Set default start date to tomorrow
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  order.value.startDate = tomorrow.toISOString().slice(0, 16)
})
</script>

<style scoped>
.order-form-content {
  max-width: 800px;
  margin: 0 auto;
}

.order-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
}

.form-section h2 {
  margin: 0 0 1.5rem 0;
  color: #f1f5f9;
  font-size: 1.25rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #f1f5f9;
  font-weight: 500;
  font-size: 0.875rem;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(255, 255, 255, 0.08);
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #f1f5f9;
  font-size: 0.875rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  accent-color: #3b82f6;
}

.form-actions {
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.icon {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 768px) {
  .form-section {
    padding: 1.5rem;
  }
  
  .checkbox-group {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>

<style scoped>
.legacy-page-container {
  padding: 1rem;
}
.page-title { margin-bottom: 0.5rem; }
.page-subtitle { color: var(--text-secondary); margin-bottom: 1rem; }
.page-actions { margin-bottom: 1.5rem; }
</style>
