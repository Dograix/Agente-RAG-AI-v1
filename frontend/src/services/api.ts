import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_CONFIG } from '../config';

class ApiService {
    private api: AxiosInstance;

    constructor() {
        this.api = axios.create({
            baseURL: API_CONFIG.BASE_URL,
            timeout: API_CONFIG.REQUEST_TIMEOUT,
            headers: API_CONFIG.DEFAULT_HEADERS,
        });

        this.setupInterceptors();
    }

    private setupInterceptors(): void {
        // Interceptor de requisição
        this.api.interceptors.request.use(
            (config) => {
                // Adiciona token de autenticação se necessário
                const token = localStorage.getItem('token');
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => {
                return Promise.reject(error);
            }
        );

        // Interceptor de resposta
        this.api.interceptors.response.use(
            (response) => response,
            async (error: AxiosError) => {
                if (!error.response) {
                    throw new Error('NETWORK_ERROR');
                }

                switch (error.response.status) {
                    case 401:
                        // Redireciona para login se não autenticado
                        localStorage.removeItem('token');
                        window.location.href = '/login';
                        break;
                    case 403:
                        throw new Error('FORBIDDEN');
                    case 404:
                        throw new Error('NOT_FOUND');
                    case 422:
                        throw new Error('VALIDATION_ERROR');
                    default:
                        throw new Error('SERVER_ERROR');
                }
            }
        );
    }

    // Conversas
    async createConversation(title: string): Promise<AxiosResponse> {
        return this.api.post(API_CONFIG.ENDPOINTS.CREATE_CONVERSATION, { title });
    }

    async listConversations(page: number = 1, limit: number = 10): Promise<AxiosResponse> {
        return this.api.get(API_CONFIG.ENDPOINTS.LIST_CONVERSATIONS, {
            params: { skip: (page - 1) * limit, limit },
        });
    }

    async getConversation(id: string): Promise<AxiosResponse> {
        return this.api.get(API_CONFIG.ENDPOINTS.GET_CONVERSATION(id));
    }

    async deleteConversation(id: string): Promise<AxiosResponse> {
        return this.api.delete(API_CONFIG.ENDPOINTS.DELETE_CONVERSATION(id));
    }

    // Mensagens
    async sendMessage(conversationId: string, content: string): Promise<AxiosResponse> {
        return this.api.post(API_CONFIG.ENDPOINTS.SEND_MESSAGE(conversationId), {
            content,
            role: 'user',
        });
    }

    async listMessages(conversationId: string, page: number = 1, limit: number = 10): Promise<AxiosResponse> {
        return this.api.get(API_CONFIG.ENDPOINTS.LIST_MESSAGES(conversationId), {
            params: { skip: (page - 1) * limit, limit },
        });
    }

    // Documentos
    async uploadDocument(file: File): Promise<AxiosResponse> {
        const formData = new FormData();
        formData.append('file', file);
        return this.api.post(API_CONFIG.ENDPOINTS.UPLOAD_DOCUMENT, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    }

    async listDocuments(): Promise<AxiosResponse> {
        return this.api.get(API_CONFIG.ENDPOINTS.LIST_DOCUMENTS);
    }

    async deleteDocument(id: string): Promise<AxiosResponse> {
        return this.api.delete(API_CONFIG.ENDPOINTS.DELETE_DOCUMENT(id));
    }

    async getDocumentStatus(id: string): Promise<AxiosResponse> {
        return this.api.get(API_CONFIG.ENDPOINTS.DOCUMENT_STATUS(id));
    }

    // Analytics
    async getSystemOverview(): Promise<AxiosResponse> {
        return this.api.get(API_CONFIG.ENDPOINTS.SYSTEM_OVERVIEW);
    }

    async getPopularTopics(days: number = 7): Promise<AxiosResponse> {
        return this.api.get(API_CONFIG.ENDPOINTS.POPULAR_TOPICS, {
            params: { days },
        });
    }

    async getConversationStats(id: string): Promise<AxiosResponse> {
        return this.api.get(API_CONFIG.ENDPOINTS.CONVERSATION_STATS(id));
    }

    // Sistema
    async checkHealth(): Promise<AxiosResponse> {
        return this.api.get(API_CONFIG.ENDPOINTS.HEALTH);
    }

    async clearCache(): Promise<AxiosResponse> {
        return this.api.post(API_CONFIG.ENDPOINTS.CLEAR_CACHE);
    }
}

export const apiService = new ApiService();
export default apiService; 