'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '../../lib/supabaseClient';
import type { AuthUser } from '@supabase/supabase-js';

export default function DashboardPage() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const getUser = async () => {
      const { data, error } = await supabase.auth.getUser();
      if (error || !data.user) {
        router.replace('/auth');
      } else {
        setUser(data.user);
      }
      setLoading(false);
    };
    getUser();
  }, [router]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.replace('/auth');
  };

  if (loading) {
    return <main style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>Loading...</main>;
  }

  return (
    <main style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <h1>Welcome to your Dashboard!</h1>
      <p>{user ? `Logged in as: ${user.email}` : ''}</p>
      {/* Placeholder for profiles list */}
      <div style={{ margin: '2rem 0' }}>
        <h2>Your Profiles</h2>
        <p>(Profile management coming soon...)</p>
        <button disabled style={{ marginTop: '1rem' }}>Create New Profile (coming soon)</button>
      </div>
      <button onClick={handleLogout} style={{ marginTop: '2rem' }}>Log out</button>
    </main>
  );
}
