"""
Edge case generator module.
Generates edge case test scenarios based on parameter types and constraints.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EdgeCaseGenerator:
    """Generates edge case test scenarios for API endpoints."""
    
    def __init__(self):
        self.edge_case_templates = {
            'string': [
                {'name': 'empty_string', 'value': '', 'description': 'Empty string'},
                {'name': 'null_value', 'value': None, 'description': 'Null value'},
                {'name': 'long_string', 'value': 'a' * 1000, 'description': 'Very long string (1000 chars)'},
                {'name': 'special_chars', 'value': '!@#$%^&*()_+-=[]{}|;:,.<>?', 'description': 'Special characters'},
                {'name': 'unicode_chars', 'value': 'こんにちは🌍', 'description': 'Unicode characters'},
                {'name': 'sql_injection', 'value': "'; DROP TABLE users; --", 'description': 'SQL injection attempt'},
                {'name': 'xss_attempt', 'value': '<script>alert("xss")</script>', 'description': 'XSS injection attempt'},
                {'name': 'path_traversal', 'value': '../../../etc/passwd', 'description': 'Path traversal attempt'},
            ],
            'integer': [
                {'name': 'zero', 'value': 0, 'description': 'Zero value'},
                {'name': 'negative', 'value': -1, 'description': 'Negative value'},
                {'name': 'max_int', 'value': 2147483647, 'description': 'Maximum 32-bit integer'},
                {'name': 'min_int', 'value': -2147483648, 'description': 'Minimum 32-bit integer'},
                {'name': 'null_value', 'value': None, 'description': 'Null value'},
                {'name': 'string_as_int', 'value': 'not_a_number', 'description': 'String instead of integer'},
            ],
            'number': [
                {'name': 'zero', 'value': 0.0, 'description': 'Zero value'},
                {'name': 'negative', 'value': -1.5, 'description': 'Negative value'},
                {'name': 'very_large', 'value': 1.7976931348623157e+308, 'description': 'Very large number'},
                {'name': 'very_small', 'value': 5e-324, 'description': 'Very small number'},
                {'name': 'infinity', 'value': float('inf'), 'description': 'Infinity'},
                {'name': 'null_value', 'value': None, 'description': 'Null value'},
                {'name': 'string_as_number', 'value': 'not_a_number', 'description': 'String instead of number'},
            ],
            'boolean': [
                {'name': 'null_value', 'value': None, 'description': 'Null value'},
                {'name': 'string_true', 'value': 'true', 'description': 'String "true" instead of boolean'},
                {'name': 'string_false', 'value': 'false', 'description': 'String "false" instead of boolean'},
                {'name': 'integer_zero', 'value': 0, 'description': 'Integer 0 instead of boolean'},
                {'name': 'integer_one', 'value': 1, 'description': 'Integer 1 instead of boolean'},
            ],
            'array': [
                {'name': 'empty_array', 'value': [], 'description': 'Empty array'},
                {'name': 'null_value', 'value': None, 'description': 'Null value'},
                {'name': 'single_item', 'value': ['item'], 'description': 'Array with single item'},
                {'name': 'large_array', 'value': list(range(1000)), 'description': 'Very large array (1000 items)'},
                {'name': 'mixed_types', 'value': [1, 'string', True, None], 'description': 'Array with mixed types'},
                {'name': 'nested_arrays', 'value': [[1, 2], [3, 4]], 'description': 'Nested arrays'},
            ],
            'object': [
                {'name': 'empty_object', 'value': {}, 'description': 'Empty object'},
                {'name': 'null_value', 'value': None, 'description': 'Null value'},
                {'name': 'large_object', 'value': {f'key_{i}': f'value_{i}' for i in range(100)}, 'description': 'Object with many properties'},
                {'name': 'nested_object', 'value': {'level1': {'level2': {'level3': 'deep'}}}, 'description': 'Deeply nested object'},
                {'name': 'special_keys', 'value': {'': 'empty_key', ' ': 'space_key', '!@#': 'special_chars'}, 'description': 'Object with special character keys'},
            ]
        }
    
    def generate_edge_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate edge case variations for the given test cases.
        
        Args:
            test_cases: List of basic test cases
            
        Returns:
            List of edge case test scenarios
        """
        edge_cases = []
        
        for test_case in test_cases:
            # Skip if this is already an edge case
            if test_case.get('test_type') == 'edge_case':
                continue
            
            logger.info(f"Generating edge cases for {test_case['method']} {test_case['endpoint']}")
            
            # Generate edge cases for query parameters
            edge_cases.extend(self._generate_parameter_edge_cases(test_case, 'query_params'))
            
            # Generate edge cases for path parameters
            edge_cases.extend(self._generate_parameter_edge_cases(test_case, 'path_params'))
            
            # Generate edge cases for request body
            if test_case.get('body'):
                edge_cases.extend(self._generate_body_edge_cases(test_case))
            
            # Generate authentication edge cases
            edge_cases.extend(self._generate_auth_edge_cases(test_case))
            
            # Generate HTTP method edge cases
            edge_cases.extend(self._generate_method_edge_cases(test_case))
        
        logger.info(f"Generated {len(edge_cases)} edge case test scenarios")
        return edge_cases
    
    def _generate_parameter_edge_cases(self, test_case: Dict[str, Any], param_type: str) -> List[Dict[str, Any]]:
        """Generate edge cases for parameters (query or path)."""
        edge_cases = []
        params = test_case.get(param_type, {})
        
        if not params:
            return edge_cases
        
        # For each parameter, generate edge cases
        for param_name, param_value in params.items():
            param_data_type = self._infer_parameter_type(param_value)
            edge_case_templates = self.edge_case_templates.get(param_data_type, [])
            
            for template in edge_case_templates:
                edge_case = self._create_edge_case_from_template(
                    test_case, template, param_name, param_type
                )
                edge_cases.append(edge_case)
        
        return edge_cases
    
    def _generate_body_edge_cases(self, test_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate edge cases for request body."""
        edge_cases = []
        
        # Empty body
        edge_case = self._create_body_edge_case(
            test_case, None, 'empty_body', 'Empty request body'
        )
        edge_cases.append(edge_case)
        
        # Invalid JSON
        edge_case = self._create_body_edge_case(
            test_case, '{"invalid": json}', 'invalid_json', 'Invalid JSON syntax'
        )
        edge_cases.append(edge_case)
        
        # Very large body
        large_body = {'data': 'x' * 10000}
        edge_case = self._create_body_edge_case(
            test_case, large_body, 'large_body', 'Very large request body'
        )
        edge_cases.append(edge_case)
        
        # If body is an object, generate field-specific edge cases
        if isinstance(test_case.get('body'), dict):
            edge_cases.extend(self._generate_object_field_edge_cases(test_case))
        
        return edge_cases
    
    def _generate_object_field_edge_cases(self, test_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate edge cases for object fields in request body."""
        edge_cases = []
        original_body = test_case.get('body', {})
        
        if not isinstance(original_body, dict):
            return edge_cases
        
        # For each field in the body, generate edge cases
        for field_name, field_value in original_body.items():
            field_type = self._infer_parameter_type(field_value)
            edge_case_templates = self.edge_case_templates.get(field_type, [])
            
            for template in edge_case_templates:
                # Create a new body with the edge case value for this field
                edge_body = original_body.copy()
                edge_body[field_name] = template['value']
                
                edge_case = self._create_body_edge_case(
                    test_case, 
                    edge_body, 
                    f"{field_name}_{template['name']}", 
                    f"Edge case for field '{field_name}': {template['description']}"
                )
                edge_cases.append(edge_case)
        
        return edge_cases
    
    def _generate_auth_edge_cases(self, test_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate authentication-related edge cases."""
        edge_cases = []
        
        # Missing authentication
        edge_case = test_case.copy()
        edge_case.update({
            'id': f"{test_case['id']}_no_auth",
            'description': f"{test_case['description']} - No authentication",
            'headers': {k: v for k, v in test_case.get('headers', {}).items() 
                       if not k.lower().startswith('auth')},
            'test_type': 'edge_case',
            'edge_case_category': 'authentication',
            'expected_status_code': 401,
            'created_at': datetime.now().isoformat()
        })
        edge_cases.append(edge_case)
        
        # Invalid authentication token
        edge_case = test_case.copy()
        headers = edge_case.get('headers', {}).copy()
        headers['Authorization'] = 'Bearer invalid_token'
        edge_case.update({
            'id': f"{test_case['id']}_invalid_auth",
            'description': f"{test_case['description']} - Invalid authentication",
            'headers': headers,
            'test_type': 'edge_case',
            'edge_case_category': 'authentication',
            'expected_status_code': 401,
            'created_at': datetime.now().isoformat()
        })
        edge_cases.append(edge_case)
        
        # Expired authentication (simulated)
        edge_case = test_case.copy()
        headers = edge_case.get('headers', {}).copy()
        headers['Authorization'] = 'Bearer expired_token'
        edge_case.update({
            'id': f"{test_case['id']}_expired_auth",
            'description': f"{test_case['description']} - Expired authentication",
            'headers': headers,
            'test_type': 'edge_case',
            'edge_case_category': 'authentication',
            'expected_status_code': 401,
            'created_at': datetime.now().isoformat()
        })
        edge_cases.append(edge_case)
        
        return edge_cases
    
    def _generate_method_edge_cases(self, test_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate HTTP method-related edge cases."""
        edge_cases = []
        
        # Wrong HTTP method
        wrong_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        if test_case['method'] in wrong_methods:
            wrong_methods.remove(test_case['method'])
        
        for wrong_method in wrong_methods[:2]:  # Limit to 2 to avoid too many cases
            edge_case = test_case.copy()
            edge_case.update({
                'id': f"{test_case['id']}_method_{wrong_method.lower()}",
                'method': wrong_method,
                'description': f"{test_case['description']} - Wrong HTTP method ({wrong_method})",
                'test_type': 'edge_case',
                'edge_case_category': 'http_method',
                'expected_status_code': 405,  # Method Not Allowed
                'created_at': datetime.now().isoformat()
            })
            
            # Update cURL command with new method
            edge_case['curl_command'] = edge_case['curl_command'].replace(
                f"-X {test_case['method']}", f"-X {wrong_method}"
            )
            
            edge_cases.append(edge_case)
        
        return edge_cases
    
    def _create_edge_case_from_template(self, test_case: Dict[str, Any], template: Dict[str, Any], 
                                      param_name: str, param_type: str) -> Dict[str, Any]:
        """Create an edge case test from a template."""
        edge_case = test_case.copy()
        
        # Update the specific parameter
        params = edge_case.get(param_type, {}).copy()
        params[param_name] = template['value']
        edge_case[param_type] = params
        
        # Update metadata
        edge_case.update({
            'id': f"{test_case['id']}_{param_name}_{template['name']}",
            'description': f"{test_case['description']} - {template['description']} for {param_name}",
            'test_type': 'edge_case',
            'edge_case_category': param_type,
            'edge_case_template': template['name'],
            'expected_status_code': 400 if template['value'] is None or template['name'] in ['string_as_int', 'string_as_number'] else test_case['expected_status_code'],
            'created_at': datetime.now().isoformat()
        })
        
        # Update cURL command
        edge_case['curl_command'] = self._update_curl_command(edge_case)
        
        return edge_case
    
    def _create_body_edge_case(self, test_case: Dict[str, Any], edge_body: Any, 
                             edge_name: str, description: str) -> Dict[str, Any]:
        """Create an edge case test for request body."""
        edge_case = test_case.copy()
        
        edge_case.update({
            'id': f"{test_case['id']}_{edge_name}",
            'body': edge_body,
            'description': f"{test_case['description']} - {description}",
            'test_type': 'edge_case',
            'edge_case_category': 'request_body',
            'edge_case_template': edge_name,
            'expected_status_code': 400 if edge_name in ['empty_body', 'invalid_json'] else test_case['expected_status_code'],
            'created_at': datetime.now().isoformat()
        })
        
        # Update cURL command
        edge_case['curl_command'] = self._update_curl_command(edge_case)
        
        return edge_case
    
    def _update_curl_command(self, test_case: Dict[str, Any]) -> str:
        """Update the cURL command for an edge case."""
        # This is a simplified version - in a real implementation,
        # you might want to regenerate the entire cURL command
        from .test_generator import TestCaseGenerator
        generator = TestCaseGenerator()
        
        # Create a mock endpoint for curl generation
        endpoint = {
            'method': test_case['method'],
            'path': test_case['endpoint'],
            'base_url': test_case.get('base_url', ''),
            'request_body': {'content_type': 'application/json'} if test_case.get('body') else None
        }
        
        return generator._generate_curl_command(
            endpoint,
            test_case.get('query_params', {}),
            test_case.get('path_params', {}),
            test_case.get('headers', {}),
            test_case.get('body')
        )
    
    def _infer_parameter_type(self, value: Any) -> str:
        """Infer the parameter type from its value."""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'number'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return 'string'
    
    def get_edge_case_summary(self, edge_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get a summary of generated edge cases."""
        
        categories = {}
        templates = {}
        
        for case in edge_cases:
            category = case.get('edge_case_category', 'unknown')
            template = case.get('edge_case_template', 'unknown')
            
            categories[category] = categories.get(category, 0) + 1
            templates[template] = templates.get(template, 0) + 1
        
        return {
            'total_edge_cases': len(edge_cases),
            'categories': categories,
            'templates': templates,
            'generated_at': datetime.now().isoformat()
        }