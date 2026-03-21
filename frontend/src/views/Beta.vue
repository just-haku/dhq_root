<template>
  <div class="beta">
    <div class="page-header">
      <h1>Beta Program</h1>
      <p>Get early access to new features and help shape the future</p>
    </div>

    <!-- Beta Status -->
    <div class="status-section">
      <div class="section-header">
        <h2>Your Beta Status</h2>
      </div>
      
      <div class="status-card">
        <div class="status-header">
          <div class="beta-info">
            <div class="beta-icon">
              <i class="fas fa-flask"></i>
            </div>
            <div class="beta-details">
              <h3>{{ betaStatus.program }}</h3>
              <p>{{ betaStatus.description }}</p>
            </div>
          </div>
          <div class="status-badge">
            <span :class="['badge', betaStatus.status]">{{ formatStatus(betaStatus.status) }}</span>
          </div>
        </div>
        
        <div class="status-stats">
          <div class="stat-item">
            <div class="stat-value">{{ betaStats.featuresTested }}</div>
            <div class="stat-label">Features Tested</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ betaStats.bugsReported }}</div>
            <div class="stat-label">Bugs Reported</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ betaStats.contributions }}</div>
            <div class="stat-label">Contributions</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ betaStats.reputation }}</div>
            <div class="stat-label">Reputation Score</div>
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
        <div class="action-card" @click="showEnrollModal = true" v-if="!betaStatus.enrolled">
          <div class="action-icon">
            <i class="fas fa-user-plus"></i>
          </div>
          <h3>Join Beta Program</h3>
          <p>Enroll in the beta program to get early access</p>
        </div>
        
        <div class="action-card" @click="viewAvailableFeatures">
          <div class="action-icon features">
            <i class="fas fa-rocket"></i>
          </div>
          <h3>Available Features</h3>
          <p>See what's ready for testing</p>
        </div>
        
        <div class="action-card" @click="reportBug">
          <div class="action-icon bug">
            <i class="fas fa-bug"></i>
          </div>
          <h3>Report Bug</h3>
          <p>Help us improve by reporting issues</p>
        </div>
        
        <div class="action-card" @click="submitFeedback">
          <div class="action-icon feedback">
            <i class="fas fa-comment"></i>
          </div>
          <h3>Submit Feedback</h3>
          <p>Share your thoughts and suggestions</p>
        </div>
      </div>
    </div>

    <!-- Beta Features -->
    <div class="features-section">
      <div class="section-header">
        <h2>Beta Features</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="featureFilter" @change="filterFeatures">
              <option value="">All Features</option>
              <option value="available">Available</option>
              <option value="testing">Testing</option>
              <option value="coming-soon">Coming Soon</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="categoryFilter" @change="filterFeatures">
              <option value="">All Categories</option>
              <option value="ui">User Interface</option>
              <option value="performance">Performance</option>
              <option value="security">Security</option>
              <option value="automation">Automation</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading beta features...</p>
      </div>

      <div v-else-if="filteredFeatures.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-flask"></i>
        </div>
        <h3>No beta features found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="features-grid">
        <div 
          v-for="feature in filteredFeatures" 
          :key="feature.id"
          class="feature-card"
          :class="{ 'testing': feature.status === 'testing', 'coming-soon': feature.status === 'coming-soon' }"
        >
          <div class="feature-header">
            <div class="feature-icon">
              <i :class="getFeatureIcon(feature.category)"></i>
            </div>
            <div class="feature-meta">
              <span :class="['status-badge', feature.status]">{{ formatFeatureStatus(feature.status) }}</span>
              <span class="feature-category">{{ feature.category }}</span>
            </div>
          </div>
          
          <div class="feature-content">
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
            
            <div class="feature-details">
              <div class="detail-item">
                <label>Version:</label>
                <span>{{ feature.version }}</span>
              </div>
              <div class="detail-item">
                <label>Release:</label>
                <span>{{ formatDate(feature.releaseDate) }}</span>
              </div>
              <div class="detail-item">
                <label>Difficulty:</label>
                <span :class="['difficulty-badge', feature.difficulty]">{{ feature.difficulty }}</span>
              </div>
            </div>
            
            <div class="feature-progress" v-if="feature.status === 'testing'">
              <div class="progress-header">
                <span>Testing Progress</span>
                <span>{{ feature.testingProgress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: feature.testingProgress + '%' }"></div>
              </div>
            </div>
          </div>
          
          <div class="feature-footer">
            <div class="feature-stats">
              <span class="testers">{{ feature.testers }} testers</span>
              <span class="bugs">{{ feature.bugsReported }} bugs</span>
              <span class="rating">{{ feature.rating }}★</span>
            </div>
            <div class="feature-actions">
              <button 
                v-if="feature.status === 'available' && betaStatus.enrolled"
                class="action-btn start" 
                @click="startTesting(feature)"
              >
                <i class="fas fa-play"></i>
                Start Testing
              </button>
              <button 
                v-if="feature.status === 'testing' && userTestingFeature(feature.id)"
                class="action-btn continue" 
                @click="continueTesting(feature)"
              >
                <i class="fas fa-play"></i>
                Continue
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

    <!-- Testing Activity -->
    <div class="activity-section">
      <div class="section-header">
        <h2>Your Testing Activity</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="activityTimeRange" @change="updateActivity">
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
            </select>
          </div>
        </div>
      </div>

      <div class="activity-grid">
        <div class="activity-card">
          <div class="activity-header">
            <h3>Testing Sessions</h3>
            <div class="activity-value">{{ activityStats.sessions }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="sessionsChart"></canvas>
          </div>
        </div>

        <div class="activity-card">
          <div class="activity-header">
            <h3>Bugs Found</h3>
            <div class="activity-value">{{ activityStats.bugsFound }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="bugsChart"></canvas>
          </div>
        </div>

        <div class="activity-card">
          <div class="activity-header">
            <h3>Feedback Given</h3>
            <div class="activity-value">{{ activityStats.feedback }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="feedbackChart"></canvas>
          </div>
        </div>

        <div class="activity-card">
          <div class="activity-header">
            <h3>Impact Score</h3>
            <div class="activity-value">{{ activityStats.impact }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="impactChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="recent-section">
      <div class="section-header">
        <h2>Recent Activity</h2>
        <div class="header-actions">
          <button class="refresh-btn" @click="refreshActivity">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="activity-list">
        <div 
          v-for="activity in recentActivity" 
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-icon">
            <i :class="getActivityIcon(activity.type)"></i>
          </div>
          
          <div class="activity-content">
            <div class="activity-header">
              <h4>{{ activity.title }}</h4>
              <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
            </div>
            <p>{{ activity.description }}</p>
            
            <div class="activity-meta" v-if="activity.feature">
              <span class="feature-name">{{ activity.feature.title }}</span>
              <span class="feature-version">v{{ activity.feature.version }}</span>
            </div>
          </div>
          
          <div class="activity-actions">
            <button class="action-btn view" @click="viewActivity(activity)">
              <i class="fas fa-eye"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Beta Community -->
    <div class="community-section">
      <div class="section-header">
        <h2>Beta Community</h2>
        <div class="header-actions">
          <button class="join-community-btn" @click="joinCommunity">
            <i class="fas fa-users"></i>
            Join Community
          </button>
        </div>
      </div>

      <div class="community-stats">
        <div class="community-stat">
          <div class="stat-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-content">
            <h3>{{ communityStats.totalMembers }}</h3>
            <p>Beta Testers</p>
          </div>
        </div>
        
        <div class="community-stat">
          <div class="stat-icon active">
            <i class="fas fa-user-check"></i>
          </div>
          <div class="stat-content">
            <h3>{{ communityStats.activeToday }}</h3>
            <p>Active Today</p>
          </div>
        </div>
        
        <div class="community-stat">
          <div class="stat-icon discussions">
            <i class="fas fa-comments"></i>
          </div>
          <div class="stat-content">
            <h3>{{ communityStats.discussions }}</h3>
            <p>Discussions</p>
          </div>
        </div>
        
        <div class="community-stat">
          <div class="stat-icon achievements">
            <i class="fas fa-trophy"></i>
          </div>
          <div class="stat-content">
            <h3>{{ communityStats.achievements }}</h3>
            <p>Achievements Unlocked</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Enroll Modal -->
    <div v-if="showEnrollModal" class="modal-overlay" @click="closeEnrollModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Join Beta Program</h2>
          <button class="close-btn" @click="closeEnrollModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="enroll-form">
            <div class="form-intro">
              <h3>Welcome to the Beta Program!</h3>
              <p>Join our exclusive community of testers and help shape the future of our platform. As a beta tester, you'll get early access to new features and directly influence product development.</p>
            </div>

            <div class="form-group">
              <label>Testing Experience *</label>
              <select v-model="enrollForm.experience" required>
                <option value="">Select your experience level</option>
                <option value="beginner">Beginner (0-1 years)</option>
                <option value="intermediate">Intermediate (1-3 years)</option>
                <option value="advanced">Advanced (3-5 years)</option>
                <option value="expert">Expert (5+ years)</option>
              </select>
            </div>

            <div class="form-group">
              <label>Primary Interest *</label>
              <select v-model="enrollForm.interest" required>
                <option value="">Select your primary interest</option>
                <option value="ui">User Interface Testing</option>
                <option value="performance">Performance Testing</option>
                <option value="security">Security Testing</option>
                <option value="automation">Automation Testing</option>
                <option value="usability">Usability Testing</option>
              </select>
            </div>

            <div class="form-group">
              <label>Available Time per Week *</label>
              <select v-model="enrollForm.timeCommitment" required>
                <option value="">Select time commitment</option>
                <option value="1-2">1-2 hours</option>
                <option value="3-5">3-5 hours</option>
                <option value="5-10">5-10 hours</option>
                <option value="10+">10+ hours</option>
              </select>
            </div>

            <div class="form-group">
              <label>Device Types</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="enrollForm.devices" value="desktop" />
                  <span>Desktop</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="enrollForm.devices" value="mobile" />
                  <span>Mobile</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="enrollForm.devices" value="tablet" />
                  <span>Tablet</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Additional Comments</label>
              <textarea 
                v-model="enrollForm.comments" 
                placeholder="Tell us why you want to join the beta program..."
                rows="4"
              ></textarea>
            </div>

            <div class="form-agreement">
              <label class="checkbox-item">
                <input type="checkbox" v-model="enrollForm.agreement" required />
                <span>I agree to the <a href="#" @click.stop>Beta Program Terms and Conditions</a></span>
              </label>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeEnrollModal">Cancel</button>
          <button class="btn-primary" @click="enrollBeta">
            <i class="fas fa-user-plus"></i>
            Join Beta Program
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
const featureFilter = ref('')
const categoryFilter = ref('')
const activityTimeRange = ref('month')
const showEnrollModal = ref(false)

// Chart refs
const sessionsChart = ref(null)
const bugsChart = ref(null)
const feedbackChart = ref(null)
const impactChart = ref(null)

// Beta status
const betaStatus = reactive({
  program: 'Advanced Beta Tester',
  description: 'You have access to all beta features and exclusive content',
  status: 'active',
  enrolled: true,
  joinedDate: '2024-01-15T00:00:00Z'
})

// Beta stats
const betaStats = reactive({
  featuresTested: 23,
  bugsReported: 47,
  contributions: 156,
  reputation: 892
})

// Activity stats
const activityStats = reactive({
  sessions: 45,
  bugsFound: 12,
  feedback: 28,
  impact: 94
})

// Community stats
const communityStats = reactive({
  totalMembers: 1250,
  activeToday: 89,
  discussions: 234,
  achievements: 1567
})

// Enroll form
const enrollForm = reactive({
  experience: '',
  interest: '',
  timeCommitment: '',
  devices: [],
  comments: '',
  agreement: false
})

// Beta features
const betaFeatures = ref([
  {
    id: 1,
    title: 'Advanced Analytics Dashboard',
    description: 'New analytics dashboard with real-time data visualization and custom reports',
    status: 'available',
    category: 'ui',
    version: '2.4.0-beta',
    releaseDate: '2024-01-20T00:00:00Z',
    difficulty: 'medium',
    testingProgress: 65,
    testers: 234,
    bugsReported: 12,
    rating: 4.2
  },
  {
    id: 2,
    title: 'Performance Optimization Engine',
    description: 'AI-powered performance optimization for faster load times and better user experience',
    status: 'testing',
    category: 'performance',
    version: '2.3.1-beta',
    releaseDate: '2024-01-18T00:00:00Z',
    difficulty: 'hard',
    testingProgress: 42,
    testers: 156,
    bugsReported: 8,
    rating: 4.5
  },
  {
    id: 3,
    title: 'Enhanced Security Suite',
    description: 'Advanced security features including 2FA, encryption, and threat detection',
    status: 'coming-soon',
    category: 'security',
    version: '2.5.0-beta',
    releaseDate: '2024-02-01T00:00:00Z',
    difficulty: 'hard',
    testingProgress: 0,
    testers: 0,
    bugsReported: 0,
    rating: 0
  },
  {
    id: 4,
    title: 'Automated Workflow Builder',
    description: 'Visual workflow builder for creating custom automation sequences',
    status: 'available',
    category: 'automation',
    version: '2.4.1-beta',
    releaseDate: '2024-01-22T00:00:00Z',
    difficulty: 'easy',
    testingProgress: 78,
    testers: 189,
    bugsReported: 5,
    rating: 4.7
  }
])

// Recent activity
const recentActivity = ref([
  {
    id: 1,
    type: 'testing',
    title: 'Started testing Advanced Analytics Dashboard',
    description: 'Began testing session for the new analytics dashboard feature',
    timestamp: '2024-01-21T14:30:00Z',
    feature: betaFeatures.value[0]
  },
  {
    id: 2,
    type: 'bug',
    title: 'Reported bug in Performance Optimization',
    description: 'Found a memory leak issue when processing large datasets',
    timestamp: '2024-01-21T10:15:00Z',
    feature: betaFeatures.value[1]
  },
  {
    id: 3,
    type: 'feedback',
    title: 'Submitted feedback for Workflow Builder',
    description: 'Suggested improvements to the drag-and-drop interface',
    timestamp: '2024-01-20T16:45:00Z',
    feature: betaFeatures.value[3]
  },
  {
    id: 4,
    type: 'achievement',
    title: 'Unlocked "Bug Hunter" achievement',
    description: 'Successfully reported 50 bugs in beta features',
    timestamp: '2024-01-20T09:30:00Z',
    feature: null
  }
])

// User testing features
const userTestingFeatures = ref([1, 4]) // Feature IDs user is currently testing

// Computed properties
const filteredFeatures = computed(() => {
  let filtered = betaFeatures.value

  if (featureFilter.value) {
    filtered = filtered.filter(feature => feature.status === featureFilter.value)
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(feature => feature.category === categoryFilter.value)
  }

  return filtered.sort((a, b) => {
    const statusOrder = { 'available': 1, 'testing': 2, 'coming-soon': 3 }
    return statusOrder[a.status] - statusOrder[b.status]
  })
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

const formatTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getEmptyMessage = () => {
  if (featureFilter.value || categoryFilter.value) {
    return 'No features match your filter criteria'
  }
  return 'No beta features available'
}

const getFeatureIcon = (category) => {
  const icons = {
    'ui': 'fas fa-paint-brush',
    'performance': 'fas fa-tachometer-alt',
    'security': 'fas fa-shield-alt',
    'automation': 'fas fa-robot'
  }
  return icons[category] || 'fas fa-cube'
}

const getActivityIcon = (type) => {
  const icons = {
    'testing': 'fas fa-play',
    'bug': 'fas fa-bug',
    'feedback': 'fas fa-comment',
    'achievement': 'fas fa-trophy'
  }
  return icons[type] || 'fas fa-circle'
}

const userTestingFeature = (featureId) => {
  return userTestingFeatures.value.includes(featureId)
}

const filterFeatures = () => {
  // Filtering is handled by computed property
}

const viewAvailableFeatures = () => {
  featureFilter.value = 'available'
  categoryFilter.value = ''
  showSuccess('Showing available beta features')
}

const reportBug = () => {
  showSuccess('Opening bug report form')
}

const submitFeedback = () => {
  showSuccess('Opening feedback form')
}

const startTesting = async (feature) => {
  try {
    // const response = await apiPost(`/beta/features/${feature.id}/start`)
    // if (response.success) {
    //   userTestingFeatures.value.push(feature.id)
    //   showSuccess('Started testing feature successfully')
    // }
    
    // For demo, simulate start
    userTestingFeatures.value.push(feature.id)
    showSuccess('Started testing feature successfully')
  } catch (error) {
    console.error('Error starting testing:', error)
    showError('Failed to start testing')
  }
}

const continueTesting = (feature) => {
  showSuccess(`Continuing testing of ${feature.title}`)
}

const viewFeature = (feature) => {
  showSuccess(`Viewing details for ${feature.title}`)
}

const updateActivity = () => {
  // Update activity based on time range
  initCharts()
  showSuccess('Activity updated')
}

const refreshActivity = async () => {
  try {
    // const response = await apiGet('/beta/activity/refresh')
    // if (response.success) {
    //   recentActivity.value = response.activity || []
    //   showSuccess('Activity refreshed successfully')
    // }
    
    // For demo, simulate refresh
    showSuccess('Activity refreshed successfully')
  } catch (error) {
    console.error('Error refreshing activity:', error)
    showError('Failed to refresh activity')
  }
}

const viewActivity = (activity) => {
  showSuccess(`Viewing activity: ${activity.title}`)
}

const joinCommunity = () => {
  showSuccess('Opening community portal')
}

const enrollBeta = async () => {
  if (!enrollForm.experience || !enrollForm.interest || !enrollForm.timeCommitment || !enrollForm.agreement) {
    showError('Please fill in all required fields and accept the terms')
    return
  }

  try {
    // const response = await apiPost('/beta/enroll', enrollForm)
    // if (response.success) {
    //   betaStatus.enrolled = true
    //   betaStatus.status = 'active'
    //   showSuccess('Successfully enrolled in beta program!')
    //   closeEnrollModal()
    //   resetEnrollForm()
    // }
    
    // For demo, simulate enrollment
    betaStatus.enrolled = true
    betaStatus.status = 'active'
    showSuccess('Successfully enrolled in beta program!')
    closeEnrollModal()
    resetEnrollForm()
  } catch (error) {
    console.error('Error enrolling in beta:', error)
    showError('Failed to enroll in beta program')
  }
}

const closeEnrollModal = () => {
  showEnrollModal.value = false
  resetEnrollForm()
}

const resetEnrollForm = () => {
  Object.assign(enrollForm, {
    experience: '',
    interest: '',
    timeCommitment: '',
    devices: [],
    comments: '',
    agreement: false
  })
}

const initCharts = () => {
  // Initialize Sessions Chart
  if (sessionsChart.value) sessionsChart.value.destroy()
  sessionsChart.value = new Chart(sessionsChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Testing Sessions',
        data: [8, 12, 6, 9, 15, 11, 7],
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

  // Initialize Bugs Chart
  if (bugsChart.value) bugsChart.value.destroy()
  bugsChart.value = new Chart(bugsChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Bugs Found',
        data: [2, 3, 1, 4, 2, 1, 0],
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgb(239, 68, 68)',
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

  // Initialize Feedback Chart
  if (feedbackChart.value) feedbackChart.value.destroy()
  feedbackChart.value = new Chart(feedbackChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Feedback Given',
        data: [5, 8, 3, 6, 9, 4, 2],
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

  // Initialize Impact Chart
  if (impactChart.value) impactChart.value.destroy()
  impactChart.value = new Chart(impactChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['High Impact', 'Medium Impact', 'Low Impact'],
      datasets: [{
        data: [65, 25, 10],
        backgroundColor: [
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(156, 163, 175)'
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
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/beta')
    // if (response.success) {
    //   betaFeatures.value = response.features || []
    //   recentActivity.value = response.activity || []
    //   Object.assign(betaStatus, response.status)
    //   Object.assign(betaStats, response.stats)
    //   Object.assign(activityStats, response.activityStats)
    //   Object.assign(communityStats, response.communityStats)
    // }
    
    // For demo, use mock data
    nextTick(() => {
      initCharts()
    })
  } catch (error) {
    console.error('Error loading beta data:', error)
    showError('Failed to load beta data')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.beta {
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
.activity-section,
.recent-section,
.community-section {
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

.beta-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.beta-icon {
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

.beta-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.beta-details p {
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

.action-icon.bug {
  background: var(--danger-color);
}

.action-icon.feedback {
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

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
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

.feature-card.testing {
  border-left: 4px solid var(--info-color);
}

.feature-card.coming-soon {
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

.status-badge.testing {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.coming-soon {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
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

.difficulty-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.difficulty-badge.easy {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.difficulty-badge.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.difficulty-badge.hard {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.feature-progress {
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

.action-btn.start:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.continue:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
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

.activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.activity-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.activity-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.activity-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.chart-container {
  height: 150px;
  position: relative;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: var(--glass-bg-hover);
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-content h4 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.activity-content p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.activity-time {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.activity-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.feature-name {
  color: var(--primary-color);
  font-weight: 500;
}

.activity-actions {
  display: flex;
  align-items: center;
}

.refresh-btn,
.join-community-btn {
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

.refresh-btn:hover,
.join-community-btn:hover {
  background: var(--primary-hover);
}

.community-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.community-stat {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
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

.stat-icon.active {
  background: var(--success-color);
}

.stat-icon.discussions {
  background: var(--info-color);
}

.stat-icon.achievements {
  background: var(--warning-color);
}

.stat-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
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

.enroll-form {
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

.checkbox-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
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

.form-agreement {
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.form-agreement a {
  color: var(--primary-color);
  text-decoration: none;
}

.form-agreement a:hover {
  text-decoration: underline;
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
  .beta {
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
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-details {
    grid-template-columns: 1fr;
  }
  
  .activity-grid {
    grid-template-columns: 1fr;
  }
  
  .community-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .checkbox-group {
    flex-direction: column;
  }
}
</style>
