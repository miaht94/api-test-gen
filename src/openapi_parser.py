"""
OpenAPI/Swagger specification parser module.
Handles parsing and validation of OpenAPI specifications.
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAPIParser:
    """Parser for OpenAPI/Swagger specifications."""
    
    def __init__(self):
        self.spec = None
        self.endpoints = []
        
    def load_from_file(self, file_path: str) -> bool:
        """
        Load OpenAPI spec from file (JSON or YAML).
        
        Args:
            file_path: Path to the OpenAPI specification file
            
        Returns:
            bool: True if successfully loaded and validated
        """
        try:
            # Read the specification
            spec_result = read_from_filename(file_path)
            # The function returns a tuple (spec_dict, base_uri)
            if isinstance(spec_result, tuple):
                spec_dict = spec_result[0]
            else:
                spec_dict = spec_result
            
            logger.info(f"Successfully read spec file: {file_path}")
            
            # Basic validation - check if it has required OpenAPI structure
            if not self._basic_validate(spec_dict):
                raise ValueError("Invalid OpenAPI structure")
            
            # Try to validate the specification (this can be lenient)
            try:
                validate_spec(spec_dict)
                logger.info(f"Successfully validated OpenAPI spec with strict validation")
            except Exception as validation_error:
                logger.warning(f"Strict validation failed, but continuing with basic validation: {validation_error}")
                # Still continue if basic structure is valid
            
            self.spec = spec_dict
            logger.info(f"Successfully loaded OpenAPI spec from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading OpenAPI spec: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def load_from_string(self, spec_content: str, file_type: str = "json") -> bool:
        """
        Load OpenAPI spec from string content.
        
        Args:
            spec_content: The specification content as string
            file_type: Either "json" or "yaml"
            
        Returns:
            bool: True if successfully loaded and validated
        """
        try:
            if file_type.lower() == "json":
                spec_dict = json.loads(spec_content)
            elif file_type.lower() in ["yaml", "yml"]:
                spec_dict = yaml.safe_load(spec_content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Basic validation - check if it has required OpenAPI structure
            if not self._basic_validate(spec_dict):
                raise ValueError("Invalid OpenAPI structure")
            
            # Try to validate the specification (this can be lenient)
            try:
                validate_spec(spec_dict)
                logger.info(f"Successfully validated OpenAPI spec with strict validation")
            except Exception as validation_error:
                logger.warning(f"Strict validation failed, but continuing with basic validation: {validation_error}")
                # Still continue if basic structure is valid
            
            self.spec = spec_dict
            logger.info(f"Successfully loaded OpenAPI spec from string")
            return True
            
        except Exception as e:
            logger.error(f"Error loading OpenAPI spec from string: {str(e)}")
            return False
    
    def parse_endpoints(self) -> List[Dict[str, Any]]:
        """
        Parse all endpoints from the OpenAPI specification.
        
        Returns:
            List of endpoint dictionaries with method, path, parameters, etc.
        """
        if not self.spec:
            raise ValueError("No OpenAPI specification loaded")
        
        endpoints = []
        base_url = self._get_base_url()
        
        paths = self.spec.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'operation_id': operation.get('operationId', f"{method}_{path.replace('/', '_')}"),
                        'summary': operation.get('summary', ''),
                        'description': operation.get('description', ''),
                        'parameters': self._parse_parameters(operation, path_item),
                        'request_body': self._parse_request_body(operation),
                        'responses': self._parse_responses(operation),
                        'tags': operation.get('tags', []),
                        'base_url': base_url
                    }
                    endpoints.append(endpoint)
        
        self.endpoints = endpoints
        logger.info(f"Parsed {len(endpoints)} endpoints from OpenAPI spec")
        return endpoints
    
    def _get_base_url(self) -> str:
        """Extract base URL from the OpenAPI spec."""
        # OpenAPI 3.x
        if 'servers' in self.spec and self.spec['servers']:
            return self.spec['servers'][0].get('url', '')
        
        # OpenAPI 2.x (Swagger)
        if 'host' in self.spec:
            scheme = self.spec.get('schemes', ['http'])[0]
            host = self.spec['host']
            base_path = self.spec.get('basePath', '')
            return f"{scheme}://{host}{base_path}"
        
        return "http://localhost"
    
    def _parse_parameters(self, operation: Dict, path_item: Dict) -> List[Dict[str, Any]]:
        """Parse parameters from operation and path item."""
        parameters = []
        
        # Parameters from path level
        path_params = path_item.get('parameters', [])
        
        # Parameters from operation level
        operation_params = operation.get('parameters', [])
        
        # Combine and process all parameters
        all_params = path_params + operation_params
        
        for param in all_params:
            param_info = {
                'name': param.get('name', ''),
                'in': param.get('in', ''),  # query, header, path, cookie
                'description': param.get('description', ''),
                'required': param.get('required', False),
                'schema': param.get('schema', {}),
                'type': param.get('type', param.get('schema', {}).get('type', 'string')),
                'example': param.get('example', param.get('schema', {}).get('example')),
                'enum': param.get('enum', param.get('schema', {}).get('enum')),
            }
            parameters.append(param_info)
        
        return parameters
    
    def _parse_request_body(self, operation: Dict) -> Optional[Dict[str, Any]]:
        """Parse request body from operation."""
        request_body = operation.get('requestBody')
        if not request_body:
            return None
        
        content = request_body.get('content', {})
        
        # Try to get JSON content first, then any other content type
        for content_type in ['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data']:
            if content_type in content:
                schema = content[content_type].get('schema', {})
                return {
                    'content_type': content_type,
                    'schema': schema,
                    'required': request_body.get('required', False),
                    'description': request_body.get('description', '')
                }
        
        # If no specific content type found, take the first one
        if content:
            first_content_type = list(content.keys())[0]
            schema = content[first_content_type].get('schema', {})
            return {
                'content_type': first_content_type,
                'schema': schema,
                'required': request_body.get('required', False),
                'description': request_body.get('description', '')
            }
        
        return None
    
    def _parse_responses(self, operation: Dict) -> Dict[str, Dict[str, Any]]:
        """Parse responses from operation."""
        responses = {}
        
        for status_code, response in operation.get('responses', {}).items():
            responses[status_code] = {
                'description': response.get('description', ''),
                'content': response.get('content', {}),
                'headers': response.get('headers', {})
            }
        
        return responses
    
    def _basic_validate(self, spec_dict: dict) -> bool:
        """Basic validation of OpenAPI structure."""
        try:
            # Check for required top-level fields
            required_fields = ['info', 'paths']
            for field in required_fields:
                if field not in spec_dict:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Check for OpenAPI version field (3.x) or swagger field (2.x)
            if 'openapi' not in spec_dict and 'swagger' not in spec_dict:
                logger.error("Missing openapi or swagger version field")
                return False
            
            # Check info object structure
            info = spec_dict.get('info', {})
            if not isinstance(info, dict) or 'title' not in info:
                logger.error("Invalid info object structure")
                return False
            
            # Check paths object structure
            paths = spec_dict.get('paths', {})
            if not isinstance(paths, dict):
                logger.error("Invalid paths object structure")
                return False
            
            logger.info("Basic OpenAPI structure validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Basic validation failed: {str(e)}")
            return False
    
    def get_spec_info(self) -> Dict[str, Any]:
        """Get basic information about the OpenAPI specification."""
        if not self.spec:
            return {}
        
        info = self.spec.get('info', {})
        return {
            'title': info.get('title', 'Unknown API'),
            'version': info.get('version', '1.0.0'),
            'description': info.get('description', ''),
            'base_url': self._get_base_url(),
            'total_endpoints': len(self.endpoints),
            'openapi_version': self.spec.get('openapi', self.spec.get('swagger', 'Unknown'))
        }