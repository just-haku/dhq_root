<template>
  <div class="white-label">
    <div class="page-header">
      <h1>White Label Solutions</h1>
      <p>Customize and brand our platform as your own</p>
    </div>

    <!-- White Label Status -->
    <div class="status-section">
      <div class="section-header">
        <h2>Your White Label Status</h2>
      </div>
      
      <div class="status-card">
        <div class="status-header">
          <div class="whitelabel-info">
            <div class="whitelabel-icon">
              <i class="fas fa-palette"></i>
            </div>
            <div class="whitelabel-details">
              <h3>{{ whiteLabelStatus.level }}</h3>
              <p>{{ whiteLabelStatus.description }}</p>
            </div>
          </div>
          <div class="status-badge">
            <span :class="['badge', whiteLabelStatus.status]">{{ formatStatus(whiteLabelStatus.status) }}</span>
          </div>
        </div>
        
        <div class="status-stats">
          <div class="stat-item">
            <div class="stat-value">{{ whiteLabelStats.activeInstances }}</div>
            <div class="stat-label">Active Instances</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ whiteLabelStats.totalUsers }}</div>
            <div class="stat-label">Total Users</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ whiteLabelStats.customDomains }}</div>
            <div class="stat-label">Custom Domains</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ whiteLabelStats.apiCalls }}</div>
            <div class="stat-label">API Calls/Month</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="section-header">
        <h2>Quick Actions</h2>
      </div>
      
      <div class="actions-grid">
        <div class="action-card" @click="showInstanceModal = true">
          <div class="action-icon">
            <i class="fas fa-plus"></i>
          </div>
          <h3>Create Instance</h3>
          <p>Set up new white label instance</p>
        </div>
        
        <div class="action-card" @click="viewBranding">
          <div class="action-icon branding">
            <i class="fas fa-paint-brush"></i>
          </div>
          <h3>Branding</h3>
          <p>Customize appearance and branding</p>
        </div>
        
        <div class="action-card" @click="viewDomains">
          <div class="action-icon domains">
            <i class="fas fa-globe"></i>
          </div>
          <h3>Domains</h3>
          <p>Manage custom domains</p>
        </div>
        
        <div class="action-card" @click="viewApiKeys">
          <div class="action-icon api">
            <i class="fas fa-key"></i>
          </div>
          <h3>API Keys</h3>
          <p>Manage API access keys</p>
        </div>
      </div>
    </div>

    <!-- White Label Instances -->
    <div class="instances-section">
      <div class="section-header">
        <h2>Your Instances</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="instanceFilter" @change="filterInstances">
              <option value="">All Instances</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="development">Development</option>
              <option value="production">Production</option>
            </select>
          </div>
          <button class="create-btn" @click="showInstanceModal = true">
            <i class="fas fa-plus"></i>
            New Instance
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading instances...</p>
      </div>

      <div v-else-if="filteredInstances.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-server"></i>
        </div>
        <h3>No instances found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showInstanceModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Instance
        </button>
      </div>

      <div v-else class="instances-grid">
        <div 
          v-for="instance in filteredInstances" 
          :key="instance.id"
          class="instance-card"
          :class="{ 'inactive': instance.status === 'inactive' }"
        >
          <div class="instance-header">
            <div class="instance-info">
              <div class="instance-logo">
                <img :src="instance.logo" :alt="instance.name" />
              </div>
              <div class="instance-details">
                <h3>{{ instance.name }}</h3>
                <span :class="['status-badge', instance.status]">{{ formatInstanceStatus(instance.status) }}</span>
              </div>
            </div>
            <div class="instance-meta">
              <span :class="['environment-badge', instance.environment]">{{ instance.environment }}</span>
              <span class="instance-plan">{{ instance.plan }}</span>
            </div>
          </div>
          
          <div class="instance-content">
            <p>{{ instance.description }}</p>
            
            <div class="instance-stats">
              <div class="stat-item">
                <label>Domain:</label>
                <span>{{ instance.domain }}</span>
              </div>
              <div class="stat-item">
                <label>Users:</label>
                <span>{{ instance.users }}</span>
              </div>
              <div class="stat-item">
                <label>Created:</label>
                <span>{{ formatDate(instance.createdAt) }}</span>
              </div>
              <div class="stat-item">
                <label>Last Active:</label>
                <span>{{ formatDate(instance.lastActive) }}</span>
              </div>
            </div>
            
            <div class="instance-features">
              <h4>Enabled Features:</h4>
              <div class="features-list">
                <span 
                  v-for="feature in instance.features" 
                  :key="feature"
                  class="feature-tag"
                >
                  {{ feature }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="instance-footer">
            <div class="instance-actions">
              <button class="action-btn manage" @click="manageInstance(instance)">
                <i class="fas fa-cog"></i>
                Manage
              </button>
              <button class="action-btn analytics" @click="viewInstanceAnalytics(instance)">
                <i class="fas fa-chart-line"></i>
                Analytics
              </button>
              <button class="action-btn edit" @click="editInstance(instance)">
                <i class="fas fa-edit"></i>
              </button>
            </div>
            <div class="instance-health">
              <div class="health-indicator" :class="instance.health">
                <span class="health-dot"></span>
                <span class="health-label">{{ instance.health }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Branding Customization -->
    <div class="branding-section">
      <div class="section-header">
        <h2>Branding Customization</h2>
        <div class="header-actions">
          <button class="preview-btn" @click="previewBranding">
            <i class="fas fa-eye"></i>
            Preview
          </button>
        </div>
      </div>

      <div class="branding-grid">
        <div class="branding-card">
          <div class="branding-header">
            <h3>Logo & Colors</h3>
          </div>
          
          <div class="branding-content">
            <div class="form-group">
              <label>Company Logo</label>
              <div class="logo-upload">
                <input 
                  type="file" 
                  ref="logoInput"
                  @change="handleLogoUpload"
                  accept="image/*"
                />
                <button class="upload-btn" @click="$refs.logoInput.click()">
                  <i class="fas fa-upload"></i>
                  Upload Logo
                </button>
                <div class="uploaded-logo" v-if="brandingForm.logo">
                  <img :src="brandingForm.logo" alt="Company logo" />
                  <button class="remove-logo" @click="removeLogo">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Primary Color</label>
                <div class="color-input">
                  <input 
                    v-model="brandingForm.primaryColor" 
                    type="color" 
                    class="color-picker"
                  />
                  <input 
                    v-model="brandingForm.primaryColor" 
                    type="text" 
                    class="color-text"
                    placeholder="#3B82F6"
                  />
                </div>
              </div>
              
              <div class="form-group">
                <label>Secondary Color</label>
                <div class="color-input">
                  <input 
                    v-model="brandingForm.secondaryColor" 
                    type="color" 
                    class="color-picker"
                  />
                  <input 
                    v-model="brandingForm.secondaryColor" 
                    type="text" 
                    class="color-text"
                    placeholder="#10B981"
                  />
                </div>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Accent Color</label>
                <div class="color-input">
                  <input 
                    v-model="brandingForm.accentColor" 
                    type="color" 
                    class="color-picker"
                  />
                  <input 
                    v-model="brandingForm.accentColor" 
                    type="text" 
                    class="color-text"
                    placeholder="#F59E0B"
                  />
                </div>
              </div>
              
              <div class="form-group">
                <label>Text Color</label>
                <div class="color-input">
                  <input 
                    v-model="brandingForm.textColor" 
                    type="color" 
                    class="color-picker"
                  />
                  <input 
                    v-model="brandingForm.textColor" 
                    type="text" 
                    class="color-text"
                    placeholder="#1F2937"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="branding-card">
          <div class="branding-header">
            <h3>Typography & Layout</h3>
          </div>
          
          <div class="branding-content">
            <div class="form-group">
              <label>Font Family</label>
              <select v-model="brandingForm.fontFamily">
                <option value="Inter">Inter</option>
                <option value="Roboto">Roboto</option>
                <option value="Open Sans">Open Sans</option>
                <option value="Lato">Lato</option>
                <option value="Montserrat">Montserrat</option>
                <option value="Poppins">Poppins</option>
                <option value="Custom">Custom Font</option>
              </select>
            </div>

            <div class="form-group">
              <label>Layout Style</label>
              <select v-model="brandingForm.layoutStyle">
                <option value="modern">Modern</option>
                <option value="classic">Classic</option>
                <option value="minimal">Minimal</option>
                <option value="bold">Bold</option>
              </select>
            </div>

            <div class="form-group">
              <label>Navigation Position</label>
              <select v-model="brandingForm.navigationPosition">
                <option value="top">Top</option>
                <option value="side">Side</option>
                <option value="bottom">Bottom</option>
              </select>
            </div>

            <div class="form-group">
              <label>Button Style</label>
              <select v-model="brandingForm.buttonStyle">
                <option value="rounded">Rounded</option>
                <option value="square">Square</option>
                <option value="pill">Pill</option>
                <option value="outline">Outline</option>
              </select>
            </div>
          </div>
        </div>

        <div class="branding-card">
          <div class="branding-header">
            <h3>Content & Messaging</h3>
          </div>
          
          <div class="branding-content">
            <div class="form-group">
              <label>Company Name</label>
              <input 
                v-model="brandingForm.companyName" 
                type="text" 
                placeholder="Your company name"
              />
            </div>

            <div class="form-group">
              <label>Tagline</label>
              <input 
                v-model="brandingForm.tagline" 
                type="text" 
                placeholder="Your company tagline"
              />
            </div>

            <div class="form-group">
              <label>Welcome Message</label>
              <textarea 
                v-model="brandingForm.welcomeMessage" 
                placeholder="Custom welcome message for users"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Footer Text</label>
              <input 
                v-model="brandingForm.footerText" 
                type="text" 
                placeholder="Custom footer text"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="branding-actions">
        <button class="btn-secondary" @click="resetBranding">
          <i class="fas fa-undo"></i>
          Reset to Default
        </button>
        <button class="btn-primary" @click="saveBranding">
          <i class="fas fa-save"></i>
          Save Branding
        </button>
      </div>
    </div>

    <!-- Domain Management -->
    <div class="domains-section">
      <div class="section-header">
        <h2>Domain Management</h2>
        <div class="header-actions">
          <button class="create-btn" @click="showDomainModal = true">
            <i class="fas fa-plus"></i>
            Add Domain
          </button>
        </div>
      </div>

      <div class="domains-table">
        <div class="table-header">
          <div class="header-cell">Domain</div>
          <div class="header-cell">Instance</div>
          <div class="header-cell">Status</div>
          <div class="header-cell">SSL</div>
          <div class="header-cell">Added</div>
          <div class="header-cell">Actions</div>
        </div>
        
        <div 
          v-for="domain in domains" 
          :key="domain.id"
          class="table-row"
        >
          <div class="table-cell">
            <div class="domain-info">
              <span class="domain-name">{{ domain.name }}</span>
              <span class="domain-url">{{ domain.url }}</span>
            </div>
          </div>
          
          <div class="table-cell">
            <span class="instance-name">{{ domain.instance }}</span>
          </div>
          
          <div class="table-cell">
            <span :class="['status-badge', domain.status]">{{ formatDomainStatus(domain.status) }}</span>
          </div>
          
          <div class="table-cell">
            <span :class="['ssl-badge', domain.ssl]">{{ domain.ssl }}</span>
          </div>
          
          <div class="table-cell">
            <span class="added-date">{{ formatDate(domain.addedDate) }}</span>
          </div>
          
          <div class="table-cell">
            <div class="domain-actions">
              <button class="action-btn verify" @click="verifyDomain(domain)" v-if="domain.status === 'pending'">
                <i class="fas fa-check"></i>
                Verify
              </button>
              <button class="action-btn edit" @click="editDomain(domain)">
                <i class="fas fa-edit"></i>
              </button>
              <button class="action-btn delete" @click="deleteDomain(domain)">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- API Management -->
    <div class="api-section">
      <div class="section-header">
        <h2>API Management</h2>
        <div class="header-actions">
          <button class="create-btn" @click="showApiModal = true">
            <i class="fas fa-plus"></i>
            Generate API Key
          </button>
        </div>
      </div>

      <div class="api-keys-grid">
        <div 
          v-for="apiKey in apiKeys" 
          :key="apiKey.id"
          class="api-key-card"
        >
          <div class="api-key-header">
            <div class="key-info">
              <h3>{{ apiKey.name }}</h3>
              <span :class="['status-badge', apiKey.status]">{{ apiKey.status }}</span>
            </div>
            <div class="key-actions">
              <button class="action-btn copy" @click="copyApiKey(apiKey)">
                <i class="fas fa-copy"></i>
              </button>
              <button class="action-btn delete" @click="deleteApiKey(apiKey)">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          
          <div class="api-key-content">
            <div class="key-details">
              <div class="detail-item">
                <label>API Key:</label>
                <code class="key-value">{{ maskedApiKey(apiKey.key) }}</code>
              </div>
              <div class="detail-item">
                <label>Created:</label>
                <span>{{ formatDate(apiKey.createdAt) }}</span>
              </div>
              <div class="detail-item">
                <label>Last Used:</label>
                <span>{{ formatDate(apiKey.lastUsed) }}</span>
              </div>
              <div class="detail-item">
                <label>Usage:</label>
                <span>{{ apiKey.usage }} calls</span>
              </div>
            </div>
            
            <div class="key-permissions">
              <h4>Permissions:</h4>
              <div class="permissions-list">
                <span 
                  v-for="permission in apiKey.permissions" 
                  :key="permission"
                  class="permission-tag"
                >
                  {{ permission }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Instance Modal -->
    <div v-if="showInstanceModal" class="modal-overlay" @click="closeInstanceModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create New Instance</h2>
          <button class="close-btn" @click="closeInstanceModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="instance-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Instance Name *</label>
                <input 
                  v-model="instanceForm.name" 
                  type="text" 
                  placeholder="Enter instance name"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>Environment *</label>
                <select v-model="instanceForm.environment" required>
                  <option value="">Select environment</option>
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="instanceForm.description" 
                placeholder="Describe the purpose of this instance"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Plan *</label>
                <select v-model="instanceForm.plan" required>
                  <option value="">Select plan</option>
                  <option value="starter">Starter</option>
                  <option value="professional">Professional</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Domain</label>
                <input 
                  v-model="instanceForm.domain" 
                  type="text" 
                  placeholder="your-domain.com"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Enabled Features</label>
              <div class="feature-selection">
                <label class="checkbox-item" v-for="feature in availableFeatures" :key="feature">
                  <input 
                    type="checkbox" 
                    :value="feature"
                    v-model="instanceForm.features"
                  />
                  <span>{{ feature }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeInstanceModal">Cancel</button>
          <button class="btn-primary" @click="createInstance">
            <i class="fas fa-plus"></i>
            Create Instance
          </button>
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
const instanceFilter = ref('')
const showInstanceModal = ref(false)
const showDomainModal = ref(false)
const showApiModal = ref(false)

// White label status
const whiteLabelStatus = reactive({
  level: 'Enterprise White Label',
  description: 'You have full white label capabilities with unlimited customization',
  status: 'active',
  joinedDate: '2023-06-15T00:00:00Z'
})

// White label stats
const whiteLabelStats = reactive({
  activeInstances: 5,
  totalUsers: 1250,
  customDomains: 8,
  apiCalls: 45000
})

// Instance form
const instanceForm = reactive({
  name: '',
  environment: '',
  description: '',
  plan: '',
  domain: '',
  features: []
})

// Branding form
const brandingForm = reactive({
  logo: '',
  primaryColor: '#3B82F6',
  secondaryColor: '#10B981',
  accentColor: '#F59E0B',
  textColor: '#1F2937',
  fontFamily: 'Inter',
  layoutStyle: 'modern',
  navigationPosition: 'top',
  buttonStyle: 'rounded',
  companyName: '',
  tagline: '',
  welcomeMessage: '',
  footerText: ''
})

// Available features
const availableFeatures = [
  'User Management',
  'Analytics Dashboard',
  'API Access',
  'Custom Branding',
  'Email Integration',
  'File Storage',
  'Advanced Security',
  'Multi-language Support'
]

// Instances data
const instances = ref([
  {
    id: 1,
    name: 'Main Platform',
    description: 'Primary white label instance for production use',
    status: 'active',
    environment: 'production',
    plan: 'Enterprise',
    domain: 'platform.example.com',
    logo: '/api/placeholder/60x60',
    users: 850,
    createdAt: '2023-06-15T00:00:00Z',
    lastActive: '2024-01-21T10:30:00Z',
    health: 'excellent',
    features: ['User Management', 'Analytics', 'API', 'Custom Branding']
  },
  {
    id: 2,
    name: 'Development Instance',
    description: 'Development and testing environment',
    status: 'active',
    environment: 'development',
    plan: 'Professional',
    domain: 'dev.platform.example.com',
    logo: '/api/placeholder/60x60',
    users: 45,
    createdAt: '2023-08-20T00:00:00Z',
    lastActive: '2024-01-20T15:45:00Z',
    health: 'good',
    features: ['User Management', 'Analytics', 'API']
  },
  {
    id: 3,
    name: 'Client Portal',
    description: 'White label instance for major client',
    status: 'inactive',
    environment: 'production',
    plan: 'Professional',
    domain: 'client.example.com',
    logo: '/api/placeholder/60x60',
    users: 355,
    createdAt: '2023-10-10T00:00:00Z',
    lastActive: '2024-01-15T09:20:00Z',
    health: 'warning',
    features: ['User Management', 'Analytics', 'Email Integration']
  }
])

// Domains data
const domains = ref([
  {
    id: 1,
    name: 'platform.example.com',
    url: 'https://platform.example.com',
    instance: 'Main Platform',
    status: 'active',
    ssl: 'valid',
    addedDate: '2023-06-15T00:00:00Z'
  },
  {
    id: 2,
    name: 'dev.platform.example.com',
    url: 'https://dev.platform.example.com',
    instance: 'Development Instance',
    status: 'active',
    ssl: 'valid',
    addedDate: '2023-08-20T00:00:00Z'
  },
  {
    id: 3,
    name: 'client.example.com',
    url: 'https://client.example.com',
    instance: 'Client Portal',
    status: 'pending',
    ssl: 'expired',
    addedDate: '2023-10-10T00:00:00Z'
  }
])

// API keys data
const apiKeys = ref([
  {
    id: 1,
    name: 'Production API Key',
    key: 'wl_prod_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz',
    status: 'active',
    permissions: ['read', 'write', 'admin'],
    createdAt: '2023-06-15T00:00:00Z',
    lastUsed: '2024-01-21T08:30:00Z',
    usage: 15420
  },
  {
    id: 2,
    name: 'Development API Key',
    key: 'wl_dev_xyz789abc456def123ghi456jkl789mno012pqr345stu678vwx901yz',
    status: 'active',
    permissions: ['read', 'write'],
    createdAt: '2023-08-20T00:00:00Z',
    lastUsed: '2024-01-20T14:15:00Z',
    usage: 8750
  }
])

// Computed properties
const filteredInstances = computed(() => {
  let filtered = instances.value

  if (instanceFilter.value) {
    filtered = filtered.filter(instance => instance.status === instanceFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.lastActive) - new Date(a.lastActive))
})

// Methods
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatInstanceStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDomainStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getEmptyMessage = () => {
  if (instanceFilter.value) {
    return 'No instances match your filter criteria'
  }
  return 'No instances found'
}

const filterInstances = () => {
  // Filtering is handled by computed property
}

const viewBranding = () => {
  showSuccess('Opening branding customization')
}

const viewDomains = () => {
  showSuccess('Opening domain management')
}

const viewApiKeys = () => {
  showSuccess('Opening API key management')
}

const manageInstance = (instance) => {
  showSuccess(`Opening management for ${instance.name}`)
}

const viewInstanceAnalytics = (instance) => {
  showSuccess(`Opening analytics for ${instance.name}`)
}

const editInstance = (instance) => {
  showSuccess(`Editing instance: ${instance.name}`)
}

const handleLogoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      brandingForm.logo = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const removeLogo = () => {
  brandingForm.logo = ''
}

const previewBranding = () => {
  showSuccess('Opening branding preview')
}

const resetBranding = () => {
  Object.assign(brandingForm, {
    logo: '',
    primaryColor: '#3B82F6',
    secondaryColor: '#10B981',
    accentColor: '#F59E0B',
    textColor: '#1F2937',
    fontFamily: 'Inter',
    layoutStyle: 'modern',
    navigationPosition: 'top',
    buttonStyle: 'rounded',
    companyName: '',
    tagline: '',
    welcomeMessage: '',
    footerText: ''
  })
  showSuccess('Branding reset to default')
}

const saveBranding = async () => {
  try {
    // const response = await apiPost('/whitelabel/branding', brandingForm)
    // if (response.success) {
    //   showSuccess('Branding saved successfully')
    // }
    
    // For demo, simulate save
    showSuccess('Branding saved successfully')
  } catch (error) {
    console.error('Error saving branding:', error)
    showError('Failed to save branding')
  }
}

const verifyDomain = async (domain) => {
  try {
    // const response = await apiPost(`/whitelabel/domains/${domain.id}/verify`)
    // if (response.success) {
    //   domain.status = 'active'
    //   showSuccess('Domain verified successfully')
    // }
    
    // For demo, simulate verification
    domain.status = 'active'
    showSuccess('Domain verified successfully')
  } catch (error) {
    console.error('Error verifying domain:', error)
    showError('Failed to verify domain')
  }
}

const editDomain = (domain) => {
  showSuccess(`Editing domain: ${domain.name}`)
}

const deleteDomain = async (domain) => {
  const confirmed = await showConfirm('Are you sure you want to delete this domain?')
  if (confirmed) {
    try {
      // const response = await apiDelete(`/whitelabel/domains/${domain.id}`)
      // if (response.success) {
      //   const index = domains.value.findIndex(d => d.id === domain.id)
      //   domains.value.splice(index, 1)
      //   showSuccess('Domain deleted successfully')
      // }
      
      // For demo, simulate deletion
      const index = domains.value.findIndex(d => d.id === domain.id)
      domains.value.splice(index, 1)
      showSuccess('Domain deleted successfully')
    } catch (error) {
      console.error('Error deleting domain:', error)
      showError('Failed to delete domain')
    }
  }
}

const copyApiKey = async (apiKey) => {
  try {
    await navigator.clipboard.writeText(apiKey.key)
    showSuccess('API key copied to clipboard')
  } catch (error) {
    console.error('Error copying API key:', error)
    showError('Failed to copy API key')
  }
}

const maskedApiKey = (key) => {
  if (!key) return ''
  return key.substring(0, 8) + '...' + key.substring(key.length - 4)
}

const deleteApiKey = async (apiKey) => {
  const confirmed = await showConfirm('Are you sure you want to delete this API key?')
  if (confirmed) {
    try {
      // const response = await apiDelete(`/whitelabel/api-keys/${apiKey.id}`)
      // if (response.success) {
      //   const index = apiKeys.value.findIndex(k => k.id === apiKey.id)
      //   apiKeys.value.splice(index, 1)
      //   showSuccess('API key deleted successfully')
      // }
      
      // For demo, simulate deletion
      const index = apiKeys.value.findIndex(k => k.id === apiKey.id)
      apiKeys.value.splice(index, 1)
      showSuccess('API key deleted successfully')
    } catch (error) {
      console.error('Error deleting API key:', error)
      showError('Failed to delete API key')
    }
  }
}

const closeInstanceModal = () => {
  showInstanceModal.value = false
  resetInstanceForm()
}

const resetInstanceForm = () => {
  Object.assign(instanceForm, {
    name: '',
    environment: '',
    description: '',
    plan: '',
    domain: '',
    features: []
  })
}

const createInstance = async () => {
  if (!instanceForm.name || !instanceForm.environment || !instanceForm.plan) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/whitelabel/instances', instanceForm)
    // if (response.success) {
    //   instances.value.unshift(response.instance)
    //   showSuccess('Instance created successfully')
    //   closeInstanceModal()
    //   resetInstanceForm()
    // }
    
    // For demo, simulate creation
    const newInstance = {
      id: Date.now(),
      name: instanceForm.name,
      description: instanceForm.description,
      status: 'active',
      environment: instanceForm.environment,
      plan: instanceForm.plan,
      domain: instanceForm.domain,
      logo: '/api/placeholder/60x60',
      users: 0,
      createdAt: new Date().toISOString(),
      lastActive: new Date().toISOString(),
      health: 'good',
      features: instanceForm.features
    }
    
    instances.value.unshift(newInstance)
    showSuccess('Instance created successfully')
    closeInstanceModal()
    resetInstanceForm()
  } catch (error) {
    console.error('Error creating instance:', error)
    showError('Failed to create instance')
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/whitelabel')
    // if (response.success) {
    //   instances.value = response.instances || []
    //   domains.value = response.domains || []
    //   apiKeys.value = response.apiKeys || []
    //   Object.assign(whiteLabelStatus, response.status)
    //   Object.assign(whiteLabelStats, response.stats)
    // }
    
    // For demo, use mock data
    loading.value = false
  } catch (error) {
    console.error('Error loading white label data:', error)
    showError('Failed to load white label data')
    loading.value = false
  }
})
</script>

<style scoped>
.white-label {
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

.status-section,
.actions-section,
.instances-section,
.branding-section,
.domains-section,
.api-section {
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

.status-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.whitelabel-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.whitelabel-icon {
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

.whitelabel-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.whitelabel-details p {
  margin: 0;
  color: var(--text-secondary);
}

.status-badge .badge {
  padding: 0.5rem 1.5rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.badge.inactive {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.action-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
}

.action-icon.branding {
  background: var(--info-color);
}

.action-icon.domains {
  background: var(--warning-color);
}

.action-icon.api {
  background: var(--success-color);
}

.action-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.action-card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.filter-dropdown {
  position: relative;
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

.create-btn,
.create-first-btn,
.preview-btn {
  padding: 0.75rem 1.5rem;
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

.create-btn:hover,
.create-first-btn:hover,
.preview-btn:hover {
  background: var(--primary-hover);
}

.create-first-btn {
  margin-top: 2rem;
  align-self: center;
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

.instances-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.instance-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.instance-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.instance-card.inactive {
  opacity: 0.7;
  border-left: 4px solid var(--warning-color);
}

.instance-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.instance-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.instance-logo {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
}

.instance-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.instance-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.instance-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
}

.environment-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.environment-badge.production {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.environment-badge.development {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.instance-plan {
  padding: 0.25rem 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.instance-content {
  padding: 1.5rem;
}

.instance-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.instance-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.instance-stats .detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.instance-stats .detail-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.instance-stats .detail-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.instance-features h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.feature-tag {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.instance-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--glass-bg-tertiary);
  border-top: 1px solid var(--glass-border);
}

.instance-actions {
  display: flex;
  gap: 0.5rem;
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

.action-btn.manage:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.analytics:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.edit:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.delete:hover,
.action-btn.verify:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.instance-health {
  display: flex;
  align-items: center;
}

.health-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success-color);
}

.health-indicator.excellent .health-dot {
  background: var(--success-color);
}

.health-indicator.good .health-dot {
  background: var(--info-color);
}

.health-indicator.warning .health-dot {
  background: var(--warning-color);
}

.branding-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.branding-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.branding-header {
  margin-bottom: 1.5rem;
}

.branding-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.branding-content {
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

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.logo-upload {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.upload-btn {
  padding: 0.75rem 1.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  align-self: flex-start;
}

.upload-btn:hover {
  background: var(--glass-bg-hover);
}

.uploaded-logo {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
}

.uploaded-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-logo {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 24px;
  height: 24px;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.color-input {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.color-picker {
  width: 50px;
  height: 40px;
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  cursor: pointer;
}

.color-text {
  flex: 1;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  font-family: monospace;
}

.feature-selection {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
}

.branding-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 1rem 2rem;
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

.domains-table {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
  padding: 1rem;
  border-bottom: 1px solid var(--glass-border);
  transition: all 0.3s ease;
}

.table-row:hover {
  background: var(--glass-bg-hover);
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.domain-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.domain-name {
  color: var(--text-primary);
  font-weight: 600;
}

.domain-url {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.instance-name {
  color: var(--text-primary);
  font-weight: 600;
}

.ssl-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.ssl-badge.valid {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.ssl-badge.expired {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.added-date {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.domain-actions {
  display: flex;
  gap: 0.5rem;
}

.api-keys-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.api-key-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.api-key-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.key-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.key-actions {
  display: flex;
  gap: 0.5rem;
}

.api-key-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.key-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.key-details .detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.key-details .detail-item label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.key-details .detail-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.key-value {
  background: var(--glass-bg-tertiary);
  padding: 0.5rem;
  border-radius: 6px;
  font-family: monospace;
  font-size: 0.8rem;
  color: var(--text-primary);
}

.key-permissions h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.permission-tag {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
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
  max-width: 700px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
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

.instance-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

@media (max-width: 768px) {
  .white-label {
    padding: 1rem;
  }
  
  .status-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .instances-grid {
    grid-template-columns: 1fr;
  }
  
  .branding-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-selection {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .table-cell {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .api-keys-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
