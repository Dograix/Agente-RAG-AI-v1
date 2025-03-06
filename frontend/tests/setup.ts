import '@testing-library/jest-dom';
import { vi, afterEach } from 'vitest';
import { QueryClient } from '@tanstack/react-query';

// Mock do QueryClient
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

// Limpa todos os mocks após cada teste
afterEach(() => {
  vi.clearAllMocks();
}); 