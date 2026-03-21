// =============================================================================
// DHQ Notification System
// =============================================================================

/**
 * Show a success notification
 * @param {string} message - Notification message
 * @param {Object} options - Additional options
 */
export function showSuccess(message, options = {}) {
  showNotification(message, 'success', options)
}

/**
 * Show an error notification
 * @param {string} message - Notification message
 * @param {Object} options - Additional options
 */
export function showError(message, options = {}) {
  showNotification(message, 'error', options)
}

/**
 * Show a warning notification
 * @param {string} message - Notification message
 * @param {Object} options - Additional options
 */
export function showWarning(message, options = {}) {
  showNotification(message, 'warning', options)
}

/**
 * Show an info notification
 * @param {string} message - Notification message
 * @param {Object} options - Additional options
 */
export function showInfo(message, options = {}) {
  showNotification(message, 'info', options)
}

/**
 * Show a confirmation dialog
 * @param {string} message - Confirmation message
 * @param {string} confirmText - Text for confirm button
 * @param {string} cancelText - Text for cancel button
 * @returns {Promise<boolean>} True if confirmed, False if cancelled
 */
export function showConfirm(message, confirmText = 'Confirm', cancelText = 'Cancel') {
  return new Promise((resolve) => {
    // Create modal overlay
    const modalOverlay = document.createElement('div')
    modalOverlay.className = 'notification-overlay'
    modalOverlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      animation: fadeIn 0.3s ease;
    `

    // Create modal content
    const modalContent = document.createElement('div')
    modalContent.className = 'notification-modal'
    modalContent.style.cssText = `
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      backdrop-filter: blur(16px);
      border-radius: 12px;
      padding: 24px;
      max-width: 400px;
      width: 90%;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    `

    modalContent.innerHTML = `
      <div class="notification-header" style="color: var(--text-primary); border-bottom: 1px solid var(--border-color); padding-bottom: 12px; margin-bottom: 16px;">
        <h3 style="margin: 0; font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
          <i class="fas fa-exclamation-triangle" style="color: var(--accent-warning, #f59e0b);"></i> Confirm Action
        </h3>
      </div>
      <div class="notification-body" style="color: var(--text-secondary); margin-bottom: 24px; line-height: 1.5;">
        <p style="margin: 0;">${message}</p>
      </div>
      <div class="notification-footer" style="display: flex; gap: 12px; justify-content: flex-end;">
        <button class="btn btn-cancel" style="background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 6px; cursor: pointer; transition: all 0.2s;">${cancelText}</button>
        <button class="btn btn-primary" style="background: var(--accent-primary); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; transition: all 0.2s;">${confirmText}</button>
      </div>
    `

    modalOverlay.appendChild(modalContent)
    document.body.appendChild(modalOverlay)

    // Add event listeners
    const cancelBtn = modalContent.querySelector('.btn-cancel')
    const confirmBtn = modalContent.querySelector('.btn-primary')

    cancelBtn.addEventListener('click', () => {
      document.body.removeChild(modalOverlay)
      resolve(false)
    })

    confirmBtn.addEventListener('click', () => {
      document.body.removeChild(modalOverlay)
      resolve(true)
    })

    // Auto-focus confirm button
    confirmBtn.focus()

    // Close on escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        document.body.removeChild(modalOverlay)
        resolve(false)
      }
      document.removeEventListener('keydown', handleEscape)
    }
    document.addEventListener('keydown', handleEscape)
  })
}

/**
 * Show a toast notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, warning, info)
 * @param {Object} options - Additional options
 */
function showNotification(message, type = 'info', options = {}) {
  // Create notification element
  const notification = document.createElement('div')
  notification.className = `notification notification-${type}`
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 10000;
    animation: slideInRight 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    max-width: 400px;
    word-wrap: break-word;
  `

  // Set background color based on type
  const colors = {
    success: '#10b981',
    error: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6'
  }
  notification.style.background = colors[type] || colors.info

  // Add icon based on type
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  }
  notification.innerHTML = `${icons[type] || icons.info} ${message}`

  // Add to page
  document.body.appendChild(notification)

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (document.body.contains(notification)) {
      notification.style.animation = 'slideOutRight 0.3s ease'
      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification)
        }
      }, 300)
    }
  }, 5000)

  // Add click to dismiss
  notification.addEventListener('click', () => {
    notification.style.animation = 'slideOutRight 0.3s ease'
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification)
      }
    }, 300)
  })
}

// Add CSS animations
const style = document.createElement('style')
style.textContent = `
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  @keyframes slideOutRight {
    from {
      opacity: 1;
      transform: stop_order(0);
    }
    to {
      opacity: 0;
      transform: translateX(100%);
    }
  }
  
  .notification-overlay {
    backdrop-filter: blur(4px);
  }
  
  .notification-modal h3 {
    margin: 0 0 16px 0;
    color: #2c3e50;
  }
  
  .notification-modal p {
    margin: 0 0 20px 0;
    color: #666;
    line-height: 1.5;
  }
  
  .notification-footer {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }
  
  .btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .btn-primary {
    background: #3b82f6;
    color: white;
  }
  
  .btn-primary:hover {
    background: #2563eb;
  }
  
  .btn-cancel {
    background: #6c757d;
    color: white;
  }
  
  .btn-cancel:hover {
    background: #5a6268;
  }
  
  .btn-secondary {
    background: #6c757d;
    color: white;
  }
  
  .btn-secondary:hover {
    background: #5a6268;
  }
  
  .btn-danger {
    background: #dc3545;
    color: white;
  }
  
  .btn-danger:hover {
    background: #c82333;
  }
`
document.head.appendChild(style)
