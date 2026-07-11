/**
 * AIVOX — Audio Recorder using MediaRecorder API + simple VAD.
 * Records from the browser microphone, auto-stops on 3 seconds of silence.
 * Sends the recorded audio blob to the backend for Groq Whisper transcription.
 */

const API_URL = import.meta.env.VITE_API_URL ?? '';
const SILENCE_THRESHOLD = 0.01;  // RMS amplitude below this = silence
const SILENCE_DURATION_MS = 3000; // Stop after 3 consecutive seconds of silence
const MAX_RECORDING_MS = 90000;   // Hard cap at 90 seconds

export type RecordingResult = {
  transcript: string;
  durationSeconds: number;
  blob: Blob;
};

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private stream: MediaStream | null = null;
  private chunks: Blob[] = [];
  private silenceTimer: ReturnType<typeof setTimeout> | null = null;
  private maxTimer: ReturnType<typeof setTimeout> | null = null;
  private onSilenceDetected: (() => void) | null = null;
  private stopResolve: ((blob: Blob | null) => void) | null = null;

  async requestPermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      stream.getTracks().forEach(t => t.stop()); // Just check permission, don't hold
      return true;
    } catch {
      return false;
    }
  }

  startRecording(onSilence?: () => void): Promise<Blob | null> {
    this.chunks = [];
    this.onSilenceDetected = onSilence ?? null;
    console.log("[AudioRecorder] startRecording requested");

    return new Promise(async (resolve, reject) => {
      this.stopResolve = resolve;

      try {
        console.log("[AudioRecorder] Requesting microphone stream...");
        this.stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 16000,
          },
        });
        console.log("[AudioRecorder] Microphone stream acquired successfully");

        // Set up AudioContext for VAD
        this.audioContext = new AudioContext({ sampleRate: 16000 });
        const source = this.audioContext.createMediaStreamSource(this.stream);
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 512;
        source.connect(this.analyser);

        // Choose the best supported MIME type
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/ogg';

        console.log("[AudioRecorder] Using mimeType:", mimeType);
        this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });
        this.mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            this.chunks.push(e.data);
          }
        };

        this.mediaRecorder.onstop = () => {
          const blob = new Blob(this.chunks, { type: this.mediaRecorder!.mimeType });
          console.log("[AudioRecorder] mediaRecorder onstop. Chunks count:", this.chunks.length, "Blob size:", blob.size);
          this._cleanup();
          if (this.stopResolve) {
            this.stopResolve(blob);
            this.stopResolve = null;
          }
        };

        this.mediaRecorder.start(250); // Collect chunks every 250ms
        console.log("[AudioRecorder] mediaRecorder started, state:", this.mediaRecorder.state);

        // Start silence detection loop
        this._detectSilence();

        // Hard max recording time
        this.maxTimer = setTimeout(() => {
          console.log("[AudioRecorder] Max recording duration reached (90s)");
          this.stopRecording();
        }, MAX_RECORDING_MS);
      } catch (err) {
        console.error("[AudioRecorder] Failed to initialize recording:", err);
        reject(err);
      }
    });
  }

  private _detectSilence(): void {
    if (!this.analyser) return;
    const buffer = new Float32Array(this.analyser.fftSize);

    const check = () => {
      if (!this.analyser || !this.mediaRecorder || this.mediaRecorder.state !== 'recording') return;

      this.analyser.getFloatTimeDomainData(buffer);
      const rms = Math.sqrt(buffer.reduce((sum, v) => sum + v * v, 0) / buffer.length);

      if (rms < SILENCE_THRESHOLD) {
        // Silence detected — start/continue silence timer
        if (!this.silenceTimer) {
          console.log("[AudioRecorder] Silence threshold breached, VAD timer started");
          this.silenceTimer = setTimeout(() => {
            console.log("[AudioRecorder] Silence duration threshold reached, auto-stopping");
            this.onSilenceDetected?.();
            this.stopRecording();
          }, SILENCE_DURATION_MS);
        }
      } else {
        // Speech detected — reset silence timer
        if (this.silenceTimer) {
          console.log("[AudioRecorder] Speech detected, resetting VAD timer");
          clearTimeout(this.silenceTimer);
          this.silenceTimer = null;
        }
      }

      requestAnimationFrame(check);
    };

    requestAnimationFrame(check);
  }

  async stopRecording(): Promise<void> {
    console.log("[AudioRecorder] stopRecording triggered");
    if (this.silenceTimer) { clearTimeout(this.silenceTimer); this.silenceTimer = null; }
    if (this.maxTimer) { clearTimeout(this.maxTimer); this.maxTimer = null; }

    if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
      console.log("[AudioRecorder] mediaRecorder already inactive or null, state:", this.mediaRecorder?.state);
      if (this.stopResolve) {
        this.stopResolve(null);
        this.stopResolve = null;
      }
      return;
    }
    
    this.mediaRecorder.stop();
  }

  private _cleanup(): void {
    this.stream?.getTracks().forEach(t => t.stop());
    this.audioContext?.close();
    this.analyser = null;
    this.audioContext = null;
    this.stream = null;
    this.mediaRecorder = null;
    this.chunks = [];
  }

  /** Upload audio blob to backend and get transcript */
  static async transcribe(blob: Blob): Promise<string> {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');

    const res = await fetch(`${API_URL}/api/transcribe`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) throw new Error(`Transcription API error: ${res.status}`);
    const data = await res.json();
    return data.transcript ?? '';
  }
}
