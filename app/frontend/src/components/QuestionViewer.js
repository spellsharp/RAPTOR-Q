import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Eye, 
  FileText, 
  CheckCircle, 
  Download,
  Book,
  Target,
  Clock,
  Award
} from 'lucide-react';

const QuestionViewer = () => {
  const [selectedExample, setSelectedExample] = useState(null);

  const exampleQuestions = [
    {
      id: 1,
      title: "Machine Learning Fundamentals",
      subject: "Computer Science",
      difficulty: "Medium",
      totalQuestions: 15,
      totalPoints: 75,
      estimatedTime: "45 minutes",
      questions: [
        {
          id: 1,
          type: "multiple_choice",
          text: "What is the main purpose of a neural network activation function?",
          options: [
            "A) To initialize weights randomly",
            "B) To introduce non-linearity into the network",
            "C) To reduce overfitting",
            "D) To increase computational speed"
          ],
          points: 3,
          answer: "B) To introduce non-linearity into the network"
        },
        {
          id: 2,
          type: "short_answer",
          text: "Explain the difference between supervised and unsupervised learning.",
          points: 8,
          answer: "Supervised learning uses labeled training data to learn a mapping between inputs and outputs, while unsupervised learning finds patterns in data without labeled examples. Supervised learning includes classification and regression tasks, while unsupervised learning includes clustering and dimensionality reduction."
        },
        {
          id: 3,
          type: "essay",
          text: "Discuss the trade-off between bias and variance in machine learning models. How can this trade-off be managed?",
          points: 15,
          answer: "The bias-variance trade-off is a fundamental concept in machine learning. High bias leads to underfitting (model too simple), while high variance leads to overfitting (model too complex). This trade-off can be managed through techniques like cross-validation, regularization, ensemble methods, and proper feature selection. The goal is to find the optimal balance that minimizes total error."
        }
      ]
    },
    {
      id: 2,
      title: "Data Structures and Algorithms",
      subject: "Computer Science",
      difficulty: "Hard",
      totalQuestions: 12,
      totalPoints: 90,
      estimatedTime: "60 minutes",
      questions: [
        {
          id: 1,
          type: "multiple_choice",
          text: "What is the time complexity of inserting an element into a balanced binary search tree?",
          options: [
            "A) O(1)",
            "B) O(log n)",
            "C) O(n)",
            "D) O(n log n)"
          ],
          points: 4,
          answer: "B) O(log n)"
        },
        {
          id: 2,
          type: "short_answer",
          text: "Describe the key differences between depth-first search (DFS) and breadth-first search (BFS).",
          points: 10,
          answer: "DFS explores as far as possible along each branch before backtracking, using a stack (or recursion). BFS explores all vertices at the current depth before moving to the next level, using a queue. DFS has space complexity O(h) where h is the height, while BFS has space complexity O(w) where w is the maximum width. DFS is better for finding any path, while BFS is better for finding the shortest path in unweighted graphs."
        }
      ]
    },
    {
      id: 3,
      title: "Database Management Systems",
      subject: "Information Technology",
      difficulty: "Easy",
      totalQuestions: 10,
      totalPoints: 50,
      estimatedTime: "30 minutes",
      questions: [
        {
          id: 1,
          type: "multiple_choice",
          text: "What does ACID stand for in database transactions?",
          options: [
            "A) Atomicity, Consistency, Isolation, Durability",
            "B) Accuracy, Completeness, Integrity, Dependability",
            "C) Access, Control, Identity, Data",
            "D) Automatic, Continuous, Integrated, Distributed"
          ],
          points: 3,
          answer: "A) Atomicity, Consistency, Isolation, Durability"
        },
        {
          id: 2,
          type: "short_answer",
          text: "What is the purpose of database normalization?",
          points: 7,
          answer: "Database normalization is the process of organizing data to reduce redundancy and dependency. It helps eliminate data duplication, ensures data integrity, reduces storage space, and makes the database more flexible and easier to maintain. The main goal is to structure data efficiently while maintaining consistency."
        }
      ]
    }
  ];

  const handleExampleSelect = (example) => {
    setSelectedExample(example);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getQuestionTypeIcon = (type) => {
    switch (type) {
      case 'multiple_choice': return <Target className="h-4 w-4" />;
      case 'short_answer': return <FileText className="h-4 w-4" />;
      case 'essay': return <Book className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Question Paper Examples
        </h1>
        <p className="text-gray-600">
          Explore example question papers generated by VelociRAPTOR to see the quality and format
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Examples List */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="lg:col-span-1"
        >
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Example Papers
          </h2>
          <div className="space-y-4">
            {exampleQuestions.map((example) => (
              <div
                key={example.id}
                onClick={() => handleExampleSelect(example)}
                className={`bg-white rounded-lg shadow-md p-4 cursor-pointer transition-all hover:shadow-lg ${
                  selectedExample?.id === example.id ? 'ring-2 ring-indigo-500' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-800 text-sm">
                    {example.title}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(example.difficulty)}`}>
                    {example.difficulty}
                  </span>
                </div>
                <p className="text-xs text-gray-600 mb-2">{example.subject}</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{example.totalQuestions} questions</span>
                  <span>{example.totalPoints} points</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Question Preview */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="lg:col-span-2"
        >
          {selectedExample ? (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">
                    {selectedExample.title}
                  </h2>
                  <p className="text-gray-600">{selectedExample.subject}</p>
                </div>
                <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2">
                  <Download className="h-4 w-4" />
                  <span>Download PDF</span>
                </button>
              </div>

              {/* Paper Info */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <FileText className="h-5 w-5 text-indigo-600" />
                  </div>
                  <p className="text-sm text-gray-600">Questions</p>
                  <p className="font-semibold text-gray-800">{selectedExample.totalQuestions}</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <Award className="h-5 w-5 text-indigo-600" />
                  </div>
                  <p className="text-sm text-gray-600">Total Points</p>
                  <p className="font-semibold text-gray-800">{selectedExample.totalPoints}</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <Clock className="h-5 w-5 text-indigo-600" />
                  </div>
                  <p className="text-sm text-gray-600">Time</p>
                  <p className="font-semibold text-gray-800">{selectedExample.estimatedTime}</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <Target className="h-5 w-5 text-indigo-600" />
                  </div>
                  <p className="text-sm text-gray-600">Difficulty</p>
                  <p className="font-semibold text-gray-800">{selectedExample.difficulty}</p>
                </div>
              </div>

              {/* Questions */}
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                  Questions
                </h3>
                {selectedExample.questions.map((question, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-gray-800">
                        Q{question.id}. {question.text}
                      </h4>
                      <div className="flex items-center space-x-2">
                        {getQuestionTypeIcon(question.type)}
                        <span className="text-sm text-gray-500">
                          {question.points} pts
                        </span>
                      </div>
                    </div>
                    
                    {question.type === 'multiple_choice' && question.options && (
                      <div className="ml-4 space-y-2 mb-4">
                        {question.options.map((option, optIndex) => (
                          <div key={optIndex} className="flex items-center">
                            <div className="w-2 h-2 bg-gray-300 rounded-full mr-3"></div>
                            <p className="text-gray-700">{option}</p>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-center mb-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                        <span className="text-sm font-medium text-green-800">Answer</span>
                      </div>
                      <p className="text-sm text-gray-700">{question.answer}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <Eye className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Select an Example
              </h3>
              <p className="text-gray-600">
                Choose a question paper from the list to preview its contents
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default QuestionViewer; 