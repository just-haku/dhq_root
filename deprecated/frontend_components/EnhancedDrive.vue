<template>
  <div class="enhanced-drive">
    <!-- Drive Header -->
    <div class="drive-header">
      <div class="header-left">
        <h2>📁 Drive</h2>
        <div class="breadcrumb">
          <span @click="navigateToFolder('/')" class="breadcrumb-item">🏠 Home</span>
          <span v-for="(crumb, index) in breadcrumbs" :key="index">
            <span class="breadcrumb-separator">/</span>
            <span @click="navigateToFolder(crumb.path)" class="breadcrumb-item">{{ crumb.name }}</span>
          </span>
        </div>
      </div>
      
      <div class="header-right">
        <div class="view-controls">
          <button @click="viewMode = 'list'" :class="['view-btn', { active: viewMode === 'list' }]">
            📋 List
          </button>
          <button @click="viewMode = 'grid'" :class="['view-btn', { active: viewMode === 'grid' }]">
            ⚏ Grid
          </button>
        </div>
        
        <div class="drive-actions">
          <button @click="pasteItem" v-if="clipboard.item" class="btn btn-secondary">
            📋 Paste ({{ clipboard.action }})
          </button>
          <button @click="showUploadModal = true" class="btn btn-primary">
            📤 Upload
          </button>
          <button @click="showFolderModal = true" class="btn btn-secondary">
            📁 New Folder
          </button>
        </div>
      </div>
    </div>

    <!-- Quota Information -->
    <div class="quota-info">
      <div class="quota-bar">
        <div class="quota-used" :style="{ width: quotaPercentage + '%' }"></div>
      </div>
      <div class="quota-text">
        {{ formatBytes(quota.used_space) }} of {{ formatBytes(quota.total_quota + quota.additional_quota) }} used
        ({{ quotaPercentage.toFixed(1) }}%)
      </div>
    </div>

    <!-- File Area with Drag and Drop -->
    <div 
      class="file-area"
      :class="{ 
        'drag-over': isDragging, 
        'list-view': viewMode === 'list',
        'grid-view': viewMode === 'grid'
      }"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
      @dragover="handleDragOver"
      @drop="handleDrop"
      @contextmenu.prevent="showContextMenu($event, null)"
    >
      <!-- Drag Overlay -->
      <div v-if="isDragging" class="drag-overlay">
        <div class="drag-message">
          📁 Drop files here to upload to "{{ currentFolderName }}"
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="files.length === 0" class="empty-state">
        <div class="empty-icon">📁</div>
        <h3>No files in {{ currentFolderName }}</h3>
        <p>Upload some files or create folders to get started!</p>
        <button @click="showUploadModal = true" class="btn btn-primary">
          📤 Upload Files
        </button>
      </div>

      <!-- List View -->
      <div v-else-if="viewMode === 'list'" class="file-list">
        <div class="list-header">
          <div class="list-col name">Name</div>
          <div class="list-col size">Size</div>
          <div class="list-col modified">Modified</div>
          <div class="list-col views">Views</div>
          <div class="list-col actions">Actions</div>
        </div>
        <div 
          v-for="file in files" 
          :key="file.id"
          class="list-item file-item"
          :class="{ selected: selectedFiles.has(file.id) }"
          @click="selectFile(file, $event)"
          @dblclick="openFile(file)"
          @contextmenu.prevent="showContextMenu($event, file)"
          @dragstart="handleDragStart(file, $event)"
          @dragend="handleDragEnd"
          draggable="true"
          :data-file-id="file.id"
          :data-file-name="file.filename"
        >
          <div class="list-col name">
            <div class="file-icon">
              <img v-if="file.has_thumbnail && file.thumbnail_path" :src="file.thumbnail_path" class="thumbnail" />
              <span v-else>{{ file.is_folder ? '📁' : getFileIcon(file.filename) }}</span>
            </div>
            <span class="filename">{{ file.filename }}</span>
          </div>
          <div class="list-col size">{{ formatBytes(file.file_size) }}</div>
          <div class="list-col modified">{{ formatDate(file.modified_at) }}</div>
          <div class="list-col views">👁️ {{ file.download_count || 0 }}</div>
          <div class="list-col actions">
            <button @click.stop="showFileInfo(file)" class="btn btn-sm btn-secondary">ℹ️</button>
          </div>
        </div>
      </div>

      <!-- Grid View -->
      <div v-else class="file-grid">
        <div 
          v-for="file in files" 
          :key="file.id"
          class="grid-item file-item"
          :class="{ selected: selectedFiles.has(file.id) }"
          @click="selectFile(file, $event)"
          @dblclick="openFile(file)"
          @contextmenu.prevent="showContextMenu($event, file)"
          @dragstart="handleDragStart(file, $event)"
          @dragend="handleDragEnd"
          draggable="true"
          :data-file-id="file.id"
          :data-file-name="file.filename"
        >
          <div class="grid-icon">
            <img v-if="file.has_thumbnail && file.thumbnail_path" :src="file.thumbnail_path" class="thumbnail" />
            <span v-else class="icon-large">{{ file.is_folder ? '📁' : getFileIcon(file.filename) }}</span>
          </div>
          <div class="grid-name">{{ file.filename }}</div>
          <div class="grid-size">{{ formatBytes(file.file_size) }}</div>
        </div>
      </div>
    </div>

    <!-- File Viewer Modal -->
    <div v-if="showFileViewer" class="file-viewer-overlay" @click="closeFileViewer">
      <div class="file-viewer-modal" @click.stop>
        <div class="file-viewer-header">
          <h3>{{ viewerFile?.filename }}</h3>
          <div class="viewer-controls">
            <button @click="downloadFile(viewerFile)" class="btn btn-sm btn-primary">⬇️ Download</button>
            <button @click="closeFileViewer" class="btn btn-sm btn-secondary">✕ Close</button>
          </div>
        </div>
        <div class="file-viewer-content">
          <!-- Image Viewer -->
          <div v-if="viewerFile?.mime_type?.startsWith('image/')" class="image-viewer">
            <div class="image-controls">
              <button @click="zoomIn" class="zoom-btn">🔍+</button>
              <button @click="zoomOut" class="zoom-btn">🔍-</button>
              <button @click="resetZoom" class="zoom-btn">🔄</button>
              <button @click="fitToScreen" class="zoom-btn">⛶</button>
            </div>
            <div class="image-container" @wheel="handleImageWheel" @mousedown="startPan" @mousemove="pan" @mouseup="endPan" @mouseleave="endPan">
              <img 
                :src="viewerUrl" 
                :alt="viewerFile.filename" 
                :style="imageStyle"
                draggable="false"
              />
            </div>
          </div>
          
          <!-- PDF Viewer -->
          <div v-else-if="viewerFile?.mime_type === 'application/pdf'" class="pdf-viewer">
            <iframe :src="viewerUrl" width="100%" height="100%"></iframe>
          </div>
          
          <!-- Text Viewer -->
          <div v-else-if="isTextFile(viewerFile)" class="text-viewer">
            <pre>{{ textContent }}</pre>
          </div>
          
          <!-- Unsupported File Type -->
          <div v-else class="unsupported-viewer">
            <div class="unsupported-icon">📄</div>
            <h4>Preview not available</h4>
            <p>This file type cannot be previewed in the browser.</p>
            <button @click="downloadFile(viewerFile)" class="btn btn-primary">Download to view</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Context Menu -->
    <div 
      v-if="contextMenu.show" 
      class="context-menu"
      :style="{ 
        left: contextMenu.x + 'px', 
        top: contextMenu.y + 'px',
        position: 'fixed'
      }"
      @click.stop
      @mouseenter="keepSideMenuOpen"
      @mouseleave="scheduleSideMenuClose"
    >
      <!-- Debug info -->
      <div style="background: #007bff; color: white; padding: 5px; font-size: 12px;">
        DEBUG: User Role = {{ user.role }} | File = {{ contextMenu.file?.filename || 'null' }}
      </div>
      
      <div v-if="contextMenu.file" class="menu-section">
        <!-- File/Folder Operations -->
        <div @click="openFile(contextMenu.file)" class="menu-item">
          {{ contextMenu.file.is_folder ? '📂 Open Folder' : '� Open File' }}
        </div>
        <div v-if="!contextMenu.file.is_folder" @click="viewFileInBrowser(contextMenu.file)" class="menu-item">👁️ View in Browser</div>
        <div v-if="!contextMenu.file.is_folder" @click="downloadFile(contextMenu.file)" class="menu-item">⬇️ Download</div>
        <div class="menu-divider"></div>
        
        <!-- Basic Operations -->
        <div @click="copyItem(contextMenu.file)" class="menu-item">📋 Copy</div>
        <div @click="cutItem(contextMenu.file)" class="menu-item">✂️ Cut</div>
        <div @click="pasteItem" v-if="clipboard.item" class="menu-item">📋 Paste ({{ clipboard.action }})</div>
        
        <div class="menu-divider"></div>
        
        <!-- Advanced Options (opens side panel on hover) -->
        <div 
          @mouseenter="openSidePanel(contextMenu.file)" 
          @mouseleave="scheduleSideMenuClose"
          class="menu-item"
        >⚙️ More Options</div>
        
        <div class="menu-divider"></div>
        
        <!-- Delete Operations -->
        <div @click="deleteItem(contextMenu.file)" class="menu-item danger">🗑️ Delete</div>
        <div v-if="contextMenu.file.is_folder" @click="clearFolder(contextMenu.file)" class="menu-item danger">🗑️ Delete All Files in Folder</div>
      </div>
      
      <div v-else class="menu-section">
        <div @click="showUploadModal = true" class="menu-item">📤 Upload Files</div>
        <div @click="showFolderModal = true" class="menu-item">📁 New Folder</div>
        <div @click="pasteItem" v-if="clipboard.item" class="menu-item">📋 Paste ({{ clipboard.action }})</div>
        <div class="menu-divider"></div>
        <div @click="refreshFiles" class="menu-item">� Refresh</div>
      </div>
    </div>

    <!-- Side Context Menu -->
    <div 
      v-if="showSideContextMenu" 
      class="side-context-menu"
      :style="{ 
        left: sideContextMenu.x + 'px', 
        top: sideContextMenu.y + 'px',
        position: 'fixed'
      }"
      @click.stop
      @mouseenter="keepSideMenuOpen"
      @mouseleave="closeSideContextMenu"
    >
      <div class="side-menu-section">
        <h4>🔗 Share & Access</h4>
        <div @click="copyLink(sideContextMenu.file)" class="side-menu-item">🔗 Copy Link</div>
        <div @click="openAccessModal(sideContextMenu.file)" class="side-menu-item">👥 Manage Access</div>
      </div>

      <div class="side-menu-section">
        <h4>📁 Move & Organize</h4>
        <div @click="showMoveDialog(sideContextMenu.file)" class="side-menu-item">📁 Move to...</div>
        <div v-if="user.role === 'OP'" @click="moveToVault(sideContextMenu.file)" class="side-menu-item">🔐 Move to Vault</div>
      </div>

      <div class="side-menu-section">
        <h4>💬 Communication</h4>
        <div @click="sendToChat(sideContextMenu.file)" class="side-menu-item" disabled>💬 Send to Chat (Coming Soon)</div>
      </div>

      <div class="side-menu-section">
        <h4>ℹ️ File Information</h4>
        <div @click="showFileInfo(sideContextMenu.file)" class="side-menu-item">ℹ️ Info</div>
      </div>
    </div>

    <!-- Move Dialog -->
    <div v-if="showMoveModal" class="modal-overlay" @click="showMoveModal = false">
      <div class="modal" @click.stop>
        <h3>📁 Move "{{ moveFile?.filename }}"</h3>
        <div class="folder-tree">
          <div 
            v-for="folder in availableFolders" 
            :key="folder.id"
            class="folder-option"
            :class="{ selected: selectedMoveFolder === folder.id }"
            @click="selectedMoveFolder = folder.id"
          >
            📁 {{ folder.filename }}
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showMoveModal = false" class="btn btn-secondary">Cancel</button>
          <button @click="confirmMove" class="btn btn-primary">Move</button>
        </div>
      </div>
    </div>

    <!-- Manage Access Modal -->
    <div v-if="showAccessModal" class="modal-overlay" @click="showAccessModal = false">
      <div class="modal access-modal" @click.stop>
        <h3>👥 Manage Access - {{ accessFile?.filename }}</h3>
        
        <div class="access-section">
          <h4>🔗 Share Link</h4>
          <div class="share-link-section">
            <input 
              v-if="shareLink" 
              :value="shareLink" 
              readonly 
              class="form-input" 
            />
            <div class="share-actions">
              <button @click="generateShareLink" class="btn btn-primary">Generate Link</button>
              <button v-if="shareLink" @click="copyShareLink" class="btn btn-secondary">Copy Link</button>
            </div>
          </div>
        </div>

        <div class="access-section">
          <h4>🔐 Who can access</h4>
          <div class="access-options">
            <label class="access-option">
              <input 
                type="radio" 
                v-model="shareSettings.access_level" 
                value="only_me" 
                @change="updateAccess"
              />
              <div class="access-option-content">
                <div class="access-option-title">🔒 Only me</div>
                <div class="access-option-desc">Only you can access this file</div>
              </div>
            </label>
            
            <label class="access-option">
              <input 
                type="radio" 
                v-model="shareSettings.access_level" 
                value="internal" 
                @change="updateAccess"
              />
              <div class="access-option-content">
                <div class="access-option-title">👥 Internal users</div>
                <div class="access-option-desc">Anyone with an account can access</div>
              </div>
            </label>
            
            <label class="access-option">
              <input 
                type="radio" 
                v-model="shareSettings.access_level" 
                value="public" 
                @change="updateAccess"
              />
              <div class="access-option-content">
                <div class="access-option-title">🌐 Anyone with the link</div>
                <div class="access-option-desc">Anyone can access with the share link</div>
              </div>
            </label>
          </div>
        </div>

        <div v-if="shareSettings.access_level !== 'only_me'" class="access-section">
          <h4>🔑 Password Protection (Optional)</h4>
          <input 
            v-model="shareSettings.password" 
            placeholder="Enter password to protect access" 
            class="form-input"
            @blur="updateAccess"
          />
          <small class="form-help">Leave empty for no password protection</small>
        </div>

        <div v-if="shareSettings.access_level === 'internal'" class="access-section">
          <h4>👤 Specific Users (Optional)</h4>
          <div class="user-access">
            <div class="add-user">
              <input 
                v-model="newUserEmail" 
                placeholder="Enter username or email" 
                class="form-input"
                @keyup.enter="addUserAccess"
              />
              <button @click="addUserAccess" class="btn btn-primary">Add User</button>
            </div>
            <div v-if="accessFile?.allowed_users && accessFile.allowed_users.length > 0" class="user-list">
              <div class="user-list-header">
                <strong>Users with access:</strong>
              </div>
              <div 
                v-for="user in accessFile.allowed_users" 
                :key="user.id"
                class="user-item"
              >
                <div class="user-info">
                  <span class="user-avatar">👤</span>
                  <span class="user-name">{{ user.display_name || user.username }}</span>
                  <span class="user-email">{{ user.username }}</span>
                </div>
                <button @click="removeUserAccess(user.id)" class="btn btn-sm btn-danger">Remove</button>
              </div>
            </div>
            <div v-else class="no-users">
              <small>No specific users added. All internal users can access.</small>
            </div>
          </div>
        </div>

        <div class="access-section">
          <h4>📊 Link Settings</h4>
          <div class="link-settings">
            <label class="checkbox-option">
              <input 
                type="checkbox" 
                v-model="shareSettings.disable_download"
                @change="updateAccess"
              />
              <span>Disable download</span>
            </label>
            <label class="checkbox-option">
              <input 
                type="checkbox" 
                v-model="shareSettings.require_signin"
                @change="updateAccess"
              />
              <span>Require sign-in to view</span>
            </label>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="showAccessModal = false" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- File Info Modal -->
    <div v-if="showInfoModal" class="modal-overlay" @click="showInfoModal = false">
      <div class="modal" @click.stop>
        <h3>📄 File Information</h3>
        <div v-if="selectedInfoFile" class="file-info">
          <div class="info-row">
            <label>Name:</label>
            <span>{{ selectedInfoFile.filename }}</span>
          </div>
          <div class="info-row">
            <label>Type:</label>
            <span>{{ selectedInfoFile.mime_type || 'Folder' }}</span>
          </div>
          <div class="info-row">
            <label>Size:</label>
            <span>{{ formatBytes(selectedInfoFile.file_size) }}</span>
          </div>
          <div class="info-row">
            <label>Created:</label>
            <span>{{ formatDate(selectedInfoFile.created_at) }}</span>
          </div>
          <div class="info-row">
            <label>Modified:</label>
            <span>{{ formatDate(selectedInfoFile.modified_at) }}</span>
          </div>
          <div class="info-row">
            <label>Downloads:</label>
            <span>{{ selectedInfoFile.download_count }}</span>
          </div>
          <div v-if="selectedInfoFile.public_share_link" class="info-row">
            <label>Share Link:</label>
            <input :value="selectedInfoFile.public_share_link" readonly class="share-link-input" />
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showInfoModal = false" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click="showUploadModal = false">
      <div class="modal" @click.stop>
        <h3>📤 Upload to {{ currentFolderName }}</h3>
        <div class="upload-area" @dragover.prevent @drop.prevent="handleModalDrop">
          <input type="file" multiple @change="handleFileUpload" ref="fileInput" />
          <div class="upload-text">
            Drag & drop files here or click to select
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showUploadModal = false" class="btn btn-secondary">Cancel</button>
          <button @click="uploadFiles" class="btn btn-primary">Upload</button>
        </div>
      </div>
    </div>

    <!-- Folder Modal -->
    <div v-if="showFolderModal" class="modal-overlay" @click="showFolderModal = false">
      <div class="modal" @click.stop>
        <h3>📁 Create Folder in {{ currentFolderName }}</h3>
        <input v-model="folderName" placeholder="Folder name" class="form-input" />
        <div class="modal-actions">
          <button @click="showFolderModal = false" class="btn btn-secondary">Cancel</button>
          <button @click="createFolder" class="btn btn-primary">Create</button>
        </div>
      </div>
    </div>

    <!-- Share Modal (reusing from previous) -->
    <div v-if="showShareModal" class="modal-overlay" @click="showShareModal = false">
      <div class="modal" @click.stop>
        <h3>🔗 Share File</h3>
        <div class="share-options">
          <label>
            <input type="radio" v-model="shareSettings.access_level" value="only_me" />
            Only me
          </label>
          <label>
            <input type="radio" v-model="shareSettings.access_level" value="internal" />
            Anyone with the link (internal)
          </label>
          <label>
            <input type="radio" v-model="shareSettings.access_level" value="public" />
            Anyone with the link (public)
          </label>
        </div>
        <input 
          v-if="shareSettings.access_level !== 'only_me'"
          v-model="shareSettings.password" 
          placeholder="Optional password" 
          class="form-input"
        />
        <div v-if="shareLink" class="share-link">
          <input :value="shareLink" readonly class="form-input" />
          <button @click="copyShareLink" class="btn btn-sm btn-primary">Copy</button>
        </div>
        <div class="modal-actions">
          <button @click="showShareModal = false" class="btn btn-secondary">Close</button>
          <button @click="generateShareLink" class="btn btn-primary">Share</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { apiGet, apiPost, apiDelete, apiPostForm, handleAuthError } from '../../utils/api.js'

export default {
  name: 'EnhancedDrive',
  setup() {
    // State
    const files = ref([])
    const quota = ref({
      used_space: 0,
      total_quota: 30 * 1024 * 1024 * 1024,
      additional_quota: 0
    })
    const currentPath = ref('/')
    const viewMode = ref('list')
    const selectedFiles = ref(new Set())
    const isDragging = ref(false)
    const dragCounter = ref(0)
    
    // Modal states
    const showUploadModal = ref(false)
    const showFolderModal = ref(false)
    const showShareModal = ref(false)
    const showInfoModal = ref(false)
    const showMoveModal = ref(false)
    const showAccessModal = ref(false)
    const showFileViewer = ref(false)
    const showSideContextMenu = ref(false)
    
    // File viewer state
    const viewerFile = ref(null)
    const viewerUrl = ref('')
    const textContent = ref('')
    
    // Image viewer state
    const imageZoom = ref(1)
    const imagePanX = ref(0)
    const imagePanY = ref(0)
    const isPanning = ref(false)
    const lastMouseX = ref(0)
    const lastMouseY = ref(0)
    
    // Side context menu state
    const sideContextMenu = ref({ show: false, x: 0, y: 0, file: null })
    const sideMenuHoverTimer = ref(null)
    
    // Form data
    const folderName = ref('')
    const shareLink = ref('')
    const shareSettings = ref({
      access_level: 'only_me',
      password: '',
      disable_download: false,
      require_signin: false
    })
    const selectedInfoFile = ref(null)
    const fileInput = ref(null)
    
    // Move dialog state
    const moveFile = ref(null)
    const selectedMoveFolder = ref(null)
    const availableFolders = ref([])
    
    // Access management state
    const accessFile = ref(null)
    const newUserEmail = ref('')
    
    // User state (get from localStorage)
    const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
    
    // Debug: Log user data to console
    console.log('User data:', user.value)
    
    // Context menu
    const contextMenu = ref({
      show: false,
      x: 0,
      y: 0,
      file: null
    })
    
    // Clipboard for copy/paste
    const clipboard = ref({
      item: null,
      action: null // 'copy' or 'cut'
    })

    // Computed
    const quotaPercentage = computed(() => {
      if (!quota.value.total_quota && !quota.value.additional_quota) return 0
      const total = quota.value.total_quota + quota.value.additional_quota
      return (quota.value.used_space / total) * 100
    })

    const currentFolderName = computed(() => {
      if (currentPath.value === '/') return 'Home'
      return currentPath.value.split('/').filter(Boolean).pop() || 'Home'
    })

    const breadcrumbs = computed(() => {
      if (currentPath.value === '/') return []
      const parts = currentPath.value.split('/').filter(Boolean)
      const crumbs = []
      let path = '/'
      
      for (const part of parts) {
        path += part + '/'
        crumbs.push({ name: part, path })
      }
      
      return crumbs
    })

    // Methods
    const loadFiles = async () => {
      try {
        const data = await apiGet(`/drive/files?folder_path=${encodeURIComponent(currentPath.value)}`)
        files.value = data.files || []
        if (data.quota) {
          quota.value = data.quota
        }
      } catch (error) {
        console.error('Failed to load files:', error)
        files.value = []
      }
    }

    const navigateToFolder = (path) => {
      console.log('DEBUG: Navigating to folder:', path)
      currentPath.value = path
      selectedFiles.value.clear()
      closeSideContextMenu() // Close side menu when navigating
      hideContextMenu() // Also close main context menu
      loadFiles()
    }

    const openFile = (file) => {
      hideContextMenu()
      if (file.is_folder) {
        navigateToFolder(file.folder_path + file.filename + '/')
      } else {
        viewFileInBrowser(file)
      }
    }

    const selectFile = (file, event) => {
      if (event.ctrlKey || event.metaKey) {
        // Multi-select
        if (selectedFiles.value.has(file.id)) {
          selectedFiles.value.delete(file.id)
        } else {
          selectedFiles.value.add(file.id)
        }
      } else {
        // Single select
        selectedFiles.value.clear()
        selectedFiles.value.add(file.id)
      }
    }

    const showContextMenu = (event, file) => {
      event.preventDefault()
      event.stopPropagation()
      
      console.log('Showing context menu for:', file?.filename || 'null')
      console.log('User role:', user.value.role)
      console.log('Event target:', event.target)
      
      // Get viewport-relative position
      const x = event.clientX
      const y = event.clientY
      
      // Calculate menu dimensions (estimated)
      const menuWidth = 200
      const menuItemHeight = 40
      const dividerHeight = 10
      
      // Calculate menu height based on content
      let menuHeight = 40 // Debug bar
      
      if (file) {
        menuHeight += menuItemHeight // Open
        if (!file.is_folder) {
          menuHeight += menuItemHeight * 2 // View + Download
        }
        menuHeight += menuItemHeight * 3 // Copy, Cut, Paste
        menuHeight += dividerHeight
        menuHeight += menuItemHeight // More Options
        menuHeight += dividerHeight
        menuHeight += menuItemHeight // Delete
        if (file.is_folder) {
          menuHeight += menuItemHeight // Delete All Files
        }
      } else {
        menuHeight += menuItemHeight * 4 // Upload, Folder, Paste, Refresh
        menuHeight += dividerHeight
      }
      
      // Smart positioning - ensure menu stays within viewport
      let adjustedX = x
      let adjustedY = y
      
      // Adjust horizontal position
      if (x + menuWidth > window.innerWidth) {
        adjustedX = window.innerWidth - menuWidth - 10
      }
      
      // Adjust vertical position
      if (y + menuHeight > window.innerHeight) {
        adjustedY = window.innerHeight - menuHeight - 10
      }
      
      // Ensure menu doesn't go off-screen on the left or top
      adjustedX = Math.max(10, adjustedX)
      adjustedY = Math.max(10, adjustedY)
      
      contextMenu.value = {
        show: true,
        x: adjustedX,
        y: adjustedY,
        file
      }
    }

    const hideContextMenu = () => {
      contextMenu.value.show = false
    }

    const openSidePanel = (file) => {
      // Position side menu relative to the main context menu
      sideContextMenu.value = {
        show: true,
        x: contextMenu.value.x + 200, // 200px to the right of main menu
        y: contextMenu.value.y,      // Same vertical position as main menu
        file
      }
      showSideContextMenu.value = true
      // Don't hide main context menu - keep it persistent
    }

    const closeSideContextMenu = () => {
      showSideContextMenu.value = false
      sideContextMenu.value = { show: false, x: 0, y: 0, file: null }
      if (sideMenuHoverTimer.value) {
        clearTimeout(sideMenuHoverTimer.value)
        sideMenuHoverTimer.value = null
      }
    }

    const keepSideMenuOpen = () => {
      // Clear any pending close timer when hovering over side menu
      if (sideMenuHoverTimer.value) {
        clearTimeout(sideMenuHoverTimer.value)
        sideMenuHoverTimer.value = null
      }
    }

    const scheduleSideMenuClose = () => {
      // Schedule close after a short delay to allow moving between menus
      if (sideMenuHoverTimer.value) {
        clearTimeout(sideMenuHoverTimer.value)
      }
      sideMenuHoverTimer.value = setTimeout(() => {
        closeSideContextMenu()
      }, 200) // 200ms delay
    }

    const openAccessModal = (file) => {
      accessFile.value = file
      showAccessModal.value = true
      closeSideContextMenu()
    }

    const copyItem = (file) => {
      clipboard.value = { item: file, action: 'copy' }
      hideContextMenu()
      closeSideContextMenu()
    }

    const cutItem = (file) => {
      clipboard.value = { item: file, action: 'cut' }
      hideContextMenu()
      closeSideContextMenu()
    }

    const pasteItem = async () => {
      if (!clipboard.value.item) return

      try {
        const endpoint = clipboard.value.action === 'copy' ? '/drive/copy' : '/drive/move'
        
        await apiPost(endpoint, {
          file_id: clipboard.value.item.id,
          target_path: currentPath.value
        })

        loadFiles()
        clipboard.value = { item: null, action: null }
        hideContextMenu()
        closeSideContextMenu()
      } catch (error) {
        console.error('Paste failed:', error)
        alert('Paste failed: ' + error.message)
      }
    }

    const deleteItem = async (file) => {
      if (!confirm(`Are you sure you want to delete "${file.filename}"?`)) return

      try {
        await apiDelete(`/drive/file/${file.id}`)
        
        loadFiles()
        hideContextMenu()
        closeSideContextMenu()
      } catch (error) {
        console.error('Delete failed:', error)
        alert('Delete failed: ' + error.message)
      }
    }

    const showFileInfo = (file) => {
      selectedInfoFile.value = file
      showInfoModal.value = true
      hideContextMenu()
      closeSideContextMenu()
    }

    const shareFile = (file) => {
      accessFile.value = file
      shareSettings.value = {
        access_level: file.access_level || 'only_me',
        password: file.share_password || ''
      }
      shareLink.value = file.public_share_link || ''
      showAccessModal.value = true
      hideContextMenu()
    }

    const copyLink = (file) => {
      if (file.public_share_link) {
        navigator.clipboard.writeText(file.public_share_link)
        alert('Share link copied to clipboard!')
      } else {
        alert('No share link available. Please generate one first.')
      }
      hideContextMenu()
    }

    const showMoveDialog = (file) => {
      moveFile.value = file
      selectedMoveFolder.value = null
      loadAvailableFolders()
      showMoveModal.value = true
      hideContextMenu()
    }

    const loadAvailableFolders = async () => {
      try {
        const data = await apiGet('/drive/folders/all')
        availableFolders.value = data.folders || []
      } catch (error) {
        console.error('Failed to load folders:', error)
      }
    }

    const confirmMove = async () => {
      if (!moveFile.value || !selectedMoveFolder.value) return

      try {
        await apiPost('/drive/move', {
          file_id: moveFile.value.id,
          target_folder: selectedMoveFolder.value
        })

        showMoveModal.value = false
        loadFiles()
      } catch (error) {
        console.error('Move failed:', error)
        alert('Move failed: ' + error.message)
      }
    }

    const clearFolder = async (file) => {
      if (!file.is_folder) return
      
      if (!confirm(`Are you sure you want to delete ALL files in "${file.filename}"? This cannot be undone.`)) return

      try {
        await apiDelete(`/drive/folder/${file.id}/contents`)
        
        loadFiles()
        hideContextMenu()
      } catch (error) {
        console.error('Clear folder failed:', error)
        alert('Clear folder failed: ' + error.message)
      }
    }

    const refreshFiles = () => {
      loadFiles()
      hideContextMenu()
    }

    const moveToVault = (file) => {
      alert('Move to Vault feature coming soon!')
      hideContextMenu()
    }

    const sendToChat = (file) => {
      alert('Send to Chat feature coming soon!')
      hideContextMenu()
    }

    const updateAccess = async () => {
      if (!accessFile.value) return

      try {
        await apiPost('/drive/update-access', {
          file_id: accessFile.value.id,
          access_level: shareSettings.value.access_level,
          password: shareSettings.value.password
        })
        loadFiles()
      } catch (error) {
        console.error('Update access failed:', error)
      }
    }

    const addUserAccess = async () => {
      if (!newUserEmail.value.trim() || !accessFile.value) return

      try {
        await apiPost('/drive/add-user-access', {
          file_id: accessFile.value.id,
          username: newUserEmail.value.trim()
        })
        
        newUserEmail.value = ''
        loadFiles()
        // Update accessFile to show new user
        const updatedFile = files.value.find(f => f.id === accessFile.value.id)
        if (updatedFile) {
          accessFile.value = updatedFile
        }
      } catch (error) {
        console.error('Add user failed:', error)
        alert('Add user failed: ' + error.message)
      }
    }

    const removeUserAccess = async (userId) => {
      if (!accessFile.value) return

      try {
        await apiPost('/drive/remove-user-access', {
          file_id: accessFile.value.id,
          user_id: userId
        })
        
        loadFiles()
        // Update accessFile to reflect removal
        const updatedFile = files.value.find(f => f.id === accessFile.value.id)
        if (updatedFile) {
          accessFile.value = updatedFile
        }
      } catch (error) {
        console.error('Remove user failed:', error)
        alert('Remove user failed: ' + error.message)
      }
    }

    // Drag and drop handlers
    const handleDragEnter = (e) => {
      e.preventDefault()
      e.stopPropagation()
      dragCounter.value++
      if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
        isDragging.value = true
      }
    }

    const handleDragLeave = (e) => {
      e.preventDefault()
      e.stopPropagation()
      dragCounter.value--
      if (dragCounter.value === 0) {
        isDragging.value = false
      }
    }

    const handleDragOver = (e) => {
      e.preventDefault()
      e.stopPropagation()
    }

    const handleDrop = (e) => {
      e.preventDefault()
      e.stopPropagation()
      isDragging.value = false
      dragCounter.value = 0

      const files = e.dataTransfer.files
      if (files && files.length > 0) {
        handleMultipleFiles(files)
      }
    }

    const handleDragStart = (file, e) => {
      e.dataTransfer.effectAllowed = 'move'
      e.dataTransfer.setData('text/plain', file.id)
    }

    const handleDragEnd = () => {
      // Clean up drag state
    }

    const handleModalDrop = (e) => {
      const files = e.dataTransfer.files
      if (files && files.length > 0) {
        fileInput.value.files = files
      }
    }

    const handleFileUpload = (event) => {
      // Files selected
    }

    const handleMultipleFiles = async (files) => {
      for (let i = 0; i < files.length; i++) {
        await uploadSingleFile(files[i])
      }
    }

    const uploadSingleFile = async (file) => {
      try {
        console.log('DEBUG: Uploading file to path:', currentPath.value)
        
        // Check for duplicate filenames in current folder
        const existingFile = files.value.find(f => 
          f.filename === file.name && 
          f.folder_path === currentPath.value &&
          !f.is_folder
        )
        
        if (existingFile) {
          alert(`A file named "${file.name}" already exists in this folder. Please rename the file and try again.`)
          return
        }

        const formData = new FormData()
        formData.append('file', file)
        formData.append('folder_path', currentPath.value)

        console.log('DEBUG: Form data folder_path:', currentPath.value)

        await apiPostForm('/drive/upload', formData)
        
        loadFiles() // Refresh file list
      } catch (error) {
        console.error('Upload failed:', error)
        alert('Upload failed: ' + error.message)
      }
    }

    const uploadFiles = async () => {
      const files = fileInput.value.files
      if (!files || files.length === 0) return

      for (let i = 0; i < files.length; i++) {
        await uploadSingleFile(files[i])
      }
      
      showUploadModal.value = false
      loadFiles()
    }

    const createFolder = async () => {
      if (!folderName.value.trim()) return

      try {
        await apiPost('/drive/folder', {
          name: folderName.value.trim(),
          parent_folder: currentPath.value === '/' ? null : currentPath.value
        })
        
        showFolderModal.value = false
        folderName.value = ''
        loadFiles()
      } catch (error) {
        console.error('Create folder failed:', error)
      }
    }

    const downloadFile = async (file) => {
      try {
        const token = localStorage.getItem('token')
        const response = await fetch(`/api/drive/download/${file.id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!response.ok) {
          if (response.status === 401) handleAuthError()
          throw new Error('Download failed')
        }
        
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = file.filename
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Download failed:', error)
        alert('Download failed: ' + error.message)
      }
    }

    const viewFileInBrowser = async (file) => {
      hideContextMenu()
      closeSideContextMenu()
      try {
        viewerFile.value = file
        showFileViewer.value = true
        
        const token = localStorage.getItem('token')
        const response = await fetch(`/api/drive/download/${file.id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!response.ok) {
          if (response.status === 401) handleAuthError()
          throw new Error('Failed to load file')
        }
        
        const blob = await response.blob()
        viewerUrl.value = URL.createObjectURL(blob)
        
        // For text files, read the content
        if (isTextFile(file)) {
          const text = await blob.text()
          textContent.value = text
        }
        
      } catch (error) {
        console.error('View file failed:', error)
        alert('Failed to view file: ' + error.message)
        closeFileViewer()
      }
    }

    const closeFileViewer = () => {
      showFileViewer.value = false
      viewerFile.value = null
      if (viewerUrl.value) {
        URL.revokeObjectURL(viewerUrl.value)
        viewerUrl.value = ''
      }
      textContent.value = ''
      // Reset image viewer state
      imageZoom.value = 1
      imagePanX.value = 0
      imagePanY.value = 0
    }

    // Image viewer functions
    const imageStyle = computed(() => ({
      transform: `scale(${imageZoom.value}) translate(${imagePanX.value}px, ${imagePanY.value}px)`,
      transformOrigin: 'center',
      transition: isPanning.value ? 'none' : 'transform 0.2s ease',
      cursor: isPanning.value ? 'grabbing' : 'grab'
    }))

    const zoomIn = () => {
      imageZoom.value = Math.min(imageZoom.value * 1.2, 5)
    }

    const zoomOut = () => {
      imageZoom.value = Math.max(imageZoom.value / 1.2, 0.1)
    }

    const resetZoom = () => {
      imageZoom.value = 1
      imagePanX.value = 0
      imagePanY.value = 0
    }

    const fitToScreen = () => {
      imageZoom.value = 1
      imagePanX.value = 0
      imagePanY.value = 0
    }

    const handleImageWheel = (event) => {
      event.preventDefault()
      const delta = event.deltaY > 0 ? 0.9 : 1.1
      imageZoom.value = Math.min(Math.max(imageZoom.value * delta, 0.1), 5)
    }

    const startPan = (event) => {
      isPanning.value = true
      lastMouseX.value = event.clientX
      lastMouseY.value = event.clientY
    }

    const pan = (event) => {
      if (!isPanning.value) return
      const deltaX = event.clientX - lastMouseX.value
      const deltaY = event.clientY - lastMouseY.value
      imagePanX.value += deltaX / imageZoom.value
      imagePanY.value += deltaY / imageZoom.value
      lastMouseX.value = event.clientX
      lastMouseY.value = event.clientY
    }

    const endPan = () => {
      isPanning.value = false
    }

    const isTextFile = (file) => {
      const textMimeTypes = [
        'text/plain',
        'text/html',
        'text/css',
        'text/javascript',
        'application/json',
        'application/xml',
        'text/xml',
        'text/markdown'
      ]
      
      const textExtensions = ['.txt', '.md', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.cpp', '.c', '.h']
      
      return textMimeTypes.includes(file.mime_type) || 
             textExtensions.some(ext => file.filename.toLowerCase().endsWith(ext))
    }

    const generateShareLink = async () => {
      // Share link generation logic
    }

    const copyShareLink = () => {
      navigator.clipboard.writeText(shareLink.value)
    }

    const getFileIcon = (filename) => {
      const ext = filename.split('.').pop().toLowerCase()
      const icons = {
        pdf: '📄',
        doc: '📝', docx: '📝',
        xls: '📊', xlsx: '📊',
        ppt: '📈', pptx: '📈',
        jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🖼️',
        mp4: '🎬', avi: '🎬', mov: '🎬',
        mp3: '🎵', wav: '🎵',
        zip: '📦', rar: '📦',
        txt: '📄',
        js: '📜', html: '🌐', css: '🎨'
      }
      return icons[ext] || '📄'
    }

    const formatBytes = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    // Hide context menu when clicking outside
    const handleGlobalClick = (event) => {
      if (contextMenu.value.show && !event.target.closest('.context-menu') && !event.target.closest('.file-item')) {
        hideContextMenu()
        closeSideContextMenu() // Also close side menu when main menu closes
      }
      if (showSideContextMenu.value && !event.target.closest('.side-context-menu') && !event.target.closest('.context-menu') && !event.target.closest('.file-item')) {
        closeSideContextMenu()
      }
    }

    // Check if side context menu is out of viewport and close it
    const checkSideMenuViewport = () => {
      if (showSideContextMenu.value && sideContextMenu.value.file) {
        const fileElement = document.querySelector(`[data-file-id="${sideContextMenu.value.file.id}"]`)
        if (fileElement) {
          const rect = fileElement.getBoundingClientRect()
          // If file is not visible in viewport, close the side menu
          if (rect.bottom < 0 || rect.top > window.innerHeight) {
            closeSideContextMenu()
          }
        }
      }
    }

    // Don't hide context menu on scroll - keep it sticky
    // const handleScroll = () => {
    //   if (contextMenu.value.show) {
    //     hideContextMenu()
    //   }
    // }

    onMounted(() => {
      loadFiles()
      document.addEventListener('click', handleGlobalClick)
      window.addEventListener('scroll', checkSideMenuViewport)
      // window.addEventListener('scroll', handleScroll) // Removed for sticky positioning
      
      // Add touch support for mobile
      let touchTimer
      const handleTouchStart = (e) => {
        const fileItem = e.target.closest('.file-item')
        if (fileItem) {
          touchTimer = setTimeout(() => {
            const fileId = fileItem.dataset.fileId
            const file = files.value.find(f => f.id === fileId)
            if (file) {
              const touch = e.touches[0]
              showContextMenu({
                clientX: touch.clientX,
                clientY: touch.clientY,
                preventDefault: () => {},
                stopPropagation: () => {}
              }, file)
            }
          }, 500) // 500ms long press
        }
      }
      
      const handleTouchEnd = () => {
        if (touchTimer) {
          clearTimeout(touchTimer)
          touchTimer = null
        }
      }
      
      document.addEventListener('touchstart', handleTouchStart, { passive: false })
      document.addEventListener('touchend', handleTouchEnd)
      document.addEventListener('touchmove', handleTouchEnd)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleGlobalClick)
      window.removeEventListener('scroll', checkSideMenuViewport)
      // window.removeEventListener('scroll', handleScroll) // Removed for sticky positioning
    })

    return {
      files,
      quota,
      quotaPercentage,
      currentPath,
      currentFolderName,
      breadcrumbs,
      viewMode,
      selectedFiles,
      isDragging,
      showUploadModal,
      showFolderModal,
      showShareModal,
      showInfoModal,
      showMoveModal,
      showAccessModal,
      showFileViewer,
      showSideContextMenu,
      folderName,
      shareLink,
      shareSettings,
      selectedInfoFile,
      fileInput,
      contextMenu,
      clipboard,
      moveFile,
      selectedMoveFolder,
      availableFolders,
      accessFile,
      newUserEmail,
      user,
      viewerFile,
      viewerUrl,
      textContent,
      imageZoom,
      imagePanX,
      imagePanY,
      isPanning,
      imageStyle,
      sideContextMenu,
      loadFiles,
      navigateToFolder,
      openFile,
      selectFile,
      showContextMenu,
      hideContextMenu,
      copyItem,
      cutItem,
      pasteItem,
      deleteItem,
      showFileInfo,
      shareFile,
      copyLink,
      showMoveDialog,
      loadAvailableFolders,
      confirmMove,
      clearFolder,
      refreshFiles,
      moveToVault,
      sendToChat,
      updateAccess,
      addUserAccess,
      removeUserAccess,
      handleDragEnter,
      handleDragLeave,
      handleDragOver,
      handleDrop,
      handleDragStart,
      handleDragEnd,
      handleModalDrop,
      handleFileUpload,
      handleMultipleFiles,
      uploadSingleFile,
      uploadFiles,
      createFolder,
      downloadFile,
      viewFileInBrowser,
      closeFileViewer,
      isTextFile,
      openSidePanel,
      closeSideContextMenu,
      keepSideMenuOpen,
      scheduleSideMenuClose,
      openAccessModal,
      zoomIn,
      zoomOut,
      resetZoom,
      fitToScreen,
      handleImageWheel,
      startPan,
      pan,
      endPan,
      generateShareLink,
      copyShareLink,
      getFileIcon,
      formatBytes,
      formatDate
    }
  }
}
</script>

<style scoped>
.enhanced-drive {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.drive-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.header-left h2 {
  margin: 0 0 5px 0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
}

.breadcrumb-item {
  cursor: pointer;
  color: #007bff;
}

.breadcrumb-item:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  margin: 0 5px;
  color: #999;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.view-controls {
  display: flex;
  gap: 5px;
}

.view-btn {
  padding: 5px 10px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
}

.view-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.drive-actions {
  display: flex;
  gap: 10px;
}

.quota-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.quota-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.quota-used {
  height: 100%;
  background: #28a745;
  transition: width 0.3s ease;
}

.quota-text {
  font-size: 14px;
  color: #666;
}

.file-area {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
  overflow: auto;
}

.file-area.drag-over {
  border: 2px dashed #007bff;
  background: #f8f9ff;
}

.drag-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 123, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border: 2px dashed #007bff;
  border-radius: 8px;
}

.drag-message {
  background: white;
  padding: 20px 40px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 500;
  color: #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.empty-state {
  padding: 60px 40px;
  text-align: center;
  color: #666;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

/* List View Styles */
.file-list {
  width: 100%;
}

.list-header {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  font-weight: 600;
  padding: 10px;
}

.list-item {
  display: flex;
  border-bottom: 1px solid #eee;
  padding: 10px;
  cursor: pointer;
}

.list-item:hover {
  background: #f8f9fa;
}

.list-item.selected {
  background: #e3f2fd;
}

.list-col {
  display: flex;
  align-items: center;
  padding: 0 10px;
}

.list-col.name {
  flex: 1;
}

.list-col.size {
  width: 100px;
}

.list-col.modified {
  width: 150px;
}

.list-col.views {
  flex: 0 0 80px;
  text-align: center;
  color: #666;
  font-size: 12px;
}

.list-col.actions {
  width: 80px;
}

.file-icon {
  display: flex;
  align-items: center;
  margin-right: 10px;
}

.thumbnail {
  width: 24px;
  height: 24px;
  object-fit: cover;
  border-radius: 2px;
}

/* Grid View Styles */
.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
  padding: 20px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
}

.grid-item:hover {
  background: #f8f9fa;
}

.grid-item.selected {
  background: #e3f2fd;
  border-color: #007bff;
}

.grid-icon {
  margin-bottom: 8px;
}

.icon-large {
  font-size: 32px;
}

.grid-name {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 4px;
  word-break: break-word;
}

.grid-size {
  font-size: 10px;
  color: #666;
}

/* Context Menu */
.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 1000;
  min-width: 150px;
}

.menu-section {
  padding: 5px 0;
}

.menu-item {
  padding: 8px 15px;
  cursor: pointer;
  font-size: 14px;
}

.menu-item:hover {
  background: #f8f9fa;
}

.menu-item.danger {
  color: #dc3545;
}

.menu-divider {
  height: 1px;
  background: #eee;
  margin: 5px 0;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 20px;
  border-radius: 8px;
  min-width: 400px;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  margin-bottom: 20px;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #007bff;
}

.upload-text {
  color: #666;
  margin-bottom: 10px;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 15px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

/* File Info Styles */
.file-info {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  margin-bottom: 10px;
}

.info-row label {
  font-weight: 600;
  width: 100px;
  flex-shrink: 0;
}

.share-link-input {
  flex: 1;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

/* Access Modal Styles */
.access-modal {
  min-width: 600px;
  max-width: 700px;
}

.access-section {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.access-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.access-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.share-link-section {
  margin-bottom: 15px;
}

.share-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.access-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.access-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.access-option:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.access-option input[type="radio"] {
  margin: 4px 0 0 0;
  accent-color: #007bff;
}

.access-option-content {
  flex: 1;
}

.access-option-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.access-option-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

.form-help {
  display: block;
  margin-top: 5px;
  color: #666;
  font-size: 12px;
}

.user-list-header {
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.user-avatar {
  font-size: 16px;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.user-email {
  font-size: 12px;
  color: #666;
}

.no-users {
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  text-align: center;
  color: #666;
  font-style: italic;
}

.link-settings {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.checkbox-option:hover {
  background: #f8f9fa;
}

.checkbox-option input[type="checkbox"] {
  accent-color: #007bff;
}

.user-access {
  margin-top: 10px;
}

.add-user {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.add-user .form-input {
  flex: 1;
}

.user-list {
  border: 1px solid #eee;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.user-item:last-child {
  border-bottom: none;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

/* Move Dialog Styles */
.folder-tree {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 20px;
}

.folder-option {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.folder-option:hover {
  background: #f8f9fa;
}

.folder-option.selected {
  background: #007bff;
  color: white;
}

.folder-option:last-child {
  border-bottom: none;
}

/* Side Context Menu Styles */
.side-context-menu {
  position: absolute;
  min-width: 200px;
  max-width: 250px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 10001;
  font-size: 14px;
}

.side-menu-section {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.side-menu-section:last-child {
  border-bottom: none;
}

.side-menu-section h4 {
  margin: 0 0 8px 0;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.side-menu-item {
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.side-menu-item:hover {
  background: #f8f9fa;
}

.side-menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.side-menu-item:disabled:hover {
  background: transparent;
}

/* Side Panel Styles */
.side-panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: flex-end;
  z-index: 10001;
}

.side-panel {
  width: 400px;
  max-width: 90vw;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.side-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
}

.side-panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.side-panel-content {
  padding: 20px;
}

.panel-section {
  margin-bottom: 30px;
}

.panel-section h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.panel-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  text-align: left;
}

.panel-btn:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.panel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.panel-btn:disabled:hover {
  background: white;
  border-color: #ddd;
}

.file-info {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 600;
  color: #666;
  font-size: 13px;
}

.info-value {
  color: #333;
  font-size: 13px;
  text-align: right;
}

/* File Viewer Styles */
.file-viewer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.file-viewer-modal {
  background: white;
  border-radius: 8px;
  width: 90vw;
  height: 90vh;
  max-width: 1200px;
  max-height: 800px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.file-viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
}

.file-viewer-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 400px;
}

.viewer-controls {
  display: flex;
  gap: 10px;
}

.file-viewer-content {
  flex: 1;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.image-viewer img {
  max-width: none;
  max-height: none;
  width: auto;
  height: auto;
  border-radius: 4px;
  user-select: none;
  -webkit-user-drag: none;
}

.image-controls {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  gap: 5px;
  z-index: 10;
}

.zoom-btn {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.2s;
}

.zoom-btn:hover {
  background: rgba(0, 0, 0, 0.9);
}

.image-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.pdf-viewer {
  width: 100%;
  height: 100%;
}

.pdf-viewer iframe {
  border: none;
}

.text-viewer {
  width: 100%;
  height: 100%;
  padding: 20px;
  background: white;
  overflow: auto;
}

.text-viewer pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.unsupported-viewer {
  text-align: center;
  padding: 40px;
  color: #666;
}

.unsupported-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.unsupported-viewer h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.unsupported-viewer p {
  margin: 0 0 20px 0;
  color: #666;
}

/* Enhanced Context Menu */
.context-menu {
  position: fixed;
  min-width: 200px;
  max-width: 250px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 10000;
  font-size: 14px;
}

.menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-item:disabled:hover {
  background: transparent;
}
</style>
