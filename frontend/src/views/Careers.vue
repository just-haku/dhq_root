<template>
  <div class="careers">
    <div class="page-header">
      <h1>Join Our Team</h1>
      <p>Build your career with us and make a difference</p>
    </div>

    <div class="careers-container">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-content">
          <div class="hero-text">
            <h2>{{ companyData.name }} Careers</h2>
            <p class="hero-tagline">{{ companyData.careerTagline }}</p>
            <p class="hero-description">{{ companyData.careerDescription }}</p>
            <div class="hero-stats">
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.openPositions }}</div>
                <div class="stat-label">Open Positions</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.teamGrowth }}%</div>
                <div class="stat-label">Team Growth</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.employeeSatisfaction }}%</div>
                <div class="stat-label">Employee Satisfaction</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.globalOffices }}</div>
                <div class="stat-label">Global Offices</div>
              </div>
            </div>
          </div>
          <div class="hero-image">
            <div class="image-placeholder">
              <i class="fas fa-users"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- Why Join Us -->
      <section class="why-join-section">
        <div class="section-header">
          <h2>Why Join {{ companyData.name }}?</h2>
          <p>Discover what makes us a great place to work</p>
        </div>
        <div class="benefits-grid">
          <div 
            v-for="benefit in benefits" 
            :key="benefit.id"
            class="benefit-card"
          >
            <div class="benefit-icon">
              <i :class="benefit.icon"></i>
            </div>
            <h3>{{ benefit.title }}</h3>
            <p>{{ benefit.description }}</p>
          </div>
        </div>
      </section>

      <!-- Open Positions -->
      <section class="positions-section">
        <div class="section-header">
          <h2>Open Positions</h2>
          <div class="header-actions">
            <div class="filter-dropdown">
              <select v-model="positionFilter" @change="filterPositions">
                <option value="">All Departments</option>
                <option value="engineering">Engineering</option>
                <option value="design">Design</option>
                <option value="marketing">Marketing</option>
                <option value="sales">Sales</option>
                <option value="hr">Human Resources</option>
                <option value="finance">Finance</option>
                <option value="operations">Operations</option>
              </select>
            </div>
            <div class="filter-dropdown">
              <select v-model="locationFilter" @change="filterPositions">
                <option value="">All Locations</option>
                <option value="san-francisco">San Francisco</option>
                <option value="new-york">New York</option>
                <option value="london">London</option>
                <option value="remote">Remote</option>
              </select>
            </div>
            <div class="filter-dropdown">
              <select v-model="typeFilter" @change="filterPositions">
                <option value="">All Types</option>
                <option value="full-time">Full Time</option>
                <option value="part-time">Part Time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading positions...</p>
        </div>

        <div v-else-if="filteredPositions.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-briefcase"></i>
          </div>
          <h3>No positions found</h3>
          <p>{{ getEmptyMessage() }}</p>
        </div>

        <div v-else class="positions-grid">
          <div 
            v-for="position in paginatedPositions" 
            :key="position.id"
            class="position-card"
            @click="viewPosition(position)"
          >
            <div class="position-header">
              <div class="position-info">
                <h3>{{ position.title }}</h3>
                <div class="position-meta">
                  <span class="department">{{ position.department }}</span>
                  <span class="location">{{ position.location }}</span>
                  <span :class="['type', position.type]">{{ formatType(position.type) }}</span>
                </div>
              </div>
              <div class="position-actions">
                <button class="action-btn save" @click.stop="savePosition(position)">
                  <i class="fas fa-bookmark"></i>
                </button>
                <button class="action-btn share" @click.stop="sharePosition(position)">
                  <i class="fas fa-share"></i>
                </button>
              </div>
            </div>
            
            <div class="position-content">
              <p class="position-description">{{ position.description }}</p>
              
              <div class="position-details">
                <div class="detail-item">
                  <label>Experience:</label>
                  <span>{{ position.experience }}</span>
                </div>
                <div class="detail-item">
                  <label>Salary Range:</label>
                  <span>{{ position.salaryRange }}</span>
                </div>
                <div class="detail-item">
                  <label>Posted:</label>
                  <span>{{ formatDate(position.postedDate) }}</span>
                </div>
              </div>
              
              <div class="position-skills">
                <h4>Required Skills:</h4>
                <div class="skills-list">
                  <span 
                    v-for="skill in position.skills" 
                    :key="skill"
                    class="skill-tag"
                  >
                    {{ skill }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="position-footer">
              <button class="apply-btn" @click.stop="applyForPosition(position)">
                <i class="fas fa-paper-plane"></i>
                Apply Now
              </button>
              <div class="position-deadline">
                <span class="deadline-label">Apply by:</span>
                <span class="deadline-date">{{ formatDate(position.deadline) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination" v-if="totalPages > 1">
          <button 
            class="pagination-btn" 
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button 
            class="pagination-btn" 
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </section>

      <!-- Company Culture -->
      <section class="culture-section">
        <div class="section-header">
          <h2>Our Culture</h2>
          <p>What it's like to work at {{ companyData.name }}</p>
        </div>
        <div class="culture-grid">
          <div 
            v-for="value in companyData.culture" 
            :key="value.title"
            class="culture-card"
          >
            <div class="culture-icon">
              <i :class="value.icon"></i>
            </div>
            <h3>{{ value.title }}</h3>
            <p>{{ value.description }}</p>
          </div>
        </div>
      </section>

      <!-- Benefits & Perks -->
      <section class="benefits-section">
        <div class="section-header">
          <h2>Benefits & Perks</h2>
          <p>What we offer our team members</p>
        </div>
        <div class="benefits-categories">
          <div class="benefit-category">
            <div class="category-header">
              <div class="category-icon">
                <i class="fas fa-heart"></i>
              </div>
              <h3>Health & Wellness</h3>
            </div>
            <ul class="benefit-list">
              <li>Comprehensive medical, dental, and vision insurance</li>
              <li>Flexible spending accounts (FSA/HSA)</li>
              <li>Wellness programs and gym memberships</li>
              <li>Mental health support and counseling</li>
              <li>Life and disability insurance</li>
            </ul>
          </div>
          
          <div class="benefit-category">
            <div class="category-header">
              <div class="category-icon">
                <i class="fas fa-dollar-sign"></i>
              </div>
              <h3>Financial Benefits</h3>
            </div>
            <ul class="benefit-list">
              <li>Competitive salary and equity packages</li>
              <li>Performance bonuses and stock options</li>
              <li>401(k) retirement plan with company match</li>
              <li>Financial planning and advisory services</li>
              <li>Transportation and parking benefits</li>
            </ul>
          </div>
          
          <div class="benefit-category">
            <div class="category-header">
              <div class="category-icon">
                <i class="fas fa-calendar-alt"></i>
              </div>
              <h3>Work-Life Balance</h3>
            </div>
            <ul class="benefit-list">
              <li>Flexible work arrangements and remote options</li>
              <li>Generous paid time off and holidays</li>
              <li>Parental leave and family support</li>
              <li>Sabbatical programs for long-term employees</li>
              <li>Flexible scheduling and compressed workweeks</li>
            </ul>
          </div>
          
          <div class="benefit-category">
            <div class="category-header">
              <div class="category-icon">
                <i class="fas fa-graduation-cap"></i>
              </div>
              <h3>Professional Growth</h3>
            </div>
            <ul class="benefit-list">
              <li>Learning and development programs</li>
              <li>Tuition reimbursement and educational assistance</li>
              <li>Conference attendance and professional memberships</li>
              <li>Internal mobility and career advancement</li>
              <li>Mentorship programs and skill workshops</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Interview Process -->
      <section class="interview-section">
        <div class="section-header">
          <h2>Our Interview Process</h2>
          <p>What to expect when you apply</p>
        </div>
        <div class="process-timeline">
          <div 
            v-for="step in interviewProcess" 
            :key="step.id"
            class="process-step"
          >
            <div class="step-marker">
              <div class="step-number">{{ step.id }}</div>
              <div class="step-icon">
                <i :class="step.icon"></i>
              </div>
            </div>
            <div class="step-content">
              <h3>{{ step.title }}</h3>
              <p>{{ step.description }}</p>
              <div class="step-duration">
                <span class="duration-label">Duration:</span>
                <span class="duration-time">{{ step.duration }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Life at Company -->
      <section class="life-section">
        <div class="section-header">
          <h2>Life at {{ companyData.name }}</h2>
          <p>A glimpse into our daily work environment</p>
        </div>
        <div class="life-grid">
          <div class="life-card">
            <div class="life-image">
              <img src="https://via.placeholder.com/400x250" alt="Office Environment" />
            </div>
            <div class="life-content">
              <h3>Modern Workspaces</h3>
              <p>Collaborative, open office spaces designed for creativity and productivity</p>
            </div>
          </div>
          
          <div class="life-card">
            <div class="life-image">
              <img src="https://via.placeholder.com/400x250" alt="Team Events" />
            </div>
            <div class="life-content">
              <h3>Team Events & Activities</h3>
              <p>Regular team building events, happy hours, and company-wide celebrations</p>
            </div>
          </div>
          
          <div class="life-card">
            <div class="life-image">
              <img src="https://via.placeholder.com/400x250" alt="Learning & Development" />
            </div>
            <div class="life-content">
              <h3>Learning & Development</h3>
              <p>Continuous learning opportunities through workshops, courses, and mentorship</p>
            </div>
          </div>
          
          <div class="life-card">
            <div class="life-image">
              <img src="https://via.placeholder.com/400x250" alt="Diversity & Inclusion" />
            </div>
            <div class="life-content">
              <h3>Diversity & Inclusion</h3>
              <p>Committed to building a diverse and inclusive workplace for all</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="cta-section">
        <div class="cta-content">
          <h2>Ready to Join Us?</h2>
          <p>Take the next step in your career journey</p>
          <div class="cta-buttons">
            <button class="cta-btn primary" @click="viewAllPositions">
              <i class="fas fa-briefcase"></i>
              View All Positions
            </button>
            <button class="cta-btn secondary" @click="joinTalentPool">
              <i class="fas fa-users"></i>
              Join Talent Pool
            </button>
            <button class="cta-btn outline" @click="connectWithRecruiter">
              <i class="fab fa-linkedin"></i>
              Connect on LinkedIn
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
const positionFilter = ref('')
const locationFilter = ref('')
const typeFilter = ref('')
const currentPage = ref(1)
const positionsPerPage = ref(9)

// Company data
const companyData = reactive({
  name: 'Digital HQ',
  careerTagline: 'Where Innovation Meets Opportunity',
  careerDescription: 'Join a team of passionate innovators building the future of digital transformation. We offer challenging work, growth opportunities, and a culture that values your unique perspective.',
  stats: {
    openPositions: 15,
    teamGrowth: 25,
    employeeSatisfaction: 92,
    globalOffices: 8
  },
  culture: [
    {
      title: 'Innovation First',
      description: 'We encourage creative thinking and bold ideas that push boundaries',
      icon: 'fas fa-lightbulb'
    },
    {
      title: 'Collaborative Spirit',
      description: 'We believe in the power of teamwork and diverse perspectives',
      icon: 'fas fa-users'
    },
    {
      title: 'Growth Mindset',
      description: 'We invest in your development and celebrate your achievements',
      icon: 'fas fa-chart-line'
    },
    {
      title: 'Work-Life Harmony',
      description: 'We support your well-being both inside and outside of work',
      icon: 'fas fa-balance-scale'
    }
  ]
})

// Interview process
const interviewProcess = ref([
  {
    id: 1,
    title: 'Application Review',
    description: 'Our recruiting team reviews your application and qualifications',
    duration: '1-2 weeks',
    icon: 'fas fa-eye'
  },
  {
    id: 2,
    title: 'Phone Screening',
    description: 'Initial phone conversation to discuss your experience and interests',
    duration: '30 minutes',
    icon: 'fas fa-phone'
  },
  {
    id: 3,
    title: 'Technical Interview',
    description: 'In-depth technical assessment with the hiring team',
    duration: '1-2 hours',
    icon: 'fas fa-laptop-code'
  },
  {
    id: 4,
    title: 'Cultural Fit Interview',
    description: 'Discussion about teamwork, values, and work style preferences',
    duration: '45-60 minutes',
    icon: 'fas fa-comments'
  },
  {
    id: 5,
    title: 'Final Decision',
    description: 'Team evaluation and decision-making process',
    duration: '1 week',
    icon: 'fas fa-check-circle'
  }
])

// Open positions
const positions = ref([
  {
    id: 1,
    title: 'Senior Frontend Developer',
    department: 'Engineering',
    location: 'San Francisco',
    type: 'full-time',
    experience: '5+ years',
    salaryRange: '$120k - $160k',
    description: 'We are looking for an experienced Frontend Developer to join our growing engineering team. You will work on cutting-edge web applications using modern JavaScript frameworks.',
    postedDate: '2024-01-15T00:00:00Z',
    deadline: '2024-02-15T00:00:00Z',
    skills: ['Vue.js', 'React', 'TypeScript', 'CSS', 'Node.js', 'Git']
  },
  {
    id: 2,
    title: 'Product Designer',
    department: 'Design',
    location: 'Remote',
    type: 'full-time',
    experience: '3+ years',
    salaryRange: '$100k - $140k',
    description: 'Join our design team to create beautiful and intuitive user experiences. You will work closely with product managers and engineers.',
    postedDate: '2024-01-10T00:00:00Z',
    deadline: '2024-02-10T00:00:00Z',
    skills: ['UI/UX Design', 'Figma', 'Sketch', 'Prototyping', 'User Research']
  },
  {
    id: 3,
    title: 'Marketing Manager',
    department: 'Marketing',
    location: 'New York',
    type: 'full-time',
    experience: '5+ years',
    salaryRange: '$90k - $130k',
    description: 'Lead our marketing initiatives and drive growth through innovative campaigns and strategies.',
    postedDate: '2024-01-12T00:00:00Z',
    deadline: '2024-02-12T00:00:00Z',
    skills: ['Digital Marketing', 'Campaign Management', 'Analytics', 'SEO/SEM', 'Content Strategy']
  },
  {
    id: 4,
    title: 'Backend Engineer',
    department: 'Engineering',
    location: 'London',
    type: 'full-time',
    experience: '4+ years',
    salaryRange: '$110k - $150k',
    description: 'Build scalable backend systems and APIs that power our applications. Experience with cloud platforms is essential.',
    postedDate: '2024-01-08T00:00:00Z',
    deadline: '2024-02-08T00:00:00Z',
    skills: ['Python', 'Node.js', 'AWS', 'Databases', 'Microservices', 'REST APIs']
  },
  {
    id: 5,
    title: 'Sales Development Representative',
    department: 'Sales',
    location: 'San Francisco',
    type: 'full-time',
    experience: '2+ years',
    salaryRange: '$70k - $100k + commission',
    description: 'Drive new business opportunities and build relationships with potential clients.',
    postedDate: '2024-01-20T00:00:00Z',
    deadline: '2024-02-20T00:00:00Z',
    skills: ['Sales', 'Communication', 'CRM', 'Lead Generation', 'Negotiation']
  },
  {
    id: 6,
    title: 'Data Scientist',
    department: 'Engineering',
    location: 'Remote',
    type: 'full-time',
    experience: '3+ years',
    salaryRange: '$130k - $180k',
    description: 'Apply machine learning and statistical analysis to solve complex business problems.',
    postedDate: '2024-01-18T00:00:00Z',
    deadline: '2024-02-18T00:00:00Z',
    skills: ['Python', 'Machine Learning', 'Statistics', 'SQL', 'TensorFlow', 'Data Analysis']
  },
  {
    id: 7,
    title: 'UX Researcher',
    department: 'Design',
    location: 'New York',
    type: 'full-time',
    experience: '2+ years',
    salaryRange: '$80k - $120k',
    description: 'Conduct user research to inform design decisions and improve user experiences.',
    postedDate: '2024-01-14T00:00:00Z',
    deadline: '2024-02-14T00:00:00Z',
    skills: ['User Research', 'Usability Testing', 'Data Analysis', 'Prototyping', 'Survey Design']
  },
  {
    id: 8,
    title: 'DevOps Engineer',
    department: 'Engineering',
    location: 'London',
    type: 'full-time',
    experience: '4+ years',
    salaryRange: '$100k - $140k',
    description: 'Build and maintain CI/CD pipelines and infrastructure for our applications.',
    postedDate: '2024-01-16T00:00:00Z',
    deadline: '2024-02-16T00:00:00Z',
    skills: ['DevOps', 'Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Monitoring']
  },
  {
    id: 9,
    title: 'Content Marketing Specialist',
    department: 'Marketing',
    location: 'Remote',
    type: 'full-time',
    experience: '2+ years',
    salaryRange: '$60k - $80k',
    description: 'Create compelling content that drives engagement and supports our marketing goals.',
    postedDate: '2024-01-22T00:00:00Z',
    deadline: '2024-02-22T00:00:00Z',
    skills: ['Content Creation', 'SEO', 'Social Media', 'Writing', 'Analytics']
  }
])

// Benefits data
const benefits = ref([
  {
    id: 1,
    title: 'Innovation & Impact',
    description: 'Work on cutting-edge projects that make a real difference in the world',
    icon: 'fas fa-rocket'
  },
  {
    id: 2,
    title: 'Growth & Learning',
    description: 'Continuous learning opportunities and clear career advancement paths',
    icon: 'fas fa-graduation-cap'
  },
  {
    id: 3,
    title: 'Flexibility & Freedom',
    description: 'Flexible work arrangements and autonomy to do your best work',
    icon: 'fas fa-clock'
  },
  {
    id: 4,
    title: 'Team & Culture',
    description: 'Collaborative environment with talented and supportive colleagues',
    icon: 'fas fa-users'
  },
  {
    id: 5,
    title: 'Competitive Compensation',
    description: 'Market-leading salary, equity, and comprehensive benefits package',
    icon: 'fas fa-dollar-sign'
  },
  {
    id: 6,
    title: 'Work-Life Balance',
    description: 'Generous time off and support for your personal well-being',
    icon: 'fas fa-balance-scale'
  }
])

// Computed properties
const filteredPositions = computed(() => {
  let filtered = positions.value

  if (positionFilter.value) {
    filtered = filtered.filter(position => position.department.toLowerCase() === positionFilter.value.toLowerCase())
  }

  if (locationFilter.value) {
    filtered = filtered.filter(position => position.location.toLowerCase() === locationFilter.value.toLowerCase())
  }

  if (typeFilter.value) {
    filtered = filtered.filter(position => position.type.toLowerCase() === typeFilter.value.toLowerCase())
  }

  return filtered
})

const paginatedPositions = computed(() => {
  const start = (currentPage.value - 1) * positionsPerPage.value
  const end = start + positionsPerPage.value
  return filteredPositions.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredPositions.value.length / positionsPerPage.value)
})

// Methods
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatType = (type) => {
  return type.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const getEmptyMessage = () => {
  if (positionFilter.value || locationFilter.value || typeFilter.value) {
    return 'No positions match your filter criteria'
  }
  return 'No open positions at this time'
}

const filterPositions = () => {
  currentPage.value = 1
}

const viewPosition = (position) => {
  showSuccess(`Viewing details for ${position.title}`)
  // In a real app, this would navigate to position details
}

const savePosition = (position) => {
  showSuccess(`Position ${position.title} saved to your profile`)
  // In a real app, this would save the position
}

const sharePosition = (position) => {
  showSuccess(`Sharing ${position.title} position`)
  // In a real app, this would open share dialog
}

const applyForPosition = (position) => {
  showSuccess(`Starting application for ${position.title}`)
  // In a real app, this would open application form
}

const viewAllPositions = () => {
  showSuccess('Viewing all open positions')
  // In a real app, this would show all positions
}

const joinTalentPool = () => {
  showSuccess('Joining talent pool')
  // In a real app, this would open talent pool form
}

const connectWithRecruiter = () => {
  showSuccess('Opening LinkedIn recruiter connection')
  // In a real app, this would open LinkedIn
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/careers/positions')
    // if (response.success) {
    //   positions.value = response.positions || []
    // }
    
    // For demo, use mock data
    loading.value = false
  } catch (error) {
    console.error('Error loading positions:', error)
    showError('Failed to load positions')
    loading.value = false
  }
})
</script>

<style scoped>
.careers {
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

.careers-container {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.hero-section,
.why-join-section,
.positions-section,
.culture-section,
.benefits-section,
.interview-section,
.life-section,
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

.image-placeholder {
  width: 200px;
  height: 200px;
  background: var(--glass-bg-primary);
  border: 2px dashed var(--glass-border);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: 3rem;
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

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.benefit-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.benefit-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.benefit-icon {
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

.benefit-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.benefit-card p {
  color: var(--text-secondary);
  line-height: 1.6;
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

.positions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.position-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.position-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.position-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.position-info {
  flex: 1;
}

.position-info h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.position-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.department,
.location {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.type {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.type.full-time {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.type.part-time {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.type.contract {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.type.internship {
  background: rgba(156, 163, 175, 0.1);
  color: #6b7280;
}

.position-actions {
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

.action-btn.save:hover {
  background: var(--warning-color);
  color: white;
  border-color: var(--warning-color);
}

.action-btn.share:hover {
  background: var(--info-color);
  color: white;
  border-color: var(--info-color);
}

.position-content {
  margin-bottom: 1.5rem;
}

.position-description {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.position-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
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

.position-skills {
  margin-bottom: 1rem;
}

.position-skills h4 {
  font-size: 1rem;
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.position-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--glass-border);
}

.apply-btn {
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

.apply-btn:hover {
  background: var(--primary-hover);
}

.position-deadline {
  text-align: right;
}

.deadline-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-right: 0.5rem;
}

.deadline-date {
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

.culture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.culture-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.culture-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.culture-icon {
  width: 60px;
  height: 60px;
  background: var(--success-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1.5rem;
}

.culture-card h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.culture-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.benefits-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.benefit-category {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
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
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.category-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.benefit-list {
  padding: 1.5rem;
}

.benefit-list li {
  padding: 0.5rem 0;
  color: var(--text-secondary);
  position: relative;
  padding-left: 1.5rem;
  line-height: 1.6;
}

.benefit-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--success-color);
  font-weight: bold;
}

.process-timeline {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.process-step {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 2rem;
  align-items: start;
}

.step-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
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
  font-size: 1.2rem;
}

.step-icon {
  width: 50px;
  height: 50px;
  background: var(--info-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.step-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.step-content p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.step-duration {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.duration-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.duration-time {
  color: var(--text-primary);
  font-weight: 600;
}

.life-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.life-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.life-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.life-image {
  height: 200px;
  overflow: hidden;
}

.life-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.life-content {
  padding: 1.5rem;
}

.life-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.life-content p {
  color: var(--text-secondary);
  line-height: 1.6;
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
  .careers {
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
  
  .benefits-grid,
  .culture-grid,
  .benefits-categories {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .positions-grid {
    grid-template-columns: 1fr;
  }
  
  .position-details {
    grid-template-columns: 1fr;
  }
  
  .process-step {
    grid-template-columns: 60px 1fr;
    gap: 1rem;
  }
  
  .life-grid {
    grid-template-columns: 1fr;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>
