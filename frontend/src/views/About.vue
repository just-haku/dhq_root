<template>
  <div class="about">
    <div class="page-header">
      <h1>About Us</h1>
      <p>Learn more about our company, mission, and team</p>
    </div>

    <div class="about-container">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-content">
          <div class="hero-text">
            <h2>{{ companyData.name }}</h2>
            <p class="hero-tagline">{{ companyData.tagline }}</p>
            <p class="hero-description">{{ companyData.description }}</p>
            <div class="hero-stats">
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.yearsInBusiness }}</div>
                <div class="stat-label">Years in Business</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.customers }}</div>
                <div class="stat-label">Happy Customers</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.projects }}</div>
                <div class="stat-label">Projects Completed</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ companyData.stats.teamMembers }}</div>
                <div class="stat-label">Team Members</div>
              </div>
            </div>
          </div>
          <div class="hero-image">
            <div class="image-placeholder">
              <i class="fas fa-building"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- Mission & Vision -->
      <section class="mission-section">
        <div class="section-header">
          <h2>Our Mission & Vision</h2>
        </div>
        <div class="mission-grid">
          <div class="mission-card">
            <div class="card-icon">
              <i class="fas fa-bullseye"></i>
            </div>
            <h3>Our Mission</h3>
            <p>{{ companyData.mission }}</p>
          </div>
          <div class="mission-card">
            <div class="card-icon">
              <i class="fas fa-eye"></i>
            </div>
            <h3>Our Vision</h3>
            <p>{{ companyData.vision }}</p>
          </div>
          <div class="mission-card">
            <div class="card-icon">
              <i class="fas fa-heart"></i>
            </div>
            <h3>Our Values</h3>
            <p>{{ companyData.values }}</p>
          </div>
        </div>
      </section>

      <!-- Company Story -->
      <section class="story-section">
        <div class="section-header">
          <h2>Our Story</h2>
        </div>
        <div class="story-content">
          <div class="story-timeline">
            <div 
              v-for="milestone in companyData.story" 
              :key="milestone.year"
              class="timeline-item"
            >
              <div class="timeline-marker">
                <div class="marker-dot"></div>
                <div class="marker-year">{{ milestone.year }}</div>
              </div>
              <div class="timeline-content">
                <h3>{{ milestone.title }}</h3>
                <p>{{ milestone.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Leadership Team -->
      <section class="team-section">
        <div class="section-header">
          <h2>Leadership Team</h2>
          <p>Meet the people behind our success</p>
        </div>
        <div class="team-grid">
          <div 
            v-for="member in leadershipTeam" 
            :key="member.id"
            class="team-member"
          >
            <div class="member-photo">
              <img :src="member.photo" :alt="member.name" />
              <div class="member-overlay">
                <div class="social-links">
                  <a v-if="member.linkedin" :href="member.linkedin" class="social-link">
                    <i class="fab fa-linkedin"></i>
                  </a>
                  <a v-if="member.twitter" :href="member.twitter" class="social-link">
                    <i class="fab fa-twitter"></i>
                  </a>
                  <a v-if="member.email" :href="`mailto:${member.email}`" class="social-link">
                    <i class="fas fa-envelope"></i>
                  </a>
                </div>
              </div>
            </div>
            <div class="member-info">
              <h3>{{ member.name }}</h3>
              <p class="member-role">{{ member.role }}</p>
              <p class="member-bio">{{ member.bio }}</p>
              <div class="member-skills">
                <span 
                  v-for="skill in member.skills" 
                  :key="skill"
                  class="skill-tag"
                >
                  {{ skill }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Company Culture -->
      <section class="culture-section">
        <div class="section-header">
          <h2>Our Culture</h2>
          <p>What makes us different</p>
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

      <!-- Technology Stack -->
      <section class="tech-section">
        <div class="section-header">
          <h2>Technology & Innovation</h2>
          <p>The tools and technologies we use</p>
        </div>
        <div class="tech-categories">
          <div 
            v-for="category in technologyStack" 
            :key="category.name"
            class="tech-category"
          >
            <div class="category-header">
              <div class="category-icon">
                <i :class="category.icon"></i>
              </div>
              <h3>{{ category.name }}</h3>
            </div>
            <div class="tech-list">
              <div 
                v-for="tech in category.technologies" 
                :key="tech.name"
                class="tech-item"
              >
                <div class="tech-logo">
                  <img v-if="tech.logo" :src="tech.logo" :alt="tech.name" />
                  <i v-else :class="tech.icon"></i>
                </div>
                <span class="tech-name">{{ tech.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Achievements -->
      <section class="achievements-section">
        <div class="section-header">
          <h2>Achievements & Awards</h2>
        </div>
        <div class="achievements-grid">
          <div 
            v-for="achievement in achievements" 
            :key="achievement.id"
            class="achievement-card"
          >
            <div class="achievement-icon">
              <i :class="achievement.icon"></i>
            </div>
            <div class="achievement-content">
              <h3>{{ achievement.title }}</h3>
              <p>{{ achievement.description }}</p>
              <div class="achievement-meta">
                <span class="achievement-year">{{ achievement.year }}</span>
                <span class="achievement-organization">{{ achievement.organization }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Partners -->
      <section class="partners-section">
        <div class="section-header">
          <h2>Our Partners</h2>
          <p>Companies we work with</p>
        </div>
        <div class="partners-grid">
          <div 
            v-for="partner in partners" 
            :key="partner.id"
            class="partner-card"
          >
            <div class="partner-logo">
              <img :src="partner.logo" :alt="partner.name" />
            </div>
            <div class="partner-info">
              <h3>{{ partner.name }}</h3>
              <p>{{ partner.description }}</p>
              <span class="partner-type">{{ partner.type }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Office Locations -->
      <section class="offices-section">
        <div class="section-header">
          <h2>Our Offices</h2>
          <p>Where you can find us</p>
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
                  <i class="fas fa-users"></i>
                  <span>{{ office.employees }} employees</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Contact CTA -->
      <section class="cta-section">
        <div class="cta-content">
          <h2>Ready to Work With Us?</h2>
          <p>Join thousands of satisfied customers who trust our solutions</p>
          <div class="cta-buttons">
            <button class="cta-btn primary" @click="navigateToContact">
              <i class="fas fa-envelope"></i>
              Contact Us
            </button>
            <button class="cta-btn secondary" @click="navigateToCareers">
              <i class="fas fa-briefcase"></i>
              Join Our Team
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { showSuccess } from '@/utils/notification'

// Company data
const companyData = reactive({
  name: 'Digital HQ',
  tagline: 'Innovating Tomorrow, Today',
  description: 'We are a leading technology company dedicated to creating innovative solutions that transform businesses and improve lives through cutting-edge technology and exceptional service.',
  mission: 'To empower businesses with innovative technology solutions that drive growth, efficiency, and success in the digital age.',
  vision: 'To be the global leader in digital transformation, setting new standards for excellence and innovation in technology.',
  values: 'We believe in innovation, integrity, customer-centricity, and continuous improvement. Our values guide every decision we make and every solution we create.',
  stats: {
    yearsInBusiness: 10,
    customers: '10,000+',
    projects: '5,000+',
    teamMembers: '150+'
  },
  story: [
    {
      year: 2014,
      title: 'The Beginning',
      description: 'Founded with a vision to revolutionize digital transformation for businesses of all sizes.'
    },
    {
      year: 2016,
      title: 'First Major Product',
      description: 'Launched our flagship product that transformed how businesses manage their digital presence.'
    },
    {
      year: 2018,
      title: 'International Expansion',
      description: 'Expanded operations to serve customers across 50+ countries worldwide.'
    },
    {
      year: 2020,
      title: 'Innovation Milestone',
      description: 'Achieved breakthrough in AI-powered solutions, setting new industry standards.'
    },
    {
      year: 2022,
      title: 'Growth & Recognition',
      description: 'Reached 10,000+ customers and received multiple industry awards for excellence.'
    },
    {
      year: 2024,
      title: 'Future Forward',
      description: 'Continuing our journey of innovation with expanded services and global reach.'
    }
  ],
  culture: [
    {
      title: 'Innovation First',
      description: 'We constantly push boundaries and explore new possibilities to deliver cutting-edge solutions.',
      icon: 'fas fa-lightbulb'
    },
    {
      title: 'Customer Obsessed',
      description: 'Our customers are at the heart of everything we do. Their success is our success.',
      icon: 'fas fa-heart'
    },
    {
      title: 'Team Collaboration',
      description: 'We believe in the power of diverse perspectives and collaborative problem-solving.',
      icon: 'fas fa-users'
    },
    {
      title: 'Continuous Learning',
      description: 'We embrace curiosity and continuous improvement as core to our growth.',
      icon: 'fas fa-graduation-cap'
    }
  ]
})

// Leadership team
const leadershipTeam = ref([
  {
    id: 1,
    name: 'Sarah Johnson',
    role: 'Chief Executive Officer',
    bio: 'Sarah brings over 15 years of technology leadership experience. Previously led digital transformation initiatives at Fortune 500 companies.',
    photo: '/api/placeholder/200x200',
    skills: ['Leadership', 'Strategy', 'Innovation'],
    linkedin: 'https://linkedin.com/in/sarahjohnson',
    twitter: 'https://twitter.com/sarahjohnson',
    email: 'sarah.johnson@company.com'
  },
  {
    id: 2,
    name: 'Michael Chen',
    role: 'Chief Technology Officer',
    bio: 'Michael is a technology visionary with expertise in AI, cloud computing, and scalable architecture.',
    photo: '/api/placeholder/200x200',
    skills: ['AI/ML', 'Cloud Architecture', 'DevOps'],
    linkedin: 'https://linkedin.com/in/michaelchen',
    email: 'michael.chen@company.com'
  },
  {
    id: 3,
    name: 'Emily Rodriguez',
    role: 'Chief Operating Officer',
    bio: 'Emily excels at operational excellence and has a proven track record of scaling high-growth technology companies.',
    photo: '/api/placeholder/200x200',
    skills: ['Operations', 'Strategy', 'Team Building'],
    linkedin: 'https://linkedin.com/in/emilyrodriguez',
    email: 'emily.rodriguez@company.com'
  },
  {
    id: 4,
    name: 'David Kim',
    role: 'Chief Marketing Officer',
    bio: 'David is a marketing expert with deep experience in brand building and customer acquisition strategies.',
    photo: '/api/placeholder/200x200',
    skills: ['Marketing', 'Brand Strategy', 'Growth'],
    linkedin: 'https://linkedin.com/in/davidkim',
    twitter: 'https://twitter.com/davidkim',
    email: 'david.kim@company.com'
  }
])

// Technology stack
const technologyStack = ref([
  {
    name: 'Frontend',
    icon: 'fas fa-laptop-code',
    technologies: [
      { name: 'Vue.js', icon: 'fab fa-vuejs', logo: null },
      { name: 'React', icon: 'fab fa-react', logo: null },
      { name: 'TypeScript', icon: 'fab fa-js', logo: null },
      { name: 'Tailwind CSS', icon: 'fas fa-paint-brush', logo: null }
    ]
  },
  {
    name: 'Backend',
    icon: 'fas fa-server',
    technologies: [
      { name: 'Node.js', icon: 'fab fa-node-js', logo: null },
      { name: 'Python', icon: 'fab fa-python', logo: null },
      { name: 'PostgreSQL', icon: 'fas fa-database', logo: null },
      { name: 'Redis', icon: 'fas fa-memory', logo: null }
    ]
  },
  {
    name: 'Cloud & DevOps',
    icon: 'fas fa-cloud',
    technologies: [
      { name: 'AWS', icon: 'fab fa-aws', logo: null },
      { name: 'Docker', icon: 'fab fa-docker', logo: null },
      { name: 'Kubernetes', icon: 'fas fa-dharmachakra', logo: null },
      { name: 'GitHub Actions', icon: 'fab fa-github', logo: null }
    ]
  },
  {
    name: 'AI & Machine Learning',
    icon: 'fas fa-brain',
    technologies: [
      { name: 'TensorFlow', icon: null, logo: '/api/placeholder/40x40' },
      { name: 'PyTorch', icon: null, logo: '/api/placeholder/40x40' },
      { name: 'OpenAI', icon: null, logo: '/api/placeholder/40x40' },
      { name: 'Hugging Face', icon: null, logo: '/api/placeholder/40x40' }
    ]
  }
])

// Achievements
const achievements = ref([
  {
    id: 1,
    title: 'Best Innovation Award',
    description: 'Recognized for breakthrough AI-powered business intelligence platform',
    year: '2023',
    organization: 'Tech Innovation Awards',
    icon: 'fas fa-trophy'
  },
  {
    id: 2,
    title: 'Fastest Growing Company',
    description: 'Ranked among the top 10 fastest growing technology companies',
    year: '2022',
    organization: 'Business Weekly',
    icon: 'fas fa-rocket'
  },
  {
    id: 3,
    title: 'Customer Excellence',
    description: 'Achieved 98% customer satisfaction rating',
    year: '2023',
    organization: 'Customer Service Institute',
    icon: 'fas fa-star'
  },
  {
    id: 4,
    title: 'Industry Leadership',
    description: 'Recognized as market leader in digital transformation solutions',
    year: '2024',
    organization: 'Digital Transformation Association',
    icon: 'fas fa-crown'
  }
])

// Partners
const partners = ref([
  {
    id: 1,
    name: 'TechCorp Solutions',
    description: 'Strategic technology partner for cloud infrastructure',
    type: 'Technology Partner',
    logo: '/api/placeholder/100x50'
  },
  {
    id: 2,
    name: 'Global Finance Bank',
    description: 'Financial services partner for enterprise solutions',
    type: 'Financial Partner',
    logo: '/api/placeholder/100x50'
  },
  {
    id: 3,
    name: 'Innovation Labs',
    description: 'Research and development collaboration partner',
    type: 'Research Partner',
    logo: '/api/placeholder/100x50'
  },
  {
    id: 4,
    name: 'Digital Marketing Pro',
    description: 'Marketing and growth strategy partner',
    type: 'Marketing Partner',
    logo: '/api/placeholder/100x50'
  }
])

// Office locations
const offices = ref([
  {
    id: 1,
    city: 'San Francisco',
    address: '123 Tech Street, San Francisco, CA 94105',
    phone: '+1 (415) 555-0100',
    email: 'sf@company.com',
    employees: 80,
    image: '/api/placeholder/300x200'
  },
  {
    id: 2,
    city: 'New York',
    address: '456 Innovation Ave, New York, NY 10001',
    phone: '+1 (212) 555-0200',
    email: 'ny@company.com',
    employees: 45,
    image: '/api/placeholder/300x200'
  },
  {
    id: 3,
    city: 'London',
    address: '789 Digital Road, London, UK EC1A 1BB',
    phone: '+44 20 5555 0300',
    email: 'london@company.com',
    employees: 25,
    image: '/api/placeholder/300x200'
  }
])

// Methods
const navigateToContact = () => {
  showSuccess('Navigating to contact page...')
  // In a real app, this would navigate to the contact page
}

const navigateToCareers = () => {
  showSuccess('Navigating to careers page...')
  // In a real app, this would navigate to the careers page
}

// Lifecycle
onMounted(() => {
  // Any initialization logic
})
</script>

<style scoped>
.about {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 4rem;
}

.page-header h1 {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.page-header p {
  font-size: 1.2rem;
  color: var(--text-secondary);
}

.about-container {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.hero-section {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 3rem;
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
  font-size: 2.5rem;
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

.mission-section,
.story-section,
.team-section,
.culture-section,
.tech-section,
.achievements-section,
.partners-section,
.offices-section,
.cta-section {
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

.mission-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.mission-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.mission-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.card-icon {
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

.mission-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.mission-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.story-timeline {
  position: relative;
  padding-left: 3rem;
}

.story-timeline::before {
  content: '';
  position: absolute;
  left: 1rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--primary-color);
}

.timeline-item {
  position: relative;
  margin-bottom: 3rem;
}

.timeline-marker {
  position: absolute;
  left: -3rem;
  top: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.marker-dot {
  width: 20px;
  height: 20px;
  background: var(--primary-color);
  border: 4px solid var(--glass-bg-secondary);
  border-radius: 50%;
  z-index: 1;
}

.marker-year {
  background: var(--primary-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
}

.timeline-content h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.timeline-content p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 3rem;
}

.team-member {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.team-member:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.member-photo {
  position: relative;
  height: 250px;
  overflow: hidden;
}

.member-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.member-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.team-member:hover .member-overlay {
  opacity: 1;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-link {
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  text-decoration: none;
  transition: all 0.3s ease;
}

.social-link:hover {
  background: var(--primary-color);
  color: white;
  transform: scale(1.1);
}

.member-info {
  padding: 2rem;
}

.member-info h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.member-role {
  color: var(--primary-color);
  font-weight: 600;
  margin-bottom: 1rem;
}

.member-bio {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.member-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.culture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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

.tech-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.tech-category {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.category-icon {
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

.category-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
}

.tech-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.tech-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.tech-item:hover {
  background: var(--glass-bg-hover);
}

.tech-logo {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tech-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.tech-name {
  color: var(--text-primary);
  font-weight: 500;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.achievement-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  transition: all 0.3s ease;
}

.achievement-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.achievement-icon {
  width: 60px;
  height: 60px;
  background: var(--warning-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1.5rem;
}

.achievement-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.achievement-content p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.achievement-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.achievement-year {
  background: var(--primary-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.achievement-organization {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.partners-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.partner-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.partner-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.partner-logo {
  width: 100px;
  height: 50px;
  margin: 0 auto 1.5rem;
}

.partner-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.partner-info h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.partner-info p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.partner-type {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
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
  padding: 2rem;
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
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.detail-item i {
  width: 20px;
  color: var(--primary-color);
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

@media (max-width: 768px) {
  .about {
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
  
  .mission-grid,
  .culture-grid,
  .tech-categories,
  .achievements-grid,
  .partners-grid,
  .offices-grid {
    grid-template-columns: 1fr;
  }
  
  .team-grid {
    grid-template-columns: 1fr;
  }
  
  .story-timeline {
    padding-left: 2rem;
  }
  
  .timeline-marker {
    left: -2rem;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>
