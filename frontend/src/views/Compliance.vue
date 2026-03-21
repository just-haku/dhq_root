<template>
  <div class="compliance">
    <div class="page-header">
      <h1>Compliance Center</h1>
      <p>Manage regulatory compliance and audit requirements</p>
    </div>

    <!-- Compliance Overview -->
    <div class="overview-section">
      <div class="section-header">
        <h2>Compliance Overview</h2>
        <div class="header-actions">
          <button class="audit-btn" @click="runComplianceAudit">
            <i class="fas fa-shield-alt"></i>
            Run Audit
          </button>
        </div>
      </div>
      
      <div class="overview-card">
        <div class="overview-header">
          <div class="compliance-info">
            <div class="compliance-icon">
              <i class="fas fa-shield-alt"></i>
            </div>
            <div class="compliance-details">
              <h3>{{ complianceStatus.level }}</h3>
              <p>{{ complianceStatus.description }}</p>
            </div>
          </div>
          <div class="status-badge">
            <span :class="['badge', complianceStatus.status]">{{ formatStatus(complianceStatus.status) }}</span>
          </div>
        </div>
        
        <div class="overview-stats">
          <div class="stat-item">
            <div class="stat-value">{{ complianceStats.overallScore }}%</div>
            <div class="stat-label">Overall Score</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ complianceStats.activeStandards }}</div>
            <div class="stat-label">Active Standards</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ complianceStats.pendingAudits }}</div>
            <div class="stat-label">Pending Audits</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ complianceStats.lastAudit }}</div>
            <div class="stat-label">Last Audit</div>
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
        <div class="action-card" @click="viewStandards">
          <div class="action-icon">
            <i class="fas fa-clipboard-check"></i>
          </div>
          <h3>Standards</h3>
          <p>View compliance standards</p>
        </div>
        
        <div class="action-card" @click="viewAudits">
          <div class="action-icon audits">
            <i class="fas fa-search"></i>
          </div>
          <h3>Audits</h3>
          <p>Manage audit schedule</p>
        </div>
        
        <div class="action-card" @click="viewReports">
          <div class="action-icon reports">
            <i class="fas fa-file-alt"></i>
          </div>
          <h3>Reports</h3>
          <p>Generate compliance reports</p>
        </div>
        
        <div class="action-card" @click="viewPolicies">
          <div class="action-icon policies">
            <i class="fas fa-book"></i>
          </div>
          <h3>Policies</h3>
          <p>Manage compliance policies</p>
        </div>
      </div>
    </div>

    <!-- Compliance Standards -->
    <div class="standards-section">
      <div class="section-header">
        <h2>Compliance Standards</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="standardFilter" @change="filterStandards">
              <option value="">All Standards</option>
              <option value="active">Active</option>
              <option value="pending">Pending</option>
              <option value="non-compliant">Non-Compliant</option>
            </select>
          </div>
          <button class="create-btn" @click="showStandardModal = true">
            <i class="fas fa-plus"></i>
            Add Standard
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading compliance standards...</p>
      </div>

      <div v-else-if="filteredStandards.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-clipboard-check"></i>
        </div>
        <h3>No standards found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showStandardModal = true">
          <i class="fas fa-plus"></i>
          Add Your First Standard
        </button>
      </div>

      <div v-else class="standards-grid">
        <div 
          v-for="standard in filteredStandards" 
          :key="standard.id"
          class="standard-card"
          :class="{ 'non-compliant': standard.status === 'non-compliant' }"
        >
          <div class="standard-header">
            <div class="standard-info">
              <div class="standard-logo">
                <img :src="standard.logo" :alt="standard.name" />
              </div>
              <div class="standard-details">
                <h3>{{ standard.name }}</h3>
                <span :class="['status-badge', standard.status]">{{ formatStandardStatus(standard.status) }}</span>
              </div>
            </div>
            <div class="standard-meta">
              <span class="standard-category">{{ standard.category }}</span>
              <span class="standard-score">{{ standard.score }}%</span>
            </div>
          </div>
          
          <div class="standard-content">
            <p>{{ standard.description }}</p>
            
            <div class="standard-requirements">
              <h4>Key Requirements:</h4>
              <ul>
                <li v-for="requirement in standard.requirements" :key="requirement" class="requirement-item">
                  <i :class="['requirement-icon', getRequirementIcon(requirement.status)]"></i>
                  {{ requirement.text }}
                </li>
              </ul>
            </div>
            
            <div class="standard-progress">
              <div class="progress-header">
                <span>Compliance Progress</span>
                <span>{{ standard.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: standard.progress + '%' }"></div>
              </div>
            </div>
          </div>
          
          <div class="standard-footer">
            <div class="standard-actions">
              <button class="action-btn view" @click="viewStandard(standard)">
                <i class="fas fa-eye"></i>
                View
              </button>
              <button class="action-btn audit" @click="auditStandard(standard)">
                <i class="fas fa-search"></i>
                Audit
              </button>
              <button class="action-btn report" @click="generateReport(standard)">
                <i class="fas fa-file-alt"></i>
                Report
              </button>
            </div>
            <div class="standard-deadline">
              <span class="deadline-label">Next Audit:</span>
              <span class="deadline-date">{{ formatDate(standard.nextAudit) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Audit Schedule -->
    <div class="audits-section">
      <div class="section-header">
        <h2>Audit Schedule</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="auditFilter" @change="filterAudits">
              <option value="">All Audits</option>
              <option value="scheduled">Scheduled</option>
              <option value="in-progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <button class="create-btn" @click="showAuditModal = true">
            <i class="fas fa-plus"></i>
            Schedule Audit
          </button>
        </div>
      </div>

      <div class="audits-timeline">
        <div 
          v-for="audit in filteredAudits" 
          :key="audit.id"
          class="audit-item"
          :class="audit.status"
        >
          <div class="audit-date">
            <div class="date-marker">
              <span class="date-day">{{ getAuditDay(audit.date) }}</span>
              <span class="date-month">{{ getAuditMonth(audit.date) }}</span>
            </div>
          </div>
          
          <div class="audit-content">
            <div class="audit-header">
              <h3>{{ audit.title }}</h3>
              <span :class="['status-badge', audit.status]">{{ formatAuditStatus(audit.status) }}</span>
            </div>
            
            <div class="audit-details">
              <p>{{ audit.description }}</p>
              
              <div class="audit-meta">
                <div class="meta-item">
                  <label>Standard:</label>
                  <span>{{ audit.standard }}</span>
                </div>
                <div class="meta-item">
                  <label>Auditor:</label>
                  <span>{{ audit.auditor }}</span>
                </div>
                <div class="meta-item">
                  <label>Duration:</label>
                  <span>{{ audit.duration }}</span>
                </div>
              </div>
              
              <div class="audit-results" v-if="audit.status === 'completed'">
                <div class="result-summary">
                  <span class="result-score">Score: {{ audit.score }}%</span>
                  <span class="result-findings">{{ audit.findings }} findings</span>
                </div>
              </div>
            </div>
            
            <div class="audit-actions">
              <button class="action-btn view" @click="viewAudit(audit)">
                <i class="fas fa-eye"></i>
                View Details
              </button>
              <button 
                v-if="audit.status === 'scheduled'"
                class="action-btn start" 
                @click="startAudit(audit)"
              >
                <i class="fas fa-play"></i>
                Start Audit
              </button>
              <button 
                v-if="audit.status === 'completed'"
                class="action-btn download" 
                @click="downloadAuditReport(audit)"
              >
                <i class="fas fa-download"></i>
                Download Report
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compliance Reports -->
    <div class="reports-section">
      <div class="section-header">
        <h2>Compliance Reports</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="reportFilter" @change="filterReports">
              <option value="">All Reports</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="annual">Annual</option>
              <option value="ad-hoc">Ad-hoc</option>
            </select>
          </div>
          <button class="create-btn" @click="generateNewReport">
            <i class="fas fa-file-alt"></i>
            Generate Report
          </button>
        </div>
      </div>

      <div class="reports-grid">
        <div 
          v-for="report in filteredReports" 
          :key="report.id"
          class="report-card"
          @click="viewReport(report)"
        >
          <div class="report-header">
            <div class="report-icon">
              <i class="fas fa-file-alt"></i>
            </div>
            <div class="report-meta">
              <span class="report-type">{{ report.type }}</span>
              <span class="report-date">{{ formatDate(report.generatedDate) }}</span>
            </div>
          </div>
          
          <div class="report-content">
            <h3>{{ report.title }}</h3>
            <p>{{ report.description }}</p>
            
            <div class="report-stats">
              <div class="stat-item">
                <label>Overall Score:</label>
                <span :class="['score-value', getScoreClass(report.overallScore)]">{{ report.overallScore }}%</span>
              </div>
              <div class="stat-item">
                <label>Standards:</label>
                <span>{{ report.standards.length }}</span>
              </div>
              <div class="stat-item">
                <label>Findings:</label>
                <span>{{ report.findings }}</span>
              </div>
            </div>
          </div>
          
          <div class="report-footer">
            <div class="report-actions">
              <button class="action-btn download" @click.stop="downloadReport(report)">
                <i class="fas fa-download"></i>
                Download
              </button>
              <button class="action-btn share" @click.stop="shareReport(report)">
                <i class="fas fa-share"></i>
                Share
              </button>
            </div>
            <div class="report-size">{{ report.size }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compliance Policies -->
    <div class="policies-section">
      <div class="section-header">
        <h2>Compliance Policies</h2>
        <div class="header-actions">
          <button class="create-btn" @click="showPolicyModal = true">
            <i class="fas fa-plus"></i>
            Create Policy
          </button>
        </div>
      </div>

      <div class="policies-grid">
        <div 
          v-for="policy in policies" 
          :key="policy.id"
          class="policy-card"
        >
          <div class="policy-header">
            <div class="policy-icon">
              <i :class="policy.icon"></i>
            </div>
            <div class="policy-info">
              <h3>{{ policy.name }}</h3>
              <span class="policy-category">{{ policy.category }}</span>
            </div>
            <div class="policy-status">
              <span :class="['status-badge', policy.status]">{{ formatPolicyStatus(policy.status) }}</span>
            </div>
          </div>
          
          <div class="policy-content">
            <p>{{ policy.description }}</p>
            
            <div class="policy-details">
              <div class="detail-item">
                <label>Effective Date:</label>
                <span>{{ formatDate(policy.effectiveDate) }}</span>
              </div>
              <div class="detail-item">
                <label>Last Updated:</label>
                <span>{{ formatDate(policy.lastUpdated) }}</span>
              </div>
              <div class="detail-item">
                <label>Version:</label>
                <span>{{ policy.version }}</span>
              </div>
            </div>
          </div>
          
          <div class="policy-footer">
            <div class="policy-actions">
              <button class="action-btn view" @click="viewPolicy(policy)">
                <i class="fas fa-eye"></i>
                View
              </button>
              <button class="action-btn edit" @click="editPolicy(policy)">
                <i class="fas fa-edit"></i>
                Edit
              </button>
              <button class="action-btn download" @click="downloadPolicy(policy)">
                <i class="fas fa-download"></i>
                Download
              </button>
            </div>
            <div class="policy-compliance">
              <span class="compliance-badge">{{ policy.compliance }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Standard Modal -->
    <div v-if="showStandardModal" class="modal-overlay" @click="closeStandardModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add Compliance Standard</h2>
          <button class="close-btn" @click="closeStandardModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="standard-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Standard Name *</label>
                <input 
                  v-model="standardForm.name" 
                  type="text" 
                  placeholder="Enter standard name"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>Category *</label>
                <select v-model="standardForm.category" required>
                  <option value="">Select category</option>
                  <option value="data-privacy">Data Privacy</option>
                  <option value="security">Security</option>
                  <option value="financial">Financial</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="environmental">Environmental</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Description *</label>
              <textarea 
                v-model="standardForm.description" 
                placeholder="Describe the compliance standard"
                rows="4"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label>Requirements</label>
              <div class="requirements-list">
                <div 
                  v-for="(requirement, index) in standardForm.requirements" 
                  :key="index"
                  class="requirement-input"
                >
                  <input 
                    v-model="requirement.text" 
                    type="text" 
                    placeholder="Enter requirement"
                  />
                  <button class="remove-btn" @click="removeRequirement(index)">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-btn" @click="addRequirement">
                  <i class="fas fa-plus"></i>
                  Add Requirement
                </button>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Next Audit Date</label>
                <input 
                  v-model="standardForm.nextAudit" 
                  type="date" 
                />
              </div>
              
              <div class="form-group">
                <label>Audit Frequency</label>
                <select v-model="standardForm.frequency">
                  <option value="monthly">Monthly</option>
                  <option value="quarterly">Quarterly</option>
                  <option value="semi-annual">Semi-Annual</option>
                  <option value="annual">Annual</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Logo Upload</label>
              <div class="file-upload">
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
                <div class="uploaded-logo" v-if="standardForm.logo">
                  <img :src="standardForm.logo" alt="Standard logo" />
                  <button class="remove-logo" @click="removeLogo">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeStandardModal">Cancel</button>
          <button class="btn-primary" @click="addStandard">
            <i class="fas fa-plus"></i>
            Add Standard
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
const standardFilter = ref('')
const auditFilter = ref('')
const reportFilter = ref('')
const showStandardModal = ref(false)
const showAuditModal = ref(false)
const showPolicyModal = ref(false)

// Compliance status
const complianceStatus = reactive({
  level: 'Advanced Compliance',
  description: 'Your organization maintains high compliance standards across all regulatory frameworks',
  status: 'compliant',
  lastAudit: '2024-01-15T00:00:00Z'
})

// Compliance stats
const complianceStats = reactive({
  overallScore: 94,
  activeStandards: 8,
  pendingAudits: 2,
  lastAudit: '15 days ago'
})

// Standard form
const standardForm = reactive({
  name: '',
  category: '',
  description: '',
  requirements: [{ text: '' }],
  nextAudit: '',
  frequency: 'annual',
  logo: ''
})

// Compliance standards
const standards = ref([
  {
    id: 1,
    name: 'GDPR - General Data Protection Regulation',
    description: 'EU regulation for data protection and privacy for all individuals within the European Union',
    category: 'data-privacy',
    status: 'compliant',
    score: 98,
    progress: 95,
    logo: '/api/placeholder/60x60',
    nextAudit: '2024-04-15T00:00:00Z',
    requirements: [
      { text: 'Data protection officer appointment', status: 'compliant' },
      { text: 'Privacy by design implementation', status: 'compliant' },
      { text: 'Data breach notification procedures', status: 'compliant' },
      { text: 'Right to be forgotten implementation', status: 'compliant' }
    ]
  },
  {
    id: 2,
    name: 'SOC 2 Type II',
    description: 'Security controls relevant to security, availability, processing integrity, confidentiality, and privacy',
    category: 'security',
    status: 'compliant',
    score: 92,
    progress: 88,
    logo: '/api/placeholder/60x60',
    nextAudit: '2024-06-15T00:00:00Z',
    requirements: [
      { text: 'Access control management', status: 'compliant' },
      { text: 'Security monitoring and incident response', status: 'compliant' },
      { text: 'Change management procedures', status: 'compliant' },
      { text: 'Risk assessment processes', status: 'compliant' }
    ]
  },
  {
    id: 3,
    name: 'HIPAA - Health Insurance Portability',
    description: 'US law protecting sensitive patient health information',
    category: 'healthcare',
    status: 'non-compliant',
    score: 78,
    progress: 65,
    logo: '/api/placeholder/60x60',
    nextAudit: '2024-03-01T00:00:00Z',
    requirements: [
      { text: 'Administrative safeguards', status: 'compliant' },
      { text: 'Physical safeguards', status: 'compliant' },
      { text: 'Technical safeguards', status: 'non-compliant' },
      { text: 'Breach notification procedures', status: 'non-compliant' }
    ]
  }
])

// Audits data
const audits = ref([
  {
    id: 1,
    title: 'GDPR Annual Audit 2024',
    description: 'Comprehensive audit of GDPR compliance across all data processing activities',
    standard: 'GDPR',
    status: 'completed',
    date: '2024-01-15T00:00:00Z',
    auditor: 'External Audit Firm',
    duration: '5 days',
    score: 98,
    findings: 3
  },
  {
    id: 2,
    title: 'SOC 2 Type II Assessment',
    description: 'Bi-annual SOC 2 Type II assessment of security controls',
    standard: 'SOC 2',
    status: 'in-progress',
    date: '2024-02-01T00:00:00Z',
    auditor: 'Internal Audit Team',
    duration: '3 days',
    score: 0,
    findings: 0
  },
  {
    id: 3,
    title: 'HIPAA Compliance Review',
    description: 'Quarterly review of HIPAA compliance measures',
    standard: 'HIPAA',
    status: 'scheduled',
    date: '2024-03-01T00:00:00Z',
    auditor: 'Healthcare Compliance Officer',
    duration: '2 days',
    score: 0,
    findings: 0
  }
])

// Reports data
const reports = ref([
  {
    id: 1,
    title: 'Q1 2024 Compliance Report',
    description: 'Comprehensive quarterly compliance report covering all standards',
    type: 'quarterly',
    generatedDate: '2024-01-31T00:00:00Z',
    overallScore: 94,
    standards: ['GDPR', 'SOC 2', 'HIPAA'],
    findings: 8,
    size: '2.4 MB'
  },
  {
    id: 2,
    title: 'GDPR Compliance Assessment',
    description: 'Detailed assessment of GDPR compliance status',
    type: 'ad-hoc',
    generatedDate: '2024-01-15T00:00:00Z',
    overallScore: 98,
    standards: ['GDPR'],
    findings: 3,
    size: '1.8 MB'
  },
  {
    id: 3,
    title: 'Annual Compliance Summary 2023',
    description: 'Annual summary of compliance activities and achievements',
    type: 'annual',
    generatedDate: '2023-12-31T00:00:00Z',
    overallScore: 91,
    standards: ['GDPR', 'SOC 2', 'HIPAA', 'ISO 27001'],
    findings: 15,
    size: '3.2 MB'
  }
])

// Policies data
const policies = ref([
  {
    id: 1,
    name: 'Data Protection Policy',
    description: 'Comprehensive policy for protecting personal data and ensuring privacy compliance',
    category: 'Data Privacy',
    status: 'active',
    icon: 'fas fa-shield-alt',
    effectiveDate: '2023-01-01T00:00:00Z',
    lastUpdated: '2024-01-15T00:00:00Z',
    version: '2.1',
    compliance: 'GDPR'
  },
  {
    id: 2,
    name: 'Information Security Policy',
    description: 'Policy for maintaining information security and protecting organizational assets',
    category: 'Security',
    status: 'active',
    icon: 'fas fa-lock',
    effectiveDate: '2023-01-01T00:00:00Z',
    lastUpdated: '2024-01-10T00:00:00Z',
    version: '3.0',
    compliance: 'SOC 2'
  },
  {
    id: 3,
    name: 'Incident Response Policy',
    description: 'Procedures for responding to security incidents and data breaches',
    category: 'Security',
    status: 'active',
    icon: 'fas fa-exclamation-triangle',
    effectiveDate: '2023-06-01T00:00:00Z',
    lastUpdated: '2024-01-20T00:00:00Z',
    version: '1.5',
    compliance: 'HIPAA'
  }
])

// Computed properties
const filteredStandards = computed(() => {
  let filtered = standards.value

  if (standardFilter.value) {
    filtered = filtered.filter(standard => standard.status === standardFilter.value)
  }

  return filtered.sort((a, b) => b.score - a.score)
})

const filteredAudits = computed(() => {
  let filtered = audits.value

  if (auditFilter.value) {
    filtered = filtered.filter(audit => audit.status === auditFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const filteredReports = computed(() => {
  let filtered = reports.value

  if (reportFilter.value) {
    filtered = filtered.filter(report => report.type === reportFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.generatedDate) - new Date(a.generatedDate))
})

// Methods
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatStandardStatus = (status) => {
  return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatAuditStatus = (status) => {
  return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatPolicyStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getEmptyMessage = () => {
  if (standardFilter.value) {
    return 'No standards match your filter criteria'
  }
  return 'No standards found'
}

const getRequirementIcon = (status) => {
  if (status === 'compliant') return 'fas fa-check-circle'
  if (status === 'non-compliant') return 'fas fa-times-circle'
  return 'fas fa-exclamation-circle'
}

const getScoreClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'fair'
  return 'poor'
}

const getAuditDay = (dateString) => {
  return new Date(dateString).getDate()
}

const getAuditMonth = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', { month: 'short' })
}

const filterStandards = () => {
  // Filtering is handled by computed property
}

const filterAudits = () => {
  // Filtering is handled by computed property
}

const filterReports = () => {
  // Filtering is handled by computed property
}

const viewStandards = () => {
  showSuccess('Opening compliance standards')
}

const viewAudits = () => {
  showSuccess('Opening audit schedule')
}

const viewReports = () => {
  showSuccess('Opening compliance reports')
}

const viewPolicies = () => {
  showSuccess('Opening compliance policies')
}

const runComplianceAudit = () => {
  showSuccess('Initiating comprehensive compliance audit...')
}

const viewStandard = (standard) => {
  showSuccess(`Viewing details for ${standard.name}`)
}

const auditStandard = (standard) => {
  showSuccess(`Starting audit for ${standard.name}`)
}

const generateReport = (standard) => {
  showSuccess(`Generating compliance report for ${standard.name}`)
}

const viewAudit = (audit) => {
  showSuccess(`Viewing audit: ${audit.title}`)
}

const startAudit = async (audit) => {
  try {
    // const response = await apiPost(`/compliance/audits/${audit.id}/start`)
    // if (response.success) {
    //   audit.status = 'in-progress'
    //   showSuccess('Audit started successfully')
    // }
    
    // For demo, simulate start
    audit.status = 'in-progress'
    showSuccess('Audit started successfully')
  } catch (error) {
    console.error('Error starting audit:', error)
    showError('Failed to start audit')
  }
}

const downloadAuditReport = (audit) => {
  showSuccess(`Downloading audit report for ${audit.title}`)
}

const viewReport = (report) => {
  showSuccess(`Viewing report: ${report.title}`)
}

const downloadReport = (report) => {
  showSuccess(`Downloading ${report.title}`)
}

const shareReport = (report) => {
  showSuccess(`Sharing ${report.title}`)
}

const viewPolicy = (policy) => {
  showSuccess(`Viewing policy: ${policy.name}`)
}

const editPolicy = (policy) => {
  showSuccess(`Editing policy: ${policy.name}`)
}

const downloadPolicy = (policy) => {
  showSuccess(`Downloading ${policy.name}`)
}

const generateNewReport = () => {
  showSuccess('Opening report generation wizard')
}

const closeStandardModal = () => {
  showStandardModal.value = false
  resetStandardForm()
}

const resetStandardForm = () => {
  Object.assign(standardForm, {
    name: '',
    category: '',
    description: '',
    requirements: [{ text: '' }],
    nextAudit: '',
    frequency: 'annual',
    logo: ''
  })
}

const addRequirement = () => {
  standardForm.requirements.push({ text: '' })
}

const removeRequirement = (index) => {
  standardForm.requirements.splice(index, 1)
}

const handleLogoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      standardForm.logo = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const removeLogo = () => {
  standardForm.logo = ''
}

const addStandard = async () => {
  if (!standardForm.name || !standardForm.category || !standardForm.description) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/compliance/standards', standardForm)
    // if (response.success) {
    //   standards.value.unshift(response.standard)
    //   showSuccess('Standard added successfully')
    //   closeStandardModal()
    //   resetStandardForm()
    // }
    
    // For demo, simulate addition
    const newStandard = {
      id: Date.now(),
      name: standardForm.name,
      description: standardForm.description,
      category: standardForm.category,
      status: 'pending',
      score: 0,
      progress: 0,
      logo: standardForm.logo || '/api/placeholder/60x60',
      nextAudit: standardForm.nextAudit,
      requirements: standardForm.requirements.filter(r => r.text.trim())
    }
    
    standards.value.unshift(newStandard)
    showSuccess('Standard added successfully')
    closeStandardModal()
    resetStandardForm()
  } catch (error) {
    console.error('Error adding standard:', error)
    showError('Failed to add standard')
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/compliance')
    // if (response.success) {
    //   standards.value = response.standards || []
    //   audits.value = response.audits || []
    //   reports.value = response.reports || []
    //   policies.value = response.policies || []
    //   Object.assign(complianceStatus, response.status)
    //   Object.assign(complianceStats, response.stats)
    // }
    
    // For demo, use mock data
    loading.value = false
  } catch (error) {
    console.error('Error loading compliance data:', error)
    showError('Failed to load compliance data')
    loading.value = false
  }
})
</script>

<style scoped>
.compliance {
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
.standards-section,
.audits-section,
.reports-section,
.policies-section {
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

.compliance-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.compliance-icon {
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

.compliance-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.compliance-details p {
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

.badge.compliant {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.badge.non-compliant {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
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

.action-icon.audits {
  background: var(--info-color);
}

.action-icon.reports {
  background: var(--warning-color);
}

.action-icon.policies {
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

.audit-btn,
.create-btn,
.create-first-btn {
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

.audit-btn:hover,
.create-btn:hover,
.create-first-btn:hover {
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

.standards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.standard-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.standard-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.standard-card.non-compliant {
  border-left: 4px solid var(--danger-color);
}

.standard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.standard-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.standard-logo {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
}

.standard-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.standard-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.standard-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
}

.standard-category {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.standard-score {
  padding: 0.25rem 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.standard-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.standard-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.standard-requirements h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.standard-requirements ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.requirement-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.requirement-icon.fa-check-circle {
  color: var(--success-color);
}

.requirement-icon.fa-times-circle {
  color: var(--danger-color);
}

.requirement-icon.fa-exclamation-circle {
  color: var(--warning-color);
}

.standard-progress {
  margin-top: 1rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
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

.standard-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  margin-top: 1rem;
}

.standard-actions {
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

.action-btn.view:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.audit:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.report:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.standard-deadline {
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

.audits-timeline {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.audit-item {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 2rem;
  padding: 2rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.audit-item:hover {
  background: var(--glass-bg-hover);
}

.audit-item.completed {
  border-left: 4px solid var(--success-color);
}

.audit-item.in-progress {
  border-left: 4px solid var(--info-color);
}

.audit-item.failed {
  border-left: 4px solid var(--danger-color);
}

.audit-date {
  display: flex;
  align-items: center;
  justify-content: center;
}

.date-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  text-align: center;
}

.date-day {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.date-month {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.audit-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.audit-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.audit-header h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.in-progress {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.scheduled {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.audit-details p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.audit-meta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.audit-meta .meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.audit-meta .meta-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.audit-meta .meta-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.audit-results {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.result-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-score {
  font-weight: 600;
  color: var(--text-primary);
}

.result-findings {
  color: var(--text-secondary);
}

.audit-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.action-btn.start:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.download:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.report-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.report-icon {
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

.report-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
}

.report-type {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.report-date {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.report-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.report-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.4;
}

.report-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.report-stats .stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.report-stats .stat-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.report-stats .stat-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.score-value.excellent {
  color: var(--success-color);
}

.score-value.good {
  color: var(--info-color);
}

.score-value.fair {
  color: var(--warning-color);
}

.score-value.poor {
  color: var(--danger-color);
}

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  margin-top: 1rem;
}

.report-actions {
  display: flex;
  gap: 0.5rem;
}

.report-size {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.policies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
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
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
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

.policy-info {
  flex: 1;
  margin-left: 1rem;
}

.policy-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.policy-category {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.policy-status {
  margin-left: auto;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.inactive {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.policy-content {
  margin-bottom: 1rem;
}

.policy-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.policy-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.policy-details .detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.policy-details .detail-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.policy-details .detail-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.policy-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  margin-top: 1rem;
}

.policy-actions {
  display: flex;
  gap: 0.5rem;
}

.policy-compliance {
  margin-left: auto;
}

.compliance-badge {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 600;
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

.standard-form {
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

.requirements-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.requirement-input {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.requirement-input input {
  flex: 1;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.remove-btn {
  padding: 0.5rem;
  background: var(--danger-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: #dc2626;
}

.add-btn {
  padding: 0.5rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  align-self: flex-start;
}

.add-btn:hover {
  background: var(--primary-hover);
}

.file-upload {
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
  .compliance {
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
  
  .standards-grid {
    grid-template-columns: 1fr;
  }
  
  .audit-item {
    grid-template-columns: 60px 1fr;
  }
  
  .reports-grid {
    grid-template-columns: 1fr;
  }
  
  .policies-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
