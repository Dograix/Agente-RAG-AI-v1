import React, { useState, useRef, useEffect } from 'react';
import {
    Box,
    Paper,
    TextField,
    IconButton,
    Typography,
    CircularProgress,
    Divider,
} from '@mui/material';
import { Send as SendIcon, AttachFile as AttachFileIcon } from '@mui/icons-material';
import { useConversation } from '../../hooks/useConversation';
import { useDocument } from '../../hooks/useDocument';
import { UI_CONFIG } from '../../config';
import ChatMessage from './ChatMessage';
import FileUploadDialog from '../Documents/FileUploadDialog';

interface ChatWindowProps {
    conversationId: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ conversationId }) => {
    const [message, setMessage] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const {
        useMessages,
        useSendMessage,
    } = useConversation(conversationId);

    const { useUploadDocument } = useDocument();

    const {
        data: messagesData,
        isLoading: isLoadingMessages,
        error: messagesError,
    } = useMessages(conversationId);

    const {
        mutate: sendMessage,
        isLoading: isSending,
    } = useSendMessage();

    const {
        mutate: uploadDocument,
        isLoading: isUploadingDocument,
    } = useUploadDocument();

    // Rola para a última mensagem
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messagesData]);

    // Envia mensagem
    const handleSendMessage = async () => {
        if (!message.trim() || isSending) return;

        try {
            await sendMessage({ conversationId, content: message });
            setMessage('');
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
        }
    };

    // Lida com tecla Enter
    const handleKeyPress = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    };

    // Abre diálogo de upload
    const handleAttachClick = () => {
        fileInputRef.current?.click();
    };

    // Processa upload de arquivo
    const handleFileUpload = async (file: File) => {
        try {
            setIsUploading(true);
            await uploadDocument(file);
            // Envia mensagem informando sobre o upload
            await sendMessage({
                conversationId,
                content: `Arquivo enviado: ${file.name}`,
            });
        } catch (error) {
            console.error('Erro no upload:', error);
        } finally {
            setIsUploading(false);
        }
    };

    if (messagesError) {
        return (
            <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography color="error">
                    Erro ao carregar mensagens. Por favor, tente novamente.
                </Typography>
            </Box>
        );
    }

    return (
        <Paper
            elevation={3}
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.default',
            }}
        >
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
                {isLoadingMessages ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    messagesData?.data.map((msg: any) => (
                        <ChatMessage
                            key={msg.id}
                            message={msg}
                            isUser={msg.role === 'user'}
                        />
                    ))
                )}
                <div ref={messagesEndRef} />
            </Box>

            <Divider />

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
                    disabled={isUploading || isUploadingDocument}
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
                    disabled={isSending}
                    sx={{ flex: 1 }}
                />

                <IconButton
                    color="primary"
                    onClick={handleSendMessage}
                    disabled={!message.trim() || isSending}
                >
                    {isSending ? <CircularProgress size={24} /> : <SendIcon />}
                </IconButton>
            </Box>

            {/* Input de arquivo oculto */}
            <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload(file);
                }}
                accept={UI_CONFIG.DOCUMENTS.ALLOWED_FILE_TYPES.join(',')}
            />

            {/* Diálogo de upload */}
            <FileUploadDialog
                open={isUploading}
                onClose={() => setIsUploading(false)}
            />
        </Paper>
    );
};

export default ChatWindow; 