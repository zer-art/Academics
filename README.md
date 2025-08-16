# AI-Powered Interview Coach: Multimodal Emotion & Language-Aware Feedback System

An advanced AI interview coaching platform that simulates mock interviews using Large Language Models (LLM) and analyzes candidate performance through Computer Vision, Natural Language Processing, and Deep Learning techniques.

## Project Overview

This system provides comprehensive interview preparation by:
- **AI Interviewer**: Uses LLM to conduct realistic mock interviews
- **Facial Expression Analysis**: Computer vision algorithms analyze micro-expressions, confidence, and emotional state
- **Voice Analysis**: Audio processing evaluates tone, pace, clarity, and stress levels
- **Language Processing**: NLP assesses communication skills, grammar, and content quality
- **Real-time Feedback**: Instant performance analysis and improvement suggestions

## Features

### 🤖 AI-Powered Interview Simulation
- **Dynamic Question Generation**: Creates job-specific interview questions
- **Intelligent Response Evaluation**: AI scoring of answers with detailed feedback
- **Adaptive Difficulty**: Adjusts questions based on candidate responses
- **Multiple Interview Types**: Technical, behavioral, and situational interviews

### 👁️ Computer Vision Analysis
- **Facial Expression Recognition**: Real-time emotion detection
- **Eye Contact Tracking**: Measures engagement and confidence
- **Posture Analysis**: Body language assessment
- **Micro-expression Detection**: Subtle emotional cues

### 🎤 Voice & Speech Analysis  
- **Tone Analysis**: Emotional state through voice patterns
- **Speech Clarity**: Pronunciation and articulation assessment
- **Pace Evaluation**: Speaking speed optimization
- **Stress Detection**: Voice-based anxiety indicators

### 📝 Natural Language Processing
- **Content Quality**: Answer relevance and structure
- **Grammar Analysis**: Language proficiency assessment
- **Communication Skills**: Clarity and effectiveness measurement
- **Keyword Recognition**: Industry-specific terminology usage

### 📊 Comprehensive Reporting
- **Performance Metrics**: Detailed scoring across all dimensions
- **Visual Analytics**: Charts and graphs showing strengths/weaknesses
- **Improvement Suggestions**: Personalized coaching recommendations
- **Progress Tracking**: Performance evolution over time

## Technology Stack

### Frontend
- **HTML5/CSS3/JavaScript**: Modern web interface
- **Bootstrap 5**: Responsive design framework
- **WebRTC**: Real-time audio/video capture
- **Chart.js**: Interactive performance visualizations

### Backend
- **Python**: Core application logic
- **Flask/FastAPI**: Web framework for API endpoints
- **OpenCV**: Computer vision processing
- **TensorFlow/PyTorch**: Deep learning models
- **spaCy/NLTK**: Natural language processing

### AI & ML Models
- **LLM Integration**: Gemini/GPT for interview generation
- **Emotion Recognition**: Pre-trained facial expression models
- **Speech Processing**: Audio analysis algorithms
- **Sentiment Analysis**: Text emotion classification

## Project Structure

```
MAJOR-PROJECT/
├── frontend/                    # Web interface
│   ├── index.html              # Main landing page
│   ├── interview-demo.html     # Interactive demo page
│   ├── assets/                 # Static assets
│   │   ├── css/               # Stylesheets
│   │   ├── js/                # JavaScript files
│   │   ├── img/               # Images and icons
│   │   └── vendor/            # Third-party libraries
│   └── forms/                 # Contact forms
├── src/                        # Backend source code
│   ├── __init__.py            # Package initialization
│   ├── LLM_integration.py     # AI model integration
│   ├── utils.py               # Utility functions
│   └── vision.py              # Computer vision processing
├── models/                     # ML model storage
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script
└── README.md                  # Project documentation
```

## Setup & Installation

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root:

```env
GEMINI=your_gemini_api_key_here
```

To get a Gemini API key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### 3. Optional: Google Cloud Setup (for Voice Features)

For Text-to-Speech and Speech-to-Text features:

1. Create a Google Cloud project
2. Enable the Text-to-Speech and Speech-to-Text APIs
3. Create a service account and download the JSON key file
4. Set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

## Usage

### Quick Start

Run the main application:

```bash
python main.py
```

Follow the prompts to:
1. Enter candidate name
2. Specify job title
3. Select experience level
4. Choose number of questions
5. Conduct the interview

### Example Usage

```python
from src.LLM_integration import InterviewConductor

# Initialize the interview system
conductor = InterviewConductor()

# Start an interview
questions = conductor.start_interview(
    job_title="Software Engineer",
    candidate_name="John Doe",
    experience_level="mid-level"
)

# Conduct the interview (this will prompt for responses)
interview_data = conductor.conduct_interview(questions)

# Generate a report
report = conductor.generate_final_report()
print(report)

# Save the data
filename = conductor.save_interview_data()
```

### Run Example Demo

```bash
python example_usage.py
```

This will run a simulated interview with sample responses to demonstrate the system.

## File Structure

```
MAJOR-PROJECT/
├── main.py                 # Main application
├── example_usage.py        # Example/demo script
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── src/
│   ├── __init__.py
│   ├── utils.py          # Utility functions (TTS, STT, question generation)
│   └── LLM_integration.py # Main interview conductor class
└── models/               # (Future: ML models)
```

## Interview Process

1. **Setup**: System generates job-specific questions based on the role and experience level
2. **Question Types**:
   - Technical questions specific to the role
   - Behavioral questions
   - Situational questions
   - Problem-solving scenarios
   - Experience and background questions
3. **Evaluation**: Each response is scored (0-10) with detailed feedback
4. **Reporting**: Comprehensive report with overall score and recommendations

## Sample Interview Questions

For a "Python Developer" position, the system might generate:

- "Explain the difference between lists and tuples in Python and when you'd use each."
- "Describe a time when you had to debug a complex issue in production."
- "How would you optimize a Python application that's running slowly?"
- "Tell me about your experience with Python frameworks like Django or Flask."

## Scoring System

- **9-10**: Excellent response demonstrating deep knowledge
- **7-8**: Good response with solid understanding
- **5-6**: Average response meeting basic requirements
- **3-4**: Below average response with gaps
- **0-2**: Poor response or no answer

## Voice Features (Beta)

The system includes basic support for voice interactions:

- **Text-to-Speech**: Convert interview questions to audio
- **Speech-to-Text**: Convert candidate responses to text

Note: Voice features require Google Cloud setup and are currently in beta.

## Customization

### Adding New Question Types

Modify the prompt in `InterviewConductor.generate_job_specific_questions()` to include different question categories.

### Changing Evaluation Criteria

Update the evaluation prompt in `InterviewConductor.evaluate_response()` to emphasize different aspects.

### Supporting New Languages

Modify the language codes in the TTS/STT functions in `utils.py`.

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure your Gemini API key is correctly set in `.env`
   - Check if your API key has the necessary permissions

2. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Check your Python version (3.7+ recommended)

3. **Google Cloud Issues**
   - Verify your service account key is correctly configured
   - Ensure the APIs are enabled in your Google Cloud project

### Error Messages

- `Gemini API key not found`: Check your `.env` file
- `Import "dotenv" could not be resolved`: Install dependencies
- `Unable to evaluate response`: Check your internet connection and API limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with API terms of service.

## Future Enhancements

- [ ] Video interview support
- [ ] Multiple language support
- [ ] Integration with HR systems
- [ ] Advanced analytics dashboard
- [ ] Custom question templates
- [ ] Interview scheduling system
- [ ] Candidate comparison tools

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example usage
3. Create an issue in the repository

---

*This AI Interview System is designed to assist in the interview process but should not replace human judgment in hiring decisions.*
