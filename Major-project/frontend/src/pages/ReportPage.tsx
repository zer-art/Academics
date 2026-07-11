import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useReportStore } from '@/store';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import styles from './ReportPage.module.css';

export default function ReportPage() {
  const navigate = useNavigate();
  const { report, clearReport } = useReportStore();

  useEffect(() => {
    if (!report) navigate('/', { replace: true });
  }, [report, navigate]);

  if (!report) return null;

  const r = report as Record<string, any>;
  const scoring = r.scoring ?? {};
  const summary = r.interview_summary ?? {};
  const analysis = (r.question_analysis ?? []) as Array<Record<string, any>>;
  const confidence = r.confidence_analysis ?? {};
  const recs = (r.recommendations ?? []) as string[];
  const finalScore = scoring.final_score ?? 0;

  const scoreColor = finalScore >= 80 ? '#10b981' : finalScore >= 60 ? '#6366f1' : finalScore >= 45 ? '#f59e0b' : '#ef4444';
  const scoreLabel = finalScore >= 85 ? 'Outstanding' : finalScore >= 70 ? 'Strong' : finalScore >= 55 ? 'Good' : 'Keep Practicing';

  const radarData = [
    { subject: 'Content', A: scoring.answer_score ?? 0 },
    { subject: 'Confidence', A: scoring.confidence_score ?? 0 },
    { subject: 'Posture', A: confidence.average_confidence ?? 0 },
    { subject: 'Eye Contact', A: Math.min(100, (confidence.average_confidence ?? 0) * 1.1) },
    { subject: 'Fluency', A: analysis.length > 0 ? analysis.reduce((s: number, a: Record<string,any>) => s + a.score, 0) / analysis.length : 0 },
  ];

  const progressData = analysis.map((a, i) => ({ name: `Q${i + 1}`, score: a.score }));

  const handleNewInterview = () => { clearReport(); navigate('/interview'); };

  return (
    <div className={styles.page}>
      <nav className="navbar">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="gradient-text" style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.3rem' }}>AIVOX</span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>Dashboard</button>
            <button className="btn btn-primary btn-sm" onClick={handleNewInterview}>New Interview</button>
          </div>
        </div>
      </nav>

      <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
        {/* ── Hero Score ── */}
        <div className={`glass-card ${styles.scoreHero}`}>
          <div className={styles.scoreRingWrap}>
            <svg width="140" height="140" viewBox="0 0 140 140">
              <circle cx="70" cy="70" r="60" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
              <circle cx="70" cy="70" r="60" fill="none" stroke={scoreColor} strokeWidth="10"
                strokeDasharray={`${2 * Math.PI * 60}`}
                strokeDashoffset={`${2 * Math.PI * 60 * (1 - finalScore / 100)}`}
                strokeLinecap="round"
                style={{ transform: 'rotate(-90deg)', transformOrigin: '70px 70px', transition: 'stroke-dashoffset 1.5s ease' }}
              />
            </svg>
            <div className={styles.scoreCenter}>
              <div className={styles.scoreNum} style={{ color: scoreColor }}>{Math.round(finalScore)}</div>
              <div className={styles.scoreMax}>/100</div>
            </div>
          </div>
          <div className={styles.scoreInfo}>
            <div className="badge badge-accent" style={{ marginBottom: 12 }}>{scoreLabel}</div>
            <h1 style={{ fontSize: '1.8rem', marginBottom: 8 }}>Interview Complete</h1>
            <p style={{ marginBottom: 20, fontSize: '0.95rem' }}>
              Role: <strong style={{ color: 'var(--text-primary)' }}>{summary.role}</strong> ·
              {' '}{summary.questions_answered} questions · {summary.duration}
            </p>
            <div className={styles.scoreBreakdown}>
              {[
                { label: 'Answer Quality', val: scoring.answer_score, col: '#6366f1' },
                { label: 'Confidence', val: scoring.confidence_score, col: '#10b981' },
              ].map(s => (
                <div key={s.label} className={styles.breakdownItem}>
                  <div className={styles.breakdownLabel}>{s.label}</div>
                  <div className="progress-bar-track" style={{ flex: 1 }}>
                    <div className="progress-bar-fill" style={{ width: `${s.val}%`, background: s.col }} />
                  </div>
                  <div className={styles.breakdownVal} style={{ color: s.col }}>{Math.round(s.val)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Charts ── */}
        <div className={styles.chartsGrid}>
          <div className={`glass-card ${styles.chartCard}`}>
            <h3 className={styles.sectionTitle}>Score by Question</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={progressData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="#475569" fontSize={12} />
                <YAxis domain={[0, 100]} stroke="#475569" fontSize={12} />
                <Tooltip contentStyle={{ background: 'rgba(15,15,30,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#f1f5f9' }} />
                <Line type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={2.5} dot={{ fill: '#6366f1', r: 5 }} activeDot={{ r: 7 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className={`glass-card ${styles.chartCard}`}>
            <h3 className={styles.sectionTitle}>Performance Radar</h3>
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.06)" />
                <PolarAngleAxis dataKey="subject" stroke="#475569" fontSize={11} />
                <Radar name="Score" dataKey="A" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* ── Q&A Breakdown ── */}
        <h2 className={styles.sectionTitle} style={{ marginBottom: 20, marginTop: 40 }}>Answer Breakdown</h2>
        <div className={styles.qaList}>
          {analysis.map((a, i) => {
            const sc = a.score >= 80 ? 'var(--success)' : a.score >= 60 ? 'var(--accent)' : 'var(--warning)';
            return (
              <div key={i} className={`glass-card ${styles.qaCard}`}>
                <div className={styles.qaHeader}>
                  <span className="badge badge-accent">Q{i + 1}</span>
                  <span style={{ color: sc, fontWeight: 700, fontSize: '1rem', fontFamily: 'var(--font-display)' }}>{a.score}/100</span>
                </div>
                <p className={styles.qaQuestion}>{a.question}</p>
                <p className={styles.qaAnswer}>"{a.answer || '(no answer)'}"</p>
                <p className={styles.qaFeedback}>{a.feedback}</p>
                <div className={styles.qaTagsRow}>
                  {a.strengths?.slice(0,2).map((s: string) => <span key={s} className={styles.tagGreen}>✓ {s}</span>)}
                  {a.improvements?.slice(0,1).map((s: string) => <span key={s} className={styles.tagAmber}>↑ {s}</span>)}
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Recommendations ── */}
        <h2 className={styles.sectionTitle} style={{ marginBottom: 20, marginTop: 40 }}>Recommendations</h2>
        <div className={styles.recList}>
          {recs.map((r, i) => <div key={i} className={`glass-card ${styles.recItem}`}>{r}</div>)}
        </div>

        {/* ── Actions ── */}
        <div className={styles.actions}>
          <button className="btn btn-primary btn-lg" onClick={handleNewInterview}>🚀 Practice Again</button>
          <button className="btn btn-ghost btn-lg" onClick={() => window.print()}>📄 Download PDF</button>
          <button className="btn btn-ghost btn-lg" onClick={() => navigate('/dashboard')}>📊 Dashboard</button>
        </div>
      </div>
    </div>
  );
}
