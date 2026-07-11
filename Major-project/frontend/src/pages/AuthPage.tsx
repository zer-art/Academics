import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signInWithGoogle } from '@/lib/auth';
import styles from './AuthPage.module.css';

export default function AuthPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError(null);
    try {
      await signInWithGoogle();
      navigate('/interview');
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Sign-in failed. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.orb1} />
      <div className={styles.orb2} />

      <div className={styles.card + ' glass-card animate-fade-in-up'}>
        {/* Logo */}
        <div className={styles.logoWrap}>
          <div className={styles.logoIcon}>✦</div>
          <span className={`gradient-text ${styles.logoText}`}>AIVOX</span>
        </div>

        <h1 className={styles.title}>Welcome Back</h1>
        <p className={styles.subtitle}>
          Sign in to start your AI mock interview and track your progress over time.
        </p>

        {error && (
          <div className="alert alert-danger" style={{ marginBottom: '20px' }}>
            ⚠️ {error}
          </div>
        )}

        {/* Google Sign-In Button */}
        <button
          id="google-signin-btn"
          className={`btn btn-ghost ${styles.googleBtn}`}
          onClick={handleGoogleSignIn}
          disabled={loading}
        >
          {loading ? (
            <span className="spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
          )}
          {loading ? 'Signing in...' : 'Continue with Google'}
        </button>

        <div className={styles.dividerRow}>
          <span className={styles.dividerLine} />
          <span className={styles.dividerText}>free forever</span>
          <span className={styles.dividerLine} />
        </div>

        {/* Feature list */}
        <ul className={styles.featureList}>
          {[
            '5 interview questions per session',
            'Real-time facial confidence analysis',
            'Detailed AI feedback per answer',
            'Full session history & score tracking',
          ].map(f => (
            <li key={f} className={styles.featureItem}>
              <span className={styles.featureCheck}>✓</span>
              {f}
            </li>
          ))}
        </ul>

        <p className={styles.terms}>
          By signing in, you agree to our{' '}
          <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.
        </p>
      </div>

      <button className={`btn btn-ghost btn-sm ${styles.backBtn}`} onClick={() => navigate('/')}>
        ← Back to Home
      </button>
    </div>
  );
}
