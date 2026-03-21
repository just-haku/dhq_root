// =============================================================================
// DHQ API Utility
// =============================================================================

/**
 * Get the base API URL based on current domain
 * @returns {string} Base API URL
 */
export function getApiBaseUrl() {
  const origin = window.location.origin

  // Check if test mode is enabled (localStorage flag)
  const testMode = localStorage.getItem('test_mode_enabled') === 'true'

  // Test mode - force local backend even on production domain
  if (testMode && (origin === 'https://haku.io.vn' || origin === 'https://www.haku.io.vn')) {
    return ''  // Use relative paths but will be overridden by fetch interceptor
  }

  // Production domain - use relative paths for proper proxying
  if (origin === 'https://haku.io.vn' || origin === 'https://www.haku.io.vn') {
    return ''  // Use relative paths for production
  }

  // Development - handle external network access
  if (origin.includes('192.168.') || origin.includes('113.177') || origin.includes('localhost') || origin.includes('localhost:3001')) {
    // Extract host from current origin and use port 8000 for API
    const url = new URL(origin)
    return `${url.protocol}//${url.hostname}:8000/api`
  }

  // Default to localhost for safety
  return 'http://localhost:8000/api'
}

/**
 * Get the Socket.IO URL based on current domain
 * @returns {string} Socket.IO URL
 */
export function getSocketIoUrl() {
  const origin = window.location.origin

  // Production domain - use relative paths
  if (origin === 'https://haku.io.vn' || origin === 'https://www.haku.io.vn') {
    return ''  // Use relative paths for production
  }

  // Development - handle external network access
  if (origin.includes('192.168.') || origin.includes('113.177') || origin.includes('localhost') || origin.includes('localhost:3001')) {
    // Extract host from current origin and use port 8001 for Socket.IO
    const url = new URL(origin)
    return `${url.protocol}//${url.hostname}:8001`
  }

  // Default to localhost for safety
  return 'http://localhost:8001'
}

/**
 * Get authentication headers
 * @returns {Object} Headers object with Authorization
 */
export function getAuthHeaders() {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

/**
 * Handle authentication errors (401 Unauthorized)
 * Clears credentials and redirects to homepage (clock)
 */
export function handleAuthError() {
  localStorage.removeItem('token')
  localStorage.removeItem('userRole')
  localStorage.removeItem('user')
  window.location.href = '/'
}

/**
 * Enable test mode for local backend testing on production domain
 */
export function enableTestMode() {
  localStorage.setItem('test_mode_enabled', 'true')
  console.log('🧪 Test mode enabled - API calls will route to local backend')
}

/**
 * Disable test mode and return to production
 */
export function disableTestMode() {
  localStorage.removeItem('test_mode_enabled')
  console.log('🔧 Test mode disabled - API calls will route to production')
}

/**
 * Check if test mode is enabled
 * @returns {boolean} True if test mode is enabled
 */
export function isTestModeEnabled() {
  return localStorage.getItem('test_mode_enabled') === 'true'
}

import { ref } from 'vue'

export const kpiBalance = ref(parseInt(localStorage.getItem('kpi_balance') || '0'))
export const notificationState = ref({
  show: false,
  title: '',
  message: '',
  type: 'info',
  icon: '',
  duration: 5000
})

export function updateKpiBalance(newBalance) {
  if (newBalance !== undefined && newBalance !== null) {
    const oldBalance = kpiBalance.value
    kpiBalance.value = parseInt(newBalance)
    localStorage.setItem('kpi_balance', newBalance.toString())
    console.log(`%c🔄 KPI Ref Updated: ${oldBalance} ➡️ ${kpiBalance.value}`, 'color: #10b981; font-weight: bold')

    // Also update the user object in localStorage if it exists
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        user.kpi_current = parseInt(newBalance)
        localStorage.setItem('user', JSON.stringify(user))
        console.log('%c👤 Local User Object Synced: kpi_current updated', 'color: #3b82f6')
      } catch (e) {
        console.error('Error updating user in localStorage:', e)
      }
    }
  }
}

/**
 * Trigger a global custom notification
 */
export function showAlert(title, message, type = 'info', icon = '') {
  notificationState.value = {
    show: true,
    title,
    message,
    type,
    icon,
    duration: type === 'error' ? 8000 : 5000
  }
}

/**
 * Make an authenticated API request
 * @param {string} endpoint - API endpoint (without /api prefix)
 * @param {Object} options - Fetch options
 * @returns {Promise} Parsed JSON response
 */
export function apiRequest(endpoint, options = {}) {
  const baseUrl = getApiBaseUrl()
  const url = baseUrl ? `${baseUrl}${endpoint}` : `/api${endpoint}`
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
    ...options.headers
  }

  return fetch(url, {
    ...options,
    headers
  }).then(async response => {
    if (!response.ok) {
      if (response.status === 401) {
        handleAuthError()
      }

      let errorMessage = `HTTP error! status: ${response.status}`
      try {
        const errorData = await response.json()
        if (errorData.detail) {
          errorMessage = errorData.detail
        }
      } catch (e) {
        // Fallback if not JSON or no detail
      }

      throw new Error(errorMessage)
    }

    // Parse JSON response
    const data = await response.json()

    // Auto-sync KPI balance if present in response
    if (data.kpi_current !== undefined) {
      console.log(`%c💰 KPI Sync: kpi_current found in response: ${data.kpi_current}`, 'color: #fbbf24; font-weight: bold')
      updateKpiBalance(data.kpi_current)
    } else if (data.new_balance !== undefined) {
      console.log(`%c💰 KPI Sync: new_balance found in response: ${data.new_balance}`, 'color: #fbbf24; font-weight: bold')
      updateKpiBalance(data.new_balance)
    }

    return data
  }).catch(error => {
    console.error(`API Error (${endpoint}):`, error)
    showAlert('API Error', error.message || 'An unexpected error occurred', 'error', '❌')
    throw error
  })
}

/**
 * Make a GET request to the API
 * @param {string} endpoint - API endpoint
 * @returns {Promise} Parsed JSON response
 */
export function apiGet(endpoint) {
  return apiRequest(endpoint, { method: 'GET' })
}

/**
 * Make a POST request to the API
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body data
 * @returns {Promise} Parsed JSON response
 */
export function apiPost(endpoint, data) {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

/**
 * Make a PUT request to the API
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body data
 * @returns {Promise} Parsed JSON response
 */
export function apiPut(endpoint, data) {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

/**
 * Make a PATCH request to the API
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body data
 * @returns {Promise} Parsed JSON response
 */
export function apiPatch(endpoint, data) {
  return apiRequest(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data)
  })
}

/**
 * Make a DELETE request to the API
 * @param {string} endpoint - API endpoint
 * @returns {Promise} Parsed JSON response
 */
export function apiDelete(endpoint) {
  return apiRequest(endpoint, { method: 'DELETE' })
}

/**
 * Make a POST request with FormData (multipart/form-data)
 * @param {string} endpoint - API endpoint
 * @param {FormData} formData - Form data
 * @returns {Promise} Parsed JSON response
 */
export function apiPostForm(endpoint, formData) {
  const baseUrl = getApiBaseUrl()
  const url = baseUrl ? `${baseUrl}${endpoint}` : `/api${endpoint}`

  return fetch(url, {
    method: 'POST',
    headers: {
      ...getAuthHeaders()
    },
    body: formData
  }).then(async response => {
    if (!response.ok) {
      if (response.status === 401) {
        handleAuthError()
      }
      const data = await response.json().catch(() => ({}))
      const err = new Error(data.detail || `HTTP ${res.status}`)
      err.status = response.status
      throw err
    }
    return response.json()
  })
}

/**
 * Make a file upload request with progress tracking
 * @param {string} endpoint - API endpoint
 * @param {FormData} formData - Form data with files
 * @param {Function} onProgress - Callback for upload progress (0-100)
 * @returns {Promise} XHR promise resolving to response
 */
export function apiUpload(endpoint, formData, onProgress = null) {
  return new Promise((resolve, reject) => {
    const baseUrl = getApiBaseUrl()
    const url = baseUrl ? `${baseUrl}${endpoint}` : `/api${endpoint}`

    const xhr = new XMLHttpRequest()
    xhr.open('POST', url, true)

    // Set authentication headers
    const authHeaders = getAuthHeaders()
    if (authHeaders.Authorization) {
      xhr.setRequestHeader('Authorization', authHeaders.Authorization)
    }

    // Attach progress listener if provided
    if (onProgress) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100)
          onProgress(percentComplete)
        }
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText)
          resolve(response)
        } catch (e) {
          resolve(xhr.responseText)
        }
      } else {
        if (xhr.status === 401) {
          handleAuthError()
        }

        try {
          const errorResp = JSON.parse(xhr.responseText)
          const error = new Error(errorResp.detail || `HTTP error! status: ${xhr.status}`)
          error.status = xhr.status
          reject(error)
        } catch {
          const error = new Error(`HTTP error! status: ${xhr.status}`)
          error.status = xhr.status
          reject(error)
        }
      }
    }

    xhr.onerror = () => {
      reject(new Error('Network error during upload'))
    }

    xhr.send(formData)
  })
}
