import os
import sys
import json
import tempfile
import random
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# Add VelociRAPTOR to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'VelociRAPTOR'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'VelociRAPTOR', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'VelociRAPTOR', 'utils'))

from dotenv import load_dotenv
from langchain.schema.runnable import RunnableSequence, RunnableLambda
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings

# Load environment variables
load_dotenv()

try:
    from utils.lm_studio import LMStudioLLM
    from src.translation import translation_template
    from src.routing import semantic_routing_template
    from src.indexing import indexing_template, extract_questions
    from src.raptor import raptor_template
    from src.retrieval import retrieval_template
    from src.generation import generation_template
    from utils.pdf_summarizer import get_summaries
    from utils.find_documents import find_documents
except ImportError as e:
    print(f"Warning: Could not import VelociRAPTOR components: {e}")
    print("Make sure VelociRAPTOR is properly set up and dependencies are installed.")

class QuestionPaperGenerator:
    def __init__(self):
        self.lm_studio_llm = None
        self.embedder = None
        self.text_splitter = None
        self.top_k_indexing = 50
        self.top_k_retrieval = 7
        
        try:
            # Initialize VelociRAPTOR components
            self.lm_studio_llm = LMStudioLLM(path='completions')
            self.embedder = GPT4AllEmbeddings()
            self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=300,
                chunk_overlap=50
            )
            print("VelociRAPTOR components initialized successfully")
        except Exception as e:
            print(f"Error initializing VelociRAPTOR components: {e}")
            print("Using fallback question generation method")
    
    def generate_question_paper(self, file_path, num_questions=10, difficulty='medium', question_types=['multiple_choice', 'short_answer']):
        """
        Generate a question paper from a document using VelociRAPTOR's RAG capabilities
        """
        try:
            # Process the document and extract content
            document_content = self._extract_document_content(file_path)
            
            # Generate questions using VelociRAPTOR
            questions = []
            answer_key = []
            
            for i in range(num_questions):
                question_type = random.choice(question_types)
                question, answer = self._generate_single_question(
                    document_content, 
                    question_type, 
                    difficulty, 
                    i + 1
                )
                questions.append(question)
                answer_key.append(answer)
            
            return {
                'questions': questions,
                'answer_key': answer_key
            }
            
        except Exception as e:
            print(f"Error generating question paper: {e}")
            return self._generate_fallback_questions(file_path, num_questions, difficulty, question_types)
    
    def _extract_document_content(self, file_path):
        """Extract content from various document formats"""
        try:
            if file_path.lower().endswith('.pdf'):
                return self._extract_pdf_content(file_path)
            elif file_path.lower().endswith(('.doc', '.docx')):
                return self._extract_word_content(file_path)
            elif file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
        except Exception as e:
            print(f"Error extracting document content: {e}")
            return "Document content could not be extracted."
    
    def _extract_pdf_content(self, file_path):
        """Extract content from PDF files"""
        try:
            import PyPDF2
            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            return content
        except ImportError:
            print("PyPDF2 not installed, using fallback method")
            return "PDF content extraction requires PyPDF2"
        except Exception as e:
            print(f"Error extracting PDF content: {e}")
            return "PDF content could not be extracted."
    
    def _extract_word_content(self, file_path):
        """Extract content from Word documents"""
        try:
            import docx
            doc = docx.Document(file_path)
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content
        except ImportError:
            print("python-docx not installed, using fallback method")
            return "Word document content extraction requires python-docx"
        except Exception as e:
            print(f"Error extracting Word content: {e}")
            return "Word document content could not be extracted."
    
    def _generate_single_question(self, document_content, question_type, difficulty, question_number):
        """Generate a single question using VelociRAPTOR's RAG capabilities"""
        try:
            if self.lm_studio_llm is None:
                return self._generate_fallback_single_question(document_content, question_type, difficulty, question_number)
            
            # Create a focused question prompt based on the document content
            if question_type == 'multiple_choice':
                base_question = f"Generate a {difficulty} difficulty multiple choice question about the content provided"
            elif question_type == 'short_answer':
                base_question = f"Generate a {difficulty} difficulty short answer question about the content provided"
            elif question_type == 'essay':
                base_question = f"Generate a {difficulty} difficulty essay question about the content provided"
            else:
                base_question = f"Generate a {difficulty} difficulty question about the content provided"
            
            # Use VelociRAPTOR's pipeline to generate question and answer
            question_prompt = f"""
            Based on the following document content, {base_question}.
            
            Document content: {document_content[:2000]}...
            
            Please provide:
            1. The question
            2. The answer (for multiple choice, provide options A, B, C, D and indicate the correct answer)
            
            Format your response as:
            QUESTION: [Your question here]
            ANSWER: [Your answer here]
            """

            # question_prompt = f"""
            # Hi. How are you?
            # """
            
            # Use the generation template to get the response
            response = self.lm_studio_llm.invoke(question_prompt)
            
            # Parse the response to extract question and answer
            question, answer = self._parse_llm_response(response, question_type, question_number)
            
            return question, answer
            
        except Exception as e:
            print(f"Error generating single question: {e}")
            return self._generate_fallback_single_question(document_content, question_type, difficulty, question_number)
    
    def _parse_llm_response(self, response, question_type, question_number):
        """Parse the LLM response to extract question and answer with robust parsing"""
        
        try:
            response = response.strip()
            question_text = ""
            answer_text = ""
            
            # Multiple patterns to match different LLM response formats
            question_patterns = [
                r'QUESTION:\s*(.+?)(?=ANSWER:|$)',
                r'Question:\s*(.+?)(?=Answer:|$)', 
                r'Q:\s*(.+?)(?=A:|$)',
                r'Q\d*[.)]\s*(.+?)(?=A\d*[.)]|Answer|$)',
                r'^\d+[.)]\s*(.+?)(?=Answer:|A:|$)',
                r'Question\s*\d*[:]?\s*(.+?)(?=Answer|A:|$)'
            ]
            
            answer_patterns = [
                r'ANSWER:\s*(.+?)$',
                r'Answer:\s*(.+?)$',
                r'A:\s*(.+?)$',
                r'A\d*[.)]\s*(.+?)$',
                r'(?:Correct answer|Answer):\s*(.+?)$'
            ]
            
            # Try to extract question using patterns
            for pattern in question_patterns:
                match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
                if match:
                    question_text = match.group(1).strip()
                    # Clean up the question text
                    question_text = re.sub(r'\n+', ' ', question_text)
                    question_text = re.sub(r'\s+', ' ', question_text)
                    break
            
            # Try to extract answer using patterns
            for pattern in answer_patterns:
                match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
                if match:
                    answer_text = match.group(1).strip()
                    # Clean up the answer text
                    answer_text = re.sub(r'\n+', ' ', answer_text)
                    answer_text = re.sub(r'\s+', ' ', answer_text)
                    break
            
            # Fallback: try to split on common separators
            if not question_text or not answer_text:
                parts = re.split(r'(?:answer:|a:|\nanswer|\na:)', response, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    if not question_text:
                        question_text = parts[0].strip()
                        # Remove common question prefixes
                        question_text = re.sub(r'^(?:question:|q:|\d+[.)]\s*)', '', question_text, flags=re.IGNORECASE)
                    if not answer_text:
                        answer_text = parts[1].strip()
            
            # Additional fallback: extract first sentence as question if no clear structure
            if not question_text:
                sentences = re.split(r'[.!?]+', response)
                if sentences:
                    question_text = sentences[0].strip()
                    # Ensure it ends with a question mark if it's a question
                    if question_type in ['multiple_choice', 'short_answer'] and not question_text.endswith('?'):
                        question_text += '?'
            
            # Final fallback for question
            if not question_text or len(question_text) < 10:
                question_text = f"Based on the document content, please explain the main concepts discussed?"
            
            # Final fallback for answer
            if not answer_text:
                # Try to extract remaining text after question
                remaining_text = response.replace(question_text, '').strip()
                if remaining_text and len(remaining_text) > 10:
                    answer_text = remaining_text
                else:
                    answer_text = "Please refer to the document content for the answer."
            
            # Validate and clean question text
            question_text = self._clean_question_text(question_text, question_type)
            
            # Validate and clean answer text
            answer_text = self._clean_answer_text(answer_text, question_type)
            
            question = {
                'id': question_number,
                'type': question_type,
                'text': f"Question {question_number}: {question_text}",
                'points': self._get_points_by_difficulty_and_type(question_type)
            }
            
            if question_type == 'multiple_choice':
                # Try to extract options from the response
                options = self._extract_multiple_choice_options(response)
                question['options'] = options
                
                # If we found options in the response, try to extract the correct answer
                if len(options) > 0 and any(opt.startswith(('A)', 'B)', 'C)', 'D)')) for opt in options):
                    correct_answer = self._extract_correct_answer(response, options)
                    if correct_answer:
                        answer_text = correct_answer
            
            answer = {
                'id': question_number,
                'type': question_type,
                'answer': answer_text
            }
            
            return question, answer
            
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Raw response: {response[:200]}...")
            return self._generate_fallback_single_question("", question_type, "medium", question_number)
    
    def _clean_question_text(self, text, question_type):
        """Clean and validate question text"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove leading question numbers/markers if already present
        text = re.sub(r'^(?:question\s*\d*[.:]?\s*|q\d*[.:]?\s*|\d+[.)]?\s*)', '', text, flags=re.IGNORECASE)
        
        # Ensure question ends appropriately
        if question_type in ['multiple_choice', 'short_answer']:
            if not text.endswith('?'):
                text += '?'
        elif question_type == 'essay':
            if not text.endswith(('.', '?', ':')):
                text += '.'
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def _clean_answer_text(self, text, question_type):
        """Clean and validate answer text"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common answer prefixes
        text = re.sub(r'^(?:answer:|a:|the answer is:?|correct answer:?)\s*', '', text, flags=re.IGNORECASE)
        
        # Capitalize first letter if it's not already capitalized
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text
    
    def _extract_correct_answer(self, response, options):
        """Extract the correct answer for multiple choice questions"""
        
        # Look for patterns indicating correct answer
        correct_patterns = [
            r'(?:correct answer|answer):\s*([A-D])\)',
            r'(?:correct|answer):\s*([A-D])',
            r'(?:the answer is|answer is):\s*([A-D])\)',
            r'(?:the answer is|answer is):\s*([A-D])',
            r'\b([A-D])\s*(?:is correct|is the answer)',
        ]
        
        for pattern in correct_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                letter = match.group(1).upper()
                # Find the corresponding option
                for option in options:
                    if option.startswith(f"{letter})"):
                        return option
        
        return None
    
    def _extract_multiple_choice_options(self, response):
        """Extract multiple choice options from LLM response with robust parsing"""
        
        try:
            options = []
            
            # Multiple patterns to match different option formats
            option_patterns = [
                r'([A-D])\)\s*(.+?)(?=\n[A-D]\)|$)',  # A) option text
                r'([A-D])\.\s*(.+?)(?=\n[A-D]\.|$)',  # A. option text
                r'([A-D]):\s*(.+?)(?=\n[A-D]:|$)',    # A: option text
                r'([A-D])\s*-\s*(.+?)(?=\n[A-D]\s*-|$)',  # A - option text
                r'\(([A-D])\)\s*(.+?)(?=\n\([A-D]\)|$)',  # (A) option text
            ]
            
            # Try each pattern
            for pattern in option_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE | re.MULTILINE)
                if matches and len(matches) >= 2:  # Need at least 2 options to be valid
                    options = []
                    for letter, text in matches:
                        if letter.upper() in ['A', 'B', 'C', 'D']:
                            # Clean up the option text
                            text = re.sub(r'\s+', ' ', text.strip())
                            # Remove trailing punctuation except periods that are part of content
                            text = re.sub(r'[,;]\s*$', '', text)
                            if text:  # Only add non-empty options
                                options.append(f"{letter.upper()}) {text}")
                    
                    if len(options) >= 2:  # Valid set of options found
                        break
            
            # Fallback: try to find options in a more flexible way
            if len(options) < 2:
                lines = response.split('\n')
                option_lines = []
                
                for line in lines:
                    line = line.strip()
                    # Look for lines that might be options
                    if re.match(r'^[A-D][.):\-]\s*\w+', line, re.IGNORECASE):
                        option_lines.append(line)
                    elif re.match(r'^\([A-D]\)\s*\w+', line, re.IGNORECASE):
                        option_lines.append(line)
                    elif re.match(r'^\d+[.)]\s*\w+', line) and len(option_lines) < 4:
                        # Convert numbered options to lettered ones
                        num = line[0]
                        if num in '1234':
                            letter = ['A', 'B', 'C', 'D'][int(num) - 1]
                            text = re.sub(r'^\d+[.)]\s*', '', line)
                            option_lines.append(f"{letter}) {text}")
                
                if len(option_lines) >= 2:
                    options = option_lines[:4]  # Take at most 4 options
            
            # Ensure we have exactly 4 options with proper formatting
            if len(options) < 4:
                # Fill in missing options or create defaults
                expected_letters = ['A', 'B', 'C', 'D']
                existing_letters = []
                
                # Extract existing letters
                for opt in options:
                    match = re.match(r'^([A-D])', opt)
                    if match:
                        existing_letters.append(match.group(1))
                
                # Add missing options
                for letter in expected_letters:
                    if letter not in existing_letters:
                        if len(options) < 4:
                            options.append(f"{letter}) Option {letter}")
            
            # Clean up and standardize format
            standardized_options = []
            for i, option in enumerate(options[:4]):  # Ensure max 4 options
                letter = ['A', 'B', 'C', 'D'][i]
                # Extract just the text part
                text_match = re.search(r'^[A-D][.):\-]\s*(.+)', option, re.IGNORECASE)
                if text_match:
                    text = text_match.group(1).strip()
                else:
                    text = f"Option {letter}"
                
                standardized_options.append(f"{letter}) {text}")
            
            # Final fallback if still no valid options
            if len(standardized_options) < 4:
                standardized_options = [
                    "A) Option A",
                    "B) Option B", 
                    "C) Option C",
                    "D) Option D"
                ]
            
            return standardized_options[:4]  # Return exactly 4 options
            
        except Exception as e:
            print(f"Error extracting multiple choice options: {e}")
            return ["A) Option A", "B) Option B", "C) Option C", "D) Option D"]
    
    def _get_points_by_difficulty_and_type(self, question_type):
        """Get points based on question type"""
        if question_type == 'multiple_choice':
            return 2
        elif question_type == 'short_answer':
            return 5
        elif question_type == 'essay':
            return 10
        else:
            return 3
    
    def _generate_fallback_questions(self, file_path, num_questions, difficulty, question_types):
        """Generate fallback questions when VelociRAPTOR is not available"""
        print("Using fallback question generation method")
        
        questions = []
        answer_key = []
        
        fallback_questions = [
            {
                'type': 'multiple_choice',
                'text': 'What is the main topic discussed in the document?',
                'options': ['A) Topic A', 'B) Topic B', 'C) Topic C', 'D) Topic D'],
                'answer': 'A) Topic A'
            },
            {
                'type': 'short_answer',
                'text': 'Explain the key concepts presented in the document.',
                'answer': 'The document presents several key concepts including...'
            },
            {
                'type': 'essay',
                'text': 'Analyze the main arguments presented in the document.',
                'answer': 'The main arguments can be analyzed as follows...'
            }
        ]
        
        for i in range(num_questions):
            question_type = random.choice(question_types)
            base_question = random.choice([q for q in fallback_questions if q['type'] == question_type])
            
            question = {
                'id': i + 1,
                'type': question_type,
                'text': f"Question {i + 1}: {base_question['text']}",
                'points': self._get_points_by_difficulty_and_type(question_type)
            }
            
            if question_type == 'multiple_choice':
                question['options'] = base_question['options']
            
            answer = {
                'id': i + 1,
                'type': question_type,
                'answer': base_question['answer']
            }
            
            questions.append(question)
            answer_key.append(answer)
        
        return {
            'questions': questions,
            'answer_key': answer_key
        }
    
    def _generate_fallback_single_question(self, document_content, question_type, difficulty, question_number):
        """Generate a fallback single question"""
        question = {
            'id': question_number,
            'type': question_type,
            'text': f"Question {question_number}: Based on the document, explain the main concepts discussed.",
            'points': self._get_points_by_difficulty_and_type(question_type)
        }
        
        if question_type == 'multiple_choice':
            question['options'] = ['A) Option A', 'B) Option B', 'C) Option C', 'D) Option D']
        
        answer = {
            'id': question_number,
            'type': question_type,
            'answer': 'Answer based on document content'
        }
        
        return question, answer
    
    def generate_pdf(self, questions, answer_key):
        """Generate a PDF file with questions and answer key"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            
            # Create PDF document
            doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                alignment=TA_CENTER,
                spaceAfter=30
            )
            story.append(Paragraph("Question Paper", title_style))
            story.append(Spacer(1, 12))
            
            # Instructions
            instructions = """
            Instructions:
            1. Read all questions carefully before answering
            2. Write your answers clearly and legibly
            3. Manage your time effectively
            4. Show your work where applicable
            """
            story.append(Paragraph(instructions, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Questions
            for i, question in enumerate(questions):
                question_text = f"Q{question['id']}. {question['text']} ({question['points']} points)"
                story.append(Paragraph(question_text, styles['Normal']))
                
                if question['type'] == 'multiple_choice' and 'options' in question:
                    for option in question['options']:
                        story.append(Paragraph(f"    {option}", styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            # Page break before answer key
            story.append(PageBreak())
            
            # Answer Key
            answer_title_style = ParagraphStyle(
                'AnswerTitle',
                parent=styles['Heading1'],
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            story.append(Paragraph("Answer Key", answer_title_style))
            story.append(Spacer(1, 12))
            
            for answer in answer_key:
                answer_text = f"A{answer['id']}. {answer['answer']}"
                story.append(Paragraph(answer_text, styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise Exception(f"PDF generation failed: {str(e)}") 