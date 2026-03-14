import { motion } from 'framer-motion';
import { GraduationCap } from 'lucide-react';
import { useAuth } from '../lib/supabase';

export default function Login() {
  const { signInWithGoogle } = useAuth();

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #6366f1 0%, #3b82f6 50%, #8b5cf6 100%)',
      backgroundSize: '300% 300%',
      animation: 'gradientShift 8s ease infinite',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      position: 'relative',
      overflow: 'hidden',
    }}>

      {/* Floating blobs */}
      <div style={{
        position: 'absolute', top: '-80px', right: '-80px',
        width: '300px', height: '300px', borderRadius: '50%',
        background: 'rgba(139, 92, 246, 0.3)',
        filter: 'blur(60px)',
      }} />
      <div style={{
        position: 'absolute', bottom: '-80px', left: '-80px',
        width: '300px', height: '300px', borderRadius: '50%',
        background: 'rgba(59, 130, 246, 0.3)',
        filter: 'blur(60px)',
      }} />

      {/* Glass card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        style={{
          background: 'rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          borderRadius: '24px',
          padding: '48px',
          width: '100%',
          maxWidth: '420px',
          textAlign: 'center',
          boxShadow: '0 25px 50px rgba(0,0,0,0.2)',
          position: 'relative',
          zIndex: 10,
        }}
      >
        {/* Icon */}
        <div style={{
          width: '64px', height: '64px', borderRadius: '16px',
          background: 'rgba(255,255,255,0.2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 20px',
        }}>
          <GraduationCap size={32} color="white" />
        </div>

        {/* Title */}
        <h1 style={{
          fontSize: '28px', fontWeight: '700', color: 'white',
          margin: '0 0 8px', letterSpacing: '-0.5px',
        }}>
          NSU Audit Core
        </h1>

        {/* Subtitle */}
        <p style={{
          color: 'rgba(255,255,255,0.75)', fontSize: '14px',
          margin: '0 0 32px', lineHeight: '1.5',
        }}>
          AI-powered transcript auditing and verification system
        </p>

        {/* Google Sign In Button */}
        <button
          onClick={signInWithGoogle}
          style={{
            width: '100%', padding: '14px 24px',
            background: 'white', color: '#374151',
            border: 'none', borderRadius: '12px',
            fontSize: '15px', fontWeight: '600',
            cursor: 'pointer', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            gap: '10px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.15)',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={e => {
            e.target.style.transform = 'translateY(-1px)';
            e.target.style.boxShadow = '0 8px 25px rgba(0,0,0,0.2)';
          }}
          onMouseLeave={e => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 15px rgba(0,0,0,0.15)';
          }}
        >
          {/* Google SVG icon */}
          <svg width="18" height="18" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Sign in with Google
        </button>

        {/* Note */}
        <p style={{
          color: 'rgba(255,255,255,0.6)', fontSize: '12px',
          marginTop: '16px',
        }}>
          Only @northsouth.edu accounts are allowed
        </p>

        {/* Footer */}
        <p style={{
          color: 'rgba(255,255,255,0.4)', fontSize: '11px',
          marginTop: '24px', borderTop: '1px solid rgba(255,255,255,0.1)',
          paddingTop: '16px',
        }}>
          North South University • CSE226.1 — Vibe Coding
        </p>
      </motion.div>
    </div>
  );
}