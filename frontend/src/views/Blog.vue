<template>
  <div class="blog">
    <div class="page-header">
      <h1>Blog</h1>
      <p>Insights, tutorials, and industry news</p>
    </div>

    <div class="blog-container">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-content">
          <div class="hero-text">
            <h2>{{ blogData.title }}</h2>
            <p class="hero-tagline">{{ blogData.tagline }}</p>
            <p class="hero-description">{{ blogData.description }}</p>
            <div class="hero-stats">
              <div class="stat-item">
                <div class="stat-number">{{ blogData.stats.posts }}</div>
                <div class="stat-label">Posts</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ blogData.stats.authors }}</div>
                <div class="stat-label">Authors</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ blogData.stats.categories }}</div>
                <div class="stat-label">Categories</div>
              </div>
            </div>
          </div>
          <div class="hero-image">
            <div class="image-placeholder">
              <i class="fas fa-blog"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- Featured Post -->
      <section class="featured-section" v-if="featuredPost">
        <div class="section-header">
          <h2>Featured Post</h2>
        </div>
        <div class="featured-post" @click="viewPost(featuredPost)">
          <div class="featured-image">
            <img :src="featuredPost.image" :alt="featuredPost.title" />
          </div>
          <div class="featured-content">
            <div class="post-meta">
              <span class="category">{{ featuredPost.category }}</span>
              <span class="date">{{ formatDate(featuredPost.date) }}</span>
              <span class="read-time">{{ featuredPost.readTime }} min read</span>
            </div>
            <h3>{{ featuredPost.title }}</h3>
            <p class="excerpt">{{ featuredPost.excerpt }}</p>
            <div class="author-info">
              <img :src="featuredPost.author.avatar" :alt="featuredPost.author.name" class="author-avatar" />
              <div class="author-details">
                <span class="author-name">{{ featuredPost.author.name }}</span>
                <span class="author-title">{{ featuredPost.author.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Blog Posts -->
      <section class="posts-section">
        <div class="section-header">
          <h2>Latest Posts</h2>
          <div class="header-actions">
            <div class="filter-dropdown">
              <select v-model="categoryFilter" @change="filterPosts">
                <option value="">All Categories</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>
            <div class="filter-dropdown">
              <select v-model="sortBy" @change="sortPosts">
                <option value="date">Latest</option>
                <option value="popular">Most Popular</option>
                <option value="trending">Trending</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading posts...</p>
        </div>

        <div v-else-if="filteredPosts.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-newspaper"></i>
          </div>
          <h3>No posts found</h3>
          <p>Try adjusting your filters or check back later for new content.</p>
        </div>

        <div v-else class="posts-grid">
          <div 
            v-for="post in paginatedPosts" 
            :key="post.id"
            class="post-card"
            @click="viewPost(post)"
          >
            <div class="post-image">
              <img :src="post.image" :alt="post.title" />
              <div class="post-overlay">
                <button class="read-btn">Read More</button>
              </div>
            </div>
            <div class="post-content">
              <div class="post-meta">
                <span class="category" :class="post.category">{{ post.category }}</span>
                <span class="date">{{ formatDate(post.date) }}</span>
                <span class="read-time">{{ post.readTime }} min read</span>
              </div>
              <h3>{{ post.title }}</h3>
              <p class="excerpt">{{ post.excerpt }}</p>
              <div class="post-stats">
                <div class="stat">
                  <i class="fas fa-eye"></i>
                  <span>{{ formatNumber(post.views) }}</span>
                </div>
                <div class="stat">
                  <i class="fas fa-heart"></i>
                  <span>{{ formatNumber(post.likes) }}</span>
                </div>
                <div class="stat">
                  <i class="fas fa-comment"></i>
                  <span>{{ post.comments }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination" v-if="totalPages > 1">
          <button 
            class="pagination-btn" 
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button 
            class="pagination-btn" 
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </section>

      <!-- Categories -->
      <section class="categories-section">
        <div class="section-header">
          <h2>Categories</h2>
          <p>Explore content by topic</p>
        </div>
        <div class="categories-grid">
          <div 
            v-for="category in categoryData" 
            :key="category.name"
            class="category-card"
            @click="filterByCategory(category.name)"
          >
            <div class="category-icon">
              <i :class="category.icon"></i>
            </div>
            <h3>{{ category.name }}</h3>
            <p>{{ category.description }}</p>
            <span class="post-count">{{ category.count }} posts</span>
          </div>
        </div>
      </section>

      <!-- Authors -->
      <section class="authors-section">
        <div class="section-header">
          <h2>Our Authors</h2>
          <p>Meet the people behind our content</p>
        </div>
        <div class="authors-grid">
          <div 
            v-for="author in authors" 
            :key="author.id"
            class="author-card"
            @click="viewAuthor(author)"
          >
            <div class="author-avatar">
              <img :src="author.avatar" :alt="author.name" />
            </div>
            <div class="author-info">
              <h3>{{ author.name }}</h3>
              <p class="author-title">{{ author.title }}</p>
              <p class="author-bio">{{ author.bio }}</p>
              <div class="author-stats">
                <div class="stat">
                  <span class="stat-number">{{ author.posts }}</span>
                  <span class="stat-label">Posts</span>
                </div>
                <div class="stat">
                  <span class="stat-number">{{ author.followers }}</span>
                  <span class="stat-label">Followers</span>
                </div>
              </div>
              <div class="author-social">
                <a v-if="author.twitter" :href="author.twitter" class="social-link">
                  <i class="fab fa-twitter"></i>
                </a>
                <a v-if="author.linkedin" :href="author.linkedin" class="social-link">
                  <i class="fab fa-linkedin"></i>
                </a>
                <a v-if="author.website" :href="author.website" class="social-link">
                  <i class="fas fa-globe"></i>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Newsletter Signup -->
      <section class="newsletter-section">
        <div class="section-header">
          <h2>Stay Updated</h2>
          <p>Get the latest posts delivered to your inbox</p>
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
                <label for="interests">Interests</label>
                <div class="interests-grid">
                  <label class="checkbox-label" v-for="interest in interests" :key="interest">
                    <input 
                      type="checkbox" 
                      v-model="newsletterForm.interests"
                      :value="interest"
                      :id="`interest-${interest}`"
                    />
                    <span class="checkmark"></span>
                    {{ interest }}
                  </label>
                </div>
              </div>
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    v-model="newsletterForm.weekly"
                    id="weekly"
                  />
                  <span class="checkmark"></span>
                  Send weekly digest instead of instant updates
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
              <h3>Never Miss a Post</h3>
              <p>Get instant notifications when new content is published.</p>
            </div>
            <div class="info-card">
              <div class="info-icon">
                <i class="fas fa-filter"></i>
              </div>
              <h3>Personalized Content</h3>
              <p>Receive posts tailored to your interests and reading habits.</p>
            </div>
            <div class="info-card">
              <div class="info-icon">
                <i class="fas fa-times-circle"></i>
              </div>
              <h3>Easy Unsubscribe</h3>
              <p>Unsubscribe at any time with a single click.</p>
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
const categoryFilter = ref('')
const sortBy = ref('date')
const currentPage = ref(1)
const postsPerPage = ref(9)
const isSubscribing = ref(false)

// Newsletter form
const newsletterForm = reactive({
  email: '',
  interests: [],
  weekly: false
})

// Blog data
const blogData = reactive({
  title: 'Digital HQ Blog',
  tagline: 'Insights & Innovation',
  description: 'Explore our latest thoughts on technology, business, and digital transformation. Get expert insights, tutorials, and industry news from our team of experts.',
  stats: {
    posts: 150,
    authors: 12,
    categories: 8
  }
})

// Categories
const categories = ref([
  'Technology',
  'Business',
  'Design',
  'Marketing',
  'Development',
  'Innovation',
  'Strategy',
  'Tutorials'
])

const categoryData = ref([
  {
    name: 'Technology',
    description: 'Latest tech trends and innovations',
    icon: 'fas fa-microchip',
    count: 45
  },
  {
    name: 'Business',
    description: 'Business strategy and insights',
    icon: 'fas fa-briefcase',
    count: 32
  },
  {
    name: 'Design',
    description: 'UI/UX design principles and trends',
    icon: 'fas fa-palette',
    count: 28
  },
  {
    name: 'Marketing',
    description: 'Digital marketing strategies',
    icon: 'fas fa-bullhorn',
    count: 20
  },
  {
    name: 'Development',
    description: 'Coding tutorials and best practices',
    icon: 'fas fa-code',
    count: 35
  },
  {
    name: 'Innovation',
    description: 'Cutting-edge innovations',
    icon: 'fas fa-lightbulb',
    count: 18
  }
])

// Authors
const authors = ref([
  {
    id: 1,
    name: 'Sarah Johnson',
    title: 'Tech Lead',
    bio: 'Passionate about emerging technologies and their impact on business transformation.',
    avatar: '/api/placeholder/100x100',
    posts: 25,
    followers: 1200,
    twitter: 'https://twitter.com/sarahjohnson',
    linkedin: 'https://linkedin.com/in/sarahjohnson',
    website: 'https://sarahjohnson.com'
  },
  {
    id: 2,
    name: 'Michael Chen',
    title: 'Product Designer',
    bio: 'Creating intuitive user experiences through thoughtful design and user research.',
    avatar: '/api/placeholder/100x100',
    posts: 18,
    followers: 800,
    linkedin: 'https://linkedin.com/in/michaelchen',
    website: 'https://michaelchen.design'
  },
  {
    id: 3,
    name: 'Emily Rodriguez',
    title: 'Marketing Expert',
    bio: 'Helping businesses grow through innovative digital marketing strategies.',
    avatar: '/api/placeholder/100x100',
    posts: 22,
    followers: 950,
    twitter: 'https://twitter.com/emilyrodriguez',
    linkedin: 'https://linkedin.com/in/emilyrodriguez'
  }
])

// Newsletter interests
const interests = ref([
  'Technology',
  'Business',
  'Design',
  'Marketing',
  'Development',
  'Innovation'
])

// Blog posts
const blogPosts = ref([
  {
    id: 1,
    title: 'The Future of AI in Business: Trends and Predictions for 2024',
    excerpt: 'Explore the latest AI trends shaping business in 2024, from machine learning advancements to practical implementation strategies.',
    content: 'Full blog post content here...',
    category: 'Technology',
    date: '2024-01-20T00:00:00Z',
    readTime: 8,
    image: '/api/placeholder/400x250',
    author: {
      name: 'Sarah Johnson',
      title: 'Tech Lead',
      avatar: '/api/placeholder/50x50'
    },
    views: 5420,
    likes: 234,
    comments: 45,
    featured: true
  },
  {
    id: 2,
    title: 'Building Scalable Applications: Best Practices for Modern Development',
    excerpt: 'Learn the essential principles and practices for building applications that can scale with your business growth.',
    content: 'Full blog post content here...',
    category: 'Development',
    date: '2024-01-18T00:00:00Z',
    readTime: 12,
    image: '/api/placeholder/400x250',
    author: {
      name: 'Michael Chen',
      title: 'Product Designer',
      avatar: '/api/placeholder/50x50'
    },
    views: 3200,
    likes: 156,
    comments: 28
  },
  {
    id: 3,
    title: 'User-Centered Design: Creating Products People Love',
    excerpt: 'Discover the principles of user-centered design and how to apply them to create products that users truly love.',
    content: 'Full blog post content here...',
    category: 'Design',
    date: '2024-01-15T00:00:00Z',
    readTime: 6,
    image: '/api/placeholder/400x250',
    author: {
      name: 'Emily Rodriguez',
      title: 'Marketing Expert',
      avatar: '/api/placeholder/50x50'
    },
    views: 2800,
    likes: 142,
    comments: 19
  },
  {
    id: 4,
    title: 'Digital Transformation: A Complete Guide for Modern Businesses',
    excerpt: 'Everything you need to know about digital transformation, from strategy to implementation and beyond.',
    content: 'Full blog post content here...',
    category: 'Business',
    date: '2024-01-12T00:00:00Z',
    readTime: 15,
    image: '/api/placeholder/400x250',
    author: {
      name: 'Sarah Johnson',
      title: 'Tech Lead',
      avatar: '/api/placeholder/50x50'
    },
    views: 4100,
    likes: 189,
    comments: 34
  },
  {
    id: 5,
    title: 'Marketing Automation: Tools and Strategies for Growth',
    excerpt: 'Explore the best marketing automation tools and strategies to scale your marketing efforts effectively.',
    content: 'Full blog post content here...',
    category: 'Marketing',
    date: '2024-01-10T00:00:00Z',
    readTime: 10,
    image: '/api/placeholder/400x250',
    author: {
      name: 'Emily Rodriguez',
      title: 'Marketing Expert',
      avatar: '/api/placeholder/50x50'
    },
    views: 2500,
    likes: 128,
    comments: 22
  }
])

// Computed properties
const featuredPost = computed(() => {
  return blogPosts.value.find(post => post.featured)
})

const filteredPosts = computed(() => {
  let filtered = blogPosts.value

  if (categoryFilter.value) {
    filtered = filtered.filter(post => post.category === categoryFilter.value)
  }

  // Sort posts
  if (sortBy.value === 'date') {
    filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
  } else if (sortBy.value === 'popular') {
    filtered.sort((a, b) => b.views - a.views)
  } else if (sortBy.value === 'trending') {
    filtered.sort((a, b) => b.likes - a.likes)
  }

  return filtered
})

const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * postsPerPage.value
  const end = start + postsPerPage.value
  return filteredPosts.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredPosts.value.length / postsPerPage.value)
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

const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

const filterPosts = () => {
  currentPage.value = 1
}

const sortPosts = () => {
  currentPage.value = 1
}

const filterByCategory = (category) => {
  categoryFilter.value = category
  currentPage.value = 1
}

const viewPost = (post) => {
  showSuccess(`Opening post: ${post.title}`)
  // In a real app, this would navigate to post details
}

const viewAuthor = (author) => {
  showSuccess(`Viewing posts by ${author.name}`)
  // In a real app, this would navigate to author page
}

const subscribeNewsletter = async () => {
  isSubscribing.value = true

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    showSuccess('Successfully subscribed to blog newsletter!')
    
    // Reset form
    Object.assign(newsletterForm, {
      email: '',
      interests: [],
      weekly: false
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
    // const response = await apiGet('/blog/posts')
    // if (response.success) {
    //   blogPosts.value = response.posts || []
    // }
    
    // For demo, use mock data
    loading.value = false
  } catch (error) {
    console.error('Error loading blog posts:', error)
    showError('Failed to load blog posts')
    loading.value = false
  }
})
</script>

<style scoped>
.blog {
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

.blog-container {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.hero-section,
.featured-section,
.posts-section,
.categories-section,
.authors-section,
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

.featured-post {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.featured-post:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.featured-image {
  height: 300px;
  overflow: hidden;
}

.featured-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.featured-content {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.post-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.category {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  width: fit-content;
}

.category.Technology {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.category.Business {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.category.Design {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.category.Marketing {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.category.Development {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.date,
.read-time {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.featured-content h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.featured-content .excerpt {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.author-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.author-name {
  color: var(--text-primary);
  font-weight: 600;
}

.author-title {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.post-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.post-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.post-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.post-card:hover .post-image img {
  transform: scale(1.05);
}

.post-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.post-card:hover .post-overlay {
  opacity: 1;
}

.read-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.read-btn:hover {
  background: var(--primary-hover);
}

.post-content {
  padding: 1.5rem;
}

.post-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.post-content .excerpt {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.post-stats {
  display: flex;
  gap: 1.5rem;
}

.post-stats .stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.post-stats .stat i {
  color: var(--primary-color);
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

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.category-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.category-icon {
  width: 60px;
  height: 60px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1.5rem;
}

.category-card h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.category-card p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.post-count {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.authors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.author-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.author-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.author-card .author-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
}

.author-info {
  text-align: center;
}

.author-info h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.author-info .author-title {
  color: var(--primary-color);
  font-weight: 600;
  margin-bottom: 1rem;
}

.author-info .author-bio {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.author-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.author-stats .stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.author-stats .stat-number {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.author-stats .stat-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.author-social {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.social-link {
  width: 40px;
  height: 40px;
  background: var(--glass-bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s ease;
}

.social-link:hover {
  background: var(--primary-color);
  color: white;
  transform: scale(1.1);
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

.interests-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
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

.checkmark {
  position: relative;
  padding-left: 1.5rem;
}

.checkmark::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  border: 2px solid var(--glass-border);
  border-radius: 4px;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::before {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  left: 2px;
  top: 50%;
  transform: translateY(-50%);
  color: white;
  font-weight: bold;
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
  .blog {
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
  
  .featured-post {
    grid-template-columns: 1fr;
  }
  
  .posts-grid,
  .categories-grid,
  .authors-grid {
    grid-template-columns: 1fr;
  }
  
  .newsletter-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .interests-grid {
    grid-template-columns: 1fr;
  }
}
</style>
