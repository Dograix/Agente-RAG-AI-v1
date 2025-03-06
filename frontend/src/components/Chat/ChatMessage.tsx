import React from 'react';
import { Box, Paper, Typography, Avatar } from '@mui/material';
import { Person as PersonIcon, SmartToy as BotIcon } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
}

interface ChatMessageProps {
    message: Message;
    isUser: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser }) => {
    return (
        <Box
            sx={{
                display: 'flex',
                gap: 2,
                alignItems: 'flex-start',
                flexDirection: isUser ? 'row-reverse' : 'row',
            }}
        >
            <Avatar
                sx={{
                    bgcolor: isUser ? 'primary.main' : 'secondary.main',
                }}
            >
                {isUser ? <PersonIcon /> : <BotIcon />}
            </Avatar>

            <Paper
                elevation={1}
                sx={{
                    p: 2,
                    maxWidth: '70%',
                    bgcolor: isUser ? 'primary.dark' : 'background.paper',
                    borderRadius: 2,
                }}
            >
                <Typography
                    component="div"
                    sx={{
                        '& p': { m: 0 },
                        '& pre': {
                            p: 1,
                            borderRadius: 1,
                            bgcolor: 'background.default',
                            overflow: 'auto',
                        },
                        '& code': {
                            fontFamily: 'monospace',
                            p: 0.5,
                            borderRadius: 0.5,
                            bgcolor: 'background.default',
                        },
                    }}
                >
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </Typography>

                {message.timestamp && (
                    <Typography
                        variant="caption"
                        sx={{
                            display: 'block',
                            mt: 1,
                            textAlign: isUser ? 'right' : 'left',
                            color: 'text.secondary',
                        }}
                    >
                        {new Date(message.timestamp).toLocaleTimeString()}
                    </Typography>
                )}
            </Paper>
        </Box>
    );
};

export default ChatMessage;

 