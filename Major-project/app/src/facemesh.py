import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Tuple, Optional
from scipy.spatial.transform import Rotation


class MediaPipeFaceMesh:
    """Blazing-fast confidence analysis using MediaPipe Face Mesh"""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # 3D model points (relative facial landmarks)
        # Nose tip, chin, left eye left corner, right eye right corner, left mouth corner, right mouth corner
        self.model_points = np.array(
            [
                (0.0, 0.0, 0.0),  # Nose tip (idx 1)
                (0.0, -330.0, -65.0),  # Chin (idx 152)
                (-225.0, 170.0, -135.0),  # Left eye left corner (idx 33)
                (225.0, 170.0, -135.0),  # Right eye right corner (idx 263)
                (-150.0, -150.0, -125.0),  # Left mouth corner (idx 61)
                (150.0, -150.0, -125.0),  # Right mouth corner (idx 291)
            ],
            dtype=np.float64,
        )

        # Landmark indices for key points
        self.key_landmark_indices = [1, 152, 33, 263, 61, 291]

        # Mouth landmarks for MAR calculation
        self.mouth_top = [13, 14]  # Upper lip center
        self.mouth_bottom = [17, 18]  # Lower lip center
        self.mouth_left = [61]  # Left corner
        self.mouth_right = [291]  # Right corner

        # Eye landmarks for blink detection (optional)
        self.left_eye_top = [159]
        self.left_eye_bottom = [145]
        self.right_eye_top = [386]
        self.right_eye_bottom = [374]

    def calculate_head_pose(
        self, landmarks: np.ndarray, image_shape: Tuple[int, int]
    ) -> Dict:
        """
        Calculate head pose angles (yaw, pitch, roll) using SolvePnP

        Args:
            landmarks: 468x3 array of normalized face landmarks
            image_shape: (height, width) of image

        Returns:
            Dict with yaw, pitch, roll angles in degrees
        """
        height, width = image_shape

        # Extract 2D image points from key landmarks
        image_points = np.array(
            [landmarks[idx][:2] * [width, height] for idx in self.key_landmark_indices],
            dtype=np.float64,
        )

        # Camera matrix (assuming standard webcam)
        focal_length = width
        center = (width / 2, height / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]],
            dtype=np.float64,
        )

        # Distortion coefficients (assuming no lens distortion)
        dist_coeffs = np.zeros((4, 1))

        # Solve PnP to get rotation and translation vectors
        success, rotation_vec, translation_vec = cv2.solvePnP(
            self.model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

        if not success:
            return {"yaw": 0, "pitch": 0, "roll": 0, "success": False}

        # Convert rotation vector to rotation matrix
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)

        # Extract Euler angles from rotation matrix
        # Using scipy for accurate conversion
        r = Rotation.from_matrix(rotation_mat)
        euler_angles = r.as_euler("yxz", degrees=True)  # yaw, pitch, roll

        yaw, pitch, roll = euler_angles

        return {
            "yaw": float(yaw),  # Left/Right head turn (-90 to +90)
            "pitch": float(pitch),  # Up/Down head tilt (-90 to +90)
            "roll": float(roll),  # Head tilt to sides (-90 to +90)
            "success": True,
        }

    def calculate_mouth_aspect_ratio(self, landmarks: np.ndarray) -> float:
        """
        Calculate Mouth Aspect Ratio (MAR) to detect speaking/smiling

        Formula: MAR = (vertical_distance) / (horizontal_distance)
        High MAR = mouth open (speaking), Low MAR = mouth closed
        """
        # Vertical distance (top to bottom)
        top = np.mean([landmarks[i] for i in self.mouth_top], axis=0)
        bottom = np.mean([landmarks[i] for i in self.mouth_bottom], axis=0)
        vertical = np.linalg.norm(top - bottom)

        # Horizontal distance (left to right)
        left = landmarks[self.mouth_left[0]]
        right = landmarks[self.mouth_right[0]]
        horizontal = np.linalg.norm(left - right)

        if horizontal < 1e-6:  # Avoid division by zero
            return 0.0

        mar = vertical / horizontal
        return float(mar)

    def detect_smile(self, landmarks: np.ndarray) -> float:
        """
        Detect smile by analyzing mouth corner elevation

        Returns: smile_score (0.0-1.0)
        """
        # Get mouth corners
        left_corner = landmarks[61]
        right_corner = landmarks[291]

        # Get nose tip as reference point
        nose_tip = landmarks[1]

        # Calculate if corners are elevated relative to nose
        left_elevation = nose_tip[1] - left_corner[1]
        right_elevation = nose_tip[1] - right_corner[1]

        # Normalize (smile if corners are above a threshold)
        avg_elevation = (left_elevation + right_elevation) / 2

        # Convert to 0-1 score (empirically tuned threshold)
        smile_score = np.clip(avg_elevation * 10, 0, 1)

        return float(smile_score)

    def calculate_confidence_score(
        self, head_pose: Dict, mar: float, smile_score: float
    ) -> Dict:
        """
        Calculate overall confidence score based on geometric features

        Scoring logic:
        - Head pose alignment (50%): Looking at camera = high confidence
        - Speaking engagement (30%): Active speaking = engaged
        - Positive expression (20%): Smiling = confident
        """
        if not head_pose.get("success"):
            return {
                "confidence": 0,
                "head_alignment": 0,
                "speaking_engagement": 0,
                "positive_expression": 0,
                "feedback": "Face not detected",
            }

        yaw = abs(head_pose["yaw"])
        pitch = abs(head_pose["pitch"])

        # 1. Head Alignment Score (0-50)
        # Perfect alignment: yaw and pitch near 0
        # Penalize looking away (yaw) or down (pitch)
        yaw_score = max(0, 50 - (yaw * 0.8))  # -0.8 per degree yaw
        pitch_score = max(0, 50 - (pitch * 1.0))  # -1.0 per degree pitch
        head_alignment = (yaw_score + pitch_score) / 2

        # 2. Speaking Engagement Score (0-30)
        # MAR > 0.3 indicates speaking/open mouth
        # MAR between 0.15-0.3 is optimal (not too wide)
        if 0.15 <= mar <= 0.4:
            speaking_engagement = 30
        elif mar > 0.4:
            speaking_engagement = 20  # Too wide (shouting?)
        else:
            speaking_engagement = max(0, mar * 100)  # Proportional to opening

        # 3. Positive Expression Score (0-20)
        positive_expression = smile_score * 20

        # Total confidence score (0-100)
        total_confidence = head_alignment + speaking_engagement + positive_expression

        # Generate feedback
        feedback_parts = []
        if head_alignment < 25:
            if yaw > 20:
                feedback_parts.append("Look directly at the camera")
            if pitch > 15:
                feedback_parts.append("Lift your head up")

        if speaking_engagement < 10:
            feedback_parts.append("Speak more clearly and expressively")

        if positive_expression < 5:
            feedback_parts.append("Try to appear more positive")

        if total_confidence >= 80:
            feedback = "Excellent presence and confidence!"
        elif total_confidence >= 60:
            feedback = (
                "Good engagement. " + "; ".join(feedback_parts)
                if feedback_parts
                else "Keep it up!"
            )
        else:
            feedback = (
                "; ".join(feedback_parts)
                if feedback_parts
                else "Improve your camera presence"
            )

        return {
            "confidence": round(total_confidence, 2),
            "head_alignment": round(head_alignment, 2),
            "speaking_engagement": round(speaking_engagement, 2),
            "positive_expression": round(positive_expression, 2),
            "head_pose": head_pose,
            "mouth_aspect_ratio": round(mar, 3),
            "smile_score": round(smile_score, 3),
            "feedback": feedback,
        }

    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Main analysis function - replaces DeepFace

        Args:
            frame: BGR image from OpenCV

        Returns:
            Dict with confidence analysis results
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]

        # Process with MediaPipe
        results = self.face_mesh.process(image_rgb)

        if not results.multi_face_landmarks:
            return {
                "success": False,
                "confidence": 0,
                "feedback": "No face detected",
                "error": "No face landmarks found",
            }

        # Get first face landmarks (assuming single person)
        face_landmarks = results.multi_face_landmarks[0]

        # Convert to numpy array
        landmarks = np.array([[lm.x, lm.y, lm.z] for lm in face_landmarks.landmark])

        # Calculate head pose
        head_pose = self.calculate_head_pose(landmarks, (height, width))

        # Calculate mouth aspect ratio
        mar = self.calculate_mouth_aspect_ratio(landmarks)

        # Detect smile
        smile_score = self.detect_smile(landmarks)

        # Calculate overall confidence score
        confidence_result = self.calculate_confidence_score(head_pose, mar, smile_score)

        return {"success": True, **confidence_result}

    def draw_debug_overlay(
        self, frame: np.ndarray, analysis_result: Dict
    ) -> np.ndarray:
        """
        Draw debug information on frame for visualization
        """
        if not analysis_result.get("success"):
            return frame

        overlay = frame.copy()
        confidence = analysis_result["confidence"]

        # Color based on confidence level
        if confidence >= 75:
            color = (0, 255, 0)  # Green
        elif confidence >= 50:
            color = (0, 255, 255)  # Yellow
        else:
            color = (0, 0, 255)  # Red

        # Draw confidence bar
        bar_width = int((confidence / 100) * 200)
        cv2.rectangle(overlay, (10, 10), (210, 40), (0, 0, 0), -1)
        cv2.rectangle(overlay, (10, 10), (10 + bar_width, 40), color, -1)
        cv2.putText(
            overlay,
            f"Confidence: {confidence:.1f}%",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # Draw feedback
        cv2.putText(
            overlay,
            analysis_result["feedback"][:50],
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

        # Draw head pose angles
        head_pose = analysis_result.get("head_pose", {})
        if head_pose.get("success"):
            y_pos = 90
            cv2.putText(
                overlay,
                f"Yaw: {head_pose['yaw']:.1f}deg",
                (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1,
            )
            cv2.putText(
                overlay,
                f"Pitch: {head_pose['pitch']:.1f}deg",
                (10, y_pos + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1,
            )

        return overlay

    def __del__(self):
        """Cleanup MediaPipe resources"""
        if hasattr(self, "face_mesh"):
            self.face_mesh.close()


# Global analyzer instance
facemesh_analyzer = MediaPipeFaceMesh()
