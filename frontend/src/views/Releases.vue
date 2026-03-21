<template>
  <div class="releases">
    <div class="page-header">
      <h1>Release Management</h1>
      <p>Manage software releases, versioning, and deployment strategies</p>
    </div>

    <!-- Release Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-rocket"></i>
          </div>
          <div class="card-content">
            <h3>{{ releaseStats.totalReleases }}</h3>
            <p>Total Releases</p>
            <span class="release-count">{{ releaseStats.publishedReleases }} published</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon latest">
            <i class="fas fa-star"></i>
          </div>
          <div class="card-content">
            <h3>{{ releaseStats.latestVersion }}</h3>
            <p>Latest Version</p>
            <span class="version-date">{{ formatDate(releaseStats.latestReleaseDate) }}</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon pending">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ releaseStats.pendingReleases }}</h3>
            <p>Pending Releases</p>
            <span class="pending-count">{{ releaseStats.inProgressReleases }} in progress</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon health">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <h3>{{ releaseStats.healthScore }}%</h3>
            <p>Release Health</p>
            <span class="health-status" :class="getHealthClass(releaseStats.healthScore)">
              {{ getHealthStatus(releaseStats.healthScore) }}
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
          New Release
        </button>
        <button class="deploy-btn" @click="showDeployModal = true">
          <i class="fas fa-rocket"></i>
          Deploy
        </button>
        <button class="rollback-btn" @click="showRollbackModal = true">
          <i class="fas fa-undo"></i>
          Rollback
        </button>
        <button class="monitor-btn" @click="showMonitorModal = true">
          <i class="fas fa-chart-line"></i>
          Monitor
        </button>
      </div>
    </div>

    <!-- Release History -->
    <div class="releases-section">
      <div class="section-header">
        <h2>Release History</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterReleases">
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="pending">Pending</option>
              <option value="published">Published</option>
              <option value="failed">Failed</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="typeFilter" @change="filterReleases">
              <option value="">All Types</option>
              <option value="major">Major</option>
              <option value="minor">Minor</option>
              <option value="patch">Patch</option>
              <option value="hotfix">Hotfix</option>
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
        <p>Loading releases...</p>
      </div>

      <div v-else-if="filteredReleases.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-rocket"></i>
        </div>
        <h3>No releases found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Release
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="releases-grid">
          <div 
            v-for="release in filteredReleases" 
            :key="release.id"
            class="release-card"
            :class="{ 'draft': release.status === 'draft', 'pending': release.status === 'pending', 'failed': release.status === 'failed', 'archived': release.status === 'archived' }"
          >
            <div class="release-header">
              <div class="release-icon">
                <i :class="getReleaseIcon(release.type)"></i>
              </div>
              <div class="release-status">
                <span :class="['status-badge', release.status]">{{ release.status }}</span>
              </div>
            </div>

            <div class="release-content">
              <h3>{{ release.version }}</h3>
              <p>{{ release.description }}</p>
              
              <div class="release-info">
                <span class="type">{{ release.type }}</span>
                <span class="branch">{{ release.branch }}</span>
                <span class="date">{{ formatDate(release.createdAt) }}</span>
              </div>

              <div class="release-details">
                <div class="detail-item">
                  <label>Build:</label>
                  <span>{{ release.buildNumber }}</span>
                </div>
                <div class="detail-item">
                  <label>Changes:</label>
                  <span>{{ release.changes.length }}</span>
                </div>
                <div class="detail-item">
                  <label>Environment:</label>
                  <span>{{ release.environment }}</span>
                </div>
              </div>

              <div class="release-progress" v-if="release.status === 'pending' && release.deploying">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: release.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ release.progress }}%</span>
              </div>

              <div class="release-actions">
                <button class="action-btn view" @click="viewRelease(release)">
                  <i class="fas fa-eye"></i>
                  View
                </button>
                <button class="action-btn deploy" @click="deployRelease(release)" v-if="release.status === 'pending'">
                  <i class="fas fa-rocket"></i>
                  Deploy
                </button>
                <button class="action-btn rollback" @click="rollbackRelease(release)" v-if="release.status === 'published'">
                  <i class="fas fa-undo"></i>
                  Rollback
                </button>
                <button class="action-btn archive" @click="archiveRelease(release)" v-if="release.status === 'published'">
                  <i class="fas fa-archive"></i>
                  Archive
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="releases-list">
          <div 
            v-for="release in filteredReleases" 
            :key="release.id"
            class="release-list-card"
            :class="{ 'draft': release.status === 'draft', 'pending': release.status === 'pending', 'failed': release.status === 'failed', 'archived': release.status === 'archived' }"
          >
            <div class="release-list-header">
              <div class="release-list-info">
                <div class="release-icon">
                  <i :class="getReleaseIcon(release.type)"></i>
                </div>
                <div class="release-details">
                  <h3>{{ release.version }}</h3>
                  <p>{{ release.description }}</p>
                  <div class="release-info">
                    <span class="type">{{ release.type }}</span>
                    <span class="branch">{{ release.branch }}</span>
                    <span :class="['status-badge', release.status]">{{ release.status }}</span>
                    <span class="date">{{ formatDate(release.createdAt) }}</span>
                  </div>
                </div>
              </div>
              <div class="release-list-stats">
                <div class="detail-item">
                  <label>Build:</label>
                  <span>{{ release.buildNumber }}</span>
                </div>
                <div class="detail-item">
                  <label>Changes:</label>
                  <span>{{ release.changes.length }}</span>
                </div>
                <div class="detail-item">
                  <label>Environment:</label>
                  <span>{{ release.environment }}</span>
                </div>
              </div>
              <div class="release-list-actions">
                <button class="action-btn view" @click="viewRelease(release)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn deploy" @click="deployRelease(release)" v-if="release.status === 'pending'">
                  <i class="fas fa-rocket"></i>
                </button>
                <button class="action-btn rollback" @click="rollbackRelease(release)" v-if="release.status === 'published'">
                  <i class="fas fa-undo"></i>
                </button>
                <button class="action-btn archive" @click="archiveRelease(release)" v-if="release.status === 'published'">
                  <i class="fas fa-archive"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Release Pipeline -->
    <div class="pipeline-section">
      <div class="section-header">
        <h2>Release Pipeline</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="pipelineFilter" @change="filterPipelines">
              <option value="">All Pipelines</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
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
          :class="{ 'active': pipeline.status === 'active', 'completed': pipeline.status === 'completed', 'failed': pipeline.status === 'failed' }"
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
            <button class="action-btn run" @click="runPipeline(pipeline)" v-if="pipeline.status !== 'completed'">
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

    <!-- Release Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Release Analytics</h2>
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
            <h3>Release Success Rate</h3>
            <span class="analytics-value">{{ analytics.successRate }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="successChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Successful: {{ analytics.successfulReleases }}</span>
            <span class="detail-item">Failed: {{ analytics.failedReleases }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Release Frequency</h3>
            <span class="analytics-value">{{ analytics.releasesPerMonth }}/month</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="frequencyChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">This month: {{ analytics.monthlyReleases }}</span>
            <span class="detail-item">This year: {{ analytics.yearlyReleases }}</span>
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
            <h3>Release Types</h3>
            <span class="analytics-value">{{ analytics.releaseTypes.length }}</span>
          </div>
          <div class="release-types-chart">
            <canvas ref="typesChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Major: {{ analytics.releaseTypes.major }}</span>
            <span class="detail-item">Minor: {{ analytics.releaseTypes.minor }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Release Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Create Release</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="release-form">
            <div class="form-group">
              <label>Version Number *</label>
              <input 
                v-model="releaseForm.version" 
                type="text" 
                placeholder="v2.1.0"
                required
              />
            </div>

            <div class="form-group">
              <label>Release Name</label>
              <input 
                v-model="releaseForm.name" 
                type="text" 
                placeholder="Enter release name"
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="releaseForm.description" 
                placeholder="Describe this release"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Release Type *</label>
                <select v-model="releaseForm.type" required>
                  <option value="major">Major</option>
                  <option value="minor">Minor</option>
                  <option value="patch">Patch</option>
                  <option value="hotfix">Hotfix</option>
                </select>
              </div>

              <div class="form-group">
                <label>Branch *</label>
                <select v-model="releaseForm.branch" required>
                  <option value="main">main</option>
                  <option value="develop">develop</option>
                  <option value="release">release</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Build Number</label>
              <input 
                v-model="releaseForm.buildNumber" 
                type="text" 
                placeholder="Build #1234"
              />
            </div>

            <div class="form-group">
              <label>Target Environment</label>
              <select v-model="releaseForm.environment">
                <option value="production">Production</option>
                <option value="staging">Staging</option>
                <option value="development">Development</option>
                <option value="testing">Testing</option>
              </select>
            </div>

            <div class="form-group">
              <label>Release Notes</label>
              <textarea 
                v-model="releaseForm.releaseNotes" 
                placeholder="Enter release notes"
                rows="5"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Changelog</label>
              <div class="changelog-container">
                <div 
                  v-for="(change, index) in releaseForm.changelog" 
                  :key="index"
                  class="changelog-item"
                >
                  <input 
                    v-model="change.description" 
                    type="text" 
                    placeholder="Describe the change"
                  />
                  <select v-model="change.type">
                    <option value="feature">Feature</option>
                    <option value="bugfix">Bug Fix</option>
                    <option value="improvement">Improvement</option>
                    <option value="breaking">Breaking Change</option>
                  </select>
                  <button 
                    class="remove-btn"
                    @click="removeChange(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-change-btn" @click="addChange">
                  <i class="fas fa-plus"></i>
                  Add Change
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>Deployment Strategy</label>
              <select v-model="releaseForm.deploymentStrategy">
                <option value="immediate">Immediate</option>
                <option value="canary">Canary</option>
                <option value="blue-green">Blue-Green</option>
                <option value="rolling">Rolling</option>
              </select>
            </div>

            <div class="form-group">
              <label>Options</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="releaseForm.createTag"
                  />
                  <span>Create Git tag</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="releaseForm.notifyUsers"
                  />
                  <span>Notify users</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="releaseForm.backupBeforeDeploy"
                  />
                  <span>Backup before deploy</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="releaseForm.runTests"
                  />
                  <span>Run tests before release</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button class="btn-primary" @click="createRelease">
            <i class="fas fa-rocket"></i>
            Create Release
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
const pipelineFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('30')
const showCreateModal = ref(false)
const showDeployModal = ref(false)
const showRollbackModal = ref(false)
const showMonitorModal = ref(false)
const showCreatePipelineModal = ref(false)

// Chart instances
const successChart = ref(null)
const frequencyChart = ref(null)
const timeChart = ref(null)
const typesChart = ref(null)

// Release stats
const releaseStats = reactive({
  totalReleases: 89,
  publishedReleases: 67,
  latestVersion: 'v2.1.0',
  latestReleaseDate: '2024-01-21T10:30:00Z',
  pendingReleases: 8,
  inProgressReleases: 3,
  healthScore: 92
})

// Analytics
const analytics = reactive({
  successRate: 92,
  successfulReleases: 67,
  failedReleases: 6,
  releasesPerMonth: 4.5,
  monthlyReleases: 4,
  yearlyReleases: 54,
  avgDeploymentTime: '15 min 30 sec',
  fastestDeployment: '5 min 15 sec',
  slowestDeployment: '45 min 20 sec',
  releaseTypes: { major: 12, minor: 45, patch: 28, hotfix: 4 }
})

// Release form
const releaseForm = reactive({
  version: '',
  name: '',
  description: '',
  type: 'minor',
  branch: 'main',
  buildNumber: '',
  environment: 'staging',
  releaseNotes: '',
  changelog: [],
  deploymentStrategy: 'canary',
  createTag: true,
  notifyUsers: true,
  backupBeforeDeploy: true,
  runTests: true
})

// Mock data
const releases = ref([
  {
    id: 1,
    version: 'v2.1.0',
    name: 'Major Release v2.1.0',
    description: 'Major feature release with new dashboard and API improvements',
    status: 'published',
    type: 'major',
    branch: 'main',
    buildNumber: '#1234',
    environment: 'production',
    createdAt: '2024-01-21T10:30:00Z',
    changes: [
      { type: 'feature', description: 'New dashboard UI' },
      { type: 'feature', description: 'API v2.0' },
      { type: 'improvement', description: 'Performance improvements' }
    ],
    deploying: false,
    progress: 100
  },
  {
    id: 2,
    version: 'v2.0.5',
    name: 'Security Update v2.0.5',
    description: 'Security patch for authentication vulnerability',
    status: 'published',
    type: 'patch',
    branch: 'main',
    buildNumber: '#1233',
    environment: 'production',
    createdAt: '2024-01-15T14:20:00Z',
    changes: [
      { type: 'bugfix', description: 'Fixed auth vulnerability' },
      { type: 'improvement', description: 'Enhanced security measures' }
    ],
    deploying: false,
    progress: 100
  },
  {
    id: 3,
    version: 'v2.0.4',
    name: 'Feature Release v2.0.4',
    description: 'Feature release with new reporting capabilities',
    status: 'pending',
    type: 'minor',
    branch: 'develop',
    buildNumber: '#1232',
    environment: 'staging',
    createdAt: '2024-01-20T09:45:00Z',
    changes: [
      { type: 'feature', description: 'New reporting module' },
      { type: 'improvement', description: 'Enhanced data visualization' }
    ],
    deploying: true,
    progress: 67
  },
  {
    id: 4,
    version: 'v2.0.3',
    name: 'Hotfix v2.0.3',
    description: 'Hotfix for critical bug in payment processing',
    status: 'draft',
    type: 'hotfix',
    branch: 'hotfix/payment-bug',
    buildNumber: '#1231',
    environment: 'testing',
    createdAt: '2024-01-19T16:30:00Z',
    changes: [
      { type: 'bugfix', description: 'Fixed payment processing bug' }
    ],
    deploying: false,
    progress: 0
  }
])

const pipelines = ref([
  {
    id: 1,
    name: 'Production Release Pipeline',
    status: 'completed',
    stages: [
      { name: 'Build', type: 'build', status: 'completed' },
      { name: 'Test', type: 'test', status: 'completed' },
      { name: 'Security Scan', type: 'security', status: 'completed' },
      { name: 'Deploy', type: 'deploy', status: 'completed' },
      { name: 'Verify', type: 'verify', status: 'completed' }
    ]
  },
  {
    id: 2,
    name: 'Staging Release Pipeline',
    status: 'active',
    stages: [
      { name: 'Build', type: 'build', status: 'completed' },
      { name: 'Test', type: 'test', status: 'running' },
      { name: 'Security Scan', type: 'security', status: 'pending' },
      { name: 'Deploy', type: 'deploy', status: 'pending' },
      { name: 'Verify', type: 'verify', status: 'pending' }
    ]
  },
  {
    id: 3,
    name: 'Hotfix Pipeline',
    status: 'failed',
    stages: [
      { name: 'Build', type: 'build', status: 'failed' },
      { name: 'Test', type: 'test', status: 'pending' },
      { name: 'Security Scan', type: 'security', status: 'pending' },
      { name: 'Deploy', type: 'deploy', status: 'pending' },
      { name: 'Verify', type: 'verify', status: 'pending' }
    ]
  }
])

// Computed properties
const filteredReleases = computed(() => {
  let filtered = releases.value

  if (statusFilter.value) {
    filtered = filtered.filter(release => release.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(release => release.type === typeFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

const filteredPipelines = computed(() => {
  let filtered = pipelines.value

  if (pipelineFilter.value) {
    filtered = filtered.filter(pipeline => pipeline.status === pipelineFilter.value)
  }

  return filtered
})

// Methods
const loadReleaseData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/releases')
    // if (response.success) {
    //   releases.value = response.releases || []
    //   pipelines.value = response.pipelines || []
    //   Object.assign(releaseStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading release data:', error)
    showError('Failed to load release data')
  } finally {
    loading.value = false
  }
}

const filterReleases = () => {
  // This is reactive, no additional action needed
}

const filterPipelines = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || typeFilter.value) {
    return 'No releases match your filter criteria'
  }
  return 'No releases found'
}

const getReleaseIcon = (type) => {
  const icons = {
    'major': 'fas fa-star',
    'minor': 'fas fa-plus',
    'patch': 'fas fa-wrench',
    'hotfix': 'fas fa-fire'
  }
  return icons[type] || 'fas fa-rocket'
}

const getStageIcon = (type) => {
  const icons = {
    'build': 'fas fa-hammer',
    'test': 'fas fa-check-circle',
    'security': 'fas fa-shield-alt',
    'deploy': 'fas fa-rocket',
    'verify': 'fas fa-check-double'
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

const viewRelease = (release) => {
  // Open release details modal or navigate to detailed view
  showSuccess(`Viewing release details: ${release.version}`)
}

const deployRelease = async (release) => {
  const confirmed = await showConfirm(`Are you sure you want to deploy release "${release.version}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/releases/${release.id}/deploy`)
    // if (response.success) {
    //   release.status = 'published'
    //   release.deploying = false
    //   release.progress = 100
    //   showSuccess('Release deployed successfully')
    // }
    
    // For demo, simulate deployment
    release.status = 'published'
    release.deploying = false
    release.progress = 100
    showSuccess('Release deployed successfully')
  } catch (error) {
    console.error('Error deploying release:', error)
    showError('Failed to deploy release')
  }
}

const rollbackRelease = async (release) => {
  const confirmed = await showConfirm(`Are you sure you want to rollback release "${release.version}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/releases/${release.id}/rollback`)
    // if (response.success) {
    //   showSuccess('Release rollback initiated')
    // }
    
    // For demo, simulate rollback
    showSuccess('Release rollback initiated')
  } catch (error) {
    console.error('Error rolling back release:', error)
    showError('Failed to rollback release')
  }
}

const archiveRelease = async (release) => {
  const confirmed = await showConfirm(`Are you sure you want to archive release "${release.version}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/releases/${release.id}/archive`)
    // if (response.success) {
    //   release.status = 'archived'
    //   showSuccess('Release archived successfully')
    // }
    
    // For demo, simulate archive
    release.status = 'archived'
    showSuccess('Release archived successfully')
  } catch (error) {
    console.error('Error archiving release:', error)
    showError('Failed to archive release')
  }
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

const addChange = () => {
  releaseForm.changelog.push({ type: 'feature', description: '' })
}

const removeChange = (index) => {
  releaseForm.changelog.splice(index, 1)
}

const createRelease = async () => {
  if (!releaseForm.version || !releaseForm.branch) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/releases', releaseForm)
    // if (response.success) {
    //   releases.value.unshift(response.release)
    //   showSuccess('Release created successfully')
    //   closeCreateModal()
    //   resetReleaseForm()
    // }
    
    // For demo, simulate creation
    const newRelease = {
      id: Date.now(),
      ...releaseForm,
      status: 'draft',
      createdAt: new Date().toISOString(),
      changes: releaseForm.changelog,
      deploying: false,
      progress: 0
    }
    
    releases.value.unshift(newRelease)
    showSuccess('Release created successfully')
    closeCreateModal()
    resetReleaseForm()
  } catch (error) {
    console.error('Error creating release:', error)
    showError('Failed to create release')
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetReleaseForm()
}

const resetReleaseForm = () => {
  Object.assign(releaseForm, {
    version: '',
    name: '',
    description: '',
    type: 'minor',
    branch: 'main',
    buildNumber: '',
    environment: 'staging',
    releaseNotes: '',
    changelog: [],
    deploymentStrategy: 'canary',
    createTag: true,
    notifyUsers: true,
    backupBeforeDeploy: true,
    runTests: true
  })
}

const updateAnalytics = async () => {
  try {
    // const response = await apiGet('/releases/analytics', { timeRange: timeRange.value })
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
    // const response = await apiGet('/releases/analytics/refresh')
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
        data: [analytics.successfulReleases, analytics.failedReleases],
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
      labels: Array.from({ length: 12 }, (_, i) => `Month ${i + 1}`),
      datasets: [{
        label: 'Releases',
        data: Array.from({ length: 12 }, () => Math.floor(Math.random() * 8)),
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
        data: [15, 20, 10, 25, 12, 8, 5],
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

  // Initialize Types chart
  if (typesChart.value) typesChart.value.destroy()
  typesChart.value = new Chart(typesChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Major', 'Minor', 'Patch', 'Hotfix'],
      datasets: [{
        data: [analytics.releaseTypes.major, analytics.releaseTypes.minor, analytics.releaseTypes.patch, analytics.releaseTypes.hotfix],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)'
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
    successChart.value.data.datasets[0].data = [analytics.successfulReleases, analytics.failedReleases]
    successChart.value.update('none')
  }

  if (frequencyChart.value) {
    frequencyChart.value.data.datasets[0].data = Array.from({ length: 12 }, () => Math.floor(Math.random() * 8))
    frequencyChart.value.update('none')
  }

  if (timeChart.value) {
    timeChart.value.data.datasets[0].data = [15, 20, 10, 25, 12, 8, 5]
    timeChart.value.update('none')
  }

  if (typesChart.value) {
    typesChart.value.data.datasets[0].data = [analytics.releaseTypes.major, analytics.releaseTypes.minor, analytics.releaseTypes.patch, analytics.releaseTypes.hotfix]
    typesChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadReleaseData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (successChart.value) successChart.value.destroy()
  if (frequencyChart.value) frequencyChart.value.destroy()
  if (timeChart.value) timeChart.value.destroy()
  if (typesChart.value) typesChart.value.destroy()
})
</script>

<style scoped>
.releases {
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

.card-icon.latest {
  background: var(--warning-color);
}

.card-icon.pending {
  background: var(--info-color);
}

.card-icon.health {
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

.release-count,
.version-date,
.pending-count,
.health-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.release-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.version-date {
  color: var(--text-secondary);
}

.pending-count {
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

.create-btn,
.deploy-btn,
.rollback-btn,
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

.create-btn:hover,
.deploy-btn:hover,
.rollback-btn:hover,
.monitor-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.deploy-btn {
  background: var(--success-color);
}

.deploy-btn:hover {
  background: var(--success-hover);
}

.rollback-btn {
  background: var(--warning-color);
}

.rollback-btn:hover {
  background: var(--warning-hover);
}

.monitor-btn {
  background: var(--info-color);
}

.monitor-btn:hover {
  background: var(--info-hover);
}

.releases-section,
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

.releases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.release-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.release-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.release-card.draft {
  border-color: var(--info-color);
}

.release-card.pending {
  border-color: var(--warning-color);
}

.release-card.failed {
  border-color: var(--danger-color);
}

.release-card.archived {
  border-color: var(--text-tertiary);
  opacity: 0.7;
}

.release-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.release-icon {
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

.status-badge.draft {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.published {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.archived {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.release-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.release-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.release-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.branch,
.date {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.release-details {
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

.release-progress {
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

.release-actions {
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

.action-btn.rollback:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.archive:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.releases-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.release-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.release-list-card:hover {
  background: var(--glass-bg-hover);
}

.release-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.release-list-info {
  flex: 1;
}

.release-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.release-list-actions {
  display: flex;
  gap: 0.5rem;
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

.pipeline-card.completed {
  border-color: var(--info-color);
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
.release-types-chart {
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

.release-form {
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

.changelog-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.changelog-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.changelog-item input {
  flex: 1;
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
}

.changelog-item select {
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

.add-change-btn {
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

.add-change-btn:hover {
  background: var(--primary-hover);
}

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

.btn-secondary {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
}

@media (max-width: 768px) {
  .releases {
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
  
  .releases-grid {
    grid-template-columns: 1fr;
  }
  
  .release-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .release-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .pipeline-flow {
    gap: 1rem;
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
