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

# Try to import the simple evaluation system (fallback if full system fails)
try:
    from evaluation_system import QuestionAnswerEvaluator, evaluate_raptor_q_output
    FULL_EVALUATION_AVAILABLE = True
except ImportError as e:
    print(f"Full evaluation system not available: {e}")
    try:
        from evaluation_system_simple import SimpleQuestionAnswerEvaluator, simple_evaluate_raptor_q
        FULL_EVALUATION_AVAILABLE = False
        print("Using simple evaluation system instead")
    except ImportError as e2:
        print(f"Simple evaluation system also not available: {e2}")
        FULL_EVALUATION_AVAILABLE = False

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

@app.route('/api/evaluate-questions', methods=['POST'])
def evaluate_questions():
    """
    Evaluate generated questions against reference data or built-in examples.
    
    Expected JSON payload:
    {
        "generated_questions": [
            {
                "question": "What was the French and Indian War?",
                "answer": "A conflict between Britain and France",
                "type": "short_answer"
            }
        ],
        "reference_data": {...},  // Optional SQuAD2.0 format data
        "evaluation_type": "french_indian_war"  // Optional: specify evaluation type
    }
    """
    try:
        data = request.json
        generated_questions = data.get('generated_questions', [])
        reference_data = data.get('reference_data')
        evaluation_type = data.get('evaluation_type', 'auto')
        
        if not generated_questions:
            return jsonify({'error': 'No generated questions provided'}), 400
        
        # Initialize evaluator (use simple version if full version not available)
        if FULL_EVALUATION_AVAILABLE:
            evaluator = QuestionAnswerEvaluator()
            
            # Perform evaluation
            if reference_data:
                results = evaluator.evaluate_against_squad_data(generated_questions, reference_data)
            elif evaluation_type == 'french_indian_war':
                results = evaluator.evaluate_french_indian_war_example(generated_questions)
            else:
                # Default to French-Indian War example
                results = evaluator.evaluate_french_indian_war_example(generated_questions)
            
            # Generate evaluation report
            report = evaluator.generate_evaluation_report(results)
        else:
            # Fallback to simple evaluation
            if 'SimpleQuestionAnswerEvaluator' in globals():
                evaluator = SimpleQuestionAnswerEvaluator(use_embeddings=False)
                results = evaluator.evaluate_french_indian_war_example(generated_questions)
                report = evaluator.generate_evaluation_report(results)
            else:
                # Basic fallback evaluation
                results = simple_evaluate_raptor_q(generated_questions) if 'simple_evaluate_raptor_q' in globals() else {}
                report = "Simple evaluation completed. Install full dependencies for detailed reports."
        
        return jsonify({
            'message': 'Evaluation completed successfully',
            'results': results,
            'report': report,
            'metadata': {
                'total_questions': len(generated_questions),
                'evaluation_type': evaluation_type,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Evaluation failed: {str(e)}'}), 500

@app.route('/api/evaluation-examples', methods=['GET'])
def get_evaluation_examples():
    """
    Get sample evaluation data for testing.
    
    Returns examples of:
    - French-Indian War reference questions
    - SQuAD2.0 format data structure
    - Sample generated questions for testing
    """
    try:
        examples = {
            'french_indian_war_references': [
                {
                    'question': 'What was the French and Indian War?',
                    'answer': 'The French and Indian War was a conflict between Britain and France in North America from 1754 to 1763.',
                    'type': 'short_answer'
                },
                {
                    'question': 'When did the French and Indian War take place?',
                    'answer': '1754 to 1763',
                    'type': 'short_answer'
                },
                {
                    'question': 'Which European powers were involved in the French and Indian War?',
                    'answer': 'Britain and France',
                    'type': 'short_answer'
                },
                {
                    'question': 'What was the outcome of the French and Indian War?',
                    'answer': 'Britain gained control of most French territories in North America.',
                    'type': 'short_answer'
                }
            ],
            'sample_paragraph': {
                'title': 'French and Indian War',
                'context': 'The French and Indian War (1754–1763) was a conflict between Great Britain and France in North America. The war was fought primarily along the frontiers between New France and the British colonies, from the Province of Virginia in the south to Newfoundland in the north. The conflict arose from disputes over land in the Ohio River valley. British colonists wanted to settle in the region, while the French wanted to maintain control over their lucrative fur trade. The war ended with the Treaty of Paris in 1763, which resulted in France ceding most of its North American territories to Britain.',
                'qas': [
                    {
                        'question': 'What time period did the French and Indian War cover?',
                        'answers': [{'text': '1754–1763', 'answer_start': 29}],
                        'is_impossible': False
                    },
                    {
                        'question': 'What was the main cause of the French and Indian War?',
                        'answers': [{'text': 'disputes over land in the Ohio River valley', 'answer_start': 391}],
                        'is_impossible': False
                    },
                    {
                        'question': 'How did the French and Indian War end?',
                        'answers': [{'text': 'Treaty of Paris in 1763', 'answer_start': 632}],
                        'is_impossible': False
                    }
                ]
            },
            'sample_generated_questions': [
                {
                    'question': 'What was the duration of the French and Indian War?',
                    'answer': 'The French and Indian War lasted from 1754 to 1763.',
                    'type': 'short_answer'
                },
                {
                    'question': 'Which nations were the primary combatants in the French and Indian War?',
                    'answer': 'Great Britain and France',
                    'type': 'short_answer'
                },
                {
                    'question': 'What geographical area was the focus of the French and Indian War?',
                    'answer': 'North America, particularly the Ohio River valley',
                    'type': 'short_answer'
                }
            ]
        }
        
        return jsonify({
            'message': 'Evaluation examples retrieved successfully',
            'examples': examples,
            'usage_instructions': {
                'evaluation_endpoint': '/api/evaluate-questions',
                'required_fields': ['generated_questions'],
                'optional_fields': ['reference_data', 'evaluation_type'],
                'supported_evaluation_types': ['french_indian_war', 'auto']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve examples: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 