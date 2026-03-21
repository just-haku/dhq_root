import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdvancedClock from '../components/Clock/AdvancedClock.vue'
import Funny404 from '../views/Funny404.vue'
import DashboardLayout from '../layouts/DashboardLayout.vue'

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
        path: '/orders/create',
        name: 'OrdersCreate',
        component: () => import('../views/OrdersCreate.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/orders/manage',
        name: 'OrdersManage',
        component: () => import('../views/OrdersManage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/admin/tasks',
        name: 'AdminTasks',
        component: () => import('../views/AdminTasks.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/virus-scan',
        name: 'VirusScan',
        component: () => import('../views/VirusScan.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/admin/users',
        name: 'AdminUsers',
        component: () => import('../views/AdminUsers.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/admin/system',
        name: 'AdminSystem',
        component: () => import('../views/AdminSystem.vue'),
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
        path: '/calendar',
        name: 'Calendar',
        component: () => import('../views/Calendar.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/messages',
        name: 'Messages',
        component: () => import('../views/Messages.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/notifications',
        name: 'Notifications',
        component: () => import('../views/Notifications.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/team',
        name: 'Team',
        component: () => import('../views/Team.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/projects',
        name: 'Projects',
        component: () => import('../views/Projects.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/projects/:id',
        name: 'ProjectDetail',
        component: () => import('../views/ProjectDetail.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/invoices',
        name: 'Invoices',
        component: () => import('../views/Invoices.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/invoices/:id',
        name: 'InvoiceDetail',
        component: () => import('../views/InvoiceDetail.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/help',
        name: 'Help',
        component: () => import('../views/Help.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/changelog',
        name: 'Changelog',
        component: () => import('../views/Changelog.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/api-keys',
        name: 'ApiKeys',
        component: () => import('../views/ApiKeys.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/integrations',
        name: 'Integrations',
        component: () => import('../views/Integrations.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/backup',
        name: 'Backup',
        component: () => import('../views/Backup.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/audit-log',
        name: 'AuditLog',
        component: () => import('../views/AuditLog.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/performance',
        name: 'Performance',
        component: () => import('../views/Performance.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/security',
        name: 'Security',
        component: () => import('../views/Security.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/billing',
        name: 'Billing',
        component: () => import('../views/Billing.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/subscription',
        name: 'Subscription',
        component: () => import('../views/Subscription.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/referrals',
        name: 'Referrals',
        component: () => import('../views/Referrals.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/marketplace',
        name: 'Marketplace',
        component: () => import('../views/Marketplace.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/templates',
        name: 'Templates',
        component: () => import('../views/Templates.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/automation',
        name: 'Automation',
        component: () => import('../views/Automation.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/workflows',
        name: 'Workflows',
        component: () => import('../views/Workflows.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/webhooks',
        name: 'Webhooks',
        component: () => import('../views/Webhooks.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/logs',
        name: 'Logs',
        component: () => import('../views/Logs.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/monitoring',
        name: 'Monitoring',
        component: () => import('../views/Monitoring.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/database',
        name: 'Database',
        component: () => import('../views/Database.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/cache',
        name: 'Cache',
        component: () => import('../views/Cache.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/emails',
        name: 'Emails',
        component: () => import('../views/Emails.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/sms',
        name: 'SMS',
        component: () => import('../views/SMS.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/storage',
        name: 'Storage',
        component: () => import('../views/Storage.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/domains',
        name: 'Domains',
        component: () => import('../views/Domains.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/ssl',
        name: 'SSL',
        component: () => import('../views/SSL.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/firewall',
        name: 'Firewall',
        component: () => import('../views/Firewall.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/backups',
        name: 'Backups',
        component: () => import('../views/Backups.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/restores',
        name: 'Restores',
        component: () => import('../views/Restores.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/migrations',
        name: 'Migrations',
        component: () => import('../views/Migrations.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/deployments',
        name: 'Deployments',
        component: () => import('../views/Deployments.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/environments',
        name: 'Environments',
        component: () => import('../views/Environments.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/builds',
        name: 'Builds',
        component: () => import('../views/Builds.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/releases',
        name: 'Releases',
        component: () => import('../views/Releases.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/testing',
        name: 'Testing',
        component: () => import('../views/Testing.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/debug',
        name: 'Debug',
        component: () => import('../views/Debug.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: '/sandbox',
        name: 'Sandbox',
        component: () => import('../views/Sandbox.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/playground',
        name: 'Playground',
        component: () => import('../views/Playground.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/documentation',
        name: 'Documentation',
        component: () => import('../views/Documentation.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/tutorials',
        name: 'Tutorials',
        component: () => import('../views/Tutorials.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/support',
        name: 'Support',
        component: () => import('../views/Support.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/feedback',
        name: 'Feedback',
        component: () => import('../views/Feedback.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/roadmap',
        name: 'Roadmap',
        component: () => import('../views/Roadmap.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/beta',
        name: 'Beta',
        component: () => import('../views/Beta.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/early-access',
        name: 'EarlyAccess',
        component: () => import('../views/EarlyAccess.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/partners',
        name: 'Partners',
        component: () => import('../views/Partners.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/affiliate',
        name: 'Affiliate',
        component: () => import('../views/Affiliate.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/reseller',
        name: 'Reseller',
        component: () => import('../views/Reseller.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/white-label',
        name: 'WhiteLabel',
        component: () => import('../views/WhiteLabel.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/enterprise',
        name: 'Enterprise',
        component: () => import('../views/Enterprise.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/compliance',
        name: 'Compliance',
        component: () => import('../views/Compliance.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/gdpr',
        name: 'GDPR',
        component: () => import('../views/GDPR.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/privacy-policy',
        name: 'PrivacyPolicy',
        component: () => import('../views/PrivacyPolicy.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/terms-of-service',
        name: 'TermsOfService',
        component: () => import('../views/TermsOfService.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/cookie-policy',
        name: 'CookiePolicy',
        component: () => import('../views/CookiePolicy.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/about',
        name: 'About',
        component: () => import('../views/About.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/contact',
        name: 'Contact',
        component: () => import('../views/Contact.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/careers',
        name: 'Careers',
        component: () => import('../views/Careers.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/press',
        name: 'Press',
        component: () => import('../views/Press.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/investors',
        name: 'Investors',
        component: () => import('../views/Investors.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/blog',
        name: 'Blog',
        component: () => import('../views/Blog.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: '/drive',
        name: 'Drive',
        component: () => import('../views/Drive.vue'),
        meta: { requiresAuth: true }
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
    ]
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
  } else if (to.path === '/shadow-garden/login' && isAuthenticated) {
    // Already logged in, go to dashboard
    next('/dashboard')
  } else {
    next()
  }
})

export default router
