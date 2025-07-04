#!/usr/bin/env python3
"""Test script for separated question and answer generation"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from question_paper_generator import QuestionPaperGenerator

def test_separated_generation():
    """Test that question and answer generation work separately"""
    
    # Create a simple test document
    test_content = """
    The French and Indian War was a conflict between Great Britain and France 
    in North America from 1754 to 1763. It was part of the larger Seven Years' War.
    The war began over territorial disputes in the Ohio Valley.
    """
    
    # Create test file
    test_file = "/tmp/test_document.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Initialize generator
    generator = QuestionPaperGenerator()
    
    try:
        # Test question generation
        print("Testing separated question and answer generation...")
        
        # Generate a question paper
        result = generator.generate_question_paper(
            file_path=test_file,
            num_questions=3,
            difficulty='easy',
            question_types=['short_answer']
        )
        
        print(f"Generated {len(result['questions'])} questions")
        print(f"Generated {len(result['answer_key'])} answers")
        
        # Display results
        for i, (question, answer) in enumerate(zip(result['questions'], result['answer_key']), 1):
            print(f"\nQuestion {i}:")
            print(f"  Text: {question['text']}")
            print(f"  Type: {question['type']}")
            print(f"  Points: {question['points']}")
            
            print(f"Answer {i}:")
            print(f"  Answer: {answer['answer']}")
            print(f"  Type: {answer['type']}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_separated_generation() 