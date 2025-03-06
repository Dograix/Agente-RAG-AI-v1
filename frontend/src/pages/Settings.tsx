import React, { useState } from 'react';
import {
    Box,
    Typography,
    Paper,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Switch,
    Button,
    Divider,
    Alert,
} from '@mui/material';
import {
    DarkMode as DarkModeIcon,
    Notifications as NotificationsIcon,
    Delete as DeleteIcon,
} from '@mui/icons-material';

const Settings: React.FC = () => {
    const [darkMode, setDarkMode] = useState(true);
    const [notifications, setNotifications] = useState(true);
    const [showAlert, setShowAlert] = useState(false);

    const handleClearCache = () => {
        // Implementar limpeza do cache
        setShowAlert(true);
        setTimeout(() => setShowAlert(false), 3000);
    };

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
                Configurações
            </Typography>

            {showAlert && (
                <Alert
                    severity="success"
                    sx={{ mb: 3 }}
                    onClose={() => setShowAlert(false)}
                >
                    Cache do sistema limpo com sucesso!
                </Alert>
            )}

            <Paper sx={{ mb: 3 }}>
                <List>
                    <ListItem>
                        <ListItemIcon>
                            <DarkModeIcon />
                        </ListItemIcon>
                        <ListItemText
                            primary="Modo Escuro"
                            secondary="Ativar tema escuro na interface"
                        />
                        <Switch
                            edge="end"
                            checked={darkMode}
                            onChange={(e) => setDarkMode(e.target.checked)}
                        />
                    </ListItem>

                    <Divider />

                    <ListItem>
                        <ListItemIcon>
                            <NotificationsIcon />
                        </ListItemIcon>
                        <ListItemText
                            primary="Notificações"
                            secondary="Receber notificações do sistema"
                        />
                        <Switch
                            edge="end"
                            checked={notifications}
                            onChange={(e) => setNotifications(e.target.checked)}
                        />
                    </ListItem>
                </List>
            </Paper>

            <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                    Cache do Sistema
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                    Limpar o cache do sistema pode ajudar a resolver problemas de desempenho,
                    mas pode tornar o sistema mais lento temporariamente enquanto o cache é
                    reconstruído.
                </Typography>
                <Button
                    variant="outlined"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={handleClearCache}
                >
                    Limpar Cache
                </Button>
            </Paper>
        </Box>
    );
};

export default Settings; 