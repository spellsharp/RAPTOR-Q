# 🚀 Quick Start Guide

Get VelociRAPTOR Question Paper Generator running in **one command**!

## ⚡ One-Click Setup

```bash
./start.sh
```

That's it! The script will:
- ✅ Check system requirements
- ✅ Install all dependencies
- ✅ Download LMStudio automatically
- ✅ Configure API keys (interactive)
- ✅ Start all servers
- ✅ Test all components

## 📋 Prerequisites

- **Python 3.8+** - [Download](https://python.org)
- **Node.js 14+** - [Download](https://nodejs.org)
- **2GB+ free disk space** - For AI models

## 🔑 API Keys Needed

### Required: Hugging Face API Key
1. Go to https://huggingface.co/settings/tokens
2. Create a token with "Read" permissions
3. Copy the key (starts with `hf_`)

### Optional: LangSmith API Key
1. Go to https://smith.langchain.com/settings
2. Create API key for tracing
3. Copy the key (starts with `lsv2_`)

## 🎯 Usage

1. **Run the setup script:**
   ```bash
   ./start.sh
   ```

2. **Enter your API keys when prompted**

3. **Wait for everything to install and start**

4. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:5000

5. **Upload a document and generate questions!**

## 🛠️ Manual Setup (if needed)

If the automatic setup fails:

```bash
# Backend
cd app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Frontend (new terminal)
cd app/frontend
npm install
npm start
```

## 🐛 Common Issues

**Script fails?**
- Check you have Python 3.8+ and Node.js 14+
- Ensure you have internet connection
- Try running with `bash start.sh` instead

**LMStudio not starting?**
- The script handles the --no-sandbox flag automatically
- You may need to manually load TinyLlama model in LMStudio

**API errors?**
- Check your Hugging Face API key is valid
- Edit `app/backend/.env` to update keys

## 🎉 Success!

Once everything is running:
- Upload PDF/DOC files via the web interface
- Configure question parameters
- Generate professional question papers
- Download as PDF with answer keys

---

**Need help?** Check the full [README.md](README.md) for detailed documentation. 