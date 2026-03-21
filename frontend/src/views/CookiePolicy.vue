<template>
  <div class="cookie-policy">
    <div class="page-header">
      <h1>Cookie Policy</h1>
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
              This Cookie Policy explains how our website uses cookies and similar technologies to recognize you when you visit our site. It explains what these technologies are and why we use them, as well as your rights to control our use of them.
            </p>
            <p>
              Cookies are small text files that are stored on your device (computer, tablet, or mobile) when you visit a website. They help us provide you with a better experience by remembering your preferences and enabling certain functionality.
            </p>
            
            <div class="info-box">
              <h3>Key Points</h3>
              <ul>
                <li>We use cookies to enhance your browsing experience</li>
                <li>You can control which cookies are accepted</li>
                <li>We respect your privacy and data protection rights</li>
                <li>This policy is regularly updated to reflect changes</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- What Are Cookies -->
        <section id="what-are-cookies" class="policy-section">
          <h2>2. What Are Cookies?</h2>
          <div class="section-content">
            <p>
              Cookies are small text files that are placed on your device when you visit a website. They are widely used to make websites work more efficiently and to provide information to website owners.
            </p>
            
            <div class="cookie-types-overview">
              <div class="cookie-type-card">
                <div class="cookie-icon">
                  <i class="fas fa-cookie"></i>
                </div>
                <h4>Session Cookies</h4>
                <p>Temporary cookies that are deleted when you close your browser</p>
              </div>
              
              <div class="cookie-type-card">
                <div class="cookie-icon">
                  <i class="fas fa-save"></i>
                </div>
                <h4>Persistent Cookies</h4>
                <p>Cookies that remain on your device for a set period</p>
              </div>
              
              <div class="cookie-type-card">
                <div class="cookie-icon">
                  <i class="fas fa-globe"></i>
                </div>
                <h4>First-Party Cookies</h4>
                <p>Cookies set by the website you're visiting</p>
              </div>
              
              <div class="cookie-type-card">
                <div class="cookie-icon">
                  <i class="fas fa-link"></i>
                </div>
                <h4>Third-Party Cookies</h4>
                <p>Cookies set by external services on our website</p>
              </div>
            </div>

            <div class="how-cookies-work">
              <h3>How Cookies Work</h3>
              <div class="process-flow">
                <div class="process-step">
                  <div class="step-number">1</div>
                  <h4>Visit Website</h4>
                  <p>You visit our website</p>
                </div>
                <div class="process-step">
                  <div class="step-number">2</div>
                  <h4>Cookie Placement</h4>
                  <p>Our server places a cookie on your device</p>
                </div>
                <div class="process-step">
                  <div class="step-number">3</div>
                  <h4>Information Storage</h4>
                  <p>Cookie stores information about your visit</p>
                </div>
                <div class="process-step">
                  <div class="step-number">4</div>
                  <h4>Future Recognition</h4>
                  <p>Website recognizes you on future visits</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Types of Cookies We Use -->
        <section id="cookie-types" class="policy-section">
          <h2>3. Types of Cookies We Use</h2>
          <div class="section-content">
            <p>We use different types of cookies for various purposes. Here's a detailed breakdown:</p>
            
            <div class="cookie-categories">
              <div class="category-card essential">
                <div class="category-header">
                  <div class="category-icon">
                    <i class="fas fa-shield-alt"></i>
                  </div>
                  <div class="category-info">
                    <h3>Essential Cookies</h3>
                    <span class="category-status">Required</span>
                  </div>
                </div>
                <div class="category-content">
                  <p>These cookies are necessary for the website to function properly. They enable basic functions like page navigation, access to secure areas, and authentication.</p>
                  <div class="cookie-examples">
                    <h4>Examples:</h4>
                    <ul>
                      <li>Login authentication</li>
                      <li>Shopping cart contents</li>
                      <li>Security tokens</li>
                      <li>Load balancing</li>
                    </ul>
                  </div>
                  <div class="cookie-duration">
                    <strong>Duration:</strong> Session or persistent (up to 1 year)
                  </div>
                </div>
              </div>

              <div class="category-card performance">
                <div class="category-header">
                  <div class="category-icon">
                    <i class="fas fa-tachometer-alt"></i>
                  </div>
                  <div class="category-info">
                    <h3>Performance Cookies</h3>
                    <span class="category-status">Optional</span>
                  </div>
                </div>
                <div class="category-content">
                  <p>These cookies collect information about how visitors use our website, such as which pages are visited most often and if users receive error messages.</p>
                  <div class="cookie-examples">
                    <h4>Examples:</h4>
                    <ul>
                      <li>Page load times</li>
                      <li>Bounce rates</li>
                      <li>User journey tracking</li>
                      <li>Error reporting</li>
                    </ul>
                  </div>
                  <div class="cookie-duration">
                    <strong>Duration:</strong> Persistent (typically 30 days)
                  </div>
                </div>
              </div>

              <div class="category-card functional">
                <div class="category-header">
                  <div class="category-icon">
                    <i class="fas fa-cogs"></i>
                  </div>
                  <div class="category-info">
                    <h3>Functional Cookies</h3>
                    <span class="category-status">Optional</span>
                  </div>
                </div>
                <div class="category-content">
                  <p>These cookies enable enhanced functionality and personalization, such as videos and live chats. They may be set by us or by third-party providers.</p>
                  <div class="cookie-examples">
                    <h4>Examples:</h4>
                    <ul>
                      <li>Language preferences</li>
                      <li>Remembered login</li>
                      <li>Video player settings</li>
                      <li>Custom themes</li>
                    </ul>
                  </div>
                  <div class="cookie-duration">
                    <strong>Duration:</strong> Persistent (up to 1 year)
                  </div>
                </div>
              </div>

              <div class="category-card marketing">
                <div class="category-header">
                  <div class="category-icon">
                    <i class="fas fa-bullhorn"></i>
                  </div>
                  <div class="category-info">
                    <h3>Marketing Cookies</h3>
                    <span class="category-status">Optional</span>
                  </div>
                </div>
                <div class="category-content">
                  <p>These cookies are used to deliver advertisements that are relevant to you and your interests. They are also used to limit the number of times you see an advertisement.</p>
                  <div class="cookie-examples">
                    <h4>Examples:</h4>
                    <ul>
                      <li>Ad personalization</li>
                      <li>Cross-site tracking</li>
                      <li>Retargeting</li>
                      <li>A/B testing</li>
                    </ul>
                  </div>
                  <div class="cookie-duration">
                    <strong>Duration:</strong> Persistent (up to 2 years)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Third-Party Cookies -->
        <section id="third-party-cookies" class="policy-section">
          <h2>4. Third-Party Cookies</h2>
          <div class="section-content">
            <p>
              We work with third-party service providers who may place their own cookies on your device. These cookies are used for various purposes including analytics, advertising, and social media integration.
            </p>
            
            <div class="third-party-grid">
              <div class="provider-card">
                <div class="provider-logo">
                  <i class="fas fa-chart-line"></i>
                </div>
                <h4>Google Analytics</h4>
                <p>Website analytics and user behavior tracking</p>
                <div class="provider-details">
                  <span class="provider-purpose">Analytics</span>
                  <span class="provider-duration">2 years</span>
                </div>
              </div>
              
              <div class="provider-card">
                <div class="provider-logo">
                  <i class="fas fa-ad"></i>
                </div>
                <h4>Google Ads</h4>
                <p>Advertising and retargeting services</p>
                <div class="provider-details">
                  <span class="provider-purpose">Marketing</span>
                  <span class="provider-duration">18 months</span>
                </div>
              </div>
              
              <div class="provider-card">
                <div class="provider-logo">
                  <i class="fas fa-share-alt"></i>
                </div>
                <h4>Facebook Pixel</h4>
                <p>Social media advertising and analytics</p>
                <div class="provider-details">
                  <span class="provider-purpose">Marketing</span>
                  <span class="provider-duration">90 days</span>
                </div>
              </div>
              
              <div class="provider-card">
                <div class="provider-logo">
                  <i class="fas fa-video"></i>
                </div>
                <h4>YouTube</h4>
                <p>Video hosting and playback</p>
                <div class="provider-details">
                  <span class="provider-purpose">Functional</span>
                  <span class="provider-duration">1 year</span>
                </div>
              </div>
            </div>

            <div class="privacy-note">
              <h3>Privacy Notice</h3>
              <p>We do not control these third-party cookies. Please review the privacy policies of these third-party services for more information about their cookie practices.</p>
            </div>
          </div>
        </section>

        <!-- Managing Cookies -->
        <section id="managing-cookies" class="policy-section">
          <h2>5. Managing Your Cookie Preferences</h2>
          <div class="section-content">
            <p>You have several options to manage cookies on our website:</p>
            
            <div class="management-options">
              <div class="option-card">
                <div class="option-icon">
                  <i class="fas fa-sliders-h"></i>
                </div>
                <h3>Cookie Consent Banner</h3>
                <p>Use our cookie consent banner to choose which types of cookies to accept</p>
                <button class="option-btn" @click="openCookieSettings">
                  <i class="fas fa-cog"></i>
                  Open Settings
                </button>
              </div>
              
              <div class="option-card">
                <div class="option-icon">
                  <i class="fas fa-browser"></i>
                </div>
                <h3>Browser Settings</h3>
                <p>Configure your browser to accept, reject, or delete cookies</p>
                <div class="browser-links">
                  <a href="#" @click.prevent="showBrowserHelp('chrome')">Chrome</a>
                  <a href="#" @click.prevent="showBrowserHelp('firefox')">Firefox</a>
                  <a href="#" @click.prevent="showBrowserHelp('safari')">Safari</a>
                  <a href="#" @click.prevent="showBrowserHelp('edge')">Edge</a>
                </div>
              </div>
              
              <div class="option-card">
                <div class="option-icon">
                  <i class="fas fa-shield-alt"></i>
                </div>
                <h3>Privacy Tools</h3>
                <p>Use third-party privacy tools to manage tracking across websites</p>
                <div class="tool-links">
                  <a href="#" @click.prevent="showPrivacyTool('adblock')">Ad Blockers</a>
                  <a href="#" @click.prevent="showPrivacyTool('dnt')">Do Not Track</a>
                  <a href="#" @click.prevent="showPrivacyTool('privacy')">Privacy Badges</a>
                </div>
              </div>
            </div>

            <div class="browser-guide">
              <h3>Browser-Specific Instructions</h3>
              <div class="browser-instructions">
                <div class="instruction-item" v-for="browser in browserInstructions" :key="browser.name">
                  <h4>{{ browser.name }}</h4>
                  <ol>
                    <li v-for="step in browser.steps" :key="step">{{ step }}</li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Cookie Settings -->
        <section id="cookie-settings" class="policy-section">
          <h2>6. Your Cookie Settings</h2>
          <div class="section-content">
            <p>Customize your cookie preferences below. Changes will be saved for future visits.</p>
            
            <div class="settings-panel">
              <div class="setting-item" v-for="setting in cookieSettings" :key="setting.id">
                <div class="setting-header">
                  <div class="setting-info">
                    <h3>{{ setting.name }}</h3>
                    <p>{{ setting.description }}</p>
                  </div>
                  <div class="setting-control">
                    <label class="toggle-label">
                      <input 
                        type="checkbox" 
                        :checked="setting.enabled"
                        :disabled="setting.required"
                        @change="updateCookieSetting(setting.id, $event.target.checked)"
                      />
                      <span class="toggle-slider"></span>
                    </label>
                    <span class="setting-status" :class="{ 'required': setting.required }">
                      {{ setting.required ? 'Required' : (setting.enabled ? 'Enabled' : 'Disabled') }}
                    </span>
                  </div>
                </div>
                
                <div class="setting-details" v-if="setting.details">
                  <h4>What these cookies do:</h4>
                  <ul>
                    <li v-for="detail in setting.details" :key="detail">{{ detail }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="settings-actions">
              <button class="btn-secondary" @click="resetToDefaults">
                <i class="fas fa-undo"></i>
                Reset to Defaults
              </button>
              <button class="btn-primary" @click="saveCookieSettings">
                <i class="fas fa-save"></i>
                Save Preferences
              </button>
            </div>
          </div>
        </section>

        <!-- Cookie Lifespan -->
        <section id="lifespan" class="policy-section">
          <h2>7. Cookie Lifespan</h2>
          <div class="section-content">
            <p>Different cookies have different lifespans depending on their purpose:</p>
            
            <div class="lifespan-grid">
              <div class="lifespan-card">
                <div class="lifespan-icon">
                  <i class="fas fa-clock"></i>
                </div>
                <h3>Session Cookies</h3>
                <p>Deleted when you close your browser</p>
                <div class="lifespan-examples">
                  <strong>Used for:</strong>
                  <ul>
                    <li>Login sessions</li>
                    <li>Shopping cart</li>
                    <li>Security tokens</li>
                  </ul>
                </div>
              </div>
              
              <div class="lifespan-card">
                <div class="lifespan-icon">
                  <i class="fas fa-calendar-day"></i>
                </div>
                <h3>Short-term Cookies</h3>
                <p>Last from a few hours to a few days</p>
                <div class="lifespan-examples">
                  <strong>Used for:</strong>
                  <ul>
                    <li>Analytics tracking</li>
                    <li>A/B testing</li>
                    <li>Feature flags</li>
                  </ul>
                </div>
              </div>
              
              <div class="lifespan-card">
                <div class="lifespan-icon">
                  <i class="fas fa-calendar-week"></i>
                </div>
                <h3>Medium-term Cookies</h3>
                <p>Last from weeks to several months</p>
                <div class="lifespan-examples">
                  <strong>Used for:</strong>
                  <ul>
                    <li>User preferences</li>
                    <li>Personalization</li>
                    <li>Marketing attribution</li>
                  </ul>
                </div>
              </div>
              
              <div class="lifespan-card">
                <div class="lifespan-icon">
                  <i class="fas fa-calendar-alt"></i>
                </div>
                <h3>Long-term Cookies</h3>
                <p>Last from several months to years</p>
                <div class="lifespan-examples">
                  <strong>Used for:</strong>
                  <ul>
                    <li>Remembered login</li>
                    <li>Advertising ID</li>
                    <li>User analytics</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Your Rights -->
        <section id="your-rights" class="policy-section">
          <h2>8. Your Rights Regarding Cookies</h2>
          <div class="section-content">
            <p>Under data protection laws, you have specific rights regarding cookies:</p>
            
            <div class="rights-grid">
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-info-circle"></i>
                </div>
                <h3>Right to Information</h3>
                <p>You have the right to know what cookies are being used and for what purpose</p>
              </div>
              
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-ban"></i>
                </div>
                <h3>Right to Consent</h3>
                <p>You have the right to give or withhold consent for non-essential cookies</p>
              </div>
              
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-trash"></i>
                </div>
                <h3>Right to Delete</h3>
                <p>You have the right to delete cookies from your device at any time</p>
              </div>
              
              <div class="right-card">
                <div class="right-icon">
                  <i class="fas fa-cog"></i>
                </div>
                <h3>Right to Control</h3>
                <p>You have the right to control which cookies are accepted through settings</p>
              </div>
            </div>

            <div class="legal-compliance">
              <h3>Legal Compliance</h3>
              <p>We comply with:</p>
              <ul>
                <li><strong>GDPR:</strong> Requires explicit consent for non-essential cookies</li>
                <li><strong>ePrivacy Directive:</strong> Requires user consent for tracking technologies</li>
                <li><strong>CCPA:</strong> Provides opt-out options for California residents</li>
                <li><strong>PECR:</strong> UK regulations for electronic communications</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Updates to Policy -->
        <section id="policy-updates" class="policy-section">
          <h2>9. Updates to This Cookie Policy</h2>
          <div class="section-content">
            <p>We may update this Cookie Policy from time to time to reflect changes in our practices or for legal reasons.</p>
            
            <div class="update-process">
              <h3>How We Notify Changes</h3>
              <div class="notification-methods">
                <div class="method-item">
                  <div class="method-icon">
                    <i class="fas fa-bell"></i>
                  </div>
                  <h4>Website Notice</h4>
                  <p>Updated date displayed on this page</p>
                </div>
                
                <div class="method-item">
                  <div class="method-icon">
                    <i class="fas fa-envelope"></i>
                  </div>
                  <h4>Email Notification</h4>
                  <p>Email for significant policy changes</p>
                </div>
                
                <div class="method-item">
                  <div class="method-icon">
                    <i class="fas fa-cookie-bite"></i>
                  </div>
                  <h4>Cookie Banner</h4>
                  <p>Updated consent banner for new cookie types</p>
                </div>
              </div>
            </div>

            <div class="recent-updates">
              <h3>Recent Updates</h3>
              <div class="update-timeline">
                <div class="update-item">
                  <div class="update-date">{{ formatDate('2024-01-15T00:00:00Z') }}</div>
                  <div class="update-content">
                    <h4>Enhanced Cookie Categories</h4>
                    <p>Added more detailed descriptions of cookie types and purposes</p>
                  </div>
                </div>
                <div class="update-item">
                  <div class="update-date">{{ formatDate('2023-12-01T00:00:00Z') }}</div>
                  <div class="update-content">
                    <h4>Third-Party Provider Updates</h4>
                    <p>Updated list of third-party cookie providers and their purposes</p>
                  </div>
                </div>
                <div class="update-item">
                  <div class="update-date">{{ formatDate('2023-10-15T00:00:00Z') }}</div>
                  <div class="update-content">
                    <h4>Browser Instructions</h4>
                    <p>Added detailed instructions for managing cookies in different browsers</p>
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
            <p>If you have any questions about this Cookie Policy or our use of cookies, please contact us:</p>
            
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
                <a href="tel:+1-800-COOKIES">+1-800-COOKIES</a>
              </div>
              
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-map-marker-alt"></i>
                </div>
                <h4>Mail</h4>
                <p>Privacy Officer<br>123 Cookie Street<br>San Francisco, CA 94105</p>
              </div>
              
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-globe"></i>
                </div>
                <h4>Online Form</h4>
                <a href="/contact">Contact Form</a>
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
                  <h4>Privacy Concerns</h4>
                  <p>Within 24-48 hours</p>
                </div>
                <div class="time-item">
                  <h4>Technical Issues</h4>
                  <p>Within 24 hours</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Cookie Settings Modal -->
    <div v-if="showCookieModal" class="modal-overlay" @click="closeCookieModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Cookie Preferences</h2>
          <button class="close-btn" @click="closeCookieModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="cookie-settings-modal">
            <div class="setting-item" v-for="setting in cookieSettings" :key="setting.id">
              <div class="setting-header">
                <div class="setting-info">
                  <h3>{{ setting.name }}</h3>
                  <p>{{ setting.description }}</p>
                </div>
                <div class="setting-control">
                  <label class="toggle-label">
                    <input 
                      type="checkbox" 
                      :checked="setting.enabled"
                      :disabled="setting.required"
                      @change="updateCookieSetting(setting.id, $event.target.checked)"
                    />
                    <span class="toggle-slider"></span>
                  </label>
                  <span class="setting-status" :class="{ 'required': setting.required }">
                    {{ setting.required ? 'Required' : (setting.enabled ? 'Enabled' : 'Disabled') }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="acceptAllCookies">
            <i class="fas fa-check"></i>
            Accept All
          </button>
          <button class="btn-secondary" @click="rejectNonEssential">
            <i class="fas fa-times"></i>
            Reject Non-Essential
          </button>
          <button class="btn-primary" @click="saveAndClose">
            <i class="fas fa-save"></i>
            Save Preferences
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
const showCookieModal = ref(false)
const lastUpdated = ref('2024-01-15T00:00:00Z')

// Cookie settings
const cookieSettings = reactive([
  {
    id: 'essential',
    name: 'Essential Cookies',
    description: 'Required for basic website functionality',
    enabled: true,
    required: true,
    details: [
      'User authentication',
      'Shopping cart management',
      'Security features',
      'Load balancing'
    ]
  },
  {
    id: 'performance',
    name: 'Performance Cookies',
    description: 'Help us understand how visitors interact with our website',
    enabled: true,
    required: false,
    details: [
      'Page load analytics',
      'User behavior tracking',
      'Performance monitoring',
      'Error reporting'
    ]
  },
  {
    id: 'functional',
    name: 'Functional Cookies',
    description: 'Enable enhanced features and personalization',
    enabled: false,
    required: false,
    details: [
      'Remember preferences',
      'Custom themes',
      'Video player settings',
      'Social media integration'
    ]
  },
  {
    id: 'marketing',
    name: 'Marketing Cookies',
    description: 'Used to deliver relevant advertisements',
    enabled: false,
    required: false,
    details: [
      'Ad personalization',
      'Cross-site tracking',
      'Retargeting campaigns',
      'Conversion tracking'
    ]
  }
])

// Browser instructions
const browserInstructions = ref([
  {
    name: 'Chrome',
    steps: [
      'Click on the three dots in the top right corner',
      'Select "Settings" from the dropdown menu',
      'Click on "Privacy and security" in the left sidebar',
      'Select "Cookies and other site data"',
      'Choose your preferred cookie settings'
    ]
  },
  {
    name: 'Firefox',
    steps: [
      'Click on the three lines in the top right corner',
      'Select "Settings" from the dropdown menu',
      'Scroll down to "Privacy & Security" section',
      'Click on "Cookies and Site Data"',
      'Configure your cookie preferences'
    ]
  },
  {
    name: 'Safari',
    steps: [
      'Click on "Safari" in the top menu bar',
      'Select "Preferences" from the dropdown menu',
      'Go to the "Privacy" tab',
      'Click on "Manage Website Data"',
      'Adjust your cookie settings'
    ]
  },
  {
    name: 'Edge',
    steps: [
      'Click on the three dots in the top right corner',
      'Select "Settings" from the dropdown menu',
      'Click on "Privacy, search, and services"',
      'Find the "Cookies" section',
      'Choose your preferred settings'
    ]
  }
])

// Policy sections
const sections = ref([
  { id: 'introduction', title: 'Introduction' },
  { id: 'what-are-cookies', title: 'What Are Cookies?' },
  { id: 'cookie-types', title: 'Types of Cookies We Use' },
  { id: 'third-party-cookies', title: 'Third-Party Cookies' },
  { id: 'managing-cookies', title: 'Managing Your Preferences' },
  { id: 'cookie-settings', title: 'Your Cookie Settings' },
  { id: 'lifespan', title: 'Cookie Lifespan' },
  { id: 'your-rights', title: 'Your Rights' },
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

const openCookieSettings = () => {
  showCookieModal.value = true
}

const closeCookieModal = () => {
  showCookieModal.value = false
}

const updateCookieSetting = (settingId, enabled) => {
  const setting = cookieSettings.find(s => s.id === settingId)
  if (setting && !setting.required) {
    setting.enabled = enabled
  }
}

const saveCookieSettings = () => {
  localStorage.setItem('cookieSettings', JSON.stringify(cookieSettings))
  showSuccess('Cookie preferences saved successfully')
}

const resetToDefaults = () => {
  cookieSettings.forEach(setting => {
    if (!setting.required) {
      setting.enabled = false
    }
  })
  showSuccess('Cookie settings reset to defaults')
}

const acceptAllCookies = () => {
  cookieSettings.forEach(setting => {
    setting.enabled = true
  })
  saveCookieSettings()
  closeCookieModal()
}

const rejectNonEssential = () => {
  cookieSettings.forEach(setting => {
    if (!setting.required) {
      setting.enabled = false
    }
  })
  saveCookieSettings()
  closeCookieModal()
}

const saveAndClose = () => {
  saveCookieSettings()
  closeCookieModal()
}

const showBrowserHelp = (browser) => {
  showSuccess(`Opening ${browser} cookie help...`)
}

const showPrivacyTool = (tool) => {
  showSuccess(`Opening information about ${tool}...`)
}

// Intersection Observer for active section tracking
onMounted(() => {
  // Load saved cookie settings
  const saved = localStorage.getItem('cookieSettings')
  if (saved) {
    const savedSettings = JSON.parse(saved)
    cookieSettings.forEach(setting => {
      const savedSetting = savedSettings.find(s => s.id === setting.id)
      if (savedSetting && !setting.required) {
        setting.enabled = savedSetting.enabled
      }
    })
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
.cookie-policy {
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

.section-content ul {
  margin: 1rem 0;
  padding: 0;
  list-style: none;
}

.section-content li {
  padding: 0.5rem 0;
  color: var(--text-secondary);
  position: relative;
  padding-left: 1.5rem;
}

.section-content li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--primary-color);
  font-weight: bold;
}

.info-box {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 2rem 0;
  border-left: 4px solid var(--info-color);
}

.info-box h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
}

.cookie-types-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.cookie-type-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.cookie-type-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.cookie-icon {
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

.cookie-type-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.how-cookies-work {
  margin: 3rem 0;
}

.process-flow {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.process-step {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
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
  margin: 0 auto 1rem;
}

.process-step h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.cookie-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.category-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.category-card.essential {
  border-left: 4px solid var(--success-color);
}

.category-card.performance {
  border-left: 4px solid var(--info-color);
}

.category-card.functional {
  border-left: 4px solid var(--warning-color);
}

.category-card.marketing {
  border-left: 4px solid var(--danger-color);
}

.category-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--glass-bg-tertiary);
  border-bottom: 1px solid var(--glass-border);
}

.category-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.category-card.essential .category-icon {
  background: var(--success-color);
}

.category-card.performance .category-icon {
  background: var(--info-color);
}

.category-card.functional .category-icon {
  background: var(--warning-color);
}

.category-card.marketing .category-icon {
  background: var(--danger-color);
}

.category-info {
  flex: 1;
}

.category-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.category-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.category-status.required {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.category-status.optional {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.category-content {
  padding: 1.5rem;
}

.cookie-examples {
  margin: 1rem 0;
}

.cookie-examples h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.cookie-duration {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
  font-size: 0.9rem;
}

.third-party-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.provider-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.provider-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.provider-logo {
  width: 50px;
  height: 50px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  margin: 0 auto 1rem;
}

.provider-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.provider-details {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  font-size: 0.8rem;
}

.provider-purpose {
  padding: 0.25rem 0.75rem;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border-radius: 12px;
}

.provider-duration {
  color: var(--text-secondary);
}

.privacy-note {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 2rem 0;
  border-left: 4px solid var(--warning-color);
}

.management-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.option-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
}

.option-icon {
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

.option-card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.browser-links,
.tool-links {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

.browser-links a,
.tool-links a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border: 1px solid var(--primary-color);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.browser-links a:hover,
.tool-links a:hover {
  background: var(--primary-color);
  color: white;
}

.option-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.option-btn:hover {
  background: var(--primary-hover);
}

.browser-guide {
  margin: 3rem 0;
}

.browser-instructions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.instruction-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.instruction-item h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.instruction-item ol {
  margin: 0;
  padding-left: 1.5rem;
}

.instruction-item li {
  padding: 0.5rem 0;
  color: var(--text-secondary);
}

.settings-panel {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem 0;
}

.setting-item {
  padding: 2rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.setting-info {
  flex: 1;
}

.setting-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.setting-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.setting-control {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
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

.setting-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
}

.setting-status.required {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.setting-status:not(.required) {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
}

.setting-details {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
}

.setting-details h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.settings-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
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

.lifespan-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.lifespan-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.lifespan-icon {
  width: 50px;
  height: 50px;
  background: var(--warning-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  margin: 0 auto 1rem;
}

.lifespan-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.lifespan-examples {
  margin-top: 1rem;
  text-align: left;
}

.lifespan-examples strong {
  color: var(--text-primary);
  font-size: 0.9rem;
}

.rights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.right-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.right-icon {
  width: 50px;
  height: 50px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  margin: 0 auto 1rem;
}

.right-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.legal-compliance {
  margin: 2rem 0;
}

.update-process {
  margin: 2rem 0;
}

.notification-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.method-item {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.method-icon {
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

.method-item h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.recent-updates {
  margin: 2rem 0;
}

.update-timeline {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.update-item {
  display: flex;
  gap: 2rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.update-date {
  min-width: 120px;
  color: var(--text-secondary);
  font-weight: 600;
}

.update-content h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.update-content p {
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
  margin: 2rem 0;
}

.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

.cookie-settings-modal {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid var(--glass-border);
}

@media (max-width: 768px) {
  .cookie-policy {
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
  
  .cookie-types-overview,
  .cookie-categories,
  .third-party-grid,
  .management-options,
  .lifespan-grid,
  .rights-grid,
  .notification-methods,
  .contact-methods,
  .time-grid {
    grid-template-columns: 1fr;
  }
  
  .process-flow {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .setting-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-footer {
    flex-direction: column;
  }
}
</style>
