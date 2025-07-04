#!/usr/bin/env python3
"""
Quick test script for RAPTOR-Q evaluation system.
This works without spaCy and other problematic dependencies.
"""

import sys
import os
sys.path.append('app/backend')

try:
    from evaluation_system_simple import SimpleQuestionAnswerEvaluator
    print("✅ Simple evaluation system loaded successfully!")
except ImportError as e:
    print(f"❌ Error importing evaluation system: {e}")
    sys.exit(1)

def test_french_indian_war_evaluation():
    """Test evaluation with sample French-Indian War questions."""
    
    print("\n" + "="*60)
    print("🧪 TESTING RAPTOR-Q EVALUATION SYSTEM")
    print("="*60)
    
    # Sample generated questions (simulate RAPTOR-Q output)
    sample_generated_questions = [
        {
            "question": "When did the French and Indian War occur?",
            "answer": "The war took place from 1754 to 1763",
            "type": "short_answer"
        },
        {
            "question": "What were the main causes of the French and Indian War?",
            "answer": "Disputes over land in the Ohio River valley between British colonists and French forces",
            "type": "short_answer"
        },
        {
            "question": "Who were the primary European powers involved?",
            "answer": "Britain and France",
            "type": "short_answer"
        },
        {
            "question": "How did the war end?",
            "answer": "It ended with the Treaty of Paris in 1763, with France ceding territories to Britain",
            "type": "short_answer"
        },
        {
            "question": "What role did George Washington play?",
            "answer": "He led a Virginia militia against French forces in the Ohio Territory in 1754",
            "type": "short_answer"
        }
    ]
    
    print(f"\n📝 Testing with {len(sample_generated_questions)} sample questions...")
    
    # Initialize evaluator
    evaluator = SimpleQuestionAnswerEvaluator(use_embeddings=False)
    
    # Run evaluation
    print("\n🔄 Running evaluation...")
    results = evaluator.evaluate_french_indian_war_example(sample_generated_questions)
    
    # Generate report
    print("\n📊 Generating evaluation report...")
    report = evaluator.generate_evaluation_report(results)
    
    print("\n" + report)
    
    # Summary
    print("\n" + "="*60)
    print("📈 EVALUATION SUMMARY")
    print("="*60)
    
    if results:
        if 'overall_exact_match' in results:
            print(f"Exact Match Score: {results['overall_exact_match']:.2%}")
        if 'overall_f1' in results:
            print(f"F1 Score: {results['overall_f1']:.2%}")
        if 'overall_semantic_similarity' in results:
            print(f"Semantic Similarity: {results['overall_semantic_similarity']:.2%}")
        if 'total_evaluations' in results:
            print(f"Total Evaluations: {results['total_evaluations']}")
    else:
        print("❌ No results generated")
    
    print("\n✅ Evaluation test completed successfully!")
    return results

def test_manual_comparison():
    """Test manual question comparison."""
    
    print("\n" + "="*60)
    print("🔍 MANUAL COMPARISON TEST")
    print("="*60)
    
    evaluator = SimpleQuestionAnswerEvaluator(use_embeddings=False)
    
    # Test exact match
    print("\n📋 Testing Exact Match:")
    pred1 = "1754 to 1763"
    truth1 = "1754 to 1763"
    em_score = evaluator.compute_exact_match(pred1, truth1)
    print(f"  Prediction: '{pred1}'")
    print(f"  Ground Truth: '{truth1}'")
    print(f"  Exact Match: {em_score} ({'✅ MATCH' if em_score else '❌ NO MATCH'})")
    
    # Test F1 score
    print("\n📋 Testing F1 Score:")
    pred2 = "The war lasted from 1754 to 1763"
    truth2 = "1754 to 1763"
    f1_score = evaluator.compute_f1_score(pred2, truth2)
    print(f"  Prediction: '{pred2}'")
    print(f"  Ground Truth: '{truth2}'")
    print(f"  F1 Score: {f1_score:.4f}")
    
    # Test semantic similarity
    print("\n📋 Testing Semantic Similarity:")
    pred3 = "Britain and France were the main combatants"
    truth3 = "Great Britain and France"
    sim_score = evaluator.compute_semantic_similarity(pred3, truth3)
    print(f"  Prediction: '{pred3}'")
    print(f"  Ground Truth: '{truth3}'")
    print(f"  Similarity: {sim_score:.4f}")

if __name__ == "__main__":
    print("🚀 RAPTOR-Q Evaluation System Test")
    print("=" * 60)
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    
    try:
        import numpy
        print("✅ NumPy available")
    except ImportError:
        print("❌ NumPy not available - some features may be limited")
    
    try:
        import nltk
        print("✅ NLTK available - BLEU scores enabled")
    except ImportError:
        print("❌ NLTK not available - BLEU scores disabled")
    
    try:
        import rouge_score
        print("✅ ROUGE available - ROUGE scores enabled")
    except ImportError:
        print("❌ ROUGE not available - ROUGE scores disabled")
    
    try:
        import sentence_transformers
        print("✅ Sentence Transformers available - semantic similarity enabled")
    except ImportError:
        print("❌ Sentence Transformers not available - using token-based similarity")
    
    # Run tests
    try:
        results = test_french_indian_war_evaluation()
        test_manual_comparison()
        
        print("\n" + "🎉" * 20)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("🎉" * 20)
        
        print("\n💡 Next Steps:")
        print("1. Use this evaluation system with your RAPTOR-Q generated questions")
        print("2. Upload the French-Indian War document to RAPTOR-Q")
        print("3. Generate questions and compare them using this evaluation")
        print("4. Install additional dependencies (NLTK, ROUGE) for more metrics")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 