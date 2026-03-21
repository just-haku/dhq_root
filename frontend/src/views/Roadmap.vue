<template>
  <div class="roadmap">
    <div class="page-header">
      <h1>Product Roadmap</h1>
      <p>Our vision and upcoming features</p>
    </div>

    <!-- Roadmap Overview -->
    <div class="overview-section">
      <div class="section-header">
        <h2>Roadmap Overview</h2>
        <div class="header-actions">
          <div class="view-toggle">
            <button 
              :class="['view-btn', { active: viewMode === 'timeline' }]"
              @click="viewMode = 'timeline'"
            >
              <i class="fas fa-stream"></i>
              Timeline
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'board' }]"
              @click="viewMode = 'board'"
            >
              <i class="fas fa-th-large"></i>
              Board
            </button>
          </div>
          <div class="filter-dropdown">
            <select v-model="timeFilter" @change="filterRoadmap">
              <option value="">All Time</option>
              <option value="current">Current Quarter</option>
              <option value="next">Next Quarter</option>
              <option value="year">This Year</option>
            </select>
          </div>
        </div>
      </div>

      <div class="overview-stats">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-rocket"></i>
          </div>
          <div class="stat-content">
            <h3>{{ roadmapStats.totalFeatures }}</h3>
            <p>Total Features</p>
            <span class="stat-detail">{{ roadmapStats.completed }} completed</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon progress">
            <i class="fas fa-tasks"></i>
          </div>
          <div class="stat-content">
            <h3>{{ roadmapStats.inProgress }}</h3>
            <p>In Progress</p>
            <span class="stat-detail">{{ roadmapStats.percentage }}% complete</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon upcoming">
            <i class="fas fa-calendar-alt"></i>
          </div>
          <div class="stat-content">
            <h3>{{ roadmapStats.upcoming }}</h3>
            <p>Upcoming</p>
            <span class="stat-detail">Next 3 months</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon released">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <h3>{{ roadmapStats.released }}</h3>
            <p>Released</p>
            <span class="stat-detail">Last 6 months</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Timeline View -->
    <div v-if="viewMode === 'timeline'" class="timeline-section">
      <div class="timeline-container">
        <div 
          v-for="(quarter, index) in filteredQuarters" 
          :key="quarter.id"
          class="timeline-quarter"
        >
          <div class="quarter-header">
            <div class="quarter-info">
              <h3>{{ quarter.name }}</h3>
              <p>{{ quarter.dateRange }}</p>
            </div>
            <div class="quarter-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: quarter.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ quarter.progress }}%</span>
            </div>
          </div>
          
          <div class="quarter-features">
            <div 
              v-for="feature in quarter.features" 
              :key="feature.id"
              class="feature-card"
              :class="{ 'completed': feature.status === 'completed', 'in-progress': feature.status === 'in-progress' }"
            >
              <div class="feature-header">
                <div class="feature-status">
                  <span :class="['status-indicator', feature.status]"></span>
                  <span class="feature-title">{{ feature.title }}</span>
                </div>
                <div class="feature-meta">
                  <span :class="['priority-badge', feature.priority]">{{ feature.priority }}</span>
                  <span class="feature-category">{{ feature.category }}</span>
                </div>
              </div>
              
              <div class="feature-content">
                <p>{{ feature.description }}</p>
                
                <div class="feature-details">
                  <div class="detail-item">
                    <label>Team:</label>
                    <span>{{ feature.team }}</span>
                  </div>
                  <div class="detail-item">
                    <label>Effort:</label>
                    <span>{{ feature.effort }} story points</span>
                  </div>
                  <div class="detail-item">
                    <label>Target:</label>
                    <span>{{ formatDate(feature.targetDate) }}</span>
                  </div>
                </div>
                
                <div class="feature-progress" v-if="feature.status === 'in-progress'">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: feature.progress + '%' }"></div>
                  </div>
                  <span class="progress-text">{{ feature.progress }}% complete</span>
                </div>
              </div>
              
              <div class="feature-footer">
                <div class="feature-team">
                  <div class="team-avatars">
                    <img 
                      v-for="member in feature.teamMembers" 
                      :key="member.id"
                      :src="member.avatar" 
                      :alt="member.name"
                      :title="member.name"
                    />
                  </div>
                </div>
                <div class="feature-actions">
                  <button class="action-btn view" @click="viewFeature(feature)">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="action-btn vote" @click="voteFeature(feature)">
                    <i class="fas fa-thumbs-up"></i>
                    {{ feature.votes }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Board View -->
    <div v-else class="board-section">
      <div class="board-container">
        <div 
          v-for="column in boardColumns" 
          :key="column.id"
          class="board-column"
        >
          <div class="column-header">
            <h3>{{ column.title }}</h3>
            <span class="column-count">{{ column.features.length }}</span>
          </div>
          
          <div class="column-features">
            <div 
              v-for="feature in column.features" 
              :key="feature.id"
              class="board-feature-card"
              @click="viewFeature(feature)"
            >
              <div class="board-feature-header">
                <span :class="['priority-indicator', feature.priority]"></span>
                <h4>{{ feature.title }}</h4>
              </div>
              
              <p>{{ feature.description }}</p>
              
              <div class="board-feature-meta">
                <span class="feature-category">{{ feature.category }}</span>
                <span class="feature-effort">{{ feature.effort }} pts</span>
              </div>
              
              <div class="board-feature-footer">
                <div class="team-avatars">
                  <img 
                    v-for="member in feature.teamMembers.slice(0, 3)" 
                    :key="member.id"
                    :src="member.avatar" 
                    :alt="member.name"
                    :title="member.name"
                  />
                  <span class="more-members" v-if="feature.teamMembers.length > 3">
                    +{{ feature.teamMembers.length - 3 }}
                  </span>
                </div>
                <div class="feature-votes">
                  <i class="fas fa-thumbs-up"></i>
                  {{ feature.votes }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Feature Details -->
    <div class="details-section">
      <div class="section-header">
        <h2>Feature Details</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="categoryFilter" @change="filterFeatures">
              <option value="">All Categories</option>
              <option value="frontend">Frontend</option>
              <option value="backend">Backend</option>
              <option value="infrastructure">Infrastructure</option>
              <option value="security">Security</option>
              <option value="performance">Performance</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="priorityFilter" @change="filterFeatures">
              <option value="">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      <div class="features-grid">
        <div 
          v-for="feature in filteredFeatures" 
          :key="feature.id"
          class="feature-detail-card"
          @click="viewFeature(feature)"
        >
          <div class="feature-detail-header">
            <div class="feature-status-large">
              <span :class="['status-indicator', feature.status]"></span>
              <div class="feature-info">
                <h3>{{ feature.title }}</h3>
                <span :class="['priority-badge', feature.priority]">{{ feature.priority }}</span>
              </div>
            </div>
            <div class="feature-actions">
              <button class="action-btn vote" @click.stop="voteFeature(feature)">
                <i class="fas fa-thumbs-up"></i>
                {{ feature.votes }}
              </button>
            </div>
          </div>
          
          <div class="feature-detail-content">
            <p>{{ feature.description }}</p>
            
            <div class="feature-detail-grid">
              <div class="detail-item">
                <label>Category:</label>
                <span>{{ feature.category }}</span>
              </div>
              <div class="detail-item">
                <label>Team:</label>
                <span>{{ feature.team }}</span>
              </div>
              <div class="detail-item">
                <label>Effort:</label>
                <span>{{ feature.effort }} story points</span>
              </div>
              <div class="detail-item">
                <label>Target:</label>
                <span>{{ formatDate(feature.targetDate) }}</span>
              </div>
            </div>
            
            <div class="feature-detail-progress" v-if="feature.status === 'in-progress'">
              <div class="progress-header">
                <span>Progress</span>
                <span>{{ feature.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: feature.progress + '%' }"></div>
              </div>
            </div>
          </div>
          
          <div class="feature-detail-footer">
            <div class="team-info">
              <div class="team-avatars">
                <img 
                  v-for="member in feature.teamMembers" 
                  :key="member.id"
                  :src="member.avatar" 
                  :alt="member.name"
                  :title="member.name"
                />
              </div>
              <span class="team-size">{{ feature.teamMembers.length }} members</span>
            </div>
            <div class="feature-detail-meta">
              <span class="feature-category">{{ feature.category }}</span>
              <span class="feature-status">{{ formatStatus(feature.status) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Progress Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Progress Analytics</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="analyticsTimeRange" @change="updateAnalytics">
              <option value="quarter">Last Quarter</option>
              <option value="half-year">Last 6 Months</option>
              <option value="year">Last Year</option>
            </select>
          </div>
        </div>
      </div>

      <div class="analytics-grid">
        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Completion Rate</h3>
            <div class="analytics-value">{{ analytics.completionRate }}%</div>
          </div>
          <div class="chart-container">
            <canvas ref="completionChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Feature Distribution</h3>
            <div class="analytics-value">{{ analytics.totalFeatures }} features</div>
          </div>
          <div class="chart-container">
            <canvas ref="distributionChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Team Velocity</h3>
            <div class="analytics-value">{{ analytics.velocity }} pts/sprint</div>
          </div>
          <div class="chart-container">
            <canvas ref="velocityChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Release Timeline</h3>
            <div class="analytics-value">{{ analytics.releases }} releases</div>
          </div>
          <div class="chart-container">
            <canvas ref="releaseChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Feature Modal -->
    <div v-if="showFeatureModal" class="modal-overlay" @click="closeFeatureModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedFeature?.title }}</h2>
          <button class="close-btn" @click="closeFeatureModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="feature-viewer">
            <div class="feature-overview">
              <div class="feature-status-header">
                <span :class="['status-indicator', selectedFeature?.status]"></span>
                <h3>{{ selectedFeature?.title }}</h3>
                <span :class="['priority-badge', selectedFeature?.priority]">{{ selectedFeature?.priority }}</span>
              </div>
              
              <div class="feature-description">
                <p>{{ selectedFeature?.description }}</p>
              </div>
              
              <div class="feature-details-grid">
                <div class="detail-item">
                  <label>Category:</label>
                  <span>{{ selectedFeature?.category }}</span>
                </div>
                <div class="detail-item">
                  <label>Team:</label>
                  <span>{{ selectedFeature?.team }}</span>
                </div>
                <div class="detail-item">
                  <label>Effort:</label>
                  <span>{{ selectedFeature?.effort }} story points</span>
                </div>
                <div class="detail-item">
                  <label>Status:</label>
                  <span>{{ formatStatus(selectedFeature?.status) }}</span>
                </div>
                <div class="detail-item">
                  <label>Target Date:</label>
                  <span>{{ formatDate(selectedFeature?.targetDate) }}</span>
                </div>
                <div class="detail-item">
                  <label>Created:</label>
                  <span>{{ formatDateTime(selectedFeature?.createdAt) }}</span>
                </div>
              </div>
              
              <div class="feature-progress-section" v-if="selectedFeature?.status === 'in-progress'">
                <h4>Progress</h4>
                <div class="progress-bar-large">
                  <div class="progress-fill" :style="{ width: selectedFeature?.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ selectedFeature?.progress }}% complete</span>
              </div>
            </div>
            
            <div class="feature-team-section">
              <h4>Team Members</h4>
              <div class="team-list">
                <div 
                  v-for="member in selectedFeature?.teamMembers" 
                  :key="member.id"
                  class="team-member"
                >
                  <img :src="member.avatar" :alt="member.name" />
                  <div class="member-info">
                    <span class="member-name">{{ member.name }}</span>
                    <span class="member-role">{{ member.role }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div class="footer-actions">
            <button class="action-btn vote" @click="voteFeature(selectedFeature)">
              <i class="fas fa-thumbs-up"></i>
              Vote ({{ selectedFeature?.votes }})
            </button>
            <button class="action-btn share" @click="shareFeature">
              <i class="fas fa-share"></i>
              Share
            </button>
            <button class="action-btn subscribe" @click="subscribeFeature">
              <i class="fas fa-bell"></i>
              Subscribe
            </button>
          </div>
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
const viewMode = ref('timeline')
const timeFilter = ref('')
const categoryFilter = ref('')
const priorityFilter = ref('')
const analyticsTimeRange = ref('quarter')
const showFeatureModal = ref(false)
const selectedFeature = ref(null)

// Chart refs
const completionChart = ref(null)
const distributionChart = ref(null)
const velocityChart = ref(null)
const releaseChart = ref(null)

// Roadmap stats
const roadmapStats = reactive({
  totalFeatures: 45,
  completed: 12,
  inProgress: 8,
  percentage: 27,
  upcoming: 15,
  released: 10
})

// Analytics data
const analytics = reactive({
  completionRate: 87,
  totalFeatures: 45,
  velocity: 23,
  releases: 6
})

// Roadmap data
const quarters = ref([
  {
    id: 1,
    name: 'Q1 2024',
    dateRange: 'Jan - Mar 2024',
    progress: 75,
    features: [
      {
        id: 101,
        title: 'Dark Mode Implementation',
        description: 'Add dark mode support across the entire application',
        status: 'completed',
        priority: 'high',
        category: 'frontend',
        team: 'Frontend Team',
        effort: 8,
        progress: 100,
        targetDate: '2024-03-15T00:00:00Z',
        votes: 45,
        teamMembers: [
          { id: 1, name: 'John Doe', role: 'Lead Developer', avatar: '/api/placeholder/40x40' },
          { id: 2, name: 'Jane Smith', role: 'UI Designer', avatar: '/api/placeholder/40x40' }
        ],
        createdAt: '2024-01-01T00:00:00Z'
      },
      {
        id: 102,
        title: 'API Rate Limiting',
        description: 'Implement rate limiting for all API endpoints',
        status: 'in-progress',
        priority: 'critical',
        category: 'backend',
        team: 'Backend Team',
        effort: 13,
        progress: 60,
        targetDate: '2024-03-31T00:00:00Z',
        votes: 32,
        teamMembers: [
          { id: 3, name: 'Mike Wilson', role: 'Backend Engineer', avatar: '/api/placeholder/40x40' },
          { id: 4, name: 'Sarah Johnson', role: 'DevOps Engineer', avatar: '/api/placeholder/40x40' }
        ],
        createdAt: '2024-01-15T00:00:00Z'
      }
    ]
  },
  {
    id: 2,
    name: 'Q2 2024',
    dateRange: 'Apr - Jun 2024',
    progress: 40,
    features: [
      {
        id: 201,
        title: 'Mobile App Redesign',
        description: 'Complete redesign of the mobile application interface',
        status: 'in-progress',
        priority: 'high',
        category: 'frontend',
        team: 'Mobile Team',
        effort: 21,
        progress: 35,
        targetDate: '2024-06-30T00:00:00Z',
        votes: 67,
        teamMembers: [
          { id: 5, name: 'Emily Davis', role: 'Mobile Developer', avatar: '/api/placeholder/40x40' },
          { id: 6, name: 'Chris Martin', role: 'UX Designer', avatar: '/api/placeholder/40x40' },
          { id: 7, name: 'Alex Turner', role: 'QA Engineer', avatar: '/api/placeholder/40x40' }
        ],
        createdAt: '2024-02-01T00:00:00Z'
      },
      {
        id: 202,
        title: 'Database Optimization',
        description: 'Optimize database queries and improve performance',
        status: 'planned',
        priority: 'medium',
        category: 'backend',
        team: 'Backend Team',
        effort: 16,
        progress: 0,
        targetDate: '2024-05-15T00:00:00Z',
        votes: 28,
        teamMembers: [
          { id: 8, name: 'David Brown', role: 'Database Admin', avatar: '/api/placeholder/40x40' },
          { id: 3, name: 'Mike Wilson', role: 'Backend Engineer', avatar: '/api/placeholder/40x40' }
        ],
        createdAt: '2024-02-15T00:00:00Z'
      }
    ]
  },
  {
    id: 3,
    name: 'Q3 2024',
    dateRange: 'Jul - Sep 2024',
    progress: 15,
    features: [
      {
        id: 301,
        title: 'AI-Powered Analytics',
        description: 'Implement AI-driven analytics and insights',
        status: 'planned',
        priority: 'high',
        category: 'infrastructure',
        team: 'AI Team',
        effort: 34,
        progress: 0,
        targetDate: '2024-09-30T00:00:00Z',
        votes: 89,
        teamMembers: [
          { id: 9, name: 'Dr. Lisa Chen', role: 'AI Engineer', avatar: '/api/placeholder/40x40' },
          { id: 10, name: 'Robert Kim', role: 'Data Scientist', avatar: '/api/placeholder/40x40' },
          { id: 11, name: 'Nina Patel', role: 'ML Engineer', avatar: '/api/placeholder/40x40' }
        ],
        createdAt: '2024-03-01T00:00:00Z'
      }
    ]
  }
])

// Computed properties
const filteredQuarters = computed(() => {
  if (!timeFilter.value) return quarters.value
  
  if (timeFilter.value === 'current') {
    return quarters.value.filter(q => q.id === 1)
  } else if (timeFilter.value === 'next') {
    return quarters.value.filter(q => q.id === 2)
  } else if (timeFilter.value === 'year') {
    return quarters.value
  }
  
  return quarters.value
})

const boardColumns = computed(() => {
  const columns = [
    { id: 'planned', title: 'Planned', features: [] },
    { id: 'in-progress', title: 'In Progress', features: [] },
    { id: 'testing', title: 'Testing', features: [] },
    { id: 'completed', title: 'Completed', features: [] }
  ]
  
  quarters.value.forEach(quarter => {
    quarter.features.forEach(feature => {
      let status = feature.status
      if (status === 'planned') {
        columns[0].features.push(feature)
      } else if (status === 'in-progress') {
        columns[1].features.push(feature)
      } else if (status === 'testing') {
        columns[2].features.push(feature)
      } else if (status === 'completed') {
        columns[3].features.push(feature)
      }
    })
  })
  
  return columns
})

const allFeatures = computed(() => {
  const features = []
  quarters.value.forEach(quarter => {
    features.push(...quarter.features)
  })
  return features
})

const filteredFeatures = computed(() => {
  let filtered = allFeatures.value

  if (categoryFilter.value) {
    filtered = filtered.filter(feature => feature.category === categoryFilter.value)
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(feature => feature.priority === priorityFilter.value)
  }

  return filtered.sort((a, b) => {
    const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
    return priorityOrder[b.priority] - priorityOrder[a.priority]
  })
})

// Methods
const filterRoadmap = () => {
  // Filtering is handled by computed property
}

const filterFeatures = () => {
  // Filtering is handled by computed property
}

const formatStatus = (status) => {
  return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not set'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const viewFeature = (feature) => {
  selectedFeature.value = feature
  showFeatureModal.value = true
}

const closeFeatureModal = () => {
  showFeatureModal.value = false
  selectedFeature.value = null
}

const voteFeature = async (feature) => {
  try {
    // const response = await apiPost(`/roadmap/features/${feature.id}/vote`)
    // if (response.success) {
    //   feature.votes++
    //   showSuccess('Vote submitted successfully')
    // }
    
    // For demo, simulate vote
    feature.votes++
    showSuccess('Vote submitted successfully')
  } catch (error) {
    console.error('Error voting on feature:', error)
    showError('Failed to submit vote')
  }
}

const shareFeature = async () => {
  try {
    // const response = await apiPost(`/roadmap/features/${selectedFeature.value.id}/share`)
    // if (response.success) {
    //   navigator.clipboard.writeText(response.shareUrl)
    //   showSuccess('Feature shared! URL copied to clipboard')
    // }
    
    // For demo, simulate share
    const shareUrl = `https://roadmap.example.com/feature/${selectedFeature.value.id}`
    navigator.clipboard.writeText(shareUrl)
    showSuccess('Feature shared! URL copied to clipboard')
  } catch (error) {
    console.error('Error sharing feature:', error)
    showError('Failed to share feature')
  }
}

const subscribeFeature = async () => {
  try {
    // const response = await apiPost(`/roadmap/features/${selectedFeature.value.id}/subscribe`)
    // if (response.success) {
    //   showSuccess('Subscribed to feature updates')
    // }
    
    // For demo, simulate subscribe
    showSuccess('Subscribed to feature updates')
  } catch (error) {
    console.error('Error subscribing to feature:', error)
    showError('Failed to subscribe to feature')
  }
}

const updateAnalytics = () => {
  // Update analytics based on time range
  initCharts()
  showSuccess('Analytics updated')
}

const initCharts = () => {
  // Initialize Completion Chart
  if (completionChart.value) completionChart.value.destroy()
  completionChart.value = new Chart(completionChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Completion Rate %',
        data: [65, 72, 78, 82, 85, 87],
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
        y: { 
          beginAtZero: false,
          min: 50,
          max: 100
        }
      }
    }
  })

  // Initialize Distribution Chart
  if (distributionChart.value) distributionChart.value.destroy()
  distributionChart.value = new Chart(distributionChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Frontend', 'Backend', 'Infrastructure', 'Security', 'Performance'],
      datasets: [{
        data: [15, 12, 8, 5, 5],
        backgroundColor: [
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)',
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

  // Initialize Velocity Chart
  if (velocityChart.value) velocityChart.value.destroy()
  velocityChart.value = new Chart(velocityChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4', 'Sprint 5', 'Sprint 6'],
      datasets: [{
        label: 'Story Points',
        data: [18, 22, 25, 20, 23, 23],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgb(59, 130, 246)',
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

  // Initialize Release Chart
  if (releaseChart.value) releaseChart.value.destroy()
  releaseChart.value = new Chart(releaseChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Releases',
        data: [1, 0, 2, 1, 1, 1],
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
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
        y: { 
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  })
}

// Lifecycle
onMounted(async () => {
  try {
    // const response = await apiGet('/roadmap')
    // if (response.success) {
    //   quarters.value = response.quarters || []
    //   Object.assign(roadmapStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
    nextTick(() => {
      initCharts()
    })
  } catch (error) {
    console.error('Error loading roadmap data:', error)
    showError('Failed to load roadmap data')
  }
})
</script>

<style scoped>
.roadmap {
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
.timeline-section,
.board-section,
.details-section,
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

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.view-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
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

.stat-icon.progress {
  background: var(--info-color);
}

.stat-icon.upcoming {
  background: var(--warning-color);
}

.stat-icon.released {
  background: var(--success-color);
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

.stat-detail {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.timeline-quarter {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
}

.quarter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: var(--glass-bg-tertiary);
  border-bottom: 1px solid var(--glass-border);
}

.quarter-info h3 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.quarter-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.quarter-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  width: 120px;
  height: 8px;
  background: var(--glass-bg-hover);
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
  font-weight: 600;
}

.quarter-features {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature-card {
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.feature-card.completed {
  border-left: 4px solid var(--success-color);
}

.feature-card.in-progress {
  border-left: 4px solid var(--info-color);
}

.feature-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.feature-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.completed {
  background: var(--success-color);
}

.status-indicator.in-progress {
  background: var(--info-color);
}

.status-indicator.planned {
  background: var(--warning-color);
}

.status-indicator.testing {
  background: var(--primary-color);
}

.feature-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.feature-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.priority-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.priority-badge.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.priority-badge.high {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.priority-badge.medium {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.priority-badge.low {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.feature-category {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
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

.feature-progress {
  margin-top: 1rem;
}

.feature-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  margin-top: 1rem;
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
  margin-right: -0.5rem;
}

.team-avatars img:first-child {
  margin-left: 0;
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

.action-btn.vote:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.view:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.board-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.board-column {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-bottom: 1px solid var(--glass-border);
}

.column-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1rem;
}

.column-count {
  padding: 0.25rem 0.75rem;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.column-features {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 400px;
}

.board-feature-card {
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.board-feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.board-feature-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.priority-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.priority-indicator.critical {
  background: var(--danger-color);
}

.priority-indicator.high {
  background: var(--warning-color);
}

.priority-indicator.medium {
  background: var(--info-color);
}

.priority-indicator.low {
  background: var(--success-color);
}

.board-feature-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.board-feature-card p {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.4;
}

.board-feature-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.feature-effort {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.board-feature-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.feature-votes {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.feature-detail-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-detail-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.feature-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.feature-status-large {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.feature-info h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.feature-detail-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.feature-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.feature-detail-progress {
  margin-top: 1rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-bar-large {
  width: 100%;
  height: 10px;
  background: var(--glass-bg-tertiary);
  border-radius: 5px;
  overflow: hidden;
}

.feature-detail-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  margin-top: 1rem;
}

.team-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.team-size {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.feature-detail-meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.feature-status {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  color: var(--text-secondary);
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

.feature-viewer {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.feature-overview {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.feature-status-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.feature-status-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.feature-description p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.feature-details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.feature-progress-section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.progress-bar-large {
  width: 100%;
  height: 12px;
  background: var(--glass-bg-tertiary);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.feature-team-section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.team-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.team-member img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.member-name {
  font-weight: 600;
  color: var(--text-primary);
}

.member-role {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

.footer-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn.share:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.subscribe:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

@media (max-width: 768px) {
  .roadmap {
    padding: 1rem;
  }
  
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .board-container {
    grid-template-columns: 1fr;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-details {
    grid-template-columns: 1fr;
  }
  
  .feature-detail-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-detail-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-content.large {
    max-width: 95%;
  }
  
  .feature-viewer {
    grid-template-columns: 1fr;
  }
  
  .feature-details-grid {
    grid-template-columns: 1fr;
  }
}
</style>
