<template>
  <div class="builds">
    <div class="page-header">
      <h1>Build Management</h1>
      <p>Manage application builds, CI/CD pipelines, and build configurations</p>
    </div>

    <!-- Build Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-hammer"></i>
          </div>
          <div class="card-content">
            <h3>{{ buildStats.totalBuilds }}</h3>
            <p>Total Builds</p>
            <span class="build-count">{{ buildStats.successfulBuilds }} successful</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon running">
            <i class="fas fa-play-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ buildStats.runningBuilds }}</h3>
            <p>Running Builds</p>
            <span class="running-count">{{ buildStats.queuedBuilds }} queued</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon pipelines">
            <i class="fas fa-project-diagram"></i>
          </div>
          <div class="card-content">
            <h3>{{ buildStats.activePipelines }}</h3>
            <p>Active Pipelines</p>
            <span class="pipeline-count">{{ buildStats.totalPipelines }} total</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon health">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <h3>{{ buildStats.healthScore }}%</h3>
            <p>Health Score</p>
            <span class="health-status" :class="getHealthClass(buildStats.healthScore)">
              {{ getHealthStatus(buildStats.healthScore) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="build-btn" @click="showBuildModal = true">
          <i class="fas fa-hammer"></i>
          New Build
        </button>
        <button class="pipeline-btn" @click="showPipelineModal = true">
          <i class="fas fa-project-diagram"></i>
          Pipeline
        </button>
        <button class="queue-btn" @click="showQueueModal = true">
          <i class="fas fa-list"></i>
          Queue
        </button>
        <button class="monitor-btn" @click="showMonitorModal = true">
          <i class="fas fa-chart-line"></i>
          Monitor
        </button>
      </div>
    </div>

    <!-- Build History -->
    <div class="builds-section">
      <div class="section-header">
        <h2>Build History</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterBuilds">
              <option value="">All Status</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="running">Running</option>
              <option value="pending">Pending</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="branchFilter" @change="filterBuilds">
              <option value="">All Branches</option>
              <option value="main">main</option>
              <option value="develop">develop</option>
              <option value="feature">feature/*</option>
              <option value="hotfix">hotfix/*</option>
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
        <p>Loading builds...</p>
      </div>

      <div v-else-if="filteredBuilds.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-hammer"></i>
        </div>
        <h3>No builds found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="build-first-btn" @click="showBuildModal = true">
          <i class="fas fa-hammer"></i>
          Create Your First Build
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="builds-grid">
          <div 
            v-for="build in filteredBuilds" 
            :key="build.id"
            class="build-card"
            :class="{ 'running': build.status === 'running', 'failed': build.status === 'failed', 'cancelled': build.status === 'cancelled' }"
          >
            <div class="build-header">
              <div class="build-icon">
                <i :class="getBuildIcon(build.type)"></i>
              </div>
              <div class="build-status">
                <span :class="['status-badge', build.status]">{{ build.status }}</span>
              </div>
            </div>

            <div class="build-content">
              <h3>{{ build.name }}</h3>
              <p>{{ build.description }}</p>
              
              <div class="build-info">
                <span class="branch">{{ build.branch }}</span>
                <span class="commit">{{ build.commit }}</span>
                <span class="duration">{{ build.duration }}</span>
              </div>

              <div class="build-details">
                <div class="detail-item">
                  <label>Started:</label>
                  <span>{{ formatDateTime(build.startedAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Trigger:</label>
                  <span>{{ build.trigger }}</span>
                </div>
                <div class="detail-item">
                  <label>Environment:</label>
                  <span>{{ build.environment }}</span>
                </div>
              </div>

              <div class="build-progress" v-if="build.status === 'running'">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: build.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ build.progress }}%</span>
              </div>

              <div class="build-actions">
                <button class="action-btn view" @click="viewBuild(build)">
                  <i class="fas fa-eye"></i>
                  View
                </button>
                <button class="action-btn cancel" @click="cancelBuild(build)" v-if="['running', 'pending'].includes(build.status)">
                  <i class="fas fa-times"></i>
                  Cancel
                </button>
                <button class="action-btn retry" @click="retryBuild(build)" v-if="build.status === 'failed'">
                  <i class="fas fa-redo"></i>
                  Retry
                </button>
                <button class="action-btn download" @click="downloadBuild(build)" v-if="build.status === 'success'">
                  <i class="fas fa-download"></i>
                  Download
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="builds-list">
          <div 
            v-for="build in filteredBuilds" 
            :key="build.id"
            class="build-list-card"
            :class="{ 'running': build.status === 'running', 'failed': build.status === 'failed', 'cancelled': build.status === 'cancelled' }"
          >
            <div class="build-list-header">
              <div class="build-list-info">
                <div class="build-icon">
                  <i :class="getBuildIcon(build.type)"></i>
                </div>
                <div class="build-details">
                  <h3>{{ build.name }}</h3>
                  <p>{{ build.description }}</p>
                  <div class="build-info">
                    <span class="branch">{{ build.branch }}</span>
                    <span class="commit">{{ build.commit }}</span>
                    <span :class="['status-badge', build.status]">{{ build.status }}</span>
                    <span class="duration">{{ build.duration }}</span>
                  </div>
                </div>
              </div>
              <div class="build-list-stats">
                <div class="detail-item">
                  <label>Started:</label>
                  <span>{{ formatDateTime(build.startedAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Trigger:</label>
                  <span>{{ build.trigger }}</span>
                </div>
                <div class="detail-item">
                  <label>Environment:</label>
                  <span>{{ build.environment }}</span>
                </div>
              </div>
              <div class="build-list-actions">
                <button class="action-btn view" @click="viewBuild(build)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn cancel" @click="cancelBuild(build)" v-if="['running', 'pending'].includes(build.status)">
                  <i class="fas fa-times"></i>
                </button>
                <button class="action-btn retry" @click="retryBuild(build)" v-if="build.status === 'failed'">
                  <i class="fas fa-redo"></i>
                </button>
                <button class="action-btn download" @click="downloadBuild(build)" v-if="build.status === 'success'">
                  <i class="fas fa-download"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Build Queue -->
    <div class="queue-section">
      <div class="section-header">
        <h2>Build Queue</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="queueFilter" @change="filterQueue">
              <option value="">All Queue</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <button class="clear-queue-btn" @click="clearQueue">
            <i class="fas fa-trash"></i>
            Clear Queue
          </button>
        </div>
      </div>

      <div class="queue-list">
        <div 
          v-for="item in filteredQueue" 
          :key="item.id"
          class="queue-item"
          :class="{ 'running': item.status === 'running', 'failed': item.status === 'failed' }"
        >
          <div class="queue-item-header">
            <div class="queue-item-info">
              <div class="queue-item-icon">
                <i :class="getBuildIcon(item.type)"></i>
              </div>
              <div class="queue-item-details">
                <h3>{{ item.name }}</h3>
                <p>{{ item.description }}</p>
                <div class="queue-item-info">
                  <span class="branch">{{ item.branch }}</span>
                  <span class="priority">{{ item.priority }}</span>
                  <span class="estimated">{{ item.estimatedTime }}</span>
                </div>
              </div>
            </div>
            <div class="queue-item-actions">
              <button class="action-btn start" @click="startBuild(item)" v-if="item.status === 'pending'">
                <i class="fas fa-play"></i>
                Start
              </button>
              <button class="action-btn stop" @click="stopBuild(item)" v-if="item.status === 'running'">
                <i class="fas fa-stop"></i>
                Stop
              </button>
              <button class="action-btn remove" @click="removeFromQueue(item)">
                <i class="fas fa-times"></i>
                Remove
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Build Pipelines -->
    <div class="pipelines-section">
      <div class="section-header">
        <h2>Build Pipelines</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="pipelineFilter" @change="filterPipelines">
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

      <div class="pipelines-grid">
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

    <!-- Build Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Build Analytics</h2>
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
            <h3>Build Success Rate</h3>
            <span class="analytics-value">{{ analytics.successRate }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="successChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Successful: {{ analytics.successfulBuilds }}</span>
            <span class="detail-item">Failed: {{ analytics.failedBuilds }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Build Frequency</h3>
            <span class="analytics-value">{{ analytics.buildsPerDay }}/day</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="frequencyChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">This week: {{ analytics.weeklyBuilds }}</span>
            <span class="detail-item">This month: {{ analytics.monthlyBuilds }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Average Build Time</h3>
            <span class="analytics-value">{{ analytics.avgBuildTime }}</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="timeChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Fastest: {{ analytics.fastestBuild }}</span>
            <span class="detail-item">Slowest: {{ analytics.slowestBuild }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Build Types</h3>
            <span class="analytics-value">{{ analytics.buildTypes.length }}</span>
          </div>
          <div class="build-types-chart">
            <canvas ref="typesChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Release: {{ analytics.buildTypes.release }}</span>
            <span class="detail-item">Feature: {{ analytics.buildTypes.feature }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- New Build Modal -->
    <div v-if="showBuildModal" class="modal-overlay" @click="closeBuildModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>New Build</h2>
          <button class="close-btn" @click="closeBuildModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="build-form">
            <div class="form-group">
              <label>Build Name *</label>
              <input 
                v-model="buildForm.name" 
                type="text" 
                placeholder="Enter build name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="buildForm.description" 
                placeholder="Describe this build"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Branch *</label>
                <select v-model="buildForm.branch" required>
                  <option value="main">main</option>
                  <option value="develop">develop</option>
                  <option value="feature/test">feature/test</option>
                </select>
              </div>

              <div class="form-group">
                <label>Commit *</label>
                <input 
                  v-model="buildForm.commit" 
                  type="text" 
                  placeholder="Enter commit SHA"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label>Build Type</label>
              <select v-model="buildForm.type">
                <option value="release">Release</option>
                <option value="feature">Feature</option>
                <option value="hotfix">Hotfix</option>
                <option value="debug">Debug</option>
              </select>
            </div>

            <div class="form-group">
              <label>Environment</label>
              <select v-model="buildForm.environment">
                <option value="production">Production</option>
                <option value="staging">Staging</option>
                <option value="development">Development</option>
                <option value="testing">Testing</option>
              </select>
            </div>

            <div class="form-group">
              <label>Build Configuration</label>
              <div class="build-config">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="buildForm.config.runTests"
                  />
                  <span>Run tests</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="buildForm.config.runLinting"
                  />
                  <span>Run linting</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="buildForm.config.buildAssets"
                  />
                  <span>Build assets</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="buildForm.config.optimize"
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
                    v-model="buildForm.notifyOnStart"
                  />
                  <span>Notify on start</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="buildForm.notifyOnComplete"
                  />
                  <span>Notify on completion</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="buildForm.notifyOnFailure"
                  />
                  <span>Notify on failure</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeBuildModal">Cancel</button>
          <button class="btn-primary" @click="createBuild">
            <i class="fas fa-hammer"></i>
            Start Build
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
const branchFilter = ref('')
const queueFilter = ref('')
const pipelineFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('30')
const showBuildModal = ref(false)
const showPipelineModal = ref(false)
const showQueueModal = ref(false)
const showMonitorModal = ref(false)
const showCreatePipelineModal = ref(false)

// Chart instances
const successChart = ref(null)
const frequencyChart = ref(null)
const timeChart = ref(null)
const typesChart = ref(null)

// Build stats
const buildStats = reactive({
  totalBuilds: 456,
  successfulBuilds: 398,
  runningBuilds: 3,
  queuedBuilds: 8,
  activePipelines: 12,
  totalPipelines: 18,
  healthScore: 87
})

// Analytics
const analytics = reactive({
  successRate: 87,
  successfulBuilds: 398,
  failedBuilds: 58,
  buildsPerDay: 5.2,
  weeklyBuilds: 36,
  monthlyBuilds: 156,
  avgBuildTime: '12 min 30 sec',
  fastestBuild: '3 min 15 sec',
  slowestBuild: '45 min 20 sec',
  buildTypes: { release: 89, feature: 234, hotfix: 45, debug: 88 }
})

// Build form
const buildForm = reactive({
  name: '',
  description: '',
  branch: 'main',
  commit: '',
  type: 'release',
  environment: 'staging',
  config: {
    runTests: true,
    runLinting: true,
    buildAssets: true,
    optimize: false
  },
  notifyOnStart: true,
  notifyOnComplete: true,
  notifyOnFailure: true
})

// Mock data
const builds = ref([
  {
    id: 1,
    name: 'Release Build v2.1.0',
    description: 'Production release build',
    status: 'success',
    type: 'release',
    branch: 'main',
    commit: 'abc123def456',
    duration: '12 min 30 sec',
    startedAt: '2024-01-21T10:30:00Z',
    trigger: 'Manual',
    environment: 'production',
    progress: 100
  },
  {
    id: 2,
    name: 'Feature Build - User Dashboard',
    description: 'Feature branch build for user dashboard',
    status: 'running',
    type: 'feature',
    branch: 'feature/user-dashboard',
    commit: 'def456ghi789',
    duration: 'In progress',
    startedAt: '2024-01-21T11:00:00Z',
    trigger: 'Push',
    environment: 'staging',
    progress: 67
  },
  {
    id: 3,
    name: 'Hotfix Build - Login Issue',
    description: 'Hotfix for login authentication issue',
    status: 'failed',
    type: 'hotfix',
    branch: 'hotfix/login-fix',
    commit: 'ghi789jkl012',
    duration: 'Failed',
    startedAt: '2024-01-21T09:15:00Z',
    trigger: 'Manual',
    environment: 'testing',
    progress: 0
  },
  {
    id: 4,
    name: 'Debug Build - Performance',
    description: 'Debug build for performance testing',
    status: 'pending',
    type: 'debug',
    branch: 'develop',
    commit: 'jkl012mno345',
    duration: 'Pending',
    startedAt: '2024-01-21T23:45:00Z',
    trigger: 'Scheduled',
    environment: 'development',
    progress: 0
  }
])

const buildQueue = ref([
  {
    id: 1,
    name: 'API Build v2.0.5',
    description: 'API service build',
    status: 'pending',
    type: 'release',
    branch: 'main',
    priority: 'high',
    estimatedTime: '15 min'
  },
  {
    id: 2,
    name: 'Frontend Build - Dashboard',
    description: 'Frontend dashboard build',
    status: 'running',
    type: 'feature',
    branch: 'feature/dashboard',
    priority: 'medium',
    estimatedTime: '8 min'
  },
  {
    id: 3,
    name: 'Mobile App Build',
    description: 'Mobile application build',
    status: 'pending',
    type: 'release',
    branch: 'main',
    priority: 'low',
    estimatedTime: '25 min'
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

// Computed properties
const filteredBuilds = computed(() => {
  let filtered = builds.value

  if (statusFilter.value) {
    filtered = filtered.filter(build => build.status === statusFilter.value)
  }

  if (branchFilter.value) {
    filtered = filtered.filter(build => build.branch.includes(branchFilter.value))
  }

  return filtered.sort((a, b) => new Date(b.startedAt) - new Date(a.startedAt))
})

const filteredQueue = computed(() => {
  let filtered = buildQueue.value

  if (queueFilter.value) {
    filtered = filtered.filter(item => item.status === queueFilter.value)
  }

  return filtered.sort((a, b) => {
    const priorityOrder = { high: 0, medium: 1, low: 2 }
    return priorityOrder[a.priority] - priorityOrder[b.priority]
  })
})

const filteredPipelines = computed(() => {
  let filtered = pipelines.value

  if (pipelineFilter.value) {
    filtered = filtered.filter(pipeline => pipeline.status === pipelineFilter.value)
  }

  return filtered
})

// Methods
const loadBuildData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/builds')
    // if (response.success) {
    //   builds.value = response.builds || []
    //   buildQueue.value = response.queue || []
    //   pipelines.value = response.pipelines || []
    //   Object.assign(buildStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading build data:', error)
    showError('Failed to load build data')
  } finally {
    loading.value = false
  }
}

const filterBuilds = () => {
  // This is reactive, no additional action needed
}

const filterQueue = () => {
  // This is reactive, no additional action needed
}

const filterPipelines = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || branchFilter.value) {
    return 'No builds match your filter criteria'
  }
  return 'No builds found'
}

const getBuildIcon = (type) => {
  const icons = {
    'release': 'fas fa-rocket',
    'feature': 'fas fa-code-branch',
    'hotfix': 'fas fa-wrench',
    'debug': 'fas fa-bug'
  }
  return icons[type] || 'fas fa-hammer'
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

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const viewBuild = (build) => {
  // Open build details modal or navigate to detailed view
  showSuccess(`Viewing build details: ${build.name}`)
}

const cancelBuild = async (build) => {
  const confirmed = await showConfirm(`Are you sure you want to cancel build "${build.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/builds/${build.id}/cancel`)
    // if (response.success) {
    //   build.status = 'cancelled'
    //   showSuccess('Build cancelled successfully')
    // }
    
    // For demo, simulate cancellation
    build.status = 'cancelled'
    showSuccess('Build cancelled successfully')
  } catch (error) {
    console.error('Error cancelling build:', error)
    showError('Failed to cancel build')
  }
}

const retryBuild = async (build) => {
  try {
    // const response = await apiPost(`/builds/${build.id}/retry`)
    // if (response.success) {
    //   build.status = 'pending'
    //   build.progress = 0
    //   showSuccess('Build retry initiated')
    // }
    
    // For demo, simulate retry
    build.status = 'pending'
    build.progress = 0
    showSuccess('Build retry initiated')
  } catch (error) {
    console.error('Error retrying build:', error)
    showError('Failed to retry build')
  }
}

const downloadBuild = async (build) => {
  try {
    // const response = await apiGet(`/builds/${build.id}/download`)
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `${build.name}.zip`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Build downloaded successfully')
    // }
    
    // For demo, simulate download
    showSuccess('Build downloaded successfully')
  } catch (error) {
    console.error('Error downloading build:', error)
    showError('Failed to download build')
  }
}

const startBuild = async (item) => {
  try {
    // const response = await apiPost(`/builds/queue/${item.id}/start`)
    // if (response.success) {
    //   item.status = 'running'
    //   showSuccess('Build started successfully')
    // }
    
    // For demo, simulate start
    item.status = 'running'
    showSuccess('Build started successfully')
  } catch (error) {
    console.error('Error starting build:', error)
    showError('Failed to start build')
  }
}

const stopBuild = async (item) => {
  try {
    // const response = await apiPost(`/builds/queue/${item.id}/stop`)
    // if (response.success) {
    //   item.status = 'pending'
    //   showSuccess('Build stopped successfully')
    // }
    
    // For demo, simulate stop
    item.status = 'pending'
    showSuccess('Build stopped successfully')
  } catch (error) {
    console.error('Error stopping build:', error)
    showError('Failed to stop build')
  }
}

const removeFromQueue = async (item) => {
  const confirmed = await showConfirm(`Are you sure you want to remove "${item.name}" from the queue?`)
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/builds/queue/${item.id}`)
    // if (response.success) {
    //   const index = buildQueue.value.findIndex(i => i.id === item.id)
    //   if (index > -1) {
    //     buildQueue.value.splice(index, 1)
    //     showSuccess('Build removed from queue')
    //   }
    // }
    
    // For demo, simulate removal
    const index = buildQueue.value.findIndex(i => i.id === item.id)
    if (index > -1) {
      buildQueue.value.splice(index, 1)
      showSuccess('Build removed from queue')
    }
  } catch (error) {
    console.error('Error removing build from queue:', error)
    showError('Failed to remove build from queue')
  }
}

const clearQueue = async () => {
  const confirmed = await showConfirm('Are you sure you want to clear the entire build queue?')
  if (!confirmed) return

  try {
    // const response = await apiPost('/builds/queue/clear')
    // if (response.success) {
    //   buildQueue.value = []
    //   showSuccess('Build queue cleared successfully')
    // }
    
    // For demo, simulate clear
    buildQueue.value = []
    showSuccess('Build queue cleared successfully')
  } catch (error) {
    console.error('Error clearing build queue:', error)
    showError('Failed to clear build queue')
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

const createBuild = async () => {
  if (!buildForm.name || !buildForm.branch || !buildForm.commit) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/builds', buildForm)
    // if (response.success) {
    //   builds.value.unshift(response.build)
    //   showSuccess('Build created successfully')
    //   closeBuildModal()
    //   resetBuildForm()
    // }
    
    // For demo, simulate creation
    const newBuild = {
      id: Date.now(),
      ...buildForm,
      status: 'pending',
      duration: 'Pending',
      startedAt: new Date().toISOString(),
      trigger: 'Manual',
      progress: 0
    }
    
    builds.value.unshift(newBuild)
    showSuccess('Build created successfully')
    closeBuildModal()
    resetBuildForm()
  } catch (error) {
    console.error('Error creating build:', error)
    showError('Failed to create build')
  }
}

const closeBuildModal = () => {
  showBuildModal.value = false
  resetBuildForm()
}

const resetBuildForm = () => {
  Object.assign(buildForm, {
    name: '',
    description: '',
    branch: 'main',
    commit: '',
    type: 'release',
    environment: 'staging',
    config: {
      runTests: true,
      runLinting: true,
      buildAssets: true,
      optimize: false
    },
    notifyOnStart: true,
    notifyOnComplete: true,
    notifyOnFailure: true
  })
}

const updateAnalytics = async () => {
  try {
    // const response = await apiGet('/builds/analytics', { timeRange: timeRange.value })
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
    // const response = await apiGet('/builds/analytics/refresh')
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
        data: [analytics.successfulBuilds, analytics.failedBuilds],
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
        label: 'Builds',
        data: Array.from({ length: 7 }, () => Math.floor(Math.random() * 10)),
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
        label: 'Build Time (min)',
        data: [12, 15, 8, 20, 10, 5, 7],
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
      labels: ['Release', 'Feature', 'Hotfix', 'Debug'],
      datasets: [{
        data: [analytics.buildTypes.release, analytics.buildTypes.feature, analytics.buildTypes.hotfix, analytics.buildTypes.debug],
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
    successChart.value.data.datasets[0].data = [analytics.successfulBuilds, analytics.failedBuilds]
    successChart.value.update('none')
  }

  if (frequencyChart.value) {
    frequencyChart.value.data.datasets[0].data = Array.from({ length: 7 }, () => Math.floor(Math.random() * 10))
    frequencyChart.value.update('none')
  }

  if (timeChart.value) {
    timeChart.value.data.datasets[0].data = [12, 15, 8, 20, 10, 5, 7]
    timeChart.value.update('none')
  }

  if (typesChart.value) {
    typesChart.value.data.datasets[0].data = [analytics.buildTypes.release, analytics.buildTypes.feature, analytics.buildTypes.hotfix, analytics.buildTypes.debug]
    typesChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadBuildData()
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
.builds {
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

.card-icon.running {
  background: var(--success-color);
}

.card-icon.pipelines {
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

.build-count,
.running-count,
.pipeline-count,
.health-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.build-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.running-count {
  color: var(--text-secondary);
}

.pipeline-count {
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

.build-btn,
.pipeline-btn,
.queue-btn,
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

.build-btn:hover,
.pipeline-btn:hover,
.queue-btn:hover,
.monitor-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.pipeline-btn {
  background: var(--info-color);
}

.pipeline-btn:hover {
  background: var(--info-hover);
}

.queue-btn {
  background: var(--warning-color);
}

.queue-btn:hover {
  background: var(--warning-hover);
}

.monitor-btn {
  background: var(--success-color);
}

.monitor-btn:hover {
  background: var(--success-hover);
}

.builds-section,
.queue-section,
.pipelines-section,
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

.clear-queue-btn,
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

.clear-queue-btn:hover,
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

.build-first-btn {
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

.build-first-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.builds-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.build-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.build-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.build-card.running {
  border-color: var(--warning-color);
}

.build-card.failed {
  border-color: var(--danger-color);
}

.build-card.cancelled {
  border-color: var(--warning-color);
  opacity: 0.7;
}

.build-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.build-icon {
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

.build-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.build-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.build-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.branch,
.commit,
.duration {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.build-details {
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

.build-progress {
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

.build-actions {
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

.action-btn.download:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.builds-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.build-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.build-list-card:hover {
  background: var(--glass-bg-hover);
}

.build-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.build-list-info {
  flex: 1;
}

.build-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.build-list-actions {
  display: flex;
  gap: 0.5rem;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.queue-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.queue-item:hover {
  background: var(--glass-bg-hover);
}

.queue-item.running {
  border-color: var(--warning-color);
}

.queue-item.failed {
  border-color: var(--danger-color);
}

.queue-item-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.queue-item-info {
  flex: 1;
}

.queue-item-icon {
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

.queue-item-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.queue-item-info p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.queue-item-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.priority,
.estimated {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.priority {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.queue-item-actions {
  display: flex;
  gap: 0.5rem;
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

.action-btn.remove:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.pipelines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
.build-types-chart {
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

.build-form {
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

.btn-secondary {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
}

@media (max-width: 768px) {
  .builds {
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
  
  .builds-grid {
    grid-template-columns: 1fr;
  }
  
  .build-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .build-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .pipelines-grid {
    grid-template-columns: 1fr;
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
