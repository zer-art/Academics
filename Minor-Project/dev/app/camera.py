import cv2
import numpy as np
from keras.models import model_from_json
import mediapipe as mp
import threading
import time

# Load Model
json_file = open("S:/Github/Minor Project/MINOR-PROJECT/dev/app/model/model.json", "r")
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)
model.load_weights("S:/Github/Minor Project/MINOR-PROJECT/dev/app/model/model.h5")

actions = ['D', 'E', 'H', 'L', 'O', 'R', 'W']
threshold = 0.5

mp_hands = mp.solutions.hands

sequence = []
predictions = []
word = []

running = False
frame = None
lock = threading.Lock()  # Thread-safe lock for shared variables


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR), results


def extract_keypoints(results):
    if results.multi_hand_landmarks:
        keypoints = []
        for hand_landmarks in results.multi_hand_landmarks:
            for landmark in hand_landmarks.landmark:
                keypoints.append(landmark.x)
                keypoints.append(landmark.y)
                keypoints.append(landmark.z)  # Include the z-coordinate
        return np.array(keypoints, dtype=np.float32)  # Ensure dtype is float32
    else:
        return np.zeros(21 * 3, dtype=np.float32)  # Return zeros with dtype float32


def prediction_loop():
    global running, frame, sequence, predictions, word
    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while running:
            ret, frame_read = cap.read()
            if not ret:
                continue

            cropframe = frame_read[40:400, 0:300]
            image, results = mediapipe_detection(cropframe, hands)
            keypoints = extract_keypoints(results)

            with lock:
                sequence.append(keypoints)
                sequence = sequence[-30:]

                try:
                    if len(sequence) == 30:
                        # Convert sequence to a NumPy array with the correct dtype
                        input_sequence = np.array(sequence, dtype=np.float32)
                        res = model.predict(np.expand_dims(input_sequence, axis=0))[0]
                        predictions.append(np.argmax(res))

                        if np.unique(predictions[-10:])[0] == np.argmax(res):
                            if res[np.argmax(res)] > threshold:
                                if len(word) == 0 or actions[np.argmax(res)] != word[-1]:
                                    word.append(actions[np.argmax(res)])
                except Exception as e:
                    print(f"Error during prediction: {e}")
                    print(f"Sequence dtype: {np.array(sequence).dtype}, Sequence shape: {np.array(sequence).shape}")

            # Update the frame
            with lock:
                frame = frame_read.copy()

            # Add visual elements to the frame
            cv2.rectangle(frame, (0, 40), (300, 400), (0, 255, 0), 2)  # Green box
            small_crop = cv2.resize(cropframe, (200, 200))
            frame[50:250, 320:520] = small_crop
            cv2.putText(frame, 'Place hand inside green box!', (10, 430),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

            time.sleep(0.05)

    cap.release()


def start_prediction():
    global running
    if not running:
        running = True
        threading.Thread(target=prediction_loop, daemon=True).start()


def stop_prediction():
    global running
    running = False


def get_current_word():
    with lock:
        return ''.join(word)


def reset_word():
    global word
    with lock:
        word.clear()


def get_frame():
    with lock:
        return frame

