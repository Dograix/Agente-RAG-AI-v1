import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Home as HomeIcon } from '@mui/icons-material';

const NotFound: React.FC = () => {
    const navigate = useNavigate();

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '100vh',
                textAlign: 'center',
                p: 3,
            }}
        >
            <Typography
                variant="h1"
                sx={{
                    fontSize: '8rem',
                    fontWeight: 'bold',
                    color: 'primary.main',
                    mb: 2,
                }}
            >
                404
            </Typography>

            <Typography
                variant="h4"
                sx={{
                    mb: 2,
                    color: 'text.primary',
                }}
            >
                Página não encontrada
            </Typography>

            <Typography
                variant="body1"
                sx={{
                    mb: 4,
                    color: 'text.secondary',
                    maxWidth: 500,
                }}
            >
                A página que você está procurando não existe ou foi removida.
                Por favor, verifique o endereço ou retorne à página inicial.
            </Typography>

            <Button
                variant="contained"
                startIcon={<HomeIcon />}
                onClick={() => navigate('/')}
                size="large"
            >
                Voltar para o Início
            </Button>
        </Box>
    );
};

export default NotFound; 