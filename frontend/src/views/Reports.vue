<template>
  <div class="reports">
    <div class="page-header">
      <h1>Reports</h1>
      <p>Generate and view comprehensive reports for your business</p>
    </div>

    <!-- Report Controls -->
    <div class="report-controls">
      <div class="control-section">
        <h3>Report Type</h3>
        <select v-model="selectedReportType" @change="updateReportConfig">
          <option value="sales">Sales Report</option>
          <option value="orders">Orders Report</option>
          <option value="users">Users Report</option>
          <option value="products">Products Report</option>
          <option value="financial">Financial Report</option>
          <option value="analytics">Analytics Report</option>
        </select>
      </div>

      <div class="control-section">
        <h3>Date Range</h3>
        <div class="date-range">
          <input 
            v-model="dateRange.start" 
            type="date" 
            :max="dateRange.end"
            @change="generateReport"
          />
          <span>to</span>
          <input 
            v-model="dateRange.end" 
            type="date" 
            :min="dateRange.start"
            @change="generateReport"
          />
        </div>
      </div>

      <div class="control-section">
        <h3>Format</h3>
        <div class="format-options">
          <button 
            v-for="format in exportFormats" 
            :key="format.value"
            :class="['format-btn', { active: selectedFormat === format.value }]"
            @click="selectedFormat = format.value"
          >
            {{ format.label }}
          </button>
        </div>
      </div>

      <div class="control-section">
        <button 
          class="generate-btn" 
          @click="generateReport"
          :disabled="loading"
        >
          <span v-if="!loading">Generate Report</span>
          <span v-else>Generating...</span>
        </button>
        <button 
          v-if="reportData" 
          class="export-btn" 
          @click="exportReport"
          :disabled="exporting"
        >
          <span v-if="!exporting">Export {{ selectedFormat.toUpperCase() }}</span>
          <span v-else>Exporting...</span>
        </button>
      </div>
    </div>

    <!-- Report Preview -->
    <div v-if="reportData" class="report-preview">
      <div class="report-header">
        <h2>{{ getReportTitle() }}</h2>
        <div class="report-meta">
          <span>Generated: {{ new Date().toLocaleString() }}</span>
          <span>Period: {{ formatDate(dateRange.start) }} - {{ formatDate(dateRange.end) }}</span>
          <span>Total Records: {{ reportData.totalRecords || 0 }}</span>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="summary-cards">
        <div 
          v-for="(summary, index) in reportData.summary" 
          :key="index"
          class="summary-card"
        >
          <div class="summary-icon">
            <i :class="summary.icon"></i>
          </div>
          <div class="summary-content">
            <h4>{{ summary.label }}</h4>
            <p class="summary-value">{{ formatValue(summary.value, summary.format) }}</p>
            <span 
              v-if="summary.change" 
              :class="['summary-change', summary.change > 0 ? 'positive' : 'negative']"
            >
              {{ summary.change > 0 ? '↑' : '↓' }} {{ Math.abs(summary.change) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- Report Table -->
      <div class="report-table-container">
        <table class="report-table">
          <thead>
            <tr>
              <th v-for="column in reportData.columns" :key="column.key">
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in reportData.rows" :key="index">
              <td v-for="column in reportData.columns" :key="column.key">
                {{ formatTableCell(row[column.key], column.format) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Charts Section -->
      <div v-if="reportData.charts" class="report-charts">
        <h3>Visual Analytics</h3>
        <div class="charts-grid">
          <div 
            v-for="(chart, index) in reportData.charts" 
            :key="index"
            class="chart-container"
          >
            <h4>{{ chart.title }}</h4>
            <canvas :ref="`chart-${index}`"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-icon">
        <i class="fas fa-chart-bar"></i>
      </div>
      <h3>No Report Generated</h3>
      <p>Select report type and date range, then click "Generate Report" to get started</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Generating your report...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { apiGet } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const selectedReportType = ref('sales')
const selectedFormat = ref('pdf')
const loading = ref(false)
const exporting = ref(false)
const reportData = ref(null)
const charts = ref([])

const dateRange = reactive({
  start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
  end: new Date().toISOString().split('T')[0] // Today
})

const exportFormats = [
  { label: 'PDF', value: 'pdf' },
  { label: 'Excel', value: 'excel' },
  { label: 'CSV', value: 'csv' },
  { label: 'JSON', value: 'json' }
]

// Computed properties
const getReportTitle = () => {
  const titles = {
    sales: 'Sales Report',
    orders: 'Orders Report',
    users: 'Users Report',
    products: 'Products Report',
    financial: 'Financial Report',
    analytics: 'Analytics Report'
  }
  return titles[selectedReportType.value] || 'Report'
}

// Methods
const updateReportConfig = () => {
  // Update date range defaults based on report type
  const now = new Date()
  let startDays = 30 // Default 30 days

  switch (selectedReportType.value) {
    case 'financial':
      startDays = 90 // 3 months for financial
      break
    case 'analytics':
      startDays = 7 // 1 week for analytics
      break
    case 'users':
      startDays = 60 // 2 months for users
      break
  }

  dateRange.start = new Date(now - startDays * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  dateRange.end = now.toISOString().split('T')[0]
}

const generateReport = async () => {
  if (loading.value) return

  loading.value = true
  reportData.value = null

  try {
    const params = {
      type: selectedReportType.value,
      start_date: dateRange.start,
      end_date: dateRange.end,
      format: 'json' // Always get JSON for preview
    }

    const response = await apiGet('/reports/generate', params)
    
    if (response.success) {
      reportData.value = response.data
      showSuccess('Report generated successfully!')
      
      // Render charts after DOM update
      await nextTick()
      renderCharts()
    } else {
      showError('Failed to generate report: ' + (response.message || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error generating report:', error)
    showError('Failed to generate report: ' + error.message)
  } finally {
    loading.value = false
  }
}

const exportReport = async () => {
  if (exporting.value || !reportData.value) return

  exporting.value = true

  try {
    const params = {
      type: selectedReportType.value,
      start_date: dateRange.start,
      end_date: dateRange.end,
      format: selectedFormat.value
    }

    const response = await apiGet('/reports/export', params)
    
    if (response.success) {
      // Create download link
      const downloadUrl = response.download_url
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `${selectedReportType.value}_report_${dateRange.start}_to_${dateRange.end}.${selectedFormat.value}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      showSuccess(`Report exported as ${selectedFormat.value.toUpperCase()} successfully!`)
    } else {
      showError('Failed to export report: ' + (response.message || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error exporting report:', error)
    showError('Failed to export report: ' + error.message)
  } finally {
    exporting.value = false
  }
}

const renderCharts = () => {
  // This would integrate with Chart.js or similar library
  // For now, we'll just log that charts would be rendered
  console.log('Charts would be rendered here:', reportData.value?.charts)
}

const formatValue = (value, format) => {
  if (!value) return '0'

  switch (format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value)
    case 'percentage':
      return `${value}%`
    case 'number':
      return new Intl.NumberFormat().format(value)
    case 'date':
      return new Date(value).toLocaleDateString()
    default:
      return value
  }
}

const formatTableCell = (value, format) => {
  return formatValue(value, format)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  updateReportConfig()
})
</script>

<style scoped>
.reports {
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

.report-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.control-section h3 {
  margin-bottom: 1rem;
  color: var(--text-primary);
  font-weight: 600;
}

.control-section select {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
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
}

.date-range span {
  color: var(--text-secondary);
  font-weight: 500;
}

.format-options {
  display: flex;
  gap: 0.5rem;
}

.format-btn {
  flex: 1;
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.format-btn:hover {
  background: var(--glass-bg-hover);
}

.format-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.generate-btn, .export-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-right: 0.5rem;
}

.generate-btn {
  background: var(--primary-color);
  color: white;
}

.generate-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.export-btn {
  background: var(--success-color);
  color: white;
}

.export-btn:hover:not(:disabled) {
  background: var(--success-hover);
}

.generate-btn:disabled, .export-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.report-preview {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.report-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.report-header h2 {
  font-size: 1.8rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.report-meta {
  display: flex;
  gap: 2rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.summary-icon {
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

.summary-content h4 {
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.summary-change {
  font-size: 0.8rem;
  font-weight: 600;
}

.summary-change.positive {
  color: var(--success-color);
}

.summary-change.negative {
  color: var(--danger-color);
}

.report-table-container {
  overflow-x: auto;
  margin-bottom: 2rem;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--glass-bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.report-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.report-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.report-table tr:last-child td {
  border-bottom: none;
}

.report-charts {
  margin-top: 2rem;
}

.report-charts h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.chart-container {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.chart-container h4 {
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.empty-state, .loading-state {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
}

.empty-icon, .loading-spinner {
  font-size: 3rem;
  color: var(--text-tertiary);
  margin-bottom: 1rem;
}

.loading-spinner {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 3px solid var(--glass-border);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .reports {
    padding: 1rem;
  }
  
  .report-controls {
    grid-template-columns: 1fr;
    padding: 1.5rem;
  }
  
  .report-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
