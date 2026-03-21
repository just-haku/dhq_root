<template>
  <div class="testing">
    <div class="page-header">
      <h1>Testing</h1>
      <p>Test and debug your applications</p>
    </div>

    <div class="testing-container">
      <div class="testing-grid">
        <div class="test-card">
          <div class="card-icon">
            <i class="fas fa-vial"></i>
          </div>
          <h3>Unit Tests</h3>
          <p>Run unit tests for your components and utilities</p>
          <button class="btn-primary" @click="runUnitTests">
            <i class="fas fa-play"></i>
            Run Tests
          </button>
        </div>

        <div class="test-card">
          <div class="card-icon">
            <i class="fas fa-cogs"></i>
          </div>
          <h3>Integration Tests</h3>
          <p>Test component interactions and API integrations</p>
          <button class="btn-primary" @click="runIntegrationTests">
            <i class="fas fa-play"></i>
            Run Tests
          </button>
        </div>

        <div class="test-card">
          <div class="card-icon">
            <i class="fas fa-desktop"></i>
          </div>
          <h3>E2E Tests</h3>
          <p>End-to-end testing with browser automation</p>
          <button class="btn-primary" @click="runE2ETests">
            <i class="fas fa-play"></i>
            Run Tests
          </button>
        </div>

        <div class="test-card">
          <div class="card-icon">
            <i class="fas fa-bug"></i>
          </div>
          <h3>Debug Console</h3>
          <p>Debug and troubleshoot application issues</p>
          <button class="btn-primary" @click="openDebugConsole">
            <i class="fas fa-terminal"></i>
            Open Console
          </button>
        </div>
      </div>

      <div class="test-results" v-if="testResults.length > 0">
        <h2>Test Results</h2>
        <div class="results-grid">
          <div 
            v-for="result in testResults" 
            :key="result.id"
            class="result-card"
            :class="{ 'success': result.status === 'passed', 'error': result.status === 'failed' }"
          >
            <div class="result-header">
              <h4>{{ result.name }}</h4>
              <span :class="['status', result.status]">{{ result.status }}</span>
            </div>
            <div class="result-details">
              <p>{{ result.description }}</p>
              <div class="result-meta">
                <span>Duration: {{ result.duration }}ms</span>
                <span>Tests: {{ result.tests }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { showSuccess, showError } from '@/utils/notification'

// Reactive state
const testResults = ref([])

// Methods
const runUnitTests = async () => {
  showSuccess('Running unit tests...')
  
  // Simulate test execution
  const results = [
    {
      id: 1,
      name: 'Component Tests',
      status: 'passed',
      description: 'All component tests passed successfully',
      duration: 1250,
      tests: 45
    },
    {
      id: 2,
      name: 'Utility Tests',
      status: 'passed',
      description: 'All utility function tests passed',
      duration: 850,
      tests: 23
    }
  ]
  
  setTimeout(() => {
    testResults.value = results
    showSuccess('Unit tests completed')
  }, 2000)
}

const runIntegrationTests = async () => {
  showSuccess('Running integration tests...')
  
  const results = [
    {
      id: 3,
      name: 'API Integration',
      status: 'passed',
      description: 'All API integration tests passed',
      duration: 2100,
      tests: 18
    }
  ]
  
  setTimeout(() => {
    testResults.value = [...testResults.value, ...results]
    showSuccess('Integration tests completed')
  }, 3000)
}

const runE2ETests = async () => {
  showSuccess('Running E2E tests...')
  
  const results = [
    {
      id: 4,
      name: 'User Flow Tests',
      status: 'failed',
      description: '2 out of 5 user flow tests failed',
      duration: 5400,
      tests: 5
    }
  ]
  
  setTimeout(() => {
    testResults.value = [...testResults.value, ...results]
    showError('Some E2E tests failed')
  }, 5000)
}

const openDebugConsole = () => {
  showSuccess('Opening debug console...')
  // In a real app, this would open a debug console
}
</script>

<style scoped>
.testing {
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
  margin-bottom: 1rem;
}

.page-header p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.testing-container {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.testing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.test-card {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.test-card:hover {
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

.test-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.test-card p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 2rem;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.test-results {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 2rem;
}

.test-results h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.result-card {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.result-card.success {
  border-left: 4px solid var(--success-color);
}

.result-card.error {
  border-left: 4px solid var(--danger-color);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.result-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status.passed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.result-details p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.result-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}
</style>
