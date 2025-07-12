import Image from "next/image";
import Link from 'next/link';

export default function Home() {
  return (
    <main style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <h1>VSCode Sync Tool</h1>
      <p>Welcome to the web frontend! Authentication, profile management, and cloud sync coming soon.</p>
      <Link href="/auth" style={{ marginTop: 24, color: '#0070f3', textDecoration: 'underline' }}>
        Sign In / Sign Up
      </Link>
    </main>
  );
}
