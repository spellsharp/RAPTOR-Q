#!/usr/bin/env python3
"""
Practical example: Evaluate your RAPTOR-Q generated questions
against the French-Indian War paragraph using SQuAD2.0 metrics.
"""

import sys
import os
import json
sys.path.append('app/backend')

from evaluation_system_simple import SimpleQuestionAnswerEvaluator

def evaluate_my_raptor_q_questions():
    """
    Example of how to evaluate your actual RAPTOR-Q generated questions.
    
    Replace the sample_questions with your actual RAPTOR-Q output.
    """
    
    print("🔥 EVALUATING RAPTOR-Q FRENCH-INDIAN WAR QUESTIONS")
    print("=" * 60)
    
    # 📝 REPLACE THIS with your actual RAPTOR-Q generated questions
    # This is just an example - use your real generated questions here
    my_generated_questions = [
        {
            "question": "What time period did the French and Indian War span?",
            "answer": "The French and Indian War lasted from 1754 to 1763, a period of 9 years.",
            "type": "short_answer"
        },
        {
            "question": "Which two European nations were the primary adversaries?",
            "answer": "Great Britain and France were the main combatants in North America.",
            "type": "short_answer"
        },
        {
            "question": "What geographical region was the main source of conflict?",
            "answer": "The Ohio River valley was disputed territory that caused the conflict.",
            "type": "short_answer"
        },
        {
            "question": "How was the conflict resolved?",
            "answer": "The war ended with the Treaty of Paris in 1763, giving Britain control of French territories.",
            "type": "short_answer"
        },
        {
            "question": "What role did George Washington play in the early conflict?",
            "answer": "Washington led Virginia militia forces against the French in 1754.",
            "type": "short_answer"
        }
    ]
    
    print(f"📊 Evaluating {len(my_generated_questions)} questions...")
    print("\nYour Generated Questions:")
    for i, q in enumerate(my_generated_questions, 1):
        print(f"{i}. {q['question']}")
        print(f"   Answer: {q['answer']}")
        print()
    
    # Initialize evaluator
    evaluator = SimpleQuestionAnswerEvaluator(use_embeddings=False)
    
    # Run evaluation against French-Indian War reference data
    print("🔍 Comparing against SQuAD2.0-style reference answers...")
    results = evaluator.evaluate_french_indian_war_example(my_generated_questions)
    
    # Generate detailed report
    print("\n📋 DETAILED EVALUATION REPORT")
    print("=" * 60)
    report = evaluator.generate_evaluation_report(results)
    print(report)
    
    # Performance analysis
    print("\n🎯 PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    if results:
        em_score = results.get('overall_exact_match', 0)
        f1_score = results.get('overall_f1', 0)
        sim_score = results.get('overall_semantic_similarity', 0)
        
        print(f"📊 Your Results:")
        print(f"   Exact Match: {em_score:.1%} - {'🟢 Good' if em_score > 0.5 else '🟡 Fair' if em_score > 0.3 else '🔴 Needs Improvement'}")
        print(f"   F1 Score: {f1_score:.1%} - {'🟢 Good' if f1_score > 0.6 else '🟡 Fair' if f1_score > 0.4 else '🔴 Needs Improvement'}")
        print(f"   Similarity: {sim_score:.1%} - {'🟢 Good' if sim_score > 0.6 else '🟡 Fair' if sim_score > 0.4 else '🔴 Needs Improvement'}")
        
        # Specific feedback
        print(f"\n💡 Feedback:")
        if em_score < 0.3:
            print("   • Consider making answers more concise and factual")
        if f1_score < 0.5:
            print("   • Answers could include more key terms from the text")
        if sim_score < 0.5:
            print("   • Questions could be more focused on main concepts")
        
        if em_score > 0.4 and f1_score > 0.5:
            print("   ✅ Good quality questions! Keep it up!")
    
    # Save results
    output_file = "my_evaluation_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'questions': my_generated_questions,
            'evaluation_results': results,
            'timestamp': str(os.path.getctime('.')),
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return results

def compare_individual_answers():
    """Show individual question comparisons."""
    
    print("\n🔍 INDIVIDUAL QUESTION ANALYSIS")
    print("=" * 60)
    
    evaluator = SimpleQuestionAnswerEvaluator(use_embeddings=False)
    
    # Example comparisons
    examples = [
        {
            "your_answer": "The war lasted from 1754 to 1763, a period of 9 years",
            "reference": "1754 to 1763",
            "question": "When did the French and Indian War take place?"
        },
        {
            "your_answer": "Great Britain and France were the main combatants",
            "reference": "Britain and France",
            "question": "Which European powers were involved?"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📋 Comparison {i}:")
        print(f"Question: {example['question']}")
        print(f"Your Answer: '{example['your_answer']}'")
        print(f"Reference: '{example['reference']}'")
        
        em = evaluator.compute_exact_match(example['your_answer'], example['reference'])
        f1 = evaluator.compute_f1_score(example['your_answer'], example['reference'])
        sim = evaluator.compute_semantic_similarity(example['your_answer'], example['reference'])
        
        print(f"Results:")
        print(f"  Exact Match: {'✅' if em else '❌'} ({em})")
        print(f"  F1 Score: {f1:.3f}")
        print(f"  Similarity: {sim:.3f}")

def main():
    print("🎯 RAPTOR-Q Question Evaluation Tool")
    print("=" * 60)
    print("This tool evaluates your generated questions against SQuAD2.0 standards")
    print("for the French-Indian War topic.\n")
    
    try:
        # Run main evaluation
        results = evaluate_my_raptor_q_questions()
        
        # Show individual comparisons
        compare_individual_answers()
        
        print("\n" + "🎉" * 20)
        print("EVALUATION COMPLETE!")
        print("🎉" * 20)
        
        print(f"\n📝 Next Steps:")
        print("1. Review the evaluation report above")
        print("2. Replace sample questions with your actual RAPTOR-Q output")
        print("3. Iterate and improve based on the feedback")
        print("4. Try with different documents and topics")
        
        # Instructions for using with real RAPTOR-Q
        print(f"\n🔧 To use with real RAPTOR-Q questions:")
        print("1. Generate questions using RAPTOR-Q web interface")
        print("2. Copy the generated questions into 'my_generated_questions' list")
        print("3. Run this script again")
        print("4. Compare your scores against the reference standards")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 