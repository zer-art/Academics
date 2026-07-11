import {
  collection,
  query,
  orderBy,
  limit,
  getDocs,
  doc,
  getDoc,
  getDocFromServer,
} from 'firebase/firestore';
import { db, isFirebaseConfigured } from './firebase';

export type InterviewReport = {
  report_id: string;
  role: string;
  created_at: { seconds: number };
  scoring: {
    final_score: number;
    answer_score: number;
    confidence_score: number;
  };
  question_analysis: Array<{
    question: string;
    answer: string;
    score: number;
    feedback: string;
    strengths: string[];
    improvements: string[];
  }>;
  confidence_analysis: {
    average_confidence: number;
    peak_confidence: number;
    trend: string;
    distribution: Record<string, number>;
  };
  recommendations: string[];
};

export type UserProfile = {
  uid: string;
  displayName: string | null;
  email: string | null;
  photoURL: string | null;
  total_interviews: number;
  last_score: number | null;
};

export type GlobalStats = {
  total_interviews: number;
};

/** Fetch user's last N interview reports, sorted by newest first */
export async function getUserReports(uid: string, maxCount = 10): Promise<InterviewReport[]> {
  if (!isFirebaseConfigured || !db) return [];
  const q = query(
    collection(db, 'users', uid, 'interviews'),
    orderBy('created_at', 'desc'),
    limit(maxCount)
  );
  const snap = await getDocs(q);
  return snap.docs.map(d => d.data() as InterviewReport);
}

/** Fetch user profile from Firestore */
export async function getUserProfile(uid: string): Promise<UserProfile | null> {
  if (!isFirebaseConfigured || !db) return null;
  const snap = await getDoc(doc(db, 'users', uid));
  return snap.exists() ? (snap.data() as UserProfile) : null;
}

/** Fetch global platform stats (total interviews conducted) */
export async function getGlobalStats(): Promise<GlobalStats> {
  if (!isFirebaseConfigured || !db) return { total_interviews: 0 };
  try {
    const snap = await getDocFromServer(doc(db, 'stats', 'global'));
    return snap.exists() ? (snap.data() as GlobalStats) : { total_interviews: 0 };
  } catch {
    return { total_interviews: 0 };
  }
}
