<template>
  <div class="invoices">
    <div class="page-header">
      <h1>Invoices</h1>
      <p>Manage your invoices, payments, and billing</p>
    </div>

    <!-- Invoice Controls -->
    <div class="invoice-controls">
      <div class="control-section">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search invoices..."
            @input="filterInvoices"
          />
        </div>
      </div>

      <div class="control-section">
        <div class="filter-dropdown">
          <select v-model="statusFilter" @change="filterInvoices">
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      <div class="control-section">
        <div class="date-range">
          <input 
            v-model="dateRange.start" 
            type="date" 
            @change="filterInvoices"
          />
          <span>to</span>
          <input 
            v-model="dateRange.end" 
            type="date" 
            @change="filterInvoices"
          />
        </div>
      </div>

      <div class="control-section">
        <button class="add-invoice-btn" @click="showAddInvoiceModal = true">
          <i class="fas fa-plus"></i>
          New Invoice
        </button>
      </div>
    </div>

    <!-- Invoice Statistics -->
    <div class="invoice-stats">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-file-invoice"></i>
        </div>
        <div class="stat-content">
          <h3>{{ invoiceStats.total }}</h3>
          <p>Total Invoices</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon pending">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <h3>{{ invoiceStats.pending }}</h3>
          <p>Pending</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon paid">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ invoiceStats.paid }}</h3>
          <p>Paid</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon overdue">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ invoiceStats.overdue }}</h3>
          <p>Overdue</p>
        </div>
      </div>
    </div>

    <!-- Revenue Summary -->
    <div class="revenue-summary">
      <div class="summary-card">
        <h3>Total Revenue</h3>
        <p class="amount">{{ formatCurrency(invoiceStats.totalRevenue) }}</p>
        <span class="period">{{ dateRange.start }} to {{ dateRange.end }}</span>
      </div>
      <div class="summary-card">
        <h3>Outstanding</h3>
        <p class="amount outstanding">{{ formatCurrency(invoiceStats.outstanding) }}</p>
        <span class="period">Unpaid invoices</span>
      </div>
      <div class="summary-card">
        <h3>Average Invoice</h3>
        <p class="amount">{{ formatCurrency(invoiceStats.averageInvoice) }}</p>
        <span class="period">Per invoice</span>
      </div>
    </div>

    <!-- Invoices Table -->
    <div class="invoices-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading invoices...</p>
      </div>

      <div v-else-if="filteredInvoices.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-file-invoice-dollar"></i>
        </div>
        <h3>No invoices found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else class="invoices-table-container">
        <table class="invoices-table">
          <thead>
            <tr>
              <th>Invoice #</th>
              <th>Client</th>
              <th>Date</th>
              <th>Due Date</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="invoice in filteredInvoices" 
              :key="invoice.id"
              class="invoice-row"
            >
              <td>
                <div class="invoice-number">
                  <span class="number">#{{ invoice.invoice_number }}</span>
                  <button 
                    class="copy-btn"
                    @click="copyInvoiceNumber(invoice.invoice_number)"
                    title="Copy invoice number"
                  >
                    <i class="fas fa-copy"></i>
                  </button>
                </div>
              </td>
              <td>
                <div class="client-info">
                  <div class="client-avatar">
                    <img 
                      :src="invoice.client.avatar || getDefaultAvatar(invoice.client.name)" 
                      :alt="invoice.client.name"
                    />
                  </div>
                  <div>
                    <h4>{{ invoice.client.name }}</h4>
                    <p>{{ invoice.client.email }}</p>
                  </div>
                </div>
              </td>
              <td>{{ formatDate(invoice.created_at) }}</td>
              <td :class="{ 'overdue': isOverdue(invoice) }">
                {{ formatDate(invoice.due_date) }}
              </td>
              <td class="amount">{{ formatCurrency(invoice.total) }}</td>
              <td>
                <span :class="['status-badge', invoice.status]">{{ invoice.status }}</span>
              </td>
              <td>
                <div class="actions">
                  <button 
                    class="action-btn view"
                    @click="viewInvoice(invoice)"
                    title="View Invoice"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    class="action-btn edit"
                    @click="editInvoice(invoice)"
                    title="Edit Invoice"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button 
                    class="action-btn download"
                    @click="downloadInvoice(invoice)"
                    title="Download PDF"
                  >
                    <i class="fas fa-download"></i>
                  </button>
                  <button 
                    class="action-btn delete"
                    @click="deleteInvoice(invoice)"
                    title="Delete Invoice"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Invoice Modal -->
    <div v-if="showAddInvoiceModal || showEditInvoiceModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ showEditInvoiceModal ? 'Edit Invoice' : 'Create New Invoice' }}</h2>
          <button class="close-btn" @click="closeModals">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label>Invoice Number</label>
              <input 
                v-model="invoiceForm.invoice_number" 
                type="text" 
                placeholder="INV-001"
              />
            </div>

            <div class="form-group">
              <label>Client *</label>
              <select v-model="invoiceForm.client_id" required>
                <option value="">Select Client</option>
                <option 
                  v-for="client in clients" 
                  :key="client.id"
                  :value="client.id"
                >
                  {{ client.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Issue Date *</label>
              <input 
                v-model="invoiceForm.issue_date" 
                type="date"
                required
              />
            </div>

            <div class="form-group">
              <label>Due Date *</label>
              <input 
                v-model="invoiceForm.due_date" 
                type="date"
                required
              />
            </div>

            <div class="form-group">
              <label>Status</label>
              <select v-model="invoiceForm.status">
                <option value="draft">Draft</option>
                <option value="sent">Sent</option>
                <option value="paid">Paid</option>
                <option value="overdue">Overdue</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div class="form-group">
              <label>Currency</label>
              <select v-model="invoiceForm.currency">
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
                <option value="JPY">JPY - Japanese Yen</option>
              </select>
            </div>
          </div>

          <!-- Invoice Items -->
          <div class="invoice-items-section">
            <div class="section-header">
              <h3>Invoice Items</h3>
              <button class="add-item-btn" @click="addInvoiceItem">
                <i class="fas fa-plus"></i>
                Add Item
              </button>
            </div>

            <div class="invoice-items">
              <div 
                v-for="(item, index) in invoiceForm.items" 
                :key="index"
                class="invoice-item"
              >
                <div class="item-row">
                  <div class="form-group">
                    <label>Description</label>
                    <input 
                      v-model="item.description" 
                      type="text" 
                      placeholder="Item description"
                    />
                  </div>
                  <div class="form-group">
                    <label>Quantity</label>
                    <input 
                      v-model.number="item.quantity" 
                      type="number" 
                      min="1"
                      step="0.01"
                    />
                  </div>
                  <div class="form-group">
                    <label>Unit Price</label>
                    <input 
                      v-model.number="item.unit_price" 
                      type="number" 
                      min="0"
                      step="0.01"
                    />
                  </div>
                  <div class="form-group">
                    <label>Total</label>
                    <input 
                      :value="item.quantity * item.unit_price"
                      type="text" 
                      readonly
                      class="readonly"
                    />
                  </div>
                  <button 
                    class="remove-item-btn"
                    @click="removeInvoiceItem(index)"
                    title="Remove item"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Invoice Totals -->
          <div class="invoice-totals">
            <div class="total-row">
              <span>Subtotal:</span>
              <span>{{ formatCurrency(calculateSubtotal()) }}</span>
            </div>
            <div class="total-row">
              <label>Tax Rate (%):</label>
              <input 
                v-model.number="invoiceForm.tax_rate" 
                type="number" 
                min="0"
                max="100"
                step="0.01"
              />
            </div>
            <div class="total-row">
              <span>Tax:</span>
              <span>{{ formatCurrency(calculateTax()) }}</span>
            </div>
            <div class="total-row grand-total">
              <span>Total:</span>
              <span>{{ formatCurrency(calculateTotal()) }}</span>
            </div>
          </div>

          <div class="form-group">
            <label>Notes</label>
            <textarea 
              v-model="invoiceForm.notes" 
              placeholder="Additional notes or payment instructions..."
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModals">Cancel</button>
          <button 
            class="btn-primary" 
            @click="saveInvoice"
            :disabled="saving"
          >
            {{ saving ? 'Saving...' : (showEditInvoiceModal ? 'Update Invoice' : 'Create Invoice') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Invoice Preview Modal -->
    <div v-if="showPreviewModal" class="modal-overlay" @click="closePreviewModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Invoice Preview</h2>
          <div class="preview-actions">
            <button class="action-btn" @click="downloadPreview" title="Download PDF">
              <i class="fas fa-download"></i>
            </button>
            <button class="action-btn" @click="printPreview" title="Print">
              <i class="fas fa-print"></i>
            </button>
            <button class="close-btn" @click="closePreviewModal">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <div class="modal-body">
          <div class="invoice-preview" ref="invoicePreview">
            <!-- Invoice preview content would be rendered here -->
            <div class="preview-header">
              <h1>INVOICE</h1>
              <div class="invoice-details">
                <p><strong>Invoice #:</strong> {{ selectedInvoice?.invoice_number }}</p>
                <p><strong>Date:</strong> {{ formatDate(selectedInvoice?.created_at) }}</p>
                <p><strong>Due Date:</strong> {{ formatDate(selectedInvoice?.due_date) }}</p>
              </div>
            </div>

            <div class="preview-client">
              <h3>Bill To:</h3>
              <p>{{ selectedInvoice?.client?.name }}</p>
              <p>{{ selectedInvoice?.client?.email }}</p>
              <p>{{ selectedInvoice?.client?.address }}</p>
            </div>

            <div class="preview-items">
              <table>
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in selectedInvoice?.items" :key="item.id">
                    <td>{{ item.description }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ formatCurrency(item.unit_price) }}</td>
                    <td>{{ formatCurrency(item.quantity * item.unit_price) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="preview-totals">
              <div class="total-row">
                <span>Subtotal:</span>
                <span>{{ formatCurrency(selectedInvoice?.subtotal) }}</span>
              </div>
              <div class="total-row">
                <span>Tax:</span>
                <span>{{ formatCurrency(selectedInvoice?.tax) }}</span>
              </div>
              <div class="total-row grand-total">
                <span>Total:</span>
                <span>{{ formatCurrency(selectedInvoice?.total) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const saving = ref(false)
const invoices = ref([])
const clients = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const selectedInvoice = ref(null)

// Modal states
const showAddInvoiceModal = ref(false)
const showEditInvoiceModal = ref(false)
const showPreviewModal = ref(false)

const dateRange = reactive({
  start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
  end: new Date().toISOString().split('T')[0] // Today
})

const invoiceForm = reactive({
  invoice_number: '',
  client_id: '',
  issue_date: new Date().toISOString().split('T')[0],
  due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days from now
  status: 'draft',
  currency: 'USD',
  tax_rate: 0,
  notes: '',
  items: [
    {
      description: '',
      quantity: 1,
      unit_price: 0
    }
  ]
})

// Computed properties
const filteredInvoices = computed(() => {
  let filtered = invoices.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(invoice => 
      invoice.invoice_number.toLowerCase().includes(query) ||
      invoice.client.name.toLowerCase().includes(query) ||
      invoice.client.email.toLowerCase().includes(query)
    )
  }

  // Apply status filter
  if (statusFilter.value) {
    filtered = filtered.filter(invoice => invoice.status === statusFilter.value)
  }

  // Apply date filter
  if (dateRange.start && dateRange.end) {
    const startDate = new Date(dateRange.start)
    const endDate = new Date(dateRange.end)
    filtered = filtered.filter(invoice => {
      const invoiceDate = new Date(invoice.created_at)
      return invoiceDate >= startDate && invoiceDate <= endDate
    })
  }

  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const invoiceStats = computed(() => {
  const filtered = filteredInvoices.value
  const stats = {
    total: filtered.length,
    pending: filtered.filter(i => i.status === 'sent' || i.status === 'draft').length,
    paid: filtered.filter(i => i.status === 'paid').length,
    overdue: filtered.filter(i => i.status === 'overdue').length,
    totalRevenue: filtered.filter(i => i.status === 'paid').reduce((sum, i) => sum + i.total, 0),
    outstanding: filtered.filter(i => i.status !== 'paid' && i.status !== 'cancelled').reduce((sum, i) => sum + i.total, 0),
    averageInvoice: 0
  }
  
  stats.averageInvoice = stats.total > 0 ? stats.totalRevenue / stats.paid : 0
  
  return stats
})

// Methods
const loadInvoices = async () => {
  loading.value = true
  try {
    const response = await apiGet('/invoices')
    if (response.success) {
      invoices.value = response.invoices || []
    }
  } catch (error) {
    console.error('Error loading invoices:', error)
    showError('Failed to load invoices')
  } finally {
    loading.value = false
  }
}

const loadClients = async () => {
  try {
    const response = await apiGet('/clients')
    if (response.success) {
      clients.value = response.clients || []
    }
  } catch (error) {
    console.error('Error loading clients:', error)
  }
}

const filterInvoices = () => {
  // This is reactive, no additional action needed
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not set'
  return new Date(dateString).toLocaleDateString()
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

const isOverdue = (invoice) => {
  if (invoice.status === 'paid' || invoice.status === 'cancelled') return false
  return new Date(invoice.due_date) < new Date()
}

const getEmptyMessage = () => {
  if (searchQuery.value || statusFilter.value) {
    return 'No invoices match your search criteria'
  }
  return 'Create your first invoice to get started'
}

const copyInvoiceNumber = (invoiceNumber) => {
  navigator.clipboard.writeText(invoiceNumber)
  showSuccess('Invoice number copied to clipboard')
}

const viewInvoice = (invoice) => {
  selectedInvoice.value = invoice
  showPreviewModal.value = true
}

const editInvoice = (invoice) => {
  selectedInvoice.value = invoice
  Object.assign(invoiceForm, {
    ...invoice,
    client_id: invoice.client.id,
    items: invoice.items.length > 0 ? [...invoice.items] : [{
      description: '',
      quantity: 1,
      unit_price: 0
    }]
  })
  showEditInvoiceModal.value = true
}

const deleteInvoice = async (invoice) => {
  const confirmed = await showConfirm(`Are you sure you want to delete invoice #${invoice.invoice_number}?`)
  if (!confirmed) return

  try {
    const response = await apiDelete(`/invoices/${invoice.id}`)
    if (response.success) {
      const index = invoices.value.findIndex(i => i.id === invoice.id)
      if (index > -1) {
        invoices.value.splice(index, 1)
        showSuccess('Invoice deleted successfully')
      }
    }
  } catch (error) {
    console.error('Error deleting invoice:', error)
    showError('Failed to delete invoice')
  }
}

const downloadInvoice = async (invoice) => {
  try {
    const response = await apiGet(`/invoices/${invoice.id}/download`)
    if (response.success) {
      const downloadUrl = response.download_url
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `invoice_${invoice.invoice_number}.pdf`
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

const addInvoiceItem = () => {
  invoiceForm.items.push({
    description: '',
    quantity: 1,
    unit_price: 0
  })
}

const removeInvoiceItem = (index) => {
  if (invoiceForm.items.length > 1) {
    invoiceForm.items.splice(index, 1)
  }
}

const calculateSubtotal = () => {
  return invoiceForm.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0)
}

const calculateTax = () => {
  return calculateSubtotal() * (invoiceForm.tax_rate / 100)
}

const calculateTotal = () => {
  return calculateSubtotal() + calculateTax()
}

const saveInvoice = async () => {
  if (!invoiceForm.client_id || !invoiceForm.issue_date || !invoiceForm.due_date) {
    showError('Please fill in all required fields')
    return
  }

  // Validate items
  const validItems = invoiceForm.items.filter(item => item.description && item.quantity > 0 && item.unit_price > 0)
  if (validItems.length === 0) {
    showError('Please add at least one valid item')
    return
  }

  saving.value = true
  try {
    const isEdit = showEditInvoiceModal.value
    const endpoint = isEdit ? `/invoices/${selectedInvoice.value.id}` : '/invoices'
    const method = isEdit ? apiPut : apiPost

    const invoiceData = {
      ...invoiceForm,
      items: validItems,
      subtotal: calculateSubtotal(),
      tax: calculateTax(),
      total: calculateTotal()
    }

    const response = await method(endpoint, invoiceData)
    
    if (response.success) {
      if (isEdit) {
        Object.assign(selectedInvoice.value, response.invoice)
        showSuccess('Invoice updated successfully')
      } else {
        invoices.value.push(response.invoice)
        showSuccess('Invoice created successfully')
      }
      closeModals()
    }
  } catch (error) {
    console.error('Error saving invoice:', error)
    showError('Failed to save invoice')
  } finally {
    saving.value = false
  }
}

const closeModals = () => {
  showAddInvoiceModal.value = false
  showEditInvoiceModal.value = false
  resetInvoiceForm()
}

const closePreviewModal = () => {
  showPreviewModal.value = false
  selectedInvoice.value = null
}

const downloadPreview = () => {
  if (selectedInvoice.value) {
    downloadInvoice(selectedInvoice.value)
  }
}

const printPreview = () => {
  window.print()
}

const resetInvoiceForm = () => {
  Object.assign(invoiceForm, {
    invoice_number: '',
    client_id: '',
    issue_date: new Date().toISOString().split('T')[0],
    due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    status: 'draft',
    currency: 'USD',
    tax_rate: 0,
    notes: '',
    items: [
      {
        description: '',
        quantity: 1,
        unit_price: 0
      }
    ]
  })
  selectedInvoice.value = null
}

// Lifecycle
onMounted(() => {
  loadInvoices()
  loadClients()
})
</script>

<style scoped>
.invoices {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
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

.invoice-controls {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: center;
}

.search-box {
  position: relative;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.filter-dropdown select {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-range input {
  flex: 1;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.date-range span {
  color: var(--text-secondary);
  font-weight: 500;
}

.add-invoice-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add-invoice-btn:hover {
  background: var(--primary-hover);
}

.invoice-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
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

.stat-icon.pending {
  background: var(--warning-color);
}

.stat-icon.paid {
  background: var(--success-color);
}

.stat-icon.overdue {
  background: var(--danger-color);
}

.stat-content h3 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.9rem;
}

.revenue-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.summary-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-weight: 500;
}

.summary-card .amount {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.summary-card .amount.outstanding {
  color: var(--warning-color);
}

.summary-card .period {
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

.invoices-container {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
}

.loading-state, .empty-state {
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

.empty-icon {
  font-size: 3rem;
  color: var(--text-tertiary);
  margin-bottom: 1rem;
}

.invoices-table-container {
  overflow-x: auto;
}

.invoices-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--glass-bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.invoices-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.invoices-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.invoice-row {
  transition: background 0.3s ease;
}

.invoice-row:hover {
  background: var(--glass-bg-hover);
}

.invoice-number {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.number {
  font-weight: 600;
  color: var(--primary-color);
}

.copy-btn {
  padding: 0.25rem 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
}

.copy-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.client-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.client-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.client-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.client-info h4 {
  margin: 0 0 0.25rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.client-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.overdue {
  color: var(--danger-color);
  font-weight: 600;
}

.amount {
  font-weight: 600;
  color: var(--text-primary);
}

.status-badge {
  padding: 0.25rem 0.75rem;
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

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  background: var(--glass-bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.view:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.edit:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.download:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.delete:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
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
  max-width: 900px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1200px;
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

.preview-actions {
  display: flex;
  gap: 0.5rem;
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
  margin-bottom: 2rem;
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

.form-group input.readonly {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
}

.invoice-items-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.add-item-btn {
  padding: 0.5rem 1rem;
  background: var(--success-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add-item-btn:hover {
  background: var(--success-hover);
}

.invoice-items {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
}

.invoice-item {
  margin-bottom: 1rem;
}

.invoice-item:last-child {
  margin-bottom: 0;
}

.item-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr auto;
  gap: 1rem;
  align-items: end;
}

.remove-item-btn {
  width: 36px;
  height: 36px;
  background: var(--danger-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-item-btn:hover {
  background: var(--danger-hover);
}

.invoice-totals {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
  max-width: 400px;
  margin-left: auto;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.total-row:last-child {
  margin-bottom: 0;
}

.total-row.grand-total {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-primary);
  padding-top: 0.75rem;
  border-top: 1px solid var(--glass-border);
}

.total-row label {
  color: var(--text-primary);
  font-weight: 500;
}

.total-row input {
  width: 80px;
  text-align: right;
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

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
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

/* Invoice Preview Styles */
.invoice-preview {
  background: white;
  color: black;
  padding: 2rem;
  border-radius: 8px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #eee;
}

.preview-header h1 {
  margin: 0;
  color: #333;
  font-size: 2rem;
}

.preview-details p {
  margin: 0.25rem 0;
  color: #666;
}

.preview-client {
  margin-bottom: 2rem;
}

.preview-client h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.preview-client p {
  margin: 0.25rem 0;
  color: #666;
}

.preview-items table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 2rem;
}

.preview-items th,
.preview-items td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.preview-items th {
  background: #f8f9fa;
  font-weight: 600;
}

.preview-totals {
  max-width: 300px;
  margin-left: auto;
}

@media (max-width: 768px) {
  .invoices {
    padding: 1rem;
  }
  
  .invoice-controls {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .invoice-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .revenue-summary {
    grid-template-columns: 1fr;
  }
  
  .item-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .preview-header {
    flex-direction: column;
    gap: 1rem;
  }
}

@media print {
  .modal-overlay {
    position: static;
    background: none;
    backdrop-filter: none;
  }
  
  .modal-content {
    box-shadow: none;
    max-width: 100%;
    width: 100%;
    max-height: none;
    overflow: visible;
  }
  
  .modal-header,
  .modal-footer {
    display: none;
  }
}
</style>
