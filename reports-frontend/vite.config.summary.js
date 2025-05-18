import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { viteSingleFile } from 'vite-plugin-singlefile';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), viteSingleFile()],
  build: {
    outDir: "dist/summary",
    target: 'esnext',
    assetsInlineLimit: 100000000, // Large limit to inline assets
    cssCodeSplit: false,
    minify: false,
    rollupOptions: {
      input: './summaryReport.html',
      output: {
        inlineDynamicImports: true, // Inline dynamic imports
      }
    }
  },
})
