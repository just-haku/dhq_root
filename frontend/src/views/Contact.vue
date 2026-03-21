<template>
  <div class="contact">
    <div class="page-header">
      <h1>Contact Us</h1>
      <p>Get in touch with our team for any questions or support</p>
    </div>

    <div class="contact-container">
      <!-- Contact Methods -->
      <section class="contact-methods">
        <div class="methods-grid">
          <div class="method-card">
            <div class="method-icon">
              <i class="fas fa-envelope"></i>
            </div>
            <h3>Email Us</h3>
            <p>Send us an email and we'll respond within 24 hours</p>
            <div class="method-details">
              <div class="detail-item">
                <label>General Inquiries:</label>
                <a href="mailto:info@company.com">info@company.com</a>
              </div>
              <div class="detail-item">
                <label>Support:</label>
                <a href="mailto:support@company.com">support@company.com</a>
              </div>
              <div class="detail-item">
                <label>Sales:</label>
                <a href="mailto:sales@company.com">sales@company.com</a>
              </div>
            </div>
          </div>

          <div class="method-card">
            <div class="method-icon">
              <i class="fas fa-phone"></i>
            </div>
            <h3>Call Us</h3>
            <p>Speak directly with our support team</p>
            <div class="method-details">
              <div class="detail-item">
                <label>Main Office:</label>
                <a href="tel:+1-800-555-0100">+1 (800) 555-0100</a>
              </div>
              <div class="detail-item">
                <label>Support Hotline:</label>
                <a href="tel:+1-800-555-0200">+1 (800) 555-0200</a>
              </div>
              <div class="detail-item">
                <label>Hours:</label>
                <span>Mon-Fri 9AM-6PM EST</span>
              </div>
            </div>
          </div>

          <div class="method-card">
            <div class="method-icon">
              <i class="fas fa-comments"></i>
            </div>
            <h3>Live Chat</h3>
            <p>Get instant help from our support team</p>
            <div class="method-details">
              <div class="detail-item">
                <label>Availability:</label>
                <span>24/7 for premium customers</span>
              </div>
              <div class="detail-item">
                <label>Response Time:</label>
                <span>Under 2 minutes</span>
              </div>
              <button class="chat-btn" @click="startLiveChat">
                <i class="fas fa-comment-dots"></i>
                Start Chat
              </button>
            </div>
          </div>

          <div class="method-card">
            <div class="method-icon">
              <i class="fas fa-map-marker-alt"></i>
            </div>
            <h3>Visit Us</h3>
            <p>Stop by our headquarters</p>
            <div class="method-details">
              <div class="detail-item">
                <label>Address:</label>
                <span>123 Tech Street, San Francisco, CA 94105</span>
              </div>
              <div class="detail-item">
                <label>Office Hours:</label>
                <span>Mon-Fri 9AM-6PM EST</span>
              </div>
              <button class="directions-btn" @click="getDirections">
                <i class="fas fa-directions"></i>
                Get Directions
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Contact Form -->
      <section class="contact-form-section">
        <div class="section-header">
          <h2>Send Us a Message</h2>
          <p>Fill out the form below and we'll get back to you as soon as possible</p>
        </div>

        <form @submit.prevent="submitForm" class="contact-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="firstName">First Name *</label>
              <input 
                id="firstName"
                v-model="form.firstName"
                type="text"
                required
                :class="{ 'error': errors.firstName }"
                placeholder="Enter your first name"
              />
              <span class="error-message" v-if="errors.firstName">{{ errors.firstName }}</span>
            </div>

            <div class="form-group">
              <label for="lastName">Last Name *</label>
              <input 
                id="lastName"
                v-model="form.lastName"
                type="text"
                required
                :class="{ 'error': errors.lastName }"
                placeholder="Enter your last name"
              />
              <span class="error-message" v-if="errors.lastName">{{ errors.lastName }}</span>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label for="email">Email Address *</label>
              <input 
                id="email"
                v-model="form.email"
                type="email"
                required
                :class="{ 'error': errors.email }"
                placeholder="your.email@example.com"
              />
              <span class="error-message" v-if="errors.email">{{ errors.email }}</span>
            </div>

            <div class="form-group">
              <label for="phone">Phone Number</label>
              <input 
                id="phone"
                v-model="form.phone"
                type="tel"
                :class="{ 'error': errors.phone }"
                placeholder="+1 (555) 555-0100"
              />
              <span class="error-message" v-if="errors.phone">{{ errors.phone }}</span>
            </div>
          </div>

          <div class="form-group">
            <label for="company">Company</label>
            <input 
              id="company"
              v-model="form.company"
              type="text"
              placeholder="Your company name"
            />
          </div>

          <div class="form-group">
            <label for="subject">Subject *</label>
            <select 
              id="subject"
              v-model="form.subject"
              required
              :class="{ 'error': errors.subject }"
            >
              <option value="">Select a subject</option>
              <option value="general">General Inquiry</option>
              <option value="support">Technical Support</option>
              <option value="sales">Sales Question</option>
              <option value="partnership">Partnership Opportunity</option>
              <option value="feedback">Feedback</option>
              <option value="other">Other</option>
            </select>
            <span class="error-message" v-if="errors.subject">{{ errors.subject }}</span>
          </div>

          <div class="form-group">
            <label for="message">Message *</label>
            <textarea 
              id="message"
              v-model="form.message"
              required
              :class="{ 'error': errors.message }"
              placeholder="Tell us how we can help you..."
              rows="6"
            ></textarea>
            <span class="error-message" v-if="errors.message">{{ errors.message }}</span>
          </div>

          <div class="form-group">
            <label for="priority">Priority</label>
            <select id="priority" v-model="form.priority">
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="form.newsletter"
                id="newsletter"
              />
              <span class="checkmark"></span>
              Subscribe to our newsletter for updates and tips
            </label>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="resetForm">
              <i class="fas fa-undo"></i>
              Reset Form
            </button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              <i class="fas fa-paper-plane" v-if="!isSubmitting"></i>
              <i class="fas fa-spinner fa-spin" v-else></i>
              {{ isSubmitting ? 'Sending...' : 'Send Message' }}
            </button>
          </div>
        </form>
      </section>

      <!-- FAQ Section -->
      <section class="faq-section">
        <div class="section-header">
          <h2>Frequently Asked Questions</h2>
          <p>Find quick answers to common questions</p>
        </div>

        <div class="faq-grid">
          <div 
            v-for="faq in faqs" 
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

        <div class="faq-more">
          <p>Can't find what you're looking for?</p>
          <button class="btn-link" @click="viewMoreFaq">
            View All FAQs
            <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </section>

      <!-- Office Locations -->
      <section class="offices-section">
        <div class="section-header">
          <h2>Our Offices</h2>
          <p>Visit us at one of our global locations</p>
        </div>

        <div class="offices-grid">
          <div 
            v-for="office in offices" 
            :key="office.id"
            class="office-card"
          >
            <div class="office-image">
              <img :src="office.image" :alt="office.city" />
            </div>
            <div class="office-info">
              <h3>{{ office.city }}</h3>
              <p class="office-address">{{ office.address }}</p>
              <div class="office-details">
                <div class="detail-item">
                  <i class="fas fa-phone"></i>
                  <span>{{ office.phone }}</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-envelope"></i>
                  <span>{{ office.email }}</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-clock"></i>
                  <span>{{ office.hours }}</span>
                </div>
              </div>
              <div class="office-actions">
                <button class="btn-outline" @click="getOfficeDirections(office)">
                  <i class="fas fa-directions"></i>
                  Directions
                </button>
                <button class="btn-outline" @click="scheduleOfficeVisit(office)">
                  <i class="fas fa-calendar"></i>
                  Schedule Visit
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Support Resources -->
      <section class="resources-section">
        <div class="section-header">
          <h2>Support Resources</h2>
          <p>Self-service options and helpful resources</p>
        </div>

        <div class="resources-grid">
          <div 
            v-for="resource in supportResources" 
            :key="resource.id"
            class="resource-card"
            @click="navigateToResource(resource)"
          >
            <div class="resource-icon">
              <i :class="resource.icon"></i>
            </div>
            <h3>{{ resource.title }}</h3>
            <p>{{ resource.description }}</p>
            <div class="resource-link">
              <span>Learn More</span>
              <i class="fas fa-arrow-right"></i>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { showSuccess, showError, showConfirm } from '@/utils/notification'

// Reactive state
const isSubmitting = ref(false)
const faqs = ref([
  {
    id: 1,
    question: 'What are your business hours?',
    answer: 'Our main office is open Monday through Friday, 9AM to 6PM EST. Support is available 24/7 for premium customers.',
    isOpen: false
  },
  {
    id: 2,
    question: 'How quickly will I receive a response?',
    answer: 'We respond to all inquiries within 24 hours during business days. Premium customers receive priority support with faster response times.',
    isOpen: false
  },
  {
    id: 3,
    question: 'Do you offer technical support?',
    answer: 'Yes, we offer comprehensive technical support through multiple channels including phone, email, and live chat. Our support team is highly trained and ready to help.',
    isOpen: false
  },
  {
    id: 4,
    question: 'Can I schedule a demo?',
    answer: 'Absolutely! We offer personalized demos for all our products and services. Contact our sales team to schedule a time that works for you.',
    isOpen: false
  },
  {
    id: 5,
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit cards, PayPal, bank transfers, and cryptocurrency for enterprise customers. Payment plans are available for qualified organizations.',
    isOpen: false
  }
])

// Contact form
const form = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  company: '',
  subject: '',
  message: '',
  priority: 'normal',
  newsletter: false
})

// Form errors
const errors = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  subject: '',
  message: ''
})

// Office locations
const offices = ref([
  {
    id: 1,
    city: 'San Francisco',
    address: '123 Tech Street, San Francisco, CA 94105',
    phone: '+1 (415) 555-0100',
    email: 'sf@company.com',
    hours: 'Mon-Fri 9AM-6PM EST',
    image: '/api/placeholder/300x200'
  },
  {
    id: 2,
    city: 'New York',
    address: '456 Innovation Ave, New York, NY 10001',
    phone: '+1 (212) 555-0200',
    email: 'ny@company.com',
    hours: 'Mon-Fri 9AM-6PM EST',
    image: '/api/placeholder/300x200'
  },
  {
    id: 3,
    city: 'London',
    address: '789 Digital Road, London, UK EC1A 1BB',
    phone: '+44 20 5555 0300',
    email: 'london@company.com',
    hours: 'Mon-Fri 9AM-6PM GMT',
    image: '/api/placeholder/300x200'
  }
])

// Support resources
const supportResources = ref([
  {
    id: 1,
    title: 'Help Center',
    description: 'Comprehensive guides and tutorials',
    icon: 'fas fa-book',
    url: '/help'
  },
  {
    id: 2,
    title: 'Documentation',
    description: 'Technical documentation and API references',
    icon: 'fas fa-code',
    url: '/docs'
  },
  {
    id: 3,
    title: 'Community Forum',
    description: 'Connect with other users and experts',
    icon: 'fas fa-users',
    url: '/community'
  },
  {
    id: 4,
    title: 'Video Tutorials',
    description: 'Step-by-step video guides',
    icon: 'fas fa-video',
    url: '/tutorials'
  },
  {
    id: 5,
    title: 'Status Page',
    description: 'Real-time system status and updates',
    icon: 'fas fa-heartbeat',
    url: '/status'
  },
  {
    id: 6,
    title: 'Developer Portal',
    description: 'Resources for developers and integrators',
    icon: 'fas fa-laptop-code',
    url: '/developers'
  }
])

// Methods
const validateForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })

  let isValid = true

  // Validate required fields
  if (!form.firstName.trim()) {
    errors.firstName = 'First name is required'
    isValid = false
  }

  if (!form.lastName.trim()) {
    errors.lastName = 'Last name is required'
    isValid = false
  }

  if (!form.email.trim()) {
    errors.email = 'Email address is required'
    isValid = false
  } else if (!isValidEmail(form.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  if (!form.subject) {
    errors.subject = 'Please select a subject'
    isValid = false
  }

  if (!form.message.trim()) {
    errors.message = 'Message is required'
    isValid = false
  }

  return isValid
}

const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

const submitForm = async () => {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    showSuccess('Message sent successfully! We\'ll respond within 24 hours.')
    resetForm()
  } catch (error) {
    console.error('Error submitting form:', error)
    showError('Failed to send message. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  Object.assign(form, {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    company: '',
    subject: '',
    message: '',
    priority: 'normal',
    newsletter: false
  })

  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
}

const toggleFaq = (faqId) => {
  const faq = faqs.value.find(f => f.id === faqId)
  if (faq) {
    faq.isOpen = !faq.isOpen
  }
}

const startLiveChat = () => {
  showSuccess('Opening live chat...')
  // In a real app, this would open the chat widget
}

const getDirections = () => {
  showSuccess('Opening directions to our office...')
  // In a real app, this would open Google Maps or similar
}

const getOfficeDirections = (office) => {
  showSuccess(`Getting directions to ${office.city} office...`)
  // In a real app, this would open directions for specific office
}

const scheduleOfficeVisit = (office) => {
  showSuccess(`Opening calendar for ${office.city} office visit...`)
  // In a real app, this would open a scheduling tool
}

const viewMoreFaq = () => {
  showSuccess('Navigating to full FAQ page...')
  // In a real app, this would navigate to the FAQ page
}

const navigateToResource = (resource) => {
  showSuccess(`Navigating to ${resource.title}...`)
  // In a real app, this would navigate to the resource
}

// Lifecycle
onMounted(() => {
  // Any initialization logic
})
</script>

<style scoped>
.contact {
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

.contact-container {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.contact-methods,
.contact-form-section,
.faq-section,
.offices-section,
.resources-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 3rem;
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

.methods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.method-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.method-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.method-icon {
  width: 80px;
  height: 80px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  margin: 0 auto 1.5rem;
}

.method-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.method-card p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.method-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.detail-item a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.detail-item a:hover {
  text-decoration: underline;
}

.detail-item span {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.chat-btn,
.directions-btn {
  padding: 0.75rem 1.5rem;
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
  margin-top: 1rem;
}

.chat-btn:hover,
.directions-btn:hover {
  background: var(--primary-hover);
}

.contact-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
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
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: var(--danger-color);
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.error-message {
  color: var(--danger-color);
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-weight: 500;
  color: var(--text-primary);
}

.checkbox-label input[type="checkbox"] {
  width: 20px;
  height: 20px;
  accent-color: var(--primary-color);
}

.checkmark {
  position: relative;
  padding-left: 1.5rem;
}

.checkmark::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  border: 2px solid var(--glass-border);
  border-radius: 4px;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::before {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  left: 2px;
  top: 50%;
  transform: translateY(-50%);
  color: white;
  font-weight: bold;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary,
.btn-outline,
.btn-link {
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

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.7;
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

.btn-outline {
  background: transparent;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
}

.btn-outline:hover {
  background: var(--primary-color);
  color: white;
}

.btn-link {
  background: transparent;
  color: var(--primary-color);
  border: none;
  text-decoration: none;
  font-weight: 500;
}

.btn-link:hover {
  text-decoration: underline;
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

.faq-more {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--glass-border);
}

.faq-more p {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.offices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.office-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.office-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.office-image {
  height: 200px;
  overflow: hidden;
}

.office-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.office-info {
  padding: 1.5rem;
}

.office-info h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.office-address {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.office-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.office-actions {
  display: flex;
  gap: 1rem;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.resource-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.resource-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.resource-icon {
  width: 60px;
  height: 60px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1.5rem;
}

.resource-card h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.resource-card p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.resource-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--primary-color);
  font-weight: 500;
}

.resource-link i {
  transition: transform 0.3s ease;
}

.resource-card:hover .resource-link i {
  transform: translateX(5px);
}

@media (max-width: 768px) {
  .contact {
    padding: 1rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .methods-grid,
  .offices-grid,
  .resources-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .office-actions {
    flex-direction: column;
  }
}
</style>
