import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import axios from 'axios';
import {
  Upload,
  FileText,
  Settings,
  Play,
  Download,
  CheckCircle,
  X,
  Loader
} from 'lucide-react';

const QuestionGenerator = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [fileId, setFileId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState(null);
  const [generatedAnswers, setGeneratedAnswers] = useState(null);
  const [config, setConfig] = useState({
    numQuestions: 10,
    difficulty: 'easy',
    questionTypes: ['short_answer']
  });

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadedFile(file);
      setFileId(response.data.file_id);
      toast.success('File uploaded successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.error || 'Failed to upload file');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    maxSize: 16 * 1024 * 1024 // 16MB
  });

  const handleGenerateQuestions = async () => {
    if (!fileId) {
      toast.error('Please upload a file first');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await axios.post('/api/generate-questions', {
        file_id: fileId,
        num_questions: config.numQuestions,
        difficulty: config.difficulty,
        question_types: config.questionTypes
      });

      setGeneratedQuestions(response.data.questions);
      setGeneratedAnswers(response.data.answer_key);
      toast.success('Questions generated successfully!');
    } catch (error) {
      console.error('Generation error:', error);
      toast.error(error.response?.data?.error || 'Failed to generate questions');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!generatedQuestions || !generatedAnswers) {
      toast.error('No questions to download');
      return;
    }

    try {
      const response = await axios.post('/api/export-pdf', {
        questions: generatedQuestions,
        answer_key: generatedAnswers
      }, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `question_paper_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('PDF downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download PDF');
    }
  };

  const handleConfigChange = (key, value) => {
    setConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleQuestionTypeChange = (type) => {
    setConfig(prev => ({
      ...prev,
      questionTypes: [type]  // Only allow one selection for radio buttons
    }));
  };

  const removeFile = () => {
    setUploadedFile(null);
    setFileId(null);
    setGeneratedQuestions(null);
    setGeneratedAnswers(null);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Generate Question Papers
        </h1>
        <p className="text-gray-600">
          Upload a document and configure your preferences to generate intelligent question papers
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* File Upload Section */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
            <Upload className="h-5 w-5 mr-2" />
            Upload Document
          </h2>

          {!uploadedFile ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-gray-300 hover:border-indigo-400'
              }`}
            >
              <input {...getInputProps()} />
              {isUploading ? (
                <div className="flex flex-col items-center">
                  <Loader className="h-12 w-12 text-indigo-600 animate-spin mb-4" />
                  <p className="text-gray-600">Uploading...</p>
                </div>
              ) : (
                <div className="flex flex-col items-center">
                  <FileText className="h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-gray-600 mb-2">
                    {isDragActive
                      ? 'Drop the file here...'
                      : 'Drag and drop your document here, or click to select'}
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports PDF, DOC, DOCX, TXT (max 16MB)
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      {uploadedFile.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={removeFile}
                  className="text-red-500 hover:text-red-700 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </motion.div>

        {/* Configuration Section */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Configuration
          </h2>

          <div className="space-y-6">
            {/* Number of Questions */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Questions
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={config.numQuestions}
                onChange={(e) => handleConfigChange('numQuestions', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Difficulty Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Level
              </label>
              <select
                value={config.difficulty}
                onChange={(e) => handleConfigChange('difficulty', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            {/* Question Types */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Question Types
              </label>
              <div className="space-y-2">
                {[
                  { value: 'multiple_choice', label: 'Multiple Choice' },
                  { value: 'short_answer', label: 'Short Answer' },
                  { value: 'essay', label: 'Essay' }
                ].map(type => (
                  <label key={type.value} className="flex items-center">
                    <input
                      type="radio"
                      name="questionType"
                      value={type.value}
                      checked={config.questionTypes.includes(type.value)}
                      onChange={() => handleQuestionTypeChange(type.value)}
                      className="mr-2 h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="text-sm text-gray-700">{type.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Generate Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="mt-8 text-center"
      >
        <button
          onClick={handleGenerateQuestions}
          disabled={!fileId || isGenerating}
          className={`px-8 py-3 rounded-lg font-semibold flex items-center space-x-2 mx-auto transition-colors ${
            !fileId || isGenerating
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          }`}
        >
          {isGenerating ? (
            <>
              <Loader className="h-5 w-5 animate-spin" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Play className="h-5 w-5" />
              <span>Generate Questions</span>
            </>
          )}
        </button>

      </motion.div>

      {/* Results Section */}
      {generatedQuestions && generatedAnswers && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mt-8 bg-white rounded-lg shadow-lg p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-800">
              Generated Questions
            </h2>
            <button
              onClick={handleDownloadPDF}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Download PDF</span>
            </button>
          </div>

          <div className="space-y-4">
            {generatedQuestions.map((question, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-medium text-gray-800 mb-2">
                  Q{question.id}. {question.text} ({question.points} points)
                </h3>
                {question.type === 'multiple_choice' && question.options && (
                  <div className="ml-4 space-y-1">
                    {question.options.map((option, optIndex) => (
                      <p key={optIndex} className="text-gray-600">
                        {option}
                      </p>
                    ))}
                  </div>
                )}
                <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                  <strong>Answer:</strong> {generatedAnswers[index]?.answer}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default QuestionGenerator; 