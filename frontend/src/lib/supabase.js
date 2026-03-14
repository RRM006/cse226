import { createClient } from '@supabase/supabase-js';
import { useEffect, useState } from 'react';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://zxzcnpkfabiiecagczao.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4emNucGtmYWJpaWVjYWdjemFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDExNDMsImV4cCI6MjA4ODM3NzE0M30.0Qo8IT6gBIOF3YMlHZm4dnh47lMUW5QesD_f3EVf9tM';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export const getSession = () => supabase.auth.getSession();

export const signInWithGoogle = () => 
  supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: window.location.origin
    }
  });

export const signOut = () => supabase.auth.signOut();

export const onAuthStateChange = (callback) => 
  supabase.auth.onAuthStateChange(callback);

export const useAuth = () => {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getInitialSession = async () => {
      const { data } = await supabase.auth.getSession();
      setSession(data);
      setLoading(false);
    };

    getInitialSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setSession(session);
        setLoading(false);
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
