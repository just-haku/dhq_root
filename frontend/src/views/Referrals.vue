<template>
  <div class="referrals">
    <div class="page-header">
      <h1>Referral Program</h1>
      <p>Invite friends and earn rewards</p>
    </div>

    <!-- Referral Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="card-content">
            <h3>{{ referralStats.totalReferrals }}</h3>
            <p>Total Referrals</p>
            <span class="referral-count">{{ referralStats.thisMonth }} this month</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon rewards">
            <i class="fas fa-gift"></i>
          </div>
          <div class="card-content">
            <h3>${{ referralStats.totalRewards }}</h3>
            <p>Total Rewards</p>
            <span class="reward-status">${{ referralStats.pendingRewards }} pending</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon conversion">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="card-content">
            <h3>{{ referralStats.conversionRate }}%</h3>
            <p>Conversion Rate</p>
            <span class="conversion-trend" :class="referralStats.conversionTrend">
              {{ referralStats.conversionTrend }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon next">
            <i class="fas fa-trophy"></i>
          </div>
          <div class="card-content">
            <h3>{{ referralStats.nextReward }}</h3>
            <p>Next Reward</p>
            <span class="reward-progress">{{ referralStats.progressToNext }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Referral Link Section -->
    <div class="referral-link-section">
      <div class="section-header">
        <h2>Your Referral Link</h2>
        <button class="share-btn" @click="shareReferralLink">
          <i class="fas fa-share-alt"></i>
          Share
        </button>
      </div>

      <div class="referral-link-card">
        <div class="link-display">
          <div class="link-input">
            <input 
              :value="referralLink" 
              readonly 
              type="text"
              ref="referralInput"
            />
            <button class="copy-btn" @click="copyReferralLink">
              <i :class="copied ? 'fas fa-check' : 'fas fa-copy'"></i>
              {{ copied ? 'Copied!' : 'Copy' }}
            </button>
          </div>
          <div class="link-stats">
            <span class="stat-item">
              <i class="fas fa-eye"></i>
              {{ referralStats.linkClicks }} clicks
            </span>
            <span class="stat-item">
              <i class="fas fa-user-plus"></i>
              {{ referralStats.signUps }} sign-ups
            </span>
          </div>
        </div>

        <div class="share-options">
          <button class="share-option" @click="shareViaEmail">
            <i class="fas fa-envelope"></i>
            Email
          </button>
          <button class="share-option" @click="shareViaTwitter">
            <i class="fab fa-twitter"></i>
            Twitter
          </button>
          <button class="share-option" @click="shareViaFacebook">
            <i class="fab fa-facebook"></i>
            Facebook
          </button>
          <button class="share-option" @click="shareViaLinkedIn">
            <i class="fab fa-linkedin"></i>
            LinkedIn
          </button>
        </div>
      </div>
    </div>

    <!-- Referral Rewards -->
    <div class="rewards-section">
      <div class="section-header">
        <h2>Referral Rewards</h2>
        <button class="claim-btn" @click="claimRewards" :disabled="!hasPendingRewards">
          <i class="fas fa-gift"></i>
          Claim Rewards
        </button>
      </div>

      <div class="rewards-grid">
        <div 
          v-for="reward in referralRewards" 
          :key="reward.id"
          class="reward-card"
          :class="{ 
            'available': reward.status === 'available',
            'claimed': reward.status === 'claimed',
            'pending': reward.status === 'pending'
          }"
        >
          <div class="reward-header">
            <div class="reward-icon">
              <i :class="getRewardIcon(reward.type)"></i>
            </div>
            <div class="reward-info">
              <h3>{{ reward.title }}</h3>
              <p>{{ reward.description }}</p>
            </div>
            <div class="reward-status">
              <span :class="['status-badge', reward.status]">{{ reward.status }}</span>
            </div>
          </div>

          <div class="reward-details">
            <div class="reward-item">
              <label>Value:</label>
              <span class="reward-value">${{ reward.value }}</span>
            </div>
            <div class="reward-item">
              <label>Required Referrals:</label>
              <span>{{ reward.requiredReferrals }}</span>
            </div>
            <div class="reward-item">
              <label>Progress:</label>
              <div class="progress-container">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: (reward.progress / reward.requiredReferrals * 100) + '%' }"
                  ></div>
                </div>
                <span>{{ reward.progress }}/{{ reward.requiredReferrals }}</span>
              </div>
            </div>
            <div class="reward-item">
              <label>Expires:</label>
              <span>{{ formatDate(reward.expiresAt) }}</span>
            </div>
          </div>

          <div class="reward-actions">
            <button 
              v-if="reward.status === 'available'"
              class="action-btn claim"
              @click="claimReward(reward)"
            >
              <i class="fas fa-gift"></i>
              Claim
            </button>
            <button 
              v-if="reward.status === 'pending'"
              class="action-btn disabled"
              disabled
            >
              <i class="fas fa-clock"></i>
              Pending
            </button>
            <span v-if="reward.status === 'claimed'" class="claimed-text">
              <i class="fas fa-check"></i>
              Claimed
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Referral History -->
    <div class="history-section">
      <div class="section-header">
        <h2>Referral History</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="historyFilter" @change="filterHistory">
              <option value="">All Time</option>
              <option value="30">Last 30 Days</option>
              <option value="90">Last 90 Days</option>
              <option value="365">Last Year</option>
            </select>
          </div>
          <button class="export-btn" @click="exportHistory">
            <i class="fas fa-download"></i>
            Export
          </button>
        </div>
      </div>

      <div class="history-table-container">
        <table class="history-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Referred User</th>
              <th>Email</th>
              <th>Status</th>
              <th>Reward</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="referral in filteredHistory" 
              :key="referral.id"
              class="history-row"
            >
              <td>{{ formatDate(referral.date) }}</td>
              <td>
                <div class="user-info">
                  <div class="user-avatar">
                    <img :src="referral.avatar || getDefaultAvatar()" :alt="referral.name" />
                  </div>
                  <span class="user-name">{{ referral.name }}</span>
                </div>
              </td>
              <td>{{ referral.email }}</td>
              <td>
                <span :class="['status-badge', referral.status]">{{ referral.status }}</span>
              </td>
              <td>
                <span v-if="referral.reward" class="reward-amount">${{ referral.reward }}</span>
                <span v-else class="no-reward">-</span>
              </td>
              <td>
                <button 
                  class="action-btn remind"
                  @click="sendReminder(referral)"
                  :disabled="referral.status === 'completed'"
                >
                  <i class="fas fa-bell"></i>
                  Remind
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Referral Settings Modal -->
    <div v-if="showSettingsModal" class="modal-overlay" @click="closeSettingsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Referral Settings</h2>
          <button class="close-btn" @click="closeSettingsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="settings-form">
            <div class="setting-section">
              <h3>Notification Preferences</h3>
              <div class="setting-item">
                <label>Email Notifications</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="referralSettings.emailNotifications"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>New Referral Alerts</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="referralSettings.newReferralAlerts"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>Reward Notifications</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="referralSettings.rewardNotifications"
                  />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="setting-section">
              <h3>Referral Message</h3>
              <div class="setting-item">
                <label>Custom Message</label>
                <textarea 
                  v-model="referralSettings.customMessage" 
                  placeholder="Customize your referral message..."
                  rows="4"
                ></textarea>
              </div>
              <div class="setting-item">
                <label>Include Your Name</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="referralSettings.includeName"
                  />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="setting-section">
              <h3>Privacy Settings</h3>
              <div class="setting-item">
                <label>Public Profile</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="referralSettings.publicProfile"
                  />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="setting-item">
                <label>Show Referral Count</label>
                <label class="switch">
                  <input 
                    type="checkbox" 
                    v-model="referralSettings.showReferralCount"
                  />
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeSettingsModal">Cancel</button>
          <button class="btn-primary" @click="saveSettings">Save Settings</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const copied = ref(false)
const historyFilter = ref('')
const showSettingsModal = ref(false)
const referralInput = ref(null)

// Referral stats
const referralStats = reactive({
  totalReferrals: 24,
  thisMonth: 3,
  totalRewards: 450.00,
  pendingRewards: 75.00,
  conversionRate: 68,
  conversionTrend: 'up',
  nextReward: 3,
  progressToNext: 75,
  linkClicks: 156,
  signUps: 24
})

// Referral settings
const referralSettings = reactive({
  emailNotifications: true,
  newReferralAlerts: true,
  rewardNotifications: true,
  customMessage: 'Join me on this amazing platform and get great benefits!',
  includeName: true,
  publicProfile: false,
  showReferralCount: true
})

// Mock data
const referralLink = ref('https://app.example.com/referral/abc123def456')

const referralRewards = ref([
  {
    id: 1,
    title: '$10 Credit',
    description: 'Get $10 credit for each successful referral',
    type: 'credit',
    value: 10,
    requiredReferrals: 1,
    progress: 3,
    status: 'available',
    expiresAt: '2024-12-31'
  },
  {
    id: 2,
    title: 'Free Month',
    description: 'Get one month free for 3 successful referrals',
    type: 'subscription',
    value: '1 month',
    requiredReferrals: 3,
    progress: 3,
    status: 'available',
    expiresAt: '2024-12-31'
  },
  {
    id: 3,
    title: '$50 Bonus',
    description: 'Earn $50 bonus for 5 successful referrals',
    type: 'cash',
    value: 50,
    requiredReferrals: 5,
    progress: 2,
    status: 'pending',
    expiresAt: '2024-12-31'
  },
  {
    id: 4,
    title: 'Premium Upgrade',
    description: 'Upgrade to premium plan for 10 referrals',
    type: 'upgrade',
    value: 'Premium',
    requiredReferrals: 10,
    progress: 8,
    status: 'pending',
    expiresAt: '2024-12-31'
  }
])

const referralHistory = ref([
  {
    id: 1,
    date: '2024-01-15',
    name: 'John Smith',
    email: 'john.smith@example.com',
    status: 'completed',
    reward: '$10',
    avatar: 'https://via.placeholder.com/40x40?text=JS'
  },
  {
    id: 2,
    date: '2024-01-10',
    name: 'Sarah Johnson',
    email: 'sarah.j@example.com',
    status: 'pending',
    reward: null,
    avatar: 'https://via.placeholder.com/40x40?text=SJ'
  },
  {
    id: 3,
    date: '2024-01-05',
    name: 'Mike Davis',
    email: 'mike.davis@example.com',
    status: 'completed',
    reward: '$10',
    avatar: 'https://via.placeholder.com/40x40?text=MD'
  },
  {
    id: 4,
    date: '2023-12-28',
    name: 'Emily Wilson',
    email: 'emily.w@example.com',
    status: 'expired',
    reward: null,
    avatar: 'https://via.placeholder.com/40x40?text=EW'
  }
])

// Computed properties
const filteredHistory = computed(() => {
  let filtered = referralHistory.value
  
  if (historyFilter.value) {
    const days = parseInt(historyFilter.value)
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000)
    filtered = filtered.filter(referral => 
      new Date(referral.date) >= cutoffDate
    )
  }
  
  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const hasPendingRewards = computed(() => {
  return referralRewards.value.some(reward => reward.status === 'available')
})

// Methods
const loadReferralData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/referrals')
    // if (response.success) {
    //   Object.assign(referralStats, response.stats)
    //   referralLink.value = response.referralLink
    //   referralRewards.value = response.rewards || []
    //   referralHistory.value = response.history || []
    //   referralSettings.value = response.settings || referralSettings
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading referral data:', error)
    showError('Failed to load referral data')
  } finally {
    loading.value = false
  }
}

const filterHistory = () => {
  // This is reactive, no additional action needed
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const getDefaultAvatar = () => {
  return 'https://via.placeholder.com/40x40?text=U'
}

const getRewardIcon = (type) => {
  const icons = {
    'credit': 'fas fa-credit-card',
    'subscription': 'fas fa-calendar',
    'cash': 'fas fa-dollar-sign',
    'upgrade': 'fas fa-arrow-up'
  }
  return icons[type] || 'fas fa-gift'
}

const copyReferralLink = async () => {
  try {
    await navigator.clipboard.writeText(referralLink.value)
    copied.value = true
    showSuccess('Referral link copied to clipboard')
    
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    showError('Failed to copy referral link')
  }
}

const shareReferralLink = async () => {
  try {
    if (navigator.share) {
      await navigator.share({
        title: 'Join me on this amazing platform!',
        text: referralSettings.customMessage,
        url: referralLink.value
      })
    } else {
      // Fallback to copying link
      await copyReferralLink()
    }
  } catch (error) {
    console.error('Error sharing referral link:', error)
  }
}

const shareViaEmail = () => {
  const subject = 'Join me on this amazing platform!'
  const body = `${referralSettings.customMessage}\n\n${referralLink.value}`
  const mailtoUrl = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
  window.open(mailtoUrl)
}

const shareViaTwitter = () => {
  const text = `${referralSettings.customMessage} ${referralLink.value}`
  const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`
  window.open(twitterUrl, '_blank')
}

const shareViaFacebook = () => {
  const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(referralLink.value)}`
  window.open(facebookUrl, '_blank')
}

const shareViaLinkedIn = () => {
  const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(referralLink.value)}`
  window.open(linkedInUrl, '_blank')
}

const claimReward = async (reward) => {
  try {
    // const response = await apiPost(`/referrals/claim-reward/${reward.id}`)
    // if (response.success) {
    //   reward.status = 'claimed'
    //   showSuccess('Reward claimed successfully')
    // }
    
    // For demo, simulate claim
    reward.status = 'claimed'
    showSuccess('Reward claimed successfully')
  } catch (error) {
    console.error('Error claiming reward:', error)
    showError('Failed to claim reward')
  }
}

const claimRewards = async () => {
  const availableRewards = referralRewards.value.filter(r => r.status === 'available')
  
  if (availableRewards.length === 0) {
    showError('No rewards available to claim')
    return
  }

  try {
    // const response = await apiPost('/referrals/claim-rewards', { 
    //   rewardIds: availableRewards.map(r => r.id) 
    // })
    // if (response.success) {
    //   availableRewards.forEach(reward => {
    //     reward.status = 'claimed'
    //   })
    //   showSuccess('All available rewards claimed successfully')
    // }
    
    // For demo, simulate claim
    availableRewards.forEach(reward => {
      reward.status = 'claimed'
    })
    showSuccess('All available rewards claimed successfully')
  } catch (error) {
    console.error('Error claiming rewards:', error)
    showError('Failed to claim rewards')
  }
}

const sendReminder = async (referral) => {
  if (referral.status === 'completed') {
    showError('Referral already completed')
    return
  }

  try {
    // const response = await apiPost(`/referrals/send-reminder/${referral.id}`)
    // if (response.success) {
    //   showSuccess('Reminder sent successfully')
    // }
    
    // For demo, simulate send
    showSuccess('Reminder sent successfully')
  } catch (error) {
    console.error('Error sending reminder:', error)
    showError('Failed to send reminder')
  }
}

const exportHistory = async () => {
  try {
    // const response = await apiPost('/referrals/export-history')
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `referral-history-${new Date().toISOString().split('T')[0]}.csv`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Referral history exported successfully')
    // }
    
    // For demo, simulate export
    showSuccess('Referral history exported successfully')
  } catch (error) {
    console.error('Error exporting history:', error)
    showError('Failed to export referral history')
  }
}

const saveSettings = async () => {
  try {
    // const response = await apiPut('/referrals/settings', referralSettings)
    // if (response.success) {
    //   showSuccess('Settings saved successfully')
    //   closeSettingsModal()
    // }
    
    // For demo, simulate save
    showSuccess('Settings saved successfully')
    closeSettingsModal()
  } catch (error) {
    console.error('Error saving settings:', error)
    showError('Failed to save settings')
  }
}

const closeSettingsModal = () => {
  showSettingsModal.value = false
}

// Lifecycle
onMounted(() => {
  loadReferralData()
})
</script>

<style scoped>
.referrals {
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

.card-icon.rewards {
  background: var(--success-color);
}

.card-icon.conversion {
  background: var(--warning-color);
}

.card-icon.next {
  background: var(--info-color);
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

.referral-count,
.reward-status,
.conversion-trend,
.reward-progress {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.referral-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.reward-status {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.conversion-trend.up {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.conversion-trend.down {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.reward-progress {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.referral-link-section,
.rewards-section,
.history-section {
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

.share-btn,
.claim-btn {
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

.share-btn:hover,
.claim-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.claim-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.referral-link-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
}

.link-display {
  margin-bottom: 2rem;
}

.link-input {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.link-input input {
  flex: 1;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  font-family: 'Courier New', monospace;
}

.copy-btn {
  padding: 1rem 1.5rem;
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

.link-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat-item i {
  color: var(--primary-color);
}

.share-options {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.share-option {
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
  font-weight: 500;
}

.share-option:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-2px);
}

.rewards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.reward-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.reward-card:hover {
  transform: translateY(-2px);
}

.reward-card.available {
  border-color: var(--success-color);
}

.reward-card.claimed {
  opacity: 0.6;
}

.reward-card.pending {
  border-color: var(--warning-color);
}

.reward-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.reward-icon {
  width: 50px;
  height: 50px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.reward-info {
  flex: 1;
}

.reward-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.reward-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.reward-status {
  flex-shrink: 0;
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

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.claimed {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.reward-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.reward-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.reward-item label {
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
}

.reward-value {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--glass-bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
  border-radius: 3px;
  transition: width 0.3s ease;
}

.reward-actions {
  display: flex;
  justify-content: center;
}

.action-btn {
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

.action-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.action-btn.claim {
  background: var(--success-color);
}

.action-btn.claim:hover:not(:disabled) {
  background: var(--success-hover);
}

.action-btn.remind {
  background: var(--info-color);
}

.action-btn.remind:hover:not(:disabled) {
  background: var(--info-hover);
}

.action-btn.disabled {
  background: var(--glass-bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.claimed-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--success-color);
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

.export-btn {
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

.export-btn:hover {
  background: var(--primary-hover);
}

.history-table-container {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--glass-bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.history-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.history-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.history-row {
  transition: background 0.3s ease;
}

.history-row:hover {
  background: var(--glass-bg-hover);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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

.user-name {
  font-weight: 600;
  color: var(--text-primary);
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.expired {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.reward-amount {
  color: var(--success-color);
  font-weight: 600;
}

.no-reward {
  color: var(--text-tertiary);
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
  padding: 1.5rem;
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
  font-size: 1.2rem;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.setting-section {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.setting-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-item label {
  font-weight: 500;
  color: var(--text-primary);
}

.setting-item textarea {
  width: 100%;
  padding: 0.75rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.9rem;
  resize: vertical;
  min-height: 80px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch .slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--text-tertiary);
  transition: 0.4s;
  border-radius: 24px;
}

.switch .slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

.switch input:checked + .slider {
  background-color: var(--primary-color);
}

.switch input:checked + .slider:before {
  transform: translateX(26px);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
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
  .referrals {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .link-input {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .share-options {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .rewards-grid {
    grid-template-columns: 1fr;
  }
  
  .reward-details {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
