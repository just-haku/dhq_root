<template>
  <div class="invoice-detail">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading invoice details...</p>
    </div>

    <div v-else-if="!invoice" class="error-state">
      <div class="error-icon">
        <i class="fas fa-exclamation-triangle"></i>
      </div>
      <h3>Invoice not found</h3>
      <p>The invoice you're looking for doesn't exist or you don't have permission to view it.</p>
      <button class="btn-primary" @click="$router.push('/invoices')">
        <i class="fas fa-arrow-left"></i>
        Back to Invoices
      </button>
    </div>

    <div v-else class="invoice-content">
      <!-- Invoice Header -->
      <div class="invoice-header">
        <div class="header-left">
          <button class="back-btn" @click="$router.push('/invoices')">
            <i class="fas fa-arrow-left"></i>
            Back to Invoices
          </button>
          <div class="invoice-title">
            <h1>Invoice #{{ invoice.invoice_number }}</h1>
            <div class="invoice-badges">
              <span :class="['status-badge', invoice.status]">{{ invoice.status }}</span>
              <span v-if="isOverdue()" class="overdue-badge">Overdue</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <div class="invoice-actions">
            <button class="action-btn" @click="editInvoice" title="Edit Invoice">
              <i class="fas fa-edit"></i>
              Edit
            </button>
            <button class="action-btn" @click="downloadPDF" title="Download PDF">
              <i class="fas fa-download"></i>
              Download
            </button>
            <button class="action-btn" @click="printInvoice" title="Print Invoice">
              <i class="fas fa-print"></i>
              Print
            </button>
            <button 
              v-if="invoice.status === 'sent'" 
              class="action-btn success" 
              @click="markAsPaid" 
              title="Mark as Paid"
            >
              <i class="fas fa-check"></i>
              Mark Paid
            </button>
            <button class="action-btn danger" @click="deleteInvoice" title="Delete Invoice">
              <i class="fas fa-trash"></i>
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Invoice Overview Cards -->
      <div class="invoice-overview">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-calendar"></i>
          </div>
          <div class="card-content">
            <h3>{{ formatDate(invoice.issue_date) }}</h3>
            <p>Issue Date</p>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3 :class="{ 'overdue': isOverdue() }">{{ formatDate(invoice.due_date) }}</h3>
            <p>Due Date</p>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="card-content">
            <h3>{{ formatCurrency(invoice.total, invoice.currency) }}</h3>
            <p>Total Amount</p>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-hourglass-half"></i>
          </div>
          <div class="card-content">
            <h3>{{ getDaysRemaining() }}</h3>
            <p>Days Remaining</p>
          </div>
        </div>
      </div>

      <!-- Main Invoice Content -->
      <div class="invoice-main">
        <!-- Client and Company Info -->
        <div class="invoice-parties">
          <div class="party-section">
            <h3>Bill From</h3>
            <div class="party-info">
              <h4>Your Company</h4>
              <p>123 Business Street</p>
              <p>City, State 12345</p>
              <p>contact@yourcompany.com</p>
              <p>(555) 123-4567</p>
            </div>
          </div>

          <div class="party-section">
            <h3>Bill To</h3>
            <div class="party-info">
              <h4>{{ invoice.client.name }}</h4>
              <p>{{ invoice.client.email }}</p>
              <p v-if="invoice.client.phone">{{ invoice.client.phone }}</p>
              <p v-if="invoice.client.address">{{ invoice.client.address }}</p>
            </div>
          </div>
        </div>

        <!-- Invoice Items Table -->
        <div class="invoice-items-section">
          <h3>Invoice Items</h3>
          <div class="items-table-container">
            <table class="items-table">
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Quantity</th>
                  <th>Unit Price</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in invoice.items" :key="item.id">
                  <td class="description">
                    <h4>{{ item.description }}</h4>
                    <p v-if="item.details">{{ item.details }}</p>
                  </td>
                  <td class="quantity">{{ item.quantity }}</td>
                  <td class="unit-price">{{ formatCurrency(item.unit_price, invoice.currency) }}</td>
                  <td class="line-total">{{ formatCurrency(item.quantity * item.unit_price, invoice.currency) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Invoice Totals -->
        <div class="invoice-totals">
          <div class="totals-card">
            <h3>Invoice Summary</h3>
            <div class="total-row">
              <span>Subtotal:</span>
              <span>{{ formatCurrency(invoice.subtotal, invoice.currency) }}</span>
            </div>
            <div class="total-row">
              <span>Tax ({{ invoice.tax_rate }}%):</span>
              <span>{{ formatCurrency(invoice.tax, invoice.currency) }}</span>
            </div>
            <div v-if="invoice.discount" class="total-row discount">
              <span>Discount:</span>
              <span>-{{ formatCurrency(invoice.discount, invoice.currency) }}</span>
            </div>
            <div class="total-row grand-total">
              <span>Total:</span>
              <span>{{ formatCurrency(invoice.total, invoice.currency) }}</span>
            </div>
          </div>
        </div>

        <!-- Payment Information -->
        <div v-if="invoice.payments && invoice.payments.length > 0" class="payments-section">
          <h3>Payment History</h3>
          <div class="payments-list">
            <div 
              v-for="payment in invoice.payments" 
              :key="payment.id"
              class="payment-item"
            >
              <div class="payment-info">
                <h4>{{ formatCurrency(payment.amount, invoice.currency) }}</h4>
                <p>{{ formatDate(payment.payment_date) }}</p>
                <span :class="['payment-status', payment.status]">{{ payment.status }}</span>
              </div>
              <div class="payment-method">
                <span>{{ payment.method }}</span>
                <p v-if="payment.transaction_id">ID: {{ payment.transaction_id }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Notes and Terms -->
        <div class="notes-section">
          <div class="notes-card">
            <h3>Notes</h3>
            <p>{{ invoice.notes || 'No notes provided' }}</p>
          </div>
          <div class="terms-card">
            <h3>Payment Terms</h3>
            <p>{{ invoice.payment_terms || 'Payment due within 30 days' }}</p>
          </div>
        </div>
      </div>

      <!-- Activity Timeline -->
      <div class="activity-section">
        <div class="section-header">
          <h2>Activity Timeline</h2>
          <button class="refresh-btn" @click="loadActivities">
            <i class="fas fa-sync"></i>
          </button>
        </div>
        <div class="timeline">
          <div 
            v-for="activity in invoice.activities" 
            :key="activity.id"
            class="timeline-item"
          >
            <div class="timeline-icon">
              <i :class="getActivityIcon(activity.type)"></i>
            </div>
            <div class="timeline-content">
              <div class="timeline-header">
                <h4>{{ activity.title }}</h4>
                <span class="timeline-time">{{ formatDateTime(activity.created_at) }}</span>
              </div>
              <p>{{ activity.description }}</p>
              <div v-if="activity.user" class="activity-user">
                <img 
                  :src="activity.user.avatar || getDefaultAvatar(activity.user.name)" 
                  :alt="activity.user.name"
                />
                <span>{{ activity.user.name }}</span>
              </div>
            </div>
          </div>
          <div v-if="!invoice.activities || invoice.activities.length === 0" class="empty-timeline">
            <p>No activity recorded yet</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Invoice Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Edit Invoice</h2>
          <button class="close-btn" @click="closeEditModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label>Invoice Number</label>
              <input v-model="editForm.invoice_number" type="text" />
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="editForm.status">
                <option value="draft">Draft</option>
                <option value="sent">Sent</option>
                <option value="paid">Paid</option>
                <option value="overdue">Overdue</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div class="form-group">
              <label>Issue Date</label>
              <input v-model="editForm.issue_date" type="date" />
            </div>
            <div class="form-group">
              <label>Due Date</label>
              <input v-model="editForm.due_date" type="date" />
            </div>
            <div class="form-group">
              <label>Tax Rate (%)</label>
              <input v-model.number="editForm.tax_rate" type="number" min="0" max="100" step="0.01" />
            </div>
            <div class="form-group">
              <label>Discount</label>
              <input v-model.number="editForm.discount" type="number" min="0" step="0.01" />
            </div>
          </div>

          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="editForm.notes" rows="3"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeEditModal">Cancel</button>
          <button class="btn-primary" @click="saveInvoice">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiGet, apiPut, apiDelete, apiPost } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

const route = useRoute()
const router = useRouter()

// Reactive state
const loading = ref(false)
const invoice = ref(null)
const showEditModal = ref(false)

const editForm = reactive({
  invoice_number: '',
  status: '',
  issue_date: '',
  due_date: '',
  tax_rate: 0,
  discount: 0,
  notes: ''
})

// Methods
const loadInvoice = async () => {
  loading.value = true
  try {
    const response = await apiGet(`/invoices/${route.params.id}`)
    if (response.success) {
      invoice.value = response.invoice
    } else {
      invoice.value = null
    }
  } catch (error) {
    console.error('Error loading invoice:', error)
    invoice.value = null
  } finally {
    loading.value = false
  }
}

const loadActivities = async () => {
  if (!invoice.value) return
  
  try {
    const response = await apiGet(`/invoices/${invoice.value.id}/activities`)
    if (response.success) {
      invoice.value.activities = response.activities || []
    }
  } catch (error) {
    console.error('Error loading activities:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not set'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Not set'
  return new Date(dateString).toLocaleString()
}

const formatCurrency = (amount, currency = 'USD') => {
  if (!amount) return '0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount)
}

const getDefaultAvatar = (name) => {
  if (!name) return ''
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3b82f6&color=fff&size=40`
}

const isOverdue = () => {
  if (!invoice.value) return false
  if (invoice.value.status === 'paid' || invoice.value.status === 'cancelled') return false
  return new Date(invoice.value.due_date) < new Date()
}

const getDaysRemaining = () => {
  if (!invoice.value) return 'N/A'
  if (invoice.value.status === 'paid' || invoice.value.status === 'cancelled') return 'N/A'
  
  const dueDate = new Date(invoice.value.due_date)
  const today = new Date()
  const diffTime = dueDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) {
    return `${Math.abs(diffDays)} days overdue`
  } else if (diffDays === 0) {
    return 'Due today'
  } else {
    return `${diffDays} days`
  }
}

const getActivityIcon = (type) => {
  const icons = {
    'invoice_created': 'fas fa-plus-circle',
    'invoice_updated': 'fas fa-edit',
    'invoice_sent': 'fas fa-envelope',
    'invoice_paid': 'fas fa-check-circle',
    'invoice_overdue': 'fas fa-exclamation-triangle',
    'payment_received': 'fas fa-dollar-sign',
    'invoice_cancelled': 'fas fa-times-circle'
  }
  return icons[type] || 'fas fa-circle'
}

const editInvoice = () => {
  if (!invoice.value) return
  
  Object.assign(editForm, {
    invoice_number: invoice.value.invoice_number,
    status: invoice.value.status,
    issue_date: invoice.value.issue_date,
    due_date: invoice.value.due_date,
    tax_rate: invoice.value.tax_rate,
    discount: invoice.value.discount || 0,
    notes: invoice.value.notes
  })
  
  showEditModal.value = true
}

const saveInvoice = async () => {
  if (!invoice.value) return
  
  try {
    const response = await apiPut(`/invoices/${invoice.value.id}`, editForm)
    if (response.success) {
      Object.assign(invoice.value, response.invoice)
      showSuccess('Invoice updated successfully')
      closeEditModal()
    }
  } catch (error) {
    console.error('Error saving invoice:', error)
    showError('Failed to save invoice')
  }
}

const markAsPaid = async () => {
  if (!invoice.value) return
  
  const confirmed = await showConfirm('Mark this invoice as paid?')
  if (!confirmed) return
  
  try {
    const response = await apiPost(`/invoices/${invoice.value.id}/mark-paid`)
    if (response.success) {
      invoice.value.status = 'paid'
      showSuccess('Invoice marked as paid')
    }
  } catch (error) {
    console.error('Error marking invoice as paid:', error)
    showError('Failed to mark invoice as paid')
  }
}

const downloadPDF = async () => {
  if (!invoice.value) return
  
  try {
    const response = await apiGet(`/invoices/${invoice.value.id}/download`)
    if (response.success) {
      const downloadUrl = response.download_url
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `invoice_${invoice.value.invoice_number}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      showSuccess('Invoice downloaded successfully')
    }
  } catch (error) {
    console.error('Error downloading invoice:', error)
    showError('Failed to download invoice')
  }
}

const printInvoice = () => {
  window.print()
}

const deleteInvoice = async () => {
  if (!invoice.value) return
  
  const confirmed = await showConfirm(`Are you sure you want to delete invoice #${invoice.value.invoice_number}?`)
  if (!confirmed) return
  
  try {
    const response = await apiDelete(`/invoices/${invoice.value.id}`)
    if (response.success) {
      showSuccess('Invoice deleted successfully')
      router.push('/invoices')
    }
  } catch (error) {
    console.error('Error deleting invoice:', error)
    showError('Failed to delete invoice')
  }
}

const closeEditModal = () => {
  showEditModal.value = false
}

// Lifecycle
onMounted(() => {
  loadInvoice()
})
</script>

<style scoped>
.invoice-detail {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loading-state, .error-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 3px solid var(--glass-border);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  color: var(--danger-color);
  margin-bottom: 1rem;
}

.invoice-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
}

.header-left {
  flex: 1;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
  font-weight: 500;
}

.back-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.invoice-title h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.75rem 0;
}

.invoice-badges {
  display: flex;
  gap: 0.75rem;
}

.status-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.draft {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.status-badge.sent {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.paid {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.overdue {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.cancelled {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.overdue-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.invoice-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.625rem 1.25rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.success {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.success:hover {
  background: var(--success-hover);
}

.action-btn.danger {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.action-btn.danger:hover {
  background: var(--danger-hover);
}

.invoice-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.overview-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-icon {
  width: 50px;
  height: 50px;
  background: var(--primary-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.card-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.card-content h3.overdue {
  color: var(--danger-color);
}

.card-content p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.9rem;
}

.invoice-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.invoice-parties {
  display: flex;
  gap: 2rem;
}

.party-section {
  flex: 1;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.party-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.party-info h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.party-info p {
  margin: 0.25rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.invoice-items-section {
  grid-column: 1 / -1;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.invoice-items-section h3 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.items-table-container {
  overflow-x: auto;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--glass-bg-primary);
  border-radius: 8px;
  overflow: hidden;
}

.items-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.items-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.description h4 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.description p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.quantity, .unit-price, .line-total {
  text-align: center;
  font-weight: 600;
}

.line-total {
  color: var(--primary-color);
}

.invoice-totals {
  display: flex;
  justify-content: flex-end;
}

.totals-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  min-width: 300px;
}

.totals-card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.total-row.discount {
  color: var(--success-color);
}

.total-row.grand-total {
  font-weight: 700;
  font-size: 1.2rem;
  color: var(--text-primary);
  padding-top: 0.75rem;
  border-top: 1px solid var(--glass-border);
}

.payments-section {
  grid-column: 1 / -1;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.payments-section h3 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.payments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.payment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.payment-info h4 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.payment-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.payment-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.payment-status.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.payment-status.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.payment-status.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.payment-method {
  text-align: right;
}

.payment-method span {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.payment-method p {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

.notes-section {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.notes-card, .terms-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.notes-card h3, .terms-card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.notes-card p, .terms-card p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.activity-section {
  grid-column: 1 / -1;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.refresh-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  background: var(--glass-bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
}

.timeline-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.timeline-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.timeline-time {
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

.timeline-content p {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.activity-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.activity-user img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.empty-timeline {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
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
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-weight: 500;
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
  font-size: 0.9rem;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
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
  .invoice-detail {
    padding: 1rem;
  }
  
  .invoice-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .invoice-actions {
    justify-content: center;
  }
  
  .invoice-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .invoice-main {
    grid-template-columns: 1fr;
  }
  
  .invoice-parties {
    flex-direction: column;
  }
  
  .notes-section {
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

@media print {
  .invoice-detail {
    padding: 0;
    background: white;
  }
  
  .invoice-header,
  .invoice-overview,
  .activity-section {
    display: none;
  }
  
  .invoice-main {
    grid-template-columns: 1fr;
    gap: 0;
  }
  
  .invoice-parties {
    display: block;
    margin-bottom: 2rem;
  }
  
  .party-section {
    background: white;
    border: 1px solid #ddd;
    margin-bottom: 1rem;
  }
  
  .invoice-items-section,
  .invoice-totals,
  .payments-section,
  .notes-section {
    background: white;
    border: 1px solid #ddd;
    margin-bottom: 1rem;
  }
  
  .items-table {
    background: white;
  }
  
  .totals-card {
    background: white;
    border: 1px solid #ddd;
  }
}
</style>
