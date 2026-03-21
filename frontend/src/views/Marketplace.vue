<template>
  <div class="marketplace">
    <div class="page-header">
      <h1>Marketplace</h1>
      <p>Discover apps, integrations, and services</p>
    </div>

    <!-- Search and Filter -->
    <div class="search-section">
      <div class="search-controls">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search apps and integrations..."
            @input="filterItems"
          />
        </div>
        <div class="filter-dropdown">
          <select v-model="categoryFilter" @change="filterItems">
            <option value="">All Categories</option>
            <option value="productivity">Productivity</option>
            <option value="analytics">Analytics</option>
            <option value="communication">Communication</option>
            <option value="development">Development</option>
            <option value="design">Design</option>
            <option value="marketing">Marketing</option>
            <option value="sales">Sales</option>
            <option value="finance">Finance</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="priceFilter" @change="filterItems">
            <option value="">All Prices</option>
            <option value="free">Free</option>
            <option value="paid">Paid</option>
            <option value="freemium">Freemium</option>
          </select>
        </div>
        <div class="filter-dropdown">
          <select v-model="ratingFilter" @change="filterItems">
            <option value="">All Ratings</option>
            <option value="4">4+ Stars</option>
            <option value="3">3+ Stars</option>
            <option value="2">2+ Stars</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Featured Items -->
    <div class="featured-section">
      <div class="section-header">
        <h2>Featured Apps</h2>
        <button class="view-all-btn" @click="viewAllFeatured">
          View All
        </button>
      </div>

      <div class="featured-carousel">
        <div class="carousel-container">
          <div class="featured-grid">
            <div 
              v-for="item in featuredItems" 
              :key="item.id"
              class="featured-card"
              @click="viewItemDetails(item)"
            >
              <div class="featured-badge">
                <i class="fas fa-star"></i>
                Featured
              </div>
              <div class="app-icon">
                <img :src="item.icon" :alt="item.name" />
              </div>
              <div class="app-info">
                <h3>{{ item.name }}</h3>
                <p>{{ item.description }}</p>
                <div class="app-meta">
                  <span class="category">{{ item.category }}</span>
                  <span class="price">{{ item.price }}</span>
                </div>
                <div class="rating">
                  <div class="stars">
                    <i 
                      v-for="star in 5" 
                      :key="star"
                      :class="['fas fa-star', { 'filled': star <= item.rating }]"
                    ></i>
                  </div>
                  <span class="rating-count">({{ item.reviews }})</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Categories -->
    <div class="categories-section">
      <div class="section-header">
        <h2>Browse Categories</h2>
      </div>

      <div class="categories-grid">
        <div 
          v-for="category in categories" 
          :key="category.id"
          class="category-card"
          @click="filterByCategory(category.id)"
        >
          <div class="category-icon">
            <i :class="category.icon"></i>
          </div>
          <h3>{{ category.name }}</h3>
          <p>{{ category.count }} apps</p>
        </div>
      </div>
    </div>

    <!-- Marketplace Items -->
    <div class="items-section">
      <div class="section-header">
        <h2>All Apps & Integrations</h2>
        <div class="header-actions">
          <div class="sort-dropdown">
            <select v-model="sortBy" @change="sortItems">
              <option value="popular">Most Popular</option>
              <option value="newest">Newest</option>
              <option value="rating">Highest Rated</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
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
        <p>Loading marketplace items...</p>
      </div>

      <div v-else-if="filteredItems.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-store"></i>
        </div>
        <h3>No items found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="items-grid">
          <div 
            v-for="item in filteredItems" 
            :key="item.id"
            class="item-card"
            @click="viewItemDetails(item)"
          >
            <div class="item-header">
              <div class="app-icon">
                <img :src="item.icon" :alt="item.name" />
              </div>
              <div class="item-actions">
                <button 
                  class="action-btn favorite"
                  @click.stop="toggleFavorite(item)"
                  :class="{ 'active': item.isFavorite }"
                >
                  <i :class="item.isFavorite ? 'fas fa-heart' : 'far fa-heart'"></i>
                </button>
              </div>
            </div>

            <div class="item-content">
              <h3>{{ item.name }}</h3>
              <p>{{ item.shortDescription }}</p>
              
              <div class="item-meta">
                <span class="category">{{ item.category }}</span>
                <span class="developer">{{ item.developer }}</span>
              </div>

              <div class="rating">
                <div class="stars">
                  <i 
                    v-for="star in 5" 
                    :key="star"
                    :class="['fas fa-star', { 'filled': star <= item.rating }]"
                  ></i>
                </div>
                <span class="rating-count">({{ item.reviews }})</span>
              </div>

              <div class="price-section">
                <span class="price">{{ item.price }}</span>
                <button 
                  class="install-btn"
                  @click.stop="installItem(item)"
                  :disabled="item.installed"
                >
                  {{ item.installed ? 'Installed' : 'Install' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="items-list">
          <div 
            v-for="item in filteredItems" 
            :key="item.id"
            class="item-list-card"
            @click="viewItemDetails(item)"
          >
            <div class="item-list-header">
              <div class="app-icon">
                <img :src="item.icon" :alt="item.name" />
              </div>
              <div class="item-list-content">
                <div class="item-list-info">
                  <h3>{{ item.name }}</h3>
                  <p>{{ item.shortDescription }}</p>
                  <div class="item-list-meta">
                    <span class="category">{{ item.category }}</span>
                    <span class="developer">{{ item.developer }}</span>
                    <span class="price">{{ item.price }}</span>
                  </div>
                </div>
                <div class="item-list-rating">
                  <div class="stars">
                    <i 
                      v-for="star in 5" 
                      :key="star"
                      :class="['fas fa-star', { 'filled': star <= item.rating }]"
                    ></i>
                  </div>
                  <span class="rating-count">({{ item.reviews }})</span>
                </div>
              </div>
              <div class="item-list-actions">
                <button 
                  class="action-btn favorite"
                  @click.stop="toggleFavorite(item)"
                  :class="{ 'active': item.isFavorite }"
                >
                  <i :class="item.isFavorite ? 'fas fa-heart' : 'far fa-heart'"></i>
                </button>
                <button 
                  class="install-btn"
                  @click.stop="installItem(item)"
                  :disabled="item.installed"
                >
                  {{ item.installed ? 'Installed' : 'Install' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Item Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <div class="app-header-info">
            <div class="app-icon large">
              <img :src="selectedItem?.icon" :alt="selectedItem?.name" />
            </div>
            <div class="app-details">
              <h2>{{ selectedItem?.name }}</h2>
              <p>{{ selectedItem?.description }}</p>
              <div class="app-meta-info">
                <span class="category">{{ selectedItem?.category }}</span>
                <span class="developer">by {{ selectedItem?.developer }}</span>
                <div class="rating">
                  <div class="stars">
                    <i 
                      v-for="star in 5" 
                      :key="star"
                      :class="['fas fa-star', { 'filled': star <= selectedItem?.rating }]"
                    ></i>
                  </div>
                  <span class="rating-count">({{ selectedItem?.reviews }})</span>
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
              <h3>About</h3>
              <p>{{ selectedItem?.fullDescription }}</p>
            </div>

            <div class="details-section">
              <h3>Features</h3>
              <div class="features-list">
                <div 
                  v-for="feature in selectedItem?.features" 
                  :key="feature"
                  class="feature-item"
                >
                  <i class="fas fa-check"></i>
                  <span>{{ feature }}</span>
                </div>
              </div>
            </div>

            <div class="details-section">
              <h3>Screenshots</h3>
              <div class="screenshots-carousel">
                <div 
                  v-for="(screenshot, index) in selectedItem?.screenshots" 
                  :key="index"
                  class="screenshot"
                >
                  <img :src="screenshot" :alt="`Screenshot ${index + 1}`" />
                </div>
              </div>
            </div>

            <div class="details-section">
              <h3>Pricing</h3>
              <div class="pricing-options">
                <div 
                  v-for="plan in selectedItem?.pricing" 
                  :key="plan.name"
                  class="pricing-card"
                >
                  <h4>{{ plan.name }}</h4>
                  <div class="price">{{ plan.price }}</div>
                  <p>{{ plan.description }}</p>
                  <ul>
                    <li 
                      v-for="feature in plan.features" 
                      :key="feature"
                    >
                      {{ feature }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="details-section">
              <h3>Reviews</h3>
              <div class="reviews-summary">
                <div class="rating-summary">
                  <div class="average-rating">
                    <span class="rating-number">{{ selectedItem?.rating }}</span>
                    <div class="stars large">
                      <i 
                        v-for="star in 5" 
                        :key="star"
                        :class="['fas fa-star', { 'filled': star <= selectedItem?.rating }]"
                      ></i>
                    </div>
                    <span class="total-reviews">{{ selectedItem?.reviews }} reviews</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div class="footer-actions">
            <button class="btn-secondary" @click="closeDetailsModal">Close</button>
            <button 
              class="btn-primary"
              @click="installItem(selectedItem)"
              :disabled="selectedItem?.installed"
            >
              {{ selectedItem?.installed ? 'Installed' : 'Install App' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const searchQuery = ref('')
const categoryFilter = ref('')
const priceFilter = ref('')
const ratingFilter = ref('')
const sortBy = ref('popular')
const viewMode = ref('grid')
const showDetailsModal = ref(false)
const selectedItem = ref(null)

// Mock data
const marketplaceItems = ref([
  {
    id: 1,
    name: 'Analytics Pro',
    description: 'Advanced analytics and reporting tools',
    shortDescription: 'Advanced analytics and reporting',
    icon: 'https://via.placeholder.com/100x100?text=AP',
    category: 'analytics',
    developer: 'Analytics Corp',
    price: '$29/month',
    rating: 4.5,
    reviews: 234,
    isFavorite: false,
    installed: false,
    featured: true,
    fullDescription: 'Comprehensive analytics platform with real-time data visualization, custom dashboards, and advanced reporting features.',
    features: [
      'Real-time analytics',
      'Custom dashboards',
      'Advanced reporting',
      'Data export',
      'Team collaboration'
    ],
    screenshots: [
      'https://via.placeholder.com/600x400?text=Dashboard',
      'https://via.placeholder.com/600x400?text=Reports',
      'https://via.placeholder.com/600x400?text=Analytics'
    ],
    pricing: [
      {
        name: 'Starter',
        price: '$29/month',
        description: 'Perfect for small teams',
        features: ['Basic analytics', '5 users', 'Email support']
      },
      {
        name: 'Professional',
        price: '$99/month',
        description: 'For growing businesses',
        features: ['Advanced analytics', 'Unlimited users', 'Priority support']
      }
    ]
  },
  {
    id: 2,
    name: 'Team Chat',
    description: 'Real-time team communication and collaboration',
    shortDescription: 'Real-time team communication',
    icon: 'https://via.placeholder.com/100x100?text=TC',
    category: 'communication',
    developer: 'Chat Solutions',
    price: 'Free',
    rating: 4.8,
    reviews: 567,
    isFavorite: true,
    installed: true,
    featured: true,
    fullDescription: 'Modern team communication platform with real-time messaging, file sharing, and integrations.',
    features: [
      'Real-time messaging',
      'File sharing',
      'Video calls',
      'Integrations',
      'Mobile apps'
    ],
    screenshots: [
      'https://via.placeholder.com/600x400?text=Chat',
      'https://via.placeholder.com/600x400?text=Channels',
      'https://via.placeholder.com/600x400?text=Integrations'
    ],
    pricing: [
      {
        name: 'Free',
        price: 'Free',
        description: 'Basic features for small teams',
        features: ['Chat', 'File sharing', '5 integrations']
      },
      {
        name: 'Pro',
        price: '$8/user/month',
        description: 'Advanced features for teams',
        features: ['Unlimited integrations', 'Video calls', 'Priority support']
      }
    ]
  },
  {
    id: 3,
    name: 'Design System',
    description: 'Complete design system and component library',
    shortDescription: 'Design system and components',
    icon: 'https://via.placeholder.com/100x100?text=DS',
    category: 'design',
    developer: 'Design Tools Inc',
    price: '$49/month',
    rating: 4.6,
    reviews: 189,
    isFavorite: false,
    installed: false,
    featured: false,
    fullDescription: 'Comprehensive design system with reusable components, design tokens, and documentation.',
    features: [
      'Component library',
      'Design tokens',
      'Documentation',
      'Theme system',
      'Figma plugin'
    ],
    screenshots: [
      'https://via.placeholder.com/600x400?text=Components',
      'https://via.placeholder.com/600x400?text=Tokens',
      'https://via.placeholder.com/600x400?text=Documentation'
    ],
    pricing: [
      {
        name: 'Team',
        price: '$49/month',
        description: 'For design teams',
        features: ['All components', 'Unlimited projects', 'Team collaboration']
      }
    ]
  }
])

const categories = ref([
  { id: 'productivity', name: 'Productivity', icon: 'fas fa-tasks', count: 45 },
  { id: 'analytics', name: 'Analytics', icon: 'fas fa-chart-line', count: 32 },
  { id: 'communication', name: 'Communication', icon: 'fas fa-comments', count: 28 },
  { id: 'development', name: 'Development', icon: 'fas fa-code', count: 56 },
  { id: 'design', name: 'Design', icon: 'fas fa-palette', count: 23 },
  { id: 'marketing', name: 'Marketing', icon: 'fas fa-bullhorn', count: 19 },
  { id: 'sales', name: 'Sales', icon: 'fas fa-chart-bar', count: 15 },
  { id: 'finance', name: 'Finance', icon: 'fas fa-dollar-sign', count: 12 }
])

// Computed properties
const featuredItems = computed(() => {
  return marketplaceItems.value.filter(item => item.featured)
})

const filteredItems = computed(() => {
  let filtered = marketplaceItems.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item => 
      item.name.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query) ||
      item.developer.toLowerCase().includes(query)
    )
  }

  // Apply category filter
  if (categoryFilter.value) {
    filtered = filtered.filter(item => item.category === categoryFilter.value)
  }

  // Apply price filter
  if (priceFilter.value) {
    filtered = filtered.filter(item => {
      if (priceFilter.value === 'free') return item.price === 'Free'
      if (priceFilter.value === 'paid') return item.price !== 'Free'
      if (priceFilter.value === 'freemium') return item.price.includes('Free')
      return true
    })
  }

  // Apply rating filter
  if (ratingFilter.value) {
    const minRating = parseInt(ratingFilter.value)
    filtered = filtered.filter(item => item.rating >= minRating)
  }

  // Apply sorting
  if (sortBy.value === 'popular') {
    filtered.sort((a, b) => b.reviews - a.reviews)
  } else if (sortBy.value === 'newest') {
    filtered.sort((a, b) => b.id - a.id)
  } else if (sortBy.value === 'rating') {
    filtered.sort((a, b) => b.rating - a.rating)
  } else if (sortBy.value === 'price-low') {
    filtered.sort((a, b) => {
      const priceA = parseInt(a.price.replace(/[^0-9]/g, '')) || 0
      const priceB = parseInt(b.price.replace(/[^0-9]/g, '')) || 0
      return priceA - priceB
    })
  } else if (sortBy.value === 'price-high') {
    filtered.sort((a, b) => {
      const priceA = parseInt(a.price.replace(/[^0-9]/g, '')) || 0
      const priceB = parseInt(b.price.replace(/[^0-9]/g, '')) || 0
      return priceB - priceA
    })
  }

  return filtered
})

// Methods
const loadMarketplaceData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/marketplace')
    // if (response.success) {
    //   marketplaceItems.value = response.items || []
    //   categories.value = response.categories || []
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading marketplace data:', error)
    showError('Failed to load marketplace data')
  } finally {
    loading.value = false
  }
}

const filterItems = () => {
  // This is reactive, no additional action needed
}

const sortItems = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (searchQuery.value || categoryFilter.value || priceFilter.value || ratingFilter.value) {
    return 'No items match your search criteria'
  }
  return 'No items available in the marketplace'
}

const filterByCategory = (categoryId) => {
  categoryFilter.value = categoryId
}

const viewAllFeatured = () => {
  // Navigate to featured items or filter by featured
  showSuccess('Viewing all featured items')
}

const viewItemDetails = (item) => {
  selectedItem.value = item
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedItem.value = null
}

const toggleFavorite = async (item) => {
  try {
    // const response = await apiPut(`/marketplace/items/${item.id}/favorite`)
    // if (response.success) {
    //   item.isFavorite = !item.isFavorite
    //   showSuccess(item.isFavorite ? 'Added to favorites' : 'Removed from favorites')
    // }
    
    // For demo, simulate toggle
    item.isFavorite = !item.isFavorite
    showSuccess(item.isFavorite ? 'Added to favorites' : 'Removed from favorites')
  } catch (error) {
    console.error('Error toggling favorite:', error)
    showError('Failed to update favorites')
  }
}

const installItem = async (item) => {
  if (item.installed) return

  try {
    // const response = await apiPost(`/marketplace/items/${item.id}/install`)
    // if (response.success) {
    //   item.installed = true
    //   showSuccess('App installed successfully')
    // }
    
    // For demo, simulate installation
    item.installed = true
    showSuccess('App installed successfully')
  } catch (error) {
    console.error('Error installing app:', error)
    showError('Failed to install app')
  }
}

// Lifecycle
onMounted(() => {
  loadMarketplaceData()
})
</script>

<style scoped>
.marketplace {
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

.featured-section,
.categories-section,
.items-section {
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

.view-all-btn {
  padding: 0.75rem 1.25rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-all-btn:hover {
  background: var(--primary-hover);
}

.featured-carousel {
  position: relative;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.featured-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.featured-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.featured-badge {
  position: absolute;
  top: -10px;
  right: 20px;
  background: var(--warning-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.app-icon {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  overflow: hidden;
  margin: 0 auto 1rem;
  background: var(--glass-bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-icon img {
  width: 60px;
  height: 60px;
  object-fit: contain;
}

.app-icon.large {
  width: 120px;
  height: 120px;
}

.app-icon.large img {
  width: 100px;
  height: 100px;
}

.app-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  text-align: center;
}

.app-info p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.5;
}

.app-meta {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.category,
.developer,
.price {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.price {
  background: var(--success-color);
  color: white;
}

.rating {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.stars {
  display: flex;
  gap: 0.25rem;
}

.stars .fas.fa-star {
  color: var(--warning-color);
}

.stars .fas.fa-star.filled {
  color: var(--warning-color);
}

.rating-count {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
}

.category-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-2px);
  background: var(--glass-bg-hover);
}

.category-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
}

.category-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.category-card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.sort-dropdown select {
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

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.item-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.item-actions {
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

.item-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.item-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.price-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.install-btn {
  padding: 0.5rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.install-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.install-btn:disabled {
  background: var(--glass-bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.item-list-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.item-list-card:hover {
  background: var(--glass-bg-hover);
}

.item-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.item-list-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-list-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.item-list-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
}

.item-list-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
}

.item-list-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.item-list-actions {
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
  max-width: 1200px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 2rem;
  border-bottom: 1px solid var(--glass-border);
}

.app-header-info {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.app-details h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.8rem;
}

.app-details p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.app-meta-info {
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

.features-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border-radius: 8px;
}

.feature-item i {
  color: var(--success-color);
}

.screenshots-carousel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.screenshot {
  border-radius: 8px;
  overflow: hidden;
}

.screenshot img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.pricing-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.pricing-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.pricing-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.pricing-card .price {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.pricing-card p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
}

.pricing-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.pricing-card li {
  padding: 0.5rem 0;
  color: var(--text-secondary);
}

.pricing-card li::before {
  content: "✓";
  color: var(--success-color);
  margin-right: 0.5rem;
}

.reviews-summary {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
}

.average-rating {
  text-align: center;
}

.rating-number {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  display: block;
  margin-bottom: 0.5rem;
}

.stars.large {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.stars.large .fas.fa-star {
  font-size: 1.5rem;
}

.total-reviews {
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
  .marketplace {
    padding: 1rem;
  }
  
  .search-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-box {
    min-width: 100%;
  }
  
  .featured-grid {
    grid-template-columns: 1fr;
  }
  
  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .items-grid {
    grid-template-columns: 1fr;
  }
  
  .item-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .item-list-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .app-header-info {
    flex-direction: column;
    gap: 1rem;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
