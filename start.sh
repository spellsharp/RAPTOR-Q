#!/bin/bash

# VelociRAPTOR Question Paper Generator Startup Script

echo "🚀 Starting VelociRAPTOR Question Paper Generator"
echo "================================================="

# Check if required directories exist
if [ ! -d "app/backend" ]; then
    echo "❌ Backend directory not found!"
    exit 1
fi

if [ ! -d "app/frontend" ]; then
    echo "❌ Frontend directory not found!"
    exit 1
fi

if [ ! -d "VelociRAPTOR" ]; then
    echo "❌ VelociRAPTOR directory not found!"
    echo "Please ensure VelociRAPTOR is properly installed in the project root."
    exit 1
fi

# Check if .env file exists
if [ ! -f "app/backend/.env" ]; then
    echo "⚠️  .env file not found in backend directory"
    echo "Copying example configuration..."
    cp app/backend/config.example app/backend/.env
    echo "Please edit app/backend/.env with your API keys and configuration"
    echo "Press Enter to continue..."
    read
fi

# Function to start backend
start_backend() {
    echo "🔧 Starting Backend Server..."
    cd app/backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip and install build tools first
    echo "Upgrading pip and installing build tools..."
    pip install --upgrade pip setuptools wheel
    
    # Install dependencies in stages to avoid conflicts
    echo "Installing basic dependencies..."
    pip install Flask Flask-CORS python-dotenv reportlab PyPDF2 python-docx requests
    
    echo "Installing AI/ML dependencies..."
    pip install numpy pydantic
    
    echo "Installing LangChain components..."
    pip install langchain langchain-community tiktoken
    
    # Test if the app can start
    echo "Testing Flask application..."
    if python test_app.py --check 2>/dev/null; then
        echo "✅ Flask app test passed"
    else
        echo "⚠️  Flask app test failed, but continuing..."
    fi
    
    # Start Flask server
    echo "Starting Flask server on http://localhost:5000"
    python app.py &
    BACKEND_PID=$!
    
    cd ../..
    echo "✅ Backend server started (PID: $BACKEND_PID)"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend Server..."
    cd app/frontend
    
    # Install dependencies
    echo "Installing frontend dependencies..."
    npm install
    
    # Start React development server
    echo "Starting React development server on http://localhost:3000"
    npm start &
    FRONTEND_PID=$!
    
    cd ../..
    echo "✅ Frontend server started (PID: $FRONTEND_PID)"
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend server stopped"
    fi
    echo "👋 Goodbye!"
    exit 0
}

# Set up trap for cleanup on exit
trap cleanup SIGINT SIGTERM

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed or not in PATH"
    exit 1
fi

# Start the servers
start_backend
start_frontend

echo ""
echo "🎉 VelociRAPTOR Question Paper Generator is now running!"
echo "================================================="
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "🔍 Health Check: http://localhost:5000/api/health"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop the servers
wait 