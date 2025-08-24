# Check if running on localhost or development
if [[ "$1" == "--https" ]]; then
    echo "Starting server with HTTPS (for camera access)..."
    # Generate self-signed certificate if it doesn't exist
    if [ ! -f "cert.pem" ] || [ ! -f "key.pem" ]; then
        echo "Generating self-signed certificate..."
        openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=Dev/L=Local/O=DevServer/CN=localhost"
    fi
    uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem --reload
else
    echo "Starting server with HTTP..."
    echo "Note: For camera access, use --https flag or access via https://localhost:8443"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi