<template>
  <div class="documentation">
    <div class="page-header">
      <h1>Documentation Center</h1>
      <p>Comprehensive documentation and guides for the platform</p>
    </div>

    <!-- Search and Navigation -->
    <div class="search-section">
      <div class="search-container">
        <div class="search-input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search documentation..."
            @input="searchDocumentation"
            class="search-input"
          />
        </div>
        <div class="search-filters">
          <select v-model="searchCategory" @change="searchDocumentation">
            <option value="">All Categories</option>
            <option value="getting-started">Getting Started</option>
            <option value="api">API Reference</option>
            <option value="guides">Guides</option>
            <option value="tutorials">Tutorials</option>
            <option value="examples">Examples</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Quick Links -->
    <div class="quick-links-section">
      <div class="section-header">
        <h2>Quick Links</h2>
      </div>
      <div class="quick-links-grid">
        <div 
          v-for="link in quickLinks" 
          :key="link.id"
          class="quick-link-card"
          @click="navigateToSection(link.section)"
        >
          <div class="quick-link-icon">
            <i :class="link.icon"></i>
          </div>
          <div class="quick-link-content">
            <h3>{{ link.title }}</h3>
            <p>{{ link.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Documentation Content -->
    <div class="content-section">
      <div class="section-header">
        <h2>Documentation</h2>
        <div class="header-actions">
          <div class="view-toggle">
            <button 
              :class="['view-btn', { active: viewMode === 'tree' }]"
              @click="viewMode = 'tree'"
            >
              <i class="fas fa-sitemap"></i>
              Tree View
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'list' }]"
              @click="viewMode = 'list'"
            >
              <i class="fas fa-list"></i>
              List View
            </button>
          </div>
          <button class="expand-all-btn" @click="toggleExpandAll">
            <i class="fas fa-expand-alt"></i>
            {{ allExpanded ? 'Collapse All' : 'Expand All' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading documentation...</p>
      </div>

      <div v-else-if="filteredDocs.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-book"></i>
        </div>
        <h3>No documentation found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else>
        <!-- Tree View -->
        <div v-if="viewMode === 'tree'" class="tree-view">
          <div 
            v-for="category in filteredDocs" 
            :key="category.id"
            class="doc-category"
          >
            <div class="category-header" @click="toggleCategory(category.id)">
              <div class="category-icon">
                <i :class="category.icon"></i>
              </div>
              <h3>{{ category.title }}</h3>
              <div class="category-toggle">
                <i :class="['fas', expandedCategories.includes(category.id) ? 'fa-chevron-up' : 'fa-chevron-down']"></i>
              </div>
            </div>
            
            <div v-if="expandedCategories.includes(category.id)" class="category-content">
              <div class="category-description">
                <p>{{ category.description }}</p>
              </div>
              
              <div class="topics-list">
                <div 
                  v-for="topic in category.topics" 
                  :key="topic.id"
                  class="topic-item"
                >
                  <div class="topic-header" @click="toggleTopic(topic.id)">
                    <h4>{{ topic.title }}</h4>
                    <div class="topic-toggle">
                      <i :class="['fas', expandedTopics.includes(topic.id) ? 'fa-chevron-up' : 'fa-chevron-down']"></i>
                    </div>
                  </div>
                  
                  <div v-if="expandedTopics.includes(topic.id)" class="topic-content">
                    <div class="topic-description">
                      <p>{{ topic.description }}</p>
                    </div>
                    
                    <div class="sections-list">
                      <div 
                        v-for="section in topic.sections" 
                        :key="section.id"
                        class="section-item"
                        @click="openDocument(section)"
                      >
                        <div class="section-info">
                          <h5>{{ section.title }}</h5>
                          <p>{{ section.description }}</p>
                          <div class="section-meta">
                            <span class="section-type">{{ section.type }}</span>
                            <span class="section-read-time">{{ section.readTime }} min read</span>
                          </div>
                        </div>
                        <div class="section-actions">
                          <i class="fas fa-arrow-right"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="list-view">
          <div class="docs-list">
            <div 
              v-for="doc in allDocsFlat" 
              :key="doc.id"
              class="doc-item"
              @click="openDocument(doc)"
            >
              <div class="doc-icon">
                <i :class="doc.icon"></i>
              </div>
              <div class="doc-content">
                <h3>{{ doc.title }}</h3>
                <p>{{ doc.description }}</p>
                <div class="doc-meta">
                  <span class="doc-category">{{ doc.category }}</span>
                  <span class="doc-type">{{ doc.type }}</span>
                  <span class="doc-read-time">{{ doc.readTime }} min read</span>
                </div>
              </div>
              <div class="doc-actions">
                <i class="fas fa-arrow-right"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Updates -->
    <div class="updates-section">
      <div class="section-header">
        <h2>Recent Updates</h2>
        <div class="header-actions">
          <button class="refresh-btn" @click="refreshUpdates">
            <i class="fas fa-sync"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="updates-list">
        <div 
          v-for="update in recentUpdates" 
          :key="update.id"
          class="update-item"
        >
          <div class="update-header">
            <div class="update-type">
              <span :class="['type-badge', update.type]">{{ update.type }}</span>
            </div>
            <div class="update-date">{{ formatDate(update.date) }}</div>
          </div>
          
          <div class="update-content">
            <h4>{{ update.title }}</h4>
            <p>{{ update.description }}</p>
          </div>
          
          <div class="update-actions">
            <button class="action-btn view" @click="viewUpdate(update)">
              <i class="fas fa-eye"></i>
              View
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Document Viewer Modal -->
    <div v-if="showDocumentModal" class="modal-overlay" @click="closeDocumentModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedDocument?.title }}</h2>
          <button class="close-btn" @click="closeDocumentModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="document-viewer">
            <div class="document-meta">
              <div class="meta-item">
                <label>Category:</label>
                <span>{{ selectedDocument?.category }}</span>
              </div>
              <div class="meta-item">
                <label>Type:</label>
                <span>{{ selectedDocument?.type }}</span>
              </div>
              <div class="meta-item">
                <label>Last Updated:</label>
                <span>{{ formatDateTime(selectedDocument?.lastUpdated) }}</span>
              </div>
              <div class="meta-item">
                <label>Read Time:</label>
                <span>{{ selectedDocument?.readTime }} minutes</span>
              </div>
            </div>
            
            <div class="document-content">
              <div v-html="selectedDocument?.content"></div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div class="footer-actions">
            <button class="action-btn bookmark" @click="bookmarkDocument">
              <i class="fas fa-bookmark"></i>
              Bookmark
            </button>
            <button class="action-btn share" @click="shareDocument">
              <i class="fas fa-share"></i>
              Share
            </button>
            <button class="action-btn download" @click="downloadDocument">
              <i class="fas fa-download"></i>
              Download
            </button>
            <button class="action-btn print" @click="printDocument">
              <i class="fas fa-print"></i>
              Print
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
const searchQuery = ref('')
const searchCategory = ref('')
const viewMode = ref('tree')
const loading = ref(false)
const showDocumentModal = ref(false)
const selectedDocument = ref(null)

// UI state
const expandedCategories = ref([])
const expandedTopics = ref([])
const allExpanded = ref(false)

// Documentation data
const documentation = ref([
  {
    id: 1,
    title: 'Getting Started',
    description: 'Learn the basics and get up and running quickly',
    icon: 'fas fa-rocket',
    topics: [
      {
        id: 11,
        title: 'Installation',
        description: 'Step-by-step installation guide',
        sections: [
          {
            id: 111,
            title: 'System Requirements',
            description: 'Minimum system requirements for installation',
            type: 'Guide',
            readTime: 5,
            content: '<h3>System Requirements</h3><p>Before installing the application, ensure your system meets the following requirements:</p><ul><li>Operating System: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)</li><li>RAM: Minimum 4GB, recommended 8GB</li><li>Storage: At least 2GB of free disk space</li><li>Node.js: Version 14.0 or higher</li></ul>'
          },
          {
            id: 112,
            title: 'Quick Start',
            description: 'Get started in minutes',
            type: 'Tutorial',
            readTime: 10,
            content: '<h3>Quick Start Guide</h3><p>Follow these steps to get started quickly:</p><ol><li>Clone the repository</li><li>Install dependencies</li><li>Configure environment variables</li><li>Run the development server</li></ol>'
          }
        ]
      },
      {
        id: 12,
        title: 'Configuration',
        description: 'Configure your development environment',
        sections: [
          {
            id: 121,
            title: 'Environment Setup',
            description: 'Set up your development environment',
            type: 'Configuration',
            readTime: 8,
            content: '<h3>Environment Setup</h3><p>Configure your development environment with these settings:</p><pre><code>export NODE_ENV=development\nexport PORT=3000\nexport DATABASE_URL=postgresql://localhost:5432/myapp</code></pre>'
          }
        ]
      }
    ]
  },
  {
    id: 2,
    title: 'API Reference',
    description: 'Complete API documentation and examples',
    icon: 'fas fa-code',
    topics: [
      {
        id: 21,
        title: 'Authentication',
        description: 'Authentication endpoints and usage',
        sections: [
          {
            id: 211,
            title: 'Login Endpoint',
            description: 'User authentication endpoint',
            type: 'API',
            readTime: 5,
            content: '<h3>Login Endpoint</h3><p>POST /api/auth/login</p><h4>Request Body:</h4><pre><code>{\n  "email": "user@example.com",\n  "password": "password123"\n}</code></pre><h4>Response:</h4><pre><code>{\n  "token": "jwt_token_here",\n  "user": { "id": 1, "name": "John Doe" }\n}</code></pre>'
          }
        ]
      },
      {
        id: 22,
        title: 'Users',
        description: 'User management endpoints',
        sections: [
          {
            id: 221,
            title: 'Get Users',
            description: 'Retrieve user list',
            type: 'API',
            readTime: 3,
            content: '<h3>Get Users</h3><p>GET /api/users</p><h4>Parameters:</h4><ul><li><strong>page</strong>: Page number (default: 1)</li><li><strong>limit</strong>: Items per page (default: 10)</li></ul>'
          }
        ]
      }
    ]
  },
  {
    id: 3,
    title: 'Guides',
    description: 'Step-by-step guides for common tasks',
    icon: 'fas fa-book',
    topics: [
      {
        id: 31,
        title: 'Deployment',
        description: 'Deploy your application',
        sections: [
          {
            id: 311,
            title: 'Production Deployment',
            description: 'Deploy to production environment',
            type: 'Guide',
            readTime: 15,
            content: '<h3>Production Deployment</h3><p>Follow this comprehensive guide to deploy your application to production:</p><ol><li>Build your application</li><li>Run tests</li><li>Configure production environment</li><li>Deploy to your hosting provider</li><li>Monitor deployment</li></ol>'
          }
        ]
      }
    ]
  }
])

// Quick links
const quickLinks = ref([
  {
    id: 1,
    title: 'Getting Started',
    description: 'New to the platform? Start here',
    icon: 'fas fa-rocket',
    section: 'getting-started'
  },
  {
    id: 2,
    title: 'API Reference',
    description: 'Complete API documentation',
    icon: 'fas fa-code',
    section: 'api'
  },
  {
    id: 3,
    title: 'Tutorials',
    description: 'Step-by-step tutorials',
    icon: 'fas fa-graduation-cap',
    section: 'tutorials'
  },
  {
    id: 4,
    title: 'Examples',
    description: 'Code examples and samples',
    icon: 'fas fa-flask',
    section: 'examples'
  }
])

// Recent updates
const recentUpdates = ref([
  {
    id: 1,
    type: 'new',
    title: 'New Authentication Guide',
    description: 'Comprehensive guide for implementing authentication',
    date: '2024-01-21T10:00:00Z'
  },
  {
    id: 2,
    type: 'updated',
    title: 'API Documentation Updated',
    description: 'Added new endpoints and updated existing ones',
    date: '2024-01-20T15:30:00Z'
  },
  {
    id: 3,
    type: 'fixed',
    title: 'Fixed Broken Links',
    description: 'Resolved broken documentation links',
    date: '2024-01-19T09:15:00Z'
  }
])

// Computed properties
const filteredDocs = computed(() => {
  let filtered = documentation.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(category => 
      category.title.toLowerCase().includes(query) ||
      category.description.toLowerCase().includes(query) ||
      category.topics.some(topic => 
        topic.title.toLowerCase().includes(query) ||
        topic.description.toLowerCase().includes(query)
      )
    )
  }

  if (searchCategory.value) {
    filtered = filtered.filter(category => category.title.toLowerCase().includes(searchCategory.value.toLowerCase()))
  }

  return filtered
})

const allDocsFlat = computed(() => {
  const flat = []
  documentation.value.forEach(category => {
    category.topics.forEach(topic => {
      topic.sections.forEach(section => {
        flat.push({
          ...section,
          category: category.title,
          icon: category.icon
        })
      })
    })
  })
  return flat
})

// Methods
const searchDocumentation = () => {
  // Search is handled by computed property
}

const navigateToSection = (section) => {
  searchCategory.value = section
  searchQuery.value = ''
}

const toggleCategory = (categoryId) => {
  const index = expandedCategories.value.indexOf(categoryId)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
  } else {
    expandedCategories.value.push(categoryId)
  }
}

const toggleTopic = (topicId) => {
  const index = expandedTopics.value.indexOf(topicId)
  if (index > -1) {
    expandedTopics.value.splice(index, 1)
  } else {
    expandedTopics.value.push(topicId)
  }
}

const toggleExpandAll = () => {
  if (allExpanded.value) {
    expandedCategories.value = []
    expandedTopics.value = []
  } else {
    const allCategoryIds = documentation.value.map(cat => cat.id)
    const allTopicIds = []
    documentation.value.forEach(cat => {
      cat.topics.forEach(topic => {
        allTopicIds.push(topic.id)
      })
    })
    expandedCategories.value = allCategoryIds
    expandedTopics.value = allTopicIds
  }
  allExpanded.value = !allExpanded.value
}

const openDocument = (doc) => {
  selectedDocument.value = doc
  showDocumentModal.value = true
}

const closeDocumentModal = () => {
  showDocumentModal.value = false
  selectedDocument.value = null
}

const bookmarkDocument = async () => {
  try {
    // const response = await apiPost('/documentation/bookmark', {
    //   documentId: selectedDocument.value.id
    // })
    // if (response.success) {
    //   showSuccess('Document bookmarked successfully')
    // }
    
    // For demo, simulate bookmark
    showSuccess('Document bookmarked successfully')
  } catch (error) {
    console.error('Error bookmarking document:', error)
    showError('Failed to bookmark document')
  }
}

const shareDocument = async () => {
  try {
    // const response = await apiPost('/documentation/share', {
    //   documentId: selectedDocument.value.id
    // })
    // if (response.success) {
    //   navigator.clipboard.writeText(response.shareUrl)
    //   showSuccess('Document shared! URL copied to clipboard')
    // }
    
    // For demo, simulate share
    const shareUrl = `https://docs.example.com/doc/${selectedDocument.value.id}`
    navigator.clipboard.writeText(shareUrl)
    showSuccess('Document shared! URL copied to clipboard')
  } catch (error) {
    console.error('Error sharing document:', error)
    showError('Failed to share document')
  }
}

const downloadDocument = () => {
  if (selectedDocument.value) {
    const content = selectedDocument.value.content.replace(/<[^>]*>/g, '')
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${selectedDocument.value.title}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    showSuccess('Document downloaded successfully')
  }
}

const printDocument = () => {
  if (selectedDocument.value) {
    const printWindow = window.open('', '_blank')
    printWindow.document.write(`
      <html>
        <head>
          <title>${selectedDocument.value.title}</title>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1, h2, h3, h4, h5 { color: #333; }
            code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
          </style>
        </head>
        <body>
          ${selectedDocument.value.content}
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
    
    showSuccess('Print dialog opened')
  }
}

const viewUpdate = (update) => {
  // Navigate to update details or open modal
  showSuccess(`Viewing update: ${update.title}`)
}

const refreshUpdates = async () => {
  try {
    // const response = await apiGet('/documentation/updates')
    // if (response.success) {
    //   recentUpdates.value = response.updates
    //   showSuccess('Updates refreshed successfully')
    // }
    
    // For demo, simulate refresh
    showSuccess('Updates refreshed successfully')
  } catch (error) {
    console.error('Error refreshing updates:', error)
    showError('Failed to refresh updates')
  }
}

const getEmptyMessage = () => {
  if (searchQuery.value || searchCategory.value) {
    return 'No documentation matches your search criteria'
  }
  return 'No documentation found'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/documentation')
    // if (response.success) {
    //   documentation.value = response.documentation || []
    //   recentUpdates.value = response.updates || []
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading documentation:', error)
    showError('Failed to load documentation')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.documentation {
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

.search-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.search-container {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-secondary);
  font-size: 1rem;
}

.search-input {
  flex: 1;
  padding: 1rem 1rem 1rem 3rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  outline: none;
}

.search-input:focus {
  border-color: var(--primary-color);
}

.search-filters select {
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.quick-links-section,
.content-section,
.updates-section {
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

.expand-all-btn,
.refresh-btn {
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

.expand-all-btn:hover,
.refresh-btn:hover {
  background: var(--primary-hover);
}

.quick-links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.quick-link-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.quick-link-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.quick-link-icon {
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

.quick-link-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.quick-link-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
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

.tree-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.doc-category {
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
  transition: transform 0.3s ease;
}

.category-description {
  padding: 0 1.5rem 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.category-description p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.topics-list {
  padding: 0 1.5rem 1.5rem;
}

.topic-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  margin-bottom: 1rem;
  overflow: hidden;
}

.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.topic-header:hover {
  background: var(--glass-bg-hover);
}

.topic-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.topic-toggle {
  color: var(--text-secondary);
}

.topic-content {
  padding: 0 1rem 1rem;
}

.topic-description {
  margin-bottom: 1rem;
}

.topic-description p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.sections-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.section-item {
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

.section-item:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
}

.section-info {
  flex: 1;
}

.section-info h5 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.section-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.section-meta {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.section-type {
  padding: 0.25rem 0.75rem;
  background: var(--info-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.section-read-time {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.section-actions {
  color: var(--primary-color);
  font-size: 1rem;
}

.list-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.docs-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.doc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.doc-item:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
}

.doc-icon {
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

.doc-content {
  flex: 1;
  margin-left: 1rem;
}

.doc-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.doc-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.doc-meta {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.doc-category,
.doc-type {
  padding: 0.25rem 0.75rem;
  background: var(--info-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.doc-read-time {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.doc-actions {
  color: var(--primary-color);
  font-size: 1rem;
}

.updates-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.update-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.update-item:hover {
  background: var(--glass-bg-hover);
}

.update-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.type-badge.new {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.type-badge.updated {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.type-badge.fixed {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.update-date {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.update-content h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.update-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.update-actions {
  margin-top: 1rem;
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
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
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

.document-viewer {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.document-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  padding: 1.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.meta-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.document-content {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 2rem;
  min-height: 400px;
  overflow-y: auto;
}

.document-content h1,
.document-content h2,
.document-content h3,
.document-content h4,
.document-content h5,
.document-content h6 {
  color: var(--text-primary);
  margin: 1rem 0;
}

.document-content p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 1rem 0;
}

.document-content code {
  background: var(--glass-bg-tertiary);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 0.9rem;
}

.document-content pre {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1rem 0;
}

.document-content ul,
.document-content ol {
  margin: 1rem 0;
  padding-left: 2rem;
}

.document-content li {
  margin: 0.5rem 0;
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

.action-btn.bookmark:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.share:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.download:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.print:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

@media (max-width: 768px) {
  .documentation {
    padding: 1rem;
  }
  
  .search-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .quick-links-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-link-card {
    flex-direction: column;
    text-align: center;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .doc-item {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .doc-content {
    margin-left: 0;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-content.large {
    max-width: 95%;
  }
  
  .document-meta {
    grid-template-columns: 1fr;
  }
  
  .footer-actions {
    flex-direction: column;
  }
}
</style>
