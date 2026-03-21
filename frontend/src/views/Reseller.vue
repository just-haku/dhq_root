<template>
  <div class="reseller">
    <div class="page-header">
      <h1>Reseller Program</h1>
      <p>Manage your reseller business and maximize your earnings</p>
    </div>

    <!-- Reseller Status -->
    <div class="status-section">
      <div class="section-header">
        <h2>Your Reseller Status</h2>
      </div>
      
      <div class="status-card">
        <div class="status-header">
          <div class="reseller-info">
            <div class="reseller-icon">
              <i class="fas fa-store"></i>
            </div>
            <div class="reseller-details">
              <h3>{{ resellerStatus.level }}</h3>
              <p>{{ resellerStatus.description }}</p>
            </div>
          </div>
          <div class="status-badge">
            <span :class="['badge', resellerStatus.status]">{{ formatStatus(resellerStatus.status) }}</span>
          </div>
        </div>
        
        <div class="status-stats">
          <div class="stat-item">
            <div class="stat-value">${{ resellerStats.totalRevenue.toLocaleString() }}</div>
            <div class="stat-label">Total Revenue</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ resellerStats.totalSales }}</div>
            <div class="stat-label">Total Sales</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ resellerStats.activeCustomers }}</div>
            <div class="stat-label">Active Customers</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ resellerStats.commissionRate }}%</div>
            <div class="stat-label">Commission Rate</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="section-header">
        <h2>Quick Actions</h2>
      </div>
      
      <div class="actions-grid">
        <div class="action-card" @click="showCustomerModal = true">
          <div class="action-icon">
            <i class="fas fa-user-plus"></i>
          </div>
          <h3>Add Customer</h3>
          <p>Register new customer</p>
        </div>
        
        <div class="action-card" @click="viewProducts">
          <div class="action-icon products">
            <i class="fas fa-box"></i>
          </div>
          <h3>Products</h3>
          <p>Browse reseller catalog</p>
        </div>
        
        <div class="action-card" @click="viewPricing">
          <div class="action-icon pricing">
            <i class="fas fa-tags"></i>
          </div>
          <h3>Pricing</h3>
          <p>Set customer pricing</p>
        </div>
        
        <div class="action-card" @click="viewAnalytics">
          <div class="action-icon analytics">
            <i class="fas fa-chart-line"></i>
          </div>
          <h3>Analytics</h3>
          <p>Track sales performance</p>
        </div>
      </div>
    </div>

    <!-- Products Catalog -->
    <div class="products-section">
      <div class="section-header">
        <h2>Reseller Products</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="productFilter" @change="filterProducts">
              <option value="">All Products</option>
              <option value="software">Software</option>
              <option value="hardware">Hardware</option>
              <option value="service">Services</option>
              <option value="bundle">Bundles</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="availabilityFilter" @change="filterProducts">
              <option value="">All Availability</option>
              <option value="available">Available</option>
              <option value="out-of-stock">Out of Stock</option>
              <option value="coming-soon">Coming Soon</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading products...</p>
      </div>

      <div v-else-if="filteredProducts.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-box"></i>
        </div>
        <h3>No products found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="products-grid">
        <div 
          v-for="product in filteredProducts" 
          :key="product.id"
          class="product-card"
          :class="{ 'out-of-stock': product.availability === 'out-of-stock' }"
        >
          <div class="product-header">
            <div class="product-image">
              <img :src="product.image" :alt="product.name" />
              <div class="product-badge" v-if="product.featured">
                <i class="fas fa-star"></i>
                Featured
              </div>
            </div>
            <div class="product-meta">
              <span :class="['availability-badge', product.availability]">{{ formatAvailability(product.availability) }}</span>
              <span class="product-category">{{ product.category }}</span>
            </div>
          </div>
          
          <div class="product-content">
            <h3>{{ product.name }}</h3>
            <p>{{ product.description }}</p>
            
            <div class="product-pricing">
              <div class="price-info">
                <span class="retail-price">Retail: ${{ product.retailPrice.toFixed(2) }}</span>
                <span class="reseller-price">Your Price: ${{ product.resellerPrice.toFixed(2) }}</span>
              </div>
              <div class="commission-info">
                <span class="commission-rate">Commission: {{ product.commissionRate }}%</span>
                <span class="profit-margin">Margin: {{ product.profitMargin }}%</span>
              </div>
            </div>
            
            <div class="product-features">
              <div class="feature-item" v-for="feature in product.features" :key="feature">
                <i class="fas fa-check"></i>
                {{ feature }}
              </div>
            </div>
          </div>
          
          <div class="product-footer">
            <div class="product-stats">
              <span class="sales-count">{{ product.sales }} sold</span>
              <span class="rating">{{ product.rating }}★</span>
            </div>
            <div class="product-actions">
              <button class="action-btn sell" @click="sellProduct(product)">
                <i class="fas fa-shopping-cart"></i>
                Sell
              </button>
              <button class="action-btn view" @click="viewProduct(product)">
                <i class="fas fa-eye"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Customers Management -->
    <div class="customers-section">
      <div class="section-header">
        <h2>Your Customers</h2>
        <div class="header-actions">
          <div class="search-box">
            <input 
              v-model="customerSearch" 
              type="text" 
              placeholder="Search customers..."
              @input="searchCustomers"
            />
            <i class="fas fa-search"></i>
          </div>
          <div class="filter-dropdown">
            <select v-model="customerFilter" @change="filterCustomers">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="trial">Trial</option>
              <option value="expired">Expired</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading customers...</p>
      </div>

      <div v-else-if="filteredCustomers.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-users"></i>
        </div>
        <h3>No customers found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="create-first-btn" @click="showCustomerModal = true">
          <i class="fas fa-plus"></i>
          Add Your First Customer
        </button>
      </div>

      <div v-else class="customers-table">
        <div class="table-header">
          <div class="header-cell">Customer</div>
          <div class="header-cell">Products</div>
          <div class="header-cell">Revenue</div>
          <div class="header-cell">Status</div>
          <div class="header-cell">Joined</div>
          <div class="header-cell">Actions</div>
        </div>
        
        <div 
          v-for="customer in filteredCustomers" 
          :key="customer.id"
          class="table-row"
        >
          <div class="table-cell">
            <div class="customer-info">
              <div class="customer-avatar">
                <img :src="customer.avatar" :alt="customer.name" />
              </div>
              <div class="customer-details">
                <span class="customer-name">{{ customer.name }}</span>
                <span class="customer-email">{{ customer.email }}</span>
              </div>
            </div>
          </div>
          
          <div class="table-cell">
            <span class="product-count">{{ customer.products.length }}</span>
          </div>
          
          <div class="table-cell">
            <span class="revenue-amount">${{ customer.revenue.toFixed(2) }}</span>
          </div>
          
          <div class="table-cell">
            <span :class="['status-badge', customer.status]">{{ formatCustomerStatus(customer.status) }}</span>
          </div>
          
          <div class="table-cell">
            <span class="join-date">{{ formatDate(customer.joinDate) }}</span>
          </div>
          
          <div class="table-cell">
            <div class="customer-actions">
              <button class="action-btn view" @click="viewCustomer(customer)">
                <i class="fas fa-eye"></i>
              </button>
              <button class="action-btn edit" @click="editCustomer(customer)">
                <i class="fas fa-edit"></i>
              </button>
              <button class="action-btn message" @click="messageCustomer(customer)">
                <i class="fas fa-envelope"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sales Analytics -->
    <div class="analytics-section">
      <div class="section-header">
        <h2>Sales Analytics</h2>
        <div class="header-actions">
          <div class="time-range">
            <select v-model="analyticsTimeRange" @change="updateAnalytics">
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="quarter">Last Quarter</option>
              <option value="year">Last Year</option>
            </select>
          </div>
        </div>
      </div>

      <div class="analytics-grid">
        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Sales Revenue</h3>
            <div class="analytics-value">${{ analytics.revenue.toLocaleString() }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="revenueChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Top Products</h3>
            <div class="analytics-value">{{ analytics.topProducts }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="productsChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Customer Growth</h3>
            <div class="analytics-value">{{ analytics.growth }}%</div>
          </div>
          <div class="chart-container">
            <canvas ref="growthChart"></canvas>
          </div>
        </div>

        <div class="analytics-card">
          <div class="analytics-header">
            <h3>Commission Earned</h3>
            <div class="analytics-value">${{ analytics.commission.toLocaleString() }}</div>
          </div>
          <div class="chart-container">
            <canvas ref="commissionChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Commission Structure -->
    <div class="commission-section">
      <div class="section-header">
        <h2>Commission Structure</h2>
      </div>

      <div class="commission-tiers">
        <div 
          v-for="tier in commissionTiers" 
          :key="tier.id"
          class="tier-card"
          :class="{ 'current': tier.id === resellerStatus.currentTier, 'recommended': tier.recommended }"
        >
          <div class="tier-header">
            <div class="tier-icon">
              <i :class="tier.icon"></i>
            </div>
            <div class="tier-info">
              <h3>{{ tier.name }}</h3>
              <p>{{ tier.description }}</p>
            </div>
            <div class="tier-badge">
              <span v-if="tier.id === resellerStatus.currentTier" class="current-badge">Current</span>
              <span v-if="tier.recommended" class="recommended-badge">Recommended</span>
            </div>
          </div>
          
          <div class="tier-commission">
            <div class="commission-rate">
              <span class="rate-value">{{ tier.commissionRate }}%</span>
              <span class="rate-label">Commission</span>
            </div>
            <div class="tier-requirements">
              <h4>Requirements:</h4>
              <ul>
                <li v-for="requirement in tier.requirements" :key="requirement">{{ requirement }}</li>
              </ul>
            </div>
          </div>
          
          <div class="tier-benefits">
            <h4>Benefits:</h4>
            <ul>
              <li v-for="benefit in tier.benefits" :key="benefit" class="benefit-item">
                <i class="fas fa-check"></i>
                {{ benefit }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Customer Modal -->
    <div v-if="showCustomerModal" class="modal-overlay" @click="closeCustomerModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add New Customer</h2>
          <button class="close-btn" @click="closeCustomerModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="customer-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Company Name *</label>
                <input 
                  v-model="customerForm.companyName" 
                  type="text" 
                  placeholder="Enter company name"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>Contact Name *</label>
                <input 
                  v-model="customerForm.contactName" 
                  type="text" 
                  placeholder="Enter contact name"
                  required
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Email *</label>
                <input 
                  v-model="customerForm.email" 
                  type="email" 
                  placeholder="Enter email address"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>Phone</label>
                <input 
                  v-model="customerForm.phone" 
                  type="tel" 
                  placeholder="Enter phone number"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Address</label>
              <input 
                v-model="customerForm.address" 
                type="text" 
                placeholder="Enter address"
              />
            </div>

            <div class="form-group">
              <label>Products to Assign</label>
              <div class="product-selection">
                <div 
                  v-for="product in availableProducts" 
                  :key="product.id"
                  class="product-option"
                >
                  <label class="checkbox-item">
                    <input 
                      type="checkbox" 
                      :value="product.id"
                      v-model="customerForm.products"
                    />
                    <span>{{ product.name }}</span>
                    <span class="product-price">${{ product.resellerPrice.toFixed(2) }}</span>
                  </label>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Pricing Tier</label>
              <select v-model="customerForm.pricingTier">
                <option value="standard">Standard</option>
                <option value="premium">Premium</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>

            <div class="form-group">
              <label>Notes</label>
              <textarea 
                v-model="customerForm.notes" 
                placeholder="Add any additional notes"
                rows="4"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeCustomerModal">Cancel</button>
          <button class="btn-primary" @click="addCustomer">
            <i class="fas fa-plus"></i>
            Add Customer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { Chart } from 'chart.js/auto'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const productFilter = ref('')
const availabilityFilter = ref('')
const customerSearch = ref('')
const customerFilter = ref('')
const analyticsTimeRange = ref('month')
const showCustomerModal = ref(false)

// Chart refs
const revenueChart = ref(null)
const productsChart = ref(null)
const growthChart = ref(null)
const commissionChart = ref(null)

// Reseller status
const resellerStatus = reactive({
  level: 'Gold Reseller',
  description: 'You are a top-performing reseller with premium benefits and higher commission rates',
  status: 'active',
  currentTier: 3,
  joinedDate: '2023-06-15T00:00:00Z'
})

// Reseller stats
const resellerStats = reactive({
  totalRevenue: 125000,
  totalSales: 450,
  activeCustomers: 78,
  commissionRate: 25
})

// Analytics data
const analytics = reactive({
  revenue: 45000,
  topProducts: 12,
  growth: 28,
  commission: 11250
})

// Customer form
const customerForm = reactive({
  companyName: '',
  contactName: '',
  email: '',
  phone: '',
  address: '',
  products: [],
  pricingTier: 'standard',
  notes: ''
})

// Products data
const products = ref([
  {
    id: 1,
    name: 'Professional Suite',
    description: 'Complete business solution with all premium features',
    category: 'software',
    availability: 'available',
    featured: true,
    image: '/api/placeholder/200x150',
    retailPrice: 299.99,
    resellerPrice: 199.99,
    commissionRate: 25,
    profitMargin: 33,
    features: ['Advanced Analytics', 'Priority Support', 'Custom Integrations', 'Unlimited Users'],
    sales: 145
  },
  {
    id: 2,
    name: 'Hardware Bundle Pro',
    description: 'Professional hardware bundle for enterprise needs',
    category: 'hardware',
    availability: 'available',
    featured: false,
    image: '/api/placeholder/200x150',
    retailPrice: 1299.99,
    resellerPrice: 899.99,
    commissionRate: 20,
    profitMargin: 31,
    features: ['Server Hardware', 'Networking Equipment', 'Storage Solutions', '24/7 Support'],
    sales: 67
  },
  {
    id: 3,
    name: 'Cloud Services',
    description: 'Scalable cloud infrastructure and services',
    category: 'service',
    availability: 'coming-soon',
    featured: false,
    image: '/api/placeholder/200x150',
    retailPrice: 199.99,
    resellerPrice: 149.99,
    commissionRate: 22,
    profitMargin: 25,
    features: ['Unlimited Storage', 'Auto Backup', '99.9% Uptime', 'Global CDN'],
    sales: 0
  }
])

// Customers data
const customers = ref([
  {
    id: 1,
    name: 'TechCorp Solutions',
    email: 'contact@techcorp.com',
    status: 'active',
    revenue: 12500,
    joinDate: '2023-08-15T00:00:00Z',
    avatar: '/api/placeholder/40x40',
    products: [1, 2]
  },
  {
    id: 2,
    name: 'Global Enterprises',
    email: 'sales@globalent.com',
    status: 'active',
    revenue: 8750,
    joinDate: '2023-10-20T00:00:00Z',
    avatar: '/api/placeholder/40x40',
    products: [1]
  },
  {
    id: 3,
    name: 'Startup Inc',
    email: 'founder@startup.com',
    status: 'trial',
    revenue: 0,
    joinDate: '2024-01-10T00:00:00Z',
    avatar: '/api/placeholder/40x40',
    products: [1]
  }
])

// Commission tiers
const commissionTiers = ref([
  {
    id: 1,
    name: 'Bronze Reseller',
    description: 'Entry-level reseller with basic benefits',
    icon: 'fas fa-medal',
    commissionRate: 15,
    requirements: ['0-10 customers', '$0-5,000 monthly revenue'],
    benefits: [
      '15% commission rate',
      'Basic support',
      'Standard marketing materials',
      'Monthly payments'
    ]
  },
  {
    id: 2,
    name: 'Silver Reseller',
    description: 'Intermediate reseller with enhanced benefits',
    icon: 'fas fa-award',
    commissionRate: 20,
    requirements: ['11-25 customers', '$5,001-15,000 monthly revenue'],
    benefits: [
      '20% commission rate',
      'Priority support',
      'Advanced marketing materials',
      'Bi-weekly payments',
      'Co-branded materials'
    ]
  },
  {
    id: 3,
    name: 'Gold Reseller',
    description: 'Premium reseller with maximum benefits',
    icon: 'fas fa-trophy',
    commissionRate: 25,
    recommended: true,
    requirements: ['26-50 customers', '$15,001+ monthly revenue'],
    benefits: [
      '25% commission rate',
      'Dedicated support',
      'Custom marketing materials',
      'Weekly payments',
      'Full branding options',
      'Lead generation program'
    ]
  },
  {
    id: 4,
    name: 'Platinum Reseller',
    description: 'Elite reseller with exclusive benefits',
    icon: 'fas fa-crown',
    commissionRate: 30,
    requirements: ['50+ customers', '$50,000+ monthly revenue'],
    benefits: [
      '30% commission rate',
      'White-glove support',
      'Exclusive marketing materials',
      'Daily payments',
      'Full white-label options',
      'Dedicated account manager',
      'Revenue sharing program'
    ]
  }
])

// Computed properties
const filteredProducts = computed(() => {
  let filtered = products.value

  if (productFilter.value) {
    filtered = filtered.filter(product => product.category === productFilter.value)
  }

  if (availabilityFilter.value) {
    filtered = filtered.filter(product => product.availability === availabilityFilter.value)
  }

  return filtered.sort((a, b) => b.sales - a.sales)
})

const filteredCustomers = computed(() => {
  let filtered = customers.value

  if (customerSearch.value) {
    const query = customerSearch.value.toLowerCase()
    filtered = filtered.filter(customer => 
      customer.name.toLowerCase().includes(query) ||
      customer.email.toLowerCase().includes(query)
    )
  }

  if (customerFilter.value) {
    filtered = filtered.filter(customer => customer.status === customerFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.joinDate) - new Date(a.joinDate))
})

const availableProducts = computed(() => {
  return products.value.filter(product => product.availability === 'available')
})

// Methods
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatAvailability = (availability) => {
  return availability.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatCustomerStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getEmptyMessage = () => {
  if (productFilter.value || availabilityFilter.value || customerSearch.value || customerFilter.value) {
    return 'No items match your search criteria'
  }
  return 'No items found'
}

const filterProducts = () => {
  // Filtering is handled by computed property
}

const searchCustomers = () => {
  // Search is handled by computed property
}

const filterCustomers = () => {
  // Filtering is handled by computed property
}

const viewProducts = () => {
  showSuccess('Viewing reseller products catalog')
}

const viewPricing = () => {
  showSuccess('Opening pricing management')
}

const viewAnalytics = () => {
  showSuccess('Opening sales analytics')
}

const sellProduct = (product) => {
  showSuccess(`Opening sales process for ${product.name}`)
}

const viewProduct = (product) => {
  showSuccess(`Viewing product details: ${product.name}`)
}

const viewCustomer = (customer) => {
  showSuccess(`Viewing customer: ${customer.name}`)
}

const editCustomer = (customer) => {
  showSuccess(`Editing customer: ${customer.name}`)
}

const messageCustomer = (customer) => {
  showSuccess(`Opening message to ${customer.name}`)
}

const closeCustomerModal = () => {
  showCustomerModal.value = false
  resetCustomerForm()
}

const resetCustomerForm = () => {
  Object.assign(customerForm, {
    companyName: '',
    contactName: '',
    email: '',
    phone: '',
    address: '',
    products: [],
    pricingTier: 'standard',
    notes: ''
  })
}

const addCustomer = async () => {
  if (!customerForm.companyName || !customerForm.contactName || !customerForm.email) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/reseller/customers', customerForm)
    // if (response.success) {
    //   customers.value.unshift(response.customer)
    //   showSuccess('Customer added successfully')
    //   closeCustomerModal()
    //   resetCustomerForm()
    // }
    
    // For demo, simulate addition
    const newCustomer = {
      id: Date.now(),
      name: customerForm.companyName,
      email: customerForm.email,
      status: 'trial',
      revenue: 0,
      joinDate: new Date().toISOString(),
      avatar: '/api/placeholder/40x40',
      products: customerForm.products
    }
    
    customers.value.unshift(newCustomer)
    showSuccess('Customer added successfully')
    closeCustomerModal()
    resetCustomerForm()
  } catch (error) {
    console.error('Error adding customer:', error)
    showError('Failed to add customer')
  }
}

const updateAnalytics = () => {
  // Update analytics based on time range
  initCharts()
  showSuccess('Analytics updated')
}

const initCharts = () => {
  // Initialize Revenue Chart
  if (revenueChart.value) revenueChart.value.destroy()
  revenueChart.value = new Chart(revenueChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Revenue $',
        data: [2500, 3200, 2800, 4500, 3800, 4200, 3500],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Products Chart
  if (productsChart.value) productsChart.value.destroy()
  productsChart.value = new Chart(productsChart.value.$el.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Professional Suite', 'Hardware Bundle', 'Cloud Services', 'Add-ons'],
      datasets: [{
        data: [145, 67, 89, 34],
        backgroundColor: [
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(139, 92, 246)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  })

  // Initialize Growth Chart
  if (growthChart.value) growthChart.value.destroy()
  growthChart.value = new Chart(growthChart.value.$el.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'New Customers',
        data: [5, 8, 12, 6, 15, 9],
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })

  // Initialize Commission Chart
  if (commissionChart.value) commissionChart.value.destroy()
  commissionChart.value = new Chart(commissionChart.value.$el.getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Commission Earned $',
        data: [1250, 1890, 2340, 1670, 2890, 2150],
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/reseller')
    // if (response.success) {
    //   products.value = response.products || []
    //   customers.value = response.customers || []
    //   Object.assign(resellerStatus, response.status)
    //   Object.assign(resellerStats, response.stats)
    //   Object.assign(analytics, response.analytics)
    // }
    
    // For demo, use mock data
    nextTick(() => {
      initCharts()
    })
  } catch (error) {
    console.error('Error loading reseller data:', error)
    showError('Failed to load reseller data')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.reseller {
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

.status-section,
.actions-section,
.products-section,
.customers-section,
.analytics-section,
.commission-section {
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

.status-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.reseller-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.reseller-icon {
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

.reseller-details h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.reseller-details p {
  margin: 0;
  color: var(--text-secondary);
}

.status-badge .badge {
  padding: 0.5rem 1.5rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.badge.inactive {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.actions-grid {
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

.action-icon.products {
  background: var(--info-color);
}

.action-icon.pricing {
  background: var(--warning-color);
}

.action-icon.analytics {
  background: var(--success-color);
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

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box input {
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  width: 250px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  color: var(--text-secondary);
}

.filter-dropdown,
.time-range {
  position: relative;
}

.filter-dropdown select,
.time-range select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
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
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
}

.create-first-btn:hover {
  background: var(--primary-hover);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.product-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.product-card.out-of-stock {
  opacity: 0.7;
  border-left: 4px solid var(--warning-color);
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.product-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.5rem 0.75rem;
  background: rgba(245, 158, 11, 0.9);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.product-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
}

.availability-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.availability-badge.available {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.availability-badge.out-of-stock {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.availability-badge.coming-soon {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.product-category {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.product-content {
  padding: 1.5rem;
}

.product-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.product-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.product-pricing {
  margin-bottom: 1rem;
}

.price-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.retail-price {
  color: var(--text-secondary);
  text-decoration: line-through;
  font-size: 0.9rem;
}

.reseller-price {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.commission-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}

.commission-rate {
  color: var(--success-color);
  font-weight: 600;
}

.profit-margin {
  color: var(--info-color);
  font-weight: 600;
}

.product-features {
  margin-bottom: 1rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.feature-item i {
  color: var(--success-color);
  font-size: 0.7rem;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--glass-bg-tertiary);
  border-top: 1px solid var(--glass-border);
}

.product-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.product-actions {
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

.action-btn.sell:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.view:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.edit:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.message:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.customers-table {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
  padding: 1rem;
  border-bottom: 1px solid var(--glass-border);
  transition: all 0.3s ease;
}

.table-row:hover {
  background: var(--glass-bg-hover);
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.customer-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.customer-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.customer-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.customer-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.customer-name {
  color: var(--text-primary);
  font-weight: 600;
}

.customer-email {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.product-count {
  color: var(--text-primary);
  font-weight: 600;
}

.revenue-amount {
  font-weight: 600;
  color: var(--success-color);
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
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.status-badge.trial {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.expired {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.join-date {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.customer-actions {
  display: flex;
  gap: 0.5rem;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.analytics-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.analytics-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.analytics-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.chart-container {
  height: 200px;
  position: relative;
}

.commission-tiers {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.tier-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  position: relative;
  transition: all 0.3s ease;
}

.tier-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.tier-card.current {
  border-color: var(--success-color);
}

.tier-card.recommended {
  border-color: var(--primary-color);
}

.tier-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.tier-icon {
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

.tier-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.tier-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.tier-badge {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.current-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.recommended-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.tier-commission {
  text-align: center;
  margin-bottom: 1.5rem;
}

.commission-rate {
  margin-bottom: 1rem;
}

.rate-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  display: block;
}

.rate-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.tier-requirements h4,
.tier-benefits h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.tier-requirements ul,
.tier-benefits ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.tier-requirements li {
  padding: 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  position: relative;
  padding-left: 1rem;
}

.tier-requirements li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--warning-color);
  font-weight: 600;
}

.benefit-item {
  padding: 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  position: relative;
  padding-left: 1.5rem;
}

.benefit-item i {
  position: absolute;
  left: 0;
  color: var(--success-color);
  font-size: 0.8rem;
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
  max-width: 700px;
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

.customer-form {
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
  min-height: 100px;
}

.product-selection {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.product-option {
  padding: 0.5rem 0;
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

.product-price {
  margin-left: auto;
  color: var(--success-color);
  font-weight: 600;
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
  .reseller {
    padding: 1rem;
  }
  
  .status-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .search-box input {
    width: 200px;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .table-cell {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .commission-tiers {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .product-selection {
    grid-template-columns: 1fr;
  }
}
</style>
