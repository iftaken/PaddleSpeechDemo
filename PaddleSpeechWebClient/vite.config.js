import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteSingleFile } from "vite-plugin-singlefile"


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), viteSingleFile({ useRecommendedBuildConfig: false, removeViteModuleLoader: true })],
  base: process.env.NODE_ENV === 'production' ? './' : '/',
  css: 
    { preprocessorOptions:
      { css: 
        { 
          charset: false 
        } 
      } 
    },
  build: {
      assetsInlineLimit: '204800' // 2kb
  },
  server: {
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: "http://localhost:8010",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
})
