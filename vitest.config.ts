import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./frontend/tests/setup.ts'],
    include: ['./frontend/tests/**/*.{test,spec}.{ts,tsx}'],
  },
}); 