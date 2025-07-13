import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation } from '@tanstack/react-query'
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Download,
  Settings,
  Play
} from 'lucide-react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000'

const TestGeneration = () => {
  const [uploadedSpec, setUploadedSpec] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [testCases, setTestCases] = useState([])
  const [options, setOptions] = useState({
    useAI: false,
    includeEdgeCases: true,
    openaiApiKey: ''
  })
  const [activeTab, setActiveTab] = useState('upload')

  // File upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await axios.post(`${API_BASE_URL}/upload`, formData)
      return response.data
    },
    onSuccess: (data) => {
      setUploadedSpec(data)
      setSessionId(data.session_id)
      setActiveTab('configure')
    }
  })

  // Text upload mutation
  const uploadTextMutation = useMutation({
    mutationFn: async ({ content, type }) => {
      const response = await axios.post(`${API_BASE_URL}/upload_text`, {
        content,
        type
      })
      return response.data
    },
    onSuccess: (data) => {
      setUploadedSpec(data)
      setSessionId(data.session_id)
      setActiveTab('configure')
    }
  })

  // Test generation mutation
  const generateMutation = useMutation({
    mutationFn: async () => {
      const params = new URLSearchParams({
        use_ai: options.useAI,
        include_edge_cases: options.includeEdgeCases,
        openai_api_key: options.openaiApiKey
      })
      const response = await axios.get(`${API_BASE_URL}/generate/${sessionId}?${params}`)
      return response.data
    },
    onSuccess: (data) => {
      setTestCases(data.test_cases)
      setActiveTab('results')
    }
  })

  // Export function
  const exportTestCases = async (format) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/export/${sessionId}/${format}`, {
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `api_test_cases.${format === 'shell' ? 'sh' : format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  // Dropzone for file upload
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      uploadMutation.mutate(acceptedFiles[0])
    }
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'text/yaml': ['.yaml', '.yml'],
      'text/plain': ['.txt']
    },
    maxFiles: 1
  })

  const [textInput, setTextInput] = useState('')
  const [textFormat, setTextFormat] = useState('json')

  const handleTextUpload = () => {
    if (textInput.trim()) {
      uploadTextMutation.mutate({
        content: textInput,
        type: textFormat
      })
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          API Test Generation
        </h1>
        <p className="text-gray-600">
          Upload your OpenAPI specification and generate comprehensive test cases
        </p>
      </div>

      {/* Progress Tabs */}
      <div className="flex mb-8 border-b border-gray-200">
        <button
          className={`px-6 py-3 font-medium border-b-2 transition-colors ${
            activeTab === 'upload' 
              ? 'border-indigo-600 text-indigo-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('upload')}
        >
          <Upload className="h-4 w-4 inline mr-2" />
          Upload Spec
        </button>
        <button
          className={`px-6 py-3 font-medium border-b-2 transition-colors ${
            activeTab === 'configure' 
              ? 'border-indigo-600 text-indigo-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
          disabled={!uploadedSpec}
        >
          <Settings className="h-4 w-4 inline mr-2" />
          Configure
        </button>
        <button
          className={`px-6 py-3 font-medium border-b-2 transition-colors ${
            activeTab === 'results' 
              ? 'border-indigo-600 text-indigo-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
          disabled={testCases.length === 0}
        >
          <FileText className="h-4 w-4 inline mr-2" />
          Results
        </button>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div className="space-y-8">
          {/* File Upload */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Upload OpenAPI Specification
            </h2>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive 
                  ? 'border-indigo-400 bg-indigo-50' 
                  : 'border-gray-300 hover:border-indigo-400 hover:bg-gray-50'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              {isDragActive ? (
                <p className="text-indigo-600 font-medium">Drop the file here...</p>
              ) : (
                <div>
                  <p className="text-gray-600 font-medium mb-2">
                    Click to select file or drag and drop
                  </p>
                  <p className="text-gray-500 text-sm">
                    Supports JSON and YAML files (OpenAPI 2.x & 3.x)
                  </p>
                </div>
              )}
            </div>
            
            {uploadMutation.isLoading && (
              <div className="mt-4 flex items-center text-indigo-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600 mr-2"></div>
                Uploading and validating...
              </div>
            )}
            
            {uploadMutation.isError && (
              <div className="mt-4 flex items-center text-red-600">
                <AlertCircle className="h-4 w-4 mr-2" />
                {uploadMutation.error?.response?.data?.error || 'Upload failed'}
              </div>
            )}
          </div>

          {/* Text Input */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Or Paste Specification
            </h2>
            <div className="space-y-4">
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="json"
                    checked={textFormat === 'json'}
                    onChange={(e) => setTextFormat(e.target.value)}
                    className="mr-2"
                  />
                  JSON
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="yaml"
                    checked={textFormat === 'yaml'}
                    onChange={(e) => setTextFormat(e.target.value)}
                    className="mr-2"
                  />
                  YAML
                </label>
              </div>
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste your OpenAPI specification here..."
                className="w-full h-64 p-4 border border-gray-300 rounded-lg font-mono text-sm"
              />
              <button
                onClick={handleTextUpload}
                disabled={!textInput.trim() || uploadTextMutation.isLoading}
                className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploadTextMutation.isLoading ? 'Processing...' : 'Upload Specification'}
              </button>
            </div>
            
            {uploadTextMutation.isError && (
              <div className="mt-4 flex items-center text-red-600">
                <AlertCircle className="h-4 w-4 mr-2" />
                {uploadTextMutation.error?.response?.data?.error || 'Processing failed'}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Configure Tab */}
      {activeTab === 'configure' && uploadedSpec && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Specification Details
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">API Title</p>
                <p className="font-medium">{uploadedSpec.spec_info?.title || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Version</p>
                <p className="font-medium">{uploadedSpec.spec_info?.version || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Endpoints Found</p>
                <p className="font-medium">{uploadedSpec.endpoints_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">OpenAPI Version</p>
                <p className="font-medium">{uploadedSpec.spec_info?.openapi_version || 'N/A'}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Generation Options
            </h2>
            <div className="space-y-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={options.includeEdgeCases}
                  onChange={(e) => setOptions(prev => ({ ...prev, includeEdgeCases: e.target.checked }))}
                  className="mr-3"
                />
                <span className="font-medium">Include Edge Cases</span>
                <span className="ml-2 text-sm text-gray-600">
                  (Security tests, boundary values, invalid inputs)
                </span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={options.useAI}
                  onChange={(e) => setOptions(prev => ({ ...prev, useAI: e.target.checked }))}
                  className="mr-3"
                />
                <span className="font-medium">Enable AI Enhancement</span>
                <span className="ml-2 text-sm text-gray-600">
                  (Requires OpenAI API key)
                </span>
              </label>
              
              {options.useAI && (
                <div className="ml-6">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={options.openaiApiKey}
                    onChange={(e) => setOptions(prev => ({ ...prev, openaiApiKey: e.target.value }))}
                    placeholder="sk-..."
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  />
                </div>
              )}
            </div>
            
            <button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isLoading}
              className="mt-6 bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Play className="h-4 w-4" />
              <span>{generateMutation.isLoading ? 'Generating...' : 'Generate Test Cases'}</span>
            </button>
            
            {generateMutation.isError && (
              <div className="mt-4 flex items-center text-red-600">
                <AlertCircle className="h-4 w-4 mr-2" />
                {generateMutation.error?.response?.data?.error || 'Generation failed'}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && testCases.length > 0 && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Generated Test Cases ({testCases.length})
              </h2>
              <div className="flex space-x-2">
                {['csv', 'json', 'python', 'shell', 'postman', 'html'].map((format) => (
                  <button
                    key={format}
                    onClick={() => exportTestCases(format)}
                    className="bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-200 flex items-center space-x-1"
                  >
                    <Download className="h-3 w-3" />
                    <span>{format.toUpperCase()}</span>
                  </button>
                ))}
              </div>
            </div>
            
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {testCases.map((testCase, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium text-gray-900">{testCase.id}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      testCase.test_type === 'basic' ? 'bg-blue-100 text-blue-800' :
                      testCase.test_type === 'edge_case' ? 'bg-red-100 text-red-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {testCase.test_type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{testCase.description}</p>
                  <div className="bg-gray-50 rounded p-2 text-xs font-mono">
                    {testCase.method} {testCase.endpoint}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TestGeneration