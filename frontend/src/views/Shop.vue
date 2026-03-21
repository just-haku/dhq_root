<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>Item Shop</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>Browse and purchase items with your KPI points</p>
    
</div>

    <div class="page-actions flex-wrap gap-3">
      <div class="balance-grid">
        <div class="compact-balance kpi">
          <i class="fas fa-coins"></i>
          <div class="balance-info">
            <span class="value">{{ userKPI }}</span>
            <span class="label">KPI</span>
          </div>
        </div>
        
        <div class="compact-balance api-dollar">
          <i class="fas fa-file-invoice-dollar"></i>
          <div class="balance-info">
            <span class="value">{{ apiDollarBalance.toFixed(2) }}</span>
            <span class="label">API$</span>
          </div>
        </div>

        <div class="compact-balance chips" v-if="userStore.user?.chip_balance !== undefined">
          <i class="fas fa-gamepad"></i>
          <div class="balance-info">
            <span class="value">{{ formatNumber(userStore.user.chip_balance) }}</span>
            <span class="label">Chips</span>
          </div>
        </div>
      </div>

      <button class="btn btn-secondary btn-sm h-[40px]" @click="fetchBalances">
        <i class="fas fa-sync-alt mr-2"></i> Sync
      </button>
    </div>

    <div class="shop-content">
      <div class="shop-categories mb-4">
        <button 
          v-for="category in displayCategories" 
          :key="category.id"
          class="category-btn"
          :class="{ active: selectedCategory === category.id }"
          @click="selectCategory(category.id)"
        >
          <i :class="category.icon" class="mr-2"></i>
          {{ category.name }}
        </button>
      </div>

      <!-- Conversion Target Selector (Only shown in Conversion Center) -->
      <div v-if="selectedCategory === 'conversion'" class="flex flex-col md:flex-row gap-4 mb-8 p-6 glass-card border-primary/20">
        <div class="flex-1">
          <label class="text-xs font-bold uppercase tracking-wider text-muted mb-2 block">I want to get:</label>
          <select v-model="conversionTarget" class="form-input bg-slate-800/50">
            <option value="chips">Arcade Chips (from KPI)</option>
            <option value="api-dollar">API$ Credits (from KPI or Chips)</option>
            <option value="api-to-chips">Chips (from API$)</option>
          </select>
        </div>
      </div>

      <div class="shop-grid" :class="{ 'highlight': highlightSelection }">
        <div 
          v-for="item in filteredItems" 
          :key="item.id"
          class="shop-item"
          :class="{ 'featured': item.featured, 'purchased': item.purchased }"
        >
          <div class="item-badge" v-if="item.featured">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2 L15.09 8.26 L22 9.27 L17 14.14 L18.18 21.02 L12 17.77 L5.82 21.02 L7 14.14 L2 9.27 L8.91 8.26 L12 2 Z" fill="currentColor"/>
            </svg>
            Featured
          </div>
          
          <div class="item-image">
            <img :src="item.image" :alt="item.name" />
          </div>
          
          <div class="item-info">
            <h3>{{ item.name }}</h3>
            <p class="item-description">{{ item.description }}</p>
            
            <div class="item-stats">
              <div class="stat">
                <span class="stat-label">Price:</span>
                <span class="stat-value price" v-if="item.category === 'api-dollar'">
                  {{ item.basePrice.toLocaleString() }} KPI / {{ (item.basePrice * 1000).toLocaleString() }} Chips
                </span>
                <span class="stat-value price" v-else>
                  {{ item.price.toLocaleString() }} {{ item.source }}
                </span>
              </div>
              <div class="stat">
                <span class="stat-label">Stock:</span>
                <span class="stat-value" :class="{ 'low': item.stock <= 5 }">{{ item.stock }}</span>
              </div>
            </div>
          </div>
          
          <div class="item-actions flex-col gap-2">
            <template v-if="item.category === 'api-dollar'">
              <div class="flex gap-2 w-full">
                <button 
                  class="btn btn-primary btn-sm flex-1" 
                  @click="addToCart(item, 'KPI')"
                  :disabled="userKPI < item.basePrice"
                >
                  <i class="fas fa-cart-plus mr-2"></i> KPI
                </button>
                <button 
                  class="btn bg-slate-800 border-white/10 btn-sm flex-1 text-emerald-400 hover:bg-slate-700" 
                  @click="addToCart(item, 'CHIPS')"
                  :disabled="!userStore.user || userStore.user.chip_balance < (item.basePrice * 1000)"
                >
                  <i class="fas fa-cart-plus mr-2"></i> Chips
                </button>
              </div>
              <p class="text-[10px] text-muted text-center italic mt-1">Add to cart to purchase</p>
            </template>
            <template v-else>
              <button 
                class="btn btn-primary" 
                @click="addToCart(item, item.source)"
                :disabled="item.purchased || (item.source === 'KPI' && userKPI < item.price) || (item.source === 'CHIPS' && userStore.arcadeProfile?.chip_balance < item.price) || item.stock === 0"
              >
                <i class="fas fa-cart-plus mr-2"></i>
                {{ item.category === 'chips' ? 'Add to Cart' : item.purchased ? 'Owned' : item.stock === 0 ? 'Out of Stock' : 'Add to Cart' }}
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Floating Cart Icon -->
    <div class="fixed bottom-8 right-8 z-[100]" v-if="cart.length > 0">
      <button 
        @click="isCartOpen = true" 
        class="relative p-5 rounded-[20px] bg-blue-600 shadow-2xl hover:scale-110 transition-transform active:scale-95 group border-2 border-white/10"
      >
        <i class="fas fa-shopping-cart text-2xl text-white"></i>
        <div 
          class="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-red-500 text-white text-xs flex items-center justify-center border-2 border-slate-950 font-black shadow-lg"
        >
          {{ cartCount }}
        </div>
        
        <!-- Cart Preview Tooltip -->
        <div class="absolute bottom-full right-0 mb-4 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity">
          <div class="bg-slate-900 border border-white/10 rounded-xl p-3 shadow-xl whitespace-nowrap min-w-[150px]">
            <div class="text-[10px] uppercase tracking-widest text-muted font-bold mb-1">In your cart</div>
            <div class="text-sm font-bold text-white">{{ cartCount }} Items</div>
            <div class="h-px bg-white/10 my-2"></div>
            <div class="text-xs text-amber-400 font-mono">{{ formatNumber(cartTotals.kpi) }} KPI</div>
          </div>
        </div>
      </button>
    </div>

    <!-- Cart Drawer -->
    <Teleport to="body">
      <Transition name="slide-over">
        <div 
          v-if="isCartOpen" 
          class="fixed inset-0 z-[1000] flex justify-end"
          @click.self="isCartOpen = false"
        >
          <div class="w-full max-w-md bg-slate-950 border-l border-white/10 h-full shadow-[-20px_0_50px_rgba(0,0,0,0.5)] flex flex-col">
            <!-- Drawer Header -->
            <div class="p-6 border-b border-white/10 flex items-center justify-between bg-slate-900/50">
              <div>
                <h2 class="text-xl font-bold flex items-center gap-2">
                  <i class="fas fa-shopping-cart text-primary"></i>
                  Checkout Cart
                </h2>
                <p class="text-xs text-muted">Review your items before processing</p>
              </div>
              <button @click="isCartOpen = false" class="w-10 h-10 hover:bg-white/5 rounded-xl transition-colors flex items-center justify-center">
                <i class="fas fa-times text-xl text-muted"></i>
              </button>
            </div>

            <!-- Cart Items -->
            <div class="flex-1 overflow-y-auto p-6 space-y-4">
              <div v-for="(item, index) in cart" :key="index" class="p-4 bg-white/5 border border-white/10 rounded-2xl flex items-center gap-4 transition-all hover:border-primary/30">
                <div class="w-16 h-12 rounded-xl bg-slate-800 overflow-hidden shrink-0 flex items-center justify-center border border-white/10">
                  <img :src="item.image" class="w-full h-full object-cover">
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="font-bold text-sm truncate text-white">{{ item.name }}</h4>
                  <p class="text-xs font-mono" :class="getSourceColor(item.sourceType)">
                    {{ formatNumber(item.price) }} {{ item.sourceType.toUpperCase() }}
                  </p>
                </div>
                <div class="flex flex-col items-center gap-2">
                  <div class="flex items-center gap-3 bg-slate-900 rounded-xl p-1 border border-white/5">
                    <button @click="updateCartQuantity(index, -1)" class="w-8 h-8 hover:bg-white/10 rounded-lg flex items-center justify-center text-lg">-</button>
                    <span class="text-sm font-bold w-4 text-center select-none">{{ item.quantity }}</span>
                    <button @click="updateCartQuantity(index, 1)" class="w-8 h-8 hover:bg-white/10 rounded-lg flex items-center justify-center text-lg">+</button>
                  </div>
                  <button @click="removeFromCart(index)" class="text-[10px] text-red-400 hover:text-red-300 transition-colors uppercase font-bold tracking-widest">Remove</button>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="p-8 border-t border-white/10 bg-slate-900/80 backdrop-blur-xl space-y-6">
              <div class="space-y-3 bg-white/5 p-4 rounded-2xl border border-white/5">
                <div class="text-[10px] uppercase tracking-[0.2em] text-muted font-black mb-1">Total Order Summary</div>
                <div v-if="cartTotals.kpi > 0" class="flex justify-between items-center">
                  <span class="text-muted text-sm italic">KPI Points</span>
                  <span class="text-amber-400 font-black text-lg">{{ formatNumber(cartTotals.kpi) }}</span>
                </div>
                <div v-if="cartTotals.chips > 0" class="flex justify-between items-center">
                  <span class="text-muted text-sm italic">Casino Chips</span>
                  <span class="text-emerald-400 font-black text-lg">{{ formatNumber(cartTotals.chips) }}</span>
                </div>
                <div v-if="cartTotals.api_dollar > 0" class="flex justify-between items-center">
                  <span class="text-muted text-sm italic">API Credits</span>
                  <span class="text-sky-400 font-black text-lg">${{ cartTotals.api_dollar.toFixed(2) }}</span>
                </div>
              </div>
              
              <button 
                @click="performCheckout" 
                :disabled="cart.length === 0 || isCheckingOut"
                class="w-full py-5 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-black text-xl shadow-[0_10px_30px_rgba(37,99,235,0.3)] hover:shadow-[0_15px_40px_rgba(37,99,235,0.4)] disabled:opacity-50 transition-all active:scale-95"
              >
                <template v-if="isCheckingOut">
                  <i class="fas fa-circle-notch fa-spin mr-3"></i> PROCESSING...
                </template>
                <template v-else>
                  CONFIRM CHECKOUT
                </template>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiPost, kpiBalance, showAlert, updateKpiBalance } from '../utils/api.js'
import { useUserStore } from '@/stores/userStore'

const route = useRoute()
const userStore = useUserStore()
const userKPI = computed(() => kpiBalance.value)
const apiDollarBalance = ref(0)
const selectedCategory = ref('all')
const highlightSelection = ref(false)
const conversionTarget = ref('chips')
const isCartOpen = ref(false)
const isCheckingOut = ref(false)
const cart = ref([])

const cartCount = computed(() => cart.value.reduce((acc, item) => acc + item.quantity, 0))

const cartTotals = computed(() => {
  return cart.value.reduce((acc, item) => {
    const cost = item.price * item.quantity
    acc[item.sourceType] = (acc[item.sourceType] || 0) + cost
    return acc
  }, { kpi: 0, chips: 0, api_dollar: 0 })
})

const getSourceColor = (type) => {
  if (type === 'kpi') return 'text-amber-400'
  if (type === 'chips') return 'text-emerald-400'
  if (type === 'api_dollar') return 'text-sky-400'
  return 'text-white'
}

const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

const categories = [
  { id: 'all', name: 'All Items', icon: 'fas fa-th-large' },
  { id: 'conversion', name: 'Conversion Center', icon: 'fas fa-exchange-alt' },
  { id: 'frames', name: 'Avatar Frames', icon: 'fas fa-portrait' },
  { id: 'backgrounds', name: 'Backgrounds', icon: 'fas fa-image' },
  { id: 'titles', name: 'Titles', icon: 'fas fa-heading' }
]

const displayCategories = computed(() => categories)

const chipPackages = [
  { id: 'basic', name: '5,000 Chips', description: 'Basic conversion package', price: 5, category: 'chips', chips: 5000, color: '#3b82f6', source: 'KPI' },
  { id: 'bonus_10', name: '55,000 Chips', description: '10% Bonus chips included!', price: 50, category: 'chips', chips: 55000, color: '#10b981', featured: true, source: 'KPI' },
  { id: 'bonus_20', name: '600,000 Chips', description: '20% Bonus chips included!', price: 500, category: 'chips', chips: 600000, color: '#f59e0b', featured: true, source: 'KPI' },
  { id: 'mega_50', name: '7,500,000 Chips', description: 'MEGA 50% Bonus chips!', price: 5000, category: 'chips', chips: 7500000, color: '#ef4444', featured: true, source: 'KPI' }
]

const apiDollarPackages = [
  { id: 'kpi_to_api_1', name: '1.00 API$', description: 'Instant API reload', basePrice: 1, category: 'api-dollar', amount: 1, color: '#7dd3fc' },
  { id: 'kpi_to_api_5', name: '5.00 API$', description: 'Quick API reload', basePrice: 5, category: 'api-dollar', amount: 5, color: '#38bdf8' },
  { id: 'kpi_to_api_10', name: '10.00 API$', description: 'Standard API reload', basePrice: 10, category: 'api-dollar', amount: 10, color: '#0ea5e9' },
  { id: 'kpi_to_api_50', name: '50.00 API$', description: 'Business API reload', basePrice: 50, category: 'api-dollar', amount: 50, color: '#0284c7', featured: true },
  { id: 'kpi_to_api_100', name: '100.00 API$', description: 'Enterprise API reload', basePrice: 100, category: 'api-dollar', amount: 100, color: '#0369a1', featured: true },
  { id: 'api_to_chips_1', name: '1,000 Chips', description: 'Back to the arcade!', price: 1, basePrice: 1, category: 'api-to-chips', chips: 1000, color: '#8b5cf6', source: 'API$' }
]

const items = ref([
  ...chipPackages.map(pkg => ({
    ...pkg,
    image: `https://dummyimage.com/600x400/${pkg.color.replace('#','')}/ffffff&text=${pkg.chips.toLocaleString()}+Chips`,
    stock: 999,
    purchased: false
  })),
  ...apiDollarPackages.map(pkg => ({
    ...pkg,
    image: `https://dummyimage.com/600x400/${pkg.color.replace('#','')}/ffffff&text=${pkg.name.replace(' ','+')}`,
    stock: 999,
    purchased: false,
    source: pkg.source || 'KPI' // Default to KPI
  })),
  {
    id: 1,
    name: 'Golden Avatar Frame',
    description: 'Premium golden frame for your avatar',
    price: 500,
    basePrice: 500,
    stock: 10,
    category: 'frames',
    featured: true,
    purchased: false,
    image: 'https://picsum.photos/seed/golden-frame/200/150.jpg'
  }
])

const processedItems = computed(() => {
  return items.value.map(item => {
    return { ...item }
  })
})

const filteredItems = computed(() => {
  const allProcessed = processedItems.value
  if (selectedCategory.value === 'all') {
    return allProcessed
  }
  if (selectedCategory.value === 'conversion') {
    return allProcessed.filter(item => {
      if (conversionTarget.value === 'chips' && item.category === 'chips') return true
      if (conversionTarget.value === 'api-dollar' && item.category === 'api-dollar') return true
      if (conversionTarget.value === 'api-to-chips' && item.category === 'api-to-chips') return true
      return false
    })
  }
  return allProcessed.filter(item => item.category === selectedCategory.value)
})

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId
}

const fetchBalances = async () => {
  await userStore.fetchProfile()
  const profile = userStore.user
  if (profile) {
    apiDollarBalance.value = profile.api_dollar_balance || 0
  }
}

const addToCart = (item, sourceOverride = null) => {
  const finalSource = sourceOverride || item.source
  const sourceMap = {
    'KPI': 'kpi',
    'CHIPS': 'chips',
    'API$': 'api_dollar'
  }
  const sourceType = sourceMap[finalSource.toUpperCase()] || finalSource.toLowerCase()
  const price = sourceType === 'chips' && item.category === 'api-dollar' ? item.basePrice * 1000 : (item.price || item.basePrice || 0)

  const existing = cart.value.find(ci => ci.id === item.id && ci.sourceType === sourceType)
  if (existing) {
    existing.quantity++
  } else {
    cart.value.push({
      id: item.id,
      name: item.name,
      image: item.image,
      price: price,
      sourceType: sourceType,
      quantity: 1,
      category: item.category
    })
  }
  
  // Visual feedback
  showAlert('Added to Cart', `${item.name} added to your checkout summary.`, 'info')
}

const removeFromCart = (index) => {
  cart.value.splice(index, 1)
}

const updateCartQuantity = (index, delta) => {
  const item = cart.value[index]
  item.quantity = Math.max(1, item.quantity + delta)
}

const performCheckout = async () => {
  if (cart.value.length === 0) return
  
  isCheckingOut.value = true
  try {
    const checkoutItems = cart.value.map(item => ({
      item_id: item.id.toString(),
      quantity: item.quantity,
      source_type: item.sourceType
    }))

    const resp = await apiPost('/economy/checkout', { items: checkoutItems })
    
    // Update store
    updateKpiBalance(resp.new_balance)
    if (userStore.user) {
        userStore.user.kpi_current = resp.new_balance
        userStore.user.chip_balance = resp.new_chips
        userStore.user.api_dollar_balance = resp.new_api_dollars
    }
    apiDollarBalance.value = resp.new_api_dollars
    
    showAlert('Checkout Complete', resp.message, 'success', '🎉')
    cart.value = []
    isCartOpen.value = false
  } catch (err) {
    console.error('Checkout failed:', err)
  } finally {
    isCheckingOut.value = false
  }
}

const purchaseItem = async (item, sourceOverride = null) => {
  // We now use addToCart for most items, but keep this for backward compatibility or direct buys if needed
  addToCart(item, sourceOverride)
  isCartOpen.value = true
}

const viewDetails = (item) => {
  console.log('Viewing details for:', item.name)
}

const refreshShop = () => {
  console.log('Refreshing shop items...')
}

onMounted(async () => {
  await fetchBalances()
  
  if (userStore.user) {
    apiDollarBalance.value = userStore.user.api_dollar_balance || 0
  }
  
  if (route.query.category === 'chips') {
    selectedCategory.value = 'chips'
  }
  if (route.query.tab === 'api-dollar') {
    selectedCategory.value = 'api-dollar'
    if (route.query.focus === 'true') {
      highlightSelection.value = true
      setTimeout(() => highlightSelection.value = false, 3000)
    }
  }
})
</script>

<style scoped>
.shop-content {
  max-width: 1200px;
  margin: 0 auto;
}

.balance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  flex: 1;
}

.compact-balance {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: rgba(15, 23, 42, 0.85); /* Slightly higher opacity */
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: transform 0.2s ease, background 0.2s ease;
}

.compact-balance i {
  font-size: 1.25rem;
  opacity: 0.8;
}

.balance-info {
  display: flex;
  flex-direction: column;
}

.balance-info .value {
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 1.1rem;
  line-height: 1;
}

.balance-info .label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.6;
}

.compact-balance.kpi { border-left: 3px solid #f59e0b; color: #f59e0b; }
.compact-balance.api-dollar { border-left: 3px solid #38bdf8; color: #38bdf8; }
.compact-balance.chips { border-left: 3px solid #10b981; color: #10b981; }

.compact-balance:hover {
  background: rgba(15, 23, 42, 0.6);
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.15);
}

.shop-categories {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 2rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.category-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 25px;
  color: #94a3b8;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease;
  white-space: nowrap;
}

.category-btn:hover {
  background: rgba(15, 23, 42, 0.8);
  color: #f1f5f9;
  transform: translateY(-1px);
}

.category-btn.active {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: white;
  border-color: rgba(96, 165, 250, 0.3);
}

.shop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  transition: all 0.5s ease;
  padding: 10px;
  border-radius: 20px;
}

.shop-grid.highlight {
  background: rgba(56, 189, 248, 0.05);
  box-shadow: 0 0 30px rgba(56, 189, 248, 0.2);
  animation: pulse-border 1.5s infinite alternate;
}

@keyframes pulse-border {
  from { border: 1px solid rgba(56, 189, 248, 0.1); }
  to { border: 1px solid rgba(56, 189, 248, 0.5); }
}

.shop-item {
  background: rgba(15, 23, 42, 0.9); /* Higher opacity instead of blur */
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease; /* Simplified transition */
  position: relative;
  will-change: transform; /* Hint to browser */
}

.shop-item:hover {
  background: rgba(15, 23, 42, 0.95);
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
}

.shop-item.featured {
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.1);
}

.shop-item.purchased {
  opacity: 0.7;
}

.item-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 20px;
  z-index: 1;
}

.item-image {
  aspect-ratio: 4/3;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.shop-item:hover .item-image img {
  transform: scale(1.05);
}

.item-info {
  padding: 1.5rem;
}

.item-info h3 {
  margin: 0 0 0.5rem 0;
  color: #f1f5f9;
  font-size: 1.125rem;
  font-weight: 600;
}

.item-description {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.item-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  color: #64748b;
  font-size: 0.75rem;
}

.stat-value {
  color: #f1f5f9;
  font-weight: 600;
  font-size: 0.875rem;
}

.stat-value.price {
  color: #f59e0b;
}

.stat-value.low {
  color: #ef4444;
}

.item-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-outline {
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
}

.icon {
  width: 1rem;
  height: 1rem;
}

@keyframes floatBubble {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(2deg); }
}

/* Slide Over Animation */
.slide-over-enter-active, .slide-over-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-over-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.slide-over-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

@media (max-width: 768px) {
  .shop-categories {
    padding-bottom: 1rem;
  }
  
  .shop-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
  }
  
  .item-info {
    padding: 1rem;
  }
  
  .item-actions {
    flex-direction: column;
  }
}
</style>

<style scoped>
.legacy-page-container {
  padding: 1rem;
}
.page-title { margin-bottom: 0.5rem; }
.page-subtitle { color: var(--text-secondary); margin-bottom: 1rem; }
.page-actions { margin-bottom: 1.5rem; }
</style>
