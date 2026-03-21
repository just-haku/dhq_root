<template>
  <div class="profile-view">
    <!-- Banner Section -->
    <div class="profile-banner-container">
      <div 
        class="profile-banner" 
        :style="{ backgroundImage: bannerUrl ? `url(${bannerUrl})` : 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' }"
      >
        <div class="banner-overlay"></div>
      </div>
      
      <!-- Profile Card Float -->
      <div class="profile-card-container">
        <div class="profile-card glass-panel">
          <div class="avatar-wrapper">
            <div class="avatar-border">
              <img :src="avatarUrl || defaultAvatar" class="avatar-img" />
            </div>
          </div>
          
          <div class="profile-info">
            <h1 class="display-name">{{ displayName }}</h1>
            <p class="username">@{{ username }}</p>
            <div class="badge-container">
              <span class="role-badge" :class="role.toLowerCase()">{{ role }}</span>
            </div>
          </div>
          
          <div class="profile-stats">
            <div class="stat-item">
              <span class="stat-value">{{ formattedJoinDate }}</span>
              <span class="stat-label">Member Since</span>
            </div>
          </div>

          <div class="profile-actions">
            <router-link to="/settings" class="btn btn-secondary">
              <i class="fas fa-edit"></i> Edit Profile
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile Content -->
    <div class="profile-content-grid">
      <div class="content-section glass-panel">
        <h3>About</h3>
        <p class="email-info" v-if="email">
          <i class="fas fa-envelope"></i> {{ email }}
        </p>
        <p class="bio-placeholder">
          Welcome to my profile. I am a member of the DHQ network.
        </p>
      </div>
      
      <div class="content-section glass-panel">
        <h3>Activity</h3>
        <p class="activity-placeholder">
          Recent activity will appear here as you interact with the system.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/userStore'

const userStore = useUserStore()

const username = computed(() => userStore.username)
const displayName = computed(() => userStore.displayName)
const email = computed(() => userStore.email)
const avatarUrl = computed(() => userStore.avatarUrl)
const bannerUrl = computed(() => userStore.bannerUrl)
const role = computed(() => userStore.role)

const defaultAvatar = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(userStore.displayName) + '&background=6366f1&color=fff&size=200'

const formattedJoinDate = computed(() => {
  if (!userStore.user?.created_at) return 'N/A'
  return new Date(userStore.user.created_at).toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric'
  })
})

onMounted(() => {
  userStore.fetchProfile()
})
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  padding-bottom: 4rem;
}

.profile-banner-container {
  height: 400px;
  position: relative;
  margin-bottom: 12rem;
}

.profile-banner {
  height: 350px;
  background-size: cover;
  background-position: center;
  position: relative;
  border-radius: 0 0 40px 40px;
  overflow: hidden;
}

.banner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(15, 23, 42, 0.2), rgba(15, 23, 42, 0.8));
}

.profile-card-container {
  position: absolute;
  top: 250px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 800px;
  z-index: 10;
}

.profile-card {
  padding: 2.5rem;
  display: flex;
  align-items: center;
  gap: 3rem;
  border-radius: 30px;
  background: var(--glass-bg-primary);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow-xl);
}

.avatar-wrapper {
  flex-shrink: 0;
}

.avatar-border {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  padding: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--glass-bg-primary);
}

.profile-info {
  flex: 1;
}

.display-name {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.username {
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin: 0.25rem 0 1rem 0;
}

.badge-container {
  display: flex;
  gap: 0.5rem;
}

.role-badge {
  padding: 0.4rem 1.2rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.role-badge.op {
  background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%);
  color: white;
}

.role-badge.ad {
  background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%);
  color: white;
}

.role-badge.user {
  background: linear-gradient(135deg, #10b981 0%, #065f46 100%);
  color: white;
}

.profile-stats {
  padding-left: 2rem;
  border-left: 1px solid var(--glass-border);
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-tertiary);
  text-transform: uppercase;
}

.profile-actions {
  margin-top: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.btn-secondary {
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
}

.profile-content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
}

.content-section {
  padding: 2rem;
  border-radius: 20px;
  background: var(--glass-bg-primary);
}

.content-section h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  color: var(--text-primary);
}

.email-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-secondary);
}

.bio-placeholder, .activity-placeholder {
  color: var(--text-tertiary);
  font-style: italic;
}

@media (max-width: 768px) {
  .profile-card {
    flex-direction: column;
    text-align: center;
    padding: 2rem;
  }
  
  .profile-stats {
    padding-left: 0;
    padding-top: 1.5rem;
    border-left: none;
    border-top: 1px solid var(--glass-border);
    width: 100%;
  }
  
  .profile-content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
