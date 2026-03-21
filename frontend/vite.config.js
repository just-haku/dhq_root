import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0', // Allow external access
    port: 3001,
    // Fix "Blocked request": explicitly allow your domain
    allowedHosts: ['haku.io.vn', 'www.haku.io.vn', 'localhost', '0.0.0.0', '113.177.128.116', 'dhq_frontend'],
    // Fix MIME type issues
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      // Proxy the hidden login routes
      '/shadow-garden': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        bypass: function (req, res, proxyOptions) {
          if (req.method === 'GET' && req.url.includes('/login')) {
            return '/index.html';
          }
        }
      },
      // Proxy Socket.IO traffic to the standalone process on port 8001
      '/socket.io': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        ws: true
      }
    }
  },
  // Fix module loading issues
  optimizeDeps: {
    force: true,
    include: ['vue', 'vue-router']
  },
  // Production build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue'],
          chart: ['chart.js']
        }
      }
    }
  }
})