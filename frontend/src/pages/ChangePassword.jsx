import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Key, Eye, EyeOff, Lock } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { studentChangePassword } from '../lib/api';
import { getStudentToken } from '../lib/supabase';
import StudentLayout from '../components/StudentLayout';

export default function ChangePassword() {
  const navigate = useNavigate();
  const location = useLocation();
  const isFirstLogin = location.state?.isFirstLogin || false;

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!getStudentToken()) {
      navigate('/student/login');
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!currentPassword) {
      setError('Current password is required');
      return;
    }
    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (newPassword === currentPassword) {
      setError('New password must be different from current password');
      return;
    }

    setLoading(true);
    try {
      await studentChangePassword(currentPassword, newPassword);
      alert('Password changed successfully!');
      navigate('/student/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <StudentLayout>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
      }}>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '18px',
            padding: '36px',
            width: '100%',
            maxWidth: '420px',
          }}
        >
          <div style={{
            width: '52px', height: '52px', borderRadius: '14px',
            background: 'rgba(251, 191, 36, 0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px',
          }}>
            <Lock size={24} color="#fbbf24" />
          </div>

          <h2 style={{
            fontSize: '20px', fontWeight: '700', textAlign: 'center', marginBottom: '6px',
            color: 'white',
          }}>
            {isFirstLogin ? 'Set New Password' : 'Change Password'}
          </h2>
          <p style={{
            fontSize: '13px', color: 'rgba(255,255,255,0.5)',
            textAlign: 'center', marginBottom: '24px',
          }}>
            {isFirstLogin
              ? 'Please change your default password to continue.'
              : 'Update your password below.'
            }
          </p>

          {error && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '10px',
              padding: '10px 14px',
              marginBottom: '18px',
              color: '#fca5a5',
              fontSize: '13px',
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block', fontSize: '12px', fontWeight: '600',
                color: 'rgba(255,255,255,0.7)', marginBottom: '6px',
              }}>
                Current Password
              </label>
              <div style={{
                display: 'flex', alignItems: 'center',
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: '10px', padding: '0 14px',
              }}>
                <Key size={16} color="rgba(255,255,255,0.3)" style={{ marginRight: '10px' }} />
                <input
                  type={showCurrent ? 'text' : 'password'}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Current password"
                  style={{
                    width: '100%', padding: '12px 0', background: 'none',
                    border: 'none', outline: 'none', color: 'white', fontSize: '14px',
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowCurrent(!showCurrent)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px' }}
                >
                  {showCurrent
                    ? <EyeOff size={15} color="rgba(255,255,255,0.3)" />
                    : <Eye size={15} color="rgba(255,255,255,0.3)" />
                  }
                </button>
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block', fontSize: '12px', fontWeight: '600',
                color: 'rgba(255,255,255,0.7)', marginBottom: '6px',
              }}>
                New Password
              </label>
              <div style={{
                display: 'flex', alignItems: 'center',
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: '10px', padding: '0 14px',
              }}>
                <Key size={16} color="rgba(255,255,255,0.3)" style={{ marginRight: '10px' }} />
                <input
                  type={showNew ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="New password (min 6 chars)"
                  style={{
                    width: '100%', padding: '12px 0', background: 'none',
                    border: 'none', outline: 'none', color: 'white', fontSize: '14px',
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowNew(!showNew)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px' }}
                >
                  {showNew
                    ? <EyeOff size={15} color="rgba(255,255,255,0.3)" />
                    : <Eye size={15} color="rgba(255,255,255,0.3)" />
                  }
                </button>
              </div>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block', fontSize: '12px', fontWeight: '600',
                color: 'rgba(255,255,255,0.7)', marginBottom: '6px',
              }}>
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                style={{
                  width: '100%', padding: '12px 14px',
                  background: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: '10px', color: 'white',
                  fontSize: '14px', outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%', padding: '13px',
                background: loading ? 'rgba(59,130,246,0.5)' : '#3b82f6',
                color: 'white', border: 'none', borderRadius: '12px',
                fontSize: '15px', fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              {loading ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        </motion.div>
      </div>
    </StudentLayout>
  );
}
