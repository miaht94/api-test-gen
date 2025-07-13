"""
Test case generator module.
Generates test cases from OpenAPI endpoints using OpenAI and rule-based logic.
"""

import json
import os
from typing import Dict, List, Any, Optional
import openai
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCaseGenerator:
    """Generates test cases from OpenAPI endpoints."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the test case generator.
        
        Args:
            openai_api_key: OpenAI API key. If not provided, will try to get from environment.
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("No OpenAI API key provided. AI-powered features will be disabled.")
        
        self.test_cases = []
    
    def generate_test_cases(self, endpoints: List[Dict[str, Any]], use_ai: bool = True) -> List[Dict[str, Any]]:
        """
        Generate test cases for all endpoints.
        
        Args:
            endpoints: List of parsed endpoints from OpenAPI spec
            use_ai: Whether to use AI for enhanced test case generation
            
        Returns:
            List of test case dictionaries
        """
        self.test_cases = []
        
        for endpoint in endpoints:
            logger.info(f"Generating test cases for {endpoint['method']} {endpoint['path']}")
            
            # Generate basic test case
            basic_test_case = self._generate_basic_test_case(endpoint)
            self.test_cases.append(basic_test_case)
            
            # Generate AI-enhanced test case if available
            if use_ai and self.openai_api_key:
                try:
                    ai_test_case = self._generate_ai_test_case(endpoint)
                    if ai_test_case:
                        self.test_cases.append(ai_test_case)
                except Exception as e:
                    logger.error(f"Error generating AI test case: {str(e)}")
        
        logger.info(f"Generated {len(self.test_cases)} test cases")
        return self.test_cases
    
    def _generate_basic_test_case(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a basic test case using rule-based logic."""
        
        # Generate example parameters
        query_params = {}
        path_params = {}
        headers = {}
        body = None
        
        for param in endpoint.get('parameters', []):
            example_value = self._generate_example_value(param)
            
            if param['in'] == 'query':
                query_params[param['name']] = example_value
            elif param['in'] == 'path':
                path_params[param['name']] = example_value
            elif param['in'] == 'header':
                headers[param['name']] = example_value
        
        # Generate request body if present
        if endpoint.get('request_body'):
            body = self._generate_example_body(endpoint['request_body'])
        
        # Generate cURL command
        curl_command = self._generate_curl_command(endpoint, query_params, path_params, headers, body)
        
        # Determine expected status code
        expected_status = self._get_expected_status_code(endpoint)
        
        return {
            'id': f"{endpoint['method'].lower()}_{endpoint['path'].replace('/', '_').replace('{', '').replace('}', '')}",
            'method': endpoint['method'],
            'endpoint': endpoint['path'],
            'base_url': endpoint.get('base_url', ''),
            'full_url': self._build_full_url(endpoint, path_params),
            'description': f"Test {endpoint['method']} {endpoint['path']} - {endpoint.get('summary', 'Basic test case')}",
            'query_params': query_params,
            'path_params': path_params,
            'headers': headers,
            'body': body,
            'expected_status_code': expected_status,
            'curl_command': curl_command,
            'test_type': 'basic',
            'tags': endpoint.get('tags', []),
            'created_at': datetime.now().isoformat()
        }
    
    def _generate_ai_test_case(self, endpoint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate an AI-enhanced test case using OpenAI."""
        
        prompt = self._build_ai_prompt(endpoint)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert API test case generator. Generate comprehensive test cases based on OpenAPI specifications."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse AI response and create test case
            return self._parse_ai_response(endpoint, ai_response)
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return None
    
    def _build_ai_prompt(self, endpoint: Dict[str, Any]) -> str:
        """Build a prompt for OpenAI to generate test cases."""
        
        prompt = f"""
Generate a comprehensive test case for the following API endpoint:

Method: {endpoint['method']}
Path: {endpoint['path']}
Summary: {endpoint.get('summary', 'N/A')}
Description: {endpoint.get('description', 'N/A')}

Parameters:
{json.dumps(endpoint.get('parameters', []), indent=2)}

Request Body:
{json.dumps(endpoint.get('request_body', {}), indent=2)}

Responses:
{json.dumps(endpoint.get('responses', {}), indent=2)}

Please provide:
1. Realistic example values for all parameters
2. A detailed test description
3. Expected behavior and status code
4. Any edge cases to consider
5. Security considerations if applicable

Format your response as a JSON object with the following structure:
{{
    "description": "Detailed test description",
    "parameters": {{"param_name": "example_value"}},
    "request_body": {{}},
    "expected_status": 200,
    "edge_cases": ["case1", "case2"],
    "security_notes": "Any security considerations"
}}
"""
        return prompt
    
    def _parse_ai_response(self, endpoint: Dict[str, Any], ai_response: str) -> Dict[str, Any]:
        """Parse AI response and create a test case."""
        
        try:
            # Try to extract JSON from the AI response
            ai_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # If JSON parsing fails, create a basic test case with AI description
            logger.warning("Could not parse AI response as JSON, using basic test case")
            return self._generate_basic_test_case(endpoint)
        
        # Build test case from AI data
        query_params = {}
        path_params = {}
        headers = {}
        
        ai_params = ai_data.get('parameters', {})
        
        for param in endpoint.get('parameters', []):
            param_name = param['name']
            if param_name in ai_params:
                value = ai_params[param_name]
            else:
                value = self._generate_example_value(param)
            
            if param['in'] == 'query':
                query_params[param_name] = value
            elif param['in'] == 'path':
                path_params[param_name] = value
            elif param['in'] == 'header':
                headers[param_name] = value
        
        body = ai_data.get('request_body')
        curl_command = self._generate_curl_command(endpoint, query_params, path_params, headers, body)
        
        return {
            'id': f"{endpoint['method'].lower()}_{endpoint['path'].replace('/', '_').replace('{', '').replace('}', '')}_ai",
            'method': endpoint['method'],
            'endpoint': endpoint['path'],
            'base_url': endpoint.get('base_url', ''),
            'full_url': self._build_full_url(endpoint, path_params),
            'description': ai_data.get('description', f"AI-generated test for {endpoint['method']} {endpoint['path']}"),
            'query_params': query_params,
            'path_params': path_params,
            'headers': headers,
            'body': body,
            'expected_status_code': ai_data.get('expected_status', 200),
            'curl_command': curl_command,
            'test_type': 'ai_enhanced',
            'edge_cases': ai_data.get('edge_cases', []),
            'security_notes': ai_data.get('security_notes', ''),
            'tags': endpoint.get('tags', []),
            'created_at': datetime.now().isoformat()
        }
    
    def _generate_example_value(self, param: Dict[str, Any]) -> Any:
        """Generate an example value for a parameter based on its type and constraints."""
        
        param_type = param.get('type', 'string')
        param_format = param.get('schema', {}).get('format', param.get('format'))
        param_enum = param.get('enum', param.get('schema', {}).get('enum'))
        example = param.get('example', param.get('schema', {}).get('example'))
        
        # Use provided example if available
        if example is not None:
            return example
        
        # Use enum value if available
        if param_enum:
            return param_enum[0]
        
        # Generate based on type
        if param_type == 'integer':
            return 1
        elif param_type == 'number':
            return 1.0
        elif param_type == 'boolean':
            return True
        elif param_type == 'array':
            return ["example_item"]
        elif param_type == 'object':
            return {"key": "value"}
        else:  # string or unknown
            if param_format == 'date':
                return "2024-01-01"
            elif param_format == 'date-time':
                return "2024-01-01T00:00:00Z"
            elif param_format == 'email':
                return "test@example.com"
            elif param_format == 'uuid':
                return "123e4567-e89b-12d3-a456-426614174000"
            else:
                return f"example_{param['name']}"
    
    def _generate_example_body(self, request_body: Dict[str, Any]) -> Any:
        """Generate an example request body."""
        
        schema = request_body.get('schema', {})
        content_type = request_body.get('content_type', 'application/json')
        
        if content_type == 'application/json':
            return self._generate_example_from_schema(schema)
        elif content_type == 'application/x-www-form-urlencoded':
            # Return a simple form data example
            return {"field1": "value1", "field2": "value2"}
        else:
            return "example_body_content"
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Generate an example value from a JSON schema."""
        
        schema_type = schema.get('type')
        example = schema.get('example')
        
        if example is not None:
            return example
        
        if schema_type == 'object':
            result = {}
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                result[prop_name] = self._generate_example_from_schema(prop_schema)
            return result
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self._generate_example_from_schema(items_schema)]
        elif schema_type == 'string':
            return "example_string"
        elif schema_type == 'integer':
            return 1
        elif schema_type == 'number':
            return 1.0
        elif schema_type == 'boolean':
            return True
        else:
            return "example_value"
    
    def _generate_curl_command(self, endpoint: Dict[str, Any], query_params: Dict, 
                             path_params: Dict, headers: Dict, body: Any) -> str:
        """Generate a cURL command for the test case."""
        
        # Build URL
        url = self._build_full_url(endpoint, path_params)
        
        # Add query parameters
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            url += f"?{query_string}"
        
        # Build cURL command
        curl_parts = ["curl", "-X", endpoint['method']]
        
        # Add headers
        if headers:
            for key, value in headers.items():
                curl_parts.extend(["-H", f"'{key}: {value}'"])
        
        # Add content type for body
        if body is not None:
            content_type = endpoint.get('request_body', {}).get('content_type', 'application/json')
            curl_parts.extend(["-H", f"'Content-Type: {content_type}'"])
        
        # Add body
        if body is not None:
            if isinstance(body, dict) or isinstance(body, list):
                body_str = json.dumps(body)
                curl_parts.extend(["-d", f"'{body_str}'"])
            else:
                curl_parts.extend(["-d", f"'{body}'"])
        
        # Add URL
        curl_parts.append(f"'{url}'")
        
        return " ".join(curl_parts)
    
    def _build_full_url(self, endpoint: Dict[str, Any], path_params: Dict) -> str:
        """Build the full URL for an endpoint with path parameters."""
        
        base_url = endpoint.get('base_url', '').rstrip('/')
        path = endpoint['path']
        
        # Replace path parameters
        for param_name, param_value in path_params.items():
            path = path.replace(f"{{{param_name}}}", str(param_value))
        
        return f"{base_url}{path}"
    
    def _get_expected_status_code(self, endpoint: Dict[str, Any]) -> int:
        """Determine the expected status code for successful requests."""
        
        responses = endpoint.get('responses', {})
        
        # Look for success status codes in order of preference
        for status_code in ['200', '201', '202', '204']:
            if status_code in responses:
                return int(status_code)
        
        # If no standard success code found, return 200 as default
        return 200
    
    def _get_expected_status_code(self, endpoint: Dict[str, Any]) -> int:
        """Determine the expected status code for successful requests."""
        
        responses = endpoint.get('responses', {})
        
        # Look for success status codes in order of preference
        for status_code in ['200', '201', '202', '204']:
            if status_code in responses:
                return int(status_code)
        
        # If no standard success code found, return 200 as default
        return 200