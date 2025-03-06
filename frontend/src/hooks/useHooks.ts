import { useMutation, useQuery } from '@tanstack/react-query';
import { apiService } from '../services/apiService';
import type { 
    UseConversation,
    Conversation,
    Message
} from '../types/hooks';

/**
 * Hook para gerenciar conversas e mensagens
 * 
 * @param conversationId - ID opcional da conversa atual
 * @returns Objeto com funções e estados para gerenciar conversas
 */
export const useConversation = (conversationId?: string): UseConversation => {
    /**
     * Mutação para criar uma nova conversa
     */
    const createConversationMutation = useMutation({
        mutationFn: async (title: string) => {
            const { data } = await apiService.createConversation(title);
            return data as Conversation;
        },
        onError: (error) => {
            console.error('Erro ao criar conversa:', error);
        }
    });

    /**
     * Função para enviar mensagem em uma conversa existente
     * 
     * @param content - Conteúdo da mensagem a ser enviada
     * @param targetConversationId - ID opcional da conversa (sobrescreve o ID do hook)
     * @returns Promise com a mensagem enviada
     * @throws Error se não houver ID de conversa
     */
    const sendMessage = async (content: string, targetConversationId?: string): Promise<Message> => {
        const effectiveConversationId = targetConversationId || conversationId;
        
        if (!effectiveConversationId) {
            throw new Error('Conversation ID is required to send a message');
        }
        
        try {
            const { data } = await apiService.sendMessage(effectiveConversationId, content);
            return data as Message;
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            throw error;
        }
    };

    /**
     * Consulta para listar mensagens de uma conversa
     * Habilitada apenas se houver um conversationId
     */
    const messagesQuery = useQuery({
        queryKey: ['messages', conversationId || 'no-conversation'],
        queryFn: async () => {
            if (!conversationId) return [] as Message[];
            const { data } = await apiService.listMessages(conversationId);
            return data as Message[];
        },
        enabled: !!conversationId,
        refetchOnWindowFocus: false
    });

    return {
        createConversationMutation,
        sendMessage,
        messagesQuery
    };
}; 