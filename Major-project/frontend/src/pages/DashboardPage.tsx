import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store';
import { getUserReports, getUserProfile, getGlobalStats, type InterviewReport, type UserProfile, type GlobalStats } from '@/lib/firestore';
import { logout } from '@/lib/auth';
import styles from './DashboardPage.module.css';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, setUser } = useAuthStore();
  const [reports, setReports] = useState<InterviewReport[]>([]);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [globalStats, setGlobalStats] = useState<GlobalStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    (async () => {
      const [r, p, g] = await Promise.all([
        getUserReports(user.uid),
        getUserProfile(user.uid),
        getGlobalStats(),
      ]);
      setReports(r);
      setProfile(p);
      setGlobalStats(g);
      setLoading(false);
    })();
  }, [user]);

  const handleLogout = async () => {
    await logout();
    setUser(null);
    navigate('/');
  };

  const avgScore = reports.length > 0
    ? Math.round(reports.reduce((s, r) => s + r.scoring.final_score, 0) / reports.length)
    : 0;
  const bestScore = reports.length > 0
    ? Math.round(Math.max(...reports.map(r => r.scoring.final_score)))
    : 0;

  if (loading) return <div className="loading-screen"><div className="spinner" /></div>;

  return (
    <div className={styles.page}>
      <nav className="navbar">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="gradient-text" style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.3rem' }}>AIVOX</span>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            {user?.photoURL && <img src={user.photoURL} alt="avatar" className={styles.avatar} />}
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{user?.displayName ?? user?.email}</span>
            <button className="btn btn-ghost btn-sm" onClick={handleLogout}>Sign Out</button>
          </div>
        </div>
      </nav>

      <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 32 }}>
          <div>
            <h1 style={{ marginBottom: 6 }}>Your Dashboard</h1>
            <p>Track your interview progress over time</p>
          </div>
          <button className="btn btn-primary" onClick={() => navigate('/interview')}>🚀 New Interview</button>
        </div>

        {/* ── Stats Grid ── */}
        <div className={styles.statsGrid}>
          {[
            { label: 'Interviews Taken', val: reports.length, icon: '🎙️', col: 'var(--accent)' },
            { label: 'Average Score', val: `${avgScore}/100`, icon: '📊', col: 'var(--info)' },
            { label: 'Best Score', val: `${bestScore}/100`, icon: '🏆', col: 'var(--success)' },
            { label: 'Platform Total', val: (globalStats?.total_interviews ?? 0).toLocaleString(), icon: '🌍', col: 'var(--warning)' },
          ].map(s => (
            <div key={s.label} className={`glass-card ${styles.statCard}`}>
              <div className={styles.statIcon} style={{ color: s.col }}>{s.icon}</div>
              <div className={styles.statVal} style={{ color: s.col }}>{s.val}</div>
              <div className={styles.statLabel}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* ── Interview History ── */}
        <h2 style={{ marginBottom: 20, marginTop: 40 }}>Interview History</h2>
        {reports.length === 0 ? (
          <div className={`glass-card ${styles.emptyState}`}>
            <div style={{ fontSize: '3rem', marginBottom: 16 }}>🎯</div>
            <h3 style={{ marginBottom: 8 }}>No interviews yet</h3>
            <p style={{ marginBottom: 24 }}>Complete your first interview to see your results here.</p>
            <button className="btn btn-primary" onClick={() => navigate('/interview')}>Start First Interview</button>
          </div>
        ) : (
          <div className={styles.historyList}>
            {reports.map((r) => {
              const date = r.created_at ? new Date(r.created_at.seconds * 1000).toLocaleDateString() : 'Unknown date';
              const sc = r.scoring.final_score >= 80 ? 'var(--success)' : r.scoring.final_score >= 60 ? 'var(--accent)' : 'var(--warning)';
              return (
                <div key={r.report_id} className={`glass-card ${styles.historyCard}`}>
                  <div className={styles.historyLeft}>
                    <div className={styles.historyScore} style={{ color: sc, borderColor: sc }}>
                      {Math.round(r.scoring.final_score)}
                    </div>
                    <div>
                      <div className={styles.historyRole}>{r.role}</div>
                      <div className={styles.historyMeta}>{date} · {r.question_analysis?.length ?? 0} questions</div>
                    </div>
                  </div>
                  <div className={styles.historyRight}>
                    <div className={styles.historyBars}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.8rem' }}>
                        <span style={{ color: 'var(--text-muted)', width: 90 }}>Answer Quality</span>
                        <div className="progress-bar-track" style={{ flex: 1 }}>
                          <div className="progress-bar-fill" style={{ width: `${r.scoring.answer_score}%` }} />
                        </div>
                        <span style={{ width: 28, textAlign: 'right', color: 'var(--text-secondary)' }}>{Math.round(r.scoring.answer_score)}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.8rem' }}>
                        <span style={{ color: 'var(--text-muted)', width: 90 }}>Confidence</span>
                        <div className="progress-bar-track" style={{ flex: 1 }}>
                          <div className="progress-bar-fill" style={{ width: `${r.scoring.confidence_score}%`, background: '#10b981' }} />
                        </div>
                        <span style={{ width: 28, textAlign: 'right', color: 'var(--text-secondary)' }}>{Math.round(r.scoring.confidence_score)}</span>
                      </div>
                    </div>
                    <span className={`badge ${r.confidence_analysis?.trend === 'improving' ? 'badge-success' : r.confidence_analysis?.trend === 'declining' ? 'badge-danger' : 'badge-accent'}`}>
                      {r.confidence_analysis?.trend ?? 'stable'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
