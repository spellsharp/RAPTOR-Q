# 📊 RAPTOR-Q Evaluation Guide

## Overview

This guide explains how to evaluate RAPTOR-Q generated questions and answers using comprehensive metrics compatible with SQuAD2.0 standards. The evaluation system provides multiple metrics to assess question quality, answer accuracy, and overall performance.

## 🎯 Evaluation Metrics

### Core SQuAD2.0 Metrics
- **Exact Match (EM)**: Percentage of predictions that match the ground truth exactly
- **F1 Score**: Token-level F1 score between prediction and ground truth
- **Semantic Similarity**: Cosine similarity using sentence embeddings

### Additional Quality Metrics
- **BLEU Score**: Evaluates question quality against reference questions
- **ROUGE Scores**: Evaluates answer quality (ROUGE-1, ROUGE-2, ROUGE-L)
- **Question Type Accuracy**: Accuracy of question type classification
- **Answer Span Accuracy**: Accuracy of answer span identification

## 🚀 Getting Started

### Installation

Install the required dependencies:
```bash
pip install -r app/backend/requirements.txt
python -m spacy download en_core_web_sm
```

### Python API Usage

```python
from app.backend.evaluation_system import QuestionAnswerEvaluator, evaluate_raptor_q_output

# Initialize evaluator
evaluator = QuestionAnswerEvaluator()

# Example generated questions
generated_questions = [
    {
        "question": "What was the duration of the French and Indian War?",
        "answer": "The French and Indian War lasted from 1754 to 1763.",
        "type": "short_answer"
    },
    {
        "question": "Which nations were the primary combatants?",
        "answer": "Great Britain and France",
        "type": "short_answer"
    }
]

# Evaluate against French-Indian War references
results = evaluator.evaluate_french_indian_war_example(generated_questions)

# Generate report
report = evaluator.generate_evaluation_report(results)
print(report)
```

### REST API Usage

The evaluation system is integrated into the RAPTOR-Q backend with two endpoints:

#### 1. Evaluate Questions
```bash
curl -X POST http://localhost:5000/api/evaluate-questions \
-H "Content-Type: application/json" \
-d '{
  "generated_questions": [
    {
      "question": "What was the French and Indian War?",
      "answer": "A conflict between Britain and France in North America from 1754 to 1763",
      "type": "short_answer"
    }
  ],
  "evaluation_type": "french_indian_war"
}'
```

#### 2. Get Evaluation Examples
```bash
curl -X GET http://localhost:5000/api/evaluation-examples
```

## 📋 Evaluation Examples

### French-Indian War Evaluation

#### Step 1: Generate Questions
Use RAPTOR-Q to generate questions from the French-Indian War paragraph:

```bash
# Upload the French-Indian War document
curl -X POST http://localhost:5000/api/upload \
-F "file=@evaluation_samples/french_indian_war_paragraph.txt"

# Generate questions
curl -X POST http://localhost:5000/api/generate-questions \
-H "Content-Type: application/json" \
-d '{
  "file_id": "your_file_id",
  "num_questions": 5,
  "difficulty": "medium",
  "question_types": ["short_answer", "multiple_choice"]
}'
```

#### Step 2: Evaluate Generated Questions
```bash
curl -X POST http://localhost:5000/api/evaluate-questions \
-H "Content-Type: application/json" \
-d '{
  "generated_questions": [
    {
      "question": "When did the French and Indian War take place?",
      "answer": "1754 to 1763",
      "type": "short_answer"
    },
    {
      "question": "What caused the French and Indian War?",
      "answer": "Disputes over land in the Ohio River valley",
      "type": "short_answer"
    }
  ],
  "evaluation_type": "french_indian_war"
}'
```

#### Step 3: Interpret Results
```json
{
  "message": "Evaluation completed successfully",
  "results": {
    "overall_exact_match": 0.6,
    "overall_f1": 0.75,
    "overall_semantic_similarity": 0.82,
    "avg_rouge1": 0.68,
    "avg_rouge2": 0.54,
    "avg_rougeL": 0.71,
    "total_evaluations": 5
  },
  "report": "=== RAPTOR-Q Evaluation Report ===\n..."
}
```

### SQuAD2.0 Data Evaluation

For evaluation against actual SQuAD2.0 data:

```python
import json
from app.backend.evaluation_system import load_squad_data, evaluate_raptor_q_output

# Load SQuAD2.0 data
squad_data = load_squad_data('path/to/squad_data.json')

# Load generated questions
with open('generated_questions.json', 'r') as f:
    generated_questions = json.load(f)

# Evaluate
results = evaluate_raptor_q_output(generated_questions, squad_data)
```

## 📊 Understanding Evaluation Results

### Score Interpretation

| Score Range | Grade | Interpretation |
|-------------|-------|----------------|
| 0.9 - 1.0   | A+    | Excellent - Human-level performance |
| 0.8 - 0.9   | A     | Very Good - High-quality generation |
| 0.7 - 0.8   | B     | Good - Acceptable performance |
| 0.6 - 0.7   | C     | Fair - Needs improvement |
| 0.5 - 0.6   | D     | Poor - Significant issues |
| 0.0 - 0.5   | F     | Fail - Major problems |

### Key Metrics Explained

#### Exact Match (EM)
- **Range**: 0.0 to 1.0
- **Interpretation**: Percentage of answers that match exactly after normalization
- **Good Score**: > 0.7 for factual questions

#### F1 Score
- **Range**: 0.0 to 1.0
- **Interpretation**: Token-level overlap between generated and reference answers
- **Good Score**: > 0.8 for most question types

#### Semantic Similarity
- **Range**: 0.0 to 1.0
- **Interpretation**: Semantic closeness using sentence embeddings
- **Good Score**: > 0.7 indicates good semantic alignment

#### ROUGE Scores
- **ROUGE-1**: Unigram overlap
- **ROUGE-2**: Bigram overlap
- **ROUGE-L**: Longest common subsequence
- **Good Score**: > 0.6 for answer quality

## 🔧 Advanced Usage

### Custom Reference Data

Create custom reference data for domain-specific evaluation:

```python
custom_references = [
    {
        'question': 'What is machine learning?',
        'answer': 'Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.',
        'type': 'short_answer'
    }
]

# Evaluate against custom references
evaluator = QuestionAnswerEvaluator()
results = []
for gen_qa in generated_questions:
    best_match = evaluator._find_best_match(gen_qa, custom_references)
    if best_match:
        result = evaluator.evaluate_question_answer_pair(gen_qa, best_match)
        results.append(result)

final_results = evaluator._aggregate_results(results)
```

### Batch Evaluation

For large-scale evaluation:

```python
import json
from pathlib import Path

def batch_evaluate(questions_dir: str, output_dir: str):
    """Evaluate multiple question sets in batch."""
    evaluator = QuestionAnswerEvaluator()
    
    for question_file in Path(questions_dir).glob('*.json'):
        with open(question_file, 'r') as f:
            questions = json.load(f)
        
        results = evaluator.evaluate_french_indian_war_example(questions)
        
        # Save results
        output_file = Path(output_dir) / f"{question_file.stem}_evaluation.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate report
        report_file = Path(output_dir) / f"{question_file.stem}_report.txt"
        report = evaluator.generate_evaluation_report(results, str(report_file))

# Usage
batch_evaluate('generated_questions/', 'evaluation_results/')
```

### Command Line Interface

The evaluation system includes a CLI for direct evaluation:

```bash
# Evaluate generated questions
python app/backend/evaluation_system.py \
    --generated generated_questions.json \
    --reference squad_data.json \
    --output evaluation_report.txt

# For French-Indian War evaluation (no reference needed)
python app/backend/evaluation_system.py \
    --generated generated_questions.json \
    --output evaluation_report.txt
```

## 🎯 Best Practices

### 1. Question Format
Ensure your generated questions follow this format:
```json
{
  "question": "Clear, specific question text?",
  "answer": "Complete, accurate answer",
  "type": "short_answer|multiple_choice|essay"
}
```

### 2. Evaluation Strategy
- **Start with built-in examples** (French-Indian War) to understand the system
- **Use domain-specific references** for specialized content
- **Combine multiple metrics** for comprehensive evaluation
- **Iterate and improve** based on evaluation feedback

### 3. Performance Optimization
- **Batch processing** for large datasets
- **Caching** sentence embeddings for repeated evaluations
- **Parallel processing** for multiple question sets

### 4. Quality Assurance
- **Manual review** of low-scoring questions
- **Cross-validation** with human evaluators
- **Continuous monitoring** of evaluation trends

## 📈 Evaluation Workflow

1. **Generate Questions**: Use RAPTOR-Q to create questions from your documents
2. **Prepare Reference Data**: Either use built-in examples or prepare custom references
3. **Run Evaluation**: Use the API or Python interface to evaluate questions
4. **Analyze Results**: Review scores and identify areas for improvement
5. **Iterate**: Adjust generation parameters based on evaluation feedback
6. **Deploy**: Use high-scoring question sets in production

## 🔍 Troubleshooting

### Common Issues

#### Low Exact Match Scores
- Check for spelling variations
- Verify answer normalization
- Consider semantic similarity instead

#### Poor Semantic Similarity
- Ensure questions are contextually relevant
- Check if answers address the question properly
- Verify reference data quality

#### Missing Dependencies
```bash
pip install sentence-transformers spacy nltk rouge-score scikit-learn
python -m spacy download en_core_web_sm
```

#### Memory Issues
- Use smaller batch sizes
- Consider using lighter embedding models
- Process files sequentially instead of in parallel

## 📚 Reference Data Sources

### Built-in Examples
- **French-Indian War**: Comprehensive historical context
- **SQuAD2.0 Format**: Standard question-answering format
- **Multiple Question Types**: Short answer, multiple choice, essay

### Custom Data Creation
Create your own reference data in SQuAD2.0 format:
```json
{
  "data": [
    {
      "title": "Your Topic",
      "paragraphs": [
        {
          "context": "Your paragraph text...",
          "qas": [
            {
              "question": "Your question?",
              "answers": [
                {
                  "text": "Answer text",
                  "answer_start": 123
                }
              ],
              "is_impossible": false
            }
          ]
        }
      ]
    }
  ]
}
```

## 🚀 Next Steps

1. **Try the French-Indian War example** to understand the evaluation process
2. **Experiment with different question types** and difficulties
3. **Create custom reference data** for your specific domain
4. **Integrate evaluation into your workflow** for continuous improvement
5. **Share your results** and contribute to the evaluation framework

---

**Happy evaluating! 🎉**

For more information, see the main [README.md](README.md) or [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for setup instructions. 