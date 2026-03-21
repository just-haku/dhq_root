<template>
  <div class="terms-of-service">
    <div class="page-header">
      <h1>Terms of Service</h1>
      <p>Last updated: {{ formatDate(lastUpdated) }}</p>
    </div>

    <div class="terms-container">
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

      <!-- Terms Content -->
      <div class="terms-content">
        <!-- Agreement -->
        <section id="agreement" class="terms-section">
          <h2>1. Agreement to Terms</h2>
          <div class="section-content">
            <p>
              Welcome to our Service. These Terms of Service ("Terms") govern your access to and use of our website, applications, and services (collectively, the "Service").
            </p>
            <p>
              By accessing or using our Service, you agree to be bound by these Terms. If you disagree with any part of these terms, then you may not access the Service.
            </p>
            
            <div class="agreement-box">
              <h3>By using our Service, you confirm that:</h3>
              <ul>
                <li>You are at least 18 years of age or have parental consent</li>
                <li>You have the legal capacity to enter into these Terms</li>
                <li>You will comply with all applicable laws and regulations</li>
                <li>You have read and understood these Terms</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Description of Service -->
        <section id="description" class="terms-section">
          <h2>2. Description of Service</h2>
          <div class="section-content">
            <p>
              Our Service provides [brief description of your service]. We reserve the right to modify, suspend, or discontinue the Service at any time without notice.
            </p>
            
            <div class="service-features">
              <div class="feature-card">
                <div class="feature-icon">
                  <i class="fas fa-rocket"></i>
                </div>
                <h4>Core Features</h4>
                <ul>
                  <li>Feature 1 description</li>
                  <li>Feature 2 description</li>
                  <li>Feature 3 description</li>
                </ul>
              </div>
              
              <div class="feature-card">
                <div class="feature-icon">
                  <i class="fas fa-shield-alt"></i>
                </div>
                <h4>Security & Privacy</h4>
                <ul>
                  <li>Enterprise-grade security</li>
                  <li>GDPR compliant</li>
                  <li>Data encryption</li>
                </ul>
              </div>
              
              <div class="feature-card">
                <div class="feature-icon">
                  <i class="fas fa-headset"></i>
                </div>
                <h4>Support</h4>
                <ul>
                  <li>24/7 customer support</li>
                  <li>Comprehensive documentation</li>
                  <li>Community forums</li>
                </ul>
              </div>
            </div>

            <div class="service-limits">
              <h3>Service Limitations</h3>
              <p>The Service is provided on an "as is" and "as available" basis. We do not guarantee:</p>
              <ul>
                <li>Uninterrupted or error-free operation</li>
                <li>Compatibility with all devices or browsers</li>
                <li>Availability of specific features at all times</li>
                <li>Protection against all security threats</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- User Accounts -->
        <section id="accounts" class="terms-section">
          <h2>3. User Accounts</h2>
          <div class="section-content">
            <h3>Account Creation</h3>
            <p>To access certain features of our Service, you must create an account. When creating an account, you must:</p>
            <ul>
              <li>Provide accurate and complete information</li>
              <li>Keep your account information up to date</li>
              <li>Choose a strong password and keep it secure</li>
              <li>Not share your account credentials with others</li>
            </ul>

            <h3>Account Responsibilities</h3>
            <p>You are solely responsible for all activities that occur under your account. You agree to:</p>
            <ul>
              <li>Notify us immediately of any unauthorized use</li>
              <li>Take reasonable steps to secure your account</li>
              <li>Accept responsibility for all account activities</li>
              <li>Comply with these Terms at all times</li>
            </ul>

            <div class="account-types">
              <h3>Account Types</h3>
              <div class="account-grid">
                <div class="account-card">
                  <h4>Free Account</h4>
                  <ul>
                    <li>Limited features</li>
                    <li>Basic support</li>
                    <li>Community access</li>
                  </ul>
                </div>
                <div class="account-card">
                  <h4>Premium Account</h4>
                  <ul>
                    <li>All features</li>
                    <li>Priority support</li>
                    <li>Advanced tools</li>
                  </ul>
                </div>
                <div class="account-card">
                  <h4>Enterprise Account</h4>
                  <ul>
                    <li>Custom features</li>
                    <li>Dedicated support</li>
                    <li>SLA guarantee</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- User Conduct -->
        <section id="conduct" class="terms-section">
          <h2>4. User Conduct</h2>
          <div class="section-content">
            <h3>Acceptable Use</h3>
            <p>You agree to use our Service only for lawful purposes and in accordance with these Terms. You may not:</p>
            
            <div class="conduct-grid">
              <div class="conduct-card prohibited">
                <div class="conduct-icon">
                  <i class="fas fa-ban"></i>
                </div>
                <h4>Prohibited Activities</h4>
                <ul>
                  <li>Violate any applicable laws</li>
                  <li>Infringe on intellectual property rights</li>
                  <li>Transmit harmful or offensive content</li>
                  <li>Engage in harassment or abuse</li>
                  <li>Spread malware or viruses</li>
                  <li>Attempt to gain unauthorized access</li>
                </ul>
              </div>
              
              <div class="conduct-card restricted">
                <div class="conduct-icon">
                  <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h4>Restricted Activities</h4>
                <ul>
                  <li>Commercial use without permission</li>
                  <li>Reverse engineering our Service</li>
                  <li>Automated access or scraping</li>
                  <li>Interfering with Service operation</li>
                  <li>Competing with our Service</li>
                  <li>Spam or unsolicited communications</li>
                </ul>
              </div>
            </div>

            <div class="consequences">
              <h3>Consequences of Violation</h3>
              <p>We reserve the right to:</p>
              <ul>
                <li>Issue warnings for minor violations</li>
                <li>Suspend or terminate accounts</li>
                <li>Remove offending content</li>
                <li>Report violations to authorities</li>
                <li>Pursue legal remedies</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Intellectual Property -->
        <section id="intellectual-property" class="terms-section">
          <h2>5. Intellectual Property</h2>
          <div class="section-content">
            <h3>Our Intellectual Property</h3>
            <p>The Service and its original content, features, and functionality are owned by us and are protected by international copyright, trademark, and other intellectual property laws.</p>
            
            <div class="ip-categories">
              <div class="ip-card">
                <div class="ip-icon">
                  <i class="fas fa-copyright"></i>
                </div>
                <h4>Copyright</h4>
                <p>All text, graphics, logos, and software are protected by copyright</p>
              </div>
              
              <div class="ip-card">
                <div class="ip-icon">
                  <i class="fas fa-trademark"></i>
                </div>
                <h4>Trademarks</h4>
                <p>Our company name, logos, and product names are trademarks</p>
              </div>
              
              <div class="ip-card">
                <div class="ip-icon">
                  <i class="fas fa-patent"></i>
                </div>
                <h4>Patents</h4>
                <p>Certain technologies and processes are protected by patents</p>
              </div>
            </div>

            <h3>User-Generated Content</h3>
            <p>You retain ownership of content you create or upload to our Service. However, you grant us a license to use your content as described below:</p>
            
            <div class="license-box">
              <h4>License Grant</h4>
              <p>By posting content, you grant us a worldwide, non-exclusive, royalty-free license to:</p>
              <ul>
                <li>Use, reproduce, and display your content</li>
                <li>Modify and adapt your content for Service improvement</li>
                <li>Distribute your content as necessary for Service operation</li>
                <li>Use your content in marketing materials (with consent)</li>
              </ul>
            </div>

            <div class="user-rights">
              <h4>Your Rights</h4>
              <p>You retain the right to:</p>
              <ul>
                <li>Access and download your content</li>
                <li>Delete your content at any time</li>
                <li>Request removal of infringing content</li>
                <li>Control privacy settings for your content</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Privacy and Data -->
        <section id="privacy" class="terms-section">
          <h2>6. Privacy and Data Protection</h2>
          <div class="section-content">
            <p>
              Your privacy is important to us. Our collection and use of personal information is governed by our Privacy Policy, which is incorporated into these Terms by reference.
            </p>
            
            <div class="privacy-highlights">
              <div class="privacy-card">
                <div class="privacy-icon">
                  <i class="fas fa-eye"></i>
                </div>
                <h4>Transparency</h4>
                <p>We clearly explain what data we collect and why</p>
              </div>
              
              <div class="privacy-card">
                <div class="privacy-icon">
                  <i class="fas fa-user-control"></i>
                </div>
                <h4>Control</h4>
                <p>You have control over your personal information</p>
              </div>
              
              <div class="privacy-card">
                <div class="privacy-icon">
                  <i class="fas fa-shield-alt"></i>
                </div>
                <h4>Security</h4>
                <p>We protect your data with industry-standard security</p>
              </div>
            </div>

            <div class="data-usage">
              <h3>Data Usage</h3>
              <p>We use your data to:</p>
              <ul>
                <li>Provide and maintain our Service</li>
                <li>Improve and personalize your experience</li>
                <li>Communicate with you about our Service</li>
                <li>Analyze usage patterns for improvements</li>
                <li>Ensure security and prevent fraud</li>
              </ul>
            </div>

            <div class="compliance-info">
              <h3>Legal Compliance</h3>
              <p>We comply with applicable data protection laws including:</p>
              <ul>
                <li>GDPR (General Data Protection Regulation)</li>
                <li>CCPA (California Consumer Privacy Act)</li>
                <li>Other regional privacy regulations</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Payment Terms -->
        <section id="payment" class="terms-section">
          <h2>7. Payment Terms</h2>
          <div class="section-content">
            <h3>Paid Services</h3>
            <p>Some features of our Service may require payment. By subscribing to paid services, you agree to:</p>
            
            <div class="payment-grid">
              <div class="payment-card">
                <div class="payment-icon">
                  <i class="fas fa-credit-card"></i>
                </div>
                <h4>Payment Methods</h4>
                <ul>
                  <li>Credit/Debit cards</li>
                  <li>PayPal</li>
                  <li>Bank transfers</li>
                  <li>Cryptocurrency (select plans)</li>
                </ul>
              </div>
              
              <div class="payment-card">
                <div class="payment-icon">
                  <i class="fas fa-sync"></i>
                </div>
                <h4>Billing Cycle</h4>
                <ul>
                  <li>Monthly subscriptions</li>
                  <li>Annual subscriptions (discounted)</li>
                  <li>Custom enterprise billing</li>
                </ul>
              </div>
              
              <div class="payment-card">
                <div class="payment-icon">
                  <i class="fas fa-undo"></i>
                </div>
                <h4>Refund Policy</h4>
                <ul>
                  <li>30-day money-back guarantee</li>
                  <li>Pro-rated refunds for annual plans</li>
                  <li>No refunds for used services</li>
                </ul>
              </div>
            </div>

            <div class="billing-terms">
              <h3>Billing Terms</h3>
              <ul>
                <li>Payments are processed in advance</li>
                <li>Prices are subject to change with notice</li>
                <li>Taxes may apply based on your location</li>
                <li>Failed payments may result in service suspension</li>
                <li>Auto-renewal can be disabled at any time</li>
              </ul>
            </div>

            <div class="disclaimer-box">
              <h3>Important Disclaimer</h3>
              <p>We use third-party payment processors and are not responsible for their security or reliability. Please review their terms and conditions.</p>
            </div>
          </div>
        </section>

        <!-- Termination -->
        <section id="termination" class="terms-section">
          <h2>8. Termination</h2>
          <div class="section-content">
            <h3>Termination by You</h3>
            <p>You may terminate your account at any time by:</p>
            <ul>
              <li>Using the account deletion feature in settings</li>
              <li>Contacting our support team</li>
              <li>Cancelling your subscription (if applicable)</li>
            </ul>

            <h3>Termination by Us</h3>
            <p>We may terminate or suspend your account immediately if you:</p>
            <ul>
              <li>Violate these Terms of Service</li>
              <li>Engage in fraudulent or illegal activities</li>
              <li>Compromise the security of our Service</li>
              <li>Fail to pay for services when due</li>
            </ul>

            <div class="termination-effects">
              <h3>Effects of Termination</h3>
              <p>Upon termination:</p>
              <ul>
                <li>Your right to use the Service ends immediately</li>
                <li>Your account and data may be deleted</li>
                <li>You may lose access to purchased services</li>
                <li>We may retain certain information as required by law</li>
              </ul>
            </div>

            <div class="survival-box">
              <h3>Survival</h3>
              <p>The following sections survive termination:</p>
              <ul>
                <li>Intellectual Property Rights</li>
                <li>Disclaimer of Warranties</li>
                <li>Limitation of Liability</li>
                <li>Indemnification</li>
                <li>Governing Law</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Disclaimers -->
        <section id="disclaimers" class="terms-section">
          <h2>9. Disclaimers</h2>
          <div class="section-content">
            <div class="disclaimer-box">
              <h3>Service Disclaimer</h3>
              <p>Our Service is provided on an "AS IS" and "AS AVAILABLE" basis. We make no representations or warranties of any kind, express or implied, including but not limited to:</p>
              <ul>
                <li>Warranty of merchantability</li>
                <li>Warranty of fitness for a particular purpose</li>
                <li>Warranty of non-infringement</li>
                <li>Warranty of title</li>
              </ul>
            </div>

            <div class="disclaimer-box">
              <h3>Limitation of Liability</h3>
              <p>To the maximum extent permitted by law, we shall not be liable for:</p>
              <ul>
                <li>Any indirect, incidental, or consequential damages</li>
                <li>Loss of profits, data, or business opportunities</li>
                <li>Damages arising from service interruption</li>
                <li>Damages exceeding the amount you paid for the service</li>
              </ul>
            </div>

            <div class="disclaimer-box">
              <h3>Third-Party Services</h3>
              <p>Our Service may contain links to third-party websites or services. We are not responsible for the content, privacy policies, or practices of third-party sites.</p>
            </div>
          </div>
        </section>

        <!-- Governing Law -->
        <section id="governing-law" class="terms-section">
          <h2>10. Governing Law and Dispute Resolution</h2>
          <div class="section-content">
            <h3>Governing Law</h3>
            <p>These Terms shall be governed by and construed in accordance with the laws of [Your Jurisdiction], without regard to its conflict of law provisions.</p>

            <h3>Dispute Resolution</h3>
            <p>If you have any dispute with us, you agree to first attempt to resolve it informally by contacting us at [contact email].</p>
            
            <div class="resolution-process">
              <div class="process-step">
                <div class="step-number">1</div>
                <h4>Informal Resolution</h4>
                <p>Contact us to resolve the dispute informally</p>
              </div>
              
              <div class="process-step">
                <div class="step-number">2</div>
                <h4>Mediation</h4>
                <p>If informal resolution fails, we agree to mediation</p>
              </div>
              
              <div class="process-step">
                <div class="step-number">3</div>
                <h4>Arbitration</h4>
                <p>Binding arbitration as final resolution method</p>
              </div>
            </div>

            <div class="jurisdiction-info">
              <h3>Jurisdiction</h3>
              <p>Any legal action shall be brought in the courts of [Your City, State]. You consent to the personal jurisdiction of these courts.</p>
            </div>

            <div class="class-action-waiver">
              <h3>Class Action Waiver</h3>
              <p>You agree to resolve disputes individually and waive any right to participate in class actions or class-wide arbitration.</p>
            </div>
          </div>
        </section>

        <!-- Changes to Terms -->
        <section id="changes" class="terms-section">
          <h2>11. Changes to These Terms</h2>
          <div class="section-content">
            <p>We reserve the right to modify these Terms at any time. Changes will be effective immediately upon posting.</p>
            
            <div class="change-process">
              <h3>How We Notify Changes</h3>
              <ul>
                <li>Email notification for significant changes</li>
                <li>Website banner notice for major updates</li>
                <li>In-app notifications for active users</li>
                <li>Updated "Last Modified" date</li>
              </ul>
            </div>

            <div class="change-types">
              <h3>Types of Changes</h3>
              <div class="change-grid">
                <div class="change-card">
                  <h4>Minor Changes</h4>
                  <p>Clarifications, typos, or minor updates</p>
                </div>
                <div class="change-card">
                  <h4>Significant Changes</h4>
                  <p>New features, pricing, or major policy updates</p>
                </div>
                <div class="change-card">
                  <h4>Material Changes</h4>
                  <p>Changes affecting your rights or obligations</p>
                </div>
              </div>
            </div>

            <div class="continuation-box">
              <h3>Continued Use</h3>
              <p>Your continued use of the Service after changes constitutes acceptance of the modified Terms. If you disagree with any changes, you must terminate your account.</p>
            </div>
          </div>
        </section>

        <!-- Contact Information -->
        <section id="contact" class="terms-section">
          <h2>12. Contact Information</h2>
          <div class="section-content">
            <p>If you have any questions about these Terms of Service, please contact us:</p>
            
            <div class="contact-methods">
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-envelope"></i>
                </div>
                <h4>Email</h4>
                <a href="mailto:legal@company.com">legal@company.com</a>
              </div>
              
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-phone"></i>
                </div>
                <h4>Phone</h4>
                <a href="tel:+1-800-LEGAL">+1-800-LEGAL</a>
              </div>
              
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-map-marker-alt"></i>
                </div>
                <h4>Mail</h4>
                <p>Legal Department<br>123 Legal Street<br>San Francisco, CA 94105</p>
              </div>
              
              <div class="contact-card">
                <div class="contact-icon">
                  <i class="fas fa-globe"></i>
                </div>
                <h4>Website</h4>
                <a href="/contact">Contact Form</a>
              </div>
            </div>

            <div class="response-info">
              <h3>Response Times</h3>
              <div class="time-grid">
                <div class="time-item">
                  <h4>General Inquiries</h4>
                  <p>Within 3-5 business days</p>
                </div>
                <div class="time-item">
                  <h4>Legal Matters</h4>
                  <p>Within 7-10 business days</p>
                </div>
                <div class="time-item">
                  <h4>Urgent Issues</h4>
                  <p>Within 24-48 hours</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Reactive state
const activeSection = ref('agreement')
const lastUpdated = ref('2024-01-15T00:00:00Z')

// Terms sections
const sections = ref([
  { id: 'agreement', title: 'Agreement to Terms' },
  { id: 'description', title: 'Description of Service' },
  { id: 'accounts', title: 'User Accounts' },
  { id: 'conduct', title: 'User Conduct' },
  { id: 'intellectual-property', title: 'Intellectual Property' },
  { id: 'privacy', title: 'Privacy and Data' },
  { id: 'payment', title: 'Payment Terms' },
  { id: 'termination', title: 'Termination' },
  { id: 'disclaimers', title: 'Disclaimers' },
  { id: 'governing-law', title: 'Governing Law' },
  { id: 'changes', title: 'Changes to Terms' },
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

// Intersection Observer for active section tracking
onMounted(() => {
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
    const sections = document.querySelectorAll('.terms-section')
    sections.forEach(section => observer.observe(section))
  }, 100)
})
</script>

<style scoped>
.terms-of-service {
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

.terms-container {
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

.terms-content {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 3rem;
}

.terms-section {
  margin-bottom: 4rem;
}

.terms-section:last-child {
  margin-bottom: 0;
}

.terms-section h2 {
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

.agreement-box,
.disclaimer-box,
.license-box,
.user-rights,
.termination-effects,
.survival-box,
.continuation-box {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 2rem 0;
}

.agreement-box {
  border-left: 4px solid var(--info-color);
}

.disclaimer-box {
  border-left: 4px solid var(--warning-color);
}

.license-box {
  border-left: 4px solid var(--success-color);
}

.survival-box {
  border-left: 4px solid var(--primary-color);
}

.service-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.feature-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.feature-icon {
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

.feature-card h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.feature-card ul {
  text-align: left;
}

.service-limits {
  margin: 3rem 0;
}

.account-types {
  margin: 3rem 0;
}

.account-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.account-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.account-card h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.conduct-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.conduct-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.conduct-card.prohibited {
  border-left: 4px solid var(--danger-color);
}

.conduct-card.restricted {
  border-left: 4px solid var(--warning-color);
}

.conduct-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.conduct-card.prohibited .conduct-icon {
  background: var(--danger-color);
}

.conduct-card.restricted .conduct-icon {
  background: var(--warning-color);
}

.consequences {
  margin: 3rem 0;
}

.ip-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.ip-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.ip-icon {
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

.ip-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.user-rights {
  margin: 2rem 0;
}

.privacy-highlights {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.privacy-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.privacy-icon {
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

.privacy-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.data-usage,
.compliance-info {
  margin: 2rem 0;
}

.payment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.payment-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.payment-icon {
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

.payment-card h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.billing-terms {
  margin: 2rem 0;
}

.resolution-process {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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

.jurisdiction-info,
.class-action-waiver {
  margin: 2rem 0;
}

.change-process {
  margin: 2rem 0;
}

.change-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.change-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.change-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
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

.response-info {
  margin: 3rem 0;
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

@media (max-width: 768px) {
  .terms-of-service {
    padding: 1rem;
  }
  
  .terms-container {
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
  
  .terms-content {
    padding: 2rem;
  }
  
  .service-features,
  .account-grid,
  .conduct-grid,
  .ip-categories,
  .privacy-highlights,
  .payment-grid,
  .resolution-process,
  .change-grid,
  .contact-methods,
  .time-grid {
    grid-template-columns: 1fr;
  }
}
</style>
