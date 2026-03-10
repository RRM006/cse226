import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase, signInWithGoogle, getSession } from '../lib/supabase';

export default function Login() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkUser();
  }, []);

  async function checkUser() {
    const { data: { session } } = await getSession();
    if (session) {
      navigate('/upload');
    }
  }

  async function handleLogin() {
    setLoading(true);
    try {
      const { error } = await signInWithGoogle();
      if (error) throw error;
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>NSU Audit Core</h1>
        <p style={styles.subtitle}>Sign in to continue</p>
        
        <button 
          onClick={handleLogin} 
          disabled={loading}
          style={styles.button}
        >
          {loading ? 'Signing in...' : 'Sign in with Google'}
        </button>
        
        <p style={styles.note}>
          Only @northsouth.edu accounts are allowed
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    fontFamily: 'system-ui, sans-serif'
  },
  card: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    textAlign: 'center',
    maxWidth: '400px',
    width: '100%'
  },
  title: {
    margin: '0 0 0.5rem',
    color: '#1a1a1a',
    fontSize: '1.75rem'
  },
  subtitle: {
    margin: '0 0 1.5rem',
    color: '#666'
  },
  button: {
    backgroundColor: '#4285f4',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '4px',
    fontSize: '1rem',
    cursor: 'pointer',
    width: '100%',
    fontWeight: '500'
  },
  note: {
    marginTop: '1rem',
    fontSize: '0.875rem',
    color: '#888'
  }
};
