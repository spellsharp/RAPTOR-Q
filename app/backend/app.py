import os
import sys
import json
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime

# Add the VelociRAPTOR src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'VelociRAPTOR'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'VelociRAPTOR', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'VelociRAPTOR', 'utils'))

from question_paper_generator import QuestionPaperGenerator

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the question paper generator
question_generator = QuestionPaperGenerator()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'VelociRAPTOR Question Paper Generator API is running'})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload PDF, DOC, DOCX, or TXT files'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': unique_filename,
            'original_filename': filename
        })
    
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    try:
        data = request.json
        file_id = data.get('file_id')
        num_questions = data.get('num_questions', 10)
        difficulty = data.get('difficulty', 'medium')
        question_types = data.get('question_types', ['multiple_choice', 'short_answer'])
        
        if not file_id:
            return jsonify({'error': 'File ID is required'}), 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Generate questions using VelociRAPTOR
        result = question_generator.generate_question_paper(
            file_path=file_path,
            num_questions=num_questions,
            difficulty=difficulty,
            question_types=question_types
        )
        
        return jsonify({
            'message': 'Questions generated successfully',
            'questions': result['questions'],
            'answer_key': result['answer_key'],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_questions': len(result['questions']),
                'difficulty': difficulty,
                'question_types': question_types
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Question generation failed: {str(e)}'}), 500

@app.route('/api/export-pdf', methods=['POST'])
def export_pdf():
    try:
        data = request.json
        questions = data.get('questions', [])
        answer_key = data.get('answer_key', [])
        
        if not questions:
            return jsonify({'error': 'No questions provided'}), 400
        
        # Generate PDF using the question paper generator
        pdf_path = question_generator.generate_pdf(questions, answer_key)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'question_paper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return jsonify({'error': f'PDF export failed: {str(e)}'}), 500

@app.route('/api/file-info/<file_id>', methods=['GET'])
def get_file_info(file_id):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        file_stats = os.stat(file_path)
        return jsonify({
            'file_id': file_id,
            'size': file_stats.st_size,
            'uploaded_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'status': 'ready'
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get file info: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 