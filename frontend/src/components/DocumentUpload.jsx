import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQuery } from '@tanstack/react-query'
import { 
  Upload, 
  FileText, 
  Code, 
  Database, 
  CheckCircle, 
  AlertCircle, 
  Trash2,
  File
} from 'lucide-react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000'

const DocumentUpload = () => {
  const [uploadedDocuments, setUploadedDocuments] = useState([])
  const [uploadType, setUploadType] = useState('document') // 'document' or 'code'

  // Get uploaded documents
  const { data: documents, refetch } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/documents`)
      return response.data
    },
    initialData: []
  })

  // File upload mutation
  const uploadMutation = useMutation({
    mutationFn: async ({ files, type }) => {
      const formData = new FormData()
      files.forEach((file, index) => {
        formData.append(`file_${index}`, file)
      })
      formData.append('type', type)
      
      const response = await axios.post(`${API_BASE_URL}/api/upload-documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    },
    onSuccess: (data) => {
      setUploadedDocuments(prev => [...prev, ...data.documents])
      refetch()
    }
  })

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: async (documentId) => {
      await axios.delete(`${API_BASE_URL}/api/documents/${documentId}`)
    },
    onSuccess: () => {
      refetch()
    }
  })

  // Process documents (embed into vector database)
  const processMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`${API_BASE_URL}/api/process-documents`)
      return response.data
    }
  })

  // Dropzone for file upload
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      uploadMutation.mutate({ files: acceptedFiles, type: uploadType })
    }
  }, [uploadMutation, uploadType])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: uploadType === 'document' ? {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/json': ['.json']
    } : {
      'text/javascript': ['.js'],
      'text/x-typescript': ['.ts'],
      'text/x-python': ['.py'],
      'text/x-java': ['.java'],
      'text/x-c': ['.c'],
      'text/x-csharp': ['.cs'],
      'text/plain': ['.txt', '.md', '.readme'],
      'application/json': ['.json']
    },
    multiple: true
  })

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase()
    if (['js', 'ts', 'py', 'java', 'c', 'cs'].includes(ext)) {
      return <Code className="h-8 w-8 text-blue-600" />
    }
    return <FileText className="h-8 w-8 text-green-600" />
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Document & Code Upload
        </h1>
        <p className="text-gray-600">
          Upload business documents and source code to create a knowledge base for AI-powered test generation
        </p>
      </div>

      {/* Upload Type Selection */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Upload Type
        </h2>
        <div className="flex space-x-4">
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              value="document"
              checked={uploadType === 'document'}
              onChange={(e) => setUploadType(e.target.value)}
              className="mr-3"
            />
            <FileText className="h-5 w-5 text-green-600 mr-2" />
            <span className="font-medium">Business Documents</span>
            <span className="ml-2 text-sm text-gray-600">
              (PDF, Word, Markdown, Text files)
            </span>
          </label>
          
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              value="code"
              checked={uploadType === 'code'}
              onChange={(e) => setUploadType(e.target.value)}
              className="mr-3"
            />
            <Code className="h-5 w-5 text-blue-600 mr-2" />
            <span className="font-medium">Source Code</span>
            <span className="ml-2 text-sm text-gray-600">
              (JS, TS, Python, Java, C#, etc.)
            </span>
          </label>
        </div>
      </div>

      {/* File Upload Area */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Upload {uploadType === 'document' ? 'Documents' : 'Code Files'}
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
          {uploadType === 'document' ? (
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          ) : (
            <Code className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          )}
          
          {isDragActive ? (
            <p className="text-indigo-600 font-medium">Drop the files here...</p>
          ) : (
            <div>
              <p className="text-gray-600 font-medium mb-2">
                Click to select files or drag and drop
              </p>
              <p className="text-gray-500 text-sm">
                {uploadType === 'document' 
                  ? 'Support: PDF, DOC, DOCX, TXT, MD, JSON'
                  : 'Support: JS, TS, PY, JAVA, C, CS, TXT, MD, JSON'
                }
              </p>
              <p className="text-gray-500 text-xs mt-1">
                Multiple files supported
              </p>
            </div>
          )}
        </div>
        
        {uploadMutation.isLoading && (
          <div className="mt-4 flex items-center text-indigo-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600 mr-2"></div>
            Uploading files...
          </div>
        )}
        
        {uploadMutation.isError && (
          <div className="mt-4 flex items-center text-red-600">
            <AlertCircle className="h-4 w-4 mr-2" />
            {uploadMutation.error?.response?.data?.error || 'Upload failed'}
          </div>
        )}
        
        {uploadMutation.isSuccess && (
          <div className="mt-4 flex items-center text-green-600">
            <CheckCircle className="h-4 w-4 mr-2" />
            Files uploaded successfully!
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Uploaded Files ({documents?.length || 0})
          </h2>
          {documents?.length > 0 && (
            <button
              onClick={() => processMutation.mutate()}
              disabled={processMutation.isLoading}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Database className="h-4 w-4" />
              <span>{processMutation.isLoading ? 'Processing...' : 'Process into Vector DB'}</span>
            </button>
          )}
        </div>
        
        {processMutation.isSuccess && (
          <div className="mb-4 flex items-center text-green-600">
            <CheckCircle className="h-4 w-4 mr-2" />
            Documents processed and indexed successfully!
          </div>
        )}
        
        {processMutation.isError && (
          <div className="mb-4 flex items-center text-red-600">
            <AlertCircle className="h-4 w-4 mr-2" />
            Processing failed: {processMutation.error?.response?.data?.error || 'Unknown error'}
          </div>
        )}
        
        {documents?.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <File className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>No files uploaded yet</p>
            <p className="text-sm">Upload documents or code files to get started</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {documents.map((doc, index) => (
              <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  {getFileIcon(doc.name)}
                  <div>
                    <p className="font-medium text-gray-900">{doc.name}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>{formatFileSize(doc.size)}</span>
                      <span>{doc.type}</span>
                      <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {doc.processed && (
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                      Processed
                    </span>
                  )}
                  <button
                    onClick={() => deleteMutation.mutate(doc.id)}
                    disabled={deleteMutation.isLoading}
                    className="text-red-600 hover:text-red-800 p-1"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* RAG Status */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Vector Database Status
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <Database className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="font-medium text-gray-900">Total Documents</p>
            <p className="text-2xl font-bold text-blue-600">{documents?.length || 0}</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <p className="font-medium text-gray-900">Processed</p>
            <p className="text-2xl font-bold text-green-600">
              {documents?.filter(d => d.processed).length || 0}
            </p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <Code className="h-8 w-8 text-purple-600 mx-auto mb-2" />
            <p className="font-medium text-gray-900">Ready for AI</p>
            <p className="text-2xl font-bold text-purple-600">
              {documents?.filter(d => d.processed).length > 0 ? 'Yes' : 'No'}
            </p>
          </div>
        </div>
        
        {documents?.filter(d => d.processed).length > 0 && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 font-medium">
              ✨ Your knowledge base is ready! You can now use the AI Chat to generate contextual test cases.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentUpload