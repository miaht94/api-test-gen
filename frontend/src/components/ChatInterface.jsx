import { useState, useRef, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { 
  Send, 
  Bot, 
  User, 
  Download, 
  AlertCircle, 
  MessageSquare,
  FileText,
  Lightbulb,
  Zap
} from 'lucide-react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000'

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hi! I'm your AI assistant for API test generation. I can help you create test cases based on your uploaded documents and business requirements. What would you like to test?",
      timestamp: new Date()
    }
  ])
  const [currentMessage, setCurrentMessage] = useState('')
  const [generatedTests, setGeneratedTests] = useState([])
  const messagesEndRef = useRef(null)

  // Check if documents are available
  const { data: hasDocuments } = useQuery({
    queryKey: ['has-documents'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/documents/status`)
      return response.data
    }
  })

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (message) => {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message,
        context: 'test_generation'
      })
      return response.data
    },
    onSuccess: (data) => {
      // Add bot response
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: data.response,
        timestamp: new Date(),
        testCases: data.test_cases
      }])
      
      if (data.test_cases && data.test_cases.length > 0) {
        setGeneratedTests(prev => [...prev, ...data.test_cases])
      }
    },
    onError: (error) => {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: "I'm sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
        error: true
      }])
    }
  })

  const handleSendMessage = () => {
    if (!currentMessage.trim()) return
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    sendMessageMutation.mutate(currentMessage)
    setCurrentMessage('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const exportTestCases = async (testCases, format) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/export-chat-tests`, {
        test_cases: testCases,
        format
      }, {
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `chat_test_cases.${format === 'shell' ? 'sh' : format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const suggestionPrompts = [
    "Generate test cases for user authentication endpoints",
    "Create boundary tests for payment processing API",
    "Generate security tests for file upload functionality", 
    "Create performance tests for search endpoints",
    "Generate edge cases for user profile management",
    "Create integration tests for payment workflows"
  ]

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          AI Chat Assistant
        </h1>
        <p className="text-gray-600">
          Chat with AI to generate contextual test cases based on your business requirements and uploaded documents
        </p>
      </div>

      {/* Status Banner */}
      {hasDocuments && !hasDocuments.has_processed_documents && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-orange-600 mr-2" />
            <p className="text-orange-800">
              <span className="font-medium">No processed documents found.</span> 
              {' '}Upload and process documents first to get contextual test generation.
            </p>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 h-[600px] flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <Bot className="h-6 w-6 text-indigo-600" />
                <h2 className="text-lg font-semibold text-gray-900">AI Test Generator</h2>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                  Online
                </span>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${
                    message.type === 'user' 
                      ? 'bg-indigo-600 text-white' 
                      : message.error 
                      ? 'bg-red-50 text-red-800 border border-red-200'
                      : 'bg-gray-100 text-gray-900'
                  } rounded-lg p-3`}>
                    <div className="flex items-start space-x-2">
                      {message.type === 'bot' && <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />}
                      {message.type === 'user' && <User className="h-4 w-4 mt-0.5 flex-shrink-0" />}
                      <div className="flex-1">
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        
                        {/* Test Cases Display */}
                        {message.testCases && message.testCases.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-gray-300">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium">Generated {message.testCases.length} test cases</span>
                              <div className="flex space-x-1">
                                {['json', 'python', 'shell'].map((format) => (
                                  <button
                                    key={format}
                                    onClick={() => exportTestCases(message.testCases, format)}
                                    className="bg-white text-gray-700 px-2 py-1 rounded text-xs hover:bg-gray-50 flex items-center space-x-1"
                                  >
                                    <Download className="h-3 w-3" />
                                    <span>{format.toUpperCase()}</span>
                                  </button>
                                ))}
                              </div>
                            </div>
                            <div className="space-y-1 max-h-32 overflow-y-auto">
                              {message.testCases.slice(0, 3).map((testCase, index) => (
                                <div key={index} className="bg-white rounded p-2 text-xs">
                                  <div className="font-medium text-gray-900">{testCase.id}</div>
                                  <div className="text-gray-600">{testCase.method} {testCase.endpoint}</div>
                                </div>
                              ))}
                              {message.testCases.length > 3 && (
                                <div className="text-xs text-gray-600 text-center">
                                  +{message.testCases.length - 3} more test cases
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                        
                        <p className="text-xs opacity-75 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {sendMessageMutation.isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-900 rounded-lg p-3 max-w-xs">
                    <div className="flex items-center space-x-2">
                      <Bot className="h-4 w-4" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Describe what you want to test..."
                  className="flex-1 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows="2"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!currentMessage.trim() || sendMessageMutation.isLoading}
                  className="bg-indigo-600 text-white p-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Suggestions */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              <Lightbulb className="h-5 w-5 inline mr-2 text-yellow-500" />
              Quick Suggestions
            </h3>
            <div className="space-y-2">
              {suggestionPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentMessage(prompt)}
                  className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Generated Tests Summary */}
          {generatedTests.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                <FileText className="h-5 w-5 inline mr-2 text-green-500" />
                Session Summary
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Test Cases</span>
                  <span className="font-semibold text-gray-900">{generatedTests.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Unique Endpoints</span>
                  <span className="font-semibold text-gray-900">
                    {new Set(generatedTests.map(t => t.endpoint)).size}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">HTTP Methods</span>
                  <span className="font-semibold text-gray-900">
                    {new Set(generatedTests.map(t => t.method)).size}
                  </span>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600 mb-2">Export all generated tests:</p>
                <div className="flex space-x-2">
                  {['json', 'python', 'shell'].map((format) => (
                    <button
                      key={format}
                      onClick={() => exportTestCases(generatedTests, format)}
                      className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs hover:bg-gray-200 flex items-center space-x-1"
                    >
                      <Download className="h-3 w-3" />
                      <span>{format.toUpperCase()}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tips */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              <Zap className="h-5 w-5 inline mr-2 text-indigo-500" />
              Tips for Better Results
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Be specific about the API endpoints you want to test</li>
              <li>• Mention business rules and edge cases</li>
              <li>• Include authentication requirements</li>
              <li>• Specify data validation rules</li>
              <li>• Upload relevant business documents for context</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface