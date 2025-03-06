import axios, { AxiosInstance } from 'axios';
import { API_CONFIG } from '../config';

class ApiService {
    private api: AxiosInstance;

    constructor() {
        this.api = axios.create({
            baseURL: API_CONFIG.API_BASE_URL,
            headers: API_CONFIG.DEFAULT_HEADERS,
            timeout: API_CONFIG.REQUEST_TIMEOUT,
        });
    }

    // Conversas
    async listConversations() {
        return this.api.get(API_CONFIG.ENDPOINTS.CONVERSATIONS);
    }

    async getConversation(id: string) {
        return this.api.get(`${API_CONFIG.ENDPOINTS.CONVERSATIONS}/${id}`);
    }

    async createConversation(title: string) {
        return this.api.post(API_CONFIG.ENDPOINTS.CONVERSATIONS, { title });
    }

    async deleteConversation(id: string) {
        return this.api.delete(`${API_CONFIG.ENDPOINTS.CONVERSATIONS}/${id}`);
    }

    // Mensagens
    async listMessages(conversationId: string) {
        return this.api.get(`${API_CONFIG.ENDPOINTS.CONVERSATIONS}/${conversationId}/messages`);
    }

    async sendMessage(conversationId: string, content: string) {
        return this.api.post(`${API_CONFIG.ENDPOINTS.CONVERSATIONS}/${conversationId}/messages`, {
            content,
            role: 'user'
        });
    }
}

export const apiService = new ApiService(); 