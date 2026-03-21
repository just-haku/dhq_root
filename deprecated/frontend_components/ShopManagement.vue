<template>
  <div class="shop-management">
    <div class="shop-header">
      <div class="header-left">
        <h2>
          <i class="fas fa-store"></i>
          Shop Management
        </h2>
        <p class="subtitle">Create and manage shop items</p>
      </div>
      <div class="header-right">
        <button @click="showCreateItem = true" class="btn btn-primary">
          <i class="fas fa-plus"></i>
          Create New Item
        </button>
      </div>
    </div>

    <!-- Shop Items List -->
    <div class="shop-content">
      <div class="items-header">
        <h3>Shop Items ({{ items.length }})</h3>
        <div class="filters">
          <select v-model="filterType" class="form-control">
            <option value="">All Types</option>
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
          <select v-model="filterRarity" class="form-control">
            <option value="">All Rarities</option>
            <option value="COMMON">Common</option>
            <option value="RARE">Rare</option>
            <option value="EPIC">Epic</option>
            <option value="LEGENDARY">Legendary</option>
          </select>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search items..."
            class="form-control"
          />
        </div>
      </div>

      <!-- Items Grid -->
      <div v-if="!loading" class="items-grid">
        <div 
          v-for="item in filteredItems" 
          :key="item.id"
          class="shop-item-card"
        >
          <div class="item-header">
            <div class="item-rarity" :class="item.rarity.toLowerCase()">
              {{ item.rarity }}
            </div>
            <div class="item-status">
              <span 
                class="status-badge"
                :class="item.is_active ? 'active' : 'inactive'"
              >
                {{ item.is_active ? 'Active' : 'Inactive' }}
              </span>
              <span v-if="item.is_limited" class="limited-badge">
                Limited ({{ item.stock_quantity }})
              </span>
            </div>
          </div>
          
          <div class="item-icon">
            <img 
              v-if="item.asset_url"
              :src="item.asset_url"
              :alt="item.name"
              class="item-image"
              @error="handleImageError"
            />
            <i v-else :class="getItemIcon(item.type)" class="item-type-icon"></i>
          </div>
          
          <div class="item-info">
            <h4>{{ item.name }}</h4>
            <p class="item-description">{{ item.description }}</p>
            <div class="item-meta">
              <span class="item-type">{{ item.type }}</span>
              <span class="item-price">{{ item.price }} KPI</span>
            </div>
          </div>
          
          <div class="item-actions">
            <button @click="editItem(item)" class="btn btn-sm btn-secondary">
              <i class="fas fa-edit"></i>
              Edit
            </button>
            <button 
              @click="toggleItemStatus(item)" 
              class="btn btn-sm"
              :class="item.is_active ? 'btn-warning' : 'btn-success'"
            >
              <i :class="item.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
              {{ item.is_active ? 'Deactivate' : 'Activate' }}
            </button>
            <button @click="deleteItem(item)" class="btn btn-sm btn-danger">
              <i class="fas fa-trash"></i>
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Loading shop items...</p>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && filteredItems.length === 0" class="empty-state">
        <i class="fas fa-store empty-icon"></i>
        <h3>No items found</h3>
        <p>Create your first shop item to get started.</p>
      </div>
    </div>

    <!-- Create/Edit Item Modal -->
    <div v-if="showCreateItem || editingItem" class="modal-overlay" @click="closeItemModal">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingItem ? 'Edit Item' : 'Create New Item' }}</h3>
          <button @click="closeItemModal" class="btn btn-icon">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>Item Name *</label>
              <input 
                type="text" 
                v-model="itemForm.name" 
                class="form-control"
                placeholder="Enter item name"
                required
              />
            </div>
            <div class="form-group">
              <label>Item Type *</label>
              <select v-model="itemForm.type" class="form-control" required>
                <option value="">Select type</option>
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
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Rarity *</label>
              <select v-model="itemForm.rarity" class="form-control" required>
                <option value="COMMON">Common</option>
                <option value="RARE">Rare</option>
                <option value="EPIC">Epic</option>
                <option value="LEGENDARY">Legendary</option>
              </select>
            </div>
            <div class="form-group">
              <label>Price (KPI) *</label>
              <input 
                type="number" 
                v-model="itemForm.price" 
                class="form-control"
                placeholder="0"
                min="0"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label>Description *</label>
            <textarea 
              v-model="itemForm.description" 
              class="form-control"
              placeholder="Describe this item..."
              rows="3"
              required
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Asset URL</label>
              <input 
                type="url" 
                v-model="itemForm.asset_url" 
                class="form-control"
                placeholder="https://example.com/asset.png"
              />
            </div>
            <div class="form-group">
              <label>Tags (comma separated)</label>
              <input 
                type="text" 
                v-model="tagsString" 
                class="form-control"
                placeholder="premium, animated, rare"
              />
            </div>
          </div>

          <div class="form-section">
            <h4>Limited Item Settings</h4>
            <div class="form-row">
              <div class="form-group">
                <label>
                  <input 
                    type="checkbox" 
                    v-model="itemForm.is_limited"
                  />
                  Limited Edition Item
                </label>
              </div>
              <div class="form-group" v-if="itemForm.is_limited">
                <label>Stock Quantity</label>
                <input 
                  type="number" 
                  v-model="itemForm.stock_quantity" 
                  class="form-control"
                  placeholder="0"
                  min="0"
                />
              </div>
            </div>
          </div>

          <div class="form-section">
            <h4>Requirements</h4>
            <div class="form-row">
              <div class="form-group">
                <label>Minimum Level</label>
                <input 
                  type="number" 
                  v-model="itemForm.requirements.level" 
                  class="form-control"
                  placeholder="1"
                  min="1"
                />
              </div>
              <div class="form-group">
                <label>KPI Required</label>
                <input 
                  type="number" 
                  v-model="itemForm.requirements.kpi_required" 
                  class="form-control"
                  placeholder="0"
                  min="0"
                />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeItemModal" class="btn btn-secondary">Cancel</button>
          <button @click="saveItem" class="btn btn-primary" :disabled="!isFormValid">
            <i class="fas fa-save"></i>
            {{ editingItem ? 'Update Item' : 'Create Item' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost } from '../../utils/api.js'

export default {
  name: 'ShopManagement',
  setup() {
    const loading = ref(false)
    const items = ref([])
    const filterType = ref('')
    const filterRarity = ref('')
    const searchQuery = ref('')
    const showCreateItem = ref(false)
    const editingItem = ref(null)
    
    // Form data
    const itemForm = ref({
      name: '',
      type: '',
      rarity: 'COMMON',
      price: 0,
      description: '',
      asset_url: '',
      is_limited: false,
      stock_quantity: 0,
      requirements: {
        level: 1,
        kpi_required: 0
      },
      tags: []
    })
    
    const tagsString = ref('')

    const filteredItems = computed(() => {
      let filtered = items.value

      if (filterType.value) {
        filtered = filtered.filter(item => item.type === filterType.value)
      }

      if (filterRarity.value) {
        filtered = filtered.filter(item => item.rarity === filterRarity.value)
      }

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(item => 
          item.name.toLowerCase().includes(query) ||
          item.description.toLowerCase().includes(query) ||
          item.tags.some(tag => tag.toLowerCase().includes(query))
        )
      }

      return filtered
    })

    const isFormValid = computed(() => {
      return itemForm.value.name.trim() &&
             itemForm.value.type &&
             itemForm.value.price >= 0 &&
             itemForm.value.description.trim()
    })

    const loadShopItems = async () => {
      loading.value = true
      try {
        const response = await apiGet('/vault-drive/shop/items-list')
        items.value = response.items || []
      } catch (error) {
        console.error('Failed to load shop items:', error)
        items.value = []
      } finally {
        loading.value = false
      }
    }

    const resetForm = () => {
      itemForm.value = {
        name: '',
        type: '',
        rarity: 'COMMON',
        price: 0,
        description: '',
        asset_url: '',
        is_limited: false,
        stock_quantity: 0,
        requirements: {
          level: 1,
          kpi_required: 0
        },
        tags: []
      }
      tagsString.value = ''
    }

    const closeItemModal = () => {
      showCreateItem.value = false
      editingItem.value = null
      resetForm()
    }

    const editItem = (item) => {
      editingItem.value = item
      itemForm.value = {
        name: item.name,
        type: item.type,
        rarity: item.rarity,
        price: item.price,
        description: item.description,
        asset_url: item.asset_url || '',
        is_limited: item.is_limited,
        stock_quantity: item.stock_quantity,
        requirements: {
          level: item.requirements.level || 1,
          kpi_required: item.requirements.kpi_required || 0
        },
        tags: item.tags || []
      }
      tagsString.value = item.tags ? item.tags.join(', ') : ''
    }

    const saveItem = async () => {
      try {
        // Parse tags
        if (tagsString.value.trim()) {
          itemForm.value.tags = tagsString.value
            .split(',')
            .map(tag => tag.trim())
            .filter(tag => tag)
        } else {
          itemForm.value.tags = []
        }

        if (editingItem.value) {
          // Update existing item
          await apiPut(`/vault-drive/shop/update/${editingItem.value.id}`, itemForm.value)
        } else {
          // Create new item
          await apiPost('/vault-drive/shop/create-item', itemForm.value)
        }

        closeItemModal()
        loadShopItems()
      } catch (error) {
        console.error('Failed to save item:', error)
      }
    }

    const toggleItemStatus = async (item) => {
      try {
        await apiPut(`/vault-drive/shop/update/${item.id}`, {
          ...item,
          is_active: !item.is_active
        })
        loadShopItems()
      } catch (error) {
        console.error('Failed to toggle item status:', error)
      }
    }

    const deleteItem = async (item) => {
      if (!confirm(`Are you sure you want to delete "${item.name}"?`)) {
        return
      }

      try {
        await apiDelete(`/vault-drive/shop/delete/${item.id}`)
        loadShopItems()
      } catch (error) {
        console.error('Failed to delete item:', error)
      }
    }

    const getItemIcon = (type) => {
      const iconMap = {
        'Avatar Frame': 'fas fa-user-circle',
        'Banner Frame': 'fas fa-image',
        'Animated Avatar': 'fas fa-user-astronaut',
        'Animated Banner': 'fas fa-film',
        'Role': 'fas fa-user-tag',
        'Profile Decoration': 'fas fa-palette',
        'Chat Badge': 'fas fa-comment-dots',
        'Title': 'fas fa-certificate',
        'Effect': 'fas fa-magic'
      }
      return iconMap[type] || 'fas fa-box'
    }

    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }

    onMounted(() => {
      loadShopItems()
    })

    return {
      loading,
      items,
      filterType,
      filterRarity,
      searchQuery,
      showCreateItem,
      editingItem,
      itemForm,
      tagsString,
      filteredItems,
      isFormValid,
      loadShopItems,
      resetForm,
      closeItemModal,
      editItem,
      saveItem,
      toggleItemStatus,
      deleteItem,
      getItemIcon,
      handleImageError
    }
  }
}
</script>

<style scoped>
.shop-management {
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 12px;
  min-height: 100vh;
}

.shop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.header-left h2 {
  margin: 0;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left h2 i {
  color: var(--primary-color);
}

.subtitle {
  margin: 5px 0 0 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.shop-content {
  min-height: 400px;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.items-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.filters {
  display: flex;
  gap: 10px;
}

.filters .form-control {
  min-width: 150px;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.shop-item-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.shop-item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.item-rarity {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.item-rarity.common {
  background: #6c757d;
  color: white;
}

.item-rarity.rare {
  background: #007bff;
  color: white;
}

.item-rarity.epic {
  background: #6f42c1;
  color: white;
}

.item-rarity.legendary {
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  color: white;
}

.item-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.status-badge {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
}

.status-badge.active {
  background: #28a745;
  color: white;
}

.status-badge.inactive {
  background: #dc3545;
  color: white;
}

.limited-badge {
  background: #ffc107;
  color: #212529;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
}

.item-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 8px;
  overflow: hidden;
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-type-icon {
  font-size: 32px;
  color: var(--primary-color);
}

.item-info {
  margin-bottom: 20px;
}

.item-info h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-size: 16px;
}

.item-description {
  margin: 0 0 12px 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.item-type {
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}

.item-price {
  color: var(--primary-color);
  font-weight: 600;
}

.item-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.loading-state i {
  font-size: 32px;
  margin-bottom: 15px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
}

.large-modal {
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.modal-body {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: var(--text-primary);
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
}

textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

.form-section {
  margin: 25px 0;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.form-section h4 {
  margin: 0 0 15px 0;
  color: var(--text-primary);
  font-size: 16px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--border-color);
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.btn-icon:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}
</style>
