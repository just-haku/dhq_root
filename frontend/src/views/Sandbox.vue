<template>
  <div class="sandbox">
    <div class="page-header">
      <h1>Development Sandbox</h1>
      <p>Safe environment for testing and experimentation</p>
    </div>

    <!-- Sandbox Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-flask"></i>
          </div>
          <div class="card-content">
            <h3>{{ sandboxStats.activeSandboxes }}</h3>
            <p>Active Sandboxes</p>
            <span class="sandbox-count">{{ sandboxStats.totalSandboxes }} total</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon resources">
            <i class="fas fa-server"></i>
          </div>
          <div class="card-content">
            <h3>{{ sandboxStats.resourceUsage }}%</h3>
            <p>Resource Usage</p>
            <span class="resource-status" :class="getResourceClass(sandboxStats.resourceUsage)">
              {{ getResourceStatus(sandboxStats.resourceUsage) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon uptime">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ sandboxStats.uptime }}h</h3>
            <p>Total Uptime</p>
            <span class="uptime-status">{{ sandboxStats.avgUptime }}h avg</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon experiments">
            <i class="fas fa-vial"></i>
          </div>
          <div class="card-content">
            <h3>{{ sandboxStats.experiments }}</h3>
            <p>Experiments</p>
            <span class="experiment-count">{{ sandboxStats.runningExperiments }} running</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="create-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          New Sandbox
        </button>
        <button class="clone-btn" @click="showCloneModal = true">
          <i class="fas fa-copy"></i>
          Clone
        </button>
        <button class="import-btn" @click="showImportModal = true">
          <i class="fas fa-upload"></i>
          Import
        </button>
        <button class="export-btn" @click="exportSandboxes">
          <i class="fas fa-download"></i>
          Export
        </button>
      </div>
    </div>

    <!-- Sandbox List -->
    <div class="sandboxes-section">
      <div class="section-header">
        <h2>My Sandboxes</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterSandboxes">
              <option value="">All Status</option>
              <option value="running">Running</option>
              <option value="stopped">Stopped</option>
              <option value="paused">Paused</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="environmentFilter" @change="filterSandboxes">
              <option value="">All Environments</option>
              <option value="development">Development</option>
              <option value="staging">Staging</option>
              <option value="testing">Testing</option>
              <option value="production">Production</option>
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
        <p>Loading sandboxes...</p>
      </div>

      <div v-else-if="filteredSandboxes.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-flask"></i>
        </div>
        <h3>No sandboxes found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Sandbox
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="sandboxes-grid">
          <div 
            v-for="sandbox in filteredSandboxes" 
            :key="sandbox.id"
            class="sandbox-card"
            :class="{ 'running': sandbox.status === 'running', 'stopped': sandbox.status === 'stopped', 'paused': sandbox.status === 'paused', 'error': sandbox.status === 'error' }"
          >
            <div class="sandbox-header">
              <div class="sandbox-icon">
                <i :class="getEnvironmentIcon(sandbox.environment)"></i>
              </div>
              <div class="sandbox-status">
                <span :class="['status-badge', sandbox.status]">{{ sandbox.status }}</span>
              </div>
            </div>

            <div class="sandbox-content">
              <h3>{{ sandbox.name }}</h3>
              <p>{{ sandbox.description }}</p>
              
              <div class="sandbox-info">
                <span class="environment">{{ sandbox.environment }}</span>
                <span class="template">{{ sandbox.template }}</span>
                <span class="duration">{{ sandbox.duration }}</span>
              </div>

              <div class="sandbox-details">
                <div class="detail-item">
                  <label>Created:</label>
                  <span>{{ formatDateTime(sandbox.createdAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Resources:</label>
                  <span>{{ sandbox.resources }}</span>
                </div>
                <div class="detail-item">
                  <label>URL:</label>
                  <span class="sandbox-url">{{ sandbox.url }}</span>
                </div>
              </div>

              <div class="sandbox-progress" v-if="sandbox.status === 'running'">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: sandbox.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ sandbox.progress }}%</span>
              </div>

              <div class="sandbox-actions">
                <button class="action-btn open" @click="openSandbox(sandbox)" v-if="sandbox.status === 'running'">
                  <i class="fas fa-external-link-alt"></i>
                  Open
                </button>
                <button class="action-btn start" @click="startSandbox(sandbox)" v-if="sandbox.status === 'stopped'">
                  <i class="fas fa-play"></i>
                  Start
                </button>
                <button class="action-btn stop" @click="stopSandbox(sandbox)" v-if="sandbox.status === 'running'">
                  <i class="fas fa-stop"></i>
                  Stop
                </button>
                <button class="action-btn restart" @click="restartSandbox(sandbox)" v-if="['running', 'stopped'].includes(sandbox.status)">
                  <i class="fas fa-redo"></i>
                  Restart
                </button>
                <button class="action-btn clone" @click="cloneSandbox(sandbox)">
                  <i class="fas fa-copy"></i>
                  Clone
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="sandboxes-list">
          <div 
            v-for="sandbox in filteredSandboxes" 
            :key="sandbox.id"
            class="sandbox-list-card"
            :class="{ 'running': sandbox.status === 'running', 'stopped': sandbox.status === 'stopped', 'paused': sandbox.status === 'paused', 'error': sandbox.status === 'error' }"
          >
            <div class="sandbox-list-header">
              <div class="sandbox-list-info">
                <div class="sandbox-icon">
                  <i :class="getEnvironmentIcon(sandbox.environment)"></i>
                </div>
                <div class="sandbox-details">
                  <h3>{{ sandbox.name }}</h3>
                  <p>{{ sandbox.description }}</p>
                  <div class="sandbox-info">
                    <span class="environment">{{ sandbox.environment }}</span>
                    <span class="template">{{ sandbox.template }}</span>
                    <span :class="['status-badge', sandbox.status]">{{ sandbox.status }}</span>
                    <span class="duration">{{ sandbox.duration }}</span>
                  </div>
                </div>
              </div>
              <div class="sandbox-list-stats">
                <div class="detail-item">
                  <label>Created:</label>
                  <span>{{ formatDateTime(sandbox.createdAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Resources:</label>
                  <span>{{ sandbox.resources }}</span>
                </div>
                <div class="detail-item">
                  <label>URL:</label>
                  <span class="sandbox-url">{{ sandbox.url }}</span>
                </div>
              </div>
              <div class="sandbox-list-actions">
                <button class="action-btn open" @click="openSandbox(sandbox)" v-if="sandbox.status === 'running'">
                  <i class="fas fa-external-link-alt"></i>
                </button>
                <button class="action-btn start" @click="startSandbox(sandbox)" v-if="sandbox.status === 'stopped'">
                  <i class="fas fa-play"></i>
                </button>
                <button class="action-btn stop" @click="stopSandbox(sandbox)" v-if="sandbox.status === 'running'">
                  <i class="fas fa-stop"></i>
                </button>
                <button class="action-btn restart" @click="restartSandbox(sandbox)" v-if="['running', 'stopped'].includes(sandbox.status)">
                  <i class="fas fa-redo"></i>
                </button>
                <button class="action-btn clone" @click="cloneSandbox(sandbox)">
                  <i class="fas fa-copy"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Templates -->
    <div class="templates-section">
      <div class="section-header">
        <h2>Sandbox Templates</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="templateFilter" @change="filterTemplates">
              <option value="">All Templates</option>
              <option value="web">Web Applications</option>
              <option value="api">API Services</option>
              <option value="database">Database</option>
              <option value="mobile">Mobile</option>
            </select>
          </div>
          <button class="create-template-btn" @click="showTemplateModal = true">
            <i class="fas fa-plus"></i>
            Create Template
          </button>
        </div>
      </div>

      <div class="templates-grid">
        <div 
          v-for="template in filteredTemplates" 
          :key="template.id"
          class="template-card"
        >
          <div class="template-header">
            <div class="template-icon">
              <i :class="getTemplateIcon(template.type)"></i>
            </div>
            <div class="template-badge">
              <span class="badge">{{ template.type }}</span>
            </div>
          </div>

          <div class="template-content">
            <h3>{{ template.name }}</h3>
            <p>{{ template.description }}</p>
            
            <div class="template-info">
              <span class="version">{{ template.version }}</span>
              <span class="popularity">{{ template.popularity }} uses</span>
              <span class="rating">{{ template.rating }}★</span>
            </div>

            <div class="template-features">
              <div 
                v-for="feature in template.features" 
                :key="feature"
                class="feature-tag"
              >
                {{ feature }}
              </div>
            </div>

            <div class="template-actions">
              <button class="action-btn use" @click="useTemplate(template)">
                <i class="fas fa-plus"></i>
                Use Template
              </button>
              <button class="action-btn preview" @click="previewTemplate(template)">
                <i class="fas fa-eye"></i>
                Preview
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Resource Usage -->
    <div class="resources-section">
      <div class="section-header">
        <h2>Resource Usage</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="timeRange" @change="updateResources">
              <option value="1">Last hour</option>
              <option value="24">Last 24 hours</option>
              <option value="168">Last week</option>
              <option value="720">Last month</option>
            </select>
          </div>
          <button class="refresh-btn" @click="refreshResources">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="resources-grid">
        <div class="resource-card">
          <div class="resource-header">
            <h3>CPU Usage</h3>
            <span class="resource-value">{{ resources.cpuUsage }}%</span>
          </div>
          <div class="resource-chart">
            <canvas ref="cpuChart"></canvas>
          </div>
          <div class="resource-details">
            <span class="detail-item">Average: {{ resources.avgCpu }}%</span>
            <span class="detail-item">Peak: {{ resources.peakCpu }}%</span>
          </div>
        </div>

        <div class="resource-card">
          <div class="resource-header">
            <h3>Memory Usage</h3>
            <span class="resource-value">{{ resources.memoryUsage }}MB</span>
          </div>
          <div class="resource-chart">
            <canvas ref="memoryChart"></canvas>
          </div>
          <div class="resource-details">
            <span class="detail-item">Average: {{ resources.avgMemory }}MB</span>
            <span class="detail-item">Peak: {{ resources.peakMemory }}MB</span>
          </div>
        </div>

        <div class="resource-card">
          <div class="resource-header">
            <h3>Storage Usage</h3>
            <span class="resource-value">{{ resources.storageUsage }}GB</span>
          </div>
          <div class="resource-chart">
            <canvas ref="storageChart"></canvas>
          </div>
          <div class="resource-details">
            <span class="detail-item">Used: {{ resources.usedStorage }}GB</span>
            <span class="detail-item">Total: {{ resources.totalStorage }}GB</span>
          </div>
        </div>

        <div class="resource-card">
          <div class="resource-header">
            <h3>Network Usage</h3>
            <span class="resource-value">{{ resources.networkUsage }}MB/s</span>
          </div>
          <div class="resource-chart">
            <canvas ref="networkChart"></canvas>
          </div>
          <div class="resource-details">
            <span class="detail-item">Upload: {{ resources.uploadSpeed }}MB/s</span>
            <span class="detail-item">Download: {{ resources.downloadSpeed }}MB/s</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Sandbox Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create New Sandbox</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="sandbox-form">
            <div class="form-group">
              <label>Sandbox Name *</label>
              <input 
                v-model="sandboxForm.name" 
                type="text" 
                placeholder="Enter sandbox name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="sandboxForm.description" 
                placeholder="Describe your sandbox"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Template *</label>
                <select v-model="sandboxForm.template" required>
                  <option value="">Select template</option>
                  <option 
                    v-for="template in templates" 
                    :key="template.id"
                    :value="template.id"
                  >
                    {{ template.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Environment *</label>
                <select v-model="sandboxForm.environment" required>
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="testing">Testing</option>
                  <option value="production">Production</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Resources</label>
              <div class="resources-config">
                <div class="resource-input">
                  <label>CPU Cores</label>
                  <input 
                    v-model.number="sandboxForm.resources.cpu" 
                    type="number" 
                    min="1" 
                    max="8"
                  />
                </div>
                <div class="resource-input">
                  <label>Memory (GB)</label>
                  <input 
                    v-model.number="sandboxForm.resources.memory" 
                    type="number" 
                    min="1" 
                    max="32"
                  />
                </div>
                <div class="resource-input">
                  <label>Storage (GB)</label>
                  <input 
                    v-model.number="sandboxForm.resources.storage" 
                    type="number" 
                    min="10" 
                    max="500"
                  />
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Configuration</label>
              <div class="config-options">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sandboxForm.config.autoStart"
                  />
                  <span>Auto start</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sandboxForm.config.autoStop"
                  />
                  <span>Auto stop after inactivity</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sandboxForm.config.enableBackups"
                  />
                  <span>Enable automatic backups</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="sandboxForm.config.enableMonitoring"
                  />
                  <span>Enable monitoring</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Environment Variables</label>
              <div class="env-vars-container">
                <div 
                  v-for="(envVar, index) in sandboxForm.environmentVariables" 
                  :key="index"
                  class="env-var-item"
                >
                  <input 
                    v-model="envVar.key" 
                    type="text" 
                    placeholder="Key"
                  />
                  <input 
                    v-model="envVar.value" 
                    type="text" 
                    placeholder="Value"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeEnvVar(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-env-var-btn" @click="addEnvVar">
                  <i class="fas fa-plus"></i>
                  Add Variable
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button class="btn-primary" @click="createSandbox">
            <i class="fas fa-plus"></i>
            Create Sandbox
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Chart } from 'chart.js/auto'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const statusFilter = ref('')
const environmentFilter = ref('')
const templateFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('24')
const showCreateModal = ref(false)
const showCloneModal = ref(false)
const showImportModal = ref(false)
const showTemplateModal = ref(false)

// Chart instances
const cpuChart = ref(null)
const memoryChart = ref(null)
const storageChart = ref(null)
const networkChart = ref(null)

// Sandbox stats
const sandboxStats = reactive({
  activeSandboxes: 3,
  totalSandboxes: 12,
  resourceUsage: 65,
  uptime: 156,
  avgUptime: 24,
  experiments: 8,
  runningExperiments: 2
})

// Resources data
const resources = reactive({
  cpuUsage: 45,
  avgCpu: 42,
  peakCpu: 78,
  memoryUsage: 2048,
  avgMemory: 1856,
  peakMemory: 3072,
  storageUsage: 45,
  usedStorage: 45,
  totalStorage: 100,
  networkUsage: 12.5,
  uploadSpeed: 5.2,
  downloadSpeed: 7.3
})

// Sandbox form
const sandboxForm = reactive({
  name: '',
  description: '',
  template: '',
  environment: 'development',
  resources: {
    cpu: 2,
    memory: 4,
    storage: 50
  },
  config: {
    autoStart: true,
    autoStop: false,
    enableBackups: true,
    enableMonitoring: true
  },
  environmentVariables: []
})

// Mock data
const sandboxes = ref([
  {
    id: 1,
    name: 'Frontend Development',
    description: 'React development environment with hot reload',
    status: 'running',
    environment: 'development',
    template: 'React App',
    duration: '2 days 5 hours',
    createdAt: '2024-01-19T10:30:00Z',
    resources: '2 CPU, 4GB RAM, 50GB Storage',
    url: 'https://frontend-dev.example.com',
    progress: 85
  },
  {
    id: 2,
    name: 'API Testing',
    description: 'Node.js API testing environment',
    status: 'stopped',
    environment: 'staging',
    template: 'Node.js API',
    duration: '1 day 12 hours',
    createdAt: '2024-01-20T14:45:00Z',
    resources: '1 CPU, 2GB RAM, 20GB Storage',
    url: 'https://api-test.example.com',
    progress: 0
  },
  {
    id: 3,
    name: 'Database Sandbox',
    description: 'PostgreSQL database for testing',
    status: 'paused',
    environment: 'testing',
    template: 'PostgreSQL',
    duration: '3 days 8 hours',
    createdAt: '2024-01-18T09:00:00Z',
    resources: '1 CPU, 2GB RAM, 30GB Storage',
    url: 'https://db-test.example.com',
    progress: 60
  },
  {
    id: 4,
    name: 'Mobile App Testing',
    description: 'React Native mobile development',
    status: 'error',
    environment: 'development',
    template: 'React Native',
    duration: 'Failed',
    createdAt: '2024-01-17T16:30:00Z',
    resources: '2 CPU, 4GB RAM, 40GB Storage',
    url: 'https://mobile-dev.example.com',
    progress: 0
  }
])

const templates = ref([
  {
    id: 1,
    name: 'React App',
    description: 'Modern React application with Vite',
    type: 'web',
    version: 'v18.2.0',
    popularity: 234,
    rating: 4.8,
    features: ['Hot Reload', 'TypeScript', 'Tailwind CSS', 'ESLint']
  },
  {
    id: 2,
    name: 'Node.js API',
    description: 'RESTful API with Express.js',
    type: 'api',
    version: 'v20.0.0',
    popularity: 189,
    rating: 4.6,
    features: ['Express', 'MongoDB', 'JWT Auth', 'API Docs']
  },
  {
    id: 3,
    name: 'PostgreSQL',
    description: 'Relational database server',
    type: 'database',
    version: 'v15.4',
    popularity: 156,
    rating: 4.9,
    features: ['pgAdmin', 'Backups', 'Replication', 'Monitoring']
  },
  {
    id: 4,
    name: 'React Native',
    description: 'Cross-platform mobile development',
    type: 'mobile',
    version: 'v0.72.6',
    popularity: 98,
    rating: 4.5,
    features: ['iOS/Android', 'Hot Reload', 'Debug Tools', 'OTA Updates']
  }
])

// Computed properties
const filteredSandboxes = computed(() => {
  let filtered = sandboxes.value

  if (statusFilter.value) {
    filtered = filtered.filter(sandbox => sandbox.status === statusFilter.value)
  }

  if (environmentFilter.value) {
    filtered = filtered.filter(sandbox => sandbox.environment === environmentFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

const filteredTemplates = computed(() => {
  let filtered = templates.value

  if (templateFilter.value) {
    filtered = filtered.filter(template => template.type === templateFilter.value)
  }

  return filtered.sort((a, b) => b.popularity - a.popularity)
})

// Methods
const loadSandboxData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/sandbox')
    // if (response.success) {
    //   sandboxes.value = response.sandboxes || []
    //   templates.value = response.templates || []
    //   Object.assign(sandboxStats, response.stats)
    //   Object.assign(resources, response.resources)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading sandbox data:', error)
    showError('Failed to load sandbox data')
  } finally {
    loading.value = false
  }
}

const filterSandboxes = () => {
  // This is reactive, no additional action needed
}

const filterTemplates = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || environmentFilter.value) {
    return 'No sandboxes match your filter criteria'
  }
  return 'No sandboxes found'
}

const getEnvironmentIcon = (environment) => {
  const icons = {
    'development': 'fas fa-code',
    'staging': 'fas fa-flask',
    'testing': 'fas fa-vial',
    'production': 'fas fa-rocket'
  }
  return icons[environment] || 'fas fa-server'
}

const getTemplateIcon = (type) => {
  const icons = {
    'web': 'fas fa-globe',
    'api': 'fas fa-plug',
    'database': 'fas fa-database',
    'mobile': 'fas fa-mobile-alt'
  }
  return icons[type] || 'fas fa-cube'
}

const getResourceClass = (usage) => {
  if (usage >= 90) return 'critical'
  if (usage >= 75) return 'high'
  if (usage >= 50) return 'medium'
  return 'low'
}

const getResourceStatus = (usage) => {
  if (usage >= 90) return 'Critical'
  if (usage >= 75) return 'High'
  if (usage >= 50) return 'Medium'
  return 'Low'
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const openSandbox = (sandbox) => {
  // Open sandbox in new tab
  window.open(sandbox.url, '_blank')
  showSuccess(`Opening sandbox: ${sandbox.name}`)
}

const startSandbox = async (sandbox) => {
  try {
    // const response = await apiPost(`/sandbox/${sandbox.id}/start`)
    // if (response.success) {
    //   sandbox.status = 'running'
    //   showSuccess('Sandbox started successfully')
    // }
    
    // For demo, simulate start
    sandbox.status = 'running'
    sandbox.progress = 0
    showSuccess('Sandbox started successfully')
  } catch (error) {
    console.error('Error starting sandbox:', error)
    showError('Failed to start sandbox')
  }
}

const stopSandbox = async (sandbox) => {
  const confirmed = await showConfirm(`Are you sure you want to stop sandbox "${sandbox.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/sandbox/${sandbox.id}/stop`)
    // if (response.success) {
    //   sandbox.status = 'stopped'
    //   sandbox.progress = 0
    //   showSuccess('Sandbox stopped successfully')
    // }
    
    // For demo, simulate stop
    sandbox.status = 'stopped'
    sandbox.progress = 0
    showSuccess('Sandbox stopped successfully')
  } catch (error) {
    console.error('Error stopping sandbox:', error)
    showError('Failed to stop sandbox')
  }
}

const restartSandbox = async (sandbox) => {
  const confirmed = await showConfirm(`Are you sure you want to restart sandbox "${sandbox.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/sandbox/${sandbox.id}/restart`)
    // if (response.success) {
    //   sandbox.status = 'running'
    //   sandbox.progress = 0
    //   showSuccess('Sandbox restarted successfully')
    // }
    
    // For demo, simulate restart
    sandbox.status = 'running'
    sandbox.progress = 0
    showSuccess('Sandbox restarted successfully')
  } catch (error) {
    console.error('Error restarting sandbox:', error)
    showError('Failed to restart sandbox')
  }
}

const cloneSandbox = async (sandbox) => {
  try {
    // const response = await apiPost(`/sandbox/${sandbox.id}/clone`)
    // if (response.success) {
    //   sandboxes.value.unshift(response.sandbox)
    //   showSuccess('Sandbox cloned successfully')
    // }
    
    // For demo, simulate clone
    const newSandbox = {
      id: Date.now(),
      name: `${sandbox.name} (Clone)`,
      description: sandbox.description,
      status: 'stopped',
      environment: sandbox.environment,
      template: sandbox.template,
      duration: '0 min',
      createdAt: new Date().toISOString(),
      resources: sandbox.resources,
      url: `https://${sandbox.name.toLowerCase().replace(/\s+/g, '-')}-clone.example.com`,
      progress: 0
    }
    
    sandboxes.value.unshift(newSandbox)
    showSuccess('Sandbox cloned successfully')
  } catch (error) {
    console.error('Error cloning sandbox:', error)
    showError('Failed to clone sandbox')
  }
}

const exportSandboxes = async () => {
  try {
    // const response = await apiPost('/sandbox/export')
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = 'sandboxes.json'
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Sandboxes exported successfully')
    // }
    
    // For demo, simulate export
    showSuccess('Sandboxes exported successfully')
  } catch (error) {
    console.error('Error exporting sandboxes:', error)
    showError('Failed to export sandboxes')
  }
}

const useTemplate = (template) => {
  sandboxForm.template = template.id
  showCreateModal.value = true
  showSuccess(`Selected template: ${template.name}`)
}

const previewTemplate = (template) => {
  // Open template preview modal or navigate to detailed view
  showSuccess(`Previewing template: ${template.name}`)
}

const addEnvVar = () => {
  sandboxForm.environmentVariables.push({ key: '', value: '' })
}

const removeEnvVar = (index) => {
  sandboxForm.environmentVariables.splice(index, 1)
}

const createSandbox = async () => {
  if (!sandboxForm.name || !sandboxForm.template || !sandboxForm.environment) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/sandbox', sandboxForm)
    // if (response.success) {
    //   sandboxes.value.unshift(response.sandbox)
    //   showSuccess('Sandbox created successfully')
    //   closeCreateModal()
    //   resetSandboxForm()
    // }
    
    // For demo, simulate creation
    const template = templates.value.find(t => t.id === sandboxForm.template)
    const newSandbox = {
      id: Date.now(),
      name: sandboxForm.name,
      description: sandboxForm.description,
      status: sandboxForm.config.autoStart ? 'running' : 'stopped',
      environment: sandboxForm.environment,
      template: template ? template.name : 'Custom',
      duration: sandboxForm.config.autoStart ? '0 min' : 'Pending',
      createdAt: new Date().toISOString(),
      resources: `${sandboxForm.resources.cpu} CPU, ${sandboxForm.resources.memory}GB RAM, ${sandboxForm.resources.storage}GB Storage`,
      url: `https://${sandboxForm.name.toLowerCase().replace(/\s+/g, '-')}.example.com`,
      progress: 0
    }
    
    sandboxes.value.unshift(newSandbox)
    showSuccess('Sandbox created successfully')
    closeCreateModal()
    resetSandboxForm()
  } catch (error) {
    console.error('Error creating sandbox:', error)
    showError('Failed to create sandbox')
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetSandboxForm()
}

const resetSandboxForm = () => {
  Object.assign(sandboxForm, {
    name: '',
    description: '',
    template: '',
    environment: 'development',
    resources: {
      cpu: 2,
      memory: 4,
      storage: 50
    },
    config: {
      autoStart: true,
      autoStop: false,
      enableBackups: true,
      enableMonitoring: true
    },
    environmentVariables: []
  })
}

const updateResources = async () => {
  try {
    // const response = await apiGet('/sandbox/resources', { timeRange: timeRange.value })
    // if (response.success) {
    //   Object.assign(resources, response.resources)
    //   updateCharts()
    // }
    
    // For demo, simulate update
    updateCharts()
  } catch (error) {
    console.error('Error updating resources:', error)
    showError('Failed to update resources')
  }
}

const refreshResources = async () => {
  try {
    // const response = await apiGet('/sandbox/resources/refresh')
    // if (response.success) {
    //   Object.assign(resources, response.resources)
    //   updateCharts()
    // }
    
    // For demo, simulate refresh
    updateCharts()
    showSuccess('Resource data refreshed successfully')
  } catch (error) {
    console.error('Error refreshing resources:', error)
    showError('Failed to refresh resources')
  }
}

const initCharts = () => {
  // Initialize CPU chart
  if (cpuChart.value) cpuChart.value.destroy()
  cpuChart.value = new Chart(cpuChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 60 }, (_, i) => `${i}s`),
      datasets: [{
        label: 'CPU Usage %',
        data: Array.from({ length: 60 }, () => Math.random() * 100),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  })

  // Initialize Memory chart
  if (memoryChart.value) memoryChart.value.destroy()
  memoryChart.value = new Chart(memoryChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 60 }, (_, i) => `${i}s`),
      datasets: [{
        label: 'Memory Usage MB',
        data: Array.from({ length: 60 }, () => Math.random() * 4096),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Storage chart
  if (storageChart.value) storageChart.value.destroy()
  storageChart.value = new Chart(storageChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 60 }, (_, i) => `${i}s`),
      datasets: [{
        label: 'Storage Usage GB',
        data: Array.from({ length: 60 }, () => Math.random() * 100),
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Network chart
  if (networkChart.value) networkChart.value.destroy()
  networkChart.value = new Chart(networkChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 60 }, (_, i) => `${i}s`),
      datasets: [{
        label: 'Network Usage MB/s',
        data: Array.from({ length: 60 }, () => Math.random() * 50),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })
}

const updateCharts = () => {
  // Update charts with new data
  if (cpuChart.value) {
    cpuChart.value.data.datasets[0].data = Array.from({ length: 60 }, () => Math.random() * 100)
    cpuChart.value.update('none')
  }

  if (memoryChart.value) {
    memoryChart.value.data.datasets[0].data = Array.from({ length: 60 }, () => Math.random() * 4096)
    memoryChart.value.update('none')
  }

  if (storageChart.value) {
    storageChart.value.data.datasets[0].data = Array.from({ length: 60 }, () => Math.random() * 100)
    storageChart.value.update('none')
  }

  if (networkChart.value) {
    networkChart.value.data.datasets[0].data = Array.from({ length: 60 }, () => Math.random() * 50)
    networkChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadSandboxData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (cpuChart.value) cpuChart.value.destroy()
  if (memoryChart.value) memoryChart.value.destroy()
  if (storageChart.value) storageChart.value.destroy()
  if (networkChart.value) networkChart.value.destroy()
})
</script>

<style scoped>
.sandbox {
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

.card-icon.resources {
  background: var(--warning-color);
}

.card-icon.uptime {
  background: var(--info-color);
}

.card-icon.experiments {
  background: var(--success-color);
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

.sandbox-count,
.resource-status,
.uptime-status,
.experiment-count {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.sandbox-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.resource-status.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.resource-status.high {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.resource-status.medium {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.resource-status.low {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.uptime-status {
  color: var(--text-secondary);
}

.experiment-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
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
.clone-btn,
.import-btn,
.export-btn {
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
.clone-btn:hover,
.import-btn:hover,
.export-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.clone-btn {
  background: var(--info-color);
}

.clone-btn:hover {
  background: var(--info-hover);
}

.import-btn {
  background: var(--warning-color);
}

.import-btn:hover {
  background: var(--warning-hover);
}

.export-btn {
  background: var(--success-color);
}

.export-btn:hover {
  background: var(--success-hover);
}

.sandboxes-section,
.templates-section,
.resources-section {
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

.create-template-btn,
.refresh-btn {
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

.create-template-btn:hover,
.refresh-btn:hover {
  background: var(--primary-hover);
}

.time-range select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
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

.sandboxes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.sandbox-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.sandbox-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.sandbox-card.running {
  border-color: var(--success-color);
}

.sandbox-card.stopped {
  border-color: var(--text-tertiary);
}

.sandbox-card.paused {
  border-color: var(--warning-color);
}

.sandbox-card.error {
  border-color: var(--danger-color);
}

.sandbox-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.sandbox-icon {
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

.status-badge.running {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.stopped {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.status-badge.paused {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.sandbox-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.sandbox-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.sandbox-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.environment,
.template,
.duration {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.sandbox-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.detail-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.sandbox-url {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: var(--primary-color);
}

.sandbox-progress {
  margin-bottom: 1rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.sandbox-actions {
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

.action-btn.open:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.start:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.stop:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.action-btn.restart:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.clone:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.sandboxes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sandbox-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.sandbox-list-card:hover {
  background: var(--glass-bg-hover);
}

.sandbox-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.sandbox-list-info {
  flex: 1;
}

.sandbox-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.sandbox-list-actions {
  display: flex;
  gap: 0.5rem;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.template-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.template-icon {
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

.template-badge .badge {
  padding: 0.25rem 0.75rem;
  background: var(--info-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.template-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.template-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.template-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.version,
.popularity,
.rating {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.template-features {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.feature-tag {
  padding: 0.25rem 0.5rem;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn.use:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.preview:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.resource-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.resource-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.resource-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.resource-chart {
  height: 150px;
  margin-bottom: 1rem;
}

.resource-details {
  display: flex;
  justify-content: space-between;
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
  max-width: 800px;
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

.sandbox-form {
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

.resources-config {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.resource-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.resource-input label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.resource-input input {
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
}

.config-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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

.env-vars-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.env-var-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.env-var-item input {
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
  font-size: 0.9rem;
}

.remove-btn:hover {
  background: var(--danger-hover);
}

.add-env-var-btn {
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

.add-env-var-btn:hover {
  background: var(--primary-hover);
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

@media (max-width: 768px) {
  .sandbox {
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
  
  .sandboxes-grid {
    grid-template-columns: 1fr;
  }
  
  .sandbox-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .sandbox-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .resources-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .resources-config {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
