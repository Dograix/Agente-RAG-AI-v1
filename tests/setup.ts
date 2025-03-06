/// <reference types="node" />
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock do fetch global
const fetchMock = vi.fn();
vi.stubGlobal('fetch', fetchMock);

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  clear: vi.fn(),
  removeItem: vi.fn(),
  length: 0,
  key: vi.fn(),
};
vi.stubGlobal('localStorage', localStorageMock);

// Mock do ResizeObserver
const resizeObserverMock = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
vi.stubGlobal('ResizeObserver', resizeObserverMock); 