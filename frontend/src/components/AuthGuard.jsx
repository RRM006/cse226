import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { getSession, supabase } from '../lib/supabase';

function isNsuEmail(email) {
  return email?.toLowerCase().endsWith('@northsouth.edu');
}

async function verifyWithBackend(session) {
  const apiUrl = import.meta.env.VITE_API_URL || '';
  try {
    const response = await fetch(`${apiUrl}/api/v1/me`, {
      headers: {
        'Authorization': `Bearer ${session.access_token}`,
      },
    });
    if (response.status === 403) {
      return false;
    }
    return response.ok;
  } catch {
    return true;
  }
}

export default function AuthGuard({ children }) {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const { data: { session } } = await getSession();
      
      if (session) {
        const email = session.user?.email;
        
        if (!isNsuEmail(email)) {
          await supabase.auth.signOut();
          setAuthenticated(false);
          setLoading(false);
          return;
        }
        
        const isValid = await verifyWithBackend(session);
        if (!isValid) {
          await supabase.auth.signOut();
          setAuthenticated(false);
        } else {
          setAuthenticated(true);
        }
      } else {
        setAuthenticated(false);
      }
    } catch {
      setAuthenticated(false);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        Loading...
      </div>
    );
  }

  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
