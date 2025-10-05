// interview.js - Custom JS for Interview Page
class InterviewSession {
    constructor() {
        this.userRole = new URLSearchParams(window.location.search).get('domain') || 'Software Engineer';
        this.currentQuestionIndex = 0;
        this.totalQuestions = 5;
        this.isRecording = false;
        this.isInterviewActive = false;
        this.videoStream = null;
        this.emotionInterval = null;
        this.initializeElements();
        this.setupCamera();
        this.bindEvents();
    }
    initializeElements() {
        this.videoFeed = document.getElementById('videoFeed');
        this.startBtn = document.getElementById('startBtn');
        this.recordBtn = document.getElementById('recordBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.currentQuestion = document.getElementById('currentQuestion');
        this.currentEmotion = document.getElementById('currentEmotion');
        this.emotionConfidence = document.getElementById('emotionConfidence');
        this.statusMessages = document.getElementById('statusMessages');
        this.liveFeedback = document.getElementById('liveFeedback');
        this.progressFill = document.getElementById('progressFill');
        this.currentQ = document.getElementById('currentQ');
        this.totalQ = document.getElementById('totalQ');
        this.recordText = document.getElementById('recordText');
        this.aiStatus = document.getElementById('aiStatus');
        this.emotionOverlay = document.getElementById('emotionOverlay');
        this.videoPlaceholder = document.getElementById('videoPlaceholder');
    }
    async setupCamera() {
        try {
            this.videoStream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 },
                audio: true
            });
            this.videoFeed.srcObject = this.videoStream;
            this.videoFeed.style.display = 'block';
            if (this.videoPlaceholder) {
                this.videoPlaceholder.style.display = 'none';
            }
            this.addStatus('Camera initialized successfully', 'success');
        } catch (error) {
            this.addStatus('Camera access denied. Please enable camera permissions.', 'danger');
            console.error('Camera setup error:', error);
        }
    }
    bindEvents() {
        this.startBtn.addEventListener('click', () => this.startInterview());
        this.recordBtn.addEventListener('click', () => this.toggleRecording());
        this.nextBtn.addEventListener('click', () => this.nextQuestion());
    }
    async startInterview() {
        try {
            this.addStatus('Initializing interview...', 'info');
            const response = await fetch('/start_interview', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_role: this.userRole})
            });
            const data = await response.json();
            if (data.success) {
                this.totalQuestions = data.questions.length;
                this.totalQ.textContent = this.totalQuestions;
                this.isInterviewActive = true;
                this.startBtn.disabled = true;
                this.recordBtn.disabled = false;
                this.addStatus('Interview started successfully!', 'success');
                this.startEmotionAnalysis();
                this.askCurrentQuestion();
            }
        } catch (error) {
            this.addStatus('Failed to start interview', 'danger');
        }
    }
    async askCurrentQuestion() {
        try {
            this.addStatus('Loading question...', 'info');
            const response = await fetch(`/ask_question/${this.currentQuestionIndex}`);
            const data = await response.json();
            if (data.success) {
                this.currentQuestion.textContent = data.question;
                this.updateProgress();
                this.addStatus('Question ready. Click record to answer.', 'primary');
            }
        } catch (error) {
            this.addStatus('Failed to load question', 'danger');
        }
    }
    async toggleRecording() {
        if (!this.isRecording) {
            this.startRecording();
        } else {
            this.stopRecording();
        }
    }
    async startRecording() {
        this.isRecording = true;
        this.recordBtn.classList.add('recording');
        this.recordText.textContent = 'Recording... (3s silence to finish)';
        this.nextBtn.disabled = true;
        this.addStatus('Recording your answer...', 'warning');
        try {
            const response = await fetch('/record_answer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: 'default'})
            });
            const data = await response.json();
            if (data.success) {
                this.handleAnswerRecorded(data);
            } else {
                this.addStatus('Failed to record answer', 'danger');
            }
        } catch (error) {
            this.addStatus('Recording failed', 'danger');
        } finally {
            this.stopRecording();
        }
    }
    stopRecording() {
        this.isRecording = false;
        this.recordBtn.classList.remove('recording');
        this.recordText.textContent = 'Click to Answer';
        this.recordBtn.disabled = true;
        this.nextBtn.disabled = false;
    }
    handleAnswerRecorded(data) {
        this.addStatus(`Answer recorded! Score: ${data.score}/100`, 'success');
        this.liveFeedback.innerHTML = `
            <div class="alert alert-info">
                <strong>Answer Score:</strong> ${data.score}/100<br>
                <strong>Feedback:</strong> ${data.feedback}
            </div>
        `;
    }
    async nextQuestion() {
        this.currentQuestionIndex++;
        if (this.currentQuestionIndex >= this.totalQuestions) {
            this.finishInterview();
        } else {
            this.recordBtn.disabled = false;
            this.nextBtn.disabled = true;
            this.askCurrentQuestion();
        }
    }
    async finishInterview() {
        this.isInterviewActive = false;
        this.stopEmotionAnalysis();
        this.addStatus('Generating final report...', 'info');
        try {
            const response = await fetch('/finish_interview', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: 'default'})
            });
            const data = await response.json();
            if (data.success) {
                this.showCompletionModal(data.report);
            }
        } catch (error) {
            this.addStatus('Failed to generate report', 'danger');
        }
    }
    startEmotionAnalysis() {
        this.emotionInterval = setInterval(() => {
            this.captureAndAnalyzeEmotion();
        }, 2000);
    }
    stopEmotionAnalysis() {
        if (this.emotionInterval) {
            clearInterval(this.emotionInterval);
        }
    }
    async captureAndAnalyzeEmotion() {
        if (!this.videoStream) return;
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = this.videoFeed.videoWidth;
            canvas.height = this.videoFeed.videoHeight;
            ctx.drawImage(this.videoFeed, 0, 0);
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            const response = await fetch('/analyze_emotion', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({image: imageData})
            });
            const data = await response.json();
            if (data.success) {
                this.updateEmotionDisplay(data);
            }
        } catch (error) {}
    }
    updateEmotionDisplay(emotionData) {
        if (this.currentEmotion && this.emotionConfidence) {
            this.currentEmotion.textContent = emotionData.emotion || 'Unknown';
            this.emotionConfidence.textContent = Math.round(emotionData.confidence || 0);
            
            // Show emotion overlay
            if (this.emotionOverlay) {
                this.emotionOverlay.style.display = 'block';
            }
            
            const emotionColors = {
                'happy': '#28a745',
                'neutral': '#007bff',
                'sad': '#dc3545',
                'angry': '#dc3545',
                'fear': '#ffc107',
                'surprise': '#6f42c1',
                'disgust': '#fd7e14'
            };
            const color = emotionColors[emotionData.emotion] || '#6c757d';
            this.currentEmotion.style.color = color;
        }
    }
    updateProgress() {
        const progress = ((this.currentQuestionIndex + 1) / this.totalQuestions) * 100;
        const progressBar = document.getElementById('progressFill');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
        this.currentQ.textContent = this.currentQuestionIndex + 1;
    }
    addStatus(message, type) {
        const alertClass = `alert-${type}`;
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'danger' ? 'x-circle' : 
                    type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        const statusHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show">
                <i class="bi bi-${icon}"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        this.statusMessages.insertAdjacentHTML('afterbegin', statusHtml);
        const alerts = this.statusMessages.querySelectorAll('.alert');
        if (alerts.length > 3) {
            alerts[alerts.length - 1].remove();
        }
    }
    showCompletionModal(report) {
        document.getElementById('scoreDisplay').textContent = report.scoring.final_score;
        localStorage.setItem('interviewReport', JSON.stringify(report));
        const modal = new bootstrap.Modal(document.getElementById('completeModal'));
        modal.show();
    }
}
function viewReport() {
    window.location.href = '/report';
}

function startNew() {
    window.location.href = '/';
}

function endInterview() {
    if (confirm('Are you sure you want to end the interview? Your progress will be lost.')) {
        window.location.href = '/';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS if available
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 600,
            easing: 'ease-in-out',
            once: true,
            mirror: false
        });
    }
    
    // Initialize interview session
    new InterviewSession();
});
