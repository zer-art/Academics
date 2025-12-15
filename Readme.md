# Academics Repository

This repository contains academic resources, notes, and practical files organized by semester and subject. Below is an overview of the structure and contents:

## 2ND_SEM
- **DBMS**: Practical files, SQL commands, and Python integration with database operations.
- **EVS**: Environmental Studies - activities and reference materials.
- **Excel**: Advanced Excel practicals, notes, and worksheets.
- **FTW-sel**: Fit to Work - Inclusive culture and workplace readiness materials.
- **MFDA**: Mathematics for Data Analysis - assignments and practicals on mathematical functions, derivatives, Taylor series, partial derivatives, and extreme value problems.
- **VSD**: Visual Statistics and Data - Data visualization using Seaborn, assignments, and end-term practicals with stock market data.

## 3RD_SEM
- **BML**: Business Machine Learning - practical implementations, decision trees, pandas, and various ML algorithms.
- **BML_SELF**: Self-study notebooks for BML course concepts.
- **DSA**: Data Structures and Algorithms - notes, practicals, and Python implementations including linked lists, hash tables, and algorithm exercises.
- **E**: Miscellaneous resources and materials.
- **SDA**: Statistical Data Analysis - probability, mathematics, slides, and PDFs.

## 5TH_SEM
- **AI**: Artificial Intelligence - practical implementations of AI algorithms including BFS, DFS, and other search algorithms.
- **Cyber Security**: Cybersecurity course materials and resources.
- **Time Series**: Time series analysis - practicals, notes, and course materials.

## 6TH_SEM
- Materials and resources for sixth semester courses.

## Projects

### Major Project: AIVOX - AI Interview Coach
An AI-powered mock interview platform that provides real-time speech recognition, emotion analysis, and intelligent feedback to help users prepare for job interviews. The system combines multiple AI technologies to create an interactive, comprehensive interview practice experience.

**Core Features:**
- **Real-time Speech Recognition**: Utilizes Groq Whisper API with Silero VAD for accurate voice-to-text conversion during interview responses
- **Emotion Analysis**: MediaPipe face tracking analyzes facial expressions to provide confidence scoring and emotional state assessment
- **AI Interviewer**: Dynamic question generation powered by Google Gemini, adapting questions based on selected domain (Software Engineering, Data Science, Product Management, etc.)
- **Performance Reports**: Comprehensive analytics including speech patterns, emotional consistency, answer quality, and actionable improvement suggestions
- **Modern Web Interface**: Responsive Tailwind CSS interface with real-time feedback visualization

**Technical Architecture:**
Built for real-time interaction, AIVOX employs a geometry-based confidence analysis system using MediaPipe's 468 3D facial landmarks instead of traditional CNNs, achieving **19x faster processing** (1.6ms vs 31ms latency) with **42% less CPU usage** and smaller memory footprint. The system leverages Groq's LPU for near-instant speech-to-text processing and geometric analysis for transparent, mathematical confidence scoring (head pose, eye contact, smile elevation).

**Performance Metrics:**
- **Latency**: 1.6ms per frame (vs 31ms with CNN)
- **Processing Speed**: 616 FPS (vs 32 FPS with CNN)
- **CPU Usage**: 113% (vs 155% with CNN)
- **Memory**: 766 MB (vs 881 MB with CNN)

**Technologies Used:** FastAPI, Python 3.10+, Groq Whisper, MediaPipe, Google Gemini, Silero VAD, SoundDevice, Tailwind CSS, Vanilla JavaScript

The project includes detailed benchmarking scripts, comprehensive documentation, environment setup guides, and deployment instructions. Users can run `benchmark_cnn_vs_mediapipe.py` to verify performance improvements on their own hardware.

### Minor Project: Sign Language Recognition & Predictive Text System
An integrated system combining real-time sign language recognition with a predictive text engine, accessible through a Django web interface. The project demonstrates end-to-end machine learning pipeline from gesture capture to text refinement.

**System Components:**

**1. Hand Detection (LSTM-based Recognition)**
- Captures video feed and extracts hand landmarks using MediaPipe Holistic
- LSTM neural network trained to classify sign language gestures into specific actions (D, E, H, L, O, R, W)
- Real-time sequence-based gesture recognition with temporal modeling
- Achieves **100% accuracy** on validation set (280 test sequences)
- **1.16ms average latency** per sequence inference
- Includes data collection pipeline (`collectdata.py`) for creating custom gesture datasets
- Model persistence in H5 format with comprehensive training logs

**2. Word Suggestion & Autocorrect Engine**
- Probabilistic spell-checking algorithm using statistical language models
- Trained on extensive text corpus for context-aware corrections
- Edit distance algorithms (Levenshtein) for identifying and correcting misspelled words
- **Top-1 accuracy**: 20% (correct word as first suggestion)
- **Top-5 accuracy**: 33.33% (correct word in top 5 suggestions)
- **Average latency**: 160ms per word
- Handles common typing errors and gesture recognition ambiguities

**3. Django Web Application Interface**
- Full-stack web application serving the integrated system
- Real-time gesture recognition interface with webcam integration
- Database persistence using SQLite for user sessions and results
- MVC architecture with Django best practices
- User-friendly interface for gesture practice and text verification
- Development server accessible at `http://127.0.0.1:8000/`

**Performance Benchmarks:**
The project includes dedicated benchmarking scripts:
- `hand-detection/benchmark_model.py`: Validates model accuracy and inference latency
- `word-suggest/benchmark.py`: Evaluates autocorrect performance and suggestion quality

**Technologies Used:** Python 3.9+, TensorFlow/Keras, MediaPipe Holistic, OpenCV, Django 3.2, LSTM Networks, NLP libraries, SQLite, Conda

The system is modular, with each component (hand detection, word suggestion, web interface) being independently runnable and testable. Complete setup instructions, dependency management via `requirements.txt`, and usage documentation are included.

## How to Use
Navigate through the folders to find resources for specific subjects or semesters. Files are named descriptively for easy identification.

