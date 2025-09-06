#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AI Interview Coach Setup & Launch${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running on localhost or development
if [[ "$1" == "--https" ]]; then
    echo -e "${YELLOW}🔒 Starting server with HTTPS (for camera access)...${NC}"
    
    # Generate self-signed certificate if it doesn't exist
    if [ ! -f "cert.pem" ] || [ ! -f "key.pem" ]; then
        echo -e "${YELLOW}🔐 Generating self-signed certificate...${NC}"
        openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
            -subj "/C=US/ST=Dev/L=Local/O=DevServer/CN=localhost"
    fi
    
    # Install dependencies if needed
    if [[ "$2" == "--install" ]]; then
        install_system_deps
        echo -e "${YELLOW}📚 Installing Python libraries...${NC}"
        pip install -r requirements.txt
    fi
    
    echo -e "${GREEN}🌐 Starting HTTPS server on port 8443...${NC}"
    uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem --reload

elif [[ "$1" == "--install" ]]; then
    echo -e "${YELLOW}🔧 Installing dependencies...${NC}"
    install_system_deps
    echo -e "${YELLOW}📚 Installing Python libraries...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed! Run ./run.sh to start the server${NC}"

else
    echo -e "${YELLOW}📚 Installing Python libraries...${NC}"
    pip install -r requirements.txt
    
    echo -e "${GREEN}🌐 Starting HTTP server on port 8000...${NC}"
    echo -e "${YELLOW}💡 Note: For camera access, use --https flag or access via https://localhost:8443${NC}"
    echo -e "${YELLOW}💡 For full installation (including system deps): ./run.sh --install${NC}"
    
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi