import React, { useState, useRef, useEffect } from 'react';
import {
    Box,
    Paper,
    TextField,
    IconButton,
    Typography,
    CircularProgress,
    Divider,
    Alert,
    Snackbar,
} from '@mui/material';
import {
    Send as SendIcon,
    AttachFile as AttachFileIcon,
} from '@mui/icons-material';
import ChatMessage from './ChatMessage';
import { useConversation } from '../../hooks';
import type { Message } from '../../types/hooks';
import axios from 'axios';

// Constantes
const ALLOWED_FILE_TYPES = ['.pdf', '.txt', '.doc', '.docx'];

// Interfaces
interface ChatWindowProps {
    conversationId?: string;
    onConversationCreated?: (id: string) => void;
}

interface UploadResponse {
    id: string;
    filename: string;
    size: number;
    upload_date: string;
}

/**
 * Componente ChatWindow - Exibe a interface de chat com mensagens e controles de entrada
 */
const ChatWindow: React.FC<ChatWindowProps> = ({ conversationId, onConversationCreated }) => {
    // Estados
    const [message, setMessage] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [localConversationId, setLocalConversationId] = useState<string | undefined>(conversationId);
    const [messages, setMessages] = useState<Message[]>([]);

    // Refs
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Hooks
    const {
        createConversationMutation,
        sendMessage,
        messagesQuery
    } = useConversation(localConversationId);

    // Efeitos
    useEffect(() => {
        if (messagesQuery?.data) {
            setMessages(messagesQuery.data);
        }
    }, [messagesQuery?.data]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        setLocalConversationId(conversationId);
    }, [conversationId]);

    // Funções auxiliares
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    /**
     * Cria uma mensagem temporária do usuário para exibição imediata
     */
    const createTempUserMessage = (content: string): Message => ({
        id: Date.now().toString(),
        role: 'user',
        content,
        conversation_id: localConversationId || 'temp',
        created_at: new Date().toISOString(),
    });

    /**
     * Remove uma mensagem temporária da lista em caso de erro
     */
    const removeTempMessage = (messageId: string) => {
        setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
    };

    /**
     * Gerencia o envio de mensagem em uma conversa existente
     */
    const handleSendInExistingConversation = async (messageText: string, tempMessage: Message) => {
        try {
            await sendMessage(messageText);
            // Atualiza as mensagens após enviar
            messagesQuery?.refetch();
        } catch (error) {
            setError("Erro ao enviar mensagem: " + (error instanceof Error ? error.message : "Erro de conexão com o servidor"));
            removeTempMessage(tempMessage.id);
        }
    };

    /**
     * Gerencia a criação de uma nova conversa e envio da primeira mensagem
     */
    const handleCreateConversationAndSendMessage = async (messageText: string, tempMessage: Message) => {
        try {
            // Cria a conversa
            const newConversation = await createConversationMutation.mutateAsync("Nova Conversa");
            
            // Atualiza o ID da conversa
            setLocalConversationId(newConversation.id);
            onConversationCreated?.(newConversation.id);
            
            try {
                // Envia a mensagem usando o novo ID explicitamente
                const response = await sendMessage(messageText, newConversation.id);
                messagesQuery?.refetch();
                return response;
            } catch (error) {
                setError("Erro ao enviar mensagem: " + (error instanceof Error ? error.message : "Erro de conexão com o servidor"));
                removeTempMessage(tempMessage.id);
            }
        } catch (error) {
            setError("Erro ao criar conversa: " + (error instanceof Error ? error.message : "Erro de conexão com o servidor"));
            removeTempMessage(tempMessage.id);
            throw error;
        }
    };

    /**
     * Gerencia o envio de mensagens
     */
    const handleSendMessage = async () => {
        if (message.trim() && !messagesQuery?.isLoading && !createConversationMutation.isPending) {
            try {
                setError(null);
                const messageText = message.trim();
                setMessage('');

                // Cria a mensagem do usuário localmente
                const tempUserMessage = createTempUserMessage(messageText);
                
                // Adiciona a mensagem do usuário imediatamente
                setMessages((prev) => [...prev, tempUserMessage]);
                
                // Se não houver conversationId, cria uma nova conversa
                if (!localConversationId) {
                    await handleCreateConversationAndSendMessage(messageText, tempUserMessage);
                } else {
                    await handleSendInExistingConversation(messageText, tempUserMessage);
                }
            } catch (error) {
                console.error('Erro ao enviar mensagem:', error);
                setError("Erro ao enviar mensagem: " + (error instanceof Error ? error.message : "Erro de conexão com o servidor"));
            }
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleAttachClick = () => {
        fileInputRef.current?.click();
    };

    /**
     * Gerencia o upload de arquivos
     */
    const handleFileUpload = async (file: File): Promise<UploadResponse> => {
        try {
            setIsUploading(true);
            const formData = new FormData();
            formData.append('file', file);
            const response = await axios.post<UploadResponse>('/api/documents/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            console.error('Erro ao fazer upload do arquivo:', error);
            throw error;
        } finally {
            setIsUploading(false);
        }
    };

    // Renderização do componente
    return (
        <Paper
            elevation={2}
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2,
                overflow: 'hidden',
            }}
        >
            {/* Cabeçalho */}
            <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
                <Typography variant="h6">Chat</Typography>
            </Box>
            <Divider />

            {/* Área de mensagens */}
            <Box
                sx={{
                    flex: 1,
                    overflow: 'auto',
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                }}
            >
                {messages?.map((msg, index) => (
                    <ChatMessage
                        key={index}
                        message={msg}
                        isUser={msg.role === 'user'}
                    />
                ))}
                <div ref={messagesEndRef} />
            </Box>

            {/* Área de input */}
            <Box
                sx={{
                    p: 2,
                    bgcolor: 'background.paper',
                    display: 'flex',
                    gap: 1,
                    alignItems: 'flex-end',
                }}
            >
                <IconButton
                    color="primary"
                    onClick={handleAttachClick}
                    disabled={isUploading}
                >
                    <AttachFileIcon />
                </IconButton>

                <TextField
                    fullWidth
                    multiline
                    maxRows={4}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Digite sua mensagem..."
                    disabled={messagesQuery?.isLoading || createConversationMutation.isPending}
                    sx={{ flex: 1 }}
                />

                <IconButton
                    color="primary"
                    onClick={handleSendMessage}
                    disabled={!message.trim() || messagesQuery?.isLoading || createConversationMutation.isPending}
                >
                    {(messagesQuery?.isLoading || createConversationMutation.isPending) ? <CircularProgress size={24} /> : <SendIcon />}
                </IconButton>
            </Box>

            {/* Snackbar para erros */}
            <Snackbar 
                open={!!error} 
                autoHideDuration={6000} 
                onClose={() => setError(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
                    {error}
                </Alert>
            </Snackbar>

            {/* Input de arquivo oculto */}
            <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload(file);
                }}
                accept={ALLOWED_FILE_TYPES.join(',')}
            />
        </Paper>
    );
};

export default ChatWindow; 