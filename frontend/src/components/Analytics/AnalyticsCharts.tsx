import React from 'react';
import {
    Grid,
    Paper,
    Typography,
    Box,
    CircularProgress,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
} from '@mui/material';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';
import { useAnalytics } from '../../hooks/useAnalytics';
import { ANALYTICS_CONFIG } from '../../config';

// Registra os componentes do Chart.js
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

const AnalyticsCharts: React.FC = () => {
    const [timeRange, setTimeRange] = React.useState(ANALYTICS_CONFIG.TIME_RANGES.LAST_7_DAYS);
    const { usePopularTopics, useSystemOverview, generateChartOptions } = useAnalytics();

    const { data: topicsData, isLoading: isLoadingTopics } = usePopularTopics(
        parseInt(timeRange)
    );

    const { data: overviewData, isLoading: isLoadingOverview } = useSystemOverview();

    if (isLoadingTopics || isLoadingOverview) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    const messageDistributionData = {
        labels: ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'],
        datasets: [
            {
                label: 'Mensagens',
                data: [65, 59, 80, 81, 56, 55, 40],
                fill: false,
                borderColor: ANALYTICS_CONFIG.CHART_COLORS[0],
                tension: 0.1,
            },
        ],
    };

    const topicDistributionData = {
        labels: topicsData?.data.map((topic: any) => topic.topic) || [],
        datasets: [
            {
                label: 'Tópicos',
                data: topicsData?.data.map((topic: any) => topic.count) || [],
                backgroundColor: ANALYTICS_CONFIG.CHART_COLORS,
            },
        ],
    };

    const responseTimeData = {
        labels: ['0-1s', '1-2s', '2-3s', '3-4s', '4-5s', '>5s'],
        datasets: [
            {
                label: 'Tempo de Resposta',
                data: [30, 40, 20, 5, 3, 2],
                backgroundColor: ANALYTICS_CONFIG.CHART_COLORS[2],
            },
        ],
    };

    return (
        <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h5">Análise de Dados</Typography>
                <FormControl sx={{ minWidth: 200 }}>
                    <InputLabel>Período</InputLabel>
                    <Select
                        value={timeRange}
                        label="Período"
                        onChange={(e) => setTimeRange(e.target.value)}
                    >
                        <MenuItem value={ANALYTICS_CONFIG.TIME_RANGES.LAST_24_HOURS}>
                            Últimas 24 horas
                        </MenuItem>
                        <MenuItem value={ANALYTICS_CONFIG.TIME_RANGES.LAST_7_DAYS}>
                            Últimos 7 dias
                        </MenuItem>
                        <MenuItem value={ANALYTICS_CONFIG.TIME_RANGES.LAST_30_DAYS}>
                            Últimos 30 dias
                        </MenuItem>
                        <MenuItem value={ANALYTICS_CONFIG.TIME_RANGES.LAST_90_DAYS}>
                            Últimos 90 dias
                        </MenuItem>
                    </Select>
                </FormControl>
            </Box>

            <Grid container spacing={3}>
                {/* Distribuição de Mensagens */}
                <Grid item xs={12} md={6}>
                    <Paper
                        elevation={2}
                        sx={{
                            p: 2,
                            height: 400,
                            display: 'flex',
                            flexDirection: 'column',
                            borderRadius: 2,
                        }}
                    >
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Distribuição de Mensagens
                        </Typography>
                        <Box sx={{ flex: 1, position: 'relative' }}>
                            <Line
                                data={messageDistributionData}
                                options={generateChartOptions('Mensagens por Dia')}
                            />
                        </Box>
                    </Paper>
                </Grid>

                {/* Distribuição de Tópicos */}
                <Grid item xs={12} md={6}>
                    <Paper
                        elevation={2}
                        sx={{
                            p: 2,
                            height: 400,
                            display: 'flex',
                            flexDirection: 'column',
                            borderRadius: 2,
                        }}
                    >
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Tópicos Populares
                        </Typography>
                        <Box sx={{ flex: 1, position: 'relative' }}>
                            <Pie
                                data={topicDistributionData}
                                options={generateChartOptions('Distribuição de Tópicos')}
                            />
                        </Box>
                    </Paper>
                </Grid>

                {/* Tempo de Resposta */}
                <Grid item xs={12}>
                    <Paper
                        elevation={2}
                        sx={{
                            p: 2,
                            height: 400,
                            display: 'flex',
                            flexDirection: 'column',
                            borderRadius: 2,
                        }}
                    >
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Tempo de Resposta
                        </Typography>
                        <Box sx={{ flex: 1, position: 'relative' }}>
                            <Bar
                                data={responseTimeData}
                                options={generateChartOptions('Distribuição do Tempo de Resposta')}
                            />
                        </Box>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default AnalyticsCharts; 