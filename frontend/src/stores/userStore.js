import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
    const user = ref(null)

    // Initialize from localStorage
    const init = () => {
        const userData = localStorage.getItem('user')
        if (userData) {
            try {
                user.value = JSON.parse(userData)
            } catch (e) {
                user.value = null
            }
        }
    }

    const setUser = (userData) => {
        user.value = { ...user.value, ...userData } // Merge to preserve fields
        localStorage.setItem('user', JSON.stringify(user.value))
    }

    const clearUser = () => {
        user.value = null
        localStorage.removeItem('user')
        localStorage.removeItem('token')
    }

    const fetchProfile = async () => {
        try {
            const { apiGet } = await import('@/utils/api')
            const response = await apiGet('/user/profile')
            if (response) {
                setUser(response)
            }
        } catch (error) {
            console.error('Failed to fetch user profile:', error)
        }
    }

    const username = computed(() => user.value?.username || '')
    const displayName = computed(() => user.value?.display_name || user.value?.username || '')
    const email = computed(() => user.value?.email || '')
    const avatarUrl = computed(() => user.value?.avatar_url || '')
    const bannerUrl = computed(() => user.value?.banner_url || '')
    const role = computed(() => user.value?.role || 'USER')
    const activeTheme = computed(() => user.value?.active_theme || 'dark')
    const unlockedThemes = computed(() => user.value?.unlocked_themes || ['dark', 'light'])
    const sideMenuLayout = computed(() => user.value?.side_menu_layout || 'list')

    return {
        user,
        init,
        setUser,
        clearUser,
        fetchProfile,
        username,
        displayName,
        email,
        avatarUrl,
        bannerUrl,
        role,
        activeTheme,
        unlockedThemes,
        sideMenuLayout
    }
})
