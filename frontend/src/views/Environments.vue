<template>
  <div class="environments">
    <div class="page-header">
      <h1>Environment Management</h1>
      <p>Manage deployment environments, configurations, and infrastructure</p>
    </div>

    <!-- Environment Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-server"></i>
          </div>
          <div class="card-content">
            <h3>{{ envStats.totalEnvironments }}</h3>
            <p>Total Environments</p>
            <span class="env-count">{{ envStats.activeEnvironments }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon healthy">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <h3>{{ envStats.healthyEnvironments }}</h3>
            <p>Healthy</p>
            <span class="health-count">{{ envStats.issuesCount }} issues</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon services">
            <i class="fas fa-cubes"></i>
          </div>
          <div class="card-content">
            <h3>{{ envStats.totalServices }}</h3>
            <p>Services</p>
            <span class="service-count">{{ envStats.runningServices }} running</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon resources">
            <i class="fas fa-microchip"></i>
          </div>
          <div class="card-content">
            <h3>{{ envStats.resourceUsage }}%</h3>
            <p>Resource Usage</p>
            <span class="resource-status" :class="getResourceClass(envStats.resourceUsage)">
              {{ getResourceStatus(envStats.resourceUsage) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="create-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Environment
        </button>
        <button class="deploy-btn" @click="showDeployModal = true">
          <i class="fas fa-rocket"></i>
          Deploy
        </button>
        <button class="monitor-btn" @click="showMonitorModal = true">
          <i class="fas fa-chart-line"></i>
          Monitor
        </button>
        <button class="config-btn" @click="showConfigModal = true">
          <i class="fas fa-cog"></i>
          Configure
        </button>
      </div>
    </div>

    <!-- Environment List -->
    <div class="environments-section">
      <div class="section-header">
        <h2>Environments</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterEnvironments">
              <option value="">All Status</option>
              <option value="healthy">Healthy</option>
              <option value="unhealthy">Unhealthy</option>
              <option value="maintenance">Maintenance</option>
              <option value="offline">Offline</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="typeFilter" @change="filterEnvironments">
              <option value="">All Types</option>
              <option value="production">Production</option>
              <option value="staging">Staging</option>
              <option value="development">Development</option>
              <option value="testing">Testing</option>
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
        <p>Loading environments...</p>
      </div>

      <div v-else-if="filteredEnvironments.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-server"></i>
        </div>
        <h3>No environments found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Environment
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="environments-grid">
          <div 
            v-for="environment in filteredEnvironments" 
            :key="environment.id"
            class="environment-card"
            :class="{ 'unhealthy': environment.status === 'unhealthy', 'maintenance': environment.status === 'maintenance', 'offline': environment.status === 'offline' }"
          >
            <div class="environment-header">
              <div class="environment-icon">
                <i :class="getEnvironmentIcon(environment.type)"></i>
              </div>
              <div class="environment-status">
                <span :class="['status-badge', environment.status]">{{ environment.status }}</span>
              </div>
            </div>

            <div class="environment-content">
              <h3>{{ environment.name }}</h3>
              <p>{{ environment.description }}</p>
              
              <div class="environment-info">
                <span class="type">{{ environment.type }}</span>
                <span class="region">{{ environment.region }}</span>
                <span class="version">{{ environment.version }}</span>
              </div>

              <div class="environment-details">
                <div class="detail-item">
                  <label>URL:</label>
                  <span>{{ environment.url }}</span>
                </div>
                <div class="detail-item">
                  <label>Services:</label>
                  <span>{{ environment.services }}</span>
                </div>
                <div class="detail-item">
                  <label>Health:</label>
                  <span>{{ environment.health }}%</span>
                </div>
              </div>

              <div class="environment-metrics">
                <div class="metric-item">
                  <div class="metric-label">CPU</div>
                  <div class="metric-bar">
                    <div class="metric-fill" :style="{ width: environment.metrics.cpu + '%' }"></div>
                  </div>
                  <span class="metric-value">{{ environment.metrics.cpu }}%</span>
                </div>
                <div class="metric-item">
                  <div class="metric-label">Memory</div>
                  <div class="metric-bar">
                    <div class="metric-fill" :style="{ width: environment.metrics.memory + '%' }"></div>
                  </div>
                  <span class="metric-value">{{ environment.metrics.memory }}%</span>
                </div>
                <div class="metric-item">
                  <div class="metric-label">Storage</div>
                  <div class="metric-bar">
                    <div class="metric-fill" :style="{ width: environment.metrics.storage + '%' }"></div>
                  </div>
                  <span class="metric-value">{{ environment.metrics.storage }}%</span>
                </div>
              </div>

              <div class="environment-actions">
                <button class="action-btn view" @click="viewEnvironment(environment)">
                  <i class="fas fa-eye"></i>
                  View
                </button>
                <button class="action-btn deploy" @click="deployToEnvironment(environment)">
                  <i class="fas fa-rocket"></i>
                  Deploy
                </button>
                <button class="action-btn health" @click="checkHealth(environment)">
                  <i class="fas fa-heartbeat"></i>
                  Health
                </button>
                <button class="action-btn config" @click="configureEnvironment(environment)">
                  <i class="fas fa-cog"></i>
                  Config
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="environments-list">
          <div 
            v-for="environment in filteredEnvironments" 
            :key="environment.id"
            class="environment-list-card"
            :class="{ 'unhealthy': environment.status === 'unhealthy', 'maintenance': environment.status === 'maintenance', 'offline': environment.status === 'offline' }"
          >
            <div class="environment-list-header">
              <div class="environment-list-info">
                <div class="environment-icon">
                  <i :class="getEnvironmentIcon(environment.type)"></i>
                </div>
                <div class="environment-details">
                  <h3>{{ environment.name }}</h3>
                  <p>{{ environment.description }}</p>
                  <div class="environment-info">
                    <span class="type">{{ environment.type }}</span>
                    <span class="region">{{ environment.region }}</span>
                    <span :class="['status-badge', environment.status]">{{ environment.status }}</span>
                    <span class="version">{{ environment.version }}</span>
                  </div>
                </div>
              </div>
              <div class="environment-list-stats">
                <div class="detail-item">
                  <label>URL:</label>
                  <span>{{ environment.url }}</span>
                </div>
                <div class="detail-item">
                  <label>Services:</label>
                  <span>{{ environment.services }}</span>
                </div>
                <div class="detail-item">
                  <label>Health:</label>
                  <span>{{ environment.health }}%</span>
                </div>
              </div>
              <div class="environment-list-actions">
                <button class="action-btn view" @click="viewEnvironment(environment)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn deploy" @click="deployToEnvironment(environment)">
                  <i class="fas fa-rocket"></i>
                </button>
                <button class="action-btn health" @click="checkHealth(environment)">
                  <i class="fas fa-heartbeat"></i>
                </button>
                <button class="action-btn config" @click="configureEnvironment(environment)">
                  <i class="fas fa-cog"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Services Overview -->
    <div class="services-section">
      <div class="section-header">
        <h2>Services</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="serviceFilter" @change="filterServices">
              <option value="">All Services</option>
              <option value="running">Running</option>
              <option value="stopped">Stopped</option>
              <option value="error">Error</option>
            </select>
          </div>
          <button class="add-service-btn" @click="showAddServiceModal = true">
            <i class="fas fa-plus"></i>
            Add Service
          </button>
        </div>
      </div>

      <div class="services-grid">
        <div 
          v-for="service in filteredServices" 
          :key="service.id"
          class="service-card"
          :class="{ 'running': service.status === 'running', 'stopped': service.status === 'stopped', 'error': service.status === 'error' }"
        >
          <div class="service-header">
            <div class="service-icon">
              <i :class="getServiceIcon(service.type)"></i>
            </div>
            <div class="service-status">
              <span :class="['status-badge', service.status]">{{ service.status }}</span>
            </div>
          </div>

          <div class="service-content">
            <h3>{{ service.name }}</h3>
            <p>{{ service.description }}</p>
            
            <div class="service-info">
              <span class="type">{{ service.type }}</span>
              <span class="environment">{{ service.environment }}</span>
              <span class="version">{{ service.version }}</span>
            </div>

            <div class="service-details">
              <div class="detail-item">
                <label>Port:</label>
                <span>{{ service.port }}</span>
              </div>
              <div class="detail-item">
                <label>Uptime:</label>
                <span>{{ service.uptime }}</span>
              </div>
              <div class="detail-item">
                <label>Memory:</label>
                <span>{{ service.memory }}</span>
              </div>
            </div>

            <div class="service-actions">
              <button class="action-btn start" @click="startService(service)" v-if="service.status === 'stopped'">
                <i class="fas fa-play"></i>
                Start
              </button>
              <button class="action-btn stop" @click="stopService(service)" v-if="service.status === 'running'">
                <i class="fas fa-stop"></i>
                Stop
              </button>
              <button class="action-btn restart" @click="restartService(service)" v-if="service.status === 'running'">
                <i class="fas fa-redo"></i>
                Restart
              </button>
              <button class="action-btn logs" @click="viewLogs(service)">
                <i class="fas fa-file-alt"></i>
                Logs
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Infrastructure Overview -->
    <div class="infrastructure-section">
      <div class="section-header">
        <h2>Infrastructure</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="infraFilter" @change="filterInfrastructure">
              <option value="">All Resources</option>
              <option value="server">Servers</option>
              <option value="database">Databases</option>
              <option value="storage">Storage</option>
            </select>
          </div>
          <button class="add-resource-btn" @click="showAddResourceModal = true">
            <i class="fas fa-plus"></i>
            Add Resource
          </button>
        </div>
      </div>

      <div class="infrastructure-grid">
        <div 
          v-for="resource in filteredInfrastructure" 
          :key="resource.id"
          class="infrastructure-card"
          :class="{ 'online': resource.status === 'online', 'offline': resource.status === 'offline', 'maintenance': resource.status === 'maintenance' }"
        >
          <div class="infrastructure-header">
            <div class="infrastructure-icon">
              <i :class="getInfrastructureIcon(resource.type)"></i>
            </div>
            <div class="infrastructure-status">
              <span :class="['status-badge', resource.status]">{{ resource.status }}</span>
            </div>
          </div>

          <div class="infrastructure-content">
            <h3>{{ resource.name }}</h3>
            <p>{{ resource.description }}</p>
            
            <div class="infrastructure-info">
              <span class="type">{{ resource.type }}</span>
              <span class="size">{{ resource.size }}</span>
              <span class="location">{{ resource.location }}</span>
            </div>

            <div class="infrastructure-details">
              <div class="detail-item">
                <label>IP Address:</label>
                <span>{{ resource.ip }}</span>
              </div>
              <div class="detail-item">
                <label>Created:</label>
                <span>{{ formatDate(resource.createdAt) }}</span>
              </div>
              <div class="detail-item">
                <label>Cost:</label>
                <span>{{ resource.cost }}/month</span>
              </div>
            </div>

            <div class="infrastructure-actions">
              <button class="action-btn manage" @click="manageResource(resource)">
                <i class="fas fa-cog"></i>
                Manage
              </button>
              <button class="action-btn monitor" @click="monitorResource(resource)">
                <i class="fas fa-chart-line"></i>
                Monitor
              </button>
              <button class="action-btn delete" @click="deleteResource(resource)">
                <i class="fas fa-trash"></i>
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Environment Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Environment Analytics</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="timeRange" @change="updateAnalytics">
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
            </select>
          </div>
          <button class="refresh-btn" @click="refreshAnalytics">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="analytics-grid">
        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Environment Health</h3>
            <span class="analytics-value">{{ analytics.healthScore }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="healthChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Healthy: {{ analytics.healthyEnvironments }}</span>
            <span class="detail-item">Issues: {{ analytics.issueCount }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Resource Usage</h3>
            <span class="analytics-value">{{ analytics.avgResourceUsage }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="resourceChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">CPU: {{ analytics.avgCpuUsage }}%</span>
            <span class="detail-item">Memory: {{ analytics.avgMemoryUsage }}%</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Service Performance</h3>
            <span class="analytics-value">{{ analytics.serviceUptime }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="performanceChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Running: {{ analytics.runningServices }}</span>
            <span class="detail-item">Total: {{ analytics.totalServices }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Cost Analysis</h3>
            <span class="analytics-value">${{ analytics.totalCost }}/mo</span>
          </div>
          <div class="cost-chart">
            <canvas ref="costChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Infrastructure: ${{ analytics.infraCost }}</span>
            <span class="detail-item">Services: ${{ analytics.serviceCost }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Environment Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Create Environment</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="environment-form">
            <div class="form-group">
              <label>Environment Name *</label>
              <input 
                v-model="envForm.name" 
                type="text" 
                placeholder="Enter environment name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="envForm.description" 
                placeholder="Describe this environment"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Environment Type *</label>
                <select v-model="envForm.type" required>
                  <option value="production">Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                  <option value="testing">Testing</option>
                </select>
              </div>

              <div class="form-group">
                <label>Region *</label>
                <select v-model="envForm.region" required>
                  <option value="us-east-1">US East (N. Virginia)</option>
                  <option value="us-west-2">US West (Oregon)</option>
                  <option value="eu-west-1">EU West (Ireland)</option>
                  <option value="ap-southeast-1">AP Southeast (Singapore)</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Domain/URL</label>
              <input 
                v-model="envForm.url" 
                type="text" 
                placeholder="https://app.example.com"
              />
            </div>

            <div class="form-group">
              <label>Infrastructure Template</label>
              <select v-model="envForm.template">
                <option value="basic">Basic Setup</option>
                <option value="standard">Standard Setup</option>
                <option value="enterprise">Enterprise Setup</option>
                <option value="custom">Custom Setup</option>
              </select>
            </div>

            <div class="form-group">
              <label>Services to Include</label>
              <div class="services-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="envForm.services.web"
                  />
                  <span>Web Server</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="envForm.services.database"
                  />
                  <span>Database</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="envForm.services.cache"
                  />
                  <span>Cache</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="envForm.services.storage"
                  />
                  <span>Storage</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Configuration</label>
              <div class="config-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="envForm.config.autoScaling"
                  />
                  <span>Auto-scaling enabled</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="envForm.config.monitoring"
                  />
                  <span>Monitoring enabled</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="envForm.config.backup"
                  />
                  <span>Automated backups</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="envForm.config.ssl"
                  />
                  <span>SSL certificate</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button class="btn-primary" @click="createEnvironment">
            <i class="fas fa-plus"></i>
            Create Environment
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
const typeFilter = ref('')
const serviceFilter = ref('')
const infraFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('30')
const showCreateModal = ref(false)
const showDeployModal = ref(false)
const showMonitorModal = ref(false)
const showConfigModal = ref(false)
const showAddServiceModal = ref(false)
const showAddResourceModal = ref(false)

// Chart instances
const healthChart = ref(null)
const resourceChart = ref(null)
const performanceChart = ref(null)
const costChart = ref(null)

// Environment stats
const envStats = reactive({
  totalEnvironments: 8,
  activeEnvironments: 7,
  healthyEnvironments: 6,
  issuesCount: 2,
  totalServices: 24,
  runningServices: 21,
  resourceUsage: 67
})

// Analytics
const analytics = reactive({
  healthScore: 85,
  healthyEnvironments: 6,
  issueCount: 2,
  avgResourceUsage: 67,
  avgCpuUsage: 45,
  avgMemoryUsage: 72,
  serviceUptime: 98.5,
  runningServices: 21,
  totalServices: 24,
  totalCost: 1250,
  infraCost: 890,
  serviceCost: 360
})

// Environment form
const envForm = reactive({
  name: '',
  description: '',
  type: 'development',
  region: 'us-east-1',
  url: '',
  template: 'basic',
  services: {
    web: true,
    database: true,
    cache: false,
    storage: false
  },
  config: {
    autoScaling: false,
    monitoring: true,
    backup: true,
    ssl: false
  }
})

// Mock data
const environments = ref([
  {
    id: 1,
    name: 'Production',
    description: 'Live production environment',
    type: 'production',
    status: 'healthy',
    region: 'us-east-1',
    url: 'https://app.example.com',
    version: 'v2.1.0',
    services: 8,
    health: 98,
    metrics: {
      cpu: 45,
      memory: 67,
      storage: 23
    }
  },
  {
    id: 2,
    name: 'Staging',
    description: 'Staging environment for testing',
    type: 'staging',
    status: 'healthy',
    region: 'us-east-1',
    url: 'https://staging.example.com',
    version: 'v2.1.0-beta',
    services: 6,
    health: 95,
    metrics: {
      cpu: 32,
      memory: 45,
      storage: 18
    }
  },
  {
    id: 3,
    name: 'Development',
    description: 'Development environment',
    type: 'development',
    status: 'unhealthy',
    region: 'us-west-2',
    url: 'https://dev.example.com',
    version: 'v2.0.9',
    services: 4,
    health: 45,
    metrics: {
      cpu: 78,
      memory: 89,
      storage: 34
    }
  },
  {
    id: 4,
    name: 'Testing',
    description: 'Testing environment',
    type: 'testing',
    status: 'maintenance',
    region: 'us-west-2',
    url: 'https://test.example.com',
    version: 'v2.0.8',
    services: 3,
    health: 0,
    metrics: {
      cpu: 0,
      memory: 0,
      storage: 12
    }
  }
])

const services = ref([
  {
    id: 1,
    name: 'Web Server',
    description: 'Main web application server',
    type: 'web',
    status: 'running',
    environment: 'Production',
    version: 'v2.1.0',
    port: 8080,
    uptime: '15 days',
    memory: '512MB'
  },
  {
    id: 2,
    name: 'Database',
    description: 'PostgreSQL database server',
    type: 'database',
    status: 'running',
    environment: 'Production',
    version: 'v14.2',
    port: 5432,
    uptime: '30 days',
    memory: '2GB'
  },
  {
    id: 3,
    name: 'Cache Server',
    description: 'Redis cache server',
    type: 'cache',
    status: 'stopped',
    environment: 'Staging',
    version: 'v6.2',
    port: 6379,
    uptime: '0 days',
    memory: '256MB'
  },
  {
    id: 4,
    name: 'API Gateway',
    description: 'API gateway service',
    type: 'api',
    status: 'error',
    environment: 'Development',
    version: 'v1.5',
    port: 3000,
    uptime: '2 days',
    memory: '128MB'
  }
])

const infrastructure = ref([
  {
    id: 1,
    name: 'Web Server 1',
    description: 'Primary web server',
    type: 'server',
    status: 'online',
    size: 't3.medium',
    location: 'us-east-1',
    ip: '52.23.45.67',
    createdAt: '2024-01-15T10:30:00Z',
    cost: 45
  },
  {
    id: 2,
    name: 'Database Server',
    description: 'Primary database server',
    type: 'database',
    status: 'online',
    size: 'db.t3.large',
    location: 'us-east-1',
    ip: '52.23.45.68',
    createdAt: '2024-01-10T15:45:00Z',
    cost: 120
  },
  {
    id: 3,
    name: 'Storage Volume',
    description: 'Main storage volume',
    type: 'storage',
    status: 'online',
    size: '500GB',
    location: 'us-east-1',
    ip: 'N/A',
    createdAt: '2024-01-05T09:20:00Z',
    cost: 25
  }
])

// Computed properties
const filteredEnvironments = computed(() => {
  let filtered = environments.value

  if (statusFilter.value) {
    filtered = filtered.filter(env => env.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(env => env.type === typeFilter.value)
  }

  return filtered.sort((a, b) => a.name.localeCompare(b.name))
})

const filteredServices = computed(() => {
  let filtered = services.value

  if (serviceFilter.value) {
    filtered = filtered.filter(service => service.status === serviceFilter.value)
  }

  return filtered.sort((a, b) => a.name.localeCompare(b.name))
})

const filteredInfrastructure = computed(() => {
  let filtered = infrastructure.value

  if (infraFilter.value) {
    filtered = filtered.filter(resource => resource.type === infraFilter.value)
  }

  return filtered.sort((a, b) => a.name.localeCompare(b.name))
})

// Methods
const loadEnvironmentData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/environments')
    // if (response.success) {
    //   environments.value = response.environments || []
    //   services.value = response.services || []
    //   infrastructure.value = response.infrastructure || []
    //   Object.assign(envStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading environment data:', error)
    showError('Failed to load environment data')
  } finally {
    loading.value = false
  }
}

const filterEnvironments = () => {
  // This is reactive, no additional action needed
}

const filterServices = () => {
  // This is reactive, no additional action needed
}

const filterInfrastructure = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || typeFilter.value) {
    return 'No environments match your filter criteria'
  }
  return 'No environments found'
}

const getEnvironmentIcon = (type) => {
  const icons = {
    'production': 'fas fa-globe',
    'staging': 'fas fa-flask',
    'development': 'fas fa-code',
    'testing': 'fas fa-vial'
  }
  return icons[type] || 'fas fa-server'
}

const getServiceIcon = (type) => {
  const icons = {
    'web': 'fas fa-globe',
    'database': 'fas fa-database',
    'cache': 'fas fa-memory',
    'api': 'fas fa-plug'
  }
  return icons[type] || 'fas fa-cube'
}

const getInfrastructureIcon = (type) => {
  const icons = {
    'server': 'fas fa-server',
    'database': 'fas fa-database',
    'storage': 'fas fa-hdd'
  }
  return icons[type] || 'fas fa-cube'
}

const getResourceClass = (usage) => {
  if (usage < 50) return 'good'
  if (usage < 80) return 'warning'
  return 'critical'
}

const getResourceStatus = (usage) => {
  if (usage < 50) return 'Good'
  if (usage < 80) return 'Warning'
  return 'Critical'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const viewEnvironment = (environment) => {
  // Open environment details modal or navigate to detailed view
  showSuccess(`Viewing environment details: ${environment.name}`)
}

const deployToEnvironment = (environment) => {
  // Open deploy modal or navigate to deployment page
  showSuccess(`Deploying to environment: ${environment.name}`)
}

const checkHealth = async (environment) => {
  try {
    // const response = await apiPost(`/environments/${environment.id}/health-check`)
    // if (response.success) {
    //   environment.health = response.health
    //   environment.status = response.status
    //   showSuccess('Health check completed')
    // }
    
    // For demo, simulate health check
    environment.health = Math.floor(Math.random() * 100)
    environment.status = environment.health > 80 ? 'healthy' : 'unhealthy'
    showSuccess('Health check completed')
  } catch (error) {
    console.error('Error checking environment health:', error)
    showError('Failed to check environment health')
  }
}

const configureEnvironment = (environment) => {
  // Open configuration modal
  showSuccess(`Configuring environment: ${environment.name}`)
}

const startService = async (service) => {
  try {
    // const response = await apiPost(`/services/${service.id}/start`)
    // if (response.success) {
    //   service.status = 'running'
    //   showSuccess('Service started successfully')
    // }
    
    // For demo, simulate start
    service.status = 'running'
    showSuccess('Service started successfully')
  } catch (error) {
    console.error('Error starting service:', error)
    showError('Failed to start service')
  }
}

const stopService = async (service) => {
  const confirmed = await showConfirm(`Are you sure you want to stop service "${service.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/services/${service.id}/stop`)
    // if (response.success) {
    //   service.status = 'stopped'
    //   showSuccess('Service stopped successfully')
    // }
    
    // For demo, simulate stop
    service.status = 'stopped'
    showSuccess('Service stopped successfully')
  } catch (error) {
    console.error('Error stopping service:', error)
    showError('Failed to stop service')
  }
}

const restartService = async (service) => {
  try {
    // const response = await apiPost(`/services/${service.id}/restart`)
    // if (response.success) {
    //   showSuccess('Service restarted successfully')
    // }
    
    // For demo, simulate restart
    showSuccess('Service restarted successfully')
  } catch (error) {
    console.error('Error restarting service:', error)
    showError('Failed to restart service')
  }
}

const viewLogs = (service) => {
  // Open logs modal or navigate to logs page
  showSuccess(`Viewing logs for service: ${service.name}`)
}

const manageResource = (resource) => {
  // Open resource management modal
  showSuccess(`Managing resource: ${resource.name}`)
}

const monitorResource = (resource) => {
  // Open monitoring dashboard
  showSuccess(`Monitoring resource: ${resource.name}`)
}

const deleteResource = async (resource) => {
  const confirmed = await showConfirm(`Are you sure you want to delete resource "${resource.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/infrastructure/${resource.id}`)
    // if (response.success) {
    //   const index = infrastructure.value.findIndex(r => r.id === resource.id)
    //   if (index > -1) {
    //     infrastructure.value.splice(index, 1)
    //     showSuccess('Resource deleted successfully')
    //   }
    // }
    
    // For demo, simulate deletion
    const index = infrastructure.value.findIndex(r => r.id === resource.id)
    if (index > -1) {
      infrastructure.value.splice(index, 1)
      showSuccess('Resource deleted successfully')
    }
  } catch (error) {
    console.error('Error deleting resource:', error)
    showError('Failed to delete resource')
  }
}

const createEnvironment = async () => {
  if (!envForm.name || !envForm.type || !envForm.region) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/environments', envForm)
    // if (response.success) {
    //   environments.value.unshift(response.environment)
    //   showSuccess('Environment created successfully')
    //   closeCreateModal()
    //   resetEnvironmentForm()
    // }
    
    // For demo, simulate creation
    const newEnvironment = {
      id: Date.now(),
      ...envForm,
      status: 'healthy',
      version: 'v1.0.0',
      services: Object.values(envForm.services).filter(Boolean).length,
      health: 100,
      metrics: {
        cpu: 0,
        memory: 0,
        storage: 0
      }
    }
    
    environments.value.unshift(newEnvironment)
    showSuccess('Environment created successfully')
    closeCreateModal()
    resetEnvironmentForm()
  } catch (error) {
    console.error('Error creating environment:', error)
    showError('Failed to create environment')
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetEnvironmentForm()
}

const resetEnvironmentForm = () => {
  Object.assign(envForm, {
    name: '',
    description: '',
    type: 'development',
    region: 'us-east-1',
    url: '',
    template: 'basic',
    services: {
      web: true,
      database: true,
      cache: false,
      storage: false
    },
    config: {
      autoScaling: false,
      monitoring: true,
      backup: true,
      ssl: false
    }
  })
}

const updateAnalytics = async () => {
  try {
    // const response = await apiGet('/environments/analytics', { timeRange: timeRange.value })
    // if (response.success) {
    //   Object.assign(analytics, response.analytics)
    //   updateCharts()
    // }
    
    // For demo, simulate update
    updateCharts()
  } catch (error) {
    console.error('Error updating analytics:', error)
    showError('Failed to update analytics')
  }
}

const refreshAnalytics = async () => {
  try {
    // const response = await apiGet('/environments/analytics/refresh')
    // if (response.success) {
    //   Object.assign(analytics, response.analytics)
    //   updateCharts()
    // }
    
    // For demo, simulate refresh
    updateCharts()
    showSuccess('Analytics refreshed successfully')
  } catch (error) {
    console.error('Error refreshing analytics:', error)
    showError('Failed to refresh analytics')
  }
}

const initCharts = () => {
  // Initialize Health chart
  if (healthChart.value) healthChart.value.destroy()
  healthChart.value = new Chart(healthChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Healthy', 'Issues'],
      datasets: [{
        data: [analytics.healthyEnvironments, analytics.issueCount],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      }
    }
  })

  // Initialize Resource chart
  if (resourceChart.value) resourceChart.value.destroy()
  resourceChart.value = new Chart(resourceChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 7 }, (_, i) => `Day ${i + 1}`),
      datasets: [{
        label: 'CPU',
        data: Array.from({ length: 7 }, () => Math.floor(Math.random() * 100)),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      }, {
        label: 'Memory',
        data: Array.from({ length: 7 }, () => Math.floor(Math.random() * 100)),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true }
      },
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  })

  // Initialize Performance chart
  if (performanceChart.value) performanceChart.value.destroy()
  performanceChart.value = new Chart(performanceChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Service Uptime %',
        data: [98, 99, 97, 98.5, 99, 98, 99.5],
        backgroundColor: 'rgba(245, 158, 11, 0.8)'
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

  // Initialize Cost chart
  if (costChart.value) costChart.value.destroy()
  costChart.value = new Chart(costChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Infrastructure', 'Services'],
      datasets: [{
        data: [analytics.infraCost, analytics.serviceCost],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      }
    }
  })
}

const updateCharts = () => {
  // Update charts with new data
  if (healthChart.value) {
    healthChart.value.data.datasets[0].data = [analytics.healthyEnvironments, analytics.issueCount]
    healthChart.value.update('none')
  }

  if (resourceChart.value) {
    resourceChart.value.data.datasets[0].data = Array.from({ length: 7 }, () => Math.floor(Math.random() * 100))
    resourceChart.value.data.datasets[1].data = Array.from({ length: 7 }, () => Math.floor(Math.random() * 100))
    resourceChart.value.update('none')
  }

  if (performanceChart.value) {
    performanceChart.value.data.datasets[0].data = [98, 99, 97, 98.5, 99, 98, 99.5]
    performanceChart.value.update('none')
  }

  if (costChart.value) {
    costChart.value.data.datasets[0].data = [analytics.infraCost, analytics.serviceCost]
    costChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadEnvironmentData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (healthChart.value) healthChart.value.destroy()
  if (resourceChart.value) resourceChart.value.destroy()
  if (performanceChart.value) performanceChart.value.destroy()
  if (costChart.value) costChart.value.destroy()
})
</script>

<style scoped>
.environments {
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

.card-icon.healthy {
  background: var(--success-color);
}

.card-icon.services {
  background: var(--info-color);
}

.card-icon.resources {
  background: var(--warning-color);
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

.env-count,
.health-count,
.service-count,
.resource-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.env-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.health-count {
  color: var(--text-secondary);
}

.service-count {
  color: var(--text-secondary);
}

.resource-status.good {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.resource-status.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.resource-status.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
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
.deploy-btn,
.monitor-btn,
.config-btn {
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
.deploy-btn:hover,
.monitor-btn:hover,
.config-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.deploy-btn {
  background: var(--success-color);
}

.deploy-btn:hover {
  background: var(--success-hover);
}

.monitor-btn {
  background: var(--info-color);
}

.monitor-btn:hover {
  background: var(--info-hover);
}

.config-btn {
  background: var(--warning-color);
}

.config-btn:hover {
  background: var(--warning-hover);
}

.environments-section,
.services-section,
.infrastructure-section,
.analytics-section {
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

.add-service-btn,
.add-resource-btn {
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

.add-service-btn:hover,
.add-resource-btn:hover {
  background: var(--primary-hover);
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

.environments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.environment-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.environment-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.environment-card.unhealthy {
  border-color: var(--danger-color);
}

.environment-card.maintenance {
  border-color: var(--warning-color);
}

.environment-card.offline {
  border-color: var(--text-tertiary);
  opacity: 0.7;
}

.environment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.environment-icon {
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

.status-badge.healthy {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.unhealthy {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.maintenance {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.offline {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.environment-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.environment-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.environment-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.region,
.version {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.environment-details {
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

.environment-metrics {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.metric-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
  min-width: 60px;
}

.metric-bar {
  flex: 1;
  height: 8px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.metric-value {
  font-size: 0.8rem;
  color: var(--text-primary);
  font-weight: 600;
  min-width: 35px;
  text-align: right;
}

.environment-actions {
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

.action-btn.view:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.deploy:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.health:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.config:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.environments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.environment-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.environment-list-card:hover {
  background: var(--glass-bg-hover);
}

.environment-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.environment-list-info {
  flex: 1;
}

.environment-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.environment-list-actions {
  display: flex;
  gap: 0.5rem;
}

.services-grid,
.infrastructure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.service-card,
.infrastructure-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.service-card:hover,
.infrastructure-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.service-card.running {
  border-color: var(--success-color);
}

.service-card.stopped {
  border-color: var(--warning-color);
}

.service-card.error {
  border-color: var(--danger-color);
}

.infrastructure-card.online {
  border-color: var(--success-color);
}

.infrastructure-card.offline {
  border-color: var(--danger-color);
}

.infrastructure-card.maintenance {
  border-color: var(--warning-color);
}

.service-header,
.infrastructure-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.service-icon,
.infrastructure-icon {
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

.service-status,
.infrastructure-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.service-status.running,
.infrastructure-status.online {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.service-status.stopped {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.service-status.error,
.infrastructure-status.offline {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.infrastructure-status.maintenance {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.service-content,
.infrastructure-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.service-content,
.infrastructure-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.service-info,
.infrastructure-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.service-actions,
.infrastructure-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn.start:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.stop:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.restart:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.logs:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.manage:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.monitor:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.analytics-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.analytics-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.analytics-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.analytics-chart,
.cost-chart {
  height: 150px;
  margin-bottom: 1rem;
}

.analytics-details {
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

.environment-form {
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

.services-container,
.config-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
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
  .environments {
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
  
  .environments-grid {
    grid-template-columns: 1fr;
  }
  
  .environment-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .environment-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .services-grid,
  .infrastructure-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .services-container,
  .config-container {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
