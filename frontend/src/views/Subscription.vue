<template>
  <div class="subscription">
    <div class="page-header">
      <h1>Subscription Management</h1>
      <p>Manage your subscription plans and services</p>
    </div>

    <!-- Current Subscription Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-crown"></i>
          </div>
          <div class="card-content">
            <h3>{{ currentSubscription.plan }}</h3>
            <p>Current Plan</p>
            <span class="subscription-status" :class="currentSubscription.status">
              {{ currentSubscription.status }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon price">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="card-content">
            <h3>${{ currentSubscription.price }}</h3>
            <p>Monthly Price</p>
            <span class="billing-cycle">{{ currentSubscription.billingCycle }}</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon renewal">
            <i class="fas fa-sync"></i>
          </div>
          <div class="card-content">
            <h3>{{ formatDate(currentSubscription.renewalDate) }}</h3>
            <p>Next Renewal</p>
            <span class="renewal-status" :class="currentSubscription.autoRenew ? 'active' : 'inactive'">
              {{ currentSubscription.autoRenew ? 'Auto-renewal ON' : 'Auto-renewal OFF' }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon services">
            <i class="fas fa-box"></i>
          </div>
          <div class="card-content">
            <h3>{{ currentSubscription.services.length }}</h3>
            <p>Active Services</p>
            <span class="service-count">{{ currentSubscription.services.length }} services</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="upgrade-btn" @click="showPlansModal = true">
          <i class="fas fa-arrow-up"></i>
          Change Plan
        </button>
        <button class="service-btn" @click="showServiceModal = true">
          <i class="fas fa-plus"></i>
          Add Service
        </button>
        <button class="billing-btn" @click="goToBilling">
          <i class="fas fa-credit-card"></i>
          Billing
        </button>
        <button class="settings-btn" @click="showSettingsModal = true">
          <i class="fas fa-cog"></i>
          Settings
        </button>
      </div>
    </div>

    <!-- Current Plan Details -->
    <div class="plan-section">
      <div class="section-header">
        <h2>Current Plan Details</h2>
        <button class="change-plan-btn" @click="showPlansModal = true">
          Change Plan
        </button>
      </div>

      <div class="plan-details-card">
        <div class="plan-header">
          <div class="plan-info">
            <h3>{{ currentSubscription.plan }}</h3>
            <p>{{ currentSubscription.description }}</p>
          </div>
          <div class="plan-price">
            <span class="price">${{ currentSubscription.price }}</span>
            <span class="period">/{{ currentSubscription.billingCycle }}</span>
          </div>
        </div>

        <div class="plan-features">
          <div class="features-grid">
            <div 
              v-for="feature in currentSubscription.features" 
              :key="feature.name"
              class="feature-item"
              :class="{ 'disabled': !feature.included }"
            >
              <div class="feature-icon">
                <i :class="feature.included ? 'fas fa-check' : 'fas fa-times'"></i>
              </div>
              <div class="feature-content">
                <span class="feature-name">{{ feature.name }}</span>
                <span v-if="feature.limit" class="feature-limit">{{ feature.limit }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="plan-usage">
          <h4>Usage Statistics</h4>
          <div class="usage-grid">
            <div 
              v-for="usage in currentSubscription.usage" 
              :key="usage.metric"
              class="usage-item"
            >
              <div class="usage-header">
                <span class="usage-name">{{ usage.metric }}</span>
                <span class="usage-percentage">{{ usage.percentage }}%</span>
              </div>
              <div class="usage-bar-container">
                <div class="usage-bar">
                  <div 
                    class="usage-fill" 
                    :style="{ width: usage.percentage + '%' }"
                    :class="getUsageClass(usage.percentage)"
                  ></div>
                </div>
                <span class="usage-details">{{ usage.used }} / {{ usage.total }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Services -->
    <div class="services-section">
      <div class="section-header">
        <h2>Active Services</h2>
        <button class="add-service-btn" @click="showServiceModal = true">
          <i class="fas fa-plus"></i>
          Add Service
        </button>
      </div>

      <div class="services-grid">
        <div 
          v-for="service in activeServices" 
          :key="service.id"
          class="service-card"
          :class="{ 'expired': service.status === 'expired' }"
        >
          <div class="service-header">
            <div class="service-info">
              <h3>{{ service.name }}</h3>
              <p>{{ service.description }}</p>
            </div>
            <div class="service-status">
              <span :class="['status-badge', service.status]">{{ service.status }}</span>
            </div>
          </div>

          <div class="service-details">
            <div class="service-item">
              <label>Price:</label>
              <span>${{ service.price }}/{{ service.billingCycle }}</span>
            </div>
            <div class="service-item">
              <label>Started:</label>
              <span>{{ formatDate(service.startDate) }}</span>
            </div>
            <div class="service-item">
              <label>Renewal:</label>
              <span>{{ formatDate(service.renewalDate) }}</span>
            </div>
            <div class="service-item">
              <label>Usage:</label>
              <span>{{ service.usage }}{{ service.unit }}</span>
            </div>
          </div>

          <div class="service-actions">
            <button class="action-btn manage" @click="manageService(service)">
              <i class="fas fa-cog"></i>
              Manage
            </button>
            <button 
              class="action-btn cancel"
              @click="cancelService(service)"
              :disabled="service.status === 'expired'"
            >
              <i class="fas fa-times"></i>
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Subscription History -->
    <div class="history-section">
      <div class="section-header">
        <h2>Subscription History</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="historyFilter" @change="filterHistory">
              <option value="">All Time</option>
              <option value="30">Last 30 Days</option>
              <option value="90">Last 90 Days</option>
              <option value="365">Last Year</option>
            </select>
          </div>
          <button class="export-btn" @click="exportHistory">
            <i class="fas fa-download"></i>
            Export
          </button>
        </div>
      </div>

      <div class="history-table-container">
        <table class="history-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Action</th>
              <th>Plan/Service</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Period</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="record in filteredHistory" 
              :key="record.id"
              class="history-row"
            >
              <td>{{ formatDateTime(record.date) }}</td>
              <td>
                <span :class="['action-badge', record.type]">{{ record.action }}</span>
              </td>
              <td>{{ record.plan }}</td>
              <td>
                <span :class="['amount', record.type]">
                  {{ record.type === 'charge' ? '-' : '+' }}${{ record.amount }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', record.status]">{{ record.status }}</span>
              </td>
              <td>{{ record.period }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Plans Modal -->
    <div v-if="showPlansModal" class="modal-overlay" @click="closePlansModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Choose Your Plan</h2>
          <button class="close-btn" @click="closePlansModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="plans-grid">
            <div 
              v-for="plan in availablePlans" 
              :key="plan.id"
              class="plan-option"
              :class="{ 
                'selected': selectedPlan?.id === plan.id,
                'current': plan.name === currentSubscription.plan
              }"
              @click="selectPlan(plan)"
            >
              <div class="plan-header">
                <h3>{{ plan.name }}</h3>
                <span v-if="plan.name === currentSubscription.plan" class="current-badge">Current</span>
              </div>
              <div class="plan-price">
                <span class="price">${{ plan.price }}</span>
                <span class="period">/{{ plan.billingCycle }}</span>
              </div>
              <p class="plan-description">{{ plan.description }}</p>
              
              <div class="plan-features">
                <div 
                  v-for="feature in plan.features" 
                  :key="feature.name"
                  class="feature-item"
                >
                  <i :class="feature.included ? 'fas fa-check' : 'fas fa-times'"></i>
                  <span>{{ feature.name }}</span>
                  <span v-if="feature.limit" class="feature-limit">{{ feature.limit }}</span>
                </div>
              </div>

              <button 
                class="select-plan-btn"
                :class="{ 'disabled': plan.name === currentSubscription.plan }"
                @click.stop="changePlan(plan)"
              >
                {{ plan.name === currentSubscription.plan ? 'Current Plan' : 'Select Plan' }}
              </button>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closePlansModal">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Service Modal -->
    <div v-if="showServiceModal" class="modal-overlay" @click="closeServiceModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add Service</h2>
          <button class="close-btn" @click="closeServiceModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="service-form">
            <div class="form-group">
              <label>Select Service</label>
              <select v-model="serviceForm.serviceId">
                <option value="">Choose a service...</option>
                <option 
                  v-for="service in availableServices" 
                  :key="service.id"
                  :value="service.id"
                >
                  {{ service.name }} - ${{ service.price }}/{{ service.billingCycle }}
                </option>
              </select>
            </div>

            <div v-if="selectedService" class="service-details">
              <h3>{{ selectedService.name }}</h3>
              <p>{{ selectedService.description }}</p>
              
              <div class="service-features">
                <div 
                  v-for="feature in selectedService.features" 
                  :key="feature.name"
                  class="feature-item"
                >
                  <i :class="feature.included ? 'fas fa-check' : 'fas fa-times'"></i>
                  <span>{{ feature.name }}</span>
                  <span v-if="feature.limit" class="feature-limit">{{ feature.limit }}</span>
                </div>
              </div>

              <div class="pricing-info">
                <div class="price-item">
                  <label>Price:</label>
                  <span>${{ selectedService.price }}/{{ selectedService.billingCycle }}</span>
                </div>
                <div class="price-item">
                  <label>Setup Fee:</label>
                  <span>${{ selectedService.setupFee || 0 }}</span>
                </div>
                <div class="price-item">
                  <label>Trial Period:</label>
                  <span>{{ selectedService.trialDays || 0 }} days</span>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Billing Cycle</label>
              <select v-model="serviceForm.billingCycle">
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeServiceModal">Cancel</button>
          <button 
            class="btn-primary" 
            @click="addService"
            :disabled="!serviceForm.serviceId"
          >
            Add Service
          </button>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettingsModal" class="modal-overlay" @click="closeSettingsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Subscription Settings</h2>
          <button class="close-btn" @click="closeSettingsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="settings-form">
            <div class="setting-section">
              <h3>Auto-renewal Settings</h3>
              <div class="setting-item">
                <label>Enable Auto-renewal</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="subscriptionSettings.autoRenew"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>Renewal Reminder (days before)</label>
                <input 
                  v-model.number="subscriptionSettings.renewalReminder" 
                  type="number" 
                  min="1" 
                  max="30"
                />
              </div>
            </div>

            <div class="setting-section">
              <h3>Notification Preferences</h3>
              <div class="setting-item">
                <label>Email Notifications</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="subscriptionSettings.emailNotifications"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>Usage Alerts</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="subscriptionSettings.usageAlerts"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>Billing Updates</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="subscriptionSettings.billingUpdates"
                  />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="setting-section">
              <h3>Service Management</h3>
              <div class="setting-item">
                <label>Allow Service Cancellation</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="subscriptionSettings.allowCancellation"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>Cancellation Period (days)</label>
                <input 
                  v-model.number="subscriptionSettings.cancellationPeriod" 
                  type="number" 
                  min="1" 
                  max="90"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeSettingsModal">Cancel</button>
          <button class="btn-primary" @click="saveSettings">Save Settings</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

const router = useRouter()

// Reactive state
const loading = ref(false)
const historyFilter = ref('')
const showPlansModal = ref(false)
const showServiceModal = ref(false)
const showSettingsModal = ref(false)
const selectedPlan = ref(null)

// Current subscription
const currentSubscription = reactive({
  plan: 'Professional',
  status: 'active',
  price: 99,
  billingCycle: 'month',
  renewalDate: '2024-02-01',
  autoRenew: true,
  description: 'Perfect for growing teams and businesses',
  features: [
    { name: 'Unlimited Users', included: true },
    { name: '100GB Storage', included: true, limit: '100GB' },
    { name: 'API Access', included: true },
    { name: 'Priority Support', included: true },
    { name: 'Advanced Analytics', included: true },
    { name: 'Custom Integrations', included: true }
  ],
  usage: [
    { metric: 'Storage', used: '67GB', total: '100GB', percentage: 67 },
    { metric: 'API Calls', used: '67,000', total: '100,000', percentage: 67 },
    { metric: 'Team Members', used: '15', total: 'Unlimited', percentage: 15 },
    { metric: 'Projects', used: '45', total: 'Unlimited', percentage: 45 }
  ],
  services: ['Main Plan', 'Backup Service', 'Analytics Plus']
})

// Subscription settings
const subscriptionSettings = reactive({
  autoRenew: true,
  renewalReminder: 7,
  emailNotifications: true,
  usageAlerts: true,
  billingUpdates: true,
  allowCancellation: true,
  cancellationPeriod: 30
})

// Service form
const serviceForm = reactive({
  serviceId: '',
  billingCycle: 'monthly'
})

// Mock data
const activeServices = ref([
  {
    id: 1,
    name: 'Backup Service',
    description: 'Automated daily backups with 30-day retention',
    price: 29,
    billingCycle: 'month',
    status: 'active',
    startDate: '2024-01-01',
    renewalDate: '2024-02-01',
    usage: 250,
    unit: 'GB'
  },
  {
    id: 2,
    name: 'Analytics Plus',
    description: 'Advanced analytics and reporting features',
    price: 49,
    billingCycle: 'month',
    status: 'active',
    startDate: '2024-01-01',
    renewalDate: '2024-02-01',
    usage: 15000,
    unit: 'events'
  },
  {
    id: 3,
    name: 'Priority Support',
    description: '24/7 priority support with dedicated account manager',
    price: 99,
    billingCycle: 'month',
    status: 'active',
    startDate: '2024-01-01',
    renewalDate: '2024-02-01',
    usage: 45,
    unit: 'tickets'
  }
])

const subscriptionHistory = ref([
  {
    id: 1,
    date: '2024-01-01',
    action: 'Plan Upgrade',
    plan: 'Professional',
    amount: 99.00,
    type: 'charge',
    status: 'completed',
    period: 'Jan 2024'
  },
  {
    id: 2,
    date: '2023-12-15',
    action: 'Service Added',
    plan: 'Backup Service',
    amount: 29.00,
    type: 'charge',
    status: 'completed',
    period: 'Monthly'
  },
  {
    id: 3,
    date: '2023-12-01',
    action: 'Plan Renewal',
    plan: 'Professional',
    amount: 99.00,
    type: 'charge',
    status: 'completed',
    period: 'Dec 2023'
  },
  {
    id: 4,
    date: '2023-11-01',
    action: 'Plan Renewal',
    plan: 'Professional',
    amount: 99.00,
    type: 'charge',
    status: 'completed',
    period: 'Nov 2023'
  }
])

const availablePlans = ref([
  {
    id: 1,
    name: 'Starter',
    price: 29,
    billingCycle: 'month',
    description: 'Perfect for individuals and small teams',
    features: [
      { name: 'Up to 5 Users', included: true, limit: '5' },
      { name: '10GB Storage', included: true, limit: '10GB' },
      { name: 'Basic Analytics', included: true },
      { name: 'Email Support', included: true },
      { name: 'API Access', included: false },
      { name: 'Priority Support', included: false }
    ]
  },
  {
    id: 2,
    name: 'Professional',
    price: 99,
    billingCycle: 'month',
    description: 'Perfect for growing teams',
    features: [
      { name: 'Unlimited Users', included: true },
      { name: '100GB Storage', included: true, limit: '100GB' },
      { name: 'API Access', included: true },
      { name: 'Priority Support', included: true },
      { name: 'Advanced Analytics', included: true },
      { name: 'Custom Integrations', included: true }
    ]
  },
  {
    id: 3,
    name: 'Enterprise',
    price: 299,
    billingCycle: 'month',
    description: 'For large organizations',
    features: [
      { name: 'Unlimited Users', included: true },
      { name: 'Unlimited Storage', included: true },
      { name: 'API Access', included: true },
      { name: '24/7 Phone Support', included: true },
      { name: 'Advanced Analytics', included: true },
      { name: 'Custom Integrations', included: true },
      { name: 'Dedicated Account Manager', included: true },
      { name: 'SLA Guarantee', included: true }
    ]
  }
])

const availableServices = ref([
  {
    id: 1,
    name: 'Backup Service',
    description: 'Automated daily backups with 30-day retention',
    price: 29,
    billingCycle: 'month',
    setupFee: 0,
    trialDays: 14,
    features: [
      { name: 'Daily Backups', included: true },
      { name: '30-day Retention', included: true },
      { name: 'One-click Restore', included: true },
      { name: 'Encrypted Storage', included: true }
    ]
  },
  {
    id: 2,
    name: 'Analytics Plus',
    description: 'Advanced analytics and reporting features',
    price: 49,
    billingCycle: 'month',
    setupFee: 0,
    trialDays: 7,
    features: [
      { name: 'Custom Reports', included: true },
      { name: 'Real-time Analytics', included: true },
      { name: 'Data Export', included: true },
      { name: 'Advanced Dashboards', included: true }
    ]
  },
  {
    id: 3,
    name: 'Priority Support',
    description: '24/7 priority support with dedicated account manager',
    price: 99,
    billingCycle: 'month',
    setupFee: 0,
    trialDays: 0,
    features: [
      { name: '24/7 Support', included: true },
      { name: 'Dedicated Account Manager', included: true },
      { name: 'Priority Queue', included: true },
      { name: 'SLA Guarantee', included: true }
    ]
  }
])

// Computed properties
const filteredHistory = computed(() => {
  let filtered = subscriptionHistory.value
  
  if (historyFilter.value) {
    const days = parseInt(historyFilter.value)
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000)
    filtered = filtered.filter(record => 
      new Date(record.date) >= cutoffDate
    )
  }
  
  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const selectedService = computed(() => {
  if (!serviceForm.serviceId) return null
  return availableServices.value.find(s => s.id === parseInt(serviceForm.serviceId))
})

// Methods
const loadSubscriptionData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/subscription')
    // if (response.success) {
    //   Object.assign(currentSubscription, response.currentSubscription)
    //   activeServices.value = response.services || []
    //   subscriptionHistory.value = response.history || []
    //   subscriptionSettings.value = response.settings || subscriptionSettings
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading subscription data:', error)
    showError('Failed to load subscription data')
  } finally {
    loading.value = false
  }
}

const filterHistory = () => {
  // This is reactive, no additional action needed
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const getUsageClass = (percentage) => {
  if (percentage >= 90) return 'critical'
  if (percentage >= 75) return 'warning'
  return 'normal'
}

const selectPlan = (plan) => {
  selectedPlan.value = plan
}

const changePlan = async (plan) => {
  if (plan.name === currentSubscription.plan) return
  
  const confirmed = await showConfirm(`Are you sure you want to change to ${plan.name} plan?`)
  if (!confirmed) return

  try {
    // const response = await apiPost('/subscription/change-plan', { planId: plan.id })
    // if (response.success) {
    //   currentSubscription.plan = plan.name
    //   currentSubscription.price = plan.price
    //   showSuccess('Plan changed successfully')
    //   closePlansModal()
    // }
    
    // For demo, simulate change
    currentSubscription.plan = plan.name
    currentSubscription.price = plan.price
    showSuccess('Plan changed successfully')
    closePlansModal()
  } catch (error) {
    console.error('Error changing plan:', error)
    showError('Failed to change plan')
  }
}

const addService = async () => {
  if (!serviceForm.serviceId) {
    showError('Please select a service')
    return
  }

  try {
    // const response = await apiPost('/subscription/add-service', serviceForm)
    // if (response.success) {
    //   activeServices.value.push(response.service)
    //   showSuccess('Service added successfully')
    //   closeServiceModal()
    // }
    
    // For demo, simulate addition
    const service = selectedService.value
    const newService = {
      id: Date.now(),
      name: service.name,
      description: service.description,
      price: service.price,
      billingCycle: serviceForm.billingCycle,
      status: 'active',
      startDate: new Date().toISOString().split('T')[0],
      renewalDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      usage: 0,
      unit: 'units'
    }
    
    activeServices.value.push(newService)
    showSuccess('Service added successfully')
    closeServiceModal()
  } catch (error) {
    console.error('Error adding service:', error)
    showError('Failed to add service')
  }
}

const manageService = (service) => {
  showSuccess(`Managing service: ${service.name}`)
}

const cancelService = async (service) => {
  const confirmed = await showConfirm(`Are you sure you want to cancel ${service.name}?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/subscription/cancel-service/${service.id}`)
    // if (response.success) {
    //   service.status = 'cancelled'
    //   showSuccess('Service cancelled successfully')
    // }
    
    // For demo, simulate cancellation
    service.status = 'cancelled'
    showSuccess('Service cancelled successfully')
  } catch (error) {
    console.error('Error cancelling service:', error)
    showError('Failed to cancel service')
  }
}

const saveSettings = async () => {
  try {
    // const response = await apiPut('/subscription/settings', subscriptionSettings)
    // if (response.success) {
    //   showSuccess('Settings saved successfully')
    //   closeSettingsModal()
    // }
    
    // For demo, simulate save
    showSuccess('Settings saved successfully')
    closeSettingsModal()
  } catch (error) {
    console.error('Error saving settings:', error)
    showError('Failed to save settings')
  }
}

const exportHistory = async () => {
  try {
    // const response = await apiPost('/subscription/export-history')
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `subscription-history-${new Date().toISOString().split('T')[0]}.csv`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('History exported successfully')
    // }
    
    // For demo, simulate export
    showSuccess('History exported successfully')
  } catch (error) {
    console.error('Error exporting history:', error)
    showError('Failed to export history')
  }
}

const goToBilling = () => {
  router.push('/billing')
}

// Modal close methods
const closePlansModal = () => {
  showPlansModal.value = false
  selectedPlan.value = null
}

const closeServiceModal = () => {
  showServiceModal.value = false
  serviceForm.serviceId = ''
  serviceForm.billingCycle = 'monthly'
}

const closeSettingsModal = () => {
  showSettingsModal.value = false
}

// Lifecycle
onMounted(() => {
  loadSubscriptionData()
})
</script>

<style scoped>
.subscription {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.overview-section {
  margin-bottom: 3rem;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.overview-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  text-align: center;
}

.card-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.card-icon.price {
  background: var(--success-color);
}

.card-icon.renewal {
  background: var(--warning-color);
}

.card-icon.services {
  background: var(--info-color);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.card-content p {
  color: var(--text-secondary);
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.subscription-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  text-transform: capitalize;
}

.subscription-status.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.subscription-status.inactive {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.billing-cycle,
.renewal-status,
.service-count {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.renewal-status.active {
  color: var(--success-color);
}

.renewal-status.inactive {
  color: var(--warning-color);
}

.actions-section {
  margin-bottom: 3rem;
}

.action-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.upgrade-btn,
.service-btn,
.billing-btn,
.settings-btn {
  padding: 1rem 2rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.upgrade-btn:hover,
.service-btn:hover,
.billing-btn:hover,
.settings-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.service-btn {
  background: var(--success-color);
}

.service-btn:hover {
  background: var(--success-hover);
}

.billing-btn {
  background: var(--info-color);
}

.billing-btn:hover {
  background: var(--info-hover);
}

.settings-btn {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.settings-btn:hover {
  background: var(--glass-bg-hover);
}

.plan-section,
.services-section,
.history-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.change-plan-btn,
.add-service-btn {
  padding: 0.75rem 1.25rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.change-plan-btn:hover,
.add-service-btn:hover {
  background: var(--primary-hover);
}

.plan-details-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.plan-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.5rem;
}

.plan-info p {
  margin: 0;
  color: var(--text-secondary);
}

.plan-price {
  text-align: right;
}

.plan-price .price {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
}

.plan-price .period {
  color: var(--text-secondary);
  font-size: 1rem;
}

.plan-features {
  margin-bottom: 2rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.feature-item.disabled {
  opacity: 0.5;
}

.feature-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-icon i {
  color: var(--success-color);
}

.feature-item.disabled .feature-icon i {
  color: var(--danger-color);
}

.feature-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.feature-name {
  color: var(--text-primary);
  font-weight: 500;
}

.feature-limit {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.plan-usage h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.usage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.usage-item {
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
  padding: 1rem;
}

.usage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.usage-name {
  font-weight: 600;
  color: var(--text-primary);
}

.usage-percentage {
  font-weight: 600;
  color: var(--text-secondary);
}

.usage-bar-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.usage-bar {
  width: 100%;
  height: 8px;
  background: var(--glass-bg-primary);
  border-radius: 4px;
  overflow: hidden;
}

.usage-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.usage-fill.normal {
  background: var(--success-color);
}

.usage-fill.warning {
  background: var(--warning-color);
}

.usage-fill.critical {
  background: var(--danger-color);
}

.usage-details {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.service-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.service-card:hover {
  transform: translateY(-2px);
}

.service-card.expired {
  opacity: 0.6;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.service-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.service-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.cancelled {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.expired {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.service-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.service-item label {
  color: var(--text-secondary);
  font-weight: 500;
}

.service-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.service-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn:hover:not(:disabled) {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.manage:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.cancel:hover:not(:disabled) {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-dropdown select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.export-btn {
  padding: 0.75rem 1.25rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.export-btn:hover {
  background: var(--primary-hover);
}

.history-table-container {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--glass-bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.history-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.history-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.history-row {
  transition: background 0.3s ease;
}

.history-row:hover {
  background: var(--glass-bg-hover);
}

.action-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.action-badge.upgrade {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.action-badge.renewal {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.action-badge.cancellation {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.amount {
  font-weight: 600;
}

.amount.charge {
  color: var(--danger-color);
}

.amount.credit {
  color: var(--success-color);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  max-width: 900px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1200px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.plan-option {
  background: var(--glass-bg-primary);
  border: 2px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.plan-option:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.plan-option.selected {
  border-color: var(--primary-color);
}

.plan-option.current {
  border-color: var(--success-color);
}

.plan-option .plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.plan-option .plan-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.current-badge {
  background: var(--success-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.plan-option .plan-price {
  margin-bottom: 1rem;
}

.plan-option .plan-price .price {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.plan-option .plan-price .period {
  color: var(--text-secondary);
  font-size: 1rem;
}

.plan-option .plan-description {
  color: var(--text-secondary);
  margin-bottom: 2rem;
  line-height: 1.5;
}

.plan-option .plan-features {
  margin-bottom: 2rem;
}

.plan-option .feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.plan-option .feature-item i {
  color: var(--success-color);
}

.plan-option .feature-item.disabled i {
  color: var(--danger-color);
}

.select-plan-btn {
  width: 100%;
  padding: 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.select-plan-btn:hover:not(.disabled) {
  background: var(--primary-hover);
}

.select-plan-btn.disabled {
  background: var(--glass-bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.service-form,
.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-primary);
}

.form-group select,
.form-group input {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.service-details {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.service-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.service-details p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
}

.service-features {
  margin-bottom: 1rem;
}

.service-features .feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.service-features .feature-item i {
  color: var(--success-color);
}

.pricing-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.price-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.price-item label {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.price-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.setting-section {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.setting-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-item label {
  font-weight: 500;
  color: var(--text-primary);
}

.setting-item input,
.setting-item select {
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch .slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--text-tertiary);
  transition: 0.4s;
  border-radius: 24px;
}

.switch .slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

.switch input:checked + .slider {
  background-color: var(--primary-color);
}

.switch input:checked + .slider:before {
  transform: translateX(26px);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
}

@media (max-width: 768px) {
  .subscription {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .usage-grid {
    grid-template-columns: 1fr;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .service-details {
    grid-template-columns: 1fr;
  }
  
  .pricing-info {
    grid-template-columns: 1fr;
  }
  
  .plans-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
