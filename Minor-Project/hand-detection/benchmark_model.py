import os
import numpy as np
import time
from keras.models import model_from_json
from sklearn.metrics import accuracy_score

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model.h5')
JSON_PATH = os.path.join(BASE_DIR, 'model.json')
DATA_PATH = os.path.join(BASE_DIR, 'MP_Data')

# Constants
actions = np.array(['D', 'E', 'H', 'L', 'O', 'R', 'W'])
sequence_length = 30

def load_model():
    with open(JSON_PATH, "r") as json_file:
        model_json = json_file.read()
    model = model_from_json(model_json)
    model.load_weights(MODEL_PATH)
    return model

def prepare_test_data():
    sequences, labels = [], []
    label_map = {label:num for num, label in enumerate(actions)}
    
    print("Loading data...")
    for action in actions:
        action_path = os.path.join(DATA_PATH, action)
        if not os.path.exists(action_path):
            continue
            
        # Get all sequence folders
        sequence_folders = [f for f in os.listdir(action_path) if os.path.isdir(os.path.join(action_path, f))]
        
        for sequence in sequence_folders:
            window = []
            try:
                for frame_num in range(sequence_length):
                    res = np.load(os.path.join(action_path, sequence, "{}.npy".format(frame_num)))
                    window.append(res)
                sequences.append(window)
                labels.append(label_map[action])
            except Exception as e:
                # print(f"Skipping sequence {sequence} in {action}: {e}")
                pass
                
    return np.array(sequences), np.array(labels)

def benchmark():
    try:
        model = load_model()
        X, y = prepare_test_data()
        
        if len(X) == 0:
            print("No data found for benchmarking.")
            return

        print(f"Running benchmark on {len(X)} sequences...")
        
        start_time = time.time()
        y_pred_probs = model.predict(X)
        end_time = time.time()
        
        y_pred = np.argmax(y_pred_probs, axis=1)
        
        accuracy = accuracy_score(y, y_pred)
        total_time = end_time - start_time
        avg_latency = (total_time / len(X)) * 1000 # ms
        
        print("\n=== Benchmark Results ===")
        print(f"Total Sequences: {len(X)}")
        print(f"Accuracy: {accuracy * 100:.2f}%")
        print(f"Average Inference Latency: {avg_latency:.2f} ms")
        print("=========================")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    benchmark()
