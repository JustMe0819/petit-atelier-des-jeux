import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// En développement, Vite sert le site (port 5173) et redirige /api vers le serveur Express (port 8787).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8787' },
  },
  build: { outDir: 'dist', sourcemap: false },
  test: {
    include: ['tests/**/*.test.ts'],
    environment: 'node',
    pool: 'forks',
  },
} as never);
