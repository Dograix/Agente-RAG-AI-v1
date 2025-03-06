import React from 'react';
import { Box } from '@mui/material';
import ChatWindow from '../components/Chat/ChatWindow';

const Chat: React.FC = () => {
    return (
        <Box sx={{ height: '100%', p: 2 }}>
            <ChatWindow />
        </Box>
    );
};

export default Chat; 