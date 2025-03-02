import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from '../components/Layout';
import ChatWindow from '../components/Chat/ChatWindow';
import SystemStats from '../components/Analytics/SystemStats';
import AnalyticsCharts from '../components/Analytics/AnalyticsCharts';
import DocumentList from '../components/Documents/DocumentList';
import NotFound from '../components/NotFound';

const AppRoutes: React.FC = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout />}>
                    {/* Redireciona a rota raiz para /chat */}
                    <Route index element={<Navigate to="/chat" replace />} />

                    {/* Rotas do Chat */}
                    <Route path="chat" element={<ChatWindow conversationId="default" />} />
                    <Route path="chat/:conversationId" element={<ChatWindow conversationId="default" />} />

                    {/* Rotas de Analytics */}
                    <Route path="analytics" element={<SystemStats />} />
                    <Route path="analytics/charts" element={<AnalyticsCharts />} />

                    {/* Rotas de Documentos */}
                    <Route path="documents" element={<DocumentList />} />

                    {/* Rota 404 */}
                    <Route path="*" element={<NotFound />} />
                </Route>
            </Routes>
        </BrowserRouter>
    );
};

export default AppRoutes; 