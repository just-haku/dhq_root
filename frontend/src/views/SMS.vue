<template>
  <div class="sms">
    <div class="page-header">
      <h1>SMS Management</h1>
      <p>Configure and manage SMS services and messaging</p>
    </div>

    <!-- SMS Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-sms"></i>
          </div>
          <div class="card-content">
            <h3>{{ smsStats.totalSent }}</h3>
            <p>Total Sent</p>
            <span class="sent-count">{{ smsStats.todaySent }} today</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon templates">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ smsStats.totalTemplates }}</h3>
            <p>Templates</p>
            <span class="template-count">{{ smsStats.activeTemplates }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon delivery">
            <i class="fas fa-paper-plane"></i>
          </div>
          <div class="card-content">
            <h3>{{ smsStats.deliveryRate }}%</h3>
            <p>Delivery Rate</p>
            <span class="delivery-status" :class="getDeliveryClass(smsStats.deliveryRate)">
              {{ getDeliveryStatus(smsStats.deliveryRate) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon queue">
            <i class="fas fa-inbox"></i>
          </div>
          <div class="card-content">
            <h3>{{ smsStats.queueSize }}</h3>
            <p>Queue Size</p>
            <span class="queue-status">{{ smsStats.processingRate }}/min</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="send-btn" @click="showComposeModal = true">
          <i class="fas fa-paper-plane"></i>
          Send SMS
        </button>
        <button class="template-btn" @click="showTemplateModal = true">
          <i class="fas fa-file-alt"></i>
          Create Template
        </button>
        <button class="test-btn" @click="showTestModal = true">
          <i class="fas fa-vial"></i>
          Test SMS
        </button>
        <button class="settings-btn" @click="showSettingsModal = true">
          <i class="fas fa-cog"></i>
          Settings
        </button>
      </div>
    </div>

    <!-- SMS Services -->
    <div class="services-section">
      <div class="section-header">
        <h2>SMS Services</h2>
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
        <p>Loading SMS services...</p>
      </div>

      <div v-else-if="filteredServices.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-sms"></i>
        </div>
        <h3>No SMS services found</h3>
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

    <!-- SMS Templates -->
    <div class="templates-section">
      <div class="section-header">
        <h2>SMS Templates</h2>
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

    <!-- Compose SMS Modal -->
    <div v-if="showComposeModal" class="modal-overlay" @click="closeComposeModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Compose SMS</h2>
          <button class="close-btn" @click="closeComposeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="sms-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Phone Number *</label>
                <input 
                  v-model="smsForm.phoneNumber" 
                  type="tel" 
                  placeholder="+1234567890"
                  required
                />
              </div>
              <div class="form-group">
                <label>Country Code</label>
                <select v-model="smsForm.countryCode">
                  <option value="+1">+1 (US)</option>
                  <option value="+44">+44 (UK)</option>
                  <option value="+49">+49 (DE)</option>
                  <option value="+33">+33 (FR)</option>
                  <option value="+86">+86 (CN)</option>
                  <option value="+91">+91 (IN)</option>
                  <option value="+81">+81 (JP)</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Message *</label>
              <textarea 
                v-model="smsForm.message" 
                placeholder="SMS message (max 160 characters)"
                rows="4"
                maxlength="160"
                required
              ></textarea>
              <div class="character-count">
                {{ smsForm.message.length }}/160 characters
              </div>
            </div>

            <div class="form-group">
              <label>Template</label>
              <select v-model="smsForm.templateId">
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
              <label>Schedule</label>
              <select v-model="smsForm.schedule">
                <option value="immediate">Send Immediately</option>
                <option value="scheduled">Schedule</option>
              </select>
            </div>

            <div class="form-group" v-if="smsForm.schedule === 'scheduled'">
              <label>Schedule Time</label>
              <input 
                v-model="smsForm.scheduledTime" 
                type="datetime-local"
                required
              />
            </div>

            <div class="form-group">
              <label>Options</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="smsForm.trackDelivery"
                  />
                  <span>Track delivery</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="smsForm.priority"
                  />
                  <span>High priority</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="smsForm.flash"
                  />
                  <span>Flash SMS</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeComposeModal">Cancel</button>
          <button class="btn-primary" @click="sendSMS">
            <i class="fas fa-paper-plane"></i>
            Send SMS
          </button>
        </div>
      </div>
    </div>

    <!-- Test SMS Modal -->
    <div v-if="showTestModal" class="modal-overlay" @click="closeTestModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Test SMS Service</h2>
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
              <label>Test Phone Number *</label>
              <input 
                v-model="testForm.phoneNumber" 
                type="tel" 
                placeholder="+1234567890"
                required
              />
            </div>

            <div class="form-group">
              <label>Test Message</label>
              <textarea 
                v-model="testForm.message" 
                placeholder="Test SMS message"
                rows="3"
                maxlength="160"
              ></textarea>
              <div class="character-count">
                {{ testForm.message.length }}/160 characters
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeTestModal">Cancel</button>
          <button class="btn-primary" @click="testSMS">
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

// SMS stats
const smsStats = reactive({
  totalSent: 345678,
  todaySent: 567,
  totalTemplates: 23,
  activeTemplates: 18,
  deliveryRate: 98.2,
  queueSize: 12,
  processingRate: 234
})

// SMS form
const smsForm = reactive({
  phoneNumber: '',
  countryCode: '+1',
  message: '',
  templateId: '',
  schedule: 'immediate',
  scheduledTime: '',
  trackDelivery: true,
  priority: false,
  flash: false
})

// Test form
const testForm = reactive({
  serviceId: '',
  phoneNumber: '',
  message: 'This is a test SMS to verify the SMS service configuration.'
})

// Mock data
const services = ref([
  {
    id: 1,
    name: 'Twilio',
    description: 'Twilio SMS service',
    provider: 'Twilio',
    status: 'active',
    region: 'US East',
    sentToday: 234,
    deliveryRate: 98.5,
    avgDeliveryTime: 1.2,
    lastSent: '2024-01-21T10:30:00Z'
  },
  {
    id: 2,
    name: 'Nexmo',
    description: 'Nexmo SMS service',
    provider: 'Nexmo',
    status: 'active',
    region: 'US West',
    sentToday: 156,
    deliveryRate: 97.8,
    avgDeliveryTime: 1.5,
    lastSent: '2024-01-21T10:15:00Z'
  },
  {
    id: 3,
    name: 'Plivo',
    description: 'Plivo SMS service',
    provider: 'Plivo',
    status: 'inactive',
    region: 'EU',
    sentToday: 0,
    deliveryRate: 95.1,
    avgDeliveryTime: 1.8,
    lastSent: '2024-01-20T23:45:00Z'
  },
  {
    id: 4,
    name: 'MessageBird',
    description: 'MessageBird SMS service',
    provider: 'MessageBird',
    status: 'active',
    region: 'US East',
    sentToday: 177,
    deliveryRate: 99.1,
    avgDeliveryTime: 1.0,
    lastSent: '2024-01-21T10:25:00Z'
  }
])

const templates = ref([
  {
    id: 1,
    name: 'Welcome SMS',
    description: 'Welcome SMS for new users',
    type: 'Welcome',
    language: 'English',
    status: 'active',
    usageCount: 1234,
    createdAt: '2024-01-15T10:30:00Z'
  },
  {
    id: 2,
    name: 'Verification Code',
    description: 'Two-factor authentication code',
    type: 'Security',
    language: 'English',
    status: 'active',
    usageCount: 567,
    createdAt: '2024-01-10T09:15:00Z'
  },
  {
    id: 3,
    name: 'Order Confirmation',
    description: 'Order confirmation SMS',
    type: 'E-commerce',
    language: 'English',
    status: 'active',
    usageCount: 890,
    createdAt: '2024-01-05T11:20:00Z'
  },
  {
    id: 4,
    name: 'Appointment Reminder',
    description: 'Appointment reminder SMS',
    type: 'Notification',
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
const loadSMSData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/sms')
    // if (response.success) {
    //   services.value = response.services || []
    //   templates.value = response.templates || []
    //   Object.assign(smsStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading SMS data:', error)
    showError('Failed to load SMS data')
  } finally {
    loading.value = false
  }
}

const filterServices = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (serviceFilter.value) {
    return 'No SMS services match your filter criteria'
  }
  return 'No SMS services found'
}

const getServiceIcon = (provider) => {
  const icons = {
    'Twilio': 'fab fa-twilio',
    'Nexmo': 'fas fa-comment-dots',
    'Plivo': 'fas fa-comment',
    'MessageBird': 'fas fa-comment-alt',
    'Clickatell': 'fas fa-comment-alt',
    'Vonage': 'fas fa-comment'
  }
  return icons[provider] || 'fas fa-comment'
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
    // const response = await apiPost(`/sms/services/${service.id}/test`)
    // if (response.success) {
    //   showSuccess('Test SMS sent successfully')
    // }
    
    // For demo, simulate test
    showSuccess('Test SMS sent successfully')
  } catch (error) {
    console.error('Error testing service:', error)
    showError('Failed to send test SMS')
  }
}

const configureService = (service) => {
  // Open service configuration modal or navigate to detailed view
  showSuccess(`Opening configuration for ${service.name}`)
}

const toggleService = async (service) => {
  try {
    // const response = await apiPut(`/sms/services/${service.id}/toggle`)
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
    // const response = await apiPost(`/sms/templates/${template.id}/duplicate`)
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
    // const response = await apiDelete(`/sms/templates/${template.id}`)
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

const sendSMS = async () => {
  if (!smsForm.phoneNumber || !smsForm.message) {
    showError('Please fill in all required fields')
    return
  }

  if (smsForm.message.length > 160) {
    showError('Message exceeds 160 character limit')
    return
  }

  try {
    // const response = await apiPost('/sms/send', smsForm)
    // if (response.success) {
    //   showSuccess('SMS sent successfully')
    //   closeComposeModal()
    //   resetSMSForm()
    // }
    
    // For demo, simulate send
    showSuccess('SMS sent successfully')
    closeComposeModal()
    resetSMSForm()
  } catch (error) {
    console.error('Error sending SMS:', error)
    showError('Failed to send SMS')
  }
}

const testSMS = async () => {
  if (!testForm.serviceId || !testForm.phoneNumber) {
    showError('Please fill in all required fields')
    return
  }

  if (testForm.message.length > 160) {
    showError('Message exceeds 160 character limit')
    return
  }

  try {
    // const response = await apiPost('/sms/test', testForm)
    // if (response.success) {
    //   showSuccess('Test SMS sent successfully')
    //   closeTestModal()
    //   resetTestForm()
    // }
    
    // For demo, simulate test
    showSuccess('Test SMS sent successfully')
    closeTestModal()
    resetTestForm()
  } catch (error) {
    console.error('Error sending test SMS:', error)
    showError('Failed to send test SMS')
  }
}

const closeComposeModal = () => {
  showComposeModal.value = false
  resetSMSForm()
}

const closeTestModal = () => {
  showTestModal.value = false
  resetTestForm()
}

const resetSMSForm = () => {
  Object.assign(smsForm, {
    phoneNumber: '',
    countryCode: '+1',
    message: '',
    templateId: '',
    schedule: 'immediate',
    scheduledTime: '',
    trackDelivery: true,
    priority: false,
    flash: false
  })
}

const resetTestForm = () => {
  Object.assign(testForm, {
    serviceId: '',
    phoneNumber: '',
    message: 'This is a test SMS to verify the SMS service configuration.'
  })
}

// Lifecycle
onMounted(() => {
  loadSMSData()
})
</script>

<style scoped>
.sms {
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

.sms-form,
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

.character-count {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: right;
  margin-top: 0.25rem;
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
  .sms {
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
