import { useConversation } from '../../src/hooks';
import { apiService } from '../../src/services/apiService';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import type { AxiosResponse } from 'axios';
import type { 
    Conversation, 
    Message
} from '../../src/types/hooks';

/**
 * Mocks e configurações para os testes
 */

// Mock do apiService
vi.mock('../../src/services/apiService', () => ({
    apiService: {
        createConversation: vi.fn(),
        sendMessage: vi.fn(),
        listConversations: vi.fn(),
        getConversation: vi.fn(),
        deleteConversation: vi.fn(),
        listMessages: vi.fn()
    }
}));

// Mock do React Query
vi.mock('@tanstack/react-query', () => ({
    useMutation: vi.fn().mockImplementation(({ mutationFn, onError }) => ({
        mutateAsync: async (arg: any) => mutationFn(arg),
        isLoading: false,
        isPending: false,
        isError: false,
        error: null
    })),
    useQuery: vi.fn().mockImplementation(({ queryFn, enabled }) => ({
        data: enabled ? [] : undefined,
        isLoading: false,
        isError: false,
        error: null,
        refetch: vi.fn()
    }))
}));

/**
 * Funções auxiliares para os testes
 */

// Função auxiliar para criar resposta do Axios
const createAxiosResponse = <T,>(data: T): AxiosResponse<T> => ({
    data,
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as any
});

// Dados de exemplo para testes
const mockConversation: Conversation = {
    id: '123',
    title: 'Test Conversation',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
};

const mockMessage: Message = {
    id: '456',
    content: 'Test message',
    role: 'user',
    conversation_id: '123',
    created_at: new Date().toISOString(),
};

const mockMessages: Message[] = [
    mockMessage,
    {
        id: '457',
        content: 'Response message',
        role: 'assistant',
        conversation_id: '123',
        created_at: new Date().toISOString(),
    }
];

/**
 * Testes do hook useConversation
 */
describe('useConversation', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('createConversation', () => {
        it('deve criar uma nova conversa', async () => {
            // Arrange
            vi.mocked(apiService.createConversation).mockResolvedValue(
                createAxiosResponse(mockConversation)
            );

            // Act
            const hook = useConversation();
            await hook.createConversationMutation.mutateAsync('Test Conversation');
            
            // Assert
            expect(hook.createConversationMutation).toBeDefined();
            expect(apiService.createConversation).toHaveBeenCalledWith('Test Conversation');
        });
    });

    describe('sendMessage', () => {
        it('deve enviar uma mensagem', async () => {
            // Arrange
            vi.mocked(apiService.sendMessage).mockResolvedValue(
                createAxiosResponse(mockMessage)
            );

            // Act
            const hook = useConversation('123');
            const message = await hook.sendMessage('Test message');
            
            // Assert
            expect(apiService.sendMessage).toHaveBeenCalledWith('123', 'Test message');
            expect(message).toEqual(mockMessage);
        });

        it('deve lançar erro quando não há conversationId', async () => {
            // Arrange
            const hook = useConversation();
            
            // Act & Assert
            await expect(hook.sendMessage('Test message')).rejects.toThrow('Conversation ID is required');
        });
    });

    describe('messagesQuery', () => {
        it('deve buscar mensagens de uma conversa', async () => {
            // Arrange
            vi.mocked(apiService.listMessages).mockResolvedValue(
                createAxiosResponse(mockMessages)
            );

            // Act
            const hook = useConversation('123');
            
            // Assert
            expect(hook.messagesQuery).toBeDefined();
        });

        it('deve estar desabilitado quando não há conversationId', () => {
            // Arrange & Act
            const hook = useConversation();
            
            // Assert
            expect(hook.messagesQuery.data).toBeUndefined();
        });
    });
}); 