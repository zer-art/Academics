import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { onAuthChange, DEMO_USER } from '@/lib/auth';
import { isFirebaseConfigured } from '@/lib/firebase';
import { useAuthStore } from '@/store';
import LandingPage from '@/pages/LandingPage';
import AuthPage from '@/pages/AuthPage';
import InterviewPage from '@/pages/InterviewPage';
import ReportPage from '@/pages/ReportPage';
import DashboardPage from '@/pages/DashboardPage';
import '@/styles/globals.css';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isAuthLoading } = useAuthStore();
  if (isAuthLoading) return <div className="loading-screen"><div className="spinner" /></div>;
  if (!user) return <Navigate to="/auth" replace />;
  return <>{children}</>;
}

export default function App() {
  const { setUser, setAuthLoading } = useAuthStore();

  useEffect(() => {
    if (!isFirebaseConfigured) {
      // Demo mode: auto sign-in with mock user so all pages are accessible
      setUser(DEMO_USER);
      setAuthLoading(false);
      return;
    }

    // Real Firebase auth listener
    const unsub = onAuthChange((fbUser: import('firebase/auth').User | null) => {
      setUser(
        fbUser
          ? { uid: fbUser.uid, email: fbUser.email, displayName: fbUser.displayName, photoURL: fbUser.photoURL }
          : null
      );
      setAuthLoading(false);
    });
    return unsub;
  }, [setUser, setAuthLoading]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/interview" element={<ProtectedRoute><InterviewPage /></ProtectedRoute>} />
        <Route path="/report" element={<ProtectedRoute><ReportPage /></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
