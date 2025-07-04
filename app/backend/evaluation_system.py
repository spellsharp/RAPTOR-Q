"""
RAPTOR-Q Evaluation System

This module provides comprehensive evaluation capabilities for generated questions and answers,
including metrics compatible with SQuAD2.0 evaluation standards.
"""

import json
import re
import string
import numpy as np
from typing import List, Dict, Tuple, Union, Optional
from collections import Counter
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class QuestionAnswerEvaluator:
    """
    Comprehensive evaluation system for question-answer pairs generated by RAPTOR-Q.
    
    Supports multiple evaluation metrics:
    - SQuAD-style metrics (Exact Match, F1)
    - BLEU scores for question quality
    - ROUGE scores for answer quality
    - Semantic similarity measures
    - Question type classification accuracy
    - Answer span evaluation
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the evaluator with necessary models and scorers.
        
        Args:
            model_name (str): Name of the sentence transformer model for semantic similarity
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize scoring models
        try:
            self.sentence_model = SentenceTransformer(model_name)
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("Spacy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        self.smoothing_function = SmoothingFunction().method1
        
        # Initialize evaluation metrics storage
        self.reset_metrics()
    
    def reset_metrics(self):
        """Reset all accumulated metrics."""
        self.metrics = {
            'exact_match': [],
            'f1_score': [],
            'bleu_scores': [],
            'rouge_scores': {'rouge1': [], 'rouge2': [], 'rougeL': []},
            'semantic_similarity': [],
            'question_type_accuracy': [],
            'answer_span_accuracy': [],
            'has_answer_accuracy': []
        }
    
    def normalize_answer(self, text: str) -> str:
        """
        Normalize answer text following SQuAD evaluation standards.
        
        Args:
            text (str): Text to normalize
            
        Returns:
            str: Normalized text
        """
        def remove_articles(text):
            return re.sub(r'\b(a|an|the)\b', ' ', text)
        
        def white_space_fix(text):
            return ' '.join(text.split())
        
        def remove_punc(text):
            exclude = set(string.punctuation)
            return ''.join(ch for ch in text if ch not in exclude)
        
        def lower(text):
            return text.lower()
        
        return white_space_fix(remove_articles(remove_punc(lower(text))))
    
    def get_tokens(self, text: str) -> List[str]:
        """
        Tokenize text for F1 score calculation.
        
        Args:
            text (str): Text to tokenize
            
        Returns:
            List[str]: List of tokens
        """
        if not text:
            return []
        return self.normalize_answer(text).split()
    
    def compute_exact_match(self, prediction: str, ground_truth: str) -> bool:
        """
        Compute exact match score following SQuAD standards.
        
        Args:
            prediction (str): Predicted answer
            ground_truth (str): Ground truth answer
            
        Returns:
            bool: True if exact match, False otherwise
        """
        return self.normalize_answer(prediction) == self.normalize_answer(ground_truth)
    
    def compute_f1_score(self, prediction: str, ground_truth: str) -> float:
        """
        Compute F1 score following SQuAD standards.
        
        Args:
            prediction (str): Predicted answer
            ground_truth (str): Ground truth answer
            
        Returns:
            float: F1 score between 0 and 1
        """
        pred_tokens = self.get_tokens(prediction)
        gold_tokens = self.get_tokens(ground_truth)
        
        if len(pred_tokens) == 0 or len(gold_tokens) == 0:
            return int(pred_tokens == gold_tokens)
        
        common_tokens = Counter(pred_tokens) & Counter(gold_tokens)
        num_same = sum(common_tokens.values())
        
        if num_same == 0:
            return 0
        
        precision = 1.0 * num_same / len(pred_tokens)
        recall = 1.0 * num_same / len(gold_tokens)
        f1 = (2 * precision * recall) / (precision + recall)
        
        return f1
    
    def compute_bleu_score(self, candidate: str, references: List[str]) -> float:
        """
        Compute BLEU score for question quality evaluation.
        
        Args:
            candidate (str): Generated question
            references (List[str]): Reference questions
            
        Returns:
            float: BLEU score
        """
        candidate_tokens = self.get_tokens(candidate)
        reference_tokens = [self.get_tokens(ref) for ref in references]
        
        if not candidate_tokens or not any(reference_tokens):
            return 0.0
        
        try:
            score = sentence_bleu(reference_tokens, candidate_tokens, 
                                smoothing_function=self.smoothing_function)
            return score
        except:
            return 0.0
    
    def compute_rouge_scores(self, candidate: str, reference: str) -> Dict[str, float]:
        """
        Compute ROUGE scores for answer quality evaluation.
        
        Args:
            candidate (str): Generated answer
            reference (str): Reference answer
            
        Returns:
            Dict[str, float]: ROUGE scores
        """
        scores = self.rouge_scorer.score(reference, candidate)
        return {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }
    
    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Cosine similarity score
        """
        try:
            embeddings = self.sentence_model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def evaluate_question_answer_pair(self, 
                                    generated_qa: Dict, 
                                    reference_qa: Dict) -> Dict[str, float]:
        """
        Evaluate a single question-answer pair against reference.
        
        Args:
            generated_qa (Dict): Generated Q&A with keys 'question', 'answer', 'type'
            reference_qa (Dict): Reference Q&A with keys 'question', 'answer', 'type'
            
        Returns:
            Dict[str, float]: Evaluation metrics
        """
        results = {}
        
        # Answer evaluation
        if 'answer' in generated_qa and 'answer' in reference_qa:
            # Exact match
            results['exact_match'] = self.compute_exact_match(
                generated_qa['answer'], reference_qa['answer']
            )
            
            # F1 score
            results['f1_score'] = self.compute_f1_score(
                generated_qa['answer'], reference_qa['answer']
            )
            
            # ROUGE scores
            rouge_scores = self.compute_rouge_scores(
                generated_qa['answer'], reference_qa['answer']
            )
            results.update(rouge_scores)
            
            # Semantic similarity
            results['semantic_similarity'] = self.compute_semantic_similarity(
                generated_qa['answer'], reference_qa['answer']
            )
        
        # Question evaluation
        if 'question' in generated_qa and 'question' in reference_qa:
            # BLEU score for question quality
            results['question_bleu'] = self.compute_bleu_score(
                generated_qa['question'], [reference_qa['question']]
            )
            
            # Question semantic similarity
            results['question_similarity'] = self.compute_semantic_similarity(
                generated_qa['question'], reference_qa['question']
            )
        
        # Question type accuracy
        if 'type' in generated_qa and 'type' in reference_qa:
            results['type_accuracy'] = int(generated_qa['type'] == reference_qa['type'])
        
        return results
    
    def evaluate_against_squad_data(self, 
                                   generated_qas: List[Dict], 
                                   squad_data: Dict) -> Dict[str, float]:
        """
        Evaluate generated questions against SQuAD2.0 format data.
        
        Args:
            generated_qas (List[Dict]): List of generated Q&As
            squad_data (Dict): SQuAD2.0 format data
            
        Returns:
            Dict[str, float]: Comprehensive evaluation metrics
        """
        all_results = []
        
        # Extract reference Q&As from SQuAD data
        reference_qas = []
        for paragraph in squad_data.get('data', []):
            for qa in paragraph.get('qas', []):
                ref_qa = {
                    'question': qa.get('question', ''),
                    'answer': qa.get('answers', [{}])[0].get('text', '') if qa.get('answers') else '',
                    'type': self._infer_question_type(qa.get('question', '')),
                    'is_impossible': qa.get('is_impossible', False)
                }
                reference_qas.append(ref_qa)
        
        # Evaluate each generated Q&A against the most similar reference
        for gen_qa in generated_qas:
            best_match = self._find_best_match(gen_qa, reference_qas)
            if best_match:
                result = self.evaluate_question_answer_pair(gen_qa, best_match)
                all_results.append(result)
        
        return self._aggregate_results(all_results)
    
    def evaluate_french_indian_war_example(self, generated_qas: List[Dict]) -> Dict[str, float]:
        """
        Evaluate against a sample French-Indian War paragraph similar to SQuAD2.0.
        
        Args:
            generated_qas (List[Dict]): Generated question-answer pairs
            
        Returns:
            Dict[str, float]: Evaluation metrics
        """
        # Sample reference Q&As for French-Indian War context
        reference_qas = [
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
        ]
        
        all_results = []
        for gen_qa in generated_qas:
            best_match = self._find_best_match(gen_qa, reference_qas)
            if best_match:
                result = self.evaluate_question_answer_pair(gen_qa, best_match)
                all_results.append(result)
        
        return self._aggregate_results(all_results)
    
    def _find_best_match(self, generated_qa: Dict, reference_qas: List[Dict]) -> Optional[Dict]:
        """
        Find the best matching reference Q&A for a generated Q&A.
        
        Args:
            generated_qa (Dict): Generated Q&A
            reference_qas (List[Dict]): List of reference Q&As
            
        Returns:
            Optional[Dict]: Best matching reference Q&A
        """
        if not reference_qas:
            return None
        
        best_score = -1
        best_match = None
        
        for ref_qa in reference_qas:
            # Calculate similarity based on question content
            if 'question' in generated_qa and 'question' in ref_qa:
                similarity = self.compute_semantic_similarity(
                    generated_qa['question'], ref_qa['question']
                )
                if similarity > best_score:
                    best_score = similarity
                    best_match = ref_qa
        
        return best_match
    
    def _infer_question_type(self, question: str) -> str:
        """
        Infer question type from question text.
        
        Args:
            question (str): Question text
            
        Returns:
            str: Inferred question type
        """
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['what', 'who', 'when', 'where', 'why', 'how']):
            return 'short_answer'
        elif 'which' in question_lower and ('a)', 'b)', 'c)', 'd)') in question_lower:
            return 'multiple_choice'
        elif len(question.split()) > 15:
            return 'essay'
        else:
            return 'short_answer'
    
    def _aggregate_results(self, results: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Aggregate evaluation results across multiple Q&A pairs.
        
        Args:
            results (List[Dict[str, float]]): List of individual evaluation results
            
        Returns:
            Dict[str, float]: Aggregated metrics
        """
        if not results:
            return {}
        
        aggregated = {}
        
        # Calculate averages for each metric
        for metric in results[0].keys():
            values = [r[metric] for r in results if metric in r and r[metric] is not None]
            if values:
                aggregated[f"avg_{metric}"] = np.mean(values)
                aggregated[f"max_{metric}"] = np.max(values)
                aggregated[f"min_{metric}"] = np.min(values)
                aggregated[f"std_{metric}"] = np.std(values)
        
        # Calculate overall scores
        if any('exact_match' in r for r in results):
            aggregated['overall_exact_match'] = np.mean([r.get('exact_match', 0) for r in results])
        
        if any('f1_score' in r for r in results):
            aggregated['overall_f1'] = np.mean([r.get('f1_score', 0) for r in results])
        
        if any('semantic_similarity' in r for r in results):
            aggregated['overall_semantic_similarity'] = np.mean([r.get('semantic_similarity', 0) for r in results])
        
        # Count total evaluations
        aggregated['total_evaluations'] = len(results)
        
        return aggregated
    
    def generate_evaluation_report(self, results: Dict[str, float], 
                                 output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive evaluation report.
        
        Args:
            results (Dict[str, float]): Evaluation results
            output_path (Optional[str]): Path to save the report
            
        Returns:
            str: Formatted evaluation report
        """
        report = []
        report.append("=" * 60)
        report.append("RAPTOR-Q Evaluation Report")
        report.append("=" * 60)
        report.append("")
        
        # Overall Performance
        report.append("📊 OVERALL PERFORMANCE")
        report.append("-" * 30)
        if 'overall_exact_match' in results:
            report.append(f"Exact Match Score: {results['overall_exact_match']:.4f}")
        if 'overall_f1' in results:
            report.append(f"F1 Score: {results['overall_f1']:.4f}")
        if 'overall_semantic_similarity' in results:
            report.append(f"Semantic Similarity: {results['overall_semantic_similarity']:.4f}")
        report.append("")
        
        # Detailed Metrics
        report.append("📈 DETAILED METRICS")
        report.append("-" * 30)
        
        metric_categories = {
            'Answer Quality': ['exact_match', 'f1_score', 'rouge1', 'rouge2', 'rougeL'],
            'Question Quality': ['question_bleu', 'question_similarity'],
            'Semantic Understanding': ['semantic_similarity'],
            'Type Accuracy': ['type_accuracy']
        }
        
        for category, metrics in metric_categories.items():
            report.append(f"\n{category}:")
            for metric in metrics:
                avg_key = f"avg_{metric}"
                if avg_key in results:
                    report.append(f"  {metric}: {results[avg_key]:.4f}")
        
        # Statistics
        report.append("")
        report.append("📊 STATISTICS")
        report.append("-" * 30)
        if 'total_evaluations' in results:
            report.append(f"Total Evaluations: {results['total_evaluations']}")
        
        # Performance Grade
        report.append("")
        report.append("🎯 PERFORMANCE GRADE")
        report.append("-" * 30)
        grade = self._calculate_grade(results)
        report.append(f"Overall Grade: {grade}")
        
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"Evaluation report saved to: {output_path}")
        
        return report_text
    
    def _calculate_grade(self, results: Dict[str, float]) -> str:
        """
        Calculate an overall performance grade.
        
        Args:
            results (Dict[str, float]): Evaluation results
            
        Returns:
            str: Performance grade
        """
        scores = []
        
        if 'overall_f1' in results:
            scores.append(results['overall_f1'])
        if 'overall_semantic_similarity' in results:
            scores.append(results['overall_semantic_similarity'])
        if 'avg_rouge1' in results:
            scores.append(results['avg_rouge1'])
        
        if not scores:
            return "Insufficient data"
        
        avg_score = np.mean(scores)
        
        if avg_score >= 0.9:
            return "A+ (Excellent)"
        elif avg_score >= 0.8:
            return "A (Very Good)"
        elif avg_score >= 0.7:
            return "B (Good)"
        elif avg_score >= 0.6:
            return "C (Fair)"
        elif avg_score >= 0.5:
            return "D (Poor)"
        else:
            return "F (Fail)"

# Example usage functions
def load_squad_data(file_path: str) -> Dict:
    """Load SQuAD2.0 format data from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def evaluate_raptor_q_output(generated_questions: List[Dict], 
                           reference_data: Optional[Dict] = None) -> Dict[str, float]:
    """
    Evaluate RAPTOR-Q generated questions against reference data.
    
    Args:
        generated_questions (List[Dict]): Generated questions from RAPTOR-Q
        reference_data (Optional[Dict]): Reference SQuAD2.0 data
        
    Returns:
        Dict[str, float]: Evaluation results
    """
    evaluator = QuestionAnswerEvaluator()
    
    if reference_data:
        results = evaluator.evaluate_against_squad_data(generated_questions, reference_data)
    else:
        # Use French-Indian War example
        results = evaluator.evaluate_french_indian_war_example(generated_questions)
    
    return results

# CLI interface for evaluation
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate RAPTOR-Q generated questions")
    parser.add_argument("--generated", required=True, help="Path to generated questions JSON")
    parser.add_argument("--reference", help="Path to reference SQuAD2.0 data JSON")
    parser.add_argument("--output", help="Path to save evaluation report")
    
    args = parser.parse_args()
    
    # Load generated questions
    with open(args.generated, 'r', encoding='utf-8') as f:
        generated_data = json.load(f)
    
    # Load reference data if provided
    reference_data = None
    if args.reference:
        reference_data = load_squad_data(args.reference)
    
    # Evaluate
    results = evaluate_raptor_q_output(generated_data, reference_data)
    
    # Generate report
    evaluator = QuestionAnswerEvaluator()
    report = evaluator.generate_evaluation_report(results, args.output)
    print(report) 