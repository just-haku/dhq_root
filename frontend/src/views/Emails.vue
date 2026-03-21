<template>
  <div class="emails">
    <div class="page-header">
      <h1>Email Management</h1>
      <p>Configure and manage email services and templates</p>
    </div>

    <!-- Email Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-envelope"></i>
          </div>
          <div class="card-content">
            <h3>{{ emailStats.totalSent }}</h3>
            <p>Total Sent</p>
            <span class="sent-count">{{ emailStats.todaySent }} today</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon templates">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ emailStats.totalTemplates }}</h3>
            <p>Templates</p>
            <span class="template-count">{{ emailStats.activeTemplates }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon delivery">
            <i class="fas fa-paper-plane"></i>
          </div>
          <div class="card-content">
            <h3>{{ emailStats.deliveryRate }}%</h3>
            <p>Delivery Rate</p>
            <span class="delivery-status" :class="getDeliveryClass(emailStats.deliveryRate)">
              {{ getDeliveryStatus(emailStats.deliveryRate) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon queue">
            <i class="fas fa-inbox"></i>
          </div>
          <div class="card-content">
            <h3>{{ emailStats.queueSize }}</h3>
            <p>Queue Size</p>
            <span class="queue-status">{{ emailStats.processingRate }}/min</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="send-btn" @click="showComposeModal = true">
          <i class="fas fa-paper-plane"></i>
          Send Email
        </button>
        <button class="template-btn" @click="showTemplateModal = true">
          <i class="fas fa-file-alt"></i>
          Create Template
        </button>
        <button class="test-btn" @click="showTestModal = true">
          <i class="fas fa-vial"></i>
          Test Email
        </button>
        <button class="settings-btn" @click="showSettingsModal = true">
          <i class="fas fa-cog"></i>
          Settings
        </button>
      </div>
    </div>

    <!-- Email Services -->
    <div class="services-section">
      <div class="section-header">
        <h2>Email Services</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="serviceFilter" @change="filterServices">
              <option value="">All Services</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div class="view-toggle">
            <button 
              :class="['view-btn', { active: viewMode === 'grid' }]"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'list' }]"
              @click="viewMode = 'list'"
            >
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading email services...</p>
      </div>

      <div v-else-if="filteredServices.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-envelope"></i>
        </div>
        <h3>No email services found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="services-grid">
          <div 
            v-for="service in filteredServices" 
            :key="service.id"
            class="service-card"
            :class="{ 'inactive': service.status === 'inactive', 'error': service.status === 'error' }"
          >
            <div class="service-header">
              <div class="service-icon">
                <i :class="getServiceIcon(service.provider)"></i>
              </div>
              <div class="service-status">
                <span :class="['status-badge', service.status]">{{ service.status }}</span>
              </div>
            </div>

            <div class="service-content">
              <h3>{{ service.name }}</h3>
              <p>{{ service.description }}</p>
              
              <div class="service-info">
                <span class="provider">{{ service.provider }}</span>
                <span class="region">{{ service.region }}</span>
                <span class="sent">{{ service.sentToday }} sent today</span>
              </div>

              <div class="service-stats">
                <div class="stat-item">
                  <label>Delivery Rate:</label>
                  <span :class="getDeliveryClass(service.deliveryRate)">{{ service.deliveryRate }}%</span>
                </div>
                <div class="stat-item">
                  <label>Avg Time:</label>
                  <span>{{ service.avgDeliveryTime }}s</span>
                </div>
                <div class="stat-item">
                  <label>Last Sent:</label>
                  <span>{{ formatDateTime(service.lastSent) }}</span>
                </div>
              </div>

              <div class="service-actions">
                <button class="action-btn test" @click="testService(service)">
                  <i class="fas fa-vial"></i>
                  Test
                </button>
                <button class="action-btn configure" @click="configureService(service)">
                  <i class="fas fa-cog"></i>
                  Configure
                </button>
                <button 
                  class="action-btn toggle"
                  @click="toggleService(service)"
                  :class="service.status === 'active' ? 'disable' : 'enable'"
                >
                  <i :class="service.status === 'active' ? 'fas fa-pause' : 'fas fa-play'"></i>
                  {{ service.status === 'active' ? 'Disable' : 'Enable' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="services-list">
          <div 
            v-for="service in filteredServices" 
            :key="service.id"
            class="service-list-card"
            :class="{ 'inactive': service.status === 'inactive', 'error': service.status === 'error' }"
          >
            <div class="service-list-header">
              <div class="service-list-info">
                <div class="service-icon">
                  <i :class="getServiceIcon(service.provider)"></i>
                </div>
                <div class="service-details">
                  <h3>{{ service.name }}</h3>
                  <p>{{ service.description }}</p>
                  <div class="service-info">
                    <span class="provider">{{ service.provider }}</span>
                    <span class="region">{{ service.region }}</span>
                    <span :class="['status-badge', service.status]">{{ service.status }}</span>
                    <span class="sent">{{ service.sentToday }} sent today</span>
                  </div>
                </div>
              </div>
              <div class="service-list-stats">
                <div class="stat-item">
                  <label>Delivery Rate:</label>
                  <span :class="getDeliveryClass(service.deliveryRate)">{{ service.deliveryRate }}%</span>
                </div>
                <div class="stat-item">
                  <label>Avg Time:</label>
                  <span>{{ service.avgDeliveryTime }}s</span>
                </div>
                <div class="stat-item">
                  <label>Last Sent:</label>
                  <span>{{ formatDateTime(service.lastSent) }}</span>
                </div>
              </div>
              <div class="service-list-actions">
                <button class="action-btn test" @click="testService(service)">
                  <i class="fas fa-vial"></i>
                </button>
                <button class="action-btn configure" @click="configureService(service)">
                  <i class="fas fa-cog"></i>
                </button>
                <button 
                  class="action-btn toggle"
                  @click="toggleService(service)"
                  :class="service.status === 'active' ? 'disable' : 'enable'"
                >
                  <i :class="service.status === 'active' ? 'fas fa-pause' : 'fas fa-play'"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Email Templates -->
    <div class="templates-section">
      <div class="section-header">
        <h2>Email Templates</h2>
        <div class="header-actions">
          <button class="create-template-btn" @click="showTemplateModal = true">
            <i class="fas fa-plus"></i>
            Create Template
          </button>
        </div>
      </div>

      <div class="templates-grid">
        <div 
          v-for="template in templates" 
          :key="template.id"
          class="template-card"
        >
          <div class="template-header">
            <div class="template-icon">
              <i class="fas fa-file-alt"></i>
            </div>
            <div class="template-info">
              <h3>{{ template.name }}</h3>
              <p>{{ template.description }}</p>
            </div>
            <div class="template-status">
              <span :class="['status-badge', template.status]">{{ template.status }}</span>
            </div>
          </div>

          <div class="template-details">
            <div class="template-item">
              <label>Type:</label>
              <span>{{ template.type }}</span>
            </div>
            <div class="template-item">
              <label>Language:</label>
              <span>{{ template.language }}</span>
            </div>
            <div class="template-item">
              <label>Used:</label>
              <span>{{ template.usageCount }} times</span>
            </div>
            <div class="template-item">
              <label>Created:</label>
              <span>{{ formatDate(template.createdAt) }}</span>
            </div>
          </div>

          <div class="template-actions">
            <button class="action-btn preview" @click="previewTemplate(template)">
              <i class="fas fa-eye"></i>
              Preview
            </button>
            <button class="action-btn edit" @click="editTemplate(template)">
              <i class="fas fa-edit"></i>
              Edit
            </button>
            <button class="action-btn duplicate" @click="duplicateTemplate(template)">
              <i class="fas fa-copy"></i>
              Duplicate
            </button>
            <button class="action-btn delete" @click="deleteTemplate(template)">
              <i class="fas fa-trash"></i>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Compose Email Modal -->
    <div v-if="showComposeModal" class="modal-overlay" @click="closeComposeModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Compose Email</h2>
          <button class="close-btn" @click="closeComposeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="email-form">
            <div class="form-grid">
              <div class="form-group">
                <label>To *</label>
                <input 
                  v-model="emailForm.to" 
                  type="email" 
                  placeholder="recipient@example.com"
                  required
                />
              </div>
              <div class="form-group">
                <label>CC</label>
                <input 
                  v-model="emailForm.cc" 
                  type="email" 
                  placeholder="cc@example.com"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Subject *</label>
              <input 
                v-model="emailForm.subject" 
                type="text" 
                placeholder="Email subject"
                required
              />
            </div>

            <div class="form-group">
              <label>Template</label>
              <select v-model="emailForm.templateId">
                <option value="">No template</option>
                <option 
                  v-for="template in templates" 
                  :key="template.id"
                  :value="template.id"
                >
                  {{ template.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Message *</label>
              <textarea 
                v-model="emailForm.message" 
                placeholder="Email message"
                rows="10"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label>Attachments</label>
              <div class="attachments-container">
                <div 
                  v-for="(attachment, index) in emailForm.attachments" 
                  :key="index"
                  class="attachment-item"
                >
                  <span class="attachment-name">{{ attachment.name }}</span>
                  <button 
                    class="remove-attachment"
                    @click="removeAttachment(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-attachment-btn" @click="addAttachment">
                  <i class="fas fa-paperclip"></i>
                  Add Attachment
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>Options</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="emailForm.trackOpens"
                  />
                  <span>Track opens</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="emailForm.trackClicks"
                  />
                  <span>Track clicks</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="emailForm.priority"
                  />
                  <span>High priority</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeComposeModal">Cancel</button>
          <button class="btn-primary" @click="sendEmail">
            <i class="fas fa-paper-plane"></i>
            Send Email
          </button>
        </div>
      </div>
    </div>

    <!-- Test Email Modal -->
    <div v-if="showTestModal" class="modal-overlay" @click="closeTestModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Test Email Service</h2>
          <button class="close-btn" @click="closeTestModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="test-form">
            <div class="form-group">
              <label>Service *</label>
              <select v-model="testForm.serviceId" required>
                <option value="">Select service</option>
                <option 
                  v-for="service in services.value" 
                  :key="service.id"
                  :value="service.id"
                >
                  {{ service.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Test Email *</label>
              <input 
                v-model="testForm.email" 
                type="email" 
                placeholder="test@example.com"
                required
              />
            </div>

            <div class="form-group">
              <label>Subject</label>
              <input 
                v-model="testForm.subject" 
                type="text" 
                placeholder="Test email subject"
              />
            </div>

            <div class="form-group">
              <label>Message</label>
              <textarea 
                v-model="testForm.message" 
                placeholder="Test email message"
                rows="5"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeTestModal">Cancel</button>
          <button class="btn-primary" @click="testEmail">
            <i class="fas fa-vial"></i>
            Send Test
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
const serviceFilter = ref('')
const viewMode = ref('grid')
const showComposeModal = ref(false)
const showTemplateModal = ref(false)
const showTestModal = ref(false)
const showSettingsModal = ref(false)

// Email stats
const emailStats = reactive({
  totalSent: 12456,
  todaySent: 234,
  totalTemplates: 45,
  activeTemplates: 38,
  deliveryRate: 96.8,
  queueSize: 23,
  processingRate: 450
})

// Email form
const emailForm = reactive({
  to: '',
  cc: '',
  subject: '',
  templateId: '',
  message: '',
  attachments: [],
  trackOpens: true,
  trackClicks: true,
  priority: false
})

// Test form
const testForm = reactive({
  serviceId: '',
  email: '',
  subject: 'Test Email',
  message: 'This is a test email to verify the email service configuration.'
})

// Mock data
const services = ref([
  {
    id: 1,
    name: 'Primary SMTP',
    description: 'Main SMTP email service',
    provider: 'SMTP',
    status: 'active',
    region: 'US East',
    sentToday: 156,
    deliveryRate: 97.2,
    avgDeliveryTime: 2.3,
    lastSent: '2024-01-21T10:30:00Z'
  },
  {
    id: 2,
    name: 'SendGrid',
    description: 'SendGrid email service',
    provider: 'SendGrid',
    status: 'active',
    region: 'US West',
    sentToday: 78,
    deliveryRate: 98.5,
    avgDeliveryTime: 1.8,
    lastSent: '2024-01-21T10:15:00Z'
  },
  {
    id: 3,
    name: 'Mailgun',
    description: 'Mailgun email service',
    provider: 'Mailgun',
    status: 'inactive',
    region: 'EU',
    sentToday: 0,
    deliveryRate: 95.1,
    avgDeliveryTime: 2.1,
    lastSent: '2024-01-20T23:45:00Z'
  },
  {
    id: 4,
    name: 'Amazon SES',
    description: 'Amazon SES email service',
    provider: 'AWS SES',
    status: 'active',
    region: 'US East',
    sentToday: 234,
    deliveryRate: 99.1,
    avgDeliveryTime: 1.5,
    lastSent: '2024-01-21T10:25:00Z'
  }
])

const templates = ref([
  {
    id: 1,
    name: 'Welcome Email',
    description: 'Welcome email for new users',
    type: 'Welcome',
    language: 'English',
    status: 'active',
    usageCount: 456,
    createdAt: '2024-01-15T10:30:00Z'
  },
  {
    id: 2,
    name: 'Password Reset',
    description: 'Password reset email template',
    type: 'Security',
    language: 'English',
    status: 'active',
    usageCount: 234,
    createdAt: '2024-01-10T09:15:00Z'
  },
  {
    id: 3,
    name: 'Order Confirmation',
    description: 'Order confirmation email',
    type: 'E-commerce',
    language: 'English',
    status: 'active',
    usageCount: 789,
    createdAt: '2024-01-05T11:20:00Z'
  },
  {
    id: 4,
    name: 'Newsletter',
    description: 'Monthly newsletter template',
    type: 'Marketing',
    language: 'English',
    status: 'draft',
    usageCount: 0,
    createdAt: '2024-01-20T14:30:00Z'
  }
])

// Computed properties
const filteredServices = computed(() => {
  let filtered = services.value

  if (serviceFilter.value) {
    filtered = filtered.filter(service => service.status === serviceFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.lastSent) - new Date(a.lastSent))
})

// Methods
const loadEmailData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/emails')
    // if (response.success) {
    //   services.value = response.services || []
    //   templates.value = response.templates || []
    //   Object.assign(emailStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading email data:', error)
    showError('Failed to load email data')
  } finally {
    loading.value = false
  }
}

const filterServices = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (serviceFilter.value) {
    return 'No email services match your filter criteria'
  }
  return 'No email services found'
}

const getServiceIcon = (provider) => {
  const icons = {
    'SMTP': 'fas fa-envelope',
    'SendGrid': 'fas fa-paper-plane',
    'Mailgun': 'fas fa-envelope-open-text',
    'AWS SES': 'fab fa-aws',
    'Postmark': 'fas fa-envelope-square',
    'Mailchimp': 'fas fa-envelope-open'
  }
  return icons[provider] || 'fas fa-envelope'
}

const getDeliveryClass = (rate) => {
  if (rate >= 98) return 'excellent'
  if (rate >= 95) return 'good'
  if (rate >= 90) return 'fair'
  return 'poor'
}

const getDeliveryStatus = (rate) => {
  if (rate >= 98) return 'Excellent'
  if (rate >= 95) return 'Good'
  if (rate >= 90) return 'Fair'
  return 'Needs Improvement'
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const testService = async (service) => {
  try {
    // const response = await apiPost(`/emails/services/${service.id}/test`)
    // if (response.success) {
    //   showSuccess('Test email sent successfully')
    // }
    
    // For demo, simulate test
    showSuccess('Test email sent successfully')
  } catch (error) {
    console.error('Error testing service:', error)
    showError('Failed to send test email')
  }
}

const configureService = (service) => {
  // Open service configuration modal or navigate to detailed view
  showSuccess(`Opening configuration for ${service.name}`)
}

const toggleService = async (service) => {
  try {
    // const response = await apiPut(`/emails/services/${service.id}/toggle`)
    // if (response.success) {
    //   service.status = service.status === 'active' ? 'inactive' : 'active'
    //   showSuccess(`Service ${service.status === 'active' ? 'activated' : 'deactivated'}`)
    // }
    
    // For demo, simulate toggle
    service.status = service.status === 'active' ? 'inactive' : 'active'
    showSuccess(`Service ${service.status === 'active' ? 'activated' : 'deactivated'}`)
  } catch (error) {
    console.error('Error toggling service:', error)
    showError('Failed to toggle service')
  }
}

const previewTemplate = (template) => {
  // Open template preview modal
  showSuccess(`Previewing template: ${template.name}`)
}

const editTemplate = (template) => {
  // Open template editor
  showSuccess(`Editing template: ${template.name}`)
}

const duplicateTemplate = async (template) => {
  try {
    // const response = await apiPost(`/emails/templates/${template.id}/duplicate`)
    // if (response.success) {
    //   const newTemplate = response.template
    //   templates.value.unshift(newTemplate)
    //   showSuccess('Template duplicated successfully')
    // }
    
    // For demo, simulate duplication
    const newTemplate = {
      ...template,
      id: Date.now(),
      name: `${template.name} (Copy)`,
      usageCount: 0,
      status: 'draft',
      createdAt: new Date().toISOString()
    }
    
    templates.value.unshift(newTemplate)
    showSuccess('Template duplicated successfully')
  } catch (error) {
    console.error('Error duplicating template:', error)
    showError('Failed to duplicate template')
  }
}

const deleteTemplate = async (template) => {
  const confirmed = await showConfirm(`Are you sure you want to delete template "${template.name}"?`)
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/emails/templates/${template.id}`)
    // if (response.success) {
    //   const index = templates.value.findIndex(t => t.id === template.id)
    //   if (index > -1) {
    //     templates.value.splice(index, 1)
    //     showSuccess('Template deleted successfully')
    //   }
    // }
    
    // For demo, simulate deletion
    const index = templates.value.findIndex(t => t.id === template.id)
    if (index > -1) {
      templates.value.splice(index, 1)
      showSuccess('Template deleted successfully')
    }
  } catch (error) {
    console.error('Error deleting template:', error)
    showError('Failed to delete template')
  }
}

const addAttachment = () => {
  // In real app, this would open file picker
  const mockAttachment = {
    name: 'document.pdf',
    size: '2.3MB',
    type: 'application/pdf'
  }
  emailForm.attachments.push(mockAttachment)
}

const removeAttachment = (index) => {
  emailForm.attachments.splice(index, 1)
}

const sendEmail = async () => {
  if (!emailForm.to || !emailForm.subject || !emailForm.message) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/emails/send', emailForm)
    // if (response.success) {
    //   showSuccess('Email sent successfully')
    //   closeComposeModal()
    //   resetEmailForm()
    // }
    
    // For demo, simulate send
    showSuccess('Email sent successfully')
    closeComposeModal()
    resetEmailForm()
  } catch (error) {
    console.error('Error sending email:', error)
    showError('Failed to send email')
  }
}

const testEmail = async () => {
  if (!testForm.serviceId || !testForm.email) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/emails/test', testForm)
    // if (response.success) {
    //   showSuccess('Test email sent successfully')
    //   closeTestModal()
    //   resetTestForm()
    // }
    
    // For demo, simulate test
    showSuccess('Test email sent successfully')
    closeTestModal()
    resetTestForm()
  } catch (error) {
    console.error('Error sending test email:', error)
    showError('Failed to send test email')
  }
}

const closeComposeModal = () => {
  showComposeModal.value = false
  resetEmailForm()
}

const closeTestModal = () => {
  showTestModal.value = false
  resetTestForm()
}

const resetEmailForm = () => {
  Object.assign(emailForm, {
    to: '',
    cc: '',
    subject: '',
    templateId: '',
    message: '',
    attachments: [],
    trackOpens: true,
    trackClicks: true,
    priority: false
  })
}

const resetTestForm = () => {
  Object.assign(testForm, {
    serviceId: '',
    email: '',
    subject: 'Test Email',
    message: 'This is a test email to verify the email service configuration.'
  })
}

// Lifecycle
onMounted(() => {
  loadEmailData()
})
</script>

<style scoped>
.emails {
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

.card-icon.templates {
  background: var(--success-color);
}

.card-icon.delivery {
  background: var(--warning-color);
}

.card-icon.queue {
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

.sent-count,
.template-count,
.delivery-status,
.queue-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.sent-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.template-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.delivery-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.delivery-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.delivery-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.delivery-status.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.queue-status {
  color: var(--text-secondary);
}

.actions-section {
  margin-bottom: 3rem;
}

.action-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.send-btn,
.template-btn,
.test-btn,
.settings-btn {
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
}

.send-btn:hover,
.template-btn:hover,
.test-btn:hover,
.settings-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.template-btn {
  background: var(--success-color);
}

.template-btn:hover {
  background: var(--success-hover);
}

.test-btn {
  background: var(--warning-color);
}

.test-btn:hover {
  background: var(--warning-hover);
}

.settings-btn {
  background: var(--info-color);
}

.settings-btn:hover {
  background: var(--info-hover);
}

.services-section,
.templates-section {
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

.filter-dropdown select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.create-template-btn {
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

.create-template-btn:hover {
  background: var(--primary-hover);
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

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.service-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.service-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.service-card.inactive {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.service-card.error {
  border-color: var(--danger-color);
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.service-icon {
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

.status-badge.inactive {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.service-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.service-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.service-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.provider,
.region,
.sent {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.service-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
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

.excellent {
  color: #10b981;
}

.good {
  color: #3b82f6;
}

.fair {
  color: #f59e0b;
}

.poor {
  color: #ef4444;
}

.service-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.action-btn.test:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.configure:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.toggle.enable:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.toggle.disable:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.services-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.service-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.service-list-card:hover {
  background: var(--glass-bg-hover);
}

.service-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.service-list-info {
  flex: 1;
}

.service-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.service-list-actions {
  display: flex;
  gap: 0.5rem;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.template-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.template-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.template-icon {
  width: 50px;
  height: 50px;
  background: var(--info-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.template-info {
  flex: 1;
}

.template-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.template-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.template-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.template-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.template-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.template-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn.preview:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.edit:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.duplicate:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
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

.email-form,
.test-form {
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
  min-height: 80px;
}

.attachments-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.attachment-name {
  color: var(--text-primary);
  font-weight: 500;
}

.remove-attachment {
  width: 32px;
  height: 32px;
  border: 1px solid var(--danger-color);
  border-radius: 6px;
  background: var(--danger-color);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.remove-attachment:hover {
  background: var(--danger-hover);
}

.add-attachment-btn {
  padding: 0.75rem 1rem;
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
  align-self: flex-start;
}

.add-attachment-btn:hover {
  background: var(--primary-hover);
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary {
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
  .emails {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .service-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .service-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .template-details {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
