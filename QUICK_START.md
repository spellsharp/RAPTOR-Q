# 🚀 Quick Start Guide

## Ready to Use! 

Your VelociRAPTOR Question Paper Generator website is now **fully functional**! Here's how to get started:

## ✅ What's Working

- ✅ **Backend**: Flask API with all dependencies resolved
- ✅ **Frontend**: React app with modern UI and animations  
- ✅ **File Upload**: Drag-and-drop for PDF, DOC, DOCX, TXT
- ✅ **Question Generation**: Ready for VelociRAPTOR integration
- ✅ **PDF Export**: Professional question paper generation
- ✅ **Responsive Design**: Beautiful UI that works on all devices

## 🎯 Start the Application

### Option 1: One-Click Start (Recommended)
```bash
./start.sh
```

### Option 2: Manual Start
```bash
# Terminal 1 - Backend
cd app/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install Flask Flask-CORS python-dotenv reportlab PyPDF2 python-docx requests numpy pydantic langchain langchain-community tiktoken
python app.py

# Terminal 2 - Frontend  
cd app/frontend
npm install
npm start
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 🔧 VelociRAPTOR Integration

To fully activate VelociRAPTOR's RAG capabilities:

1. **Set up environment variables**:
   ```bash
   cp app/backend/config.example app/backend/.env
   # Edit .env with your API keys
   ```

2. **Required API Keys**:
   - `LANGSMITH_API_KEY`: For LangSmith tracing
   - `SUMMARIZER_API_KEY`: Hugging Face API key

3. **Start LMStudio**:
   - Install and run LMStudio locally
   - Load `llama-3.2-3b-instruct` model

## 🎨 Features Available Now

### 📤 File Upload
- Drag and drop files or click to select
- Supports PDF, DOC, DOCX, TXT
- Real-time upload progress

### ⚙️ Configuration
- Number of questions (1-50)
- Difficulty levels (Easy, Medium, Hard)
- Question types (Multiple Choice, Short Answer, Essay)

### 📋 Question Generation
- AI-powered question creation
- Automatic answer key generation
- Context-aware from uploaded documents

### 📄 PDF Export
- Professional question paper format
- Separate answer key section
- Ready for printing

## 🔍 Testing the Setup

1. **Test Backend**:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Test Frontend**: 
   - Open http://localhost:3000
   - Navigate through the interface
   - Upload a test document

## 📱 User Interface

- **Home**: Welcome page with features overview
- **Generate**: Upload documents and create question papers
- **View**: Preview example question papers

## 🚨 Troubleshooting

### Common Issues:

1. **Port already in use**:
   ```bash
   lsof -ti:5000 | xargs kill -9  # Kill process on port 5000
   lsof -ti:3000 | xargs kill -9  # Kill process on port 3000
   ```

2. **Python dependencies**:
   - Ensure Python 3.8+ is installed
   - Use the staged installation in start.sh

3. **Node.js dependencies**:
   - Ensure Node.js 14+ is installed
   - Run `npm install` in frontend directory

## 🎊 Next Steps

1. **Upload a document** via the web interface
2. **Configure question settings** (count, difficulty, types)
3. **Generate questions** using the AI pipeline
4. **Download the PDF** with questions and answers

Your website is ready to use! The fallback question generation will work immediately, and once you configure VelociRAPTOR with the proper API keys, you'll get the full AI-powered question generation experience.

## 📞 Need Help?

- Check the main README.md for detailed documentation
- Ensure VelociRAPTOR is properly configured
- Verify all API keys are set correctly

**Happy Question Generation!** 🎓 