"""
Flask web application for APITestGen.
Provides a web interface for uploading OpenAPI specs and generating test cases.
Extended with RAG functionality for document-based context generation.
"""

import os
import json
import tempfile
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import logging

from .openapi_parser import OpenAPIParser
from .test_generator import TestCaseGenerator
from .edge_case_generator import EdgeCaseGenerator
from .exporters import TestCaseExporter
from .rag import RAGManager
from .rag.chat import ChatManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Global storage for session data (in production, use proper session storage)
sessions = {}

# Initialize RAG manager
rag_manager = RAGManager()
chat_manager = ChatManager(rag_manager)


@app.route('/')
def index():
    """Home page with file upload form."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle OpenAPI spec file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Parse the OpenAPI spec
            parser = OpenAPIParser()
            success = parser.load_from_file(filepath)
            
            if not success:
                os.remove(filepath)
                return jsonify({'error': 'Invalid OpenAPI specification'}), 400
            
            # Parse endpoints
            endpoints = parser.parse_endpoints()
            spec_info = parser.get_spec_info()
            
            # Store session data
            session_id = f"session_{len(sessions)}"
            sessions[session_id] = {
                'parser': parser,
                'endpoints': endpoints,
                'spec_info': spec_info,
                'filepath': filepath
            }
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'spec_info': spec_info,
                'endpoints_count': len(endpoints),
                'endpoints': endpoints[:10]  # Return first 10 for preview
            })
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/upload_text', methods=['POST'])
def upload_text():
    """Handle OpenAPI spec text upload."""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'No content provided'}), 400
        
        content = data['content']
        file_type = data.get('type', 'json')
        
        # Parse the OpenAPI spec
        parser = OpenAPIParser()
        success = parser.load_from_string(content, file_type)
        
        if not success:
            return jsonify({'error': 'Invalid OpenAPI specification'}), 400
        
        # Parse endpoints
        endpoints = parser.parse_endpoints()
        spec_info = parser.get_spec_info()
        
        # Store session data
        session_id = f"session_{len(sessions)}"
        sessions[session_id] = {
            'parser': parser,
            'endpoints': endpoints,
            'spec_info': spec_info,
            'filepath': None
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'spec_info': spec_info,
            'endpoints_count': len(endpoints),
            'endpoints': endpoints[:10]  # Return first 10 for preview
        })
    
    except Exception as e:
        logger.error(f"Error processing text upload: {str(e)}")
        return jsonify({'error': f'Error processing content: {str(e)}'}), 500


@app.route('/generate/<session_id>')
def generate_tests(session_id):
    """Generate test cases for the uploaded spec."""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = sessions[session_id]
        endpoints = session_data['endpoints']
        spec_info = session_data['spec_info']
        
        # Get options from query parameters
        use_ai = request.args.get('use_ai', 'false').lower() == 'true'
        include_edge_cases = request.args.get('include_edge_cases', 'true').lower() == 'true'
        openai_api_key = request.args.get('openai_api_key', '')
        
        # Generate basic test cases
        generator = TestCaseGenerator(openai_api_key if openai_api_key else None)
        test_cases = generator.generate_test_cases(endpoints, use_ai=use_ai)
        
        # Generate edge cases if requested
        if include_edge_cases:
            edge_generator = EdgeCaseGenerator()
            edge_cases = edge_generator.generate_edge_cases(test_cases)
            test_cases.extend(edge_cases)
        
        # Store test cases in session
        session_data['test_cases'] = test_cases
        
        return jsonify({
            'success': True,
            'test_cases_count': len(test_cases),
            'test_cases': test_cases
        })
    
    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}")
        return jsonify({'error': f'Error generating test cases: {str(e)}'}), 500


@app.route('/export/<session_id>/<format>')
def export_tests(session_id, format):
    """Export test cases in the specified format."""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = sessions[session_id]
        if 'test_cases' not in session_data:
            return jsonify({'error': 'No test cases generated yet'}), 400
        
        test_cases = session_data['test_cases']
        spec_info = session_data['spec_info']
        
        # Create exporter
        exporter = TestCaseExporter()
        
        # Export in the requested format
        if format == 'csv':
            filepath = exporter.export_csv(test_cases, spec_info)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        elif format == 'json':
            filepath = exporter.export_json(test_cases, spec_info)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        elif format == 'shell':
            filepath = exporter.export_shell_script(test_cases, spec_info)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        elif format == 'python':
            filepath = exporter.export_python_test_script(test_cases, spec_info)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        elif format == 'postman':
            filepath = exporter.export_postman_collection(test_cases, spec_info)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        elif format == 'html':
            filepath = exporter.export_html_report(test_cases, spec_info)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        elif format == 'all':
            exported_files = exporter.export_all_formats(test_cases, spec_info)
            return jsonify({
                'success': True,
                'exported_files': {k: os.path.basename(v) for k, v in exported_files.items()}
            })
        else:
            return jsonify({'error': 'Unsupported export format'}), 400
    
    except Exception as e:
        logger.error(f"Error exporting test cases: {str(e)}")
        return jsonify({'error': f'Error exporting test cases: {str(e)}'}), 500


@app.route('/preview/<session_id>')
def preview_tests(session_id):
    """Preview generated test cases."""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = sessions[session_id]
        if 'test_cases' not in session_data:
            return jsonify({'error': 'No test cases generated yet'}), 400
        
        test_cases = session_data['test_cases']
        spec_info = session_data['spec_info']
        
        # Group test cases by type
        basic_cases = [tc for tc in test_cases if tc.get('test_type') == 'basic']
        ai_cases = [tc for tc in test_cases if tc.get('test_type') == 'ai_enhanced']
        edge_cases = [tc for tc in test_cases if tc.get('test_type') == 'edge_case']
        
        return render_template('preview.html', 
                             spec_info=spec_info,
                             basic_cases=basic_cases,
                             ai_cases=ai_cases,
                             edge_cases=edge_cases,
                             session_id=session_id)
    
    except Exception as e:
        logger.error(f"Error previewing test cases: {str(e)}")
        return jsonify({'error': f'Error previewing test cases: {str(e)}'}), 500


# RAG and Document Management Endpoints

@app.route('/api/upload-documents', methods=['POST'])
def upload_documents():
    """Upload documents for RAG processing."""
    try:
        if not request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        doc_type = request.form.get('type', 'document')
        uploaded_docs = []
        
        for key in request.files:
            file = request.files[key]
            if file.filename:
                filename = secure_filename(file.filename)
                content = file.read().decode('utf-8', errors='ignore')
                file_extension = filename.split('.')[-1] if '.' in filename else ''
                
                # Add document to RAG manager
                doc_id = rag_manager.add_document(
                    name=filename,
                    content=content,
                    doc_type=doc_type,
                    file_extension=file_extension
                )
                
                uploaded_docs.append({
                    'id': doc_id,
                    'name': filename,
                    'type': doc_type,
                    'size': len(content)
                })
        
        return jsonify({
            'success': True,
            'documents': uploaded_docs,
            'count': len(uploaded_docs)
        })
    
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        return jsonify({'error': f'Error uploading documents: {str(e)}'}), 500


@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get all uploaded documents."""
    try:
        documents = rag_manager.get_documents()
        return jsonify(documents)
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return jsonify({'error': f'Error retrieving documents: {str(e)}'}), 500


@app.route('/api/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document."""
    try:
        success = rag_manager.delete_document(doc_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete document'}), 500
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        return jsonify({'error': f'Error deleting document: {str(e)}'}), 500


@app.route('/api/process-documents', methods=['POST'])
def process_documents():
    """Process documents into vector database."""
    try:
        results = rag_manager.process_documents()
        return jsonify({
            'success': True,
            'processed_count': results['processed_count'],
            'failed_count': results['failed_count'],
            'errors': results['errors']
        })
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        return jsonify({'error': f'Error processing documents: {str(e)}'}), 500


@app.route('/api/documents/status', methods=['GET'])
def get_documents_status():
    """Get RAG system status."""
    try:
        status = rag_manager.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': f'Error getting status: {str(e)}'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for AI-powered test generation."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        message = data['message']
        context = data.get('context', 'test_generation')
        
        # Generate AI response
        response = chat_manager.generate_response(message, context)
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': f'Error generating response: {str(e)}'}), 500


@app.route('/api/export-chat-tests', methods=['POST'])
def export_chat_tests():
    """Export test cases generated from chat."""
    try:
        data = request.get_json()
        if not data or 'test_cases' not in data:
            return jsonify({'error': 'No test cases provided'}), 400
        
        test_cases = data['test_cases']
        format_type = data.get('format', 'json')
        
        # Create exporter
        exporter = TestCaseExporter()
        
        # Mock spec info for chat-generated tests
        spec_info = {
            'title': 'Chat Generated Tests',
            'version': '1.0.0',
            'description': 'Test cases generated via AI chat'
        }
        
        # Export in the requested format
        if format_type == 'json':
            filepath = exporter.export_json(test_cases, spec_info)
        elif format_type == 'python':
            filepath = exporter.export_python_test_script(test_cases, spec_info)
        elif format_type == 'shell':
            filepath = exporter.export_shell_script(test_cases, spec_info)
        else:
            return jsonify({'error': 'Unsupported export format'}), 400
        
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
    
    except Exception as e:
        logger.error(f"Error exporting chat tests: {str(e)}")
        return jsonify({'error': f'Error exporting tests: {str(e)}'}), 500


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)