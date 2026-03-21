<template>
  <div class="virus-scan">
    <div class="page-header">
      <h1><i class="fas fa-shield-virus"></i> Virus Scan Dashboard</h1>
      <p>Analyze URLs and files for security threats using VirusTotal</p>
    </div>

    <div class="scan-container">
      <!-- Tabs -->
      <div class="scan-tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'url' }]" 
          @click="activeTab = 'url'"
        >
          <i class="fas fa-link"></i> Scan URL
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'file' }]" 
          @click="activeTab = 'file'"
        >
          <i class="fas fa-file-upload"></i> Scan File
        </button>
      </div>

      <div class="card scan-card">
        <!-- URL Tab Content -->
        <div v-if="activeTab === 'url'" class="tab-content">
          <div class="input-group">
            <label>Enter URL to analyze</label>
            <div class="search-box">
              <input 
                type="text" 
                v-model="urlToScan" 
                placeholder="https://example.com"
                @keyup.enter="submitUrlScan"
              >
              <button class="btn btn-primary" @click="submitUrlScan" :disabled="loading">
                <i v-if="loading" class="fas fa-spinner fa-spin"></i>
                <span v-else>Analyze URL</span>
              </button>
            </div>
          </div>
        </div>

        <!-- File Tab Content -->
        <div v-else class="tab-content">
          <div 
            class="drop-zone" 
            @dragover.prevent="isDragging = true" 
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleFileDrop"
            :class="{ dragging: isDragging }"
            @click="$refs.fileInput.click()"
          >
            <input 
              type="file" 
              ref="fileInput" 
              class="hidden" 
              @change="handleFileSelect"
            >
            <div class="drop-content">
              <i class="fas fa-cloud-upload-alt"></i>
              <h3>Click or drag file back here</h3>
              <p>Maximum file size: 32MB</p>
              <div v-if="selectedFile" class="selected-file">
                <span class="file-name">{{ selectedFile.name }}</span>
                <span class="file-size">({{ formatSize(selectedFile.size) }})</span>
              </div>
            </div>
          </div>
          <div class="file-actions" v-if="selectedFile">
            <button class="btn btn-primary w-full" @click="submitFileScan" :disabled="loading">
              <i v-if="loading" class="fas fa-spinner fa-spin"></i>
              <span v-else>Analyze File</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Results Section -->
      <div v-if="scanResult" class="results-section">
        <div class="card result-header-card">
          <div class="result-overview">
            <div class="risk-meter">
              <div class="meter-score" :style="{ color: getRiskColor(scanResult.attributes.stats) }">
                {{ scanResult.attributes.stats.malicious }} / {{ getTotalEngines(scanResult.attributes.stats) }}
              </div>
              <div class="meter-label">Detection Engines</div>
            </div>
            
            <div class="result-details">
              <h2 class="threat-status" :style="{ color: getRiskColor(scanResult.attributes.stats) }">
                {{ getThreatLevel(scanResult.attributes.stats) }}
              </h2>
              <div class="result-meta">
                <span><i class="fas fa-id-card"></i> ID: <code>{{ scanResult.id }}</code></span>
                <span><i class="far fa-clock"></i> Logged: {{ formatDate(scanResult.attributes.date) }}</span>
              </div>
            </div>

            <div v-if="isScanning" class="polling-indicator">
              <i class="fas fa-circle-notch fa-spin"></i>
              Analysis in progress...
            </div>
          </div>
        </div>

        <!-- Engine Breakdown -->
        <div class="card engines-card">
          <div class="card-header">
            <h3>Detection Breakdown</h3>
            <div class="engine-filters">
              <span class="badge badge-malicious">{{ scanResult.attributes.stats.malicious }} Malicious</span>
              <span class="badge badge-suspicious">{{ scanResult.attributes.stats.suspicious }} Suspicious</span>
              <span class="badge badge-clean">{{ scanResult.attributes.stats.harmless }} Clean</span>
            </div>
          </div>
          
          <div class="engines-grid">
            <div 
              v-for="(res, engine) in scanResult.attributes.results" 
              :key="engine"
              :class="['engine-item', res.category]"
            >
              <div class="engine-info">
                <span class="engine-name">{{ engine }}</span>
                <span class="engine-category">{{ res.category }}</span>
              </div>
              <div class="engine-result">
                {{ res.result || 'Clean' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'

const activeTab = ref('url')
const urlToScan = ref('')
const selectedFile = ref(null)
const isDragging = ref(false)
const loading = ref(false)
const isScanning = ref(false)
const scanResult = ref(null)
const pollInterval = ref(null)

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    if (file.size > 32 * 1024 * 1024) {
      showError('File is too large (max 32MB)')
      return
    }
    selectedFile.value = file
  }
}

const handleFileDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const submitUrlScan = async () => {
  if (!urlToScan.value) return
  loading.value = true
  scanResult.value = null
  stopPolling()

  try {
    const formData = new FormData()
    formData.append('url', urlToScan.value)
    
    // Using regular axios for FormData
    const response = await apiPost('/scan/url', formData)
    if (response?.data?.id) {
      showSuccess('URL submitted for analysis')
      startPolling(response.data.id)
    }
  } catch (e) {
    showError(e.response?.data?.detail || 'Failed to submit URL')
  } finally {
    loading.value = false
  }
}

const submitFileScan = async () => {
  if (!selectedFile.value) return
  loading.value = true
  scanResult.value = null
  stopPolling()

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await apiPost('/scan/file', formData)
    if (response?.data?.id) {
      showSuccess('File submitted for analysis')
      startPolling(response.data.id)
    }
  } catch (e) {
    showError(e.response?.data?.detail || 'Failed to submit file')
  } finally {
    loading.value = false
  }
}

const startPolling = (id) => {
  isScanning.value = true
  fetchReport(id)
  pollInterval.value = setInterval(() => fetchReport(id), 5000)
}

const stopPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
  isScanning.value = false
}

const fetchReport = async (id) => {
  try {
    const r = await apiGet(`/scan/report/${id}`)
    if (r?.data) {
      scanResult.value = r.data
      if (r.data.attributes.status === 'completed') {
        stopPolling()
        showSuccess('Analysis complete')
      }
    }
  } catch (e) {
    console.error('Polling error:', e)
    stopPolling()
  }
}

const getTotalEngines = (stats) => {
  return stats.malicious + stats.suspicious + stats.harmless + stats.undetected
}

const getRiskColor = (stats) => {
  if (stats.malicious > 0) return '#ef4444'
  if (stats.suspicious > 0) return '#f59e0b'
  return '#10b981'
}

const getThreatLevel = (stats) => {
  if (stats.malicious >= 5) return 'CRITICAL THREAT DETECTED'
  if (stats.malicious > 0) return 'MALICIOUS ACTIVITY DETECTED'
  if (stats.suspicious > 0) return 'SUSPICIOUS OBJECT'
  return 'CLEAN / NO THREATS FOUND'
}

const formatDate = (ts) => {
  if (!ts) return 'N/A'
  return new Date(ts * 1000).toLocaleString()
}

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.virus-scan {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.scan-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.scan-tabs {
  display: flex;
  gap: 1rem;
  padding: 0.5rem;
  background: var(--glass-bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  width: fit-content;
  margin: 0 auto;
}

.tab-btn {
  background: none;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  color: var(--text-secondary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-btn.active {
  background: var(--primary-color);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.scan-card {
  padding: 2.5rem;
}

.search-box {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.search-box input {
  flex: 1;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 0.8rem 1.2rem;
  color: var(--text-primary);
  font-size: 1rem;
}

.drop-zone {
  border: 2px dashed var(--glass-border);
  border-radius: 16px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.02);
}

.drop-zone.dragging {
  border-color: var(--primary-color);
  background: rgba(59, 130, 246, 0.05);
}

.drop-content i {
  font-size: 3rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
  opacity: 0.8;
}

.selected-file {
  margin-top: 1.5rem;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  border-radius: 8px;
  display: inline-flex;
  gap: 1rem;
  align-items: center;
}

.file-name { font-weight: 600; color: var(--text-primary); }
.file-size { color: var(--text-tertiary); font-size: 0.85rem; }

.file-actions {
  margin-top: 1.5rem;
}

/* Results */
.results-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: fadeIn 0.5s ease-out;
}

.result-header-card {
  padding: 2rem;
}

.result-overview {
  display: flex;
  align-items: center;
  gap: 3rem;
}

.risk-meter {
  text-align: center;
  border-right: 1px solid var(--glass-border);
  padding-right: 3rem;
}

.meter-score {
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1;
}

.meter-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-tertiary);
  margin-top: 0.5rem;
}

.threat-status {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.result-meta {
  display: flex;
  gap: 2rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.result-meta code {
  background: var(--glass-bg-primary);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.polling-indicator {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 0.9rem;
}

/* Engines Grid */
.engines-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.engine-filters {
  display: flex;
  gap: 0.5rem;
}

.badge {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge-malicious { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.badge-suspicious { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.badge-clean { background: rgba(16, 185, 129, 0.15); color: #10b981; }

.engines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.engine-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.engine-item:hover {
  transform: translateY(-2px);
  background: var(--glass-bg-hover);
}

.engine-item.malicious { border-left: 4px solid #ef4444; }
.engine-item.suspicious { border-left: 4px solid #f59e0b; }
.engine-item.harmless { border-left: 4px solid #10b981; }

.engine-info {
  display: flex;
  flex-direction: column;
}

.engine-name {
  font-weight: 700;
  color: var(--text-primary);
}

.engine-category {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  text-transform: capitalize;
}

.engine-result {
  font-size: 0.85rem;
  font-weight: 600;
}

.malicious .engine-result { color: #ef4444; }
.suspicious .engine-result { color: #f59e0b; }
.harmless .engine-result { color: #10b981; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .result-overview {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  .risk-meter {
    border-right: none;
    padding-right: 0;
  }
}
</style>
