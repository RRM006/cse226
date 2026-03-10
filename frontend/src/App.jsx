import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { supabase, onAuthStateChange } from './lib/supabase';
import AuthGuard from './components/AuthGuard';
import Login from './pages/Login';
import Upload from './pages/Upload';
import Result from './pages/Result';
import History from './pages/History';
import AdminPanel from './pages/AdminPanel';

function App() {
  useEffect(() => {
    const { data: { subscription } } = onAuthStateChange((event, session) => {
      if (event === 'SIGNED_OUT') {
        window.location.href = '/login';
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<AuthGuard><Navigate to="/upload" replace /></AuthGuard>} />
        <Route path="/upload" element={<AuthGuard><Upload /></AuthGuard>} />
        <Route path="/result/:scanId" element={<AuthGuard><Result /></AuthGuard>} />
        <Route path="/history" element={<AuthGuard><History /></AuthGuard>} />
        <Route path="/admin" element={<AuthGuard><AdminPanel /></AuthGuard>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
