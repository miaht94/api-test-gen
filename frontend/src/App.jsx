import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import HomePage from './components/HomePage'
import TestGeneration from './components/TestGeneration'
import DocumentUpload from './components/DocumentUpload'
import ChatInterface from './components/ChatInterface'
import Navbar from './components/Navbar'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/test-generation" element={<TestGeneration />} />
              <Route path="/documents" element={<DocumentUpload />} />
              <Route path="/chat" element={<ChatInterface />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App
