import React from 'react';
import { Box, Paper, Typography, Avatar } from '@mui/material';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { UI_CONFIG } from '../../config';
import { Message } from '../../hooks/useConversation';

interface ChatMessageProps {
    message: Message;
    isUser: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser }) => {
    const formattedTime = format(
        new Date(message.created_at),
        'HH:mm',
        { locale: ptBR }
    );

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: isUser ? 'row-reverse' : 'row',
                gap: 1,
                maxWidth: '80%',
                alignSelf: isUser ? 'flex-end' : 'flex-start',
            }}
        >
            <Avatar
                sx={{
                    bgcolor: isUser ? 'primary.main' : 'secondary.main',
                    width: 32,
                    height: 32,
                }}
            >
                {isUser ? 'U' : 'A'}
            </Avatar>

            <Box sx={{ maxWidth: 'calc(100% - 40px)' }}>
                <Paper
                    elevation={1}
                    sx={{
                        p: 1.5,
                        bgcolor: isUser ? 'primary.light' : 'background.paper',
                        borderRadius: 2,
                        borderTopRightRadius: isUser ? 0 : 2,
                        borderTopLeftRadius: isUser ? 2 : 0,
                    }}
                >
                    <Typography
                        variant="body1"
                        sx={{
                            color: isUser ? 'primary.contrastText' : 'text.primary',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                        }}
                    >
                        {message.content}
                    </Typography>
                </Paper>

                <Typography
                    variant="caption"
                    sx={{
                        mt: 0.5,
                        display: 'block',
                        textAlign: isUser ? 'right' : 'left',
                        color: 'text.secondary',
                    }}
                >
                    {formattedTime}
                </Typography>
            </Box>
        </Box>
    );
};

 