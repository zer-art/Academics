# AI-Powered Interview Coach: Multimodal Emotion & Language-Aware Feedback System

An advanced AI interview coaching platform that simulates mock interviews using Large Language Models (LLM) and provides real-time multimodal analysis through Computer Vision, Natural Language Processing, and Deep Learning techniques.

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

### Frontend
- **HTML5/CSS3/JavaScript**: Modern responsive web interface
- **Bootstrap 5**: Professional UI framework
- **WebRTC**: Real-time audio/video capture and processing
- **Canvas API**: Live video frame analysis
- **Chart.js**: Interactive performance visualizations

### Backend
- **Python/Flask**: Core application logic and API endpoints
- **OpenCV**: Computer vision and image processing
- **DeepFace**: Advanced facial emotion recognition
- **N8N Integration**: Workflow automation capabilities

### AI & ML Models
- **LLM Integration**: Gemini/GPT for interview question generation and evaluation
- **DeepFace**: Pre-trained facial expression and emotion recognition
- **Real-time Analysis**: Live emotion detection and feedback systems
- **Multimodal Processing**: Combined vision, audio, and text analysis

## Project Structure

```
MAJOR-PROJECT/
├── app/                        # Main application backend
│   ├── main.py                # Flask application entry point
│   ├── config.py              # Application configuration
│   ├── routers/               # API route handlers
│   │   └── interview.py       # Interview-specific endpoints
│   ├── services/              # Business logic services
│   │   ├── integration/       # External service integrations
│   │   │   └── n8n.py        # N8N workflow integration
│   │   └── vision/           # Computer vision services
│   │       └── deepface.py   # Facial analysis implementation
│   └── templates/            # HTML templates
│       └── interview.html    # Interactive interview interface
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
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration (if applicable)
DATABASE_URL=your_database_url_here

# N8N Integration (optional)
N8N_WEBHOOK_URL=your_n8n_webhook_url
```

### 3. API Key Setup

**For Gemini AI:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

**For OpenAI (optional):**
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an API key
3. Add it to your `.env` file

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
cd app
python main.py
```

### Accessing the Application

1. **Landing Page**: Visit `http://localhost:5000` for the marketing site
2. **Interview Interface**: Navigate to the interview section or visit `http://localhost:5000/interview`
3. **API Endpoints**: Available at `http://localhost:5000/api/`

### Interview Flow

1. **Camera Permission**: Grant camera access for facial analysis
2. **Interview Setup**: AI generates personalized questions
3. **Live Interview**: Real-time interaction with emotion tracking
4. **Performance Analysis**: Continuous feedback and scoring
5. **Session Summary**: Comprehensive report with recommendations

## API Endpoints

### Core Interview APIs

- `POST /api/analyze-frame`: Real-time facial emotion analysis
- `GET /api/interview/questions`: Generate interview questions
- `POST /api/interview/evaluate`: Evaluate interview responses
- `GET /api/interview/report`: Generate performance reports

### Integration APIs

- `POST /api/n8n/webhook`: N8N workflow integration
- `GET /api/health`: Application health check

## Real-time Features

### Live Emotion Analysis
- **Frequency**: Analysis every 2 seconds
- **Models**: DeepFace emotion recognition
- **Output**: Emotion, confidence score, facial landmarks
- **History**: Last 10 emotion states tracked

### Performance Feedback
- **Real-time Scoring**: Instant evaluation of responses
- **Visual Feedback**: Live performance overlays
- **Adaptive Questions**: Dynamic difficulty adjustment
- **Progress Tracking**: Session-based improvement metrics

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

1. **Camera Access Denied**
   - Ensure browser permissions are granted
   - Check HTTPS requirements for WebRTC
   - Verify camera is not in use by other applications

2. **API Connection Issues**
   - Verify API keys in `.env` file
   - Check internet connectivity
   - Confirm API rate limits not exceeded

3. **Emotion Analysis Not Working**
   - Ensure adequate lighting for facial recognition
   - Check DeepFace model installation
   - Verify camera feed quality

### Error Messages

- **"Camera permission required"**: Grant browser camera access
- **"API key not found"**: Check `.env` configuration
- **"Analysis failed"**: Verify DeepFace installation and model files

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
cd app
python main.py
```

### Adding New Features

1. **New API Endpoints**: Add to [`app/routers/`](app/routers/)
2. **Business Logic**: Implement in [`app/services/`](app/services/)
3. **Frontend Updates**: Modify templates in [`app/templates/`](app/templates/)
4. **Landing Page**: Update [`landing/index.html`](landing/index.html)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational and research purposes. Please ensure compliance with API terms of service and respect privacy regulations when handling user data.

## Future Enhancements

- [ ] Advanced voice analysis integration
- [ ] Multi-language interview support
- [ ] HR system integrations
- [ ] Advanced analytics dashboard
- [ ] Mobile application development
- [ ] Interview scheduling system
- [ ] Candidate comparison tools
- [ ] Custom branding options
- [ ] Advanced reporting templates
- [ ] Machine learning model improvements

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the [issues](issues) in the repository
3. Contact the development team

---

*This AI Interview Coach is designed to enhance interview preparation and should be used as a supplementary tool in the hiring process. Human judgment remains essential in final hiring decisions.*
