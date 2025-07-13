# 🚀 APITestGen Development Setup Guide

This guide will help you set up the complete APITestGen development environment with both the React frontend and Python backend.

## 📋 Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/miaht94/api-test-gen.git
cd api-test-gen
```

### 2. One-Command Setup
```bash
chmod +x start-dev.sh
./start-dev.sh
```

This script will:
- Install Python dependencies
- Install frontend dependencies  
- Start the Flask backend (port 5000)
- Start the React frontend (port 3000)

### 3. Access the Application
- **React Frontend**: http://localhost:3000
- **Flask API**: http://localhost:5000

## 🔧 Manual Setup

If you prefer to set up manually:

### Backend (Python)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Flask server
python -m src.app
```

### Frontend (React)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🌟 Features Overview

### 🎯 Traditional OpenAPI Testing
1. Upload OpenAPI/Swagger files via drag-and-drop
2. Generate comprehensive test cases automatically
3. Export in multiple formats (JSON, Python, Shell, Postman, etc.)

### 🧠 NEW: RAG-Powered Context Testing
1. **Upload Documents**: Business docs, requirements, source code
2. **Process into Vector DB**: Automatic embedding and indexing
3. **AI Chat Interface**: Natural language test generation
4. **Context-Aware Tests**: Tests that understand your business logic

## 📁 Project Structure

```
api-test-gen/
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── App.jsx           # Main app component
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Frontend dependencies
│   └── vite.config.js        # Vite configuration
├── src/                       # Python backend
│   ├── app.py                # Flask application
│   ├── rag/                  # RAG functionality
│   │   ├── __init__.py       # Vector DB and document storage
│   │   └── chat.py           # AI chat interface
│   ├── openapi_parser.py     # OpenAPI parsing
│   ├── test_generator.py     # Test generation
│   └── exporters.py          # Export functionality
├── requirements.txt          # Python dependencies
├── start-dev.sh             # Development startup script
└── README.md                # Main documentation
```

## 🔑 Environment Variables

### Required for AI Features
```bash
# OpenAI API key for AI-enhanced generation
export OPENAI_API_KEY="sk-your-openai-key-here"
```

### Optional
```bash
# Flask secret key (for production)
export SECRET_KEY="your-secret-key"
```

## 📦 Dependencies

### Python (Backend)
- **Flask**: Web framework
- **OpenAI**: AI integration
- **ChromaDB**: Vector database (optional)
- **Sentence Transformers**: Text embeddings (optional)
- **Flask-CORS**: Cross-origin requests

### JavaScript (Frontend)
- **React 19**: UI framework
- **Vite 7**: Build tool
- **Tailwind CSS 4**: Styling
- **React Query**: Data fetching
- **React Router**: Navigation
- **Axios**: HTTP client

## 🧪 Usage Examples

### 1. Traditional OpenAPI Testing
1. Go to "API Tests" tab
2. Upload your OpenAPI spec file
3. Configure generation options
4. Generate and export test cases

### 2. RAG-Powered Testing
1. Go to "Documents" tab
2. Upload business documents/code
3. Process into vector database
4. Go to "AI Chat" tab
5. Describe your testing needs in natural language
6. Get contextual test cases

### Example Chat Interactions:
```
"Generate authentication tests for our user login API"
"Create boundary tests for the payment processing endpoint"
"Generate security tests based on our security policy document"
```

## 🔧 Development Commands

### Backend
```bash
# Start Flask development server
python -m src.app

# Install new Python dependency
pip install package-name
pip freeze > requirements.txt
```

### Frontend
```bash
cd frontend

# Start development server
npm run dev

# Build for production
npm run build

# Install new dependency
npm install package-name
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes on specific ports
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:5000 | xargs kill -9  # Backend
```

### Python Dependencies Issues
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Build Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues
The backend includes CORS headers for development. If you still have issues:
1. Check that both servers are running
2. Verify frontend is on port 3000, backend on port 5000
3. Clear browser cache

## 🧠 RAG Setup (Optional Advanced Features)

For full RAG functionality, install additional dependencies:

```bash
pip install chromadb sentence-transformers
```

These provide:
- Vector database storage
- Document embedding
- Semantic search
- Context retrieval

**Note**: The application works without these dependencies, but RAG features will be disabled.

## 🌐 Production Deployment

### Frontend Build
```bash
cd frontend
npm run build
# Deploy dist/ folder to your web server
```

### Backend Deployment
```bash
# Set production environment variables
export FLASK_ENV=production
export SECRET_KEY="your-production-secret"

# Use WSGI server like Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.app:app"
```

## 📚 Additional Resources

- **API Documentation**: Check `/health` endpoint for server status
- **Examples**: See `examples/` directory for sample OpenAPI specs
- **Issues**: Report bugs on GitHub Issues
- **Contributing**: See CONTRIBUTING.md (if available)

## 🎉 You're Ready!

Your APITestGen development environment is now set up and ready for both traditional OpenAPI testing and advanced RAG-powered contextual test generation.

Happy testing! 🚀