<template>
  <div class="prompt-library">
    <div class="header-section">
      <div class="title-area">
        <h1>📜 Prompt Library</h1>
        <p>Manage AI templates for collaboration responses</p>
      </div>
      <div class="action-area">
        <button class="btn btn-primary" @click="openCreateModal">
          <i class="fas fa-plus mr-2"></i> Create Template
        </button>
      </div>
    </div>

    <div class="prompts-grid mt-8">
      <div v-for="prompt in prompts" :key="prompt._id.$oid" class="prompt-card glass-panel">
        <div class="card-header">
          <div class="flex items-center gap-3">
            <span class="category-icon">{{ getCategoryIcon(prompt.category) }}</span>
            <h3>{{ prompt.name }}</h3>
          </div>
          <div class="actions">
            <button class="btn-icon" @click="editPrompt(prompt)"><i class="fas fa-edit"></i></button>
            <button class="btn-icon text-danger" @click="deletePrompt(prompt._id.$oid)"><i class="fas fa-trash"></i></button>
          </div>
        </div>
        <p class="description">{{ prompt.description || 'No description provided' }}</p>
        <div class="content-preview">
          {{ prompt.content.substring(0, 150) }}...
        </div>
        <div class="card-footer mt-4">
          <span class="category-tag">{{ prompt.category }}</span>
          <span class="variable-count">{{ prompt.variables?.length || 0 }} Variables</span>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-container glass-panel">
        <div class="modal-header">
          <h2>{{ editingId ? 'Edit Template' : 'Create New Template' }}</h2>
          <button class="btn-icon" @click="showModal = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Template Name</label>
            <input v-model="form.name" placeholder="e.g. Friendly Acceptance" />
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="form.category">
              <option value="General">General</option>
              <option value="Collaboration">Collaboration</option>
              <option value="Product">Product</option>
              <option value="Refusal">Refusal</option>
              <option value="Negotiation">Negotiation</option>
            </select>
          </div>
          <div class="form-group">
            <label>Description</label>
            <input v-model="form.description" placeholder="Short description for your reference" />
          </div>
          <div class="form-group">
            <label>Prompt Instructions / Template Content</label>
            <p class="hint">Use {{variable_name}} for placeholders like {{collaborator_name}} or {{scope}}</p>
            <textarea v-model="form.content" rows="8"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn border border-slate-600" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary px-8" @click="savePrompt" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save Template' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiGet, apiPost, apiPatch, apiDelete } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'

const prompts = ref([])
const showModal = ref(false)
const saving = ref(false)
const editingId = ref(null)

const form = ref({
  name: '',
  category: 'Collaboration',
  description: '',
  content: '',
  variables: []
})

const fetchPrompts = async () => {
    try {
        const resp = await apiGet('/prompts/')
        prompts.value = resp.prompts
    } catch (e) {
        showError('Failed to load templates')
    }
}

const openCreateModal = () => {
    editingId.value = null
    form.value = { name: '', category: 'Collaboration', description: '', content: '', variables: [] }
    showModal.value = true
}

const editPrompt = (prompt) => {
    editingId.value = prompt._id.$oid
    form.value = { ...prompt }
    showModal.value = true
}

const savePrompt = async () => {
    saving.value = true
    try {
        if (editingId.value) {
            await apiPatch(`/prompts/${editingId.value}`, form.value)
            showSuccess('Template updated!')
        } else {
            await apiPost('/prompts/', form.value)
            showSuccess('Template created!')
        }
        showModal.value = false
        fetchPrompts()
    } catch (e) {
        showError('Failed to save template')
    } finally {
        saving.value = false
    }
}

const deletePrompt = async (id) => {
    if (!confirm('Are you sure you want to delete this template?')) return
    try {
        await apiDelete(`/prompts/${id}`)
        showSuccess('Template deleted')
        fetchPrompts()
    } catch (e) {
        showError('Failed to delete template')
    }
}

const getCategoryIcon = (cat) => {
    const icons = {
        'Collaboration': '🤝',
        'Product': '🎁',
        'Refusal': '❌',
        'Negotiation': '⚖️',
        'General': '📝'
    }
    return icons[cat] || '📝'
}

onMounted(fetchPrompts)
</script>

<style scoped>
.prompt-library {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-area h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.prompts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.prompt-card {
  padding: 1.5rem;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
}

.prompt-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.category-icon { font-size: 1.5rem; }

.description {
  color: var(--text-tertiary);
  font-size: 0.9rem;
  margin-bottom: 1rem;
  height: 2.7rem;
  overflow: hidden;
}

.content-preview {
  background: rgba(0,0,0,0.2);
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  height: 6rem;
  overflow: hidden;
}

.category-tag {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: bold;
}

.variable-count {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.modal-overlay {
  position: fixed;
  top:0; left:0; right:0; bottom:0;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(8px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.modal-container {
  width: 100%;
  max-width: 600px;
  border-radius: 24px;
}

.modal-header, .modal-footer {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 1.5rem;
  max-height: 70vh;
  overflow-y: auto;
}

.hint { font-size: 0.75rem; color: var(--primary); margin-bottom: 0.5rem; }

.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
.form-group input, .form-group textarea, .form-group select {
  width: 100%;
  padding: 0.75rem;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: white;
}
</style>
