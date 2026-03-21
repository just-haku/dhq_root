<template>
  <div class="press">
    <div class="page-header">
      <h1>Press & Media</h1>
      <p>Latest news, press releases, and media resources</p>
    </div>

    <div class="press-container">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-content">
          <div class="hero-text">
            <h2>Media Resources</h2>
            <p class="hero-tagline">Stay updated with our latest news and announcements</p>
            <p class="hero-description">
              Welcome to our press center. Here you'll find the latest press releases, media coverage, company news, and resources for journalists and media professionals.
            </p>
            <div class="hero-stats">
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.pressReleases }}</div>
                <div class="stat-label">Press Releases</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.mediaCoverage }}</div>
                <div class="stat-label">Media Mentions</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.awards }}</div>
                <div class="stat-label">Awards</div>
              </div>
            </div>
          </div>
          <div class="hero-image">
            <div class="image-placeholder">
              <i class="fas fa-newspaper"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- Press Releases -->
      <section class="press-releases-section">
        <div class="section-header">
          <h2>Press Releases</h2>
          <div class="header-actions">
            <div class="filter-dropdown">
              <select v-model="releaseFilter" @change="filterReleases">
                <option value="">All Categories</option>
                <option value="product">Product Launch</option>
                <option value="partnership">Partnership</option>
                <option value="funding">Funding</option>
                <option value="award">Awards</option>
                <option value="milestone">Milestone</option>
              </select>
            </div>
            <div class="filter-dropdown">
              <select v-model="yearFilter" @change="filterReleases">
                <option value="">All Years</option>
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
                <option value="2021">2021</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading press releases...</p>
        </div>

        <div v-else-if="filteredReleases.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <h3>No press releases found</h3>
          <p>Try adjusting your filters or check back later for new releases.</p>
        </div>

        <div v-else class="releases-grid">
          <div 
            v-for="release in paginatedReleases" 
            :key="release.id"
            class="release-card"
            @click="viewRelease(release)"
          >
            <div class="release-header">
              <div class="release-meta">
                <span class="category" :class="release.category">{{ formatCategory(release.category) }}</span>
                <span class="date">{{ formatDate(release.date) }}</span>
              </div>
              <div class="release-actions">
                <button class="action-btn download" @click.stop="downloadRelease(release)">
                  <i class="fas fa-download"></i>
                </button>
                <button class="action-btn share" @click.stop="shareRelease(release)">
                  <i class="fas fa-share"></i>
                </button>
              </div>
            </div>
            
            <div class="release-content">
              <h3>{{ release.title }}</h3>
              <p class="release-summary">{{ release.summary }}</p>
              
              <div class="release-details">
                <div class="detail-item">
                  <label>Location:</label>
                  <span>{{ release.location }}</span>
                </div>
                <div class="detail-item">
                  <label>Contact:</label>
                  <span>{{ release.contact }}</span>
                </div>
              </div>
            </div>
            
            <div class="release-footer">
              <button class="read-more-btn" @click.stop="viewRelease(release)">
                Read Full Release
                <i class="fas fa-arrow-right"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination" v-if="totalReleasePages > 1">
          <button 
            class="pagination-btn" 
            :disabled="currentReleasePage === 1"
            @click="currentReleasePage--"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="page-info">{{ currentReleasePage }} / {{ totalReleasePages }}</span>
          <button 
            class="pagination-btn" 
            :disabled="currentReleasePage === totalReleasePages"
            @click="currentReleasePage++"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </section>

      <!-- Media Coverage -->
      <section class="media-coverage-section">
        <div class="section-header">
          <h2>Media Coverage</h2>
          <p>What the media is saying about us</p>
        </div>
        <div class="coverage-grid">
          <div 
            v-for="coverage in mediaCoverage" 
            :key="coverage.id"
            class="coverage-card"
            @click="openCoverage(coverage)"
          >
            <div class="coverage-header">
              <div class="publication-info">
                <img :src="coverage.logo" :alt="coverage.publication" class="publication-logo" />
                <div class="publication-details">
                  <h4>{{ coverage.publication }}</h4>
                  <span class="coverage-date">{{ formatDate(coverage.date) }}</span>
                </div>
              </div>
              <div class="coverage-actions">
                <button class="action-btn external" @click.stop="openCoverage(coverage)">
                  <i class="fas fa-external-link-alt"></i>
                </button>
              </div>
            </div>
            
            <div class="coverage-content">
              <h3>{{ coverage.title }}</h3>
              <p class="coverage-excerpt">{{ coverage.excerpt }}</p>
              
              <div class="coverage-tags">
                <span 
                  v-for="tag in coverage.tags" 
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Awards & Recognition -->
      <section class="awards-section">
        <div class="section-header">
          <h2>Awards & Recognition</h2>
          <p>Our achievements and industry recognition</p>
        </div>
        <div class="awards-grid">
          <div 
            v-for="award in awards" 
            :key="award.id"
            class="award-card"
          >
            <div class="award-icon">
              <i :class="award.icon"></i>
            </div>
            <div class="award-content">
              <h3>{{ award.title }}</h3>
              <p class="award-organization">{{ award.organization }}</p>
              <p class="award-description">{{ award.description }}</p>
              <div class="award-meta">
                <span class="award-year">{{ award.year }}</span>
                <span class="award-category">{{ award.category }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Media Kit -->
      <section class="media-kit-section">
        <div class="section-header">
          <h2>Media Kit</h2>
          <p>Download our brand assets and resources</p>
        </div>
        <div class="media-kit-grid">
          <div 
            v-for="resource in mediaKit" 
            :key="resource.id"
            class="kit-item"
            @click="downloadResource(resource)"
          >
            <div class="kit-icon">
              <i :class="resource.icon"></i>
            </div>
            <div class="kit-content">
              <h3>{{ resource.title }}</h3>
              <p>{{ resource.description }}</p>
              <div class="kit-meta">
                <span class="file-size">{{ resource.fileSize }}</span>
                <span class="file-type">{{ resource.fileType }}</span>
              </div>
            </div>
            <div class="kit-action">
              <i class="fas fa-download"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- Press Contacts -->
      <section class="contacts-section">
        <div class="section-header">
          <h2>Press Contacts</h2>
          <p>Get in touch with our media relations team</p>
        </div>
        <div class="contacts-grid">
          <div 
            v-for="contact in pressContacts" 
            :key="contact.id"
            class="contact-card"
          >
            <div class="contact-avatar">
              <img :src="contact.photo" :alt="contact.name" />
            </div>
            <div class="contact-info">
              <h3>{{ contact.name }}</h3>
              <p class="contact-title">{{ contact.title }}</p>
              <div class="contact-details">
                <div class="detail-item">
                  <i class="fas fa-envelope"></i>
                  <a :href="`mailto:${contact.email}`">{{ contact.email }}</a>
                </div>
                <div class="detail-item">
                  <i class="fas fa-phone"></i>
                  <a :href="`tel:${contact.phone}`">{{ contact.phone }}</a>
                </div>
                <div class="detail-item">
                  <i class="fas fa-clock"></i>
                  <span>{{ contact.availability }}</span>
                </div>
              </div>
              <div class="contact-topics">
                <h4>Topics:</h4>
                <div class="topics-list">
                  <span 
                    v-for="topic in contact.topics" 
                    :key="topic"
                    class="topic-tag"
                  >
                    {{ topic }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Newsletter Signup -->
      <section class="newsletter-section">
        <div class="section-header">
          <h2>Press Newsletter</h2>
          <p>Get the latest news and updates delivered to your inbox</p>
        </div>
        <div class="newsletter-content">
          <div class="newsletter-form">
            <form @submit.prevent="subscribeNewsletter">
              <div class="form-group">
                <label for="email">Email Address</label>
                <input 
                  id="email"
                  v-model="newsletterForm.email"
                  type="email"
                  required
                  placeholder="your.email@example.com"
                />
              </div>
              <div class="form-group">
                <label for="name">Name</label>
                <input 
                  id="name"
                  v-model="newsletterForm.name"
                  type="text"
                  placeholder="Your name"
                />
              </div>
              <div class="form-group">
                <label for="organization">Organization</label>
                <input 
                  id="organization"
                  v-model="newsletterForm.organization"
                  type="text"
                  placeholder="Media organization"
                />
              </div>
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    v-model="newsletterForm.immediate"
                    id="immediate"
                  />
                  <span class="checkmark"></span>
                  Send immediate alerts for breaking news
                </label>
              </div>
              <button type="submit" class="subscribe-btn" :disabled="isSubscribing">
                <i class="fas fa-envelope" v-if="!isSubscribing"></i>
                <i class="fas fa-spinner fa-spin" v-else></i>
                {{ isSubscribing ? 'Subscribing...' : 'Subscribe' }}
              </button>
            </form>
          </div>
          <div class="newsletter-info">
            <div class="info-card">
              <div class="info-icon">
                <i class="fas fa-bell"></i>
              </div>
              <h3>Stay Informed</h3>
              <p>Get instant access to press releases, company news, and media updates as they happen.</p>
            </div>
            <div class="info-card">
              <div class="info-icon">
                <i class="fas fa-shield-alt"></i>
              </div>
              <h3>Privacy Protected</h3>
              <p>Your information is secure and will only be used for press-related communications.</p>
            </div>
            <div class="info-card">
              <div class="info-icon">
                <i class="fas fa-times-circle"></i>
              </div>
              <h3>Easy Unsubscribe</h3>
              <p>Unsubscribe at any time with a single click. No questions asked.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const releaseFilter = ref('')
const yearFilter = ref('')
const currentReleasePage = ref(1)
const releasesPerPage = ref(6)
const isSubscribing = ref(false)

// Newsletter form
const newsletterForm = reactive({
  email: '',
  name: '',
  organization: '',
  immediate: false
})

// Company data
const companyData = reactive({
  name: 'Digital HQ',
  stats: {
    pressReleases: 45,
    mediaCoverage: 120,
    awards: 15
  }
})

// Press releases
const pressReleases = ref([
  {
    id: 1,
    title: 'Digital HQ Raises $50M Series C Funding to Accelerate Global Expansion',
    summary: 'Leading digital transformation platform secures major investment to fuel international growth and product innovation.',
    category: 'funding',
    date: '2024-01-15T00:00:00Z',
    location: 'San Francisco, CA',
    contact: 'Sarah Johnson, PR Manager',
    content: 'Full press release content here...'
  },
  {
    id: 2,
    title: 'New AI-Powered Analytics Platform Transforms Business Intelligence',
    summary: 'Revolutionary platform uses advanced machine learning to provide real-time business insights and predictive analytics.',
    category: 'product',
    date: '2024-01-10T00:00:00Z',
    location: 'New York, NY',
    contact: 'Michael Chen, Product Communications',
    content: 'Full press release content here...'
  },
  {
    id: 3,
    title: 'Digital HQ Named "Best Workplace for Innovation" by Tech Magazine',
    summary: 'Company recognized for fostering culture of innovation and employee empowerment in annual industry awards.',
    category: 'award',
    date: '2024-01-05T00:00:00Z',
    location: 'San Francisco, CA',
    contact: 'Emily Rodriguez, HR Communications',
    content: 'Full press release content here...'
  },
  {
    id: 4,
    title: 'Strategic Partnership with Global Tech Leader Announced',
    summary: 'Collaboration aims to deliver integrated solutions for enterprise digital transformation initiatives.',
    category: 'partnership',
    date: '2023-12-20T00:00:00Z',
    location: 'London, UK',
    contact: 'David Kim, Partnership Communications',
    content: 'Full press release content here...'
  },
  {
    id: 5,
    title: 'Digital HQ Achieves 10,000 Customer Milestone',
    summary: 'Company celebrates rapid growth with customer base expanding to over 10,000 businesses worldwide.',
    category: 'milestone',
    date: '2023-12-15T00:00:00Z',
    location: 'San Francisco, CA',
    contact: 'Sarah Johnson, PR Manager',
    content: 'Full press release content here...'
  }
])

// Media coverage
const mediaCoverage = ref([
  {
    id: 1,
    publication: 'TechCrunch',
    title: 'How Digital HQ is Revolutionizing Enterprise Digital Transformation',
    excerpt: 'A deep dive into the company\'s innovative approach to helping businesses navigate their digital journey...',
    date: '2024-01-12T00:00:00Z',
    url: 'https://techcrunch.com/article',
    logo: '/api/placeholder/60x40',
    tags: ['Enterprise', 'Innovation', 'Growth']
  },
  {
    id: 2,
    publication: 'Forbes',
    title: 'The Future of Business Intelligence: Interview with CEO',
    excerpt: 'An exclusive interview discussing the future of AI in business analytics and data-driven decision making...',
    date: '2024-01-08T00:00:00Z',
    url: 'https://forbes.com/article',
    logo: '/api/placeholder/60x40',
    tags: ['Leadership', 'AI', 'Analytics']
  },
  {
    id: 3,
    publication: 'Business Insider',
    title: 'Inside Digital HQ\'s Rapid Growth Strategy',
    excerpt: 'How the company achieved 200% year-over-year growth while maintaining product quality and customer satisfaction...',
    date: '2024-01-05T00:00:00Z',
    url: 'https://businessinsider.com/article',
    logo: '/api/placeholder/60x40',
    tags: ['Growth', 'Strategy', 'Success']
  }
])

// Awards
const awards = ref([
  {
    id: 1,
    title: 'Best Enterprise Software Solution',
    organization: 'Tech Innovation Awards',
    description: 'Recognized for excellence in enterprise digital transformation solutions',
    year: 2024,
    category: 'Product Excellence',
    icon: 'fas fa-trophy'
  },
  {
    id: 2,
    title: 'Fastest Growing Tech Company',
    organization: 'Business Weekly',
    description: 'Ranked among top 10 fastest growing technology companies globally',
    year: 2023,
    category: 'Growth',
    icon: 'fas fa-rocket'
  },
  {
    id: 3,
    title: 'Best Workplace for Innovation',
    organization: 'Tech Magazine',
    description: 'Recognized for fostering culture of innovation and creativity',
    year: 2024,
    category: 'Culture',
    icon: 'fas fa-star'
  }
])

// Media kit resources
const mediaKit = ref([
  {
    id: 1,
    title: 'Company Overview',
    description: 'Comprehensive company information, history, and mission',
    icon: 'fas fa-building',
    fileSize: '2.5 MB',
    fileType: 'PDF',
    url: '/downloads/company-overview.pdf'
  },
  {
    id: 2,
    title: 'Brand Guidelines',
    description: 'Logo usage, color palette, and brand standards',
    icon: 'fas fa-palette',
    fileSize: '15.8 MB',
    fileType: 'ZIP',
    url: '/downloads/brand-guidelines.zip'
  },
  {
    id: 3,
    title: 'Executive Photos',
    description: 'High-resolution photos of leadership team',
    icon: 'fas fa-camera',
    fileSize: '45.2 MB',
    fileType: 'ZIP',
    url: '/downloads/executive-photos.zip'
  },
  {
    id: 4,
    title: 'Product Screenshots',
    description: 'High-quality screenshots of our products',
    icon: 'fas fa-desktop',
    fileSize: '8.7 MB',
    fileType: 'ZIP',
    url: '/downloads/screenshots.zip'
  },
  {
    id: 5,
    title: 'Press Kit (Complete)',
    description: 'All media resources in one download',
    icon: 'fas fa-archive',
    fileSize: '125.4 MB',
    fileType: 'ZIP',
    url: '/downloads/complete-press-kit.zip'
  }
])

// Press contacts
const pressContacts = ref([
  {
    id: 1,
    name: 'Sarah Johnson',
    title: 'PR Manager',
    email: 'press@company.com',
    phone: '+1 (415) 555-0100',
    photo: '/api/placeholder/100x100',
    availability: 'Mon-Fri 9AM-6PM EST',
    topics: ['General Inquiries', 'Product News', 'Partnerships']
  },
  {
    id: 2,
    name: 'Michael Chen',
    title: 'Product Communications',
    email: 'product-press@company.com',
    phone: '+1 (415) 555-0200',
    photo: '/api/placeholder/100x100',
    availability: 'Mon-Fri 9AM-6PM EST',
    topics: ['Product Launches', 'Technical Updates', 'Innovation']
  },
  {
    id: 3,
    name: 'Emily Rodriguez',
    title: 'Investor Relations',
    email: 'investors@company.com',
    phone: '+1 (415) 555-0300',
    photo: '/api/placeholder/100x100',
    availability: 'Mon-Fri 9AM-6PM EST',
    topics: ['Funding', 'Financial Results', 'Investment News']
  }
])

// Computed properties
const filteredReleases = computed(() => {
  let filtered = pressReleases.value

  if (releaseFilter.value) {
    filtered = filtered.filter(release => release.category === releaseFilter.value)
  }

  if (yearFilter.value) {
    filtered = filtered.filter(release => new Date(release.date).getFullYear().toString() === yearFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const paginatedReleases = computed(() => {
  const start = (currentReleasePage.value - 1) * releasesPerPage.value
  const end = start + releasesPerPage.value
  return filteredReleases.value.slice(start, end)
})

const totalReleasePages = computed(() => {
  return Math.ceil(filteredReleases.value.length / releasesPerPage.value)
})

// Methods
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatCategory = (category) => {
  return category.charAt(0).toUpperCase() + category.slice(1)
}

const filterReleases = () => {
  currentReleasePage.value = 1
}

const viewRelease = (release) => {
  showSuccess(`Opening press release: ${release.title}`)
  // In a real app, this would navigate to release details
}

const downloadRelease = (release) => {
  showSuccess(`Downloading press release: ${release.title}`)
  // In a real app, this would download the release
}

const shareRelease = (release) => {
  showSuccess(`Sharing press release: ${release.title}`)
  // In a real app, this would open share dialog
}

const openCoverage = (coverage) => {
  showSuccess(`Opening article: ${coverage.title}`)
  // In a real app, this would open the article in new tab
  window.open(coverage.url, '_blank')
}

const downloadResource = (resource) => {
  showSuccess(`Downloading: ${resource.title}`)
  // In a real app, this would download the resource
  window.open(resource.url, '_blank')
}

const subscribeNewsletter = async () => {
  isSubscribing.value = true

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    showSuccess('Successfully subscribed to press newsletter!')
    
    // Reset form
    Object.assign(newsletterForm, {
      email: '',
      name: '',
      organization: '',
      immediate: false
    })
  } catch (error) {
    console.error('Error subscribing to newsletter:', error)
    showError('Failed to subscribe. Please try again.')
  } finally {
    isSubscribing.value = false
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/press/releases')
    // if (response.success) {
    //   pressReleases.value = response.releases || []
    // }
    
    // For demo, use mock data
    loading.value = false
  } catch (error) {
    console.error('Error loading press releases:', error)
    showError('Failed to load press releases')
    loading.value = false
  }
})
</script>

<style scoped>
.press {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 4rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.page-header p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.press-container {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.hero-section,
.press-releases-section,
.media-coverage-section,
.awards-section,
.media-kit-section,
.contacts-section,
.newsletter-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 3rem;
}

.hero-section {
  margin-bottom: 4rem;
}

.hero-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 3rem;
  align-items: center;
}

.hero-text h2 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.hero-tagline {
  font-size: 1.3rem;
  color: var(--primary-color);
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.hero-description {
  font-size: 1.1rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 2rem;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.hero-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-placeholder {
  width: 200px;
  height: 200px;
  background: var(--glass-bg-primary);
  border: 2px dashed var(--glass-border);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: 3rem;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.section-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.filter-dropdown {
  position: relative;
}

.filter-dropdown select {
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  min-width: 150px;
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

.releases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.release-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.release-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.release-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.release-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  width: fit-content;
}

.category.product {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.category.partnership {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.category.funding {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.category.award {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.category.milestone {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.date {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.release-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.download:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.share:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.external:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.release-content h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.release-summary {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.release-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
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

.release-footer {
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

.read-more-btn {
  background: none;
  border: none;
  color: var(--primary-color);
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.read-more-btn:hover {
  gap: 1rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--glass-bg-hover);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-primary);
  font-weight: 600;
}

.coverage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.coverage-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.coverage-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.coverage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.publication-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.publication-logo {
  width: 60px;
  height: 40px;
  object-fit: contain;
}

.publication-details h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.coverage-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.coverage-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.coverage-excerpt {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.coverage-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.awards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.award-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  gap: 1.5rem;
  transition: all 0.3s ease;
}

.award-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.award-icon {
  width: 60px;
  height: 60px;
  background: var(--warning-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.award-content {
  flex: 1;
}

.award-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.award-organization {
  color: var(--primary-color);
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.award-description {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.award-meta {
  display: flex;
  gap: 1rem;
}

.award-year {
  background: var(--primary-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.award-category {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.media-kit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.kit-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.kit-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.kit-icon {
  width: 50px;
  height: 50px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.kit-content {
  flex: 1;
}

.kit-content h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.kit-content p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.kit-meta {
  display: flex;
  gap: 1rem;
}

.file-size,
.file-type {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.kit-action {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.kit-item:hover .kit-action {
  transform: scale(1.1);
}

.contacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.contact-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  gap: 1.5rem;
  transition: all 0.3s ease;
}

.contact-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.contact-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.contact-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.contact-info {
  flex: 1;
}

.contact-info h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.contact-title {
  color: var(--primary-color);
  font-weight: 600;
  margin-bottom: 1rem;
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.contact-details .detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.contact-details .detail-item i {
  width: 20px;
  color: var(--primary-color);
}

.contact-details .detail-item a {
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 500;
}

.contact-details .detail-item a:hover {
  text-decoration: underline;
}

.contact-topics h4 {
  font-size: 1rem;
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.topics-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.topic-tag {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.newsletter-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 3rem;
}

.newsletter-form {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 1rem;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-weight: 500;
  color: var(--text-primary);
}

.checkbox-label input[type="checkbox"] {
  width: 20px;
  height: 20px;
  accent-color: var(--primary-color);
}

.subscribe-btn {
  width: 100%;
  padding: 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1rem;
}

.subscribe-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.subscribe-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.newsletter-info {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.info-icon {
  width: 50px;
  height: 50px;
  background: var(--success-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  margin: 0 auto 1rem;
}

.info-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.info-card p {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .press {
    padding: 1rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .hero-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .hero-stats {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .releases-grid,
  .coverage-grid {
    grid-template-columns: 1fr;
  }
  
  .release-details {
    grid-template-columns: 1fr;
  }
  
  .awards-grid,
  .media-kit-grid,
  .contacts-grid {
    grid-template-columns: 1fr;
  }
  
  .award-card,
  .contact-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .newsletter-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}
</style>
