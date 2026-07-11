/**
 * AIVOX — Text-to-Speech wrapper using Web Speech Synthesis API.
 * Zero network latency — uses the browser's built-in speech engine.
 */

let selectedVoice: SpeechSynthesisVoice | null = null;

/** Pre-select the best available English voice */
function pickVoice(): SpeechSynthesisVoice | null {
  const voices = window.speechSynthesis.getVoices();
  // Priority order: natural-sounding voices first
  const preferred = [
    'Google US English', 'Microsoft David', 'Microsoft Zira',
    'Alex', 'Samantha', 'Karen',
  ];
  for (const name of preferred) {
    const v = voices.find(v => v.name === name);
    if (v) return v;
  }
  return voices.find(v => v.lang.startsWith('en')) ?? voices[0] ?? null;
}

/** Load voices (some browsers load them async) */
export function initTTS(): Promise<void> {
  return new Promise(resolve => {
    const voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
      selectedVoice = pickVoice();
      resolve();
    } else {
      window.speechSynthesis.onvoiceschanged = () => {
        selectedVoice = pickVoice();
        resolve();
      };
    }
  });
}

/** Speak text — returns a Promise that resolves when speech is done */
export function speak(text: string, rate = 1.0, pitch = 1.0): Promise<void> {
  return new Promise((resolve, reject) => {
    window.speechSynthesis.cancel(); // Stop any ongoing speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = selectedVoice;
    utterance.rate = rate;
    utterance.pitch = pitch;
    utterance.volume = 1.0;
    utterance.lang = 'en-US';

    utterance.onend = () => resolve();
    utterance.onerror = (e) => reject(new Error(`TTS error: ${e.error}`));

    window.speechSynthesis.speak(utterance);
  });
}

/** Stop any ongoing speech immediately */
export function stopSpeaking(): void {
  window.speechSynthesis.cancel();
}

/** Check if currently speaking */
export function isSpeaking(): boolean {
  return window.speechSynthesis.speaking;
}
