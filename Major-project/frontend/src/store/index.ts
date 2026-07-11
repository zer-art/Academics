/**
 * AIVOX — Zustand Global State Store
 * Manages auth state, interview session state, and report data.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ─── Types ────────────────────────────────────────────────────────────────────
export type AppUser = {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
};

export type InterviewDomain =
  | 'Software Engineer'
  | 'Data Scientist'
  | 'Product Manager'
  | 'UI/UX Designer'
  | 'DevOps Engineer';

export type AnswerScore = {
  question: string;
  answer: string;
  score: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
};

export type ConfidenceMetric = {
  confidence: number;
  head_alignment: number;
  eye_contact: number;
  speaking_engagement: number;
  timestamp: number;
};

export type InterviewPhase =
  | 'idle'
  | 'loading_questions'
  | 'asking'       // AI is speaking the question
  | 'ready_to_answer' // Waiting for user to click "Start Answering" or "Skip"
  | 'listening'    // User is recording their answer
  | 'processing'   // Transcribing + evaluating
  | 'feedback'     // Showing score for this Q
  | 'finished';

// ─── Auth Store ───────────────────────────────────────────────────────────────
type AuthState = {
  user: AppUser | null;
  isAuthLoading: boolean;
  setUser: (user: AppUser | null) => void;
  setAuthLoading: (v: boolean) => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthLoading: true,
  setUser: (user) => set({ user }),
  setAuthLoading: (isAuthLoading) => set({ isAuthLoading }),
}));

// ─── Interview Store ──────────────────────────────────────────────────────────
type InterviewState = {
  domain: InterviewDomain;
  questions: string[];
  currentIndex: number;
  phase: InterviewPhase;
  answerScores: AnswerScore[];
  confidenceHistory: ConfidenceMetric[];
  sessionStartTime: number | null;

  // Actions
  setDomain: (d: InterviewDomain) => void;
  setQuestions: (q: string[]) => void;
  setPhase: (p: InterviewPhase) => void;
  nextQuestion: () => void;
  addAnswerScore: (s: AnswerScore) => void;
  addConfidenceMetric: (m: ConfidenceMetric) => void;
  startSession: () => void;
  resetSession: () => void;
};

export const useInterviewStore = create<InterviewState>((set) => ({
  domain: 'Software Engineer',
  questions: [],
  currentIndex: 0,
  phase: 'idle',
  answerScores: [],
  confidenceHistory: [],
  sessionStartTime: null,

  setDomain: (domain) => set({ domain }),
  setQuestions: (questions) => set({ questions }),
  setPhase: (phase) => set({ phase }),
  nextQuestion: () => set((s) => ({ currentIndex: s.currentIndex + 1, phase: 'asking' })),
  addAnswerScore: (score) => set((s) => ({ answerScores: [...s.answerScores, score] })),
  addConfidenceMetric: (metric) =>
    set((s) => ({ confidenceHistory: [...s.confidenceHistory, metric] })),
  startSession: () => set({ sessionStartTime: Date.now(), phase: 'loading_questions', answerScores: [], confidenceHistory: [], currentIndex: 0 }),
  resetSession: () =>
    set({ questions: [], currentIndex: 0, phase: 'idle', answerScores: [], confidenceHistory: [], sessionStartTime: null }),
}));

// ─── Report Store (persisted to localStorage for /report page) ───────────────
type ReportState = {
  report: Record<string, unknown> | null;
  setReport: (r: Record<string, unknown>) => void;
  clearReport: () => void;
};

export const useReportStore = create<ReportState>()(
  persist(
    (set) => ({
      report: null,
      setReport: (report) => set({ report }),
      clearReport: () => set({ report: null }),
    }),
    { name: 'aivox-report' }
  )
);
