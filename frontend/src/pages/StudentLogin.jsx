import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Eye, EyeOff, Key } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { studentLogin } from '../lib/api';

export default function StudentLogin() {
  const [studentId, setStudentId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!/^\d{10}$/.test(studentId)) {
      setError('Student ID must be exactly 10 digits');
      return;
    }

    if (!password) {
      setError('Password is required');
      return;
    }

    setLoading(true);
    try {
      const data = await studentLogin(studentId, password);
      if (data.is_first_login) {
        navigate('/student/change-password', { state: { studentId } });
      } else {
        navigate('/student/dashboard');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0c4a6e 100%)',
      backgroundSize: '300% 300%',
      animation: 'gradientShift 8s ease infinite',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: '-60px', right: '-60px',
        width: '250px', height: '250px', borderRadius: '50%',
        background: 'rgba(59, 130, 246, 0.2)',
        filter: 'blur(50px)',
      }} />
      <div style={{
        position: 'absolute', bottom: '-60px', left: '-60px',
        width: '250px', height: '250px', borderRadius: '50%',
        background: 'rgba(16, 185, 129, 0.2)',
        filter: 'blur(50px)',
      }} />

      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '24px',
          padding: '40px',
          width: '100%',
          maxWidth: '400px',
          textAlign: 'center',
          boxShadow: '0 25px 50px rgba(0,0,0,0.3)',
          position: 'relative',
          zIndex: 10,
        }}
      >
        {/* Back button */}
        <button
          onClick={() => navigate('/login')}
          style={{
            position: 'absolute', top: '16px', left: '16px',
            background: 'none', border: 'none', color: 'rgba(255,255,255,0.6)',
            cursor: 'pointer', fontSize: '13px',
            display: 'flex', alignItems: 'center', gap: '4px',
          }}
        >
          ← Back
        </button>

        {/* Icon */}
        <div style={{
          width: '56px', height: '56px', borderRadius: '14px',
          background: 'rgba(59, 130, 246, 0.3)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 16px',
        }}>
          <User size={28} color="#93c5fd" />
        </div>

        <h1 style={{
          fontSize: '24px', fontWeight: '700', color: 'white',
          margin: '0 0 6px',
        }}>
          Student Login
        </h1>

        <p style={{
          color: 'rgba(255,255,255,0.6)', fontSize: '13px',
          margin: '0 0 28px',
        }}>
          Enter your Student ID and password
        </p>

        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.2)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: '10px',
            padding: '10px 14px',
            marginBottom: '20px',
            color: '#fca5a5',
            fontSize: '13px',
            textAlign: 'left',
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px', textAlign: 'left' }}>
            <label style={{
              color: 'rgba(255,255,255,0.7)', fontSize: '12px',
              fontWeight: '600', display: 'block', marginBottom: '6px',
            }}>
              Student ID
            </label>
            <div style={{
              display: 'flex', alignItems: 'center',
              background: 'rgba(255,255,255,0.08)',
              border: '1px solid rgba(255,255,255,0.15)',
              borderRadius: '10px',
              padding: '0 14px',
            }}>
              <Key size={16} color="rgba(255,255,255,0.4)" style={{ marginRight: '10px' }} />
              <input
                type="text"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value.replace(/\D/g, '').slice(0, 10))}
                placeholder="2221971042"
                maxLength={10}
                style={{
                  width: '100%', padding: '12px 0',
                  background: 'none', border: 'none', outline: 'none',
                  color: 'white', fontSize: '15px', letterSpacing: '2px',
                }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '24px', textAlign: 'left' }}>
            <label style={{
              color: 'rgba(255,255,255,0.7)', fontSize: '12px',
              fontWeight: '600', display: 'block', marginBottom: '6px',
            }}>
              Password
            </label>
            <div style={{
              display: 'flex', alignItems: 'center',
              background: 'rgba(255,255,255,0.08)',
              border: '1px solid rgba(255,255,255,0.15)',
              borderRadius: '10px',
              padding: '0 14px',
            }}>
              <Key size={16} color="rgba(255,255,255,0.4)" style={{ marginRight: '10px' }} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                style={{
                  width: '100%', padding: '12px 0',
                  background: 'none', border: 'none', outline: 'none',
                  color: 'white', fontSize: '15px',
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  padding: '4px',
                }}
              >
                {showPassword
                  ? <EyeOff size={16} color="rgba(255,255,255,0.4)" />
                  : <Eye size={16} color="rgba(255,255,255,0.4)" />
                }
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%', padding: '13px',
              background: loading ? 'rgba(59, 130, 246, 0.5)' : '#3b82f6',
              color: 'white', border: 'none', borderRadius: '12px',
              fontSize: '15px', fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)',
              transition: 'all 0.2s ease',
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p style={{
          color: 'rgba(255,255,255,0.4)', fontSize: '11px',
          marginTop: '20px', borderTop: '1px solid rgba(255,255,255,0.1)',
          paddingTop: '16px',
        }}>
          First time? Use your Student ID as default password
        </p>
      </motion.div>
    </div>
  );
}
