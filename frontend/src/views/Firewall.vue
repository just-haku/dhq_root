<template>
  <div class="firewall">
    <div class="page-header">
      <h1>Firewall Management</h1>
      <p>Configure and manage firewall rules and security policies</p>
    </div>

    <!-- Firewall Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-shield-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ firewallStats.totalRules }}</h3>
            <p>Total Rules</p>
            <span class="rule-count">{{ firewallStats.activeRules }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon blocked">
            <i class="fas fa-ban"></i>
          </div>
          <div class="card-content">
            <h3>{{ firewallStats.blockedAttempts }}</h3>
            <p>Blocked Attempts</p>
            <span class="blocked-count">{{ firewallStats.todayBlocked }} today</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon traffic">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="card-content">
            <h3>{{ firewallStats.totalTraffic }}</h3>
            <p>Total Traffic</p>
            <span class="traffic-status">{{ firewallStats.allowedTraffic }} allowed</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon security">
            <i class="fas fa-lock"></i>
          </div>
          <div class="card-content">
            <h3>{{ firewallStats.securityScore }}%</h3>
            <p>Security Score</p>
            <span class="security-status" :class="getSecurityClass(firewallStats.securityScore)">
              {{ getSecurityStatus(firewallStats.securityScore) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="add-rule-btn" @click="showAddRuleModal = true">
          <i class="fas fa-plus"></i>
          Add Rule
        </button>
        <button class="import-btn" @click="showImportModal = true">
          <i class="fas fa-upload"></i>
          Import Rules
        </button>
        <button class="test-btn" @click="testFirewall">
          <i class="fas fa-vial"></i>
          Test Firewall
        </button>
        <button class="settings-btn" @click="showSettingsModal = true">
          <i class="fas fa-cog"></i>
          Settings
        </button>
      </div>
    </div>

    <!-- Firewall Rules -->
    <div class="rules-section">
      <div class="section-header">
        <h2>Firewall Rules</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterRules">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="pending">Pending</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="typeFilter" @change="filterRules">
              <option value="">All Types</option>
              <option value="allow">Allow</option>
              <option value="deny">Deny</option>
              <option value="log">Log</option>
              <option value="rate-limit">Rate Limit</option>
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
        <p>Loading firewall rules...</p>
      </div>

      <div v-else-if="filteredRules.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-shield-alt"></i>
        </div>
        <h3>No firewall rules found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="add-first-btn" @click="showAddRuleModal = true">
          <i class="fas fa-plus"></i>
          Add Your First Rule
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="rules-grid">
          <div 
            v-for="rule in filteredRules" 
            :key="rule.id"
            class="rule-card"
            :class="{ 'inactive': rule.status === 'inactive', 'pending': rule.status === 'pending', 'error': rule.status === 'error' }"
          >
            <div class="rule-header">
              <div class="rule-icon">
                <i :class="getRuleIcon(rule.type)"></i>
              </div>
              <div class="rule-status">
                <span :class="['status-badge', rule.status]">{{ rule.status }}</span>
              </div>
            </div>

            <div class="rule-content">
              <h3>{{ rule.name }}</h3>
              <p>{{ rule.description }}</p>
              
              <div class="rule-info">
                <span class="type">{{ rule.type }}</span>
                <span class="protocol">{{ rule.protocol }}</span>
                <span class="action">{{ rule.action }}</span>
              </div>

              <div class="rule-details">
                <div class="detail-item">
                  <label>Source:</label>
                  <span>{{ rule.source }}</span>
                </div>
                <div class="detail-item">
                  <label>Destination:</label>
                  <span>{{ rule.destination }}</span>
                </div>
                <div class="detail-item">
                  <label>Port:</label>
                  <span>{{ rule.port }}</span>
                </div>
              </div>

              <div class="rule-actions">
                <button class="action-btn test" @click="testRule(rule)">
                  <i class="fas fa-vial"></i>
                  Test
                </button>
                <button class="action-btn edit" @click="editRule(rule)">
                  <i class="fas fa-edit"></i>
                  Edit
                </button>
                <button 
                  class="action-btn toggle"
                  @click="toggleRule(rule)"
                  :class="rule.status === 'active' ? 'disable' : 'enable'"
                >
                  <i :class="rule.status === 'active' ? 'fas fa-pause' : 'fas fa-play'"></i>
                  {{ rule.status === 'active' ? 'Disable' : 'Enable' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="rules-list">
          <div 
            v-for="rule in filteredRules" 
            :key="rule.id"
            class="rule-list-card"
            :class="{ 'inactive': rule.status === 'inactive', 'pending': rule.status === 'pending', 'error': rule.status === 'error' }"
          >
            <div class="rule-list-header">
              <div class="rule-list-info">
                <div class="rule-icon">
                  <i :class="getRuleIcon(rule.type)"></i>
                </div>
                <div class="rule-details">
                  <h3>{{ rule.name }}</h3>
                  <p>{{ rule.description }}</p>
                  <div class="rule-info">
                    <span class="type">{{ rule.type }}</span>
                    <span class="protocol">{{ rule.protocol }}</span>
                    <span :class="['status-badge', rule.status]">{{ rule.status }}</span>
                    <span class="action">{{ rule.action }}</span>
                  </div>
                </div>
              </div>
              <div class="rule-list-stats">
                <div class="detail-item">
                  <label>Source:</label>
                  <span>{{ rule.source }}</span>
                </div>
                <div class="detail-item">
                  <label>Destination:</label>
                  <span>{{ rule.destination }}</span>
                </div>
                <div class="detail-item">
                  <label>Port:</label>
                  <span>{{ rule.port }}</span>
                </div>
              </div>
              <div class="rule-list-actions">
                <button class="action-btn test" @click="testRule(rule)">
                  <i class="fas fa-vial"></i>
                </button>
                <button class="action-btn edit" @click="editRule(rule)">
                  <i class="fas fa-edit"></i>
                </button>
                <button 
                  class="action-btn toggle"
                  @click="toggleRule(rule)"
                  :class="rule.status === 'active' ? 'disable' : 'enable'"
                >
                  <i :class="rule.status === 'active' ? 'fas fa-pause' : 'fas fa-play'"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Traffic Monitoring -->
    <div class="traffic-section">
      <div class="section-header">
        <h2>Traffic Monitoring</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="timeRange" @change="updateTrafficData">
              <option value="1">Last Hour</option>
              <option value="6">Last 6 Hours</option>
              <option value="24">Last 24 Hours</option>
              <option value="168">Last Week</option>
            </select>
          </div>
          <button class="refresh-btn" @click="refreshTrafficData">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="traffic-grid">
        <div class="traffic-card">
          <div class="traffic-header">
            <h3>Blocked Traffic</h3>
            <span class="traffic-value">{{ trafficStats.blocked }}</span>
          </div>
          <div class="traffic-chart">
            <canvas ref="blockedChart"></canvas>
          </div>
          <div class="traffic-details">
            <span class="detail-item">Last hour: {{ trafficStats.blockedHour }}</span>
            <span class="detail-item">Today: {{ trafficStats.blockedToday }}</span>
          </div>
        </div>

        <div class="traffic-card">
          <div class="traffic-header">
            <h3>Allowed Traffic</h3>
            <span class="traffic-value">{{ trafficStats.allowed }}</span>
          </div>
          <div class="traffic-chart">
            <canvas ref="allowedChart"></canvas>
          </div>
          <div class="traffic-details">
            <span class="detail-item">Last hour: {{ trafficStats.allowedHour }}</span>
            <span class="detail-item">Today: {{ trafficStats.allowedToday }}</span>
          </div>
        </div>

        <div class="traffic-card">
          <div class="traffic-header">
            <h3>Protocol Distribution</h3>
            <span class="traffic-value">{{ trafficStats.protocols.length }}</span>
          </div>
          <div class="protocol-chart">
            <canvas ref="protocolChart"></canvas>
          </div>
          <div class="traffic-details">
            <span class="detail-item">HTTP: {{ trafficStats.protocols.http }}</span>
            <span class="detail-item">HTTPS: {{ trafficStats.protocols.https }}</span>
          </div>
        </div>

        <div class="traffic-card">
          <div class="traffic-header">
            <h3>Top Sources</h3>
            <span class="traffic-value">{{ trafficStats.topSources.length }}</span>
          </div>
          <div class="sources-list">
            <div 
              v-for="(source, index) in trafficStats.topSources" 
              :key="index"
              class="source-item"
            >
              <span class="source-ip">{{ source.ip }}</span>
              <span class="source-count">{{ source.count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Security Policies -->
    <div class="policies-section">
      <div class="section-header">
        <h2>Security Policies</h2>
        <div class="header-actions">
          <button class="add-policy-btn" @click="showAddPolicyModal = true">
            <i class="fas fa-plus"></i>
            Add Policy
          </button>
        </div>
      </div>

      <div class="policies-grid">
        <div 
          v-for="policy in policies" 
          :key="policy.id"
          class="policy-card"
          :class="{ 'inactive': policy.status === 'inactive', 'error': policy.status === 'error' }"
        >
          <div class="policy-header">
            <div class="policy-icon">
              <i :class="getPolicyIcon(policy.type)"></i>
            </div>
            <div class="policy-status">
              <span :class="['status-badge', policy.status]">{{ policy.status }}</span>
            </div>
          </div>

          <div class="policy-content">
            <h3>{{ policy.name }}</h3>
            <p>{{ policy.description }}</p>
            
            <div class="policy-info">
              <span class="type">{{ policy.type }}</span>
              <span class="severity">{{ policy.severity }}</span>
              <span class="enabled">{{ policy.enabled ? 'Enabled' : 'Disabled' }}</span>
            </div>

            <div class="policy-details">
              <div class="detail-item">
                <label>Created:</label>
                <span>{{ formatDate(policy.createdAt) }}</span>
              </div>
              <div class="detail-item">
                <label>Last Modified:</label>
                <span>{{ formatDate(policy.updatedAt) }}</span>
              </div>
              <div class="detail-item">
                <label>Trigger Count:</label>
                <span>{{ policy.triggerCount }}</span>
              </div>
            </div>

            <div class="policy-actions">
              <button class="action-btn test" @click="testPolicy(policy)">
                <i class="fas fa-vial"></i>
                Test
              </button>
              <button class="action-btn edit" @click="editPolicy(policy)">
                <i class="fas fa-edit"></i>
                Edit
              </button>
              <button 
                class="action-btn toggle"
                @click="togglePolicy(policy)"
                :class="policy.enabled ? 'disable' : 'enable'"
              >
                <i :class="policy.enabled ? 'fas fa-pause' : 'fas fa-play'"></i>
                {{ policy.enabled ? 'Disable' : 'Enable' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Rule Modal -->
    <div v-if="showAddRuleModal" class="modal-overlay" @click="closeAddRuleModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Add Firewall Rule</h2>
          <button class="close-btn" @click="closeAddRuleModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="rule-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Rule Name *</label>
                <input 
                  v-model="ruleForm.name" 
                  type="text" 
                  placeholder="Enter rule name"
                  required
                />
              </div>
              <div class="form-group">
                <label>Rule Type *</label>
                <select v-model="ruleForm.type" required>
                  <option value="allow">Allow</option>
                  <option value="deny">Deny</option>
                  <option value="log">Log</option>
                  <option value="rate-limit">Rate Limit</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="ruleForm.description" 
                placeholder="Describe this rule"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Protocol *</label>
                <select v-model="ruleForm.protocol" required>
                  <option value="tcp">TCP</option>
                  <option value="udp">UDP</option>
                  <option value="icmp">ICMP</option>
                </select>
              </div>

              <div class="form-group">
                <label>Source</label>
                <input 
                  v-model="ruleForm.source" 
                  type="text" 
                  placeholder="192.168.1.1"
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Destination</label>
                <input 
                  v-model="ruleForm.destination" 
                  type="text" 
                  placeholder="192.168.1.1"
                />
              </div>

              <div class="form-group">
                <label>Port</label>
                <input 
                  v-model.number="ruleForm.port" 
                  type="number" 
                  placeholder="80"
                  min="1"
                  max="65535"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Priority</label>
              <select v-model="ruleForm.priority">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div class="form-group">
              <label>Log Level</label>
              <select v-model="ruleForm.logLevel">
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div class="form-group" v-if="ruleForm.type === 'rate-limit'">
              <label>Rate Limit</label>
              <input 
                v-model.number="ruleForm.rateLimit" 
                type="number" 
                placeholder="100"
                min="1"
              />
            </div>

            <div class="form-group">
              <label>Time Range</label>
              <select v-model="ruleForm.timeRange">
                <option value="1">1 minute</option>
                <option value="5">5 minutes</option>
                <option value="15">15 minutes</option>
                <option value="1">1 hour</option>
                <option value="6">6 hours</option>
                <option value="24">24 hours</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeAddRuleModal">Cancel</button>
          <button class="btn-primary" @click="addRule">
            <i class="fas fa-plus"></i>
            Add Rule
          </button>
        </div>
      </div>
    </div>

    <!-- Add Policy Modal -->
    <div v-if="showAddPolicyModal" class="modal-overlay" @click="closeAddPolicyModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add Security Policy</h2>
          <button class="close-btn" @click="closeAddPolicyModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="policy-form">
            <div class="form-group">
              <label>Policy Name *</label>
              <input 
                v-model="policyForm.name" 
                type="text" 
                placeholder="Enter policy name"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="policyForm.description" 
                placeholder="Describe this security policy"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Policy Type *</label>
                <select v-model="policyForm.type" required>
                  <option value="intrusion-prevention">Intrusion Prevention</option>
                  <option value="malware-detection">Malware Detection</option>
                  <option value="data-protection">Data Protection</option>
                  <option value="access-control">Access Control</option>
                  <option value="audit-logging">Audit Logging</option>
                  <option value="compliance">Compliance</option>
                </select>
              </div>

              <div class="form-group">
                <label>Severity Level</label>
                <select v-model="policyForm.severity">
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Trigger Condition</label>
              <textarea 
                v-model="policyForm.triggerCondition" 
                placeholder="Define trigger condition"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Response Action</label>
              <select v-model="policyForm.responseAction">
                <option value="log">Log Only</option>
                <option value="alert">Alert</option>
                <option value="block">Block</option>
                <option value="quarantine">Quarantine</option>
              </select>
            </div>

            <div class="form-group">
              <label>Auto-remediation</label>
              <select v-model="policyForm.autoRemediation">
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeAddPolicyModal">Cancel</button>
          <button class="btn-primary" @click="addPolicy">
            <i class="fas fa-plus"></i>
            Add Policy
          </button>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettingsModal" class="modal-overlay" @click="closeSettingsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Firewall Settings</h2>
          <button class="close-btn" @click="closeSettingsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="settings-form">
            <div class="form-group">
              <label>Default Action</label>
              <select v-model="settingsForm.defaultAction">
                <option value="deny">Deny</option>
                <option value="allow">Allow</option>
                <option value="log">Log</option>
              </select>
            </div>

            <div class="form-group">
              <label>Log Level</label>
              <select v-model="settingsForm.logLevel">
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div class="form-group">
              <label>Max Log Retention</label>
              <select v-model="settingsForm.logRetention">
                <option value="7">7 days</option>
                <option value="30">30 days</option>
                <option value="90">90 days</option>
                <option value="365">1 year</option>
              </select>
            </div>

            <div class="form-group">
              <label>Alert Email</label>
              <input 
                v-model="settingsForm.alertEmail" 
                type="email" 
                placeholder="admin@example.com"
              />
            </div>

            <div class="form-group">
              <label>Alert Threshold</label>
              <input 
                v-model.number="settingsConfig.alertThreshold" 
                type="number" 
                placeholder="10"
                min="1"
              />
            </div>

            <div class="form-group">
              <label>Block Duration</label>
              <select v-model="settingsForm.blockDuration">
                <option value="300">5 minutes</option>
                <option value="900">15 minutes</option>
                <option value="3600">1 hour</option>
                <option value="86400">24 hours</option>
                <option value="604800">1 week</option>
              </select>
            </div>

            <div class="form-group">
              <label>IP Whitelist</label>
              <textarea 
                v-model="settingsConfig.ipWhitelist" 
                placeholder="Enter IP addresses (one per line)"
                rows="4"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Blacklist</label>
              <textarea 
                v-model="settingsConfig.ipBlacklist" 
                placeholder="Enter IP addresses (one per line)"
                rows="4"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeSettingsModal">Cancel</button>
          <button class="btn-primary" @click="saveSettings">
            <i class="fas fa-save"></i>
            Save Settings
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
const viewMode = ref('grid')
const timeRange = ref('24')
const showAddRuleModal = ref(false)
const showImportModal = ref(false)
const showSettingsModal = ref(false)
const showAddPolicyModal = ref(false)

// Chart instances
const blockedChart = ref(null)
const allowedChart = ref(null)
const protocolChart = ref(null)

// Firewall stats
const firewallStats = reactive({
  totalRules: 45,
  activeRules: 38,
  blockedAttempts: 1234,
  todayBlocked: 89,
  totalTraffic: '2.4TB',
  allowedTraffic: '2.3TB',
  securityScore: 94
})

// Traffic stats
const trafficStats = reactive({
  blocked: 45678,
  blockedHour: 123,
  blockedToday: 89,
  allowed: 45234,
  allowedHour: 234,
  allowedToday: 234,
  protocols: { http: 1234, https: 4567 },
  topSources: [
    { ip: '192.168.1.1', count: 45 },
    { ip: '10.0.0.1', count: 23 },
    { ip: '172.16.0.1', count: 12 }
  ]
})

// Rule form
const ruleForm = reactive({
  name: '',
  description: '',
  type: 'allow',
  protocol: 'tcp',
  source: '',
  destination: '',
  port: 80,
  priority: 'medium',
  logLevel: 'info',
  timeRange: '1',
  rateLimit: 100
})

// Policy form
const policyForm = reactive({
  name: '',
  description: '',
  type: 'intrusion-prevention',
  severity: 'warning',
  triggerCondition: '',
  responseAction: 'log',
  autoRemediation: 'yes'
})

// Settings form
const settingsConfig = reactive({
  defaultAction: 'deny',
  logLevel: 'info',
  logRetention: '30',
  alertEmail: '',
  alertThreshold: 10,
  blockDuration: '300',
  ipWhitelist: '',
  ipBlacklist: ''
})

// Mock data
const rules = ref([
  {
    id: 1,
    name: 'Block Malware IPs',
    description: 'Block known malicious IP addresses',
    type: 'deny',
    protocol: 'tcp',
    source: 'any',
    destination: 'any',
    port: 'any',
    priority: 'high',
    logLevel: 'critical',
    status: 'active',
    createdAt: '2024-01-21T10:30:00Z',
    updatedAt: '2024-01-21T10:30:00Z'
  },
  {
    id: 2,
    name: 'Allow HTTP Traffic',
    description: 'Allow all HTTP traffic',
    type: 'allow',
    protocol: 'tcp',
    source: 'any',
    destination: 'any',
    port: 80,
    priority: 'medium',
    logLevel: 'info',
    status: 'active',
    createdAt: '2024-01-21T10:30:00Z',
    updatedAt: '2024-01-21T10:30:00Z'
  },
  {
    id: 3,
    name: 'Block SSH Brute Force',
    description: 'Block SSH brute force attempts',
    type: 'deny',
    protocol: 'tcp',
    source: 'any',
    destination: 'any',
    port: 22,
    priority: 'critical',
    logLevel: 'critical',
    status: 'active',
    createdAt: '2024-01-21T10:30:00Z',
    updatedAt: '2024-01-21T10:30:00Z'
  },
  {
    id: 4,
    name: 'Log Suspicious Activity',
    description: 'Log suspicious network activity',
    type: 'log',
    protocol: 'any',
    source: 'any',
    destination: 'any',
    port: 'any',
    priority: 'medium',
    logLevel: 'warning',
    status: 'active',
    createdAt: '2024-01-21T10:30:00Z',
    updatedAt: '2024-01-21T10:30:00Z'
  }
])

const policies = ref([
  {
    id: 1,
    name: 'Intrusion Prevention',
    description: 'Prevent known intrusion attempts',
    type: 'intrusion-prevention',
    severity: 'warning',
    triggerCondition: 'Multiple failed login attempts',
    responseAction: 'block',
    enabled: true,
    triggerCount: 5,
    createdAt: '2024-01-21T10:30:00Z',
    updatedAt: '2024-01-21T10:30:00Z'
  },
  {
    id: 2,
    name: 'Malware Detection',
    description: 'Detect and block malware threats',
    type: 'malware-detection',
    severity: 'critical',
    triggerCondition: 'Malware signature detected',
    responseAction: 'quarantine',
    enabled: true,
    triggerCount: 12,
    createdAt: '2024-01-21T10:30:00Z',
    updatedAt: '2024-01-21T10:30:00Z'
  },
  {
    id: 3,
    name: 'Data Protection',
    description: 'Protect sensitive data access',
    type: 'data-protection',
    severity: 'high',
    triggerCondition: 'Unauthorized data access attempt',
    responseAction: 'block',
    enabled: true,
    triggerCount: 3,
    createdAt: '2024-01-21T10:30:00Z',
    updatedAt: '2024-01-21T10:30:00Z'
  }
])

// Computed properties
const filteredRules = computed(() => {
  let filtered = rules.value

  if (statusFilter.value) {
    filtered = filtered.filter(rule => rule.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(rule => rule.type === typeFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
})

// Methods
const loadFirewallData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/firewall')
    // if (response.success) {
    //   rules.value = response.rules || []
    //   policies.value = response.policies || []
    //   Object.assign(firewallStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading firewall data:', error)
    showError('Failed to load firewall data')
  } finally {
    loading.value = false
  }
}

const filterRules = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || typeFilter.value) {
    return 'No firewall rules match your filter criteria'
  }
  return 'No firewall rules found'
}

const getRuleIcon = (type) => {
  const icons = {
    'allow': 'fas fa-check-circle',
    'deny': 'fas fa-ban',
    'log': 'fas fa-file-alt',
    'rate-limit': 'fas fa-tachometer-alt'
  }
  return icons[type] || 'fas fa-shield-alt'
}

const getPolicyIcon = (type) => {
  const icons = {
    'intrusion-prevention': 'fas fa-shield-alt',
    'malware-detection': 'fas fa-bug',
    'data-protection': 'fas fa-lock',
    'access-control': 'fas fa-user-shield',
    'audit-logging': 'fas fa-clipboard-list',
    'compliance': 'fas fa-check-circle'
  }
  return icons[type] || 'fas fa-shield-alt'
}

const getSecurityClass = (score) => {
  if (score >= 95) return 'excellent'
  if (score >= 90) return 'good'
  if (score >= 80) return 'fair'
  return 'poor'
}

const getSecurityStatus = (score) => {
  if (score >= 95) return 'Excellent'
  if (score >= 90) return 'Good'
  if (score >= 80) return 'Fair'
  return 'Needs Improvement'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const testRule = async (rule) => {
  try {
    // const response = await apiPost(`/firewall/rules/${rule.id}/test`)
    // if (response.success) {
    //   showSuccess('Rule test completed successfully')
    // }
    
    // For demo, simulate test
    showSuccess('Rule test completed successfully')
  } catch (error) {
    console.error('Error testing rule:', error)
    showError('Failed to test rule')
  }
}

const editRule = (rule) => {
  // Open rule edit modal or navigate to detailed view
  showSuccess(`Editing rule: ${rule.name}`)
}

const toggleRule = async (rule) => {
  try {
    // const response = await apiPut(`/firewall/rules/${rule.id}/toggle`)
    // if (response.success) {
    //   rule.status = rule.status === 'active' ? 'inactive' : 'active'
    //   showSuccess(`Rule ${rule.status === 'active' ? 'activated' : 'deactivated'}`)
    // }
    
    // For demo, simulate toggle
    rule.status = rule.status === 'active' ? 'inactive' : 'active'
    showSuccess(`Rule ${rule.status === 'active' ? 'activated' : 'deactivated'}`)
  } catch (error) {
    console.error('Error toggling rule:', error)
    showError('Failed to toggle rule')
  }
}

const testFirewall = async () => {
  try {
    // const response = await apiPost('/firewall/test')
    // if (response.success) {
    //   Object.assign(firewallStats, response.stats)
    //   showSuccess('Firewall test completed')
    // }
    
    // For demo, simulate test
    showSuccess('Firewall test completed')
  } catch (error) {
    console.error('Error testing firewall:', error)
    showError('Failed to test firewall')
  }
}

const addRule = async () => {
  if (!ruleForm.name || !ruleForm.destination) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/firewall/rules', ruleForm)
    // if (response.success) {
    //   rules.value.unshift(response.rule)
    //   showSuccess('Rule added successfully')
    //   closeAddRuleModal()
    //   resetRuleForm()
    // }
    
    // For demo, simulate addition
    const newRule = {
      id: Date.now(),
      ...ruleForm,
      status: 'pending',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    rules.value.unshift(newRule)
    showSuccess('Rule added successfully')
    closeAddRuleModal()
    resetRuleForm()
  } catch (error) {
    console.error('Error adding rule:', error)
    showError('Failed to add rule')
  }
}

const addPolicy = async () => {
  if (!policyForm.name || !policyForm.triggerCondition) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/firewall/policies', policyForm)
    // if (response.success) {
    //   policies.value.unshift(response.policy)
    //   showSuccess('Policy added successfully')
    //   closeAddPolicyModal()
    //   resetPolicyForm()
    // }
    
    // For demo, simulate addition
    const newPolicy = {
      id: Date.now(),
      ...policyForm,
      status: 'active',
      enabled: true,
      triggerCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    policies.value.unshift(newPolicy)
    showSuccess('Policy added successfully')
    closeAddPolicyModal()
    resetPolicyForm()
  } catch (error) {
    console.error('Error adding policy:', error)
    showError('Failed to add policy')
  }
}

const testPolicy = async (policy) => {
  try {
    // const response = await apiPost(`/firewall/policies/${policy.id}/test`)
    // if (response.success) {
    //   showSuccess('Policy test completed successfully')
    // }
    
    // For demo, simulate test
    showSuccess('Policy test completed successfully')
  } catch (error) {
    console.error('Error testing policy:', error)
    showError('Failed to test policy')
  }
}

const editPolicy = (policy) => {
  // Open policy edit modal or navigate to detailed view
  showSuccess(`Editing policy: ${policy.name}`)
}

const togglePolicy = async (policy) => {
  try {
    // const response = await apiPut(`/firewall/policies/${policy.id}/toggle`)
    // if (response.success) {
    //   policy.enabled = !policy.enabled
    //   showSuccess(`Policy ${policy.enabled ? 'enabled' : 'disabled'}`)
    // }
    
    // For demo, simulate toggle
    policy.enabled = !policy.enabled
    showSuccess(`Policy ${policy.enabled ? 'enabled' : 'disabled'}`)
  } catch (error) {
    console.error('Error toggling policy:', error)
    showError('Failed to toggle policy')
  }
}

const saveSettings = async () => {
  try {
    // const response = await apiPut('/firewall/settings', settingsConfig)
    // if (response.success) {
    //   Object.assign(settingsConfig, response.settings)
    //   showSuccess('Settings saved successfully')
    // }
    
    // For demo, simulate save
    showSuccess('Settings saved successfully')
  } catch (error) {
    console.error('Error saving settings:', error)
    showError('Failed to save settings')
  }
}

const closeAddRuleModal = () => {
  showAddRuleModal.value = false
  resetRuleForm()
}

const closeImportModal = () => {
  showImportModal.value = false
}

const closeSettingsModal = () => {
  showSettingsModal.value = false
}

const resetRuleForm = () => {
  Object.assign(ruleForm, {
    name: '',
    description: '',
    type: 'allow',
    protocol: 'tcp',
    source: '',
    destination: '',
    port: 80,
    priority: 'medium',
    logLevel: 'info',
    timeRange: '1',
    rateLimit: 100
  })
}

const resetPolicyForm = () => {
  Object.assign(policyForm, {
    name: '',
    description: '',
    type: 'intrusion-prevention',
    severity: 'warning',
    triggerCondition: '',
    responseAction: 'log',
    autoRemediation: 'yes'
  })
}

const resetSettingsForm = () => {
  Object.assign(settingsConfig, {
    defaultAction: 'deny',
    logLevel: 'info',
    logRetention: '30',
    alertEmail: '',
    alertThreshold: 10,
    blockDuration: '300',
    ipWhitelist: '',
    ipBlacklist: ''
  })
}

const updateTrafficData = async () => {
  try {
    // const response = await apiGet('/firewall/traffic', { timeRange: timeRange.value })
    // if (response.success) {
    //   Object.assign(trafficStats, response.traffic)
    //   updateCharts()
    // }
    
    // For demo, simulate update
    updateCharts()
  } catch (error) {
    console.error('Error updating traffic data:', error)
    showError('Failed to update traffic data')
  }
}

const initCharts = () => {
  // Initialize Blocked Traffic chart
  if (blockedChart.value) blockedChart.value.destroy()
  blockedChart.value = new Chart(blockedChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Blocked Traffic',
        data: Array.from({ length: 20 }, () => Math.random() * 1000),
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

  // Initialize Allowed Traffic chart
  if (allowedChart.value) allowedChart.value.destroy()
  allowedChart.value = new Chart(allowedChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: Array.from({ length: 20 }, (_, i) => `${i * 5}m`),
      datasets: [{
        label: 'Allowed Traffic',
        data: Array.from({ length: 20 }, () => Math.random() * 1000),
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

  // Initialize Protocol Distribution chart
  if (protocolChart.value) protocolChart.value.destroy()
  protocolChart.value = new Chart(protocolChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['HTTP', 'HTTPS', 'TCP', 'UDP', 'ICMP'],
      datasets: [{
        data: [1234, 4567, 2345, 567],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(6, 182, 212, 0.8)'
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
  if (blockedChart.value) {
    blockedChart.value.data.datasets[0].data.shift()
    blockedChart.value.data.datasets[0].push(trafficStats.blocked)
    blockedChart.value.update('none')
  }

  if (allowedChart.value) {
    allowedChart.value.data.datasets[0].data.shift()
    allowedChart.value.data.datasets[0].push(trafficStats.allowed)
    allowedChart.value.update('none')
  }

  if (protocolChart.value) {
    protocolChart.value.data.datasets[0].data = [
      trafficStats.protocols.http,
      trafficStats.protocols.https,
      trafficStats.protocols.tcp,
      trafficStats.protocols.udp,
      trafficStats.protocols.icmp
    ]
    protocolChart.value.update('none')
  }
}

// Lifecycle
onMounted(() => {
  loadFirewallData()
  initCharts()
})

onUnmounted(() => {
  // Destroy charts
  if (blockedChart.value) blockedChart.value.destroy()
  if (allowedChart.value) allowedChart.value.destroy()
  if (protocolChart.value) protocolChart.value.destroy()
})
</script>

<style scoped>
.firewall {
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

.card-icon.blocked {
  background: var(--danger-color);
}

.card-icon.traffic {
  background: var(--info-color);
}

.card-icon.security {
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

.rule-count,
.blocked-count,
.traffic-status,
.security-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.rule-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.blocked-count {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.traffic-status {
  color: var(--text-secondary);
}

.security-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.security-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.security-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.security-status.poor {
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

.add-rule-btn,
.import-btn,
.test-btn,
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

.add-rule-btn:hover,
.import-btn:hover,
.test-btn:hover,
.settings-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.import-btn {
  background: var(--success-color);
}

.import-btn:hover {
  background: var(--success-hover);
}

.test-btn {
  background: var(--warning-color);
}

.test-btn:hover {
  background: var(--warning-hover);
}

.settings-btn {
  background: var(--info-color);
}

.settings-btn:hover {
  background: var(--info-hover);
}

.rules-section,
.policies-section,
.traffic-section {
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

.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.rule-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.rule-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.rule-card.inactive {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.rule-card.pending {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.rule-card.error {
  border-color: var(--danger-color);
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.rule-icon {
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

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.rule-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.rule-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.rule-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.protocol,
.action {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.rule-details {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
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

.rule-actions {
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

.action-btn.test:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.edit:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.toggle.enable:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.disable:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.rule-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.rule-list-card:hover {
  background: var(--glass-bg-hover);
}

.rule-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.rule-list-info {
  flex: 1;
}

.rule-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.rule-list-actions {
  display: flex;
  gap: 0.5rem;
}

.rule-list-actions .action-btn {
  width: 32px;
  height: 32px;
  padding: 0;
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

.rule-list-actions .action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.rule-list-actions .action-btn.enable:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.rule-list-actions .action-btn.disable:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.traffic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.traffic-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.traffic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.traffic-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.traffic-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.traffic-chart {
  height: 150px;
  margin-bottom: 1rem;
}

.traffic-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-secondary);
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

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.source-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.source-ip {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--text-primary);
}

.source-count {
  font-weight: 600;
  color: var(--text-primary);
}

.policies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.policy-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.policy-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.policy-card.inactive {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.policy-card.error {
  border-color: var(--danger-color);
}

.policy-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.policy-icon {
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

.policy-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.policy-status.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.policy-status.inactive {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.policy-status.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.policy-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.policy-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.policy-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.severity,
.enabled {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.enabled {
  color: #10b981;
}

.disabled {
  color: #ef4444;
}

.policy-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
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

.detail-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.policy-actions {
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

.action-btn.test:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.edit:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.toggle.enable:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.disable:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
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

.rule-form,
.import-form,
.policy-form,
.settings-form {
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

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.nameservers-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.nameserver-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nameserver-item input {
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

.add-domain-btn {
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

.add-domain-btn:hover {
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
  .firewall {
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
  
  .rules-grid {
    grid-template-columns: 1fr;
  }
  
  .rules-list {
    grid-template-columns: 1fr;
  }
  
  .rule-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .rule-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .rule-list-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .traffic-grid {
    grid-template-columns: 1fr;
  }
  
  .security-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
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
