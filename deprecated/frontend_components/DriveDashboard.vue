<template>
  <div class="drive-dashboard">
    <div class="drive-header">
      <h2>📁 Drive - File Storage</h2>
      <div class="drive-actions">
        <button @click="showUploadModal = true" class="btn btn-primary">
          📤 Upload File
        </button>
        <button @click="showFolderModal = true" class="btn btn-secondary">
          📁 New Folder
        </button>
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

    <!-- File List with Drag and Drop -->
    <div 
      class="file-list"
      :class="{ 'drag-over': isDragging }"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
      @dragover="handleDragOver"
      @drop="handleDrop"
    >
      <!-- Drag overlay -->
      <div v-if="isDragging" class="drag-overlay">
        <div class="drag-message">
          📁 Drop files here to upload
        </div>
      </div>

      <div v-if="files.length === 0" class="empty-state">
        <div class="empty-icon">📁</div>
        <h3>No files in your Drive</h3>
        <p>Upload some files or drag and drop them here to get started!</p>
        <button @click="showUploadModal = true" class="btn btn-primary">
          📤 Upload Files
        </button>
      </div>
      <div v-else>
        <div class="file-grid">
          <div v-for="file in files" :key="file.id" class="file-item" @contextmenu.prevent="showContextMenu($event, file)">
            <div class="file-icon">
              {{ file.is_folder ? '📁' : '📄' }}
            </div>
            <div class="file-info">
              <div class="file-name">{{ file.filename }}</div>
              <div class="file-meta">
                {{ formatBytes(file.file_size) }} • {{ formatDate(file.created_at) }}
              </div>
            </div>
            <div class="file-actions">
              <button @click="shareFile(file)" class="file-action-btn">
                🔗 Share
              </button>
              <button @click="downloadFile(file)" class="file-action-btn">
                ⬇️ Download
              </button>
            </div>
          </div>
        </div>
      </div>

    <!-- Context Menu -->
    <div 
      v-if="contextMenu.visible" 
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      class="context-menu"
      @click.stop
    >
      <div class="context-menu-item" @click="downloadFile(contextMenu.file)">
        <i class="fas fa-download"></i>
        Download
      </div>
      <div class="context-menu-item" @click="shareFile(contextMenu.file)">
        <i class="fas fa-share"></i>
        Share
      </div>
      <div class="context-menu-item" @click="renameFile(contextMenu.file)">
        <i class="fas fa-edit"></i>
        Rename
      </div>
      <div class="context-menu-separator"></div>
      <div class="context-menu-item danger" @click="deleteFile(contextMenu.file)">
        <i class="fas fa-trash"></i>
        Delete
      </div>
    </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click="showUploadModal = false">
      <div class="modal" @click.stop>
        <h3>Upload File</h3>
        <input type="file" @change="handleFileUpload" ref="fileInput" />
        <div class="modal-actions">
          <button @click="showUploadModal = false" class="btn btn-secondary">Cancel</button>
          <button @click="uploadFile" class="btn btn-primary">Upload</button>
        </div>
      </div>
    </div>

    <!-- Folder Modal -->
    <div v-if="showFolderModal" class="modal-overlay" @click="showFolderModal = false">
      <div class="modal" @click.stop>
        <h3>Create Folder</h3>
        <input v-model="folderName" placeholder="Folder name" class="form-input" />
        <div class="modal-actions">
          <button @click="showFolderModal = false" class="btn btn-secondary">Cancel</button>
          <button @click="createFolder" class="btn btn-primary">Create</button>
        </div>
      </div>
    </div>

    <!-- Share Modal -->
    <div v-if="showShareModal" class="modal-overlay" @click="showShareModal = false">
      <div class="modal" @click.stop>
        <h3>Share File</h3>
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
import { ref, onMounted } from 'vue'
import { apiGet, apiPost, apiPostForm, apiDelete } from '@/utils/api.js'

export default {
  name: 'DriveDashboard',
  setup() {
    const files = ref([])
    const quota = ref({
      used_space: 0,
      total_quota: 0,
      additional_quota: 0
    })
    const showUploadModal = ref(false)
    const showFolderModal = ref(false)
    const showShareModal = ref(false)
    const contextMenu = ref({
      visible: false,
      x: 0,
      y: 0,
      file: null
    })
    const folderName = ref('')
    const selectedFile = ref(null)
    const shareLink = ref('')
    const shareSettings = ref({
      access_level: 'only_me',
      password: ''
    })
    const fileInput = ref(null)

    const quotaPercentage = ref(0)

    const loadFiles = async () => {
      try {
        const data = await apiGet('/drive/files')
        files.value = data.files || []
        if (data.quota) {
          quota.value = data.quota
          quotaPercentage.value = data.quota.usage_percentage || 0
        } else {
          // Set default quota if not provided
          quota.value = {
            used_space: 0,
            total_quota: 30 * 1024 * 1024 * 1024, // 30GB
            additional_quota: 0
          }
          quotaPercentage.value = 0
        }
      } catch (error) {
        console.error('Failed to load files:', error)
        // Set default values on error
        files.value = []
        quota.value = {
          used_space: 0,
          total_quota: 30 * 1024 * 1024 * 1024,
          additional_quota: 0
        }
        quotaPercentage.value = 0
      }
    }

    const handleFileUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        uploadSingleFile(file)
      }
    }

    const uploadSingleFile = async (file) => {
      const formData = new FormData()
      formData.append('file', file)

      try {
        await apiPostForm('/drive/upload', formData)
        showUploadModal.value = false
        loadFiles()
      } catch (error) {
        console.error('Upload failed:', error)
        alert('Upload failed: ' + (error.message || 'Unknown error'))
      }
    }

    const uploadFile = async () => {
      const file = fileInput.value.files[0]
      if (!file) return
      await uploadSingleFile(file)
    }

    // Drag and drop handlers
    const isDragging = ref(false)
    const dragCounter = ref(0)

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

    const handleMultipleFiles = async (files) => {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        if (file.type === '' && file.name.endsWith('/')) {
          // It's a directory, skip for now or handle differently
          console.log('Directory upload not supported yet:', file.name)
          continue
        }
        await uploadSingleFile(file)
      }
    }

    const createFolder = async () => {
      if (!folderName.value.trim()) {
        alert('Please enter a folder name')
        return
      }

      try {
        await apiPost('/drive/folder', {
          name: folderName.value.trim()
        })
        showFolderModal.value = false
        folderName.value = ''
        loadFiles()
      } catch (error) {
        console.error('Folder creation failed:', error)
        alert('Failed to create folder: ' + (error.message || 'Unknown error'))
      }
    }

    const shareFile = (file) => {
      selectedFile.value = file
      showShareModal.value = true
      shareLink.value = ''
    }

    const generateShareLink = async () => {
      if (!selectedFile.value) return

      try {
        const result = await apiPost('/drive/share', {
          file_id: selectedFile.value.id,
          access_level: shareSettings.value.access_level,
          share_password: shareSettings.value.password || undefined
        })

        shareLink.value = result.share_link
      } catch (error) {
        console.error('Share failed:', error)
        alert('Share failed: ' + (error.message || 'Unknown error'))
      }
    }

    const copyShareLink = () => {
      navigator.clipboard.writeText(shareLink.value)
    }

    const downloadFile = async (file) => {
      try {
        const downloadUrl = `/drive/download/${file.id}`
        
        // Use fetch with apiRequest logic to ensure auth handling
        // But since we need the blob, let's just use raw fetch but with the same token
        const token = localStorage.getItem('token')
        const response = await fetch(downloadUrl, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (!response.ok) {
          if (response.status === 401) handleAuthError()
          throw new Error('Download failed')
        }
        
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const downloadLink = document.createElement('a')
        downloadLink.href = url
        downloadLink.download = file.filename
        document.body.appendChild(downloadLink)
        downloadLink.click()
        downloadLink.remove()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Download failed:', error)
        alert('Download failed: ' + (error.message || 'Unknown error'))
      }
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

    onMounted(() => {
      loadFiles()
    })

    const deleteFile = async (file) => {
      if (confirm(`Are you sure you want to delete "${file.filename}"?`)) {
        try {
          await apiDelete(`/drive/files/${file.id}/delete`)
          await loadFiles()
        } catch (error) {
          console.error('Error deleting file:', error)
          alert('Delete failed: ' + (error.message || 'Unknown error'))
        }
      }
      hideContextMenu()
    }

    const renameFile = (file) => {
      const newName = prompt(`Rename "${file.filename}" to:`, file.filename)
      if (newName && newName !== file.filename) {
        // TODO: Implement rename API call
        console.log('Renaming file:', file.id, 'to', newName)
      }
      hideContextMenu()
    }

    const showContextMenu = (event, file) => {
      contextMenu.value = {
        visible: true,
        x: event.clientX,
        y: event.clientY,
        file: file
      }
      
      // Hide context menu when clicking elsewhere
      document.addEventListener('click', hideContextMenu)
    }

    const hideContextMenu = () => {
      contextMenu.value.visible = false
      document.removeEventListener('click', hideContextMenu)
    }

    return {
      files,
      quota,
      quotaPercentage,
      showUploadModal,
      showFolderModal,
      showShareModal,
      contextMenu,
      folderName,
      shareLink,
      shareSettings,
      fileInput,
      isDragging,
      loadFiles,
      handleFileUpload,
      uploadFile,
      uploadSingleFile,
      createFolder,
      shareFile,
      generateShareLink,
      copyShareLink,
      downloadFile,
      deleteFile,
      renameFile,
      showContextMenu,
      hideContextMenu,
      formatBytes,
      formatDate,
      handleDragEnter,
      handleDragLeave,
      handleDragOver,
      handleDrop,
      handleMultipleFiles
    }
  }
  }
}
</script>

<style scoped>
.drive-dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
}

.drive-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.drive-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.drive-header h2 {
  margin: 0;
  color: #ffffff;
  font-size: 2rem;
  font-weight: 700;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.drive-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 1rem 2rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(102, 126, 234, 0.5);
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.6);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.2);
}

.btn-sm {
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
}

.quota-info {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.quota-info::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.quota-bar {
  width: 100%;
  height: 16px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.quota-used {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #06b6d4 100%);
  transition: width 0.3s ease;
  border-radius: 6px;
  box-shadow: 0 0 16px rgba(16, 185, 129, 0.5);
}

.quota-text {
  color: #ffffff;
  font-weight: 600;
  font-size: 1.1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.file-list {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  min-height: 500px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.file-list::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.file-list.drag-over {
  border-color: rgba(16, 185, 129, 0.8);
  background: rgba(16, 185, 129, 0.1);
}

.drag-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(16, 185, 129, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 3px dashed rgba(16, 185, 129, 0.8);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drag-message {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
}

.empty-state {
  text-align: center;
  padding: 6rem 3rem;
  color: #ffffff;
}

.empty-icon {
  font-size: 6rem;
  margin-bottom: 2rem;
  filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.5));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-15px);
  }
}

.empty-state h3 {
  margin: 0 0 1.5rem 0;
  color: #ffffff;
  font-weight: 700;
  font-size: 1.8rem;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
}

.empty-state p {
  margin: 0 0 3rem 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.2rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
  padding: 1rem;
}

.file-item {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 20px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.file-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.file-item:hover {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

.file-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  text-align: center;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.5));
  transition: transform 0.3s ease;
}

.file-item:hover .file-icon {
  transform: scale(1.1);
}

.file-name {
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.75rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  word-break: break-word;
  font-size: 1.1rem;
  line-height: 1.4;
}

.file-meta {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  margin-bottom: 1.5rem;
}

.file-actions {
  display: flex;
  gap: 1rem;
  margin-top: auto;
  width: 100%;
  justify-content: center;
}

.file-action-btn {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 0.75rem 1.5rem;
  color: #ffffff;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.file-action-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(255, 255, 255, 0.2);
}

.context-menu {
  position: fixed;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  padding: 0.75rem 0;
  min-width: 200px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  overflow: hidden;
}

.context-menu::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.context-menu-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  font-weight: 500;
}

.context-menu-item:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.context-menu-item.danger {
  color: var(--danger-color, #ef4444);
}

.context-menu-item.danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

.context-menu-item i {
  width: 16px;
  text-align: center;
}

.context-menu-separator {
  height: 1px;
  background: var(--glass-border);
  margin: 0.25rem 0;
}

@media (max-width: 768px) {
  .drive-dashboard {
    padding: 1rem;
  }
  
  .drive-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .file-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .modal {
    min-width: 90%;
    margin: 1rem;
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 2.5rem;
  border-radius: 20px;
  min-width: 500px;
  max-width: 600px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
  position: relative;
  overflow: hidden;
}

.modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 3s ease-in-out infinite;
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 2rem;
  color: #ffffff;
  font-weight: 700;
  font-size: 1.5rem;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
}

.form-input {
  width: 100%;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  color: #ffffff;
  font-size: 1rem;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
}

.form-input:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 16px rgba(102, 126, 234, 0.3);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@media (max-width: 768px) {
  .drive-dashboard {
    padding: 1rem;
  }
  
  .drive-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .file-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .modal {
    min-width: 90%;
    margin: 1rem;
  }
}
</style>
