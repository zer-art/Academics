# AIVOX - AI Interview Coach

AI-powered mock interview platform with real-time speech recognition, emotion analysis, and intelligent feedback.

## ✨ Features

- **🎤 Real-time Speech Recognition** - Groq Whisper API with Silero VAD
- **😊 Emotion Analysis** - MediaPipe face tracking and expression detection  
- **🤖 AI Interviewer** - Dynamic questions via Google Gemini
- **📊 Performance Reports** - Comprehensive analytics and feedback
- **🌐 Modern UI** - Responsive Tailwind CSS interface

## ⚡ Performance & Architecture

Built for real-time interaction, AIVOX uses a geometry-based confidence analysis system (MediaPipe) instead of traditional heavy CNNs, resulting in **19x faster processing**.

| Metric | Traditional CNN (ResNet50) | AIVOX (MediaPipe) | Improvement |
|--------|----------------------------|-------------------|-------------|
| **Latency** | 31.0ms | **1.6ms** | 🚀 **19.1x Faster** |
| **FPS** | 32 FPS | **616 FPS** | ⏩ **High Frequency** |
| **CPU Usage** | 155% | **113%** | 🔋 **42% Less Load** |
| **Memory** | 881 MB | **766 MB** | 📦 **1.2x Smaller** |

### 🔬 Benchmarking Methodology

Results were measured on **Apple Silicon (ARM64)** using the included `benchmark_cnn_vs_mediapipe.py` script.
- **Hardware:** Apple Silicon (macOS Darwin 24.6.0)
- **Baseline:** ResNet50 (PyTorch) running on CPU.
- **AIVOX:** MediaPipe FaceMesh running on CPU.
- **Method:** Average over 100 runs after 10 warm-up iterations.

```bash
# Verify these results on your machine
conda activate major
python benchmark_cnn_vs_mediapipe.py
```

### Key Technical Highlights
- **Groq LPU Inference:** Utilizes Groq's LPU for near-instant speech-to-text processing.
- **Geometric Analysis:** Uses 468 3D facial landmarks for transparent, mathematical confidence scoring (Head Pose, Eye Contact, Smile Elevation) rather than "black box" neural networks.
- **Client-Side Optimization:** Heavy lifting is done efficiently, allowing smooth performance even on standard hardware.

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (3.10.19 recommended)
- **Audio devices** (microphone and speakers required)
- **Groq API key** - Free tier available at [console.groq.com](https://console.groq.com)
- **Google Gemini API key** - Free tier at [makersuite.google.com](https://makersuite.google.com)

### Installation

1. **Clone the repository**

Option A — Full clone
```bash
git clone https://github.com/zer-art/Academics.git
cd Academics/Major-project
```

Option B — Sparse clone (recommended if you only need the `Major-project` folder)
Requires Git >= 2.25
```bash
# Clone repository with sparse support (only downloads required files)
git clone --filter=blob:none --sparse https://github.com/zer-art/Academics.git
cd Academics
# Initialize and set sparse-checkout to only include Major-project
git sparse-checkout init --cone
git sparse-checkout set Major-project
cd Major-project
```

2. **Create virtual environment** (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create .env file in project root
touch .env
```

Add the following to `.env`:
```env
GEMINI=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here
```

5. **Run the application**
```bash
chmod +x run.sh  # Make script executable (first time only)
./run.sh
```

6. **Access the application**
   - Open browser at `http://localhost:8000`
   - Ensure microphone permissions are granted

## 🛠️ Tech Stack

**Backend:** FastAPI, Python 3.10  
**AI/ML:** Groq Whisper, MediaPipe, Google Gemini  
**Frontend:** Tailwind CSS, Vanilla JS  
**Audio:** Silero VAD, SoundDevice  

## 📁 Project Structure

```
Major-project/
├── app/
│   ├── main.py              # FastAPI application & API endpoints
│   ├── config.py            # Configuration settings
│   ├── src/
│   │   ├── __init__.py
│   │   ├── facemesh.py      # MediaPipe emotion analysis
│   │   ├── llm.py           # Gemini AI integration
│   │   ├── prompt.py        # Interview prompts
│   │   └── utils.py         # Core interview logic & audio
│   └── templates/
│       ├── interview.html   # Interview session page
│       └── report.html      # Performance report page
├── landing/
│   ├── index.html           # Landing page
│   └── assets/              # CSS, JS, images
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── run.sh                   # Launch script
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with:

```env
# Required API Keys
GEMINI=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Application Secret (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your_secret_key_here
```

### Getting API Keys

**Groq API (Whisper Speech-to-Text)**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Navigate to API Keys section
4. Create new API key
5. Copy key to `GROQ_API_KEY` in `.env`

**Google Gemini API (AI Interviewer)**
1. Visit [makersuite.google.com](https://makersuite.google.com)
2. Sign in with Google account
3. Get API key from console
4. Copy key to `GEMINI` in `.env`

### Audio Configuration

The application requires:
- **Microphone access** for recording answers
- **Speaker/headphone output** for AI question playback
- **Default audio device** properly configured in your system

On macOS/Linux, ensure no other applications are blocking audio access.

## 📖 Usage

1. **Launch application** - Run `./run.sh` and open `http://localhost:8000`
2. **Select domain** - Choose from Software Engineering, Data Science, Product Management, etc.
3. **Start interview** - AI will ask domain-specific questions
4. **Answer via voice** - Speak your answers (microphone required)
5. **Real-time feedback** - Camera tracks facial expressions for confidence analysis
6. **View report** - Get comprehensive performance analysis at the end
7. **Download PDF** - On the Report page click **Download Report** to save a PDF copy of your interview analysis (client-side PDF generation).

### Tips for Best Results
- Use in a quiet environment for better speech recognition
- Maintain good lighting for accurate emotion detection
- Speak clearly and at a moderate pace
- Allow camera and microphone permissions when prompted

## 🔍 Troubleshooting

**Audio Issues**
- Ensure microphone/speakers are connected and set as default
- Check system audio permissions for the terminal/Python
- Verify no other apps are using audio devices

**API Errors**
- Verify API keys are correctly set in `.env`
- Check Groq/Gemini API quotas and rate limits
- Ensure stable internet connection

**Installation Issues**
- Use Python 3.10+ (check with `python3 --version`)
- Update pip: `pip install --upgrade pip`
- On macOS, install PortAudio: `brew install portaudio`
- On Linux, install: `sudo apt-get install portaudio19-dev python3-pyaudio`

## 🤝 Contributing

Pull requests welcome! Please follow existing code style.

## 📄 License

Educational and research use only.
