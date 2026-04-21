import { createClient } from '@supabase/supabase-js';
import { useEffect, useState } from 'react';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    'Missing required environment variables: VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set in frontend/.env'
  );
}

export const supabase = (supabaseUrl && supabaseAnonKey) 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

export const getSession = () => supabase?.auth.getSession();

export const signInWithGoogle = () => 
  supabase?.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: window.location.origin
    }
  });

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const saveSession = async (accessToken) => {
  if (!accessToken) return;
  try {
    await fetch(`${API_URL}/api/v1/session/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ access_token: accessToken }),
    });
  } catch (e) {
    console.error('Failed to save session:', e);
  }
};

export const signOut = () => supabase?.auth.signOut();

export const onAuthStateChange = (callback) => 
  supabase?.auth.onAuthStateChange(callback);

export const useAuth = () => {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }

    const getInitialSession = async () => {
      try {
        const { data } = await supabase.auth.getSession();
        setSession(data);
      } catch (err) {
        console.error("useAuth getSession error:", err);
      } finally {
        setLoading(false);
      }
    };

    getInitialSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setSession(session);
        setLoading(false);
        // Save token to backend for MCP
        if (session?.access_token) {
          saveSession(session.access_token);
        }
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  return {
    supabase,
    session,
    loading,
    signInWithGoogle,
    signOut,
    getSession,
    onAuthStateChange
  };
};

// Student auth
const STUDENT_TOKEN_KEY = 'student_token';

export const getStudentToken = () => localStorage.getItem(STUDENT_TOKEN_KEY);

export const setStudentToken = (token) => localStorage.setItem(STUDENT_TOKEN_KEY, token);

export const clearStudentToken = () => localStorage.removeItem(STUDENT_TOKEN_KEY);

export const isStudentLoggedIn = () => !!getStudentToken();

export const studentSignOut = () => {
  clearStudentToken();
};
