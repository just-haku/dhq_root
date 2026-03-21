<template>
  <div class="early-access">
    <div class="page-header">
      <h1>Early Access Program</h1>
      <p>Get exclusive early access to upcoming features and products</p>
    </div>

    <!-- Access Status -->
    <div class="status-section">
      <div class="section-header">
        <h2>Your Access Status</h2>
      </div>
      
      <div class="status-card">
        <div class="status-header">
          <div class="access-info">
            <div class="access-icon">
              <i class="fas fa-key"></i>
            </div>
            <div class="access-details">
              <h3>{{ accessStatus.level }}</h3>
              <p>{{ accessStatus.description }}</p>
            </div>
          </div>
          <div class="status-badge">
            <span :class="['badge', accessStatus.status]">{{ formatStatus(accessStatus.status) }}</span>
          </div>
        </div>
        
        <div class="status-stats">
          <div class="stat-item">
            <div class="stat-value">{{ accessStats.featuresUnlocked }}</div>
            <div class="stat-label">Features Unlocked</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ accessStats.productsAccessed }}</div>
            <div class="stat-label">Products Accessed</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ accessStats.exclusiveContent }}</div>
            <div class="stat-label">Exclusive Content</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ accessStatus.points }}</div>
            <div class="stat-label">Access Points</div>
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
        <div class="action-card" @click="showUpgradeModal = true">
          <div class="action-icon">
            <i class="fas fa-crown"></i>
          </div>
          <h3>Upgrade Access</h3>
          <p>Get premium early access features</p>
        </div>
        
        <div class="action-card" @click="viewAvailableFeatures">
          <div class="action-icon features">
            <i class="fas fa-rocket"></i>
          </div>
          <h3>Available Features</h3>
          <p>See what's available for early access</p>
        </div>
        
        <div class="action-card" @click="viewExclusiveContent">
          <div class="action-icon content">
            <i class="fas fa-gem"></i>
          </div>
          <h3>Exclusive Content</h3>
          <p>Access exclusive tutorials and resources</p>
        </div>
        
        <div class="action-card" @click="inviteFriends">
          <div class="action-icon invite">
            <i class="fas fa-user-plus"></i>
          </div>
          <h3>Invite Friends</h3>
          <p>Share early access and earn rewards</p>
        </div>
      </div>
    </div>

    <!-- Early Access Features -->
    <div class="features-section">
      <div class="section-header">
        <h2>Early Access Features</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="featureFilter" @change="filterFeatures">
              <option value="">All Features</option>
              <option value="unlocked">Unlocked</option>
              <option value="locked">Locked</option>
              <option value="coming-soon">Coming Soon</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="categoryFilter" @change="filterFeatures">
              <option value="">All Categories</option>
              <option value="product">New Products</option>
              <option value="feature">New Features</option>
              <option value="integration">Integrations</option>
              <option value="tool">Tools & Utilities</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading early access features...</p>
      </div>

      <div v-else-if="filteredFeatures.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-key"></i>
        </div>
        <h3>No features found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="features-grid">
        <div 
          v-for="feature in filteredFeatures" 
          :key="feature.id"
          class="feature-card"
          :class="{ 'locked': feature.locked, 'coming-soon': feature.status === 'coming-soon' }"
        >
          <div class="feature-header">
            <div class="feature-icon">
              <i :class="getFeatureIcon(feature.category)"></i>
            </div>
            <div class="feature-meta">
              <span :class="['status-badge', feature.status]">{{ formatFeatureStatus(feature.status) }}</span>
              <span class="feature-category">{{ feature.category }}</span>
              <span v-if="feature.locked" class="lock-badge">
                <i class="fas fa-lock"></i>
                {{ feature.requiredLevel }}
              </span>
            </div>
          </div>
          
          <div class="feature-content">
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
            
            <div class="feature-details">
              <div class="detail-item">
                <label>Release:</label>
                <span>{{ formatDate(feature.releaseDate) }}</span>
              </div>
              <div class="detail-item">
                <label>Access Type:</label>
                <span>{{ feature.accessType }}</span>
              </div>
              <div class="detail-item">
                <label>Points:</label>
                <span>{{ feature.points }} pts</span>
              </div>
            </div>
            
            <div class="feature-benefits" v-if="feature.benefits.length > 0">
              <h4>Benefits:</h4>
              <ul>
                <li v-for="benefit in feature.benefits" :key="benefit">{{ benefit }}</li>
              </ul>
            </div>
          </div>
          
          <div class="feature-footer">
            <div class="feature-stats">
              <span class="users">{{ feature.users }} users</span>
              <span class="rating">{{ feature.rating }}★</span>
              <span class="availability">{{ feature.availability }}</span>
            </div>
            <div class="feature-actions">
              <button 
                v-if="!feature.locked && feature.status === 'available'"
                class="action-btn access" 
                @click="accessFeature(feature)"
              >
                <i class="fas fa-unlock"></i>
                Access Now
              </button>
              <button 
                v-else-if="feature.locked"
                class="action-btn upgrade" 
                @click="upgradeAccess(feature)"
              >
                <i class="fas fa-crown"></i>
                Upgrade
              </button>
              <button 
                v-else
                class="action-btn view" 
                @click="viewFeature(feature)"
              >
                <i class="fas fa-eye"></i>
                View
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Access Levels -->
    <div class="levels-section">
      <div class="section-header">
        <h2>Access Levels</h2>
      </div>

      <div class="levels-grid">
        <div 
          v-for="level in accessLevels" 
          :key="level.id"
          class="level-card"
          :class="{ 'current': level.id === accessStatus.currentLevel, 'recommended': level.recommended }"
        >
          <div class="level-header">
            <div class="level-icon">
              <i :class="level.icon"></i>
            </div>
            <div class="level-info">
              <h3>{{ level.name }}</h3>
              <p>{{ level.description }}</p>
            </div>
            <div class="level-badge">
              <span v-if="level.id === accessStatus.currentLevel" class="current-badge">Current</span>
              <span v-if="level.recommended" class="recommended-badge">Recommended</span>
            </div>
          </div>
          
          <div class="level-price">
            <div class="price-amount">
              <span class="currency">{{ level.currency }}</span>
              <span class="amount">{{ level.price }}</span>
              <span class="period">/month</span>
            </div>
            <div v-if="level.discount" class="discount-badge">
              {{ level.discount }}% OFF
            </div>
          </div>
          
          <div class="level-features">
            <h4>Features:</h4>
            <ul>
              <li v-for="feature in level.features" :key="feature" class="feature-item">
                <i class="fas fa-check"></i>
                {{ feature }}
              </li>
            </ul>
          </div>
          
          <div class="level-footer">
            <button 
              :class="['level-btn', level.id === accessStatus.currentLevel ? 'current' : 'upgrade']"
              @click="selectLevel(level)"
            >
              {{ level.id === accessStatus.currentLevel ? 'Current Plan' : 'Upgrade Now' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Exclusive Content -->
    <div class="content-section">
      <div class="section-header">
        <h2>Exclusive Content</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="contentTypeFilter" @change="filterContent">
              <option value="">All Content</option>
              <option value="tutorial">Tutorials</option>
              <option value="webinar">Webinars</option>
              <option value="guide">Guides</option>
              <option value="template">Templates</option>
            </select>
          </div>
        </div>
      </div>

      <div class="content-grid">
        <div 
          v-for="content in filteredContent" 
          :key="content.id"
          class="content-card"
          @click="viewContent(content)"
        >
          <div class="content-thumbnail">
            <img :src="content.thumbnail" :alt="content.title" />
            <div class="content-duration">{{ content.duration }}</div>
          </div>
          
          <div class="content-info">
            <h3>{{ content.title }}</h3>
            <p>{{ content.description }}</p>
            
            <div class="content-meta">
              <span class="content-type">{{ content.type }}</span>
              <span class="content-level">{{ content.level }}</span>
              <span class="content-date">{{ formatDate(content.publishDate) }}</span>
            </div>
          </div>
          
          <div class="content-footer">
            <div class="content-stats">
              <span class="views">{{ content.views }} views</span>
              <span class="likes">{{ content.likes }} likes</span>
            </div>
            <div class="content-action">
              <i class="fas fa-play"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Invite Friends -->
    <div class="invite-section">
      <div class="section-header">
        <h2>Invite Friends</h2>
        <div class="header-actions">
          <div class="invite-stats">
            <span>{{ inviteStats.invited }} invited</span>
            <span>{{ inviteStats.joined }} joined</span>
            <span>{{ inviteStats.rewards }} rewards earned</span>
          </div>
        </div>
      </div>

      <div class="invite-card">
        <div class="invite-content">
          <h3>Share Early Access</h3>
          <p>Invite friends to join the early access program and earn exclusive rewards when they sign up.</p>
          
          <div class="invite-link">
            <input 
              v-model="inviteLink" 
              type="text" 
              readonly 
              @click="selectInviteLink"
            />
            <button class="copy-btn" @click="copyInviteLink">
              <i class="fas fa-copy"></i>
              Copy
            </button>
          </div>
          
          <div class="invite-methods">
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
          </div>
        </div>
        
        <div class="invite-rewards">
          <h4>Rewards</h4>
          <div class="reward-list">
            <div class="reward-item">
              <div class="reward-icon">
                <i class="fas fa-user-plus"></i>
              </div>
              <div class="reward-info">
                <span class="reward-title">Friend Joins</span>
                <span class="reward-value">+50 Points</span>
              </div>
            </div>
            <div class="reward-item">
              <div class="reward-icon">
                <i class="fas fa-crown"></i>
              </div>
              <div class="reward-info">
                <span class="reward-title">Friend Upgrades</span>
                <span class="reward-value">+200 Points</span>
              </div>
            </div>
            <div class="reward-item">
              <div class="reward-icon">
                <i class="fas fa-gift"></i>
              </div>
              <div class="reward-info">
                <span class="reward-title">5 Friends Join</span>
                <span class="reward-value">+1 Month Free</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upgrade Modal -->
    <div v-if="showUpgradeModal" class="modal-overlay" @click="closeUpgradeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Upgrade Early Access</h2>
          <button class="close-btn" @click="closeUpgradeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="upgrade-options">
            <div 
              v-for="option in upgradeOptions" 
              :key="option.id"
              class="upgrade-option"
              :class="{ 'selected': selectedUpgrade === option.id }"
              @click="selectedUpgrade = option.id"
            >
              <div class="option-header">
                <h3>{{ option.name }}</h3>
                <div class="option-price">
                  <span class="currency">{{ option.currency }}</span>
                  <span class="amount">{{ option.price }}</span>
                  <span class="period">/month</span>
                </div>
              </div>
              
              <div class="option-description">
                <p>{{ option.description }}</p>
              </div>
              
              <div class="option-features">
                <ul>
                  <li v-for="feature in option.features" :key="feature" class="feature-item">
                    <i class="fas fa-check"></i>
                    {{ feature }}
                  </li>
                </ul>
              </div>
              
              <div class="option-bonus" v-if="option.bonus">
                <div class="bonus-badge">
                  <i class="fas fa-gift"></i>
                  {{ option.bonus }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeUpgradeModal">Cancel</button>
          <button class="btn-primary" @click="confirmUpgrade">
            <i class="fas fa-crown"></i>
            Upgrade Now
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
const featureFilter = ref('')
const categoryFilter = ref('')
const contentTypeFilter = ref('')
const showUpgradeModal = ref(false)
const selectedUpgrade = ref(null)

// Access status
const accessStatus = reactive({
  level: 'Premium Early Access',
  description: 'You have access to all premium early access features and exclusive content',
  status: 'active',
  currentLevel: 2,
  points: 1250,
  joinedDate: '2024-01-15T00:00:00Z'
})

// Access stats
const accessStats = reactive({
  featuresUnlocked: 18,
  productsAccessed: 5,
  exclusiveContent: 42,
  earlyAccessDays: 67
})

// Invite stats
const inviteStats = reactive({
  invited: 12,
  joined: 8,
  rewards: 650
})

// Invite link
const inviteLink = ref('https://early-access.example.com/invite/abc123xyz789')

// Early access features
const earlyAccessFeatures = ref([
  {
    id: 1,
    title: 'AI-Powered Analytics Pro',
    description: 'Advanced analytics with AI insights and predictive modeling',
    status: 'available',
    category: 'feature',
    locked: false,
    releaseDate: '2024-02-01T00:00:00Z',
    accessType: 'Premium',
    points: 150,
    users: 234,
    rating: 4.8,
    availability: 'Limited',
    benefits: [
      'AI-powered insights',
      'Predictive analytics',
      'Custom dashboards',
      'Real-time data'
    ]
  },
  {
    id: 2,
    title: 'Next-Gen Collaboration Suite',
    description: 'Revolutionary collaboration tools with real-time editing and AI assistance',
    status: 'available',
    category: 'product',
    locked: true,
    requiredLevel: 'VIP',
    releaseDate: '2024-02-15T00:00:00Z',
    accessType: 'VIP',
    points: 300,
    users: 0,
    rating: 0,
    availability: 'VIP Only',
    benefits: [
      'Real-time collaboration',
      'AI assistance',
      'Advanced security',
      'Unlimited storage'
    ]
  },
  {
    id: 3,
    title: 'Advanced Integration Hub',
    description: 'Connect with 100+ third-party services and custom APIs',
    status: 'coming-soon',
    category: 'integration',
    locked: false,
    releaseDate: '2024-03-01T00:00:00Z',
    accessType: 'Premium',
    points: 100,
    users: 0,
    rating: 0,
    availability: 'Coming Soon',
    benefits: [
      '100+ integrations',
      'Custom API support',
      'Webhook automation',
      'Data synchronization'
    ]
  }
])

// Access levels
const accessLevels = ref([
  {
    id: 1,
    name: 'Basic Early Access',
    description: 'Get early access to basic features and content',
    icon: 'fas fa-star',
    currency: '$',
    price: 9,
    features: [
      'Early access to basic features',
      'Monthly exclusive content',
      'Community access',
      'Email support'
    ]
  },
  {
    id: 2,
    name: 'Premium Early Access',
    description: 'Unlock premium features and exclusive content',
    icon: 'fas fa-crown',
    currency: '$',
    price: 29,
    recommended: true,
    discount: 20,
    features: [
      'All basic features',
      'Premium early access',
      'Weekly exclusive content',
      'Priority support',
      'Advanced integrations',
      'Beta program access'
    ]
  },
  {
    id: 3,
    name: 'VIP Early Access',
    description: 'Ultimate access with exclusive benefits and personalized support',
    icon: 'fas fa-gem',
    currency: '$',
    price: 99,
    features: [
      'All premium features',
      'VIP-only features',
      'Daily exclusive content',
      '24/7 dedicated support',
      'Custom integrations',
      'Private beta access',
      'Personal onboarding'
    ]
  }
])

// Exclusive content
const exclusiveContent = ref([
  {
    id: 1,
    title: 'Mastering AI Analytics',
    description: 'Complete guide to using AI-powered analytics for business insights',
    type: 'tutorial',
    level: 'Advanced',
    duration: '2h 30m',
    thumbnail: '/api/placeholder/300x200',
    publishDate: '2024-01-20T00:00:00Z',
    views: 1234,
    likes: 89
  },
  {
    id: 2,
    title: 'Future of Collaboration Tools',
    description: 'Exclusive webinar on upcoming collaboration features and trends',
    type: 'webinar',
    level: 'Intermediate',
    duration: '1h 15m',
    thumbnail: '/api/placeholder/300x200',
    publishDate: '2024-01-18T00:00:00Z',
    views: 567,
    likes: 45
  },
  {
    id: 3,
    title: 'Advanced Integration Templates',
    description: 'Ready-to-use templates for common integration scenarios',
    type: 'template',
    level: 'All Levels',
    duration: '45m',
    thumbnail: '/api/placeholder/300x200',
    publishDate: '2024-01-15T00:00:00Z',
    views: 890,
    likes: 67
  }
])

// Upgrade options
const upgradeOptions = ref([
  {
    id: 'monthly',
    name: 'Monthly Premium',
    description: 'Flexible monthly billing with full premium access',
    currency: '$',
    price: 29,
    features: [
      'All premium early access features',
      'Weekly exclusive content',
      'Priority support',
      'Advanced integrations'
    ]
  },
  {
    id: 'yearly',
    name: 'Yearly Premium',
    description: 'Best value with 2 months free',
    currency: '$',
    price: 290,
    bonus: '2 Months Free',
    features: [
      'All premium early access features',
      'Weekly exclusive content',
      'Priority support',
      'Advanced integrations',
      'Annual savings of $58'
    ]
  }
])

// Computed properties
const filteredFeatures = computed(() => {
  let filtered = earlyAccessFeatures.value

  if (featureFilter.value) {
    filtered = filtered.filter(feature => {
      if (featureFilter.value === 'unlocked') return !feature.locked
      if (featureFilter.value === 'locked') return feature.locked
      if (featureFilter.value === 'coming-soon') return feature.status === 'coming-soon'
      return true
    })
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(feature => feature.category === categoryFilter.value)
  }

  return filtered.sort((a, b) => {
    if (a.locked && !b.locked) return 1
    if (!a.locked && b.locked) return -1
    return 0
  })
})

const filteredContent = computed(() => {
  let filtered = exclusiveContent.value

  if (contentTypeFilter.value) {
    filtered = filtered.filter(content => content.type === contentTypeFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate))
})

// Methods
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatFeatureStatus = (status) => {
  return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatDate = (dateString) => {
  if (!dateString) return 'TBD'
  return new Date(dateString).toLocaleDateString()
}

const getEmptyMessage = () => {
  if (featureFilter.value || categoryFilter.value) {
    return 'No features match your filter criteria'
  }
  return 'No early access features available'
}

const getFeatureIcon = (category) => {
  const icons = {
    'product': 'fas fa-box',
    'feature': 'fas fa-star',
    'integration': 'fas fa-plug',
    'tool': 'fas fa-wrench'
  }
  return icons[category] || 'fas fa-cube'
}

const filterFeatures = () => {
  // Filtering is handled by computed property
}

const filterContent = () => {
  // Filtering is handled by computed property
}

const viewAvailableFeatures = () => {
  featureFilter.value = 'unlocked'
  categoryFilter.value = ''
  showSuccess('Showing available early access features')
}

const viewExclusiveContent = () => {
  showSuccess('Opening exclusive content library')
}

const inviteFriends = () => {
  showSuccess('Opening invite friends panel')
}

const accessFeature = async (feature) => {
  try {
    // const response = await apiPost(`/early-access/features/${feature.id}/access`)
    // if (response.success) {
    //   showSuccess('Feature accessed successfully')
    // }
    
    // For demo, simulate access
    showSuccess(`Accessed ${feature.title} successfully`)
  } catch (error) {
    console.error('Error accessing feature:', error)
    showError('Failed to access feature')
  }
}

const upgradeAccess = (feature) => {
  showUpgradeModal.value = true
  selectedUpgrade.value = 'monthly'
}

const viewFeature = (feature) => {
  showSuccess(`Viewing details for ${feature.title}`)
}

const selectLevel = async (level) => {
  if (level.id === accessStatus.currentLevel) {
    showSuccess('You are already on this plan')
    return
  }

  try {
    // const response = await apiPost('/early-access/upgrade', { levelId: level.id })
    // if (response.success) {
    //   accessStatus.currentLevel = level.id
    //   accessStatus.level = level.name
    //   showSuccess(`Successfully upgraded to ${level.name}`)
    // }
    
    // For demo, simulate upgrade
    accessStatus.currentLevel = level.id
    accessStatus.level = level.name
    showSuccess(`Successfully upgraded to ${level.name}`)
  } catch (error) {
    console.error('Error upgrading access:', error)
    showError('Failed to upgrade access')
  }
}

const viewContent = (content) => {
  showSuccess(`Opening ${content.title}`)
}

const selectInviteLink = () => {
  inviteLink.value.select()
}

const copyInviteLink = async () => {
  try {
    await navigator.clipboard.writeText(inviteLink.value)
    showSuccess('Invite link copied to clipboard')
  } catch (error) {
    console.error('Error copying invite link:', error)
    showError('Failed to copy invite link')
  }
}

const shareViaEmail = () => {
  const subject = 'Join Early Access Program'
  const body = `I'd like to invite you to join the Early Access Program. Here's your invite link: ${inviteLink.value}`
  window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
}

const shareViaSocial = () => {
  showSuccess('Opening social share options')
}

const shareViaQR = () => {
  showSuccess('Generating QR code for invite link')
}

const closeUpgradeModal = () => {
  showUpgradeModal.value = false
  selectedUpgrade.value = null
}

const confirmUpgrade = async () => {
  if (!selectedUpgrade.value) {
    showError('Please select an upgrade option')
    return
  }

  try {
    // const response = await apiPost('/early-access/upgrade', { option: selectedUpgrade.value })
    // if (response.success) {
    //   showSuccess('Upgrade completed successfully')
    //   closeUpgradeModal()
    // }
    
    // For demo, simulate upgrade
    showSuccess('Upgrade completed successfully')
    closeUpgradeModal()
  } catch (error) {
    console.error('Error upgrading:', error)
    showError('Failed to complete upgrade')
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/early-access')
    // if (response.success) {
    //   earlyAccessFeatures.value = response.features || []
    //   exclusiveContent.value = response.content || []
    //   Object.assign(accessStatus, response.status)
    //   Object.assign(accessStats, response.stats)
    //   Object.assign(inviteStats, response.inviteStats)
    // }
    
    // For demo, use mock data
    loading.value = false
  } catch (error) {
    console.error('Error loading early access data:', error)
    showError('Failed to load early access data')
    loading.value = false
  }
})
</script>

<style scoped>
.early-access {
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
.features-section,
.levels-section,
.content-section,
.invite-section {
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

.access-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.access-icon {
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

.access-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.access-details p {
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

.action-icon.features {
  background: var(--info-color);
}

.action-icon.content {
  background: var(--warning-color);
}

.action-icon.invite {
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

.features-grid,
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.feature-card,
.content-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.feature-card:hover,
.content-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.feature-card.locked {
  border-left: 4px solid var(--warning-color);
}

.feature-card.coming-soon {
  border-left: 4px solid var(--info-color);
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

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.available {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.coming-soon {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.feature-category {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.lock-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
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

.feature-details {
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

.feature-benefits {
  margin-top: 1rem;
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

.feature-benefits li {
  padding: 0.25rem 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  position: relative;
  padding-left: 1rem;
}

.feature-benefits li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--success-color);
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

.feature-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
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

.action-btn.access:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.upgrade:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.view:hover {
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

.levels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.level-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  position: relative;
  transition: all 0.3s ease;
}

.level-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.level-card.current {
  border-color: var(--success-color);
}

.level-card.recommended {
  border-color: var(--primary-color);
}

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.level-icon {
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

.level-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.level-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.level-badge {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.current-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.recommended-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.level-price {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.price-amount {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.currency {
  font-size: 1.2rem;
  color: var(--text-primary);
  font-weight: 600;
}

.amount {
  font-size: 2rem;
  color: var(--text-primary);
  font-weight: 700;
}

.period {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.discount-badge {
  padding: 0.5rem 1rem;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.level-features h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.level-features ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.feature-item {
  padding: 0.5rem 0;
  color: var(--text-secondary);
  position: relative;
  padding-left: 1.5rem;
}

.feature-item::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--success-color);
  font-weight: 600;
}

.level-footer {
  margin-top: 2rem;
}

.level-btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.level-btn.current {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--glass-border);
}

.level-btn.upgrade {
  background: var(--primary-color);
  color: white;
}

.level-btn.upgrade:hover {
  background: var(--primary-hover);
}

.content-thumbnail {
  position: relative;
  margin-bottom: 1rem;
  border-radius: 8px;
  overflow: hidden;
}

.content-thumbnail img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.content-duration {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem 0.5rem;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 4px;
  font-size: 0.8rem;
}

.content-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.content-info p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.content-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.content-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.content-action {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.content-action:hover {
  background: var(--primary-hover);
}

.invite-stats {
  display: flex;
  gap: 2rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.invite-card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.invite-content h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.invite-content p {
  margin: 0 0 2rem 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.invite-link {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.invite-link input {
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

.invite-methods {
  display: flex;
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

.invite-rewards h4 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.reward-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reward-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.reward-icon {
  width: 40px;
  height: 40px;
  background: var(--success-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.reward-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.reward-title {
  color: var(--text-primary);
  font-weight: 500;
}

.reward-value {
  color: var(--success-color);
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
  max-width: 800px;
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

.upgrade-options {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.upgrade-option {
  background: var(--glass-bg-primary);
  border: 2px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upgrade-option:hover {
  border-color: var(--primary-color);
}

.upgrade-option.selected {
  border-color: var(--primary-color);
  background: var(--glass-bg-hover);
}

.option-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.option-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.option-price {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.option-description {
  margin-bottom: 1.5rem;
}

.option-description p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.option-features ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.option-bonus {
  margin-top: 1rem;
}

.bonus-badge {
  padding: 0.5rem 1rem;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
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
  .early-access {
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
  
  .features-grid,
  .content-grid,
  .levels-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-details {
    grid-template-columns: 1fr;
  }
  
  .invite-card {
    grid-template-columns: 1fr;
  }
  
  .invite-stats {
    flex-direction: column;
    gap: 1rem;
  }
  
  .invite-methods {
    flex-direction: column;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
