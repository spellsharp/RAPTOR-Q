import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Brain, 
  Download, 
  Upload, 
  Settings, 
  CheckCircle,
  Zap,
  BookOpen,
  Target
} from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: <Upload className="h-8 w-8 text-indigo-600" />,
      title: 'Upload Documents',
      description: 'Support for PDF, DOC, DOCX, and TXT files'
    },
    {
      icon: <Brain className="h-8 w-8 text-indigo-600" />,
      title: 'AI-Powered Generation',
      description: 'Uses RAPTOR-Q\'s advanced RAG capabilities'
    },
    {
      icon: <Settings className="h-8 w-8 text-indigo-600" />,
      title: 'Customizable Options',
      description: 'Choose question types, difficulty, and count'
    },
    {
      icon: <CheckCircle className="h-8 w-8 text-indigo-600" />,
      title: 'Answer Keys',
      description: 'Automatic generation of comprehensive answer keys'
    },
    {
      icon: <Download className="h-8 w-8 text-indigo-600" />,
      title: 'PDF Export',
      description: 'Professional PDF format for questions and answers'
    },
    {
      icon: <Target className="h-8 w-8 text-indigo-600" />,
      title: 'Multiple Formats',
      description: 'Multiple choice, short answer, and essay questions'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.3,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <motion.div 
        className="text-center mb-16"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="flex items-center justify-center mb-6">
          <Zap className="h-16 w-16 text-indigo-600 mr-4" />
          <div className="text-left">
            <h1 className="text-5xl font-bold text-gray-800 mb-2">
              RAPTOR-Q
            </h1>
            <p className="text-xl text-indigo-600 font-semibold">
              Question Paper Generator
            </p>
          </div>
        </div>
        
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Transform your documents into comprehensive question papers with intelligent
          AI-powered generation. Upload any document and get professional question papers
          with detailed answer keys in minutes.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/generate"
            className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center space-x-2"
          >
            <FileText className="h-5 w-5" />
            <span>Start Generating</span>
          </Link>
          
          <Link
            to="/view"
            className="bg-white text-indigo-600 px-8 py-3 rounded-lg font-semibold border-2 border-indigo-600 hover:bg-indigo-50 transition-colors flex items-center space-x-2"
          >
            <BookOpen className="h-5 w-5" />
            <span>View Examples</span>
          </Link>
        </div>
      </motion.div>

      {/* Features Section */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="mb-16"
      >
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">
          Powerful Features
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center mb-4">
                {feature.icon}
                <h3 className="text-xl font-semibold text-gray-800 ml-3">
                  {feature.title}
                </h3>
              </div>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* How It Works Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="bg-white rounded-lg shadow-lg p-8"
      >
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
          How It Works
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="bg-indigo-100 rounded-full p-4 w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-indigo-600">1</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              Upload Document
            </h3>
            <p className="text-gray-600">
              Upload your PDF, DOC, or TXT file
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-indigo-100 rounded-full p-4 w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-indigo-600">2</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              Configure Options
            </h3>
            <p className="text-gray-600">
              Set question count, difficulty, and types
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-indigo-100 rounded-full p-4 w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-indigo-600">3</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              AI Generation
            </h3>
            <p className="text-gray-600">
              RAPTOR-Q processes and generates questions
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-indigo-100 rounded-full p-4 w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-indigo-600">4</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              Download Results
            </h3>
            <p className="text-gray-600">
              Get your question paper and answer key
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Home; 