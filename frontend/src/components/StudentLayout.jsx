import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { User, LogOut } from 'lucide-react';
import { getStudentProfile } from '../lib/api';
import { studentSignOut } from '../lib/supabase';

export default function StudentLayout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await getStudentProfile();
      setProfile(data);
    } catch {
      navigate('/student/login');
    }
  };

  const handleLogout = () => {
    studentSignOut();
    navigate('/login');
  };

  const tabs = [
    { path: '/student/dashboard', label: 'Dashboard' },
    { path: '/student/audit-results', label: 'Audit Results' },
    { path: '/student/requests', label: 'My Requests' },
    { path: '/student/change-password', label: 'Change Password' },
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0f172a',
      color: 'white',
    }}>
      {/* Top bar */}
      <header style={{
        background: 'rgba(255,255,255,0.05)',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px', height: '32px', borderRadius: '8px',
            background: 'rgba(59, 130, 246, 0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <User size={18} color="#60a5fa" />
          </div>
          <div>
            <div style={{ fontSize: '14px', fontWeight: '600' }}>
              {profile?.name || 'Student'}
            </div>
            <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)' }}>
              {profile?.student_id}
            </div>
          </div>
        </div>
        <button
          onClick={handleLogout}
          style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            padding: '8px 14px', borderRadius: '8px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#fca5a5', cursor: 'pointer',
            fontSize: '13px', fontWeight: '500',
          }}
        >
          <LogOut size={14} />
          Logout
        </button>
      </header>

      {/* Navigation tabs */}
      <nav style={{
        padding: '0 24px',
        display: 'flex', gap: '8px',
        borderBottom: '1px solid rgba(255,255,255,0.08)',
      }}>
        {tabs.map(tab => (
          <button
            key={tab.path}
            onClick={() => navigate(tab.path)}
            style={{
              padding: '12px 16px',
              background: 'none', border: 'none',
              color: location.pathname === tab.path
                ? 'white' : 'rgba(255,255,255,0.5)',
              fontSize: '13px', fontWeight: '500',
              borderBottom: location.pathname === tab.path
                ? '2px solid #3b82f6' : '2px solid transparent',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Content */}
      <main style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        {children}
      </main>
    </div>
  );
}
