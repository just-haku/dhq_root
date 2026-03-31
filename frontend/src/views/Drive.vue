<template>
  <div class="nautilus-drive">
    <!-- Left Sidebar: Navigation & Actions -->
    <aside class="nautilus-sidebar glass-panel">
      <div class="sidebar-header">
        <div class="sidebar-creation-group">
          <!-- New Folder Button -->
          <button 
            class="btn-primary create-btn" 
            @click="createFolder" 
            :disabled="currentFilter !== null"
            :style="{ opacity: currentFilter !== null ? '0.5' : '1', cursor: currentFilter !== null ? 'not-allowed' : 'pointer' }"
          >
            <i class="fas fa-folder-plus"></i> New Folder
          </button>

          <!-- Upload Dropdown -->
          <div class="dropdown-wrapper">
             <button 
               class="btn-secondary create-btn upload-dropdown-btn" 
               @click="showDropdown.upload = !showDropdown.upload"
               :disabled="currentFilter !== null"
               :style="{ opacity: currentFilter !== null ? '0.5' : '1', cursor: currentFilter !== null ? 'not-allowed' : 'pointer' }"
             >
               <i class="fas fa-cloud-upload-alt"></i> Upload <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: auto;"></i>
             </button>
             
             <div v-if="showDropdown.upload" class="dropdown-menu glass-panel">
                <div class="dropdown-item" @click="uploadFiles(); showDropdown.upload = false">
                  <i class="fas fa-file-upload"></i> Upload Files
                </div>
                <div class="dropdown-item" @click="uploadFolder(); showDropdown.upload = false">
                  <i class="fas fa-folder-open"></i> Upload Folder
                </div>
             </div>
          </div>
        </div>
      </div>
      
      <div class="sidebar-quota">
        <div class="quota-info">
          <div class="quota-text" style="display: flex; justify-content: space-between; align-items: center;">
            <span>{{ formatSize(usedQuota) }} of {{ formatSize(userQuota) }} used ({{ typeof quotaPercentage === 'number' ? quotaPercentage.toFixed(2) : quotaPercentage }}%)</span>
            <i class="fas fa-sync-alt" @click="syncQuota" style="cursor: pointer; color: var(--text-secondary);" title="Recalculate Quota"></i>
          </div>
          <div class="quota-bar">
            <div class="quota-fill" :style="{ width: (usedQuota / userQuota * 100) + '%' }"></div>
          </div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <ul>
          <li class="nav-item" :class="{ active: currentFilter === null }" @click="setCurrentFilter(null)">
            <i class="fas fa-home"></i> Home
          </li>
          <li class="nav-item" :class="{ active: currentFilter === 'recent' }" @click="setCurrentFilter('recent')">
            <i class="fas fa-clock"></i> Recent
          </li>
          <li class="nav-item" :class="{ active: currentFilter === 'starred' }" @click="setCurrentFilter('starred')">
            <i class="fas fa-star"></i> Starred
          </li>
          <li class="nav-item" :class="{ active: currentFilter === 'trash' }" @click="setCurrentFilter('trash')">
            <i class="fas fa-trash"></i> Trash
          </li>
        </ul>
      </nav>
      
      <div class="sidebar-footer" v-if="userRole === 'OP' || userRole === 'AD'">
        <div class="nav-section-title">Network Locations</div>
        <ul>
          <li class="nav-item">
            <i class="fas fa-server"></i> Shared Drives
          </li>
          <li class="nav-item">
            <i class="fas fa-users"></i> Team Folders
          </li>
        </ul>
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
          <button class="btn-danger" v-if="currentFilter === 'trash'" @click="emptyTrash" style="padding: 0.5rem 1rem; border-radius: 6px; font-weight: bold; margin-right: 15px;">
            <i class="fas fa-trash-alt" style="margin-right: 5px;"></i> Empty Trash
          </button>
          
          <div class="search-box relative">
            <i class="fas fa-search"></i>
            <input type="text" placeholder="Search Drive..." v-model="searchQuery"/>
            
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
                  <select v-model="searchFilters.type" class="form-select-small">
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
                  <select v-model="searchFilters.size" class="form-select-small">
                    <option value="">Any Size</option>
                    <option value="small">&lt; 1 MB</option>
                    <option value="medium">1 MB - 100 MB</option>
                    <option value="large">&gt; 100 MB</option>
                  </select>
                </div>
                
                <div class="filter-group">
                  <label>Modified Date</label>
                  <select v-model="searchFilters.date" class="form-select-small">
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
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
            </button>
            <button :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'" title="List View">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
            </button>
          </div>
        </div>
      </header>
      <!-- Drive Content Array -->
      <div 
        class="nautilus-content" 
        @contextmenu.prevent="showContextMenu($event)" 
        @mousedown="startDragSelection"
        @dragover.prevent
        @drop.prevent="handleDriveDrop"
      >
        
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="view-grid">
          <div 
            v-for="item in currentFiles" 
            :key="item.id"
            class="grid-item"
            :class="{ selected: selectedFiles.includes(item.id) }"
            :data-file-id="item.id"
            draggable="true"
            @click.stop.prevent="handleItemClick(item, $event)"
            @dblclick="handleItemDoubleClick(item)"
            @contextmenu.stop.prevent="showItemContextMenu($event, item)"
            @dragstart="startItemDrag($event, item)"
          >
            <div class="item-icon-wrapper relative">
               <!-- FIXED: Added pdf group here -->
               <template v-if="['image', 'video', 'pdf'].includes(getFileTypeDetails(item.name).group) && !item.thumbnailError">
                 <img :src="getThumbnailUrl(item)" class="file-thumbnail-grid" @error="item.thumbnailError = true" />
               </template>
               <template v-else>
                 <i :class="['fas', item.type === 'folder' ? 'fa-folder folder-icon' : getFileIcon(item.name) + ' file-icon']"></i>
                 <span v-if="item.type !== 'folder' && getFileTypeDetails(item.name).ext" class="file-ext-badge">
                   {{ getFileTypeDetails(item.name).ext }}
                 </span>
               </template>
            </div>
            <div class="item-name">{{ item.name }}</div>
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
        <div v-else class="view-list">
          <div class="list-header">
            <div class="col-name">Name</div>
            <div class="col-owner">Owner</div>
            <div class="col-date">Modified</div>
            <div class="col-size">Size</div>
          </div>
          <div class="list-body">
            <div 
              v-for="item in currentFiles" 
              :key="item.id"
              class="list-row"
              :class="{ selected: selectedFiles.includes(item.id) }"
              :data-file-id="item.id"
              draggable="true"
              @click.stop.prevent="handleItemClick(item, $event)"
              @dblclick="handleItemDoubleClick(item)"
              @contextmenu.stop.prevent="showItemContextMenu($event, item)"
              @dragstart="startItemDrag($event, item)"
            >
              <div class="col-name">
                <div class="relative inline-block icon-container">
                  <template v-if="['image', 'video', 'pdf'].includes(getFileTypeDetails(item.name).group) && !item.thumbnailError">
                    <img :src="getThumbnailUrl(item)" class="file-thumbnail-list" @error="item.thumbnailError = true" />
                  </template>
                  <template v-else>
                    <i :class="['fas', item.type === 'folder' ? 'fa-folder folder-icon' : getFileIcon(item.name) + ' file-icon']"></i>
                    <span v-if="item.type !== 'folder' && getFileTypeDetails(item.name).ext" class="file-ext-badge-small">
                      {{ getFileTypeDetails(item.name).ext }}
                    </span>
                  </template>
                </div>
                <span>{{ item.name }}</span>
              </div>
              <div class="col-owner">{{ item.owner }}</div>
              <div class="col-date">{{ formatDate(item.modified) }}</div>
              <div class="col-size">{{ item.type === 'folder' ? '--' : formatSize(item.size) }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="currentFiles.length === 0" class="empty-state">
          <i :class="['fas', currentFilter === 'trash' ? 'fa-trash-empty' : currentFilter === 'starred' ? 'fa-star' : currentFilter === 'recent' ? 'fa-clock' : 'fa-folder-open', 'empty-icon']"></i>
          <h3>{{ currentFilter === 'trash' ? 'Trash is empty' : currentFilter === 'starred' ? 'No starred files' : currentFilter === 'recent' ? 'No recent files' : 'This folder is empty' }}</h3>
          <p v-if="!currentFilter">Drag files here or click "New / Upload" to add content.</p>
          <p v-else-if="currentFilter === 'trash'">Items moved to trash will appear here.</p>
          <p v-else-if="currentFilter === 'starred'">Star files and folders to easily find them later.</p>
          <p v-else-if="currentFilter === 'recent'">Your recently accessed files will appear here.</p>
        </div>
      </div>
    </main>
    <!-- Right Side Sidebar: Properties/Details Pane -->
    <aside class="nautilus-details glass-panel shadow-2xl" v-if="infoModal.visible && selectedItemDetails" v-click-outside="closeInfoModal" style="z-index: 1001;">
      <div class="details-header">
        <div class="preview-box flex items-center justify-center relative">
            <template v-if="['image', 'video', 'pdf'].includes(getFileTypeDetails(selectedItemDetails.name || selectedItemDetails.filename).group) && !selectedItemDetails.thumbnailError">
              <img :src="getThumbnailUrl(selectedItemDetails)" class="file-thumbnail-preview" @error="selectedItemDetails.thumbnailError = true" />
            </template>
            <template v-else>
              <i :class="['fas', selectedItemDetails.type === 'folder' ? 'fa-folder folder-icon' : getFileIcon(selectedItemDetails.name) + ' file-icon']" style="font-size: 4rem;"></i>
              <span v-if="selectedItemDetails.type !== 'folder' && getFileTypeDetails(selectedItemDetails.name).ext" class="file-ext-badge-preview">
                {{ getFileTypeDetails(selectedItemDetails.name).ext }}
              </span>
            </template>
        </div>
        <h3>{{ selectedItemDetails.name }}</h3>
      </div>
      
      <div class="details-body">
        <div class="detail-row">
          <span class="detail-label">Type</span>
          <span class="detail-value">{{ selectedItemDetails.type === 'folder' ? 'Folder' : 'File' }}</span>
        </div>
        <div class="detail-row" v-if="selectedItemDetails.type !== 'folder'">
          <span class="detail-label">Size</span>
          <span class="detail-value">{{ formatSize(selectedItemDetails.size) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Location</span>
          <span class="detail-value">{{ selectedItemDetails.path }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Owner</span>
          <span class="detail-value">{{ selectedItemDetails.owner }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Modified</span>
          <span class="detail-value">{{ formatDate(selectedItemDetails.modified) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Created</span>
          <span class="detail-value">{{ formatDate(selectedItemDetails.created) }}</span>
        </div>
      </div>
      
      <!-- Contextual actions -->
      <div class="details-actions">
         <button class="btn-action" v-if="selectedItemDetails.type === 'file'" @click="openFile(selectedItemDetails)">
           <i class="fas fa-eye"></i> View
         </button>
         <button class="btn-action" v-if="selectedItemDetails.type === 'file'" @click="downloadFile(selectedItemDetails)">
           <i class="fas fa-download"></i> Download
         </button>
         <button class="btn-action" @click="shareModal.visible = true; shareModal.item = selectedItemDetails">
           <i class="fas fa-share-alt"></i> Share
         </button>
         <button class="btn-action danger" @click="contextMenu.item = selectedItemDetails; deleteItem()">
           <i class="fas fa-trash"></i> Delete
         </button>
      </div>
    </aside>

    <!-- Context Menu -->
    <div 
      v-if="contextMenu.visible"
      class="context-menu glass-panel"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <template v-if="currentFilter === 'trash'">
         <div class="menu-item danger" v-if="!contextMenu.item && selectedFiles.length === 0" @click="emptyTrash">
            <i class="fas fa-times-circle"></i> Empty Trash
         </div>
         <div class="menu-item" v-if="contextMenu.item || selectedFiles.length > 0" @click="restoreSelection">
            <i class="fas fa-trash-restore"></i> Restore
         </div>
         <div class="menu-item danger" v-if="contextMenu.item || selectedFiles.length > 0" @click="deleteSelectionPermanently">
            <i class="fas fa-trash"></i> Delete Permanently
         </div>
      </template>

      <template v-else>
         <!-- bulk options if multiple items -->
         <template v-if="selectedFiles.length > 1">
            <div class="menu-item" @click="moveSelection">
              <i class="fas fa-arrows-alt"></i> Move to...
            </div>
            <div class="menu-item" @click="copySelection">
              <i class="fas fa-copy"></i> Copy to...
            </div>
            <div class="menu-item" @click="renameSelection">
              <i class="fas fa-edit"></i> Rename (Bulk)
            </div>
            <div class="menu-item" @click="createFolderWithSelection">
              <i class="fas fa-folder"></i> Group into Folder
            </div>
            <div class="menu-separator"></div>
            <div class="menu-item danger" @click="deleteSelection">
              <i class="fas fa-trash"></i> Move to Trash
            </div>
         </template>
         <!-- single item options -->
         <template v-else-if="contextMenu.item">
            <div class="menu-item" @click="moveSelection">
              <i class="fas fa-arrows-alt"></i> Move to...
            </div>
            <div class="menu-item" @click="copySelection">
              <i class="fas fa-copy"></i> Copy to...
            </div>
            <div class="menu-separator"></div>
            <div class="menu-item" @click="renameSelection">
              <i class="fas fa-edit"></i> Rename
            </div>
            <div v-if="contextMenu.item && contextMenu.item.type === 'folder'" class="menu-item" @click="downloadFolderZip(contextMenu.item)">
            <i class="fas fa-file-archive"></i> Download as Zip
          </div>
            <div class="menu-item" @click="toggleStar(contextMenu.item)">
              <i :class="['fas', contextMenu.item.is_starred ? 'fa-star-o' : 'fa-star']"></i> {{ contextMenu.item.is_starred ? 'Unstar' : 'Star' }}
            </div>
            <div class="menu-item" @click="shareItem">
              <i class="fas fa-share-alt"></i> Share
            </div>
            <div class="menu-item" @click="showItemProperties(contextMenu.item)">
        <i class="fas fa-info-circle"></i> Properties
      </div>
            <div class="menu-item" v-if="contextMenu.item.type === 'file'" @click="openFile(contextMenu.item)">
               <i class="fas fa-eye"></i> View
            </div>
            <div class="menu-item" v-if="contextMenu.item.type === 'file'" @click="downloadSelectedItem">
              <i class="fas fa-download"></i> Download
            </div>
            <div class="menu-item" v-if="contextMenu.item.is_folder" @click="downloadFolderZip(contextMenu.item)">
               <i class="fas fa-file-archive"></i> Download Folder (.zip)
            </div>
            <div class="menu-separator"></div>
            <div class="menu-item danger" @click="deleteSelection">
              <i class="fas fa-trash"></i> Move to Trash
            </div>
         </template>
         <!-- blank space options -->
         <template v-else>
            <template v-if="!currentFilter">
              <div class="menu-item" @click.stop="createFolder">
                <i class="fas fa-folder-plus"></i> New Folder
              </div>
              <div class="menu-item" @click.stop="uploadFiles">
                <i class="fas fa-file-upload"></i> Upload Files
              </div>
            </template>
            <template v-else>
               <div class="menu-item disabled" style="opacity: 0.5; cursor: not-allowed;">
                 <i class="fas fa-ban"></i> Cannot upload here
               </div>
            </template>
         </template>
      </template>
    </div>

    <!-- Modals remain mostly identical logically -->
    <!-- Upload Modal -->
    <div v-show="uploadModal.visible" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal-content upload-modal">
        <div class="modal-header">
          <div class="modal-title-with-summary">
            <h2>Upload Files</h2>
            <span v-if="uploadTotalCount > 0" class="upload-summary-badge">
              {{ uploadTotalCount }} files ({{ formatSize(uploadTotalSize) }})
            </span>
          </div>
          <button class="close-btn" @click="closeUploadModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <input 
            type="file" 
            id="driveFileInput"
            ref="fileInput" 
            multiple 
            accept="*/*"
            class="hidden-input"
            @change="handleFileSelect"
          >
          <input 
            type="file" 
            id="driveFolderInput"
            ref="folderInput" 
            webkitdirectory 
            directory
            multiple 
            class="hidden-input"
            @change="handleFileSelect"
          >
          <label 
            for="driveFileInput"
            class="upload-area"
            :class="{ 'drag-over': uploadModal.dragOver }"
            @dragover.prevent="uploadModal.dragOver = true"
            @dragleave.prevent="uploadModal.dragOver = false"
            @drop.prevent="handleDrop"
          >
            <i class="fas fa-cloud-upload-alt upload-icon"></i>
            <p>Drag and drop files/folders here or click to browse</p>
          </label>
          <div v-if="uploadModal.files.length > 0" class="upload-list-area scrollable-list">
            <h4>Selected Files ({{ uploadModal.files.length }})</h4>
            <div class="list-container">
              <div v-for="(file, index) in uploadModal.files" :key="index" class="upload-item" :class="file.status">
                <div class="file-main-info">
                  <i :class="['fas', getFileIcon(file.name)]"></i>
                  <span class="file-name" :title="file.name">{{ file.name }}</span>
                </div>
                <div class="file-meta-info">
                  <span class="file-size">{{ formatSize(file.size || 0) }}</span>
                  <button class="remove-file-btn" @click="removeFileFromUpload(index)" v-if="!uploadStatus.active">
                    <i class="fas fa-times"></i>
                  </button>
                  <!-- Status badge -->
                  <span v-if="file.status === 'duplicate'" class="upload-status-badge duplicate">
                    DUP
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeUploadModal">Cancel</button>
          <button 
            class="btn-primary" 
            :disabled="uploadModal.files.length === 0"
            @click="startUpload"
          >
            Upload {{ uploadModal.files.length }} File{{ uploadModal.files.length !== 1 ? 's' : '' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Media Preview Modal -->
    <div v-if="mediaPreviewModal.visible" class="modal-overlay" @click.self="closeMediaPreview" style="z-index: 1005;">
      <div class="modal-content glass-panel media-preview-modal" :class="{ 'document-preview-modal': mediaPreviewModal.type === 'document' }">
        <div class="modal-header">
          <div class="modal-title-with-summary">
            <h2>{{ mediaPreviewModal.item?.name }}</h2>
            <span class="upload-summary-badge">{{ formatSize(mediaPreviewModal.item?.size) }}</span>
          </div>
          <div class="header-tools">
            <a :href="mediaUrl(mediaPreviewModal.item)" target="_blank" class="tool-btn" title="Open in New Tab">
              <i class="fas fa-external-link-alt"></i>
            </a>
            <button class="close-btn" @click="closeMediaPreview">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
        <div class="modal-body media-preview-body" ref="mediaBodyRef" 
             @wheel="handleMediaZoom" 
             @mousedown="startMediaPan" 
             @mousemove="panMedia" 
             @mouseup="endMediaPan" 
             @mouseleave="endMediaPan">
             
          <!-- Image Viewer -->
          <img v-if="mediaPreviewModal.type === 'image'" 
               :src="mediaUrl(mediaPreviewModal.item)" 
               class="media-preview-content draggable-media" 
               :style="{ transform: `translate(${mediaPan.x}px, ${mediaPan.y}px) scale(${mediaZoom})` }"
               draggable="false" />
               
          <!-- Video Player -->
          <video v-else-if="mediaPreviewModal.type === 'video'" 
                 :src="mediaUrl(mediaPreviewModal.item)" 
                 controls 
                 autoplay
                 class="media-preview-content" 
                 style="width: 100%; height: 100%; object-fit: contain;"></video>
                 
          <!-- Audio Player -->
          <audio v-else-if="mediaPreviewModal.type === 'audio'"
                 :src="mediaUrl(mediaPreviewModal.item)"
                 controls
                 autoplay
                 class="media-preview-content"
                 style="width: 100%;"></audio>
                 
          <!-- Document / Fallback iframe -->
          <iframe v-else-if="mediaPreviewModal.type === 'document'" 
                  :src="mediaUrl(mediaPreviewModal.item, true)" 
                  class="media-preview-content"
                  style="width: 100%; height: 100%; border: none; background: #fff;"></iframe>
                  
          <!-- Unsupported Type -->
          <div v-else class="media-unsupported">
            <i class="fas fa-file-alt" style="font-size: 4rem; margin-bottom: 1rem;"></i>
            <p>Preview not available for this file type.</p>
            <a :href="mediaUrl(mediaPreviewModal.item)" target="_blank" class="btn-primary" style="margin-top: 1rem; text-decoration: none; display: inline-block;">Download to View</a>
          </div>
        </div>
      </div>
    </div>

    <!-- Share Modal -->
    <div v-if="shareModal.visible" class="modal-overlay" @click.self="closeShareModal" style="z-index: 1002;">
      <div class="modal-content glass-panel share-modal-box">
        <div class="modal-header">
          <h2>Share "{{ shareModal.item?.name || shareModal.item?.filename }}"</h2>
          <button class="close-btn" @click="closeShareModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body form-grid">
          <div class="form-group">
            <label>Access Level</label>
            <select class="form-select" v-model="shareModal.accessLevel">
              <option value="private">Private (Only you)</option>
              <option value="account">Specific Account</option>
              <option value="link">Anyone with link</option>
            </select>
          </div>
          
          <div class="form-group" v-if="shareModal.accessLevel !== 'private'">
            <label>Permission Level</label>
            <select class="form-select" v-model="shareModal.permissionLevel">
              <option value="visitor">Visitor (View Only, NO Download)</option>
              <option value="viewer">Viewer (View & Download)</option>
              <option value="commenter">Commenter (View, Download & Comment)</option>
              <option value="editor">Editor (Full Access)</option>
            </select>
            <p class="text-xs text-secondary mt-1" v-if="shareModal.permissionLevel === 'visitor'">
              <i class="fas fa-shield-alt"></i> Anti-screenshot & download protection enabled.
            </p>
          </div>
          
          <div class="form-group" v-if="shareModal.accessLevel === 'account'">
            <label>Target User</label>
            <input type="text" class="form-input" v-model="shareModal.targetUser" placeholder="Enter exact username..." />
          </div>
          
          <div class="toggle-group" v-if="shareModal.accessLevel === 'link'">
            <label class="toggle-switch">
              <input type="checkbox" v-model="shareModal.encrypted">
              <span class="toggle-slider"></span>
            </label>
            <span class="toggle-description">Encrypt with password</span>
          </div>

          <div class="link-display" v-if="shareModal.generatedLink">
            <input type="text" readonly :value="shareModal.generatedLink" class="form-control">
            <button class="btn-secondary" @click="copyLink">
              <i class="fas fa-copy"></i> Copy
            </button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeShareModal">Cancel</button>
          <button class="btn-primary" @click="saveShareSettings">Save Settings</button>
        </div>
      </div>
    </div>
    <!-- Properties/Info Modal (Legacy Fallback) -->
    <div v-if="infoModal.visible" class="modal-overlay" @click.self="closeInfoModal">
      <div class="modal-content glass-panel">
         <div class="modal-header">
           <h2>Properties</h2>
           <button class="close-btn" @click="closeInfoModal"><i class="fas fa-times"></i></button>
         </div>
         <div class="modal-body">
           <p>This information is now available in the Right Sidebar pane when a file is selected.</p>
         </div>
         <div class="modal-footer">
           <button class="btn-primary" @click="closeInfoModal">Close</button>
         </div>
      </div>
    </div>
      <!-- Prompt Modal -->
      <transition name="modal-fade">
        <div class="modal-overlay" v-if="promptModal.visible">
          <div class="modal-content glass-panel" v-click-outside="cancelPrompt">
            <div class="modal-header">
              <h3>{{ promptModal.title }}</h3>
              <button class="close-btn" @click="cancelPrompt">
                <i class="fas fa-times"></i>
              </button>
            </div>
            
            <div class="modal-body">
              <div class="form-group">
                <label>{{ promptModal.label }}</label>
                <input 
                  type="text" 
                  v-model="promptModal.value"
                  :placeholder="promptModal.placeholder"
                  @keyup.enter="confirmPrompt"
                  autofocus
                />
              </div>
            </div>
            
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="cancelPrompt">Cancel</button>
              <button class="btn btn-primary" @click="confirmPrompt">Submit</button>
            </div>
          </div>
        </div>
      </transition>
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
    <!-- Properties Modal (Hover Window) -->
    <div v-if="propertyModal.visible" class="modal-overlay" @click.self="propertyModal.visible = false" style="z-index: 1006;">
      <div class="modal-content glass-panel property-modal-box">
        <div class="modal-header">
          <h2><i class="fas fa-info-circle text-gold mr-2"></i> Properties</h2>
          <button class="close-btn" @click="propertyModal.visible = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body properties-grid">
          <div class="detail-row">
            <span class="label">Name</span>
            <span class="value">{{ propertyModal.item?.name }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Type</span>
            <span class="value capitalize">{{ propertyModal.item?.is_folder ? 'Folder' : (propertyModal.item?.mime_type || 'File') }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Size</span>
            <span class="value">{{ formatSize(propertyModal.item?.size) }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Location</span>
            <span class="value">{{ propertyModal.item?.folder_path }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Access</span>
            <span class="value capitalize">
              <i :class="getAccessIcon(propertyModal.item?.access_level)" class="mr-1"></i>
              {{ formatAccessLevel(propertyModal.item?.access_level) }}
            </span>
          </div>
          <div class="detail-row">
            <span class="label">Created</span>
            <span class="value">{{ formatDate(propertyModal.item?.created_at) }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Modified</span>
            <span class="value">{{ formatDate(propertyModal.item?.modified_at) }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="propertyModal.visible = false">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { showSuccess, showError, showConfirm } from '@/utils/notification'
import { apiGet, apiPost, apiUpload, apiDelete } from '@/utils/api'
import { useSystemStore } from '@/stores/systemStore'
import { useUserStore } from '@/stores/userStore'

const systemStore = useSystemStore()
const userStore = useUserStore()

// Reactive state
const viewMode = ref('grid')
const selectedFiles = ref([])
const currentPath = ref('/')
const currentFilter = ref(null) 
const showFilters = ref(false)
const searchQuery = ref('')
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

const promptModal = reactive({
  visible: false,
  title: '',
  label: '',
  value: '',
  placeholder: '',
  resolve: null
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

const fileInput = ref(null)
const folderInput = ref(null)

const uploadFolder = () => {
  if (folderInput.value) {
    folderInput.value.click()
  }
}

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

const uploadTotalCount = computed(() => uploadModal.files ? uploadModal.files.length : 0);
const uploadTotalSize = computed(() => {
    if (!uploadModal.files) return 0;
    return uploadModal.files.reduce((acc, f) => acc + (f.size || 0), 0);
});

const clearFilters = () => {
  searchFilters.type = ''
  searchFilters.size = ''
  searchFilters.date = ''
  searchQuery.value = ''
}
const selectedItemDetails = computed(() => {
   if (selectedFiles.value.length === 1) {
       return currentFiles.value.find(f => f.id === selectedFiles.value[0]);
   }
   return null;
});
const breadcrumb = ref(['Drive'])

// Context menu
const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  item: null
})

// Upload modal
const showDropdown = ref({
  upload: false,
  create: false
})

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
  dragOver: false,
  files: []
})

// Share modal
const shareModal = reactive({
  visible: false,
  item: null,
  accessLevel: 'private',
  permissionLevel: 'viewer',
  usernames: [],
  password: '',
  expiresHours: null,
  loading: false
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

// Media Preview Modal
const mediaPreviewModal = reactive({
  visible: false,
  item: null,
  type: ''
})

const mediaZoom = ref(1)
const mediaPan = reactive({ x: 0, y: 0 })
const isPanning = ref(false)
const panStart = reactive({ x: 0, y: 0 })

const accountsList = ref([]) 

const fetchAccounts = async () => {
  try {
    const data = await apiGet('/user/list')
    accountsList.value = data || []
  } catch (err) {
    console.error('Failed to parse user accounts for share modal', err)
  }
}

// Info modal
const infoModal = reactive({
  visible: false,
  item: null
})

// User role and hierarchy
const userRole = ref('USER') 
const userId = ref('') 
const userQuota = ref(30000000000) 
const usedQuota = ref(0)
const additionalQuota = ref(0)
const quotaPercentage = ref(0)

// File system data
const fileSystem = ref([])
const isLoading = ref(true)

const setCurrentFilter = (filter) => {
  currentFilter.value = filter
  currentPath.value = '/'
  breadcrumb.value = ['Drive']
  loadFiles('/', filter)
}

const loadFiles = async (folderPath = currentPath.value, filterMode = null) => {
  try {
    isLoading.value = true
    let endpoint = `/drive/files?folder_path=${encodeURIComponent(folderPath)}`
    
    if (filterMode === 'recent' || filterMode === 'starred' || filterMode === 'trash') {
      endpoint = `/drive/files?view_mode=${filterMode}`
    }
    
    const response = await apiGet(endpoint)
    
    fileSystem.value = response.files.map(file => {
      // PRE-CALCULATE common metadata for performance
      const { group, ext } = getFileTypeDetails(file.filename)
      return {
        id: file.id,
        name: file.filename,
        type: file.is_folder ? 'folder' : 'file',
        group, // optimized
        ext,   // optimized
        mime_type: file.mime_type || '', 
        size: file.file_size || 0,
        created: file.created_at,
        modified: file.modified_at,
        owner: file.owner.display_name || file.owner.username,
        ownerRole: file.owner.role || 'USER', 
        path: file.file_path || (file.folder_path.endsWith('/') ? file.folder_path + file.filename : file.folder_path + '/' + file.filename),
        is_starred: file.is_starred || false,
        is_trashed: file.is_deleted || file.is_trashed || false, 
        labels: file.labels || [],
        thumbnailError: false
      }
    })
    
    if (response.quota) {
      usedQuota.value = response.quota.used_space
      userQuota.value = response.quota.total_quota
      additionalQuota.value = response.quota.additional_quota
      quotaPercentage.value = response.quota.usage_percentage
    }
  } catch (err) {
    console.error('Error fetching drive files:', err)
    showError('Failed to load drive files')
  } finally {
    isLoading.value = false
  }
}
// Initial component API bindings
onMounted(() => {
  const userData = localStorage.getItem('user')
  if (userData) {
    try {
      const user = JSON.parse(userData)
      userRole.value = user.role || 'USER'
      userId.value = user.id || ''
    } catch (e) {
      console.error('Error parsing user data in Drive:', e)
    }
  }
  loadFiles()
  fetchAccounts()
  document.addEventListener('click', hideContextMenu)
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('click', hideContextMenu)
  document.removeEventListener('keydown', handleKeyDown)
})

// Selection state
const selectionBox = reactive({
  visible: false,
  startX: 0,
  startY: 0,
  endX: 0,
  endY: 0
})

// Computed properties
const currentFiles = computed(() => {
  let files = fileSystem.value
  
  if (currentFilter.value !== 'trash') {
    files = files.filter(f => !f.is_trashed)
  }
  
  if (userRole.value === 'USER') {
    files = files.filter(file => 
      file.ownerRole === 'USER' || 
      (file.ownerRole === 'AD' && file.accessLevel === 'account') ||
      (file.ownerRole === 'AD' && file.accessLevel === 'link')
    )
  } else if (userRole.value === 'AD') {
    files = files.filter(file => 
      file.ownerRole === 'AD' || 
      file.ownerRole === 'USER' ||
      (file.ownerRole === 'OP' && file.accessLevel === 'account') ||
      (file.ownerRole === 'OP' && file.accessLevel === 'link')
    )
  }
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    files = files.filter(file => file.name.toLowerCase().includes(q))
  }
  
  if (searchFilters.type) {
    if (searchFilters.type === 'folder') {
      files = files.filter(f => f.type === 'folder')
    } else {
      files = files.filter(f => {
        if (f.type === 'folder') return false
        const ext = f.ext
        switch(searchFilters.type) {
          case 'document': return ['pdf', 'doc', 'docx', 'txt', 'rtf', 'csv', 'xls', 'xlsx'].includes(ext)
          case 'image': return ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(ext)
          case 'video': return ['mp4', 'avi', 'mkv', 'webm', 'mov'].includes(ext)
          case 'audio': return ['mp3', 'wav', 'ogg', 'flac'].includes(ext)
          case 'archive': return ['zip', 'rar', 'tar', 'gz', '7z'].includes(ext)
          case 'code': return ['js', 'py', 'html', 'css', 'json', 'vue', 'cpp', 'c', 'java'].includes(ext)
          default: return true
        }
      })
    }
  }
  
  if (searchFilters.size) {
    files = files.filter(f => {
      if (f.type === 'folder') return true 
      const sizeMB = f.size / (1024 * 1024)
      if (searchFilters.size === 'small') return sizeMB < 1
      if (searchFilters.size === 'medium') return sizeMB >= 1 && sizeMB <= 100
      if (searchFilters.size === 'large') return sizeMB > 100
      return true
    })
  }
  
  if (searchFilters.date) {
    const now = new Date()
    files = files.filter(f => {
      const targetDate = f.modified ? new Date(f.modified) : new Date(f.created)
      if (!targetDate || isNaN(targetDate.getTime())) return true
      
      const diffTime = Math.abs(now - targetDate)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (searchFilters.date === 'today') return diffDays <= 1
      if (searchFilters.date === 'week') return diffDays <= 7
      if (searchFilters.date === 'month') return diffDays <= 30
      if (searchFilters.date === 'year') return diffDays <= 365
      return true
    })
  }
  
  return files
})
const getFileTypeDetails = (fileName) => {
  if (!fileName || typeof fileName !== 'string') return { group: 'other', ext: '' }
  const parts = fileName.split('.')
  if (parts.length === 1) return { group: 'other', ext: '' }
  const ext = parts.pop().toLowerCase()
  
  let group = 'other'
  if (['pdf'].includes(ext)) group = 'pdf'
  else if (['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'].includes(ext)) group = 'document'
  else if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(ext)) group = 'image'
  else if (['mp4', 'avi', 'mkv', 'mov', 'webm'].includes(ext)) group = 'video'
  else if (['mp3', 'wav', 'ogg', 'flac'].includes(ext)) group = 'audio'
  else if (['zip', 'rar', 'tar', 'gz', '7z'].includes(ext)) group = 'archive'
  else if (['py', 'js', 'html', 'css', 'vue', 'json'].includes(ext)) group = 'code'

  return { group, ext }
}

const getFileIcon = (fileName) => {
  if (!fileName || typeof fileName !== 'string') return 'fa-file'
  
  const parts = fileName.split('.')
  if (parts.length === 1) return 'fa-file'
  
  const extension = parts.pop().toLowerCase()
  const iconMap = {
    pdf: 'fa-file-pdf',
    doc: 'fa-file-word',
    docx: 'fa-file-word',
    xls: 'fa-file-excel',
    xlsx: 'fa-file-excel',
    ppt: 'fa-file-powerpoint',
    pptx: 'fa-file-powerpoint',
    jpg: 'fa-file-image',
    jpeg: 'fa-file-image',
    png: 'fa-file-image',
    gif: 'fa-file-image',
    svg: 'fa-file-image',
    mp4: 'fa-file-video',
    avi: 'fa-file-video',
    mkv: 'fa-file-video',
    mp3: 'fa-file-audio',
    wav: 'fa-file-audio',
    zip: 'fa-file-archive',
    rar: 'fa-file-archive',
    tar: 'fa-file-archive',
    gz: 'fa-file-archive',
    txt: 'fa-file-alt',
    csv: 'fa-file-csv',
    py: 'fa-file-code',
    js: 'fa-file-code',
    html: 'fa-file-code',
    css: 'fa-file-code'
  }
  
  return iconMap[extension] || 'fa-file'
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getThumbnailUrl = (item) => {
  const token = localStorage.getItem('token')
  return `/api/drive/thumbnail/${item.id}?token=${token}`
}

const mediaUrl = (item, preview = false) => {
  if (!item) return ''
  const token = localStorage.getItem('token')
  let url = `/api/drive/download/${item.id}?token=${token}`
  if (preview) url += '&preview=true'
  return url
}

const downloadFile = (item) => {
  if (item.type === 'folder') {
    showError('Cannot download a folder directly')
    return
  }
  const url = mediaUrl(item)
  const a = document.createElement('a')
  a.href = url
  a.download = item.name
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

const downloadSelectedItem = () => {
  if (contextMenu.item) {
    downloadFile(contextMenu.item)
  }
  hideContextMenu()
}
// Media preview controls
const closeMediaPreview = () => {
  mediaPreviewModal.visible = false
  mediaPreviewModal.item = null
  mediaPreviewModal.type = ''
  mediaZoom.value = 1
  mediaPan.x = 0
  mediaPan.y = 0
  isPanning.value = false
}

const handleMediaZoom = (event) => {
  if (mediaPreviewModal.type !== 'image') return
  event.preventDefault()
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  mediaZoom.value = Math.max(0.5, Math.min(5, mediaZoom.value + delta))
}

const startMediaPan = (event) => {
  if (mediaPreviewModal.type !== 'image') return
  isPanning.value = true
  panStart.x = event.clientX - mediaPan.x
  panStart.y = event.clientY - mediaPan.y
}

const panMedia = (event) => {
  if (!isPanning.value) return
  mediaPan.x = event.clientX - panStart.x
  mediaPan.y = event.clientY - panStart.y
}

const endMediaPan = () => {
  isPanning.value = false
}

const selectFile = (item, multiSelect = false) => {
  if (multiSelect) {
    const index = selectedFiles.value.indexOf(item.id)
    if (index > -1) {
      selectedFiles.value.splice(index, 1)
    } else {
      selectedFiles.value.push(item.id)
    }
  } else {
    selectedFiles.value = [item.id]
  }
}

const handleItemClick = (item, event) => {
  const isMulti = event.ctrlKey || event.metaKey
  selectFile(item, isMulti)
  if (userStore.isSingleClickOpen && !isMulti) {
    openFile(item)
  }
}

const handleItemDoubleClick = (item) => {
  if (!userStore.isSingleClickOpen) {
    openFile(item)
  }
}

let dragContainer = null

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
    type: 'drive-items',
    items: selectedFiles.value
  }
  event.dataTransfer.setData('text/plain', JSON.stringify(dragData))
  event.dataTransfer.effectAllowed = 'move'
}

const handleDriveDrop = async (event) => {
  try {
    const dataString = event.dataTransfer.getData('text/plain')
    if (dataString) {
      const data = JSON.parse(dataString)
      if (data.type === 'drive-items') {
        const targetElement = event.target.closest('.grid-item, .list-row')
        if (targetElement) {
          const targetId = targetElement.getAttribute('data-file-id')
          const targetObj = currentFiles.value.find(f => f.id === targetId)
          if (targetObj && targetObj.type === 'folder' && !data.items.includes(targetId)) {
            for (let id of data.items) {
               await apiPost('/drive/move', { file_id: id, target_folder: targetObj.path })
            }
            showSuccess(`Moved ${data.items.length} items to ${targetObj.name}`)
            selectedFiles.value = []
            loadFiles(currentPath.value, currentFilter.value)
          }
        }
        return 
      }
    }
  } catch (e) {}
  
  const files = Array.from(event.dataTransfer.files)
  if (files.length > 0) {
    uploadModal.dragOver = false
    uploadModal.files = files.map(file => ({
      originalFile: file,
      name: file.name,
      size: file.size,
      progress: 0
    }))
    uploadModal.visible = true
  }
}

const openFile = (item) => {
  if (item.type === 'folder') {
    navigateToFolder(item)
  } else {
    const group = getFileTypeDetails(item.name).group
    const ext = item.ext
    
    mediaPreviewModal.item = item
    
    if (group === 'image') mediaPreviewModal.type = 'image'
    else if (group === 'video') mediaPreviewModal.type = 'video'
    else if (group === 'audio') mediaPreviewModal.type = 'audio'
    else if (['pdf', 'txt', 'csv', 'md'].includes(ext)) mediaPreviewModal.type = 'document'
    else mediaPreviewModal.type = 'other'
    
    mediaZoom.value = 1
    mediaPan.x = 0
    mediaPan.y = 0
    
    mediaPreviewModal.visible = true
  }
}    

const navigateToFolder = (folder) => {
  currentPath.value = folder.path
  const pathParts = folder.path.split('/').filter(p => p)
  breadcrumb.value = ['Drive', ...pathParts]
  loadFiles(folder.path)
}

const navigateToBreadcrumb = (index) => {
  if (index === 0) {
    currentPath.value = '/'
    breadcrumb.value = ['Drive']
    loadFiles('/')
  } else {
    const newPath = '/' + breadcrumb.value.slice(1, index + 1).join('/')
    currentPath.value = newPath
    breadcrumb.value = breadcrumb.value.slice(0, index + 1)
    loadFiles(newPath)
  }
}
const createFolder = async () => {
  hideContextMenu()
  const name = await showPrompt('Create Folder', 'Enter folder name:', '', 'New Folder')
  if (name) {
    try {
      await apiPost('/drive/folder', {
        name: name,
        parent_folder: currentPath.value === '/' ? '/' : currentPath.value,
        description: ''
      })
      showSuccess(`Folder "${name}" created`)
      loadFiles(currentPath.value)
    } catch (err) {
      console.error(err)
      showError('Failed to create folder')
    }
  }
}

const uploadFiles = () => {
  uploadModal.visible = true
  hideContextMenu()
}

const removeFileFromUpload = (index) => {
  if (uploadStatus.active) return
  uploadModal.files.splice(index, 1)
}

const openUploadModal = (folderOnly = false) => {
  uploadModal.visible = false
  uploadModal.files = []
  uploadModal.dragOver = false
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  uploadModal.files = files.map(file => {
    // webkitRelativePath is available when selecting a folder via <input webkitdirectory>
    // It looks like "folder/subfolder/file.ext"
    // We want the directory part: "folder/subfolder"
    const relPath = file.webkitRelativePath ? file.webkitRelativePath.split('/').slice(0, -1).join('/') : ''
    
    return {
      originalFile: file,
      name: file.name,
      size: file.size,
      relPath: relPath, // Store relative path for backend
      progress: 0,
      status: 'pending'
    }
  })
  uploadModal.visible = true
}

const handleDrop = async (event) => {
  event.preventDefault()
  uploadModal.dragOver = false
  
  const items = event.dataTransfer.items
  if (!items) return
  
  const files = []
  
  // Recursively traverse dropped items
  const traverseFileTree = async (entry, path = '') => {
    if (entry.isFile) {
      const file = await new Promise((resolve) => entry.file(resolve))
      files.push({
        originalFile: file,
        name: file.name,
        size: file.size,
        relPath: path,
        progress: 0,
        status: 'pending'
      })
    } else if (entry.isDirectory) {
      const dirReader = entry.createReader()
      const readAllEntries = async () => {
        let allEntries = []
        let readNext = async () => {
          const entries = await new Promise((resolve) => dirReader.readEntries(resolve))
          if (entries.length > 0) {
            allEntries = allEntries.concat(entries)
            await readNext()
          }
        }
        await readNext()
        return allEntries
      }
      
      const entries = await readAllEntries()
      for (const childEntry of entries) {
        await traverseFileTree(childEntry, path ? `${path}/${entry.name}` : entry.name)
      }
    }
  }
  
  const promises = []
  for (let i = 0; i < items.length; i++) {
    const entry = items[i].webkitGetAsEntry()
    if (entry) {
      promises.push(traverseFileTree(entry))
    }
  }
  
  await Promise.all(promises)
  
  if (files.length > 0) {
    uploadModal.files = files
    uploadModal.visible = true
  }
}

const startUpload = async () => {
  if (uploadModal.files.length === 0) return
  
  // Set global upload status
  uploadStatus.active = true
  uploadStatus.minimized = false
  uploadStatus.expanded = true
  
  // Move files to global tracker with initial states
  const newUploads = uploadModal.files.map(f => ({
    name: f.name,
    size: f.size,
    progress: 0,
    status: 'uploading',
    icon: getFileIcon(f.name),
    originalFile: f.originalFile,
    relPath: f.relPath
  }))
  
  uploadStatus.files = [...newUploads, ...uploadStatus.files]
  
  // Close the selection modal
  closeUploadModal()
  
  // Process each file in the background
  for (let fileObj of newUploads) {
    const formData = new FormData()
    formData.append('file', fileObj.originalFile)
    
    let targetFolder = currentPath.value === '/' ? '' : currentPath.value
    if (fileObj.relPath) {
      targetFolder = targetFolder ? `${targetFolder}/${fileObj.relPath}` : `/${fileObj.relPath}`
    }
    if (!targetFolder) targetFolder = '/'
    
    formData.append('folder_path', targetFolder)
    
    try {
      await apiUpload('/drive/upload', formData, (progress) => {
        fileObj.progress = progress
      })
      fileObj.progress = 100
      fileObj.status = 'done'
      uploadStatus.successCount++
    } catch (err) {
      console.error('Upload Error Details:', err, err.status, err.message)
      if (err.status === 409 || (err.message && err.message.includes('already exists'))) {
        fileObj.status = 'duplicate'
        fileObj.progress = 0
      } else {
        fileObj.status = 'error'
        fileObj.progress = 0
        uploadStatus.errorCount++
        console.error('Upload Error:', err)
      }
    }
  }

  // Reload files once all in this batch are done
  await loadFiles(currentPath.value, currentFilter.value)
}

const clearCompletedUploads = () => {
  uploadStatus.files = uploadStatus.files.filter(f => f.status === 'uploading')
  if (uploadStatus.files.length === 0) {
    uploadStatus.active = false
    uploadStatus.successCount = 0
    uploadStatus.errorCount = 0
  }
}
const renameSelection = async () => {
  hideContextMenu();
  const items = selectedFiles.value.length > 0 ? selectedFiles.value : (contextMenu.item ? [contextMenu.item.id] : []);
  if (items.length === 0) return;

  if (items.length === 1) {
     const itemObj = currentFiles.value.find(f => f.id === items[0]);
     if (!itemObj) return;
     const newName = await showPrompt('Rename Item', 'Enter new name:', itemObj.name);
     if (newName && newName !== itemObj.name) {
       try {
         await apiPost('/drive/move', { file_id: items[0], target_folder: currentPath.value === '/' ? '/' : currentPath.value, new_name: newName });
         showSuccess(`Renamed to "${newName}"`);
         loadFiles(currentPath.value, currentFilter.value);
       } catch(err) { showError('Failed to rename item'); }
     }
  } else {
     const baseName = await showPrompt('Bulk Rename', `Enter base name for ${items.length} items:`, '', 'e.g. Vacation_Photo');
     if (baseName) {
       try {
         for (let i = 0; i < items.length; i++) {
            const itemObj = currentFiles.value.find(f => f.id === items[i]);
            const ext = itemObj.ext ? '.' + itemObj.ext : '';
            const newName = `${baseName} (${i+1})${ext}`;
            await apiPost('/drive/move', { file_id: items[i], target_folder: currentPath.value === '/' ? '/' : currentPath.value, new_name: newName });
         }
         showSuccess(`Bulk renamed ${items.length} items`);
         selectedFiles.value = [];
         loadFiles(currentPath.value, currentFilter.value);
       } catch(err) { showError('Failed to bulk rename'); }
     }
  }
}

const moveSelection = async () => {
   hideContextMenu();
   const items = selectedFiles.value.length > 0 ? selectedFiles.value : (contextMenu.item ? [contextMenu.item.id] : []);
   if (items.length === 0) return;
   
   const target = await showPrompt('Move Items', 'Enter target folder path (e.g. /Documents):', '/');
   if (target) {
     try {
       for (let id of items) {
         await apiPost('/drive/move', { file_id: id, target_folder: target });
       }
       showSuccess(`Moved ${items.length} item(s) to ${target}`);
       selectedFiles.value = [];
       loadFiles(currentPath.value, currentFilter.value);
     } catch(err) { showError('Failed to move items'); }
    }
}

const copySelection = async () => {
   hideContextMenu();
   const items = selectedFiles.value.length > 0 ? selectedFiles.value : (contextMenu.item ? [contextMenu.item.id] : []);
   if (items.length === 0) return;
   
   const target = await showPrompt('Copy Items', 'Enter target folder path for copy (e.g. /Documents):', currentPath.value);
   if (target) {
     try {
       for (let id of items) {
         await apiPost('/drive/copy', { file_id: id, target_folder: target });
       }
       showSuccess(`Copied ${items.length} item(s) to ${target}`);
       selectedFiles.value = [];
       loadFiles(currentPath.value, currentFilter.value);
     } catch(err) { showError('Failed to copy items'); }
    }
}

const createFolderWithSelection = async () => {
   hideContextMenu();
   const items = selectedFiles.value.length > 0 ? selectedFiles.value : (contextMenu.item ? [contextMenu.item.id] : []);
   if (items.length === 0) return;
   
   const name = await showPrompt('Group into Folder', 'Enter folder name for the selection:', '', 'New Folder');
   if (name) {
      try {
        await apiPost('/drive/folder', {
          name: name,
          parent_folder: currentPath.value === '/' ? '/' : currentPath.value,
          description: ''
        });
        
        const targetFolderPath = currentPath.value === '/' ? `/${name}` : `${currentPath.value}/${name}`;
        for (let id of items) {
           await apiPost('/drive/move', { file_id: id, target_folder: targetFolderPath });
        }
        
        showSuccess(`Grouped ${items.length} items into "${name}"`);
        selectedFiles.value = [];
        loadFiles(currentPath.value, currentFilter.value);
      } catch(err) {
        showError('Failed to group items');
      }
   }
}

const shareItem = async () => {
  if (contextMenu.item) {
    const originalItem = contextMenu.item
    hideContextMenu()
    
    try {
      // Fetch latest metadata to ensure share state is accurate
      const item = await apiGet(`/drive/file/${originalItem.id}`)
      
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
      shareModal.encrypted = item.has_password || false
      shareModal.generatedLink = item.share_link_id ? `${window.location.origin}/s/${item.share_link_id}` : ''
      shareModal.visible = true
      
      if (accountsList.value.length === 0) fetchAccounts()
    } catch (err) {
      showError('Failed to fetch share settings')
    }
  } else {
    hideContextMenu()
  }
}

const closeShareModal = () => {
  shareModal.visible = false
  shareModal.item = null
  shareModal.generatedLink = ''
  shareModal.targetUser = ''
}

const saveShareSettings = async () => {
  try {
    const payload = {
      file_id: shareModal.item.id,
      access_level: shareModal.accessLevel === 'private' ? 'only_me' : shareModal.accessLevel,
      permission_level: shareModal.permissionLevel,
      share_type: 'read'
    }
    
    if (shareModal.accessLevel === 'account' && shareModal.targetUser) {
       payload.access_level = 'specific_users';
       payload.specific_usernames = [shareModal.targetUser];
    } else if (shareModal.accessLevel === 'link') {
       payload.access_level = 'public';
       if (shareModal.encrypted) {
          const pass = await showPrompt('Password Protect Link', 'Enter a password for this link:', '');
          if (!pass) return; 
          payload.share_password = pass;
       }
    }
    
    const res = await apiPost('/drive/share', payload)

    if (res.share_link) {
      shareModal.generatedLink = res.share_link;
      showSuccess('Public link successfully generated!');
    } else {
      showSuccess('Share settings saved successfully');
      closeShareModal();
    }
  } catch (err) {
    showError(err.message || 'Failed to update share configurations')
  }
}

const downloadFolderZip = (item) => {
  window.open(`/api/drive/zip/${item.id}`)
  hideContextMenu()
}

const copyLink = () => {
  if (shareModal.generatedLink) {
    navigator.clipboard.writeText(shareModal.generatedLink)
    showSuccess('Link copied to clipboard')
  }
}
const showInfo = () => {
  if (contextMenu.item) {
    infoModal.item = contextMenu.item
    selectedFiles.value = [contextMenu.item.id]
    infoModal.visible = true
  }
  hideContextMenu()
}

const closeInfoModal = () => {
  infoModal.visible = false
}

const deleteSelection = async () => {
  const items = selectedFiles.value.length > 0 ? selectedFiles.value : (contextMenu.item ? [contextMenu.item.id] : []);
  if (items.length === 0) return;
  
  const isHardDelete = currentFilter.value === 'trash';
  if (isHardDelete) { return deleteSelectionPermanently(); }

  const confirmed = await showConfirm(`Are you sure you want to move ${items.length} item(s) to Trash?`, 'Move to Trash');
  
  if (confirmed) {
    try {
      for (let id of items) {
        await apiDelete(`/drive/file/${id}`);
      }
      showSuccess(`Moved ${items.length} item(s) to Trash`);
      selectedFiles.value = [];
      loadFiles(currentPath.value, currentFilter.value);
    } catch (err) {
      console.error('Delete Error:', err);
      showError('Failed to delete files');
    }
  }
  hideContextMenu();
}

const deleteSelectionPermanently = async () => {
  const items = selectedFiles.value.length > 0 ? selectedFiles.value : (contextMenu.item ? [contextMenu.item.id] : []);
  if (items.length === 0) return;
  
  const confirmed = await showConfirm(
    `Are you sure you want to PERMANENTLY delete ${items.length} item(s)? This cannot be undone.`, 
    'Delete Permanently'
  );
  
  if (confirmed) {
    try {
      for (let id of items) {
         await apiDelete(`/drive/trash/${id}`);
      }
      showSuccess(`Permanently deleted ${items.length} item(s)`);
      selectedFiles.value = [];
      loadFiles(currentPath.value, currentFilter.value);
      syncQuota();
    } catch(err) {
      showError('Failed to delete items permanently');
    }
  }
  hideContextMenu();
}

const toggleStar = async (item) => {
  try {
    const res = await apiPost(`/drive/star/${item.id}`)
    showSuccess(res.message)
    item.is_starred = res.is_starred
  } catch(err) {
    showError('Failed to update star status')
  }
  hideContextMenu()
}

const restoreSelection = async () => {
  const items = selectedFiles.value.length > 0 ? selectedFiles.value : (contextMenu.item ? [contextMenu.item.id] : []);
  if (items.length === 0) return;
  
  try {
    for (let id of items) {
      await apiPost(`/drive/file/${id}/restore`);
    }
    showSuccess(`Restored ${items.length} item(s)`);
    selectedFiles.value = [];
    loadFiles(currentPath.value, currentFilter.value);
  } catch(err) {
    showError(err.message || 'Restore failed. Check quota limits.');
  }
  hideContextMenu();
}

const emptyTrash = async () => {
  const confirmed = await showConfirm(
    'Are you sure you want to empty the trash? All files will be permanently deleted.', 
    'Empty Trash'
  )
  
  if (confirmed) {
    try {
      const res = await apiDelete('/drive/trash')
      showSuccess(`Trash emptied. Deleted ${res.deleted_count} files.`)
      loadFiles('/', 'trash')
      syncQuota()
    } catch (err) {
      showError('Failed to empty trash')
    }
  }
  hideContextMenu()
}

const showContextMenu = (event) => {
  contextMenu.visible = true
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.item = null
}

const showItemContextMenu = (event, item) => {
  contextMenu.visible = true
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.item = item
}

const syncQuota = async () => {
  try {
    const res = await apiPost('/drive/quota/sync');
    usedQuota.value = res.used_space;
    userQuota.value = res.total_quota;
    quotaPercentage.value = res.usage_percentage;
    showSuccess('Quota recalculated successfully');
    await loadFiles(currentPath.value, currentFilter.value);
  } catch (err) {
    showError('Failed to recalculate quota');
  }
};

const hideContextMenu = () => {
  contextMenu.visible = false
}

const handleKeyDown = (e) => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;
  
  if (e.key === 'Escape') {
    selectedFiles.value = [];
    hideContextMenu();
    cancelPrompt();         
    closeUploadModal();
    closeShareModal();
    closeInfoModal();
    closeMediaPreview();    
  } else if (e.key === 'Delete') {
    if (e.shiftKey) {
      if (selectedFiles.value.length > 0 || contextMenu.item) {
        deleteSelectionPermanently();
      }
    } else {
      if (selectedFiles.value.length > 0 || contextMenu.item) {
        if (currentFilter.value === 'trash') {
          deleteSelectionPermanently();
        } else {
          deleteSelection();
        }
      }
    }
  } else if (e.key === 'Enter') {
    if (promptModal.visible && promptModal.resolve) {
      confirmPrompt();
    } else if (selectedFiles.value.length === 1 || contextMenu.item) {
      const target = contextMenu.item || currentFiles.value.find(f => f.id === selectedFiles.value[0]);
      if (target) {
        openFile(target);
      }
    }
  } else if (e.key === 'F2') {
    if (selectedFiles.value.length === 1 || contextMenu.item) {
      renameSelection();
    }
  } else if (e.ctrlKey && e.key === 'a') {
    e.preventDefault();
    selectedFiles.value = currentFiles.value.map(f => f.id);
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

</script>

<style scoped>
.nautilus-drive {
  display: flex;
  position: absolute;
  top: 70px;
  bottom: 0;
  left: 0;
  right: 0;
  height: auto;
  width: auto;
  background: transparent;
  overflow: hidden;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  gap: 1rem;
}

.glass-panel {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(10px);
}

.nautilus-sidebar {
  width: 250px;
  display: flex;
  flex-direction: column;
  padding: 1rem 0;
  border-radius: 12px;
  flex-shrink: 0;
  position: relative;
  z-index: 60;
}

.sidebar-header {
  padding: 0 1rem 1.5rem;
}

.create-btn {
  width: 100%;
  padding: 0.75rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 600;
  background: var(--primary-color);
  color: white;
  border: none;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.create-btn:hover {
  transform: translateY(-1px);
  background: var(--primary-hover);
}

.sidebar-quota {
  padding: 0 1.5rem 1.5rem;
  border-bottom: 1px solid var(--glass-border);
  margin-bottom: 1rem;
}

.quota-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quota-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.quota-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.quota-fill {
  height: 100%;
  background: var(--primary-color);
}

.sidebar-nav ul, .sidebar-footer ul {
  list-style: none;
  padding: 0 0.5rem;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.2s;
  font-size: 0.9rem;
  font-weight: 500;
}

.nav-item i {
  color: var(--text-secondary);
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

.nav-item:hover {
  background: var(--glass-bg-hover);
}

.nav-item.active {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.nav-item.active i {
  color: #3b82f6;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

.nav-section-title {
  padding: 0 1.5rem 0.5rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-tertiary);
  font-weight: 700;
}

.nautilus-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 1rem;
}

.nautilus-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  height: 60px;
  flex-shrink: 0;
  position: relative;
  z-index: 50;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 1.1rem;
}

.crumb-item {
  cursor: pointer;
  color: var(--text-primary);
  transition: color 0.2s;
  display: flex;
  align-items: center;
}

.crumb-item:hover {
  color: var(--primary-color);
}

.crumb-item .separator {
  margin: 0 0.5rem;
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.topbar-tools {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.search-box {
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 0.4rem 1rem;
  gap: 0.5rem;
  transition: border-color 0.2s;
}

.search-box:focus-within {
  border-color: var(--primary-color);
}

.search-box input {
  background: transparent;
  border: none;
  color: white;
  outline: none;
  font-size: 0.9rem;
  width: 200px;
}

.search-box input::placeholder {
  color: var(--text-tertiary);
}

.search-box i {
  color: var(--text-secondary);
}

.view-toggles {
  display: flex;
  gap: 0.25rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  padding: 0.25rem;
}

.view-toggles button {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.view-toggles button:hover {
  color: var(--text-primary);
}

.view-toggles button.active {
  background: var(--primary-color);
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
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

.search-filters .form-select-small {
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
  color: var(--danger-color);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0;
}
.search-filters .clear-filters-btn:hover {
  text-decoration: underline;
}

.nautilus-content {
  flex: 1;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow-y: auto;
  position: relative;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  user-select: none;
}

.view-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 1.5rem;
  position: relative;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
  border: 1px solid transparent;
}

.grid-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.grid-item.selected {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
}

.item-icon-wrapper {
  font-size: 3.5rem;
  margin-bottom: 0.75rem;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
  transition: transform 0.2s;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.file-ext-badge {
  position: absolute;
  bottom: 0px;
  right: 15px;
  background: var(--primary-color);
  color: white;
  font-size: 0.55rem;
  font-weight: 800;
  padding: 1px 4px;
  border-radius: 4px;
  text-transform: uppercase;
  box-shadow: 0 2px 4px rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.2);
  letter-spacing: 0.5px;
}

.file-ext-badge-small {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: var(--primary-color);
  color: white;
  font-size: 0.45rem;
  font-weight: 800;
  padding: 1px 3px;
  border-radius: 3px;
  text-transform: uppercase;
  box-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

.file-ext-badge-preview {
  position: absolute;
  bottom: 10px;
  right: 50px;
  background: var(--primary-color);
  color: white;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  box-shadow: 0 2px 6px rgba(0,0,0,0.6);
  border: 1px solid rgba(255,255,255,0.2);
}

.grid-item:hover .item-icon-wrapper {
  transform: translateY(-2px);
}

.folder-icon { color: #3b82f6; }
.file-icon { color: #94a3b8; }

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

.file-thumbnail-grid {
  width: 80px;
  height: 80px;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.file-thumbnail-grid:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 16px rgba(0,0,0,0.4);
}

.file-thumbnail-list {
  width: 24px;
  height: 24px;
  object-fit: cover;
  border-radius: 4px;
}

.file-thumbnail-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.selection-box {
  position: absolute;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.5);
  pointer-events: none;
  z-index: 10;
}

.view-list {
  display: flex;
  flex-direction: column;
  background: rgba(0,0,0,0.1);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.05);
}

.list-header, .list-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 100px;
  padding: 0.75rem 1rem;
  align-items: center;
  gap: 1rem;
}

.list-header {
  border-bottom: 1px solid var(--glass-border);
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.list-row {
  border-bottom: 1px solid rgba(255,255,255,0.05);
  cursor: pointer;
  transition: background 0.15s;
  font-size: 0.9rem;
}

.list-row:last-child {
  border-bottom: none;
}

.list-row:hover {
  background: rgba(255,255,255,0.05);
}

.list-row.selected {
  background: rgba(59, 130, 246, 0.2);
}

.list-row .col-name {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

.list-row .col-name i {
  font-size: 1.25rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.nautilus-details {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 320px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  flex-shrink: 0;
  overflow-y: auto;
  box-shadow: -5px 0 25px rgba(0,0,0,0.5);
}

.details-header {
  padding: 2rem 1.5rem 1rem;
  text-align: center;
  border-bottom: 1px solid var(--glass-border);
}

.preview-box {
  height: 120px;
  background: rgba(0,0,0,0.2);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.details-header h3 {
  font-size: 1.1rem;
  margin: 0;
  word-break: break-all;
}

.details-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  text-transform: uppercase;
  font-weight: 600;
}

.detail-value {
  font-size: 0.9rem;
  color: var(--text-primary);
  word-break: break-all;
}

.details-actions {
  padding: 1.5rem;
  margin-top: auto;
  border-top: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.75rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
  font-weight: 500;
}

.btn-action:hover {
  background: rgba(255,255,255,0.1);
}

.btn-action.danger {
  color: #ef4444;
}

.btn-action.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
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

.context-menu {
  position: fixed;
  z-index: 1000;
  border-radius: 8px;
  padding: 0.5rem 0;
  min-width: 200px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

.menu-item {
  padding: 0.6rem 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: var(--text-primary);
  transition: background 0.2s;
}

.menu-item:hover {
  background: var(--glass-bg-hover);
}

.menu-item i {
  width: 16px;
  text-align: center;
  color: var(--text-secondary);
}

.menu-item.danger {
  color: #ef4444;
}

.menu-item.danger i {
  color: #ef4444;
}

.menu-separator {
  height: 1px;
  background: var(--glass-border);
  margin: 0.5rem 0;
}

.hidden-input { 
  opacity: 0; 
  position: absolute; 
  pointer-events: none; 
  width: 1px; 
  height: 1px; 
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
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

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 1.25rem;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.25rem;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover { color: var(--text-primary); }

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.upload-area {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  display: block;
}

.upload-area.drag-over, .upload-area:hover {
  border-color: var(--primary-color);
  background: rgba(59, 130, 246, 0.1);
}

.upload-icon {
  font-size: 3rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.upload-list-area {
  margin-top: 1.5rem;
}

.upload-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  margin-bottom: 0.5rem;
  position: relative;
  overflow: hidden;
}

.upload-progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
}

.upload-progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s;
}

.form-group {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-select, .form-input, .form-control {
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: white;
  font-size: 0.95rem;
}

.toggle-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-switch input { opacity: 0; width: 0; height: 0; }

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(255, 255, 255, 0.2);
  transition: .4s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px; width: 18px;
  left: 3px; bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--primary-color);
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

.modal-title-with-summary {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.upload-summary-badge {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
  width: fit-content;
}

@media (max-width: 768px) {
  .nautilus-drive {
    flex-direction: column;
  }
}
</style>
