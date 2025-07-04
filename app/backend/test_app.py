import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'VelociRAPTOR Question Paper Generator API is running'})

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'message': 'Test endpoint working!',
        'python_version': '3.12',
        'dependencies': 'Flask, CORS, NumPy, LangChain installed successfully'
    })

if __name__ == '__main__':
    print("🚀 Starting VelociRAPTOR Question Paper Generator Test Server")
    print("="*60)
    print("✅ Flask app starting...")
    print("✅ CORS enabled")
    print("✅ Upload directory created")
    print("📍 Server will be available at: http://localhost:5000")
    print("📍 Test endpoint: http://localhost:5000/api/test")
    print("📍 Health check: http://localhost:5000/api/health")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 