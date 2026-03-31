<template>
  <div class="public-explorer" :class="{ 'visitor-mode': metadata?.permission_level === 'visitor' }">
    <!-- Overlay for Password Protection -->
    <div v-if="requiresPassword && !isVerified" class="password-overlay glass-panel">
      <div class="password-box">
        <i class="fas fa-lock text-gold text-4xl mb-6"></i>
        <h2>Private Link</h2>
        <p class="text-secondary mb-6">This link is protected. Please enter the password to continue.</p>
        <input 
          type="password" 
          v-model="password" 
          placeholder="Enter password..." 
          class="glass-input-field mb-4"
          @keyup.enter="verifyPassword"
        >
        <button class="btn-primary vault-primary w-full" @click="verifyPassword" :disabled="loading">
          {{ loading ? 'Verifying...' : 'Access Shared Item' }}
        </button>
      </div>
    </div>

    <!-- Context Menu -->
    <div 
      v-if="contextMenu.visible" 
      class="context-menu glass-panel" 
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <template v-if="contextMenu.item">
        <div class="menu-item" v-if="contextMenu.item.is_folder" @click="downloadFolderZip(contextMenu.item)">
          <i class="fas fa-file-archive"></i> Zip and Download
        </div>
        <div class="menu-item" v-else @click="downloadFile(contextMenu.item)">
          <i class="fas fa-download"></i> Download File
        </div>
        <div class="menu-item" v-if="!contextMenu.item.is_folder" @click="openInNewTab(contextMenu.item)">
          <i class="fas fa-external-link-alt"></i> Open in New Tab
        </div>
      </template>
      <template v-else>
        <!-- For breadcrumbs or background -->
        <div class="menu-item" @click="downloadFolderZip(null)">
          <i class="fas fa-file-archive"></i> Zip and Download Folder
        </div>
      </template>
    </div>

    <!-- Main Explorer UI -->
    <template v-if="!requiresPassword || isVerified">
      <div class="explorer-layout">
        <!-- Header -->
        <header class="explorer-header glass-panel">
          <div class="logo-area" @click="$router.push('/')">
            <span class="logo-text">DHQ <span class="text-gold">Public</span> Explorer</span>
          </div>
          <div class="breadcrumb-area">
            <span class="crumb root-crumb" @contextmenu.prevent="showContextMenu($event, null)">Public: {{ metadata?.name }}</span>
            <i class="fas fa-chevron-right separator" v-if="breadcrumbs.length > 2"></i>
            <span v-for="(part, idx) in breadcrumbs.slice(2)" :key="idx" class="crumb" @click="navigateBack(idx + 2)" @contextmenu.prevent="showContextMenu($event, { is_folder: true, filename: part, virtual_path: getPathForIdx(idx + 2) })">
              {{ part }}
              <i class="fas fa-chevron-right separator" v-if="idx < breadcrumbs.length - 3"></i>
            </span>
          </div>
          <div class="user-status" v-if="currentUser">
            <span class="badge">Logged in as {{ currentUser.username }}</span>
          </div>
        </header>

        <div class="explorer-body">
          <main class="files-area">
            <div v-if="loading" class="loader-box">
              <i class="fas fa-spinner fa-spin text-4xl text-gold"></i>
              <p class="mt-4">Decrypting public link...</p>
            </div>

            <!-- Single File View -->
            <div v-else-if="metadata?.type === 'file'" class="file-view-container">
               <div class="file-card glass-panel" :class="{ 'blur-content': devToolsDetected }">
                 <div class="file-preview-large">
                   <template v-if="isImage(metadata.name)">
                     <canvas v-if="metadata.permission_level === 'visitor'" ref="imageCanvas" class="preview-canvas"></canvas>
                     <img v-else :src="previewUrl" alt="Preview" class="preview-img">
                   </template>
                   <template v-else-if="isVideo">
                     <video :src="previewUrl" controls class="preview-video" oncontextmenu="return false;" controlsList="nodownload"></video>
                   </template>
                   <template v-else-if="isPDF">
                     <!-- PDF Thumbnail / Link -->
                     <div class="pdf-placeholder">
                        <i class="fas fa-file-pdf icon-huge"></i>
                        <p>PDF Preview via Secure Stream</p>
                     </div>
                   </template>
                   <template v-else>
                     <i :class="['fas', getFileIcon(metadata.name), 'icon-huge']"></i>
                   </template>
                   
                   <div v-if="devToolsDetected" class="devtools-warning">
                     <i class="fas fa-user-secret text-6xl mb-4"></i>
                     <h2>Security Breach Detected</h2>
                     <p>Please close Developer Tools to view this high-security content.</p>
                   </div>
                 </div>
                 <div class="file-info-bar">
                   <div class="info-text">
                     <h3>{{ metadata.name }}</h3>
                     <p>{{ formatSize(metadata.size) }} • {{ metadata.owner_name }}</p>
                   </div>
                   <div class="actions">
                     <button v-if="canDownload" class="btn-primary" @click="handleDownload">
                       <i class="fas fa-download"></i> Download
                     </button>
                     <span v-else class="visitor-badge">
                       <i class="fas fa-eye"></i> Visitor Mode
                     </span>
                   </div>
                 </div>
               </div>
            </div>

            <!-- Folder Contents Grid -->
            <div v-else class="files-grid">
              <div 
                v-for="item in folderContents" 
                :key="item.id" 
                class="grid-item"
                :class="{ 
                  'is-blurred': item.access_level === 'only_me',
                  'is-locked': item.access_level === 'internal' && !userStore.isAuthenticated
                }"
                @click="handleItemClick(item)"
              >
                <div class="item-icon-wrapper">
                  <template v-if="item.access_level === 'only_me'">
                    <div class="blur-overlay">
                      <i class="fas fa-eye-slash"></i>
                      <span>Private</span>
                    </div>
                    <i :class="[getFileIcon(item.name), 'file-icon blurred-icon']"></i>
                  </template>
                  <template v-else-if="item.access_level === 'internal' && !userStore.isAuthenticated">
                    <div class="lock-overlay">
                      <i class="fas fa-user-lock"></i>
                      <span>Login Required</span>
                    </div>
                    <i :class="[getFileIcon(item.name), 'file-icon']"></i>
                  </template>
                  <template v-else>
                    <img v-if="isImage(item.name)" :src="getThumbnailUrlForItem(item)" alt="Thumbnail" class="grid-thumbnail">
                    <i v-else :class="[getFileIcon(item.name), 'file-icon']"></i>
                  </template>
                </div>
                <div class="item-name" :title="item.name">{{ item.name }}</div>
                
                <!-- Permission Note for restricted items -->
                <div v-if="item.access_level === 'only_me'" class="permission-note">
                  Ask owner for access
                </div>
                <div v-else-if="item.access_level === 'internal' && !userStore.isAuthenticated" class="permission-note">
                  Please log in to view
                </div>
              </div>
            </div>
          </main>

          <!-- Side Panels -->
          <aside class="explorer-sidebars">
            <div class="side-panel glass-panel">
              <div class="panel-header">
                <i class="fas fa-info-circle mr-2"></i> Details
              </div>
              <div class="panel-body">
                 <div class="detail-row">
                   <span class="label">Permission</span>
                   <span class="value capitalize text-gold">{{ metadata?.permission_level }}</span>
                 </div>
                 <div class="detail-row">
                   <span class="label">Owned By</span>
                   <span class="value">{{ metadata?.owner_name }}</span>
                 </div>
              </div>
            </div>

            <!-- Comments -->
            <div v-if="canComment" class="side-panel glass-panel comments-panel">
              <div class="panel-header">
                <i class="fas fa-comments mr-2"></i> Community
              </div>
              <div class="panel-body comments-list">
                <div v-for="c in comments" :key="c.id" class="comment-item">
                  <div class="comment-header">
                    <span class="author">{{ c.user?.display_name || c.guest_name || 'Guest' }}</span>
                    <span class="date">{{ formatDate(c.created_at) }}</span>
                  </div>
                  <div class="comment-content">{{ c.content }}</div>
                </div>
              </div>
              <div class="panel-footer">
                <input type="text" v-model="newComment" placeholder="Share your thoughts..." class="glass-input-field-small" @keyup.enter="postComment">
                <button class="btn-icon" @click="postComment">
                  <i class="fas fa-paper-plane"></i>
                </button>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </template>

    <!-- Restricted Overlay for Visitor -->
    <div v-if="metadata?.permission_level === 'visitor'" class="visitor-watermark">
      PREVIEW ONLY • SECURE LINK • DHQ SHIELD
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiGet, apiPost } from '@/utils/api'
import { showError, showSuccess } from '@/utils/notification'

const route = useRoute()
const router = useRouter()
const hash = route.params.hash

const loading = ref(true)
const is404 = ref(false)
const metadata = ref(null)
const files = ref([])
const comments = ref([])
const password = ref('')
const isVerified = ref(false)
const requiresPassword = computed(() => metadata.value?.has_password)
const newComment = ref('')
const previewUrl = ref('')
const imageCanvas = ref(null)
const devToolsDetected = ref(false)
const currentUser = ref(null)
const contextMenu = ref({ visible: false, x: 0, y: 0, item: null })
const transientToken = ref('')
const currentPath = ref('/')
const folderContents = ref([])

onMounted(async () => {
  const userData = localStorage.getItem('user')
  if (userData) currentUser.value = JSON.parse(userData)
  
  await fetchMetadata()
  if (!requiresPassword.value) {
    await initializeView()
  }

  // Global click to hide context menu
  window.addEventListener('click', hideContextMenu)
})

const showContextMenu = (e, item) => {
  e.preventDefault()
  contextMenu.value = {
    visible: true,
    x: e.clientX,
    y: e.clientY,
    item: item
  }
}

const hideContextMenu = () => {
  contextMenu.value.visible = false
}

const breadcrumbs = computed(() => {
  if (currentPath.value === '/' || !currentPath.value) return []
  return currentPath.value.split('/').filter(p => p)
})

const navigateToBreadcrumb = (index) => {
  const parts = currentPath.value.split('/').filter(p => p)
  currentPath.value = '/' + parts.slice(0, index + 1).join('/')
  loadFolderContents()
}

const navigateToRoot = async () => {
  currentPath.value = '/'
  // If we are deep in a child file, we need to reset metadata to root share
  if (metadata.value.is_child) {
    await fetchMetadata()
  } else {
    await loadFolderContents()
  }
}

const hasThumbnail = (file) => {
  if (file.is_folder) return false
  const ext = file.filename.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'pdf'].includes(ext)
}

const getThumbnailUrl = (file) => {
  const tokenPart = transientToken.value ? `&token=${transientToken.value}` : ''
  const passwordPart = (!transientToken.value && password.value) ? `&password=${password.value}` : ''
  return `/api/public/thumbnail/${hash}?file_id=${file.id}${tokenPart}${passwordPart}`
}

const downloadFolderZip = (item) => {
  let url = `/api/public/zip/${hash}?password=${password.value}`
  
  if (item && item.virtual_path) {
    // From breadcrumbs
    url += `&sub_path=${encodeURIComponent(item.virtual_path)}`
  } else if (item && item.is_folder) {
    // From grid item
    // Calculate relative subpath
    const rootPath = metadata.value.folder_path === '/' ? '' : metadata.value.folder_path.replace(/\/$/, '')
    const rootPrefix = rootPath + '/' + metadata.value.filename
    
    const itemPath = item.folder_path === '/' ? '' : item.folder_path.replace(/\/$/, '')
    const itemFullPath = itemPath + '/' + item.filename
    
    const subPath = itemFullPath.replace(rootPrefix, '').replace(/^\//, '')
    if (subPath) url += `&sub_path=${encodeURIComponent(subPath)}`
  }
  
  window.open(url)
  if (typeof hideContextMenu === 'function') hideContextMenu()
}

const openInNewTab = (file) => {
  if (file.is_folder) return
  window.open(`/s/${hash}/view?file_id=${file.id}`)
  hideContextMenu()
}

// DevTools detection
const detectDevTools = () => {
  const threshold = 160
  const widthDiff = window.outerWidth - window.innerWidth > threshold
  const heightDiff = window.outerHeight - window.innerHeight > threshold
  if (widthDiff || heightDiff) {
    devToolsDetected.value = true
  } else {
    devToolsDetected.value = false
  }
}

window.addEventListener('resize', detectDevTools)
setInterval(detectDevTools, 2000)

const fetchMetadata = async () => {
  try {
    console.log('[PublicView] Fetching metadata for hash:', hash)
    metadata.value = await apiGet(`/public/access/${hash}`)
    console.log('[PublicView] Metadata received:', metadata.value)
    
    if (!metadata.value) {
      throw new Error('Emply metadata received')
    }
    
    breadcrumbs.value = ['Public', metadata.value.name]
    
    if (metadata.value.type === 'folder') {
      await loadFolderContents()
    } else if (metadata.value.type === 'file') {
      // Forward individual files immediately to EmbedView
      router.replace({ name: 'PublicFileView', params: { hash: hash } })
      return
    }
  } catch (err) {
    console.error('[PublicView] Failed to fetch metadata:', err)
    showError('Link invalid or expired')
    is404.value = true
  }
  loading.value = false
}

const verifyPassword = async () => {
  if (!password.value) return
  loading.value = true
  try {
    await apiPost(`/public/verify/${hash}`, { password: password.value })
    isVerified.value = true
    await initializeView()
  } catch (err) {
    showError('Incorrect password')
  } finally {
    loading.value = false
  }
}

const loadFolderContents = async () => {
  try {
    const res = await apiGet(`/public/files/${metadata.value.share_id}?folder_path=${currentPath.value}${password.value ? '&password=' + encodeURIComponent(password.value) : ''}`)
    folderContents.value = res
  } catch (err) {
    showError('Failed to load folder contents')
  }
}

const initializeView = async () => {
  loading.value = true
  try {
    // Fetch a transient token for subsequent resource loads (thumbnails, etc)
    try {
      const { token } = await apiGet(`/public/token/${hash}${password.value ? '?password=' + password.value : ''}`)
      transientToken.value = token
    } catch (e) {
      console.warn('Failed to fetch transient token', e)
    }

    if (metadata.value.type === 'folder') {
      await loadFolder()
    } else if (metadata.value.type === 'file') {
      await refreshPreview()
    }
    if (canComment.value) {
      await loadComments()
    }
  } catch (err) {
    showError('Failed to load shared content')
  } finally {
    loading.value = false
  }
}

const refreshPreview = async () => {
  if (metadata.value.type !== 'file') return
  
  try {
    // 1. Fetch one-time token
    const { token } = await apiGet(`/public/token/${hash}${password.value ? '?password=' + password.value : ''}`)
    
    // 2. Construct transient URL
    const url = `/api/public/download/${hash}?preview=true&token=${token}`
    transientToken.value = token
    
    if (metadata.value.permission_level === 'visitor' && isImage(metadata.value.name)) {
       // Canvas rendering for images
       await renderToCanvas(url)
    } else {
       previewUrl.value = url
    }
  } catch (err) {
    showError('Could not generate secure preview')
  }
}

const renderToCanvas = (url) => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = "anonymous"
    img.onload = () => {
      const canvas = imageCanvas.value
      if (!canvas) return resolve()
      const ctx = canvas.getContext('2d')
      
      // Auto-scale canvas
      const maxWidth = 800
      const scale = Math.min(1, maxWidth / img.width)
      canvas.width = img.width * scale
      canvas.height = img.height * scale
      
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
      
      // Add a subtle scanline or noise pattern to deter screenshots
      ctx.fillStyle = "rgba(255, 255, 255, 0.05)"
      for (let i = 0; i < canvas.height; i += 4) {
        ctx.fillRect(0, i, canvas.width, 1)
      }
      
      resolve()
    }
    img.onerror = reject
    img.src = url
  })
}

// Legacy loadFolder removed, using loadFolderContents instead

const loadComments = async () => {
  comments.value = await apiGet(`/public/comments/${hash}`)
}

const postComment = async () => {
  if (!newComment.value.trim()) return
  try {
    let payload = { content: newComment.value }
    if (!currentUser.value && metadata.value.permission_level === 'editor') {
       payload.guest_name = 'Anonymous Editor'
    }
    
    await apiPost(`/public/comments/${hash}`, payload)
    newComment.value = ''
    await loadComments()
    showSuccess('Comment posted')
  } catch (err) {
    showError(err.message || 'Failed to post comment')
  }
}

// Permissions
const canDownload = computed(() => {
  if (!metadata.value) return false
  return ['viewer', 'commenter', 'editor'].includes(metadata.value.permission_level)
})

const canComment = computed(() => {
  if (!metadata.value) return false
  return ['commenter', 'editor'].includes(metadata.value.permission_level)
})

const canEdit = computed(() => {
  if (!metadata.value) return false
  return metadata.value.permission_level === 'editor'
})

// UI Helpers
const isImage = (name) => {
  if (!name) return false
  const ext = name.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)
}

const getThumbnailUrlForItem = (item) => {
  const tokenPart = transientToken.value ? `&token=${transientToken.value}` : ''
  const passwordPart = (!transientToken.value && password.value) ? `&password=${password.value}` : ''
  return `/api/public/thumbnail/${hash}?file_id=${item.id}${tokenPart}${passwordPart}`
}
const isVideo = computed(() => metadata.value?.mime_type?.startsWith('video/'))
const isPDF = computed(() => {
  const name = metadata.value?.name || ''
  return name.toLowerCase().endsWith('.pdf') || metadata.value?.mime_type === 'application/pdf'
})

const downloadUrl = (preview = false) => {
  const base = `/api/public/download/${hash}`
  return `${base}?preview=${preview}${isVerified.value ? '&password=' + password.value : ''}`
}

const handleDownload = () => {
  window.open(downloadUrl(false), '_blank')
}

const getFileIcon = (name) => {
  if (!name) return 'fa-file'
  const ext = name.split('.').pop().toLowerCase()
  if (['jpg', 'png', 'gif', 'webp'].includes(ext)) return 'fa-file-image'
  if (['mp4', 'mkv', 'webm'].includes(ext)) return 'fa-file-video'
  if (['pdf'].includes(ext)) return 'fa-file-pdf'
  if (['zip', 'rar'].includes(ext)) return 'fa-file-archive'
  return 'fa-file-alt'
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

const handleItemClick = (item) => {
  if (item.access_level === 'only_me') {
    showError('This item is private. Please ask the owner for access.')
    return
  }
  
  if (item.access_level === 'internal' && !userStore.isAuthenticated) {
    showError('This item requires an account. Please log in to view.')
    return
  }

  if (item.is_folder) {
    const base = currentPath.value === '/' ? '' : currentPath.value
    currentPath.value = `${base}/${item.name}`
    loadFolderContents()
  } else {
    // Open file view for individual file
    // We reuse the main preview modal but need to fetch metadata for the child
    openFilePreview(item)
  }
}

const openFilePreview = async (item) => {
   // Forward individual files in grid immediately to EmbedView
   router.push({ name: 'PublicFileView', params: { hash: hash }, query: { file_id: item.id } })
}

// Redundant navigation removed
</script>

<style scoped>
.public-explorer {
  width: 100vw;
  height: 100vh;
  background: #0a0a0b;
  color: #fff;
  font-family: 'Outfit', sans-serif;
  overflow: hidden;
  position: relative;
  user-select: none;
  -webkit-user-select: none;
}

.password-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(20px);
}

.password-box {
  width: 100%;
  max-width: 400px;
  text-align: center;
  padding: 3rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.explorer-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.explorer-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 2rem;
  border-bottom: 1px solid var(--glass-border);
  gap: 2rem;
}

.logo-text { font-size: 1.25rem; font-weight: 800; cursor: pointer; }

.breadcrumb-area {
  flex-grow: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
}

.crumb { cursor: pointer; transition: color 0.2s; }
.crumb:hover { color: white; }
.separator { font-size: 0.75rem; margin: 0 0.25rem; }

.explorer-body {
  flex-grow: 1;
  display: flex;
  overflow: hidden;
}

.files-area {
  flex-grow: 1;
  padding: 2rem;
  overflow-y: auto;
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1.5rem;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.grid-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-5px);
  border-color: var(--glass-border);
}

.item-icon { 
  font-size: 2.5rem; 
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  margin-bottom: 0.5rem;
}

.item-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.grid-item:hover .item-thumb {
  transform: scale(1.1);
}

.folder-icon { color: #facc15; }
.file-icon { color: #3b82f6; }
.item-name {
  font-size: 0.875rem;
  text-align: center;
  word-break: break-all;
}

.explorer-sidebars {
  width: 320px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-left: 1px solid var(--glass-border);
}

.side-panel {
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  font-weight: 700;
  font-size: 0.875rem;
  border-bottom: 1px solid var(--glass-border);
}

.panel-body { padding: 1rem; }

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.detail-row .label { color: var(--text-secondary); }

.comments-panel { flex-grow: 1; }
.comments-list {
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 0.75rem;
  border-radius: 8px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
}

.comment-header .author { color: var(--gold-primary); font-weight: 700; }
.comment-header .date { color: var(--text-secondary); }
.comment-content { font-size: 0.875rem; opacity: 0.9; }

.panel-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--glass-border);
  display: flex;
  gap: 0.5rem;
}

.context-menu {
  position: fixed;
  z-index: 10000;
  min-width: 180px;
  background: rgba(20, 20, 25, 0.9);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 5px 0;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

.menu-item {
  padding: 10px 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.menu-item i {
  width: 20px;
  text-align: center;
  color: var(--text-secondary);
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fbbf24;
}

.menu-item:hover i {
  color: #fbbf24;
}
.glass-input-field-small {
  flex-grow: 1;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: white;
  font-size: 0.875rem;
}

.file-view-container {
  max-width: 800px;
  margin: 0 auto;
}

.file-card {
  border-radius: 20px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.03);
}

.file-preview-large {
  height: 400px;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.preview-img { max-width: 100%; max-height: 100%; object-fit: contain; }
.preview-video { width: 100%; height: 100%; }
.icon-huge { font-size: 8rem; color: var(--text-secondary); opacity: 0.5; }

.file-info-bar {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-text h3 { margin: 0; font-size: 1.25rem; }
.info-text p { color: var(--text-secondary); margin: 0.25rem 0 0 0; }

.visitor-mode .files-area, .visitor-mode .preview-box {
  user-select: none;
}

.blur-content {
  filter: blur(25px) grayscale(100%);
  transition: filter 0.5s ease;
  pointer-events: none;
}

.devtools-warning {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  text-align: center;
  padding: 2rem;
  backdrop-filter: blur(10px);
}

.preview-canvas {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  box-shadow: 0 10px 50px rgba(0,0,0,0.5);
  border-radius: 8px;
}

.visitor-watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-45deg);
  font-size: 4rem;
  color: rgba(255, 255, 255, 0.07);
  white-space: nowrap;
  pointer-events: none;
  z-index: 500;
  font-weight: 900;
  letter-spacing: 1px;
  text-shadow: 0 0 10px rgba(255,255,255,0.05);
}

.visitor-badge {
  background: rgba(250, 204, 21, 0.1);
  color: #facc15;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 700;
  border: 1px solid #facc1550;
}

.no-comments {
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: 2rem 0;
}

.btn-icon {
  background: var(--gold-primary);
  color: black;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.is-blurred .grid-thumbnail,
.is-blurred .file-icon {
  filter: blur(12px) grayscale(80%);
  opacity: 0.6;
}

.item-icon-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.grid-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.blur-overlay,
.lock-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  color: white;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-align: center;
  padding: 0.5rem;
}

.blur-overlay i,
.lock-overlay i {
  font-size: 1.25rem;
  color: #fbbf24;
}

.permission-note {
  font-size: 0.7rem;
  color: #fbbf24;
  margin-top: -0.5rem;
  font-weight: 600;
  opacity: 0.8;
}

.is-locked .permission-note {
  color: #60a5fa;
}

.breadcrumb-area {
  flex-grow: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.crumb {
  cursor: pointer;
  transition: all 0.2s;
  padding: 4px 8px;
  border-radius: 4px;
}

.crumb:hover {
  color: white;
  background: rgba(255, 255, 255, 0.05);
}

.separator {
  font-size: 0.7rem;
  opacity: 0.4;
}

.pdf-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  color: var(--text-secondary);
}
</style>
