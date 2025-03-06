import { UseMutationResult, UseQueryResult } from '@tanstack/react-query';

/**
 * Interface que representa uma conversa
 */
export interface Conversation {
    /** Identificador único da conversa */
    id: string;
    /** Título da conversa */
    title: string;
    /** Data de criação no formato ISO */
    created_at: string;
    /** Data da última atualização no formato ISO */
    updated_at: string;
}

/**
 * Interface que representa uma mensagem
 */
export interface Message {
    /** Identificador único da mensagem */
    id: string;
    /** Conteúdo da mensagem */
    content: string;
    /** Papel do remetente da mensagem */
    role: 'user' | 'assistant';
    /** Identificador da conversa à qual a mensagem pertence */
    conversation_id: string;
    /** Data de criação no formato ISO */
    created_at: string;
}

/**
 * Interface que define o retorno do hook useConversation
 */
export interface UseConversation {
    /** Mutação para criar uma nova conversa */
    createConversationMutation: UseMutationResult<Conversation, Error, string>;
    /** Função para enviar uma mensagem na conversa atual */
    sendMessage: (content: string, targetConversationId?: string) => Promise<Message>;
    /** Query para obter as mensagens da conversa atual */
    messagesQuery: UseQueryResult<Message[], Error>;
} 