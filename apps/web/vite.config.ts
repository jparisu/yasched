import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  // Dev-only: forward API calls to the local FastAPI server (`yasched serve`).
  // In production the same server serves this built bundle, so no proxy is used.
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
});
