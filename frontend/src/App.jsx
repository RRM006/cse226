import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { supabase, onAuthStateChange } from './lib/supabase';
import Login from './pages/Login';
import AuthCallback from './pages/AuthCallback';
import Upload from './pages/Upload';
import Result from './pages/Result';
import History from './pages/History';
import AdminPanel from './pages/AdminPanel';

function AuthHandler() {
  const navigate = useNavigate();
  
  useEffect(() => {
    const { data: { subscription } } = onAuthStateChange((event) => {
      if (event === 'SIGNED_OUT') {
        navigate('/login');
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);
  
  return null;
}

function App() {
  return (
    <BrowserRouter>
      <AuthHandler />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/" element={<Navigate to="/upload" replace />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/result/:scanId" element={<Result />} />
        <Route path="/history" element={<History />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
