<template>
  <div class="email-detail-overlay" @click.self="$emit('close')">
    <div class="email-detail-container glass-panel">
      <div class="detail-header">
        <div class="sender-info">
          <div class="avatar">{{ senderInitial }}</div>
          <div>
            <h3>{{ email.sender_name }}</h3>
            <p>{{ email.sender_email }}</p>
          </div>
        </div>
        <button class="btn-icon" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="detail-content">
        <div class="email-meta-card">
          <h2>{{ email.subject }}</h2>
          <div class="meta-row">
            <span class="label">Date:</span>
            <span>{{ formatDate(email.processed_at.$date) }}</span>
          </div>
          <div v-if="email.is_collaboration" class="ai-extracted-box mt-4">
            <h4><i class="fas fa-robot mr-2"></i> AI Extracted Data</h4>
            <div class="extraction-grid">
              <div class="item">
                <span class="label">Scope:</span>
                <input v-model="email.ai_data.scope" class="inline-input" />
              </div>
              <div class="item">
                <span class="label">Platform:</span>
                <input v-model="email.ai_data.platform" class="inline-input" />
              </div>
              <div class="item">
                <span class="label">Price:</span>
                <input v-model="email.ai_data.price" class="inline-input" />
              </div>
            </div>
            <button class="btn btn-primary btn-sm mt-4 w-full" @click="convertToCollaboration">
              <i class="fas fa-plus-circle mr-2"></i> Create Collaboration
            </button>
          </div>
        </div>

        <div class="email-body mt-6">
          {{ email.body }}
        </div>

        <!-- AI Drafting Area -->
        <div class="ai-draft-section mt-8 pt-8 border-t border-slate-700/50">
          <div class="flex justify-between items-center mb-4">
            <h3 class="flex items-center gap-2">
              <i class="fas fa-pen-nib text-primary"></i>
              AI Response Draft
            </h3>
            <select v-model="selectedPromptId" class="prompt-select" @change="fetchDraft">
              <option value="" disabled>Select a prompt template...</option>
              <option v-for="prompt in prompts" :key="prompt._id.$oid" :value="prompt._id.$oid">
                {{ prompt.name }}
              </option>
            </select>
          </div>

          <div v-if="drafting" class="draft-loading">
            <div class="shimmer"></div>
            <div class="shimmer w-3/4"></div>
          </div>
          
          <div v-else-if="draft" class="draft-container">
            <textarea v-model="draft" class="draft-textarea"></textarea>
            <div class="draft-actions mt-4 flex justify-end gap-3">
              <button class="btn border border-slate-600" @click="draft = ''">Clear</button>
              <button class="btn btn-primary px-8">
                <i class="fas fa-paper-plane mr-2"></i> Send Reply
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'

const props = defineProps({
  email: Object
})

const emit = defineEmits(['close', 'converted'])

const selectedPromptId = ref('')
const prompts = ref([])
const drafting = ref(false)
const draft = ref('')

const senderInitial = computed(() => {
    return (props.email.sender_name || props.email.sender_email || '?').charAt(0).toUpperCase()
})

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString()
}

const fetchPrompts = async () => {
    try {
        const resp = await apiGet('/prompts/')
        prompts.value = resp.prompts
    } catch (e) {
        console.error('Failed to load prompts')
    }
}

const fetchDraft = async () => {
    if (!selectedPromptId.value) return
    drafting.value = true
    try {
        // We'll use a new endpoint or the pipeline service to generate draft
        const resp = await apiPost(`/emails/${props.email._id.$oid}/draft`, { prompt_id: selectedPromptId.value })
        draft.value = resp.draft
    } catch (e) {
        showError('Failed to generate AI draft')
    } finally {
        drafting.value = false
    }
}

const convertToCollaboration = async () => {
    try {
        await apiPost(`/emails/${props.email._id.$oid}/convert`)
        showSuccess('Collaboration created successfully!')
        emit('converted')
    } catch (e) {
        showError('Failed to create collaboration')
    }
}

onMounted(fetchPrompts)
</script>

<style scoped>
.email-detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.email-detail-container {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-header {
  padding: 1.5rem;
  background: rgba(255,255,255,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sender-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 48px;
  height: 48px;
  background: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.25rem;
}

.detail-content {
  padding: 1.5rem;
  overflow-y: auto;
}

.email-meta-card {
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.05);
}

.label {
  color: var(--text-tertiary);
  font-weight: 600;
  margin-right: 0.5rem;
}

.ai-extracted-box {
  padding: 1rem;
  background: rgba(99, 102, 241, 0.1);
  border: 1px dashed rgba(99, 102, 241, 0.3);
  border-radius: 12px;
}

.extraction-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 0.5rem;
}

.inline-input {
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  width: 100%;
  padding: 2px 0;
}

.inline-input:focus {
  outline: none;
  border-bottom-color: var(--primary);
}

.email-body {
  white-space: pre-wrap;
  color: var(--text-secondary);
  line-height: 1.6;
}

.draft-textarea {
  width: 100%;
  min-height: 200px;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 1rem;
  color: #fff;
  font-family: inherit;
  resize: vertical;
}

.prompt-select {
  padding: 0.5rem 1rem;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  color: #fff;
  border-radius: 8px;
}

.shimmer {
  height: 20px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 10px;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: -100% 0; }
  100% { background-position: 100% 0; }
}
</style>
