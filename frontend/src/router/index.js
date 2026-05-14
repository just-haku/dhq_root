import { createRouter, createWebHistory } from 'vue-router'
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const AdvancedClock = () => import('../components/Clock/AdvancedClock.vue')
const Funny404 = () => import('../views/Funny404.vue')
const DashboardLayout = () => import('../layouts/DashboardLayout.vue')

const routes = [
  {
    path: '/shadow-garden/login',
    name: 'HiddenLogin',
    component: Login
  },
  {
    path: '/shadow-garden/apply',
    name: 'HiddenRegister',
    component: Register
  },
  {
    path: '/',
    component: DashboardLayout,
    children: [
      {
        path: '',
        name: 'AdvancedClock',
        component: AdvancedClock,
        meta: { hideSideMenu: true, hideHeader: true }
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/order-center',
        name: 'OrderCenterDashboard',
        component: () => import('../views/OrderCenter/OrderCenterDashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/order-center/create',
        name: 'OrderCenterCreate',
        component: () => import('../views/OrderCenter/OrderCenterCreate.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/order-center/:id',
        name: 'OrderCenterManage',
        component: () => import('../views/OrderCenter/OrderCenterManage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/operator/server-settings',
        name: 'OperatorSettings',
        component: () => import('../views/Operator/OperatorSettings.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/operator/working-mode',
        name: 'OperatorWorkingMode',
        component: () => import('../views/Operator/WorkingMode.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/media-gallery',
        name: 'MediaGallery',
        component: () => import('../views/MediaGallery.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/shop',
        name: 'Shop',
        component: () => import('../views/Shop.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/virus-scan',
        name: 'VirusScan',
        component: () => import('../views/VirusScan.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/admin/system',
        name: 'AdminSystem',
        component: () => import('../views/AdminSystem.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/admin/panic',
        name: 'PanicMode',
        component: () => import('../views/Admin/PanicMode.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/nuke-data',
        name: 'NukeData',
        component: () => import('../views/NukeData.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/analytics',
        name: 'Analytics',
        component: () => import('../views/Analytics.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('../views/Reports.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/performance',
        name: 'Performance',
        component: () => import('../views/Performance.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/drive',
        name: 'Drive',
        component: () => import('../views/Drive.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/vault',
        name: 'Vault',
        component: () => import('../views/Vault.vue'),
        meta: { requiresAuth: true, requiresOp: true }
      },
      {
        path: '/collaboration',
        name: 'Collaboration',
        component: () => import('../views/Collaboration.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/kpi-bonus',
        name: 'KPIBonus',
        component: () => import('../components/KPI/KPIBonusDashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/arcade',
        name: 'Arcade',
        component: () => import('../components/Arcade/ArcadeDashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/daily-gifts',
        name: 'DailyGifts',
        component: () => import('../components/Arcade/DailyGifts.vue'),
        meta: { requiresAuth: true }
      },
      { path: '/arcade/daily', redirect: '/daily-gifts' },
      { path: '/arcade/gifts', redirect: '/daily-gifts' },
      {
        path: '/manage-gifts',
        name: 'ManageGifts',
        component: () => import('../components/Arcade/ManageGifts.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/gcode-generator',
        name: 'GcodeGenerator',
        component: () => import('../views/GcodeGenerator.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/convo-hub',
        name: 'ConvoHub',
        component: () => import('../views/ConvoHub.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/email-hub',
        name: 'EmailHub',
        component: () => import('../views/EmailHub.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/prompts',
        name: 'PromptLibrary',
        component: () => import('../views/PromptLibrary.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/tasks',
        name: 'TaskCenter',
        component: () => import('../views/TaskCenter.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/notifications',
        name: 'NotificationCenter',
        component: () => import('../views/NotificationCenter.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/admin/users',
        name: 'ManageUsers',
        component: () => import('../views/Operator/ManageUsers.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/admin/shop',
        name: 'ManageShop',
        component: () => import('../views/Operator/ManageShop.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
    ]
  },
  {
    path: '/s/:hash',
    name: 'PublicShare',
    component: () => import('@/views/PublicView.vue')
  },
  {
    path: '/s/:hash/view',
    name: 'PublicFileView',
    component: () => import('@/views/EmbedView.vue')
  },
  {
    path: '/:id',
    name: 'ShortLinkRedirect',
    redirect: to => {
      const id = to.params.id;
      const protectedRoutes = ['login', 'register', 'drive', 'vault', 'shop', 'profile', 'settings', 'admin', 's'];
      if (protectedRoutes.includes(id)) {
        return { name: id };
      }
      return { path: `/s/${id}` };
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: Funny404
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard - Stealth Mode
// Unauthenticated users see only the Clock (/) or the 404 page.
// The login portal is hidden at /shadow-garden/login.
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token')
  const userData = localStorage.getItem('user')
  const user = userData ? JSON.parse(userData) : null
  const userRole = user ? user.role : null

  // If trying to access a protected route without auth -> redirect to root
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/')
  } else if (to.meta.requiresAdmin && !['AD', 'OP'].includes(userRole)) {
    next('/')
  } else if (to.meta.requiresOp && userRole !== 'OP') {
    next('/')
  } else if (to.path === '/shadow-garden/login' && isAuthenticated) {
    // Already logged in, go to dashboard
    next('/dashboard')
  } else {
    next()
  }
})

export default router
