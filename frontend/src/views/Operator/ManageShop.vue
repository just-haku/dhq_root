<template>
  <div class="manage-shop p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-white flex items-center gap-3">
        <i class="fas fa-store-alt text-danger"></i>
        Shop Management
      </h1>
      <button class="btn btn-primary" @click="openCreateModal">
        <i class="fas fa-plus mr-2"></i> Add Item
      </button>
    </div>

    <!-- Shop Items Table -->
    <div class="glass-panel overflow-hidden">
      <table class="dhq-table w-full">
        <thead>
          <tr>
            <th>Item</th>
            <th>Type</th>
            <th>Price</th>
            <th>Rarity</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="text-center py-8"><div class="spinner"></div></td></tr>
          <tr v-for="item in items" :key="item.id">
            <td>
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded glass-panel p-1 flex items-center justify-center">
                  <img v-if="item.asset_url" :src="item.asset_url" class="max-w-full max-h-full" />
                  <i v-else class="fas fa-image opacity-30"></i>
                </div>
                <div>
                  <div class="font-bold text-white">{{ item.name }}</div>
                  <div class="text-xs text-muted">{{ item.description }}</div>
                </div>
              </div>
            </td>
            <td class="text-sm">{{ item.type }}</td>
            <td class="font-mono text-warning">{{ item.price }} KPI</td>
            <td>
              <span class="rarity-badge" :class="'rarity-' + item.rarity.toLowerCase()">{{ item.rarity }}</span>
            </td>
            <td>
              <span class="status-indicator" :class="{ active: item.is_active }"></span>
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </td>
            <td>
              <div class="flex gap-2">
                <button class="btn-icon text-primary" @click="editItem(item)"><i class="fas fa-edit"></i></button>
                <button class="btn-icon text-danger" @click="deleteItem(item.id)"><i class="fas fa-trash"></i></button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content glass-panel p-6 w-[500px]">
        <h2 class="text-2xl font-bold mb-4 text-white">{{ editingItem ? 'Edit Item' : 'New Shop Item' }}</h2>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Name</label>
              <input v-model="form.name" class="dhq-input w-full" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Type</label>
              <select v-model="form.type" class="dhq-input w-full">
                <option>Avatar Frame</option>
                <option>Banner Frame</option>
                <option>Chat Badge</option>
                <option>Title</option>
                <option>Effect</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Price (KPI)</label>
              <input type="number" v-model="form.price" class="dhq-input w-full" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Rarity</label>
              <select v-model="form.rarity" class="dhq-input w-full">
                <option>COMMON</option>
                <option>RARE</option>
                <option>EPIC</option>
                <option>LEGENDARY</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Description</label>
            <textarea v-model="form.description" class="dhq-input w-full h-20"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Asset Upload</label>
            <input type="file" @change="handleFile" class="text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary-hover" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button class="btn btn-secondary" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary" @click="handleSubmit">
            {{ editingItem ? 'Update Item' : 'Create Item' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiGet, apiPostForm, apiDelete, showAlert } from '@/utils/api'

const items = ref([])
const loading = ref(true)
const showModal = ref(false)
const editingItem = ref(null)
const selectedFile = ref(null)

const form = ref({
  name: '',
  type: 'Avatar Frame',
  price: 100,
  rarity: 'COMMON',
  description: ''
})

const fetchItems = async () => {
  loading.value = true
  try {
    const data = await apiGet('/shop/items')
    items.value = data
  } catch (error) {}
  finally { loading.value = false }
}

const openCreateModal = () => {
  editingItem.value = null
  form.value = { name: '', type: 'Avatar Frame', price: 100, rarity: 'COMMON', description: '' }
  showModal.value = true
}

const handleFile = (e) => {
  selectedFile.value = e.target.files[0]
}

const handleSubmit = async () => {
  const formData = new FormData()
  Object.keys(form.value).forEach(key => formData.append(key, form.value[key]))
  if (selectedFile.value) formData.append('asset', selectedFile.value)

  try {
    await apiPostForm('/admin/shop/items', formData)
    showModal.value = false
    fetchItems()
    showAlert('Success', 'Shop item updated', 'success')
  } catch (error) {}
}

const deleteItem = async (id) => {
  if (!confirm('Delete this item?')) return
  try {
    await apiDelete(`/admin/shop/items/${id}`)
    fetchItems()
  } catch (error) {}
}

onMounted(fetchItems)
</script>

<style scoped>
.manage-shop {
  max-width: 1200px;
  margin: 0 auto;
}

.rarity-badge {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 900;
}
.rarity-common { background: #64748b; color: white; }
.rarity-rare { background: #3b82f6; color: white; }
.rarity-epic { background: #a855f7; color: white; }
.rarity-legendary { background: #f59e0b; color: white; }

.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  margin-right: 4px;
}
.status-indicator.active { background: #10b981; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}
</style>
