import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';

function AuthCallback() {
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const { data, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Auth callback error:', error);
          setError(error.message);
          return;
        }

        if (data.session) {
          const email = data.session.user?.email;
          if (!email || !email.toLowerCase().endsWith('@northsouth.edu')) {
            await supabase.auth.signOut();
            setError('Only @northsouth.edu accounts are allowed. Please sign in with your NSU email.');
            return;
          }
          console.log('Session found:', data.session);
          navigate('/upload');
        } else {
          console.log('No session found, checking URL hash...');
          
          const hashParams = new URLSearchParams(window.location.hash.substring(1));
          const accessToken = hashParams.get('access_token');
          const refreshToken = hashParams.get('refresh_token');
          
          if (accessToken && refreshToken) {
            const { data: sessionData, error: setSessionError } = await supabase.auth.setSession({
              access_token: accessToken,
              refresh_token: refreshToken
            });
            
            if (setSessionError) {
              console.error('Set session error:', setSessionError);
              setError(setSessionError.message);
              return;
            }

            const email = sessionData?.user?.email;
            if (!email || !email.toLowerCase().endsWith('@northsouth.edu')) {
              await supabase.auth.signOut();
              setError('Only @northsouth.edu accounts are allowed. Please sign in with your NSU email.');
              return;
            }
            
            navigate('/upload');
          } else {
            navigate('/login');
          }
        }
      } catch (err) {
        console.error('Unexpected error:', err);
        setError(err.message);
      }
    };

    handleAuthCallback();
  }, [navigate]);

  if (error) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Authentication Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/login')}>Go to Login</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>Processing login...</h2>
    </div>
  );
}

export default AuthCallback;
