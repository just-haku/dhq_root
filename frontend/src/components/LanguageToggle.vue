<template>
  <div class="lang-toggle-wrapper">
    <button class="lang-btn" @click="toggleLanguage">
      <i class="fas fa-globe"></i>
      <span class="lang-text">{{ currentLang === 'en' ? 'EN' : 'VI' }}</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const currentLang = computed(() => locale.value)

const toggleLanguage = () => {
  const newLang = locale.value === 'en' ? 'vi' : 'en'
  locale.value = newLang
  localStorage.setItem('dhq-locale', newLang)
}
</script>

<style scoped>
.lang-toggle-wrapper {
  display: inline-block;
  margin-left: auto;
}

.lang-btn {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  padding: 0.4rem 0.8rem;
  border-radius: 50px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 0.8rem;
  transition: all 0.3s;
}

.lang-btn:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.lang-btn i {
  font-size: 0.9rem;
}
</style>
