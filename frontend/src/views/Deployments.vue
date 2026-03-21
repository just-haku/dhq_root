<template>
  <div class="deployments">
    <div class="page-header">
      <h1>Deployment Management</h1>
      <p>Manage application deployments, environments, and release pipelines</p>
    </div>

    <!-- Deployment Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-rocket"></i>
          </div>
          <div class="card-content">
            <h3>{{ deploymentStats.totalDeployments }}</h3>
            <p>Total Deployments</p>
            <span class="deployment-count">{{ deploymentStats.successfulDeployments }} successful</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon active">
            <i class="fas fa-play-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ deploymentStats.activeDeployments }}</h3>
            <p>Active Deployments</p>
            <span class="active-count">{{ deploymentStats.runningDeployments }} running</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon environments">
            <i class="fas fa-server"></i>
          </div>
          <div class="card-content">
            <h3>{{ deploymentStats.environments }}</h3>
            <p>Environments</p>
            <span class="env-count">{{ deploymentStats.healthyEnvironments }} healthy</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon health">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <h3>{{ deploymentStats.healthScore }}%</h3>
            <p>Health Score</p>
            <span class="health-status" :class="getHealthClass(deploymentStats.healthScore)">
              {{ getHealthStatus(deploymentStats.healthScore) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="deploy-btn" @click="showDeployModal = true">
          <i class="fas fa-rocket"></i>
          New Deployment
        </button>
        <button class="rollback-btn" @click="showRollbackModal = true">
          <i class="fas fa-undo"></i>
          Rollback
        </button>
        <button class="pipeline-btn" @click="showPipelineModal = true">
          <i class="fas fa-project-diagram"></i>
          Pipeline
        </button>
        <button class="monitor-btn" @click="showMonitorModal = true">
          <i class="fas fa-chart-line"></i>
          Monitor
        </button>
      </div>
    </div>

    <!-- Deployment History -->
    <div class="deployments-section">
      <div class="section-header">
        <h2>Deployment History</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterDeployments">
              <option value="">All Status</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="running">Running</option>
              <option value="pending">Pending</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="environmentFilter" @change="filterDeployments">
              <option value="">All Environments</option>
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
        <p>Loading deployments...</p>
      </div>

      <div v-else-if="filteredDeployments.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-rocket"></i>
        </div>
        <h3>No deployments found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="deploy-first-btn" @click="showDeployModal = true">
          <i class="fas fa-rocket"></i>
          Create Your First Deployment
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="deployments-grid">
          <div 
            v-for="deployment in filteredDeployments" 
            :key="deployment.id"
            class="deployment-card"
            :class="{ 'running': deployment.status === 'running', 'failed': deployment.status === 'failed', 'cancelled': deployment.status === 'cancelled' }"
          >
            <div class="deployment-header">
              <div class="deployment-icon">
                <i :class="getDeploymentIcon(deployment.environment)"></i>
              </div>
              <div class="deployment-status">
                <span :class="['status-badge', deployment.status]">{{ deployment.status }}</span>
              </div>
            </div>

            <div class="deployment-content">
              <h3>{{ deployment.name }}</h3>
              <p>{{ deployment.description }}</p>
              
              <div class="deployment-info">
                <span class="environment">{{ deployment.environment }}</span>
                <span class="version">{{ deployment.version }}</span>
                <span class="duration">{{ deployment.duration }}</span>
              </div>

              <div class="deployment-details">
                <div class="detail-item">
                  <label>Started:</label>
                  <span>{{ formatDateTime(deployment.startedAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Branch:</label>
                  <span>{{ deployment.branch }}</span>
                </div>
                <div class="detail-item">
                  <label>Commit:</label>
                  <span class="commit">{{ deployment.commit }}</span>
                </div>
              </div>

              <div class="deployment-progress" v-if="deployment.status === 'running'">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: deployment.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ deployment.progress }}%</span>
              </div>

              <div class="deployment-actions">
                <button class="action-btn view" @click="viewDeployment(deployment)">
                  <i class="fas fa-eye"></i>
                  View
                </button>
                <button class="action-btn cancel" @click="cancelDeployment(deployment)" v-if="['running', 'pending'].includes(deployment.status)">
                  <i class="fas fa-times"></i>
                  Cancel
                </button>
                <button class="action-btn retry" @click="retryDeployment(deployment)" v-if="deployment.status === 'failed'">
                  <i class="fas fa-redo"></i>
                  Retry
                </button>
                <button class="action-btn rollback" @click="rollbackDeployment(deployment)" v-if="deployment.status === 'success'">
                  <i class="fas fa-undo"></i>
                  Rollback
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="deployments-list">
          <div 
            v-for="deployment in filteredDeployments" 
            :key="deployment.id"
            class="deployment-list-card"
            :class="{ 'running': deployment.status === 'running', 'failed': deployment.status === 'failed', 'cancelled': deployment.status === 'cancelled' }"
          >
            <div class="deployment-list-header">
              <div class="deployment-list-info">
                <div class="deployment-icon">
                  <i :class="getDeploymentIcon(deployment.environment)"></i>
                </div>
                <div class="deployment-details">
                  <h3>{{ deployment.name }}</h3>
                  <p>{{ deployment.description }}</p>
                  <div class="deployment-info">
                    <span class="environment">{{ deployment.environment }}</span>
                    <span class="version">{{ deployment.version }}</span>
                    <span :class="['status-badge', deployment.status]">{{ deployment.status }}</span>
                    <span class="duration">{{ deployment.duration }}</span>
                  </div>
                </div>
              </div>
              <div class="deployment-list-stats">
                <div class="detail-item">
                  <label>Started:</label>
                  <span>{{ formatDateTime(deployment.startedAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Branch:</label>
                  <span>{{ deployment.branch }}</span>
                </div>
                <div class="detail-item">
                  <label>Commit:</label>
                  <span class="commit">{{ deployment.commit }}</span>
                </div>
              </div>
              <div class="deployment-list-actions">
                <button class="action-btn view" @click="viewDeployment(deployment)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn cancel" @click="cancelDeployment(deployment)" v-if="['running', 'pending'].includes(deployment.status)">
                  <i class="fas fa-times"></i>
                </button>
                <button class="action-btn retry" @click="retryDeployment(deployment)" v-if="deployment.status === 'failed'">
                  <i class="fas fa-redo"></i>
                </button>
                <button class="action-btn rollback" @click="rollbackDeployment(deployment)" v-if="deployment.status === 'success'">
                  <i class="fas fa-undo"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Environments -->
    <div class="environments-section">
      <div class="section-header">
        <h2>Environments</h2>
        <div class="header-actions">
          <button class="add-env-btn" @click="showAddEnvModal = true">
            <i class="fas fa-plus"></i>
            Add Environment
          </button>
        </div>
      </div>

      <div class="environments-grid">
        <div 
          v-for="environment in environments" 
          :key="environment.id"
          class="environment-card"
          :class="{ 'healthy': environment.status === 'healthy', 'unhealthy': environment.status === 'unhealthy', 'maintenance': environment.status === 'maintenance' }"
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
              <span class="url">{{ environment.url }}</span>
              <span class="region">{{ environment.region }}</span>
            </div>

            <div class="environment-details">
              <div class="detail-item">
                <label>Version:</label>
                <span>{{ environment.currentVersion }}</span>
              </div>
              <div class="detail-item">
                <label>Last Deploy:</label>
                <span>{{ formatDateTime(environment.lastDeploy) }}</span>
              </div>
              <div class="detail-item">
                <label>Health:</label>
                <span>{{ environment.health }}%</span>
              </div>
            </div>

            <div class="environment-actions">
              <button class="action-btn deploy" @click="deployToEnvironment(environment)">
                <i class="fas fa-rocket"></i>
                Deploy
              </button>
              <button class="action-btn health" @click="checkEnvironmentHealth(environment)">
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
    </div>

    <!-- Deployment Pipeline -->
    <div class="pipeline-section">
      <div class="section-header">
        <h2>Deployment Pipeline</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="pipelineFilter" @change="filterPipeline">
              <option value="">All Pipelines</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <button class="create-pipeline-btn" @click="showCreatePipelineModal = true">
            <i class="fas fa-plus"></i>
            Create Pipeline
          </button>
        </div>
      </div>

      <div class="pipeline-flow">
        <div 
          v-for="pipeline in filteredPipelines" 
          :key="pipeline.id"
          class="pipeline-card"
          :class="{ 'active': pipeline.status === 'active', 'failed': pipeline.status === 'failed' }"
        >
          <div class="pipeline-header">
            <div class="pipeline-icon">
              <i class="fas fa-project-diagram"></i>
            </div>
            <div class="pipeline-info">
              <h3>{{ pipeline.name }}</h3>
              <span class="pipeline-status">{{ pipeline.status }}</span>
            </div>
          </div>

          <div class="pipeline-stages">
            <div 
              v-for="(stage, index) in pipeline.stages" 
              :key="index"
              class="pipeline-stage"
              :class="{ 'completed': stage.status === 'completed', 'running': stage.status === 'running', 'failed': stage.status === 'failed', 'pending': stage.status === 'pending' }"
            >
              <div class="stage-icon">
                <i :class="getStageIcon(stage.type)"></i>
              </div>
              <div class="stage-info">
                <span class="stage-name">{{ stage.name }}</span>
                <span class="stage-status">{{ stage.status }}</span>
              </div>
            </div>
          </div>

          <div class="pipeline-actions">
            <button class="action-btn run" @click="runPipeline(pipeline)">
              <i class="fas fa-play"></i>
              Run
            </button>
            <button class="action-btn edit" @click="editPipeline(pipeline)">
              <i class="fas fa-edit"></i>
              Edit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Deployment Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Deployment Analytics</h2>
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
            <h3>Deployment Success Rate</h3>
            <span class="analytics-value">{{ analytics.successRate }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="successChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Successful: {{ analytics.successfulDeployments }}</span>
            <span class="detail-item">Failed: {{ analytics.failedDeployments }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Deployment Frequency</h3>
            <span class="analytics-value">{{ analytics.deploymentsPerWeek }}/week</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="frequencyChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">This week: {{ analytics.weeklyDeployments }}</span>
            <span class="detail-item">This month: {{ analytics.monthlyDeployments }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Average Deployment Time</h3>
            <span class="analytics-value">{{ analytics.avgDeploymentTime }}</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="timeChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Fastest: {{ analytics.fastestDeployment }}</span>
            <span class="detail-item">Slowest: {{ analytics.slowestDeployment }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Environment Distribution</h3>
            <span class="analytics-value">{{ analytics.environments.length }}</span>
          </div>
          <div class="env-distribution-chart">
            <canvas ref="envChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Production: {{ analytics.environments.production }}</span>
            <span class="detail-item">Staging: {{ analytics.environments.staging }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Deploy Modal -->
    <div v-if="showDeployModal" class="modal-overlay" @click="closeDeployModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>New Deployment</h2>
          <button class="close-btn" @click="closeDeployModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="deploy-form">
            <div class="form-group">
              <label>Deployment Name *</label>
              <input 
                v-model="deployForm.name" 
                type="text" 
                placeholder="Enter deployment name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="deployForm.description" 
                placeholder="Describe this deployment"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Environment *</label>
                <select v-model="deployForm.environment" required>
                  <option value="">Select environment</option>
                  <option 
                    v-for="env in environments" 
                    :key="env.id"
                    :value="env.id"
                  >
                    {{ env.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Branch *</label>
                <select v-model="deployForm.branch" required>
                  <option value="main">main</option>
                  <option value="develop">develop</option>
                  <option value="feature/test">feature/test</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Commit SHA *</label>
              <input 
                v-model="deployForm.commit" 
                type="text" 
                placeholder="Enter commit SHA"
                required
              />
            </div>

            <div class="form-group">
              <label>Version</label>
              <input 
                v-model="deployForm.version" 
                type="text" 
                placeholder="v2.1.0"
              />
            </div>

            <div class="form-group">
              <label>Deployment Strategy</label>
              <select v-model="deployForm.strategy">
                <option value="rolling">Rolling Update</option>
                <option value="blue-green">Blue-Green</option>
                <option value="canary">Canary</option>
                <option value="recreate">Recreate</option>
              </select>
            </div>

            <div class="form-group">
              <label>Build Configuration</label>
              <div class="build-config">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="deployForm.buildConfig.runTests"
                  />
                  <span>Run tests before deployment</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="deployForm.buildConfig.runLinting"
                  />
                  <span>Run code linting</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="deployForm.buildConfig.buildAssets"
                  />
                  <span>Build assets</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="deployForm.buildConfig.optimize"
                  />
                  <span>Optimize for production</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Notifications</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="deployForm.notifyOnStart"
                  />
                  <span>Notify on start</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="deployForm.notifyOnComplete"
                  />
                  <span>Notify on completion</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="deployForm.notifyOnFailure"
                  />
                  <span>Notify on failure</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeDeployModal">Cancel</button>
          <button class="btn-primary" @click="createDeployment">
            <i class="fas fa-rocket"></i>
            Deploy
          </button>
        </div>
      </div>
    </div>

    <!-- Rollback Modal -->
    <div v-if="showRollbackModal" class="modal-overlay" @click="closeRollbackModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Rollback Deployment</h2>
          <button class="close-btn" @click="closeRollbackModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="rollback-form">
            <div class="form-group">
              <label>Environment *</label>
              <select v-model="rollbackForm.environmentId" required>
                <option value="">Select environment</option>
                <option 
                  v-for="env in environments" 
                  :key="env.id"
                  :value="env.id"
                >
                  {{ env.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Target Version *</label>
              <select v-model="rollbackForm.targetVersion" required>
                <option value="">Select version to rollback to</option>
                <option 
                  v-for="version in availableVersions" 
                  :key="version.sha"
                  :value="version.sha"
                >
                  {{ version.version }} - {{ formatDateTime(version.deployedAt) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Rollback Strategy</label>
              <select v-model="rollbackForm.strategy">
                <option value="immediate">Immediate</option>
                <option value="graceful">Graceful</option>
                <option value="manual">Manual</option>
              </select>
            </div>

            <div class="form-group">
              <label>Backup Current Version</label>
              <select v-model="rollbackForm.backup">
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>

            <div class="form-group">
              <label>Confirmation Required</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="rollbackForm.confirmRequired"
                  />
                  <span>Require confirmation before rollback</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeRollbackModal">Cancel</button>
          <button class="btn-primary danger" @click="executeRollback">
            <i class="fas fa-undo"></i>
            Execute Rollback
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
const pipelineFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('30')
const showDeployModal = ref(false)
const showRollbackModal = ref(false)
const showPipelineModal = ref(false)
const showMonitorModal = ref(false)
const showAddEnvModal = ref(false)
const showCreatePipelineModal = ref(false)

// Chart instances
const successChart = ref(null)
const frequencyChart = ref(null)
const timeChart = ref(null)
const envChart = ref(null)

// Deployment stats
const deploymentStats = reactive({
  totalDeployments: 234,
  successfulDeployments: 198,
  activeDeployments: 8,
  runningDeployments: 3,
  environments: 4,
  healthyEnvironments: 3,
  healthScore: 92
})

// Analytics
const analytics = reactive({
  successRate: 85,
  successfulDeployments: 198,
  failedDeployments: 36,
  deploymentsPerWeek: 4.2,
  weeklyDeployments: 29,
  monthlyDeployments: 126,
  avgDeploymentTime: '8 min 30 sec',
  fastestDeployment: '2 min 15 sec',
  slowestDeployment: '25 min 45 sec',
  environments: { production: 89, staging: 67, development: 45, testing: 33 }
})

// Deploy form
const deployForm = reactive({
  name: '',
  description: '',
  environment: '',
  branch: 'main',
  commit: '',
  version: '',
  strategy: 'rolling',
  buildConfig: {
    runTests: true,
    runLinting: true,
    buildAssets: true,
    optimize: true
  },
  notifyOnStart: true,
  notifyOnComplete: true,
  notifyOnFailure: true
})

// Rollback form
const rollbackForm = reactive({
  environmentId: '',
  targetVersion: '',
  strategy: 'immediate',
  backup: 'yes',
  confirmRequired: true
})

// Mock data
const deployments = ref([
  {
    id: 1,
    name: 'Production Deploy v2.1.0',
    description: 'Deploy latest version to production',
    status: 'success',
    environment: 'production',
    version: 'v2.1.0',
    duration: '8 min 30 sec',
    startedAt: '2024-01-21T10:30:00Z',
    branch: 'main',
    commit: 'abc123def456',
    progress: 100
  },
  {
    id: 2,
    name: 'Staging Deploy v2.1.0-beta',
    description: 'Deploy beta version to staging',
    status: 'running',
    environment: 'staging',
    version: 'v2.1.0-beta',
    duration: 'In progress',
    startedAt: '2024-01-21T11:00:00Z',
    branch: 'develop',
    commit: 'def456ghi789',
    progress: 67
  },
  {
    id: 3,
    name: 'Development Deploy',
    description: 'Deploy feature branch to development',
    status: 'failed',
    environment: 'development',
    version: 'v2.0.9',
    duration: 'Failed',
    startedAt: '2024-01-21T09:15:00Z',
    branch: 'feature/test',
    commit: 'ghi789jkl012',
    progress: 0
  },
  {
    id: 4,
    name: 'Testing Deploy',
    description: 'Deploy to testing environment',
    status: 'pending',
    environment: 'testing',
    version: 'v2.1.0-alpha',
    duration: 'Pending',
    startedAt: '2024-01-21T23:45:00Z',
    branch: 'main',
    commit: 'jkl012mno345',
    progress: 0
  }
])

const environments = ref([
  {
    id: 1,
    name: 'Production',
    description: 'Live production environment',
    type: 'production',
    status: 'healthy',
    url: 'https://app.example.com',
    region: 'us-east-1',
    currentVersion: 'v2.1.0',
    lastDeploy: '2024-01-21T10:30:00Z',
    health: 98
  },
  {
    id: 2,
    name: 'Staging',
    description: 'Staging environment for testing',
    type: 'staging',
    status: 'healthy',
    url: 'https://staging.example.com',
    region: 'us-east-1',
    currentVersion: 'v2.1.0-beta',
    lastDeploy: '2024-01-21T11:00:00Z',
    health: 95
  },
  {
    id: 3,
    name: 'Development',
    description: 'Development environment',
    type: 'development',
    status: 'unhealthy',
    url: 'https://dev.example.com',
    region: 'us-west-2',
    currentVersion: 'v2.0.9',
    lastDeploy: '2024-01-21T09:15:00Z',
    health: 45
  },
  {
    id: 4,
    name: 'Testing',
    description: 'Testing environment',
    type: 'testing',
    status: 'maintenance',
    url: 'https://test.example.com',
    region: 'us-west-2',
    currentVersion: 'v2.0.8',
    lastDeploy: '2024-01-20T15:30:00Z',
    health: 0
  }
])

const pipelines = ref([
  {
    id: 1,
    name: 'Production Pipeline',
    status: 'active',
    stages: [
      { name: 'Build', type: 'build', status: 'completed' },
      { name: 'Test', type: 'test', status: 'completed' },
      { name: 'Deploy', type: 'deploy', status: 'running' },
      { name: 'Verify', type: 'verify', status: 'pending' }
    ]
  },
  {
    id: 2,
    name: 'Staging Pipeline',
    status: 'active',
    stages: [
      { name: 'Build', type: 'build', status: 'completed' },
      { name: 'Test', type: 'test', status: 'completed' },
      { name: 'Deploy', type: 'deploy', status: 'completed' },
      { name: 'Verify', type: 'verify', status: 'completed' }
    ]
  },
  {
    id: 3,
    name: 'Development Pipeline',
    status: 'failed',
    stages: [
      { name: 'Build', type: 'build', status: 'failed' },
      { name: 'Test', type: 'test', status: 'pending' },
      { name: 'Deploy', type: 'deploy', status: 'pending' },
      { name: 'Verify', type: 'verify', status: 'pending' }
    ]
  }
])

const availableVersions = ref([
  { version: 'v2.0.9', sha: 'ghi789jkl012', deployedAt: '2024-01-21T09:15:00Z' },
  { version: 'v2.0.8', sha: 'mno345pqr678', deployedAt: '2024-01-20T15:30:00Z' },
  { version: 'v2.0.7', sha: 'stu678vwx901', deployedAt: '2024-01-19T12:45:00Z' }
])

// Computed properties
const filteredDeployments = computed(() => {
  let filtered = deployments.value

  if (statusFilter.value) {
    filtered = filtered.filter(deployment => deployment.status === statusFilter.value)
  }

  if (environmentFilter.value) {
    filtered = filtered.filter(deployment => deployment.environment === environmentFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.startedAt) - new Date(a.startedAt))
})

const filteredPipelines = computed(() => {
  let filtered = pipelines.value

  if (pipelineFilter.value) {
    filtered = filtered.filter(pipeline => pipeline.status === pipelineFilter.value)
  }

  return filtered
})

// Methods
const loadDeploymentData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/deployments')
    // if (response.success) {
    //   deployments.value = response.deployments || []
    //   environments.value = response.environments || []
    //   pipelines.value = response.pipelines || []
    //   Object.assign(deploymentStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading deployment data:', error)
    showError('Failed to load deployment data')
  } finally {
    loading.value = false
  }
}

const filterDeployments = () => {
  // This is reactive, no additional action needed
}

const filterPipeline = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || environmentFilter.value) {
    return 'No deployments match your filter criteria'
  }
  return 'No deployments found'
}

const getDeploymentIcon = (environment) => {
  const icons = {
    'production': 'fas fa-globe',
    'staging': 'fas fa-flask',
    'development': 'fas fa-code',
    'testing': 'fas fa-vial'
  }
  return icons[environment] || 'fas fa-server'
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

const getStageIcon = (type) => {
  const icons = {
    'build': 'fas fa-hammer',
    'test': 'fas fa-check-circle',
    'deploy': 'fas fa-rocket',
    'verify': 'fas fa-shield-alt'
  }
  return icons[type] || 'fas fa-cog'
}

const getHealthClass = (score) => {
  if (score >= 95) return 'excellent'
  if (score >= 90) return 'good'
  if (score >= 80) return 'fair'
  return 'poor'
}

const getHealthStatus = (score) => {
  if (score >= 95) return 'Excellent'
  if (score >= 90) return 'Good'
  if (score >= 80) return 'Fair'
  return 'Needs Improvement'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const viewDeployment = (deployment) => {
  // Open deployment details modal or navigate to detailed view
  showSuccess(`Viewing deployment details: ${deployment.name}`)
}

const cancelDeployment = async (deployment) => {
  const confirmed = await showConfirm(`Are you sure you want to cancel deployment "${deployment.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/deployments/${deployment.id}/cancel`)
    // if (response.success) {
    //   deployment.status = 'cancelled'
    //   showSuccess('Deployment cancelled successfully')
    // }
    
    // For demo, simulate cancellation
    deployment.status = 'cancelled'
    showSuccess('Deployment cancelled successfully')
  } catch (error) {
    console.error('Error cancelling deployment:', error)
    showError('Failed to cancel deployment')
  }
}

const retryDeployment = async (deployment) => {
  try {
    // const response = await apiPost(`/deployments/${deployment.id}/retry`)
    // if (response.success) {
    //   deployment.status = 'pending'
    //   deployment.progress = 0
    //   showSuccess('Deployment retry initiated')
    // }
    
    // For demo, simulate retry
    deployment.status = 'pending'
    deployment.progress = 0
    showSuccess('Deployment retry initiated')
  } catch (error) {
    console.error('Error retrying deployment:', error)
    showError('Failed to retry deployment')
  }
}

const rollbackDeployment = async (deployment) => {
  const confirmed = await showConfirm(`Are you sure you want to rollback deployment "${deployment.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/deployments/${deployment.id}/rollback`)
    // if (response.success) {
    //   showSuccess('Rollback initiated successfully')
    // }
    
    // For demo, simulate rollback
    showSuccess('Rollback initiated successfully')
  } catch (error) {
    console.error('Error rolling back deployment:', error)
    showError('Failed to rollback deployment')
  }
}

const deployToEnvironment = (environment) => {
  // Open deploy modal with pre-selected environment
  showSuccess(`Deploying to environment: ${environment.name}`)
}

const checkEnvironmentHealth = async (environment) => {
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
  // Open environment configuration modal
  showSuccess(`Configuring environment: ${environment.name}`)
}

const runPipeline = async (pipeline) => {
  try {
    // const response = await apiPost(`/pipelines/${pipeline.id}/run`)
    // if (response.success) {
    //   pipeline.status = 'active'
    //   showSuccess('Pipeline started successfully')
    // }
    
    // For demo, simulate pipeline run
    pipeline.status = 'active'
    showSuccess('Pipeline started successfully')
  } catch (error) {
    console.error('Error running pipeline:', error)
    showError('Failed to run pipeline')
  }
}

const editPipeline = (pipeline) => {
  // Open pipeline edit modal
  showSuccess(`Editing pipeline: ${pipeline.name}`)
}

const createDeployment = async () => {
  if (!deployForm.name || !deployForm.environment || !deployForm.commit) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/deployments', deployForm)
    // if (response.success) {
    //   deployments.value.unshift(response.deployment)
    //   showSuccess('Deployment created successfully')
    //   closeDeployModal()
    //   resetDeployForm()
    // }
    
    // For demo, simulate creation
    const newDeployment = {
      id: Date.now(),
      ...deployForm,
      status: 'pending',
      duration: 'Pending',
      startedAt: new Date().toISOString(),
      progress: 0
    }
    
    deployments.value.unshift(newDeployment)
    showSuccess('Deployment created successfully')
    closeDeployModal()
    resetDeployForm()
  } catch (error) {
    console.error('Error creating deployment:', error)
    showError('Failed to create deployment')
  }
}

const executeRollback = async () => {
  if (!rollbackForm.environmentId || !rollbackForm.targetVersion) {
    showError('Please fill in all required fields')
    return
  }

  const confirmed = await showConfirm('Are you sure you want to execute this rollback? This action cannot be undone.')
  if (!confirmed) return

  try {
    // const response = await apiPost('/deployments/rollback', rollbackForm)
    // if (response.success) {
    //   showSuccess('Rollback executed successfully')
    //   closeRollbackModal()
    //   resetRollbackForm()
    // }
    
    // For demo, simulate rollback
    showSuccess('Rollback executed successfully')
    closeRollbackModal()
    resetRollbackForm()
  } catch (error) {
    console.error('Error executing rollback:', error)
    showError('Failed to execute rollback')
  }
}

const closeDeployModal = () => {
  showDeployModal.value = false
  resetDeployForm()
}

const closeRollbackModal = () => {
  showRollbackModal.value = false
  resetRollbackForm()
}

const resetDeployForm = () => {
  Object.assign(deployForm, {
    name: '',
    description: '',
    environment: '',
    branch: 'main',
    commit: '',
    version: '',
    strategy: 'rolling',
    buildConfig: {
      runTests: true,
      runLinting: true,
      buildAssets: true,
      optimize: true
    },
    notifyOnStart: true,
    notifyOnComplete: true,
    notifyOnFailure: true
  })
}

const resetRollbackForm = () => {
  Object.assign(rollbackForm, {
    environmentId: '',
    targetVersion: '',
    strategy: 'immediate',
    backup: 'yes',
    confirmRequired: true
  })
}

const updateAnalytics = async () => {
  try {
    // const response = await apiGet('/deployments/analytics', { timeRange: timeRange.value })
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
    // const response = await apiGet('/deployments/analytics/refresh')
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
  // Initialize Success Rate chart
  if (successChart.value) successChart.value.destroy()
  successChart.value = new Chart(successChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Successful', 'Failed'],
      datasets: [{
        data: [analytics.successfulDeployments, analytics.failedDeployments],
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

  // Initialize Frequency chart
  if (frequencyChart.value) frequencyChart.value.destroy()
  frequencyChart.value = new Chart(frequencyChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 7 }, (_, i) => `Day ${i + 1}`),
      datasets: [{
        label: 'Deployments',
        data: Array.from({ length: 7 }, () => Math.floor(Math.random() * 8)),
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
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Time chart
  if (timeChart.value) timeChart.value.destroy()
  timeChart.value = new Chart(timeChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Deployment Time (min)',
        data: [8, 12, 6, 15, 9, 4, 7],
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
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Environment Distribution chart
  if (envChart.value) envChart.value.destroy()
  envChart.value = new Chart(envChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Production', 'Staging', 'Development', 'Testing'],
      datasets: [{
        data: [analytics.environments.production, analytics.environments.staging, analytics.environments.development, analytics.environments.testing],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(245, 158, 11, 0.8)',
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
}

const updateCharts = () => {
  // Update charts with new data
  if (successChart.value) {
    successChart.value.data.datasets[0].data = [analytics.successfulDeployments, analytics.failedDeployments]
    successChart.value.update('none')
  }

  if (frequencyChart.value) {
    frequencyChart.value.data.datasets[0].data = Array.from({ length: 7 }, () => Math.floor(Math.random() * 8))
    frequencyChart.value.update('none')
  }

  if (timeChart.value) {
    timeChart.value.data.datasets[0].data = [8, 12, 6, 15, 9, 4, 7]
    timeChart.value.update('none')
  }

  if (envChart.value) {
    envChart.value.data.datasets[0].data = [analytics.environments.production, analytics.environments.staging, analytics.environments.development, analytics.environments.testing]
    envChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadDeploymentData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (successChart.value) successChart.value.destroy()
  if (frequencyChart.value) frequencyChart.value.destroy()
  if (timeChart.value) timeChart.value.destroy()
  if (envChart.value) envChart.value.destroy()
})
</script>

<style scoped>
.deployments {
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

.card-icon.active {
  background: var(--success-color);
}

.card-icon.environments {
  background: var(--info-color);
}

.card-icon.health {
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

.deployment-count,
.active-count,
.env-count,
.health-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.deployment-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.active-count {
  color: var(--text-secondary);
}

.env-count {
  color: var(--text-secondary);
}

.health-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.health-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.health-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.health-status.poor {
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

.deploy-btn,
.rollback-btn,
.pipeline-btn,
.monitor-btn {
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

.deploy-btn:hover,
.rollback-btn:hover,
.pipeline-btn:hover,
.monitor-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.rollback-btn {
  background: var(--warning-color);
}

.rollback-btn:hover {
  background: var(--warning-hover);
}

.pipeline-btn {
  background: var(--info-color);
}

.pipeline-btn:hover {
  background: var(--info-hover);
}

.monitor-btn {
  background: var(--success-color);
}

.monitor-btn:hover {
  background: var(--success-hover);
}

.deployments-section,
.environments-section,
.pipeline-section,
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

.add-env-btn,
.create-pipeline-btn {
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

.add-env-btn:hover,
.create-pipeline-btn:hover {
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

.deploy-first-btn {
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

.deploy-first-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.deployments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.deployment-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.deployment-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.deployment-card.running {
  border-color: var(--warning-color);
}

.deployment-card.failed {
  border-color: var(--danger-color);
}

.deployment-card.cancelled {
  border-color: var(--warning-color);
  opacity: 0.7;
}

.deployment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.deployment-icon {
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

.status-badge.success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.running {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.pending {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.cancelled {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.deployment-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.deployment-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.deployment-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.environment,
.version,
.duration {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.deployment-details {
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

.commit {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: var(--text-primary);
}

.deployment-progress {
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

.deployment-actions {
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

.action-btn.cancel:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.retry:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.rollback:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.deployments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.deployment-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.deployment-list-card:hover {
  background: var(--glass-bg-hover);
}

.deployment-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.deployment-list-info {
  flex: 1;
}

.deployment-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.deployment-list-actions {
  display: flex;
  gap: 0.5rem;
}

.environments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.environment-card.healthy {
  border-color: var(--success-color);
}

.environment-card.unhealthy {
  border-color: var(--danger-color);
}

.environment-card.maintenance {
  border-color: var(--warning-color);
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

.environment-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.environment-status.healthy {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.environment-status.unhealthy {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.environment-status.maintenance {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
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
.url,
.region {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.environment-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.pipeline-flow {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.pipeline-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.pipeline-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.pipeline-card.active {
  border-color: var(--success-color);
}

.pipeline-card.failed {
  border-color: var(--danger-color);
}

.pipeline-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.pipeline-icon {
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

.pipeline-info h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.pipeline-status {
  font-size: 0.8rem;
  color: var(--text-secondary);
  background: var(--glass-bg-tertiary);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
}

.pipeline-stages {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  overflow-x: auto;
}

.pipeline-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 100px;
}

.stage-icon {
  width: 40px;
  height: 40px;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: 1rem;
}

.pipeline-stage.completed .stage-icon {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.pipeline-stage.running .stage-icon {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.pipeline-stage.failed .stage-icon {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.stage-info {
  text-align: center;
}

.stage-name {
  font-size: 0.8rem;
  color: var(--text-primary);
  font-weight: 500;
}

.stage-status {
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.pipeline-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.run:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.edit:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
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
.env-distribution-chart {
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

.deploy-form,
.rollback-form {
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

.build-config,
.options-container {
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

.btn-primary.danger {
  background: var(--danger-color);
}

.btn-primary.danger:hover {
  background: var(--danger-hover);
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
  .deployments {
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
  
  .deployments-grid {
    grid-template-columns: 1fr;
  }
  
  .deployment-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .deployment-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .environments-grid {
    grid-template-columns: 1fr;
  }
  
  .pipeline-stages {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
