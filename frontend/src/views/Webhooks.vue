<template>
  <div class="webhooks">
    <div class="page-header">
      <h1>Webhooks</h1>
      <p>Manage webhook endpoints and configurations</p>
    </div>

    <!-- Webhook Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-link"></i>
          </div>
          <div class="card-content">
            <h3>{{ webhookStats.totalWebhooks }}</h3>
            <p>Total Webhooks</p>
            <span class="webhook-count">{{ webhookStats.activeWebhooks }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon requests">
            <i class="fas fa-exchange-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ webhookStats.totalRequests }}</h3>
            <p>Total Requests</p>
            <span class="request-count">{{ webhookStats.todayRequests }} today</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon success">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ webhookStats.successRate }}%</h3>
            <p>Success Rate</p>
            <span class="success-status" :class="getSuccessClass(webhookStats.successRate)">
              {{ getSuccessStatus(webhookStats.successRate) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon latency">
            <i class="fas fa-tachometer-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ webhookStats.avgLatency }}ms</h3>
            <p>Avg Latency</p>
            <span class="latency-status">{{ webhookStats.lastLatency }}ms last</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="create-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Webhook
        </button>
        <button class="test-btn" @click="showTestModal = true">
          <i class="fas fa-play"></i>
          Test Webhook
        </button>
        <button class="logs-btn" @click="showLogsModal = true">
          <i class="fas fa-history"></i>
          View Logs
        </button>
      </div>
    </div>

    <!-- Webhooks Grid -->
    <div class="webhooks-section">
      <div class="section-header">
        <h2>My Webhooks</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterWebhooks">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div class="view-toggle">
            <button 
              :class="['view-btn', { active: viewMode === 'grid' }]"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'list' }]"
              @click="viewMode = 'list'"
            >
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading webhooks...</p>
      </div>

      <div v-else-if="filteredWebhooks.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-link"></i>
        </div>
        <h3>No webhooks found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Webhook
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="webhooks-grid">
          <div 
            v-for="webhook in filteredWebhooks" 
            :key="webhook.id"
            class="webhook-card"
            :class="{ 'inactive': webhook.status === 'inactive', 'error': webhook.status === 'error' }"
          >
            <div class="webhook-header">
              <div class="webhook-icon">
                <i class="fas fa-link"></i>
              </div>
              <div class="webhook-status">
                <span :class="['status-badge', webhook.status]">{{ webhook.status }}</span>
              </div>
            </div>

            <div class="webhook-content">
              <h3>{{ webhook.name }}</h3>
              <p>{{ webhook.description }}</p>
              
              <div class="webhook-url">
                <code>{{ webhook.url }}</code>
                <button class="copy-btn" @click="copyUrl(webhook.url)">
                  <i class="fas fa-copy"></i>
                </button>
              </div>

              <div class="webhook-meta">
                <span class="method">{{ webhook.method }}</span>
                <span class="requests">{{ webhook.requests }} requests</span>
                <span class="success-rate">{{ webhook.successRate }}% success</span>
              </div>

              <div class="webhook-actions">
                <button class="action-btn test" @click="testWebhook(webhook)">
                  <i class="fas fa-play"></i>
                  Test
                </button>
                <button class="action-btn edit" @click="editWebhook(webhook)">
                  <i class="fas fa-edit"></i>
                  Edit
                </button>
                <button 
                  class="action-btn toggle"
                  @click="toggleWebhook(webhook)"
                  :class="webhook.status === 'active' ? 'pause' : 'resume'"
                >
                  <i :class="webhook.status === 'active' ? 'fas fa-pause' : 'fas fa-play'"></i>
                  {{ webhook.status === 'active' ? 'Pause' : 'Resume' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="webhooks-list">
          <div 
            v-for="webhook in filteredWebhooks" 
            :key="webhook.id"
            class="webhook-list-card"
            :class="{ 'inactive': webhook.status === 'inactive', 'error': webhook.status === 'error' }"
          >
            <div class="webhook-list-header">
              <div class="webhook-list-info">
                <div class="webhook-icon">
                  <i class="fas fa-link"></i>
                </div>
                <div class="webhook-details">
                  <h3>{{ webhook.name }}</h3>
                  <p>{{ webhook.description }}</p>
                  <div class="webhook-url">
                    <code>{{ webhook.url }}</code>
                    <button class="copy-btn" @click="copyUrl(webhook.url)">
                      <i class="fas fa-copy"></i>
                    </button>
                  </div>
                  <div class="webhook-meta">
                    <span class="method">{{ webhook.method }}</span>
                    <span :class="['status-badge', webhook.status]">{{ webhook.status }}</span>
                    <span class="requests">{{ webhook.requests }} requests</span>
                    <span class="success-rate">{{ webhook.successRate }}% success</span>
                  </div>
                </div>
              </div>
              <div class="webhook-list-actions">
                <button class="action-btn test" @click="testWebhook(webhook)">
                  <i class="fas fa-play"></i>
                </button>
                <button class="action-btn edit" @click="editWebhook(webhook)">
                  <i class="fas fa-edit"></i>
                </button>
                <button 
                  class="action-btn toggle"
                  @click="toggleWebhook(webhook)"
                  :class="webhook.status === 'active' ? 'pause' : 'resume'"
                >
                  <i :class="webhook.status === 'active' ? 'fas fa-pause' : 'fas fa-play'"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Webhook Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Create Webhook</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="webhook-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Webhook Name *</label>
                <input 
                  v-model="webhookForm.name" 
                  type="text" 
                  placeholder="Enter webhook name"
                  required
                />
              </div>
              <div class="form-group">
                <label>HTTP Method *</label>
                <select v-model="webhookForm.method" required>
                  <option value="POST">POST</option>
                  <option value="GET">GET</option>
                  <option value="PUT">PUT</option>
                  <option value="PATCH">PATCH</option>
                  <option value="DELETE">DELETE</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Endpoint URL *</label>
              <input 
                v-model="webhookForm.url" 
                type="url" 
                placeholder="https://example.com/webhook"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="webhookForm.description" 
                placeholder="Describe what this webhook does"
                rows="3"
              ></textarea>
            </div>

            <div class="form-section">
              <h4>Headers</h4>
              <div class="headers-container">
                <div 
                  v-for="(header, index) in webhookForm.headers" 
                  :key="index"
                  class="header-item"
                >
                  <input 
                    v-model="header.key" 
                    type="text" 
                    placeholder="Header name"
                  />
                  <input 
                    v-model="header.value" 
                    type="text" 
                    placeholder="Header value"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeHeader(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-header-btn" @click="addHeader">
                  <i class="fas fa-plus"></i>
                  Add Header
                </button>
              </div>
            </div>

            <div class="form-section">
              <h4>Security</h4>
              <div class="security-options">
                <div class="form-group">
                  <label>Secret Key</label>
                  <input 
                    v-model="webhookForm.secret" 
                    type="password" 
                    placeholder="Optional secret for HMAC signature"
                  />
                </div>
                <div class="form-group">
                  <label>IP Whitelist</label>
                  <input 
                    v-model="webhookForm.ipWhitelist" 
                    type="text" 
                    placeholder="Comma-separated IP addresses"
                  />
                </div>
                <div class="form-group">
                  <label>
                    <input 
                      type="checkbox" 
                      v-model="webhookForm.sslRequired"
                    />
                    Require SSL
                  </label>
                </div>
              </div>
            </div>

            <div class="form-section">
              <h4>Retry Settings</h4>
              <div class="retry-options">
                <div class="form-group">
                  <label>Retry Attempts</label>
                  <input 
                    v-model.number="webhookForm.retryAttempts" 
                    type="number" 
                    min="0"
                    max="10"
                  />
                </div>
                <div class="form-group">
                  <label>Retry Delay (seconds)</label>
                  <input 
                    v-model.number="webhookForm.retryDelay" 
                    type="number" 
                    min="1"
                  />
                </div>
                <div class="form-group">
                  <label>Timeout (seconds)</label>
                  <input 
                    v-model.number="webhookForm.timeout" 
                    type="number" 
                    min="1"
                    max="300"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button class="btn-primary" @click="createWebhook">Create Webhook</button>
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
const statusFilter = ref('')
const viewMode = ref('grid')
const showCreateModal = ref(false)
const showTestModal = ref(false)
const showLogsModal = ref(false)

// Webhook stats
const webhookStats = reactive({
  totalWebhooks: 6,
  activeWebhooks: 4,
  totalRequests: 1247,
  todayRequests: 89,
  successRate: 94,
  avgLatency: 245,
  lastLatency: 198
})

// Webhook form
const webhookForm = reactive({
  name: '',
  description: '',
  url: '',
  method: 'POST',
  headers: [],
  secret: '',
  ipWhitelist: '',
  sslRequired: true,
  retryAttempts: 3,
  retryDelay: 60,
  timeout: 30
})

// Mock data
const webhooks = ref([
  {
    id: 1,
    name: 'User Created',
    description: 'Triggered when a new user is created',
    url: 'https://api.example.com/webhooks/user-created',
    method: 'POST',
    status: 'active',
    requests: 456,
    successRate: 96,
    lastRequest: '2024-01-21T10:30:00Z'
  },
  {
    id: 2,
    name: 'Order Completed',
    description: 'Triggered when an order is completed',
    url: 'https://api.example.com/webhooks/order-completed',
    method: 'POST',
    status: 'active',
    requests: 234,
    successRate: 94,
    lastRequest: '2024-01-21T14:15:00Z'
  },
  {
    id: 3,
    name: 'Payment Failed',
    description: 'Triggered when a payment fails',
    url: 'https://api.example.com/webhooks/payment-failed',
    method: 'POST',
    status: 'inactive',
    requests: 89,
    successRate: 92,
    lastRequest: '2024-01-20T09:45:00Z'
  },
  {
    id: 4,
    name: 'File Uploaded',
    description: 'Triggered when a file is uploaded',
    url: 'https://api.example.com/webhooks/file-uploaded',
    method: 'POST',
    status: 'error',
    requests: 67,
    successRate: 78,
    lastRequest: '2024-01-21T11:20:00Z'
  }
])

// Computed properties
const filteredWebhooks = computed(() => {
  let filtered = webhooks.value

  if (statusFilter.value) {
    filtered = filtered.filter(webhook => webhook.status === statusFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.lastRequest) - new Date(a.lastRequest))
})

// Methods
const loadWebhooks = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/webhooks')
    // if (response.success) {
    //   webhooks.value = response.webhooks || []
    //   Object.assign(webhookStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading webhooks:', error)
    showError('Failed to load webhooks')
  } finally {
    loading.value = false
  }
}

const filterWebhooks = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value) {
    return 'No webhooks match your filter criteria'
  }
  return 'No webhooks found'
}

const getSuccessClass = (rate) => {
  if (rate >= 95) return 'excellent'
  if (rate >= 90) return 'good'
  if (rate >= 80) return 'fair'
  return 'poor'
}

const getSuccessStatus = (rate) => {
  if (rate >= 95) return 'Excellent'
  if (rate >= 90) return 'Good'
  if (rate >= 80) return 'Fair'
  return 'Needs Improvement'
}

const copyUrl = async (url) => {
  try {
    await navigator.clipboard.writeText(url)
    showSuccess('URL copied to clipboard')
  } catch (error) {
    showError('Failed to copy URL')
  }
}

const testWebhook = async (webhook) => {
  try {
    // const response = await apiPost(`/webhooks/${webhook.id}/test`)
    // if (response.success) {
    //   showSuccess('Webhook test sent successfully')
    // }
    
    // For demo, simulate test
    showSuccess('Webhook test sent successfully')
  } catch (error) {
    console.error('Error testing webhook:', error)
    showError('Failed to test webhook')
  }
}

const toggleWebhook = async (webhook) => {
  try {
    // const response = await apiPut(`/webhooks/${webhook.id}/toggle`)
    // if (response.success) {
    //   webhook.status = webhook.status === 'active' ? 'inactive' : 'active'
    //   showSuccess(`Webhook ${webhook.status === 'active' ? 'activated' : 'deactivated'}`)
    // }
    
    // For demo, simulate toggle
    webhook.status = webhook.status === 'active' ? 'inactive' : 'active'
    showSuccess(`Webhook ${webhook.status === 'active' ? 'activated' : 'deactivated'}`)
  } catch (error) {
    console.error('Error toggling webhook:', error)
    showError('Failed to toggle webhook')
  }
}

const editWebhook = (webhook) => {
  // Populate form with webhook data
  Object.assign(webhookForm, {
    name: webhook.name,
    description: webhook.description,
    url: webhook.url,
    method: webhook.method
  })
  
  showCreateModal.value = true
}

const addHeader = () => {
  webhookForm.headers.push({ key: '', value: '' })
}

const removeHeader = (index) => {
  webhookForm.headers.splice(index, 1)
}

const createWebhook = async () => {
  if (!webhookForm.name || !webhookForm.url) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/webhooks', webhookForm)
    // if (response.success) {
    //   webhooks.value.unshift(response.webhook)
    //   showSuccess('Webhook created successfully')
    //   closeCreateModal()
    // }
    
    // For demo, simulate creation
    const newWebhook = {
      id: Date.now(),
      ...webhookForm,
      status: 'active',
      requests: 0,
      successRate: 100,
      lastRequest: new Date().toISOString()
    }
    
    webhooks.value.unshift(newWebhook)
    showSuccess('Webhook created successfully')
    closeCreateModal()
  } catch (error) {
    console.error('Error creating webhook:', error)
    showError('Failed to create webhook')
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetWebhookForm()
}

const resetWebhookForm = () => {
  Object.assign(webhookForm, {
    name: '',
    description: '',
    url: '',
    method: 'POST',
    headers: [],
    secret: '',
    ipWhitelist: '',
    sslRequired: true,
    retryAttempts: 3,
    retryDelay: 60,
    timeout: 30
  })
}

// Lifecycle
onMounted(() => {
  loadWebhooks()
})
</script>

<style scoped>
.webhooks {
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

.card-icon.requests {
  background: var(--success-color);
}

.card-icon.success {
  background: var(--warning-color);
}

.card-icon.latency {
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

.webhook-count,
.request-count,
.success-status,
.latency-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.webhook-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.request-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.success-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.success-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.success-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.success-status.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.latency-status {
  background: rgba(6, 182, 212, 0.1);
  color: #06b6d4;
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

.create-btn,
.test-btn,
.logs-btn {
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

.create-btn:hover,
.test-btn:hover,
.logs-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.test-btn {
  background: var(--success-color);
}

.test-btn:hover {
  background: var(--success-hover);
}

.logs-btn {
  background: var(--info-color);
}

.logs-btn:hover {
  background: var(--info-hover);
}

.webhooks-section {
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

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 3px solid var(--glass-border);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 3rem;
  color: var(--text-tertiary);
  margin-bottom: 1rem;
}

.create-first-btn {
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
  margin-top: 2rem;
}

.create-first-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.webhooks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.webhook-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.webhook-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.webhook-card.inactive {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.webhook-card.error {
  border-color: var(--danger-color);
}

.webhook-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.webhook-icon {
  width: 50px;
  height: 50px;
  background: var(--primary-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
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

.status-badge.inactive {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.webhook-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.webhook-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.webhook-url {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 1rem;
}

.webhook-url code {
  flex: 1;
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  word-break: break-all;
}

.copy-btn {
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

.copy-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.webhook-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.method,
.requests,
.success-rate {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.webhook-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.5rem 1rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.test:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.edit:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.toggle.pause:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.toggle.resume:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.webhooks-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.webhook-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.webhook-list-card:hover {
  background: var(--glass-bg-hover);
}

.webhook-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.webhook-list-info {
  flex: 1;
}

.webhook-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.webhook-details p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
}

.webhook-list-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.webhook-list-actions {
  display: flex;
  gap: 0.5rem;
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
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1000px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
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
  font-size: 1.5rem;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 2rem;
}

.webhook-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
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
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-section {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.form-section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.headers-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.header-item input {
  flex: 1;
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
}

.remove-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--danger-color);
  border-radius: 6px;
  background: var(--danger-color);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: var(--danger-hover);
}

.add-header-btn {
  padding: 0.75rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  align-self: flex-start;
}

.add-header-btn:hover {
  background: var(--primary-hover);
}

.security-options,
.retry-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary {
  padding: 1rem 2rem;
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
  .webhooks {
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
  
  .webhooks-grid {
    grid-template-columns: 1fr;
  }
  
  .webhook-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .security-options,
  .retry-options {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
