<template>
  <div class="privacy-policy">
    <div class="page-header">
      <h1>Privacy Policy</h1>
      <p>Last updated: {{ formatDate(lastUpdated) }}</p>
    </div>

    <div class="policy-container">
      <!-- Table of Contents -->
      <div class="table-of-contents">
        <h2>Table of Contents</h2>
        <nav class="toc-nav">
          <a 
            v-for="section in sections" 
            :key="section.id"
            :href="`#${section.id}`"
            class="toc-link"
            :class="{ 'active': activeSection === section.id }"
            @click="setActiveSection(section.id)"
          >
            {{ section.title }}
          </a>
        </nav>
      </div>

      <!-- Policy Content -->
      <div class="policy-content">
        <!-- Introduction -->
        <section id="introduction" class="policy-section">
          <h2>1. Introduction</h2>
          <div class="section-content">
            <p>
              Welcome to our Privacy Policy. This document explains how we collect, use, store, and protect your personal information when you use our services. We are committed to protecting your privacy and ensuring transparency in our data practices.
            </p>
            <p>
              This Privacy Policy applies to all users of our website, applications, and services (collectively, the "Service"). By using our Service, you agree to the collection and use of information in accordance with this policy.
            </p>
            <div class="info-box">
              <h3>Key Points</h3>
              <ul>
                <li>We collect only necessary information to provide our services</li>
                <li>Your data is protected with industry-standard security measures</li>
                <li>You have control over your personal information</li>
                <li>We comply with GDPR, CCPA, and other privacy regulations</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Information We Collect -->
        <section id="information-collected" class="policy-section">
          <h2>2. Information We Collect</h2>
          <div class="section-content">
            <h3>Personal Information</h3>
            <p>We may collect the following types of personal information:</p>
            
            <div class="data-categories">
              <div class="category-card">
                <div class="category-icon">
                  <i class="fas fa-user"></i>
                </div>
                <h4>Identity Information</h4>
                <ul>
                  <li>Full name</li>
                  <li>Email address</li>
                  <li>Phone number</li>
                  <li>Date of birth</li>
                </ul>
              </div>
              
              <div class="category-card">
                <div class="category-icon">
                  <i class="fas fa-map-marker-alt"></i>
                </div>
                <h4>Location Information</h4>
                <ul>
                  <li>IP address</li>
                  <li>Geographic location</li>
                  <li>Address information</li>
                </ul>
              </div>
              
              <div class="category-card">
                <div class="category-icon">
                  <i class="fas fa-laptop"></i>
                </div>
                <h4>Technical Information</h4>
                <ul>
                  <li>Browser type</li>
                  <li>Device information</li>
                  <li>Operating system</li>
                  <li>Usage data</li>
                </ul>
              </div>
              
              <div class="category-card">
                <div class="category-icon">
                  <i class="fas fa-chart-line"></i>
                </div>
                <h4>Behavioral Information</h4>
                <ul>
                  <li>Pages visited</li>
                  <li>Time spent on pages</li>
                  <li>Click patterns</li>
                  <li>Search queries</li>
                </ul>
              </div>
            </div>

            <h3>How We Collect Information</h3>
            <div class="collection-methods">
              <div class="method-item">
                <div class="method-icon">
                  <i class="fas fa-edit"></i>
                </div>
                <div class="method-content">
                  <h4>Direct Collection</h4>
                  <p>When you register, fill out forms, or contact us directly</p>
                </div>
              </div>
              
              <div class="method-item">
                <div class="method-icon">
                  <i class="fas fa-cookie"></i>
                </div>
                <div class="method-content">
                  <h4>Automated Technologies</h4>
                  <p>Cookies, web beacons, and similar technologies</p>
                </div>
              </div>
              
              <div class="method-item">
                <div class="method-icon">
                  <i class="fas fa-link"></i>
                </div>
                <div class="method-content">
                  <h4>Third Parties</h4>
                  <p>From partners, service providers, and public sources</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- How We Use Your Information -->
        <section id="information-usage" class="policy-section">
          <h2>3. How We Use Your Information</h2>
          <div class="section-content">
            <p>We use your personal information for the following purposes:</p>
            
            <div class="usage-purposes">
              <div class="purpose-item">
                <div class="purpose-icon">
                  <i class="fas fa-cogs"></i>
                </div>
                <div class="purpose-content">
                  <h4>Service Provision</h4>
                  <p>To provide, maintain, and improve our services</p>
                </div>
              </div>
              
              <div class="purpose-item">
                <div class="purpose-icon">
                  <i class="fas fa-user-shield"></i>
                </div>
                <div class="purpose-content">
                  <h4>Security & Safety</h4>
                  <p>To protect against fraud and ensure service security</p>
                </div>
              </div>
              
              <div class="purpose-item">
                <div class="purpose-icon">
                  <i class="fas fa-bullhorn"></i>
                </div>
                <div class="purpose-content">
                  <h4>Communication</h4>
                  <p>To send important updates and respond to inquiries</p>
                </div>
              </div>
              
              <div class="purpose-item">
                <div class="purpose-icon">
                  <i class="fas fa-chart-bar"></i>
                </div>
                <div class="purpose-content">
                  <h4>Analytics</h4>
                  <p>To understand usage patterns and improve our services</p>
                </div>
              </div>
              
              <div class="purpose-item">
                <div class="purpose-icon">
                  <i class="fas fa-gavel"></i>
                </div>
                <div class="purpose-content">
                  <h4>Legal Compliance</h4>
                  <p>To comply with legal obligations and protect our rights</p>
                </div>
              </div>
            </div>

            <div class="legal-basis">
              <h3>Legal Basis for Processing</h3>
              <div class="basis-grid">
                <div class="basis-item">
                  <h4>Consent</h4>
                  <p>When you explicitly agree to our processing activities</p>
                </div>
                <div class="basis-item">
                  <h4>Contractual Necessity</h4>
                  <p>To fulfill our obligations under our service agreement</p>
                </div>
                <div class="basis-item">
                  <h4>Legal Obligation</h4>
                  <p>When required by law or regulatory authorities</p>
                </div>
                <div class="basis-item">
                  <h4>Legitimate Interest</h4>
                  <p>When necessary for our legitimate business interests</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Data Sharing -->
        <section id="data-sharing" class="policy-section">
          <h2>4. Data Sharing and Disclosure</h2>
          <div class="section-content">
            <p>We may share your personal information in the following circumstances:</p>
            
            <div class="sharing-categories">
              <div class="sharing-card">
                <div class="sharing-icon">
                  <i class="fas fa-handshake"></i>
                </div>
                <h4>Service Providers</h4>
                <p>We share information with third-party service providers who help us operate our business, such as:</p>
                <ul>
                  <li>Cloud hosting providers</li>
                  <li>Payment processors</li>
                  <li>Email service providers</li>
                  <li>Analytics providers</li>
                </ul>
              </div>
              
              <div class="sharing-card">
                <div class="sharing-icon">
                  <i class="fas fa-users"></i>
                </div>
                <h4>Business Partners</h4>
                <p>We may share information with business partners when:</p>
                <ul>
                  <li>You consent to the sharing</li>
                  <li>It's necessary for joint services</li>
                  <li>We have a legitimate business interest</li>
                </ul>
              </div>
              
              <div class="sharing-card">
                <div class="sharing-icon">
                  <i class="fas fa-gavel"></i>
                </div>
                <h4>Legal Requirements</h4>
                <p>We may disclose information when required by:</p>
                <ul>
                  <li>Court orders or subpoenas</li>
                  <li>Law enforcement requests</li>
                  <li>Regulatory requirements</li>
                  <li>To protect our rights and safety</li>
                </ul>
              </div>
            </div>

            <div class="warning-box">
              <h3>Important Notice</h3>
              <p>We never sell your personal information to third parties for marketing purposes without your explicit consent.</p>
            </div>
          </div>
        </section>

        <!-- Data Security -->
        <section id="data-security" class="policy-section">
          <h2>5. Data Security</h2>
          <div class="section-content">
            <p>We implement comprehensive security measures to protect your personal information:</p>
            
            <div class="security-measures">
              <div class="measure-item">
                <div class="measure-icon">
                  <i class="fas fa-lock"></i>
                </div>
                <div class="measure-content">
                  <h4>Encryption</h4>
                  <p>All data is encrypted in transit and at rest using industry-standard encryption protocols</p>
                </div>
              </div>
              
              <div class="measure-item">
                <div class="measure-icon">
                  <i class="fas fa-shield-alt"></i>
                </div>
                <div class="measure-content">
                  <h4>Access Controls</h4>
                  <p>Strict access controls and authentication mechanisms prevent unauthorized access</p>
                </div>
              </div>
              
              <div class="measure-item">
                <div class="measure-icon">
                  <i class="fas fa-clipboard-check"></i>
                </div>
                <div class="measure-content">
                  <h4>Audits & Monitoring</h4>
                  <p>Regular security audits and continuous monitoring of our systems</p>
                </div>
              </div>
              
              <div class="measure-item">
                <div class="measure-icon">
                  <i class="fas fa-user-shield"></i>
                </div>
                <div class="measure-content">
                  <h4>Staff Training</h4>
                  <p>Regular training for all staff on privacy and security best practices</p>
                </div>
              </div>
            </div>

            <div class="security-certifications">
              <h3>Security Certifications</h3>
              <div class="certifications-grid">
                <div class="cert-item">
                  <div class="cert-logo">
                    <i class="fas fa-certificate"></i>
                  </div>
                  <h4>ISO 27001</h4>
                  <p>Information Security Management</p>
                </div>
                <div class="cert-item">
                  <div class="cert-logo">
                    <i class="fas fa-certificate"></i>
                  </div>
                  <h4>SOC 2 Type II</h4>
                  <p>Security Controls Assurance</p>
                </div>
                <div class="cert-item">
                  <div class="cert-logo">
                    <i class="fas fa-certificate"></i>
                  </div>
                  <h4>GDPR Compliant</h4>
                  <p>Data Protection Regulation</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Your Rights -->
        <section id="your-rights" class="policy-section">
          <h2>6. Your Privacy Rights</h2>
          <div class="section-content">
            <p>You have the following rights regarding your personal information:</p>
            
            <div class="rights-grid">
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-eye"></i>
                </div>
                <h3>Right to Access</h3>
                <p>Request access to your personal information and understand how it's being used</p>
                <button class="right-action" @click="exerciseRight('access')">
                  Exercise This Right
                </button>
              </div>
              
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-edit"></i>
                </div>
                <h3>Right to Rectification</h3>
                <p>Request correction of inaccurate or incomplete personal information</p>
                <button class="right-action" @click="exerciseRight('rectification')">
                  Exercise This Right
                </button>
              </div>
              
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-trash"></i>
                </div>
                <h3>Right to Erasure</h3>
                <p>Request deletion of your personal information under certain circumstances</p>
                <button class="right-action" @click="exerciseRight('erasure')">
                  Exercise This Right
                </button>
              </div>
              
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-download"></i>
                </div>
                <h3>Right to Portability</h3>
                <p>Request transfer of your data to another service provider</p>
                <button class="right-action" @click="exerciseRight('portability')">
                  Exercise This Right
                </button>
              </div>
              
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-ban"></i>
                </div>
                <h3>Right to Restrict</h3>
                <p>Request restriction of processing of your personal information</p>
                <button class="right-action" @click="exerciseRight('restriction')">
                  Exercise This Right
                </button>
              </div>
              
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-times-circle"></i>
                </div>
                <h3>Right to Object</h3>
                <p>Object to processing of your personal information for certain purposes</p>
                <button class="right-action" @click="exerciseRight('objection')">
                  Exercise This Right
                </button>
              </div>
            </div>

            <div class="rights-process">
              <h3>How to Exercise Your Rights</h3>
              <div class="process-steps">
                <div class="step-item">
                  <div class="step-number">1</div>
                  <div class="step-content">
                    <h4>Submit Request</h4>
                    <p>Contact us through our privacy request form or email</p>
                  </div>
                </div>
                <div class="step-item">
                  <div class="step-number">2</div>
                  <div class="step-content">
                    <h4>Verification</h4>
                    <p>We'll verify your identity to protect your privacy</p>
                  </div>
                </div>
                <div class="step-item">
                  <div class="step-number">3</div>
                  <div class="step-content">
                    <h4>Response</h4>
                    <p>We'll respond within 30 days as required by law</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Cookies -->
        <section id="cookies" class="policy-section">
          <h2>7. Cookies and Tracking Technologies</h2>
          <div class="section-content">
            <p>We use cookies and similar technologies to enhance your experience:</p>
            
            <div class="cookie-types">
              <div class="cookie-card">
                <h4>Essential Cookies</h4>
                <p>Required for the website to function properly</p>
                <div class="cookie-status required">Required</div>
              </div>
              
              <div class="cookie-card">
                <h4>Performance Cookies</h4>
                <p>Help us understand how visitors interact with our website</p>
                <div class="cookie-status optional">Optional</div>
              </div>
              
              <div class="cookie-card">
                <h4>Functional Cookies</h4>
                <p>Enable enhanced functionality and personalization</p>
                <div class="cookie-status optional">Optional</div>
              </div>
              
              <div class="cookie-card">
                <h4>Marketing Cookies</h4>
                <p>Used to deliver relevant advertisements</p>
                <div class="cookie-status optional">Optional</div>
              </div>
            </div>

            <div class="cookie-controls">
              <h3>Cookie Preferences</h3>
              <div class="cookie-settings">
                <div class="setting-item">
                  <label class="toggle-label">
                    <input type="checkbox" checked disabled>
                    <span class="toggle-slider"></span>
                    Essential Cookies
                  </label>
                  <span class="setting-description">Required for basic functionality</span>
                </div>
                <div class="setting-item">
                  <label class="toggle-label">
                    <input type="checkbox" v-model="cookieSettings.performance">
                    <span class="toggle-slider"></span>
                    Performance Cookies
                  </label>
                  <span class="setting-description">Help us improve our services</span>
                </div>
                <div class="setting-item">
                  <label class="toggle-label">
                    <input type="checkbox" v-model="cookieSettings.functional">
                    <span class="toggle-slider"></span>
                    Functional Cookies
                  </label>
                  <span class="setting-description">Enable enhanced features</span>
                </div>
                <div class="setting-item">
                  <label class="toggle-label">
                    <input type="checkbox" v-model="cookieSettings.marketing">
                    <span class="toggle-slider"></span>
                    Marketing Cookies
                  </label>
                  <span class="setting-description">Show personalized ads</span>
                </div>
              </div>
              <button class="save-cookies-btn" @click="saveCookieSettings">
                Save Preferences
              </button>
            </div>
          </div>
        </section>

        <!-- International Data Transfers -->
        <section id="international-transfers" class="policy-section">
          <h2>8. International Data Transfers</h2>
          <div class="section-content">
            <p>Your personal information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place:</p>
            
            <div class="transfer-safeguards">
              <div class="safeguard-item">
                <div class="safeguard-icon">
                  <i class="fas fa-file-contract"></i>
                </div>
                <h4>Standard Contractual Clauses</h4>
                <p>EU-approved contractual protections for international data transfers</p>
              </div>
              
              <div class="safeguard-item">
                <div class="safeguard-icon">
                  <i class="fas fa-globe"></i>
                </div>
                <h4>Adequacy Decisions</h4>
                <p>Transfers to countries with EU-approved data protection laws</p>
              </div>
              
              <div class="safeguard-item">
                <div class="safeguard-icon">
                  <i class="fas fa-shield-alt"></i>
                </div>
                <h4>Binding Corporate Rules</h4>
                <p>Internal rules for intra-group data transfers</p>
              </div>
            </div>

            <div class="data-centers">
              <h3>Our Data Centers</h3>
              <div class="centers-grid">
                <div class="center-item">
                  <div class="center-flag">🇺🇸</div>
                  <h4>United States</h4>
                  <p>Primary data center location</p>
                </div>
                <div class="center-item">
                  <div class="center-flag">🇪🇺</div>
                  <h4>European Union</h4>
                  <p>GDPR-compliant data storage</p>
                </div>
                <div class="center-item">
                  <div class="center-flag">🇨🇦</div>
                  <h4>Canada</h4>
                  <p>Backup and redundancy</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Policy Updates -->
        <section id="policy-updates" class="policy-section">
          <h2>9. Policy Updates</h2>
          <div class="section-content">
            <p>We may update this Privacy Policy from time to time. Here's how we handle changes:</p>
            
            <div class="update-process">
              <div class="update-item">
                <div class="update-icon">
                  <i class="fas fa-bell"></i>
                </div>
                <h4>Notification</h4>
                <p>We'll notify you of significant changes via email or website notice</p>
              </div>
              
              <div class="update-item">
                <div class="update-icon">
                  <i class="fas fa-calendar"></i>
                </div>
                <h4>Effective Date</h4>
                <p>Changes take effect 30 days after notification</p>
              </div>
              
              <div class="update-item">
                <div class="update-icon">
                  <i class="fas fa-history"></i>
                </div>
                <h4>Archive</h4>
                <p>Previous versions are archived and available upon request</p>
              </div>
            </div>

            <div class="update-history">
              <h3>Recent Updates</h3>
              <div class="history-timeline">
                <div class="history-item">
                  <div class="history-date">{{ formatDate('2024-01-15T00:00:00Z') }}</div>
                  <div class="history-content">
                    <h4>Updated Cookie Policy</h4>
                    <p>Added new cookie categories and improved user controls</p>
                  </div>
                </div>
                <div class="history-item">
                  <div class="history-date">{{ formatDate('2023-12-01T00:00:00Z') }}</div>
                  <div class="history-content">
                    <h4>GDPR Enhancements</h4>
                    <p>Enhanced privacy rights section and data processing transparency</p>
                  </div>
                </div>
                <div class="history-item">
                  <div class="history-date">{{ formatDate('2023-10-15T00:00:00Z') }}</div>
                  <div class="history-content">
                    <h4>Security Updates</h4>
                    <p>Updated security measures and certifications</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Contact Information -->
        <section id="contact" class="policy-section">
          <h2>10. Contact Information</h2>
          <div class="section-content">
            <p>If you have questions about this Privacy Policy or want to exercise your privacy rights, please contact us:</p>
            
            <div class="contact-methods">
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-envelope"></i>
                </div>
                <h4>Email</h4>
                <a href="mailto:privacy@company.com">privacy@company.com</a>
              </div>
              
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-phone"></i>
                </div>
                <h4>Phone</h4>
                <a href="tel:+1-800-PRIVACY">+1-800-PRIVACY</a>
              </div>
              
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-map-marker-alt"></i>
                </div>
                <h4>Mail</h4>
                <p>Privacy Officer<br>123 Privacy Street<br>San Francisco, CA 94105</p>
              </div>
              
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-user-shield"></i>
                </div>
                <h4>Data Protection Officer</h4>
                <a href="mailto:dpo@company.com">dpo@company.com</a>
              </div>
            </div>

            <div class="response-times">
              <h3>Response Times</h3>
              <div class="time-grid">
                <div class="time-item">
                  <h4>General Inquiries</h4>
                  <p>Within 3-5 business days</p>
                </div>
                <div class="time-item">
                  <h4>Privacy Rights Requests</h4>
                  <p>Within 30 days (legal requirement)</p>
                </div>
                <div class="time-item">
                  <h4>Data Breach Notifications</h4>
                  <p>Within 72 hours (when required)</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Privacy Rights Modal -->
    <div v-if="showRightsModal" class="modal-overlay" @click="closeRightsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Exercise Your Privacy Rights</h2>
          <button class="close-btn" @click="closeRightsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="rights-form">
            <div class="form-group">
              <label>Right to Exercise *</label>
              <select v-model="rightsForm.right" required>
                <option value="">Select a right</option>
                <option value="access">Right to Access</option>
                <option value="rectification">Right to Rectification</option>
                <option value="erasure">Right to Erasure</option>
                <option value="portability">Right to Portability</option>
                <option value="restriction">Right to Restrict Processing</option>
                <option value="objection">Right to Object</option>
              </select>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Full Name *</label>
                <input 
                  v-model="rightsForm.name" 
                  type="text" 
                  placeholder="Enter your full name"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>Email Address *</label>
                <input 
                  v-model="rightsForm.email" 
                  type="email" 
                  placeholder="Enter your email address"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label>Request Details *</label>
              <textarea 
                v-model="rightsForm.details" 
                placeholder="Please provide details about your request"
                rows="4"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label>Identity Verification</label>
              <p class="form-help">To protect your privacy, we may need to verify your identity before processing your request.</p>
              <div class="verification-options">
                <label class="radio-item">
                  <input type="radio" value="email" v-model="rightsForm.verification" />
                  <span>Email Verification</span>
                </label>
                <label class="radio-item">
                  <input type="radio" value="phone" v-model="rightsForm.verification" />
                  <span>Phone Verification</span>
                </label>
                <label class="radio-item">
                  <input type="radio" value="document" v-model="rightsForm.verification" />
                  <span>Document Verification</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeRightsModal">Cancel</button>
          <button class="btn-primary" @click="submitRightsRequest">
            <i class="fas fa-paper-plane"></i>
            Submit Request
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const activeSection = ref('introduction')
const showRightsModal = ref(false)
const lastUpdated = ref('2024-01-15T00:00:00Z')

// Cookie settings
const cookieSettings = reactive({
  performance: true,
  functional: false,
  marketing: false
})

// Rights form
const rightsForm = reactive({
  right: '',
  name: '',
  email: '',
  details: '',
  verification: 'email'
})

// Policy sections
const sections = ref([
  { id: 'introduction', title: 'Introduction' },
  { id: 'information-collected', title: 'Information We Collect' },
  { id: 'information-usage', title: 'How We Use Your Information' },
  { id: 'data-sharing', title: 'Data Sharing and Disclosure' },
  { id: 'data-security', title: 'Data Security' },
  { id: 'your-rights', title: 'Your Privacy Rights' },
  { id: 'cookies', title: 'Cookies and Tracking' },
  { id: 'international-transfers', title: 'International Data Transfers' },
  { id: 'policy-updates', title: 'Policy Updates' },
  { id: 'contact', title: 'Contact Information' }
])

// Methods
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const setActiveSection = (sectionId) => {
  activeSection.value = sectionId
}

const exerciseRight = (right) => {
  rightsForm.right = right
  showRightsModal.value = true
}

const closeRightsModal = () => {
  showRightsModal.value = false
  resetRightsForm()
}

const resetRightsForm = () => {
  Object.assign(rightsForm, {
    right: '',
    name: '',
    email: '',
    details: '',
    verification: 'email'
  })
}

const saveCookieSettings = () => {
  // Save cookie preferences
  localStorage.setItem('cookieSettings', JSON.stringify(cookieSettings))
  showSuccess('Cookie preferences saved successfully')
}

const submitRightsRequest = () => {
  if (!rightsForm.right || !rightsForm.name || !rightsForm.email || !rightsForm.details) {
    showError('Please fill in all required fields')
    return
  }

  // Submit rights request
  showSuccess('Your privacy rights request has been submitted successfully')
  closeRightsModal()
}

// Intersection Observer for active section tracking
onMounted(() => {
  // Load saved cookie settings
  const saved = localStorage.getItem('cookieSettings')
  if (saved) {
    Object.assign(cookieSettings, JSON.parse(saved))
  }

  // Set up intersection observer for section tracking
  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -70% 0px',
    threshold: 0
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        activeSection.value = entry.target.id
      }
    })
  }, observerOptions)

  // Observe all sections
  setTimeout(() => {
    const sections = document.querySelectorAll('.policy-section')
    sections.forEach(section => observer.observe(section))
  }, 100)
})
</script>

<style scoped>
.privacy-policy {
  padding: 2rem;
  max-width: 1200px;
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

.policy-container {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 3rem;
}

.table-of-contents {
  position: sticky;
  top: 2rem;
  height: fit-content;
}

.table-of-contents h2 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.2rem;
}

.toc-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toc-link {
  padding: 0.75rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.toc-link:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

.toc-link.active {
  background: var(--primary-color);
  color: white;
}

.policy-content {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 3rem;
}

.policy-section {
  margin-bottom: 4rem;
}

.policy-section:last-child {
  margin-bottom: 0;
}

.policy-section h2 {
  margin: 0 0 2rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.8rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--glass-border);
}

.section-content p {
  margin: 0 0 1.5rem 0;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 1rem;
}

.section-content h3 {
  margin: 2rem 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.3rem;
}

.section-content h4 {
  margin: 1.5rem 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.info-box,
.warning-box {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 2rem 0;
}

.info-box {
  border-left: 4px solid var(--info-color);
}

.warning-box {
  border-left: 4px solid var(--warning-color);
}

.info-box h3,
.warning-box h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
}

.info-box ul,
.warning-box ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.info-box li,
.warning-box li {
  padding: 0.5rem 0;
  color: var(--text-secondary);
  position: relative;
  padding-left: 1.5rem;
}

.info-box li::before,
.warning-box li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--info-color);
  font-weight: bold;
}

.data-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.category-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.category-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
}

.category-card h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.category-card ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.category-card li {
  padding: 0.25rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.collection-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.method-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.method-icon {
  width: 50px;
  height: 50px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.usage-purposes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.purpose-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.purpose-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.purpose-icon {
  width: 60px;
  height: 60px;
  background: var(--success-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
}

.legal-basis {
  margin: 3rem 0;
}

.basis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.basis-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.basis-item h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.sharing-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.sharing-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.sharing-icon {
  width: 50px;
  height: 50px;
  background: var(--warning-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.sharing-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.sharing-card ul {
  margin: 1rem 0 0 0;
  padding: 0;
  list-style: none;
}

.sharing-card li {
  padding: 0.25rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  position: relative;
  padding-left: 1rem;
}

.sharing-card li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--warning-color);
}

.security-measures {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.measure-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.measure-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.measure-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
}

.security-certifications {
  margin: 3rem 0;
}

.certifications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.cert-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.cert-logo {
  width: 50px;
  height: 50px;
  background: var(--success-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  margin: 0 auto 1rem;
}

.cert-item h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.rights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.right-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.right-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.right-icon {
  width: 60px;
  height: 60px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
}

.right-card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.right-card p {
  margin: 0 0 1.5rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.right-action {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.right-action:hover {
  background: var(--primary-hover);
}

.rights-process {
  margin: 3rem 0;
}

.process-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.step-number {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  flex-shrink: 0;
}

.cookie-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.cookie-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
}

.cookie-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.cookie-card p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.cookie-status {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.cookie-status.required {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.cookie-status.optional {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.cookie-controls {
  margin: 3rem 0;
}

.cookie-settings {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  margin: 2rem 0;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.setting-item:last-child {
  border-bottom: none;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  font-weight: 500;
  color: var(--text-primary);
}

.toggle-label input[type="checkbox"] {
  display: none;
}

.toggle-slider {
  width: 50px;
  height: 26px;
  background: var(--glass-border);
  border-radius: 13px;
  position: relative;
  transition: all 0.3s ease;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: all 0.3s ease;
}

.toggle-label input[type="checkbox"]:checked + .toggle-slider {
  background: var(--primary-color);
}

.toggle-label input[type="checkbox"]:checked + .toggle-slider::before {
  transform: translateX(24px);
}

.setting-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.save-cookies-btn {
  padding: 0.75rem 2rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 2rem;
}

.save-cookies-btn:hover {
  background: var(--primary-hover);
}

.transfer-safeguards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.safeguard-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.safeguard-icon {
  width: 60px;
  height: 60px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
}

.safeguard-item h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.data-centers {
  margin: 3rem 0;
}

.centers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.center-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.center-flag {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.center-item h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.update-process {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.update-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.update-icon {
  width: 60px;
  height: 60px;
  background: var(--warning-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
}

.update-item h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.update-history {
  margin: 3rem 0;
}

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.history-item {
  display: flex;
  gap: 2rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.history-date {
  min-width: 120px;
  color: var(--text-secondary);
  font-weight: 600;
}

.history-content h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.history-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.contact-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.contact-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.contact-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
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
  margin: 0 auto 1rem;
}

.contact-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.contact-card a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.contact-card a:hover {
  text-decoration: underline;
}

.response-times {
  margin: 3rem 0;
}

.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.time-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.time-item h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
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

.rights-form {
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
  min-height: 100px;
}

.form-help {
  margin: 0.5rem 0 0 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.verification-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.radio-item input[type="radio"] {
  accent-color: var(--primary-color);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

.btn-primary,
.btn-secondary {
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
  .privacy-policy {
    padding: 1rem;
  }
  
  .policy-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .table-of-contents {
    position: static;
  }
  
  .toc-nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .policy-content {
    padding: 2rem;
  }
  
  .data-categories,
  .collection-methods,
  .usage-purposes,
  .sharing-categories,
  .security-measures,
  .rights-grid,
  .process-steps,
  .cookie-types,
  .transfer-safeguards,
  .centers-grid,
  .update-process,
  .contact-methods,
  .time-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
