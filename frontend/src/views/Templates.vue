<template>
  <div class="templates">
    <div class="page-header">
      <h1>Templates</h1>
      <p>Create, manage, and use templates for your projects</p>
    </div>

    <!-- Template Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ templateStats.totalTemplates }}</h3>
            <p>Total Templates</p>
            <span class="template-count">{{ templateStats.myTemplates }} created by you</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon shared">
            <i class="fas fa-share-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ templateStats.sharedTemplates }}</h3>
            <p>Shared Templates</p>
            <span class="share-count">{{ templateStats.publicTemplates }} public</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon usage">
            <i class="fas fa-clone"></i>
          </div>
          <div class="card-content">
            <h3>{{ templateStats.totalUses }}</h3>
            <p>Total Uses</p>
            <span class="usage-count">{{ templateStats.thisMonth }} this month</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon categories">
            <i class="fas fa-folder"></i>
          </div>
          <div class="card-content">
            <h3>{{ templateStats.categories }}</h3>
            <p>Categories</p>
            <span class="category-count">{{ templateStats.activeCategories }} active</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="create-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Template
        </button>
        <button class="import-btn" @click="showImportModal = true">
          <i class="fas fa-upload"></i>
          Import Template
        </button>
        <button class="browse-btn" @click="showBrowseModal = true">
          <i class="fas fa-search"></i>
          Browse Templates
        </button>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="search-section">
      <div class="search-controls">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search templates..."
            @input="filterTemplates"
          />
        </div>
        <div class="filter-dropdown">
          <select v-model="categoryFilter" @change="filterTemplates">
            <option value="">All Categories</option>
            <option value="business">Business</option>
            <option value="marketing">Marketing</option>
            <option value="development">Development</option>
            <option value="design">Design</option>
            <option value="education">Education</option>
            <option value="personal">Personal</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="typeFilter" @change="filterTemplates">
            <option value="">All Types</option>
            <option value="document">Document</option>
            <option value="presentation">Presentation</option>
            <option value="spreadsheet">Spreadsheet</option>
            <option value="form">Form</option>
            <option value="email">Email</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="accessFilter" @change="filterTemplates">
            <option value="">All Access</option>
            <option value="private">Private</option>
            <option value="shared">Shared</option>
            <option value="public">Public</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Templates Grid -->
    <div class="templates-section">
      <div class="section-header">
        <h2>My Templates</h2>
        <div class="header-actions">
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
        <p>Loading templates...</p>
      </div>

      <div v-else-if="filteredTemplates.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-file-alt"></i>
        </div>
        <h3>No templates found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCreateModal = true">
          <i class="fas fa-plus"></i>
          Create Your First Template
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="templates-grid">
          <div 
            v-for="template in filteredTemplates" 
            :key="template.id"
            class="template-card"
            @click="viewTemplateDetails(template)"
          >
            <div class="template-header">
              <div class="template-preview">
                <div class="preview-icon">
                  <i :class="getTemplateIcon(template.type)"></i>
                </div>
                <div class="template-type">{{ template.type }}</div>
              </div>
              <div class="template-actions">
                <button 
                  class="action-btn favorite"
                  @click.stop="toggleFavorite(template)"
                  :class="{ 'active': template.isFavorite }"
                >
                  <i :class="template.isFavorite ? 'fas fa-heart' : 'far fa-heart'"></i>
                </button>
                <button 
                  class="action-btn more"
                  @click.stop="showTemplateMenu(template)"
                >
                  <i class="fas fa-ellipsis-v"></i>
                </button>
              </div>
            </div>

            <div class="template-content">
              <h3>{{ template.name }}</h3>
              <p>{{ template.description }}</p>
              
              <div class="template-meta">
                <span class="category">{{ template.category }}</span>
                <span class="access">{{ template.access }}</span>
                <span class="uses">{{ template.uses }} uses</span>
              </div>

              <div class="template-footer">
                <span class="created-date">{{ formatDate(template.created_at) }}</span>
                <button 
                  class="use-btn"
                  @click.stop="useTemplate(template)"
                >
                  <i class="fas fa-clone"></i>
                  Use Template
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="templates-list">
          <div 
            v-for="template in filteredTemplates" 
            :key="template.id"
            class="template-list-card"
            @click="viewTemplateDetails(template)"
          >
            <div class="template-list-header">
              <div class="template-preview">
                <div class="preview-icon">
                  <i :class="getTemplateIcon(template.type)"></i>
                </div>
                <div class="template-info">
                  <h3>{{ template.name }}</h3>
                  <p>{{ template.description }}</p>
                  <div class="template-meta">
                    <span class="category">{{ template.category }}</span>
                    <span class="type">{{ template.type }}</span>
                    <span class="access">{{ template.access }}</span>
                    <span class="uses">{{ template.uses }} uses</span>
                  </div>
                </div>
              </div>
              <div class="template-list-actions">
                <button 
                  class="action-btn favorite"
                  @click.stop="toggleFavorite(template)"
                  :class="{ 'active': template.isFavorite }"
                >
                  <i :class="template.isFavorite ? 'fas fa-heart' : 'far fa-heart'"></i>
                </button>
                <button 
                  class="use-btn"
                  @click.stop="useTemplate(template)"
                >
                  <i class="fas fa-clone"></i>
                  Use
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Template Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Create New Template</h2>
          <button class="close-btn" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="template-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Template Name *</label>
                <input 
                  v-model="templateForm.name" 
                  type="text" 
                  placeholder="Enter template name"
                  required
                />
              </div>

              <div class="form-group">
                <label>Category *</label>
                <select v-model="templateForm.category" required>
                  <option value="">Select category</option>
                  <option value="business">Business</option>
                  <option value="marketing">Marketing</option>
                  <option value="development">Development</option>
                  <option value="design">Design</option>
                  <option value="education">Education</option>
                  <option value="personal">Personal</option>
                </select>
              </div>

              <div class="form-group">
                <label>Type *</label>
                <select v-model="templateForm.type" required>
                  <option value="">Select type</option>
                  <option value="document">Document</option>
                  <option value="presentation">Presentation</option>
                  <option value="spreadsheet">Spreadsheet</option>
                  <option value="form">Form</option>
                  <option value="email">Email</option>
                </select>
              </div>

              <div class="form-group">
                <label>Access Level</label>
                <select v-model="templateForm.access">
                  <option value="private">Private</option>
                  <option value="shared">Shared</option>
                  <option value="public">Public</option>
                </select>
              </div>
            </div>

            <div class="form-group full-width">
              <label>Description</label>
              <textarea 
                v-model="templateForm.description" 
                placeholder="Describe your template"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group full-width">
              <label>Tags</label>
              <input 
                v-model="templateForm.tags" 
                type="text" 
                placeholder="Enter tags separated by commas"
              />
            </div>

            <div class="form-group full-width">
              <label>Template Content</label>
              <div class="editor-container">
                <textarea 
                  v-model="templateForm.content" 
                  placeholder="Enter your template content here..."
                  rows="10"
                  class="template-editor"
                ></textarea>
              </div>
            </div>

            <div class="form-group full-width">
              <label>Variables (Optional)</label>
              <div class="variables-container">
                <div 
                  v-for="(variable, index) in templateForm.variables" 
                  :key="index"
                  class="variable-item"
                >
                  <input 
                    v-model="variable.name" 
                    type="text" 
                    placeholder="Variable name"
                  />
                  <input 
                    v-model="variable.defaultValue" 
                    type="text" 
                    placeholder="Default value"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeVariable(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-variable-btn" @click="addVariable">
                  <i class="fas fa-plus"></i>
                  Add Variable
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCreateModal">Cancel</button>
          <button 
            class="btn-primary" 
            @click="createTemplate"
            :disabled="creating"
          >
            <span v-if="!creating">Create Template</span>
            <span v-else>Creating...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Template Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <div class="template-header-info">
            <div class="template-preview large">
              <div class="preview-icon">
                <i :class="getTemplateIcon(selectedTemplate?.type)"></i>
              </div>
              <div class="template-details">
                <h2>{{ selectedTemplate?.name }}</h2>
                <p>{{ selectedTemplate?.description }}</p>
                <div class="template-meta-info">
                  <span class="category">{{ selectedTemplate?.category }}</span>
                  <span class="type">{{ selectedTemplate?.type }}</span>
                  <span class="access">{{ selectedTemplate?.access }}</span>
                  <span class="uses">{{ selectedTemplate?.uses }} uses</span>
                </div>
              </div>
            </div>
          </div>
          <button class="close-btn" @click="closeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="details-content">
            <div class="details-section">
              <h3>Content Preview</h3>
              <div class="content-preview">
                <pre>{{ selectedTemplate?.content }}</pre>
              </div>
            </div>

            <div class="details-section" v-if="selectedTemplate?.variables?.length">
              <h3>Template Variables</h3>
              <div class="variables-list">
                <div 
                  v-for="variable in selectedTemplate.variables" 
                  :key="variable.name"
                  class="variable-item"
                >
                  <div class="variable-name">{{ variable.name }}</div>
                  <div class="variable-value">{{ variable.defaultValue }}</div>
                </div>
              </div>
            </div>

            <div class="details-section" v-if="selectedTemplate?.tags">
              <h3>Tags</h3>
              <div class="tags-list">
                <span 
                  v-for="tag in selectedTemplate.tags.split(',')" 
                  :key="tag"
                  class="tag"
                >
                  {{ tag.trim() }}
                </span>
              </div>
            </div>

            <div class="details-section">
              <h3>Statistics</h3>
              <div class="stats-grid">
                <div class="stat-item">
                  <label>Created:</label>
                  <span>{{ formatDateTime(selectedTemplate?.created_at) }}</span>
                </div>
                <div class="stat-item">
                  <label>Last Modified:</label>
                  <span>{{ formatDateTime(selectedTemplate?.updated_at) }}</span>
                </div>
                <div class="stat-item">
                  <label>Total Uses:</label>
                  <span>{{ selectedTemplate?.uses }}</span>
                </div>
                <div class="stat-item">
                  <label>Created By:</label>
                  <span>{{ selectedTemplate?.created_by }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div class="footer-actions">
            <button class="btn-secondary" @click="closeDetailsModal">Close</button>
            <button class="btn-secondary" @click="editTemplate(selectedTemplate)">
              <i class="fas fa-edit"></i>
              Edit
            </button>
            <button class="btn-primary" @click="useTemplate(selectedTemplate)">
              <i class="fas fa-clone"></i>
              Use Template
            </button>
          </div>
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
const creating = ref(false)
const searchQuery = ref('')
const categoryFilter = ref('')
const typeFilter = ref('')
const accessFilter = ref('')
const viewMode = ref('grid')
const showCreateModal = ref(false)
const showDetailsModal = ref(false)
const showImportModal = ref(false)
const showBrowseModal = ref(false)
const selectedTemplate = ref(null)

// Template stats
const templateStats = reactive({
  totalTemplates: 24,
  myTemplates: 18,
  sharedTemplates: 6,
  publicTemplates: 3,
  totalUses: 156,
  thisMonth: 23,
  categories: 6,
  activeCategories: 5
})

// Template form
const templateForm = reactive({
  name: '',
  description: '',
  category: '',
  type: '',
  access: 'private',
  tags: '',
  content: '',
  variables: []
})

// Mock data
const templates = ref([
  {
    id: 1,
    name: 'Business Proposal',
    description: 'Professional business proposal template',
    category: 'business',
    type: 'document',
    access: 'shared',
    uses: 45,
    isFavorite: true,
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-20T14:20:00Z',
    created_by: 'John Doe',
    content: 'Business Proposal Template Content...',
    tags: 'business, proposal, professional',
    variables: [
      { name: 'company_name', defaultValue: 'Your Company' },
      { name: 'client_name', defaultValue: 'Client Name' },
      { name: 'project_name', defaultValue: 'Project Name' }
    ]
  },
  {
    id: 2,
    name: 'Marketing Email Campaign',
    description: 'Email marketing campaign template',
    category: 'marketing',
    type: 'email',
    access: 'public',
    uses: 89,
    isFavorite: false,
    created_at: '2024-01-10T09:15:00Z',
    updated_at: '2024-01-18T16:45:00Z',
    created_by: 'Jane Smith',
    content: 'Email Marketing Template Content...',
    tags: 'marketing, email, campaign',
    variables: [
      { name: 'subject', defaultValue: 'Special Offer' },
      { name: 'company', defaultValue: 'Your Company' },
      { name: 'offer', defaultValue: '50% Off' }
    ]
  },
  {
    id: 3,
    name: 'Project Report',
    description: 'Comprehensive project report template',
    category: 'development',
    type: 'document',
    access: 'private',
    uses: 12,
    isFavorite: true,
    created_at: '2024-01-05T11:20:00Z',
    updated_at: '2024-01-22T13:30:00Z',
    created_by: 'Mike Johnson',
    content: 'Project Report Template Content...',
    tags: 'project, report, development',
    variables: [
      { name: 'project_name', defaultValue: 'Project Name' },
      { name: 'team', defaultValue: 'Development Team' },
      { name: 'status', defaultValue: 'In Progress' }
    ]
  },
  {
    id: 4,
    name: 'Invoice Template',
    description: 'Professional invoice template',
    category: 'business',
    type: 'document',
    access: 'shared',
    uses: 67,
    isFavorite: false,
    created_at: '2023-12-20T15:45:00Z',
    updated_at: '2024-01-15T10:10:00Z',
    created_by: 'Sarah Wilson',
    content: 'Invoice Template Content...',
    tags: 'invoice, billing, finance',
    variables: [
      { name: 'invoice_number', defaultValue: 'INV-001' },
      { name: 'client', defaultValue: 'Client Name' },
      { name: 'amount', defaultValue: '0.00' }
    ]
  }
])

// Computed properties
const filteredTemplates = computed(() => {
  let filtered = templates.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(template => 
      template.name.toLowerCase().includes(query) ||
      template.description.toLowerCase().includes(query) ||
      template.tags.toLowerCase().includes(query)
    )
  }

  // Apply category filter
  if (categoryFilter.value) {
    filtered = filtered.filter(template => template.category === categoryFilter.value)
  }

  // Apply type filter
  if (typeFilter.value) {
    filtered = filtered.filter(template => template.type === typeFilter.value)
  }

  // Apply access filter
  if (accessFilter.value) {
    filtered = filtered.filter(template => template.access === accessFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

// Methods
const loadTemplates = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/templates')
    // if (response.success) {
    //   templates.value = response.templates || []
    //   templateStats.totalTemplates = response.stats.totalTemplates
    //   templateStats.myTemplates = response.stats.myTemplates
    //   templateStats.sharedTemplates = response.stats.sharedTemplates
    //   templateStats.publicTemplates = response.stats.publicTemplates
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading templates:', error)
    showError('Failed to load templates')
  } finally {
    loading.value = false
  }
}

const filterTemplates = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (searchQuery.value || categoryFilter.value || typeFilter.value || accessFilter.value) {
    return 'No templates match your search criteria'
  }
  return 'No templates found'
}

const getTemplateIcon = (type) => {
  const icons = {
    'document': 'fas fa-file-alt',
    'presentation': 'fas fa-file-powerpoint',
    'spreadsheet': 'fas fa-file-excel',
    'form': 'fas fa-file-alt',
    'email': 'fas fa-envelope'
  }
  return icons[type] || 'fas fa-file-alt'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const viewTemplateDetails = (template) => {
  selectedTemplate.value = template
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedTemplate.value = null
}

const toggleFavorite = async (template) => {
  try {
    // const response = await apiPut(`/templates/${template.id}/favorite`)
    // if (response.success) {
    //   template.isFavorite = !template.isFavorite
    //   showSuccess(template.isFavorite ? 'Added to favorites' : 'Removed from favorites')
    // }
    
    // For demo, simulate toggle
    template.isFavorite = !template.isFavorite
    showSuccess(template.isFavorite ? 'Added to favorites' : 'Removed from favorites')
  } catch (error) {
    console.error('Error toggling favorite:', error)
    showError('Failed to update favorites')
  }
}

const showTemplateMenu = (template) => {
  // Show context menu for template actions
  showSuccess(`Menu for ${template.name}`)
}

const useTemplate = async (template) => {
  try {
    // const response = await apiPost(`/templates/${template.id}/use`)
    // if (response.success) {
    //   template.uses++
    //   showSuccess('Template used successfully')
    // }
    
    // For demo, simulate use
    template.uses++
    showSuccess('Template used successfully')
  } catch (error) {
    console.error('Error using template:', error)
    showError('Failed to use template')
  }
}

const createTemplate = async () => {
  if (!templateForm.name || !templateForm.category || !templateForm.type) {
    showError('Please fill in all required fields')
    return
  }

  creating.value = true
  try {
    // const response = await apiPost('/templates', templateForm)
    // if (response.success) {
    //   templates.value.unshift(response.template)
    //   showSuccess('Template created successfully')
    //   closeCreateModal()
    // }
    
    // For demo, simulate creation
    const newTemplate = {
      id: Date.now(),
      ...templateForm,
      uses: 0,
      isFavorite: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: 'Current User'
    }
    
    templates.value.unshift(newTemplate)
    showSuccess('Template created successfully')
    closeCreateModal()
  } catch (error) {
    console.error('Error creating template:', error)
    showError('Failed to create template')
  } finally {
    creating.value = false
  }
}

const editTemplate = (template) => {
  // Populate form with template data
  Object.assign(templateForm, {
    name: template.name,
    description: template.description,
    category: template.category,
    type: template.type,
    access: template.access,
    tags: template.tags,
    content: template.content,
    variables: [...template.variables]
  })
  
  showCreateModal.value = true
}

const addVariable = () => {
  templateForm.variables.push({ name: '', defaultValue: '' })
}

const removeVariable = (index) => {
  templateForm.variables.splice(index, 1)
}

const closeCreateModal = () => {
  showCreateModal.value = false
  resetTemplateForm()
}

const resetTemplateForm = () => {
  Object.assign(templateForm, {
    name: '',
    description: '',
    category: '',
    type: '',
    access: 'private',
    tags: '',
    content: '',
    variables: []
  })
}

// Lifecycle
onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.templates {
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

.card-icon.shared {
  background: var(--success-color);
}

.card-icon.usage {
  background: var(--warning-color);
}

.card-icon.categories {
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

.template-count,
.share-count,
.usage-count,
.category-count {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.template-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.share-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.usage-count {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.category-count {
  background: rgba(6, 182, 212, 0.1);
  color: #06b6d4;
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

.create-btn,
.import-btn,
.browse-btn {
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

.create-btn:hover,
.import-btn:hover,
.browse-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.import-btn {
  background: var(--success-color);
}

.import-btn:hover {
  background: var(--success-hover);
}

.browse-btn {
  background: var(--info-color);
}

.browse-btn:hover {
  background: var(--info-hover);
}

.search-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.search-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  font-size: 1.1rem;
}

.search-box input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
}

.filter-dropdown select {
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
  cursor: pointer;
  min-width: 150px;
}

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
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.template-preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-icon {
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

.preview-icon.large {
  width: 80px;
  height: 80px;
  font-size: 1.5rem;
}

.template-type {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  background: var(--glass-bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.favorite.active {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.template-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.template-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.template-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.category,
.type,
.access,
.uses {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.template-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.created-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.use-btn {
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

.use-btn:hover {
  background: var(--primary-hover);
}

.templates-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.template-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-list-card:hover {
  background: var(--glass-bg-hover);
}

.template-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.template-list-content {
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
}

.template-list-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.template-list-actions {
  display: flex;
  gap: 0.5rem;
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
  max-width: 1000px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1200px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 2rem;
  border-bottom: 1px solid var(--glass-border);
}

.template-header-info {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.template-details h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.8rem;
}

.template-details p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.template-meta-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
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

.template-form {
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

.form-group.full-width {
  grid-column: 1 / -1;
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

.template-editor {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.variables-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.variable-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.variable-item input {
  flex: 1;
}

.remove-btn {
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
}

.remove-btn:hover {
  background: var(--danger-hover);
}

.add-variable-btn {
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
  align-self: flex-start;
}

.add-variable-btn:hover {
  background: var(--primary-hover);
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.details-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.content-preview {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
}

.content-preview pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.variables-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.variable-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.variable-name {
  font-weight: 600;
  color: var(--text-primary);
}

.variable-value {
  color: var(--text-secondary);
  font-family: 'Courier New', monospace;
}

.tags-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  padding: 0.25rem 0.75rem;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.stat-item label {
  font-weight: 600;
  color: var(--text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

.footer-actions {
  display: flex;
  gap: 1rem;
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

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  .templates {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-box {
    min-width: 100%;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .template-header-info {
    flex-direction: column;
    gap: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
