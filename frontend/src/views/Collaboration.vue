<template>
  <div class="collaboration">
    <div class="collaboration-header">
      <h1>Collaborations</h1>
      <button class="btn-primary" @click="createNewCollaboration">
        <i class="fas fa-plus"></i>
        Create New Collaboration
      </button>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button 
        v-for="filter in filters" 
        :key="filter"
        :class="{ active: activeFilter === filter }"
        @click="setActiveFilter(filter)"
      >
        {{ filter }}
      </button>
    </div>

    <!-- Collaboration List -->
    <div class="collaboration-list">
      <div 
        v-for="collab in filteredCollaborations" 
        :key="collab.id"
        class="collaboration-card"
        @click="viewCollaboration(collab)"
      >
        <div class="collab-header">
          <div class="collab-info">
            <h3>{{ collab.name }}</h3>
            <div class="collab-meta">
              <span class="channel">{{ collab.channel }}</span>
              <span class="platform">{{ collab.platform }}</span>
              <span class="type">{{ collab.type }}</span>
              <span class="price">${{ collab.price }}</span>
            </div>
          </div>
          <div class="collab-status">
            <span :class="['status', collab.status]">{{ collab.status }}</span>
          </div>
        </div>
        <div class="collab-details">
          <div class="videos-progress">
            <span>{{ collab.completedVideos }}/{{ collab.numVideos }} videos</span>
            <div class="progress-bar">
              <div 
                class="progress-fill"
                :style="{ width: (collab.completedVideos / collab.numVideos * 100) + '%' }"
              ></div>
            </div>
          </div>
          <div class="collab-actions">
            <button class="btn-icon" @click.stop="editCollaboration(collab)">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn-icon" @click.stop="deleteCollaboration(collab)">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Collaboration Modal -->
    <div v-if="collaborationModal.visible" class="modal-overlay" @click.self="attemptCloseModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ collaborationModal.isEdit ? 'Edit' : 'Create' }} Collaboration</h2>
          <button class="close-btn" @click="attemptCloseModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveCollaboration" autocomplete="off">
            <div class="form-grid">
              <div class="form-group">
                <label for="name">Name *</label>
                <input 
                  id="name"
                  v-model="collaborationForm.name"
                  type="text"
                  required
                  placeholder="Collaboration name"
                />
              </div>
              <div class="form-group">
                <label for="channel">Channel *</label>
                <input 
                  id="channel"
                  v-model="collaborationForm.channel"
                  type="text"
                  required
                  placeholder="Channel name"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Platform *</label>
              <div class="platform-checkboxes">
                <label class="checkbox-label" v-for="platform in platforms" :key="platform">
                  <input 
                    type="checkbox" 
                    v-model="collaborationForm.platform"
                    :value="platform"
                    :id="`platform-${platform}`"
                  />
                  <span class="checkmark"></span>
                  {{ platform }}
                </label>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label for="collaboratorEmail">Collaborator Email</label>
                <input 
                  id="collaboratorEmail"
                  v-model="collaborationForm.collaboratorEmail"
                  type="email"
                  placeholder="collaborator@example.com"
                />
              </div>
              <div class="form-group">
                <label for="type">Type *</label>
                <select 
                  id="type"
                  v-model="collaborationForm.type"
                  required
                  @change="handleTypeChange"
                >
                  <option value="Paid">Paid</option>
                  <option value="Product">Product</option>
                  <option value="Paid Product">Paid Product</option>
                </select>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label for="price">Price *</label>
                <input 
                  id="price"
                  v-model="collaborationForm.price"
                  type="number"
                  required
                  :disabled="collaborationForm.type === 'Product'"
                  placeholder="0.00"
                  step="0.01"
                  min="0"
                />
              </div>
              <div class="form-group">
                <label for="numVideos">Number of Videos *</label>
                <input 
                  id="numVideos"
                  v-model="collaborationForm.numVideos"
                  type="number"
                  required
                  min="1"
                  @change="updateVideoSections"
                />
              </div>
            </div>

            <!-- Video Sections -->
            <div class="video-sections" v-if="collaborationModal.isEdit">
              <h3>Video Details</h3>
              <div 
                v-for="(video, index) in collaborationForm.videos" 
                :key="index"
                class="video-section"
              >
                <div class="video-header">
                  <h4>Video {{ index + 1 }}</h4>
                  <div class="video-actions">
                    <label class="checkbox-label">
                      <input 
                        type="checkbox" 
                        v-model="video.invitation"
                        :id="`invitation-${index}`"
                      />
                      <span class="checkmark"></span>
                      Invitation
                    </label>
                    <label class="checkbox-label">
                      <input 
                        type="checkbox" 
                        v-model="video.paid"
                        :id="`paid-${index}`"
                        :disabled="collaborationForm.price === 0"
                      />
                      <span class="checkmark"></span>
                      Paid
                    </label>
                    <label class="checkbox-label">
                      <input 
                        type="checkbox" 
                        v-model="video.done"
                        :id="`done-${index}`"
                      />
                      <span class="checkmark"></span>
                      Done
                    </label>
                  </div>
                </div>

                <div class="video-fields">
                  <div class="form-group">
                    <label :for="`script-${index}`">Script</label>
                    <textarea 
                      :id="`script-${index}`"
                      v-model="video.script"
                      placeholder="Video script content..."
                      rows="4"
                      class="expandable"
                    ></textarea>
                  </div>

                  <div class="form-grid">
                    <div class="form-group">
                      <label :for="`title-${index}`">Title</label>
                      <input 
                        :id="`title-${index}`"
                        v-model="video.title"
                        type="text"
                        placeholder="Video title"
                      />
                    </div>
                    <div class="form-group">
                      <label :for="`subtitles-${index}`">Subtitles</label>
                      <input 
                        :id="`subtitles-${index}`"
                        v-model="video.subtitles"
                        type="text"
                        placeholder="Subtitles text"
                      />
                    </div>
                  </div>

                  <div class="form-group">
                    <label :for="`caption-${index}`">Caption</label>
                    <textarea 
                      :id="`caption-${index}`"
                      v-model="video.caption"
                      placeholder="Social media caption..."
                      rows="3"
                      class="expandable"
                    ></textarea>
                  </div>

                  <div class="form-group">
                    <label :for="`hashtags-${index}`">Hashtags</label>
                    <textarea 
                      :id="`hashtags-${index}`"
                      v-model="video.hashtags"
                      placeholder="#hashtag1 #hashtag2 #hashtag3"
                      rows="2"
                      class="expandable"
                    ></textarea>
                  </div>

                  <div class="form-group">
                    <label>Video Draft</label>
                    <div class="video-upload">
                      <div class="upload-area" @click="selectVideo(index)">
                        <i class="fas fa-video"></i>
                        <span>{{ video.draftFile || video.draftLink ? `Draft Link for ${collaborationForm.name || 'Untitled'} Video ${index + 1}` : 'Click to upload or paste link' }}</span>
                      </div>
                      <input 
                        type="file" 
                        accept="video/*"
                        @change="handleVideoUpload($event, index)"
                        :id="`videoInput-${index}`"
                        :ref="`videoInput-${index}`"
                        style="display: none"
                      />
                      <input 
                        type="text"
                        v-model="video.draftLink"
                        placeholder="Or paste video link here"
                        @input="handleVideoLink(index)"
                      />
                      <div class="video-actions" v-if="video.draftFile || video.draftLink">
                        <button type="button" class="btn-secondary" @click="viewVideo(index)">
                          <i class="fas fa-eye"></i>
                          View
                        </button>
                        <button type="button" class="btn-secondary" @click="replaceVideo(index)">
                          <i class="fas fa-edit"></i>
                          Replace
                        </button>
                        <button type="button" class="btn-secondary" @click="showThumbnail(index)">
                          <i class="fas fa-image"></i>
                          Thumbnail
                        </button>
                      </div>
                    </div>
                  </div>

                  <div class="form-group" v-if="collaborationForm.platform.length > 0">
                    <label>Video Post Links</label>
                    <div class="post-links">
                      <div 
                        v-for="platform in collaborationForm.platform" 
                        :key="platform"
                        class="post-link-item"
                      >
                        <label :for="`post-${platform}-${index}`">{{ platform }} Link</label>
                        <input 
                          :id="`post-${platform}-${index}`"
                          v-model="video.postLinks[platform]"
                          type="url"
                          placeholder="https://..."
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-actions sticky-actions">
              <button type="button" class="btn-secondary" @click="attemptCloseModal">
                Cancel / Exit
              </button>
              <button type="button" class="btn-danger" @click="haltCollaboration" v-if="collaborationModal.isEdit && collaborationModal.currentCollab.status !== 'Halted'">
                <i class="fas fa-pause"></i>
                Halt
              </button>
              <button type="button" class="btn-danger" @click="resumeCollaboration" v-if="collaborationModal.isEdit && collaborationModal.currentCollab.status === 'Halted'">
                <i class="fas fa-play"></i>
                Resume
              </button>
              <button type="button" class="btn-danger" @click="declineCollaboration" v-if="collaborationModal.isEdit">
                <i class="fas fa-times"></i>
                Decline
              </button>
              <button type="submit" class="btn-primary" :disabled="!isFormValid">
                <i class="fas fa-save"></i>
                {{ collaborationModal.isEdit ? 'Save' : 'Start' }} Collaboration
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Video Viewer Modal -->
    <div v-if="videoModal.visible" class="modal-overlay" @click="closeVideoModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Video Preview</h3>
          <button class="close-btn" @click="closeVideoModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="video-preview">
            <video 
              v-if="videoModal.videoUrl"
              :src="videoModal.videoUrl"
              controls
              width="100%"
            ></video>
            <div v-else class="video-placeholder">
              <i class="fas fa-video"></i>
              <p>No video available</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Thumbnail Modal -->
    <div v-if="thumbnailModal.visible" class="modal-overlay" @click="closeThumbnailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Video Thumbnail</h3>
          <button class="close-btn" @click="closeThumbnailModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="thumbnail-preview">
            <img 
              v-if="thumbnailModal.thumbnailUrl"
              :src="thumbnailModal.thumbnailUrl"
              alt="Video thumbnail"
            />
            <div v-else class="thumbnail-placeholder">
              <i class="fas fa-image"></i>
              <p>No thumbnail available</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { showSuccess, showError, showConfirm } from '@/utils/notification'
import { apiGet, apiPost, apiPut, apiDelete, apiPostForm } from '@/utils/api'

// Reactive state
const activeFilter = ref('On Going')
const collaborations = ref([])
const filters = ['On Going', 'Halted', 'Declined', 'Done']
const platforms = ['TikTok', 'Instagram', 'YouTube']

// Collaboration modal
const collaborationModal = reactive({
  visible: false,
  isEdit: false,
  currentCollab: null
})

// Collaboration form
const collaborationForm = reactive({
  name: '',
  channel: '',
  platform: [],
  collaboratorEmail: '',
  type: 'Paid',
  price: 0,
  numVideos: 1,
  videos: []
})

const originalFormStr = ref('')

const isDirty = computed(() => {
  return JSON.stringify(collaborationForm) !== originalFormStr.value
})

// Video modal
const videoModal = reactive({
  visible: false,
  videoUrl: ''
})

// Thumbnail modal
const thumbnailModal = reactive({
  visible: false,
  thumbnailUrl: ''
})

// Computed properties
const filteredCollaborations = computed(() => {
  return collaborations.value.filter(collab => collab.status === activeFilter.value)
})

const isFormValid = computed(() => {
  return collaborationForm.name && 
         collaborationForm.channel && 
         collaborationForm.platform.length > 0 && 
         collaborationForm.type && 
         collaborationForm.price >= 0 && 
         collaborationForm.numVideos > 0
})

// Methods
const setActiveFilter = (filter) => {
  activeFilter.value = filter
}

const fetchCollaborations = async () => {
  try {
    const res = await apiGet('/collaboration/collaborations');
    collaborations.value = (res.collaborations || []).map(c => ({
      id: c.id,
      name: c.name,
      channel: c.channel,
      platform: c.platform,
      collaboratorEmail: c.collaborator_email,
      type: c.type,
      price: c.agreed_price,
      numVideos: c.total_videos,
      completedVideos: c.completed_videos,
      status: c.status,
      createdAt: c.created_at,
      videos: [] 
    }));
  } catch (err) {
    console.error(err)
    showError('Failed to load collaborations');
  }
}

const createNewCollaboration = () => {
  resetForm()
  collaborationModal.isEdit = false
  originalFormStr.value = JSON.stringify(collaborationForm)
  collaborationModal.visible = true
}

const viewCollaboration = async (collab) => {
  try {
    const res = await apiGet(`/collaboration/collaborations/${collab.id}`)
    const fullCollab = res.collaboration
    
    Object.assign(collaborationForm, {
      ...collab,
      numVideos: fullCollab.total_videos || collab.numVideos,
      videos: fullCollab.videos.map(v => ({
         script: v.script || '',
         title: v.title || '',
         subtitles: v.subtitles_text || '',
         caption: v.caption || '',
         hashtags: (v.tags || []).join(' '),
         draftFile: null,
         draftLink: v.media_path || '',
         invitation: v.invitation || false,
         postLinks: v.post_links || {},
         paid: v.paid || false,
         done: v.done || false
      }))
    })
    
    if (collaborationForm.videos.length === 0) {
       collaborationForm.videos = generateVideoSections(collaborationForm.numVideos)
    }

    originalFormStr.value = JSON.stringify(collaborationForm)
    collaborationModal.isEdit = true
    collaborationModal.currentCollab = collab
    collaborationModal.visible = true
  } catch(err) {
    showError('Failed to load collaboration details')
  }
}

const editCollaboration = (collab) => {
  viewCollaboration(collab)
}

const deleteCollaboration = async (collab) => {
  const confirmed = await showConfirm(
    `Are you sure you want to delete "${collab.name}"?`,
    'Delete Collaboration'
  )
  
  if (confirmed) {
    try {
      await apiDelete(`/collaboration/collaborations/${collab.id}/delete`)
      showSuccess('Collaboration deleted successfully')
      fetchCollaborations()
    } catch(err) { showError('Failed to delete collaboration') }
  }
}

const attemptCloseModal = async () => {
  if (isDirty.value) {
    const confirmed = await showConfirm(
      'You have unsaved changes. Are you sure you want to exit without saving?',
      'Exit Without Saving'
    )
    if (!confirmed) return
  }
  closeCollaborationModal()
}

const closeCollaborationModal = () => {
  collaborationModal.visible = false
  resetForm()
}

const resetForm = () => {
  Object.assign(collaborationForm, {
    name: '',
    channel: '',
    platform: [],
    collaboratorEmail: '',
    type: 'Paid',
    price: 0,
    numVideos: 1,
    videos: generateVideoSections(1)
  })
}

const generateVideoSections = (num) => {
  const videos = []
  for (let i = 0; i < num; i++) {
    videos.push({
      script: '',
      title: '',
      subtitles: '',
      caption: '',
      hashtags: '',
      draftFile: null,
      draftLink: '',
      invitation: false,
      postLinks: {},
      paid: false,
      done: false
    })
  }
  return videos
}

const handleTypeChange = () => {
  if (collaborationForm.type === 'Product') {
    collaborationForm.price = 0
  }
}

const updateVideoSections = () => {
  const currentCount = collaborationForm.videos.length
  const newCount = collaborationForm.numVideos
  
  if (newCount > currentCount) {
    // Add new video sections
    for (let i = currentCount; i < newCount; i++) {
      collaborationForm.videos.push({
        script: '',
        title: '',
        subtitles: '',
        caption: '',
        hashtags: '',
        draftFile: null,
        draftLink: '',
        fileId: null,
        invitation: false,
        postLinks: {},
        paid: false,
        done: false
      })
    }
  } else if (newCount < currentCount) {
    // Remove excess video sections
    collaborationForm.videos.splice(newCount)
  }
}

const selectVideo = (index) => {
  const input = document.querySelector(`#videoInput-${index}`)
  if (input) {
    input.click()
  }
}

const handleVideoUpload = async (event, index) => {
  const file = event.target.files[0]
  if (file) {
    collaborationForm.videos[index].draftFile = file
    collaborationForm.videos[index].draftLink = ''
    collaborationForm.videos[index].fileId = null

    try {
      showSuccess(`Preparing ${file.name}...`)
      
      const ext = file.name.split('.').pop()
      const collabSlug = (collaborationForm.name || 'untitled').toLowerCase().replace(/\s+/g, '-')
      const newFileName = `${collabSlug}_video_${index + 1}.${ext}`
      
      // Look for identical old filename and purge it to prevent 409 conflict
      try {
         const filesRes = await apiGet('/drive/files?folder_path=/Collaboration')
         if (filesRes && filesRes.files) {
            const currentFileName = newFileName
            const existingFile = filesRes.files.find(f => (f.name === currentFileName || f.filename === currentFileName))
            if (existingFile) {
               await apiDelete(`/drive/file/${existingFile.id}`)
               console.log('Purged existing video file:', currentFileName)
            }
         }
      } catch(e) { console.warn('Purge check failed', e) }

      const renamedFile = new File([file], newFileName, { type: file.type })
      
      const formData = new FormData()
      formData.append('file', renamedFile)
      formData.append('folder_path', '/Collaboration')
      
      const uploadRes = await apiPostForm('/drive/upload', formData)
      
      if (uploadRes.file?.id) {
         collaborationForm.videos[index].fileId = uploadRes.file.id
         const shareRes = await apiPost('/drive/share', {
            file_id: uploadRes.file.id,
            access_level: 'public',
            permission_level: 'viewer',
            share_type: 'read'
         })
         
         if (shareRes.file?.public_share_link) {
            collaborationForm.videos[index].draftLink = shareRes.file.public_share_link
            showSuccess('Video uploaded and public link generated successfully!')
         } else {
            showSuccess('Upload complete.')
         }
      }
    } catch (err) {
      console.error(err)
      showError('Failed to automatically upload and generate link.')
    }
  }
}

const handleVideoLink = (index) => {
  collaborationForm.videos[index].draftFile = null
}

const viewVideo = (index) => {
  const video = collaborationForm.videos[index]
  if (video.draftFile) {
    videoModal.videoUrl = URL.createObjectURL(video.draftFile)
  } else if (video.draftLink) {
    videoModal.videoUrl = video.draftLink
  }
  videoModal.visible = true
}

const closeVideoModal = () => {
  videoModal.visible = false
  videoModal.videoUrl = ''
}

const replaceVideo = async (index) => {
  const video = collaborationForm.videos[index]
  // Purge any existing video with our naming convention to completely wipe old instances
  try {
     const collabSlug = (collaborationForm.name || 'untitled').toLowerCase().replace(/\s+/g, '-')
     const existingPrefix = `${collabSlug}_video_${index + 1}`
     
     const filesRes = await apiGet('/drive/files?folder_path=/Collaboration')
     if (filesRes && filesRes.files) {
        const matches = filesRes.files.filter(f => {
           const fname = f.name || f.filename || ''
           return fname.startsWith(existingPrefix)
        })
        for (const match of matches) {
           await apiDelete(`/drive/file/${match.id || match.file_id}`)
        }
     }
  } catch(e) { console.warn('Silent purge failed', e) }

  if (video.fileId) {
    try {
      await apiDelete(`/drive/file/${video.fileId}`)
    } catch (err) { }
  }
  
  video.draftFile = null
  video.draftLink = ''
  video.fileId = null
  selectVideo(index)
}

const showThumbnail = (index) => {
  // In a real app, this would generate and show thumbnail using ffmpeg
  thumbnailModal.thumbnailUrl = '/api/placeholder/320x180'
  thumbnailModal.visible = true
}

const closeThumbnailModal = () => {
  thumbnailModal.visible = false
  thumbnailModal.thumbnailUrl = ''
}

const saveCollaboration = async () => {
  try {
    const payload = {
      name: collaborationForm.name,
      channel: collaborationForm.channel,
      platforms: Array.isArray(collaborationForm.platform) ? collaborationForm.platform : [collaborationForm.platform],
      collaborator_email: collaborationForm.collaboratorEmail,
      type: collaborationForm.type,
      agreed_price: collaborationForm.price,
      videos: collaborationForm.videos.map(v => ({
         title: v.title,
         caption: v.caption,
         script: v.script,
         subtitles_text: v.subtitles,
         invitation: v.invitation,
         post_links: v.postLinks,
         tags: v.hashtags ? v.hashtags.split(' ').map(t => t.replace('#', '')) : [],
         subtitles_needed: false,
         media_path: v.draftLink || "",
         paid: v.paid,
         done: v.done
      }))
    };

    if (collaborationModal.isEdit) {
      await apiPut(`/collaboration/collaborations/${collaborationModal.currentCollab.id}`, payload);
      showSuccess('Collaboration updated successfully')
    } else {
      await apiPost('/collaboration/collaborations', payload);
      showSuccess('Collaboration created successfully')
    }
    
    // Explicitly reset original form string so close doesn't warn
    originalFormStr.value = JSON.stringify(collaborationForm)
    
    closeCollaborationModal()
    fetchCollaborations()
  } catch (error) {
    console.error('Error saving collaboration:', error)
    showError('Failed to save collaboration')
  }
}

const haltCollaboration = async () => {
  if (collaborationModal.currentCollab) {
    const confirmed = await showConfirm(
      'Are you sure you want to halt this collaboration?',
      'Halt Collaboration'
    )
    
    if (confirmed) {
      try {
        await apiPost(`/collaboration/collaborations/${collaborationModal.currentCollab.id}/halt`)
        showSuccess('Collaboration halted')
        closeCollaborationModal()
        fetchCollaborations()
      } catch(err) { showError('Failed to halt collaboration') }
    }
  }
}

const resumeCollaboration = async () => {
  if (collaborationModal.currentCollab) {
    const confirmed = await showConfirm(
      'Are you sure you want to resume this collaboration?',
      'Resume Collaboration'
    )
    
    if (confirmed) {
      try {
        await apiPost(`/collaboration/collaborations/${collaborationModal.currentCollab.id}/resume`)
        showSuccess('Collaboration resumed')
        closeCollaborationModal()
        fetchCollaborations()
      } catch(err) { showError('Failed to resume collaboration') }
    }
  }
}

const declineCollaboration = async () => {
  if (collaborationModal.currentCollab) {
    const reason = prompt('Please provide a reason for declining:')
    if (reason) {
      try {
        await apiPost(`/collaboration/collaborations/${collaborationModal.currentCollab.id}/decline`)
        showSuccess('Collaboration declined')
        closeCollaborationModal()
        fetchCollaborations()
      } catch(err) { showError('Failed to decline collaboration') }
    }
  }
}

onMounted(() => {
  fetchCollaborations()
})
</script>

<style scoped>
.collaboration {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.collaboration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.collaboration-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
}

.btn-danger {
  background: var(--danger-color);
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.filter-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 0.25rem;
}

.filter-tabs button {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  color: var(--text-secondary);
}

.filter-tabs button.active {
  background: var(--primary-color);
  color: white;
}

.collaboration-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.collaboration-card {
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.collaboration-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.collab-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.collab-info h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.collab-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.collab-meta span {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status.On.Going {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status.Halted {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status.Declined {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status.Done {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.collab-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.videos-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--glass-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.collab-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  padding: 0.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--glass-bg-hover);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-lg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1000px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h2,
.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.5rem;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 2rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.platform-checkboxes {
  display: flex;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-weight: 500;
  color: var(--text-primary);
}

.checkbox-label input[type="checkbox"] {
  width: 20px;
  height: 20px;
  accent-color: var(--primary-color);
}

.video-sections {
  margin-top: 2rem;
}

.video-sections h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.video-section {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.video-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.video-actions {
  display: flex;
  gap: 1rem;
}

.video-fields {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.expandable {
  resize: vertical;
  min-height: 60px;
}

.video-upload {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.upload-area {
  border: 2px dashed var(--glass-border);
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background: rgba(59, 130, 246, 0.05);
}

.upload-area i {
  font-size: 2rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.post-links {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.post-link-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--glass-border);
}

.video-preview,
.thumbnail-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.video-placeholder,
.thumbnail-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: var(--text-secondary);
}

.video-placeholder i,
.thumbnail-placeholder i {
  font-size: 3rem;
}

.video-preview video {
  max-width: 100%;
  border-radius: 8px;
}

.thumbnail-preview img {
  max-width: 100%;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .collaboration {
    padding: 1rem;
  }
  
  .collaboration-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .platform-checkboxes {
    flex-direction: column;
  }
  
  .video-actions {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
