<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>Media Gallery</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>Manage your media files and assets</p>
    
</div>

    <div class="page-actions">

      <button class="btn btn-primary" @click="uploadMedia">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 15 L21 19 C21 20.1 20.1 21 19 21 L5 21 C3.9 21 3 20.1 3 19 L3 15" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M17 8 L12 3 L7 8" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M12 3 L12 15" stroke="currentColor" stroke-width="2"/>
        </svg>
        Upload
      </button>
      <button class="btn btn-secondary" @click="toggleView">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <rect x="3" y="3" width="7" height="7" stroke="currentColor" stroke-width="2" fill="none"/>
          <rect x="14" y="3" width="7" height="7" stroke="currentColor" stroke-width="2" fill="none"/>
          <rect x="3" y="14" width="7" height="7" stroke="currentColor" stroke-width="2" fill="none"/>
          <rect x="14" y="14" width="7" height="7" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        {{ viewMode === 'grid' ? 'List' : 'Grid' }}
      </button>
    
</div>

    <div class="media-gallery-content">
      <!-- Enhanced Stats Overview -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
              <path d="M21 15 L16 10 L5 21" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalFiles }}</div>
            <div class="stat-label">Total Files</div>
            <div class="stat-change positive">+24 this week</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="12" cy="12" r="3" fill="currentColor"/>
              <path d="M12 2 L12 7 M12 17 L12 22 M2 12 L7 12 M17 12 L22 12" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatSize(totalSize) }}</div>
            <div class="stat-label">Total Storage</div>
            <div class="stat-change positive">+2.3 GB used</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="2" y="2" width="20" height="8" rx="1" stroke="currentColor" stroke-width="2" fill="none"/>
              <rect x="2" y="14" width="20" height="8" rx="1" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="6" cy="6" r="1" fill="currentColor"/>
              <circle cx="12" cy="6" r="1" fill="currentColor"/>
              <circle cx="18" cy="6" r="1" fill="currentColor"/>
              <circle cx="6" cy="18" r="1" fill="currentColor"/>
              <circle cx="12" cy="18" r="1" fill="currentColor"/>
              <circle cx="18" cy="18" r="1" fill="currentColor"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ imageCount }}</div>
            <div class="stat-label">Images</div>
            <div class="stat-change positive">+8 uploaded</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
              <polygon points="10,8 16,12 22,16" fill="currentColor"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ videoCount }}</div>
            <div class="stat-label">Videos</div>
            <div class="stat-change negative">-2 deleted</div>
          </div>
        </div>
      </div>

      <!-- Enhanced Upload Area -->
      <div class="upload-area" :class="{ 'drag-over': isDragOver }" @dragover.prevent="isDragOver = true" @dragleave="isDragOver = false" @drop="handleDrop">
        <div class="upload-content">
          <div class="upload-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M21 15 L21 19 C21 20.1 20.1 21 19 21 L5 21 C3.9 21 3 20.1 3 19 L3 5 C3 3.9 3.9 3 5 3 L16 3 L21 8 L21 15 Z" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M17 8 L17 3 L7 3 L7 8" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M3 9 L21 9 M3 15 L21 15" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
          </div>
          <div class="upload-text">
            <h3>Drag & Drop Files Here</h3>
            <p>or click to browse</p>
          </div>
          <input 
            type="file" 
            multiple 
            @change="handleFileSelect" 
            class="file-input"
            accept="image/*,video/*,application/pdf,.doc,.docx"
          />
        </div>
      </div>

      <!-- Enhanced Filters and Search -->
      <div class="media-filters">
        <div class="filter-group">
          <label>Search:</label>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search media files..."
            class="search-input"
          />
        </div>
        <div class="filter-group">
          <label>Type:</label>
          <select v-model="selectedType" class="filter-select">
            <option value="all">All Types</option>
            <option value="image">Images</option>
            <option value="video">Videos</option>
            <option value="document">Documents</option>
            <option value="audio">Audio</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Date Range:</label>
          <select v-model="dateRange" class="filter-select">
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="year">This Year</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Sort:</label>
          <select v-model="sortBy" class="filter-select">
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="name">Name A-Z</option>
            <option value="size">Size (Large to Small)</option>
            <option value="type">Type</option>
          </select>
        </div>
      </div>

      <!-- Enhanced Media Grid -->
      <div class="media-grid" :class="viewMode">
        <div 
          v-for="media in filteredMedia" 
          :key="media.id"
          class="media-item"
          :class="{ 'selected': selectedMedia.includes(media.id) }"
          @click="selectMedia(media)"
          @contextmenu.prevent="showContextMenu($event, media)"
        >
          <div class="media-preview" :class="{ 'selected': selectedMedia.includes(media.id) }">
            <img 
              v-if="media.type === 'image'" 
              :src="media.thumbnail" 
              :alt="media.name"
              class="media-image"
              @error="handleImageError"
            />
            <div v-else-if="media.type === 'video'" class="video-placeholder">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <rect x="2" y="4" width="20" height="16" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
                <polygon points="10,8 16,12 22,16" fill="currentColor"/>
              </svg>
              <div class="video-duration">{{ formatDuration(media.duration) }}</div>
            </div>
            <div v-else-if="media.type === 'document'" class="document-placeholder">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M14 2 L6 2 C4.9 2 4 2.9 4 4 L4 20 C4 21.1 4.9 22 6 22 L18 22 C19.1 22 20 21.1 20 20 L20 8 L14 2 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M14 2 L14 8 L20 8" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
              <div class="document-type">{{ media.extension }}</div>
            </div>
            <div v-else-if="media.type === 'audio'" class="audio-placeholder">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3v10.55c-.59 0-1.05-.25-1.41-.7C9.17 12.26 8.5 12.5 7.5 12.5c-1.24 0-2.13-1.25-2.13-2.5V3H12z M12 5.5c1.24 0 2.13 1.25 2.13 2.5v7.5c0 1.25-.89 2.13-1.25 2.13-2.5V5.5z" fill="currentColor"/>
              </svg>
              <div class="audio-duration">{{ formatDuration(media.duration) }}</div>
            </div>
            <div class="media-overlay" v-if="selectedMedia.includes(media.id)">
              <div class="overlay-actions">
                <button class="overlay-btn" @click.stop="viewMedia(media)">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                    <circle cx="12" cy="12" r="3" fill="currentColor"/>
                  </svg>
                </button>
                <button class="overlay-btn" @click.stop="downloadMedia(media)">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21 15 L21 19 C21 20.1 20.1 21 19 21 L5 21 C3.9 21 3 20.1 3 19 3 L3 5 C3 3.9 3.9 3 5 3 L16 3 L21 8 L21 15 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M17 8 L17 3 L7 3 L7 8" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
                <button class="overlay-btn danger" @click.stop="deleteMedia(media)">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 6 L5 6 L21 6 M19 6 L21 18" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M18 6 L6 18" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <div class="media-info">
            <h4>{{ media.name }}</h4>
            <div class="media-meta">
              <span class="media-size">{{ formatSize(media.size) }}</span>
              <span class="media-date">{{ formatDate(media.date) }}</span>
              <span class="media-dimensions">{{ media.dimensions }}</span>
            </div>
          </div>
          
          <div class="media-actions">
            <button class="btn-icon" @click.stop="viewMedia(media)" title="View">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
              </svg>
            </button>
            <button class="btn-icon" @click.stop="downloadMedia(media)" title="Download">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 15 L21 19 C21 20.1 20.1 21 19 21 L5 21 C3.9 21 3 20.1 3 19 L3 5 C3 3.9 3.9 3 5 3 L16 3 L21 8 L21 15 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M17 8 L17 3 L7 3 L7 8" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
            </button>
            <button class="btn-icon danger" @click.stop="deleteMedia(media)" title="Delete">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 6 L5 6 L21 6 M19 6 L21 18" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M18 6 L6 18" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Batch Actions -->
      <div class="batch-actions" v-if="selectedMedia.length > 0">
        <div class="batch-info">
          <span>{{ selectedMedia.length }} items selected</span>
        </div>
        <div class="batch-buttons">
          <button class="btn btn-outline" @click="selectAll">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M9 17 L9 11 L15 11 L15 17" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            Select All
          </button>
          <button class="btn btn-outline" @click="clearSelection">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41 L17.59 5 L12 10.59 L6.41 5 L5 6.41 L10.59 12 L5 17.59 L6.41 19 L12 14.41 L17.59 19 L19 17.59 L14.41 12 L19 6.41 Z" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            Clear
          </button>
          <button class="btn btn-danger" @click="deleteSelected">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 6 L5 6 L21 6 M19 6 L21 18" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M18 6 L6 18" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            Delete Selected
          </button>
        </div>
      </div>

      <!-- Context Menu -->
      <div 
        v-if="contextMenu.show" 
        class="context-menu"
        :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
        @click="closeContextMenu"
      >
        <div class="context-menu-item" @click="viewMedia(contextMenu.media)">
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
            <circle cx="12" cy="12" r="3" fill="currentColor"/>
          </svg>
          View
        </div>
        <div class="context-menu-item" @click="downloadMedia(contextMenu.media)">
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M21 15 L21 19 C21 20.1 20.1 21 19 21 L5 21 C3.9 21 3 20.1 3 19 3 L3 5 C3 3.9 3.9 3 5 3 L16 3 L21 8 L21 15 Z" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M17 8 L17 3 L7 3 L7 8" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          Download
        </div>
        <div class="context-menu-item" @click="copyLink(contextMenu.media)">
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 17 L5 12 L10 7 L15 12 L20 7 L15 2 L10 7 L5 12 L10 17 Z" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          Copy Link
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item danger" @click="deleteMedia(contextMenu.media)">
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 6 L5 6 L21 6 M19 6 L21 18" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M18 6 L6 18" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          Delete
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const viewMode = ref('grid')
const searchQuery = ref('')
const selectedType = ref('all')

const media = ref([
  {
    id: 1,
    name: 'Logo.png',
    type: 'image',
    size: 245760,
    date: new Date('2024-01-15'),
    thumbnail: 'https://picsum.photos/seed/logo/200/150.jpg'
  },
  {
    id: 2,
    name: 'Product Demo.mp4',
    type: 'video',
    size: 5242880,
    date: new Date('2024-01-14'),
    thumbnail: null
  },
  {
    id: 3,
    name: 'Brand Guidelines.pdf',
    type: 'document',
    size: 1048576,
    date: new Date('2024-01-13'),
    thumbnail: null
  },
  {
    id: 4,
    name: 'Banner.jpg',
    type: 'image',
    size: 524288,
    date: new Date('2024-01-12'),
    thumbnail: 'https://picsum.photos/seed/banner/200/150.jpg'
  }
])

const filteredMedia = computed(() => {
  return media.value.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesType = selectedType.value === 'all' || item.type === selectedType.value
    return matchesSearch && matchesType
  })
})

const uploadMedia = () => {
  console.log('Opening upload dialog...')
}

const toggleView = () => {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
}

const selectMedia = (item) => {
  console.log('Selected media:', item.name)
}

const downloadMedia = (item) => {
  console.log('Downloading:', item.name)
}

const deleteMedia = (item) => {
  console.log('Deleting:', item.name)
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date) => {
  return date.toLocaleDateString()
}

onMounted(() => {
  console.log('Media Gallery component mounted')
})
</script>

<style scoped>
.media-gallery-content {
  max-width: 1200px;
  margin: 0 auto;
}

.media-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
}

.search-input,
.filter-select {
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #f1f5f9;
  font-size: 0.875rem;
}

.search-input {
  min-width: 200px;
}

.media-grid {
  display: grid;
  gap: 1.5rem;
}

.media-grid.grid {
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.media-grid.list {
  grid-template-columns: 1fr;
}

.media-item {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.media-item:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.media-grid.list .media-item {
  display: flex;
  align-items: center;
  padding: 1rem;
}

.media-preview {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
}

.media-grid.list .media-preview {
  width: 80px;
  height: 60px;
  aspect-ratio: 4/3;
  margin-right: 1rem;
}

.media-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-placeholder,
.document-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.media-info {
  padding: 1rem;
}

.media-grid.list .media-info {
  flex: 1;
  padding: 0;
}

.media-info h4 {
  margin: 0 0 0.5rem 0;
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 600;
}

.media-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.media-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0 1rem 1rem;
}

.media-grid.list .media-actions {
  padding: 0;
}

.btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn.danger {
  border-color: rgba(239, 68, 68, 0.5);
  color: #ef4444;
}

.btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

.btn-sm {
  padding: 0.375rem 0.5rem;
  font-size: 0.75rem;
}

.icon {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 768px) {
  .media-filters {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .search-input,
  .filter-select {
    flex: 1;
  }
  
  .media-grid.grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}
</style>

<style scoped>
.legacy-page-container {
  padding: 1rem;
}
.page-title { margin-bottom: 0.5rem; }
.page-subtitle { color: var(--text-secondary); margin-bottom: 1rem; }
.page-actions { margin-bottom: 1.5rem; }
</style>
