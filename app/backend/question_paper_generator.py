import os
import sys
import json
import tempfile
import random
import re
import traceback
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
            previous_questions = []  # Track questions to avoid repetition
            
            for i in range(num_questions):
                question_type = random.choice(question_types)
                question, answer = self._generate_single_question(
                    document_content, 
                    question_type, 
                    difficulty, 
                    i + 1,
                    previous_questions  # Pass previous questions
                )
                questions.append(question)
                answer_key.append(answer)
                
                # Add this question to the list of previous questions
                previous_questions.append(question['text'])
            
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
    
    def _preprocess_document_content(self, document_content):
        """Preprocess document content for better question generation"""
        
        # Split into chunks for better processing
        if len(document_content) > 3000:
            chunks = self.text_splitter.split_text(document_content)
            # Use the most relevant chunks or summarize
            document_content = ' '.join(chunks[:2])  # Take first 2 chunks
        
        # Clean up formatting
        document_content = re.sub(r'\s+', ' ', document_content)
        document_content = re.sub(r'\n+', '\n', document_content)
        
        return document_content.strip()
    
    def _get_content_chunks(self, document_content, max_chunk_size=600):
        """Split document content into chunks for variety in question generation"""
        if len(document_content) <= max_chunk_size:
            return [document_content]
        
        # Split by sentences first, then by paragraphs if needed
        sentences = re.split(r'[.!?]+', document_content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed the limit, start a new chunk
            if len(current_chunk) + len(sentence) + 1 > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += (" " + sentence if current_chunk else sentence)
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If we still don't have enough chunks, create overlapping chunks
        if len(chunks) < 3:
            # Create overlapping chunks of max_chunk_size
            chunks = []
            for i in range(0, len(document_content), max_chunk_size // 2):
                chunk = document_content[i:i + max_chunk_size]
                if chunk.strip():
                    chunks.append(chunk.strip())
                if len(chunks) >= 5:  # Limit to avoid too many chunks
                    break
        
        return chunks if chunks else [document_content[:max_chunk_size]]
    
    def _generate_single_question(self, document_content, question_type, difficulty, question_number, previous_questions=None):
        """Generate a single question using a much simpler approach"""
        try:
            if self.lm_studio_llm is None:
                return self._generate_fallback_single_question(document_content, question_type, difficulty, question_number)
            
            # Create a very simple, direct prompt
            prompt = self._create_simple_prompt(document_content, question_type, difficulty, previous_questions)
            
            # Get response from LLM
            response = self.lm_studio_llm.invoke(prompt)
            
            # Debug: print raw response (can be disabled in production)
            self._debug_llm_response(response, question_type, question_number)
            
            # Use simple parsing
            question, answer = self._simple_parse_response(response, question_type, question_number)
            
            return question, answer
            
        except Exception as e:
            print(f"Error generating single question: {e}")
            return self._generate_fallback_single_question(document_content, question_type, difficulty, question_number)
    
    def _create_simple_prompt(self, document_content, question_type, difficulty, previous_questions=None):
        """Create a very simple, direct prompt"""
        
        # Use different chunks of content for variety
        content_chunks = self._get_content_chunks(document_content, 600)
        
        # Select a chunk based on how many questions we've already asked
        chunk_index = len(previous_questions or []) % len(content_chunks)
        selected_content = content_chunks[chunk_index]
        
        print(f"CHUNK DEBUG: Using chunk {chunk_index + 1}/{len(content_chunks)} (length: {len(selected_content)})")
        if previous_questions:
            print(f"AVOIDING {len(previous_questions)} previous questions")
        
        # Build the previous questions section
        previous_questions_text = ""
        if previous_questions and len(previous_questions) > 0:
            previous_questions_text = "\nDO NOT REPEAT THESE QUESTIONS:\n"
            for i, prev_q in enumerate(previous_questions, 1):
                previous_questions_text += f"{i}. {prev_q}\n"
            previous_questions_text += "\n"
        
        if question_type == 'multiple_choice':
            return f"""TEXT: {selected_content}{previous_questions_text}
TASK: Write EXACTLY 1 NEW multiple choice question. Use ONLY this format:

Q: [question]
A) [option]
B) [option] 
C) [option]
D) [option]
ANSWER: A

NO other text allowed."""

        elif question_type == 'short_answer':
            return f"""TEXT: {selected_content}{previous_questions_text}
TASK: Write EXACTLY 1 NEW short answer question. Use ONLY this format:

Q: [question]
A: [answer]

NO other text allowed."""

        else:  # essay
            return f"""TEXT: {selected_content}{previous_questions_text}
TASK: Write EXACTLY 1 NEW essay question. Use ONLY this format:

Q: [question]
A: [answer]

NO other text allowed."""
    
    def _simple_parse_response(self, response, question_type, question_number):
        """Super simple parsing - just grab what we can"""
        
        try:
            lines = response.strip().split('\n')
            question_text = ""
            answer_text = ""
            options = []
            
            # Debug: Show what we're trying to parse
            print(f"PARSING DEBUG: Found {len(lines)} lines")
            
            # Find question (line starting with Q:)
            for line in lines:
                line = line.strip()
                if line.startswith('Q:'):
                    question_text = line[2:].strip()
                    print(f"PARSING DEBUG: Found question: '{question_text}'")
                    break
            
            # Find answer (line starting with A: or ANSWER:)
            for line in lines:
                line = line.strip()
                if line.startswith('A:'):
                    answer_text = line[2:].strip()
                    print(f"PARSING DEBUG: Found answer: '{answer_text}'")
                    break
                elif line.startswith('ANSWER:'):
                    answer_text = line[7:].strip()
                    print(f"PARSING DEBUG: Found answer (ANSWER:): '{answer_text}'")
                    break
            
            # For multiple choice, find options
            if question_type == 'multiple_choice':
                for line in lines:
                    line = line.strip()
                    if re.match(r'^[A-D]\)', line):
                        options.append(line)
                
                print(f"PARSING DEBUG: Found {len(options)} options")
                
                # If we don't have 4 options, use defaults
                if len(options) != 4:
                    options = ["A) Option A", "B) Option B", "C) Option C", "D) Option D"]
                    print("PARSING DEBUG: Using default options")
            
            # Extra fallback: if still no Q: found, look for any question mark
            if not question_text:
                print("PARSING DEBUG: No Q: found, looking for question mark...")
                for line in lines:
                    line = line.strip()
                    if '?' in line and not line.startswith(('A)', 'B)', 'C)', 'D)')):
                        question_text = line
                        print(f"PARSING DEBUG: Found question by ?: '{question_text}'")
                        break
            
            # Extra fallback: if still no answer, look for any substantial text
            if not answer_text:
                print("PARSING DEBUG: No A: found, looking for substantial text...")
                for line in lines:
                    line = line.strip()
                    if len(line) > 10 and not line.startswith(('Q:', 'A:', 'ANSWER:', 'A)', 'B)', 'C)', 'D)')):
                        answer_text = line
                        print(f"PARSING DEBUG: Found answer by length: '{answer_text[:50]}...'")
                        break
            
            # Check if we're about to use fallbacks
            if not question_text:
                print("PARSING DEBUG: Using fallback question")
                question_text = "What is discussed in the document?"
            if not answer_text:
                print("PARSING DEBUG: Using fallback answer")
                answer_text = "Based on the document content"
            
            # Build result
            question = {
                'id': question_number,
                'type': question_type,
                'text': question_text,
                'points': self._get_points_by_difficulty_and_type(question_type)
            }
            
            if question_type == 'multiple_choice':
                question['options'] = options
            
            answer = {
                'id': question_number,
                'type': question_type,
                'answer': answer_text
            }
            
            print(f"PARSING DEBUG: Final result - Q: '{question_text}' A: '{answer_text[:50]}...'")
            
            return question, answer
            
        except Exception as e:
            print(f"Error in parsing: {e}")
            print(f"Exception traceback: {traceback.format_exc()}")
            return self._generate_fallback_single_question("", question_type, "medium", question_number)

    def _generate_default_options(self):
        """Generate default options when parsing fails"""
        return [
            "A) Option A",
            "B) Option B",
            "C) Option C", 
            "D) Option D"
        ]
    
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
            
            # Add variation to avoid repetition in fallback questions
            variation_suffix = f" (Question {i + 1})" if i > 0 else ""
            
            question = {
                'id': i + 1,
                'type': question_type,
                'text': f"{base_question['text']}{variation_suffix}",
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
        """Generate a better formatted PDF"""
        
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            
            doc = SimpleDocTemplate(
                temp_file.name, 
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            question_style = ParagraphStyle(
                'QuestionStyle',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=10,
                leftIndent=0,
                fontName='Helvetica-Bold'
            )
            
            option_style = ParagraphStyle(
                'OptionStyle',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=5,
                leftIndent=20
            )
            
            # Title and header
            story.append(Paragraph("Question Paper", title_style))
            story.append(Paragraph("French and Indian War", styles['Heading2']))
            story.append(Spacer(1, 20))
            
            # Instructions
            instructions = """
            <b>Instructions:</b><br/>
            • Read all questions carefully before answering<br/>
            • Write your answers clearly and legibly<br/>
            • Manage your time effectively<br/>
            • Show your work where applicable
            """
            story.append(Paragraph(instructions, styles['Normal']))
            story.append(Spacer(1, 30))
            
            # Questions section
            for i, question in enumerate(questions):
                # Question text
                question_text = f"<b>Question {question['id']}:</b> {question['text']} <i>({question['points']} points)</i>"
                story.append(Paragraph(question_text, question_style))
                
                # Options for multiple choice
                if question['type'] == 'multiple_choice' and 'options' in question:
                    for option in question['options']:
                        story.append(Paragraph(option, option_style))
                
                # Answer space
                if question['type'] == 'short_answer':
                    story.append(Spacer(1, 30))  # Space for writing
                elif question['type'] == 'essay':
                    story.append(Spacer(1, 50))  # More space for essay
                
                story.append(Spacer(1, 20))
            
            # Page break before answer key
            story.append(PageBreak())
            
            # Answer Key
            story.append(Paragraph("Answer Key", title_style))
            story.append(Spacer(1, 20))
            
            for answer in answer_key:
                answer_text = f"<b>Answer {answer['id']}:</b> {answer['answer']}"
                story.append(Paragraph(answer_text, styles['Normal']))
                story.append(Spacer(1, 15))
            
            # Build PDF
            doc.build(story)
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def _debug_llm_response(self, response, question_type, question_number):
        """Debug method to see what the LLM is actually returning"""
        print(f"\n=== DEBUG: Question {question_number} ({question_type}) ===")
        print(f"Raw LLM Response:")
        print(f"'{response}'")
        print(f"Response length: {len(response)}")
        print(f"Lines: {response.split(chr(10))}")
        print("=" * 50) 