<template>
  <div class="feedback">
    <div class="page-header">
      <h1>Feedback Center</h1>
      <p>Share your thoughts and help us improve</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions-section">
      <div class="section-header">
        <h2>Quick Actions</h2>
      </div>
      
      <div class="quick-actions-grid">
        <div class="action-card" @click="showFeedbackModal = true">
          <div class="action-icon">
            <i class="fas fa-comment-dots"></i>
          </div>
          <h3>Submit Feedback</h3>
          <p>Share your thoughts and suggestions</p>
        </div>
        
        <div class="action-card" @click="showBugModal = true">
          <div class="action-icon bug">
            <i class="fas fa-bug"></i>
          </div>
          <h3>Report Bug</h3>
          <p>Report issues and problems</p>
        </div>
        
        <div class="action-card" @click="showFeatureModal = true">
          <div class="action-icon feature">
            <i class="fas fa-lightbulb"></i>
          </div>
          <h3>Request Feature</h3>
          <p>Suggest new features and improvements</p>
        </div>
        
        <div class="action-card" @click="viewMyFeedback">
          <div class="action-icon my-feedback">
            <i class="fas fa-history"></i>
          </div>
          <h3>My Feedback</h3>
          <p>View your submitted feedback</p>
        </div>
      </div>
    </div>

    <!-- Feedback Stats -->
    <div class="stats-section">
      <div class="section-header">
        <h2>Feedback Overview</h2>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-comment-dots"></i>
          </div>
          <div class="stat-content">
            <h3>{{ feedbackStats.totalFeedback }}</h3>
            <p>Total Feedback</p>
            <span class="stat-change" :class="getChangeClass(feedbackStats.feedbackChange)">
              {{ formatChange(feedbackStats.feedbackChange) }}
            </span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon bugs">
            <i class="fas fa-bug"></i>
          </div>
          <div class="stat-content">
            <h3>{{ feedbackStats.bugsReported }}</h3>
            <p>Bugs Reported</p>
            <span class="stat-change" :class="getChangeClass(feedbackStats.bugsChange)">
              {{ formatChange(feedbackStats.bugsChange) }}
            </span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon features">
            <i class="fas fa-lightbulb"></i>
          </div>
          <div class="stat-content">
            <h3>{{ feedbackStats.featuresRequested }}</h3>
            <p>Features Requested</p>
            <span class="stat-change" :class="getChangeClass(feedbackStats.featuresChange)">
              {{ formatChange(feedbackStats.featuresChange) }}
            </span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon satisfaction">
            <i class="fas fa-smile"></i>
          </div>
          <div class="stat-content">
            <h3>{{ feedbackStats.satisfaction }}%</h3>
            <p>User Satisfaction</p>
            <span class="stat-change" :class="getChangeClass(feedbackStats.satisfactionChange)">
              {{ formatChange(feedbackStats.satisfactionChange) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Feedback -->
    <div class="recent-section">
      <div class="section-header">
        <h2>Recent Feedback</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="feedbackFilter" @change="filterFeedback">
              <option value="">All Types</option>
              <option value="general">General Feedback</option>
              <option value="bug">Bug Report</option>
              <option value="feature">Feature Request</option>
              <option value="improvement">Improvement</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterFeedback">
              <option value="">All Status</option>
              <option value="new">New</option>
              <option value="reviewing">Reviewing</option>
              <option value="planned">Planned</option>
              <option value="in-progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading feedback...</p>
      </div>

      <div v-else-if="filteredFeedback.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-comment-dots"></i>
        </div>
        <h3>No feedback found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showFeedbackModal = true">
          <i class="fas fa-plus"></i>
          Submit Your First Feedback
        </button>
      </div>

      <div v-else class="feedback-list">
        <div 
          v-for="item in filteredFeedback" 
          :key="item.id"
          class="feedback-card"
          :class="{ 'high-priority': item.priority === 'high' }"
        >
          <div class="feedback-header">
            <div class="feedback-info">
              <div class="feedback-type">
                <span :class="['type-badge', item.type]">{{ formatType(item.type) }}</span>
              </div>
              <div class="feedback-title">{{ item.title }}</div>
            </div>
            <div class="feedback-meta">
              <span :class="['status-badge', item.status]">{{ formatStatus(item.status) }}</span>
              <span :class="['priority-badge', item.priority]">{{ item.priority }}</span>
            </div>
          </div>
          
          <div class="feedback-content">
            <p>{{ item.description }}</p>
            
            <div class="feedback-details">
              <div class="detail-item">
                <label>Category:</label>
                <span>{{ item.category }}</span>
              </div>
              <div class="detail-item">
                <label>Submitted:</label>
                <span>{{ formatDateTime(item.createdAt) }}</span>
              </div>
              <div class="detail-item">
                <label>Updated:</label>
                <span>{{ formatDateTime(item.updatedAt) }}</span>
              </div>
            </div>
            
            <div class="feedback-author">
              <img :src="item.author.avatar" :alt="item.author.name" />
              <div class="author-info">
                <span class="author-name">{{ item.author.name }}</span>
                <span class="author-role">{{ item.author.role }}</span>
              </div>
            </div>
          </div>
          
          <div class="feedback-footer">
            <div class="feedback-stats">
              <span class="votes">{{ item.votes }} votes</span>
              <span class="comments">{{ item.comments.length }} comments</span>
              <span class="views">{{ item.views }} views</span>
            </div>
            <div class="feedback-actions">
              <button class="action-btn vote" @click="voteFeedback(item)">
                <i class="fas fa-thumbs-up"></i>
                Vote
              </button>
              <button class="action-btn comment" @click="commentFeedback(item)">
                <i class="fas fa-comment"></i>
                Comment
              </button>
              <button class="action-btn view" @click="viewFeedback(item)">
                <i class="fas fa-eye"></i>
                View
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Voted Feedback -->
    <div class="top-voted-section">
      <div class="section-header">
        <h2>Top Voted Feedback</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="timeRange" @change="updateTopVoted">
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
              <option value="all">All Time</option>
            </select>
          </div>
        </div>
      </div>

      <div class="top-voted-list">
        <div 
          v-for="(item, index) in topVotedFeedback" 
          :key="item.id"
          class="top-voted-item"
          @click="viewFeedback(item)"
        >
          <div class="rank">
            <span class="rank-number">{{ index + 1 }}</span>
          </div>
          
          <div class="item-content">
            <div class="item-header">
              <h4>{{ item.title }}</h4>
              <span :class="['type-badge', item.type]">{{ formatType(item.type) }}</span>
            </div>
            
            <p>{{ item.description }}</p>
            
            <div class="item-meta">
              <span class="votes">{{ item.votes }} votes</span>
              <span class="status" :class="item.status">{{ formatStatus(item.status) }}</span>
              <span class="date">{{ formatDate(item.createdAt) }}</span>
            </div>
          </div>
          
          <div class="vote-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: getVotePercentage(item.votes) + '%' }"></div>
            </div>
            <span class="vote-count">{{ item.votes }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Feedback Trends -->
    <div class="trends-section">
      <div class="section-header">
        <h2>Feedback Trends</h2>
        <div class="header-actions">
          <div class="chart-type">
            <select v-model="chartType" @change="updateCharts">
              <option value="volume">Volume</option>
              <option value="categories">Categories</option>
              <option value="satisfaction">Satisfaction</option>
            </select>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <h3>Feedback Volume</h3>
            <div class="chart-info">
              <span class="trend positive">+12%</span>
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="volumeChart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h3>Feedback Categories</h3>
            <div class="chart-info">
              <span class="trend neutral">0%</span>
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="categoriesChart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h3>User Satisfaction</h3>
            <div class="chart-info">
              <span class="trend positive">+5%</span>
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="satisfactionChart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h3>Response Time</h3>
            <div class="chart-info">
              <span class="trend positive">-8%</span>
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="responseChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Feedback Modal -->
    <div v-if="showFeedbackModal" class="modal-overlay" @click="closeFeedbackModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Submit Feedback</h2>
          <button class="close-btn" @click="closeFeedbackModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="feedback-form">
            <div class="form-group">
              <label>Feedback Type *</label>
              <select v-model="feedbackForm.type" required>
                <option value="">Select type</option>
                <option value="general">General Feedback</option>
                <option value="bug">Bug Report</option>
                <option value="feature">Feature Request</option>
                <option value="improvement">Improvement</option>
              </select>
            </div>

            <div class="form-group">
              <label>Title *</label>
              <input 
                v-model="feedbackForm.title" 
                type="text" 
                placeholder="Brief summary of your feedback"
                required
              />
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Category *</label>
                <select v-model="feedbackForm.category" required>
                  <option value="">Select category</option>
                  <option value="ui">User Interface</option>
                  <option value="ux">User Experience</option>
                  <option value="performance">Performance</option>
                  <option value="security">Security</option>
                  <option value="documentation">Documentation</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div class="form-group">
                <label>Priority</label>
                <select v-model="feedbackForm.priority">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Description *</label>
              <textarea 
                v-model="feedbackForm.description" 
                placeholder="Detailed description of your feedback"
                rows="5"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label>Steps to Reproduce (for bug reports)</label>
              <textarea 
                v-model="feedbackForm.steps" 
                placeholder="1. Go to...\n2. Click on...\n3. See error..."
                rows="4"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Expected vs Actual Behavior</label>
              <div class="behavior-grid">
                <div class="behavior-item">
                  <label>Expected:</label>
                  <textarea 
                    v-model="feedbackForm.expected" 
                    placeholder="What you expected to happen"
                    rows="3"
                  ></textarea>
                </div>
                <div class="behavior-item">
                  <label>Actual:</label>
                  <textarea 
                    v-model="feedbackForm.actual" 
                    placeholder="What actually happened"
                    rows="3"
                  ></textarea>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Attachments</label>
              <div class="file-upload">
                <input 
                  type="file" 
                  ref="fileInput"
                  multiple
                  @change="handleFileUpload"
                  accept="image/*,.pdf,.doc,.docx,.txt"
                />
                <button class="upload-btn" @click="$refs.fileInput.click()">
                  <i class="fas fa-paperclip"></i>
                  Attach Files
                </button>
                <div class="attached-files" v-if="feedbackForm.attachments.length > 0">
                  <div 
                    v-for="(file, index) in feedbackForm.attachments" 
                    :key="index"
                    class="attached-file"
                  >
                    <span class="file-name">{{ file.name }}</span>
                    <button class="remove-file" @click="removeFile(index)">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeFeedbackModal">Cancel</button>
          <button class="btn-primary" @click="submitFeedback">
            <i class="fas fa-paper-plane"></i>
            Submit Feedback
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
const feedbackFilter = ref('')
const statusFilter = ref('')
const timeRange = ref('month')
const chartType = ref('volume')
const showFeedbackModal = ref(false)
const showBugModal = ref(false)
const showFeatureModal = ref(false)

// Chart refs
const volumeChart = ref(null)
const categoriesChart = ref(null)
const satisfactionChart = ref(null)
const responseChart = ref(null)

// Feedback stats
const feedbackStats = reactive({
  totalFeedback: 156,
  feedbackChange: 12,
  bugsReported: 23,
  bugsChange: -5,
  featuresRequested: 45,
  featuresChange: 18,
  satisfaction: 87,
  satisfactionChange: 5
})

// Feedback form
const feedbackForm = reactive({
  type: '',
  title: '',
  category: '',
  priority: 'medium',
  description: '',
  steps: '',
  expected: '',
  actual: '',
  attachments: []
})

// Feedback data
const feedback = ref([
  {
    id: 1001,
    title: 'Dark mode toggle not working on mobile',
    description: 'The dark mode toggle button is not responding on mobile devices',
    type: 'bug',
    status: 'in-progress',
    priority: 'high',
    category: 'ui',
    createdAt: '2024-01-21T10:30:00Z',
    updatedAt: '2024-01-21T14:45:00Z',
    votes: 23,
    views: 156,
    comments: [
      {
        id: 1,
        author: 'Support Team',
        text: 'We are investigating this issue.',
        timestamp: '2024-01-21T11:00:00Z'
      }
    ],
    author: {
      name: 'John Doe',
      role: 'Developer',
      avatar: '/api/placeholder/40x40'
    }
  },
  {
    id: 1002,
    title: 'Add keyboard shortcuts for common actions',
    description: 'Would be great to have keyboard shortcuts for frequently used actions',
    type: 'feature',
    status: 'planned',
    priority: 'medium',
    category: 'ux',
    createdAt: '2024-01-20T09:15:00Z',
    updatedAt: '2024-01-21T10:30:00Z',
    votes: 45,
    views: 289,
    comments: [
      {
        id: 1,
        author: 'Product Team',
        text: 'Great suggestion! We\'ll consider this for our next sprint.',
        timestamp: '2024-01-20T10:00:00Z'
      }
    ],
    author: {
      name: 'Jane Smith',
      role: 'Designer',
      avatar: '/api/placeholder/40x40'
    }
  },
  {
    id: 1003,
    title: 'Dashboard loading time is slow',
    description: 'The main dashboard takes too long to load, especially with large datasets',
    type: 'improvement',
    status: 'new',
    priority: 'medium',
    category: 'performance',
    createdAt: '2024-01-19T16:45:00Z',
    updatedAt: '2024-01-19T16:45:00Z',
    votes: 18,
    views: 98,
    comments: [],
    author: {
      name: 'Mike Wilson',
      role: 'Product Manager',
      avatar: '/api/placeholder/40x40'
    }
  }
])

// Top voted feedback
const topVotedFeedback = computed(() => {
  return feedback.value
    .filter(item => item.votes > 0)
    .sort((a, b) => b.votes - a.votes)
    .slice(0, 10)
})

// Computed properties
const filteredFeedback = computed(() => {
  let filtered = feedback.value

  if (feedbackFilter.value) {
    filtered = filtered.filter(item => item.type === feedbackFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(item => item.status === statusFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
})

// Methods
const filterFeedback = () => {
  // Filtering is handled by computed property
}

const getEmptyMessage = () => {
  if (feedbackFilter.value || statusFilter.value) {
    return 'No feedback matches your filter criteria'
  }
  return 'No feedback found'
}

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

const formatType = (type) => {
  return type.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatStatus = (status) => {
  return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const voteFeedback = async (item) => {
  try {
    // const response = await apiPost(`/feedback/${item.id}/vote`)
    // if (response.success) {
    //   item.votes++
    //   showSuccess('Vote submitted successfully')
    // }
    
    // For demo, simulate vote
    item.votes++
    showSuccess('Vote submitted successfully')
  } catch (error) {
    console.error('Error voting on feedback:', error)
    showError('Failed to submit vote')
  }
}

const commentFeedback = (item) => {
  showSuccess(`Opening comments for feedback #${item.id}`)
}

const viewFeedback = (item) => {
  showSuccess(`Viewing feedback: ${item.title}`)
}

const viewMyFeedback = () => {
  showSuccess('Viewing your submitted feedback')
}

const getVotePercentage = (votes) => {
  const maxVotes = Math.max(...feedback.value.map(item => item.votes))
  return maxVotes > 0 ? (votes / maxVotes) * 100 : 0
}

const updateTopVoted = () => {
  // Update top voted feedback based on time range
  showSuccess('Updated top voted feedback')
}

const updateCharts = () => {
  // Update charts based on chart type
  initCharts()
}

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  feedbackForm.attachments.push(...files)
}

const removeFile = (index) => {
  feedbackForm.attachments.splice(index, 1)
}

const submitFeedback = async () => {
  if (!feedbackForm.type || !feedbackForm.title || !feedbackForm.category || !feedbackForm.description) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/feedback', feedbackForm)
    // if (response.success) {
    //   feedback.value.unshift(response.feedback)
    //   showSuccess('Feedback submitted successfully')
    //   closeFeedbackModal()
    //   resetFeedbackForm()
    // }
    
    // For demo, simulate submission
    const newFeedback = {
      id: Date.now(),
      title: feedbackForm.title,
      description: feedbackForm.description,
      type: feedbackForm.type,
      status: 'new',
      priority: feedbackForm.priority,
      category: feedbackForm.category,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      votes: 0,
      views: 0,
      comments: [],
      author: {
        name: 'Current User',
        role: 'User',
        avatar: '/api/placeholder/40x40'
      }
    }
    
    feedback.value.unshift(newFeedback)
    showSuccess('Feedback submitted successfully')
    closeFeedbackModal()
    resetFeedbackForm()
  } catch (error) {
    console.error('Error submitting feedback:', error)
    showError('Failed to submit feedback')
  }
}

const closeFeedbackModal = () => {
  showFeedbackModal.value = false
  resetFeedbackForm()
}

const resetFeedbackForm = () => {
  Object.assign(feedbackForm, {
    type: '',
    title: '',
    category: '',
    priority: 'medium',
    description: '',
    steps: '',
    expected: '',
    actual: '',
    attachments: []
  })
}

const initCharts = () => {
  // Initialize Volume Chart
  if (volumeChart.value) volumeChart.value.destroy()
  volumeChart.value = new Chart(volumeChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Feedback Volume',
        data: [12, 19, 15, 25, 22, 30, 28],
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

  // Initialize Categories Chart
  if (categoriesChart.value) categoriesChart.value.destroy()
  categoriesChart.value = new Chart(categoriesChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['UI', 'UX', 'Performance', 'Security', 'Other'],
      datasets: [{
        data: [30, 25, 20, 15, 10],
        backgroundColor: [
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)',
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

  // Initialize Satisfaction Chart
  if (satisfactionChart.value) satisfactionChart.value.destroy()
  satisfactionChart.value = new Chart(satisfactionChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Satisfaction %',
        data: [82, 84, 83, 85, 87, 87],
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
          min: 70,
          max: 100
        }
      }
    }
  })

  // Initialize Response Time Chart
  if (responseChart.value) responseChart.value.destroy()
  responseChart.value = new Chart(responseChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
      datasets: [{
        label: 'Response Time (hours)',
        data: [2.5, 2.1, 2.8, 2.3, 2.0],
        backgroundColor: 'rgba(245, 158, 11, 0.8)',
        borderColor: 'rgb(245, 158, 11)',
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
    // const response = await apiGet('/feedback')
    // if (response.success) {
    //   feedback.value = response.feedback || []
    //   Object.assign(feedbackStats, response.stats)
    // }
    
    // For demo, use mock data
    nextTick(() => {
      initCharts()
    })
  } catch (error) {
    console.error('Error loading feedback data:', error)
    showError('Failed to load feedback data')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.feedback {
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

.quick-actions-section,
.stats-section,
.recent-section,
.top-voted-section,
.trends-section {
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

.quick-actions-grid {
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

.action-icon.bug {
  background: var(--danger-color);
}

.action-icon.feature {
  background: var(--warning-color);
}

.action-icon.my-feedback {
  background: var(--info-color);
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

.stats-grid {
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

.stat-icon.bugs {
  background: var(--danger-color);
}

.stat-icon.features {
  background: var(--warning-color);
}

.stat-icon.satisfaction {
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

.filter-dropdown,
.time-range,
.chart-type {
  position: relative;
}

.filter-dropdown select,
.time-range select,
.chart-type select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
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

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feedback-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feedback-card:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
}

.feedback-card.high-priority {
  border-left: 4px solid var(--danger-color);
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.feedback-info {
  flex: 1;
}

.type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
  margin-bottom: 0.5rem;
  display: inline-block;
}

.type-badge.general {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.type-badge.bug {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.type-badge.feature {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.type-badge.improvement {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.feedback-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.feedback-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.status-badge,
.priority-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.new {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.reviewing {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.planned {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.status-badge.in-progress {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.completed {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.priority-badge.low {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.priority-badge.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.priority-badge.high {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.feedback-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.feedback-details {
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

.feedback-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.feedback-author img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.author-name {
  font-weight: 600;
  color: var(--text-primary);
}

.author-role {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.feedback-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

.feedback-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.feedback-actions {
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

.action-btn.comment:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.view:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.top-voted-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.top-voted-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.top-voted-item:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
}

.rank {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
}

.rank-number {
  width: 32px;
  height: 32px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.item-content {
  flex: 1;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.item-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.item-content p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.item-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.item-meta .status {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-weight: 500;
}

.vote-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 60px;
}

.progress-bar {
  width: 8px;
  height: 60px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  width: 100%;
  background: var(--primary-color);
  transition: height 0.3s ease;
}

.vote-count {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.chart-info .trend {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.trend.positive {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.trend.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.trend.neutral {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
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

.feedback-form {
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

.behavior-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.behavior-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.behavior-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.file-upload {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.upload-btn {
  padding: 0.75rem 1rem;
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

.attached-files {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.attached-file {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
}

.file-name {
  font-size: 0.9rem;
  color: var(--text-primary);
}

.remove-file {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.remove-file:hover {
  background: rgba(239, 68, 68, 0.1);
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
  .feedback {
    padding: 1rem;
  }
  
  .quick-actions-grid,
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .feedback-details {
    grid-template-columns: 1fr;
  }
  
  .feedback-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .top-voted-item {
    flex-direction: column;
    text-align: center;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .form-grid,
  .behavior-grid {
    grid-template-columns: 1fr;
  }
}
</style>
