<template>
  <div class="embed-view" :class="{ 'blur-content': devToolsDetected }">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading secure content...</p>
    </div>

    <div v-else-if="is404" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <h2>Link Invalid or Expired</h2>
      <p>This share link is no longer available.</p>
    </div>

    <div v-else-if="requiresPassword && !isVerified" class="password-overlay">
      <div class="password-card glass-panel">
        <i class="fas fa-lock-alt text-4xl mb-4 text-gold"></i>
        <h2>Password Protected</h2>
        <p>Enter the password to access this file.</p>
        <input 
          type="password" 
          v-model="password" 
          placeholder="Enter password..." 
          class="glass-input"
          @keyup.enter="verifyPassword"
        >
        <button class="btn-verify" @click="verifyPassword">Unlock Content</button>
      </div>
    </div>

    <div v-else class="content-container">
      <div class="preview-area">
        <template v-if="isImage">
          <canvas v-if="metadata.permission_level === 'visitor'" ref="imageCanvas" class="preview-canvas"></canvas>
          <img v-else :src="previewUrl" alt="Preview" class="preview-img">
        </template>
        <template v-else-if="isVideo">
          <video :src="previewUrl" controls class="preview-video" oncontextmenu="return false;" controlsList="nodownload"></video>
        </template>
        <template v-else>
          <div class="file-icon-box">
             <i :class="['fas', getFileIcon(metadata.name), 'icon-huge']"></i>
             <h3>{{ metadata.name }}</h3>
             <p>{{ formatSize(metadata.size) }}</p>
          </div>
        </template>
      </div>

      <!-- DevTools Warning Overlay -->
      <div v-if="devToolsDetected" class="devtools-warning">
        <i class="fas fa-user-secret text-6xl mb-4"></i>
        <h2>Security Breach Detected</h2>
        <p>Please close Developer Tools to view this high-security content.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiGet, apiPost } from '@/utils/api'
import { showError } from '@/utils/notification'

const route = useRoute()
const hash = route.params.hash
const fileId = route.query.file_id

const loading = ref(true)
const is404 = ref(false)
const metadata = ref(null)
const password = ref('')
const isVerified = ref(false)
const previewUrl = ref('')
const imageCanvas = ref(null)
const devToolsDetected = ref(false)

const requiresPassword = computed(() => metadata.value?.has_password)

onMounted(async () => {
  await fetchMetadata()
  if (!requiresPassword.value) {
    await initializeView()
  }
})

const fetchMetadata = async () => {
  try {
    const url = fileId ? `/public/access/${hash}?file_id=${fileId}` : `/public/access/${hash}`
    metadata.value = await apiGet(url)
    if (!metadata.value) throw new Error('Not found')
  } catch (err) {
    is404.value = true
  }
  loading.value = false
}

const verifyPassword = async () => {
  try {
    const res = await apiPost(`/public/verify/${hash}`, { password: password.value })
    if (res.token) {
      isVerified.value = true
      await initializeView()
    }
  } catch (err) {
    showError('Invalid password')
  }
}

const initializeView = async () => {
  try {
    const pId = fileId || metadata.value.id
    const tokenRes = await apiGet(`/public/preview-token/${hash}/${pId}?password=${password.value}`)
    const token = tokenRes.token
    previewUrl.value = `/api/public/preview/${token}`

    if (isImage.value && metadata.value.permission_level === 'visitor') {
      setTimeout(renderToCanvas, 500)
    }
  } catch (err) {
    console.error('Failed to initialize view:', err)
  }
}

const renderToCanvas = () => {
  if (!imageCanvas.value || !previewUrl.value) return
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => {
    const canvas = imageCanvas.value
    const ctx = canvas.getContext('2d')
    canvas.width = img.width
    canvas.height = img.height
    ctx.drawImage(img, 0, 0)
    // Anti-extraction: clear the URL
    previewUrl.value = ''
  }
  img.src = previewUrl.value
}

const isImage = computed(() => {
  if (!metadata.value) return false
  const ext = metadata.value.name.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)
})

const isVideo = computed(() => {
  if (!metadata.value) return false
  const ext = metadata.value.name.split('.').pop().toLowerCase()
  return ['mp4', 'webm', 'ogg', 'mkv'].includes(ext)
})

const getFileIcon = (name) => {
  const ext = name.split('.').pop().toLowerCase()
  const icons = {
    pdf: 'fa-file-pdf',
    doc: 'fa-file-word',
    docx: 'fa-file-word',
    xls: 'fa-file-excel',
    xlsx: 'fa-file-excel',
    zip: 'fa-file-archive',
    rar: 'fa-file-archive',
    txt: 'fa-file-alt',
  }
  return icons[ext] || 'fa-file'
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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
</script>

<style scoped>
.embed-view {
  width: 100vw;
  height: 100vh;
  background: #000;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  user-select: none;
  -webkit-user-select: none;
}

.content-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.preview-area {
  max-width: 95%;
  max-height: 95%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-img, .preview-canvas, .preview-video {
  max-width: 100%;
  max-height: 100vh;
  object-fit: contain;
  box-shadow: 0 0 50px rgba(0,0,0,0.5);
}

.file-icon-box {
  text-align: center;
}

.icon-huge {
  font-size: 8rem;
  color: #fbbf24;
  margin-bottom: 20px;
}

.password-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0b;
}

.password-card {
  padding: 3rem;
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.glass-input {
  width: 100%;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  padding: 12px;
  border-radius: 8px;
  color: #fff;
  margin: 20px 0;
}

.btn-verify {
  width: 100%;
  background: #fbbf24;
  color: #000;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.loading-state, .error-state {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255,255,255,0.1);
  border-top-color: #fbbf24;
  border-radius: 50%;
  animation: rotate 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes rotate {
  to { transform: rotate(360deg); }
}

.devtools-warning {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.blur-content .content-container {
  filter: blur(20px);
}
</style>
