<template>
  <div class="changelog">
    <div class="page-header">
      <h1>Changelog</h1>
      <p>Track all updates, new features, and improvements</p>
    </div>

    <!-- Version Filter -->
    <div class="filter-section">
      <div class="filter-controls">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search changelog..."
            @input="filterChangelog"
          />
        </div>
        <div class="version-filter">
          <select v-model="selectedVersion" @change="filterChangelog">
            <option value="">All Versions</option>
            <option 
              v-for="version in availableVersions" 
              :key="version"
              :value="version"
            >
              {{ version }}
            </option>
          </select>
        </div>
        <div class="type-filter">
          <select v-model="selectedType" @change="filterChangelog">
            <option value="">All Types</option>
            <option value="feature">Features</option>
            <option value="improvement">Improvements</option>
            <option value="bugfix">Bug Fixes</option>
            <option value="security">Security</option>
            <option value="breaking">Breaking Changes</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Statistics -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-code-branch"></i>
        </div>
        <div class="stat-content">
          <h3>{{ changelogStats.totalVersions }}</h3>
          <p>Total Versions</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon feature">
          <i class="fas fa-star"></i>
        </div>
        <div class="stat-content">
          <h3>{{ changelogStats.totalFeatures }}</h3>
          <p>New Features</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bugfix">
          <i class="fas fa-bug"></i>
        </div>
        <div class="stat-content">
          <h3>{{ changelogStats.totalBugFixes }}</h3>
          <p>Bug Fixes</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon security">
          <i class="fas fa-shield-alt"></i>
        </div>
        <div class="stat-content">
          <h3>{{ changelogStats.totalSecurity }}</h3>
          <p>Security Updates</p>
        </div>
      </div>
    </div>

    <!-- Changelog Timeline -->
    <div class="changelog-timeline">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading changelog...</p>
      </div>

      <div v-else-if="filteredChangelog.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-history"></i>
        </div>
        <h3>No changelog entries found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="timeline">
        <div 
          v-for="(entry, index) in filteredChangelog" 
          :key="entry.id"
          class="timeline-entry"
        >
          <!-- Version Header -->
          <div class="version-header">
            <div class="version-info">
              <h2>{{ entry.version }}</h2>
              <span :class="['version-badge', entry.type]">{{ entry.type }}</span>
              <span class="release-date">{{ formatDate(entry.releaseDate) }}</span>
            </div>
            <div class="version-actions">
              <button 
                class="action-btn"
                @click="toggleVersion(entry.version)"
                :title="expandedVersions.includes(entry.version) ? 'Collapse' : 'Expand'"
              >
                <i :class="expandedVersions.includes(entry.version) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
              <button 
                v-if="entry.downloadUrl"
                class="action-btn"
                @click="downloadVersion(entry)"
                title="Download Version"
              >
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>

          <!-- Version Content -->
          <div v-if="expandedVersions.includes(entry.version)" class="version-content">
            <div class="content-section">
              <h3>Release Notes</h3>
              <div class="release-notes" v-html="entry.releaseNotes"></div>
            </div>

            <!-- Changes by Category -->
            <div class="changes-section">
              <div v-if="entry.features && entry.features.length > 0" class="change-category">
                <h4>
                  <i class="fas fa-star"></i>
                  New Features
                </h4>
                <ul>
                  <li v-for="feature in entry.features" :key="feature.id">
                    <span class="change-title">{{ feature.title }}</span>
                    <p class="change-description">{{ feature.description }}</p>
                  </li>
                </ul>
              </div>

              <div v-if="entry.improvements && entry.improvements.length > 0" class="change-category">
                <h4>
                  <i class="fas fa-arrow-up"></i>
                  Improvements
                </h4>
                <ul>
                  <li v-for="improvement in entry.improvements" :key="improvement.id">
                    <span class="change-title">{{ improvement.title }}</span>
                    <p class="change-description">{{ improvement.description }}</p>
                  </li>
                </ul>
              </div>

              <div v-if="entry.bugfixes && entry.bugfixes.length > 0" class="change-category">
                <h4>
                  <i class="fas fa-bug"></i>
                  Bug Fixes
                </h4>
                <ul>
                  <li v-for="bugfix in entry.bugfixes" :key="bugfix.id">
                    <span class="change-title">{{ bugfix.title }}</span>
                    <p class="change-description">{{ bugfix.description }}</p>
                  </li>
                </ul>
              </div>

              <div v-if="entry.security && entry.security.length > 0" class="change-category">
                <h4>
                  <i class="fas fa-shield-alt"></i>
                  Security Updates
                </h4>
                <ul>
                  <li v-for="security in entry.security" :key="security.id">
                    <span class="change-title">{{ security.title }}</span>
                    <p class="change-description">{{ security.description }}</p>
                  </li>
                </ul>
              </div>

              <div v-if="entry.breaking && entry.breaking.length > 0" class="change-category breaking">
                <h4>
                  <i class="fas fa-exclamation-triangle"></i>
                  Breaking Changes
                </h4>
                <ul>
                  <li v-for="breaking in entry.breaking" :key="breaking.id">
                    <span class="change-title">{{ breaking.title }}</span>
                    <p class="change-description">{{ breaking.description }}</p>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Technical Details -->
            <div class="technical-section">
              <h3>Technical Details</h3>
              <div class="tech-grid">
                <div class="tech-item">
                  <label>Build Number:</label>
                  <span>{{ entry.buildNumber || 'N/A' }}</span>
                </div>
                <div class="tech-item">
                  <label>Compatibility:</label>
                  <span>{{ entry.compatibility || 'All versions' }}</span>
                </div>
                <div class="tech-item">
                  <label>Requirements:</label>
                  <span>{{ entry.requirements || 'None' }}</span>
                </div>
                <div class="tech-item">
                  <label>Checksum:</label>
                  <code>{{ entry.checksum || 'N/A' }}</code>
                </div>
              </div>
            </div>

            <!-- Migration Guide -->
            <div v-if="entry.migrationGuide" class="migration-section">
              <h3>Migration Guide</h3>
              <div class="migration-content" v-html="entry.migrationGuide"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Subscribe to Updates -->
    <div class="subscribe-section">
      <div class="subscribe-card">
        <h3>Stay Updated</h3>
        <p>Get notified about new releases and important updates</p>
        <div class="subscribe-form">
          <input 
            v-model="email" 
            type="email" 
            placeholder="Enter your email"
            @keyup.enter="subscribe"
          />
          <button 
            class="subscribe-btn"
            @click="subscribe"
            :disabled="subscribing"
          >
            <span v-if="!subscribing">Subscribe</span>
            <span v-else>Subscribing...</span>
          </button>
        </div>
        <div v-if="subscribeMessage" :class="['subscribe-message', subscribeSuccess ? 'success' : 'error']">
          {{ subscribeMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const searchQuery = ref('')
const selectedVersion = ref('')
const selectedType = ref('')
const expandedVersions = ref([])
const email = ref('')
const subscribing = ref(false)
const subscribeMessage = ref('')
const subscribeSuccess = ref(false)

const changelogData = ref([
  {
    id: 1,
    version: '2.1.0',
    type: 'feature',
    releaseDate: '2024-01-20',
    buildNumber: '2024012001',
    downloadUrl: 'https://releases.example.com/v2.1.0',
    releaseNotes: '<p>Major update with new features and improvements.</p>',
    features: [
      {
        id: 1,
        title: 'Advanced Analytics Dashboard',
        description: 'Comprehensive analytics dashboard with real-time data visualization and custom reporting tools.'
      },
      {
        id: 2,
        title: 'Team Collaboration Tools',
        description: 'Enhanced team management with role-based permissions and real-time collaboration features.'
      }
    ],
    improvements: [
      {
        id: 1,
        title: 'Performance Optimizations',
        description: 'Improved loading times and reduced memory usage across all modules.'
      },
      {
        id: 2,
        title: 'UI/UX Enhancements',
        description: 'Redesigned interface with improved navigation and accessibility features.'
      }
    ],
    bugfixes: [
      {
        id: 1,
        title: 'Fixed Memory Leak in Dashboard',
        description: 'Resolved memory leak issue that occurred during extended dashboard sessions.'
      },
      {
        id: 2,
        title: 'Corrected Export Functionality',
        description: 'Fixed CSV export that was failing with special characters in data.'
      }
    ],
    security: [
      {
        id: 1,
        title: 'Enhanced API Security',
        description: 'Implemented additional API security measures and rate limiting.'
      }
    ],
    compatibility: 'v2.0.0+',
    requirements: 'Node.js 16+, Modern browsers',
    checksum: 'sha256:abc123def456',
    migrationGuide: '<p>Follow these steps to upgrade from v2.0.x to v2.1.0</p>'
  },
  {
    id: 2,
    version: '2.0.5',
    type: 'improvement',
    releaseDate: '2024-01-10',
    buildNumber: '2024011001',
    downloadUrl: 'https://releases.example.com/v2.0.5',
    releaseNotes: '<p>Stability improvements and bug fixes.</p>',
    improvements: [
      {
        id: 1,
        title: 'Enhanced Error Handling',
        description: 'Improved error messages and recovery mechanisms throughout the application.'
      }
    ],
    bugfixes: [
      {
        id: 1,
        title: 'Fixed Login Issue',
        description: 'Resolved login problem that affected some users with special characters in passwords.'
      }
    ],
    compatibility: 'v2.0.0+',
    requirements: 'Node.js 16+, Modern browsers',
    checksum: 'sha256:def456ghi789'
  },
  {
    id: 3,
    version: '2.0.0',
    type: 'breaking',
    releaseDate: '2024-01-01',
    buildNumber: '2024010101',
    downloadUrl: 'https://releases.example.com/v2.0.0',
    releaseNotes: '<p>Major platform update with breaking changes.</p>',
    features: [
      {
        id: 1,
        title: 'New Architecture',
        description: 'Completely rewritten backend with improved performance and scalability.'
      }
    ],
    breaking: [
      {
        id: 1,
        title: 'API Endpoint Changes',
        description: 'Several API endpoints have been modified. Please review the migration guide.'
      }
    ],
    compatibility: 'v2.0.0+',
    requirements: 'Node.js 16+, Modern browsers',
    checksum: 'sha256:ghi789jkl012',
    migrationGuide: '<p>Important migration steps required for v2.0.0</p>'
  }
])

// Computed properties
const availableVersions = computed(() => {
  return [...new Set(changelogData.value.map(entry => entry.version))].sort((a, b) => {
    // Sort versions in descending order
    return b.localeCompare(a, undefined, { numeric: true, sensitivity: 'base' })
  })
})

const filteredChangelog = computed(() => {
  let filtered = changelogData.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(entry => 
      entry.version.toLowerCase().includes(query) ||
      entry.releaseNotes.toLowerCase().includes(query) ||
      entry.features.some(f => f.title.toLowerCase().includes(query) || f.description.toLowerCase().includes(query))
    )
  }

  // Apply version filter
  if (selectedVersion.value) {
    filtered = filtered.filter(entry => entry.version === selectedVersion.value)
  }

  // Apply type filter
  if (selectedType.value) {
    filtered = filtered.filter(entry => entry.type === selectedType.value)
  }

  return filtered
})

const changelogStats = computed(() => {
  const stats = {
    totalVersions: changelogData.value.length,
    totalFeatures: changelogData.value.reduce((sum, entry) => sum + (entry.features?.length || 0), 0),
    totalBugFixes: changelogData.value.reduce((sum, entry) => sum + (entry.bugfixes?.length || 0), 0),
    totalSecurity: changelogData.value.reduce((sum, entry) => sum + (entry.security?.length || 0), 0)
  }
  return stats
})

// Methods
const filterChangelog = () => {
  // This is reactive, no additional action needed
}

const toggleVersion = (version) => {
  const index = expandedVersions.value.indexOf(version)
  if (index > -1) {
    expandedVersions.value.splice(index, 1)
  } else {
    expandedVersions.value.push(version)
  }
}

const downloadVersion = (entry) => {
  if (entry.downloadUrl) {
    window.open(entry.downloadUrl, '_blank')
    showSuccess(`Downloading ${entry.version}...`)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString()
}

const getEmptyMessage = () => {
  if (searchQuery.value || selectedVersion.value || selectedType.value) {
    return 'No changelog entries match your search criteria'
  }
  return 'No changelog entries available'
}

const subscribe = () => {
  if (!email.value) {
    showError('Please enter a valid email address')
    return
  }

  if (!email.value.includes('@')) {
    showError('Please enter a valid email address')
    return
  }

  subscribing.value = true
  subscribeMessage.value = ''

  // Simulate subscription API call
  setTimeout(() => {
    subscribing.value = false
    subscribeSuccess.value = true
    subscribeMessage.value = 'Successfully subscribed to updates!'
    showSuccess('You will receive updates about new releases')
    email.value = ''
    
    // Clear success message after 5 seconds
    setTimeout(() => {
      subscribeMessage.value = ''
      subscribeSuccess.value = false
    }, 5000)
  }, 1500)
}

// Lifecycle
onMounted(() => {
  // Expand the latest version by default
  if (changelogData.value.length > 0) {
    expandedVersions.value.push(changelogData.value[0].version)
  }
})
</script>

<style scoped>
.changelog {
  padding: 2rem;
  max-width: 1200px;
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

.filter-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.filter-controls {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 1rem;
  align-items: center;
}

.search-box {
  position: relative;
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

.version-filter select,
.type-filter select {
  width: 100%;
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
  cursor: pointer;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
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

.stat-icon.feature {
  background: var(--success-color);
}

.stat-icon.bugfix {
  background: var(--warning-color);
}

.stat-icon.security {
  background: var(--danger-color);
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.stat-content p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 1rem;
}

.changelog-timeline {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.loading-state, .empty-state {
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

.timeline {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.timeline-entry {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--glass-bg-tertiary);
  border-bottom: 1px solid var(--glass-border);
}

.version-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.version-info h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 1.5rem;
}

.version-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.version-badge.feature {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.version-badge.improvement {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.version-badge.bugfix {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.version-badge.security {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.version-badge.breaking {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.release-date {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.version-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  background: var(--glass-bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.version-content {
  padding: 2rem;
}

.content-section {
  margin-bottom: 2rem;
}

.content-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.2rem;
}

.release-notes {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
  line-height: 1.6;
  color: var(--text-primary);
}

.changes-section {
  margin-bottom: 2rem;
}

.change-category {
  margin-bottom: 2rem;
}

.change-category.breaking {
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  padding: 1.5rem;
}

.change-category h4 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.change-category h4 i {
  width: 24px;
  text-align: center;
}

.change-category ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.change-category li {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.change-category li:last-child {
  border-bottom: none;
}

.change-title {
  font-weight: 600;
  color: var(--text-primary);
}

.change-description {
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

.technical-section {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.technical-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.tech-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.tech-item:last-child {
  border-bottom: none;
}

.tech-item label {
  font-weight: 600;
  color: var(--text-secondary);
}

.tech-item span,
.tech-item code {
  color: var(--text-primary);
  font-family: 'Courier New', monospace;
}

.migration-section {
  background: rgba(139, 92, 246, 0.05);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 8px;
  padding: 1.5rem;
}

.migration-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.migration-content {
  line-height: 1.6;
  color: var(--text-primary);
}

.subscribe-section {
  margin-top: 3rem;
}

.subscribe-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

.subscribe-card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.subscribe-card p {
  margin: 0 0 2rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.subscribe-form {
  display: flex;
  gap: 1rem;
  max-width: 400px;
  margin: 0 auto 2rem;
}

.subscribe-form input {
  flex: 1;
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
}

.subscribe-btn {
  padding: 1rem 2rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.subscribe-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.subscribe-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.subscribe-message {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  font-weight: 500;
}

.subscribe-message.success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.subscribe-message.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

@media (max-width: 768px) {
  .changelog {
    padding: 1rem;
  }
  
  .filter-controls {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .version-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .tech-grid {
    grid-template-columns: 1fr;
  }
  
  .subscribe-form {
    flex-direction: column;
    max-width: 100%;
  }
}
</style>
