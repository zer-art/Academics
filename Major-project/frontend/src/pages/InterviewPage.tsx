import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterviewStore, useAuthStore, useReportStore, type InterviewDomain } from '@/store';
import { speak, stopSpeaking, initTTS } from '@/lib/tts';
import { AudioRecorder } from '@/lib/audioRecorder';
import styles from './InterviewPage.module.css';

const API_URL = import.meta.env.VITE_API_URL ?? '';
const DOMAINS: InterviewDomain[] = ['Software Engineer', 'Data Scientist', 'Product Manager', 'UI/UX Designer', 'DevOps Engineer'];

type ConfidenceData = { success: boolean; confidence: number; head_alignment: number; eye_contact: number; speaking_engagement: number; };

export default function InterviewPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const store = useInterviewStore();
  const { setReport } = useReportStore();

  const videoRef = useRef<HTMLVideoElement>(null);
  const workerRef = useRef<Worker | null>(null);
  const recorderRef = useRef<AudioRecorder | null>(null);
  const frameLoopRef = useRef<number>(0);
  const streamRef = useRef<MediaStream | null>(null);

  const [confidence, setConfidence] = useState<ConfidenceData | null>(null);
  const [statusMsg, setStatusMsg] = useState('Select a domain and click Start Interview');
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [camReady, setCamReady] = useState(false);
  const [workerReady, setWorkerReady] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(0);

  // ── Timer ────────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (store.phase === 'idle') return;
    const id = setInterval(() => setTimeElapsed(t => t + 1), 1000);
    return () => clearInterval(id);
  }, [store.phase]);

  // ── Camera Setup ─────────────────────────────────────────────────────────────
  useEffect(() => {
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' }, audio: false });
        streamRef.current = stream;
        if (videoRef.current) { videoRef.current.srcObject = stream; }
        setCamReady(true);
      } catch { setStatusMsg('⚠️ Camera access denied — confidence tracking disabled.'); }
    })();
    return () => { streamRef.current?.getTracks().forEach(t => t.stop()); };
  }, []);

  // ── MediaPipe Worker ──────────────────────────────────────────────────────────
  useEffect(() => {
    const worker = new Worker(new URL('../workers/facemesh.worker.ts', import.meta.url), { type: 'module' });
    workerRef.current = worker;
    worker.onmessage = (e) => {
      if (e.data.type === 'ready') { setWorkerReady(true); startFrameLoop(); }
      else if (e.data.type === 'result' && e.data.data.success) {
        const data = e.data.data as ConfidenceData;
        setConfidence(data);
        if (store.phase !== 'idle' && store.phase !== 'finished') {
          store.addConfidenceMetric({ ...data, timestamp: Date.now() });
        }
      }
    };
    worker.postMessage({ type: 'init' });
    return () => { worker.terminate(); cancelAnimationFrame(frameLoopRef.current); };
  }, []);

  const startFrameLoop = useCallback(() => {
    const loop = () => {
      if (videoRef.current && workerRef.current && videoRef.current.readyState === 4) {
        const bitmap = videoRef.current;
        // Only send frame if worker is ready — createImageBitmap from video
        createImageBitmap(bitmap).then(bmp => {
          workerRef.current?.postMessage({ type: 'frame', bitmap: bmp, timestampMs: performance.now() }, [bmp]);
        }).catch(() => {});
      }
      frameLoopRef.current = requestAnimationFrame(loop);
    };
    // Run at ~15 FPS to balance accuracy and performance
    let last = 0;
    const throttled = (ts: number) => {
      if (ts - last > 66) { last = ts; loop(); }
      frameLoopRef.current = requestAnimationFrame(throttled);
    };
    frameLoopRef.current = requestAnimationFrame(throttled);
  }, []);

  // ── Interview Flow ────────────────────────────────────────────────────────────
  const startInterview = async () => {
    store.startSession();
    setStatusMsg('Generating questions...');
    await initTTS();

    try {
      const res = await fetch(`${API_URL}/api/questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: store.domain }),
      });
      const data = await res.json();
      store.setQuestions(data.questions);
      store.setPhase('asking');
      askQuestion(data.questions, 0);
    } catch { setStatusMsg('❌ Failed to load questions. Check your connection.'); store.setPhase('idle'); }
  };

  const askQuestion = async (questions: string[], index: number) => {
    const q = questions[index];
    store.setPhase('asking');
    setStatusMsg(`Question ${index + 1} of ${questions.length}`);
    try {
      await speak(q);
    } catch (e) {
      console.warn("TTS error:", e);
    } finally {
      store.setPhase('ready_to_answer');
      setStatusMsg('🎙️ Ready when you are — click "Start Answering" to record or "Skip Question".');
    }
  };

  const startAnswering = async () => {
    store.setPhase('listening');
    setStatusMsg('🎙️ Your turn — speak your answer. Recording stops after 3s of silence.');
    startRecording(store.questions, store.currentIndex);
  };

  const stopAnswering = async () => {
    if (recorderRef.current) {
      setStatusMsg('⏳ Processing your answer...');
      await recorderRef.current.stopRecording();
    }
  };

  const handleSkipQuestion = () => {
    stopSpeaking();
    handleNoAnswer(store.questions, store.currentIndex);
  };

  const startRecording = async (questions: string[], index: number) => {
    const recorder = new AudioRecorder();
    recorderRef.current = recorder;
    
    let blob: Blob | null = null;
    try {
      blob = await recorder.startRecording(() => setStatusMsg('⏳ Silence detected — processing your answer...'));
    } catch (e) {
      console.error("Recording error:", e);
      setStatusMsg('❌ Recording failed.');
      store.setPhase('feedback');
      return;
    }

    if (!blob || blob.size < 1000) { handleNoAnswer(questions, index); return; }

    store.setPhase('processing');
    setStatusMsg('🧠 Transcribing and evaluating your answer...');

    try {
      const transcript = await AudioRecorder.transcribe(blob);
      setCurrentAnswer(transcript || '(no speech detected)');

      const evalRes = await fetch(`${API_URL}/api/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: questions[index], answer: transcript, role: store.domain }),
      });
      const evalData = await evalRes.json();
      store.addAnswerScore({ question: questions[index], answer: transcript, ...evalData });
      store.setPhase('feedback');
      setStatusMsg(`✅ Score: ${evalData.score}/100`);

      // Auto-advance after 2.5s
      setTimeout(() => {
        if (index + 1 < questions.length) {
          store.nextQuestion();
          askQuestion(questions, index + 1);
        } else {
          finishInterview(questions);
        }
      }, 2500);
    } catch { setStatusMsg('❌ Evaluation failed.'); store.setPhase('feedback'); }
  };

  const handleNoAnswer = (questions: string[], index: number) => {
    store.addAnswerScore({ question: questions[index], answer: '', score: 0, feedback: 'Question skipped.', strengths: [], improvements: ['Please answer verbally.'] });
    if (index + 1 < questions.length) { store.nextQuestion(); askQuestion(questions, index + 1); }
    else finishInterview(questions);
  };

  const finishInterview = async (questions: string[]) => {
    store.setPhase('finished');
    stopSpeaking();
    setStatusMsg('Generating your report...');

    const confHistory = useInterviewStore.getState().confidenceHistory;
    const avgConf = confHistory.length > 0 ? confHistory.reduce((s, m) => s + m.confidence, 0) / confHistory.length : 0;

    const body = {
      role: store.domain,
      duration_seconds: timeElapsed,
      answer_scores: store.answerScores,
      confidence_summary: {
        average_confidence: Math.round(avgConf),
        peak_confidence: Math.round(Math.max(...confHistory.map(m => m.confidence), 0)),
        trend: 'stable',
        total_frames: confHistory.length,
        distribution: {
          excellent: confHistory.filter(m => m.confidence >= 80).length,
          good: confHistory.filter(m => m.confidence >= 60 && m.confidence < 80).length,
          fair: confHistory.filter(m => m.confidence >= 40 && m.confidence < 60).length,
          poor: confHistory.filter(m => m.confidence < 40).length,
        },
      },
      user_id: user?.uid ?? null,
    };

    try {
      const res = await fetch(`${API_URL}/api/finish`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const data = await res.json();
      setReport({ ...data.report, interview_summary: { ...data.report.interview_summary, date: new Date().toISOString() } });
      navigate('/report');
    } catch { setStatusMsg('❌ Report generation failed.'); }
  };

  const getPhaseLabel = () => {
    const labels: Record<string, string> = {
      idle: 'Ready',
      loading_questions: 'Loading…',
      asking: 'AI Speaking',
      ready_to_answer: 'Ready to Speak',
      listening: 'Recording',
      processing: 'Analysing',
      feedback: 'Feedback',
      finished: 'Done'
    };
    return labels[store.phase] ?? '';
  };

  const progress = store.questions.length > 0 ? ((store.currentIndex) / store.questions.length) * 100 : 0;
  const confScore = confidence?.confidence ?? 0;
  const confColor = confScore >= 70 ? 'var(--success)' : confScore >= 45 ? 'var(--warning)' : 'var(--danger)';

  return (
    <div className={styles.page}>
      {/* ── Navbar ── */}
      <nav className="navbar">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className={`gradient-text`} style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.3rem' }}>AIVOX</span>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span className="badge badge-accent">{getPhaseLabel()}</span>
            {store.phase !== 'idle' && <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontVariantNumeric: 'tabular-nums' }}>{Math.floor(timeElapsed/60)}:{String(timeElapsed%60).padStart(2,'0')}</span>}
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/')}>Exit</button>
          </div>
        </div>
      </nav>

      <div className="container" style={{ paddingTop: 28, paddingBottom: 40 }}>
        <div className={styles.grid}>
          {/* ── Left: Camera + Confidence ── */}
          <div className={styles.leftCol}>
            <div className={`glass-card ${styles.videoCard}`}>
              <video ref={videoRef} className={styles.video} autoPlay muted playsInline />
              {camReady && confidence?.success && (
                <div className={styles.hudOverlay}>
                  <div className={styles.hudRow}>
                    <span className={styles.hudLabel}>Confidence</span>
                    <span style={{ color: confColor, fontWeight: 700 }}>{confScore}%</span>
                  </div>
                  <div className={styles.hudBar}><div style={{ width: `${confScore}%`, background: confColor }} /></div>
                  <div className={styles.hudMini}>
                    <span>👁️ Eye Contact: {confidence.eye_contact}%</span>
                    <span>📐 Posture: {confidence.head_alignment}%</span>
                  </div>
                </div>
              )}
              {!camReady && <div className={styles.noCam}><span>📷</span><p>Camera not available</p></div>}
            </div>

            {/* ── AI Avatar ── */}
            <div className={`glass-card ${styles.aiCard}`}>
              <div className={`${styles.aiAvatar} ${store.phase === 'asking' ? styles.speaking : ''}`}>
                <div className={styles.aiRing} />
                <div className={styles.aiFace}>
                  <div className={styles.aiEyes}>
                    <div className={styles.aiEye} /><div className={styles.aiEye} />
                  </div>
                  <div className={`${styles.aiMouth} ${store.phase === 'asking' ? styles.aiMouthOpen : ''}`} />
                </div>
              </div>
              {store.phase === 'asking' && (
                <div className={styles.waveGroup}>
                  {[0,1,2,3,4].map(i => <div key={i} className={styles.wave} style={{ animationDelay: `${i * 0.12}s` }} />)}
                </div>
              )}
              <p className={styles.aiLabel}>AI Interviewer</p>
            </div>
          </div>

          {/* ── Right: Controls + Panels ── */}
          <div className={styles.rightCol}>
            {/* Domain selector (only when idle) */}
            {store.phase === 'idle' && (
              <div className={`glass-card ${styles.panel}`}>
                <h3 className={styles.panelTitle}>Select Interview Domain</h3>
                <div className={styles.domainGrid}>
                  {DOMAINS.map(d => (
                    <button key={d} className={`${styles.domainBtn} ${store.domain === d ? styles.domainBtnActive : ''}`}
                      onClick={() => store.setDomain(d)}>{d}</button>
                  ))}
                </div>
                <button className="btn btn-primary" style={{ width: '100%', marginTop: 20 }} onClick={startInterview} id="start-interview-btn">
                  🚀 Start Interview
                </button>
              </div>
            )}

            {/* Question panel */}
            {store.questions.length > 0 && store.phase !== 'idle' && (
              <div className={`glass-card ${styles.panel} ${store.phase === 'asking' ? 'glass-card-glow' : ''}`}>
                <div className={styles.questionHeader}>
                  <span className="badge badge-accent">Q{store.currentIndex + 1} / {store.questions.length}</span>
                  <div className="progress-bar-track" style={{ flex: 1 }}>
                    <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
                  </div>
                </div>
                <p className={styles.questionText}>{store.questions[store.currentIndex]}</p>
              </div>
            )}

            {/* Action Controls */}
            {store.questions.length > 0 && store.phase !== 'idle' && store.phase !== 'finished' && (
              <div className={`glass-card ${styles.panel}`}>
                <h4 className={styles.panelSubtitle}>Interview Actions</h4>
                <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                  {store.phase === 'ready_to_answer' && (
                    <button key="start-btn" className="btn btn-success" style={{ flex: 1 }} onClick={startAnswering} id="start-answering-btn">
                      🎙️ Start Answering
                    </button>
                  )}
                  {store.phase === 'listening' && (
                    <button key="stop-btn" className="btn btn-danger" style={{ flex: 1 }} onClick={stopAnswering} id="stop-answering-btn">
                      ⏹️ Finish & Submit
                    </button>
                  )}
                  {(store.phase === 'asking' || store.phase === 'ready_to_answer' || store.phase === 'listening') && (
                    <button key="skip-btn" className="btn btn-ghost" style={{ flex: 1 }} onClick={handleSkipQuestion} id="skip-question-btn">
                      ⏭️ Skip Question
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Status panel */}
            <div className={`glass-card ${styles.panel}`}>
              <h4 className={styles.panelSubtitle}>
                {store.phase === 'listening' ? '🎙️ Recording' : store.phase === 'processing' ? '🧠 Processing' : '📡 Status'}
              </h4>
              <p className={styles.statusText}>{statusMsg}</p>
              {store.phase === 'listening' && (
                <div className={styles.recordingIndicator}>
                  <div className={styles.recDot} />
                  <span style={{ fontSize: '0.85rem', color: 'var(--danger)' }}>Recording… speak clearly</span>
                </div>
              )}
            </div>

            {/* Latest feedback */}
            {store.answerScores.length > 0 && (
              <div className={`glass-card ${styles.panel}`}>
                <h4 className={styles.panelSubtitle}>Latest Feedback</h4>
                {(() => {
                  const last = store.answerScores[store.answerScores.length - 1];
                  const sc = last.score >= 80 ? 'var(--success)' : last.score >= 60 ? 'var(--warning)' : 'var(--danger)';
                  return (
                    <>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                        <div className={styles.scoreCircle} style={{ borderColor: sc, color: sc }}>{last.score}</div>
                        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', flex: 1 }}>{last.feedback}</p>
                      </div>
                      {last.strengths.length > 0 && <p className={styles.feedbackTag} style={{ color: 'var(--success)' }}>✓ {last.strengths[0]}</p>}
                      {last.improvements.length > 0 && <p className={styles.feedbackTag} style={{ color: 'var(--warning)' }}>↑ {last.improvements[0]}</p>}
                    </>
                  );
                })()}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
