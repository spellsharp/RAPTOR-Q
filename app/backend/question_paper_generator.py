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
        """Extract content from various document formats with robust error handling"""
        try:
            if not file_path or not os.path.exists(file_path):
                return "Error: File not found or path is invalid"
            
            file_extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
            
            if file_extension == 'pdf':
                return self._extract_pdf_content(file_path)
            elif file_extension in ['doc', 'docx']:
                return self._extract_word_content(file_path)
            elif file_extension == 'txt':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        return content if content.strip() else "Error: Text file is empty"
                except UnicodeDecodeError:
                    # Try different encodings
                    for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                                return content if content.strip() else "Error: Text file is empty"
                        except UnicodeDecodeError:
                            continue
                    return "Error: Unable to decode text file with any encoding"
            else:
                return f"Error: Unsupported file format '.{file_extension}'. Supported formats: PDF, DOCX, DOC, TXT"
        except Exception as e:
            print(f"Error extracting document content: {e}")
            return f"Error: Document content could not be extracted - {str(e)}"
    
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
        """Clean up document content formatting"""
        # Clean up formatting only - chunking is handled separately
        document_content = re.sub(r'\s+', ' ', document_content)
        document_content = re.sub(r'\n+', '\n', document_content)
        return document_content.strip()
    
    def _get_content_chunks(self, document_content, max_chunk_size=3000):
        """Split document content into meaningful chunks for question generation"""
        try:
            if not document_content or not document_content.strip():
                return ["No content available for question generation"]
            
            if len(document_content) <= max_chunk_size:
                return [document_content]
            
            # First try to split by paragraphs (double newlines)
            paragraphs = document_content.split('\n\n')
            chunks = []
            current_chunk = ""
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                    
                # If adding this paragraph would exceed the limit, start a new chunk
                if len(current_chunk) + len(paragraph) + 2 > max_chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    current_chunk += ("\n\n" + paragraph if current_chunk else paragraph)
            
            # Add the last chunk
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            # If paragraphs are too large, split by sentences
            if not chunks or max(len(chunk) for chunk in chunks) > max_chunk_size:
                chunks = []
                sentences = re.split(r'(?<=[.!?])\s+', document_content)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    if len(current_chunk) + len(sentence) + 1 > max_chunk_size and current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += (" " + sentence if current_chunk else sentence)
                
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
            
            # Ensure we have at least one chunk
            return chunks if chunks else [document_content[:max_chunk_size]]
            
        except Exception as e:
            print(f"Error in content chunking: {e}")
            # Return a safe fallback
            return [document_content[:max_chunk_size] if document_content else "No content available"]
    
    def _generate_single_question(self, document_content, question_type, difficulty, question_number, previous_questions=None):
        """Generate a single question with smart retry mechanism"""
        if self.lm_studio_llm is None:
            return self._generate_fallback_single_question(document_content, question_type, difficulty, question_number)
        
        try:
            # Clean document content
            document_content = self._preprocess_document_content(document_content)
            content_chunks = self._get_content_chunks(document_content, 3000)
            
            # Try different chunks until we get a valid question
            max_attempts = min(len(content_chunks), 3)  # Try up to 3 chunks
            
            for attempt in range(max_attempts):
                try:
                    # Calculate chunk index (start with the rotation index, then try others)
                    base_chunk_index = len(previous_questions or []) % len(content_chunks)
                    chunk_index = (base_chunk_index + attempt) % len(content_chunks)
                    
                    print(f"ATTEMPT {attempt + 1}: Trying chunk {chunk_index + 1}/{len(content_chunks)} (length: {len(content_chunks[chunk_index])})")
                    
                    # Create prompt with this specific chunk
                    prompt = self._create_prompt(
                        document_content, 
                        question_type, 
                        difficulty, 
                        previous_questions,
                        specific_chunk=content_chunks[chunk_index]
                    )
                    
                    # Get response from LLM
                    response = self.lm_studio_llm.invoke(prompt)
                    
                    # Debug: print raw response
                    self._debug_llm_response(response, question_type, question_number, attempt + 1)
                    
                    # Parse the response
                    question, answer = self._parse_response(response, question_type, question_number)
                    
                    # Check if we got a valid question (not a fallback)
                    if not self._is_fallback_question(question['text']):
                        print(f"SUCCESS: Generated valid question on attempt {attempt + 1}")
                        return question, answer
                    else:
                        print(f"ATTEMPT {attempt + 1} FAILED: Got fallback question, trying next chunk...")
                        
                except Exception as attempt_error:
                    print(f"ATTEMPT {attempt + 1} ERROR: {attempt_error}")
                    continue
            
            # If all chunks failed, generate a fallback question
            print(f"ALL ATTEMPTS FAILED: Using fallback question after {max_attempts} attempts")
            return self._generate_fallback_single_question(document_content, question_type, difficulty, question_number)
            
        except Exception as e:
            print(f"Error in question generation: {e}")
            return self._generate_fallback_single_question(document_content, question_type, difficulty, question_number)
    
    def _create_prompt(self, document_content, question_type, difficulty, previous_questions=None, specific_chunk=None):
        """Create a prompt for question generation"""
        
        if specific_chunk is not None:
            # Use the provided chunk
            selected_content = specific_chunk
            print(f"CHUNK CONTENT PREVIEW: {selected_content[:100]}...")
        else:
            # Use different chunks of content for variety
            content_chunks = self._get_content_chunks(document_content, 3000)
            
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
            for i, prev_q in enumerate(previous_questions[:5], 1):  # Limit to 5 to avoid overly long prompts
                previous_questions_text += f"{i}. {prev_q}\n"
            previous_questions_text += "\n"
        
        # Generate prompt based on question type
        prompt_templates = {
            'multiple_choice': f"""TEXT: {selected_content}{previous_questions_text}
TASK: Write EXACTLY 1 NEW multiple choice question. Use ONLY this format:

Q: [question]
A) [option]
B) [option] 
C) [option]
D) [option]
ANSWER: A

NO other text allowed.""",

            'short_answer': f"""TEXT: {selected_content}{previous_questions_text}
TASK: Write EXACTLY 1 NEW short answer question. Use ONLY this format:

Q: [question]
A: [answer around 70 words]

NO other text allowed.""",

            'essay': f"""TEXT: {selected_content}{previous_questions_text}
TASK: Write EXACTLY 1 NEW essay question. Use ONLY this format:

Q: [question]
A: [comprehensive answer around 150 words]

NO other text allowed."""
        }
        
        return prompt_templates.get(question_type, prompt_templates['short_answer'])
    
    def _is_fallback_question(self, question_text):
        """Check if a question is a generic fallback question"""
        fallback_phrases = [
            "what is discussed in the document",
            "what is the main topic",
            "explain the main concepts",
            "based on the document, explain",
            "what does the document discuss"
        ]
        
        question_lower = question_text.lower()
        return any(phrase in question_lower for phrase in fallback_phrases)
    
    def _parse_response(self, response, question_type, question_number):
        """Parse LLM response with multi-line answer support"""
        
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
            
            # Find answer with multi-line support
            if question_type == 'multiple_choice':
                # For multiple choice, find options first
                for line in lines:
                    line = line.strip()
                    if re.match(r'^[A-D]\)', line):
                        options.append(line)
                
                # Find the correct answer
                for line in lines:
                    line = line.strip()
                    if line.startswith('ANSWER:'):
                        answer_text = line[7:].strip()
                        print(f"PARSING DEBUG: Found answer (ANSWER:): '{answer_text}'")
                        break
                
                print(f"PARSING DEBUG: Found {len(options)} options")
                
                # If we don't have 4 options, use defaults
                if len(options) != 4:
                    options = ["A) Option A", "B) Option B", "C) Option C", "D) Option D"]
                    print("PARSING DEBUG: Using default options")
            else:
                # For short answer and essay, collect multi-line answers
                answer_started = False
                answer_lines = []
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line.startswith('A:'):
                        answer_started = True
                        # Add the answer text after "A:"
                        answer_content = line[2:].strip()
                        if answer_content:
                            answer_lines.append(answer_content)
                    elif answer_started and line:
                        # Check if this is a new section starting
                        if line.startswith(('Q:', 'TASK:', 'TEXT:', 'NO other text')):
                            break
                        # Otherwise, this is part of the answer
                        answer_lines.append(line)
                    elif answer_started and not line:
                        # Empty line - check if next line is continuation
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line and not next_line.startswith(('Q:', 'TASK:', 'TEXT:', 'NO other text')):
                                # Next line is continuation, add empty line
                                answer_lines.append('')
                            else:
                                # Next line is new section, stop here
                                break
                        else:
                            # End of response, stop here
                            break
                
                # Join answer lines properly
                if answer_lines:
                    # Remove trailing empty lines
                    while answer_lines and not answer_lines[-1].strip():
                        answer_lines.pop()
                    answer_text = '\n'.join(answer_lines)
                    print(f"PARSING DEBUG: Found multi-line answer: '{answer_text[:50]}...'")
            
            # Extra fallback: if still no Q: found, look for any question mark
            if not question_text:
                print("PARSING DEBUG: No Q: found, looking for question mark...")
                for line in lines:
                    line = line.strip()
                    if '?' in line and not line.startswith(('A)', 'B)', 'C)', 'D)')):
                        question_text = line
                        print(f"PARSING DEBUG: Found question by ?: '{question_text}'")
                        break
            
            # Extra fallback: if still no answer for non-multiple choice
            if not answer_text and question_type != 'multiple_choice':
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
    

    
    def _extract_correct_answer(self, response, options):
        """Extract the correct answer for multiple choice questions"""
        
        # Look for lines starting with "ANSWER:" 
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('ANSWER:'):
                answer_letter = line[7:].strip()
                if answer_letter in ['A', 'B', 'C', 'D']:
                    return answer_letter
        
        # Default to A if no answer found
        return 'A'
    
    def _extract_multiple_choice_options(self, response):
        """Extract multiple choice options from LLM response with simple parsing"""
        
        try:
            options = []
            lines = response.strip().split('\n')
            
            # Look for lines starting with A), B), C), D)
            for line in lines:
                line = line.strip()
                if re.match(r'^[A-D]\)', line):
                    options.append(line)
            
            # If we found valid options, return them
            if len(options) >= 2:
                # Ensure we have exactly 4 options
                while len(options) < 4:
                    next_letter = chr(ord('A') + len(options))
                    options.append(f"{next_letter}) Additional option")
                
                return options[:4]  # Return only first 4 options
            
            # If no valid options found, return default
            return ["A) Option A", "B) Option B", "C) Option C", "D) Option D"]
            
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
    
    def _debug_llm_response(self, response, question_type, question_number, attempt=None):
        """Debug method to see what the LLM is actually returning"""
        attempt_text = f" (Attempt {attempt})" if attempt else ""
        print(f"\n=== DEBUG: Question {question_number} ({question_type}){attempt_text} ===")
        print(f"Raw LLM Response:")
        print(f"'{response}'")
        print(f"Response length: {len(response)}")
        print(f"Lines: {response.split(chr(10))}")
        print("=" * 50) 