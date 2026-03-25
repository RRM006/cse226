import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { supabase, onAuthStateChange } from './lib/supabase';
import Login from './pages/Login';
import AuthCallback from './pages/AuthCallback';
import Upload from './pages/Upload';
import Result from './pages/Result';
import History from './pages/History';
import AdminPanel from './pages/AdminPanel';
import AuthGuard from './components/AuthGuard';

function RootRoute() {
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  useEffect(() => {
    const checkSession = async () => {
      const { data } = await supabase?.auth.getSession();
      const email = data?.session?.user?.email;
      const isNsuEmail = email?.toLowerCase().endsWith('@northsouth.edu');
      
      // Invalidate session if not NSU email
      if (data?.session && !isNsuEmail) {
        await supabase?.auth.signOut();
        setSession(null);
      } else {
        setSession(data?.session);
      }
      setLoading(false);
    };
    checkSession();
  }, []);

  if (loading) return null;
  
  // After signout, redirect to login
  return <Navigate to={session ? "/upload" : "/login"} replace />;
}

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
        <Route path="/" element={<RootRoute />} />
        <Route path="/upload" element={<AuthGuard><Upload /></AuthGuard>} />
        <Route path="/result/:scanId" element={<AuthGuard><Result /></AuthGuard>} />
        <Route path="/history" element={<AuthGuard><History /></AuthGuard>} />
        <Route path="/admin" element={<AuthGuard><AdminPanel /></AuthGuard>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
