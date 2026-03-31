<template>
  <div class="nautilus-drive">
    <!-- Left Sidebar: Navigation & Actions -->
    <aside class="nautilus-sidebar glass-panel">
      <div class="sidebar-header">
        <div class="sidebar-creation-group" style="display: flex; flex-direction: column; gap: 0.5rem;">
          <button 
            class="btn-secondary create-btn" 
            @click="createFolder" 
            :disabled="currentFilter !== null"
            :style="{ opacity: currentFilter !== null ? '0.5' : '1', cursor: currentFilter !== null ? 'not-allowed' : 'pointer', background: 'rgba(255,255,255,0.05)', color: 'white', border: '1px solid var(--glass-border)' }"
          >
            <i class="fas fa-folder-plus"></i> New Folder
          </button>
          <div class="dropdown-wrapper">
             <button 
               class="btn-primary create-btn vault-primary upload-dropdown-btn" 
               @click="showDropdown.upload = !showDropdown.upload"
               :disabled="currentFilter !== null"
               :style="{ opacity: currentFilter !== null ? '0.5' : '1', cursor: currentFilter !== null ? 'not-allowed' : 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }"
             >
               <span><i class="fas fa-shield-halved"></i> Secure Upload</span>
               <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
             </button>
             
             <div v-if="showDropdown.upload" class="dropdown-menu glass-panel">
                <div class="dropdown-item" @click="triggerFileInput(); showDropdown.upload = false">
                  <i class="fas fa-file-upload"></i> Upload Files
                </div>
                <div class="dropdown-item" @click="triggerFolderInput(); showDropdown.upload = false">
                  <i class="fas fa-folder-open"></i> Upload Folder
                </div>
             </div>
          </div>
        </div>
      </div>
      
      <div class="sidebar-status-box">
        <div class="vault-encryption-status">
          <i class="fas fa-lock text-gold"></i>
          <span>AES-256-GCM Active</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <ul>
          <li class="nav-item" :class="{ active: currentFilter === null }" @click="setCurrentFilter(null)">
            <i class="fas fa-vault"></i> All Encrypted
          </li>
          <li class="nav-item" :class="{ active: currentFilter === 'recent' }" @click="setCurrentFilter('recent')">
            <i class="fas fa-clock"></i> Recent
          </li>
          <li class="nav-item" :class="{ active: currentFilter === 'starred' }" @click="setCurrentFilter('starred')">
            <i class="fas fa-star"></i> Starred
          </li>
        </ul>
      </nav>
      
      <div class="sidebar-footer">
        <div class="nav-item" @click="showSecurityInfo">
          <i class="fas fa-info-circle"></i> Security Info
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="nautilus-main">
      
      <!-- Top Bar: Navigation & Tools -->
      <header class="nautilus-topbar glass-panel">
        <div class="breadcrumbs">
          <span 
            v-for="(crumb, index) in breadcrumb" 
            :key="index"
            class="crumb-item"
            @click="navigateToBreadcrumb(index)"
          >
            {{ crumb }}
            <i class="fas fa-chevron-right separator" v-if="index < breadcrumb.length - 1"></i>
          </span>
        </div>
        
        <div class="topbar-tools">
          <div class="search-box relative">
            <i class="fas fa-search"></i>
            <input type="text" placeholder="Search secure vault..." v-model="searchQuery"/>
            
            <button class="filter-btn" @click.stop="showFilters = !showFilters" :class="{ 'active': hasActiveFilters }" title="Search Filters">
              <i class="fas fa-filter"></i>
            </button>
            
            <transition name="dropdown-fade">
              <div class="search-filters glass-panel" v-if="showFilters" v-click-outside="() => showFilters = false">
                <div class="filter-header">
                  <span class="font-bold text-sm uppercase text-text-secondary">Filters</span>
                  <button class="clear-filters-btn" v-if="hasActiveFilters" @click="clearFilters">Clear All</button>
                </div>
                
                <div class="filter-group">
                  <label>Type</label>
                  <select v-model="searchFilters.type" class="glass-select">
                    <option value="">All Types</option>
                    <option value="folder">Folders</option>
                    <option value="document">Documents</option>
                    <option value="image">Images</option>
                    <option value="video">Videos</option>
                    <option value="audio">Audio</option>
                    <option value="archive">Archives</option>
                    <option value="code">Source Code</option>
                  </select>
                </div>
                
                <div class="filter-group">
                  <label>Size</label>
                  <select v-model="searchFilters.size" class="glass-select">
                    <option value="">Any Size</option>
                    <option value="small">&lt; 1 MB</option>
                    <option value="medium">1 MB - 100 MB</option>
                    <option value="large">&gt; 100 MB</option>
                  </select>
                </div>
                
                <div class="filter-group">
                  <label>Modified Date</label>
                  <select v-model="searchFilters.date" class="glass-select">
                    <option value="">Any Time</option>
                    <option value="today">Today</option>
                    <option value="week">Past 7 Days</option>
                    <option value="month">Past 30 Days</option>
                    <option value="year">Past Year</option>
                  </select>
                </div>
              </div>
            </transition>
          </div>
          
          <div class="view-toggles">
            <button :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'" title="Grid View">
              <i class="fas fa-th-large"></i>
            </button>
            <button :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'" title="List View">
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>
      </header>

      <!-- Vault Content Area -->
      <div 
        class="nautilus-content" 
        @contextmenu.prevent="showContextMenu($event)" 
        @mousedown="startDragSelection"
        @dragover.prevent
        @drop.prevent="handleDrop"
      >
        <div v-if="loading" class="loading-overlay">
          <div class="loader"></div>
          <span>Decrypting Metadata...</span>
        </div>

        <!-- Grid View -->
        <div v-else-if="viewMode === 'grid' && filteredFiles.length > 0" class="view-grid">
          <div 
            v-for="item in filteredFiles" 
            :key="item.id"
            class="grid-item"
            :class="{ selected: selectedFiles.includes(item.id) }"
            :data-file-id="item.id"
            draggable="true"
            @click.stop="handleItemClick(item, $event)"
            @dblclick="handleItemDoubleClick(item)"
            @contextmenu.stop.prevent="showItemContextMenu($event, item)"
            @dragstart="startItemDrag($event, item)"
          >
            <div class="item-icon-wrapper relative">
               <img v-if="hasThumbnail(item) && !item.thumbError" :src="getThumbnailUrl(item)" class="file-thumbnail" @error="item.thumbError = true">
               <i v-else :class="[getFileIcon(item), 'file-icon']"></i>
               <div v-if="item.is_starred" class="star-indicator">
                 <i class="fas fa-star text-gold"></i>
               </div>
            </div>
            <div class="item-name" :title="item.filename">{{ item.filename }}</div>
          </div>
          <!-- Selection Box Overlay -->
          <div 
            v-if="selectionBox.visible"
            class="selection-box"
            :style="{
              left: Math.min(selectionBox.startX, selectionBox.endX) + 'px',
              top: Math.min(selectionBox.startY, selectionBox.endY) + 'px',
              width: Math.abs(selectionBox.endX - selectionBox.startX) + 'px',
              height: Math.abs(selectionBox.endY - selectionBox.startY) + 'px'
            }"
          ></div>
        </div>

        <!-- List View -->
        <div v-else-if="viewMode === 'list' && filteredFiles.length > 0" class="view-list">
          <div class="list-header">
            <div class="col-name">Name</div>
            <div class="col-date">Modified</div>
            <div class="col-size">Size</div>
          </div>
          <div class="list-body">
            <div 
              v-for="item in filteredFiles" 
              :key="item.id"
              class="list-row"
              :class="{ selected: selectedFiles.includes(item.id) }"
              :data-file-id="item.id"
              draggable="true"
              @click.stop="handleItemClick(item, $event)"
              @dblclick="handleItemDoubleClick(item)"
              @contextmenu.stop.prevent="showItemContextMenu($event, item)"
              @dragstart="startItemDrag($event, item)"
            >
              <div class="col-name">
                <div class="thumbnail-wrapper-list">
                  <img v-if="hasThumbnail(item) && !item.thumbError" :src="getThumbnailUrl(item)" class="file-thumbnail-small" @error="item.thumbError = true">
                  <i v-else :class="[getFileIcon(item), 'file-icon-small']"></i>
                </div>
                <span>{{ item.filename }}</span>
                <i v-if="item.is_starred" class="fas fa-star text-gold star-small"></i>
              </div>
              <div class="col-date">{{ formatDate(item.modified_at) }}</div>
              <div class="col-size">{{ item.is_folder ? '--' : formatSize(item.file_size) }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="!loading && filteredFiles.length === 0" class="empty-state">
          <i :class="['fas', currentFilter === 'starred' ? 'fa-star' : currentFilter === 'recent' ? 'fa-history' : 'fa-vault', 'empty-icon']"></i>
          <h3>{{ currentFilter === 'starred' ? 'No starred items' : currentFilter === 'recent' ? 'No recent items' : 'Vault is Empty' }}</h3>
          <p v-if="!currentFilter">Drag and drop files here to encrypt and store them securely.</p>
          <p v-else>Items you {{ currentFilter }} will appear here.</p>
        </div>
      </div>
    </main>


    <!-- Global Hidden Inputs for Uploads -->
    <input type="file" ref="vaultFileInput" class="hidden-input" multiple @change="handleUpload" style="display: none;">
    <input type="file" ref="vaultFolderInput" class="hidden-input" webkitdirectory directory multiple @change="handleUpload" style="display: none;">

    <!-- Context Menu -->
    <div 
      v-if="contextMenu.visible"
      class="context-menu glass-panel"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <template v-if="contextMenu.item">
        <div class="menu-item" @click="openVaultFile(contextMenu.item)">
          <i class="fas fa-eye"></i> {{ contextMenu.item.is_folder ? 'Open Folder' : 'View / Preview' }}
        </div>
        <div class="menu-item" @click="toggleStar(contextMenu.item)">
          <i :class="['fas', contextMenu.item.is_starred ? 'fa-star-o' : 'fa-star']"></i> {{ contextMenu.item.is_starred ? 'Unstar' : 'Pin to Stars' }}
        </div>
        <div class="menu-item" @click="openShareModal(contextMenu.item)">
          <i class="fas fa-share-nodes"></i> Share Secure Link
        </div>
        <div v-if="contextMenu.item.is_folder" class="menu-item" @click="downloadFolderZip(contextMenu.item)">
          <i class="fas fa-file-archive"></i> Download as Zip
        </div>
        <div v-if="!contextMenu.item.is_folder" class="menu-item" @click="downloadFile(contextMenu.item)">
          <i class="fas fa-download"></i> Secure Download
        </div>
        <div class="menu-separator"></div>
        <div class="menu-item" @click="showItemProperties(contextMenu.item)">
          <i class="fas fa-info-circle"></i> Properties
        </div>
        <div class="menu-item danger" @click="confirmDelete(contextMenu.item)">
          <i class="fas fa-trash-alt"></i> Permanent Delete
        </div>
      </template>
      <template v-else>
        <div class="menu-item" @click="createFolder">
           <i class="fas fa-folder-plus"></i> New Folder
        </div>
        <div class="menu-item" @click="triggerFileInput">
           <i class="fas fa-file-upload"></i> Upload Files
        </div>
        <div class="menu-item" @click="triggerFolderInput">
           <i class="fas fa-folder-open"></i> Upload Folder
        </div>
        <div class="menu-separator"></div>
        <div class="menu-item" @click="fetchFiles()">
           <i class="fas fa-sync-alt"></i> Refresh
        </div>
      </template>
    </div>

    <!-- Modals -->
    <!-- Folder Creation Modal -->
    <div v-if="folderModal.visible" class="modal-overlay" @click.self="folderModal.visible = false">
      <div class="modal-content glass-panel folder-modal">
        <div class="modal-header">
          <h2><i class="fas fa-folder-plus text-gold mr-2"></i> New Secure Folder</h2>
          <button class="close-btn" @click="folderModal.visible = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Folder Name</label>
            <input 
              type="text" 
              v-model="folderModal.name" 
              placeholder="Enter folder name..." 
              class="glass-input-field"
              @keyup.enter="confirmCreateFolder"
              ref="folderNameInput"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="folderModal.visible = false">Cancel</button>
          <button class="btn-primary vault-primary" @click="confirmCreateFolder" :disabled="!folderModal.name">
            Create Folder
          </button>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="uploadModal.visible" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal-content upload-modal glass-panel">
        <div class="modal-header">
          <h2>Upload to Vault</h2>
          <button class="close-btn" @click="closeUploadModal"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <div class="upload-area" @click="triggerFileInput">
            <i class="fas fa-shield-alt upload-icon"></i>
            <p>Select files to encrypt and upload</p>
          </div>

          <div v-if="uploadModal.files.length > 0" class="upload-list-area scrollable-list">
            <h4>Selected Files ({{ uploadModal.files.length }})</h4>
            <div class="list-container">
              <div v-for="(file, index) in uploadModal.files" :key="index" class="upload-item">
                <div class="file-main-info">
                  <i :class="['fas', getFileIcon(file.name)]"></i>
                  <span class="file-name" :title="file.name">{{ file.name }}</span>
                </div>
                <div class="file-meta-info">
                  <span class="file-size">{{ formatSize(file.size || 0) }}</span>
                  <button class="remove-file-btn" @click="removeFileFromUpload(index)" v-if="!uploadStatus.active">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeUploadModal">Cancel</button>
          <button class="btn-primary" @click="startUpload">Encrypt & Upload</button>
        </div>
      </div>
    </div>

    <!-- Media Preview Modal -->
    <div v-if="mediaPreview.visible" class="modal-overlay" @click.self="mediaPreview.visible = false" style="z-index: 1005;">
      <div class="modal-content glass-panel media-preview-modal" :class="{ 'document-preview-modal': mediaPreview.type === 'document' }">
        <div class="modal-header">
          <h2 class="text-truncate">{{ mediaPreview.file?.filename }}</h2>
          <button class="close-btn" @click="mediaPreview.visible = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body media-body">
          <video v-if="mediaPreview.type === 'video'" 
                 :src="vaultMediaUrl(mediaPreview.file)" 
                 controls 
                 autoplay 
                 class="media-preview-content"></video>
          <img v-else-if="mediaPreview.type === 'image'" 
               :src="vaultMediaUrl(mediaPreview.file)" 
               class="media-preview-content">
          <iframe v-else 
                  :src="vaultMediaUrl(mediaPreview.file)" 
                  class="media-preview-content"
                  style="width: 100%; height: 100%; border: none;"></iframe>
        </div>
      </div>
    </div>

    <!-- Global Upload Progress Panel -->
    <div v-if="uploadStatus.active" class="global-upload-progress glass-panel" :class="{ 'minimized': uploadStatus.minimized }">
      <div class="progress-header" @click="uploadStatus.expanded = !uploadStatus.expanded">
        <div class="header-info">
          <i class="fas fa-cloud-upload-alt mr-2"></i>
          <span>{{ uploadStatus.files.filter(f => f.status === 'done').length }} / {{ uploadStatus.files.length }} uploaded</span>
        </div>
        <div class="header-actions">
          <button @click.stop="uploadStatus.minimized = !uploadStatus.minimized" class="icon-btn">
            <i :class="['fas', uploadStatus.minimized ? 'fa-window-maximize' : 'fa-minus']"></i>
          </button>
          <button v-if="uploadStatus.files.every(f => f.status !== 'uploading')" @click.stop="clearCompletedUploads" class="icon-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      
      <div v-if="!uploadStatus.minimized && uploadStatus.expanded" class="progress-body">
        <div v-for="(file, index) in uploadStatus.files" :key="index" class="progress-item">
          <div class="item-info">
            <i :class="['fas', file.icon]"></i>
            <span class="item-name" :title="file.name">{{ file.name }}</span>
            <span class="item-status">
               <i v-if="file.status === 'done'" class="fas fa-check-circle text-success"></i>
               <i v-else-if="file.status === 'error'" class="fas fa-exclamation-circle text-danger"></i>
               <span v-else>{{ file.progress }}%</span>
            </span>
          </div>
          <div class="item-bar-container">
            <div class="item-bar" :style="{ width: file.progress + '%', background: file.status === 'error' ? '#ef4444' : 'var(--accent-primary)' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Share Modal -->
    <div v-if="shareModal.visible" class="modal-overlay" @click.self="shareModal.visible = false">
      <div class="modal-content glass-panel share-modal">
        <div class="modal-header">
          <h2>Share "{{ shareModal.item?.name || shareModal.item?.filename }}"</h2>
          <button class="close-btn" @click="shareModal.visible = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Access Level</label>
            <select v-model="shareModal.accessLevel" class="glass-select">
              <option value="private">Private (Only You)</option>
              <option value="internal">Internal (Any User)</option>
              <option value="public">Public (Anyone with link)</option>
            </select>
          </div>
          
          <div class="form-group" v-if="shareModal.accessLevel !== 'private'">
            <label>Permission Level</label>
            <select v-model="shareModal.permissionLevel" class="glass-select">
              <option value="visitor">Visitor (View Only, NO Download)</option>
              <option value="viewer">Viewer (View & Download)</option>
              <option value="commenter">Commenter (View, Download & Comment)</option>
              <option value="editor">Editor (Full Access)</option>
            </select>
            <p class="text-xs text-gold mt-1" v-if="shareModal.permissionLevel === 'visitor'">
              <i class="fas fa-shield-alt"></i> Anti-screenshot & download protection enabled.
            </p>
          </div>
          
          <template v-if="shareModal.accessLevel !== 'private'">
            <div class="form-group">
              <label>Expiration (Hours)</label>
              <input type="number" v-model="shareModal.expiresHours" placeholder="Never" class="glass-input-field">
            </div>
            
            <div class="form-group">
              <label>Password Protection (Optional)</label>
              <input type="password" v-model="shareModal.password" placeholder="Set access password..." class="glass-input-field">
            </div>
            
            <div class="link-display" v-if="shareModal.generatedLink">
              <label>Hashed Link (Non-guessable)</label>
              <div class="link-copy-group">
                <input type="text" readonly :value="shareModal.generatedLink" class="glass-input-field link-input">
                <button class="btn-copy" @click="copyShareLink">
                  <i class="fas fa-copy"></i>
                </button>
              </div>
            </div>
          </template>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="shareModal.visible = false">Close</button>
          <button class="btn-primary vault-primary" @click="saveShareSettings">
            {{ shareModal.accessLevel === 'private' ? 'Disable Sharing' : 'Update Share Settings' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Hidden Inputs -->
    <input type="file" ref="fileInput" @change="handleUpload" multiple style="display: none">
    <!-- Properties Modal (Hover Window) -->
    <div v-if="propertyModal.visible" class="modal-overlay" @click.self="propertyModal.visible = false" style="z-index: 1006;">
      <div class="modal-content glass-panel property-modal-box">
        <div class="modal-header">
          <h2><i class="fas fa-shield-halved text-gold mr-2"></i> Vault Properties</h2>
          <button class="close-btn" @click="propertyModal.visible = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body properties-grid">
          <div class="detail-row">
            <span class="label">Name</span>
            <span class="value">{{ propertyModal.item?.filename }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Type</span>
            <span class="value capitalize">{{ propertyModal.item?.is_folder ? 'Secure Folder' : 'Encrypted File' }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Size</span>
            <span class="value">{{ formatSize(propertyModal.item?.file_size) }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Status</span>
            <span class="value"><i class="fas fa-lock text-gold mr-1"></i> AES-256-GCM</span>
          </div>
          <div class="detail-row">
            <span class="label">Access</span>
            <span class="value capitalize">
              <i :class="getAccessIcon(propertyModal.item?.access_level)" class="mr-1"></i>
              {{ formatAccessLevel(propertyModal.item?.access_level) }}
            </span>
          </div>
          <div class="detail-row">
            <span class="label">Modified</span>
            <span class="value">{{ formatDate(propertyModal.item?.modified_at) }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary vault-primary" @click="propertyModal.visible = false">Close</button>
        </div>
      </div>
    </div>

    <!-- Prompt Modal -->
    <div v-if="promptModal.visible" class="modal-overlay" @click.self="cancelPrompt" style="z-index: 1005;">
      <div class="modal-content glass-panel prompt-modal-box">
        <div class="modal-header">
          <h2>{{ promptModal.title }}</h2>
          <button class="close-btn" @click="cancelPrompt">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>{{ promptModal.label }}</label>
            <input 
              type="text" 
              class="glass-input-field" 
              v-model="promptModal.value" 
              :placeholder="promptModal.placeholder"
              @keyup.enter="confirmPrompt"
              ref="globalPromptInput"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="cancelPrompt">Cancel</button>
          <button class="btn-primary" @click="confirmPrompt">Confirm</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { apiGet, apiUpload, apiDelete, apiPatch, apiPost } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

const router = useRouter()
const userStore = useUserStore()

// State
const loading = ref(true)
const viewMode = ref('grid')
const files = ref([])
const selectedFiles = ref([])
const searchQuery = ref('')
const currentPath = ref('/')
const currentFilter = ref(null) 
const breadcrumb = ref(['Vault'])

const showFilters = ref(false)
const searchFilters = reactive({
  type: '',
  size: '',
  date: ''
})

const hasActiveFilters = computed(() => {
  return searchQuery.value !== '' || 
         searchFilters.type !== '' || 
         searchFilters.size !== '' || 
         searchFilters.date !== '';
});

const clearFilters = () => {
  searchQuery.value = ''
  searchFilters.type = ''
  searchFilters.size = ''
  searchFilters.date = ''
}

const promptModal = reactive({
  visible: false,
  title: '',
  label: '',
  value: '',
  placeholder: '',
  resolve: null
})

const showPrompt = (title, label, defaultValue = '', placeholder = '') => {
  return new Promise((resolve) => {
    promptModal.title = title
    promptModal.label = label
    promptModal.value = defaultValue
    promptModal.placeholder = placeholder
    promptModal.resolve = resolve
    promptModal.visible = true
  })
}

const confirmPrompt = () => {
  if (promptModal.resolve) promptModal.resolve(promptModal.value)
  promptModal.visible = false
}

const cancelPrompt = () => {
  if (promptModal.resolve) promptModal.resolve(null)
  promptModal.visible = false
}

const selectionBox = reactive({
  visible: false,
  startX: 0,
  startY: 0,
  endX: 0,
  endY: 0
})

// Selection handling
const selectFile = (file, multi = false) => {
  if (!multi) {
    selectedFiles.value = [file.id]
  } else {
    if (selectedFiles.value.includes(file.id)) {
      selectedFiles.value = selectedFiles.value.filter(id => id !== file.id)
    } else {
      selectedFiles.value.push(file.id)
    }
  }
}

const handleItemClick = (item, event) => {
  const isMulti = event.ctrlKey || event.metaKey
  selectFile(item, isMulti)
  if (userStore.isSingleClickOpen && !isMulti) {
    openVaultFile(item)
  }
}

const handleItemDoubleClick = (item) => {
  if (!userStore.isSingleClickOpen) {
    openVaultFile(item)
  }
}

const selectedItemDetails = computed(() => {
  if (selectedFiles.value.length === 1) {
    return files.value.find(f => f.id === selectedFiles.value[0])
  }
  return null
})

// Modals
const showDropdown = ref({
  upload: false,
  create: false
})

let dragContainer = null;

const startDragSelection = (event) => {
  if (event.shiftKey) return 
  
  const clickedItem = event.target.closest('.grid-item, .list-row');
  if (clickedItem) {
    const fileId = clickedItem.getAttribute('data-file-id');
    if (fileId && !selectedFiles.value.includes(fileId)) {
       selectedFiles.value = [fileId];
    }
    return; 
  }
  
  if (event.target.classList.contains('nautilus-content') || event.target.classList.contains('view-grid') || event.target.classList.contains('view-list')) {
     selectedFiles.value = []
  }

  dragContainer = event.currentTarget
  const rect = dragContainer.getBoundingClientRect()
  selectionBox.visible = false
  
  selectionBox.startX = event.clientX - rect.left + dragContainer.scrollLeft
  selectionBox.startY = event.clientY - rect.top + dragContainer.scrollTop
  selectionBox.endX = selectionBox.startX
  selectionBox.endY = selectionBox.startY
  
  document.addEventListener('mousemove', updateDragSelection)
  document.addEventListener('mouseup', endDragSelection)
}

const updateDragSelection = (event) => {
  if (!dragContainer) return
  if (event.dataTransfer && event.dataTransfer.types.includes('Files')) return;

  const rect = dragContainer.getBoundingClientRect()
  
  const currentX = event.clientX - rect.left + dragContainer.scrollLeft
  const currentY = event.clientY - rect.top + dragContainer.scrollTop
  
  if (Math.abs(currentX - selectionBox.startX) > 3 || Math.abs(currentY - selectionBox.startY) > 3) {
     selectionBox.visible = true
  }
  
  if (!selectionBox.visible) return
  
  window.getSelection().removeAllRanges()
  
  selectionBox.endX = currentX
  selectionBox.endY = currentY
  
  const minX = Math.min(selectionBox.startX, selectionBox.endX)
  const maxX = Math.max(selectionBox.startX, selectionBox.endX)
  const minY = Math.min(selectionBox.startY, selectionBox.endY)
  const maxY = Math.max(selectionBox.startY, selectionBox.endY)
  
  const items = document.querySelectorAll('.grid-item, .list-row')
  const newSelection = []
  
  items.forEach(item => {
    const itemRect = item.getBoundingClientRect()
    const containerRect = dragContainer.getBoundingClientRect()
    
    const itemLeft = itemRect.left - containerRect.left
    const itemRight = itemRect.right - containerRect.left
    const itemTop = itemRect.top - containerRect.top
    const itemBottom = itemRect.bottom - containerRect.top
    
    const intersectX = Math.max(0, Math.min(maxX, itemRight) - Math.max(minX, itemLeft))
    const intersectY = Math.max(0, Math.min(maxY, itemBottom) - Math.max(minY, itemTop))
    
    if (intersectX > 0 && intersectY > 0) {
      const fileId = item.getAttribute('data-file-id')
      if (fileId && !newSelection.includes(fileId)) {
        newSelection.push(fileId)
      }
    }
  })
  
  selectedFiles.value = newSelection
}

const endDragSelection = (event) => {
  dragContainer = null
  selectionBox.visible = false
  document.removeEventListener('mousemove', updateDragSelection)
  document.removeEventListener('mouseup', endDragSelection)
}

const startItemDrag = (event, item) => {
  if (!selectedFiles.value.includes(item.id)) {
    selectedFiles.value = [item.id]
  }
  const dragData = {
    type: 'vault-items',
    items: selectedFiles.value
  }
  event.dataTransfer.setData('text/plain', JSON.stringify(dragData))
  event.dataTransfer.effectAllowed = 'move'
}

const uploadStatus = reactive({
  active: false,
  minimized: false,
  expanded: true,
  files: [], // { name, size, progress, status, icon }
  successCount: 0,
  errorCount: 0
})

const uploadModal = reactive({
  visible: false,
  files: []
})

const folderModal = reactive({
  visible: false,
  name: ''
})

const folderNameInput = ref(null)

const mediaPreview = reactive({
  visible: false,
  file: null,
  type: 'other'
})

const shareModal = reactive({
  visible: false,
  item: null,
  accessLevel: 'private',
  permissionLevel: 'viewer',
  expiresHours: null,
  password: '',
  generatedLink: ''
})

// Watch for access level changes to show warning for folders
watch(() => shareModal.accessLevel, async (newVal) => {
  if (newVal === 'public' && shareModal.item?.is_folder) {
    const confirm = await showConfirm(
      'Public Folder Sharing',
      'Sharing a folder publicly will recursively grant access to ALL its contents. Do you want to proceed?',
      'Share Publicly',
      'Cancel'
    )
    if (!confirm) {
      shareModal.accessLevel = 'private'
    }
  }
})

const propertyModal = reactive({
  visible: false,
  item: null
})

const showItemProperties = (item) => {
  propertyModal.item = item
  propertyModal.visible = true
}

const getAccessIcon = (level) => {
  if (level === 'public') return 'fas fa-globe'
  if (level === 'internal') return 'fas fa-users'
  if (level === 'specific_users') return 'fas fa-user-friends'
  return 'fas fa-lock'
}

const formatAccessLevel = (level) => {
  if (level === 'public') return 'Anyone with link'
  if (level === 'internal') return 'Account only'
  if (level === 'specific_users') return 'Shared users'
  return 'Private'
}

const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  item: null
})

const openDetails = (item) => {
  selectedFiles.value = [item.id]
}

// API Actions
const fetchFiles = async () => {
  loading.value = true
  let url = `/nautilus/files?folder_path=${currentPath.value}`
  if (currentFilter.value) url = `/nautilus/files?filter=${currentFilter.value}`
  
  try {
    const data = await apiGet(url)
    files.value = data
  } catch (err) {
    showError('Failed to fetch vault data')
  } finally {
    loading.value = false
  }
}

const setCurrentFilter = (filter) => {
  currentFilter.value = filter
  if (filter) {
    breadcrumb.value = ['Vault', filter.charAt(0).toUpperCase() + filter.slice(1)]
  } else {
    breadcrumb.value = ['Vault']
    currentPath.value = '/'
  }
  selectedFiles.value = []
  fetchFiles()
}

const toggleStar = async (file) => {
  try {
    const res = await apiPatch(`/nautilus/star/${file.id}`)
    file.is_starred = res.is_starred
    showSuccess(file.is_starred ? 'Pinned to Stars' : 'Removed from Stars')
  } catch (err) {
    showError('Failed to toggle star')
  }
}

const confirmCreateFolder = async () => {
  if (!folderModal.name) return
  try {
    await apiPost('/nautilus/mkdir', {
      name: folderModal.name,
      folder_path: currentPath.value
    })
    showSuccess('Virtual folder created')
    folderModal.visible = false
    fetchFiles()
  } catch (err) {
    showError('Failed to create folder')
  }
}

const openUploadModal = (files) => {
  uploadModal.files = files.map(f => ({
    name: f.name,
    size: f.size,
    progress: 0,
    originalFile: f,
    relPath: f.webkitRelativePath || ''
  }))
  uploadModal.visible = true
}

const closeUploadModal = () => {
  uploadModal.visible = false
  uploadModal.files = []
}

const handleUpload = (event) => {
  const files = Array.from(event.target.files)
  if (files.length === 0) return
  openUploadModal(files)
}

const removeFileFromUpload = (index) => {
  if (uploadStatus.active) return
  uploadModal.files.splice(index, 1)
}

const startUpload = async () => {
  if (uploadModal.files.length === 0) return
  
  const targetUploadPath = currentPath.value
  const newUploads = []

  // Check for duplicates before starting
  for (let f of uploadModal.files) {
    const existingFile = files.value.find(file => file.filename === f.name && file.folder_path === targetUploadPath)
    if (existingFile) {
      const confirmed = await showConfirm(`"${f.name}" already exists in this folder. Replace it?`, 'Duplicate File', 'Cancel')
      if (confirmed) {
        try {
          await apiDelete(`/nautilus/purge/${existingFile.id}`)
        } catch(e) { console.error("Failed to purge duplicate file:", e) }
        newUploads.push({...f, targetPath: targetUploadPath})
      }
    } else {
      newUploads.push({...f, targetPath: targetUploadPath})
    }
  }

  if (newUploads.length === 0) {
    closeUploadModal()
    return
  }

  // Set global upload status
  uploadStatus.active = true
  uploadStatus.minimized = false
  uploadStatus.expanded = true
  
  // Move files to global tracker
  const trackingUploads = newUploads.map(f => ({
    name: f.name,
    size: f.size,
    progress: 0,
    status: 'uploading',
    icon: getFileIcon(f.name),
    originalFile: f.originalFile,
    relPath: f.relPath,
    targetPath: f.targetPath
  }))
  
  uploadStatus.files = [...trackingUploads, ...uploadStatus.files]
  closeUploadModal()
  
  for (let fileObj of trackingUploads) {
    const formData = new FormData()
    formData.append('file', fileObj.originalFile)
    
    let path = fileObj.targetPath === '/' ? '' : fileObj.targetPath
    if (fileObj.relPath) {
      path = path ? `${path}/${fileObj.relPath}` : `/${fileObj.relPath}`
    }
    if (!path) path = '/'
    
    formData.append('folder_path', path)
    
    try {
      await apiUpload('/nautilus/upload', formData, (progress) => {
        fileObj.progress = progress
      })
      fileObj.progress = 100
      fileObj.status = 'done'
      uploadStatus.successCount++
    } catch (err) {
      console.error('Vault Upload Error:', err)
      fileObj.status = 'error'
      fileObj.progress = 0
      uploadStatus.errorCount++
    }
  }

  if (currentPath.value === targetUploadPath) {
    await fetchFiles()
  }
}

const clearCompletedUploads = () => {
  uploadStatus.files = uploadStatus.files.filter(f => f.status === 'uploading')
  if (uploadStatus.files.length === 0) {
    uploadStatus.active = false
    uploadStatus.successCount = 0
    uploadStatus.errorCount = 0
  }
}

const downloadFile = (file) => {
  const url = vaultMediaUrl(file)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', file.filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const confirmDelete = async (file) => {
  const confirmed = await showConfirm(`PERMANENTLY delete "${file.filename}"? This cannot be undone.`, 'Delete Permanently', 'Cancel')
  if (confirmed) {
    try {
      await apiDelete(`/nautilus/purge/${file.id}`)
      showSuccess('Wiped from Vault')
      selectedFiles.value = []
      fetchFiles()
    } catch (err) {
      showError('Purge failed')
    }
  }
}

// Sharing
const openShareModal = async (originalItem) => {
  try {
    // Fetch latest metadata to ensure share state is accurate
    const item = await apiGet(`/nautilus/file/${originalItem.id}`)
    
    shareModal.item = item
    // Correctly map access level
    if (item.access_level === 'only_me' || !item.access_level) {
      shareModal.accessLevel = 'private'
    } else if (item.access_level === 'public') {
      shareModal.accessLevel = 'link'
    } else if (item.access_level === 'specific_users') {
      shareModal.accessLevel = 'account'
    } else {
      shareModal.accessLevel = 'private'
    }
    shareModal.permissionLevel = item.permission_level || 'viewer'
    shareModal.expiresHours = null
    shareModal.password = ''
    shareModal.encrypted = !!item.share_link_id && !!item.public_share_link
    shareModal.generatedLink = item.share_link_id ? `${window.location.origin}/s/${item.share_link_id}` : ''
    shareModal.visible = true
  } catch (err) {
    showError('Failed to fetch share settings')
  }
}

const saveShareSettings = async () => {
  try {
    const res = await apiPost(`/nautilus/share/${shareModal.item.id}`, {
      access_level: shareModal.accessLevel,
      permission_level: shareModal.permissionLevel,
      expires_hours: shareModal.expiresHours,
      password: shareModal.password
    })
    
    shareModal.item.access_level = res.access_level
    shareModal.item.share_link_id = res.share_link_id
    shareModal.generatedLink = res.share_link_id ? `${window.location.origin}/s/${res.share_link_id}` : ''
    
    showSuccess('Share settings updated')
    if (shareModal.accessLevel === 'private') {
      shareModal.visible = false
    }
  } catch (err) {
    showError(err.message || 'Sharing failed')
  }
}

const downloadFolderZip = (item) => {
  window.open(`/api/nautilus/zip/${item.id}`)
  hideContextMenu()
}

const copyShareLink = () => {
  navigator.clipboard.writeText(shareModal.generatedLink)
  showSuccess('Link copied to clipboard')
}

// Helpers
const filteredFiles = computed(() => {
  return files.value.filter(f => {
    if (searchQuery.value && !f.filename.toLowerCase().includes(searchQuery.value.toLowerCase())) return false;
    
    if (searchFilters.type) {
      if (searchFilters.type === 'folder' && !f.is_folder) return false;
      const mime = (f.mime_type || '').toLowerCase();
      if (searchFilters.type === 'document' && !mime.includes('text') && !mime.includes('pdf')) return false;
      if (searchFilters.type === 'image' && !mime.includes('image')) return false;
      if (searchFilters.type === 'video' && !mime.includes('video')) return false;
      if (searchFilters.type === 'audio' && !mime.includes('audio')) return false;
      if (searchFilters.type === 'archive' && !(mime.includes('zip') || mime.includes('rar') || mime.includes('tar'))) return false;
    }
    
    if (searchFilters.size && !f.is_folder) {
      const sizeMB = f.file_size / (1024 * 1024);
      if (searchFilters.size === 'small' && sizeMB >= 1) return false;
      if (searchFilters.size === 'medium' && (sizeMB < 1 || sizeMB > 100)) return false;
      if (searchFilters.size === 'large' && sizeMB <= 100) return false;
    }
    
    if (searchFilters.date) {
       const fileDate = new Date(f.modified_at);
       const now = new Date();
       const diffTime = Math.abs(now - fileDate);
       const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
       
       if (searchFilters.date === 'today' && diffDays > 1) return false;
       if (searchFilters.date === 'week' && diffDays > 7) return false;
       if (searchFilters.date === 'month' && diffDays > 30) return false;
       if (searchFilters.date === 'year' && diffDays > 365) return false;
    }
    
    return true;
  });
})

const getFileIcon = (file) => {
  if (typeof file === 'string') {
    const ext = file.split('.').pop().toLowerCase()
    if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(ext)) return 'fas fa-file-image'
    if (['mp4', 'webm', 'ogg', 'mov'].includes(ext)) return 'fas fa-file-video'
    if (['mp3', 'wav', 'flac'].includes(ext)) return 'fas fa-file-audio'
    if (['pdf'].includes(ext)) return 'fas fa-file-pdf'
    if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return 'fas fa-file-archive'
    return 'fas fa-file'
  }
  if (file.is_folder) return 'fas fa-folder text-blue-400'
  const mime = (file.mime_type || '').toLowerCase()
  if (mime.includes('pdf')) return 'fas fa-file-pdf text-red-500'
  if (mime.includes('video')) return 'fas fa-file-video text-purple-400'
  if (mime.includes('image')) return 'fas fa-file-image text-blue-400'
  if (mime.includes('zip') || mime.includes('rar')) return 'fas fa-file-archive text-yellow-500'
  return 'fas fa-file-shield text-gold'
}
const hasThumbnail = (file) => {
  if (file.is_folder) return false
  const name = file.filename || ''
  const ext = name.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'mp4', 'avi', 'mkv', 'mov', 'webm', 'pdf'].includes(ext)
}

const getThumbnailUrl = (item) => {
  const token = localStorage.getItem('token')
  return `/api/nautilus/thumbnail/${item.id}?token=${token}`
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  return new Date(dateStr).toLocaleDateString()
}

const vaultMediaUrl = (file) => {
  if (!file) return ''
  const token = localStorage.getItem('token')
  return `/api/nautilus/source/${file.id}?token=${token}&ext=.ts`
}

const openVaultFile = (file) => {
  if (file.is_folder) {
    currentPath.value = (currentPath.value === '/' ? '' : currentPath.value) + '/' + file.filename
    breadcrumb.value.push(file.filename)
    fetchFiles()
    return
  }
  const mime = file.mime_type.toLowerCase()
  mediaPreview.file = file
  if (mime.includes('video')) mediaPreview.type = 'video'
  else if (mime.includes('image')) mediaPreview.type = 'image'
  else mediaPreview.type = 'other'
  mediaPreview.visible = true
}

// Context Menu Logic
const showContextMenu = (e) => {
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
  contextMenu.item = null
  contextMenu.visible = true
}

const showItemContextMenu = (e, item) => {
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
  contextMenu.item = item
  contextMenu.visible = true
  if (!selectedFiles.value.includes(item.id)) {
    selectedFiles.value = [item.id]
  }
}

const closeContextMenu = () => contextMenu.visible = false

const navigateToBreadcrumb = (index) => {
  if (index === 0) {
    setCurrentFilter(null)
    return
  }
  if (currentFilter.value) return
  const newBreadcrumb = breadcrumb.value.slice(0, index + 1)
  breadcrumb.value = newBreadcrumb
  const pathParts = newBreadcrumb.slice(1)
  currentPath.value = '/' + pathParts.join('/')
  fetchFiles()
}

const createFolder = () => {
  folderModal.name = ''
  folderModal.visible = true
  setTimeout(() => { if (folderNameInput.value) folderNameInput.value.focus() }, 100)
}

const triggerUpload = () => fileInput.value.click()
const handleDrop = (e) => {
  const droppedFiles = e.dataTransfer.files
  if (droppedFiles.length > 0) {
    handleUpload({ target: { files: droppedFiles } })
  }
}

const vaultFileInput = ref(null)
const vaultFolderInput = ref(null)

const triggerFileInput = () => vaultFileInput.value.click()
const triggerFolderInput = () => vaultFolderInput.value.click()

const showInfo = () => {
  showSuccess('Nautilus Vault: All files are encrypted using AES-256-GCM before being stored on disk. Decryption only happens in-flight.')
}

const renameSelection = async () => {
  hideContextMenu();
  const items = selectedFiles.value.length > 0 ? selectedFiles.value : (contextMenu.item ? [contextMenu.item.id] : []);
  if (items.length !== 1) return; // Vault only supports renaming a single file at a time right now

  const itemObj = files.value.find(f => f.id === items[0]);
  if (!itemObj) return;
  
  const newName = await showPrompt('Rename Item', 'Enter new name:', itemObj.filename);
  if (newName && newName !== itemObj.filename) {
    try {
      await apiPatch('/nautilus/rename', { file_id: items[0], new_name: newName });
      showSuccess(`Renamed to "${newName}"`);
      fetchFiles();
    } catch(err) { 
      showError('Failed to rename item'); 
    }
  }
}

const handleKeyDown = (e) => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;
  
  if (e.key === 'Escape') {
    selectedFiles.value = [];
    closeContextMenu();
    cancelPrompt();         
    closeUploadModal();
    shareModal.visible = false;
    propertyModal.visible = false;
    folderModal.visible = false;
    mediaPreview.visible = false;    
  } else if (e.key === 'Delete') {
    if (selectedFiles.value.length > 0) {
      // Vault deletes permanently inherently
      confirmDelete(files.value.find(f => f.id === selectedFiles.value[0])); 
    } else if (contextMenu.item) {
      confirmDelete(contextMenu.item);
    }
  } else if (e.key === 'Enter') {
    if (promptModal.visible && promptModal.resolve) {
      confirmPrompt();
    } else if (selectedFiles.value.length === 1 || contextMenu.item) {
      const target = contextMenu.item || files.value.find(f => f.id === selectedFiles.value[0]);
      if (target) {
        openVaultFile(target);
      }
    }
  } else if (e.key === 'F2') {
    if (selectedFiles.value.length === 1 || contextMenu.item) {
      renameSelection();
    }
  } else if (e.ctrlKey && e.key === 'a') {
    e.preventDefault();
    selectedFiles.value = files.value.map(f => f.id);
  }
};

onMounted(() => {
  fetchFiles()
  window.addEventListener('click', closeContextMenu)
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('click', closeContextMenu)
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
/* Base Layout matching Drive.vue */
.nautilus-drive {
  display: flex;
  position: absolute;
  top: 70px; /* Accounts for dashboard header */
  left: 0;
  right: 0;
  bottom: 0;
  height: auto;
  background: rgba(0, 0, 0, 0.6); /* Slightly deeper to cover the whole backdrop */
}

.modal-content {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(20px);
  transition: max-width 0.3s ease, width 0.3s ease, height 0.3s ease;
}

.document-preview-modal {
  max-width: 90vw !important;
  width: 90vw;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

.document-preview-modal .media-preview-body {
  flex: 1;
  padding: 0;
  overflow: hidden;
}

.document-preview-modal iframe {
  width: 100%;
  height: 100%;
}

.property-modal-box {
  max-width: 400px;
}

.properties-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.detail-row .label {
  color: var(--text-secondary);
  font-weight: 600;
}

.detail-row .value {
  color: var(--text-primary);
  text-align: right;
  max-width: 60%;
  word-break: break-all;
}

.glass-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 1.5rem;
  box-shadow: var(--glass-shadow);
}

.vault-primary {
  background: linear-gradient(135deg, #7c3aed, #db2777) !important;
  box-shadow: 0 0 20px rgba(124, 58, 237, 0.4) !important;
}

/* Sidebar */
.nautilus-sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  flex-shrink: 0;
  position: relative;
  z-index: 60;
}

.sidebar-nav {
  margin-top: 2rem;
  flex-grow: 1;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  color: var(--text-secondary);
}

.nav-item:hover, .nav-item.active {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.nav-item.active {
  color: var(--accent-primary);
}

.sidebar-status-box {
  margin: 1.5rem 0;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
}

.vault-encryption-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: #fbbf24;
}

/* Main Content */
.nautilus-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.nautilus-topbar {
  height: 70px;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  position: relative;
  z-index: 50;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.crumb-item {
  cursor: pointer;
}

.crumb-item:last-child {
  color: white;
}

.topbar-tools {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.search-box {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 300px;
}

.search-box input {
  background: none;
  border: none;
  color: white;
  outline: none;
  width: 100%;
}

.view-toggles {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px;
  border-radius: 10px;
}

.view-toggles button {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.view-toggles button.active {
  background: rgba(255, 255, 255, 0.1);
  color: var(--accent-primary);
}

/* Content Area */
.nautilus-content {
  flex: 1;
  position: relative;
  overflow-y: auto;
  padding: 1rem;
}

.view-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1.5rem;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem 1rem;
  border-radius: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  border: 1px solid transparent;
}

.grid-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.grid-item.selected {
  background: rgba(124, 58, 237, 0.15);
  border-color: rgba(124, 58, 237, 0.3);
}

.file-thumbnail {
  width: 80px;
  height: 80px;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  transition: transform 0.2s ease;
}

.thumbnail-wrapper-list {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.file-thumbnail-small {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.star-indicator {
  font-size: 0.9rem;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-icon-wrapper {
  margin-bottom: 1rem;
  font-size: 3rem;
  height: 80px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-name {
  font-size: 0.85rem;
  text-align: center;
  font-weight: 500;
  color: var(--text-primary);
  width: 100%;
  padding: 0 4px;
  
  /* Default: Truncate to one line */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  
  transition: all 0.2s ease;
}

.grid-item.selected .item-name {
  /* Selected: Show full name */
  white-space: normal;
  word-break: break-all;
  display: -webkit-box;
  -webkit-line-clamp: 4; /* Allow up to 4 lines when selected */
  -webkit-box-orient: vertical;
  overflow: visible;
  text-overflow: initial;
}

/* List View */
.view-list {
  display: flex;
  flex-direction: column;
}

.list-header {
  display: grid;
  grid-template-columns: 2fr 1fr 100px;
  padding: 1rem 1.5rem;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--glass-border);
}

.list-row {
  display: grid;
  grid-template-columns: 2fr 1fr 100px;
  padding: 1rem 1.5rem;
  align-items: center;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.list-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.list-row.selected {
  background: rgba(124, 58, 237, 0.1);
}

.file-icon-small {
  margin-right: 1rem;
  width: 24px;
  text-align: center;
}

/* Details Sidebar */
.nautilus-details {
  width: 320px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
}

.details-header {
  text-align: center;
}

.preview-box {
  height: 180px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 1rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-icon-large {
  font-size: 5rem;
}

.details-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.detail-label { color: var(--text-secondary); }
.detail-value { font-weight: 500; }

.details-actions {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.btn-action {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  color: white;
  padding: 0.6rem;
  border-radius: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
  font-size: 0.85rem;
}

.btn-action:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-action.danger {
  color: #ef4444;
}

/* Context Menu */
.context-menu {
  position: fixed;
  z-index: 1000;
}

/* Search Filters Dropdown */
.dropdown-fade-enter-active, .dropdown-fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.dropdown-fade-enter-from, .dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
.search-filters {
  position: absolute;
  top: 110%; 
  right: 0;
  width: 300px;
  background: rgba(20, 20, 25, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  z-index: 1000;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.search-filters .filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}
.search-filters label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
  display: block;
}
.glass-select {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 0.9rem;
}
.search-filters .clear-filters-btn {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0;
}
.search-filters .clear-filters-btn:hover {
  text-decoration: underline;
}

/* Global Progress Panel */
.global-upload-progress {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 360px;
  z-index: 2000;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 15px 50px rgba(0,0,0,0.6);
  border: 1px solid var(--accent-primary);
  background: var(--glass-bg-primary);
}
.global-upload-progress.minimized {
  width: 280px;
  bottom: 1rem;
}
.progress-header {
  padding: 0.75rem 1rem;
  background: var(--accent-primary);
  color: #0f172a;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
}
.header-actions {
  display: flex;
  gap: 0.5rem;
}
.icon-btn {
  background: transparent;
  border: none;
  color: #0f172a;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}
.icon-btn:hover {
  background: rgba(15, 23, 42, 0.1);
}
.progress-body {
  max-height: 300px;
  overflow-y: auto;
  padding: 0.5rem 0;
}
.progress-item {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--glass-border);
}
.progress-item:last-child {
  border-bottom: none;
}
.item-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 0.5rem;
}
.item-status {
  font-size: 0.8rem;
  font-weight: 600;
}
.item-bar-container {
  height: 4px;
  background: rgba(0,0,0,0.2);
  border-radius: 2px;
  overflow: hidden;
}
.item-bar {
  height: 100%;
  transition: width 0.3s;
}
.text-success { color: #10b981; }
.text-danger { color: #ef4444; }

/* Selection Box */
.selection-box {
  position: absolute;
  border: 1px solid rgba(124, 58, 237, 0.8);
  background: rgba(124, 58, 237, 0.2);
  pointer-events: none;
  z-index: 100;
}
.dropdown-wrapper {
  position: relative;
  width: 100%;
}
.dropdown-menu {
  position: absolute;
  top: 105%;
  left: 0;
  width: 100%;
  z-index: 50;
  padding: 0.5rem 0;
  display: flex;
  flex-direction: column;
  background: rgba(40, 40, 45, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
}
.dropdown-item {
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: background 0.2s;
  color: var(--text-primary);
  font-size: 0.9rem;
}
.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.1);
}
.filter-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
}
.filter-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}
.filter-btn.active {
  color: var(--accent-primary);
  background: rgba(124, 58, 237, 0.15);
}

.menu-item {
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.menu-item:hover {
  background: rgba(255,255,255,0.1);
}

.menu-item.danger { color: #ef4444; }
.menu-separator { height: 1px; background: var(--glass-border); margin: 0.5rem 0; }

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.7);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}

.modal-content {
  width: 450px;
  padding: 2rem;
  position: relative;
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1.5rem;
}

.close-btn {
  background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 1.2rem;
}

.form-group { margin-bottom: 1.25rem; }
.form-group label { display: block; margin-bottom: 0.5rem; color: var(--text-secondary); font-size: 0.9rem; }

.glass-input-field, .glass-select {
  width: 100%;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--glass-border);
  border-radius: 0.5rem;
  padding: 0.75rem;
  color: white;
  outline: none;
}

.modal-footer {
  display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem;
}

/* Share Link Styles */
.link-display {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(0,0,0,0.2);
  border-radius: 0.75rem;
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.link-copy-group {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.link-input {
  font-family: monospace;
  font-size: 0.8rem;
  background: rgba(0,0,0,0.3) !important;
}

.btn-copy {
  background: var(--accent-primary);
  border: none;
  color: white;
  padding: 0 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
}

/* Indicators */
.star-indicator {
  position: absolute;
  top: -5px; right: -5px;
  background: var(--bg-secondary);
  border: 1px solid var(--accent-warning);
  border-radius: 50%; width: 20px; height: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.65rem;
}

.text-gold { color: #fbbf24; }
.mr-2 { margin-right: 0.5rem; }

/* Empty States & Loading */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; opacity: 0.5; text-align: center;
}

.empty-icon { font-size: 4rem; margin-bottom: 1rem; }

.loading-overlay {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%;
}

.loader {
  border: 3px solid rgba(255,255,255,0.1);
  border-top: 3px solid var(--accent-primary);
  border-radius: 50%; width: 40px; height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Media Preview Content */
.media-preview-content {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 0.5rem;
}

.media-modal {
  width: 80% !important;
  max-width: 1000px !important;
}

.media-body {
  display: flex; align-items: center; justify-content: center;
  min-height: 400px;
}

/* Sidebar Refinement */
.sidebar-creation-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.create-btn {
  width: 100%;
  justify-content: flex-start;
  padding: 0.8rem 1.2rem;
  font-size: 0.95rem;
}

/* Dropdown Styles */
.dropdown-wrapper {
  position: relative;
  width: 100%;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 5px;
  z-index: 1100;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

.dropdown-item {
  padding: 0.8rem 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 0.9rem;
}

.dropdown-item:hover {
  background: var(--glass-bg-hover);
}

.dropdown-item i {
  color: var(--accent-primary);
  width: 16px;
  text-align: center;
}

/* Scrollable List in Modal */
.scrollable-list {
  margin-top: 1.5rem;
}

.scrollable-list .list-container {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  background: rgba(0,0,0,0.1);
  padding: 0.5rem;
}

.scrollable-list .upload-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.8rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.scrollable-list .upload-item:last-child {
  border-bottom: none;
}

.file-main-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.9rem;
}

.file-meta-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: 1rem;
}

.file-size {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-family: monospace;
}

.remove-file-btn {
  background: transparent;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.remove-file-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* Global Progress Panel */
.global-upload-progress {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 360px;
  z-index: 2000;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 15px 50px rgba(0,0,0,0.6);
  border: 1px solid var(--accent-primary);
  background: var(--glass-bg-primary);
}

.global-upload-progress.minimized {
  width: 280px;
  bottom: 1rem;
}

.progress-header {
  padding: 0.75rem 1rem;
  background: var(--accent-primary);
  color: #0f172a;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  background: transparent;
  border: none;
  color: #0f172a;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.icon-btn:hover {
  background: rgba(15, 23, 42, 0.1);
}

.progress-body {
  max-height: 300px;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.progress-item {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.progress-item:last-child {
  border-bottom: none;
}

.item-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 0.5rem;
}

.item-name {
  flex: 1;
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-status {
  font-size: 0.8rem;
  font-weight: 600;
}

.item-bar-container {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.item-bar {
  height: 100%;
  transition: width 0.3s ease;
}

.text-success { color: #10b981; }
.text-danger { color: #ef4444; }

</style>
