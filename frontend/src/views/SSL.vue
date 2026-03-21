<template>
  <div class="ssl">
    <div class="page-header">
      <h1>SSL Certificate Management</h1>
      <p>Manage SSL certificates, security configurations, and compliance</p>
    </div>

    <!-- SSL Overview -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fas fa-shield-alt"></i>
          </div>
          <div class="card-content">
            <h3>{{ sslStats.totalCertificates }}</h3>
            <p>Total Certificates</p>
            <span class="cert-count">{{ sslStats.validCertificates }} valid</span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon expiring">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="card-content">
            <h3>{{ sslStats.expiringSoon }}</h3>
            <p>Expiring Soon</p>
            <span class="expiring-status" :class="getExpiringClass(sslStats.expiringSoon)">
              {{ getExpiringStatus(sslStats.expiringSoon) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon expired">
            <i class="fas fa-times-circle"></i>
          </div>
          <div class="card-content">
            <h3>{{ sslStats.expiredCertificates }}</h3>
            <p>Expired</p>
            <span class="expired-status" :class="getExpiredClass(sslStats.expiredCertificates)">
              {{ getExpiredStatus(sslStats.expiredCertificates) }}
            </span>
          </div>
        </div>
        <div class="overview-card">
          <div class="card-icon security">
            <i class="fas fa-lock"></i>
          </div>
          <div class="card-content">
            <h3>{{ sslStats.securityScore }}%</h3>
            <p>Security Score</p>
            <span class="security-status" :class="getSecurityClass(sslStats.securityScore)">
              {{ getSecurityStatus(sslStats.securityScore) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <div class="action-controls">
        <button class="generate-btn" @click="showGenerateModal = true">
          <i class="fas fa-plus"></i>
          Generate Certificate
        </button>
        <button class="import-btn" @click="showImportModal = true">
          <i class="fas fa-upload"></i>
          Import Certificate
        </button>
        <button class="scan-btn" @click="scanAllCertificates">
          <i class="fas fa-search"></i>
          Scan All
        </button>
        <button class="settings-btn" @click="showSettingsModal = true">
          <i class="fas fa-cog"></i>
          Settings
        </button>
      </div>
    </div>

    <!-- Certificate List -->
    <div class="certificates-section">
      <div class="section-header">
        <h2>SSL Certificates</h2>
        <div class="header-actions">
          <div class="filter-dropdown">
            <select v-model="statusFilter" @change="filterCertificates">
              <option value="">All Status</option>
              <option value="valid">Valid</option>
              <option value="expiring">Expiring Soon</option>
              <option value="expired">Expired</option>
              <option value="revoked">Revoked</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div class="filter-dropdown">
            <select v-model="typeFilter" @change="filterCertificates">
              <option value="">All Types</option>
              <option value="letsencrypt">Let's Encrypt</option>
              <option value="self-signed">Self-signed</option>
              <option value="commercial">Commercial</option>
              <option value="wildcard">Wildcard</option>
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
        <p>Loading certificates...</p>
      </div>

      <div v-else-if="filteredCertificates.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-shield-alt"></i>
        </div>
        <h3>No certificates found</h3>
        <p>{{ getEmptyMessage() }}</p>
        <button class="generate-first-btn" @click="showGenerateModal = true">
          <i class="fas fa-plus"></i>
          Generate Your First Certificate
        </button>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="certificates-grid">
          <div 
            v-for="cert in filteredCertificates" 
            :key="cert.id"
            class="cert-card"
            :class="{ 'expiring': cert.status === 'expiring', 'expired': cert.status === 'expired', 'revoked': cert.status === 'revoked', 'error': cert.status === 'error' }"
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
                <span class="type">{{ cert.type }}</span>
                <span class="algorithm">{{ cert.algorithm }}</span>
                <span class="expires">{{ formatDate(cert.expiresAt) }}</span>
              </div>

              <div class="cert-details">
                <div class="detail-item">
                  <label>Days Until Expiry:</label>
                  <span :class="getDaysClass(cert.daysUntilExpiry)">{{ cert.daysUntilExpiry }} days</span>
                </div>
                <div class="detail-item">
                  <label>Serial Number:</label>
                  <span class="serial">{{ cert.serialNumber }}</span>
                </div>
                <div class="detail-item">
                  <label>Fingerprint:</label>
                  <span class="fingerprint">{{ cert.fingerprint }}</span>
                </div>
              </div>

              <div class="cert-actions">
                <button class="action-btn renew" @click="renewCertificate(cert)" v-if="cert.status === 'expiring'">
                  <i class="fas fa-sync"></i>
                  Renew
                </button>
                <button class="action-btn download" @click="downloadCertificate(cert)">
                  <i class="fas fa-download"></i>
                  Download
                </button>
                <button class="action-btn view" @click="viewCertificate(cert)">
                  <i class="fas fa-eye"></i>
                  View
                </button>
                <button class="action-btn revoke" @click="revokeCertificate(cert)">
                  <i class="fas fa-ban"></i>
                  Revoke
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="certificates-list">
          <div 
            v-for="cert in filteredCertificates" 
            :key="cert.id"
            class="cert-list-card"
            :class="{ 'expiring': cert.status === 'expiring', 'expired': cert.status === 'expired', 'revoked': cert.status === 'revoked', 'error': cert.status === 'error' }"
          >
            <div class="cert-list-header">
              <div class="cert-list-info">
                <div class="cert-icon">
                  <i class="fas fa-shield-alt"></i>
                </div>
                <div class="cert-details">
                  <h3>{{ cert.domain }}</h3>
                  <p>{{ cert.issuer }}</p>
                  <div class="cert-info">
                    <span class="type">{{ cert.type }}</span>
                    <span class="algorithm">{{ cert.algorithm }}</span>
                    <span :class="['status-badge', cert.status]">{{ cert.status }}</span>
                    <span class="expires">{{ formatDate(cert.expiresAt) }}</span>
                  </div>
                </div>
              </div>
              <div class="cert-list-stats">
                <div class="detail-item">
                  <label>Days Until Expiry:</label>
                  <span :class="getDaysClass(cert.daysUntilExpiry)">{{ cert.daysUntilExpiry }} days</span>
                </div>
                <div class="detail-item">
                  <label>Serial Number:</label>
                  <span class="serial">{{ cert.serialNumber }}</span>
                </div>
                <div class="detail-item">
                  <label>Fingerprint:</label>
                  <span class="fingerprint">{{ cert.fingerprint }}</span>
                </div>
              </div>
              <div class="cert-list-actions">
                <button class="action-btn renew" @click="renewCertificate(cert)" v-if="cert.status === 'expiring'">
                  <i class="fas fa-sync"></i>
                </button>
                <button class="action-btn download" @click="downloadCertificate(cert)">
                  <i class="fas fa-download"></i>
                </button>
                <button class="action-btn view" @click="viewCertificate(cert)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn revoke" @click="revokeCertificate(cert)">
                  <i class="fas fa-ban"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Security Configuration -->
    <div class="security-section">
      <div class="section-header">
        <h2>Security Configuration</h2>
        <div class="header-actions">
          <button class="test-btn" @click="runSecurityTest">
            <i class="fas fa-vial"></i>
            Run Security Test
          </button>
        </div>
      </div>

      <div class="security-grid">
        <div class="security-card">
          <div class="security-header">
            <h3>SSL/TLS Configuration</h3>
            <span class="security-score" :class="getSecurityClass(sslConfig.tlsScore)">
              {{ sslConfig.tlsScore }}%
            </span>
          </div>
          <div class="security-content">
            <div class="security-item">
              <label>Protocol Version:</label>
              <span>{{ sslConfig.protocolVersion }}</span>
            </div>
            <div class="security-item">
              <label>Cipher Suite:</label>
              <span>{{ sslConfig.cipherSuite }}</span>
            </div>
            <div class="security-item">
              <label>HSTS Enabled:</label>
              <span :class="sslConfig.hstsEnabled ? 'enabled' : 'disabled'">
                {{ sslConfig.hstsEnabled ? 'Yes' : 'No' }}
              </span>
            </div>
            <div class="security-item">
              <label>OCSP Stapling:</label>
              <span :class="sslConfig.ocspStapling ? 'enabled' : 'disabled'">
                {{ sslConfig.ocspStapling ? 'Yes' : 'No' }}
              </span>
            </div>
          </div>
        </div>

        <div class="security-card">
          <div class="security-header">
            <h3>Certificate Chain</h3>
            <span class="security-score" :class="getSecurityClass(sslConfig.chainScore)">
              {{ sslConfig.chainScore }}%
            </span>
          </div>
          <div class="security-content">
            <div class="security-item">
              <label>Root Certificate:</label>
              <span>{{ sslConfig.rootCertificate }}</span>
            </div>
            <div class="security-item">
              <label>Intermediate Certificates:</label>
              <span>{{ sslConfig.intermediateCertificates }}</span>
            </div>
            <div class="security-item">
              <label>Chain Validation:</label>
              <span :class="sslConfig.chainValid ? 'valid' : 'invalid'">
                {{ sslConfig.chainValid ? 'Valid' : 'Invalid' }}
              </span>
            </div>
          </div>
        </div>

        <div class="security-card">
          <div class="security-header">
            <h3>Key Management</h3>
            <span class="security-score" :class="getSecurityClass(sslConfig.keyScore)">
              {{ sslConfig.keyScore }}%
            </span>
          </div>
          <div class="security-content">
            <div class="security-item">
              <label>Key Algorithm:</label>
              <span>{{ sslConfig.keyAlgorithm }}</span>
            </div>
            <div class="security-item">
              <label>Key Size:</label>
              <span>{{ sslConfig.keySize }}</span>
            </div>
            <div class="security-item">
              <label>Key Usage:</label>
              <span>{{ sslConfig.keyUsage }}</span>
            </div>
            <div class="security-item">
              <label>Extended Key Usage:</label>
              <span>{{ sslConfig.extendedKeyUsage }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Certificate Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Certificate Details</h2>
          <button class="close-btn" @click="closeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="cert-details">
            <div class="detail-section">
              <h3>Basic Information</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Domain:</label>
                  <span>{{ selectedCert?.domain }}</span>
                </div>
                <div class="detail-item">
                  <label>Issuer:</label>
                  <span>{{ selectedCert?.issuer }}</span>
                </div>
                <div class="detail-item">
                  <label>Serial Number:</label>
                  <span>{{ selectedCert?.serialNumber }}</span>
                </div>
                <div class="detail-item">
                  <label>Fingerprint:</label>
                  <span>{{ selectedCert?.fingerprint }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Validity Period</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Issued At:</label>
                  <span>{{ formatDateTime(selectedCert?.issuedAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Expires At:</label>
                  <span>{{ formatDateTime(selectedCert?.expiresAt) }}</span>
                </div>
                <div class="detail-item">
                  <label>Days Until Expiry:</label>
                  <span :class="getDaysClass(selectedCert?.daysUntilExpiry)">
                    {{ selectedCert?.daysUntilExpiry }} days
                  </span>
                </div>
                <div class="detail-item">
                  <label>Validity Period:</label>
                  <span>{{ selectedCert?.validityPeriod }} days</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Technical Details</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Algorithm:</label>
                  <span>{{ selectedCert?.algorithm }}</span>
                </div>
                <div class="detail-item">
                  <label>Key Size:</label>
                  <span>{{ selectedCert?.keySize }}</span>
                </div>
                <div class="detail-item">
                  <label>Signature Algorithm:</label>
                  <span>{{ selectedCert?.signatureAlgorithm }}</span>
                </div>
                <div class="detail-item">
                  <label>Public Key:</label>
                  <span class="public-key">{{ selectedCert?.publicKey }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Certificate Chain</h3>
              <div class="chain-list">
                <div 
                  v-for="(cert, index) in selectedCert?.chain" 
                  :key="index"
                  class="chain-item"
                >
                  <div class="chain-info">
                    <h4>{{ cert.subject }}</h4>
                    <p>{{ cert.issuer }}</p>
                    <span class="chain-fingerprint">{{ cert.fingerprint }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeDetailsModal">Close</button>
          <button class="btn-primary" @click="downloadCertificate(selectedCert)">
            <i class="fas fa-download"></i>
            Download Certificate
          </button>
        </div>
      </div>
    </div>

    <!-- Generate Certificate Modal -->
    <div v-if="showGenerateModal" class="modal-overlay" @click="closeGenerateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Generate SSL Certificate</h2>
          <button class="close-btn" @click="closeGenerateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="generate-form">
            <div class="form-group">
              <label>Domain *</label>
              <input 
                v-model="generateForm.domain" 
                type="text" 
                placeholder="example.com"
                required
              />
            </div>

            <div class="form-group">
              <label>Certificate Type</label>
              <select v-model="generateForm.type">
                <option value="letsencrypt">Let's Encrypt</option>
                <option value="self-signed">Self-signed</option>
                <option value="commercial">Commercial</option>
              </select>
            </div>

            <div class="form-group" v-if="generateForm.type === 'letsencrypt'">
              <label>Email for Let's Encrypt *</label>
              <input 
                v-model="generateForm.email" 
                type="email" 
                placeholder="admin@example.com"
                required
              />
            </div>

            <div class="form-group">
              <label>Key Size</label>
              <select v-model="generateForm.keySize">
                <option value="2048">2048 bits</option>
                <option value="4096">4096 bits</option>
                <option value="8192">8192 bits</option>
              </select>
            </div>

            <div class="form-group">
              <label>Domains</label>
              <div class="domains-container">
                <div 
                  v-for="(domain, index) in generateForm.domains" 
                  :key="index"
                  class="domain-item"
                >
                  <input 
                    v-model="domain.value" 
                    type="text" 
                    placeholder="example.com"
                  />
                  <button 
                    class="remove-btn"
                    @click="removeDomain(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <button class="add-domain-btn" @click="addDomain">
                  <i class="fas fa-plus"></i>
                  Add Domain
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>Options</label>
              <div class="options-container">
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="generateForm.wildcard"
                  />
                  <span>Wildcard Certificate</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="generateForm.autoRenew"
                  />
                  <span>Auto-renew</span>
                </label>
                <label class="checkbox-item">
                  <input 
                    type="checkbox" 
                    v-model="generateForm.forceRenew"
                  />
                  <span>Force Renew</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeGenerateModal">Cancel</button>
          <button class="btn-primary" @click="generateCertificate">
            <i class="fas fa-shield-alt"></i>
            Generate Certificate
          </button>
        </div>
      </div>
    </div>

    <!-- Import Certificate Modal -->
    <div v-if="showImportModal" class="modal-overlay" @click="closeImportModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Import SSL Certificate</h2>
          <button class="close-btn" @click="closeImportModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="import-form">
            <div class="form-group">
              <label>Domain *</label>
              <input 
                v-model="importForm.domain" 
                type="text" 
                placeholder="example.com"
                required
              />
            </div>

            <div class="form-group">
              <label>Certificate File *</label>
              <input 
                @change="e => handleFileUpload(e, 'certFile')" 
                type="file" 
                accept=".pem,.crt,.cer"
                required
              />
            </div>

            <div class="form-group">
              <label>Private Key File *</label>
              <input 
                @change="e => handleFileUpload(e, 'keyFile')" 
                type="file" 
                accept=".key,.pem"
                required
              />
            </div>

            <div class="form-group">
              <label>CA Bundle File (Optional)</label>
              <input 
                @change="e => handleFileUpload(e, 'caBundleFile')" 
                type="file" 
                accept=".pem,.crt,.cer"
              />
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="importForm.description" 
                placeholder="Describe this certificate"
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeImportModal">Cancel</button>
          <button class="btn-primary" @click="importCertificate">
            <i class="fas fa-upload"></i>
            Import Certificate
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
const typeFilter = ref('')
const viewMode = ref('grid')
const showDetailsModal = ref(false)
const showGenerateModal = ref(false)
const showImportModal = ref(false)
const showSettingsModal = ref(false)
const selectedCert = ref(null)

// SSL stats
const sslStats = reactive({
  totalCertificates: 15,
  validCertificates: 12,
  expiringSoon: 2,
  expiredCertificates: 1,
  securityScore: 92
})

// SSL configuration
const sslConfig = reactive({
  tlsScore: 95,
  protocolVersion: 'TLS 1.3',
  cipherSuite: 'ECDHE-RSA-AES256-GCM-SHA384',
  hstsEnabled: true,
  ocspStapling: true,
  chainScore: 88,
  rootCertificate: 'DigiCert Global Root G2',
  intermediateCertificates: 2,
  chainValid: true,
  keyScore: 90,
  keyAlgorithm: 'RSA',
  keySize: '2048',
  keyUsage: 'Digital Signature, Key Encipherment',
  extendedKeyUsage: 'Server Authentication, Client Authentication'
})

// Generate form
const generateForm = reactive({
  domain: '',
  type: 'letsencrypt',
  email: '',
  keySize: '2048',
  domains: [],
  wildcard: false,
  autoRenew: true,
  forceRenew: false
})

// Import form
const importForm = reactive({
  domain: '',
  certFile: '',
  keyFile: '',
  caBundleFile: '',
  description: ''
})

// Mock data
const certificates = ref([
  {
    id: 1,
    domain: 'example.com',
    issuer: 'Let\'s Encrypt',
    algorithm: 'RSA-2048',
    status: 'valid',
    expiresAt: '2024-03-21T23:59:59Z',
    issuedAt: '2023-03-21T23:59:59Z',
    daysUntilExpiry: 60,
    serialNumber: '12345678901234567890',
    fingerprint: 'AA:BB:CC:DD:EE:FF:GG:HH:II:JJ:KK:LL:MM:NN:OO:PP',
    type: 'letsencrypt',
    keySize: '2048',
    signatureAlgorithm: 'SHA256',
    publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----',
    chain: [
      {
        subject: 'example.com',
        issuer: 'Let\'s Encrypt Authority X3',
        fingerprint: 'AA:BB:CC:DD:EE:FF:GG:HH:II:JJ:KK:LL:MM:NN:OO:PP'
      }
    ],
    validityPeriod: 365
  },
  {
    id: 2,
    domain: 'api.example.com',
    issuer: 'Let\'s Encrypt',
    algorithm: 'RSA-2048',
    status: 'expiring',
    expiresAt: '2024-02-21T23:59:59Z',
    issuedAt: '2023-02-21T23:59:59Z',
    daysUntilExpiry: 30,
    serialNumber: '09876543210987654321',
    fingerprint: 'ZZ:YY:XX:WW:VV:UU:TT:SS:RR:QQ:PP:OO:NN:MM:LL:KK',
    type: 'letsencrypt',
    keySize: '2048',
    signatureAlgorithm: 'SHA256',
    publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----',
    chain: [
      {
        subject: 'api.example.com',
        issuer: 'Let\'s Encrypt Authority X3',
        fingerprint: 'ZZ:YY:XX:WW:VV:UU:TT:SS:RR:QQ:PP:OO:NN:MM:LL:KK'
      }
    ],
    validityPeriod: 365
  },
  {
    id: 3,
    domain: 'old.example.com',
    issuer: 'Self-signed',
    algorithm: 'RSA-2048',
    status: 'expired',
    expiresAt: '2023-12-31T23:59:59Z',
    issuedAt: '2022-12-31T23:59:59Z',
    daysUntilExpiry: -20,
    serialNumber: '11112222333344445555',
    fingerprint: 'AA:11:BB:22:CC:33:DD:44:EE:55:FF:66:GG:77:HH:88:II:99',
    type: 'self-signed',
    keySize: '2048',
    signatureAlgorithm: 'SHA256',
    publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----',
    chain: [
      {
        subject: 'old.example.com',
        issuer: 'Self-signed',
        fingerprint: 'AA:11:BB:22:CC:33:DD:44:EE:55:FF:66:GG:77:HH:88:II:99'
      }
    ],
    validityPeriod: 365
  }
])

// Computed properties
const filteredCertificates = computed(() => {
  let filtered = certificates.value

  if (statusFilter.value) {
    filtered = filtered.filter(cert => cert.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(cert => cert.type === typeFilter.value)
  }

  return filtered.sort((a, b) => new Date(a.expiresAt) - new Date(b.expiresAt))
})

// Methods
const loadCertificates = async () => {
  loading.value = true
  try {
    // In real app, this would be API calls
    // const response = await apiGet('/ssl/certificates')
    // if (response.success) {
    //   certificates.value = response.certificates || []
    //   Object.assign(sslStats, response.stats)
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading certificates:', error)
    showError('Failed to load certificates')
  } finally {
    loading.value = false
  }
}

const filterCertificates = () => {
  // This is reactive, no additional action needed
}

const getEmptyMessage = () => {
  if (statusFilter.value || typeFilter.value) {
    return 'No certificates match your filter criteria'
  }
  return 'No certificates found'
}

const getExpiringClass = (count) => {
  if (count === 0) return 'none'
  if (count <= 2) return 'low'
  if (count <= 5) return 'medium'
  return 'high'
}

const getExpiringStatus = (count) => {
  if (count === 0) return 'None'
  if (count <= 2) return 'Low'
  if (count <= 5) return 'Medium'
  return 'High'
}

const getExpiredClass = (count) => {
  if (count === 0) return 'none'
  if (count <= 1) return 'low'
  if (count <= 3) return 'medium'
  return 'high'
}

const getExpiredStatus = (count) => {
  if (count === 0) return 'None'
  if (count <= 1) return 'Low'
  if (count <= 3) return 'Medium'
  return 'High'
}

const getSecurityClass = (score) => {
  if (score >= 95) return 'excellent'
  if (score >= 90) return 'good'
  if (score >= 80) return 'fair'
  return 'poor'
}

const getSecurityStatus = (score) => {
  if (score >= 95) return 'Excellent'
  if (score >= 90) return 'Good'
  if (score >= 80) return 'Fair'
  return 'Needs Improvement'
}

const getDaysClass = (days) => {
  if (days > 30) return 'safe'
  if (days > 7) return 'warning'
  if (days > 0) return 'critical'
  return 'expired'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

const viewCertificate = (cert) => {
  selectedCert.value = cert
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedCert.value = null
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

const runSecurityTest = async () => {
  try {
    // const response = await apiPost('/ssl/security-test')
    // if (response.success) {
    //   Object.assign(sslConfig, response.config)
    //   showSuccess('Security test completed')
    // }
    
    // For demo, simulate test
    showSuccess('Security test completed')
  } catch (error) {
    console.error('Error running security test:', error)
    showError('Failed to run security test')
  }
}

const addDomain = () => {
  generateForm.domains.push({ value: '' })
}

const removeDomain = (index) => {
  generateForm.domains.splice(index, 1)
}

const generateCertificate = async () => {
  if (!generateForm.domain) {
    showError('Please enter a domain name')
    return
  }

  if (generateForm.type === 'letsencrypt' && !generateForm.email) {
    showError('Please enter an email address')
    return
  }

  try {
    // const response = await apiPost('/ssl/certificates/generate', generateForm)
    // if (response.success) {
    //   certificates.value.unshift(response.certificate)
    //   showSuccess('Certificate generated successfully')
    //   closeGenerateModal()
    //   resetGenerateForm()
    // }
    
    // For demo, simulate generation
    const newCert = {
      id: Date.now(),
      domain: generateForm.domain,
      issuer: generateForm.type === 'letsencrypt' ? 'Let\'s Encrypt' : 'Self-signed',
      algorithm: `RSA-${generateForm.keySize}`,
      status: 'valid',
      expiresAt: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      issuedAt: new Date().toISOString(),
      daysUntilExpiry: 90,
      serialNumber: Math.random().toString(36).substring(2, 20),
      fingerprint: Array.from({ length: 20 }, () => Math.random().toString(36).substring(2, 2)).join(':'),
      type: generateForm.type,
      keySize: generateForm.keySize,
      signatureAlgorithm: 'SHA256',
      publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----',
      chain: [],
      validityPeriod: 365
    }
    
    certificates.value.unshift(newCert)
    showSuccess('Certificate generated successfully')
    closeGenerateModal()
    resetGenerateForm()
  } catch (error) {
    console.error('Error generating certificate:', error)
    showError('Failed to generate certificate')
  }
}

const handleFileUpload = (event, field) => {
  const file = event.target.files[0]
  if (file) {
    importForm[field] = file
  }
}

const importCertificate = async () => {
  if (!importForm.domain || !importForm.certFile || !importForm.keyFile) {
    showError('Please fill in all required fields')
    return
  }

  try {
    // const response = await apiPost('/ssl/certificates/import', importForm)
    // if (response.success) {
    //   certificates.value.unshift(response.certificate)
    //   showSuccess('Certificate imported successfully')
    //   closeImportModal()
    //   resetImportForm()
    // }
    
    // For demo, simulate import
    const newCert = {
      id: Date.now(),
      domain: importForm.domain,
      issuer: 'Custom',
      algorithm: 'RSA-2048',
      status: 'valid',
      expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
      issuedAt: new Date().toISOString(),
      daysUntilExpiry: 365,
      serialNumber: Math.random().toString(36).substring(2, 20),
      fingerprint: Array.from({ length: 20 }, () => Math.random().toString(36).substring(2, 2)).join(':'),
      type: 'custom',
      keySize: '2048',
      signatureAlgorithm: 'SHA256',
      publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----',
      chain: [],
      validityPeriod: 365
    }
    
    certificates.value.unshift(newCert)
    showSuccess('Certificate imported successfully')
    closeImportModal()
    resetImportForm()
  } catch (error) {
    console.error('Error importing certificate:', error)
    showError('Failed to import certificate')
  }
}

const scanAllCertificates = async () => {
  try {
    // const response = await apiPost('/ssl/scan')
    // if (response.success) {
    //   certificates.value = response.certificates || []
    //   Object.assign(sslStats, response.stats)
    //   showSuccess('Certificate scan completed')
    // }
    
    // For demo, simulate scan
    certificates.value.forEach(cert => {
      cert.status = 'valid'
      cert.daysUntilExpiry = Math.floor(Math.random() * 365)
      cert.expiresAt = new Date(Date.now() + cert.daysUntilExpiry * 24 * 60 * 60 * 1000).toISOString()
    })
    
    sslStats.validCertificates = certificates.value.filter(c => c.status === 'valid').length
    sslStats.expiringSoon = certificates.value.filter(c => c.status === 'expiring').length
    sslStats.expiredCertificates = certificates.value.filter(c => c.status === 'expired').length
    
    showSuccess('Certificate scan completed')
  } catch (error) {
    console.error('Error scanning certificates:', error)
    showError('Failed to scan certificates')
  }
}

const closeGenerateModal = () => {
  showGenerateModal.value = false
  resetGenerateForm()
}

const closeImportModal = () => {
  showImportModal.value = false
  resetImportForm()
}

const resetGenerateForm = () => {
  Object.assign(generateForm, {
    domain: '',
    type: 'letsencrypt',
    email: '',
    keySize: '2048',
    domains: [],
    wildcard: false,
    autoRenew: true,
    forceRenew: false
  })
}

const resetImportForm = () => {
  Object.assign(importForm, {
    domain: '',
    certFile: '',
    keyFile: '',
    caBundleFile: '',
    description: ''
  })
}

// Lifecycle
onMounted(() => {
  loadCertificates()
})
</script>

<style scoped>
.ssl {
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

.card-icon.expiring {
  background: var(--warning-color);
}

.card-icon.expired {
  background: var(--danger-color);
}

.card-icon.security {
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

.cert-count,
.expiring-status,
.expired-status,
.security-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.cert-count {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.expiring-status.none {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.expiring-status.low {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.expiring-status.medium {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.expiring-status.high {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.expired-status.none {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.expired-status.low {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.expired-status.medium {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.expired-status.high {
  background: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.security-status.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.security-status.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.security-status.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.security-status.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
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

.generate-btn,
.import-btn,
.scan-btn,
.settings-btn {
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

.generate-btn:hover,
.import-btn:hover,
.scan-btn:hover,
.settings-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.import-btn {
  background: var(--success-color);
}

.import-btn:hover {
  background: var(--success-hover);
}

.scan-btn {
  background: var(--warning-color);
}

.scan-btn:hover {
  background: var(--warning-hover);
}

.settings-btn {
  background: var(--info-color);
}

.settings-btn:hover {
  background: var(--info-hover);
}

.certificates-section,
.security-section {
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

.test-btn {
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

.test-btn:hover {
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

.generate-first-btn {
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
  margin-top: 2rem;
}

.generate-first-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.certificates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
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
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.cert-card.expiring {
  border-color: var(--warning-color);
}

.cert-card.expired {
  border-color: var(--danger-color);
  opacity: 0.7;
}

.cert-card.revoked {
  border-color: var(--danger-color);
  opacity: 0.7;
}

.cert-card.error {
  border-color: var(--danger-color);
}

.cert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.valid {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.expiring {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.expired {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.revoked {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.cert-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.cert-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.cert-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.type,
.algorithm,
.expires {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.cert-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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
}

.days.safe {
  color: #10b981;
}

.days.warning {
  color: #f59e0b;
}

.days.critical {
  color: #ef4444;
}

.days.expired {
  color: #ef4444;
}

.serial {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  word-break: break-all;
}

.fingerprint {
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  word-break: break-all;
}

.cert-actions {
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

.action-btn.view:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.revoke:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
}

.certificates-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cert-list-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.cert-list-card:hover {
  background: var(--glass-bg-hover);
}

.cert-list-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.cert-list-info {
  flex: 1;
}

.cert-list-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.cert-list-actions {
  display: flex;
  gap: 0.5rem;
}

.security-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.security-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
}

.security-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.security-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.security-score {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.security-score.excellent {
  color: #10b981;
}

.security-score.good {
  color: #3b82f6;
}

.security-score.fair {
  color: #f59e0b;
}

.security-score.poor {
  color: #ef4444;
}

.security-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.security-item label {
  font-weight: 600;
  color: var(--text-primary);
}

.security-item span {
  color: var(--text-primary);
  font-weight: 500;
}

.enabled {
  color: #10b981;
}

.disabled {
  color: #ef4444;
}

.valid {
  color: #10b981;
}

.invalid {
  color: #ef4444;
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

.modal-content.large {
  max-width: 1000px;
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

.cert-details {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.detail-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.detail-item span {
  color: var(--text-primary);
  font-weight: 500;
}

.public-key {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  word-break: break-all;
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  padding: 0.5rem;
  max-height: 100px;
  overflow-y: auto;
}

.chain-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chain-item {
  background: var(--glass-bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1rem;
}

.chain-info h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.chain-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
}

.chain-fingerprint {
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  color: var(--text-secondary);
  word-break: break-all;
}

.generate-form,
.import-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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

.domains-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.domain-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.domain-item input {
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
  font-size: 0.9rem;
}

.remove-btn:hover {
  background: var(--danger-hover);
}

.add-domain-btn {
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

.add-domain-btn:hover {
  background: var(--primary-hover);
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
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
  .ssl {
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
  
  .certificates-grid {
    grid-template-columns: 1fr;
  }
  
  .cert-list-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .cert-list-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .security-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}
</style>
