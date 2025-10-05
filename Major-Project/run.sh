#!/bin/bash

# AI Interview Coach - Assembly AI Edition Deployment Script
# This script runs the application with Assembly AI for speech recognition

echo "🚀 AI Interview Coach - Assembly AI Edition"
echo "==========================================="

# Set the project root directory
PROJECT_ROOT="/home/pawan/dev/MAJOR-PROJECT"
APP_DIR="$PROJECT_ROOT/app"

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "❌ Error: Please run this script from the MAJOR-PROJECT directory"
    echo "Current directory: $(pwd)"
    echo "Expected directory: $PROJECT_ROOT"
    exit 1
fi

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    # Export environment variables from .env file
    export $(cat $PROJECT_ROOT/.env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env"
else
    echo "⚠️ Warning: .env file not found at $PROJECT_ROOT/.env"
fi

# Check Assembly AI API key
if [ -z "$ASSEMBLY_AI" ]; then
    echo "❌ Error: ASSEMBLY_AI environment variable not set"
    echo "Please add your Assembly AI API key to .env file:"
    echo "ASSEMBLY_AI=your_api_key_here"
    exit 1
else
    echo "✅ Assembly AI API key found"
fi

# Check Gemini API key
if [ -z "$GEMINI" ]; then
    echo "❌ Error: GEMINI environment variable not set"
    echo "Please add your Google Gemini API key to .env file:"
    echo "GEMINI=your_api_key_here"
    exit 1
else
    echo "✅ Gemini API key found"
fi

# Set environment variables for better performance and proper imports
export PYTHONPATH="$APP_DIR:$PROJECT_ROOT:$PYTHONPATH"
export DEEPFACE_LOG_LEVEL="ERROR"
export TF_CPP_MIN_LOG_LEVEL="2"
export PYTHONUNBUFFERED=1

echo "📁 Working directory: $PROJECT_ROOT"
echo "📦 Python path: $PYTHONPATH"

# Navigate to the app directory
cd "$APP_DIR"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi


# Install performance dependencies first
echo "📦 Installing Assembly AI dependencies..."
pip install aiohttp aiofiles orjson cachetools 2>/dev/null || echo "⚠️ Some performance packages may already be installed"

# Install all dependencies
echo "📦 Installing all dependencies..."
pip install -r ../requirements.txt

# Create necessary directories if they don't exist
echo "📁 Creating necessary directories..."
mkdir -p static
mkdir -p templates

# Verify critical files exist
echo "🔍 Verifying application files..."
CRITICAL_FILES=(
    "main.py"
    "src/deepface.py" 
    "src/utils.py"
    "src/llm.py"
    "src/speech_recognition.py"
    "performance_config.py"
    "performance_middleware.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - MISSING!"
        exit 1
    fi
done

# Performance optimizations info
echo ""
echo "⚡ Performance Optimizations Enabled:"
echo "  ✅ Assembly AI speech recognition (cloud-based)"
echo "  ✅ Async processing with asyncio.to_thread()"
echo "  ✅ In-memory TTL caching for transcriptions"
echo "  ✅ orjson for faster JSON serialization"  
echo "  ✅ Model preloading on startup"
echo "  ✅ Performance monitoring middleware"
echo "  ✅ Fixed import paths"

echo ""
echo "🎯 Speech Recognition Services:"
echo "  🎤 Primary: Assembly AI (API-based)"
echo "  🧠 LLM: Google Gemini"
echo "  👁️ Computer Vision: DeepFace"

echo ""
echo "🌐 Starting AI Interview Coach..."

# Run with optimized settings
if [ "$1" = "production" ]; then
    echo "🏭 Running in production mode..."
    
    # Check if gunicorn is available
    if command -v gunicorn &> /dev/null; then
        gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 120
    else
        echo "⚠️ Gunicorn not found, installing..."
        pip install gunicorn
        gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 120
    fi
else
    echo "🔧 Running in development mode..."
    echo "🌐 Application will be available at: http://localhost:8000"
    echo "🔊 Speech Recognition: Assembly AI"
    echo "📊 Performance monitoring enabled"
    echo ""
    
    # Start the application
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi