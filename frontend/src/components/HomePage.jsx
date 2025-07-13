import { Link } from 'react-router-dom'
import { 
  Upload, 
  FileText, 
  MessageSquare, 
  Zap, 
  CheckCircle, 
  ArrowRight 
} from 'lucide-react'

const HomePage = () => {
  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="flex justify-center items-center mb-6">
          <Zap className="h-16 w-16 text-indigo-600" />
        </div>
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          APITestGen
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Generate comprehensive API test cases from OpenAPI/Swagger specifications automatically. 
          Now with AI-powered contextual testing using your business documents and source code.
        </p>
        <div className="flex justify-center space-x-4">
          <Link
            to="/test-generation"
            className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center space-x-2"
          >
            <FileText className="h-5 w-5" />
            <span>Generate API Tests</span>
          </Link>
          <Link
            to="/chat"
            className="bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors flex items-center space-x-2"
          >
            <MessageSquare className="h-5 w-5" />
            <span>AI Chat Assistant</span>
          </Link>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <FileText className="h-8 w-8 text-indigo-600 mr-3" />
            <h3 className="text-xl font-semibold text-gray-900">OpenAPI Import</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Support for OpenAPI 2.x & 3.x specifications in JSON and YAML formats. 
            Drag-and-drop or paste your API specs directly.
          </p>
          <ul className="space-y-2">
            <li className="flex items-center text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Real-time validation
            </li>
            <li className="flex items-center text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Multiple formats supported
            </li>
            <li className="flex items-center text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Instant endpoint extraction
            </li>
          </ul>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <Upload className="h-8 w-8 text-purple-600 mr-3" />
            <h3 className="text-xl font-semibold text-gray-900">Document RAG</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Upload business documents and source code to create a knowledge base. 
            AI will use this context to generate more relevant test cases.
          </p>
          <ul className="space-y-2">
            <li className="flex items-center text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Vector database storage
            </li>
            <li className="flex items-center text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Contextual retrieval
            </li>
            <li className="flex items-center text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Business logic aware
            </li>
          </ul>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <MessageSquare className="h-8 w-8 text-green-600 mr-3" />
            <h3 className="text-xl font-semibold text-gray-900">AI Chat</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Chat with AI to generate custom test cases based on your specific use cases, 
            business requirements, and uploaded documentation.
          </p>
          <ul className="space-y-2">
            <li className="flex items-center text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Natural language queries
            </li>
            <li className="flex items-center text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Context-aware responses
            </li>
            <li className="flex items-center text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Iterative refinement
            </li>
          </ul>
        </div>
      </div>

      {/* Workflow Section */}
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200 mb-16">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
          How It Works
        </h2>
        <div className="grid md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Upload className="h-8 w-8 text-indigo-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Upload</h3>
            <p className="text-gray-600 text-sm">
              Upload your OpenAPI spec and business documents
            </p>
          </div>
          <div className="text-center">
            <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Zap className="h-8 w-8 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">2. Process</h3>
            <p className="text-gray-600 text-sm">
              AI processes and indexes your content for retrieval
            </p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">3. Chat</h3>
            <p className="text-gray-600 text-sm">
              Describe your testing needs in natural language
            </p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <FileText className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">4. Generate</h3>
            <p className="text-gray-600 text-sm">
              Get contextual test cases in multiple formats
            </p>
          </div>
        </div>
      </div>

      {/* Quick Start */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">
          Ready to Get Started?
        </h2>
        <p className="text-lg text-gray-600 mb-8">
          Choose your workflow: Traditional OpenAPI import or AI-powered contextual testing
        </p>
        <div className="flex justify-center space-x-4">
          <Link
            to="/test-generation"
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center space-x-2"
          >
            <span>Quick Generation</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            to="/documents"
            className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors flex items-center space-x-2"
          >
            <span>Upload Documents</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  )
}

export default HomePage