<template>
  <div class="settings-view">
    <div class="settings-container">
      <div class="settings-header">
        <h1>⚙️ User Settings</h1>
        <p>Manage your account, profile, and preferences</p>
      </div>

      <div class="settings-layout">
        <!-- Sidebar Tabs -->
        <aside class="settings-sidebar glass-panel">
          <nav class="settings-nav">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              :class="['nav-item', { active: activeTab === tab.id }]"
              @click="activeTab = tab.id"
            >
              <i :class="tab.icon"></i>
              {{ tab.label }}
            </button>
          </nav>
        </aside>

        <!-- Main Content -->
        <main class="settings-main glass-panel">
          <!-- Profile Settings -->
          <div v-if="activeTab === 'profile'" class="tab-content">
            <section class="settings-section">
              <h3>Public Profile</h3>
              
              <!-- Banner Upload -->
              <div class="banner-upload-section">
                <label>Profile Banner</label>
                <div 
                  class="banner-preview" 
                  :style="{ backgroundImage: bannerPreview || (bannerUrl ? `url(${bannerUrl})` : 'none') }"
                >
                  <div class="banner-actions">
                    <button class="btn-icon" @click="$refs.bannerInput.click()">
                      <i class="fas fa-camera"></i>
                    </button>
                  </div>
                  <input type="file" ref="bannerInput" hidden @change="handleBannerSelect" accept="image/*" />
                </div>
              </div>

              <!-- Avatar Upload -->
              <div class="avatar-upload-section">
                <div class="avatar-current" @click="$refs.avatarInput.click()">
                  <img :src="avatarPreview || avatarUrl || defaultAvatar" class="avatar-img" />
                  <div class="avatar-edit-overlay">
                    <i class="fas fa-camera"></i>
                  </div>
                </div>
                <div class="avatar-text">
                  <label>Profile Picture</label>
                  <p>Click to change. Square images work best.</p>
                  <button v-if="avatarUrl" class="btn-text mt-2" @click="resetAvatar">
                    <i class="fas fa-undo"></i> Reset to Default
                  </button>
                </div>
                <input type="file" ref="avatarInput" hidden @change="handleAvatarSelect" accept="image/*" />
              </div>

              <!-- Form Fields -->
              <div class="form-grid">
                <div class="form-group">
                  <label>Display Name</label>
                  <input v-model="profileForm.display_name" type="text" placeholder="Your brand name" />
                </div>
                <div class="form-group">
                  <label>Email Address</label>
                  <input v-model="profileForm.email" type="email" placeholder="email@example.com" />
                </div>
              </div>

              <div class="section-footer">
                <button class="btn btn-primary" :disabled="saving" @click="saveProfile">
                  <i class="fas" :class="saving ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                  {{ saving ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </section>
          </div>

          <!-- Appearance Settings -->
          <div v-if="activeTab === 'appearance'" class="tab-content">
            <section class="settings-section">
              <h3>Theme Selection</h3>
              <p class="section-desc">Choose your interface style. Unlock premium themes in the Arcade.</p>
              
              <div class="theme-grid">
                <div 
                  v-for="theme in themes" 
                  :key="theme.id"
                  :class="['theme-card', { 
                    active: userStore.activeTheme === theme.id,
                    locked: !isThemeUnlocked(theme.id)
                  }]"
                  @click="selectTheme(theme.id)"
                >
                  <div class="theme-preview" :style="{ background: theme.color }">
                    <div v-if="!isThemeUnlocked(theme.id)" class="lock-overlay" :title="theme.requirement">
                      <i class="fas fa-lock"></i>
                      <span class="unlock-hint">{{ theme.requirement }}</span>
                    </div>
                    <div v-if="userStore.activeTheme === theme.id" class="active-check">
                      <i class="fas fa-check"></i>
                    </div>
                  </div>
                  <span class="theme-name">{{ theme.name }}</span>
                </div>
              </div>
            </section>

            <section class="settings-section mt-8">
              <h3>Side Menu View</h3>
              <p class="section-desc">Choose how your navigation links are displayed.</p>
              
              <div class="layout-toggle-grid">
                <div 
                  :class="['layout-option', { active: userStore.sideMenuLayout === 'list' }]"
                  @click="updateLayout('list')"
                >
                  <div class="layout-preview list-preview">
                    <div class="line"></div>
                    <div class="line"></div>
                    <div class="line"></div>
                  </div>
                  <span>List View</span>
                </div>
                
                <div 
                  :class="['layout-option', { active: userStore.sideMenuLayout === 'grid' }]"
                  @click="updateLayout('grid')"
                >
                  <div class="layout-preview grid-preview">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                  </div>
                  <span>Grid View</span>
                </div>
              </div>
            </section>
          </div>

          <!-- Credentials & API Settings -->
          <div v-if="activeTab === 'credentials'" class="tab-content">
            <section class="settings-section">
              <h3>Credentials & AI Configuration</h3>
              <p class="section-desc">Manage your email credentials, AI providers, and API keys for external services.</p>
              
              <!-- Email Credentials Section -->
              <div class="credentials-section mt-8">
                <h4 class="text-lg font-bold mb-4 flex items-center gap-2">
                  <i class="fas fa-envelope text-primary"></i>
                  Email Credentials (IMAP)
                </h4>
                <div class="glass-panel p-6 bg-slate-900/40 border-slate-700/50 mb-8">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="form-group">
                      <label>IMAP Email</label>
                      <input v-model="credentialsForm.email" type="email" placeholder="your-email@gmail.com" />
                    </div>
                    <div class="form-group">
                      <label>App Password / Password</label>
                      <input v-model="credentialsForm.password" type="password" placeholder="••••••••••••" />
                    </div>
                  </div>
                  <div class="mt-4 flex justify-end">
                    <button class="btn btn-primary px-8" @click="saveEmailCredentials" :disabled="savingEmail">
                      <i class="fas" :class="savingEmail ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                      {{ savingEmail ? 'Saving...' : 'Save Email Creds' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- AI Providers Section -->
              <div class="ai-providers-section mt-8">
                <h4 class="text-lg font-bold mb-4 flex items-center gap-2">
                  <i class="fas fa-robot text-primary"></i>
                  AI Providers
                </h4>
                <div class="glass-panel p-6 bg-slate-900/40 border-slate-700/50 mb-8">
                  <div v-for="(provider, index) in aiProviders" :key="index" class="provider-row mb-6 pb-6 border-b border-slate-800/50 last:border-0 last:mb-0 last:pb-0">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div class="form-group">
                        <label>Provider</label>
                        <select v-model="provider.type" class="form-input bg-slate-800 h-[42px] py-0">
                          <option value="openai">OpenAI</option>
                          <option value="gemini">Google Gemini</option>
                          <option value="anthropic">Anthropic</option>
                          <option value="deepseek">DeepSeek</option>
                        </select>
                      </div>
                      <div class="form-group md:col-span-2">
                        <label>API Key</label>
                        <div class="relative">
                          <input v-model="provider.api_key" type="password" class="form-input pr-12 h-[42px]" placeholder="sk-..." />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="mt-4 flex justify-between items-center">
                    <button class="btn border border-slate-600 hover:border-primary text-slate-300 hover:text-white" @click="addAIProvider">
                      <i class="fas fa-plus mr-2"></i> Add AI Provider
                    </button>
                    <button class="btn btn-primary px-8" @click="saveAIProviders" :disabled="savingAI">
                      <i class="fas" :class="savingAI ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                      {{ savingAI ? 'Saving...' : 'Save AI Config' }}
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="api-keys-management mt-8">
                <h4 class="text-lg font-bold mb-4 flex items-center gap-2">
                  <i class="fas fa-key text-primary"></i>
                  External API Keys
                </h4>
                
                <div 
                  class="glass-panel p-6 bg-slate-900/40 border-slate-700/50 mb-6 transition-all duration-500"
                  :class="{ 'ring-2 ring-primary ring-offset-4 ring-offset-slate-900 bg-primary/10 shadow-[0_0_50px_rgba(99,102,241,0.2)]': isHighlightingApi }"
                  id="api-key-section"
                >
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                    <div class="form-group mb-0">
                      <label>Select API Server</label>
                      <select v-model="selectedServerId" class="form-input bg-slate-800 h-[42px] py-0">
                        <option value="" disabled selected>Choose a server...</option>
                        <option v-for="server in apiServers" :key="server.id" :value="server.id">
                          {{ server.display_name }}
                        </option>
                      </select>
                    </div>
                    
                    <div class="form-group mb-0">
                      <label>
                        {{ selectedServerName === 'Internal API Server' ? 'Internal Access Token' : 'Personal API Key' }}
                      </label>
                      <div class="relative">
                        <input 
                          v-model="newApiKey" 
                          :type="(showKey && selectedServerName !== 'Internal API Server') ? 'text' : 'password'" 
                          class="form-input pr-12 h-[42px]" 
                          :placeholder="selectedServerName === 'Internal API Server' ? 'Click Regenerate to create a new token' : 'Paste your API key here...'" 
                          :disabled="selectedServerName === 'Internal API Server'"
                          autocomplete="new-password"
                          @copy="selectedServerName === 'Internal API Server' ? $event.preventDefault() : null"
                          @paste="selectedServerName === 'Internal API Server' ? $event.preventDefault() : null"
                          @contextmenu="selectedServerName === 'Internal API Server' ? $event.preventDefault() : null"
                        />
                        <button 
                          v-if="selectedServerName !== 'Internal API Server'"
                          @click="showKey = !showKey" 
                          class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                        >
                          <i class="fas" :class="showKey ? 'fa-eye-slash' : 'fa-eye'"></i>
                        </button>
                      </div>
                      <div class="h-4">
                        <p v-if="selectedServerName === 'Internal API Server'" class="text-[9px] text-primary mt-1 italic leading-none">
                          <i class="fas fa-info-circle mr-1"></i> For security, internal tokens cannot be viewed, copied, or manually edited.
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="mt-4 flex justify-end gap-3">
                    <button 
                      v-if="selectedServerName === 'Internal API Server'"
                      class="btn border border-primary text-primary hover:bg-primary/10 px-8"
                      :disabled="savingKey"
                      @click="regenerateInternalKey"
                    >
                      <i class="fas" :class="savingKey ? 'fa-spinner fa-spin' : 'fa-sync-alt'"></i>
                      {{ userApiKeys.find(k => k.server_name === 'Internal API Server') ? 'Regenerate Token' : 'Generate Token' }}
                    </button>
                    <button 
                      v-else
                      class="btn btn-primary px-8" 
                      :disabled="!selectedServerId || !newApiKey || savingKey"
                      @click="saveApiKey"
                    >
                      <i class="fas" :class="savingKey ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                      {{ savingKey ? 'Saving...' : 'Save API Key' }}
                    </button>
                  </div>
                </div>

                <div class="activity-history mt-12 pt-8 border-t border-slate-800/50">
                  <h4 class="text-lg font-bold mb-4 flex items-center gap-2">
                    <i class="fas fa-terminal text-primary"></i>
                    SMM API Tokens
                  </h4>
                  <label class="block mb-4 font-bold text-slate-400 uppercase text-xs tracking-widest">Configured Keys</label>
                  <div v-if="userApiKeys.length > 0" class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                      <thead>
                        <tr class="text-xs text-slate-500 uppercase border-b border-slate-700/50">
                          <th class="py-3 px-4">Provider</th>
                          <th class="py-3 px-4">Key Preview</th>
                          <th class="py-3 px-4 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="key in userApiKeys" :key="key.id" class="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors">
                          <td class="py-4 px-4 font-bold text-slate-200">{{ key.server_name }}</td>
                          <td class="py-4 px-4 font-mono text-xs text-slate-400">
                            {{ key.api_key.substring(0, 4) }}••••••••
                          </td>
                          <td class="py-4 px-4 text-right">
                            <button @click="deleteUserApiKey(key.id)" class="text-danger hover:text-red-400 transition-colors">
                              <i class="fas fa-trash"></i>
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div v-else class="text-center py-8 text-slate-500 italic">
                    No individual API keys configured yet.
                  </div>
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>

    <!-- Cropper Modal -->
    <AvatarCropper 
      v-if="showCropper" 
      :image-src="tempImage" 
      :aspect-ratio="cropperType === 'avatar' ? 1 : 21 / 9"
      @crop="applyCrop" 
      @cancel="showCropper = false" 
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/userStore'
import { apiPatch, apiUpload, apiGet, apiPost, apiDelete } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'
import AvatarCropper from '@/components/UserSettings/AvatarCropper.vue'

const userStore = useUserStore()

const activeTab = ref('profile')
const tabs = [
  { id: 'profile', label: 'Profile', icon: 'fas fa-user-circle' },
  { id: 'appearance', label: 'Appearance', icon: 'fas fa-paint-brush' },
  { id: 'credentials', label: 'Credentials', icon: 'fas fa-id-card' },
  { id: 'notifications', label: 'Notifications', icon: 'fas fa-bell' }
]

const themes = [
  { id: 'dark', name: 'Dark', color: '#1e293b', requirement: 'Default' },
  { id: 'light', name: 'Light', color: '#f8fafc', requirement: 'Default' },
  { id: 'glass', name: 'Glass', color: 'rgba(255,255,255,0.1)', requirement: 'Reach Level 5 or play 10 games' },
  { id: 'blue', name: 'Deep Blue', color: '#1e3a8a', requirement: 'Reach 2,000 Lifetime KPI' },
  { id: 'purple', name: 'Royal Purple', color: '#581c87', requirement: 'Reach Level 10' },
  { id: 'pink', name: 'Cyber Pink', color: '#831843', requirement: 'Purchase your first item in the Shop' },
  { id: 'red', name: 'Crimson', color: '#7f1d1d', requirement: 'Maintain a 7-day login streak' },
  { id: 'silver', name: 'Silver Executive', color: '#475569', requirement: 'Play 50 games in the Arcade' },
  { id: 'gold', name: 'Gold Elite', color: '#713f12', requirement: 'Earn 5,000 total KPI or reach Level 20' }
]

const isThemeUnlocked = (themeId) => {
  return userStore.unlockedThemes.includes(themeId)
}

const selectTheme = async (themeId) => {
  if (!isThemeUnlocked(themeId)) return
  try {
    const response = await apiPatch('/user/appearance', { active_theme: themeId })
    userStore.setUser({ active_theme: themeId })
    document.documentElement.setAttribute('data-theme', themeId)
    showSuccess(`${themes.find(t => t.id === themeId).name} theme applied!`)
  } catch (e) {
    showError('Failed to apply theme')
  }
}

const updateLayout = async (layout) => {
  try {
    await apiPatch('/user/appearance', { side_menu_layout: layout })
    userStore.setUser({ side_menu_layout: layout })
    showSuccess(`Layout updated to ${layout} view`)
  } catch (e) {
    showError('Failed to update layout')
  }
}

const profileForm = reactive({
  display_name: '',
  email: ''
})

const avatarUrl = computed(() => userStore.avatarUrl)
const bannerUrl = computed(() => userStore.bannerUrl)
const defaultAvatar = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(userStore.displayName) + '&background=6366f1&color=fff&size=200'

const saving = ref(false)
const showCropper = ref(false)
const cropperType = ref('avatar') // 'avatar' or 'banner'
const tempImage = ref('')
const avatarPreview = ref(null)
const bannerPreview = ref(null)

// API Key Management
const apiServers = ref([])
const userApiKeys = ref([])
const selectedServerId = ref('')
const newApiKey = ref('')
const showKey = ref(false)
const savingKey = ref(false)
const isHighlightingApi = ref(false)

const selectedServerName = computed(() => {
    return apiServers.value.find(s => s.id === selectedServerId.value)?.display_name || ''
})

// Email & AI Credentials
const savingEmail = ref(false)
const savingAI = ref(false)
const credentialsForm = reactive({
    email: '',
    password: ''
})
const aiProviders = ref([
    { type: 'openai', api_key: '' }
])

const addAIProvider = () => {
    aiProviders.value.push({ type: 'openai', api_key: '' })
}

const saveEmailCredentials = async () => {
    savingEmail.value = true
    try {
        await apiPatch('/user/credentials/email', credentialsForm)
        showSuccess('Email credentials saved!')
    } catch (e) {
        showError('Failed to save email credentials')
    } finally {
        savingEmail.value = false
    }
}

const saveAIProviders = async () => {
    savingAI.value = true
    try {
        await apiPatch('/user/credentials/ai', { providers: aiProviders.value })
        showSuccess('AI providers updated!')
    } catch (e) {
        showError('Failed to update AI providers')
    } finally {
        savingAI.value = false
    }
}

const fetchApiServers = async () => {
    try {
        const response = await apiGet('/api-management/servers')
        if (response.success) {
            apiServers.value = response.servers
        }
    } catch (error) {
        console.error('Failed to fetch API servers:', error)
    }
}

const fetchUserApiKeys = async () => {
    try {
        const response = await apiGet('/api-management/user-keys')
        if (response.success) {
            userApiKeys.value = response.keys
        }
    } catch (error) {
        console.error('Failed to fetch user keys:', error)
    }
}

const saveApiKey = async () => {
    if (!selectedServerId.value || !newApiKey.value) return
    savingKey.value = true
    try {
        const response = await apiPost('/api-management/user-keys', {
            api_server_id: selectedServerId.value,
            api_key: newApiKey.value,
            key_name: `Key for ${apiServers.value.find(s => s.id === selectedServerId.value)?.display_name || 'Server'}`
        })
        if (response.success) {
            showSuccess('API key saved successfully!')
            newApiKey.value = ''
            await fetchUserApiKeys()
        }
    } catch (error) {
        showError('Failed to save API key')
    } finally {
        savingKey.value = false
    }
}

const regenerateInternalKey = async () => {
    savingKey.value = true
    try {
        const response = await apiPost('/api-management/internal-token/regenerate')
        if (response.success) {
            showSuccess('Internal API token regenerated!')
            await fetchUserApiKeys()
        }
    } catch (error) {
        showError('Failed to regenerate internal token')
    } finally {
        savingKey.value = false
    }
}

const deleteUserApiKey = async (keyId) => {
    if (!confirm('Are you sure you want to delete this API key?')) return
    try {
        const response = await apiDelete(`/api-management/user-keys/${keyId}`)
        if (response.success) {
            showSuccess('API key deleted')
            await fetchUserApiKeys()
        }
    } catch (error) {
        showError('Failed to delete API key')
    }
}

onMounted(async () => {
  await userStore.fetchProfile()
  profileForm.display_name = userStore.displayName || ''
  profileForm.email = userStore.email || ''
  
  // API Keys
  fetchApiServers()
  fetchUserApiKeys()

  // Load Email & AI credentials from profile
  if (userStore.profile) {
    if (userStore.profile.email_creds) {
      credentialsForm.email = userStore.profile.email_creds.email || ''
    }
    if (userStore.profile.ai_providers && userStore.profile.ai_providers.length > 0) {
      aiProviders.value = userStore.profile.ai_providers.map(p => ({
        type: p.type,
        api_key: p.api_key || ''
      }))
    }
  }

  // Handle Redirection & Highlighting
  const urlParams = new URLSearchParams(window.location.search)
  if (urlParams.get('tab') === 'security' || urlParams.get('tab') === 'credentials') {
    activeTab.value = 'credentials'
    if (urlParams.get('focus') === 'api') {
      setTimeout(() => {
        const el = document.getElementById('api-key-section')
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' })
          isHighlightingApi.value = true
          setTimeout(() => {
            isHighlightingApi.value = false
          }, 3000)
        }
      }, 500)
    }
  }
})

const handleAvatarSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (event) => {
      tempImage.value = event.target.result
      cropperType.value = 'avatar'
      showCropper.value = true
    }
    reader.readAsDataURL(file)
  }
}

const applyCrop = async (blob) => {
  showCropper.value = false
  const filename = cropperType.value === 'avatar' ? 'avatar.jpg' : 'banner.jpg'
  const endpoint = cropperType.value === 'avatar' ? '/user/avatar' : '/user/banner'
  const file = new File([blob], filename, { type: 'image/jpeg' })
  
  // Create preview
  if (cropperType.value === 'avatar') {
    avatarPreview.value = URL.createObjectURL(blob)
  } else {
    bannerPreview.value = `url(${URL.createObjectURL(blob)})`
  }
  
  // Upload immediately for best experience
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiUpload(endpoint, formData)
    
    if (cropperType.value === 'avatar' && response.avatar_url) {
      userStore.setUser({ avatar_url: response.avatar_url })
      showSuccess('Avatar updated!')
    } else if (cropperType.value === 'banner' && response.banner_url) {
      userStore.setUser({ banner_url: response.banner_url })
      showSuccess('Banner updated!')
    }
  } catch (error) {
    showError(`Failed to upload ${cropperType.value}`)
  }
}

const handleBannerSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (event) => {
      tempImage.value = event.target.result
      cropperType.value = 'banner'
      showCropper.value = true
    }
    reader.readAsDataURL(file)
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const response = await apiPatch('/user/profile', profileForm)
    if (response.user) {
      userStore.setUser(response.user)
      showSuccess('Profile updated successfully!')
    }
  } catch (error) {
    showError('Failed to save profile')
  } finally {
    saving.value = false
  }
}

const resetAvatar = async () => {
  if (!confirm('Are you sure you want to reset your avatar to default?')) return
  
  try {
    const { apiPost } = await import('@/utils/api')
    const response = await apiPost('/user/avatar/reset')
    userStore.setUser({ avatar_url: null })
    avatarPreview.value = null
    showSuccess('Avatar reset to default')
  } catch (error) {
    showError('Failed to reset avatar')
  }
}
</script>

<style scoped>
.settings-view {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.settings-header {
  margin-bottom: 2.5rem;
}

.settings-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.settings-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.settings-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  align-items: start;
}

.settings-sidebar {
  padding: 1rem;
  border-radius: 20px;
}

.settings-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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
}

.nav-item:hover {
  background: var(--glass-bg-secondary);
  color: var(--text-primary);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.settings-main {
  min-height: 600px;
  border-radius: 24px;
  padding: 2.5rem;
}

.settings-section h3 {
  margin-top: 0;
  margin-bottom: 2rem;
  font-size: 1.5rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
  padding-bottom: 1rem;
}

.banner-upload-section {
  margin-bottom: 3rem;
}

.banner-upload-section label {
  display: block;
  margin-bottom: 1rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.banner-preview {
  height: 200px;
  border-radius: 16px;
  background-color: var(--glass-bg-secondary);
  background-size: cover;
  background-position: center;
  position: relative;
  border: 2px dashed var(--glass-border);
  transition: all 0.3s ease;
}

.banner-actions {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
}

.avatar-upload-section {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 3rem;
}

.avatar-current {
  position: relative;
  width: 100px;
  height: 100px;
  cursor: pointer;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--glass-border);
}

.avatar-edit-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-current:hover .avatar-edit-overlay {
  opacity: 1;
}

.avatar-text label {
  display: block;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.avatar-text p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-tertiary);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.form-group select {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  color: var(--text-primary);
  transition: all 0.3s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='white'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1.25rem;
}

.form-group select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.form-group select option {
  background-color: #0f172a;
  color: white;
}

/* Fix Autofill background */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 1000px #0f172a inset !important;
    -webkit-text-fill-color: white !important;
    transition: background-color 5000s ease-in-out 0s;
    border: 1px solid var(--glass-border) !important;
}

select option {
  background-color: #0f172a;
  color: white;
}

.section-footer {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--glass-border);
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 0.8rem 2rem;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1rem;
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  background: var(--primary-color);
  transform: scale(1.1);
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-text {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
}

.btn-text:hover {
  filter: brightness(1.2);
  text-decoration: underline;
}

.placeholder-text {
  color: var(--text-tertiary);
  font-style: italic;
  text-align: center;
  padding: 4rem 1rem;
}

.section-desc {
  color: var(--text-secondary);
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1.5rem;
}

.theme-card {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.theme-preview {
  width: 100%;
  aspect-ratio: 16/9;
  border-radius: 12px;
  border: 2px solid var(--glass-border);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.theme-card:hover .theme-preview {
  transform: translateY(-4px);
  border-color: var(--primary-color);
}

.theme-card.active .theme-preview {
  border-color: var(--primary-color);
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
}

.theme-card.locked {
  cursor: not-allowed;
  opacity: 0.8;
}

.lock-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  gap: 0.5rem;
  padding: 1rem;
  text-align: center;
}

.unlock-hint {
  font-size: 0.65rem;
  font-weight: 600;
  display: none;
}

.lock-overlay:hover .unlock-hint {
  display: block;
}

.active-check {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: var(--primary-color);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.theme-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.layout-toggle-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.layout-option {
  cursor: pointer;
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.layout-option:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
}

.layout-option.active {
  background: rgba(99, 102, 241, 0.1);
  border-color: var(--primary-color);
  color: #a5b4fc;
}

.layout-preview {
  width: 80px;
  height: 60px;
  border: 1.5px solid currentColor;
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 6px;
}

.list-preview .line {
  height: 4px;
  background: currentColor;
  border-radius: 2px;
  width: 100%;
}

.grid-preview {
  display: grid !important;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 6px;
  width: 44px !important;
  height: 44px !important;
  padding: 0 !important;
  border: none !important;
}

.grid-preview .dot {
  background: currentColor;
  border-radius: 2px;
}

@media (max-width: 900px) {
  .settings-layout {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .layout-toggle-grid {
    grid-template-columns: 1fr;
  }
}
</style>
