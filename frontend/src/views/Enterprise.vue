<template>
  <div class="enterprise">
    <div class="page-header">
      <h1>Enterprise Solutions</h1>
      <p>Scalable solutions for large organizations</p>
    </div>

    <!-- Enterprise Overview -->
    <div class="overview-section">
      <div class="section-header">
        <h2>Your Enterprise Account</h2>
      </div>
      
      <div class="overview-card">
        <div class="overview-header">
          <div class="enterprise-info">
            <div class="enterprise-icon">
              <i class="fas fa-building"></i>
            </div>
            <div class="enterprise-details">
              <h3>{{ enterpriseStatus.plan }}</h3>
              <p>{{ enterpriseStatus.description }}</p>
            </div>
          </div>
          <div class="status-badge">
            <span :class="['badge', enterpriseStatus.status]">{{ formatStatus(enterpriseStatus.status) }}</span>
          </div>
        </div>
        
        <div class="overview-stats">
          <div class="stat-item">
            <div class="stat-value">{{ enterpriseStats.totalUsers }}</div>
            <div class="stat-label">Total Users</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ enterpriseStats.activeProjects }}</div>
            <div class="stat-label">Active Projects</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ enterpriseStats.dataProcessed }}</div>
            <div class="stat-label">Data Processed (TB)</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ enterpriseStats.apiCalls }}</div>
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
        <div class="action-card" @click="showUserModal = true">
          <div class="action-icon">
            <i class="fas fa-users"></i>
          </div>
          <h3>User Management</h3>
          <p>Manage enterprise users</p>
        </div>
        
        <div class="action-card" @click="viewProjects">
          <div class="action-icon projects">
            <i class="fas fa-project-diagram"></i>
          </div>
          <h3>Projects</h3>
          <p>Manage enterprise projects</p>
        </div>
        
        <div class="action-card" @click="viewSecurity">
          <div class="action-icon security">
            <i class="fas fa-shield-alt"></i>
          </div>
          <h3>Security</h3>
          <p>Configure security settings</p>
        </div>
        
        <div class="action-card" @click="viewBilling">
          <div class="action-icon billing">
            <i class="fas fa-credit-card"></i>
          </div>
          <h3>Billing</h3>
          <p>View billing and usage</p>
        </div>
      </div>
    </div>

    <!-- Enterprise Features -->
    <div class="features-section">
      <div class="section-header">
        <h2>Enterprise Features</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="featureFilter" @change="filterFeatures">
              <option value="">All Features</option>
              <option value="security">Security</option>
              <option value="collaboration">Collaboration</option>
              <option value="analytics">Analytics</option>
              <option value="integration">Integration</option>
              <option value="automation">Automation</option>
            </select>
          </div>
        </div>
      </div>

      <div class="features-grid">
        <div 
          v-for="feature in filteredFeatures" 
          :key="feature.id"
          class="feature-card"
          :class="{ 'disabled': !feature.enabled }"
        >
          <div class="feature-header">
            <div class="feature-icon">
              <i :class="feature.icon"></i>
            </div>
            <div class="feature-meta">
              <span :class="['status-badge', feature.enabled ? 'enabled' : 'disabled']">
                {{ feature.enabled ? 'Enabled' : 'Disabled' }}
              </span>
              <span class="feature-category">{{ feature.category }}</span>
            </div>
          </div>
          
          <div class="feature-content">
            <h3>{{ feature.name }}</h3>
            <p>{{ feature.description }}</p>
            
            <div class="feature-benefits">
              <h4>Key Benefits:</h4>
              <ul>
                <li v-for="benefit in feature.benefits" :key="benefit" class="benefit-item">
                  <i class="fas fa-check"></i>
                  {{ benefit }}
                </li>
              </ul>
            </div>
            
            <div class="feature-usage" v-if="feature.enabled">
              <div class="usage-stats">
                <div class="usage-item">
                  <label>Active Users:</label>
                  <span>{{ feature.usage.activeUsers }}</span>
                </div>
                <div class="usage-item">
                  <label>Monthly Usage:</label>
                  <span>{{ feature.usage.monthlyUsage }}</span>
                </div>
                <div class="usage-item">
                  <label>Last 30 Days:</label>
                  <span>{{ feature.usage.last30Days }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="feature-footer">
            <div class="feature-actions">
              <button 
                v-if="feature.enabled"
                class="action-btn configure" 
                @click="configureFeature(feature)"
              >
                <i class="fas fa-cog"></i>
                Configure
              </button>
              <button 
                v-else
                class="action-btn enable" 
                @click="enableFeature(feature)"
              >
                <i class="fas fa-power-off"></i>
                Enable
              </button>
              <button class="action-btn docs" @click="viewDocumentation(feature)">
                <i class="fas fa-book"></i>
                Documentation
              </button>
            </div>
            <div class="feature-compliance">
              <span class="compliance-badge" :class="feature.compliance">
                {{ feature.compliance }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Management -->
    <div class="users-section">
      <div class="section-header">
        <h2>User Management</h2>
        <div class="header-actions">
          <div class="search-box">
            <input 
              v-model="userSearch" 
              type="text" 
              placeholder="Search users..."
              @input="searchUsers"
            />
            <i class="fas fa-search"></i>
          </div>
          <div class="filter-dropdown">
            <select v-model="userFilter" @change="filterUsers">
              <option value="">All Users</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="admin">Admin</option>
              <option value="user">Regular User</option>
            </select>
          </div>
          <button class="create-btn" @click="showUserModal = true">
            <i class="fas fa-user-plus"></i>
            Add User
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading users...</p>
      </div>

      <div v-else-if="filteredUsers.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-users"></i>
        </div>
        <h3>No users found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showUserModal = true">
          <i class="fas fa-plus"></i>
          Add Your First User
        </button>
      </div>

      <div v-else class="users-table">
        <div class="table-header">
          <div class="header-cell">User</div>
          <div class="header-cell">Role</div>
          <div class="header-cell">Department</div>
          <div class="header-cell">Status</div>
          <div class="header-cell">Last Active</div>
          <div class="header-cell">Actions</div>
        </div>
        
        <div 
          v-for="user in paginatedUsers" 
          :key="user.id"
          class="table-row"
        >
          <div class="table-cell">
            <div class="user-info">
              <div class="user-avatar">
                <img :src="user.avatar" :alt="user.name" />
              </div>
              <div class="user-details">
                <span class="user-name">{{ user.name }}</span>
                <span class="user-email">{{ user.email }}</span>
              </div>
            </div>
          </div>
          
          <div class="table-cell">
            <span :class="['role-badge', user.role]">{{ formatRole(user.role) }}</span>
          </div>
          
          <div class="table-cell">
            <span class="department">{{ user.department }}</span>
          </div>
          
          <div class="table-cell">
            <span :class="['status-badge', user.status]">{{ formatUserStatus(user.status) }}</span>
          </div>
          
          <div class="table-cell">
            <span class="last-active">{{ formatDate(user.lastActive) }}</span>
          </div>
          
          <div class="table-cell">
            <div class="user-actions">
              <button class="action-btn edit" @click="editUser(user)">
                <i class="fas fa-edit"></i>
              </button>
              <button class="action-btn reset" @click="resetPassword(user)">
                <i class="fas fa-key"></i>
              </button>
              <button class="action-btn delete" @click="deleteUser(user)">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button 
          class="pagination-btn" 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Projects Management -->
    <div class="projects-section">
      <div class="section-header">
        <h2>Enterprise Projects</h2>
        <div class="header-actions">
          <button class="create-btn" @click="showProjectModal = true">
            <i class="fas fa-plus"></i>
            New Project
          </button>
        </div>
      </div>

      <div class="projects-grid">
        <div 
          v-for="project in projects" 
          :key="project.id"
          class="project-card"
          :class="{ 'archived': project.status === 'archived' }"
        >
          <div class="project-header">
            <div class="project-info">
              <h3>{{ project.name }}</h3>
              <span :class="['status-badge', project.status]">{{ formatProjectStatus(project.status) }}</span>
            </div>
            <div class="project-actions">
              <button class="action-btn settings" @click="configureProject(project)">
                <i class="fas fa-cog"></i>
              </button>
            </div>
          </div>
          
          <div class="project-content">
            <p>{{ project.description }}</p>
            
            <div class="project-stats">
              <div class="stat-item">
                <label>Team Members:</label>
                <span>{{ project.teamMembers }}</span>
              </div>
              <div class="stat-item">
                <label>Tasks:</label>
                <span>{{ project.tasks }}</span>
              </div>
              <div class="stat-item">
                <label>Progress:</label>
                <span>{{ project.progress }}%</span>
              </div>
              <div class="stat-item">
                <label>Created:</label>
                <span>{{ formatDate(project.createdAt) }}</span>
              </div>
            </div>
            
            <div class="project-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: project.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ project.progress }}% complete</span>
            </div>
          </div>
          
          <div class="project-footer">
            <div class="project-team">
              <div class="team-avatars">
                <img 
                  v-for="member in project.team.slice(0, 4)" 
                  :key="member.id"
                  :src="member.avatar" 
                  :alt="member.name"
                  :title="member.name"
                />
                <span class="more-members" v-if="project.team.length > 4">
                  +{{ project.team.length - 4 }}
                </span>
              </div>
            </div>
            <div class="project-deadline">
              <span class="deadline-label">Deadline:</span>
              <span class="deadline-date">{{ formatDate(project.deadline) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Security & Compliance -->
    <div class="security-section">
      <div class="section-header">
        <h2>Security & Compliance</h2>
        <div class="header-actions">
          <button class="audit-btn" @click="runSecurityAudit">
            <i class="fas fa-shield-alt"></i>
            Run Security Audit
          </button>
        </div>
      </div>

      <div class="security-grid">
        <div class="security-card">
          <div class="security-header">
            <h3>Security Overview</h3>
            <div class="security-score">
              <span class="score-value">{{ security.overallScore }}</span>
              <span class="score-label">Security Score</span>
            </div>
          </div>
          
          <div class="security-metrics">
            <div class="metric-item">
              <label>Authentication:</label>
              <span :class="['metric-value', security.authentication]">{{ security.authentication }}</span>
            </div>
            <div class="metric-item">
              <label>Data Encryption:</label>
              <span :class="['metric-value', security.encryption]">{{ security.encryption }}</span>
            </div>
            <div class="metric-item">
              <label>Access Control:</label>
              <span :class="['metric-value', security.accessControl]">{{ security.accessControl }}</span>
            </div>
            <div class="metric-item">
              <label>Monitoring:</label>
              <span :class="['metric-value', security.monitoring]">{{ security.monitoring }}</span>
            </div>
          </div>
        </div>

        <div class="security-card">
          <div class="security-header">
            <h3>Compliance Status</h3>
            <div class="compliance-score">
              <span class="score-value">{{ compliance.overallScore }}%</span>
              <span class="score-label">Compliance</span>
            </div>
          </div>
          
          <div class="compliance-standards">
            <div 
              v-for="standard in compliance.standards" 
              :key="standard.name"
              class="standard-item"
            >
              <div class="standard-info">
                <span class="standard-name">{{ standard.name }}</span>
                <span :class="['standard-status', standard.status]">{{ standard.status }}</span>
              </div>
              <div class="standard-details">
                <span class="standard-score">{{ standard.score }}%</span>
                <span class="standard-date">Updated: {{ formatDate(standard.lastUpdated) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add User Modal -->
    <div v-if="showUserModal" class="modal-overlay" @click="closeUserModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add New User</h2>
          <button class="close-btn" @click="closeUserModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="user-form">
            <div class="form-grid">
              <div class="form-group">
                <label>First Name *</label>
                <input 
                  v-model="userForm.firstName" 
                  type="text" 
                  placeholder="Enter first name"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>Last Name *</label>
                <input 
                  v-model="userForm.lastName" 
                  type="text" 
                  placeholder="Enter last name"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label>Email Address *</label>
              <input 
                v-model="userForm.email" 
                type="email" 
                placeholder="Enter email address"
                required
              />
            </div>

            <div class="form-group">
              <label>Phone Number</label>
              <input 
                v-model="userForm.phone" 
                type="tel" 
                placeholder="Enter phone number"
              />
            </div>
          </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Role *</label>
                <select v-model="userForm.role" required>
                  <option value="">Select role</option>
                  <option value="admin">Administrator</option>
                  <option value="manager">Manager</option>
                  <option value="user">Regular User</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Department *</label>
                <select v-model="userForm.department" required>
                  <option value="">Select department</option>
                  <option value="engineering">Engineering</option>
                  <option value="sales">Sales</option>
                  <option value="marketing">Marketing</option>
                  <option value="support">Support</option>
                  <option value="hr">Human Resources</option>
                  <option value="finance">Finance</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Permissions</label>
              <div class="permission-selection">
                <label class="checkbox-item" v-for="permission in availablePermissions" :key="permission">
                  <input 
                    type="checkbox" 
                    :value="permission"
                    v-model="userForm.permissions"
                  />
                  <span>{{ permission }}</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Notes</label>
              <textarea 
                v-model="userForm.notes" 
                placeholder="Add any additional notes about this user"
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeUserModal">Cancel</button>
          <button class="btn-primary" @click="addUser">
            <i class="fas fa-user-plus"></i>
            Add User
          </button>
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
const featureFilter = ref('')
const userSearch = ref('')
const userFilter = ref('')
const currentPage = ref(1)
const usersPerPage = ref(10)
const showUserModal = ref(false)
const showProjectModal = ref(false)

// Enterprise status
const enterpriseStatus = reactive({
  plan: 'Enterprise Plus',
  description: 'Full enterprise suite with unlimited users and advanced features',
  status: 'active',
  joinedDate: '2023-06-15T00:00:00Z'
})

// Enterprise stats
const enterpriseStats = reactive({
  totalUsers: 1250,
  activeProjects: 45,
  dataProcessed: 850,
  apiCalls: 125000
})

// Security and compliance
const security = reactive({
  overallScore: 92,
  authentication: 'Strong',
  encryption: 'AES-256',
  accessControl: 'Role-Based',
  monitoring: '24/7'
})

const compliance = reactive({
  overallScore: 94,
  standards: [
    {
      name: 'GDPR',
      status: 'Compliant',
      score: 98,
      lastUpdated: '2024-01-15T00:00:00Z'
    },
    {
      name: 'SOC 2',
      status: 'Compliant',
      score: 95,
      lastUpdated: '2024-01-10T00:00:00Z'
    },
    {
      name: 'ISO 27001',
      status: 'In Progress',
      score: 88,
      lastUpdated: '2024-01-20T00:00:00Z'
    },
    {
      name: 'HIPAA',
      status: 'Compliant',
      score: 96,
      lastUpdated: '2024-01-12T00:00:00Z'
    }
  ]
})

// User form
const userForm = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  role: '',
  department: '',
  permissions: [],
  notes: ''
})

// Available permissions
const availablePermissions = [
  'User Management',
  'Project Management',
  'Analytics Access',
  'API Access',
  'Billing Access',
  'Security Settings',
  'Report Generation',
  'Data Export'
]

// Enterprise features
const enterpriseFeatures = ref([
  {
    id: 1,
    name: 'Advanced Security',
    description: 'Enterprise-grade security with multi-factor authentication and advanced threat protection',
    category: 'security',
    icon: 'fas fa-shield-alt',
    enabled: true,
    compliance: 'SOC 2',
    benefits: [
      'Multi-factor authentication',
      'Advanced threat detection',
      'Role-based access control',
      'Security audit logs'
    ],
    usage: {
      activeUsers: 1250,
      monthlyUsage: 45000,
      last30Days: 125000
    }
  },
  {
    id: 2,
    name: 'Team Collaboration',
    description: 'Advanced collaboration tools with real-time editing and communication',
    category: 'collaboration',
    icon: 'fas fa-users',
    enabled: true,
    compliance: 'GDPR',
    benefits: [
      'Real-time collaboration',
      'Document sharing',
      'Video conferencing',
      'Team workspaces'
    ],
    usage: {
      activeUsers: 980,
      monthlyUsage: 32000,
      last30Days: 89000
    }
  },
  {
    id: 3,
    name: 'Business Analytics',
    description: 'Comprehensive analytics dashboard with custom reporting and insights',
    category: 'analytics',
    icon: 'fas fa-chart-line',
    enabled: true,
    compliance: 'GDPR',
    benefits: [
      'Custom dashboards',
      'Advanced reporting',
      'Predictive analytics',
      'Data visualization'
    ],
    usage: {
      activeUsers: 650,
      monthlyUsage: 18000,
      last30Days: 54000
    }
  },
  {
    id: 4,
    name: 'API Integration',
    description: 'Full API access with webhooks and extensive documentation',
    category: 'integration',
    icon: 'fas fa-plug',
    enabled: false,
    compliance: 'SOC 2',
    benefits: [
      'RESTful API',
      'Webhook support',
      'Extensive documentation',
      'Rate limiting'
    ],
    usage: {
      activeUsers: 0,
      monthlyUsage: 0,
      last30Days: 0
    }
  },
  {
    id: 5,
    name: 'Workflow Automation',
    description: 'Automate business processes with custom workflows and triggers',
    category: 'automation',
    icon: 'fas fa-robot',
    enabled: false,
    compliance: 'GDPR',
    benefits: [
      'Custom workflows',
      'Trigger-based automation',
      'Process optimization',
      'Integration with existing tools'
    ],
    usage: {
      activeUsers: 0,
      monthlyUsage: 0,
      last30Days: 0
    }
  }
])

// Users data
const users = ref([
  {
    id: 1,
    name: 'John Anderson',
    email: 'john.anderson@enterprise.com',
    role: 'admin',
    department: 'engineering',
    status: 'active',
    lastActive: '2024-01-21T10:30:00Z',
    avatar: '/api/placeholder/40x40'
  },
  {
    id: 2,
    name: 'Sarah Mitchell',
    email: 'sarah.mitchell@enterprise.com',
    role: 'manager',
    department: 'sales',
    status: 'active',
    lastActive: '2024-01-21T09:15:00Z',
    avatar: '/api/placeholder/40x40'
  },
  {
    id: 3,
    name: 'Michael Chen',
    email: 'michael.chen@enterprise.com',
    role: 'user',
    department: 'marketing',
    status: 'inactive',
    lastActive: '2024-01-15T14:30:00Z',
    avatar: '/api/placeholder/40x40'
  }
])

// Projects data
const projects = ref([
  {
    id: 1,
    name: 'Q1 Product Launch',
    description: 'Enterprise product launch initiative for Q1 2024',
    status: 'active',
    teamMembers: 12,
    tasks: 45,
    progress: 75,
    createdAt: '2024-01-01T00:00:00Z',
    deadline: '2024-03-31T00:00:00Z',
    team: [
      { id: 1, name: 'John Anderson', avatar: '/api/placeholder/40x40' },
      { id: 2, name: 'Sarah Mitchell', avatar: '/api/placeholder/40x40' },
      { id: 3, name: 'David Kim', avatar: '/api/placeholder/40x40' },
      { id: 4, name: 'Emily Davis', avatar: '/api/placeholder/40x40' },
      { id: 5, name: 'Robert Wilson', avatar: '/api/placeholder/40x40' }
    ]
  },
  {
    id: 2,
    name: 'Security Audit 2024',
    description: 'Comprehensive security audit and compliance review',
    status: 'active',
    teamMembers: 8,
    tasks: 32,
    progress: 60,
    createdAt: '2024-01-10T00:00:00Z',
    deadline: '2024-02-15T00:00:00Z',
    team: [
      { id: 6, name: 'Lisa Park', avatar: '/api/placeholder/40x40' },
      { id: 7, name: 'James Brown', avatar: '/api/placeholder/40x40' },
      { id: 8, name: 'Maria Garcia', avatar: '/api/placeholder/40x40' }
    ]
  },
  {
    id: 3,
    name: 'Infrastructure Upgrade',
    description: 'Complete infrastructure modernization project',
    status: 'archived',
    teamMembers: 15,
    tasks: 68,
    progress: 100,
    createdAt: '2023-09-01T00:00:00Z',
    deadline: '2023-12-31T00:00:00Z',
    team: [
      { id: 9, name: 'Tom Harris', avatar: '/api/placeholder/40x40' },
      { id: 10, name: 'Nina Patel', avatar: '/api/placeholder/40x40' },
      { id: 11, name: 'Chris Martin', avatar: '/api/placeholder/40x40' }
    ]
  }
])

// Computed properties
const filteredFeatures = computed(() => {
  let filtered = enterpriseFeatures.value

  if (featureFilter.value) {
    filtered = filtered.filter(feature => feature.category === featureFilter.value)
  }

  return filtered.sort((a, b) => {
    if (a.enabled && !b.enabled) return -1
    if (!a.enabled && b.enabled) return 1
    return 0
  })
})

const filteredUsers = computed(() => {
  let filtered = users.value

  if (userSearch.value) {
    const query = userSearch.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    )
  }

  if (userFilter.value) {
    filtered = filtered.filter(user => user.role === userFilter.value || user.status === userFilter.value)
  }

  return filtered
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * usersPerPage.value
  const end = start + usersPerPage.value
  return filteredUsers.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / usersPerPage.value)
})

// Methods
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatRole = (role) => {
  return role.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatUserStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatProjectStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getEmptyMessage = () => {
  if (userSearch.value || userFilter.value) {
    return 'No users match your search criteria'
  }
  return 'No users found'
}

const filterFeatures = () => {
  // Filtering is handled by computed property
}

const searchUsers = () => {
  // Search is handled by computed property
}

const filterUsers = () => {
  // Filtering is handled by computed property
  currentPage.value = 1
}

const viewProjects = () => {
  showSuccess('Opening enterprise projects')
}

const viewSecurity = () => {
  showSuccess('Opening security settings')
}

const viewBilling = () => {
  showSuccess('Opening billing and usage')
}

const configureFeature = (feature) => {
  showSuccess(`Opening configuration for ${feature.name}`)
}

const enableFeature = async (feature) => {
  try {
    // const response = await apiPost(`/enterprise/features/${feature.id}/enable`)
    // if (response.success) {
    //   feature.enabled = true
    //   showSuccess('Feature enabled successfully')
    // }
    
    // For demo, simulate enable
    feature.enabled = true
    showSuccess('Feature enabled successfully')
  } catch (error) {
    console.error('Error enabling feature:', error)
    showError('Failed to enable feature')
  }
}

const viewDocumentation = (feature) => {
  showSuccess(`Opening documentation for ${feature.name}`)
}

const editUser = (user) => {
  showSuccess(`Editing user: ${user.name}`)
}

const resetPassword = async (user) => {
  const confirmed = await showConfirm(`Are you sure you want to reset password for ${user.name}?`)
  if (confirmed) {
    try {
      // const response = await apiPost(`/enterprise/users/${user.id}/reset-password`)
      // if (response.success) {
      //   showSuccess('Password reset email sent')
      // }
      
      // For demo, simulate reset
      showSuccess('Password reset email sent')
    } catch (error) {
      console.error('Error resetting password:', error)
      showError('Failed to reset password')
    }
  }
}

const deleteUser = async (user) => {
  const confirmed = await showConfirm(`Are you sure you want to delete user ${user.name}?`)
  if (confirmed) {
    try {
      // const response = await apiDelete(`/enterprise/users/${user.id}`)
      // if (response.success) {
      //   const index = users.value.findIndex(u => u.id === user.id)
      //   users.value.splice(index, 1)
      //   showSuccess('User deleted successfully')
      // }
      
      // For demo, simulate deletion
      const index = users.value.findIndex(u => u.id === user.id)
      users.value.splice(index, 1)
      showSuccess('User deleted successfully')
    } catch (error) {
      console.error('Error deleting user:', error)
      showError('Failed to delete user')
    }
  }
}

const configureProject = (project) => {
  showSuccess(`Opening project configuration for ${project.name}`)
}

const runSecurityAudit = () => {
  showSuccess('Initiating security audit...')
}

const closeUserModal = () => {
  showUserModal.value = false
  resetUserForm()
}

const resetUserForm = () => {
  Object.assign(userForm, {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: '',
    department: '',
    permissions: [],
    notes: ''
  })
}

const addUser = async () => {
  if (!userForm.firstName || !userForm.lastName || !userForm.email || !userForm.role || !userForm.department) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/enterprise/users', userForm)
    // if (response.success) {
    //   users.value.unshift(response.user)
    //   showSuccess('User added successfully')
    //   closeUserModal()
    //   resetUserForm()
    // }
    
    // For demo, simulate addition
    const newUser = {
      id: Date.now(),
      name: `${userForm.firstName} ${userForm.lastName}`,
      email: userForm.email,
      role: userForm.role,
      department: userForm.department,
      status: 'active',
      lastActive: new Date().toISOString(),
      avatar: '/api/placeholder/40x40'
    }
    
    users.value.unshift(newUser)
    showSuccess('User added successfully')
    closeUserModal()
    resetUserForm()
  } catch (error) {
    console.error('Error adding user:', error)
    showError('Failed to add user')
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/enterprise')
    // if (response.success) {
    //   enterpriseFeatures.value = response.features || []
    //   users.value = response.users || []
    //   projects.value = response.projects || []
    //   Object.assign(enterpriseStatus, response.status)
    //   Object.assign(enterpriseStats, response.stats)
    //   Object.assign(security, response.security)
    //   Object.assign(compliance, response.compliance)
    // }
    
    // For demo, use mock data
    loading.value = false
  } catch (error) {
    console.error('Error loading enterprise data:', error)
    showError('Failed to load enterprise data')
    loading.value = false
  }
})
</script>

<style scoped>
.enterprise {
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

.overview-section,
.actions-section,
.features-section,
.users-section,
.projects-section,
.security-section {
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

.overview-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.enterprise-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.enterprise-icon {
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

.enterprise-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.enterprise-details p {
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

.overview-stats {
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

.action-icon.projects {
  background: var(--info-color);
}

.action-icon.security {
  background: var(--warning-color);
}

.action-icon.billing {
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
.audit-btn {
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
.audit-btn:hover {
  background: var(--primary-hover);
}

.create-first-btn {
  margin-top: 2rem;
  align-self: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.feature-card.disabled {
  opacity: 0.6;
  border-left: 4px solid var(--warning-color);
}

.feature-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.feature-icon {
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

.feature-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
}

.status-badge.enabled {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.disabled {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.feature-category {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.feature-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.feature-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.feature-benefits h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.feature-benefits ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.benefit-item {
  padding: 0.25rem 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  position: relative;
  padding-left: 1.5rem;
}

.benefit-item i {
  position: absolute;
  left: 0;
  color: var(--success-color);
  font-size: 0.8rem;
}

.feature-usage {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.usage-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.usage-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.usage-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.usage-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.feature-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  margin-top: 1rem;
}

.feature-actions {
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

.action-btn.configure:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.enable:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.docs:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.compliance-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.compliance-badge.gdpr {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.compliance-badge.soc2 {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box input {
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  width: 250px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  color: var(--text-secondary);
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

.users-table {
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

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  color: var(--text-primary);
  font-weight: 600;
}

.user-email {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.role-badge.admin {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.role-badge.manager {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.role-badge.user {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.role-badge.viewer {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.department {
  color: var(--text-primary);
  font-weight: 600;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.inactive {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.last-active {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.user-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.edit:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.reset:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--glass-bg-hover);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-primary);
  font-weight: 600;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.project-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.project-card.archived {
  opacity: 0.7;
  border-left: 4px solid var(--warning-color);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.project-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.archived {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.project-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.settings:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.project-content {
  padding: 1.5rem;
}

.project-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.project-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.project-stats .detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.project-stats .detail-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.project-stats .detail-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.project-progress {
  margin-top: 1rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  display: block;
  text-align: center;
}

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--glass-bg-tertiary);
  border-top: 1px solid var(--glass-border);
}

.project-team {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.team-avatars {
  display: flex;
  gap: -0.5rem;
}

.team-avatars img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--glass-bg-secondary);
  object-fit: cover;
}

.more-members {
  width: 24px;
  height: 24px;
  background: var(--glass-bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 600;
  border: 2px solid var(--glass-bg-secondary);
  margin-right: -0.5rem;
}

.project-deadline {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-end;
}

.deadline-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.deadline-date {
  color: var(--text-primary);
  font-weight: 600;
}

.security-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.security-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.security-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.security-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.security-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.score-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--success-color);
}

.score-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.security-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.metric-item label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.metric-value {
  font-weight: 600;
  color: var(--text-primary);
}

.metric-value.Strong {
  color: var(--success-color);
}

.metric-value.Medium {
  color: var(--warning-color);
}

.metric-value.Weak {
  color: var(--danger-color);
}

.compliance-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.compliance-score .score-value {
  color: var(--info-color);
}

.compliance-standards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.standard-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.standard-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.standard-name {
  font-weight: 600;
  color: var(--text-primary);
}

.standard-status.Compliant {
  color: var(--success-color);
  font-weight: 600;
}

.standard-status.In Progress {
  color: var(--warning-color);
  font-weight: 600;
}

.standard-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-end;
}

.standard-score {
  font-weight: 600;
  color: var(--text-primary);
}

.standard-date {
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

.user-form {
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
  min-height: 100px;
}

.permission-selection {
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
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

@media (max-width: 768px) {
  .enterprise {
    padding: 1rem;
  }
  
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .search-box input {
    width: 200px;
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
  
  .projects-grid {
    grid-template-columns: 1fr;
  }
  
  .project-stats {
    grid-template-columns: 1fr;
  }
  
  .project-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .security-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .permission-selection {
    grid-template-columns: 1fr;
  }
}
</style>
