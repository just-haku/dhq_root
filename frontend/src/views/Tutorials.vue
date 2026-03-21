<template>
  <div class="tutorials">
    <div class="page-header">
      <h1>Learning Tutorials</h1>
      <p>Step-by-step tutorials to help you master the platform</p>
    </div>

    <!-- Search and Filter -->
    <div class="search-section">
      <div class="search-container">
        <div class="search-input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search tutorials..."
            @input="searchTutorials"
            class="search-input"
          />
        </div>
        <div class="filter-controls">
          <select v-model="difficultyFilter" @change="filterTutorials">
            <option value="">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <select v-model="categoryFilter" @change="filterTutorials">
            <option value="">All Categories</option>
            <option value="getting-started">Getting Started</option>
            <option value="development">Development</option>
            <option value="deployment">Deployment</option>
            <option value="advanced">Advanced Topics</option>
          </select>
          <select v-model="durationFilter" @change="filterTutorials">
            <option value="">All Durations</option>
            <option value="short">Under 30 min</option>
            <option value="medium">30-60 min</option>
            <option value="long">Over 1 hour</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Featured Tutorials -->
    <div class="featured-section">
      <div class="section-header">
        <h2>Featured Tutorials</h2>
        <div class="header-actions">
          <button class="view-all-btn" @click="viewAllFeatured">
            View All
          </button>
        </div>
      </div>

      <div class="featured-grid">
        <div 
          v-for="tutorial in featuredTutorials" 
          :key="tutorial.id"
          class="featured-card"
          @click="startTutorial(tutorial)"
        >
          <div class="featured-image">
            <img :src="tutorial.image" :alt="tutorial.title" />
            <div class="featured-badge">
              <span class="badge">{{ tutorial.difficulty }}</span>
            </div>
          </div>
          
          <div class="featured-content">
            <div class="tutorial-meta">
              <span class="category">{{ tutorial.category }}</span>
              <span class="duration">{{ tutorial.duration }} min</span>
              <span class="rating">
                <i class="fas fa-star"></i> {{ tutorial.rating }}
              </span>
            </div>
            
            <h3>{{ tutorial.title }}</h3>
            <p>{{ tutorial.description }}</p>
            
            <div class="tutorial-stats">
              <span class="students">{{ tutorial.students }} students</span>
              <span class="progress">{{ tutorial.progress }}% complete</span>
            </div>
            
            <div class="tutorial-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: tutorial.progress + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tutorial Categories -->
    <div class="categories-section">
      <div class="section-header">
        <h2>Browse by Category</h2>
      </div>
      
      <div class="categories-grid">
        <div 
          v-for="category in categories" 
          :key="category.id"
          class="category-card"
          @click="filterByCategory(category.id)"
        >
          <div class="category-icon">
            <i :class="category.icon"></i>
          </div>
          <h3>{{ category.name }}</h3>
          <p>{{ category.description }}</p>
          <div class="category-stats">
            <span class="tutorial-count">{{ category.tutorialCount }} tutorials</span>
            <span class="duration">{{ category.totalDuration }} min total</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tutorial List -->
    <div class="tutorials-section">
      <div class="section-header">
        <h2>All Tutorials</h2>
        <div class="header-actions">
          <div class="sort-controls">
            <select v-model="sortBy" @change="sortTutorials">
              <option value="popular">Most Popular</option>
              <option value="newest">Newest First</option>
              <option value="rating">Highest Rated</option>
              <option value="duration">Duration</option>
              <option value="difficulty">Difficulty</option>
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
        <p>Loading tutorials...</p>
      </div>

      <div v-else-if="filteredTutorials.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-graduation-cap"></i>
        </div>
        <h3>No tutorials found</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>

      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="tutorials-grid">
          <div 
            v-for="tutorial in filteredTutorials" 
            :key="tutorial.id"
            class="tutorial-card"
            @click="startTutorial(tutorial)"
          >
            <div class="tutorial-image">
              <img :src="tutorial.image" :alt="tutorial.title" />
              <div class="tutorial-overlay">
                <div class="difficulty-badge" :class="tutorial.difficulty">
                  {{ tutorial.difficulty }}
                </div>
              </div>
            </div>
            
            <div class="tutorial-content">
              <div class="tutorial-meta">
                <span class="category">{{ tutorial.category }}</span>
                <span class="duration">{{ tutorial.duration }} min</span>
                <span class="rating">
                  <i class="fas fa-star"></i> {{ tutorial.rating }}
                </span>
              </div>
              
              <h3>{{ tutorial.title }}</h3>
              <p>{{ tutorial.description }}</p>
              
              <div class="tutorial-instructor">
                <img :src="tutorial.instructor.avatar" :alt="tutorial.instructor.name" />
                <span>{{ tutorial.instructor.name }}</span>
              </div>
              
              <div class="tutorial-stats">
                <span class="students">{{ tutorial.students }} students</span>
                <span class="lessons">{{ tutorial.lessons }} lessons</span>
              </div>
              
              <div class="tutorial-progress" v-if="tutorial.progress > 0">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: tutorial.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ tutorial.progress }}% complete</span>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="tutorials-list">
          <div 
            v-for="tutorial in filteredTutorials" 
            :key="tutorial.id"
            class="tutorial-list-card"
            @click="startTutorial(tutorial)"
          >
            <div class="tutorial-list-image">
              <img :src="tutorial.image" :alt="tutorial.title" />
              <div class="difficulty-badge" :class="tutorial.difficulty">
                {{ tutorial.difficulty }}
              </div>
            </div>
            
            <div class="tutorial-list-content">
              <div class="tutorial-list-header">
                <h3>{{ tutorial.title }}</h3>
                <div class="tutorial-list-meta">
                  <span class="category">{{ tutorial.category }}</span>
                  <span class="duration">{{ tutorial.duration }} min</span>
                  <span class="rating">
                    <i class="fas fa-star"></i> {{ tutorial.rating }}
                  </span>
                </div>
              </div>
              
              <p>{{ tutorial.description }}</p>
              
              <div class="tutorial-list-details">
                <div class="instructor-info">
                  <img :src="tutorial.instructor.avatar" :alt="tutorial.instructor.name" />
                  <span>{{ tutorial.instructor.name }}</span>
                </div>
                <div class="stats-info">
                  <span class="students">{{ tutorial.students }} students</span>
                  <span class="lessons">{{ tutorial.lessons }} lessons</span>
                </div>
              </div>
              
              <div class="tutorial-list-progress" v-if="tutorial.progress > 0">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: tutorial.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ tutorial.progress }}% complete</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Learning Paths -->
    <div class="learning-paths-section">
      <div class="section-header">
        <h2>Learning Paths</h2>
        <div class="header-actions">
          <button class="create-path-btn" @click="showCreatePathModal = true">
            <i class="fas fa-plus"></i>
            Create Path
          </button>
        </div>
      </div>

      <div class="paths-grid">
        <div 
          v-for="path in learningPaths" 
          :key="path.id"
          class="path-card"
          @click="startLearningPath(path)"
        >
          <div class="path-header">
            <div class="path-icon">
              <i :class="path.icon"></i>
            </div>
            <div class="path-badge">
              <span class="badge">{{ path.level }}</span>
            </div>
          </div>

          <div class="path-content">
            <h3>{{ path.title }}</h3>
            <p>{{ path.description }}</p>
            
            <div class="path-tutorials">
              <div class="tutorial-preview">
                <img 
                  v-for="tutorial in path.tutorials.slice(0, 3)" 
                  :key="tutorial.id"
                  :src="tutorial.image" 
                  :alt="tutorial.title"
                />
                <div class="more-count" v-if="path.tutorials.length > 3">
                  +{{ path.tutorials.length - 3 }}
                </div>
              </div>
            </div>
            
            <div class="path-stats">
              <span class="tutorial-count">{{ path.tutorials.length }} tutorials</span>
              <span class="total-duration">{{ path.totalDuration }} min</span>
              <span class="students">{{ path.students }} enrolled</span>
            </div>
            
            <div class="path-progress" v-if="path.progress > 0">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: path.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ path.progress }}% complete</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tutorial Viewer Modal -->
    <div v-if="showTutorialModal" class="modal-overlay" @click="closeTutorialModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedTutorial?.title }}</h2>
          <button class="close-btn" @click="closeTutorialModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="tutorial-viewer">
            <div class="tutorial-info">
              <div class="tutorial-header">
                <div class="tutorial-meta">
                  <span class="category">{{ selectedTutorial?.category }}</span>
                  <span class="duration">{{ selectedTutorial?.duration }} min</span>
                  <span class="rating">
                    <i class="fas fa-star"></i> {{ selectedTutorial?.rating }}
                  </span>
                  <span class="difficulty" :class="selectedTutorial?.difficulty">
                    {{ selectedTutorial?.difficulty }}
                  </span>
                </div>
                
                <div class="tutorial-instructor">
                  <img :src="selectedTutorial?.instructor.avatar" :alt="selectedTutorial?.instructor.name" />
                  <div class="instructor-details">
                    <span class="instructor-name">{{ selectedTutorial?.instructor.name }}</span>
                    <span class="instructor-title">{{ selectedTutorial?.instructor.title }}</span>
                  </div>
                </div>
              </div>
              
              <div class="tutorial-description">
                <h3>About This Tutorial</h3>
                <p>{{ selectedTutorial?.description }}</p>
              </div>
              
              <div class="tutorial-content">
                <div v-html="selectedTutorial?.content"></div>
              </div>
            </div>
            
            <div class="tutorial-sidebar">
              <div class="lessons-list">
                <h4>Lessons</h4>
                <div 
                  v-for="(lesson, index) in selectedTutorial?.lessons" 
                  :key="index"
                  class="lesson-item"
                  :class="{ active: currentLesson === index }"
                  @click="selectLesson(index)"
                >
                  <div class="lesson-number">{{ index + 1 }}</div>
                  <div class="lesson-info">
                    <h5>{{ lesson.title }}</h5>
                    <span class="lesson-duration">{{ lesson.duration }} min</span>
                  </div>
                  <div class="lesson-status">
                    <i :class="lesson.completed ? 'fas fa-check-circle completed' : 'far fa-circle'"></i>
                  </div>
                </div>
              </div>
              
              <div class="tutorial-actions">
                <button class="btn-primary" @click="continueTutorial">
                  <i class="fas fa-play"></i>
                  {{ selectedTutorial?.progress > 0 ? 'Continue' : 'Start' }} Tutorial
                </button>
                <button class="btn-secondary" @click="bookmarkTutorial">
                  <i class="fas fa-bookmark"></i>
                  Bookmark
                </button>
                <button class="btn-secondary" @click="shareTutorial">
                  <i class="fas fa-share"></i>
                  Share
                </button>
              </div>
            </div>
          </div>
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
const searchQuery = ref('')
const difficultyFilter = ref('')
const categoryFilter = ref('')
const durationFilter = ref('')
const sortBy = ref('popular')
const viewMode = ref('grid')
const loading = ref(false)
const showTutorialModal = ref(false)
const showCreatePathModal = ref(false)
const selectedTutorial = ref(null)
const currentLesson = ref(0)

// Tutorial data
const tutorials = ref([
  {
    id: 1,
    title: 'Getting Started with Vue 3',
    description: 'Learn the fundamentals of Vue 3 and build your first application',
    category: 'Getting Started',
    difficulty: 'beginner',
    duration: 45,
    rating: 4.8,
    students: 1234,
    lessons: 8,
    progress: 25,
    image: '/api/placeholder/400x250',
    instructor: {
      name: 'Sarah Johnson',
      title: 'Vue.js Expert',
      avatar: '/api/placeholder/50x50'
    },
    content: '<h3>Welcome to Vue 3</h3><p>This comprehensive tutorial will guide you through the fundamentals of Vue 3...</p>'
  },
  {
    id: 2,
    title: 'Advanced Component Patterns',
    description: 'Master advanced component patterns and best practices',
    category: 'Development',
    difficulty: 'advanced',
    duration: 90,
    rating: 4.9,
    students: 567,
    lessons: 12,
    progress: 0,
    image: '/api/placeholder/400x250',
    instructor: {
      name: 'Michael Chen',
      title: 'Frontend Architect',
      avatar: '/api/placeholder/50x50'
    },
    content: '<h3>Advanced Patterns</h3><p>Explore advanced component patterns in Vue 3...</p>'
  },
  {
    id: 3,
    title: 'Deploying to Production',
    description: 'Learn how to deploy your Vue applications to production',
    category: 'Deployment',
    difficulty: 'intermediate',
    duration: 60,
    rating: 4.7,
    students: 892,
    lessons: 10,
    progress: 75,
    image: '/api/placeholder/400x250',
    instructor: {
      name: 'Emily Davis',
      title: 'DevOps Engineer',
      avatar: '/api/placeholder/50x50'
    },
    content: '<h3>Production Deployment</h3><p>Master the art of deploying Vue applications...</p>'
  }
])

// Featured tutorials
const featuredTutorials = computed(() => {
  return tutorials.value.filter(tutorial => tutorial.rating >= 4.7).slice(0, 3)
})

// Categories
const categories = ref([
  {
    id: 'getting-started',
    name: 'Getting Started',
    description: 'Perfect for beginners',
    icon: 'fas fa-rocket',
    tutorialCount: 12,
    totalDuration: 480
  },
  {
    id: 'development',
    name: 'Development',
    description: 'Core development skills',
    icon: 'fas fa-code',
    tutorialCount: 24,
    totalDuration: 1200
  },
  {
    id: 'deployment',
    name: 'Deployment',
    description: 'Deploy and scale apps',
    icon: 'fas fa-server',
    tutorialCount: 8,
    totalDuration: 360
  },
  {
    id: 'advanced',
    name: 'Advanced Topics',
    description: 'Expert-level content',
    icon: 'fas fa-graduation-cap',
    tutorialCount: 15,
    totalDuration: 900
  }
])

// Learning paths
const learningPaths = ref([
  {
    id: 1,
    title: 'Vue.js Mastery',
    description: 'Complete Vue.js learning path from beginner to expert',
    level: 'Beginner to Advanced',
    icon: 'fas fa-vuejs',
    tutorials: tutorials.value.slice(0, 4),
    totalDuration: 285,
    students: 2341,
    progress: 35
  },
  {
    id: 2,
    title: 'Full-Stack Development',
    description: 'Build complete web applications with Vue and Node.js',
    level: 'Intermediate',
    icon: 'fas fa-laptop-code',
    tutorials: tutorials.value.slice(1, 5),
    totalDuration: 360,
    students: 1567,
    progress: 0
  }
])

// Computed properties
const filteredTutorials = computed(() => {
  let filtered = tutorials.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(tutorial => 
      tutorial.title.toLowerCase().includes(query) ||
      tutorial.description.toLowerCase().includes(query) ||
      tutorial.category.toLowerCase().includes(query)
    )
  }

  if (difficultyFilter.value) {
    filtered = filtered.filter(tutorial => tutorial.difficulty === difficultyFilter.value)
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(tutorial => 
      tutorial.category.toLowerCase().includes(categoryFilter.value.toLowerCase())
    )
  }

  if (durationFilter.value) {
    if (durationFilter.value === 'short') {
      filtered = filtered.filter(tutorial => tutorial.duration < 30)
    } else if (durationFilter.value === 'medium') {
      filtered = filtered.filter(tutorial => tutorial.duration >= 30 && tutorial.duration <= 60)
    } else if (durationFilter.value === 'long') {
      filtered = filtered.filter(tutorial => tutorial.duration > 60)
    }
  }

  // Sort tutorials
  if (sortBy.value === 'popular') {
    filtered.sort((a, b) => b.students - a.students)
  } else if (sortBy.value === 'newest') {
    filtered.sort((a, b) => b.id - a.id)
  } else if (sortBy.value === 'rating') {
    filtered.sort((a, b) => b.rating - a.rating)
  } else if (sortBy.value === 'duration') {
    filtered.sort((a, b) => a.duration - b.duration)
  } else if (sortBy.value === 'difficulty') {
    const difficultyOrder = { beginner: 1, intermediate: 2, advanced: 3 }
    filtered.sort((a, b) => difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty])
  }

  return filtered
})

// Methods
const searchTutorials = () => {
  // Search is handled by computed property
}

const filterTutorials = () => {
  // Filtering is handled by computed property
}

const sortTutorials = () => {
  // Sorting is handled by computed property
}

const filterByCategory = (categoryId) => {
  categoryFilter.value = categoryId
  searchQuery.value = ''
}

const getEmptyMessage = () => {
  if (searchQuery.value || difficultyFilter.value || categoryFilter.value || durationFilter.value) {
    return 'No tutorials match your filter criteria'
  }
  return 'No tutorials found'
}

const startTutorial = (tutorial) => {
  selectedTutorial.value = tutorial
  showTutorialModal.value = true
}

const closeTutorialModal = () => {
  showTutorialModal.value = false
  selectedTutorial.value = null
  currentLesson.value = 0
}

const selectLesson = (index) => {
  currentLesson.value = index
}

const continueTutorial = async () => {
  try {
    // const response = await apiPost(`/tutorials/${selectedTutorial.value.id}/continue`)
    // if (response.success) {
    //   showSuccess('Tutorial started successfully')
    //   // Navigate to tutorial player
    // }
    
    // For demo, simulate start
    showSuccess('Tutorial started successfully')
  } catch (error) {
    console.error('Error starting tutorial:', error)
    showError('Failed to start tutorial')
  }
}

const bookmarkTutorial = async () => {
  try {
    // const response = await apiPost(`/tutorials/${selectedTutorial.value.id}/bookmark`)
    // if (response.success) {
    //   showSuccess('Tutorial bookmarked successfully')
    // }
    
    // For demo, simulate bookmark
    showSuccess('Tutorial bookmarked successfully')
  } catch (error) {
    console.error('Error bookmarking tutorial:', error)
    showError('Failed to bookmark tutorial')
  }
}

const shareTutorial = async () => {
  try {
    // const response = await apiPost(`/tutorials/${selectedTutorial.value.id}/share`)
    // if (response.success) {
    //   navigator.clipboard.writeText(response.shareUrl)
    //   showSuccess('Tutorial shared! URL copied to clipboard')
    // }
    
    // For demo, simulate share
    const shareUrl = `https://tutorials.example.com/tutorial/${selectedTutorial.value.id}`
    navigator.clipboard.writeText(shareUrl)
    showSuccess('Tutorial shared! URL copied to clipboard')
  } catch (error) {
    console.error('Error sharing tutorial:', error)
    showError('Failed to share tutorial')
  }
}

const viewAllFeatured = () => {
  // Navigate to featured tutorials page
  showSuccess('Viewing all featured tutorials')
}

const startLearningPath = (path) => {
  // Navigate to learning path
  showSuccess(`Starting learning path: ${path.title}`)
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // const response = await apiGet('/tutorials')
    // if (response.success) {
    //   tutorials.value = response.tutorials || []
    //   categories.value = response.categories || []
    //   learningPaths.value = response.learningPaths || []
    // }
    
    // For demo, use mock data
  } catch (error) {
    console.error('Error loading tutorials:', error)
    showError('Failed to load tutorials')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.tutorials {
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

.search-section,
.featured-section,
.categories-section,
.tutorials-section,
.learning-paths-section {
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

.search-container {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-input-wrapper {
  flex: 1;
  min-width: 300px;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-secondary);
  font-size: 1rem;
}

.search-input {
  flex: 1;
  padding: 1rem 1rem 1rem 3rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  outline: none;
}

.search-input:focus {
  border-color: var(--primary-color);
}

.filter-controls,
.sort-controls {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-controls select,
.sort-controls select {
  padding: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
}

.view-all-btn,
.create-path-btn {
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

.view-all-btn:hover,
.create-path-btn:hover {
  background: var(--primary-hover);
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

.featured-grid,
.categories-grid,
.paths-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.featured-card,
.category-card,
.path-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.featured-card:hover,
.category-card:hover,
.path-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.featured-image,
.tutorial-image,
.tutorial-list-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.featured-image img,
.tutorial-image img,
.tutorial-list-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.featured-badge,
.tutorial-overlay {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.badge {
  padding: 0.5rem 1rem;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.featured-content,
.tutorial-content {
  padding: 1.5rem;
}

.tutorial-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.category,
.duration,
.rating {
  padding: 0.25rem 0.75rem;
  background: var(--glass-bg-tertiary);
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.rating {
  color: var(--warning-color);
}

.featured-content h3,
.tutorial-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.2rem;
}

.featured-content p,
.tutorial-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.tutorial-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.tutorial-progress {
  margin-top: 1rem;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: var(--glass-bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.category-icon,
.path-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 1.5rem auto 1rem;
}

.category-card h3,
.path-card h3 {
  text-align: center;
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.category-card p,
.path-card p {
  text-align: center;
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  padding: 0 1rem;
}

.category-stats,
.path-stats {
  display: flex;
  justify-content: center;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  padding: 0 1rem 1rem;
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

.tutorials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.tutorial-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tutorial-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.difficulty-badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.difficulty-badge.beginner {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.difficulty-badge.intermediate {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.difficulty-badge.advanced {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.tutorial-instructor {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.tutorial-instructor img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.tutorials-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tutorial-list-card {
  display: flex;
  gap: 1.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tutorial-list-card:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
}

.tutorial-list-image {
  width: 200px;
  height: 120px;
  flex-shrink: 0;
}

.tutorial-list-content {
  flex: 1;
}

.tutorial-list-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.tutorial-list-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.tutorial-list-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tutorial-list-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.instructor-info,
.stats-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.instructor-info img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.tutorial-list-progress {
  margin-top: 1rem;
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
}

.path-badge {
  padding: 0.25rem 0.75rem;
  background: var(--info-color);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.path-content {
  padding: 0 1.5rem 1.5rem;
}

.path-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.path-content p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.path-tutorials {
  margin-bottom: 1rem;
}

.tutorial-preview {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.tutorial-preview img {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  object-fit: cover;
}

.more-count {
  width: 40px;
  height: 40px;
  background: var(--glass-bg-tertiary);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  color: var(--text-secondary);
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
  max-width: 1000px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 1200px;
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

.tutorial-viewer {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
}

.tutorial-info {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.tutorial-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.tutorial-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.difficulty {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.difficulty.beginner {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.difficulty.intermediate {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.difficulty.advanced {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.tutorial-instructor {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.tutorial-instructor img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.instructor-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.instructor-name {
  font-weight: 600;
  color: var(--text-primary);
}

.instructor-title {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.tutorial-description h3,
.tutorial-content h3 {
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.tutorial-content {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 2rem;
  min-height: 400px;
}

.tutorial-sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.lessons-list {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.lessons-list h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-weight: 600;
}

.lesson-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 0.5rem;
}

.lesson-item:hover {
  background: var(--glass-bg-hover);
}

.lesson-item.active {
  background: var(--primary-color);
  color: white;
}

.lesson-number {
  width: 32px;
  height: 32px;
  background: var(--glass-bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.8rem;
}

.lesson-item.active .lesson-number {
  background: rgba(255, 255, 255, 0.2);
}

.lesson-info {
  flex: 1;
}

.lesson-info h5 {
  margin: 0 0 0.25rem 0;
  font-weight: 600;
  font-size: 0.9rem;
}

.lesson-duration {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.lesson-item.active .lesson-duration {
  color: rgba(255, 255, 255, 0.8);
}

.lesson-status {
  color: var(--text-secondary);
}

.lesson-status.completed {
  color: var(--success-color);
}

.tutorial-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-primary,
.btn-secondary {
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
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
  .tutorials {
    padding: 1rem;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .featured-grid,
  .categories-grid,
  .paths-grid,
  .tutorials-grid {
    grid-template-columns: 1fr;
  }
  
  .tutorial-list-card {
    flex-direction: column;
  }
  
  .tutorial-list-image {
    width: 100%;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-content.large {
    max-width: 95%;
  }
  
  .tutorial-viewer {
    grid-template-columns: 1fr;
  }
  
  .tutorial-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
