<template>
  <div class="playground">
    <div class="page-header">
      <h1>Code Playground</h1>
      <p>Interactive code editor with live preview and execution</p>
    </div>

    <!-- Editor Configuration -->
    <div class="editor-section">
      <div class="section-header">
        <h2>Code Editor</h2>
        <div class="header-actions">
          <div class="language-selector">
            <select v-model="selectedLanguage" @change="changeLanguage">
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="python">Python</option>
              <option value="html">HTML</option>
              <option value="css">CSS</option>
              <option value="json">JSON</option>
              <option value="sql">SQL</option>
            </select>
          </div>
          <div class="theme-selector">
            <select v-model="selectedTheme" @change="changeTheme">
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="monokai">Monokai</option>
              <option value="github">GitHub</option>
            </select>
          </div>
          <button class="format-btn" @click="formatCode">
            <i class="fas fa-magic"></i>
            Format
          </button>
        </div>
      </div>

      <div class="editor-container">
        <div class="editor-panel">
          <div class="editor-tabs">
            <div 
              v-for="(tab, index) in tabs" 
              :key="index"
              :class="['tab', { active: activeTab === index }]"
              @click="switchTab(index)"
            >
              <span class="tab-name">{{ tab.name }}</span>
              <button 
                class="tab-close"
                @click.stop="closeTab(index)"
                v-if="tabs.length > 1"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
            <button class="tab-add" @click="addTab">
              <i class="fas fa-plus"></i>
            </button>
          </div>
          
          <div class="editor-wrapper">
            <textarea
              ref="codeEditor"
              v-model="tabs[activeTab].content"
              :placeholder="getPlaceholder()"
              @input="onCodeChange"
              @keydown="handleKeyDown"
              spellcheck="false"
            ></textarea>
            <div class="line-numbers">
              <div 
                v-for="line in lineCount" 
                :key="line"
                class="line-number"
              >
                {{ line }}
              </div>
            </div>
          </div>
        </div>

        <div class="preview-panel">
          <div class="preview-header">
            <h3>Live Preview</h3>
            <div class="preview-actions">
              <button class="refresh-btn" @click="refreshPreview">
                <i class="fas fa-sync"></i>
              </button>
              <button class="fullscreen-btn" @click="toggleFullscreen">
                <i class="fas fa-expand"></i>
              </button>
            </div>
          </div>
          <div class="preview-content" ref="previewContent">
            <iframe
              v-if="selectedLanguage === 'html'"
              ref="previewFrame"
              :srcdoc="previewHtml"
              class="preview-frame"
            ></iframe>
            <pre v-else class="code-preview">{{ previewOutput }}</pre>
          </div>
        </div>
      </div>

      <div class="editor-footer">
        <div class="editor-info">
          <span class="line-info">Line {{ currentLine }}, Column {{ currentColumn }}</span>
          <span class="language-info">{{ selectedLanguage }}</span>
          <span class="encoding-info">UTF-8</span>
        </div>
        <div class="editor-actions">
          <button class="run-btn" @click="runCode">
            <i class="fas fa-play"></i>
            Run
          </button>
          <button class="save-btn" @click="saveCode">
            <i class="fas fa-save"></i>
            Save
          </button>
          <button class="share-btn" @click="shareCode">
            <i class="fas fa-share"></i>
            Share
          </button>
        </div>
      </div>
    </div>

    <!-- Console Output -->
    <div class="console-section">
      <div class="section-header">
        <h2>Console Output</h2>
        <div class="header-actions">
          <button class="clear-btn" @click="clearConsole">
            <i class="fas fa-trash"></i>
            Clear
          </button>
          <div class="filter-dropdown">
            <select v-model="consoleFilter" @change="filterConsole">
              <option value="all">All</option>
              <option value="log">Logs</option>
              <option value="error">Errors</option>
              <option value="warning">Warnings</option>
            </select>
          </div>
        </div>
      </div>

      <div class="console-content" ref="consoleContent">
        <div 
          v-for="(log, index) in filteredConsoleLogs" 
          :key="index"
          :class="['console-log', log.type]"
        >
          <span class="log-timestamp">{{ formatTime(log.timestamp) }}</span>
          <span class="log-message">{{ log.message }}</span>
          <button 
            class="log-copy"
            @click="copyLog(log.message)"
          >
            <i class="fas fa-copy"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Code Snippets -->
    <div class="snippets-section">
      <div class="section-header">
        <h2>Code Snippets</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="snippetFilter" @change="filterSnippets">
              <option value="">All Categories</option>
              <option value="algorithms">Algorithms</option>
              <option value="data-structures">Data Structures</option>
              <option value="utilities">Utilities</option>
              <option value="templates">Templates</option>
            </select>
          </div>
          <button class="create-snippet-btn" @click="showSnippetModal = true">
            <i class="fas fa-plus"></i>
            Create Snippet
          </button>
        </div>
      </div>

      <div class="snippets-grid">
        <div 
          v-for="snippet in filteredSnippets" 
          :key="snippet.id"
          class="snippet-card"
          @click="insertSnippet(snippet)"
        >
          <div class="snippet-header">
            <div class="snippet-icon">
              <i :class="getSnippetIcon(snippet.category)"></i>
            </div>
            <div class="snippet-language">{{ snippet.language }}</div>
          </div>

          <div class="snippet-content">
            <h4>{{ snippet.title }}</h4>
            <p>{{ snippet.description }}</p>
            <pre class="snippet-code">{{ snippet.code.substring(0, 100) }}{{ snippet.code.length > 100 ? '...' : '' }}</pre>
          </div>

          <div class="snippet-footer">
            <span class="snippet-category">{{ snippet.category }}</span>
            <span class="snippet-uses">{{ snippet.uses }} uses</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Execution History -->
    <div class="history-section">
      <div class="section-header">
        <h2>Execution History</h2>
        <div class="header-actions">
          <button class="clear-history-btn" @click="clearHistory">
            <i class="fas fa-trash"></i>
            Clear History
          </button>
        </div>
      </div>

      <div class="history-list">
        <div 
          v-for="execution in executionHistory" 
          :key="execution.id"
          class="history-item"
          :class="{ 'success': execution.status === 'success', 'error': execution.status === 'error' }"
        >
          <div class="history-header">
            <div class="history-info">
              <span class="history-language">{{ execution.language }}</span>
              <span class="history-time">{{ formatDateTime(execution.timestamp) }}</span>
            </div>
            <div class="history-status">
              <span :class="['status-badge', execution.status]">{{ execution.status }}</span>
            </div>
          </div>

          <div class="history-content">
            <pre class="history-code">{{ execution.code.substring(0, 200) }}{{ execution.code.length > 200 ? '...' : '' }}</pre>
            <div class="history-output" v-if="execution.output">
              <strong>Output:</strong>
              <pre>{{ execution.output }}</pre>
            </div>
          </div>

          <div class="history-actions">
            <button class="action-btn restore" @click="restoreExecution(execution)">
              <i class="fas fa-undo"></i>
              Restore
            </button>
            <button class="action-btn rerun" @click="rerunExecution(execution)">
              <i class="fas fa-redo"></i>
              Rerun
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Snippet Modal -->
    <div v-if="showSnippetModal" class="modal-overlay" @click="closeSnippetModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create Code Snippet</h2>
          <button class="close-btn" @click="closeSnippetModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="snippet-form">
            <div class="form-group">
              <label>Snippet Title *</label>
              <input 
                v-model="snippetForm.title" 
                type="text" 
                placeholder="Enter snippet title"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="snippetForm.description" 
                placeholder="Describe your snippet"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Language *</label>
                <select v-model="snippetForm.language" required>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="python">Python</option>
                  <option value="html">HTML</option>
                  <option value="css">CSS</option>
                  <option value="json">JSON</option>
                  <option value="sql">SQL</option>
                </select>
              </div>

              <div class="form-group">
                <label>Category *</label>
                <select v-model="snippetForm.category" required>
                  <option value="algorithms">Algorithms</option>
                  <option value="data-structures">Data Structures</option>
                  <option value="utilities">Utilities</option>
                  <option value="templates">Templates</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Code *</label>
              <textarea 
                v-model="snippetForm.code" 
                placeholder="Enter your code snippet"
                rows="10"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label>Tags</label>
              <div class="tags-container">
                <div 
                  v-for="(tag, index) in snippetForm.tags" 
                  :key="index"
                  class="tag-item"
                >
                  <span class="tag-text">{{ tag }}</span>
                  <button 
                    class="tag-remove"
                    @click="removeTag(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <div class="tag-input-container">
                  <input 
                    v-model="newTag" 
                    type="text" 
                    placeholder="Add tag"
                    @keydown.enter="addTag"
                  />
                  <button class="tag-add" @click="addTag">
                    <i class="fas fa-plus"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeSnippetModal">Cancel</button>
          <button class="btn-primary" @click="createSnippet">
            <i class="fas fa-plus"></i>
            Create Snippet
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const selectedLanguage = ref('javascript')
const selectedTheme = ref('dark')
const activeTab = ref(0)
const consoleFilter = ref('all')
const snippetFilter = ref('')
const showSnippetModal = ref(false)
const newTag = ref('')

// Editor refs
const codeEditor = ref(null)
const previewContent = ref(null)
const consoleContent = ref(null)

// Editor state
const currentLine = ref(1)
const currentColumn = ref(1)
const lineCount = ref(1)

// Tabs
const tabs = ref([
  { name: 'main.js', content: '', language: 'javascript' }
])

// Console logs
const consoleLogs = ref([])

// Snippets
const snippets = ref([
  {
    id: 1,
    title: 'Quick Sort',
    description: 'Efficient sorting algorithm implementation',
    language: 'javascript',
    category: 'algorithms',
    code: 'function quickSort(arr) {\n  if (arr.length <= 1) return arr;\n  const pivot = arr[arr.length - 1];\n  const left = [];\n  const right = [];\n  \n  for (let i = 0; i < arr.length - 1; i++) {\n    if (arr[i] < pivot) left.push(arr[i]);\n    else right.push(arr[i]);\n  }\n  \n  return [...quickSort(left), pivot, ...quickSort(right)];\n}',
    uses: 156
  },
  {
    id: 2,
    title: 'Binary Search',
    description: 'Binary search implementation for sorted arrays',
    language: 'javascript',
    category: 'algorithms',
    code: 'function binarySearch(arr, target) {\n  let left = 0;\n  let right = arr.length - 1;\n  \n  while (left <= right) {\n    const mid = Math.floor((left + right) / 2);\n    if (arr[mid] === target) return mid;\n    if (arr[mid] < target) left = mid + 1;\n    else right = mid - 1;\n  }\n  \n  return -1;\n}',
    uses: 89
  },
  {
    id: 3,
    title: 'Debounce Function',
    description: 'Utility function to debounce function calls',
    language: 'javascript',
    category: 'utilities',
    code: 'function debounce(func, delay) {\n  let timeoutId;\n  return function(...args) {\n    clearTimeout(timeoutId);\n    timeoutId = setTimeout(() => func.apply(this, args), delay);\n  };\n}',
    uses: 234
  }
])

// Execution history
const executionHistory = ref([])

// Snippet form
const snippetForm = reactive({
  title: '',
  description: '',
  language: 'javascript',
  category: 'utilities',
  code: '',
  tags: []
})

// Computed properties
const previewOutput = computed(() => {
  try {
    if (selectedLanguage.value === 'javascript') {
      return eval(tabs.value[activeTab.value].content)
    }
    return tabs.value[activeTab.value].content
  } catch (error) {
    return `Error: ${error.message}`
  }
})

const previewHtml = computed(() => {
  if (selectedLanguage.value === 'html') {
    return tabs.value[activeTab.value].content
  }
  return ''
})

const filteredConsoleLogs = computed(() => {
  if (consoleFilter.value === 'all') {
    return consoleLogs.value
  }
  return consoleLogs.value.filter(log => log.type === consoleFilter.value)
})

const filteredSnippets = computed(() => {
  if (!snippetFilter.value) {
    return snippets.value
  }
  return snippets.value.filter(snippet => snippet.category === snippetFilter.value)
})

// Methods
const changeLanguage = () => {
  tabs.value[activeTab.value].language = selectedLanguage.value
  updatePreview()
}

const changeTheme = () => {
  // Apply theme to editor
  if (codeEditor.value) {
    codeEditor.value.className = `editor-textarea theme-${selectedTheme.value}`
  }
}

const formatCode = () => {
  try {
    // Simple formatting logic
    let formatted = tabs.value[activeTab.value].content
    if (selectedLanguage.value === 'javascript' || selectedLanguage.value === 'typescript') {
      formatted = formatted
        .replace(/;/g, ';\n')
        .replace(/{/g, ' {\n  ')
        .replace(/}/g, '\n}')
        .replace(/\n\s*\n/g, '\n')
    }
    tabs.value[activeTab.value].content = formatted
    showSuccess('Code formatted successfully')
  } catch (error) {
    showError('Failed to format code')
  }
}

const getPlaceholder = () => {
  const placeholders = {
    javascript: '// Write your JavaScript code here...',
    typescript: '// Write your TypeScript code here...',
    python: '# Write your Python code here...',
    html: '<!-- Write your HTML code here... -->',
    css: '/* Write your CSS code here... */',
    json: '{\n  "key": "value"\n}',
    sql: '-- Write your SQL query here...'
  }
  return placeholders[selectedLanguage.value] || '// Write your code here...'
}

const onCodeChange = () => {
  updateLineCount()
  updatePreview()
}

const handleKeyDown = (event) => {
  // Handle tab key for indentation
  if (event.key === 'Tab') {
    event.preventDefault()
    const textarea = event.target
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const value = textarea.value
    
    textarea.value = value.substring(0, start) + '  ' + value.substring(end)
    textarea.selectionStart = textarea.selectionEnd = start + 2
  }
  
  // Handle Ctrl+S for save
  if (event.ctrlKey && event.key === 's') {
    event.preventDefault()
    saveCode()
  }
}

const updateLineCount = () => {
  const content = tabs.value[activeTab.value].content
  lineCount.value = content.split('\n').length
}

const updatePreview = () => {
  // Debounced preview update
  clearTimeout(previewTimeout)
  previewTimeout = setTimeout(() => {
    // Preview is updated via computed properties
  }, 500)
}

let previewTimeout

const switchTab = (index) => {
  activeTab.value = index
  selectedLanguage.value = tabs.value[index].language
  updateLineCount()
}

const addTab = () => {
  const newTab = {
    name: `untitled-${tabs.value.length + 1}.${getFileExtension()}`,
    content: '',
    language: selectedLanguage.value
  }
  tabs.value.push(newTab)
  activeTab.value = tabs.value.length - 1
}

const closeTab = (index) => {
  if (tabs.value.length > 1) {
    tabs.value.splice(index, 1)
    if (activeTab.value >= tabs.value.length) {
      activeTab.value = tabs.value.length - 1
    }
  }
}

const getFileExtension = () => {
  const extensions = {
    javascript: 'js',
    typescript: 'ts',
    python: 'py',
    html: 'html',
    css: 'css',
    json: 'json',
    sql: 'sql'
  }
  return extensions[selectedLanguage.value] || 'txt'
}

const runCode = () => {
  const code = tabs.value[activeTab.value].content
  const language = selectedLanguage.value
  
  try {
    let output
    if (language === 'javascript') {
      output = eval(code)
    } else {
      output = 'Code execution not supported for this language'
    }
    
    const execution = {
      id: Date.now(),
      language,
      code,
      output: typeof output === 'string' ? output : JSON.stringify(output),
      status: 'success',
      timestamp: new Date().toISOString()
    }
    
    executionHistory.value.unshift(execution)
    addConsoleLog('info', `Code executed successfully. Output: ${execution.output}`)
    showSuccess('Code executed successfully')
  } catch (error) {
    const execution = {
      id: Date.now(),
      language,
      code,
      output: error.message,
      status: 'error',
      timestamp: new Date().toISOString()
    }
    
    executionHistory.value.unshift(execution)
    addConsoleLog('error', `Execution error: ${error.message}`)
    showError('Code execution failed')
  }
}

const saveCode = () => {
  const code = tabs.value[activeTab.value].content
  const blob = new Blob([code], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = tabs.value[activeTab.value].name
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  showSuccess('Code saved successfully')
}

const shareCode = async () => {
  try {
    // const response = await apiPost('/playground/share', {
    //   code: tabs.value[activeTab.value].content,
    //   language: selectedLanguage.value
    // })
    // if (response.success) {
    //   navigator.clipboard.writeText(response.shareUrl)
    //   showSuccess('Code shared! URL copied to clipboard')
    // }
    
    // For demo, simulate share
    const shareUrl = `https://playground.example.com/share/${Date.now()}`
    navigator.clipboard.writeText(shareUrl)
    showSuccess('Code shared! URL copied to clipboard')
  } catch (error) {
    console.error('Error sharing code:', error)
    showError('Failed to share code')
  }
}

const refreshPreview = () => {
  updatePreview()
  showSuccess('Preview refreshed')
}

const toggleFullscreen = () => {
  if (previewContent.value) {
    if (!document.fullscreenElement) {
      previewContent.value.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }
}

const addConsoleLog = (type, message) => {
  consoleLogs.value.unshift({
    type,
    message,
    timestamp: new Date().toISOString()
  })
  
  // Keep only last 100 logs
  if (consoleLogs.value.length > 100) {
    consoleLogs.value = consoleLogs.value.slice(0, 100)
  }
  
  nextTick(() => {
    if (consoleContent.value) {
      consoleContent.value.scrollTop = 0
    }
  })
}

const clearConsole = () => {
  consoleLogs.value = []
  showSuccess('Console cleared')
}

const filterConsole = () => {
  // This is reactive, no additional action needed
}

const copyLog = (message) => {
  navigator.clipboard.writeText(message)
  showSuccess('Log copied to clipboard')
}

const getSnippetIcon = (category) => {
  const icons = {
    'algorithms': 'fas fa-chart-line',
    'data-structures': 'fas fa-sitemap',
    'utilities': 'fas fa-tools',
    'templates': 'fas fa-file-code'
  }
  return icons[category] || 'fas fa-code'
}

const insertSnippet = (snippet) => {
  tabs.value[activeTab.value].content += '\n' + snippet.code
  updateLineCount()
  showSuccess(`Snippet "${snippet.title}" inserted`)
}

const filterSnippets = () => {
  // This is reactive, no additional action needed
}

const addTag = () => {
  if (newTag.value.trim() && !snippetForm.tags.includes(newTag.value.trim())) {
    snippetForm.tags.push(newTag.value.trim())
    newTag.value = ''
  }
}

const removeTag = (index) => {
  snippetForm.tags.splice(index, 1)
}

const createSnippet = async () => {
  if (!snippetForm.title || !snippetForm.code) {
    showError('Please fill in title and code')
    return
  }

  try {
    // const response = await apiPost('/playground/snippets', snippetForm)
    // if (response.success) {
    //   snippets.value.unshift(response.snippet)
    //   showSuccess('Snippet created successfully')
    //   closeSnippetModal()
    //   resetSnippetForm()
    // }
    
    // For demo, simulate creation
    const newSnippet = {
      id: Date.now(),
      ...snippetForm,
      uses: 0
    }
    
    snippets.value.unshift(newSnippet)
    showSuccess('Snippet created successfully')
    closeSnippetModal()
    resetSnippetForm()
  } catch (error) {
    console.error('Error creating snippet:', error)
    showError('Failed to create snippet')
  }
}

const closeSnippetModal = () => {
  showSnippetModal.value = false
  resetSnippetForm()
}

const resetSnippetForm = () => {
  Object.assign(snippetForm, {
    title: '',
    description: '',
    language: 'javascript',
    category: 'utilities',
    code: '',
    tags: []
  })
}

const restoreExecution = (execution) => {
  tabs.value[activeTab.value].content = execution.code
  selectedLanguage.value = execution.language
  updateLineCount()
  showSuccess('Code restored from history')
}

const rerunExecution = (execution) => {
  tabs.value[activeTab.value].content = execution.code
  selectedLanguage.value = execution.language
  updateLineCount()
  runCode()
}

const clearHistory = async () => {
  const confirmed = await showConfirm('Are you sure you want to clear execution history?')
  if (!confirmed) return

  try {
    // const response = await apiDelete('/playground/history')
    // if (response.success) {
    //   executionHistory.value = []
    //   showSuccess('History cleared successfully')
    // }
    
    // For demo, simulate clear
    executionHistory.value = []
    showSuccess('History cleared successfully')
  } catch (error) {
    console.error('Error clearing history:', error)
    showError('Failed to clear history')
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const formatDateTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

// Lifecycle
onMounted(() => {
  // Initialize editor
  changeTheme()
  updateLineCount()
  
  // Load saved data
  const savedCode = localStorage.getItem('playground-code')
  if (savedCode) {
    tabs.value[0].content = savedCode
  }
  
  const savedHistory = localStorage.getItem('playground-history')
  if (savedHistory) {
    executionHistory.value = JSON.parse(savedHistory)
  }
})

onUnmounted(() => {
  // Save current code
  localStorage.setItem('playground-code', tabs.value[activeTab.value].content)
  localStorage.setItem('playground-history', JSON.stringify(executionHistory.value))
})
</script>

<style scoped>
.playground {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.editor-section,
.console-section,
.snippets-section,
.history-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.language-selector select,
.theme-selector select,
.filter-dropdown select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.format-btn,
.clear-btn,
.clear-history-btn,
.refresh-btn,
.fullscreen-btn,
.create-snippet-btn {
  padding: 0.75rem 1.25rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.format-btn:hover,
.clear-btn:hover,
.clear-history-btn:hover,
.refresh-btn:hover,
.fullscreen-btn:hover,
.create-snippet-btn:hover {
  background: var(--primary-hover);
}

.editor-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  height: 500px;
}

.editor-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-tabs {
  display: flex;
  background: var(--glass-bg-primary);
  border-radius: 8px 8px 0 0;
  padding: 0.5rem;
  gap: 0.25rem;
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-secondary);
}

.tab.active {
  background: var(--glass-bg-tertiary);
  color: var(--text-primary);
}

.tab-name {
  font-size: 0.9rem;
  font-weight: 500;
}

.tab-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.tab-close:hover {
  background: var(--danger-color);
  color: white;
}

.tab-add {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.tab-add:hover {
  background: var(--primary-color);
  color: white;
}

.editor-wrapper {
  flex: 1;
  display: flex;
  position: relative;
  background: var(--glass-bg-primary);
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}

.editor-textarea {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: var(--text-primary);
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 1rem;
  resize: none;
  white-space: pre;
  overflow-wrap: normal;
  overflow-x: auto;
}

.editor-textarea.theme-dark {
  background: #1e1e1e;
  color: #d4d4d4;
}

.editor-textarea.theme-light {
  background: #ffffff;
  color: #24292e;
}

.line-numbers {
  position: absolute;
  left: 0;
  top: 0;
  width: 50px;
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 1rem 0.5rem;
  text-align: right;
  user-select: none;
}

.line-number {
  line-height: 1.5;
}

.preview-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--glass-bg-primary);
  border-radius: 8px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-bottom: 1px solid var(--glass-border);
}

.preview-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.preview-actions {
  display: flex;
  gap: 0.5rem;
}

.preview-content {
  flex: 1;
  overflow: auto;
  background: white;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.code-preview {
  padding: 1rem;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-top: 1px solid var(--glass-border);
}

.editor-info {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.editor-actions {
  display: flex;
  gap: 0.5rem;
}

.run-btn,
.save-btn,
.share-btn {
  padding: 0.75rem 1.25rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.run-btn:hover,
.save-btn:hover,
.share-btn:hover {
  background: var(--primary-hover);
}

.run-btn {
  background: var(--success-color);
}

.run-btn:hover {
  background: var(--success-hover);
}

.console-content {
  height: 300px;
  overflow-y: auto;
  background: var(--glass-bg-primary);
  border-radius: 8px;
  padding: 1rem;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 14px;
}

.console-log {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  border-radius: 6px;
  align-items: flex-start;
}

.console-log.log {
  background: rgba(59, 130, 246, 0.1);
  border-left: 3px solid #3b82f6;
}

.console-log.error {
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid #ef4444;
}

.console-log.warning {
  background: rgba(245, 158, 11, 0.1);
  border-left: 3px solid #f59e0b;
}

.log-timestamp {
  font-size: 0.8rem;
  color: var(--text-secondary);
  min-width: 80px;
}

.log-message {
  flex: 1;
  color: var(--text-primary);
}

.log-copy {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.log-copy:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.snippets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.snippet-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.snippet-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.snippet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.snippet-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.snippet-language {
  padding: 0.25rem 0.75rem;
  background: var(--info-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.snippet-content h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.snippet-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.snippet-code {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  padding: 0.75rem;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 0.8rem;
  line-height: 1.4;
  overflow-x: auto;
  margin: 0;
}

.snippet-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.snippet-category {
  padding: 0.25rem 0.5rem;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border-radius: 12px;
  font-weight: 500;
}

.snippet-uses {
  color: var(--text-secondary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: var(--glass-bg-hover);
}

.history-item.success {
  border-left: 3px solid #10b981;
}

.history-item.error {
  border-left: 3px solid #ef4444;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.history-info {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
}

.history-language {
  padding: 0.25rem 0.75rem;
  background: var(--info-color);
  color: white;
  border-radius: 12px;
  font-weight: 500;
}

.history-time {
  color: var(--text-secondary);
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.history-content {
  margin-bottom: 1rem;
}

.history-code {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  padding: 0.75rem;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 0.8rem;
  line-height: 1.4;
  overflow-x: auto;
  margin: 0 0 1rem 0;
}

.history-output {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  padding: 0.75rem;
  margin-top: 1rem;
}

.history-output pre {
  margin: 0;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 0.8rem;
  white-space: pre-wrap;
}

.history-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.restore:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.rerun:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

/* Modal Styles */
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
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h2 {
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

.snippet-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
  font-family: 'Fira Code', 'Courier New', monospace;
}

.tags-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
}

.tag-text {
  padding: 0.25rem 0.75rem;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.tag-remove {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.tag-remove:hover {
  background: var(--danger-color);
  color: white;
}

.tag-input-container {
  display: flex;
  gap: 0.5rem;
}

.tag-input-container input {
  flex: 1;
  padding: 0.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
}

.tag-add {
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tag-add:hover {
  background: var(--primary-hover);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary {
  padding: 1rem 2rem;
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

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-secondary {
  background: var(--glass-bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-bg-hover);
}

@media (max-width: 768px) {
  .playground {
    padding: 1rem;
  }
  
  .editor-container {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .editor-panel {
    height: 400px;
  }
  
  .preview-panel {
    height: 300px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .snippets-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
