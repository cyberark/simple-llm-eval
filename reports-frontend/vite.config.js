import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { viteSingleFile } from 'vite-plugin-singlefile';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), viteSingleFile()],
  build: {
    target: 'esnext',
    assetsInlineLimit: 100000000, // Large limit to inline assets
    cssCodeSplit: false,
    minify: false,
    rollupOptions: {
      input: {
        main: './evalReport.html', // Existing main entry point
        compare: './compareReport.html', // New entry point for CompareReport.jsx
        summary: './summaryReport.html', // New entry point for SummaryReport.jsx
      },
      output: {
        inlineDynamicImports: true, // Inline dynamic imports
      }
    }
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/tests/setup.jsx", // Load the global setup
    globals: true, // Allow global use of expect, describe, it
  },
})
