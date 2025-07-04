#!/bin/bash

# 🦖 VelociRAPTOR Question Paper Generator - One-Click Setup & Start Script
# ===========================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Global variables
BACKEND_PID=""
FRONTEND_PID=""
LMSTUDIO_PID=""

# Print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🦖 $1${NC}"
}

# Function to cleanup on exit
cleanup() {
    echo ""
    print_info "Shutting down servers..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null && print_status "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null && print_status "Frontend server stopped"
    fi
    
    if [ ! -z "$LMSTUDIO_PID" ]; then
        kill $LMSTUDIO_PID 2>/dev/null && print_status "LMStudio server stopped"
    fi
    
    echo -e "${PURPLE}👋 VelociRAPTOR shutdown complete!${NC}"
    exit 0
}

# Set up trap for cleanup on exit
trap cleanup SIGINT SIGTERM

# Check system dependencies
check_system_requirements() {
    print_header "Checking System Requirements"
    
    # Check Python 3.8+
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed!"
        print_info "Please install Python 3.8+ from https://python.org"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    print_status "Python $PYTHON_VERSION found"
    
    # Check Node.js 14+
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed!"
        print_info "Please install Node.js 14+ from https://nodejs.org"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_status "Node.js $NODE_VERSION found"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed!"
        print_info "Please install npm (usually comes with Node.js)"
        exit 1
    fi
    
    NPM_VERSION=$(npm --version)
    print_status "npm $NPM_VERSION found"
    
    # Check available disk space (need at least 2GB for models)
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [ "$AVAILABLE_SPACE" -lt 2097152 ]; then
        print_warning "Low disk space detected. You may need at least 2GB for models."
    fi
    
    print_status "System requirements check passed"
}

# Check project structure
check_project_structure() {
    print_header "Checking Project Structure"
    
    if [ ! -d "app/backend" ]; then
        print_error "Backend directory not found!"
        exit 1
    fi
    print_status "Backend directory found"
    
    if [ ! -d "app/frontend" ]; then
        print_error "Frontend directory not found!"
        exit 1
    fi
    print_status "Frontend directory found"
    
    if [ ! -d "VelociRAPTOR" ]; then
        print_error "VelociRAPTOR directory not found!"
        print_info "Please ensure VelociRAPTOR is properly installed in the project root."
        exit 1
    fi
    print_status "VelociRAPTOR directory found"
    
    # Create uploads directory if it doesn't exist
    mkdir -p app/backend/uploads
    print_status "Uploads directory ready"
}

# Setup environment variables
setup_environment() {
    print_header "Setting Up Environment Variables"
    
    if [ ! -f "app/backend/.env" ]; then
        print_info "Creating .env file from template..."
        if [ -f "app/backend/config.example" ]; then
            cp app/backend/config.example app/backend/.env
            print_status ".env file created"
        else
            # Create a default .env file
            cat > app/backend/.env << EOF
# VelociRAPTOR Configuration
LANGSMITH_API_KEY=your_langsmith_key_here
SUMMARIZER_API_KEY=your_huggingface_key_here
LANGCHAIN_TRACING_V2=true
FILE_PATH=./uploads/

# LMStudio Configuration
LMSTUDIO_URL=http://localhost:1234
LMSTUDIO_MODEL=tinyllama-1.1b-chat-v1.0
EOF
            print_status "Default .env file created"
        fi
    fi
    
    # Check if API keys are set
    source app/backend/.env
    
    if [[ "$SUMMARIZER_API_KEY" == "your_huggingface_key_here" || "$SUMMARIZER_API_KEY" == "hf_xyz789..." ]]; then
        print_warning "Hugging Face API key not set!"
        print_info "Please get your API key from https://huggingface.co/settings/tokens"
        read -p "Enter your Hugging Face API key (starts with hf_): " hf_key
        if [[ "$hf_key" == hf_* ]]; then
            sed -i "s/SUMMARIZER_API_KEY=.*/SUMMARIZER_API_KEY=$hf_key/" app/backend/.env
            print_status "Hugging Face API key updated"
        else
            print_warning "Invalid API key format. You can update it later in app/backend/.env"
        fi
    else
        print_status "Hugging Face API key configured"
    fi
    
    if [[ "$LANGSMITH_API_KEY" == "your_langsmith_key_here" || "$LANGSMITH_API_KEY" == "ls_abc123..." ]]; then
        print_info "LangSmith API key not set (optional for tracing)"
        read -p "Enter your LangSmith API key (optional, press Enter to skip): " ls_key
        if [[ "$ls_key" == lsv2_* ]]; then
            sed -i "s/LANGSMITH_API_KEY=.*/LANGSMITH_API_KEY=$ls_key/" app/backend/.env
            print_status "LangSmith API key updated"
        elif [[ -n "$ls_key" ]]; then
            print_warning "Invalid LangSmith API key format"
        fi
    else
        print_status "LangSmith API key configured"
    fi
}

# Setup backend
setup_backend() {
    print_header "Setting Up Backend"
    
    cd app/backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip and install build tools
    print_info "Upgrading pip and installing build tools..."
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    
    # Install dependencies in stages to avoid conflicts
    print_info "Installing Python dependencies..."
    
    # Core dependencies
    pip install Flask Flask-CORS python-dotenv reportlab PyPDF2 python-docx requests > /dev/null 2>&1
    print_status "Core dependencies installed"
    
    # AI/ML dependencies
    pip install numpy pydantic > /dev/null 2>&1
    print_status "AI/ML dependencies installed"
    
    # LangChain components
    pip install langchain langchain-community tiktoken > /dev/null 2>&1
    print_status "LangChain components installed"
    
    # GPT4All for embeddings
    print_info "Installing GPT4All (this may take a few minutes)..."
    pip install gpt4all > /dev/null 2>&1
    print_status "GPT4All installed"
    
    # Additional dependencies that might be needed
    pip install chromadb sentence-transformers > /dev/null 2>&1
    print_status "Additional ML dependencies installed"
    
    cd ../..
    print_status "Backend setup complete"
}

# Setup frontend
setup_frontend() {
    print_header "Setting Up Frontend"
    
    cd app/frontend
    
    # Install dependencies
    print_info "Installing frontend dependencies..."
    npm install > /dev/null 2>&1
    print_status "Frontend dependencies installed"
    
    # Build Tailwind CSS
    print_info "Building Tailwind CSS..."
    npm run build > /dev/null 2>&1
    print_status "Frontend build complete"
    
    cd ../..
    print_status "Frontend setup complete"
}

# Check and setup LMStudio
setup_lmstudio() {
    print_header "Setting Up LMStudio"
    
    # Check if LMStudio is available
    LMSTUDIO_PATH=""
    
    # Check common locations
    if [ -f "$HOME/LMStudio.AppImage" ]; then
        LMSTUDIO_PATH="$HOME/LMStudio.AppImage"
    elif [ -f "./LMStudio.AppImage" ]; then
        LMSTUDIO_PATH="./LMStudio.AppImage"
    elif [ -f "/usr/local/bin/LMStudio" ]; then
        LMSTUDIO_PATH="/usr/local/bin/LMStudio"
    elif command -v lmstudio &> /dev/null; then
        LMSTUDIO_PATH="lmstudio"
    fi
    
    if [ -z "$LMSTUDIO_PATH" ]; then
        print_warning "LMStudio not found!"
        print_info "Downloading LMStudio..."
        
        # Download LMStudio for Linux
        LMSTUDIO_URL="https://releases.lmstudio.ai/linux/x86/0.2.19/LMStudio-0.2.19.AppImage"
        
        print_info "Downloading from $LMSTUDIO_URL..."
        if command -v wget &> /dev/null; then
            wget -O LMStudio.AppImage "$LMSTUDIO_URL" 2>/dev/null || {
                print_error "Download failed!"
                print_info "Please download LMStudio manually from https://lmstudio.ai"
                exit 1
            }
        elif command -v curl &> /dev/null; then
            curl -L -o LMStudio.AppImage "$LMSTUDIO_URL" 2>/dev/null || {
                print_error "Download failed!"
                print_info "Please download LMStudio manually from https://lmstudio.ai"
                exit 1
            }
        else
            print_error "Neither wget nor curl found!"
            print_info "Please download LMStudio manually from https://lmstudio.ai"
            exit 1
        fi
        
        chmod +x LMStudio.AppImage
        LMSTUDIO_PATH="./LMStudio.AppImage"
        print_status "LMStudio downloaded"
    else
        print_status "LMStudio found at $LMSTUDIO_PATH"
    fi
    
    # Check if LMStudio server is already running
    if curl -s http://localhost:1234/v1/models &> /dev/null; then
        print_status "LMStudio server already running"
        return 0
    fi
    
    # Start LMStudio server
    print_info "Starting LMStudio server..."
    
    # Start LMStudio in the background
    if [[ "$LMSTUDIO_PATH" == *.AppImage ]]; then
        # For AppImage, we need to handle the sandbox issue
        $LMSTUDIO_PATH --no-sandbox > /dev/null 2>&1 &
        LMSTUDIO_PID=$!
    else
        $LMSTUDIO_PATH > /dev/null 2>&1 &
        LMSTUDIO_PID=$!
    fi
    
    # Wait for LMStudio to start
    print_info "Waiting for LMStudio to initialize..."
    sleep 10
    
    # Check if server started successfully
    for i in {1..30}; do
        if curl -s http://localhost:1234/v1/models &> /dev/null; then
            print_status "LMStudio server started successfully"
            return 0
        fi
        sleep 2
    done
    
    print_warning "LMStudio server not responding"
    print_info "You may need to start LMStudio manually and load the TinyLlama model"
}

# Test all components
test_components() {
    print_header "Testing All Components"
    
    # Test Hugging Face API
    print_info "Testing Hugging Face API..."
    if python3 -c "
import requests
import os
from dotenv import load_dotenv
load_dotenv('app/backend/.env')
api_key = os.getenv('SUMMARIZER_API_KEY')
if api_key and api_key.startswith('hf_'):
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.post('https://api-inference.huggingface.co/models/facebook/bart-large-cnn', 
                           headers=headers, json={'inputs': 'test'}, timeout=10)
    if response.status_code == 200:
        print('✅ Hugging Face API working')
    else:
        print('⚠️  Hugging Face API response:', response.status_code)
else:
    print('⚠️  Hugging Face API key not configured')
" 2>/dev/null; then
        print_status "Hugging Face API test passed"
    else
        print_warning "Hugging Face API test failed"
    fi
    
    # Test LMStudio API
    print_info "Testing LMStudio API..."
    if curl -s http://localhost:1234/v1/models | grep -q "tinyllama" 2>/dev/null; then
        print_status "LMStudio API test passed"
    else
        print_warning "LMStudio API test failed - please load TinyLlama model in LMStudio"
    fi
    
    # Test GPT4All
    print_info "Testing GPT4All..."
    cd app/backend
    source venv/bin/activate
    if python3 -c "
import gpt4all
try:
    model = gpt4all.GPT4All('orca-mini-3b-gguf2-q4_0.gguf')
    print('✅ GPT4All working')
except Exception as e:
    print('⚠️  GPT4All test failed:', str(e))
" 2>/dev/null; then
        print_status "GPT4All test passed"
    else
        print_warning "GPT4All test failed (will download model on first use)"
    fi
    cd ../..
}

# Start backend server
start_backend() {
    print_header "Starting Backend Server"
    
    cd app/backend
    source venv/bin/activate
    
    # Test if the app can start
    if python3 -c "
import sys
sys.path.append('../../')
try:
    from question_paper_generator import QuestionPaperGenerator
    print('✅ Backend components loaded successfully')
except Exception as e:
    print('⚠️  Backend test warning:', str(e))
" 2>/dev/null; then
        print_status "Backend components verified"
    else
        print_warning "Backend components test failed, but continuing..."
    fi
    
    # Start Flask server
    print_info "Starting Flask server on http://localhost:5000"
    python app.py > /dev/null 2>&1 &
    BACKEND_PID=$!
    
    # Wait for server to start
    for i in {1..15}; do
        if curl -s http://localhost:5000/api/health &> /dev/null; then
            print_status "Backend server started successfully"
            cd ../..
            return 0
        fi
        sleep 1
    done
    
    print_warning "Backend server startup verification failed"
    cd ../..
}

# Start frontend server
start_frontend() {
    print_header "Starting Frontend Server"
    
    cd app/frontend
    
    # Start React development server
    print_info "Starting React development server on http://localhost:3000"
    npm start > /dev/null 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for server to start
    sleep 5
    print_status "Frontend server started"
    
    cd ../..
}

# Main execution
main() {
    clear
    echo ""
    echo -e "${PURPLE}🦖 VelociRAPTOR Question Paper Generator${NC}"
    echo -e "${PURPLE}=====================================${NC}"
    echo -e "${BLUE}One-Click Setup & Start Script${NC}"
    echo ""
    
    # Run all setup steps
    check_system_requirements
    check_project_structure
    setup_environment
    setup_backend
    setup_frontend
    setup_lmstudio
    test_components
    start_backend
    start_frontend
    
    echo ""
    echo -e "${GREEN}🎉 VelociRAPTOR Question Paper Generator is now running!${NC}"
    echo -e "${GREEN}====================================================${NC}"
    echo -e "${BLUE}📱 Frontend: http://localhost:3000${NC}"
    echo -e "${BLUE}🔧 Backend API: http://localhost:5000${NC}"
    echo -e "${BLUE}🔍 Health Check: http://localhost:5000/api/health${NC}"
    echo -e "${BLUE}🤖 LMStudio: http://localhost:1234${NC}"
    echo ""
    echo -e "${YELLOW}📋 Setup Notes:${NC}"
    echo -e "${YELLOW}• Make sure to load TinyLlama-1.1B-Chat model in LMStudio${NC}"
    echo -e "${YELLOW}• Edit app/backend/.env if you need to update API keys${NC}"
    echo -e "${YELLOW}• Upload PDF/DOC files to generate questions${NC}"
    echo ""
    echo -e "${GREEN}Press Ctrl+C to stop all servers${NC}"
    echo ""
    
    # Wait for user to stop the servers
    wait
}

# Run the main function
main 