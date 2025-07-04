# 🚀 RAPTOR-Q Windows Setup Guide

## 📋 Prerequisites

### System Requirements
- Windows 10 or Windows 11 (64-bit)
- At least 8GB RAM (16GB recommended)
- 10GB free disk space
- Internet connection for downloading dependencies

### Required Software

#### 1. Python 3.8+
**Option A: Download from Python.org**
1. Go to https://www.python.org/downloads/
2. Download Python 3.8+ (latest version recommended)
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation: Open Command Prompt and run:
   ```cmd
   python --version
   pip --version
   ```

**Option B: Using Windows Package Manager (winget)**
```powershell
winget install Python.Python.3.11
```

#### 2. Node.js 14+
**Option A: Download from nodejs.org**
1. Go to https://nodejs.org/
2. Download the LTS version
3. Run the installer with default settings
4. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

**Option B: Using winget**
```powershell
winget install OpenJS.NodeJS
```

#### 3. Git (Optional but recommended)
**Option A: Download from git-scm.com**
1. Go to https://git-scm.com/download/win
2. Download and install with default settings

**Option B: Using winget**
```powershell
winget install Git.Git
```

## 🛠️ Installation Steps

### Step 1: Download RAPTOR-Q
If you have Git:
```cmd
git clone <repository-url>
cd RAPTOR-Q
```

Or download and extract the ZIP file from the repository.

### Step 2: Install Python Dependencies
Open Command Prompt or PowerShell in the project directory:
```cmd
pip install -r requirements.txt
```

If you encounter permission errors, try:
```cmd
pip install --user -r requirements.txt
```

### Step 3: Install Frontend Dependencies
```cmd
cd app\frontend
npm install
cd ..\..
```

### Step 4: Download and Setup LMStudio
1. Go to https://lmstudio.ai/
2. Download LMStudio for Windows
3. Install and run LMStudio
4. In LMStudio:
   - Go to "Discover" tab
   - Search for "TinyLlama-1.1B-Chat-v1.0"
   - Download the model
   - Go to "Local Server" tab
   - Load the TinyLlama model
   - Start the server on port 1234

### Step 5: Create Environment File
Create a `.env` file in the project root:
```cmd
echo. > .env
```

Open the `.env` file in Notepad and add:
```
# Hugging Face API Key (get from https://huggingface.co/settings/tokens)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# LangSmith API Key (optional, get from https://smith.langchain.com/)
LANGSMITH_API_KEY=your_langsmith_api_key_here

# LMStudio Configuration
LMSTUDIO_BASE_URL=http://localhost:1234
LMSTUDIO_MODEL_NAME=tinyllama-1.1b-chat-v1.0
```

### Step 6: Get API Keys
1. **Hugging Face API Key**:
   - Go to https://huggingface.co/settings/tokens
   - Create a new token
   - Copy and paste it in the `.env` file

2. **LangSmith API Key** (optional):
   - Go to https://smith.langchain.com/
   - Create account and get API key
   - Copy and paste it in the `.env` file

## 🚀 Running the Application

### Method 1: Using Batch Script (Recommended)
Create a `start.bat` file in the project root:
```batch
@echo off
echo Starting RAPTOR-Q...

echo Starting backend...
start "Backend" cmd /k "python app\backend\app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak

echo Starting frontend...
start "Frontend" cmd /k "cd app\frontend && npm start"

echo RAPTOR-Q is starting up!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause
```

Run the batch file by double-clicking it.

### Method 2: Manual Start
Open two Command Prompt windows:

**Window 1 - Backend:**
```cmd
cd app\backend
python app.py
```

**Window 2 - Frontend:**
```cmd
cd app\frontend
npm start
```

## 🌐 Accessing the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 🔧 Troubleshooting

### Common Issues

#### Python not found
- Make sure Python is added to PATH
- Restart Command Prompt after installing Python
- Try using `py` instead of `python`:
  ```cmd
  py --version
  py -m pip install -r requirements.txt
  ```

#### Permission Errors
- Run Command Prompt as Administrator
- Or use `--user` flag with pip:
  ```cmd
  pip install --user -r requirements.txt
  ```

#### Node.js/npm not found
- Restart Command Prompt after installing Node.js
- Check if Node.js is in PATH:
  ```cmd
  where node
  where npm
  ```

#### Port Already in Use
If port 3000 or 5000 is already in use:
- For frontend: The system will automatically suggest port 3001
- For backend: Edit `app.py` to change the port

#### LMStudio Connection Issues
1. Make sure LMStudio is running
2. Check that the server is started on port 1234
3. Verify the model is loaded
4. Test the connection:
   ```cmd
   curl http://localhost:1234/v1/models
   ```

#### Windows Defender/Antivirus
- Add the project folder to Windows Defender exclusions
- Some antivirus software may block the application

### Windows-Specific Notes

#### File Paths
- Use backslashes (`\`) in Windows paths
- Or use forward slashes (`/`) which also work in most cases

#### Environment Variables
Set environment variables in Windows:
```cmd
set HUGGINGFACE_API_KEY=your_key_here
set LANGSMITH_API_KEY=your_key_here
```

Or use PowerShell:
```powershell
$env:HUGGINGFACE_API_KEY="your_key_here"
$env:LANGSMITH_API_KEY="your_key_here"
```

#### Firewall
- Windows Firewall may prompt you to allow Python and Node.js
- Click "Allow" when prompted

## 📚 Additional Resources

### Useful Windows Commands
```cmd
# Check Python version
python --version

# Check Node.js version
node --version

# Check if ports are in use
netstat -ano | findstr :3000
netstat -ano | findstr :5000

# Kill process by port (if needed)
taskkill /F /PID <process_id>
```

### PowerShell Execution Policy
If you encounter PowerShell execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 💡 Tips for Windows Users

1. **Use Windows Terminal** for a better command line experience
2. **Visual Studio Code** is recommended for editing code
3. **Keep Windows updated** for best compatibility
4. **Consider using WSL2** for a Linux-like environment if you prefer
5. **Use Windows Package Manager (winget)** for easier software installation

## 🆘 Getting Help

If you encounter issues:
1. Check the main README.md for general troubleshooting
2. Search for Windows-specific solutions online
3. Create an issue in the project repository
4. Include your Windows version and error messages

---

**Happy generating! 🎉** 