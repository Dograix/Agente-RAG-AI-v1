import { useQuery } from 'react-query';
import { apiService } from '../services/api';
import { ANALYTICS_CONFIG } from '../config';

export interface SystemOverview {
    total_conversations: number;
    total_messages: number;
    total_documents: number;
    recent_activity: Array<{
        timestamp: string;
        action: string;
        details: string;
    }>;
}

export interface PopularTopic {
    topic: string;
    count: number;
    relevance_score: number;
}

export interface ConversationStats {
    total_messages: number;
    average_response_time: number;
    user_message_count: number;
    assistant_message_count: number;
    total_tokens_used: number;
}

export const useAnalytics = () => {
    // Visão geral do sistema
    const useSystemOverview = () => {
        return useQuery(
            'system-overview',
            () => apiService.getSystemOverview(),
            {
                staleTime: 60000, // 1 minuto
            }
        );
    };

    // Tópicos populares
    const usePopularTopics = (days: number = 7) => {
        return useQuery(
            ['popular-topics', days],
            () => apiService.getPopularTopics(days),
            {
                staleTime: 300000, // 5 minutos
            }
        );
    };

    // Estatísticas de uma conversa específica
    const useConversationStats = (conversationId: string) => {
        return useQuery(
            ['conversation-stats', conversationId],
            () => apiService.getConversationStats(conversationId),
            {
                enabled: !!conversationId,
                staleTime: 60000, // 1 minuto
            }
        );
    };

    // Formata duração em milissegundos para string legível
    const formatDuration = (ms: number): string => {
        if (ms < 1000) return `${ms}ms`;
        const seconds = Math.floor(ms / 1000);
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds}s`;
    };

    // Gera opções para gráficos
    const generateChartOptions = (title: string, customOptions = {}) => {
        return {
            ...ANALYTICS_CONFIG.DEFAULT_CHART_OPTIONS,
            plugins: {
                ...ANALYTICS_CONFIG.DEFAULT_CHART_OPTIONS.plugins,
                title: {
                    display: true,
                    text: title,
                },
            },
            ...customOptions,
        };
    };

    // Gera dados para gráfico de distribuição de mensagens
    const generateMessageDistributionData = (stats: ConversationStats) => {
        return {
            labels: ['Usuário', 'Assistente'],
            datasets: [
                {
                    data: [stats.user_message_count, stats.assistant_message_count],
                    backgroundColor: [
                        ANALYTICS_CONFIG.CHART_COLORS[0],
                        ANALYTICS_CONFIG.CHART_COLORS[1],
                    ],
                },
            ],
        };
    };

    // Gera dados para gráfico de tópicos populares
    const generatePopularTopicsData = (topics: PopularTopic[]) => {
        return {
            labels: topics.map(topic => topic.topic),
            datasets: [
                {
                    label: 'Contagem',
                    data: topics.map(topic => topic.count),
                    backgroundColor: ANALYTICS_CONFIG.CHART_COLORS,
                },
            ],
        };
    };

    return {
        useSystemOverview,
        usePopularTopics,
        useConversationStats,
        formatDuration,
        generateChartOptions,
        generateMessageDistributionData,
        generatePopularTopicsData,
    };
};

export default useAnalytics; 