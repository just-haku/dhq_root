<template>
  <div class="affiliate">
    <div class="page-header">
      <h1>Affiliate Program</h1>
      <p>Manage your affiliate marketing and earn commissions</p>
    </div>

    <!-- Affiliate Status -->
    <div class="status-section">
      <div class="section-header">
        <h2>Your Affiliate Status</h2>
      </div>
      
      <div class="status-card">
        <div class="status-header">
          <div class="affiliate-info">
            <div class="affiliate-icon">
              <i class="fas fa-percentage"></i>
            </div>
            <div class="affiliate-details">
              <h3>{{ affiliateStatus.level }}</h3>
              <p>{{ affiliateStatus.description }}</p>
            </div>
          </div>
          <div class="status-badge">
            <span :class="['badge', affiliateStatus.status]">{{ formatStatus(affiliateStatus.status) }}</span>
          </div>
        </div>
        
        <div class="status-stats">
          <div class="stat-item">
            <div class="stat-value">${{ affiliateStats.totalEarnings.toLocaleString() }}</div>
            <div class="stat-label">Total Earnings</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ affiliateStats.totalReferrals }}</div>
            <div class="stat-label">Total Referrals</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ affiliateStats.activeReferrals }}</div>
            <div class="stat-label">Active Referrals</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ affiliateStats.conversionRate }}%</div>
            <div class="stat-label">Conversion Rate</div>
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
        <div class="action-card" @click="showReferralModal = true">
          <div class="action-icon">
            <i class="fas fa-user-plus"></i>
          </div>
          <h3>Refer Friends</h3>
          <p>Share your referral link</p>
        </div>
        
        <div class="action-card" @click="viewMarketingMaterials">
          <div class="action-icon marketing">
            <i class="fas fa-bullhorn"></i>
          </div>
          <h3>Marketing Materials</h3>
          <p>Access banners and assets</p>
        </div>
        
        <div class="action-card" @click="viewPayouts">
          <div class="action-icon payout">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <h3>Payouts</h3>
          <p>View payment history</p>
        </div>
        
        <div class="action-card" @click="viewAnalytics">
          <div class="action-icon analytics">
            <i class="fas fa-chart-line"></i>
          </div>
          <h3>Analytics</h3>
          <p>Track performance</p>
        </div>
      </div>
    </div>

    <!-- Referral Link -->
    <div class="referral-section">
      <div class="section-header">
        <h2>Your Referral Link</h2>
        <div class="header-actions">
          <div class="referral-stats">
            <span>{{ referralStats.clicks }} clicks</span>
            <span>{{ referralStats.conversions }} conversions</span>
          </div>
        </div>
      </div>

      <div class="referral-card">
        <div class="referral-content">
          <h3>Share and Earn</h3>
          <p>Share your unique referral link and earn commissions for every successful referral.</p>
          
          <div class="referral-link">
            <input 
              v-model="referralLink" 
              type="text" 
              readonly 
              @click="selectReferralLink"
            />
            <button class="copy-btn" @click="copyReferralLink">
              <i class="fas fa-copy"></i>
              Copy
            </button>
          </div>
          
          <div class="referral-methods">
            <button class="method-btn" @click="shareViaEmail">
              <i class="fas fa-envelope"></i>
              Email
            </button>
            <button class="method-btn" @click="shareViaSocial">
              <i class="fas fa-share-alt"></i>
              Social
            </button>
            <button class="method-btn" @click="shareViaQR">
              <i class="fas fa-qrcode"></i>
              QR Code
            </button>
            <button class="method-btn" @click="generateShortLink">
              <i class="fas fa-compress"></i>
              Short Link
            </button>
          </div>
        </div>
        
        <div class="referral-commission">
          <h4>Commission Structure</h4>
          <div class="commission-tiers">
            <div class="tier-item">
              <div class="tier-info">
                <span class="tier-name">Bronze</span>
                <span class="tier-rate">10%</span>
              </div>
              <span class="tier-requirement">1-10 referrals</span>
            </div>
            <div class="tier-item">
              <div class="tier-info">
                <span class="tier-name">Silver</span>
                <span class="tier-rate">15%</span>
              </div>
              <span class="tier-requirement">11-25 referrals</span>
            </div>
            <div class="tier-item">
              <div class="tier-info">
                <span class="tier-name">Gold</span>
                <span class="tier-rate">20%</span>
              </div>
              <span class="tier-requirement">26-50 referrals</span>
            </div>
            <div class="tier-item">
              <div class="tier-info">
                <span class="tier-name">Platinum</span>
                <span class="tier-rate">25%</span>
              </div>
              <span class="tier-requirement">50+ referrals</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Referrals List -->
    <div class="referrals-section">
      <div class="section-header">
        <h2>Your Referrals</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="referralFilter" @change="filterReferrals">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="active">Active</option>
              <option value="converted">Converted</option>
              <option value="expired">Expired</option>
            </select>
          </div>
          <div class="time-range">
            <select v-model="referralTimeRange" @change="updateReferrals">
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading referrals...</p>
      </div>

      <div v-else-if="filteredReferrals.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-users"></i>
        </div>
        <h3>No referrals found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showReferralModal = true">
          <i class="fas fa-plus"></i>
          Make Your First Referral
        </button>
      </div>

      <div v-else class="referrals-table">
        <div class="table-header">
          <div class="header-cell">Referral</div>
          <div class="header-cell">Status</div>
          <div class="header-cell">Commission</div>
          <div class="header-cell">Date</div>
          <div class="header-cell">Actions</div>
        </div>
        
        <div 
          v-for="referral in filteredReferrals" 
          :key="referral.id"
          class="table-row"
        >
          <div class="table-cell">
            <div class="referral-info">
              <div class="referral-avatar">
                <img :src="referral.avatar" :alt="referral.name" />
              </div>
              <div class="referral-details">
                <span class="referral-name">{{ referral.name }}</span>
                <span class="referral-email">{{ referral.email }}</span>
              </div>
            </div>
          </div>
          
          <div class="table-cell">
            <span :class="['status-badge', referral.status]">{{ formatReferralStatus(referral.status) }}</span>
          </div>
          
          <div class="table-cell">
            <span class="commission-amount">${{ referral.commission.toFixed(2) }}</span>
          </div>
          
          <div class="table-cell">
            <span class="referral-date">{{ formatDate(referral.date) }}</span>
          </div>
          
          <div class="table-cell">
            <div class="referral-actions">
              <button class="action-btn view" @click="viewReferral(referral)">
                <i class="fas fa-eye"></i>
              </button>
              <button class="action-btn message" @click="messageReferral(referral)">
                <i class="fas fa-envelope"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Marketing Materials -->
    <div class="marketing-section">
      <div class="section-header">
        <h2>Marketing Materials</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="materialFilter" @change="filterMaterials">
              <option value="">All Materials</option>
              <option value="banner">Banners</option>
              <option value="email">Email Templates</option>
              <option value="social">Social Media</option>
              <option value="video">Videos</option>
            </select>
          </div>
        </div>
      </div>

      <div class="materials-grid">
        <div 
          v-for="material in filteredMaterials" 
          :key="material.id"
          class="material-card"
          @click="viewMaterial(material)"
        >
          <div class="material-preview">
            <img :src="material.preview" :alt="material.title" />
            <div class="material-type">
              <i :class="getMaterialIcon(material.type)"></i>
              <span>{{ material.type }}</span>
            </div>
          </div>
          
          <div class="material-content">
            <h3>{{ material.title }}</h3>
            <p>{{ material.description }}</p>
            
            <div class="material-stats">
              <span class="downloads">{{ material.downloads }} downloads</span>
              <span class="conversion">{{ material.conversionRate }}% conversion</span>
            </div>
          </div>
          
          <div class="material-footer">
            <div class="material-size">{{ material.size }}</div>
            <button class="download-btn" @click.stop="downloadMaterial(material)">
              <i class="fas fa-download"></i>
              Download
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Payouts -->
    <div class="payouts-section">
      <div class="section-header">
        <h2>Payout History</h2>
        <div class="header-actions">
          <div class="payout-summary">
            <span class="pending-amount">Pending: ${{ payoutStats.pending.toFixed(2) }}</span>
            <span class="total-amount">Total Paid: ${{ payoutStats.totalPaid.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <div class="payouts-table">
        <div class="table-header">
          <div class="header-cell">Date</div>
          <div class="header-cell">Amount</div>
          <div class="header-cell">Status</div>
          <div class="header-cell">Method</div>
          <div class="header-cell">Referrals</div>
          <div class="header-cell">Actions</div>
        </div>
        
        <div 
          v-for="payout in payouts" 
          :key="payout.id"
          class="table-row"
        >
          <div class="table-cell">
            <span class="payout-date">{{ formatDate(payout.date) }}</span>
          </div>
          
          <div class="table-cell">
            <span class="payout-amount">${{ payout.amount.toFixed(2) }}</span>
          </div>
          
          <div class="table-cell">
            <span :class="['status-badge', payout.status]">{{ formatPayoutStatus(payout.status) }}</span>
          </div>
          
          <div class="table-cell">
            <span class="payout-method">{{ payout.method }}</span>
          </div>
          
          <div class="table-cell">
            <span class="payout-referrals">{{ payout.referrals }}</span>
          </div>
          
          <div class="table-cell">
            <div class="payout-actions">
              <button class="action-btn view" @click="viewPayout(payout)">
                <i class="fas fa-eye"></i>
              </button>
              <button 
                v-if="payout.status === 'pending'"
                class="action-btn cancel" 
                @click="cancelPayout(payout)"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Affiliate Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Performance Analytics</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="analyticsTimeRange" @change="updateAnalytics">
              <option value="week">Last Week</option>
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
            <h3>Referral Growth</h3>
            <div class="analytics-value">{{ analytics.growth }}%</div>
          </div>
          <div class="chart-container">
            <canvas ref="growthChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Earnings Trend</h3>
            <div class="analytics-value">${{ analytics.earnings.toLocaleString() }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="earningsChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Conversion Rate</h3>
            <div class="analytics-value">{{ analytics.conversionRate }}%</div>
          </div>
          <div class="chart-container">
            <canvas ref="conversionChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Top Performing Materials</h3>
            <div class="analytics-value">{{ analytics.topMaterials }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="materialsChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Referral Modal -->
    <div v-if="showReferralModal" class="modal-overlay" @click="closeReferralModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Refer a Friend</h2>
          <button class="close-btn" @click="closeReferralModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="referral-form">
            <div class="form-intro">
              <h3>Share the Benefits</h3>
              <p>Invite friends to join and earn commissions when they sign up and become active users.</p>
            </div>

            <div class="form-group">
              <label>Friend's Email *</label>
              <input 
                v-model="referralForm.email" 
                type="email" 
                placeholder="Enter friend's email address"
                required
              />
            </div>

            <div class="form-group">
              <label>Friend's Name</label>
              <input 
                v-model="referralForm.name" 
                type="text" 
                placeholder="Enter friend's name"
              />
            </div>

            <div class="form-group">
              <label>Personal Message</label>
              <textarea 
                v-model="referralForm.message" 
                placeholder="Add a personal message (optional)"
                rows="4"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Referral Method</label>
              <div class="method-options">
                <label class="radio-item">
                  <input type="radio" v-model="referralForm.method" value="email" />
                  <span>Send Email Invitation</span>
                </label>
                <label class="radio-item">
                  <input type="radio" v-model="referralForm.method" value="link" />
                  <span>Copy Referral Link</span>
                </label>
                <label class="radio-item">
                  <input type="radio" v-model="referralForm.method" value="social" />
                  <span>Share on Social Media</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeReferralModal">Cancel</button>
          <button class="btn-primary" @click="sendReferral">
            <i class="fas fa-paper-plane"></i>
            Send Referral
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
const referralFilter = ref('')
const referralTimeRange = ref('month')
const materialFilter = ref('')
const analyticsTimeRange = ref('month')
const showReferralModal = ref(false)

// Chart refs
const growthChart = ref(null)
const earningsChart = ref(null)
const conversionChart = ref(null)
const materialsChart = ref(null)

// Affiliate status
const affiliateStatus = reactive({
  level: 'Gold Affiliate',
  description: 'You are a top-performing affiliate with premium benefits',
  status: 'active',
  joinedDate: '2023-06-15T00:00:00Z'
})

// Affiliate stats
const affiliateStats = reactive({
  totalEarnings: 3450,
  totalReferrals: 67,
  activeReferrals: 23,
  conversionRate: 34
})

// Referral stats
const referralStats = reactive({
  clicks: 1250,
  conversions: 234
})

// Payout stats
const payoutStats = reactive({
  pending: 450,
  totalPaid: 3000
})

// Analytics data
const analytics = reactive({
  growth: 28,
  earnings: 1250,
  conversionRate: 34,
  topMaterials: 12
})

// Referral link
const referralLink = ref('https://affiliate.example.com/ref/abc123xyz789')

// Referral form
const referralForm = reactive({
  email: '',
  name: '',
  message: '',
  method: 'email'
})

// Referrals data
const referrals = ref([
  {
    id: 1,
    name: 'John Smith',
    email: 'john.smith@example.com',
    status: 'active',
    commission: 45.00,
    date: '2024-01-20T00:00:00Z',
    avatar: '/api/placeholder/40x40'
  },
  {
    id: 2,
    name: 'Sarah Johnson',
    email: 'sarah.j@example.com',
    status: 'converted',
    commission: 67.50,
    date: '2024-01-18T00:00:00Z',
    avatar: '/api/placeholder/40x40'
  },
  {
    id: 3,
    name: 'Mike Wilson',
    email: 'mike.w@example.com',
    status: 'pending',
    commission: 0.00,
    date: '2024-01-15T00:00:00Z',
    avatar: '/api/placeholder/40x40'
  }
])

// Marketing materials
const marketingMaterials = ref([
  {
    id: 1,
    title: 'Product Banner 728x90',
    description: 'Standard leaderboard banner for websites and blogs',
    type: 'banner',
    preview: '/api/placeholder/300x200',
    size: '728x90px',
    downloads: 145,
    conversionRate: 12
  },
  {
    id: 2,
    title: 'Welcome Email Template',
    description: 'Professional email template for inviting new users',
    type: 'email',
    preview: '/api/placeholder/300x200',
    size: 'HTML',
    downloads: 89,
    conversionRate: 18
  },
  {
    id: 3,
    title: 'Social Media Post Pack',
    description: 'Ready-to-use social media posts and images',
    type: 'social',
    preview: '/api/placeholder/300x200',
    size: '15MB',
    downloads: 234,
    conversionRate: 8
  },
  {
    id: 4,
    title: 'Product Demo Video',
    description: '2-minute product demonstration video',
    type: 'video',
    preview: '/api/placeholder/300x200',
    size: '45MB',
    downloads: 67,
    conversionRate: 25
  }
])

// Payouts data
const payouts = ref([
  {
    id: 1,
    date: '2024-01-15T00:00:00Z',
    amount: 450.00,
    status: 'paid',
    method: 'PayPal',
    referrals: 12
  },
  {
    id: 2,
    date: '2024-01-01T00:00:00Z',
    amount: 675.00,
    status: 'paid',
    method: 'Bank Transfer',
    referrals: 18
  },
  {
    id: 3,
    date: '2024-02-01T00:00:00Z',
    amount: 450.00,
    status: 'pending',
    method: 'PayPal',
    referrals: 8
  }
])

// Computed properties
const filteredReferrals = computed(() => {
  let filtered = referrals.value

  if (referralFilter.value) {
    filtered = filtered.filter(referral => referral.status === referralFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const filteredMaterials = computed(() => {
  let filtered = marketingMaterials.value

  if (materialFilter.value) {
    filtered = filtered.filter(material => material.type === materialFilter.value)
  }

  return filtered.sort((a, b) => b.downloads - a.downloads)
})

// Methods
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatReferralStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatPayoutStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getEmptyMessage = () => {
  if (referralFilter.value) {
    return 'No referrals match your filter criteria'
  }
  return 'No referrals found'
}

const getMaterialIcon = (type) => {
  const icons = {
    'banner': 'fas fa-image',
    'email': 'fas fa-envelope',
    'social': 'fas fa-share-alt',
    'video': 'fas fa-video'
  }
  return icons[type] || 'fas fa-file'
}

const filterReferrals = () => {
  // Filtering is handled by computed property
}

const filterMaterials = () => {
  // Filtering is handled by computed property
}

const updateReferrals = () => {
  // Update referrals based on time range
  showSuccess('Referrals updated')
}

const viewMarketingMaterials = () => {
  showSuccess('Opening marketing materials')
}

const viewPayouts = () => {
  showSuccess('Opening payout history')
}

const viewAnalytics = () => {
  showSuccess('Opening affiliate analytics')
}

const selectReferralLink = () => {
  referralLink.value.select()
}

const copyReferralLink = async () => {
  try {
    await navigator.clipboard.writeText(referralLink.value)
    showSuccess('Referral link copied to clipboard')
  } catch (error) {
    console.error('Error copying referral link:', error)
    showError('Failed to copy referral link')
  }
}

const shareViaEmail = () => {
  const subject = 'Join Our Affiliate Program'
  const body = `I'd like to invite you to join our affiliate program. Here's my referral link: ${referralLink.value}`
  window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
}

const shareViaSocial = () => {
  showSuccess('Opening social share options')
}

const shareViaQR = () => {
  showSuccess('Generating QR code for referral link')
}

const generateShortLink = () => {
  showSuccess('Generating shortened referral link')
}

const viewReferral = (referral) => {
  showSuccess(`Viewing referral: ${referral.name}`)
}

const messageReferral = (referral) => {
  showSuccess(`Opening message to ${referral.name}`)
}

const viewMaterial = (material) => {
  showSuccess(`Viewing material: ${material.title}`)
}

const downloadMaterial = (material) => {
  showSuccess(`Downloading ${material.title}`)
}

const viewPayout = (payout) => {
  showSuccess(`Viewing payout details`)
}

const cancelPayout = async (payout) => {
  const confirmed = await showConfirm('Are you sure you want to cancel this payout?')
  if (confirmed) {
    try {
      // const response = await apiDelete(`/affiliate/payouts/${payout.id}`)
      // if (response.success) {
      //   payout.status = 'cancelled'
      //   showSuccess('Payout cancelled successfully')
      // }
      
      // For demo, simulate cancellation
      payout.status = 'cancelled'
      showSuccess('Payout cancelled successfully')
    } catch (error) {
      console.error('Error cancelling payout:', error)
      showError('Failed to cancel payout')
    }
  }
}

const closeReferralModal = () => {
  showReferralModal.value = false
  resetReferralForm()
}

const resetReferralForm = () => {
  Object.assign(referralForm, {
    email: '',
    name: '',
    message: '',
    method: 'email'
  })
}

const sendReferral = async () => {
  if (!referralForm.email) {
    showError('Please enter friend\'s email address')
    return
  }

  try {
    // const response = await apiPost('/affiliate/referral', referralForm)
    // if (response.success) {
    //   showSuccess('Referral sent successfully')
    //   closeReferralModal()
    //   resetReferralForm()
    // }
    
    // For demo, simulate sending
    showSuccess('Referral sent successfully')
    closeReferralModal()
    resetReferralForm()
  } catch (error) {
    console.error('Error sending referral:', error)
    showError('Failed to send referral')
  }
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
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'New Referrals',
        data: [3, 5, 2, 8, 4, 6, 3],
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

  // Initialize Earnings Chart
  if (earningsChart.value) earningsChart.value.destroy()
  earningsChart.value = new Chart(earningsChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      datasets: [{
        label: 'Earnings $',
        data: [250, 320, 280, 400],
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
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Conversion Chart
  if (conversionChart.value) conversionChart.value.destroy()
  conversionChart.value = new Chart(conversionChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Converted', 'Pending', 'Expired'],
      datasets: [{
        data: [34, 45, 21],
        backgroundColor: [
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)'
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

  // Initialize Materials Chart
  if (materialsChart.value) materialsChart.value.destroy()
  materialsChart.value = new Chart(materialsChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Banners', 'Emails', 'Social', 'Videos'],
      datasets: [{
        label: 'Downloads',
        data: [145, 89, 234, 67],
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
    // const response = await apiGet('/affiliate')
    // if (response.success) {
    //   referrals.value = response.referrals || []
    //   marketingMaterials.value = response.materials || []
    //   payouts.value = response.payouts || []
    //   Object.assign(affiliateStatus, response.status)
    //   Object.assign(affiliateStats, response.stats)
    //   Object.assign(referralStats, response.referralStats)
    //   Object.assign(payoutStats, response.payoutStats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
    nextTick(() => {
      initCharts()
    })
  } catch (error) {
    console.error('Error loading affiliate data:', error)
    showError('Failed to load affiliate data')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.affiliate {
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

.status-section,
.actions-section,
.referral-section,
.referrals-section,
.marketing-section,
.payouts-section,
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

.status-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.affiliate-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.affiliate-icon {
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

.affiliate-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.affiliate-details p {
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

.status-stats {
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

.action-icon.marketing {
  background: var(--info-color);
}

.action-icon.payout {
  background: var(--success-color);
}

.action-icon.analytics {
  background: var(--warning-color);
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

.referral-stats {
  display: flex;
  gap: 2rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.referral-card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.referral-content h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.referral-content p {
  margin: 0 0 2rem 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.referral-link {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.referral-link input {
  flex: 1;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.copy-btn {
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

.copy-btn:hover {
  background: var(--primary-hover);
}

.referral-methods {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.method-btn {
  padding: 0.75rem 1.25rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.method-btn:hover {
  background: var(--glass-bg-hover);
}

.referral-commission h4 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.commission-tiers {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tier-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.tier-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.tier-name {
  font-weight: 600;
  color: var(--text-primary);
}

.tier-rate {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--primary-color);
}

.tier-requirement {
  color: var(--text-secondary);
  font-size: 0.9rem;
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

.payout-summary {
  display: flex;
  gap: 2rem;
  font-size: 0.9rem;
}

.pending-amount {
  color: var(--warning-color);
  font-weight: 600;
}

.total-amount {
  color: var(--success-color);
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

.create-first-btn {
  padding: 1rem 2rem;
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
  margin-top: 2rem;
}

.create-first-btn:hover {
  background: var(--primary-hover);
}

.referrals-table,
.payouts-table {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
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

.referral-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.referral-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.referral-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.referral-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.referral-name {
  color: var(--text-primary);
  font-weight: 600;
}

.referral-email {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.converted {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.expired {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.status-badge.paid {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.cancelled {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.commission-amount,
.payout-amount {
  font-weight: 600;
  color: var(--success-color);
}

.referral-date,
.payout-date {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.referral-actions,
.payout-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
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

.action-btn.message:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.cancel:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.materials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.material-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.material-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.material-preview {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.material-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.material-type {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.5rem 0.75rem;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.material-content {
  padding: 1.5rem;
}

.material-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.material-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.material-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.material-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--glass-bg-tertiary);
  border-top: 1px solid var(--glass-border);
}

.material-size {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.download-btn {
  padding: 0.5rem 1rem;
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
}

.download-btn:hover {
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

.referral-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-intro {
  text-align: center;
  padding: 0 0 1.5rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.form-intro h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.form-intro p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
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

.method-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.radio-item input[type="radio"] {
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
  .affiliate {
    padding: 1rem;
  }
  
  .status-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .referral-card {
    grid-template-columns: 1fr;
  }
  
  .referral-methods {
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
  
  .materials-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .payout-summary {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
