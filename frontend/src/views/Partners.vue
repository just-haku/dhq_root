<template>
  <div class="partners">
    <div class="page-header">
      <h1>Partners</h1>
      <p>Manage partnerships and collaborative opportunities</p>
    </div>

    <!-- Partnership Overview -->
    <div class="overview-section">
      <div class="section-header">
        <h2>Partnership Overview</h2>
      </div>
      
      <div class="overview-stats">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-handshake"></i>
          </div>
          <div class="stat-content">
            <h3>{{ partnershipStats.totalPartners }}</h3>
            <p>Total Partners</p>
            <span class="stat-change" :class="getChangeClass(partnershipStats.partnersChange)">
              {{ formatChange(partnershipStats.partnersChange) }}
            </span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon active">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <h3>{{ partnershipStats.activePartnerships }}</h3>
            <p>Active Partnerships</p>
            <span class="stat-change" :class="getChangeClass(partnershipStats.activeChange)">
              {{ formatChange(partnershipStats.activeChange) }}
            </span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon revenue">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="stat-content">
            <h3>${{ partnershipStats.revenue.toLocaleString() }}</h3>
            <p>Partnership Revenue</p>
            <span class="stat-change" :class="getChangeClass(partnershipStats.revenueChange)">
              {{ formatChange(partnershipStats.revenueChange) }}
            </span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon opportunities">
            <i class="fas fa-lightbulb"></i>
          </div>
          <div class="stat-content">
            <h3>{{ partnershipStats.opportunities }}</h3>
            <p>New Opportunities</p>
            <span class="stat-change" :class="getChangeClass(partnershipStats.opportunitiesChange)">
              {{ formatChange(partnershipStats.opportunitiesChange) }}
            </span>
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
        <div class="action-card" @click="showPartnerModal = true">
          <div class="action-icon">
            <i class="fas fa-user-plus"></i>
          </div>
          <h3>Add Partner</h3>
          <p>Invite new partner to join</p>
        </div>
        
        <div class="action-card" @click="viewOpportunities">
          <div class="action-icon opportunities">
            <i class="fas fa-lightbulb"></i>
          </div>
          <h3>Opportunities</h3>
          <p>Browse partnership opportunities</p>
        </div>
        
        <div class="action-card" @click="createProposal">
          <div class="action-icon proposal">
            <i class="fas fa-file-contract"></i>
          </div>
          <h3>Create Proposal</h3>
          <p>Submit partnership proposal</p>
        </div>
        
        <div class="action-card" @click="viewAnalytics">
          <div class="action-icon analytics">
            <i class="fas fa-chart-line"></i>
          </div>
          <h3>Analytics</h3>
          <p>View partnership analytics</p>
        </div>
      </div>
    </div>

    <!-- Partners List -->
    <div class="partners-section">
      <div class="section-header">
        <h2>Partners</h2>
        <div class="header-actions">
          <div class="search-box">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search partners..."
              @input="searchPartners"
            />
            <i class="fas fa-search"></i>
          </div>
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterPartners">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="pending">Pending</option>
              <option value="inactive">Inactive</option>
              <option value="proposed">Proposed</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="typeFilter" @change="filterPartners">
              <option value="">All Types</option>
              <option value="technology">Technology</option>
              <option value="reseller">Reseller</option>
              <option value="integration">Integration</option>
              <option value="strategic">Strategic</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading partners...</p>
      </div>

      <div v-else-if="filteredPartners.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-handshake"></i>
        </div>
        <h3>No partners found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showPartnerModal = true">
          <i class="fas fa-plus"></i>
          Add Your First Partner
        </button>
      </div>

      <div v-else class="partners-grid">
        <div 
          v-for="partner in filteredPartners" 
          :key="partner.id"
          class="partner-card"
          :class="{ 'inactive': partner.status === 'inactive' }"
        >
          <div class="partner-header">
            <div class="partner-info">
              <div class="partner-logo">
                <img :src="partner.logo" :alt="partner.name" />
              </div>
              <div class="partner-details">
                <h3>{{ partner.name }}</h3>
                <span :class="['status-badge', partner.status]">{{ formatStatus(partner.status) }}</span>
              </div>
            </div>
            <div class="partner-meta">
              <span :class="['type-badge', partner.type]">{{ formatType(partner.type) }}</span>
              <span class="partner-tier">{{ partner.tier }}</span>
            </div>
          </div>
          
          <div class="partner-content">
            <p>{{ partner.description }}</p>
            
            <div class="partner-stats">
              <div class="stat-item">
                <label>Partnership:</label>
                <span>{{ formatDate(partnershipDate) }}</span>
              </div>
              <div class="stat-item">
                <label>Revenue:</label>
                <span>${{ partner.revenue.toLocaleString() }}</span>
              </div>
              <div class="stat-item">
                <label>Projects:</label>
                <span>{{ partner.projects }}</span>
              </div>
            </div>
            
            <div class="partner-contact">
              <div class="contact-info">
                <span class="contact-name">{{ partner.contact.name }}</span>
                <span class="contact-email">{{ partner.contact.email }}</span>
              </div>
            </div>
          </div>
          
          <div class="partner-footer">
            <div class="partner-actions">
              <button class="action-btn view" @click="viewPartner(partner)">
                <i class="fas fa-eye"></i>
                View
              </button>
              <button class="action-btn edit" @click="editPartner(partner)">
                <i class="fas fa-edit"></i>
                Edit
              </button>
              <button class="action-btn message" @click="messagePartner(partner)">
                <i class="fas fa-envelope"></i>
                Message
              </button>
            </div>
            <div class="partner-health">
              <div class="health-indicator" :class="partner.health">
                <span class="health-dot"></span>
                <span class="health-label">{{ partner.health }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Partnership Opportunities -->
    <div class="opportunities-section">
      <div class="section-header">
        <h2>Partnership Opportunities</h2>
        <div class="header-actions">
          <button class="create-btn" @click="createOpportunity">
            <i class="fas fa-plus"></i>
            Create Opportunity
          </button>
        </div>
      </div>

      <div class="opportunities-grid">
        <div 
          v-for="opportunity in opportunities" 
          :key="opportunity.id"
          class="opportunity-card"
          @click="viewOpportunity(opportunity)"
        >
          <div class="opportunity-header">
            <div class="opportunity-type">
              <i :class="getOpportunityIcon(opportunity.type)"></i>
              <span>{{ opportunity.type }}</span>
            </div>
            <div class="opportunity-urgency">
              <span :class="['urgency-badge', opportunity.urgency]">{{ opportunity.urgency }}</span>
            </div>
          </div>
          
          <div class="opportunity-content">
            <h3>{{ opportunity.title }}</h3>
            <p>{{ opportunity.description }}</p>
            
            <div class="opportunity-details">
              <div class="detail-item">
                <label>Category:</label>
                <span>{{ opportunity.category }}</span>
              </div>
              <div class="detail-item">
                <label>Value:</label>
                <span>${{ opportunity.value.toLocaleString() }}</span>
              </div>
              <div class="detail-item">
                <label>Duration:</label>
                <span>{{ opportunity.duration }}</span>
              </div>
            </div>
          </div>
          
          <div class="opportunity-footer">
            <div class="opportunity-meta">
              <span class="posted-date">{{ formatDate(opportunity.postedDate) }}</span>
              <span class="applicants">{{ opportunity.applicants }} applicants</span>
            </div>
            <div class="opportunity-action">
              <i class="fas fa-arrow-right"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Partnership Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Partnership Analytics</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="analyticsTimeRange" @change="updateAnalytics">
              <option value="month">Last Month</option>
              <option value="quarter">Last Quarter</option>
              <option value="year">Last Year</option>
            </select>
          </div>
        </div>
      </div>

      <div class="analytics-grid">
        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Partnership Growth</h3>
            <div class="analytics-value">{{ analytics.growth }}%</div>
          </div>
          <div class="chart-container">
            <canvas ref="growthChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Revenue by Partner Type</h3>
            <div class="analytics-value">${{ analytics.revenue.toLocaleString() }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="revenueChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Partnership Success Rate</h3>
            <div class="analytics-value">{{ analytics.successRate }}%</div>
          </div>
          <div class="chart-container">
            <canvas ref="successChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Top Performing Partners</h3>
            <div class="analytics-value">{{ analytics.topPartners }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="performanceChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Partner Modal -->
    <div v-if="showPartnerModal" class="modal-overlay" @click="closePartnerModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add New Partner</h2>
          <button class="close-btn" @click="closePartnerModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="partner-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Company Name *</label>
                <input 
                  v-model="partnerForm.name" 
                  type="text" 
                  placeholder="Enter company name"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>Partner Type *</label>
                <select v-model="partnerForm.type" required>
                  <option value="">Select type</option>
                  <option value="technology">Technology</option>
                  <option value="reseller">Reseller</option>
                  <option value="integration">Integration</option>
                  <option value="strategic">Strategic</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Description *</label>
              <textarea 
                v-model="partnerForm.description" 
                placeholder="Describe the partnership"
                rows="4"
                required
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Contact Name *</label>
                <input 
                  v-model="partnerForm.contactName" 
                  type="text" 
                  placeholder="Contact person name"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>Contact Email *</label>
                <input 
                  v-model="partnerForm.contactEmail" 
                  type="email" 
                  placeholder="Contact email"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label>Website</label>
              <input 
                v-model="partnerForm.website" 
                type="url" 
                placeholder="https://example.com"
              />
            </div>

            <div class="form-group">
              <label>Partnership Tier</label>
              <select v-model="partnerForm.tier">
                <option value="bronze">Bronze</option>
                <option value="silver">Silver</option>
                <option value="gold">Gold</option>
                <option value="platinum">Platinum</option>
              </select>
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
                <div class="uploaded-logo" v-if="partnerForm.logo">
                  <img :src="partnerForm.logo" alt="Partner logo" />
                  <button class="remove-logo" @click="removeLogo">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closePartnerModal">Cancel</button>
          <button class="btn-primary" @click="addPartner">
            <i class="fas fa-plus"></i>
            Add Partner
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { Chart } from 'chart.js/auto'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const analyticsTimeRange = ref('quarter')
const showPartnerModal = ref(false)

// Chart refs
const growthChart = ref(null)
const revenueChart = ref(null)
const successChart = ref(null)
const performanceChart = ref(null)

// Partnership stats
const partnershipStats = reactive({
  totalPartners: 45,
  partnersChange: 12,
  activePartnerships: 32,
  activeChange: 8,
  revenue: 125000,
  revenueChange: 15,
  opportunities: 18,
  opportunitiesChange: -5
})

// Analytics data
const analytics = reactive({
  growth: 23,
  revenue: 125000,
  successRate: 87,
  topPartners: 8
})

// Partner form
const partnerForm = reactive({
  name: '',
  type: '',
  description: '',
  contactName: '',
  contactEmail: '',
  website: '',
  tier: 'bronze',
  logo: ''
})

// Partners data
const partners = ref([
  {
    id: 1,
    name: 'TechCorp Solutions',
    description: 'Leading technology integration partner specializing in enterprise solutions',
    status: 'active',
    type: 'technology',
    tier: 'gold',
    logo: '/api/placeholder/100x100',
    partnershipDate: '2023-06-15T00:00:00Z',
    revenue: 45000,
    projects: 12,
    health: 'excellent',
    contact: {
      name: 'Sarah Johnson',
      email: 'sarah@techcorp.com'
    }
  },
  {
    id: 2,
    name: 'Global Resellers Inc',
    description: 'Worldwide reseller network with presence in 50+ countries',
    status: 'active',
    type: 'reseller',
    tier: 'platinum',
    logo: '/api/placeholder/100x100',
    partnershipDate: '2023-03-20T00:00:00Z',
    revenue: 78000,
    projects: 25,
    health: 'good',
    contact: {
      name: 'Michael Chen',
      email: 'michael@globalresellers.com'
    }
  },
  {
    id: 3,
    name: 'Cloud Integration Partners',
    description: 'Specialized cloud integration and migration services',
    status: 'pending',
    type: 'integration',
    tier: 'silver',
    logo: '/api/placeholder/100x100',
    partnershipDate: '2024-01-10T00:00:00Z',
    revenue: 0,
    projects: 0,
    health: 'pending',
    contact: {
      name: 'Emily Davis',
      email: 'emily@cloudintegration.com'
    }
  }
])

// Opportunities data
const opportunities = ref([
  {
    id: 1,
    title: 'AI Integration Partnership',
    description: 'Looking for AI technology partners to integrate advanced machine learning capabilities',
    type: 'technology',
    category: 'Artificial Intelligence',
    urgency: 'high',
    value: 250000,
    duration: '12 months',
    postedDate: '2024-01-20T00:00:00Z',
    applicants: 8
  },
  {
    id: 2,
    title: 'European Market Expansion',
    description: 'Seeking reseller partners for European market expansion',
    type: 'reseller',
    category: 'Market Expansion',
    urgency: 'medium',
    value: 150000,
    duration: '24 months',
    postedDate: '2024-01-18T00:00:00Z',
    applicants: 15
  },
  {
    id: 3,
    title: 'API Integration Partnership',
    description: 'Partner with us for seamless API integration services',
    type: 'integration',
    category: 'API Services',
    urgency: 'low',
    value: 75000,
    duration: '6 months',
    postedDate: '2024-01-15T00:00:00Z',
    applicants: 5
  }
])

// Computed properties
const filteredPartners = computed(() => {
  let filtered = partners.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(partner => 
      partner.name.toLowerCase().includes(query) ||
      partner.description.toLowerCase().includes(query) ||
      partner.contact.name.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(partner => partner.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(partner => partner.type === typeFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.partnershipDate) - new Date(a.partnershipDate))
})

// Methods
const getChangeClass = (change) => {
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return 'neutral'
}

const formatChange = (change) => {
  if (change > 0) return `+${change}%`
  if (change < 0) return `${change}%`
  return '0%'
}

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatType = (type) => {
  return type.charAt(0).toUpperCase() + type.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getEmptyMessage = () => {
  if (searchQuery.value || statusFilter.value || typeFilter.value) {
    return 'No partners match your search criteria'
  }
  return 'No partners found'
}

const getOpportunityIcon = (type) => {
  const icons = {
    'technology': 'fas fa-microchip',
    'reseller': 'fas fa-store',
    'integration': 'fas fa-plug',
    'strategic': 'fas fa-handshake'
  }
  return icons[type] || 'fas fa-briefcase'
}

const searchPartners = () => {
  // Search is handled by computed property
}

const filterPartners = () => {
  // Filtering is handled by computed property
}

const viewOpportunities = () => {
  showSuccess('Viewing partnership opportunities')
}

const createProposal = () => {
  showSuccess('Opening partnership proposal form')
}

const viewAnalytics = () => {
  showSuccess('Opening partnership analytics')
}

const viewPartner = (partner) => {
  showSuccess(`Viewing partner: ${partner.name}`)
}

const editPartner = (partner) => {
  showSuccess(`Editing partner: ${partner.name}`)
}

const messagePartner = (partner) => {
  showSuccess(`Opening message to ${partner.contact.name}`)
}

const viewOpportunity = (opportunity) => {
  showSuccess(`Viewing opportunity: ${opportunity.title}`)
}

const createOpportunity = () => {
  showSuccess('Opening opportunity creation form')
}

const handleLogoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      partnerForm.logo = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const removeLogo = () => {
  partnerForm.logo = ''
}

const addPartner = async () => {
  if (!partnerForm.name || !partnerForm.type || !partnerForm.description || !partnerForm.contactName || !partnerForm.contactEmail) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/partners', partnerForm)
    // if (response.success) {
    //   partners.value.unshift(response.partner)
    //   showSuccess('Partner added successfully')
    //   closePartnerModal()
    //   resetPartnerForm()
    // }
    
    // For demo, simulate addition
    const newPartner = {
      id: Date.now(),
      name: partnerForm.name,
      description: partnerForm.description,
      status: 'pending',
      type: partnerForm.type,
      tier: partnerForm.tier,
      logo: partnerForm.logo || '/api/placeholder/100x100',
      partnershipDate: new Date().toISOString(),
      revenue: 0,
      projects: 0,
      health: 'pending',
      contact: {
        name: partnerForm.contactName,
        email: partnerForm.contactEmail
      }
    }
    
    partners.value.unshift(newPartner)
    showSuccess('Partner added successfully')
    closePartnerModal()
    resetPartnerForm()
  } catch (error) {
    console.error('Error adding partner:', error)
    showError('Failed to add partner')
  }
}

const closePartnerModal = () => {
  showPartnerModal.value = false
  resetPartnerForm()
}

const resetPartnerForm = () => {
  Object.assign(partnerForm, {
    name: '',
    type: '',
    description: '',
    contactName: '',
    contactEmail: '',
    website: '',
    tier: 'bronze',
    logo: ''
  })
}

const updateAnalytics = () => {
  // Update analytics based on time range
  initCharts()
  showSuccess('Analytics updated')
}

const initCharts = () => {
  // Initialize Growth Chart
  if (growthChart.value) growthChart.value.destroy()
  growthChart.value = new Chart(growthChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Partnership Growth',
        data: [32, 35, 38, 42, 45, 45],
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

  // Initialize Revenue Chart
  if (revenueChart.value) revenueChart.value.destroy()
  revenueChart.value = new Chart(revenueChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Technology', 'Reseller', 'Integration', 'Strategic'],
      datasets: [{
        data: [45000, 78000, 25000, 32000],
        backgroundColor: [
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(139, 92, 246)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  })

  // Initialize Success Chart
  if (successChart.value) successChart.value.destroy()
  successChart.value = new Chart(successChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Q1', 'Q2', 'Q3', 'Q4'],
      datasets: [{
        label: 'Success Rate %',
        data: [82, 85, 87, 87],
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { 
          beginAtZero: false,
          min: 70,
          max: 100
        }
      }
    }
  })

  // Initialize Performance Chart
  if (performanceChart.value) performanceChart.value.destroy()
  performanceChart.value = new Chart(performanceChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['TechCorp', 'Global Resellers', 'Cloud Partners', 'DataSync', 'SecurityPro'],
      datasets: [{
        label: 'Revenue',
        data: [45000, 78000, 25000, 32000, 18000],
        backgroundColor: 'rgba(139, 92, 246, 0.8)',
        borderColor: 'rgb(139, 92, 246)',
        borderWidth: 1
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

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/partners')
    // if (response.success) {
    //   partners.value = response.partners || []
    //   opportunities.value = response.opportunities || []
    //   Object.assign(partnershipStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
    nextTick(() => {
      initCharts()
    })
  } catch (error) {
    console.error('Error loading partners data:', error)
    showError('Failed to load partners data')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.partners {
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
.partners-section,
.opportunities-section,
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

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.stat-icon {
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

.stat-icon.active {
  background: var(--success-color);
}

.stat-icon.revenue {
  background: var(--warning-color);
}

.stat-icon.opportunities {
  background: var(--info-color);
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.stat-content p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
}

.stat-change {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.stat-change.positive {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stat-change.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-change.neutral {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
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

.action-icon.opportunities {
  background: var(--info-color);
}

.action-icon.proposal {
  background: var(--warning-color);
}

.action-icon.analytics {
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

.filter-dropdown,
.time-range {
  position: relative;
}

.filter-dropdown select,
.time-range select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

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

.partners-grid,
.opportunities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.partner-card,
.opportunity-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.partner-card:hover,
.opportunity-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.partner-card.inactive {
  opacity: 0.7;
  border-left: 4px solid var(--warning-color);
}

.partner-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.partner-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.partner-logo {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
}

.partner-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.partner-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
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

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.inactive {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.status-badge.proposed {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.partner-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
}

.type-badge {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-transform: capitalize;
}

.partner-tier {
  padding: 0.25rem 0.75rem;
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.partner-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.partner-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.partner-contact {
  margin-bottom: 1rem;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.contact-name {
  color: var(--text-primary);
  font-weight: 600;
}

.contact-email {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.partner-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

.partner-actions {
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

.action-btn.edit:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.message:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.partner-health {
  display: flex;
  align-items: center;
}

.health-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success-color);
}

.health-indicator.excellent .health-dot {
  background: var(--success-color);
}

.health-indicator.good .health-dot {
  background: var(--info-color);
}

.health-indicator.pending .health-dot {
  background: var(--warning-color);
}

.opportunity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.opportunity-type {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--primary-color);
  font-weight: 600;
}

.urgency-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.urgency-badge.high {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.urgency-badge.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.urgency-badge.low {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.opportunity-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.opportunity-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.opportunity-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
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

.opportunity-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

.opportunity-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.opportunity-action {
  width: 32px;
  height: 32px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.opportunity-action:hover {
  background: var(--primary-hover);
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.analytics-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
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
  color: var(--primary-color);
}

.chart-container {
  height: 200px;
  position: relative;
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
  max-width: 600px;
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

.partner-form {
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
  .partners {
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
  
  .search-box input {
    width: 200px;
  }
  
  .partners-grid,
  .opportunities-grid {
    grid-template-columns: 1fr;
  }
  
  .partner-stats,
  .opportunity-details {
    grid-template-columns: 1fr;
  }
  
  .partner-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .analytics-grid {
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
