import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiService } from '../services/api';
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from '../config';

export interface Message {
    id: number;
    content: string;
    role: 'user' | 'assistant';
    created_at: string;
    conversation_id: number;
}

export interface Conversation {
    id: number;
    title: string;
    created_at: string;
    updated_at: string;
}

export const useConversation = (conversationId?: string) => {
    const queryClient = useQueryClient();

    // Lista todas as conversas
    const useConversations = (page: number = 1, limit: number = 10) => {
        return useQuery(
            ['conversations', page, limit],
            () => apiService.listConversations(page, limit),
            {
                keepPreviousData: true,
                staleTime: 5000,
            }
        );
    };

    // Obtém uma conversa específica
    const useConversationDetails = (id: string) => {
        return useQuery(
            ['conversation', id],
            () => apiService.getConversation(id),
            {
                enabled: !!id,
                staleTime: 5000,
            }
        );
    };

    // Lista mensagens de uma conversa
    const useMessages = (conversationId: string, page: number = 1, limit: number = 10) => {
        return useQuery(
            ['messages', conversationId, page, limit],
            () => apiService.listMessages(conversationId, page, limit),
            {
                enabled: !!conversationId,
                keepPreviousData: true,
                staleTime: 5000,
            }
        );
    };

    // Cria uma nova conversa
    const useCreateConversation = () => {
        return useMutation(
            (title: string) => apiService.createConversation(title),
            {
                onSuccess: () => {
                    queryClient.invalidateQueries('conversations');
                },
            }
        );
    };

    // Envia uma mensagem
    const useSendMessage = () => {
        return useMutation(
            ({ conversationId, content }: { conversationId: string; content: string }) =>
                apiService.sendMessage(conversationId, content),
            {
                onSuccess: () => {
                    if (conversationId) {
                        queryClient.invalidateQueries(['messages', conversationId]);
                    }
                },
            }
        );
    };

    // Deleta uma conversa
    const useDeleteConversation = () => {
        return useMutation(
            (id: string) => apiService.deleteConversation(id),
            {
                onSuccess: () => {
                    queryClient.invalidateQueries('conversations');
                },
            }
        );
    };

    // Obtém estatísticas da conversa
    const useConversationStats = (id: string) => {
        return useQuery(
            ['conversation-stats', id],
            () => apiService.getConversationStats(id),
            {
                enabled: !!id,
                staleTime: 30000,
            }
        );
    };

    return {
        useConversations,
        useConversationDetails,
        useMessages,
        useCreateConversation,
        useSendMessage,
        useDeleteConversation,
        useConversationStats,
    };
};

export default useConversation; 