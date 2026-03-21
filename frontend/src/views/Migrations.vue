<template>
  <div class="migrations">
    <div class="page-header">
      <h1>Database Migrations</h1>
      <p>Manage database schema migrations and version control</p>
    </div>

    <!-- Migration Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-database"></i>
          </div>
          <div class="card-content">
            <h3>{{ migrationStats.totalMigrations }}</h3>
            <p>Total Migrations</p>
            <span class="migration-count">{{ migrationStats.appliedMigrations }} applied</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon pending">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ migrationStats.pendingMigrations }}</h3>
            <p>Pending Migrations</p>
            <span class="pending-count">{{ migrationStats.urgentMigrations }} urgent</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon version">
            <i class="fas fa-code-branch"></i>
          </div>
          <div class="card-content">
            <h3>{{ migrationStats.currentVersion }}</h3>
            <p>Current Version</p>
            <span class="version-status">{{ migrationStats.latestVersion }} available</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon health">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <h3>{{ migrationStats.healthScore }}%</h3>
            <p>Health Score</p>
            <span class="health-status" :class="getHealthClass(migrationStats.healthScore)">
              {{ getHealthStatus(migrationStats.healthScore) }}
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
          Create Migration
        </button>
        <button class="migrate-btn" @click="runPendingMigrations">
          <i class="fas fa-play"></i>
          Run Pending
        </button>
        <button class="rollback-btn" @click="showRollbackModal = true">
          <i class="fas fa-undo"></i>
          Rollback
        </button>
        <button class="verify-btn" @click="verifyAllMigrations">
          <i class="fas fa-check-circle"></i>
          Verify All
        </button>
      </div>
    </div>

    <!-- Migration List -->
    <div class="migrations-section">
      <div class="section-header">
        <h2>Migration History</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterMigrations">
              <option value="">All Status</option>
              <option value="applied">Applied</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
              <option value="rolled-back">Rolled Back</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="typeFilter" @change="filterMigrations">
              <option value="">All Types</option>
              <option value="schema">Schema</option>
              <option value="data">Data</option>
              <option value="seed">Seed</option>
              <option value="custom">Custom</option>
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
        <p>Loading migrations...</p>
      </div>

      <div v-else-if="filteredMigrations.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-database"></i>
        </div>
        <h3>No migrations found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Migration
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="migrations-grid">
          <div 
            v-for="migration in filteredMigrations" 
            :key="migration.id"
            class="migration-card"
            :class="{ 'pending': migration.status === 'pending', 'failed': migration.status === 'failed', 'rolled-back': migration.status === 'rolled-back' }"
          >
            <div class="migration-header">
              <div class="migration-icon">
                <i :class="getMigrationIcon(migration.type)"></i>
              </div>
              <div class="migration-status">
                <span :class="['status-badge', migration.status]">{{ migration.status }}</span>
              </div>
            </div>

            <div class="migration-content">
              <h3>{{ migration.name }}</h3>
              <p>{{ migration.description }}</p>
              
              <div class="migration-info">
                <span class="type">{{ migration.type }}</span>
                <span class="version">{{ migration.version }}</span>
                <span class="duration">{{ migration.duration }}</span>
              </div>

              <div class="migration-details">
                <div class="detail-item">
                  <label>Created:</label>
                  <span>{{ formatDateTime(migration.createdAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Applied:</label>
                  <span>{{ migration.appliedAt ? formatDateTime(migration.appliedAt) : 'Not applied' }}</span>
                </div>
                <div class="detail-item">
                  <label>Tables:</label>
                  <span>{{ migration.affectedTables }}</span>
                </div>
              </div>

              <div class="migration-progress" v-if="migration.status === 'pending' && migration.running">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: migration.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ migration.progress }}%</span>
              </div>

              <div class="migration-actions">
                <button class="action-btn apply" @click="applyMigration(migration)" v-if="migration.status === 'pending'">
                  <i class="fas fa-play"></i>
                  Apply
                </button>
                <button class="action-btn rollback" @click="rollbackMigration(migration)" v-if="migration.status === 'applied'">
                  <i class="fas fa-undo"></i>
                  Rollback
                </button>
                <button class="action-btn retry" @click="retryMigration(migration)" v-if="migration.status === 'failed'">
                  <i class="fas fa-redo"></i>
                  Retry
                </button>
                <button class="action-btn view" @click="viewMigration(migration)">
                  <i class="fas fa-eye"></i>
                  View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="migrations-list">
          <div 
            v-for="migration in filteredMigrations" 
            :key="migration.id"
            class="migration-list-card"
            :class="{ 'pending': migration.status === 'pending', 'failed': migration.status === 'failed', 'rolled-back': migration.status === 'rolled-back' }"
          >
            <div class="migration-list-header">
              <div class="migration-list-info">
                <div class="migration-icon">
                  <i :class="getMigrationIcon(migration.type)"></i>
                </div>
                <div class="migration-details">
                  <h3>{{ migration.name }}</h3>
                  <p>{{ migration.description }}</p>
                  <div class="migration-info">
                    <span class="type">{{ migration.type }}</span>
                    <span class="version">{{ migration.version }}</span>
                    <span :class="['status-badge', migration.status]">{{ migration.status }}</span>
                    <span class="duration">{{ migration.duration }}</span>
                  </div>
                </div>
              </div>
              <div class="migration-list-stats">
                <div class="detail-item">
                  <label>Created:</label>
                  <span>{{ formatDateTime(migration.createdAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Applied:</label>
                  <span>{{ migration.appliedAt ? formatDateTime(migration.appliedAt) : 'Not applied' }}</span>
                </div>
                <div class="detail-item">
                  <label>Tables:</label>
                  <span>{{ migration.affectedTables }}</span>
                </div>
              </div>
              <div class="migration-list-actions">
                <button class="action-btn apply" @click="applyMigration(migration)" v-if="migration.status === 'pending'">
                  <i class="fas fa-play"></i>
                </button>
                <button class="action-btn rollback" @click="rollbackMigration(migration)" v-if="migration.status === 'applied'">
                  <i class="fas fa-undo"></i>
                </button>
                <button class="action-btn retry" @click="retryMigration(migration)" v-if="migration.status === 'failed'">
                  <i class="fas fa-redo"></i>
                </button>
                <button class="action-btn view" @click="viewMigration(migration)">
                  <i class="fas fa-eye"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Database Schema -->
    <div class="schema-section">
      <div class="section-header">
        <h2>Database Schema</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="schemaFilter" @change="filterSchema">
              <option value="">All Tables</option>
              <option value="user">User Tables</option>
              <option value="system">System Tables</option>
              <option value="temp">Temporary Tables</option>
            </select>
          </div>
          <button class="refresh-schema-btn" @click="refreshSchema">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="schema-grid">
        <div 
          v-for="table in filteredSchema" 
          :key="table.name"
          class="schema-card"
        >
          <div class="schema-header">
            <div class="schema-icon">
              <i class="fas fa-table"></i>
            </div>
            <div class="schema-info">
              <h3>{{ table.name }}</h3>
              <span class="table-type">{{ table.type }}</span>
            </div>
          </div>

          <div class="schema-content">
            <div class="schema-details">
              <div class="detail-item">
                <label>Columns:</label>
                <span>{{ table.columns }}</span>
              </div>
              <div class="detail-item">
                <label>Rows:</label>
                <span>{{ table.rows.toLocaleString() }}</span>
              </div>
              <div class="detail-item">
                <label>Size:</label>
                <span>{{ table.size }}</span>
              </div>
              <div class="detail-item">
                <label>Last Modified:</label>
                <span>{{ formatDateTime(table.lastModified) }}</span>
              </div>
            </div>

            <div class="schema-actions">
              <button class="action-btn view" @click="viewTableSchema(table)">
                <i class="fas fa-eye"></i>
                View Schema
              </button>
              <button class="action-btn export" @click="exportTableSchema(table)">
                <i class="fas fa-download"></i>
                Export
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Migration Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Migration Analytics</h2>
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
            <h3>Migration Success Rate</h3>
            <span class="analytics-value">{{ analytics.successRate }}%</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="successChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Successful: {{ analytics.successfulMigrations }}</span>
            <span class="detail-item">Failed: {{ analytics.failedMigrations }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Migration Frequency</h3>
            <span class="analytics-value">{{ analytics.migrationsPerWeek }}/week</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="frequencyChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">This week: {{ analytics.weeklyMigrations }}</span>
            <span class="detail-item">This month: {{ analytics.monthlyMigrations }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Average Migration Time</h3>
            <span class="analytics-value">{{ analytics.avgMigrationTime }}</span>
          </div>
          <div class="analytics-chart">
            <canvas ref="timeChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Fastest: {{ analytics.fastestMigration }}</span>
            <span class="detail-item">Slowest: {{ analytics.slowestMigration }}</span>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Migration Types</h3>
            <span class="analytics-value">{{ analytics.migrationTypes.length }}</span>
          </div>
          <div class="migration-types-chart">
            <canvas ref="typesChart"></canvas>
          </div>
          <div class="analytics-details">
            <span class="detail-item">Schema: {{ analytics.migrationTypes.schema }}</span>
            <span class="detail-item">Data: {{ analytics.migrationTypes.data }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Migration Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Create Migration</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="migration-form">
            <div class="form-group">
              <label>Migration Name *</label>
              <input 
                v-model="migrationForm.name" 
                type="text" 
                placeholder="Enter migration name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="migrationForm.description" 
                placeholder="Describe this migration"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Migration Type *</label>
                <select v-model="migrationForm.type" required>
                  <option value="schema">Schema Migration</option>
                  <option value="data">Data Migration</option>
                  <option value="seed">Seed Migration</option>
                  <option value="custom">Custom Migration</option>
                </select>
              </div>

              <div class="form-group">
                <label>Database *</label>
                <select v-model="migrationForm.database" required>
                  <option value="main">Main Database</option>
                  <option value="test">Test Database</option>
                  <option value="staging">Staging Database</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Up Migration (SQL)</label>
              <textarea 
                v-model="migrationForm.upSql" 
                placeholder="Enter SQL for up migration"
                rows="8"
                class="sql-textarea"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Down Migration (SQL)</label>
              <textarea 
                v-model="migrationForm.downSql" 
                placeholder="Enter SQL for down migration (rollback)"
                rows="8"
                class="sql-textarea"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Affected Tables</label>
              <div class="tables-container">
                <div 
                  v-for="(table, index) in migrationForm.affectedTables" 
                  :key="index"
                  class="table-item"
                >
                  <input 
                    v-model="table.name" 
                    type="text" 
                    placeholder="table_name"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeTable(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-table-btn" @click="addTable">
                  <i class="fas fa-plus"></i>
                  Add Table
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>Dependencies</label>
              <select v-model="migrationForm.dependencies" multiple>
                <option 
                  v-for="dep in availableMigrations" 
                  :key="dep.id"
                  :value="dep.id"
                >
                  {{ dep.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Options</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="migrationForm.safeMode"
                  />
                  <span>Safe mode (dry run first)</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="migrationForm.backup"
                  />
                  <span>Backup before migration</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="migrationForm.notify"
                  />
                  <span>Notify on completion</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button class="btn-primary" @click="createMigration">
            <i class="fas fa-plus"></i>
            Create Migration
          </button>
        </div>
      </div>
    </div>

    <!-- Rollback Modal -->
    <div v-if="showRollbackModal" class="modal-overlay" @click="closeRollbackModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Rollback Migration</h2>
          <button class="close-btn" @click="closeRollbackModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="rollback-form">
            <div class="form-group">
              <label>Migration to Rollback *</label>
              <select v-model="rollbackForm.migrationId" required>
                <option value="">Select migration</option>
                <option 
                  v-for="migration in appliedMigrations" 
                  :key="migration.id"
                  :value="migration.id"
                >
                  {{ migration.name }} - {{ formatDate(migration.appliedAt) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Rollback Type</label>
              <select v-model="rollbackForm.type">
                <option value="single">Single Migration</option>
                <option value="batch">Batch Rollback</option>
                <option value="all">All Migrations</option>
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

            <div class="form-group">
              <label>Backup Before Rollback</label>
              <select v-model="rollbackForm.backup">
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
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
const typeFilter = ref('')
const schemaFilter = ref('')
const viewMode = ref('grid')
const timeRange = ref('30')
const showCreateModal = ref(false)
const showRollbackModal = ref(false)

// Chart instances
const successChart = ref(null)
const frequencyChart = ref(null)
const timeChart = ref(null)
const typesChart = ref(null)

// Migration stats
const migrationStats = reactive({
  totalMigrations: 156,
  appliedMigrations: 142,
  pendingMigrations: 14,
  urgentMigrations: 3,
  currentVersion: 'v2.1.0',
  latestVersion: 'v2.1.0',
  healthScore: 94
})

// Analytics
const analytics = reactive({
  successRate: 91,
  successfulMigrations: 142,
  failedMigrations: 14,
  migrationsPerWeek: 2.3,
  weeklyMigrations: 16,
  monthlyMigrations: 69,
  avgMigrationTime: '2 min 15 sec',
  fastestMigration: '15 sec',
  slowestMigration: '8 min 45 sec',
  migrationTypes: { schema: 89, data: 45, seed: 12, custom: 10 }
})

// Migration form
const migrationForm = reactive({
  name: '',
  description: '',
  type: 'schema',
  database: 'main',
  upSql: '',
  downSql: '',
  affectedTables: [],
  dependencies: [],
  safeMode: true,
  backup: true,
  notify: true
})

// Rollback form
const rollbackForm = reactive({
  migrationId: '',
  type: 'single',
  confirmRequired: true,
  backup: 'yes'
})

// Mock data
const migrations = ref([
  {
    id: 1,
    name: 'Create users table',
    description: 'Create initial users table with authentication fields',
    type: 'schema',
    status: 'applied',
    version: 'v2.1.0',
    duration: '45 sec',
    createdAt: '2024-01-21T10:30:00Z',
    appliedAt: '2024-01-21T10:31:00Z',
    affectedTables: 1,
    running: false,
    progress: 100
  },
  {
    id: 2,
    name: 'Add email verification',
    description: 'Add email verification field to users table',
    type: 'schema',
    status: 'applied',
    version: 'v2.1.0',
    duration: '23 sec',
    createdAt: '2024-01-21T09:15:00Z',
    appliedAt: '2024-01-21T09:15:30Z',
    affectedTables: 1,
    running: false,
    progress: 100
  },
  {
    id: 3,
    name: 'Migrate user data',
    description: 'Migrate user data from legacy system',
    type: 'data',
    status: 'pending',
    version: 'v2.1.0',
    duration: 'Pending',
    createdAt: '2024-01-21T11:00:00Z',
    appliedAt: null,
    affectedTables: 2,
    running: false,
    progress: 0
  },
  {
    id: 4,
    name: 'Create audit logs',
    description: 'Create audit logs table for tracking changes',
    type: 'schema',
    status: 'failed',
    version: 'v2.0.9',
    duration: 'Failed',
    createdAt: '2024-01-20T23:45:00Z',
    appliedAt: null,
    affectedTables: 1,
    running: false,
    progress: 0
  }
])

const schema = ref([
  {
    name: 'users',
    type: 'user',
    columns: 12,
    rows: 12345,
    size: '2.4MB',
    lastModified: '2024-01-21T10:31:00Z'
  },
  {
    name: 'posts',
    type: 'user',
    columns: 8,
    rows: 5678,
    size: '1.2MB',
    lastModified: '2024-01-21T09:45:00Z'
  },
  {
    name: 'audit_logs',
    type: 'system',
    columns: 6,
    rows: 98765,
    size: '4.5MB',
    lastModified: '2024-01-21T11:15:00Z'
  },
  {
    name: 'temp_sessions',
    type: 'temp',
    columns: 4,
    rows: 234,
    size: '45KB',
    lastModified: '2024-01-21T10:00:00Z'
  }
])

// Computed properties
const filteredMigrations = computed(() => {
  let filtered = migrations.value

  if (statusFilter.value) {
    filtered = filtered.filter(migration => migration.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(migration => migration.type === typeFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

const filteredSchema = computed(() => {
  let filtered = schema.value

  if (schemaFilter.value) {
    filtered = filtered.filter(table => table.type === schemaFilter.value)
  }

  return filtered.sort((a, b) => a.name.localeCompare(b.name))
})

const appliedMigrations = computed(() => {
  return migrations.value.filter(migration => migration.status === 'applied')
})

const availableMigrations = computed(() => {
  return migrations.value.filter(migration => migration.status === 'applied')
})

// Methods
const loadMigrationData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/migrations')
    // if (response.success) {
    //   migrations.value = response.migrations || []
    //   schema.value = response.schema || []
    //   Object.assign(migrationStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading migration data:', error)
    showError('Failed to load migration data')
  } finally {
    loading.value = false
  }
}

const filterMigrations = () => {
  // This is reactive, no additional action needed
}

const filterSchema = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || typeFilter.value) {
    return 'No migrations match your filter criteria'
  }
  return 'No migrations found'
}

const getMigrationIcon = (type) => {
  const icons = {
    'schema': 'fas fa-database',
    'data': 'fas fa-exchange-alt',
    'seed': 'fas fa-seedling',
    'custom': 'fas fa-cog'
  }
  return icons[type] || 'fas fa-database'
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

const applyMigration = async (migration) => {
  const confirmed = await showConfirm(`Are you sure you want to apply migration "${migration.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/migrations/${migration.id}/apply`)
    // if (response.success) {
    //   migration.status = 'applied'
    //   migration.appliedAt = new Date().toISOString()
    //   migration.running = false
    //   migration.progress = 100
    //   showSuccess('Migration applied successfully')
    // }
    
    // For demo, simulate application
    migration.status = 'applied'
    migration.appliedAt = new Date().toISOString()
    migration.running = false
    migration.progress = 100
    showSuccess('Migration applied successfully')
  } catch (error) {
    console.error('Error applying migration:', error)
    showError('Failed to apply migration')
  }
}

const rollbackMigration = async (migration) => {
  const confirmed = await showConfirm(`Are you sure you want to rollback migration "${migration.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiPost(`/migrations/${migration.id}/rollback`)
    // if (response.success) {
    //   migration.status = 'rolled-back'
    //   showSuccess('Migration rolled back successfully')
    // }
    
    // For demo, simulate rollback
    migration.status = 'rolled-back'
    showSuccess('Migration rolled back successfully')
  } catch (error) {
    console.error('Error rolling back migration:', error)
    showError('Failed to rollback migration')
  }
}

const retryMigration = async (migration) => {
  try {
    // const response = await apiPost(`/migrations/${migration.id}/retry`)
    // if (response.success) {
    //   migration.status = 'pending'
    //   migration.running = true
    //   migration.progress = 0
    //   showSuccess('Migration retry initiated')
    // }
    
    // For demo, simulate retry
    migration.status = 'pending'
    migration.running = true
    migration.progress = 0
    showSuccess('Migration retry initiated')
  } catch (error) {
    console.error('Error retrying migration:', error)
    showError('Failed to retry migration')
  }
}

const viewMigration = (migration) => {
  // Open migration details modal or navigate to detailed view
  showSuccess(`Viewing migration details: ${migration.name}`)
}

const runPendingMigrations = async () => {
  const pendingMigrations = migrations.value.filter(m => m.status === 'pending')
  if (pendingMigrations.length === 0) {
    showError('No pending migrations found')
    return
  }

  const confirmed = await showConfirm(`Are you sure you want to run ${pendingMigrations.length} pending migrations?`)
  if (!confirmed) return

  try {
    // const response = await apiPost('/migrations/run-pending')
    // if (response.success) {
    //   pendingMigrations.forEach(migration => {
    //     migration.status = 'applied'
    //     migration.appliedAt = new Date().toISOString()
    //   })
    //   showSuccess('All pending migrations applied successfully')
    // }
    
    // For demo, simulate application
    pendingMigrations.forEach(migration => {
      migration.status = 'applied'
      migration.appliedAt = new Date().toISOString()
    })
    showSuccess('All pending migrations applied successfully')
  } catch (error) {
    console.error('Error running pending migrations:', error)
    showError('Failed to run pending migrations')
  }
}

const verifyAllMigrations = async () => {
  try {
    // const response = await apiPost('/migrations/verify-all')
    // if (response.success) {
    //   showSuccess('All migrations verified successfully')
    // }
    
    // For demo, simulate verification
    showSuccess('All migrations verified successfully')
  } catch (error) {
    console.error('Error verifying migrations:', error)
    showError('Failed to verify migrations')
  }
}

const viewTableSchema = (table) => {
  // Open table schema modal or navigate to detailed view
  showSuccess(`Viewing schema for table: ${table.name}`)
}

const exportTableSchema = (table) => {
  // Export table schema
  showSuccess(`Exporting schema for table: ${table.name}`)
}

const refreshSchema = async () => {
  try {
    // const response = await apiGet('/migrations/schema/refresh')
    // if (response.success) {
    //   schema.value = response.schema || []
    //   showSuccess('Database schema refreshed successfully')
    // }
    
    // For demo, simulate refresh
    showSuccess('Database schema refreshed successfully')
  } catch (error) {
    console.error('Error refreshing schema:', error)
    showError('Failed to refresh database schema')
  }
}

const addTable = () => {
  migrationForm.affectedTables.push({ name: '' })
}

const removeTable = (index) => {
  migrationForm.affectedTables.splice(index, 1)
}

const createMigration = async () => {
  if (!migrationForm.name || !migrationForm.upSql) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/migrations', migrationForm)
    // if (response.success) {
    //   migrations.value.unshift(response.migration)
    //   showSuccess('Migration created successfully')
    //   closeCreateModal()
    //   resetMigrationForm()
    // }
    
    // For demo, simulate creation
    const newMigration = {
      id: Date.now(),
      ...migrationForm,
      status: 'pending',
      version: 'v2.1.0',
      duration: 'Pending',
      createdAt: new Date().toISOString(),
      appliedAt: null,
      affectedTables: migrationForm.affectedTables.length,
      running: false,
      progress: 0
    }
    
    migrations.value.unshift(newMigration)
    showSuccess('Migration created successfully')
    closeCreateModal()
    resetMigrationForm()
  } catch (error) {
    console.error('Error creating migration:', error)
    showError('Failed to create migration')
  }
}

const executeRollback = async () => {
  if (!rollbackForm.migrationId) {
    showError('Please select a migration to rollback')
    return
  }

  const confirmed = await showConfirm('Are you sure you want to execute this rollback? This action cannot be undone.')
  if (!confirmed) return

  try {
    // const response = await apiPost('/migrations/rollback', rollbackForm)
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

const closeCreateModal = () => {
  showCreateModal.value = false
  resetMigrationForm()
}

const closeRollbackModal = () => {
  showRollbackModal.value = false
  resetRollbackForm()
}

const resetMigrationForm = () => {
  Object.assign(migrationForm, {
    name: '',
    description: '',
    type: 'schema',
    database: 'main',
    upSql: '',
    downSql: '',
    affectedTables: [],
    dependencies: [],
    safeMode: true,
    backup: true,
    notify: true
  })
}

const resetRollbackForm = () => {
  Object.assign(rollbackForm, {
    migrationId: '',
    type: 'single',
    confirmRequired: true,
    backup: 'yes'
  })
}

const updateAnalytics = async () => {
  try {
    // const response = await apiGet('/migrations/analytics', { timeRange: timeRange.value })
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
    // const response = await apiGet('/migrations/analytics/refresh')
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
        data: [analytics.successfulMigrations, analytics.failedMigrations],
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
        label: 'Migrations',
        data: Array.from({ length: 7 }, () => Math.floor(Math.random() * 5)),
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
        label: 'Migration Time (sec)',
        data: [45, 23, 67, 15, 45, 12, 34],
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
      labels: ['Schema', 'Data', 'Seed', 'Custom'],
      datasets: [{
        data: [analytics.migrationTypes.schema, analytics.migrationTypes.data, analytics.migrationTypes.seed, analytics.migrationTypes.custom],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
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
    successChart.value.data.datasets[0].data = [analytics.successfulMigrations, analytics.failedMigrations]
    successChart.value.update('none')
  }

  if (frequencyChart.value) {
    frequencyChart.value.data.datasets[0].data = Array.from({ length: 7 }, () => Math.floor(Math.random() * 5))
    frequencyChart.value.update('none')
  }

  if (timeChart.value) {
    timeChart.value.data.datasets[0].data = [45, 23, 67, 15, 45, 12, 34]
    timeChart.value.update('none')
  }

  if (typesChart.value) {
    typesChart.value.data.datasets[0].data = [analytics.migrationTypes.schema, analytics.migrationTypes.data, analytics.migrationTypes.seed, analytics.migrationTypes.custom]
    typesChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadMigrationData()
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
.migrations {
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

.card-icon.pending {
  background: var(--warning-color);
}

.card-icon.version {
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

.migration-count,
.pending-count,
.version-status,
.health-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.migration-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.pending-count {
  color: var(--text-secondary);
}

.version-status {
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
.migrate-btn,
.rollback-btn,
.verify-btn {
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
.migrate-btn:hover,
.rollback-btn:hover,
.verify-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.migrate-btn {
  background: var(--success-color);
}

.migrate-btn:hover {
  background: var(--success-hover);
}

.rollback-btn {
  background: var(--warning-color);
}

.rollback-btn:hover {
  background: var(--warning-hover);
}

.verify-btn {
  background: var(--info-color);
}

.verify-btn:hover {
  background: var(--info-hover);
}

.migrations-section,
.schema-section,
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

.refresh-schema-btn,
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

.refresh-schema-btn:hover,
.refresh-btn:hover {
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

.migrations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.migration-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.migration-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.migration-card.pending {
  border-color: var(--warning-color);
}

.migration-card.failed {
  border-color: var(--danger-color);
}

.migration-card.rolled-back {
  border-color: var(--warning-color);
  opacity: 0.7;
}

.migration-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.migration-icon {
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

.status-badge.applied {
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

.status-badge.rolled-back {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.migration-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.migration-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.migration-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.version,
.duration {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.migration-details {
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

.migration-progress {
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

.migration-actions {
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

.action-btn.apply:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.rollback:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.retry:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.view:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.migrations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.migration-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.migration-list-card:hover {
  background: var(--glass-bg-hover);
}

.migration-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.migration-list-info {
  flex: 1;
}

.migration-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.migration-list-actions {
  display: flex;
  gap: 0.5rem;
}

.schema-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.schema-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.schema-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.schema-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.schema-icon {
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

.schema-info h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.table-type {
  font-size: 0.8rem;
  color: var(--text-secondary);
  background: var(--glass-bg-tertiary);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.schema-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.schema-actions {
  display: flex;
  gap: 0.5rem;
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
.migration-types-chart {
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

.migration-form,
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

.sql-textarea {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
}

.tables-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.table-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.table-item input {
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

.add-table-btn {
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

.add-table-btn:hover {
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
  .migrations {
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
  
  .migrations-grid {
    grid-template-columns: 1fr;
  }
  
  .migration-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .migration-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .schema-grid {
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
