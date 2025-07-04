import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileText, Home, Eye, Zap } from 'lucide-react';

const Header = () => {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <header className="bg-white shadow-lg border-b-2 border-indigo-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="h-8 w-8 text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-800">
              RAPTOR-Q
            </h1>
            <span className="text-sm text-gray-500 bg-indigo-100 px-2 py-1 rounded-full">
              Question Generator
            </span>
          </div>
          
          <nav className="flex space-x-6">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                isActive('/') 
                  ? 'bg-indigo-600 text-white' 
                  : 'text-gray-700 hover:bg-indigo-100'
              }`}
            >
              <Home className="h-4 w-4" />
              <span>Home</span>
            </Link>
            
            <Link
              to="/generate"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                isActive('/generate') 
                  ? 'bg-indigo-600 text-white' 
                  : 'text-gray-700 hover:bg-indigo-100'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Generate</span>
            </Link>
            
            <Link
              to="/view"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                isActive('/view') 
                  ? 'bg-indigo-600 text-white' 
                  : 'text-gray-700 hover:bg-indigo-100'
              }`}
            >
              <Eye className="h-4 w-4" />
              <span>View</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header; 