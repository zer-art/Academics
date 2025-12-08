# Sign Language Recognition & Predictive Text System 🖐️📝

An integrated system that combines real-time **Sign Language Recognition** with a **Predictive Text Engine**, verified via a **Django Web Interface**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-Enabled-orange)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Detected-green)
![Django](https://img.shields.io/badge/Django-3.2-092E20)

## 🏗️ System Architecture

The project consists of three main modules working in tandem:

1.  **Hand Detection (LSTM)**: Captures video feed, extracts landmarks using MediaPipe, and classifies gestures using an LSTM neural network.
2.  **Word Suggestion**: A probabilistic autocorrect engine that refines the recognized text to improve accuracy.
3.  **App Interface**: A Django-based web application that serves the model and provides the user interface.

## 📊 Performance Benchmarks

Real-world performance metrics collected on a local machine (M1/M2/Intel Mac).

| Component | Metric | Value | Details |
| :--- | :--- | :--- | :--- |
| **Hand Detection** | **Accuracy** | **100.00%** | Evaluated on 280 test sequences |
| | **Avg Latency** | **1.16 ms** | Per-sequence inference time |
| **Word Suggestion** | **Top-1 Accuracy** | **20.00%** | Correct word is the first suggestion |
| | **Top-5 Accuracy** | **33.33%** | Correct word is in top 5 suggestions |
| | **Avg Latency** | **160 ms** | Average processing time per word |

> **Note**: Hand detection accuracy is high on the validation set, implying robust learning of the specific training gestures (actions: D, E, H, L, O, R, W).

## 🚀 Getting Started

### Prerequisites

- Anaconda or Miniconda installed.

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd Minor-Project
    ```

2.  **Set up the Environment**
    Create and activate the conda environment:
    ```bash
    conda create -n academic python=3.9 -y
    conda activate academic
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## 💻 Usage

### Running the Web Application
Start the Django server to use the full system:

```bash
cd dev
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser.

### Running Benchmarks
You can verify the performance metrics yourself:

**Hand Detection:**
```bash
python hand-detection/benchmark_model.py
```

**Word Suggestion:**
```bash
python word-suggest/benchmark.py
```

## 📂 Project Structure

- `hand-detection/`: Model training and real-time inference logic.
- `word-suggest/`: Probabilistic spell-checking algorithm.
- `dev/`: Django web application source code.
- `requirements.txt`: Unified project dependencies.
