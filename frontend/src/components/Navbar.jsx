import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  FileText, 
  Upload, 
  MessageSquare, 
  Zap 
} from 'lucide-react'

const Navbar = () => {
  const location = useLocation()
  
  const isActive = (path) => location.pathname === path

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <Zap className="h-8 w-8 text-indigo-600" />
            <h1 className="text-xl font-bold text-gray-900">APITestGen</h1>
          </div>
          
          <div className="flex space-x-8">
            <Link
              to="/"
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/') 
                  ? 'text-indigo-600 bg-indigo-50' 
                  : 'text-gray-600 hover:text-indigo-600 hover:bg-gray-50'
              }`}
            >
              <Home className="h-4 w-4" />
              <span>Home</span>
            </Link>
            
            <Link
              to="/test-generation"
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/test-generation') 
                  ? 'text-indigo-600 bg-indigo-50' 
                  : 'text-gray-600 hover:text-indigo-600 hover:bg-gray-50'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>API Tests</span>
            </Link>
            
            <Link
              to="/documents"
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/documents') 
                  ? 'text-indigo-600 bg-indigo-50' 
                  : 'text-gray-600 hover:text-indigo-600 hover:bg-gray-50'
              }`}
            >
              <Upload className="h-4 w-4" />
              <span>Documents</span>
            </Link>
            
            <Link
              to="/chat"
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/chat') 
                  ? 'text-indigo-600 bg-indigo-50' 
                  : 'text-gray-600 hover:text-indigo-600 hover:bg-gray-50'
              }`}
            >
              <MessageSquare className="h-4 w-4" />
              <span>AI Chat</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar