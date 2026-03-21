<template>
  <div class="help">
    <div class="page-header">
      <h1>Help Center</h1>
      <p>Find answers to your questions and get support</p>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search for help articles..."
          @input="searchHelp"
        />
      </div>
      <div class="quick-links">
        <button 
          v-for="link in quickLinks" 
          :key="link.id"
          class="quick-link-btn"
          @click="navigateToSection(link.section)"
        >
          <i :class="link.icon"></i>
          {{ link.label }}
        </button>
      </div>
    </div>

    <!-- Help Categories -->
    <div class="help-categories">
      <div 
        v-for="category in filteredCategories" 
        :key="category.id"
        class="category-section"
      >
        <div class="category-header" @click="toggleCategory(category.id)">
          <div class="category-info">
            <i :class="category.icon"></i>
            <h2>{{ category.title }}</h2>
            <span class="article-count">{{ category.articles.length }} articles</span>
          </div>
          <i :class="['toggle-icon', expandedCategories.includes(category.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down']"></i>
        </div>

        <div v-if="expandedCategories.includes(category.id)" class="category-content">
          <div class="articles-grid">
            <div 
              v-for="article in category.articles" 
              :key="article.id"
              class="article-card"
              @click="openArticle(article)"
            >
              <div class="article-header">
                <h3>{{ article.title }}</h3>
                <span :class="['article-badge', article.type]">{{ article.type }}</span>
              </div>
              <p class="article-excerpt">{{ article.excerpt }}</p>
              <div class="article-meta">
                <span class="read-time">{{ article.readTime }} min read</span>
                <span class="update-date">{{ formatDate(article.updatedAt) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Popular Articles -->
    <div class="popular-section">
      <h2>Popular Articles</h2>
      <div class="popular-articles">
        <div 
          v-for="article in popularArticles" 
          :key="article.id"
          class="popular-article"
          @click="openArticle(article)"
        >
          <div class="popular-number">{{ article.rank }}</div>
          <div class="popular-content">
            <h4>{{ article.title }}</h4>
            <p>{{ article.excerpt }}</p>
            <span class="popular-category">{{ article.category }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Video Tutorials -->
    <div class="tutorials-section">
      <h2>Video Tutorials</h2>
      <div class="tutorials-grid">
        <div 
          v-for="tutorial in videoTutorials" 
          :key="tutorial.id"
          class="tutorial-card"
          @click="openTutorial(tutorial)"
        >
          <div class="tutorial-thumbnail">
            <img :src="tutorial.thumbnail" :alt="tutorial.title" />
            <div class="play-button">
              <i class="fas fa-play"></i>
            </div>
            <span class="duration">{{ tutorial.duration }}</span>
          </div>
          <div class="tutorial-info">
            <h3>{{ tutorial.title }}</h3>
            <p>{{ tutorial.description }}</p>
            <div class="tutorial-meta">
              <span class="views">{{ tutorial.views.toLocaleString() }} views</span>
              <span class="tutorial-date">{{ formatDate(tutorial.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- FAQ Section -->
    <div class="faq-section">
      <h2>Frequently Asked Questions</h2>
      <div class="faq-list">
        <div 
          v-for="(faq, index) in faqs" 
          :key="faq.id"
          class="faq-item"
        >
          <div class="faq-question" @click="toggleFAQ(index)">
            <h3>{{ faq.question }}</h3>
            <i :class="['toggle-icon', expandedFAQs.includes(index) ? 'fas fa-chevron-up' : 'fas fa-chevron-down']"></i>
          </div>
          <div v-if="expandedFAQs.includes(index)" class="faq-answer">
            <p>{{ faq.answer }}</p>
            <div v-if="faq.links" class="faq-links">
              <a 
                v-for="link in faq.links" 
                :key="link.text"
                :href="link.url"
                target="_blank"
                class="faq-link"
              >
                <i class="fas fa-external-link-alt"></i>
                {{ link.text }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Support -->
    <div class="contact-section">
      <h2>Still Need Help?</h2>
      <div class="contact-options">
        <div class="contact-card" @click="openChat">
          <div class="contact-icon">
            <i class="fas fa-comments"></i>
          </div>
          <div class="contact-info">
            <h3>Live Chat</h3>
            <p>Chat with our support team</p>
            <span class="availability">Available 24/7</span>
          </div>
        </div>

        <div class="contact-card" @click="openEmail">
          <div class="contact-icon">
            <i class="fas fa-envelope"></i>
          </div>
          <div class="contact-info">
            <h3>Email Support</h3>
            <p>Get help via email</p>
            <span class="response-time">Response within 24 hours</span>
          </div>
        </div>

        <div class="contact-card" @click="openTicket">
          <div class="contact-icon">
            <i class="fas fa-ticket-alt"></i>
          </div>
          <div class="contact-info">
            <h3>Support Ticket</h3>
            <p>Create a support ticket</p>
            <span class="tracking">Track your request</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Article Modal -->
    <div v-if="showArticleModal" class="modal-overlay" @click="closeArticleModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedArticle?.title }}</h2>
          <button class="close-btn" @click="closeArticleModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="article-content">
            <div class="article-meta-header">
              <span :class="['article-badge', selectedArticle?.type]">{{ selectedArticle?.type }}</span>
              <span class="read-time">{{ selectedArticle?.readTime }} min read</span>
              <span class="update-date">Updated {{ formatDate(selectedArticle?.updatedAt) }}</span>
            </div>
            <div class="article-body" v-html="selectedArticle?.content"></div>
            <div v-if="selectedArticle?.relatedArticles" class="related-articles">
              <h3>Related Articles</h3>
              <div class="related-list">
                <a 
                  v-for="related in selectedArticle.relatedArticles" 
                  :key="related.id"
                  @click="openArticle(related)"
                  class="related-link"
                >
                  {{ related.title }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tutorial Modal -->
    <div v-if="showTutorialModal" class="modal-overlay" @click="closeTutorialModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedTutorial?.title }}</h2>
          <button class="close-btn" @click="closeTutorialModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="tutorial-content">
            <div class="video-container">
              <iframe 
                v-if="selectedTutorial?.videoUrl"
                :src="selectedTutorial.videoUrl"
                frameborder="0"
                allowfullscreen
              ></iframe>
            </div>
            <div class="tutorial-info">
              <p>{{ selectedTutorial?.description }}</p>
              <div class="tutorial-steps">
                <h4>Steps Covered:</h4>
                <ul>
                  <li v-for="step in selectedTutorial?.steps" :key="step">{{ step }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const searchQuery = ref('')
const expandedCategories = ref([])
const expandedFAQs = ref([])
const showArticleModal = ref(false)
const showTutorialModal = ref(false)
const selectedArticle = ref(null)
const selectedTutorial = ref(null)

const quickLinks = [
  { id: 1, label: 'Getting Started', icon: 'fas fa-rocket', section: 'getting-started' },
  { id: 2, label: 'Billing', icon: 'fas fa-credit-card', section: 'billing' },
  { id: 3, label: 'Account', icon: 'fas fa-user', section: 'account' },
  { id: 4, label: 'Technical', icon: 'fas fa-cog', section: 'technical' }
]

const helpCategories = ref([
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: 'fas fa-rocket',
    articles: [
      {
        id: 1,
        title: 'Creating Your First Order',
        excerpt: 'Learn how to create your first growth order and configure all the necessary settings.',
        content: '<p>Step-by-step guide to creating your first order...</p>',
        type: 'guide',
        readTime: 5,
        updatedAt: '2024-01-15'
      },
      {
        id: 2,
        title: 'Understanding the Dashboard',
        excerpt: 'Navigate through the dashboard and understand all the available features.',
        content: '<p>Complete dashboard overview...</p>',
        type: 'tutorial',
        readTime: 8,
        updatedAt: '2024-01-14'
      }
    ]
  },
  {
    id: 'billing',
    title: 'Billing & Payments',
    icon: 'fas fa-credit-card',
    articles: [
      {
        id: 3,
        title: 'Payment Methods',
        excerpt: 'Add and manage your payment methods for seamless transactions.',
        content: '<p>Payment methods management guide...</p>',
        type: 'guide',
        readTime: 3,
        updatedAt: '2024-01-13'
      },
      {
        id: 4,
        title: 'Understanding Invoices',
        excerpt: 'How to read and understand your invoices and billing statements.',
        content: '<p>Invoice breakdown and explanation...</p>',
        type: 'guide',
        readTime: 6,
        updatedAt: '2024-01-12'
      }
    ]
  },
  {
    id: 'account',
    title: 'Account Management',
    icon: 'fas fa-user',
    articles: [
      {
        id: 5,
        title: 'Profile Settings',
        excerpt: 'Customize your profile and manage your personal information.',
        content: '<p>Profile configuration guide...</p>',
        type: 'guide',
        readTime: 4,
        updatedAt: '2024-01-11'
      }
    ]
  },
  {
    id: 'technical',
    title: 'Technical Support',
    icon: 'fas fa-cog',
    articles: [
      {
        id: 6,
        title: 'API Documentation',
        excerpt: 'Complete API documentation for developers.',
        content: '<p>API reference and examples...</p>',
        type: 'technical',
        readTime: 12,
        updatedAt: '2024-01-10'
      }
    ]
  }
])

const popularArticles = ref([
  {
    id: 1,
    title: 'Getting Started with Growth Orders',
    excerpt: 'Complete guide to creating and managing your first growth order.',
    category: 'Getting Started',
    rank: 1
  },
  {
    id: 2,
    title: 'Understanding Order Analytics',
    excerpt: 'Learn how to interpret and use the analytics data from your orders.',
    category: 'Analytics',
    rank: 2
  },
  {
    id: 3,
    title: 'Payment and Billing FAQ',
    excerpt: 'Common questions about payments, invoices, and billing.',
    category: 'Billing',
    rank: 3
  }
])

const videoTutorials = ref([
  {
    id: 1,
    title: 'Dashboard Overview',
    description: 'Complete tour of the dashboard interface and all its features.',
    thumbnail: 'https://via.placeholder.com/300x200?text=Dashboard+Tour',
    duration: '5:23',
    views: 15420,
    videoUrl: 'https://example.com/video1',
    steps: ['Navigation', 'Order Management', 'Analytics', 'Settings']
  },
  {
    id: 2,
    title: 'Creating Your First Order',
    description: 'Step-by-step tutorial on creating your first growth order.',
    thumbnail: 'https://via.placeholder.com/300x200?text=First+Order',
    duration: '8:45',
    views: 8930,
    videoUrl: 'https://example.com/video2',
    steps: ['Configuration', 'Service Selection', 'Scheduling', 'Launch']
  }
])

const faqs = ref([
  {
    id: 1,
    question: 'How do I create a new growth order?',
    answer: 'To create a new growth order, navigate to the Growth Orders section and click the "New Order" button. Fill in the required information including target link, service type, quantity, and scheduling preferences. Review your settings and click "Create Order" to launch.',
    links: [
      { text: 'View Growth Orders Tutorial', url: '/help/tutorial/growth-orders' }
    ]
  },
  {
    id: 2,
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers. All payments are processed securely through our encrypted payment gateway.',
    links: []
  },
  {
    id: 3,
    question: 'How can I track my order progress?',
    answer: 'You can track your order progress in real-time through the dashboard. Each order shows detailed status information, progress bars, and individual sub-order status. You can also enable email notifications for status updates.',
    links: [
      { text: 'Enable Notifications', url: '/settings/notifications' }
    ]
  },
  {
    id: 4,
    question: 'What is your refund policy?',
    answer: 'We offer a 30-day money-back guarantee for all unused orders. If you\'re not satisfied with our service, contact our support team within 30 days for a full refund. Used orders may be eligible for partial refunds depending on the circumstances.',
    links: [
      { text: 'View Refund Policy', url: '/policies/refunds' }
    ]
  }
])

// Computed properties
const filteredCategories = computed(() => {
  if (!searchQuery.value) return helpCategories.value
  
  const query = searchQuery.value.toLowerCase()
  return helpCategories.value.map(category => ({
    ...category,
    articles: category.articles.filter(article => 
      article.title.toLowerCase().includes(query) || 
      article.excerpt.toLowerCase().includes(query)
    )
  })).filter(category => category.articles.length > 0)
})

// Methods
const searchHelp = () => {
  // This is reactive, no additional action needed
}

const toggleCategory = (categoryId) => {
  const index = expandedCategories.value.indexOf(categoryId)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
  } else {
    expandedCategories.value.push(categoryId)
  }
}

const toggleFAQ = (index) => {
  const faqIndex = expandedFAQs.value.indexOf(index)
  if (faqIndex > -1) {
    expandedFAQs.value.splice(faqIndex, 1)
  } else {
    expandedFAQs.value.push(index)
  }
}

const navigateToSection = (sectionId) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

const openArticle = (article) => {
  selectedArticle.value = article
  showArticleModal.value = true
}

const openTutorial = (tutorial) => {
  selectedTutorial.value = tutorial
  showTutorialModal.value = true
}

const closeArticleModal = () => {
  showArticleModal.value = false
  selectedArticle.value = null
}

const closeTutorialModal = () => {
  showTutorialModal.value = false
  selectedTutorial.value = null
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const openChat = () => {
  showSuccess('Opening live chat...')
  // Implement chat functionality
}

const openEmail = () => {
  showSuccess('Opening email client...')
  // Implement email functionality
}

const openTicket = () => {
  showSuccess('Redirecting to support ticket system...')
  // Implement ticket system
}

// Lifecycle
onMounted(() => {
  // Expand first category by default
  if (helpCategories.value.length > 0) {
    expandedCategories.value.push(helpCategories.value[0].id)
  }
})
</script>

<style scoped>
.help {
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

.search-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 3rem;
  padding: 2rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
}

.search-box {
  position: relative;
  max-width: 600px;
  margin: 0 auto;
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

.quick-links {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.quick-link-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quick-link-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.help-categories {
  margin-bottom: 3rem;
}

.category-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

.category-header:hover {
  background: var(--glass-bg-hover);
}

.category-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.category-info i {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.category-info h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.article-count {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.toggle-icon {
  color: var(--text-secondary);
  transition: transform 0.3s ease;
}

.category-content {
  padding: 0 1.5rem 1.5rem;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.article-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.article-card:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.article-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  flex: 1;
}

.article-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.article-badge.guide {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.article-badge.tutorial {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.article-badge.technical {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.article-excerpt {
  color: var(--text-secondary);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: var(--text-tertiary);
}

.popular-section {
  margin-bottom: 3rem;
}

.popular-section h2 {
  margin-bottom: 2rem;
  color: var(--text-primary);
  font-weight: 600;
}

.popular-articles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.popular-article {
  display: flex;
  gap: 1rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.popular-article:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-2px);
}

.popular-number {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.popular-content {
  flex: 1;
}

.popular-content h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.popular-content p {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.popular-category {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.tutorials-section {
  margin-bottom: 3rem;
}

.tutorials-section h2 {
  margin-bottom: 2rem;
  color: var(--text-primary);
  font-weight: 600;
}

.tutorials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.tutorial-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tutorial-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.tutorial-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.tutorial-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  transition: all 0.3s ease;
}

.tutorial-card:hover .play-button {
  background: var(--primary-color);
  transform: translate(-50%, -50%) scale(1.1);
}

.duration {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.tutorial-info {
  padding: 1.5rem;
}

.tutorial-info h3 {
  margin: 0 0 0.75rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.tutorial-info p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.tutorial-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: var(--text-tertiary);
}

.tutorial-steps h4 {
  margin: 0 0 0.75rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.tutorial-steps ul {
  margin: 0;
  padding-left: 1.5rem;
  color: var(--text-secondary);
}

.tutorial-steps li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.faq-section {
  margin-bottom: 3rem;
}

.faq-section h2 {
  margin-bottom: 2rem;
  color: var(--text-primary);
  font-weight: 600;
}

.faq-list {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
}

.faq-item {
  border-bottom: 1px solid var(--glass-border);
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

.faq-question:hover {
  background: var(--glass-bg-hover);
}

.faq-question h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  flex: 1;
}

.faq-answer {
  padding: 0 1.5rem 1.5rem;
  background: var(--glass-bg-primary);
}

.faq-answer p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.faq-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.faq-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.faq-link:hover {
  color: var(--primary-hover);
}

.contact-section {
  margin-bottom: 3rem;
}

.contact-section h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--text-primary);
  font-weight: 600;
}

.contact-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.contact-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.contact-card:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.contact-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin: 0 auto 1.5rem;
}

.contact-info h3 {
  margin: 0 0 0.75rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.contact-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.availability,
.response-time,
.tracking {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
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
  padding: 1.5rem;
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
  font-size: 1.2rem;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.article-content {
  max-width: 700px;
  margin: 0 auto;
}

.article-meta-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.article-body {
  line-height: 1.8;
  color: var(--text-primary);
  margin-bottom: 2rem;
}

.related-articles h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.related-link {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  text-decoration: none;
  transition: all 0.3s ease;
}

.related-link:hover {
  background: var(--glass-bg-hover);
  color: var(--primary-color);
}

.tutorial-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.video-container {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  height: 0;
  overflow: hidden;
  border-radius: 8px;
}

.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

@media (max-width: 768px) {
  .help {
    padding: 1rem;
  }
  
  .search-section {
    padding: 1.5rem;
  }
  
  .quick-links {
    flex-direction: column;
  }
  
  .articles-grid {
    grid-template-columns: 1fr;
  }
  
  .popular-articles {
    grid-template-columns: 1fr;
  }
  
  .tutorials-grid {
    grid-template-columns: 1fr;
  }
  
  .contact-options {
    grid-template-columns: 1fr;
  }
  
  .tutorial-content {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
