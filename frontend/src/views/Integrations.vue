<template>
  <div class="integrations">
    <div class="page-header">
      <h1>Integrations</h1>
      <p>Connect your favorite tools and services</p>
    </div>

    <!-- Search and Filter -->
    <div class="search-section">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search integrations..."
          @input="filterIntegrations"
        />
      </div>
      <div class="filter-controls">
        <div class="filter-dropdown">
          <select v-model="categoryFilter" @change="filterIntegrations">
            <option value="">All Categories</option>
            <option value="analytics">Analytics</option>
            <option value="communication">Communication</option>
            <option value="payment">Payment</option>
            <option value="social">Social Media</option>
            <option value="storage">Storage</option>
            <option value="automation">Automation</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="statusFilter" @change="filterIntegrations">
            <option value="">All Status</option>
            <option value="connected">Connected</option>
            <option value="disconnected">Disconnected</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Integration Categories -->
    <div class="categories-section">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading integrations...</p>
      </div>

      <div v-else-if="filteredIntegrations.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-plug"></i>
        </div>
        <h3>No integrations found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="integrations-grid">
        <div 
          v-for="integration in filteredIntegrations" 
          :key="integration.id"
          class="integration-card"
          :class="{ 'connected': integration.status === 'connected', 'error': integration.status === 'error' }"
        >
          <div class="integration-header">
            <div class="integration-logo">
              <img :src="integration.logo" :alt="integration.name" />
              <div class="status-indicator" :class="integration.status">
                <i v-if="integration.status === 'connected'" class="fas fa-check"></i>
                <i v-else-if="integration.status === 'error'" class="fas fa-exclamation-triangle"></i>
                <i v-else class="fas fa-circle"></i>
              </div>
            </div>
            <div class="integration-info">
              <h3>{{ integration.name }}</h3>
              <p>{{ integration.description }}</p>
              <span class="category-badge">{{ integration.category }}</span>
            </div>
          </div>

          <div class="integration-body">
            <div class="features-list">
              <div 
                v-for="feature in integration.features" 
                :key="feature"
                class="feature-item"
              >
                <i :class="feature.icon"></i>
                <span>{{ feature.name }}</span>
              </div>
            </div>

            <div class="integration-actions">
              <button 
                v-if="integration.status === 'disconnected'"
                class="action-btn connect"
                @click="connectIntegration(integration)"
              >
                <i class="fas fa-link"></i>
                Connect
              </button>
              <button 
                v-else-if="integration.status === 'connected'"
                class="action-btn configure"
                @click="configureIntegration(integration)"
              >
                <i class="fas fa-cog"></i>
                Configure
              </button>
              <button 
                v-else-if="integration.status === 'error'"
                class="action-btn reconnect"
                @click="reconnectIntegration(integration)"
              >
                <i class="fas fa-sync"></i>
                Reconnect
              </button>
              <button 
                class="action-btn disconnect"
                @click="disconnectIntegration(integration)"
                :disabled="integration.status === 'disconnected'"
              >
                <i class="fas fa-unlink"></i>
                Disconnect
              </button>
            </div>
          </div>

          <div class="integration-footer">
            <div class="stats">
              <span class="stat-item">
                <i class="fas fa-calendar"></i>
                {{ formatDate(integration.connected_at) }}
              </span>
              <span class="stat-item">
                <i class="fas fa-chart-line"></i>
                {{ integration.usage_count || 0 }} uses
              </span>
            </div>
            <div class="documentation-link">
              <a 
                :href="integration.documentation" 
                target="_blank"
                class="doc-link"
              >
                <i class="fas fa-book"></i>
                Documentation
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Integration Configuration Modal -->
    <div v-if="showConfigModal" class="modal-overlay" @click="closeConfigModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Configure {{ selectedIntegration?.name }}</h2>
          <button class="close-btn" @click="closeConfigModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="config-tabs">
            <button 
              v-for="tab in configTabs" 
              :key="tab.id"
              :class="['tab-btn', { active: activeTab === tab.id }]"
              @click="activeTab = tab.id"
            >
              <i :class="tab.icon"></i>
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content">
            <!-- General Configuration -->
            <div v-if="activeTab === 'general'" class="config-section">
              <h3>General Settings</h3>
              <div class="form-group">
                <label>Display Name</label>
                <input 
                  v-model="configForm.displayName" 
                  type="text" 
                  placeholder="Custom name for this integration"
                />
              </div>
              <div class="form-group">
                <label>Sync Frequency</label>
                <select v-model="configForm.syncFrequency">
                  <option value="realtime">Real-time</option>
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>
              <div class="form-group">
                <label>Enable Notifications</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="configForm.notifications"
                  />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <!-- API Configuration -->
            <div v-if="activeTab === 'api'" class="config-section">
              <h3>API Configuration</h3>
              <div class="form-group">
                <label>API Key</label>
                <div class="api-key-input">
                  <input 
                    v-model="configForm.apiKey" 
                    :type="showApiKey ? 'text' : 'password'"
                    placeholder="Enter your API key"
                  />
                  <button 
                    class="toggle-btn"
                    @click="showApiKey = !showApiKey"
                  >
                    <i :class="showApiKey ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </div>
              </div>
              <div class="form-group">
                <label>Webhook URL</label>
                <input 
                  v-model="configForm.webhookUrl" 
                  type="url" 
                  placeholder="https://yourapp.com/webhook"
                />
              </div>
              <div class="form-group">
                <label>Environment</label>
                <select v-model="configForm.environment">
                  <option value="production">Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                </select>
              </div>
            </div>

            <!-- Advanced Configuration -->
            <div v-if="activeTab === 'advanced'" class="config-section">
              <h3>Advanced Settings</h3>
              <div class="form-group">
                <label>Timeout (seconds)</label>
                <input 
                  v-model.number="configForm.timeout" 
                  type="number" 
                  min="1"
                  placeholder="30"
                />
              </div>
              <div class="form-group">
                <label>Retry Attempts</label>
                <input 
                  v-model.number="configForm.retryAttempts" 
                  type="number" 
                  min="1"
                  max="10"
                  placeholder="3"
                />
              </div>
              <div class="form-group">
                <label>Custom Headers</label>
                <textarea 
                  v-model="configForm.customHeaders" 
                  placeholder='{"Authorization": "Bearer token"}'
                  rows="3"
                ></textarea>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeConfigModal">Cancel</button>
          <button 
            class="btn-primary" 
            @click="saveConfiguration"
            :disabled="saving"
          >
            {{ saving ? 'Saving...' : 'Save Configuration' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Integration Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedIntegration?.name }} Details</h2>
          <button class="close-btn" @click="closeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="details-grid">
            <div class="detail-section">
              <h3>Information</h3>
              <div class="detail-item">
                <label>Status:</label>
                <span :class="['status-badge', selectedIntegration?.status]">{{ selectedIntegration?.status }}</span>
              </div>
              <div class="detail-item">
                <label>Category:</label>
                <span>{{ selectedIntegration?.category }}</span>
              </div>
              <div class="detail-item">
                <label>Version:</label>
                <span>{{ selectedIntegration?.version }}</span>
              </div>
              <div class="detail-item">
                <label>Connected:</label>
                <span>{{ formatDateTime(selectedIntegration?.connected_at) }}</span>
              </div>
            </div>

            <div class="detail-section">
              <h3>Usage Statistics</h3>
              <div class="usage-stats">
                <div class="stat-item">
                  <label>Total Requests:</label>
                  <span>{{ selectedIntegration?.stats?.totalRequests || 0 }}</span>
                </div>
                <div class="stat-item">
                  <label>Success Rate:</label>
                  <span>{{ selectedIntegration?.stats?.successRate || 0 }}%</span>
                </div>
                <div class="stat-item">
                  <label>Avg Response Time:</label>
                  <span>{{ selectedIntegration?.stats?.avgResponseTime || 0 }}ms</span>
                </div>
                <div class="stat-item">
                  <label>Last Sync:</label>
                  <span>{{ formatDateTime(selectedIntegration?.stats?.lastSync) }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Recent Activity</h3>
              <div class="activity-log">
                <div 
                  v-for="activity in selectedIntegration?.recentActivity" 
                  :key="activity.id"
                  class="activity-item"
                >
                  <div class="activity-icon">
                    <i :class="getActivityIcon(activity.type)"></i>
                  </div>
                  <div class="activity-content">
                    <div class="activity-header">
                      <span class="activity-title">{{ activity.title }}</span>
                      <span class="activity-time">{{ formatDateTime(activity.timestamp) }}</span>
                    </div>
                    <p>{{ activity.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
const saving = ref(false)
const integrations = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const selectedIntegration = ref(null)
const showApiKey = ref(false)

// Modal states
const showConfigModal = ref(false)
const showDetailsModal = ref(false)
const activeTab = ref('general')

const configForm = reactive({
  displayName: '',
  syncFrequency: 'realtime',
  notifications: true,
  api_key: '',
  webhookUrl: '',
  environment: 'production',
  timeout: 30,
  retryAttempts: 3,
  customHeaders: ''
})

const configTabs = [
  { id: 'general', label: 'General', icon: 'fas fa-cog' },
  { id: 'api', label: 'API', icon: 'fas fa-key' },
  { id: 'advanced', label: 'Advanced', icon: 'fas fa-sliders-h' }
]

// Mock integrations data (in real app, this would come from API)
const mockIntegrations = [
  {
    id: 1,
    name: 'Google Analytics',
    description: 'Track website traffic and user behavior',
    category: 'Analytics',
    logo: 'https://via.placeholder.com/100x100?text=GA',
    status: 'connected',
    connected_at: '2024-01-15T10:30:00Z',
    usage_count: 1247,
    features: [
      { name: 'Traffic Analysis', icon: 'fas fa-chart-line' },
      { name: 'User Tracking', icon: 'fas fa-users' },
      { name: 'Real-time Reports', icon: 'fas fa-tachometer-alt' }
    ],
    documentation: 'https://developers.google.com/analytics'
  },
  {
    id: 2,
    name: 'Slack',
    description: 'Team communication and collaboration',
    category: 'Communication',
    logo: 'https://via.placeholder.com/100x100?text=Slack',
    status: 'connected',
    connected_at: '2024-01-10T14:20:00Z',
    usage_count: 3421,
    features: [
      { name: 'Message Channels', icon: 'fas fa-comments' },
      { name: 'File Sharing', icon: 'fas fa-share' },
      { name: 'Notifications', icon: 'fas fa-bell' }
    ],
    documentation: 'https://api.slack.com'
  },
  {
    id: 3,
    name: 'Stripe',
    description: 'Payment processing and billing',
    category: 'Payment',
    logo: 'https://via.placeholder.com/100x100?text=Stripe',
    status: 'error',
    connected_at: '2024-01-05T09:15:00Z',
    usage_count: 892,
    features: [
      { name: 'Payment Processing', icon: 'fas fa-credit-card' },
      { name: 'Subscription Management', icon: 'fas fa-sync' },
      { name: 'Webhook Support', icon: 'fas fa-link' }
    ],
    documentation: 'https://stripe.com/docs'
  },
  {
    id: 4,
    name: 'Twitter',
    description: 'Social media integration',
    category: 'Social Media',
    logo: 'https://via.placeholder.com/100x100?text=Twitter',
    status: 'disconnected',
    connected_at: null,
    usage_count: 0,
    features: [
      { name: 'Tweet Posting', icon: 'fas fa-twitter' },
      { name: 'Analytics', icon: 'fas fa-chart-bar' },
      { name: 'Direct Messages', icon: 'fas fa-envelope' }
    ],
    documentation: 'https://developer.twitter.com'
  },
  {
    id: 5,
    name: 'AWS S3',
    description: 'Cloud storage and file management',
    category: 'Storage',
    logo: 'https://via.placeholder.com/100x100?text=AWS',
    status: 'connected',
    connected_at: '2024-01-20T16:45:00Z',
    usage_count: 567,
    features: [
      { name: 'File Storage', icon: 'fas fa-database' },
      { name: 'CDN', icon: 'fas fa-globe' },
      { name: 'Backup', icon: 'fas fa-save' }
    ],
    documentation: 'https://docs.aws.amazon.com/s3'
  },
  {
    id: 6,
    name: 'Zapier',
    description: 'Automation and workflow integration',
    category: 'Automation',
    logo: 'https://via.placeholder.com/100x100?text=Zapier',
    status: 'connected',
    connected_at: '2024-01-12T11:30:00Z',
    usage_count: 2103,
    features: [
      { name: 'Workflow Automation', icon: 'fas fa-project-diagram' },
      { name: 'Multi-app Integration', icon: 'fas fa-plug' },
      { name: 'Custom Triggers', icon: 'fas fa-bolt' }
    ],
    documentation: 'https://zapier.com/docs'
  }
]

// Computed properties
const filteredIntegrations = computed(() => {
  let filtered = integrations.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(integration => 
      integration.name.toLowerCase().includes(query) ||
      integration.description.toLowerCase().includes(query)
    )
  }

  // Apply category filter
  if (categoryFilter.value) {
    filtered = filtered.filter(integration => integration.category === categoryFilter.value)
  }

  // Apply status filter
  if (statusFilter.value) {
    filtered = filtered.filter(integration => integration.status === statusFilter.value)
  }

  return filtered
})

// Methods
const loadIntegrations = async () => {
  loading.value = true
  try {
    // In real app, this would be an API call
    // const response = await apiGet('/integrations')
    // if (response.success) {
    //   integrations.value = response.integrations || []
    // }
    
    // For demo, use mock data
    integrations.value = mockIntegrations
  } catch (error) {
    console.error('Error loading integrations:', error)
    showError('Failed to load integrations')
  } finally {
    loading.value = false
  }
}

const filterIntegrations = () => {
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

const getEmptyMessage = () => {
  if (searchQuery.value || categoryFilter.value || statusFilter.value) {
    return 'No integrations match your search criteria'
  }
  return 'No integrations available'
}

const getActivityIcon = (type) => {
  const icons = {
    'connect': 'fas fa-link',
    'disconnect': 'fas fa-unlink',
    'error': 'fas fa-exclamation-triangle',
    'sync': 'fas fa-sync',
    'config': 'fas fa-cog'
  }
  return icons[type] || 'fas fa-circle'
}

const connectIntegration = async (integration) => {
  try {
    // const response = await apiPost(`/integrations/${integration.id}/connect`)
    // if (response.success) {
    //   integration.status = 'connected'
    //   showSuccess('Integration connected successfully')
    // }
    
    // For demo, simulate connection
    integration.status = 'connected'
    integration.connected_at = new Date().toISOString()
    showSuccess(`${integration.name} connected successfully`)
  } catch (error) {
    console.error('Error connecting integration:', error)
    showError('Failed to connect integration')
  }
}

const configureIntegration = (integration) => {
  selectedIntegration.value = integration
  showConfigModal.value = true
  // Reset form with current config
  Object.assign(configForm, {
    displayName: integration.displayName || integration.name,
    syncFrequency: 'realtime',
    notifications: true,
    api_key: '',
    webhookUrl: '',
    environment: 'production',
    timeout: 30,
    retryAttempts: 3,
    customHeaders: ''
  })
}

const disconnectIntegration = async (integration) => {
  const confirmed = await showConfirm(`Are you sure you want to disconnect ${integration.name}?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/integrations/${integration.id}/disconnect`)
    // if (response.success) {
    //   integration.status = 'disconnected'
    //   showSuccess('Integration disconnected successfully')
    // }
    
    // For demo, simulate disconnection
    integration.status = 'disconnected'
    showSuccess(`${integration.name} disconnected successfully`)
  } catch (error) {
    console.error('Error disconnecting integration:', error)
    showError('Failed to disconnect integration')
  }
}

const reconnectIntegration = async (integration) => {
  try {
    // const response = await apiPost(`/integrations/${integration.id}/reconnect`)
    // if (response.success) {
    //   integration.status = 'connected'
    //   showSuccess('Integration reconnected successfully')
    // }
    
    // For demo, simulate reconnection
    integration.status = 'connected'
    showSuccess(`${integration.name} reconnected successfully`)
  } catch (error) {
    console.error('Error reconnecting integration:', error)
    showError('Failed to reconnect integration')
  }
}

const saveConfiguration = async () => {
  if (!selectedIntegration.value) return

  saving.value = true
  try {
    // const response = await apiPut(`/integrations/${selectedIntegration.value.id}/config`, configForm)
    // if (response.success) {
    //   showSuccess('Configuration saved successfully')
    //   closeConfigModal()
    // }
    
    // For demo, simulate save
    showSuccess('Configuration saved successfully')
    closeConfigModal()
  } catch (error) {
    console.error('Error saving configuration:', error)
    showError('Failed to save configuration')
  } finally {
    saving.value = false
  }
}

const closeConfigModal = () => {
  showConfigModal.value = false
  selectedIntegration.value = null
  activeTab.value = 'general'
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedIntegration.value = null
}

// Lifecycle
onMounted(() => {
  loadIntegrations()
})
</script>

<style scoped>
.integrations {
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

.search-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 3rem;
  padding: 2rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  align-items: center;
}

.search-box {
  position: relative;
  flex: 1;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  font-size: 1.1rem;
}

.search-box input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
}

.filter-controls {
  display: flex;
  gap: 1rem;
}

.filter-dropdown select {
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
  cursor: pointer;
  min-width: 150px;
}

.categories-section {
  margin-bottom: 3rem;
}

.loading-state, .empty-state {
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

.integrations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.integration-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.integration-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.integration-card.connected {
  border-left: 4px solid var(--success-color);
}

.integration-card.error {
  border-left: 4px solid var(--danger-color);
}

.integration-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.integration-logo {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  overflow: hidden;
  background: var(--glass-bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.integration-logo img {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.status-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  color: white;
}

.status-indicator.connected {
  background: var(--success-color);
}

.status-indicator.error {
  background: var(--danger-color);
}

.status-indicator:not(.connected):not(.error) {
  background: var(--text-tertiary);
}

.integration-info {
  flex: 1;
  margin-left: 1rem;
}

.integration-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.integration-info p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.category-badge {
  padding: 0.25rem 0.75rem;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.integration-body {
  margin-bottom: 1rem;
}

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--glass-bg-primary);
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.feature-item i {
  color: var(--primary-color);
}

.integration-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.625rem 1.25rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.action-btn:hover:not(:disabled) {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.connect {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.connect:hover {
  background: var(--success-hover);
}

.action-btn.configure {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.configure:hover {
  background: var(--primary-hover);
}

.action-btn.reconnect {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.reconnect:hover {
  background: var(--warning-hover);
}

.action-btn.disconnect {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.action-btn.disconnect:hover {
  background: var(--danger-hover);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.integration-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

.stats {
  display: flex;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.stat-item i {
  color: var(--primary-color);
}

.documentation-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.3s ease;
}

.documentation-link:hover {
  color: var(--primary-hover);
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

.config-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--glass-border);
  padding-bottom: 1rem;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px 8px 0 0;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.tab-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.tab-content {
  padding-top: 2rem;
}

.config-section {
  margin-bottom: 2rem;
}

.config-section h3 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
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

.api-key-input {
  display: flex;
  gap: 0.5rem;
}

.api-key-input input {
  flex: 1;
}

.toggle-btn {
  padding: 0.5rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
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

.btn-primary:hover:not(:disabled) {
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

/* Details Modal Styles */
.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.detail-section {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.detail-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-secondary);
}

.usage-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 6px;
}

.stat-item label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat-item span {
  font-weight: 700;
  color: var(--text-primary);
}

.activity-log {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.activity-title {
  font-weight: 600;
  color: var(--text-primary);
}

.activity-time {
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

.activity-content p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .integrations {
    padding: 1rem;
  }
  
  .search-section {
    flex-direction: column;
    gap: 1rem;
  }
  
  .filter-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .integrations-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .config-tabs {
    flex-wrap: wrap;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .usage-stats {
    grid-template-columns: 1fr;
  }
}
</style>
