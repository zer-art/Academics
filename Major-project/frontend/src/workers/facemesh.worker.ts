/**
 * AIVOX — MediaPipe Face Landmarker Web Worker
 * Runs face mesh inference off the main thread using WebGL.
 * Receives ImageBitmap frames, emits confidence metrics.
 *
 * This worker is entirely isolated from the UI thread —
 * no jank, no dropped frames, smooth 30 FPS HUD.
 */

import {
  FaceLandmarker,
  FilesetResolver,
} from '@mediapipe/tasks-vision';

let landmarker: FaceLandmarker | null = null;
let isReady = false;

// ─── Initialize MediaPipe ─────────────────────────────────────────────────────
async function init() {
  const filesetResolver = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm'
  );
  landmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
    baseOptions: {
      modelAssetPath:
        'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',
      delegate: 'GPU',
    },
    runningMode: 'VIDEO',
    numFaces: 1,
    outputFaceBlendshapes: true,
    outputFacialTransformationMatrixes: true,
  });

  isReady = true;
  self.postMessage({ type: 'ready' });
}

// ─── Confidence Analysis ──────────────────────────────────────────────────────
function analyzeFrame(bitmap: ImageBitmap, timestampMs: number) {
  if (!landmarker || !isReady) return;

  const result = landmarker.detectForVideo(bitmap, timestampMs);
  bitmap.close(); // Free GPU memory immediately

  if (!result.faceLandmarks || result.faceLandmarks.length === 0) {
    self.postMessage({ type: 'result', data: { success: false, confidence: 0 } });
    return;
  }

  const landmarks = result.faceLandmarks[0];
  const blendshapes = result.faceBlendshapes?.[0]?.categories ?? [];

  // ── Head Pose (yaw/pitch from nose + chin alignment) ─────────────────────
  const nose = landmarks[1];       // Nose tip
  const chin = landmarks[152];     // Chin
  const leftEye = landmarks[33];
  const rightEye = landmarks[263];

  // Yaw: horizontal head rotation (0 = facing camera)
  const eyeMidX = (leftEye.x + rightEye.x) / 2;
  const yawOffset = Math.abs(nose.x - eyeMidX) * 2;
  const headAlignmentScore = Math.max(0, 100 - yawOffset * 300);

  // Pitch: vertical tilt
  const pitchOffset = Math.abs(nose.y - (chin.y + leftEye.y) / 2);
  const pitchScore = Math.max(0, 100 - pitchOffset * 200);

  // ── Eye Contact (gaze direction via iris landmarks) ───────────────────────
  // Landmarks 468-472 = left iris, 473-477 = right iris
  const leftIris = landmarks[468];
  const rightIris = landmarks[473];
  const leftX = leftIris?.x ?? 0.5;
  const rightX = rightIris?.x ?? 0.5;
  const irisX = (leftX + rightX) / 2;
  const eyeContactScore = Math.max(0, 100 - Math.abs(irisX - 0.5) * 400);

  // ── Speaking Engagement (jaw open ratio) ──────────────────────────────────
  const jawOpen = blendshapes.find(b => b.categoryName === 'jawOpen')?.score ?? 0;
  const speakingScore = jawOpen > 0.05 ? Math.min(100, jawOpen * 300) : 0;

  // ── Composite confidence ─────────────────────────────────────────────────
  const confidence = Math.round(
    headAlignmentScore * 0.4 +
    pitchScore * 0.2 +
    eyeContactScore * 0.3 +
    speakingScore * 0.1
  );

  self.postMessage({
    type: 'result',
    data: {
      success: true,
      confidence: Math.max(0, Math.min(100, confidence)),
      head_alignment: Math.round(headAlignmentScore),
      eye_contact: Math.round(eyeContactScore),
      speaking_engagement: Math.round(speakingScore),
    },
  });
}

// ─── Message Handler ──────────────────────────────────────────────────────────
self.onmessage = async (e: MessageEvent) => {
  const { type, bitmap, timestampMs } = e.data;
  if (type === 'init') {
    await init();
  } else if (type === 'frame' && isReady) {
    analyzeFrame(bitmap, timestampMs);
  }
};
