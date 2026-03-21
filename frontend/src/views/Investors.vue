<template>
  <div class="investors">
    <div class="page-header">
      <h1>Investor Relations</h1>
      <p>Financial information, reports, and investor resources</p>
    </div>

    <div class="investors-container">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-content">
          <div class="hero-text">
            <h2>{{ companyData.name }} Investor Relations</h2>
            <p class="hero-tagline">Building Value Through Innovation</p>
            <p class="hero-description">
              We are committed to transparency and providing our investors with comprehensive information about our financial performance, strategic initiatives, and growth opportunities.
            </p>
            <div class="hero-stats">
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.marketCap }}</div>
                <div class="stat-label">Market Cap</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.revenue }}</div>
                <div class="stat-label">Annual Revenue</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.growth }}%</div>
                <div class="stat-label">YoY Growth</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.shareholders }}</div>
                <div class="stat-label">Shareholders</div>
              </div>
            </div>
          </div>
          <div class="hero-image">
            <div class="stock-ticker">
              <div class="ticker-header">
                <h3>{{ companyData.stock.symbol }}</h3>
                <span class="exchange">{{ companyData.stock.exchange }}</span>
              </div>
              <div class="ticker-price">
                <span class="price">${{ companyData.stock.price }}</span>
                <span class="change" :class="{ 'positive': companyData.stock.change > 0, 'negative': companyData.stock.change < 0 }">
                  {{ companyData.stock.change > 0 ? '+' : '' }}{{ companyData.stock.change }}%
                </span>
              </div>
              <div class="ticker-details">
                <div class="detail">
                  <label>Volume:</label>
                  <span>{{ companyData.stock.volume }}</span>
                </div>
                <div class="detail">
                  <label>Market Cap:</label>
                  <span>{{ companyData.stock.marketCap }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Financial Reports -->
      <section class="financial-reports-section">
        <div class="section-header">
          <h2>Financial Reports</h2>
          <div class="header-actions">
            <div class="filter-dropdown">
              <select v-model="reportFilter" @change="filterReports">
                <option value="">All Reports</option>
                <option value="quarterly">Quarterly Reports</option>
                <option value="annual">Annual Reports</option>
                <option value="earnings">Earnings Calls</option>
                <option value="sec">SEC Filings</option>
              </select>
            </div>
            <div class="filter-dropdown">
              <select v-model="yearFilter" @change="filterReports">
                <option value="">All Years</option>
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
                <option value="2021">2021</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading financial reports...</p>
        </div>

        <div v-else-if="filteredReports.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-file-invoice-dollar"></i>
          </div>
          <h3>No reports found</h3>
          <p>Try adjusting your filters or check back later for new reports.</p>
        </div>

        <div v-else class="reports-grid">
          <div 
            v-for="report in paginatedReports" 
            :key="report.id"
            class="report-card"
            @click="viewReport(report)"
          >
            <div class="report-header">
              <div class="report-meta">
                <span class="report-type" :class="report.type">{{ formatReportType(report.type) }}</span>
                <span class="report-date">{{ formatDate(report.date) }}</span>
              </div>
              <div class="report-actions">
                <button class="action-btn download" @click.stop="downloadReport(report)">
                  <i class="fas fa-download"></i>
                </button>
                <button class="action-btn share" @click.stop="shareReport(report)">
                  <i class="fas fa-share"></i>
                </button>
              </div>
            </div>
            
            <div class="report-content">
              <h3>{{ report.title }}</h3>
              <p class="report-summary">{{ report.summary }}</p>
              
              <div class="report-details">
                <div class="detail-item">
                  <label>Period:</label>
                  <span>{{ report.period }}</span>
                </div>
                <div class="detail-item">
                  <label>File Size:</label>
                  <span>{{ report.fileSize }}</span>
                </div>
                <div class="detail-item">
                  <label>Format:</label>
                  <span>{{ report.format }}</span>
                </div>
              </div>
            </div>
            
            <div class="report-footer">
              <div class="key-metrics" v-if="report.metrics">
                <div class="metric" v-for="metric in report.metrics" :key="metric.label">
                  <span class="metric-label">{{ metric.label }}</span>
                  <span class="metric-value">{{ metric.value }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination" v-if="totalReportPages > 1">
          <button 
            class="pagination-btn" 
            :disabled="currentReportPage === 1"
            @click="currentReportPage--"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="page-info">{{ currentReportPage }} / {{ totalReportPages }}</span>
          <button 
            class="pagination-btn" 
            :disabled="currentReportPage === totalReportPages"
            @click="currentReportPage++"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </section>

      <!-- Stock Information -->
      <section class="stock-section">
        <div class="section-header">
          <h2>Stock Information</h2>
          <p>Real-time stock data and historical performance</p>
        </div>
        <div class="stock-grid">
          <div class="stock-card current">
            <div class="card-header">
              <h3>Current Stock Price</h3>
              <div class="live-indicator">
                <span class="live-dot"></span>
                Live
              </div>
            </div>
            <div class="stock-price-display">
              <span class="current-price">${{ stockData.currentPrice }}</span>
              <span class="price-change" :class="{ 'positive': stockData.change > 0, 'negative': stockData.change < 0 }">
                <i class="fas fa-arrow-up" v-if="stockData.change > 0"></i>
                <i class="fas fa-arrow-down" v-else-if="stockData.change < 0"></i>
                <i class="fas fa-minus" v-else></i>
                {{ stockData.change > 0 ? '+' : '' }}{{ stockData.change }}%
              </span>
            </div>
            <div class="stock-details">
              <div class="detail-row">
                <label>Open:</label>
                <span>${{ stockData.open }}</span>
              </div>
              <div class="detail-row">
                <label>High:</label>
                <span>${{ stockData.high }}</span>
              </div>
              <div class="detail-row">
                <label>Low:</label>
                <span>${{ stockData.low }}</span>
              </div>
              <div class="detail-row">
                <label>Volume:</label>
                <span>{{ stockData.volume }}</span>
              </div>
            </div>
          </div>

          <div class="stock-card performance">
            <h3>Performance</h3>
            <div class="performance-grid">
              <div class="performance-item">
                <label>1 Day</label>
                <span :class="{ 'positive': stockData.performance.day > 0, 'negative': stockData.performance.day < 0 }">
                  {{ stockData.performance.day > 0 ? '+' : '' }}{{ stockData.performance.day }}%
                </span>
              </div>
              <div class="performance-item">
                <label>1 Week</label>
                <span :class="{ 'positive': stockData.performance.week > 0, 'negative': stockData.performance.week < 0 }">
                  {{ stockData.performance.week > 0 ? '+' : '' }}{{ stockData.performance.week }}%
                </span>
              </div>
              <div class="performance-item">
                <label>1 Month</label>
                <span :class="{ 'positive': stockData.performance.month > 0, 'negative': stockData.performance.month < 0 }">
                  {{ stockData.performance.month > 0 ? '+' : '' }}{{ stockData.performance.month }}%
                </span>
              </div>
              <div class="performance-item">
                <label>YTD</label>
                <span :class="{ 'positive': stockData.performance.ytd > 0, 'negative': stockData.performance.ytd < 0 }">
                  {{ stockData.performance.ytd > 0 ? '+' : '' }}{{ stockData.performance.ytd }}%
                </span>
              </div>
              <div class="performance-item">
                <label>1 Year</label>
                <span :class="{ 'positive': stockData.performance.year > 0, 'negative': stockData.performance.year < 0 }">
                  {{ stockData.performance.year > 0 ? '+' : '' }}{{ stockData.performance.year }}%
                </span>
              </div>
            </div>
          </div>

          <div class="stock-card key-metrics">
            <h3>Key Metrics</h3>
            <div class="metrics-list">
              <div class="metric-item">
                <label>Market Cap</label>
                <span>{{ stockData.metrics.marketCap }}</span>
              </div>
              <div class="metric-item">
                <label>P/E Ratio</label>
                <span>{{ stockData.metrics.peRatio }}</span>
              </div>
              <div class="metric-item">
                <label>EPS</label>
                <span>${{ stockData.metrics.eps }}</span>
              </div>
              <div class="metric-item">
                <label>Dividend Yield</label>
                <span>{{ stockData.metrics.dividendYield }}%</span>
              </div>
              <div class="metric-item">
                <label>52 Week High</label>
                <span>${{ stockData.metrics.week52High }}</span>
              </div>
              <div class="metric-item">
                <label>52 Week Low</label>
                <span>${{ stockData.metrics.week52Low }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Investor Events -->
      <section class="events-section">
        <div class="section-header">
          <h2>Investor Events</h2>
          <p>Earnings calls, conferences, and shareholder meetings</p>
        </div>
        <div class="events-timeline">
          <div 
            v-for="event in investorEvents" 
            :key="event.id"
            class="event-item"
            @click="viewEvent(event)"
          >
            <div class="event-date">
              <div class="date-day">{{ formatDay(event.date) }}</div>
              <div class="date-month">{{ formatMonth(event.date) }}</div>
            </div>
            <div class="event-content">
              <div class="event-header">
                <h3>{{ event.title }}</h3>
                <span class="event-type" :class="event.type">{{ formatEventType(event.type) }}</span>
              </div>
              <p class="event-description">{{ event.description }}</p>
              <div class="event-details">
                <div class="detail-item">
                  <i class="fas fa-clock"></i>
                  <span>{{ event.time }}</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-globe"></i>
                  <span>{{ event.location }}</span>
                </div>
                <div class="detail-item" v-if="event.webcast">
                  <i class="fas fa-video"></i>
                  <a :href="event.webcast" target="_blank">Webcast Available</a>
                </div>
              </div>
              <div class="event-actions">
                <button class="action-btn" @click.stop="registerForEvent(event)">
                  <i class="fas fa-calendar-plus"></i>
                  Register
                </button>
                <button class="action-btn" @click.stop="addToCalendar(event)">
                  <i class="fas fa-calendar"></i>
                  Add to Calendar
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Corporate Governance -->
      <section class="governance-section">
        <div class="section-header">
          <h2>Corporate Governance</h2>
          <p>Our commitment to ethical business practices</p>
        </div>
        <div class="governance-grid">
          <div 
            v-for="item in governanceItems" 
            :key="item.id"
            class="governance-card"
            @click="viewGovernance(item)"
          >
            <div class="governance-icon">
              <i :class="item.icon"></i>
            </div>
            <div class="governance-content">
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
              <div class="governance-meta">
                <span class="update-date">Updated: {{ formatDate(item.updated) }}</span>
                <span class="file-type">{{ item.fileType }}</span>
              </div>
            </div>
            <div class="governance-action">
              <i class="fas fa-arrow-right"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- FAQ Section -->
      <section class="faq-section">
        <div class="section-header">
          <h2>Investor FAQ</h2>
          <p>Frequently asked questions from our investors</p>
        </div>
        <div class="faq-grid">
          <div 
            v-for="faq in investorFAQs" 
            :key="faq.id"
            class="faq-item"
            @click="toggleFaq(faq.id)"
          >
            <div class="faq-question">
              <h3>{{ faq.question }}</h3>
              <div class="faq-toggle">
                <i class="fas fa-chevron-down" :class="{ 'rotated': faq.isOpen }"></i>
              </div>
            </div>
            <div class="faq-answer" :class="{ 'open': faq.isOpen }">
              <p>{{ faq.answer }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Contact Section -->
      <section class="contact-section">
        <div class="section-header">
          <h2>Investor Relations Contact</h2>
          <p>Get in touch with our investor relations team</p>
        </div>
        <div class="contact-grid">
          <div class="contact-card">
            <div class="contact-icon">
              <i class="fas fa-user-tie"></i>
            </div>
            <div class="contact-info">
              <h3>Investor Relations</h3>
              <p>{{ companyData.investorRelations.name }}</p>
              <p>{{ companyData.investorRelations.title }}</p>
              <div class="contact-details">
                <div class="detail-item">
                  <i class="fas fa-envelope"></i>
                  <a :href="`mailto:${companyData.investorRelations.email}`">{{ companyData.investorRelations.email }}</a>
                </div>
                <div class="detail-item">
                  <i class="fas fa-phone"></i>
                  <a :href="`tel:${companyData.investorRelations.phone}`">{{ companyData.investorRelations.phone }}</a>
                </div>
                <div class="detail-item">
                  <i class="fas fa-clock"></i>
                  <span>{{ companyData.investorRelations.hours }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="contact-card">
            <div class="contact-icon">
              <i class="fas fa-building"></i>
            </div>
            <div class="contact-info">
              <h3>Transfer Agent</h3>
              <p>{{ companyData.transferAgent.name }}</p>
              <div class="contact-details">
                <div class="detail-item">
                  <i class="fas fa-envelope"></i>
                  <a :href="`mailto:${companyData.transferAgent.email}`">{{ companyData.transferAgent.email }}</a>
                </div>
                <div class="detail-item">
                  <i class="fas fa-phone"></i>
                  <a :href="`tel:${companyData.transferAgent.phone}`">{{ companyData.transferAgent.phone }}</a>
                </div>
                <div class="detail-item">
                  <i class="fas fa-globe"></i>
                  <a :href="companyData.transferAgent.website" target="_blank">{{ companyData.transferAgent.website }}</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="cta-section">
        <div class="cta-content">
          <h2>Stay Informed</h2>
          <p>Subscribe to investor updates and announcements</p>
          <div class="cta-buttons">
            <button class="cta-btn primary" @click="subscribeInvestorUpdates">
              <i class="fas fa-envelope"></i>
              Subscribe to Updates
            </button>
            <button class="cta-btn secondary" @click="setupAlerts">
              <i class="fas fa-bell"></i>
              Set Up Alerts
            </button>
            <button class="cta-btn outline" @click="downloadInvestorKit">
              <i class="fas fa-download"></i>
              Download Investor Kit
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const loading = ref(false)
const reportFilter = ref('')
const yearFilter = ref('')
const currentReportPage = ref(1)
const reportsPerPage = ref(6)

// Company data
const companyData = reactive({
  name: 'Digital HQ',
  stats: {
    marketCap: '$2.5B',
    revenue: '$450M',
    growth: 35,
    shareholders: '15,000+'
  },
  stock: {
    symbol: 'DHQ',
    exchange: 'NASDAQ',
    price: '125.50',
    change: 2.35,
    volume: '1.2M',
    marketCap: '$2.5B'
  },
  investorRelations: {
    name: 'Sarah Johnson',
    title: 'VP, Investor Relations',
    email: 'investors@company.com',
    phone: '+1 (415) 555-0100',
    hours: 'Mon-Fri 9AM-6PM EST'
  },
  transferAgent: {
    name: 'Computershare Trust Company',
    email: 'transfer@company.com',
    phone: '+1 (800) 555-0200',
    website: 'https://transfer.company.com'
  }
})

// Stock data
const stockData = reactive({
  currentPrice: '125.50',
  change: 2.35,
  open: '123.20',
  high: '126.80',
  low: '122.90',
  volume: '1,234,567',
  performance: {
    day: 1.9,
    week: 3.2,
    month: 8.5,
    ytd: 15.3,
    year: 28.7
  },
  metrics: {
    marketCap: '$2.5B',
    peRatio: '28.5',
    eps: '4.40',
    dividendYield: '1.2',
    week52High: '145.20',
    week52Low: '89.30'
  }
})

// Financial reports
const financialReports = ref([
  {
    id: 1,
    title: 'Q4 2023 Earnings Report',
    summary: 'Strong fourth quarter results with revenue growth of 35% year-over-year and record earnings per share.',
    type: 'quarterly',
    date: '2024-01-25T00:00:00Z',
    period: 'Q4 2023',
    fileSize: '2.8 MB',
    format: 'PDF',
    metrics: [
      { label: 'Revenue', value: '$125M' },
      { label: 'EPS', value: '$1.15' },
      { label: 'Growth', value: '+35%' }
    ]
  },
  {
    id: 2,
    title: '2023 Annual Report',
    summary: 'Comprehensive annual report highlighting company achievements, financial performance, and strategic initiatives.',
    type: 'annual',
    date: '2024-01-15T00:00:00Z',
    period: 'FY 2023',
    fileSize: '8.5 MB',
    format: 'PDF',
    metrics: [
      { label: 'Revenue', value: '$450M' },
      { label: 'Net Income', value: '$78M' },
      { label: 'YoY Growth', value: '+35%' }
    ]
  },
  {
    id: 3,
    title: 'Q3 2023 Earnings Report',
    summary: 'Third quarter results exceeded expectations with strong product adoption and customer growth.',
    type: 'quarterly',
    date: '2023-10-20T00:00:00Z',
    period: 'Q3 2023',
    fileSize: '2.4 MB',
    format: 'PDF',
    metrics: [
      { label: 'Revenue', value: '$118M' },
      { label: 'EPS', value: '$1.05' },
      { label: 'Growth', value: '+32%' }
    ]
  },
  {
    id: 4,
    title: 'Form 10-K Annual Report',
    summary: 'SEC filing with comprehensive financial statements and business overview.',
    type: 'sec',
    date: '2024-01-10T00:00:00Z',
    period: 'FY 2023',
    fileSize: '4.2 MB',
    format: 'PDF'
  },
  {
    id: 5,
    title: 'Q4 2023 Earnings Call Transcript',
    summary: 'Full transcript of fourth quarter earnings conference call with management.',
    type: 'earnings',
    date: '2024-01-26T00:00:00Z',
    period: 'Q4 2023',
    fileSize: '1.8 MB',
    format: 'PDF'
  }
])

// Investor events
const investorEvents = ref([
  {
    id: 1,
    title: 'Q4 2023 Earnings Call',
    description: 'Management discussion of fourth quarter financial results and business outlook.',
    type: 'earnings',
    date: '2024-01-25T00:00:00Z',
    time: '2:00 PM EST',
    location: 'Webcast',
    webcast: 'https://webcast.company.com/q4-2023'
  },
  {
    id: 2,
    title: 'Annual Shareholder Meeting',
    description: 'Annual meeting for shareholders to vote on corporate matters and hear from management.',
    type: 'shareholder',
    date: '2024-05-15T00:00:00Z',
    time: '10:00 AM EST',
    location: 'San Francisco, CA',
    webcast: 'https://webcast.company.com/annual-meeting-2024'
  },
  {
    id: 3,
    title: 'Investor Day 2024',
    description: 'Comprehensive presentation of company strategy, products, and financial outlook.',
    type: 'conference',
    date: '2024-03-20T00:00:00Z',
    time: '9:00 AM EST',
    location: 'New York, NY',
    webcast: 'https://webcast.company.com/investor-day-2024'
  }
])

// Corporate governance
const governanceItems = ref([
  {
    id: 1,
    title: 'Code of Business Conduct',
    description: 'Guidelines for ethical business practices and employee behavior.',
    icon: 'fas fa-gavel',
    updated: '2024-01-01T00:00:00Z',
    fileType: 'PDF'
  },
  {
    id: 2,
    title: 'Corporate Governance Guidelines',
    description: 'Framework for board structure, committees, and governance practices.',
    icon: 'fas fa-balance-scale',
    updated: '2024-01-01T00:00:00Z',
    fileType: 'PDF'
  },
  {
    id: 3,
    title: 'Audit Committee Charter',
    description: 'Responsibilities and procedures for the audit committee.',
    icon: 'fas fa-clipboard-check',
    updated: '2024-01-01T00:00:00Z',
    fileType: 'PDF'
  },
  {
    id: 4,
    title: 'Compensation Committee Charter',
    description: 'Guidelines for executive compensation and incentive programs.',
    icon: 'fas fa-dollar-sign',
    updated: '2024-01-01T00:00:00Z',
    fileType: 'PDF'
  }
])

// Investor FAQs
const investorFAQs = ref([
  {
    id: 1,
    question: 'How can I purchase Digital HQ stock?',
    answer: 'You can purchase our stock through any brokerage firm. Our stock trades on NASDAQ under the ticker symbol DHQ.',
    isOpen: false
  },
  {
    id: 2,
    question: 'When does Digital HQ report earnings?',
    answer: 'We typically report earnings within 45 days after quarter end and 75 days after year-end. Specific dates are announced in advance.',
    isOpen: false
  },
  {
    id: 3,
    question: 'Does Digital HQ pay dividends?',
    answer: 'Currently, we reinvest earnings back into the business to fuel growth. The board regularly reviews dividend policy.',
    isOpen: false
  },
  {
    id: 4,
    question: 'How can I receive investor communications?',
    answer: 'You can subscribe to email updates through our investor relations page or follow us on major financial news platforms.',
    isOpen: false
  },
  {
    id: 5,
    question: 'Who is Digital HQ\'s transfer agent?',
    answer: 'Computershare Trust Company serves as our transfer agent for all shareholder services including stock transfers and dividend reinvestment.',
    isOpen: false
  }
])

// Computed properties
const filteredReports = computed(() => {
  let filtered = financialReports.value

  if (reportFilter.value) {
    filtered = filtered.filter(report => report.type === reportFilter.value)
  }

  if (yearFilter.value) {
    filtered = filtered.filter(report => new Date(report.date).getFullYear().toString() === yearFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const paginatedReports = computed(() => {
  const start = (currentReportPage.value - 1) * reportsPerPage.value
  const end = start + reportsPerPage.value
  return filteredReports.value.slice(start, end)
})

const totalReportPages = computed(() => {
  return Math.ceil(filteredReports.value.length / reportsPerPage.value)
})

// Methods
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatDay = (dateString) => {
  return new Date(dateString).getDate()
}

const formatMonth = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', { month: 'short' })
}

const formatReportType = (type) => {
  const types = {
    quarterly: 'Quarterly',
    annual: 'Annual',
    earnings: 'Earnings',
    sec: 'SEC Filing'
  }
  return types[type] || type
}

const formatEventType = (type) => {
  const types = {
    earnings: 'Earnings',
    shareholder: 'Shareholder',
    conference: 'Conference'
  }
  return types[type] || type
}

const filterReports = () => {
  currentReportPage.value = 1
}

const viewReport = (report) => {
  showSuccess(`Opening report: ${report.title}`)
  // In a real app, this would open report
}

const downloadReport = (report) => {
  showSuccess(`Downloading report: ${report.title}`)
  // In a real app, this would download report
}

const shareReport = (report) => {
  showSuccess(`Sharing report: ${report.title}`)
  // In a real app, this would open share dialog
}

const viewEvent = (event) => {
  showSuccess(`Viewing event: ${event.title}`)
  // In a real app, this would navigate to event details
}

const registerForEvent = (event) => {
  showSuccess(`Registering for: ${event.title}`)
  // In a real app, this would open registration form
}

const addToCalendar = (event) => {
  showSuccess(`Adding to calendar: ${event.title}`)
  // In a real app, this would create calendar event
}

const viewGovernance = (item) => {
  showSuccess(`Opening: ${item.title}`)
  // In a real app, this would open governance document
}

const toggleFaq = (faqId) => {
  const faq = investorFAQs.value.find(f => f.id === faqId)
  if (faq) {
    faq.isOpen = !faq.isOpen
  }
}

const subscribeInvestorUpdates = () => {
  showSuccess('Opening investor updates subscription...')
  // In a real app, this would open subscription form
}

const setupAlerts = () => {
  showSuccess('Opening stock alerts setup...')
  // In a real app, this would open alerts configuration
}

const downloadInvestorKit = () => {
  showSuccess('Downloading investor kit...')
  // In a real app, this would download investor kit
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/investors/reports')
    // if (response.success) {
    //   financialReports.value = response.reports || []
    // }
    
    // For demo, use mock data
    loading.value = false
  } catch (error) {
    console.error('Error loading financial reports:', error)
    showError('Failed to load financial reports')
    loading.value = false
  }
})
</script>

<style scoped>
.investors {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 4rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.page-header p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.investors-container {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.hero-section,
.financial-reports-section,
.stock-section,
.events-section,
.governance-section,
.faq-section,
.contact-section,
.cta-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 3rem;
}

.hero-section {
  margin-bottom: 4rem;
}

.hero-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 3rem;
  align-items: center;
}

.hero-text h2 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.hero-tagline {
  font-size: 1.3rem;
  color: var(--primary-color);
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.hero-description {
  font-size: 1.1rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 2rem;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.hero-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

.stock-ticker {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  width: 100%;
  max-width: 300px;
}

.ticker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.ticker-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.exchange {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.ticker-price {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.price {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.change {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
}

.change.positive {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.change.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.ticker-details {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
}

.ticker-details .detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.ticker-details label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.ticker-details span {
  color: var(--text-primary);
  font-weight: 600;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.section-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.filter-dropdown {
  position: relative;
}

.filter-dropdown select {
  padding: 0.75rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  min-width: 150px;
}

.loading-state,
.empty-state {
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

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.report-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.report-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.report-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.report-type {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  width: fit-content;
}

.report-type.quarterly {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.report-type.annual {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.report-type.earnings {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.report-type.sec {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.report-date {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.report-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.download:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.action-btn.share:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.report-content h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.report-summary {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.report-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.report-details .detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.report-details label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.report-details span {
  color: var(--text-primary);
  font-weight: 600;
}

.key-metrics {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.metric-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.metric-value {
  font-size: 0.9rem;
  color: var(--text-primary);
  font-weight: 600;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--glass-bg-hover);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-primary);
  font-weight: 600;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.stock-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.stock-card.current {
  grid-column: span 2;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-header h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--success-color);
  font-size: 0.9rem;
  font-weight: 600;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: var(--success-color);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.stock-price-display {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.current-price {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
}

.price-change {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.1rem;
}

.price-change.positive {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.price-change.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stock-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row label {
  color: var(--text-secondary);
  font-weight: 500;
}

.detail-row span {
  color: var(--text-primary);
  font-weight: 600;
}

.performance-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.performance-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.performance-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.performance-item span {
  font-size: 1.1rem;
  font-weight: 600;
}

.performance-item span.positive {
  color: var(--success-color);
}

.performance-item span.negative {
  color: var(--danger-color);
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-item label {
  color: var(--text-secondary);
  font-weight: 500;
}

.metric-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.events-timeline {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.event-item {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 2rem;
  align-items: start;
  cursor: pointer;
  transition: all 0.3s ease;
}

.event-item:hover {
  transform: translateX(10px);
}

.event-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  padding: 1rem;
  min-width: 80px;
}

.date-day {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
}

.date-month {
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.event-content {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.event-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.event-type {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.event-type.earnings {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.event-type.shareholder {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.event-type.conference {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.event-description {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.event-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.event-details .detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.event-details .detail-item i {
  color: var(--primary-color);
}

.event-details .detail-item a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.event-details .detail-item a:hover {
  text-decoration: underline;
}

.event-actions {
  display: flex;
  gap: 1rem;
}

.governance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.governance-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.governance-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.governance-icon {
  width: 60px;
  height: 60px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.governance-content {
  flex: 1;
}

.governance-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.governance-content p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.governance-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.update-date,
.file-type {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.governance-action {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.governance-card:hover .governance-action {
  transform: scale(1.1);
}

.faq-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.faq-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.faq-item:hover {
  border-color: var(--primary-color);
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  cursor: pointer;
}

.faq-question h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.faq-toggle {
  transition: transform 0.3s ease;
}

.faq-toggle i {
  color: var(--text-secondary);
}

.faq-toggle.rotated {
  transform: rotate(180deg);
}

.faq-answer {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
  background: var(--glass-bg-tertiary);
}

.faq-answer.open {
  max-height: 200px;
}

.faq-answer p {
  padding: 1.5rem;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.contact-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  gap: 1.5rem;
}

.contact-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.contact-info {
  flex: 1;
}

.contact-info h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.contact-info p {
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.contact-details .detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.contact-details .detail-item i {
  width: 20px;
  color: var(--primary-color);
}

.contact-details .detail-item a {
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 500;
}

.contact-details .detail-item a:hover {
  text-decoration: underline;
}

.cta-section {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  text-align: center;
  border-radius: 20px;
}

.cta-content h2 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.cta-content p {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
}

.cta-btn.primary {
  background: white;
  color: var(--primary-color);
}

.cta-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 255, 255, 0.3);
}

.cta-btn.secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.cta-btn.secondary:hover {
  background: white;
  color: var(--primary-color);
}

.cta-btn.outline {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.cta-btn.outline:hover {
  background: white;
  color: var(--primary-color);
}

@media (max-width: 768px) {
  .investors {
    padding: 1rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .hero-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .hero-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stock-grid {
    grid-template-columns: 1fr;
  }
  
  .stock-card.current {
    grid-column: span 1;
  }
  
  .performance-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .event-item {
    grid-template-columns: 80px 1fr;
    gap: 1rem;
  }
  
  .governance-grid,
  .contact-grid {
    grid-template-columns: 1fr;
  }
  
  .governance-card,
  .contact-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>
