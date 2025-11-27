# AI-Powered Interview Coach: Free & Blazing Fast Multimodal System

A next-generation AI interview coaching platform featuring a **"Free & Blazing Fast"** architecture that delivers:
- **$0 Cost**: Free Groq API for state-of-the-art speech recognition
- **Low Latency**: Continuous voice activity detection with 100ms response time
- **High Accuracy**: Whisper-large-v3 transcription via Groq with local Silero VAD

This system provides comprehensive interview preparation through real-time multimodal analysis using Computer Vision, Advanced Speech Processing, and Large Language Models.

## 🚀 Modern Architecture Highlights

- **Continuous Voice Activity Detection**: Silero VAD running locally on microphone stream
- **Smart Audio Buffering**: 0.5s rolling buffer prevents word cutoff
- **Intelligent Speech Recognition**: Free Groq API with Whisper-large-v3 model
- **Real-time Emotion Analysis**: DeepFace computer vision for facial expression tracking
- **FastAPI Backend**: Modern async Python web framework
- **Blazing Fast Performance**: Optimized for sub-second response times

## Project Overview

This system provides comprehensive interview preparation by:
- **AI Interviewer**: Uses LLM to conduct realistic mock interviews with dynamic question generation
- **Real-time Facial Expression Analysis**: Computer vision algorithms analyze micro-expressions, confidence, and emotional state using DeepFace
- **Voice Analysis**: Audio processing evaluates tone, pace, clarity, and stress levels
- **Language Processing**: NLP assesses communication skills, grammar, and content quality
- **Live Performance Feedback**: Instant analysis and improvement suggestions during the interview
- **Comprehensive Reporting**: Detailed performance analytics with emotion tracking and recommendations

## Features

### 🤖 AI-Powered Interview Simulation
- **Dynamic Question Generation**: Creates job-specific interview questions
- **Intelligent Response Evaluation**: AI scoring of answers with detailed feedback
- **Adaptive Difficulty**: Adjusts questions based on candidate responses
- **Multiple Interview Types**: Technical, behavioral, and situational interviews
- **Real-time AI Interaction**: Live conversation with AI interviewer

### 👁️ Real-time Computer Vision Analysis
- **Live Facial Expression Recognition**: Real-time emotion detection using DeepFace
- **Emotion Tracking**: Continuous monitoring and history of emotional states
- **Confidence Assessment**: Body language and facial cue analysis
- **Performance Overlay**: Live feedback display during interview
- **Micro-expression Detection**: Subtle emotional pattern recognition

### 🎤 Voice & Speech Analysis (Beta)
- **Tone Analysis**: Emotional state through voice patterns
- **Speech Clarity**: Pronunciation and articulation assessment
- **Pace Evaluation**: Speaking speed optimization
- **Stress Detection**: Voice-based anxiety indicators

### 📝 Natural Language Processing
- **Content Quality Assessment**: Answer relevance and structure analysis
- **Grammar Analysis**: Language proficiency evaluation
- **Communication Skills**: Clarity and effectiveness measurement
- **Industry Keyword Recognition**: Role-specific terminology usage

### 📊 Comprehensive Real-time Reporting
- **Live Performance Metrics**: Real-time scoring across all dimensions
- **Emotion History Tracking**: Detailed emotional state progression
- **Visual Analytics**: Interactive charts and performance visualizations
- **Instant Improvement Suggestions**: Live coaching recommendations
- **Session Summary Reports**: Comprehensive post-interview analysis

### 🌐 Modern Web Interface
- **Responsive Design**: Mobile-friendly interview platform
- **WebRTC Integration**: Real-time video capture and processing
- **Professional Landing Page**: Marketing and feature showcase
- **Interactive Demo**: Live interview simulation experience

## Technology Stack

### 🎤 Modern Audio Processing Stack
- **Silero VAD**: Local voice activity detection (continuous stream processing)
- **Groq API**: Free Whisper-large-v3 speech-to-text transcription
- **Smart Buffering**: Rolling audio buffer with intelligent chunking
- **PyTorch**: Deep learning framework for audio processing
- **SoundDevice**: Real-time audio capture and streaming

### 🖥️ Backend Architecture
- **FastAPI**: Modern async Python web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: Lightning-fast ASGI server
- **Threading**: Concurrent audio processing and VAD
- **Async/Await**: Non-blocking I/O for real-time performance

### 🧠 AI & ML Models
- **Groq Whisper-large-v3**: State-of-the-art speech recognition (free)
- **Silero VAD**: Local voice activity detection model
- **DeepFace**: Advanced facial emotion recognition
- **Google Gemini**: LLM for question generation and evaluation
- **LangChain**: LLM orchestration and prompt management

### 🌐 Frontend
- **HTML5/CSS3/JavaScript**: Modern responsive web interface
- **Bootstrap 5**: Professional UI framework
- **WebRTC**: Real-time audio/video capture
- **Canvas API**: Live video frame analysis
- **Chart.js**: Performance visualization

## Project Structure

```
MAJOR-PROJECT/
├── app/                        # FastAPI application
│   ├── main.py                # FastAPI application entry point
│   ├── config.py              # Application configuration
│   ├── src/                   # Core application modules
│   │   ├── utils.py          # Interview logic and audio handling
│   │   ├── deepface.py       # Facial emotion analysis
│   │   ├── llm.py            # LLM integration (Gemini)
│   │   └── prompt.py         # Prompt templates
│   └── templates/            # Jinja2 HTML templates
│       ├── interview.html    # Interactive interview interface
│       └── report.html       # Performance report page
├── landing/                   # Marketing website
│   ├── index.html            # Main landing page
│   └── assets/               # Static assets
│       ├── css/              # Stylesheets
│       ├── js/               # JavaScript files
│       ├── img/              # Images and branding
│       └── vendor/           # Third-party libraries
├── requirements.txt          # Python dependencies
├── run.sh                   # Application startup script
├── .env                     # Environment configuration
└── README.md               # Project documentation
```

## Setup & Installation

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd MAJOR-PROJECT
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# AI Model API Keys
GEMINI=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# JWT Secret Key (change this to a secure random string in production)
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Google OAuth Credentials (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# GitHub OAuth Credentials (optional)
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback

# Frontend URL
FRONTEND_URL=http://localhost:8000
```

### 3. API Key Setup

**For Google Gemini AI:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI=your_key_here`

**For Groq API (Free Speech Recognition):**
1. Visit [Groq Console](https://console.groq.com/)
2. Create a free account and generate an API key
3. Add it to your `.env` file as `GROQ_API_KEY=your_key_here`

**Note**: Groq provides free access to Whisper-large-v3 for speech recognition!

### 4. Optional: Google Cloud Setup

For enhanced voice features:
1. Create a Google Cloud project
2. Enable Text-to-Speech and Speech-to-Text APIs
3. Download service account credentials
4. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## Usage

### Quick Start

```bash
# Make the run script executable
chmod +x run.sh

# Start the application
./run.sh
```

Or run directly with Python:

```bash
# Start the FastAPI server
python app/main.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Accessing the Application

1. **Landing Page**: Visit `http://localhost:8000` for the marketing site
2. **Interview Interface**: Navigate to `http://localhost:8000/interview`
3. **Report Page**: View results at `http://localhost:8000/report`
4. **API Documentation**: FastAPI auto-docs at `http://localhost:8000/docs`
5. **Health Check**: Monitor status at `http://localhost:8000/health`

### Interview Flow

1. **Initialize Session**: Start interview with role-specific question generation
2. **Audio Monitoring**: Continuous voice activity detection begins automatically
3. **Smart Recording**: Voice detection triggers recording with 0.5s buffer
4. **Real-time Transcription**: Audio sent to Groq for instant Whisper-large-v3 transcription
5. **Answer Completion**: 3-second silence threshold indicates complete answer
6. **Live Analysis**: Immediate emotion tracking and answer evaluation
7. **Adaptive Questions**: Dynamic follow-up based on responses
8. **Session Report**: Comprehensive analysis with improvement recommendations

### 🎤 Audio Processing Features

- **Continuous VAD**: Silero model detects voice activity in real-time
- **Smart Buffering**: Rolling 500ms buffer prevents word cutoff
- **Adaptive Recording**: Automatic start/stop based on voice activity
- **Zero Latency**: Local VAD processing with no API delays
- **High Accuracy**: Whisper-large-v3 transcription via free Groq API

## API Endpoints

### Core Interview APIs

- `POST /start_interview`: Initialize new interview session with role-specific questions
- `GET /ask_question/{question_index}`: Text-to-speech for specific question
- `POST /record_answer`: Wait for and capture complete user answer
- `POST /analyze_emotion`: Real-time facial emotion analysis
- `POST /finish_interview`: Complete session and generate comprehensive report
- `POST /test_audio`: Test audio system functionality

### System APIs

- `GET /health`: Application health check and service status
- `GET /docs`: FastAPI automatic documentation
- `GET /`: Landing page
- `GET /interview`: Interview interface
- `GET /report`: Performance report page

### API Request/Response Examples

```python
# Start Interview
POST /start_interview
{
    "user_role": "Software Engineer"
}

# Response
{
    "success": true,
    "questions": ["Tell me about yourself..."],
    "message": "Interview initialized for Software Engineer"
}

# Record Answer (waits for complete speech)
POST /record_answer
{
    "session_id": "default"
}

# Response
{
    "success": true,
    "answer": "I am a software engineer with 5 years...",
    "score": 85,
    "feedback": "Great technical depth..."
}
```

## Real-time Features

### 🎤 Continuous Audio Processing
- **Voice Activity Detection**: Silero VAD running at 10Hz (100ms intervals)
- **Smart Recording**: Automatic start/stop based on speech detection
- **Buffer Management**: 500ms rolling buffer to capture complete words
- **Silence Detection**: 1s pause stops recording, 3s pause completes answer
- **Groq Integration**: Free Whisper-large-v3 transcription with sub-second latency

### 📊 Live Emotion Analysis
- **Frequency**: Facial analysis every 2 seconds during active session
- **Models**: DeepFace emotion recognition with confidence scoring
- **Output**: Real-time emotion state, confidence, and facial landmarks
- **History**: Continuous tracking throughout interview session
- **Integration**: Synchronized with speech analysis for comprehensive feedback

### ⚡ Performance Optimization
- **Threading**: Concurrent audio processing and VAD analysis
- **Async Processing**: Non-blocking I/O for real-time responsiveness
- **Local VAD**: Zero-latency voice detection without API calls
- **Smart Chunking**: Optimal audio segment sizes for Groq API
- **Memory Efficient**: Rolling buffers prevent memory accumulation

## Interview Question Types

The system generates various question categories:

### Technical Questions
- Role-specific technical knowledge
- Problem-solving scenarios
- Coding challenges (for technical roles)
- System design questions

### Behavioral Questions
- Past experience analysis
- Situational judgment
- Leadership and teamwork
- Conflict resolution

### Company Culture
- Value alignment assessment
- Motivation evaluation
- Career goals analysis
- Cultural fit evaluation

## Scoring and Analytics

### Performance Metrics
- **Overall Score**: 0-10 scale comprehensive rating
- **Emotion Stability**: Consistency in emotional presentation
- **Response Quality**: Content relevance and depth
- **Communication Skills**: Clarity and articulation
- **Confidence Level**: Body language and speech patterns

### Real-time Feedback Categories
- **Facial Expression**: Emotion appropriateness
- **Response Content**: Answer quality and relevance
- **Communication Style**: Clarity and professionalism
- **Engagement Level**: Eye contact and attention

## Customization

### Adding New Analysis Features

Modify [`app/services/vision/deepface.py`](app/services/vision/deepface.py) to add new computer vision capabilities.

### Custom Question Templates

Update the question generation logic in [`app/routers/interview.py`](app/routers/interview.py).

### UI Customization

Modify [`app/templates/interview.html`](app/templates/interview.html) for interview interface changes or [`landing/index.html`](landing/index.html) for landing page updates.

## Troubleshooting

### Common Issues

1. **Groq API Issues**
   - Verify `GROQ_API_KEY` is set in `.env` file
   - Check Groq API rate limits (free tier limitations)
   - Ensure internet connectivity for API calls
   - Test with: `curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models`

2. **Audio System Problems**
   - **Microphone Access**: Ensure browser permissions granted
   - **Device Detection**: Run `/test_audio` endpoint to verify audio devices
   - **VAD Model Loading**: Check Silero VAD download: `torch.hub.load('snakers4/silero-vad', 'silero_vad')`
   - **Audio Quality**: Ensure microphone is not muted and has adequate volume

3. **Emotion Analysis Not Working**
   - Verify adequate lighting for facial recognition
   - Check DeepFace model installation and dependencies
   - Ensure webcam permissions are granted
   - Test camera feed quality and positioning

4. **Performance Issues**
   - **Slow Response**: Check internet connection for Groq API calls
   - **High CPU Usage**: Silero VAD processing is CPU-intensive
   - **Memory Usage**: Monitor rolling buffer sizes in continuous processing
   - **Threading Issues**: Ensure proper cleanup of audio threads

### Error Messages

- **"GROQ_API_KEY not found"**: Add API key to `.env` file
- **"Audio monitoring failed"**: Check microphone permissions and device availability
- **"VAD model loading failed"**: Install PyTorch and download Silero model
- **"Camera permission required"**: Grant browser camera access
- **"Interview not initialized"**: Call `/start_interview` endpoint first

### Debug Mode

```bash
# Enable detailed logging
uvicorn app.main:app --log-level debug --reload

# Test individual components
python -c "from app.src.utils import ModernAudioHandler; print('Audio handler ready')"
```

## Development

### Running in Development Mode

```bash
# With auto-reload for development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using the FastAPI development server
python app/main.py
```

### Testing the Audio System

```bash
# Test Groq API connection
python -c "from groq import Groq; print('Groq client ready')"

# Test Silero VAD model
python -c "import torch; torch.hub.load('snakers4/silero-vad', 'silero_vad')"

# Test audio devices
curl -X POST http://localhost:8000/test_audio
```

### Adding New Features

1. **New API Endpoints**: Add to [`app/main.py`](app/main.py)
2. **Audio Processing**: Modify [`app/src/utils.py`](app/src/utils.py) ModernAudioHandler class
3. **Frontend Updates**: Update templates in [`app/templates/`](app/templates/)
4. **Landing Page**: Modify [`landing/index.html`](landing/index.html)
5. **AI Integration**: Update LLM logic in [`app/src/llm.py`](app/src/llm.py)

### Architecture Components

```python
# Main FastAPI application
app/main.py

# Core interview logic and audio processing
app/src/utils.py:
  - InterviewSession: Session management
  - ModernAudioHandler: Groq + Silero VAD integration
  - EmotionAnalyzer: DeepFace integration
  - InterviewScorer: LLM-based answer evaluation
  - ReportGenerator: Comprehensive reporting

# AI model integrations
app/src/llm.py: Gemini LLM integration
app/src/deepface.py: Facial emotion analysis
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational and research purposes. Please ensure compliance with API terms of service and respect privacy regulations when handling user data.

## Future Enhancements

- [ ] **Enhanced Audio Processing**
  - Multi-language speech recognition support
  - Real-time accent and pronunciation analysis
  - Voice stress detection and coaching
  - Background noise cancellation

- [ ] **Advanced AI Features**
  - GPT-4 integration for enhanced question generation
  - Custom AI interviewer personalities
  - Industry-specific interview templates
  - Behavioral pattern recognition

- [ ] **Performance Optimizations**
  - WebAssembly VAD processing for browser-side detection
  - Edge computing deployment options
  - Real-time model optimization
  - Reduced latency through model quantization

- [ ] **Enterprise Features**
  - Multi-tenant support and user management
  - Advanced analytics dashboard
  - HR system integrations (ATS, HRIS)
  - White-label customization options

- [ ] **Platform Expansion**
  - Mobile application (iOS/Android)
  - Desktop application with offline capabilities
  - Progressive Web App (PWA) support
  - Multi-platform deployment guides

- [ ] **Collaboration Tools**
  - Interview scheduling system
  - Candidate comparison and ranking
  - Team collaboration features
  - Interview replay and review system

---

*This AI Interview Coach leverages cutting-edge free APIs and local processing to deliver enterprise-grade interview preparation at $0 cost. The system is designed for educational and professional development purposes.*
