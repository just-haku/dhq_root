<template>
  <div class="support">
    <div class="page-header">
      <h1>Support Center</h1>
      <p>Get help and support for all your needs</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions-section">
      <div class="section-header">
        <h2>Quick Actions</h2>
      </div>
      
      <div class="quick-actions-grid">
        <div class="action-card" @click="showTicketModal = true">
          <div class="action-icon">
            <i class="fas fa-ticket-alt"></i>
          </div>
          <h3>Create Ticket</h3>
          <p>Submit a support request</p>
        </div>
        
        <div class="action-card" @click="startLiveChat">
          <div class="action-icon chat">
            <i class="fas fa-comments"></i>
          </div>
          <h3>Live Chat</h3>
          <p>Chat with support team</p>
        </div>
        
        <div class="action-card" @click="scheduleCall">
          <div class="action-icon call">
            <i class="fas fa-phone"></i>
          </div>
          <h3>Schedule Call</h3>
          <p>Book a support call</p>
        </div>
        
        <div class="action-card" @click="viewFAQ">
          <div class="action-icon faq">
            <i class="fas fa-question-circle"></i>
          </div>
          <h3>FAQ</h3>
          <p>Browse common questions</p>
        </div>
      </div>
    </div>

    <!-- Support Stats -->
    <div class="stats-section">
      <div class="section-header">
        <h2>Support Overview</h2>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-ticket-alt"></i>
          </div>
          <div class="stat-content">
            <h3>{{ supportStats.openTickets }}</h3>
            <p>Open Tickets</p>
            <span class="stat-change" :class="getChangeClass(supportStats.ticketChange)">
              {{ formatChange(supportStats.ticketChange) }}
            </span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon response">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <h3>{{ supportStats.avgResponseTime }}h</h3>
            <p>Avg Response Time</p>
            <span class="stat-change" :class="getChangeClass(supportStats.responseChange)">
              {{ formatChange(supportStats.responseChange) }}
            </span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon resolved">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <h3>{{ supportStats.resolvedToday }}</h3>
            <p>Resolved Today</p>
            <span class="stat-change positive">
              +{{ supportStats.resolvedToday }}
            </span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon satisfaction">
            <i class="fas fa-smile"></i>
          </div>
          <div class="stat-content">
            <h3>{{ supportStats.satisfaction }}%</h3>
            <p>Customer Satisfaction</p>
            <span class="stat-change" :class="getChangeClass(supportStats.satisfactionChange)">
              {{ formatChange(supportStats.satisfactionChange) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- My Tickets -->
    <div class="tickets-section">
      <div class="section-header">
        <h2>My Support Tickets</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="ticketFilter" @change="filterTickets">
              <option value="">All Status</option>
              <option value="open">Open</option>
              <option value="in-progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="priorityFilter" @change="filterTickets">
              <option value="">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
          <button class="create-ticket-btn" @click="showTicketModal = true">
            <i class="fas fa-plus"></i>
            New Ticket
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading tickets...</p>
      </div>

      <div v-else-if="filteredTickets.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-ticket-alt"></i>
        </div>
        <h3>No tickets found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showTicketModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Ticket
        </button>
      </div>

      <div v-else class="tickets-list">
        <div 
          v-for="ticket in filteredTickets" 
          :key="ticket.id"
          class="ticket-card"
          :class="{ 'urgent': ticket.priority === 'urgent' }"
          @click="openTicket(ticket)"
        >
          <div class="ticket-header">
            <div class="ticket-info">
              <div class="ticket-id">#{{ ticket.id }}</div>
              <div class="ticket-title">{{ ticket.title }}</div>
            </div>
            <div class="ticket-meta">
              <span :class="['status-badge', ticket.status]">{{ formatStatus(ticket.status) }}</span>
              <span :class="['priority-badge', ticket.priority]">{{ ticket.priority }}</span>
            </div>
          </div>
          
          <div class="ticket-content">
            <p>{{ ticket.description }}</p>
            
            <div class="ticket-details">
              <div class="detail-item">
                <label>Category:</label>
                <span>{{ ticket.category }}</span>
              </div>
              <div class="detail-item">
                <label>Created:</label>
                <span>{{ formatDateTime(ticket.createdAt) }}</span>
              </div>
              <div class="detail-item">
                <label>Last Updated:</label>
                <span>{{ formatDateTime(ticket.updatedAt) }}</span>
              </div>
            </div>
            
            <div class="ticket-assignee" v-if="ticket.assignee">
              <img :src="ticket.assignee.avatar" :alt="ticket.assignee.name" />
              <div class="assignee-info">
                <span class="assignee-name">{{ ticket.assignee.name }}</span>
                <span class="assignee-role">{{ ticket.assignee.role }}</span>
              </div>
            </div>
          </div>
          
          <div class="ticket-footer">
            <div class="ticket-stats">
              <span class="replies">{{ ticket.replies.length }} replies</span>
              <span class="views">{{ ticket.views }} views</span>
            </div>
            <div class="ticket-actions">
              <button class="action-btn view" @click.stop="openTicket(ticket)">
                <i class="fas fa-eye"></i>
                View
              </button>
              <button class="action-btn reply" @click.stop="replyToTicket(ticket)">
                <i class="fas fa-reply"></i>
                Reply
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Knowledge Base -->
    <div class="knowledge-section">
      <div class="section-header">
        <h2>Knowledge Base</h2>
        <div class="header-actions">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input 
              v-model="kbSearchQuery" 
              type="text" 
              placeholder="Search knowledge base..."
              @input="searchKB"
            />
          </div>
        </div>
      </div>

      <div class="kb-categories">
        <div 
          v-for="category in kbCategories" 
          :key="category.id"
          class="kb-category"
          @click="expandCategory(category.id)"
        >
          <div class="category-header">
            <div class="category-icon">
              <i :class="category.icon"></i>
            </div>
            <h3>{{ category.name }}</h3>
            <div class="category-toggle">
              <i :class="['fas', expandedCategories.includes(category.id) ? 'fa-chevron-up' : 'fa-chevron-down']"></i>
            </div>
          </div>
          
          <div v-if="expandedCategories.includes(category.id)" class="category-content">
            <p>{{ category.description }}</p>
            <div class="category-articles">
              <div 
                v-for="article in category.articles" 
                :key="article.id"
                class="article-item"
                @click.stop="openArticle(article)"
              >
                <div class="article-info">
                  <h4>{{ article.title }}</h4>
                  <p>{{ article.description }}</p>
                  <div class="article-meta">
                    <span class="views">{{ article.views }} views</span>
                    <span class="helpful">{{ article.helpful }}% helpful</span>
                  </div>
                </div>
                <div class="article-actions">
                  <i class="fas fa-arrow-right"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Live Chat -->
    <div class="chat-section" v-if="showChat">
      <div class="chat-header">
        <h3>Live Support Chat</h3>
        <div class="chat-actions">
          <div class="chat-status">
            <span class="status-indicator online"></span>
            <span>Support Team Online</span>
          </div>
          <button class="minimize-btn" @click="toggleChat">
            <i class="fas fa-minus"></i>
          </button>
        </div>
      </div>
      
      <div class="chat-messages" ref="chatMessages">
        <div 
          v-for="message in chatMessages" 
          :key="message.id"
          :class="['message', message.sender]"
        >
          <div class="message-avatar">
            <img :src="message.avatar" :alt="message.senderName" />
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="sender-name">{{ message.senderName }}</span>
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div class="message-text">{{ message.text }}</div>
          </div>
        </div>
      </div>
      
      <div class="chat-input">
        <div class="input-wrapper">
          <input 
            v-model="newMessage" 
            type="text" 
            placeholder="Type your message..."
            @keydown.enter="sendMessage"
          />
          <button class="send-btn" @click="sendMessage">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Create Ticket Modal -->
    <div v-if="showTicketModal" class="modal-overlay" @click="closeTicketModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create Support Ticket</h2>
          <button class="close-btn" @click="closeTicketModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="ticket-form">
            <div class="form-group">
              <label>Subject *</label>
              <input 
                v-model="ticketForm.subject" 
                type="text" 
                placeholder="Brief description of your issue"
                required
              />
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Category *</label>
                <select v-model="ticketForm.category" required>
                  <option value="">Select category</option>
                  <option value="technical">Technical Issue</option>
                  <option value="billing">Billing</option>
                  <option value="account">Account</option>
                  <option value="feature">Feature Request</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div class="form-group">
                <label>Priority *</label>
                <select v-model="ticketForm.priority" required>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Description *</label>
              <textarea 
                v-model="ticketForm.description" 
                placeholder="Detailed description of your issue"
                rows="5"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label>Attachments</label>
              <div class="file-upload">
                <input 
                  type="file" 
                  ref="fileInput"
                  multiple
                  @change="handleFileUpload"
                  accept="image/*,.pdf,.doc,.docx"
                />
                <button class="upload-btn" @click="$refs.fileInput.click()">
                  <i class="fas fa-paperclip"></i>
                  Attach Files
                </button>
                <div class="attached-files" v-if="ticketForm.attachments.length > 0">
                  <div 
                    v-for="(file, index) in ticketForm.attachments" 
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
          <button class="btn-secondary" @click="closeTicketModal">Cancel</button>
          <button class="btn-primary" @click="createTicket">
            <i class="fas fa-paper-plane"></i>
            Submit Ticket
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const ticketFilter = ref('')
const priorityFilter = ref('')
const kbSearchQuery = ref('')
const showTicketModal = ref(false)
const showChat = ref(false)
const newMessage = ref('')

// Chat state
const chatMessages = ref([])
const chatMessagesRef = ref(null)

// UI state
const expandedCategories = ref([])

// Support stats
const supportStats = reactive({
  openTickets: 12,
  ticketChange: -2,
  avgResponseTime: 2.5,
  responseChange: -0.5,
  resolvedToday: 8,
  satisfaction: 94,
  satisfactionChange: 2
})

// Ticket form
const ticketForm = reactive({
  subject: '',
  category: '',
  priority: 'medium',
  description: '',
  attachments: []
})

// Tickets data
const tickets = ref([
  {
    id: 1001,
    title: 'Login Issue with Mobile App',
    description: 'Unable to login to mobile app after recent update',
    status: 'open',
    priority: 'high',
    category: 'technical',
    createdAt: '2024-01-21T10:30:00Z',
    updatedAt: '2024-01-21T14:45:00Z',
    replies: [
      {
        id: 1,
        sender: 'support',
        senderName: 'Support Team',
        text: 'Thank you for contacting support. We are looking into this issue.',
        timestamp: '2024-01-21T11:00:00Z',
        avatar: '/api/placeholder/40x40'
      }
    ],
    views: 15,
    assignee: {
      name: 'John Doe',
      role: 'Support Agent',
      avatar: '/api/placeholder/40x40'
    }
  },
  {
    id: 1002,
    title: 'Billing Question',
    description: 'Question about recent invoice charges',
    status: 'in-progress',
    priority: 'medium',
    category: 'billing',
    createdAt: '2024-01-20T09:15:00Z',
    updatedAt: '2024-01-21T10:30:00Z',
    replies: [
      {
        id: 1,
        sender: 'support',
        senderName: 'Sarah Johnson',
        text: 'I can help you with your billing question. Let me review your invoice.',
        timestamp: '2024-01-20T10:00:00Z',
        avatar: '/api/placeholder/40x40'
      }
    ],
    views: 8,
    assignee: {
      name: 'Sarah Johnson',
      role: 'Billing Specialist',
      avatar: '/api/placeholder/40x40'
    }
  },
  {
    id: 1003,
    title: 'Feature Request: Dark Mode',
    description: 'Request for dark mode feature in the application',
    status: 'resolved',
    priority: 'low',
    category: 'feature',
    createdAt: '2024-01-19T16:45:00Z',
    updatedAt: '2024-01-21T09:00:00Z',
    replies: [
      {
        id: 1,
        sender: 'support',
        senderName: 'Mike Wilson',
        text: 'Thank you for your suggestion! We have added this to our feature roadmap.',
        timestamp: '2024-01-19T17:30:00Z',
        avatar: '/api/placeholder/40x40'
      }
    ],
    views: 23,
    assignee: {
      name: 'Mike Wilson',
      role: 'Product Manager',
      avatar: '/api/placeholder/40x40'
    }
  }
])

// Knowledge base categories
const kbCategories = ref([
  {
    id: 1,
    name: 'Getting Started',
    description: 'Basic setup and initial configuration',
    icon: 'fas fa-rocket',
    articles: [
      {
        id: 101,
        title: 'How to Create Your First Project',
        description: 'Step-by-step guide to creating your first project',
        views: 1250,
        helpful: 92
      },
      {
        id: 102,
        title: 'Understanding the Dashboard',
        description: 'Overview of the main dashboard features',
        views: 890,
        helpful: 88
      }
    ]
  },
  {
    id: 2,
    name: 'Account Management',
    description: 'Managing your account and settings',
    icon: 'fas fa-user-cog',
    articles: [
      {
        id: 201,
        title: 'Changing Your Password',
        description: 'How to securely change your account password',
        views: 567,
        helpful: 95
      },
      {
        id: 202,
        title: 'Two-Factor Authentication Setup',
        description: 'Enable 2FA for enhanced security',
        views: 432,
        helpful: 91
      }
    ]
  },
  {
    id: 3,
    name: 'Troubleshooting',
    description: 'Common issues and solutions',
    icon: 'fas fa-wrench',
    articles: [
      {
        id: 301,
        title: 'Fixing Login Issues',
        description: 'Common login problems and their solutions',
        views: 789,
        helpful: 87
      },
      {
        id: 302,
        title: 'Performance Optimization Tips',
        description: 'How to improve application performance',
        views: 654,
        helpful: 84
      }
    ]
  }
])

// Computed properties
const filteredTickets = computed(() => {
  let filtered = tickets.value

  if (ticketFilter.value) {
    filtered = filtered.filter(ticket => ticket.status === ticketFilter.value)
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(ticket => ticket.priority === priorityFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
})

// Methods
const filterTickets = () => {
  // Filtering is handled by computed property
}

const getEmptyMessage = () => {
  if (ticketFilter.value || priorityFilter.value) {
    return 'No tickets match your filter criteria'
  }
  return 'No tickets found'
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

const formatStatus = (status) => {
  return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const openTicket = (ticket) => {
  // Navigate to ticket details or open modal
  showSuccess(`Opening ticket #${ticket.id}`)
}

const replyToTicket = (ticket) => {
  // Open reply interface
  showSuccess(`Replying to ticket #${ticket.id}`)
}

const startLiveChat = () => {
  showChat.value = true
  // Initialize chat with welcome message
  if (chatMessages.value.length === 0) {
    chatMessages.value.push({
      id: Date.now(),
      sender: 'support',
      senderName: 'Support Team',
      text: 'Hello! How can I help you today?',
      timestamp: new Date().toISOString(),
      avatar: '/api/placeholder/40x40'
    })
  }
  showSuccess('Live chat started')
}

const toggleChat = () => {
  showChat.value = !showChat.value
}

const sendMessage = () => {
  if (!newMessage.value.trim()) return

  const message = {
    id: Date.now(),
    sender: 'user',
    senderName: 'You',
    text: newMessage.value,
    timestamp: new Date().toISOString(),
    avatar: '/api/placeholder/40x40'
  }

  chatMessages.value.push(message)
  newMessage.value = ''

  // Scroll to bottom
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })

  // Simulate support response
  setTimeout(() => {
    const response = {
      id: Date.now() + 1,
      sender: 'support',
      senderName: 'Support Agent',
      text: 'Thank you for your message. I\'ll look into this and get back to you shortly.',
      timestamp: new Date().toISOString(),
      avatar: '/api/placeholder/40x40'
    }
    chatMessages.value.push(response)
    
    nextTick(() => {
      if (chatMessagesRef.value) {
        chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
      }
    })
  }, 1000)
}

const scheduleCall = () => {
  showSuccess('Opening call scheduling interface')
}

const viewFAQ = () => {
  showSuccess('Navigating to FAQ section')
}

const expandCategory = (categoryId) => {
  const index = expandedCategories.value.indexOf(categoryId)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
  } else {
    expandedCategories.value.push(categoryId)
  }
}

const searchKB = () => {
  // Search knowledge base
  showSuccess('Searching knowledge base...')
}

const openArticle = (article) => {
  showSuccess(`Opening article: ${article.title}`)
}

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  ticketForm.attachments.push(...files)
}

const removeFile = (index) => {
  ticketForm.attachments.splice(index, 1)
}

const createTicket = async () => {
  if (!ticketForm.subject || !ticketForm.category || !ticketForm.description) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/support/tickets', ticketForm)
    // if (response.success) {
    //   tickets.value.unshift(response.ticket)
    //   showSuccess('Ticket created successfully')
    //   closeTicketModal()
    //   resetTicketForm()
    // }
    
    // For demo, simulate creation
    const newTicket = {
      id: Date.now(),
      title: ticketForm.subject,
      description: ticketForm.description,
      status: 'open',
      priority: ticketForm.priority,
      category: ticketForm.category,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      replies: [],
      views: 0,
      assignee: null
    }
    
    tickets.value.unshift(newTicket)
    showSuccess('Ticket created successfully')
    closeTicketModal()
    resetTicketForm()
  } catch (error) {
    console.error('Error creating ticket:', error)
    showError('Failed to create ticket')
  }
}

const closeTicketModal = () => {
  showTicketModal.value = false
  resetTicketForm()
}

const resetTicketForm = () => {
  Object.assign(ticketForm, {
    subject: '',
    category: '',
    priority: 'medium',
    description: '',
    attachments: []
  })
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/support')
    // if (response.success) {
    //   tickets.value = response.tickets || []
    //   kbCategories.value = response.kbCategories || []
    //   Object.assign(supportStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading support data:', error)
    showError('Failed to load support data')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.support {
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
.tickets-section,
.knowledge-section {
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

.action-icon.chat {
  background: var(--success-color);
}

.action-icon.call {
  background: var(--info-color);
}

.action-icon.faq {
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

.stat-icon.response {
  background: var(--info-color);
}

.stat-icon.resolved {
  background: var(--success-color);
}

.stat-icon.satisfaction {
  background: var(--warning-color);
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

.create-ticket-btn,
.create-first-btn {
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

.create-ticket-btn:hover,
.create-first-btn:hover {
  background: var(--primary-hover);
}

.create-first-btn {
  margin-top: 2rem;
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

.tickets-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ticket-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.ticket-card:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
}

.ticket-card.urgent {
  border-left: 4px solid var(--danger-color);
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.ticket-info {
  flex: 1;
}

.ticket-id {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.ticket-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.ticket-meta {
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

.status-badge.open {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.in-progress {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.resolved {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.closed {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
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

.priority-badge.urgent {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-weight: 700;
}

.ticket-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.ticket-details {
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

.ticket-assignee {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.ticket-assignee img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.assignee-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.assignee-name {
  font-weight: 600;
  color: var(--text-primary);
}

.assignee-role {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.ticket-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

.ticket-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.ticket-actions {
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
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.reply:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box i {
  position: absolute;
  left: 1rem;
  color: var(--text-secondary);
}

.search-box input {
  padding: 0.75rem 1rem 0.75rem 3rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
}

.search-box input:focus {
  border-color: var(--primary-color);
}

.kb-categories {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.kb-category {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: var(--glass-bg-tertiary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-header:hover {
  background: var(--glass-bg-hover);
}

.category-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.category-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.category-toggle {
  color: var(--text-secondary);
}

.category-content {
  padding: 0 1.5rem 1.5rem;
}

.category-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.category-articles {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.article-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.article-item:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
}

.article-info {
  flex: 1;
}

.article-info h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.article-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.article-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.article-actions {
  color: var(--primary-color);
  font-size: 1rem;
}

.chat-section {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 400px;
  height: 500px;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-bottom: 1px solid var(--glass-border);
  border-radius: 16px 16px 0 0;
}

.chat-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1rem;
}

.chat-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chat-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success-color);
}

.status-indicator.online {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.minimize-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.minimize-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  gap: 0.75rem;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  flex: 1;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.message.user .message-header {
  flex-direction: row-reverse;
}

.sender-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
}

.message-time {
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.message-text {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  line-height: 1.4;
}

.message.user .message-text {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.chat-input {
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-top: 1px solid var(--glass-border);
  border-radius: 0 0 16px 16px;
}

.input-wrapper {
  display: flex;
  gap: 0.5rem;
}

.input-wrapper input {
  flex: 1;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  outline: none;
}

.input-wrapper input:focus {
  border-color: var(--primary-color);
}

.send-btn {
  padding: 0.75rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.send-btn:hover {
  background: var(--primary-hover);
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

.ticket-form {
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
  min-height: 120px;
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
  .support {
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
  
  .ticket-details {
    grid-template-columns: 1fr;
  }
  
  .ticket-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .chat-section {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 0;
    top: auto;
    width: 100%;
    height: 70vh;
    border-radius: 16px 16px 0 0;
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
