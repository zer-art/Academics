from deepface import DeepFace
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import json
from typing import Dict, List, Optional

class DeepFaceAnalyzer:
    def __init__(self):
        self.models = {
            'emotion': 'enet_b0_8_best_vgaf',
            'age': 'Age',
            'gender': 'Gender',
            'race': 'Race'
        }
        
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        try:
            # DeepFace expects RGB format
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame
            
            # Perform analysis
            result = DeepFace.analyze(
                img_path=frame_rgb,
                actions=['emotion', 'age', 'gender', 'race'],
                enforce_detection=False
            )
            
            # Extract first face if multiple faces detected
            if isinstance(result, list):
                result = result[0]
            
            return {
                'success': True,
                'emotion': result.get('dominant_emotion', 'unknown'),
                'emotion_scores': result.get('emotion', {}),
                'age': result.get('age', 0),
                'gender': result.get('dominant_gender', 'unknown'),
                'gender_scores': result.get('gender', {}),
                'race': result.get('dominant_race', 'unknown'),
                'race_scores': result.get('race', {}),
                'confidence': result.get('face_confidence', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'emotion': 'neutral',
                'emotion_scores': {},
                'age': 0,
                'gender': 'unknown',
                'gender_scores': {},
                'race': 'unknown',
                'race_scores': {},
                'confidence': 0
            }
    
    def analyze_base64_image(self, base64_image: str) -> Dict:
        """
        Analyze a base64 encoded image
        """
        try:
            # Remove data URL prefix if present
            if base64_image.startswith('data:image'):
                base64_image = base64_image.split(',')[1]
            
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data))
            
            # Convert to numpy array
            frame = np.array(image)
            
            return self.analyze_frame(frame)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to decode image: {str(e)}',
                'emotion': 'neutral',
                'emotion_scores': {},
                'age': 0,
                'gender': 'unknown',
                'gender_scores': {},
                'race': 'unknown',
                'race_scores': {},
                'confidence': 0
            }
    
    def get_emotion_feedback(self, emotion: str, confidence: float) -> Dict:
        feedback_map = {
            'happy': {
                'message': 'Great! You appear confident and positive.',
                'color': 'green',
                'suggestion': 'Maintain this positive energy throughout the interview.'
            },
            'neutral': {
                'message': 'You appear calm and composed.',
                'color': 'blue',
                'suggestion': 'Try to show a bit more enthusiasm for the role.'
            },
            'sad': {
                'message': 'You might want to brighten your expression.',
                'color': 'orange',
                'suggestion': 'Think of something positive to naturally improve your facial expression.'
            },
            'angry': {
                'message': 'Try to relax your facial expression.',
                'color': 'red',
                'suggestion': 'Take a deep breath and focus on staying calm.'
            },
            'fear': {
                'message': 'You seem nervous. Try to relax.',
                'color': 'yellow',
                'suggestion': 'Remember to breathe deeply and speak slowly.'
            },
            'surprise': {
                'message': 'You appear surprised or engaged.',
                'color': 'purple',
                'suggestion': 'This can be good, but maintain a professional demeanor.'
            },
            'disgust': {
                'message': 'Try to maintain a more neutral expression.',
                'color': 'brown',
                'suggestion': 'Focus on appearing interested and engaged.'
            }
        }
        
        return feedback_map.get(emotion, {
            'message': 'Unable to detect clear emotion.',
            'color': 'gray',
            'suggestion': 'Ensure good lighting and face the camera directly.'
        })

# Global analyzer instance
deepface_analyzer = DeepFaceAnalyzer()
