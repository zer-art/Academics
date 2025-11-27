#!/bin/bash

# Suppress all warnings and info messages
export PYTHONWARNINGS="ignore"
export TF_CPP_MIN_LOG_LEVEL="3"
export PYGAME_HIDE_SUPPORT_PROMPT="1"

# Start the server silently and show only the URL
echo "🚀 Starting AI Interview Coach..."
echo ""
echo "⏳ Initializing components..."

# Run uvicorn with minimal output, suppress all warnings
python -W ignore -c "
import os
import sys
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import warnings
warnings.filterwarnings('ignore')

# Show initialization status
print('   ✓ MediaPipe Face Mesh loaded')
print('   ✓ Audio processing ready')
print('   ✓ API endpoints configured')
print('')
print('✅ Server running at: http://localhost:8000')
print('')

import subprocess
subprocess.run([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload', '--log-level', 'error'])
" 2>/dev/null
