<template>
  <div class="email-hub">
    <div class="header-section">
      <div class="title-area">
        <h1>📩 Email Hub</h1>
        <p>AI-powered collaboration & inbox management</p>
      </div>
      <div class="action-area">
        <button class="btn btn-primary" @click="syncEmails" :disabled="syncing">
          <i class="fas" :class="syncing ? 'fa-spinner fa-spin' : 'fa-sync-alt'"></i>
          {{ syncing ? 'Syncing...' : 'Sync Inbox' }}
        </button>
      </div>
    </div>

    <div class="hub-layout mt-8">
      <!-- Sidebar Filters -->
      <aside class="hub-sidebar glass-panel">
        <nav class="hub-nav">
          <button 
            v-for="filter in filters" 
            :key="filter.id"
            :class="['nav-item', { active: activeFilter === filter.id }]"
            @click="activeFilter = filter.id"
          >
            <i :class="filter.icon"></i>
            {{ filter.label }}
            <span v-if="getCount(filter.id)" class="badge">{{ getCount(filter.id) }}</span>
          </button>
          
          <div class="nav-divider"></div>
          
          <router-link to="/settings?tab=credentials" class="nav-item">
            <i class="fas fa-cog"></i> Config Credentials
          </router-link>
          <router-link to="/prompts" class="nav-item">
            <i class="fas fa-terminal"></i> Prompt Library
          </router-link>
        </nav>
      </aside>

      <!-- Email List -->
      <main class="hub-main glass-panel">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading your emails...</p>
        </div>
        
        <div v-else-if="filteredEmails.length === 0" class="empty-state">
          <div class="empty-icon">📂</div>
          <h3>No emails found</h3>
          <p>Try syncing your inbox or checking your credentials.</p>
        </div>

        <div v-else class="email-list">
          <div 
            v-for="email in filteredEmails" 
            :key="email._id.$oid"
            class="email-card"
            :class="{ 
              'urgency-high': email.urgency === 'High', 
              'is-collab': email.is_collaboration 
            }"
            @click="selectEmail(email)"
          >
            <div class="email-header">
              <span class="sender">{{ email.sender_name || email.sender_email }}</span>
              <span class="time">{{ formatTime(email.processed_at.$date) }}</span>
            </div>
            <div class="email-subject">{{ email.subject }}</div>
            <div class="email-preview">{{ email.body.substring(0, 100) }}...</div>
            
            <div class="email-tags">
              <span v-if="email.urgency === 'High'" class="tag tag-high">
                <i class="fas fa-exclamation-triangle"></i> ASAP
              </span>
              <span v-if="email.is_collaboration" class="tag tag-collab">
                <i class="fas fa-handshake"></i> Collaboration
              </span>
              <span v-if="email.ai_data?.scope" class="tag tag-scope">
                {{ email.ai_data.scope }}
              </span>
            </div>
          </div>
        </div>
      </main>

      <!-- Detail Panel (Conditionally shown/Modal) -->
      <EmailDetail 
        v-if="selectedEmail" 
        :email="selectedEmail" 
        @close="selectedEmail = null"
        @converted="handleConverted"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'
import EmailDetail from '@/components/EmailHub/EmailDetail.vue'

const emails = ref([])
const loading = ref(false)
const syncing = ref(false)
const activeFilter = ref('collaboration')
const selectedEmail = ref(null)

const filters = [
  { id: 'collaboration', label: 'Collaborations', icon: 'fas fa-handshake' },
  { id: 'all', label: 'All Mail', icon: 'fas fa-envelope' },
  { id: 'skim', label: 'To Skim', icon: 'fas fa-eye' },
  { id: 'processed', label: 'Done', icon: 'fas fa-check-double' }
]

const getEmails = async () => {
    loading.value = true
    try {
        const response = await apiGet('/emails/')
        emails.value = response.emails
    } catch (e) {
        showError('Failed to load emails')
    } finally {
        loading.value = false
    }
}

const syncEmails = async () => {
    syncing.value = true
    try {
        const resp = await apiPost('/emails/sync')
        showSuccess(resp.message)
        // Set a timeout to re-fetch after background processing
        setTimeout(getEmails, 5000)
    } catch (e) {
        showError('Failed to sync emails')
    } finally {
        syncing.value = false
    }
}

const filteredEmails = computed(() => {
    if (activeFilter.value === 'collaboration') {
        return emails.value.filter(e => e.is_collaboration)
    }
    if (activeFilter.value === 'skim') {
        return emails.value.filter(e => e.status === 'Skim')
    }
    return emails.value
})

const getCount = (id) => {
    if (id === 'collaboration') return emails.value.filter(e => e.is_collaboration).length
    if (id === 'skim') return emails.value.filter(e => e.status === 'Skim').length
    return 0
}

const formatTime = (dateStr) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const selectEmail = (email) => {
    selectedEmail.value = email
}

const handleConverted = () => {
    selectedEmail.value = null
    getEmails()
}

onMounted(getEmails)
</script>

<style scoped>
.email-hub {
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

.hub-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  height: calc(100vh - 200px);
}

.hub-sidebar {
  padding: 1rem;
  border-radius: 20px;
}

.hub-main {
  border-radius: 24px;
  padding: 1.5rem;
  overflow-y: auto;
}

.nav-item {
  width: 100%;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
  transition: all 0.3s ease;
  text-decoration: none;
  margin-bottom: 0.5rem;
}

.nav-item:hover, .nav-item.active {
  background: var(--glass-bg-secondary);
  color: #a5b4fc;
}

.badge {
  margin-left: auto;
  background: var(--primary);
  color: white;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 0.75rem;
}

.email-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.email-card {
  padding: 1.5rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.email-card:hover {
  background: rgba(255,255,255,0.07);
  transform: translateY(-2px);
  border-color: rgba(99, 102, 241, 0.3);
}

.urgency-high {
  border-left: 4px solid #ef4444 !important;
  background: rgba(239, 68, 68, 0.05);
}

.is-collab {
  border-left: 4px solid #6366f1;
}

.email-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.sender {
  font-weight: bold;
  color: #a5b4fc;
}

.time {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.email-subject {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.email-preview {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.email-tags {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: bold;
}

.tag-high { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.tag-collab { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; }
.tag-scope { background: rgba(16, 185, 129, 0.2); color: #10b981; }

.loading-state, .empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255,255,255,0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
