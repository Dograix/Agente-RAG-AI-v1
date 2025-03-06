export const API_CONFIG = {
    API_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    ENDPOINTS: {
        CONVERSATIONS: '/conversations',
        ANALYTICS: {
            OVERVIEW: '/analytics/overview',
            POPULAR_TOPICS: '/analytics/popular-topics',
        },
        DOCUMENTS: '/documents',
    },
} as const; 