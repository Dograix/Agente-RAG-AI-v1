export const API_CONFIG = {
    BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    ENDPOINTS: {
        // Conversas
        CREATE_CONVERSATION: '/conversations/',
        LIST_CONVERSATIONS: '/conversations/',
        GET_CONVERSATION: (id: string) => `/conversations/${id}`,
        DELETE_CONVERSATION: (id: string) => `/conversations/${id}`,

        // Mensagens
        SEND_MESSAGE: (conversationId: string) => `/conversations/${conversationId}/messages/`,
        LIST_MESSAGES: (conversationId: string) => `/conversations/${conversationId}/messages/`,

        // Documentos
        UPLOAD_DOCUMENT: '/documents/upload/',
        LIST_DOCUMENTS: '/documents/',
        DELETE_DOCUMENT: (id: string) => `/documents/${id}`,
        DOCUMENT_STATUS: (id: string) => `/documents/${id}/status`,

        // Analytics
        SYSTEM_OVERVIEW: '/analytics/overview',
        POPULAR_TOPICS: '/analytics/popular-topics',
        CONVERSATION_STATS: (id: string) => `/analytics/conversations/${id}/stats`,

        // Sistema
        HEALTH: '/health',
        CLEAR_CACHE: '/system/clear-cache'
    },
    DEFAULT_HEADERS: {
        'Content-Type': 'application/json'
    },
    REQUEST_TIMEOUT: 30000, // 30 segundos
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1 segundo
};

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
    DOCUMENTS: {
        MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
        ALLOWED_FILE_TYPES: [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/markdown',
            'text/html',
            'text/css',
            'application/javascript',
            'application/json',
        ],
        UPLOAD_CHUNK_SIZE: 1024 * 1024, // 1MB
    },
};

export const ANALYTICS_CONFIG = {
    CHART_COLORS: [
        '#2563eb',
        '#10b981',
        '#f59e0b',
        '#ef4444',
        '#6366f1',
        '#8b5cf6',
        '#ec4899',
    ],
    DEFAULT_CHART_OPTIONS: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000,
        },
        plugins: {
            legend: {
                position: 'bottom' as const,
            },
            tooltip: {
                enabled: true,
            },
        },
    },
    TIME_RANGES: {
        LAST_24_HOURS: '24h',
        LAST_7_DAYS: '7d',
        LAST_30_DAYS: '30d',
        LAST_90_DAYS: '90d',
        CUSTOM: 'custom',
    },
};

export const ERROR_MESSAGES = {
    NETWORK_ERROR: 'Erro de conexão. Por favor, verifique sua internet.',
    SERVER_ERROR: 'Erro no servidor. Por favor, tente novamente mais tarde.',
    UNAUTHORIZED: 'Acesso não autorizado. Por favor, faça login novamente.',
    FORBIDDEN: 'Você não tem permissão para acessar este recurso.',
    NOT_FOUND: 'O recurso solicitado não foi encontrado.',
    VALIDATION_ERROR: 'Por favor, verifique os dados informados.',
    FILE_TOO_LARGE: 'O arquivo é muito grande. Tamanho máximo permitido: 10MB.',
    INVALID_FILE_TYPE: 'Tipo de arquivo não suportado.',
    UPLOAD_ERROR: 'Erro ao fazer upload do arquivo. Por favor, tente novamente.',
    PROCESSING_ERROR: 'Erro ao processar o documento. Por favor, tente novamente.',
};

export const SUCCESS_MESSAGES = {
    CONVERSATION_CREATED: 'Conversa criada com sucesso!',
    MESSAGE_SENT: 'Mensagem enviada com sucesso!',
    DOCUMENT_UPLOADED: 'Documento enviado com sucesso!',
    DOCUMENT_DELETED: 'Documento removido com sucesso!',
    CACHE_CLEARED: 'Cache limpo com sucesso!',
};

export default {
    API_CONFIG,
    UI_CONFIG,
    ANALYTICS_CONFIG,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
}; 