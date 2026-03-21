<template>
  <div class="billing">
    <div class="page-header">
      <h1>Billing & Invoicing</h1>
      <p>Manage your subscription, payments, and billing information</p>
    </div>

    <!-- Billing Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-credit-card"></i>
          </div>
          <div class="card-content">
            <h3>{{ billingInfo.currentPlan }}</h3>
            <p>Current Plan</p>
            <span class="plan-status" :class="billingInfo.status">{{ billingInfo.status }}</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon amount">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="card-content">
            <h3>${{ billingInfo.currentAmount }}</h3>
            <p>Current Bill</p>
            <span class="due-date">Due {{ formatDate(billingInfo.dueDate) }}</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon usage">
            <i class="fas fa-chart-pie"></i>
          </div>
          <div class="card-content">
            <h3>{{ billingInfo.usagePercentage }}%</h3>
            <p>Usage This Month</p>
            <div class="usage-bar">
              <div 
                class="usage-fill" 
                :style="{ width: billingInfo.usagePercentage + '%' }"
              ></div>
            </div>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon next">
            <i class="fas fa-calendar"></i>
          </div>
          <div class="card-content">
            <h3>{{ formatDate(billingInfo.nextBilling) }}</h3>
            <p>Next Billing</p>
            <span class="billing-cycle">{{ billingInfo.billingCycle }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="upgrade-btn" @click="showUpgradeModal = true">
          <i class="fas fa-arrow-up"></i>
          Upgrade Plan
        </button>
        <button class="payment-btn" @click="showPaymentModal = true">
          <i class="fas fa-plus"></i>
          Add Payment Method
        </button>
        <button class="invoice-btn" @click="showInvoiceModal = true">
          <i class="fas fa-file-invoice"></i>
          Create Invoice
        </button>
        <button class="settings-btn" @click="showSettingsModal = true">
          <i class="fas fa-cog"></i>
          Billing Settings
        </button>
      </div>
    </div>

    <!-- Current Plan Details -->
    <div class="plan-section">
      <div class="section-header">
        <h2>Current Plan</h2>
        <button class="change-plan-btn" @click="showUpgradeModal = true">
          Change Plan
        </button>
      </div>

      <div class="plan-card">
        <div class="plan-header">
          <div class="plan-info">
            <h3>{{ billingInfo.currentPlan }}</h3>
            <p>{{ billingInfo.planDescription }}</p>
          </div>
          <div class="plan-price">
            <span class="price">${{ billingInfo.price }}</span>
            <span class="period">/{{ billingInfo.billingCycle }}</span>
          </div>
        </div>

        <div class="plan-features">
          <div 
            v-for="feature in billingInfo.features" 
            :key="feature.name"
            class="feature-item"
            :class="{ 'disabled': !feature.included }"
          >
            <i :class="feature.included ? 'fas fa-check' : 'fas fa-times'"></i>
            <span>{{ feature.name }}</span>
            <span v-if="feature.limit" class="feature-limit">{{ feature.limit }}</span>
          </div>
        </div>

        <div class="plan-usage">
          <h4>Usage This Month</h4>
          <div class="usage-items">
            <div 
              v-for="usage in billingInfo.usageDetails" 
              :key="usage.type"
              class="usage-item"
            >
              <div class="usage-info">
                <span class="usage-name">{{ usage.type }}</span>
                <span class="usage-amount">{{ usage.used }} / {{ usage.limit }}</span>
              </div>
              <div class="usage-progress">
                <div 
                  class="usage-bar"
                  :class="getUsageClass(usage.percentage)"
                >
                  <div 
                    class="usage-fill" 
                    :style="{ width: usage.percentage + '%' }"
                  ></div>
                </div>
                <span class="usage-percentage">{{ usage.percentage }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Methods -->
    <div class="payment-section">
      <div class="section-header">
        <h2>Payment Methods</h2>
        <button class="add-payment-btn" @click="showPaymentModal = true">
          <i class="fas fa-plus"></i>
          Add Payment Method
        </button>
      </div>

      <div class="payment-methods-grid">
        <div 
          v-for="method in paymentMethods" 
          :key="method.id"
          class="payment-card"
          :class="{ 'default': method.isDefault }"
        >
          <div class="payment-header">
            <div class="payment-type">
              <i :class="getPaymentIcon(method.type)"></i>
              <span>{{ method.type }}</span>
            </div>
            <div class="payment-actions">
              <button 
                v-if="!method.isDefault"
                class="action-btn default"
                @click="setDefaultPayment(method)"
                title="Set as Default"
              >
                <i class="fas fa-star"></i>
              </button>
              <button 
                class="action-btn edit"
                @click="editPaymentMethod(method)"
                title="Edit"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button 
                class="action-btn delete"
                @click="deletePaymentMethod(method)"
                title="Delete"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>

          <div class="payment-details">
            <div class="card-info">
              <span class="card-number">{{ maskCardNumber(method.cardNumber) }}</span>
              <span class="card-expiry">{{ method.expiry }}</span>
            </div>
            <div class="card-holder">
              <span>{{ method.cardholder }}</span>
            </div>
          </div>

          <div v-if="method.isDefault" class="default-badge">
            <i class="fas fa-star"></i>
            Default
          </div>
        </div>
      </div>
    </div>

    <!-- Billing History -->
    <div class="history-section">
      <div class="section-header">
        <h2>Billing History</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="historyFilter" @change="filterHistory">
              <option value="">All Time</option>
              <option value="30">Last 30 Days</option>
              <option value="90">Last 90 Days</option>
              <option value="365">Last Year</option>
            </select>
          </div>
          <button class="export-btn" @click="exportBillingHistory">
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
              <th>Description</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Payment Method</th>
              <th>Invoice</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="transaction in filteredHistory" 
              :key="transaction.id"
              class="transaction-row"
            >
              <td>{{ formatDate(transaction.date) }}</td>
              <td>
                <div class="transaction-info">
                  <span class="transaction-desc">{{ transaction.description }}</span>
                  <span class="transaction-period">{{ transaction.period }}</span>
                </div>
              </td>
              <td>
                <span :class="['amount', transaction.type]">
                  {{ transaction.type === 'charge' ? '-' : '+' }}${{ transaction.amount }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', transaction.status]">{{ transaction.status }}</span>
              </td>
              <td>{{ transaction.paymentMethod }}</td>
              <td>
                <button 
                  class="invoice-btn-small"
                  @click="viewInvoice(transaction)"
                  title="View Invoice"
                >
                  <i class="fas fa-file-invoice"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Upgrade Plan Modal -->
    <div v-if="showUpgradeModal" class="modal-overlay" @click="closeUpgradeModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Choose Your Plan</h2>
          <button class="close-btn" @click="closeUpgradeModal">
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
                'current': plan.name === billingInfo.currentPlan
              }"
              @click="selectPlan(plan)"
            >
              <div class="plan-header">
                <h3>{{ plan.name }}</h3>
                <span v-if="plan.name === billingInfo.currentPlan" class="current-badge">Current</span>
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
                :class="{ 'disabled': plan.name === billingInfo.currentPlan }"
                @click.stop="upgradePlan(plan)"
              >
                {{ plan.name === billingInfo.currentPlan ? 'Current Plan' : 'Select Plan' }}
              </button>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeUpgradeModal">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Payment Method Modal -->
    <div v-if="showPaymentModal" class="modal-overlay" @click="closePaymentModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add Payment Method</h2>
          <button class="close-btn" @click="closePaymentModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="payment-form">
            <div class="form-group">
              <label>Card Type</label>
              <select v-model="paymentForm.type">
                <option value="Credit Card">Credit Card</option>
                <option value="Debit Card">Debit Card</option>
              </select>
            </div>

            <div class="form-group">
              <label>Card Number</label>
              <input 
                v-model="paymentForm.cardNumber" 
                type="text" 
                placeholder="1234 5678 9012 3456"
                maxlength="19"
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Expiry Date</label>
                <input 
                  v-model="paymentForm.expiry" 
                  type="text" 
                  placeholder="MM/YY"
                  maxlength="5"
                />
              </div>
              <div class="form-group">
                <label>CVV</label>
                <input 
                  v-model="paymentForm.cvv" 
                  type="text" 
                  placeholder="123"
                  maxlength="4"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Cardholder Name</label>
              <input 
                v-model="paymentForm.cardholder" 
                type="text" 
                placeholder="John Doe"
              />
            </div>

            <div class="form-group">
              <label>Billing Address</label>
              <input 
                v-model="paymentForm.address" 
                type="text" 
                placeholder="123 Main St, City, State 12345"
              />
            </div>

            <div class="form-group">
              <label>
                <input 
                  type="checkbox" 
                  v-model="paymentForm.setDefault"
                />
                Set as default payment method
              </label>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closePaymentModal">Cancel</button>
          <button class="btn-primary" @click="addPaymentMethod">Add Payment Method</button>
        </div>
      </div>
    </div>

    <!-- Billing Settings Modal -->
    <div v-if="showSettingsModal" class="modal-overlay" @click="closeSettingsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Billing Settings</h2>
          <button class="close-btn" @click="closeSettingsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="settings-form">
            <div class="setting-section">
              <h3>Notifications</h3>
              <div class="setting-item">
                <label>Email Notifications</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="billingSettings.emailNotifications"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>Payment Reminders</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="billingSettings.paymentReminders"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>Usage Alerts</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="billingSettings.usageAlerts"
                  />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="setting-section">
              <h3>Billing Preferences</h3>
              <div class="setting-item">
                <label>Auto-renew Subscription</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="billingSettings.autoRenew"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>Billing Cycle</label>
                <select v-model="billingSettings.billingCycle">
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>
              <div class="setting-item">
                <label>Payment Method</label>
                <select v-model="billingSettings.defaultPayment">
                  <option 
                    v-for="method in paymentMethods" 
                    :key="method.id"
                    :value="method.id"
                  >
                    {{ method.type }} ending in {{ method.cardNumber.slice(-4) }}
                  </option>
                </select>
              </div>
            </div>

            <div class="setting-section">
              <h3>Tax Information</h3>
              <div class="setting-item">
                <label>Tax ID</label>
                <input 
                  v-model="billingSettings.taxId" 
                  type="text" 
                  placeholder="Enter your tax ID"
                />
              </div>
              <div class="setting-item">
                <label>VAT Number</label>
                <input 
                  v-model="billingSettings.vatNumber" 
                  type="text" 
                  placeholder="Enter VAT number"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeSettingsModal">Cancel</button>
          <button class="btn-primary" @click="saveBillingSettings">Save Settings</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const historyFilter = ref('')
const showUpgradeModal = ref(false)
const showPaymentModal = ref(false)
const showSettingsModal = ref(false)
const showInvoiceModal = ref(false)
const selectedPlan = ref(null)

// Billing info
const billingInfo = reactive({
  currentPlan: 'Professional',
  status: 'active',
  currentAmount: 99.00,
  dueDate: '2024-02-01',
  usagePercentage: 67,
  nextBilling: '2024-02-01',
  billingCycle: 'month',
  planDescription: 'Perfect for growing teams',
  price: 99,
  features: [
    { name: 'Unlimited Users', included: true },
    { name: '100GB Storage', included: true, limit: '100GB' },
    { name: 'API Access', included: true },
    { name: 'Priority Support', included: true },
    { name: 'Advanced Analytics', included: true },
    { name: 'Custom Integrations', included: true }
  ],
  usageDetails: [
    { type: 'Storage', used: '67GB', limit: '100GB', percentage: 67 },
    { type: 'API Calls', used: '67,000', limit: '100,000', percentage: 67 },
    { type: 'Team Members', used: '15', limit: 'Unlimited', percentage: 15 },
    { type: 'Projects', used: '45', limit: 'Unlimited', percentage: 45 }
  ]
})

// Billing settings
const billingSettings = reactive({
  emailNotifications: true,
  paymentReminders: true,
  usageAlerts: true,
  autoRenew: true,
  billingCycle: 'monthly',
  defaultPayment: 1,
  taxId: '',
  vatNumber: ''
})

// Payment form
const paymentForm = reactive({
  type: 'Credit Card',
  cardNumber: '',
  expiry: '',
  cvv: '',
  cardholder: '',
  address: '',
  setDefault: false
})

// Mock data
const paymentMethods = ref([
  {
    id: 1,
    type: 'Credit Card',
    cardNumber: '4242424242424242',
    expiry: '12/25',
    cardholder: 'John Doe',
    isDefault: true
  },
  {
    id: 2,
    type: 'Debit Card',
    cardNumber: '5555555555554444',
    expiry: '09/24',
    cardholder: 'John Doe',
    isDefault: false
  }
])

const billingHistory = ref([
  {
    id: 1,
    date: '2024-01-01',
    description: 'Professional Plan',
    period: 'Jan 2024',
    amount: 99.00,
    type: 'charge',
    status: 'paid',
    paymentMethod: 'Credit Card ending in 4242'
  },
  {
    id: 2,
    date: '2023-12-01',
    description: 'Professional Plan',
    period: 'Dec 2023',
    amount: 99.00,
    type: 'charge',
    status: 'paid',
    paymentMethod: 'Credit Card ending in 4242'
  },
  {
    id: 3,
    date: '2023-11-15',
    description: 'Storage Upgrade',
    period: 'One-time',
    amount: 20.00,
    type: 'charge',
    status: 'paid',
    paymentMethod: 'Credit Card ending in 4242'
  },
  {
    id: 4,
    date: '2023-11-01',
    description: 'Professional Plan',
    period: 'Nov 2023',
    amount: 99.00,
    type: 'charge',
    status: 'paid',
    paymentMethod: 'Credit Card ending in 4242'
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
    description: 'For large organizations with advanced needs',
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

// Computed properties
const filteredHistory = computed(() => {
  let filtered = billingHistory.value
  
  if (historyFilter.value) {
    const days = parseInt(historyFilter.value)
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000)
    filtered = filtered.filter(transaction => 
      new Date(transaction.date) >= cutoffDate
    )
  }
  
  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
})

// Methods
const loadBillingData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/billing')
    // if (response.success) {
    //   Object.assign(billingInfo, response.billingInfo)
    //   paymentMethods.value = response.paymentMethods || []
    //   billingHistory.value = response.history || []
    //   billingSettings.value = response.settings || billingSettings
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading billing data:', error)
    showError('Failed to load billing data')
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

const getUsageClass = (percentage) => {
  if (percentage >= 90) return 'critical'
  if (percentage >= 75) return 'warning'
  return 'normal'
}

const getPaymentIcon = (type) => {
  const icons = {
    'Credit Card': 'fas fa-credit-card',
    'Debit Card': 'fas fa-credit-card',
    'PayPal': 'fab fa-paypal',
    'Bank Transfer': 'fas fa-university'
  }
  return icons[type] || 'fas fa-credit-card'
}

const maskCardNumber = (cardNumber) => {
  if (!cardNumber) return ''
  return '**** **** **** ' + cardNumber.slice(-4)
}

const selectPlan = (plan) => {
  selectedPlan.value = plan
}

const upgradePlan = async (plan) => {
  if (plan.name === billingInfo.currentPlan) return
  
  const confirmed = await showConfirm(`Are you sure you want to upgrade to ${plan.name} plan?`)
  if (!confirmed) return

  try {
    // const response = await apiPost('/billing/upgrade', { planId: plan.id })
    // if (response.success) {
    //   billingInfo.currentPlan = plan.name
    //   billingInfo.price = plan.price
    //   showSuccess('Plan upgraded successfully')
    //   closeUpgradeModal()
    // }
    
    // For demo, simulate upgrade
    billingInfo.currentPlan = plan.name
    billingInfo.price = plan.price
    showSuccess('Plan upgraded successfully')
    closeUpgradeModal()
  } catch (error) {
    console.error('Error upgrading plan:', error)
    showError('Failed to upgrade plan')
  }
}

const addPaymentMethod = async () => {
  if (!paymentForm.cardNumber || !paymentForm.expiry || !paymentForm.cardholder) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/billing/payment-methods', paymentForm)
    // if (response.success) {
    //   paymentMethods.value.push(response.paymentMethod)
    //   showSuccess('Payment method added successfully')
    //   closePaymentModal()
    // }
    
    // For demo, simulate addition
    const newMethod = {
      id: Date.now(),
      ...paymentForm,
      isDefault: paymentForm.setDefault
    }
    
    if (paymentForm.setDefault) {
      paymentMethods.value.forEach(method => method.isDefault = false)
    }
    
    paymentMethods.value.push(newMethod)
    showSuccess('Payment method added successfully')
    closePaymentModal()
  } catch (error) {
    console.error('Error adding payment method:', error)
    showError('Failed to add payment method')
  }
}

const setDefaultPayment = async (method) => {
  try {
    // const response = await apiPut(`/billing/payment-methods/${method.id}/default`)
    // if (response.success) {
    //   paymentMethods.value.forEach(m => m.isDefault = false)
    //   method.isDefault = true
    //   showSuccess('Default payment method updated')
    // }
    
    // For demo, simulate update
    paymentMethods.value.forEach(m => m.isDefault = false)
    method.isDefault = true
    showSuccess('Default payment method updated')
  } catch (error) {
    console.error('Error setting default payment:', error)
    showError('Failed to update default payment method')
  }
}

const editPaymentMethod = (method) => {
  showSuccess(`Editing payment method: ${method.type}`)
}

const deletePaymentMethod = async (method) => {
  if (method.isDefault) {
    showError('Cannot delete default payment method')
    return
  }

  const confirmed = await showConfirm('Are you sure you want to delete this payment method?')
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/billing/payment-methods/${method.id}`)
    // if (response.success) {
    //   const index = paymentMethods.value.findIndex(m => m.id === method.id)
    //   if (index > -1) {
    //     paymentMethods.value.splice(index, 1)
    //     showSuccess('Payment method deleted successfully')
    //   }
    // }
    
    // For demo, simulate deletion
    const index = paymentMethods.value.findIndex(m => m.id === method.id)
    if (index > -1) {
      paymentMethods.value.splice(index, 1)
      showSuccess('Payment method deleted successfully')
    }
  } catch (error) {
    console.error('Error deleting payment method:', error)
    showError('Failed to delete payment method')
  }
}

const saveBillingSettings = async () => {
  try {
    // const response = await apiPut('/billing/settings', billingSettings)
    // if (response.success) {
    //   showSuccess('Billing settings saved successfully')
    //   closeSettingsModal()
    // }
    
    // For demo, simulate save
    showSuccess('Billing settings saved successfully')
    closeSettingsModal()
  } catch (error) {
    console.error('Error saving settings:', error)
    showError('Failed to save billing settings')
  }
}

const exportBillingHistory = async () => {
  try {
    // const response = await apiPost('/billing/export')
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `billing-history-${new Date().toISOString().split('T')[0]}.csv`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Billing history exported successfully')
    // }
    
    // For demo, simulate export
    showSuccess('Billing history exported successfully')
  } catch (error) {
    console.error('Error exporting billing history:', error)
    showError('Failed to export billing history')
  }
}

const viewInvoice = (transaction) => {
  showSuccess(`Viewing invoice for ${transaction.description}`)
}

// Modal close methods
const closeUpgradeModal = () => {
  showUpgradeModal.value = false
  selectedPlan.value = null
}

const closePaymentModal = () => {
  showPaymentModal.value = false
  resetPaymentForm()
}

const closeSettingsModal = () => {
  showSettingsModal.value = false
}

const resetPaymentForm = () => {
  Object.assign(paymentForm, {
    type: 'Credit Card',
    cardNumber: '',
    expiry: '',
    cvv: '',
    cardholder: '',
    address: '',
    setDefault: false
  })
}

// Lifecycle
onMounted(() => {
  loadBillingData()
})
</script>

<style scoped>
.billing {
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

.card-icon.amount {
  background: var(--success-color);
}

.card-icon.usage {
  background: var(--warning-color);
}

.card-icon.next {
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

.plan-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  text-transform: capitalize;
}

.plan-status.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.plan-status.inactive {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.due-date,
.billing-cycle {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.usage-bar {
  width: 100%;
  height: 6px;
  background: var(--glass-bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.usage-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
  border-radius: 3px;
  transition: width 0.3s ease;
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
.payment-btn,
.invoice-btn,
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
.payment-btn:hover,
.invoice-btn:hover,
.settings-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.payment-btn {
  background: var(--success-color);
}

.payment-btn:hover {
  background: var(--success-hover);
}

.invoice-btn {
  background: var(--info-color);
}

.invoice-btn:hover {
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
.payment-section,
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
.add-payment-btn {
  padding: 0.75rem 1.25rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.change-plan-btn:hover,
.add-payment-btn:hover {
  background: var(--primary-hover);
}

.plan-card {
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

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-item.disabled {
  opacity: 0.5;
}

.feature-item i {
  width: 20px;
  color: var(--success-color);
}

.feature-item.disabled i {
  color: var(--danger-color);
}

.feature-item span {
  flex: 1;
  color: var(--text-primary);
}

.feature-limit {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.plan-usage h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.usage-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.usage-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.usage-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.usage-name {
  font-weight: 600;
  color: var(--text-primary);
}

.usage-amount {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.usage-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.usage-bar {
  flex: 1;
  height: 8px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.usage-bar.normal .usage-fill {
  background: var(--success-color);
}

.usage-bar.warning .usage-fill {
  background: var(--warning-color);
}

.usage-bar.critical .usage-fill {
  background: var(--danger-color);
}

.usage-percentage {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 40px;
}

.payment-methods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.payment-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
  transition: all 0.3s ease;
}

.payment-card.default {
  border-color: var(--primary-color);
}

.payment-card:hover {
  transform: translateY(-2px);
}

.payment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.payment-type {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.payment-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  background: var(--glass-bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.default:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.edit:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.payment-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-number {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: var(--text-primary);
}

.card-expiry {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.card-holder {
  color: var(--text-secondary);
}

.default-badge {
  position: absolute;
  top: -10px;
  right: 20px;
  background: var(--primary-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
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

.transaction-row {
  transition: background 0.3s ease;
}

.transaction-row:hover {
  background: var(--glass-bg-hover);
}

.transaction-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.transaction-desc {
  font-weight: 600;
  color: var(--text-primary);
}

.transaction-period {
  font-size: 0.8rem;
  color: var(--text-secondary);
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

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.paid {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.invoice-btn-small {
  width: 32px;
  height: 32px;
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  background: var(--glass-bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.invoice-btn-small:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
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

.payment-form,
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

.form-group input,
.form-group select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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

.btn-secondary {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
}

@media (max-width: 768px) {
  .billing {
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
  
  .payment-methods-grid {
    grid-template-columns: 1fr;
  }
  
  .plans-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
