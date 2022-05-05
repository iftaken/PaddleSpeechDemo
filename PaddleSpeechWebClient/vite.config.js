import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  css: 
    { preprocessorOptions:
      { css: 
        { 
          charset: false 
        } 
      } 
    },
  build: {
      assetsInlineLimit: '2048' // 2kb
  },
  server: {
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: "http://localhost:8010",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      "/a_ws": {
        target: "ws://localhost:8010",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api_ws/, ""),
      },
      "/VPR": {
        target: "http://localhost:8002",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/VPR/, ""),
      },
    },
  },
})
