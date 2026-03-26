import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { supabase, onAuthStateChange, getStudentToken } from './lib/supabase';
import Login from './pages/Login';
import AuthCallback from './pages/AuthCallback';
import Upload from './pages/Upload';
import Result from './pages/Result';
import History from './pages/History';
import AdminPanel from './pages/AdminPanel';
import AuthGuard from './components/AuthGuard';

// Student pages
import StudentLogin from './pages/StudentLogin';
import StudentDashboard from './pages/StudentDashboard';
import StudentAuditResults from './pages/StudentAuditResults';
import StudentRequests from './pages/StudentRequests';
import ChangePassword from './pages/ChangePassword';

// Admin pages
import ManageStudents from './pages/ManageStudents';
import AdminRequests from './pages/AdminRequests';
import AdminAuditResults from './pages/AdminAuditResults';

function RootRoute() {
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  useEffect(() => {
    const checkSession = async () => {
      // Check if student is logged in
      if (getStudentToken()) {
        setSession({ type: 'student' });
        setLoading(false);
        return;
      }

      if (!supabase) {
        setSession(null);
        setLoading(false);
        return;
      }

      try {
        const { data } = await supabase.auth.getSession();
        const email = data?.session?.user?.email;
        const isNsuEmail = email?.toLowerCase().endsWith('@northsouth.edu');
        
        // Invalidate session if not NSU email
        if (data?.session && !isNsuEmail) {
          await supabase.auth.signOut();
          setSession(null);
        } else {
          setSession(data?.session ? { type: 'admin' } : null);
        }
      } catch (error) {
        console.error("Error fetching session:", error);
        setSession(null);
      } finally {
        setLoading(false);
      }
    };
    checkSession();
  }, []);

  if (loading) return null;
  
  // Redirect based on user type
  if (session?.type === 'student') return <Navigate to="/student/dashboard" replace />;
  if (session?.type === 'admin') return <Navigate to="/upload" replace />;
  return <Navigate to="/login" replace />;
}

function AuthHandler() {
  const navigate = useNavigate();
  
  useEffect(() => {
    const result = onAuthStateChange((event) => {
      if (event === 'SIGNED_OUT') {
        navigate('/login');
      }
    });

    return () => {
      if (result?.data?.subscription) {
        result.data.subscription.unsubscribe();
      }
    };
  }, [navigate]);
  
  return null;
}

// Student route guard
function StudentGuard({ children }) {
  const navigate = useNavigate();
  const [allowed, setAllowed] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getStudentToken()) {
      navigate('/student/login');
      return;
    }
    setAllowed(true);
    setLoading(false);
  }, []);

  if (loading) return null;
  if (!allowed) return null;
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <AuthHandler />
      <Routes>
        {/* Auth routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/" element={<RootRoute />} />

        {/* Admin routes */}
        <Route path="/upload" element={<AuthGuard><Upload /></AuthGuard>} />
        <Route path="/result/:scanId" element={<AuthGuard><Result /></AuthGuard>} />
        <Route path="/history" element={<AuthGuard><History /></AuthGuard>} />
        <Route path="/admin" element={<AuthGuard><AdminPanel /></AuthGuard>} />
        <Route path="/admin/manage-students" element={<AuthGuard><ManageStudents /></AuthGuard>} />
        <Route path="/admin/requests" element={<AuthGuard><AdminRequests /></AuthGuard>} />
        <Route path="/admin/audit-results" element={<AuthGuard><AdminAuditResults /></AuthGuard>} />

        {/* Student routes */}
        <Route path="/student/login" element={<StudentLogin />} />
        <Route path="/student/dashboard" element={<StudentGuard><StudentDashboard /></StudentGuard>} />
        <Route path="/student/audit-results" element={<StudentGuard><StudentAuditResults /></StudentGuard>} />
        <Route path="/student/requests" element={<StudentGuard><StudentRequests /></StudentGuard>} />
        <Route path="/student/change-password" element={<StudentGuard><ChangePassword /></StudentGuard>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
