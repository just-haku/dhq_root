<template>
  <div class="gdpr">
    <div class="page-header">
      <h1>GDPR Compliance</h1>
      <p>General Data Protection Regulation compliance management</p>
    </div>

    <!-- GDPR Overview -->
    <div class="overview-section">
      <div class="section-header">
        <h2>GDPR Compliance Overview</h2>
        <div class="header-actions">
          <button class="audit-btn" @click="runGDPRAudit">
            <i class="fas fa-shield-alt"></i>
            Run GDPR Audit
          </button>
        </div>
      </div>
      
      <div class="overview-card">
        <div class="overview-header">
          <div class="gdpr-info">
            <div class="gdpr-icon">
              <i class="fas fa-shield-alt"></i>
            </div>
            <div class="gdpr-details">
              <h3>{{ gdprStatus.level }}</h3>
              <p>{{ gdprStatus.description }}</p>
            </div>
          </div>
          <div class="status-badge">
            <span :class="['badge', gdprStatus.status]">{{ formatStatus(gdprStatus.status) }}</span>
          </div>
        </div>
        
        <div class="overview-stats">
          <div class="stat-item">
            <div class="stat-value">{{ gdprStats.complianceScore }}%</div>
            <div class="stat-label">Compliance Score</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ gdprStats.dataSubjects }}</div>
            <div class="stat-label">Data Subjects</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ gdprStats.processingActivities }}</div>
            <div class="stat-label">Processing Activities</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ gdprStats.dataRequests }}</div>
            <div class="stat-label">Data Requests</div>
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
        <div class="action-card" @click="viewDataSubjects">
          <div class="action-icon">
            <i class="fas fa-users"></i>
          </div>
          <h3>Data Subjects</h3>
          <p>Manage data subject requests</p>
        </div>
        
        <div class="action-card" @click="viewProcessingActivities">
          <div class="action-icon activities">
            <i class="fas fa-database"></i>
          </div>
          <h3>Processing Activities</h3>
          <p>Track data processing activities</p>
        </div>
        
        <div class="action-card" @click="viewDataMapping">
          <div class="action-icon mapping">
            <i class="fas fa-sitemap"></i>
          </div>
          <h3>Data Mapping</h3>
          <p>Visualize data flows</p>
        </div>
        
        <div class="action-card" @click="viewDocumentation">
          <div class="action-icon docs">
            <i class="fas fa-file-alt"></i>
          </div>
          <h3>Documentation</h3>
          <p>GDPR documentation</p>
        </div>
      </div>
    </div>

    <!-- GDPR Principles -->
    <div class="principles-section">
      <div class="section-header">
        <h2>GDPR Principles Compliance</h2>
      </div>

      <div class="principles-grid">
        <div 
          v-for="principle in gdprPrinciples" 
          :key="principle.id"
          class="principle-card"
          :class="{ 'non-compliant': principle.status === 'non-compliant' }"
        >
          <div class="principle-header">
            <div class="principle-icon">
              <i :class="principle.icon"></i>
            </div>
            <div class="principle-info">
              <h3>{{ principle.name }}</h3>
              <span :class="['status-badge', principle.status]">{{ formatPrincipleStatus(principle.status) }}</span>
            </div>
            <div class="principle-score">
              <span class="score-value">{{ principle.score }}%</span>
            </div>
          </div>
          
          <div class="principle-content">
            <p>{{ principle.description }}</p>
            
            <div class="principle-requirements">
              <h4>Key Requirements:</h4>
              <ul>
                <li v-for="requirement in principle.requirements" :key="requirement" class="requirement-item">
                  <i :class="['requirement-icon', getRequirementIcon(requirement.status)]"></i>
                  {{ requirement.text }}
                </li>
              </ul>
            </div>
            
            <div class="principle-progress">
              <div class="progress-header">
                <span>Compliance Progress</span>
                <span>{{ principle.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: principle.progress + '%' }"></div>
              </div>
            </div>
          </div>
          
          <div class="principle-footer">
            <div class="principle-actions">
              <button class="action-btn view" @click="viewPrinciple(principle)">
                <i class="fas fa-eye"></i>
                View
              </button>
              <button class="action-btn improve" @click="improvePrinciple(principle)">
                <i class="fas fa-arrow-up"></i>
                Improve
              </button>
            </div>
            <div class="principle-last-review">
              <span class="review-label">Last Review:</span>
              <span class="review-date">{{ formatDate(principle.lastReview) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Subject Requests -->
    <div class="requests-section">
      <div class="section-header">
        <h2>Data Subject Requests</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="requestFilter" @change="filterRequests">
              <option value="">All Requests</option>
              <option value="pending">Pending</option>
              <option value="in-progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <button class="create-btn" @click="showRequestModal = true">
            <i class="fas fa-plus"></i>
            New Request
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading data subject requests...</p>
      </div>

      <div v-else-if="filteredRequests.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-users"></i>
        </div>
        <h3>No requests found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showRequestModal = true">
          <i class="fas fa-plus"></i>
          Create First Request
        </button>
      </div>

      <div v-else class="requests-table">
        <div class="table-header">
          <div class="header-cell">Request ID</div>
          <div class="header-cell">Data Subject</div>
          <div class="header-cell">Type</div>
          <div class="header-cell">Status</div>
          <div class="header-cell">Received</div>
          <div class="header-cell">Deadline</div>
          <div class="header-cell">Actions</div>
        </div>
        
        <div 
          v-for="request in paginatedRequests" 
          :key="request.id"
          class="table-row"
          :class="{ 'urgent': isUrgent(request) }"
        >
          <div class="table-cell">
            <span class="request-id">#{{ request.id }}</span>
          </div>
          
          <div class="table-cell">
            <div class="subject-info">
              <div class="subject-avatar">
                <img :src="request.avatar" :alt="request.name" />
              </div>
              <div class="subject-details">
                <span class="subject-name">{{ request.name }}</span>
                <span class="subject-email">{{ request.email }}</span>
              </div>
            </div>
          </div>
          
          <div class="table-cell">
            <span :class="['request-type', request.type]">{{ formatRequestType(request.type) }}</span>
          </div>
          
          <div class="table-cell">
            <span :class="['status-badge', request.status]">{{ formatRequestStatus(request.status) }}</span>
          </div>
          
          <div class="table-cell">
            <span class="received-date">{{ formatDate(request.receivedDate) }}</span>
          </div>
          
          <div class="table-cell">
            <span :class="['deadline', { 'overdue': isOverdue(request) }]">{{ formatDate(request.deadline) }}</span>
          </div>
          
          <div class="table-cell">
            <div class="request-actions">
              <button class="action-btn view" @click="viewRequest(request)">
                <i class="fas fa-eye"></i>
              </button>
              <button class="action-btn process" @click="processRequest(request)">
                <i class="fas fa-cog"></i>
              </button>
              <button class="action-btn complete" @click="completeRequest(request)">
                <i class="fas fa-check"></i>
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

    <!-- Processing Activities -->
    <div class="activities-section">
      <div class="section-header">
        <h2>Processing Activities</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="activityFilter" @change="filterActivities">
              <option value="">All Activities</option>
              <option value="high-risk">High Risk</option>
              <option value="medium-risk">Medium Risk</option>
              <option value="low-risk">Low Risk</option>
            </select>
          </div>
          <button class="create-btn" @click="showActivityModal = true">
            <i class="fas fa-plus"></i>
            New Activity
          </button>
        </div>
      </div>

      <div class="activities-grid">
        <div 
          v-for="activity in filteredActivities" 
          :key="activity.id"
          class="activity-card"
          :class="activity.riskLevel"
        >
          <div class="activity-header">
            <div class="activity-info">
              <h3>{{ activity.name }}</h3>
              <span :class="['risk-badge', activity.riskLevel]">{{ formatRiskLevel(activity.riskLevel) }}</span>
            </div>
            <div class="activity-status">
              <span :class="['status-badge', activity.status]">{{ formatActivityStatus(activity.status) }}</span>
            </div>
          </div>
          
          <div class="activity-content">
            <p>{{ activity.description }}</p>
            
            <div class="activity-details">
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Purpose:</label>
                  <span>{{ activity.purpose }}</span>
                </div>
                <div class="detail-item">
                  <label>Legal Basis:</label>
                  <span>{{ activity.legalBasis }}</span>
                </div>
                <div class="detail-item">
                  <label>Data Categories:</label>
                  <span>{{ activity.dataCategories.join(', ') }}</span>
                </div>
                <div class="detail-item">
                  <label>Data Subjects:</label>
                  <span>{{ activity.dataSubjects.join(', ') }}</span>
                </div>
                <div class="detail-item">
                  <label>Retention Period:</label>
                  <span>{{ activity.retentionPeriod }}</span>
                </div>
                <div class="detail-item">
                  <label>Third Parties:</label>
                  <span>{{ activity.thirdParties.length }} processors</span>
                </div>
              </div>
            </div>
            
            <div class="activity-compliance">
              <div class="compliance-score">
                <span class="score-label">Compliance Score:</span>
                <span :class="['score-value', getScoreClass(activity.complianceScore)]">{{ activity.complianceScore }}%</span>
              </div>
              <div class="compliance-issues" v-if="activity.issues.length > 0">
                <span class="issues-label">Issues:</span>
                <span class="issues-count">{{ activity.issues.length }}</span>
              </div>
            </div>
          </div>
          
          <div class="activity-footer">
            <div class="activity-actions">
              <button class="action-btn view" @click="viewActivity(activity)">
                <i class="fas fa-eye"></i>
                View
              </button>
              <button class="action-btn edit" @click="editActivity(activity)">
                <i class="fas fa-edit"></i>
                Edit
              </button>
              <button class="action-btn assess" @click="assessActivity(activity)">
                <i class="fas fa-balance-scale"></i>
                Assess
              </button>
            </div>
            <div class="activity-dpia">
              <span v-if="activity.requiresDPIA" class="dpia-badge">
                <i class="fas fa-exclamation-triangle"></i>
                DPIA Required
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Mapping -->
    <div class="mapping-section">
      <div class="section-header">
        <h2>Data Flow Mapping</h2>
        <div class="header-actions">
          <button class="refresh-btn" @click="refreshDataMap">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="data-map-container">
        <div class="map-legend">
          <div class="legend-item">
            <div class="legend-color source"></div>
            <span>Data Source</span>
          </div>
          <div class="legend-item">
            <div class="legend-color processor"></div>
            <span>Processor</span>
          </div>
          <div class="legend-item">
            <div class="legend-color destination"></div>
            <span>Destination</span>
          </div>
        </div>
        
        <div class="data-map">
          <div class="map-node source" v-for="source in dataSources" :key="source.id">
            <div class="node-icon">
              <i class="fas fa-database"></i>
            </div>
            <span class="node-label">{{ source.name }}</span>
          </div>
          
          <div class="map-node processor" v-for="processor in dataProcessors" :key="processor.id">
            <div class="node-icon">
              <i class="fas fa-cogs"></i>
            </div>
            <span class="node-label">{{ processor.name }}</span>
          </div>
          
          <div class="map-node destination" v-for="destination in dataDestinations" :key="destination.id">
            <div class="node-icon">
              <i class="fas fa-share-alt"></i>
            </div>
            <span class="node-label">{{ destination.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Documentation -->
    <div class="documentation-section">
      <div class="section-header">
        <h2>GDPR Documentation</h2>
        <div class="header-actions">
          <button class="create-btn" @click="generateDocumentation">
            <i class="fas fa-file-alt"></i>
            Generate Report
          </button>
        </div>
      </div>

      <div class="docs-grid">
        <div 
          v-for="doc in documentation" 
          :key="doc.id"
          class="doc-card"
          @click="viewDocument(doc)"
        >
          <div class="doc-header">
            <div class="doc-icon">
              <i :class="doc.icon"></i>
            </div>
            <div class="doc-meta">
              <span class="doc-type">{{ doc.type }}</span>
              <span class="doc-date">{{ formatDate(doc.lastUpdated) }}</span>
            </div>
          </div>
          
          <div class="doc-content">
            <h3>{{ doc.title }}</h3>
            <p>{{ doc.description }}</p>
            
            <div class="doc-stats">
              <div class="stat-item">
                <label>Version:</label>
                <span>{{ doc.version }}</span>
              </div>
              <div class="stat-item">
                <label>Status:</label>
                <span :class="['doc-status', doc.status]">{{ formatDocStatus(doc.status) }}</span>
              </div>
            </div>
          </div>
          
          <div class="doc-footer">
            <div class="doc-actions">
              <button class="action-btn download" @click.stop="downloadDocument(doc)">
                <i class="fas fa-download"></i>
                Download
              </button>
              <button class="action-btn share" @click.stop="shareDocument(doc)">
                <i class="fas fa-share"></i>
                Share
              </button>
            </div>
            <div class="doc-size">{{ doc.size }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Request Modal -->
    <div v-if="showRequestModal" class="modal-overlay" @click="closeRequestModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>New Data Subject Request</h2>
          <button class="close-btn" @click="closeRequestModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="request-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Request Type *</label>
                <select v-model="requestForm.type" required>
                  <option value="">Select request type</option>
                  <option value="access">Right of Access</option>
                  <option value="rectification">Right to Rectification</option>
                  <option value="erasure">Right to Erasure</option>
                  <option value="portability">Right to Data Portability</option>
                  <option value="restriction">Right to Restrict Processing</option>
                  <option value="objection">Right to Object</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Priority</label>
                <select v-model="requestForm.priority">
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Data Subject Name *</label>
                <input 
                  v-model="requestForm.subjectName" 
                  type="text" 
                  placeholder="Enter data subject name"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>Email Address *</label>
                <input 
                  v-model="requestForm.email" 
                  type="email" 
                  placeholder="Enter email address"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label>Request Details *</label>
              <textarea 
                v-model="requestForm.details" 
                placeholder="Describe the data subject request in detail"
                rows="4"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label>Supporting Documents</label>
              <div class="file-upload">
                <input 
                  type="file" 
                  ref="fileInput"
                  @change="handleFileUpload"
                  multiple
                  accept=".pdf,.doc,.docx,.jpg,.png"
                />
                <button class="upload-btn" @click="$refs.fileInput.click()">
                  <i class="fas fa-upload"></i>
                  Upload Documents
                </button>
                <div class="uploaded-files" v-if="requestForm.documents.length > 0">
                  <div 
                    v-for="(doc, index) in requestForm.documents" 
                    :key="index"
                    class="file-item"
                  >
                    <span class="file-name">{{ doc.name }}</span>
                    <button class="remove-file" @click="removeDocument(index)">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Internal Notes</label>
              <textarea 
                v-model="requestForm.notes" 
                placeholder="Add internal notes for processing"
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeRequestModal">Cancel</button>
          <button class="btn-primary" @click="createRequest">
            <i class="fas fa-plus"></i>
            Create Request
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
const requestFilter = ref('')
const activityFilter = ref('')
const currentPage = ref(1)
const requestsPerPage = ref(10)
const showRequestModal = ref(false)
const showActivityModal = ref(false)

// GDPR status
const gdprStatus = reactive({
  level: 'GDPR Compliant',
  description: 'Your organization maintains full compliance with GDPR requirements',
  status: 'compliant',
  lastAudit: '2024-01-15T00:00:00Z'
})

// GDPR stats
const gdprStats = reactive({
  complianceScore: 98,
  dataSubjects: 15420,
  processingActivities: 45,
  dataRequests: 127
})

// Request form
const requestForm = reactive({
  type: '',
  priority: 'normal',
  subjectName: '',
  email: '',
  details: '',
  documents: [],
  notes: ''
})

// GDPR principles
const gdprPrinciples = ref([
  {
    id: 1,
    name: 'Lawfulness, Fairness and Transparency',
    description: 'Process data lawfully, fairly and in a transparent manner',
    icon: 'fas fa-balance-scale',
    status: 'compliant',
    score: 95,
    progress: 92,
    lastReview: '2024-01-10T00:00:00Z',
    requirements: [
      { text: 'Legal basis documentation', status: 'compliant' },
      { text: 'Privacy notices updated', status: 'compliant' },
      { text: 'Transparency procedures', status: 'compliant' }
    ]
  },
  {
    id: 2,
    name: 'Purpose Limitation',
    description: 'Collect data for specified, explicit and legitimate purposes',
    icon: 'fas fa-bullseye',
    status: 'compliant',
    score: 92,
    progress: 88,
    lastReview: '2024-01-12T00:00:00Z',
    requirements: [
      { text: 'Purpose documentation', status: 'compliant' },
      { text: 'Purpose change procedures', status: 'compliant' },
      { text: 'Incompatible use prevention', status: 'compliant' }
    ]
  },
  {
    id: 3,
    name: 'Data Minimisation',
    description: 'Collect and process only necessary data',
    icon: 'fas fa-compress',
    status: 'non-compliant',
    score: 78,
    progress: 65,
    lastReview: '2024-01-08T00:00:00Z',
    requirements: [
      { text: 'Data necessity assessment', status: 'compliant' },
      { text: 'Data retention policies', status: 'compliant' },
      { text: 'Data minimization procedures', status: 'non-compliant' }
    ]
  },
  {
    id: 4,
    name: 'Accuracy',
    description: 'Ensure personal data is accurate and kept up to date',
    icon: 'fas fa-check-circle',
    status: 'compliant',
    score: 96,
    progress: 94,
    lastReview: '2024-01-15T00:00:00Z',
    requirements: [
      { text: 'Data verification procedures', status: 'compliant' },
      { text: 'Correction mechanisms', status: 'compliant' },
      { text: 'Data quality monitoring', status: 'compliant' }
    ]
  },
  {
    id: 5,
    name: 'Storage Limitation',
    description: 'Keep data only as long as necessary',
    icon: 'fas fa-clock',
    status: 'compliant',
    score: 88,
    progress: 85,
    lastReview: '2024-01-11T00:00:00Z',
    requirements: [
      { text: 'Retention period definition', status: 'compliant' },
      { text: 'Automated deletion processes', status: 'compliant' },
      { text: 'Review schedules', status: 'compliant' }
    ]
  },
  {
    id: 6,
    name: 'Integrity and Confidentiality',
    description: 'Process data securely using appropriate measures',
    icon: 'fas fa-shield-alt',
    status: 'compliant',
    score: 94,
    progress: 90,
    lastReview: '2024-01-14T00:00:00Z',
    requirements: [
      { text: 'Security measures implemented', status: 'compliant' },
      { text: 'Access controls', status: 'compliant' },
      { text: 'Encryption standards', status: 'compliant' }
    ]
  },
  {
    id: 7,
    name: 'Accountability',
    description: 'Demonstrate compliance with GDPR principles',
    icon: 'fas fa-user-check',
    status: 'compliant',
    score: 91,
    progress: 87,
    lastReview: '2024-01-13T00:00:00Z',
    requirements: [
      { text: 'Compliance documentation', status: 'compliant' },
      { text: 'Responsibility assignment', status: 'compliant' },
      { text: 'Audit procedures', status: 'compliant' }
    ]
  }
])

// Data subject requests
const requests = ref([
  {
    id: 1001,
    name: 'John Anderson',
    email: 'john.anderson@email.com',
    type: 'access',
    status: 'in-progress',
    priority: 'high',
    receivedDate: '2024-01-18T00:00:00Z',
    deadline: '2024-02-01T00:00:00Z',
    avatar: '/api/placeholder/40x40'
  },
  {
    id: 1002,
    name: 'Sarah Mitchell',
    email: 'sarah.mitchell@email.com',
    type: 'erasure',
    status: 'pending',
    priority: 'normal',
    receivedDate: '2024-01-20T00:00:00Z',
    deadline: '2024-02-03T00:00:00Z',
    avatar: '/api/placeholder/40x40'
  },
  {
    id: 1003,
    name: 'Michael Chen',
    email: 'michael.chen@email.com',
    type: 'portability',
    status: 'completed',
    priority: 'normal',
    receivedDate: '2024-01-10T00:00:00Z',
    deadline: '2024-01-24T00:00:00Z',
    avatar: '/api/placeholder/40x40'
  }
])

// Processing activities
const activities = ref([
  {
    id: 1,
    name: 'Customer Relationship Management',
    description: 'Processing of customer data for CRM purposes and customer service',
    riskLevel: 'medium-risk',
    status: 'active',
    purpose: 'Customer service and relationship management',
    legalBasis: 'Legitimate interest',
    dataCategories: ['Personal data', 'Contact information', 'Communication data'],
    dataSubjects: ['Customers', 'Prospects'],
    retentionPeriod: '7 years',
    thirdParties: ['CRM Provider', 'Email Service'],
    complianceScore: 92,
    issues: [],
    requiresDPIA: false
  },
  {
    id: 2,
    name: 'Marketing Analytics',
    description: 'Analysis of user behavior for marketing optimization',
    riskLevel: 'high-risk',
    status: 'active',
    purpose: 'Marketing optimization and personalization',
    legalBasis: 'Consent',
    dataCategories: ['Behavioral data', 'Analytics data', 'Device information'],
    dataSubjects: ['Website visitors', 'App users'],
    retentionPeriod: '2 years',
    thirdParties: ['Analytics Provider', 'Marketing Platform'],
    complianceScore: 78,
    issues: ['Consent documentation incomplete', 'Data minimization not fully implemented'],
    requiresDPIA: true
  },
  {
    id: 3,
    name: 'Employee Management',
    description: 'Processing of employee data for HR and payroll purposes',
    riskLevel: 'low-risk',
    status: 'active',
    purpose: 'HR management and payroll',
    legalBasis: 'Legal obligation',
    dataCategories: ['Personal data', 'Financial data', 'Performance data'],
    dataSubjects: ['Employees', 'Former employees'],
    retentionPeriod: '7 years after employment',
    thirdParties: ['Payroll Provider', 'Benefits Provider'],
    complianceScore: 96,
    issues: [],
    requiresDPIA: false
  }
])

// Data mapping
const dataSources = ref([
  { id: 1, name: 'Website Forms' },
  { id: 2, name: 'Mobile App' },
  { id: 3, name: 'CRM System' }
])

const dataProcessors = ref([
  { id: 1, name: 'Analytics Service' },
  { id: 2, name: 'Email Marketing' },
  { id: 3, name: 'Cloud Storage' }
])

const dataDestinations = ref([
  { id: 1, name: 'Marketing Database' },
  { id: 2, name: 'Customer Support' },
  { id: 3, name: 'Analytics Dashboard' }
])

// Documentation
const documentation = ref([
  {
    id: 1,
    title: 'Privacy Policy',
    description: 'Comprehensive privacy policy for GDPR compliance',
    type: 'Policy',
    icon: 'fas fa-file-contract',
    lastUpdated: '2024-01-15T00:00:00Z',
    version: '3.2',
    status: 'approved',
    size: '245 KB'
  },
  {
    id: 2,
    title: 'Data Protection Impact Assessment',
    description: 'DPIA for high-risk processing activities',
    type: 'Assessment',
    icon: 'fas fa-clipboard-check',
    lastUpdated: '2024-01-10T00:00:00Z',
    version: '1.1',
    status: 'in-review',
    size: '1.2 MB'
  },
  {
    id: 3,
    title: 'Records of Processing Activities',
    description: 'Detailed documentation of all data processing activities',
    type: 'Record',
    icon: 'fas fa-database',
    lastUpdated: '2024-01-20T00:00:00Z',
    version: '2.0',
    status: 'approved',
    size: '3.8 MB'
  }
])

// Computed properties
const filteredRequests = computed(() => {
  let filtered = requests.value

  if (requestFilter.value) {
    filtered = filtered.filter(request => request.status === requestFilter.value)
  }

  return filtered.sort((a, b) => {
    // Sort by priority first, then by date
    const priorityOrder = { urgent: 3, high: 2, normal: 1 }
    const aPriority = priorityOrder[a.priority] || 0
    const bPriority = priorityOrder[b.priority] || 0
    
    if (aPriority !== bPriority) {
      return bPriority - aPriority
    }
    
    return new Date(b.receivedDate) - new Date(a.receivedDate)
  })
})

const paginatedRequests = computed(() => {
  const start = (currentPage.value - 1) * requestsPerPage.value
  const end = start + requestsPerPage.value
  return filteredRequests.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredRequests.value.length / requestsPerPage.value)
})

const filteredActivities = computed(() => {
  let filtered = activities.value

  if (activityFilter.value) {
    filtered = filtered.filter(activity => activity.riskLevel === activityFilter.value)
  }

  return filtered.sort((a, b) => b.complianceScore - a.complianceScore)
})

// Methods
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatPrincipleStatus = (status) => {
  return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatRequestType = (type) => {
  const types = {
    access: 'Access',
    rectification: 'Rectification',
    erasure: 'Erasure',
    portability: 'Portability',
    restriction: 'Restriction',
    objection: 'Objection'
  }
  return types[type] || type
}

const formatRequestStatus = (status) => {
  return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatActivityStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatRiskLevel = (level) => {
  return level.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatDocStatus = (status) => {
  return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getEmptyMessage = () => {
  if (requestFilter.value) {
    return 'No requests match your filter criteria'
  }
  return 'No data subject requests found'
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

const isUrgent = (request) => {
  return request.priority === 'urgent' || request.priority === 'high'
}

const isOverdue = (request) => {
  return new Date(request.deadline) < new Date() && request.status !== 'completed'
}

const filterRequests = () => {
  // Filtering is handled by computed property
  currentPage.value = 1
}

const filterActivities = () => {
  // Filtering is handled by computed property
}

const viewDataSubjects = () => {
  showSuccess('Opening data subject requests')
}

const viewProcessingActivities = () => {
  showSuccess('Opening processing activities')
}

const viewDataMapping = () => {
  showSuccess('Opening data flow mapping')
}

const viewDocumentation = () => {
  showSuccess('Opening GDPR documentation')
}

const runGDPRAudit = () => {
  showSuccess('Initiating GDPR compliance audit...')
}

const viewPrinciple = (principle) => {
  showSuccess(`Viewing details for ${principle.name}`)
}

const improvePrinciple = (principle) => {
  showSuccess(`Opening improvement plan for ${principle.name}`)
}

const viewRequest = (request) => {
  showSuccess(`Viewing request #${request.id}`)
}

const processRequest = (request) => {
  showSuccess(`Processing request #${request.id}`)
}

const completeRequest = async (request) => {
  const confirmed = await showConfirm(`Are you sure you want to complete request #${request.id}?`)
  if (confirmed) {
    try {
      // const response = await apiPut(`/gdpr/requests/${request.id}/complete`)
      // if (response.success) {
      //   request.status = 'completed'
      //   showSuccess('Request completed successfully')
      // }
      
      // For demo, simulate completion
      request.status = 'completed'
      showSuccess('Request completed successfully')
    } catch (error) {
      console.error('Error completing request:', error)
      showError('Failed to complete request')
    }
  }
}

const viewActivity = (activity) => {
  showSuccess(`Viewing activity: ${activity.name}`)
}

const editActivity = (activity) => {
  showSuccess(`Editing activity: ${activity.name}`)
}

const assessActivity = (activity) => {
  showSuccess(`Starting assessment for: ${activity.name}`)
}

const refreshDataMap = () => {
  showSuccess('Refreshing data flow map...')
}

const viewDocument = (doc) => {
  showSuccess(`Viewing document: ${doc.title}`)
}

const downloadDocument = (doc) => {
  showSuccess(`Downloading ${doc.title}`)
}

const shareDocument = (doc) => {
  showSuccess(`Sharing ${doc.title}`)
}

const generateDocumentation = () => {
  showSuccess('Generating GDPR compliance report...')
}

const closeRequestModal = () => {
  showRequestModal.value = false
  resetRequestForm()
}

const resetRequestForm = () => {
  Object.assign(requestForm, {
    type: '',
    priority: 'normal',
    subjectName: '',
    email: '',
    details: '',
    documents: [],
    notes: ''
  })
}

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    requestForm.documents.push({
      name: file.name,
      size: file.size,
      type: file.type
    })
  })
}

const removeDocument = (index) => {
  requestForm.documents.splice(index, 1)
}

const createRequest = async () => {
  if (!requestForm.type || !requestForm.subjectName || !requestForm.email || !requestForm.details) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/gdpr/requests', requestForm)
    // if (response.success) {
    //   requests.value.unshift(response.request)
    //   showSuccess('Request created successfully')
    //   closeRequestModal()
    //   resetRequestForm()
    // }
    
    // For demo, simulate creation
    const newRequest = {
      id: Date.now(),
      name: requestForm.subjectName,
      email: requestForm.email,
      type: requestForm.type,
      status: 'pending',
      priority: requestForm.priority,
      receivedDate: new Date().toISOString(),
      deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days
      avatar: '/api/placeholder/40x40'
    }
    
    requests.value.unshift(newRequest)
    showSuccess('Request created successfully')
    closeRequestModal()
    resetRequestForm()
  } catch (error) {
    console.error('Error creating request:', error)
    showError('Failed to create request')
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/gdpr')
    // if (response.success) {
    //   gdprPrinciples.value = response.principles || []
    //   requests.value = response.requests || []
    //   activities.value = response.activities || []
    //   dataSources.value = response.dataSources || []
    //   dataProcessors.value = response.dataProcessors || []
    //   dataDestinations.value = response.dataDestinations || []
    //   documentation.value = response.documentation || []
    //   Object.assign(gdprStatus, response.status)
    //   Object.assign(gdprStats, response.stats)
    // }
    
    // For demo, use mock data
    loading.value = false
  } catch (error) {
    console.error('Error loading GDPR data:', error)
    showError('Failed to load GDPR data')
    loading.value = false
  }
})
</script>

<style scoped>
.gdpr {
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
.principles-section,
.requests-section,
.activities-section,
.mapping-section,
.documentation-section {
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

.gdpr-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.gdpr-icon {
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

.gdpr-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.gdpr-details p {
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

.action-icon.activities {
  background: var(--info-color);
}

.action-icon.mapping {
  background: var(--warning-color);
}

.action-icon.docs {
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
.create-first-btn,
.refresh-btn {
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
.create-first-btn:hover,
.refresh-btn:hover {
  background: var(--primary-hover);
}

.create-first-btn {
  margin-top: 2rem;
  align-self: center;
}

.principles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.principle-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.principle-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.principle-card.non-compliant {
  border-left: 4px solid var(--danger-color);
}

.principle-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.principle-icon {
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

.principle-info {
  flex: 1;
  margin-left: 1rem;
}

.principle-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.principle-score {
  margin-left: auto;
}

.score-value {
  padding: 0.5rem 1rem;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
}

.principle-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.principle-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.principle-requirements h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.principle-requirements ul {
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

.principle-progress {
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

.principle-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  margin-top: 1rem;
}

.principle-actions {
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

.action-btn.improve:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.principle-last-review {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-end;
}

.review-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.review-date {
  color: var(--text-primary);
  font-weight: 600;
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

.requests-table {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 120px 2fr 1fr 1fr 1fr 1fr 1fr;
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.table-row {
  display: grid;
  grid-template-columns: 120px 2fr 1fr 1fr 1fr 1fr 1fr;
  padding: 1rem;
  border-bottom: 1px solid var(--glass-border);
  transition: all 0.3s ease;
}

.table-row:hover {
  background: var(--glass-bg-hover);
}

.table-row.urgent {
  border-left: 4px solid var(--danger-color);
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.request-id {
  color: var(--text-primary);
  font-weight: 600;
}

.subject-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.subject-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.subject-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.subject-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.subject-name {
  color: var(--text-primary);
  font-weight: 600;
}

.subject-email {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.request-type {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.request-type.access {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.request-type.erasure {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.request-type.portability {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.in-progress {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.rejected {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.received-date {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.deadline {
  color: var(--text-primary);
  font-weight: 600;
}

.deadline.overdue {
  color: var(--danger-color);
}

.request-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.process:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.complete:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
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

.activities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 2rem;
}

.activity-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.activity-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.activity-card.high-risk {
  border-left: 4px solid var(--danger-color);
}

.activity-card.medium-risk {
  border-left: 4px solid var(--warning-color);
}

.activity-card.low-risk {
  border-left: 4px solid var(--success-color);
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.activity-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.risk-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.risk-badge.high-risk {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.risk-badge.medium-risk {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.risk-badge.low-risk {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.activity-status {
  margin-left: auto;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.activity-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.activity-details {
  margin-bottom: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
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

.activity-compliance {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.compliance-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
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

.compliance-issues {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.issues-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.issues-count {
  color: var(--danger-color);
  font-weight: 600;
}

.activity-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  margin-top: 1rem;
}

.activity-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.edit:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.assess:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.activity-dpia {
  margin-left: auto;
}

.dpia-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.data-map-container {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.map-legend {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.legend-color.source {
  background: var(--primary-color);
}

.legend-color.processor {
  background: var(--info-color);
}

.legend-color.destination {
  background: var(--success-color);
}

.data-map {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  min-height: 300px;
}

.map-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.map-node:hover {
  transform: translateY(-4px);
}

.map-node.source {
  background: rgba(59, 130, 246, 0.1);
  border: 2px solid var(--primary-color);
}

.map-node.processor {
  background: rgba(245, 158, 11, 0.1);
  border: 2px solid var(--info-color);
}

.map-node.destination {
  background: rgba(16, 185, 129, 0.1);
  border: 2px solid var(--success-color);
}

.node-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.map-node.source .node-icon {
  background: var(--primary-color);
}

.map-node.processor .node-icon {
  background: var(--info-color);
}

.map-node.destination .node-icon {
  background: var(--success-color);
}

.node-label {
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
}

.docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.doc-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.doc-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.doc-icon {
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

.doc-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
}

.doc-type {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.doc-date {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.doc-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.doc-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.4;
}

.doc-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.doc-stats .stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.doc-stats .stat-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.doc-stats .stat-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.doc-status.approved {
  color: var(--success-color);
}

.doc-status.in-review {
  color: var(--warning-color);
}

.doc-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  margin-top: 1rem;
}

.doc-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.download:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.share:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.doc-size {
  color: var(--text-secondary);
  font-size: 0.8rem;
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

.request-form {
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

.uploaded-files {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.file-name {
  color: var(--text-primary);
  font-size: 0.9rem;
}

.remove-file {
  padding: 0.25rem 0.5rem;
  background: var(--danger-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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
  .gdpr {
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
  
  .principles-grid {
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
  
  .activities-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .data-map {
    grid-template-columns: 1fr;
  }
  
  .docs-grid {
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
