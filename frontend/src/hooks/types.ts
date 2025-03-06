import { UseMutationResult, UseQueryResult } from '@tanstack/react-query';

export interface Conversation {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
}

export interface Message {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    conversation_id: string;
    created_at: string;
}

export interface SystemOverview {
    total_conversations: number;
    total_messages: number;
    total_documents: number;
    recent_activity: Array<{
        type: string;
        timestamp: string;
        details: string;
    }>;
}

export interface PopularTopic {
    topic: string;
    count: number;
}

export interface Document {
    id: string;
    filename: string;
    file_type: string;
    size: number;
    status: 'processing' | 'ready' | 'error';
    created_at: string;
    updated_at: string;
}

export interface UseConversation {
    useCreateConversation: () => UseMutationResult<Conversation, Error, string>;
    sendMessage: (content: string) => Promise<Message>;
}

export interface UseAnalytics {
    useSystemOverview: () => UseQueryResult<SystemOverview, Error>;
    usePopularTopics: (days: number) => UseQueryResult<{ data: PopularTopic[]; total: number }, Error>;
}

export interface UseDocument {
    useDocuments: () => UseQueryResult<{ data: Document[]; total: number }, Error>;
    isValidFile: (file: File) => boolean;
    formatFileSize: (size: number) => string;
} 