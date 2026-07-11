import { signInWithPopup, signOut, onAuthStateChanged, type User } from 'firebase/auth';
import { doc, setDoc, getDoc, serverTimestamp } from 'firebase/firestore';
import { auth, db, googleProvider, isFirebaseConfigured } from './firebase';

export type AppUser = {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
};

// Demo user used when Firebase is not configured
export const DEMO_USER: AppUser = {
  uid: 'demo-user',
  email: 'demo@aivox.app',
  displayName: 'Demo User',
  photoURL: null,
};

export async function signInWithGoogle(): Promise<AppUser> {
  if (!isFirebaseConfigured || !auth || !googleProvider) {
    // Demo mode — return mock user instantly
    return DEMO_USER;
  }

  const result = await signInWithPopup(auth, googleProvider);
  const user = result.user;

  // Upsert user profile in Firestore on first sign-in
  if (db) {
    const userRef = doc(db, 'users', user.uid);
    const snap = await getDoc(userRef);
    if (!snap.exists()) {
      await setDoc(userRef, {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
        createdAt: serverTimestamp(),
        total_interviews: 0,
        last_score: null,
      });
    }
  }

  return {
    uid: user.uid,
    email: user.email,
    displayName: user.displayName,
    photoURL: user.photoURL,
  };
}

export async function logout(): Promise<void> {
  if (!isFirebaseConfigured || !auth) return;
  await signOut(auth);
}

export function onAuthChange(callback: (user: User | null) => void) {
  if (!isFirebaseConfigured || !auth) {
    // Demo mode — never fires, App.tsx handles this via isFirebaseConfigured flag
    return () => {};
  }
  return onAuthStateChanged(auth, callback);
}
