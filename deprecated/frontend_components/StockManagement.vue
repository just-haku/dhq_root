<template>
  <div class="stock-management">
    <div class="stock-header">
      <h2>
        <i class="fas fa-warehouse"></i>
        Stock Management
      </h2>
      <p class="subtitle">Manage inventory and arcade games</p>
    </div>

    <!-- Tab Navigation -->
    <div class="tab-navigation">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab-button"
        :class="{ active: activeTab === tab.id }"
      >
        <i :class="tab.icon"></i>
        {{ tab.name }}
      </button>
    </div>

    <!-- Stock Items Tab -->
    <div v-if="activeTab === 'stock'" class="tab-content">
      <div class="section-header">
        <h3>Stock Inventory</h3>
        <button @click="showCreateForm = true" class="btn btn-primary">
          <i class="fas fa-plus"></i>
          Create New Item
        </button>
      </div>

      <!-- Create Item Form -->
      <div v-if="showCreateForm" class="create-form">
        <div class="form-header">
          <h4>Create New Stock Item</h4>
          <button @click="showCreateForm = false" class="btn btn-icon">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="createItem">
          <div class="form-grid">
            <div class="form-group">
              <label>Item Name *</label>
              <input v-model="itemForm.name" type="text" required class="form-input" />
            </div>
            
            <div class="form-group">
              <label>Type *</label>
              <select v-model="itemForm.type" required class="form-select">
                <option value="">Select Type</option>
                <option value="Avatar Frame">Avatar Frame</option>
                <option value="Banner Frame">Banner Frame</option>
                <option value="Animated Avatar">Animated Avatar</option>
                <option value="Animated Banner">Animated Banner</option>
                <option value="Role">Role</option>
                <option value="Profile Decoration">Profile Decoration</option>
                <option value="Chat Badge">Chat Badge</option>
                <option value="Title">Title</option>
                <option value="Effect">Effect</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Rarity</label>
              <select v-model="itemForm.rarity" class="form-select">
                <option value="COMMON">Common</option>
                <option value="RARE">Rare</option>
                <option value="EPIC">Epic</option>
                <option value="LEGENDARY">Legendary</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Price (KPI Points) *</label>
              <input v-model.number="itemForm.price" type="number" min="0" required class="form-input" />
            </div>
            
            <div class="form-group">
              <label>Stock Quantity</label>
              <input v-model.number="itemForm.stock_quantity" type="number" min="0" class="form-input" />
            </div>
            
            <div class="form-group">
              <label>Asset URL</label>
              <input v-model="itemForm.asset_url" type="url" placeholder="https://example.com/asset.png" class="form-input" />
            </div>
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="itemForm.description" rows="3" class="form-textarea"></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="itemForm.is_active" type="checkbox" />
                Active
              </label>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="itemForm.is_limited" type="checkbox" />
                Limited Edition
              </label>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="showCreateForm = false" class="btn btn-outline">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <i class="fas fa-save"></i>
              Create Item
            </button>
          </div>
        </form>
      </div>

      <!-- Stock Items List -->
      <div class="items-grid">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          Loading stock items...
        </div>
        
        <div v-else-if="items.length === 0" class="empty-state">
          <i class="fas fa-box-open"></i>
          No stock items found
        </div>
        
        <div v-else>
          <div class="filter-bar">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search items..."
              class="search-input"
            />
            <select v-model="filterType" class="filter-select">
              <option value="">All Types</option>
              <option value="Avatar Frame">Avatar Frame</option>
              <option value="Banner Frame">Banner Frame</option>
              <option value="Role">Role</option>
              <option value="Effect">Effect</option>
            </select>
            <select v-model="filterRarity" class="filter-select">
              <option value="">All Rarities</option>
              <option value="COMMON">Common</option>
              <option value="RARE">Rare</option>
              <option value="EPIC">Epic</option>
              <option value="LEGENDARY">Legendary</option>
            </select>
          </div>
          
          <div class="items-container">
            <div 
              v-for="item in filteredItems" 
              :key="item.id"
              class="stock-item"
              :class="[item.rarity.toLowerCase(), { inactive: !item.is_active }]"
            >
              <div class="item-header">
                <div class="item-icon">{{ getItemIcon(item.type) }}</div>
                <div class="item-info">
                  <h4>{{ item.name }}</h4>
                  <span class="item-type">{{ item.type }}</span>
                </div>
                <div class="item-actions">
                  <button @click="editItem(item)" class="btn btn-sm btn-outline">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button @click="deleteItem(item)" class="btn btn-sm btn-danger">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
              
              <div class="item-details">
                <div class="detail-row">
                  <span class="label">Price:</span>
                  <span class="value">{{ item.price }} KPI</span>
                </div>
                <div class="detail-row">
                  <span class="label">Stock:</span>
                  <span class="value">{{ item.stock_quantity || 'Unlimited' }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Rarity:</span>
                  <span class="rarity-badge" :class="item.rarity.toLowerCase()">
                    {{ item.rarity }}
                  </span>
                </div>
              </div>
              
              <p class="item-description">{{ item.description }}</p>
              
              <div class="item-footer">
                <span class="status-badge" :class="{ active: item.is_active }">
                  {{ item.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span v-if="item.is_limited" class="limited-badge">Limited</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Arcade Tab -->
    <div v-if="activeTab === 'arcade'" class="tab-content">
      <ArcadeDashboard />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '../../utils/api.js'
import ArcadeDashboard from '@/components/Arcade/ArcadeDashboard.vue'

export default {
  name: 'StockManagement',
  
  components: {
    ArcadeDashboard
  },
  
  setup() {
    const loading = ref(false)
    const items = ref([])
    const activeTab = ref('stock')
    const showCreateForm = ref(false)
    const searchQuery = ref('')
    const filterType = ref('')
    const filterRarity = ref('')
    
    const tabs = [
      { id: 'stock', name: 'Stock Items', icon: 'fas fa-box' },
      { id: 'arcade', name: 'Arcade Games', icon: 'fas fa-gamepad' }
    ]
    
    const itemForm = ref({
      name: '',
      type: '',
      rarity: 'COMMON',
      price: 0,
      description: '',
      asset_url: '',
      is_active: true,
      is_limited: false,
      stock_quantity: null
    })
    
    const filteredItems = computed(() => {
      let filtered = items.value
      
      if (searchQuery.value) {
        filtered = filtered.filter(item => 
          item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      }
      
      if (filterType.value) {
        filtered = filtered.filter(item => item.type === filterType.value)
      }
      
      if (filterRarity.value) {
        filtered = filtered.filter(item => item.rarity === filterRarity.value)
      }
      
      return filtered
    })
    
    const loadItems = async () => {
      loading.value = true
      try {
        const response = await apiGet('/vault-drive/shop/items-list')
        items.value = response.items || []
      } catch (error) {
        console.error('Failed to load stock items:', error)
        items.value = []
      } finally {
        loading.value = false
      }
    }
    
    const createItem = async () => {
      loading.value = true
      try {
        await apiPost('/vault-drive/shop/create-item', itemForm.value)
        
        // Reset form
        itemForm.value = {
          name: '',
          type: '',
          rarity: 'COMMON',
          price: 0,
          description: '',
          asset_url: '',
          is_active: true,
          is_limited: false,
          stock_quantity: null
        }
        
        showCreateForm.value = false
        await loadItems()
        
        alert('Stock item created successfully!')
      } catch (error) {
        console.error('Failed to create item:', error)
        alert('Failed to create item: ' + (error.response?.data?.detail || error.message))
      } finally {
        loading.value = false
      }
    }
    
    const editItem = (item) => {
      // TODO: Implement edit functionality
      console.log('Edit item:', item)
      alert('Edit functionality coming soon!')
    }
    
    const deleteItem = async (item) => {
      if (!confirm(`Are you sure you want to delete "${item.name}"?`)) {
        return
      }
      
      try {
        await apiDelete(`/vault-drive/shop/delete/${item.id}`)
        await loadItems()
        alert('Item deleted successfully!')
      } catch (error) {
        console.error('Failed to delete item:', error)
        alert('Failed to delete item: ' + (error.response?.data?.detail || error.message))
      }
    }
    
    const getItemIcon = (type) => {
      const icons = {
        'Avatar Frame': '🖼️',
        'Banner Frame': '🎨',
        'Animated Avatar': '🎭',
        'Animated Banner': '🌟',
        'Role': '👑',
        'Profile Decoration': '✨',
        'Chat Badge': '🏷️',
        'Title': '📜',
        'Effect': '⚡'
      }
      return icons[type] || '📦'
    }
    
    onMounted(() => {
      loadItems()
    })
    
    return {
      loading,
      items,
      activeTab,
      showCreateForm,
      searchQuery,
      filterType,
      filterRarity,
      tabs,
      itemForm,
      filteredItems,
      createItem,
      editItem,
      deleteItem,
      getItemIcon
    }
  }
}
</script>

<style scoped>
.stock-management {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

.stock-header {
  text-align: center;
  margin-bottom: 2rem;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.stock-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.stock-header h2 {
  color: var(--text-primary);
  margin-bottom: 1rem;
  font-size: 1.8rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.tab-navigation {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 2rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

.tab-navigation::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 8px;
}

.tab-button:hover {
  color: var(--text-primary);
  background: var(--glass-bg-hover);
  border-bottom-color: var(--glass-border-hover);
}

.tab-button.active {
  color: var(--text-primary);
  border-bottom-color: var(--primary-color);
  background: var(--glass-bg-hover);
}

.tab-content {
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.tab-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 6s ease-in-out infinite;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.3rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-md);
}

.btn-primary {
  background: var(--primary-gradient);
  border-color: var(--primary-color);
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.btn-primary:hover {
  background: var(--primary-gradient);
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-lg);
}

.btn-icon {
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
}

.create-form {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.create-form::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-header h4 {
  color: #2c3e50;
  margin: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: 500;
  color: #2c3e50;
}

.checkbox-label {
  flex-direction: row;
  align-items: center;
  cursor: pointer;
}

.checkbox-label input {
  margin-right: 8px;
}

.form-input, .form-select, .form-textarea {
  padding: 12px;
  border: 2px solid #e1e8ed;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input, .filter-select {
  padding: 10px;
  border: 2px solid #e1e8ed;
  border-radius: 6px;
  font-size: 14px;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.filter-select {
  min-width: 150px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 60px;
  color: #7f8c8d;
}

.items-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.stock-item {
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  padding: 20px;
  background: white;
  transition: all 0.3s;
}

.stock-item:hover {
  border-color: #3498db;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.1);
}

.stock-item.inactive {
  opacity: 0.6;
  border-color: #bdc3c7;
}

.stock-item.common {
  border-left: 4px solid #95a5a6;
}

.stock-item.rare {
  border-left: 4px solid #3498db;
}

.stock-item.epic {
  border-left: 4px solid #9b59b6;
}

.stock-item.legendary {
  border-left: 4px solid #f1c40f;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.item-icon {
  font-size: 24px;
  margin-right: 10px;
}

.item-info {
  flex: 1;
}

.item-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.item-type {
  font-size: 12px;
  color: #7f8c8d;
}

.item-actions {
  display: flex;
  gap: 5px;
}

.item-details {
  margin-bottom: 15px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
}

.detail-row .label {
  color: #7f8c8d;
}

.detail-row .value {
  color: #2c3e50;
  font-weight: 500;
}

.rarity-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.rarity-badge.common {
  background: #ecf0f1;
  color: #7f8c8d;
}

.rarity-badge.rare {
  background: #e3f2fd;
  color: #2196f3;
}

.rarity-badge.epic {
  background: #f3e5f5;
  color: #9c27b0;
}

.rarity-badge.legendary {
  background: #fffde7;
  color: #f57c00;
}

.item-description {
  color: #5d6d7e;
  font-size: 14px;
  margin-bottom: 15px;
  line-height: 1.4;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge:not(.active) {
  background: #f8d7da;
  color: #721c24;
}

.limited-badge {
  background: #fff3cd;
  color: #856404;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
</style>
