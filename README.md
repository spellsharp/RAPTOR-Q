# 🦖 VelociRAPTOR Question Paper Generator

A cutting-edge AI-powered question paper generation system that leverages advanced RAG (Retrieval Augmented Generation) technology to create intelligent, contextually accurate question papers from uploaded documents.

Credits: The application uses Satvik Mishra's VelociRAPTOR implementation. Click [link](https://github.com/satvshr/VelociRAPTOR.git)

![VelociRAPTOR Logo](https://img.shields.io/badge/VelociRAPTOR-Question_Generator-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18+-blue?style=for-the-badge&logo=react)

## 🌟 Features

### 🤖 **AI-Powered Question Generation**
- **Advanced RAG Pipeline**: Custom implementation with RAPTOR, GMM, UMAP, EM, and BIC algorithms
- **Multiple Question Types**: Multiple choice, short answer, and essay questions
- **Difficulty Levels**: Easy, medium, and hard question generation
- **Intelligent Parsing**: Robust LLM response parsing with multiple fallback strategies
- **Context-Aware**: Questions generated from actual document content

### 📄 **Document Processing**
- **Multi-Format Support**: PDF, DOC, DOCX, and TXT files
- **Smart Content Extraction**: Advanced PDF and Word document parsing
- **Large File Handling**: Efficient processing of large documents
- **Content Summarization**: AI-powered document summarization using BART

### 🎨 **Modern User Interface**
- **Responsive Design**: Beautiful, mobile-friendly interface
- **Drag & Drop Upload**: Intuitive file upload experience
- **Real-time Progress**: Live feedback during question generation
- **Professional Export**: High-quality PDF question papers and answer keys

### 🔧 **Enterprise Features**
- **API-First Design**: RESTful API for integration
- **Scalable Architecture**: Modular design for easy scaling
- **Error Handling**: Comprehensive error management and logging
- **Fallback Systems**: Graceful degradation when AI services are unavailable

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Flask Backend │    │  VelociRAPTOR   │
│                 │    │                 │    │                 │
│  - File Upload  │◄──►│  - API Routes   │◄──►│  - RAG Pipeline │
│  - Config UI    │    │  - File Handler │    │  - Question Gen │
│  - Results View │    │  - PDF Export   │    │  - Answer Gen   │
│  - Animations   │    │  - Error Handle │    │  - Embeddings   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        │                        │                        │
   Tailwind CSS            Flask + CORS              LMStudio + HF
```

## 🛠️ Technology Stack

### **Backend**
- **Flask**: Python web framework with CORS support
- **VelociRAPTOR**: Custom RAG implementation with advanced algorithms
- **LangChain**: LLM orchestration and document processing
- **LMStudio**: Local LLM server (TinyLlama-1.1B-Chat)
- **Hugging Face**: Summarization with facebook/bart-large-cnn
- **ReportLab**: Professional PDF generation
- **GPT4All**: Local embeddings for document vectorization
- **PyPDF2**: PDF content extraction
- **python-docx**: Word document processing

### **Frontend**
- **React 18**: Modern JavaScript library with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **React Dropzone**: File upload component
- **Axios**: HTTP client for API communication
- **React Router**: Client-side routing

### **AI/ML Components**
- **RAPTOR**: Recursive Abstractive Processing for Tree-Organized Retrieval
- **GMM**: Gaussian Mixture Models for clustering
- **UMAP**: Uniform Manifold Approximation and Projection
- **BIC**: Bayesian Information Criterion for model selection
- **Custom Embeddings**: GPT4All for local vector generation

## 🚀 Quick Start

### **One-Click Setup**
```bash
git clone https://github.com/spellsharp/RAPTOR-Q.git
cd VelociRAPTOR-Question-Generator
chmod +x start.sh
./start.sh
```

### **Manual Setup**

#### **Prerequisites**
- Python 3.8+
- Node.js 14+
- npm or yarn

#### **Backend Setup**
```bash
cd app/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### **Frontend Setup**
```bash
cd app/frontend
npm install
npm run build
```

#### **Environment Configuration**
```bash
cd app/backend
cp config.example .env
# Edit .env with your API keys:
# LANGSMITH_API_KEY=your_langsmith_key
# SUMMARIZER_API_KEY=your_huggingface_key
# LANGCHAIN_TRACING_V2=true
```

#### **LMStudio Setup**
1. Download LMStudio from [lmstudio.ai](https://lmstudio.ai)
2. Install and start LMStudio
3. Download TinyLlama-1.1B-Chat model
4. Start local server on port 1234

## 🎯 Usage Guide

### **Starting the Application**
```bash
# Option 1: One-click start
./start.sh

# Option 2: Manual start
# Terminal 1 - Backend
cd app/backend && source venv/bin/activate && python app.py

# Terminal 2 - Frontend
cd app/frontend && npm start
```

### **Access Points**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

### **Using the Application**

1. **📤 Upload Document**
   - Drag and drop or click to select file
   - Supported: PDF, DOC, DOCX, TXT
   - Real-time upload progress

2. **⚙️ Configure Generation**
   - Number of questions (1-50)
   - Difficulty level (Easy/Medium/Hard)
   - Question types (Multiple Choice/Short Answer/Essay)

3. **🚀 Generate Questions**
   - Click "Generate Questions"
   - Watch real-time progress
   - AI processes document through RAG pipeline

4. **📋 Review Results**
   - View generated questions
   - Check answer key
   - Edit if needed

5. **📄 Export PDF**
   - Download professional question paper
   - Includes answer key
   - Print-ready format

## 🔌 API Documentation

### **Endpoints**

#### **Health Check**
```http
GET /api/health
Response: {"status": "healthy", "message": "API is running"}
```

#### **File Upload**
```http
POST /api/upload
Content-Type: multipart/form-data
Body: file (PDF/DOC/DOCX/TXT)
Response: {"file_id": "uuid_filename", "message": "File uploaded successfully"}
```

#### **Generate Questions**
```http
POST /api/generate-questions
Content-Type: application/json
Body: {
  "file_id": "uuid_filename",
  "num_questions": 10,
  "difficulty": "medium",
  "question_types": ["multiple_choice", "short_answer"]
}
Response: {
  "questions": [...],
  "answer_key": [...],
  "metadata": {...}
}
```

#### **Export PDF**
```http
POST /api/export-pdf
Content-Type: application/json
Body: {
  "questions": [...],
  "answer_key": [...]
}
Response: PDF file download
```

#### **File Information**
```http
GET /api/file-info/{file_id}
Response: {
  "file_id": "uuid_filename",
  "size": 1024000,
  "uploaded_at": "2025-01-01T12:00:00",
  "status": "ready"
}
```

## ⚙️ Configuration

### **Environment Variables**
```bash
# Required for summarization
SUMMARIZER_API_KEY=hf_your_huggingface_token

# Optional for tracing
LANGSMITH_API_KEY=lsv2_your_langsmith_key
LANGCHAIN_TRACING_V2=true

# File upload path
FILE_PATH=./uploads/
```

### **LMStudio Configuration**
- **Model**: TinyLlama-1.1B-Chat-v1.0
- **Server**: http://localhost:1234
- **Endpoint**: /v1/completions
- **CPU Optimized**: Perfect for local development

### **API Keys Setup**

#### **Hugging Face API Key** (Required)
1. Go to https://huggingface.co/
2. Sign up/login
3. Settings → Access Tokens
4. Create token with "Read" permissions
5. Copy token (starts with `hf_`)

#### **LangSmith API Key** (Optional)
1. Go to https://smith.langchain.com/
2. Sign up/login
3. Settings → API Keys
4. Create new API key
5. Copy token (starts with `lsv2_`)

## 🐛 Troubleshooting

### **Common Issues**

#### **LMStudio Connection Failed**
```bash
# Check if LMStudio is running
curl http://localhost:1234/v1/models

# Start LMStudio with --no-sandbox flag if needed
./LMStudio.AppImage --no-sandbox
```

#### **CUDA Warnings**
```
Failed to load libllamamodel-mainline-cuda.so
```
**Solution**: These are harmless warnings. GPT4All automatically falls back to CPU mode.

#### **Import Errors**
```bash
# Reinstall dependencies
cd app/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

#### **Port Already in Use**
```bash
# Find and kill process using port
sudo lsof -i :5000
sudo kill -9 <PID>
```

### **Performance Optimization**

#### **For Low-Memory Systems**
- Use TinyLlama model (1.1B parameters)
- Reduce `chunk_size` in text splitter
- Limit `num_questions` to ≤ 5

#### **For Better Quality**
- Upgrade to Llama-3.2-3B model
- Increase `top_k_retrieval` parameter
- Use higher quality embeddings

## 📁 Project Structure

```
VelociRAPTOR-Question-Generator/
├── 📄 README.md                    # This file
├── 📄 QUICK_START.md               # Quick setup guide
├── 🚀 start.sh                     # One-click startup script
├── 📁 app/                         # Main application
│   ├── 📁 backend/                 # Flask API server
│   │   ├── 📄 app.py               # Main Flask application
│   │   ├── 📄 question_paper_generator.py  # Core generation logic
│   │   ├── 📄 requirements.txt     # Python dependencies
│   │   ├── 📄 .env                 # Environment variables
│   │   └── 📁 uploads/             # Uploaded files storage
│   └── 📁 frontend/                # React application
│       ├── 📁 src/                 # React source code
│       ├── 📁 public/              # Static assets
│       ├── 📄 package.json         # Node dependencies
│       └── 📄 tailwind.config.js   # Tailwind configuration
├── 📁 VelociRAPTOR/                # RAG implementation
│   ├── 📁 src/                     # Core RAG modules
│   │   ├── 📄 main.py              # Main RAG pipeline
│   │   ├── 📄 raptor.py            # RAPTOR implementation
│   │   ├── 📄 indexing.py          # Document indexing
│   │   ├── 📄 retrieval.py         # Document retrieval
│   │   ├── 📄 generation.py        # Question generation
│   │   └── 📄 routing.py           # Semantic routing
│   └── 📁 utils/                   # Utility modules
│       ├── 📄 lm_studio.py         # LMStudio integration
│       ├── 📄 pdf_summarizer.py    # PDF summarization
│       ├── 📄 gmm.py               # Gaussian Mixture Models
│       └── 📄 umap.py              # UMAP implementation
└── 📁 docs/                        # Documentation
```

## 🔬 Advanced Features

### **RAG Pipeline Components**

#### **Document Processing**
1. **Content Extraction**: Multi-format document parsing
2. **Text Chunking**: Intelligent text splitting with overlap
3. **Vectorization**: GPT4All embeddings for semantic search
4. **Indexing**: ChromaDB for efficient retrieval

#### **Question Generation**
1. **Semantic Routing**: Intelligent document selection
2. **RAPTOR Clustering**: Hierarchical document organization
3. **Context Retrieval**: Relevant passage extraction
4. **LLM Generation**: TinyLlama for question creation

#### **Quality Assurance**
1. **Response Parsing**: Robust LLM output processing
2. **Content Validation**: Question quality checks
3. **Format Standardization**: Consistent output formatting
4. **Fallback Systems**: Graceful error handling

### **Customization Options**

#### **Model Configuration**
```python
# In question_paper_generator.py
self.top_k_indexing = 50      # Documents to index
self.top_k_retrieval = 7      # Documents to retrieve
chunk_size = 300              # Text chunk size
chunk_overlap = 50            # Chunk overlap
```

#### **Question Templates**
```python
# Customize question prompts
question_prompt = f"""
Based on the document content, {base_question}.
Document: {document_content[:2000]}
Format: QUESTION: [question] ANSWER: [answer]
"""
```

## 🤝 Contributing

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/spellsharp/RAPTOR-Q.git
cd VelociRAPTOR-Question-Generator

# Setup development environment
./setup-dev.sh

# Run tests
cd app/backend && python -m pytest
cd app/frontend && npm test
```

### **Code Style**
- **Python**: Follow PEP 8 standards
- **JavaScript**: Use ESLint with React configuration
- **Documentation**: Add docstrings for all functions

### **Submitting Changes**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **RAPTOR Paper**: Original research on recursive abstractive processing
- **LangChain**: Framework for LLM application development
- **LMStudio**: Local LLM inference platform
- **Hugging Face**: Pre-trained models and transformers
- **React Team**: Frontend framework development
- **Tailwind CSS**: Utility-first CSS framework

## 📞 Support

### **Getting Help**
- 📖 **Documentation**: Check this README and QUICK_START.md
- 🐛 **Issues**: Report bugs via GitHub Issues
- 💬 **Discussions**: Join community discussions
- 📧 **Contact**: [your-email@domain.com]

### **System Requirements**
- **Minimum**: 8GB RAM, 4-core CPU
- **Recommended**: 16GB RAM, 8-core CPU
- **Storage**: 5GB free space
- **OS**: Linux, macOS, Windows 10+

---

<div align="center">
  <h3>🚀 Ready to generate amazing question papers? Get started now!</h3>
  
  [![Get Started](https://img.shields.io/badge/Get_Started-Now-green?style=for-the-badge)](./QUICK_START.md)
  [![Documentation](https://img.shields.io/badge/Read_Docs-blue?style=for-the-badge)](./docs/)
  [![Demo](https://img.shields.io/badge/View_Demo-purple?style=for-the-badge)](#)
</div> 