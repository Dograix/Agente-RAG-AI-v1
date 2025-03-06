export const API_BASE_URL = 'http://localhost:8000';

export const API_CONFIG = {
    API_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    ENDPOINTS: {
        CONVERSATIONS: '/conversations',
        DOCUMENTS: '/documents',
        ANALYTICS: '/analytics'
    },
    DEFAULT_HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    REQUEST_TIMEOUT: 30000, // 30 segundos
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1 segundo
} as const;

export const UI_CONFIG = {
    colors: {
        primary: {
            main: '#2563eb',
            light: '#60a5fa',
            dark: '#1d4ed8',
            contrastText: '#ffffff'
        },
        secondary: {
            main: '#4f46e5',
            light: '#818cf8',
            dark: '#4338ca',
            contrastText: '#ffffff'
        },
        success: {
            main: '#059669',
            light: '#34d399',
            dark: '#047857',
            contrastText: '#ffffff'
        },
        error: {
            main: '#dc2626',
            light: '#f87171',
            dark: '#b91c1c',
            contrastText: '#ffffff'
        },
        warning: {
            main: '#d97706',
            light: '#fbbf24',
            dark: '#b45309',
            contrastText: '#ffffff'
        },
        info: {
            main: '#0284c7',
            light: '#38bdf8',
            dark: '#0369a1',
            contrastText: '#ffffff'
        },
        background: {
            default: '#f9fafb',
            paper: '#ffffff'
        },
        text: {
            primary: '#111827',
            secondary: '#4b5563',
            disabled: '#9ca3af'
        }
    },
    typography: {
        fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
        fontWeights: {
            regular: 400,
            medium: 500,
            semibold: 600,
            bold: 700
        }
    },
    shape: {
        borderRadius: 8
    },
    PAGINATION: {
        DEFAULT_PAGE_SIZE: 10,
        PAGE_SIZE_OPTIONS: [5, 10, 20, 50],
    },
    DATE_FORMAT: 'DD/MM/YYYY HH:mm:ss',
    ANIMATIONS: {
        TRANSITION_DURATION: 300,
        FADE_DURATION: 200,
    },
    TOAST: {
        DURATION: 5000,
        POSITION: 'top-right',
    },
    CHAT: {
        MAX_MESSAGE_LENGTH: 4000,
        MESSAGE_PREVIEW_LENGTH: 150,
        TYPING_INDICATOR_DELAY: 1000,
    },
} as const;

export const ERROR_MESSAGES = {
    GENERIC: 'Ocorreu um erro. Por favor, tente novamente.',
    NETWORK: 'Erro de conexão. Verifique sua internet.',
} as const;

export const SUCCESS_MESSAGES = {
    CACHE_CLEARED: 'Cache limpo com sucesso!',
} as const;

const config = {
    API_CONFIG,
    UI_CONFIG,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
} as const;

export default config; 