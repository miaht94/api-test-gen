"""
Chat interface for AI-powered test generation using RAG.
"""

import os
from typing import List, Dict, Any, Optional
import json
import logging

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .rag import RAGManager

logger = logging.getLogger(__name__)

class ChatManager:
    """Manages chat interactions for AI-powered test generation."""
    
    def __init__(self, rag_manager: RAGManager):
        self.rag_manager = rag_manager
        self.openai_client = None
        
        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
    
    def is_available(self) -> bool:
        """Check if chat functionality is available."""
        return self.openai_client is not None
    
    def generate_response(self, message: str, context: str = "test_generation") -> Dict[str, Any]:
        """Generate AI response with RAG context."""
        if not self.is_available():
            return {
                "response": "AI chat is not available. Please set OPENAI_API_KEY environment variable.",
                "test_cases": [],
                "error": "OpenAI not configured"
            }
        
        try:
            # Search for relevant context
            relevant_docs = self.rag_manager.search_context(message, n_results=3)
            
            # Build context from relevant documents
            context_text = self._build_context(relevant_docs)
            
            # Generate system prompt
            system_prompt = self._create_system_prompt(context_text)
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            
            # Try to extract test cases if the response contains them
            test_cases = self._extract_test_cases(ai_response)
            
            return {
                "response": ai_response,
                "test_cases": test_cases,
                "context_used": len(relevant_docs),
                "relevant_docs": [doc['metadata']['document_name'] for doc in relevant_docs]
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "response": f"I encountered an error: {str(e)}",
                "test_cases": [],
                "error": str(e)
            }
    
    def _build_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Build context string from relevant documents."""
        if not relevant_docs:
            return "No relevant context found."
        
        context_parts = []
        for doc in relevant_docs:
            metadata = doc['metadata']
            content = doc['content']
            
            context_parts.append(f"""
Document: {metadata['document_name']} ({metadata['document_type']})
Content: {content[:500]}...
""")
        
        return "\n".join(context_parts)
    
    def _create_system_prompt(self, context: str) -> str:
        """Create system prompt for AI assistant."""
        return f"""You are an expert API testing assistant specializing in creating comprehensive test cases. You help developers generate test cases for APIs based on business requirements, documentation, and code context.

CONTEXT FROM UPLOADED DOCUMENTS:
{context}

Your capabilities:
1. Generate API test cases in multiple formats (JSON, Python, shell scripts)
2. Create edge cases and boundary tests
3. Suggest security and validation tests
4. Use business context to create realistic test scenarios

When generating test cases, include:
- Test case ID and description
- HTTP method and endpoint
- Request parameters, headers, and body
- Expected response status and data
- Test type (functional, edge case, security, etc.)

Format test cases as JSON objects when requested. Be specific and actionable in your suggestions.

If you generate test cases, format them as a JSON array at the end of your response between ```json and ``` tags."""

    def _extract_test_cases(self, response: str) -> List[Dict[str, Any]]:
        """Extract test cases from AI response."""
        test_cases = []
        
        # Look for JSON code blocks
        import re
        json_blocks = re.findall(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        
        for block in json_blocks:
            try:
                parsed = json.loads(block.strip())
                if isinstance(parsed, list):
                    test_cases.extend(parsed)
                elif isinstance(parsed, dict):
                    test_cases.append(parsed)
            except json.JSONDecodeError:
                continue
        
        return test_cases
    
    def generate_contextual_tests(self, api_spec: Dict[str, Any], requirements: str) -> List[Dict[str, Any]]:
        """Generate test cases based on API spec and business requirements."""
        if not self.is_available():
            return []
        
        try:
            # Search for relevant context
            relevant_docs = self.rag_manager.search_context(requirements, n_results=5)
            context_text = self._build_context(relevant_docs)
            
            # Create specialized prompt for test generation
            prompt = f"""
Based on the following API specification and business requirements, generate comprehensive test cases:

API SPECIFICATION:
{json.dumps(api_spec, indent=2)}

BUSINESS REQUIREMENTS:
{requirements}

RELEVANT CONTEXT:
{context_text}

Generate test cases that cover:
1. Happy path scenarios
2. Edge cases and boundary conditions
3. Error handling
4. Security considerations
5. Business rule validation

Format the response as a JSON array of test case objects. Each test case should have:
- id: unique identifier
- description: what the test validates
- method: HTTP method
- endpoint: API endpoint
- parameters: query/path parameters
- headers: required headers
- body: request body (if applicable)
- expected_status: expected HTTP status code
- test_type: type of test (functional, edge_case, security, etc.)
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert API testing specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            ai_response = response.choices[0].message.content
            return self._extract_test_cases(ai_response)
            
        except Exception as e:
            logger.error(f"Error generating contextual tests: {e}")
            return []