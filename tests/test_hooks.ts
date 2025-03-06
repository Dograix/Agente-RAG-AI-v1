import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useConversation, useAnalytics, useDocument } from '../frontend/src/hooks';
import { apiService } from '../frontend/src/services/apiService';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import React, { ReactNode } from 'react';
import type { 
    Conversation, 
    Message, 
    SystemOverview, 
    PopularTopic, 
    Document 
} from '../frontend/src/types/hooks';

// Mock do apiService
vi.mock('../frontend/src/services/apiService', () => ({
    apiService: {
        listConversations: vi.fn(),
        getConversation: vi.fn(),
        createConversation: vi.fn(),
        sendMessage: vi.fn(),
        deleteConversation: vi.fn(),
        listMessages: vi.fn(),
        getSystemOverview: vi.fn(),
        getPopularTopics: vi.fn(),
        listDocuments: vi.fn(),
        uploadDocument: vi.fn(),
        deleteDocument: vi.fn(),
    }
}));

// Wrapper para o React Query
const createWrapper = () => {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
            },
        },
    });

    const Wrapper = ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );

    return Wrapper;
};

describe('useConversation', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('deve criar uma nova conversa', async () => {
        const mockConversation: Conversation = {
            id: '123',
            title: 'Test Conversation',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };

        vi.mocked(apiService.createConversation).mockResolvedValueOnce({ data: mockConversation });

        const { result } = renderHook(
            () => useConversation(),
            { wrapper: createWrapper() }
        );

        const createMutation = result.current.useCreateConversation();
        
        await createMutation.mutateAsync('Test Conversation');

        expect(apiService.createConversation).toHaveBeenCalledWith('Test Conversation');
    });

    it('deve enviar uma mensagem', async () => {
        const mockMessage: Message = {
            id: '456',
            content: 'Test message',
            role: 'user',
            conversation_id: '123',
            created_at: new Date().toISOString(),
        };

        vi.mocked(apiService.sendMessage).mockResolvedValueOnce({ data: mockMessage });

        const { result } = renderHook(
            () => useConversation('123'),
            { wrapper: createWrapper() }
        );

        await result.current.sendMessage('Test message');

        expect(apiService.sendMessage).toHaveBeenCalledWith('123', 'Test message');
    });
});

describe('useAnalytics', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('deve buscar visão geral do sistema', async () => {
        const mockOverview: SystemOverview = {
            total_conversations: 10,
            total_messages: 50,
            total_documents: 5,
            recent_activity: []
        };

        vi.mocked(apiService.getSystemOverview).mockResolvedValueOnce({ data: mockOverview });

        const { result, waitFor } = renderHook(
            () => useAnalytics().useSystemOverview(),
            { wrapper: createWrapper() }
        );

        await waitFor(() => result.current.isSuccess);

        expect(result.current.data).toEqual(mockOverview);
    });

    it('deve buscar tópicos populares', async () => {
        const mockTopics = {
            data: [
                { topic: 'Test', count: 5 } as PopularTopic
            ],
            total: 1
        };

        vi.mocked(apiService.getPopularTopics).mockResolvedValueOnce({ data: mockTopics });

        const { result, waitFor } = renderHook(
            () => useAnalytics().usePopularTopics(7),
            { wrapper: createWrapper() }
        );

        await waitFor(() => result.current.isSuccess);

        expect(result.current.data).toEqual(mockTopics);
    });
});

describe('useDocument', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('deve listar documentos', async () => {
        const mockDocuments = {
            data: [
                {
                    id: '789',
                    filename: 'test.pdf',
                    file_type: 'pdf',
                    size: 1024,
                    status: 'ready',
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                } as Document
            ],
            total: 1
        };

        vi.mocked(apiService.listDocuments).mockResolvedValueOnce({ data: mockDocuments });

        const { result, waitFor } = renderHook(
            () => useDocument().useDocuments(),
            { wrapper: createWrapper() }
        );

        await waitFor(() => result.current.isSuccess);

        expect(result.current.data).toEqual(mockDocuments);
    });

    it('deve validar arquivo corretamente', () => {
        const { result } = renderHook(() => useDocument());

        const validFile = new File(['test'], 'test.pdf', { type: 'application/pdf' });
        const invalidFile = new File(['test'], 'test.exe', { type: 'application/x-msdownload' });

        expect(result.current.isValidFile(validFile)).toBe(true);
        expect(result.current.isValidFile(invalidFile)).toBe(false);
    });

    it('deve formatar tamanho do arquivo corretamente', () => {
        const { result } = renderHook(() => useDocument());

        expect(result.current.formatFileSize(1024)).toBe('1 KB');
        expect(result.current.formatFileSize(1024 * 1024)).toBe('1 MB');
    });
}); 