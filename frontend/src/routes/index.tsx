import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../components/Layout/MainLayout';
import Chat from '../pages/Chat';
import Settings from '../pages/Settings';

const AppRoutes: React.FC = () => {
    return (
        <Routes>
            <Route path="/" element={<MainLayout />}>
                <Route index element={<Navigate to="/chat" replace />} />
                <Route path="chat" element={<Chat />} />
                <Route path="settings" element={<Settings />} />
            </Route>
        </Routes>
    );
};

export default AppRoutes; 