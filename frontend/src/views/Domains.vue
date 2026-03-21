<template>
  <div class="domains">
    <div class="page-header">
      <h1>Domain Management</h1>
      <p>Manage domain names, DNS records, and SSL certificates</p>
    </div>

    <!-- Domain Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-globe"></i>
          </div>
          <div class="card-content">
            <h3>{{ domainStats.totalDomains }}</h3>
            <p>Total Domains</p>
            <span class="domain-count">{{ domainStats.activeDomains }} active</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon certificates">
            <i class="fas fa-shield-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ domainStats.totalCertificates }}</h3>
            <p>SSL Certificates</p>
            <span class="cert-count">{{ domainStats.validCertificates }} valid</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon dns">
            <i class="fas fa-server"></i>
          </div>
          <div class="card-content">
            <h3>{{ domainStats.totalRecords }}</h3>
            <p>DNS Records</p>
            <span class="record-count">{{ domainStats.recentRecords }} recent</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon traffic">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="card-content">
            <h3>{{ domainStats.totalTraffic }}</h3>
            <p>Total Traffic</p>
            <span class="traffic-status">{{ domainStats.todayTraffic }} today</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="add-domain-btn" @click="showAddDomainModal = true">
          <i class="fas fa-plus"></i>
          Add Domain
        </button>
        <button class="dns-btn" @click="showDNSModal = true">
          <i class="fas fa-server"></i>
          DNS Manager
        </button>
        <button class="ssl-btn" @click="showSSLModal = true">
          <i class="fas fa-shield-alt"></i>
          SSL Manager
        </button>
        <button class="verify-btn" @click="verifyAllDomains">
          <i class="fas fa-check-circle"></i>
          Verify All
        </button>
      </div>
    </div>

    <!-- Domain List -->
    <div class="domains-section">
      <div class="section-header">
        <h2>Domain Names</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterDomains">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="pending">Pending</option>
              <option value="expired">Expired</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div class="view-toggle">
            <button 
              :class="['view-btn', { active: viewMode === 'grid' }]"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'list' }]"
              @click="viewMode = 'list'"
            >
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading domains...</p>
      </div>

      <div v-else-if="filteredDomains.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-globe"></i>
        </div>
        <h3>No domains found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="domains-grid">
          <div 
            v-for="domain in filteredDomains" 
            :key="domain.id"
            class="domain-card"
            :class="{ 'pending': domain.status === 'pending', 'expired': domain.status === 'expired', 'error': domain.status === 'error' }"
          >
            <div class="domain-header">
              <div class="domain-icon">
                <i class="fas fa-globe"></i>
              </div>
              <div class="domain-status">
                <span :class="['status-badge', domain.status]">{{ domain.status }}</span>
              </div>
            </div>

            <div class="domain-content">
              <h3>{{ domain.name }}</h3>
              <p>{{ domain.description }}</p>
              
              <div class="domain-info">
                <span class="registrar">{{ domain.registrar }}</span>
                <span class="expires">{{ formatDate(domain.expiresAt) }}</span>
                <span class="ssl">{{ domain.sslStatus }}</span>
              </div>

              <div class="domain-stats">
                <div class="stat-item">
                  <label>DNS Records:</label>
                  <span>{{ domain.dnsRecords }}</span>
                </div>
                <div class="stat-item">
                  <label>SSL Status:</label>
                  <span :class="getSSLClass(domain.sslStatus)">{{ domain.sslStatus }}</span>
                </div>
                <div class="stat-item">
                  <label>Verified:</label>
                  <span>{{ domain.verified ? 'Yes' : 'No' }}</span>
                </div>
              </div>

              <div class="domain-actions">
                <button class="action-btn verify" @click="verifyDomain(domain)">
                  <i class="fas fa-check-circle"></i>
                  Verify
                </button>
                <button class="action-btn dns" @click="manageDNS(domain)">
                  <i class="fas fa-server"></i>
                  DNS
                </button>
                <button class="action-btn ssl" @click="manageSSL(domain)">
                  <i class="fas fa-shield-alt"></i>
                  SSL
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="domains-list">
          <div 
            v-for="domain in filteredDomains" 
            :key="domain.id"
            class="domain-list-card"
            :class="{ 'pending': domain.status === 'pending', 'expired': domain.status === 'expired', 'error': domain.status === 'error' }"
          >
            <div class="domain-list-header">
              <div class="domain-list-info">
                <div class="domain-icon">
                  <i class="fas fa-globe"></i>
                </div>
                <div class="domain-details">
                  <h3>{{ domain.name }}</h3>
                  <p>{{ domain.description }}</p>
                  <div class="domain-info">
                    <span class="registrar">{{ domain.registrar }}</span>
                    <span class="expires">{{ formatDate(domain.expiresAt) }}</span>
                    <span :class="['status-badge', domain.status]">{{ domain.status }}</span>
                    <span class="ssl">{{ domain.sslStatus }}</span>
                  </div>
                </div>
              </div>
              <div class="domain-list-stats">
                <div class="stat-item">
                  <label>DNS Records:</label>
                  <span>{{ domain.dnsRecords }}</span>
                </div>
                <div class="stat-item">
                  <label>SSL Status:</label>
                  <span :class="getSSLClass(domain.sslStatus)">{{ domain.sslStatus }}</span>
                </div>
                <div class="stat-item">
                  <label>Verified:</label>
                  <span>{{ domain.verified ? 'Yes' : 'No' }}</span>
                </div>
              </div>
              <div class="domain-list-actions">
                <button class="action-btn verify" @click="verifyDomain(domain)">
                  <i class="fas fa-check-circle"></i>
                </button>
                <button class="action-btn dns" @click="manageDNS(domain)">
                  <i class="fas fa-server"></i>
                </button>
                <button class="action-btn ssl" @click="manageSSL(domain)">
                  <i class="fas fa-shield-alt"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- DNS Records -->
    <div class="dns-section">
      <div class="section-header">
        <h2>DNS Records</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="dnsFilter" @change="filterDNSRecords">
              <option value="">All Records</option>
              <option value="A">A Records</option>
              <option value="AAAA">AAAA Records</option>
              <option value="CNAME">CNAME Records</option>
              <option value="MX">MX Records</option>
              <option value="TXT">TXT Records</option>
              <option value="NS">NS Records</option>
            </select>
          </div>
          <button class="add-record-btn" @click="showAddRecordModal = true">
            <i class="fas fa-plus"></i>
            Add Record
          </button>
        </div>
      </div>

      <div class="dns-table-container">
        <table class="dns-table">
          <thead>
            <tr>
              <th>Domain</th>
              <th>Type</th>
              <th>Name</th>
              <th>Value</th>
              <th>TTL</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="record in filteredDNSRecords" 
              :key="record.id"
              :class="['dns-row', record.status]"
            >
              <td>{{ record.domain }}</td>
              <td>
                <span class="record-type">{{ record.type }}</span>
              </td>
              <td>{{ record.name }}</td>
              <td class="record-value">{{ record.value }}</td>
              <td>{{ record.ttl }}</td>
              <td>
                <span :class="['status-badge', record.status]">{{ record.status }}</span>
              </td>
              <td>
                <button class="action-btn edit" @click="editDNSRecord(record)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete" @click="deleteDNSRecord(record)">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- SSL Certificates -->
    <div class="ssl-section">
      <div class="section-header">
        <h2>SSL Certificates</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="sslFilter" @change="filterCertificates">
              <option value="">All Certificates</option>
              <option value="valid">Valid</option>
              <option value="expiring">Expiring Soon</option>
              <option value="expired">Expired</option>
              <option value="error">Error</option>
            </select>
          </div>
          <button class="add-cert-btn" @click="showAddCertModal = true">
            <i class="fas fa-plus"></i>
            Add Certificate
          </button>
        </div>
      </div>

      <div class="certificates-grid">
        <div 
          v-for="cert in filteredCertificates" 
          :key="cert.id"
          class="cert-card"
          :class="{ 'expiring': cert.status === 'expiring', 'expired': cert.status === 'expired', 'error': cert.status === 'error' }"
        >
          <div class="cert-header">
            <div class="cert-icon">
              <i class="fas fa-shield-alt"></i>
            </div>
            <div class="cert-status">
              <span :class="['status-badge', cert.status]">{{ cert.status }}</span>
            </div>
          </div>

          <div class="cert-content">
            <h3>{{ cert.domain }}</h3>
            <p>{{ cert.issuer }}</p>
            
            <div class="cert-info">
              <span class="algorithm">{{ cert.algorithm }}</span>
              <span class="expires">{{ formatDate(cert.expiresAt) }}</span>
              <span class="days">{{ cert.daysUntilExpiry }} days</span>
            </div>

            <div class="cert-details">
              <div class="detail-item">
                <label>Serial:</label>
                <span>{{ cert.serialNumber }}</span>
              </div>
              <div class="detail-item">
                <label>Fingerprint:</label>
                <span>{{ cert.fingerprint }}</span>
              </div>
            </div>

            <div class="cert-actions">
              <button class="action-btn renew" @click="renewCertificate(cert)">
                <i class="fas fa-sync"></i>
                Renew
              </button>
              <button class="action-btn download" @click="downloadCertificate(cert)">
                <i class="fas fa-download"></i>
                Download
              </button>
              <button class="action-btn revoke" @click="revokeCertificate(cert)">
                <i class="fas fa-ban"></i>
                Revoke
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Domain Modal -->
    <div v-if="showAddDomainModal" class="modal-overlay" @click="closeAddDomainModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add Domain</h2>
          <button class="close-btn" @click="closeAddDomainModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="domain-form">
            <div class="form-group">
              <label>Domain Name *</label>
              <input 
                v-model="domainForm.name" 
                type="text" 
                placeholder="example.com"
                required
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="domainForm.description" 
                placeholder="Describe this domain"
                rows="3"
              ></textarea>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Registrar</label>
                <select v-model="domainForm.registrar">
                  <option value="GoDaddy">GoDaddy</option>
                  <option value="Namecheap">Namecheap</option>
                  <option value="Google Domains">Google Domains</option>
                  <option value="Cloudflare">Cloudflare</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div class="form-group">
                <label>Auto-renew</label>
                <select v-model="domainForm.autoRenew">
                  <option value="yes">Yes</option>
                  <option value="no">No</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Nameservers</label>
              <div class="nameservers-container">
                <div 
                  v-for="(nameserver, index) in domainForm.nameservers" 
                  :key="index"
                  class="nameserver-item"
                >
                  <input 
                    v-model="nameserver.value" 
                    type="text" 
                    placeholder="ns1.example.com"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeNameserver(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-nameserver-btn" @click="addNameserver">
                  <i class="fas fa-plus"></i>
                  Add Nameserver
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeAddDomainModal">Cancel</button>
          <button class="btn-primary" @click="addDomain">
            <i class="fas fa-plus"></i>
            Add Domain
          </button>
        </div>
      </div>
    </div>

    <!-- Add DNS Record Modal -->
    <div v-if="showAddRecordModal" class="modal-overlay" @click="closeAddRecordModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add DNS Record</h2>
          <button class="close-btn" @click="closeAddRecordModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="dns-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Domain *</label>
                <select v-model="dnsForm.domainId" required>
                  <option value="">Select domain</option>
                  <option 
                    v-for="domain in domains.value" 
                    :key="domain.id"
                    :value="domain.id"
                  >
                    {{ domain.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Record Type *</label>
                <select v-model="dnsForm.type" required>
                  <option value="A">A</option>
                  <option value="AAAA">AAAA</option>
                  <option value="CNAME">CNAME</option>
                  <option value="MX">MX</option>
                  <option value="TXT">TXT</option>
                  <option value="NS">NS</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Name</label>
              <input 
                v-model="dnsForm.name" 
                type="text" 
                placeholder="www"
              />
            </div>

            <div class="form-group">
              <label>Value *</label>
              <input 
                v-model="dnsForm.value" 
                type="text" 
                placeholder="192.168.1.1"
                required
              />
            </div>

            <div class="form-group">
              <label>TTL</label>
              <select v-model="dnsForm.ttl">
                <option value="300">5 minutes</option>
                <option value="600">10 minutes</option>
                <option value="1800">30 minutes</option>
                <option value="3600">1 hour</option>
                <option value="86400">1 day</option>
                <option value="604800">1 week</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeAddRecordModal">Cancel</button>
          <button class="btn-primary" @click="addDNSRecord">
            <i class="fas fa-plus"></i>
            Add Record
          </button>
        </div>
      </div>
    </div>

    <!-- Add SSL Certificate Modal -->
    <div v-if="showAddCertModal" class="modal-overlay" @click="closeAddCertModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add SSL Certificate</h2>
          <button class="close-btn" @click="closeAddCertModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="cert-form">
            <div class="form-group">
              <label>Domain *</label>
              <select v-model="certForm.domainId" required>
                <option value="">Select domain</option>
                <option 
                  v-for="domain in domains.value" 
                  :key="domain.id"
                  :value="domain.id"
                >
                  {{ domain.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Certificate Type</label>
              <select v-model="certForm.type">
                <option value="self-signed">Self-signed</option>
                <option value="letsencrypt">Let's Encrypt</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            <div class="form-group" v-if="certForm.type === 'custom'">
              <label>Certificate File</label>
              <input 
                @change="e => handleFileUpload(e, 'certFile')" 
                type="file" 
                accept=".pem,.crt,.cer"
              />
            </div>

            <div class="form-group" v-if="certForm.type === 'custom'">
              <label>Private Key File</label>
              <input 
                @change="e => handleFileUpload(e, 'keyFile')" 
                type="file" 
                accept=".key,.pem"
              />
            </div>

            <div class="form-group" v-if="certForm.type === 'letsencrypt'">
              <label>Email for Let's Encrypt</label>
              <input 
                v-model="certForm.email" 
                type="email" 
                placeholder="admin@example.com"
              />
            </div>

            <div class="form-group">
              <label>Auto-renew</label>
              <select v-model="certForm.autoRenew">
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeAddCertModal">Cancel</button>
          <button class="btn-primary" @click="addCertificate">
            <i class="fas fa-shield-alt"></i>
            Add Certificate
          </button>
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
const statusFilter = ref('')
const viewMode = ref('grid')
const dnsFilter = ref('')
const sslFilter = ref('')
const showAddDomainModal = ref(false)
const showDNSModal = ref(false)
const showSSLModal = ref(false)
const showAddRecordModal = ref(false)
const showAddCertModal = ref(false)

// Domain stats
const domainStats = reactive({
  totalDomains: 12,
  activeDomains: 10,
  totalCertificates: 15,
  validCertificates: 12,
  totalRecords: 89,
  recentRecords: 5,
  totalTraffic: '2.4TB',
  todayTraffic: '45GB'
})

// Domain form
const domainForm = reactive({
  name: '',
  description: '',
  registrar: 'GoDaddy',
  autoRenew: 'yes',
  nameservers: []
})

// DNS form
const dnsForm = reactive({
  domainId: '',
  type: 'A',
  name: '',
  value: '',
  ttl: '3600'
})

// Certificate form
const certForm = reactive({
  domainId: '',
  type: 'letsencrypt',
  certFile: '',
  keyFile: '',
  email: '',
  autoRenew: 'yes'
})

// Mock data
const domains = ref([
  {
    id: 1,
    name: 'example.com',
    description: 'Main company website',
    registrar: 'GoDaddy',
    status: 'active',
    expiresAt: '2024-12-31T23:59:59Z',
    sslStatus: 'Valid',
    dnsRecords: 8,
    verified: true
  },
  {
    id: 2,
    name: 'api.example.com',
    description: 'API subdomain',
    registrar: 'GoDaddy',
    status: 'active',
    expiresAt: '2024-12-31T23:59:59Z',
    sslStatus: 'Valid',
    dnsRecords: 5,
    verified: true
  },
  {
    id: 3,
    name: 'blog.example.com',
    description: 'Company blog',
    registrar: 'Namecheap',
    status: 'pending',
    expiresAt: '2024-06-30T23:59:59Z',
    sslStatus: 'Invalid',
    dnsRecords: 3,
    verified: false
  },
  {
    id: 4,
    name: 'old.example.com',
    description: 'Legacy domain',
    registrar: 'Google Domains',
    status: 'expired',
    expiresAt: '2023-12-31T23:59:59Z',
    sslStatus: 'Expired',
    dnsRecords: 2,
    verified: false
  }
])

const dnsRecords = ref([
  {
    id: 1,
    domain: 'example.com',
    type: 'A',
    name: '@',
    value: '192.168.1.1',
    ttl: '3600',
    status: 'active'
  },
  {
    id: 2,
    domain: 'example.com',
    type: 'A',
    name: 'www',
    value: '192.168.1.1',
    ttl: '3600',
    status: 'active'
  },
  {
    id: 3,
    domain: 'example.com',
    type: 'MX',
    name: '@',
    value: '10 mail.example.com',
    ttl: '3600',
    status: 'active'
  },
  {
    id: 4,
    domain: 'api.example.com',
    type: 'A',
    name: '@',
    value: '192.168.1.2',
    ttl: '3600',
    status: 'active'
  },
  {
    id: 5,
    domain: 'api.example.com',
    type: 'CNAME',
    name: 'api',
    value: 'api.example.com',
    ttl: '3600',
    status: 'pending'
  }
])

const certificates = ref([
  {
    id: 1,
    domain: 'example.com',
    issuer: 'Let\'s Encrypt',
    algorithm: 'RSA-2048',
    status: 'valid',
    expiresAt: '2024-03-21T23:59:59Z',
    daysUntilExpiry: 60,
    serialNumber: '12345678901234567890',
    fingerprint: 'AA:BB:CC:DD:EE:FF:GG:HH:II:JJ:KK:LL:MM:NN:OO:PP'
  },
  {
    id: 2,
    domain: 'api.example.com',
    issuer: 'Let\'s Encrypt',
    algorithm: 'RSA-2048',
    status: 'expiring',
    expiresAt: '2024-02-21T23:59:59Z',
    daysUntilExpiry: 30,
    serialNumber: '09876543210987654321',
    fingerprint: 'ZZ:YY:XX:WW:VV:UU:TT:SS:RR:QQ:PP:OO:NN:MM:LL:KK'
  },
  {
    id: 3,
    domain: 'blog.example.com',
    issuer: 'Self-signed',
    algorithm: 'RSA-2048',
    status: 'error',
    expiresAt: '2023-12-31T23:59:59Z',
    daysUntilExpiry: -20,
    serialNumber: '11112222333344445555',
    fingerprint: 'AA:11:BB:22:CC:33:DD:44:EE:55:FF:66:GG:77:HH:88'
  }
])

// Computed properties
const filteredDomains = computed(() => {
  let filtered = domains.value

  if (statusFilter.value) {
    filtered = filtered.filter(domain => domain.status === statusFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.expiresAt) - new Date(a.expiresAt))
})

const filteredDNSRecords = computed(() => {
  let filtered = dnsRecords.value

  if (dnsFilter.value) {
    filtered = filtered.filter(record => record.type === dnsFilter.value)
  }

  return filtered.sort((a, b) => a.domain.localeCompare(b.domain))
})

const filteredCertificates = computed(() => {
  let filtered = certificates.value

  if (sslFilter.value) {
    filtered = filtered.filter(cert => cert.status === sslFilter.value)
  }

  return filtered.sort((a, b) => new Date(a.expiresAt) - new Date(b.expiresAt))
})

// Methods
const loadDomainData = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/domains')
    // if (response.success) {
    //   domains.value = response.domains || []
    //   dnsRecords.value = response.dnsRecords || []
    //   certificates.value = response.certificates || []
    //   Object.assign(domainStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading domain data:', error)
    showError('Failed to load domain data')
  } finally {
    loading.value = false
  }
}

const filterDomains = () => {
  // This is reactive, no additional action needed
}

const filterDNSRecords = () => {
  // This is reactive, no additional action needed
}

const filterCertificates = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value) {
    return 'No domains match your filter criteria'
  }
  return 'No domains found'
}

const getSSLClass = (status) => {
  if (status === 'Valid') return 'valid'
  if (status === 'Invalid') return 'invalid'
  if (status === 'Expired') return 'expired'
  return 'unknown'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const verifyDomain = async (domain) => {
  try {
    // const response = await apiPost(`/domains/${domain.id}/verify`)
    // if (response.success) {
    //   domain.verified = true
    //   showSuccess('Domain verified successfully')
    // }
    
    // For demo, simulate verification
    domain.verified = true
    showSuccess('Domain verified successfully')
  } catch (error) {
    console.error('Error verifying domain:', error)
    showError('Failed to verify domain')
  }
}

const verifyAllDomains = async () => {
  try {
    // const response = await apiPost('/domains/verify-all')
    // if (response.success) {
    //   domains.value.forEach(domain => {
    //     domain.verified = true
    //   })
    //   showSuccess('All domains verified successfully')
    // }
    
    // For demo, simulate verification
    domains.value.forEach(domain => {
      domain.verified = true
    })
    showSuccess('All domains verified successfully')
  } catch (error) {
    console.error('Error verifying domains:', error)
    showError('Failed to verify domains')
  }
}

const manageDNS = (domain) => {
  // Open DNS management modal or navigate to detailed view
  showSuccess(`Opening DNS management for ${domain.name}`)
}

const manageSSL = (domain) => {
  // Open SSL management modal or navigate to detailed view
  showSuccess(`Opening SSL management for ${domain.name}`)
}

const editDNSRecord = (record) => {
  // Open DNS record edit modal
  showSuccess(`Editing DNS record for ${record.domain}`)
}

const deleteDNSRecord = async (record) => {
  const confirmed = await showConfirm(`Are you sure you want to delete this DNS record?`)
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/dns/records/${record.id}`)
    // if (response.success) {
    //   const index = dnsRecords.value.findIndex(r => r.id === record.id)
    //   if (index > -1) {
    //     dnsRecords.value.splice(index, 1)
    //     showSuccess('DNS record deleted successfully')
    //   }
    // }
    
    // For demo, simulate deletion
    const index = dnsRecords.value.findIndex(r => r.id === record.id)
    if (index > -1) {
      dnsRecords.value.splice(index, 1)
      showSuccess('DNS record deleted successfully')
    }
  } catch (error) {
    console.error('Error deleting DNS record:', error)
    showError('Failed to delete DNS record')
  }
}

const renewCertificate = async (cert) => {
  try {
    // const response = await apiPost(`/ssl/certificates/${cert.id}/renew`)
    // if (response.success) {
    //   cert.status = 'valid'
    //   cert.expiresAt = new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString()
    //   cert.daysUntilExpiry = 90
    //   showSuccess('Certificate renewed successfully')
    // }
    
    // For demo, simulate renewal
    cert.status = 'valid'
    cert.expiresAt = new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString()
    cert.daysUntilExpiry = 90
    showSuccess('Certificate renewed successfully')
  } catch (error) {
    console.error('Error renewing certificate:', error)
    showError('Failed to renew certificate')
  }
}

const downloadCertificate = async (cert) => {
  try {
    // const response = await apiGet(`/ssl/certificates/${cert.id}/download`)
    // if (response.success) {
    //   const downloadUrl = response.download_url
    //   const link = document.createElement('a')
    //   link.href = downloadUrl
    //   link.download = `${cert.domain}.crt`
    //   document.body.appendChild(link)
    //   link.click()
    //   document.body.removeChild(link)
    //   showSuccess('Certificate downloaded successfully')
    // }
    
    // For demo, simulate download
    showSuccess('Certificate downloaded successfully')
  } catch (error) {
    console.error('Error downloading certificate:', error)
    showError('Failed to download certificate')
  }
}

const revokeCertificate = async (cert) => {
  const confirmed = await showConfirm(`Are you sure you want to revoke this certificate?`)
  if (!confirmed) return

  try {
    // const response = await apiDelete(`/ssl/certificates/${cert.id}/revoke`)
    // if (response.success) {
    //   cert.status = 'revoked'
    //   showSuccess('Certificate revoked successfully')
    // }
    
    // For demo, simulate revocation
    cert.status = 'revoked'
    showSuccess('Certificate revoked successfully')
  } catch (error) {
    console.error('Error revoking certificate:', error)
    showError('Failed to revoke certificate')
  }
}

const addNameserver = () => {
  domainForm.nameservers.push({ value: '' })
}

const removeNameserver = (index) => {
  domainForm.nameservers.splice(index, 1)
}

const addDomain = async () => {
  if (!domainForm.name) {
    showError('Please enter a domain name')
    return
  }

  try {
    // const response = await apiPost('/domains', domainForm)
    // if (response.success) {
    //   domains.value.unshift(response.domain)
    //   showSuccess('Domain added successfully')
    //   closeAddDomainModal()
    // }
    
    // For demo, simulate addition
    const newDomain = {
      id: Date.now(),
      ...domainForm,
      status: 'pending',
      expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
      sslStatus: 'Invalid',
      dnsRecords: 0,
      verified: false
    }
    
    domains.value.unshift(newDomain)
    showSuccess('Domain added successfully')
    closeAddDomainModal()
  } catch (error) {
    console.error('Error adding domain:', error)
    showError('Failed to add domain')
  }
}

const addDNSRecord = async () => {
  if (!dnsForm.domainId || !dnsForm.value) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/dns/records', dnsForm)
    // if (response.success) {
    //   dnsRecords.value.unshift(response.record)
    //   showSuccess('DNS record added successfully')
    //   closeAddRecordModal()
    // }
    
    // For demo, simulate addition
    const domain = domains.value.find(d => d.id === dnsForm.domainId)
    const newRecord = {
      id: Date.now(),
      domain: domain.name,
      ...dnsForm,
      status: 'pending'
    }
    
    dnsRecords.value.unshift(newRecord)
    showSuccess('DNS record added successfully')
    closeAddRecordModal()
  } catch (error) {
    console.error('Error adding DNS record:', error)
    showError('Failed to add DNS record')
  }
}

const handleFileUpload = (event, field) => {
  const file = event.target.files[0]
  if (file) {
    certForm[field] = file
  }
}

const addCertificate = async () => {
  if (!certForm.domainId) {
    showError('Please select a domain')
    return
  }

  try {
    // const response = await apiPost('/ssl/certificates', certForm)
    // if (response.success) {
    //   certificates.value.unshift(response.certificate)
    //   showSuccess('Certificate added successfully')
    //   closeAddCertModal()
    // }
    
    // For demo, simulate addition
    const domain = domains.value.find(d => d.id === certForm.domainId)
    const newCert = {
      id: Date.now(),
      domain: domain.name,
      issuer: certForm.type === 'letsencrypt' ? 'Let\'s Encrypt' : 'Self-signed',
      algorithm: 'RSA-2048',
      status: 'valid',
      expiresAt: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      daysUntilExpiry: 90,
      serialNumber: '12345678901234567890',
      fingerprint: 'AA:BB:CC:DD:EE:FF:GG:HH:II:JJ:KK:LL:MM:NN:OO:PP'
    }
    
    certificates.value.unshift(newCert)
    showSuccess('Certificate added successfully')
    closeAddCertModal()
  } catch (error) {
    console.error('Error adding certificate:', error)
    showError('Failed to add certificate')
  }
}

const closeAddDomainModal = () => {
  showAddDomainModal.value = false
  resetDomainForm()
}

const closeAddRecordModal = () => {
  showAddRecordModal.value = false
  resetDNSForm()
}

const closeAddCertModal = () => {
  showAddCertModal.value = false
  resetCertForm()
}

const resetDomainForm = () => {
  Object.assign(domainForm, {
    name: '',
    description: '',
    registrar: 'GoDaddy',
    autoRenew: 'yes',
    nameservers: []
  })
}

const resetDNSForm = () => {
  Object.assign(dnsForm, {
    domainId: '',
    type: 'A',
    name: '',
    value: '',
    ttl: '3600'
  })
}

const resetCertForm = () => {
  Object.assign(certForm, {
    domainId: '',
    type: 'letsencrypt',
    certFile: '',
    keyFile: '',
    email: '',
    autoRenew: 'yes'
  })
}

// Lifecycle
onMounted(() => {
  loadDomainData()
})
</script>

<style scoped>
.domains {
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

.overview-section {
  margin-bottom: 3rem;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.overview-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  text-align: center;
}

.card-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.card-icon.certificates {
  background: var(--success-color);
}

.card-icon.dns {
  background: var(--warning-color);
}

.card-icon.traffic {
  background: var(--info-color);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.card-content p {
  color: var(--text-secondary);
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.domain-count,
.cert-count,
.record-count,
.traffic-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.domain-count {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.cert-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.record-count {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.traffic-status {
  color: var(--text-secondary);
}

.actions-section {
  margin-bottom: 3rem;
}

.action-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.add-domain-btn,
.dns-btn,
.ssl-btn,
.verify-btn {
  padding: 1rem 2rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.add-domain-btn:hover,
.dns-btn:hover,
.ssl-btn:hover,
.verify-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.dns-btn {
  background: var(--warning-color);
}

.dns-btn:hover {
  background: var(--warning-hover);
}

.ssl-btn {
  background: var(--success-color);
}

.ssl-btn:hover {
  background: var(--success-hover);
}

.verify-btn {
  background: var(--info-color);
}

.verify-btn:hover {
  background: var(--info-hover);
}

.domains-section,
.dns-section,
.ssl-section {
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

.filter-dropdown select {
  padding: 0.75rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.add-record-btn,
.add-cert-btn {
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

.add-record-btn:hover,
.add-cert-btn:hover {
  background: var(--primary-hover);
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

.domains-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.domain-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.domain-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.domain-card.pending {
  opacity: 0.7;
  border-color: var(--warning-color);
}

.domain-card.expired {
  opacity: 0.7;
  border-color: var(--danger-color);
}

.domain-card.error {
  border-color: var(--danger-color);
}

.domain-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.domain-icon {
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

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.expired {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.domain-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.domain-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.domain-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.registrar,
.expires,
.ssl {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.domain-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-item span {
  color: var(--text-primary);
  font-weight: 600;
}

.valid {
  color: #10b981;
}

.invalid {
  color: #ef4444;
}

.expired {
  color: #ef4444;
}

.domain-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.5rem 1rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.action-btn.verify:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.dns:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.ssl:hover {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.domains-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.domain-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.domain-list-card:hover {
  background: var(--glass-bg-hover);
}

.domain-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.domain-list-info {
  flex: 1;
}

.domain-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.domain-list-actions {
  display: flex;
  gap: 0.5rem;
}

.dns-table-container {
  overflow-x: auto;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
}

.dns-table {
  width: 100%;
  border-collapse: collapse;
}

.dns-table th {
  background: var(--glass-bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.dns-table td {
  padding: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--glass-border);
}

.dns-row {
  transition: background 0.3s ease;
}

.dns-row:hover {
  background: var(--glass-bg-hover);
}

.dns-row.pending {
  border-left: 4px solid var(--warning-color);
}

.dns-row.error {
  border-left: 4px solid var(--danger-color);
}

.record-type {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.record-value {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.certificates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.cert-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.cert-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.cert-card.expiring {
  border-color: var(--warning-color);
}

.cert-card.expired {
  border-color: var(--danger-color);
}

.cert-card.error {
  border-color: var(--danger-color);
}

.cert-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.cert-icon {
  width: 50px;
  height: 50px;
  background: var(--success-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.cert-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.cert-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.cert-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.algorithm,
.expires,
.days {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.cert-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.detail-item span {
  color: var(--text-primary);
  font-weight: 600;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  word-break: break-all;
}

.cert-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn.renew:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.download:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.action-btn.revoke:hover {
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

.domain-form,
.dns-form,
.cert-form {
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
  min-height: 80px;
}

.nameservers-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.nameserver-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nameserver-item input {
  flex: 1;
  padding: 0.5rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
}

.remove-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--danger-color);
  border-radius: 6px;
  background: var(--danger-color);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: var(--danger-hover);
}

.add-nameserver-btn {
  padding: 0.75rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  align-self: flex-start;
}

.add-nameserver-btn:hover {
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
  .domains {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .domains-grid {
    grid-template-columns: 1fr;
  }
  
  .domain-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .domain-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .certificates-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .cert-details {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
