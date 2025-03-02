import React from 'react';
import {
    Grid,
    Paper,
    Typography,
    Box,
    CircularProgress,
    List,
    ListItem,
    ListItemText,
    Divider,
} from '@mui/material';
import {
    Chat as ChatIcon,
    Message as MessageIcon,
    Description as DocumentIcon,
    Timeline as TimelineIcon,
} from '@mui/icons-material';
import { useAnalytics } from '../../hooks/useAnalytics';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const StatCard: React.FC<{
    title: string;
    value: number | string;
    icon: React.ReactNode;
    color: string;
}> = ({ title, value, icon, color }) => (
    <Paper
        elevation={2}
        sx={{
            p: 2,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 2,
        }}
    >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box
                sx={{
                    bgcolor: `${color}15`,
                    borderRadius: 1,
                    p: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                }}
            >
                {React.cloneElement(icon as React.ReactElement, {
                    sx: { color },
                })}
            </Box>
            <Typography
                variant="h6"
                sx={{
                    ml: 2,
                    color: 'text.primary',
                    fontWeight: 'medium',
                }}
            >
                {title}
            </Typography>
        </Box>
        <Typography
            variant="h4"
            sx={{
                mt: 'auto',
                color: 'text.primary',
                fontWeight: 'bold',
            }}
        >
            {value}
        </Typography>
    </Paper>
);

const SystemStats: React.FC = () => {
    const { useSystemOverview } = useAnalytics();
    const { data, isLoading, error } = useSystemOverview();

    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (error || !data) {
        return (
            <Typography color="error" align="center">
                Erro ao carregar estatísticas do sistema.
            </Typography>
        );
    }

    const stats = data.data;

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h5" sx={{ mb: 3 }}>
                Visão Geral do Sistema
            </Typography>

            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Conversas"
                        value={stats.total_conversations}
                        icon={<ChatIcon />}
                        color="#2563eb"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Mensagens"
                        value={stats.total_messages}
                        icon={<MessageIcon />}
                        color="#10b981"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Documentos"
                        value={stats.total_documents}
                        icon={<DocumentIcon />}
                        color="#f59e0b"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Taxa de Resposta"
                        value="95%"
                        icon={<TimelineIcon />}
                        color="#6366f1"
                    />
                </Grid>
            </Grid>

            <Paper elevation={2} sx={{ borderRadius: 2 }}>
                <Box sx={{ p: 2 }}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Atividade Recente
                    </Typography>
                </Box>
                <Divider />
                <List>
                    {stats.recent_activity.map((activity, index) => (
                        <React.Fragment key={index}>
                            <ListItem>
                                <ListItemText
                                    primary={activity.action}
                                    secondary={
                                        <>
                                            {activity.details}
                                            <br />
                                            {format(
                                                new Date(activity.timestamp),
                                                "dd 'de' MMMM 'às' HH:mm",
                                                { locale: ptBR }
                                            )}
                                        </>
                                    }
                                />
                            </ListItem>
                            {index < stats.recent_activity.length - 1 && <Divider />}
                        </React.Fragment>
                    ))}
                </List>
            </Paper>
        </Box>
    );
};

export default SystemStats; 