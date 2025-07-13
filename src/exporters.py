"""
Export module for generating test case outputs in various formats.
Supports CSV, JSON, shell scripts, and other export formats.
"""

import json
import csv
import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCaseExporter:
    """Export test cases in various formats."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the exporter.
        
        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_all_formats(self, test_cases: List[Dict[str, Any]], 
                          spec_info: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Export test cases in all supported formats.
        
        Args:
            test_cases: List of test case dictionaries
            spec_info: Information about the API specification
            
        Returns:
            Dictionary mapping format names to file paths
        """
        exported_files = {}
        
        try:
            # Export CSV
            csv_file = self.export_csv(test_cases, spec_info)
            exported_files['csv'] = csv_file
            
            # Export JSON
            json_file = self.export_json(test_cases, spec_info)
            exported_files['json'] = json_file
            
            # Export shell script
            shell_file = self.export_shell_script(test_cases, spec_info)
            exported_files['shell'] = shell_file
            
            # Export Python test script
            python_file = self.export_python_test_script(test_cases, spec_info)
            exported_files['python'] = python_file
            
            # Export Postman collection
            postman_file = self.export_postman_collection(test_cases, spec_info)
            exported_files['postman'] = postman_file
            
            # Export HTML report
            html_file = self.export_html_report(test_cases, spec_info)
            exported_files['html'] = html_file
            
            logger.info(f"Exported test cases in {len(exported_files)} formats")
            
        except Exception as e:
            logger.error(f"Error during export: {str(e)}")
            raise
        
        return exported_files
    
    def export_csv(self, test_cases: List[Dict[str, Any]], 
                   spec_info: Dict[str, Any] = None) -> str:
        """Export test cases as CSV file."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_cases_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'ID', 'Method', 'Endpoint', 'Description', 'Test Type',
                'Query Parameters', 'Path Parameters', 'Headers', 'Request Body',
                'Expected Status Code', 'cURL Command', 'Tags', 'Created At'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for test_case in test_cases:
                row = {
                    'ID': test_case.get('id', ''),
                    'Method': test_case.get('method', ''),
                    'Endpoint': test_case.get('endpoint', ''),
                    'Description': test_case.get('description', ''),
                    'Test Type': test_case.get('test_type', ''),
                    'Query Parameters': json.dumps(test_case.get('query_params', {})),
                    'Path Parameters': json.dumps(test_case.get('path_params', {})),
                    'Headers': json.dumps(test_case.get('headers', {})),
                    'Request Body': json.dumps(test_case.get('body', None)),
                    'Expected Status Code': test_case.get('expected_status_code', ''),
                    'cURL Command': test_case.get('curl_command', ''),
                    'Tags': ', '.join(test_case.get('tags', [])),
                    'Created At': test_case.get('created_at', '')
                }
                writer.writerow(row)
        
        logger.info(f"Exported {len(test_cases)} test cases to CSV: {filepath}")
        return filepath
    
    def export_json(self, test_cases: List[Dict[str, Any]], 
                    spec_info: Dict[str, Any] = None) -> str:
        """Export test cases as JSON file."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_cases_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        export_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_test_cases': len(test_cases),
                'api_info': spec_info or {},
                'exporter_version': '1.0.0'
            },
            'test_cases': test_cases
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(test_cases)} test cases to JSON: {filepath}")
        return filepath
    
    def export_shell_script(self, test_cases: List[Dict[str, Any]], 
                           spec_info: Dict[str, Any] = None) -> str:
        """Export test cases as shell script with cURL commands."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_script_{timestamp}.sh"
        filepath = os.path.join(self.output_dir, filename)
        
        shell_template = """#!/bin/bash
#
# API Test Script
# Generated: {{ generated_at }}
# API: {{ api_title }} ({{ api_version }})
# Total Test Cases: {{ total_cases }}
#

set -e  # Exit on any error

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to log test results
log_test() {
    local test_name="$1"
    local expected_status="$2"
    local actual_status="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$actual_status" = "$expected_status" ]; then
        echo -e "${GREEN}[PASS]${NC} $test_name (Status: $actual_status)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}[FAIL]${NC} $test_name (Expected: $expected_status, Got: $actual_status)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to run a test case
run_test() {
    local test_name="$1"
    local curl_command="$2"
    local expected_status="$3"
    
    echo -e "${YELLOW}Running:${NC} $test_name"
    
    # Execute cURL and capture status code
    local actual_status
    actual_status=$(eval "$curl_command -w '%{http_code}' -s -o /dev/null")
    
    log_test "$test_name" "$expected_status" "$actual_status"
    echo ""
}

echo "=== API Test Execution Started ==="
echo ""

{% for test_case in test_cases %}
# Test Case: {{ test_case.description }}
# Type: {{ test_case.test_type }}
# Method: {{ test_case.method }} {{ test_case.endpoint }}
run_test "{{ test_case.id }}" "{{ test_case.curl_command }}" "{{ test_case.expected_status_code }}"

{% endfor %}

echo "=== Test Summary ==="
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
"""
        
        template = Template(shell_template)
        script_content = template.render(
            generated_at=datetime.now().isoformat(),
            api_title=spec_info.get('title', 'Unknown API') if spec_info else 'Unknown API',
            api_version=spec_info.get('version', '1.0.0') if spec_info else '1.0.0',
            total_cases=len(test_cases),
            test_cases=test_cases
        )
        
        with open(filepath, 'w', encoding='utf-8') as shellfile:
            shellfile.write(script_content)
        
        # Make the script executable
        os.chmod(filepath, 0o755)
        
        logger.info(f"Exported shell script with {len(test_cases)} test cases: {filepath}")
        return filepath
    
    def export_python_test_script(self, test_cases: List[Dict[str, Any]], 
                                 spec_info: Dict[str, Any] = None) -> str:
        """Export test cases as Python test script using requests library."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_script_{timestamp}.py"
        filepath = os.path.join(self.output_dir, filename)
        
        python_template = """#!/usr/bin/env python3
\"\"\"
API Test Script
Generated: {{ generated_at }}
API: {{ api_title }} ({{ api_version }})
Total Test Cases: {{ total_cases }}

Requirements:
    pip install requests

Usage:
    python {{ filename }}
\"\"\"

import requests
import json
import sys
from datetime import datetime


class APITestRunner:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.results = []
    
    def run_test(self, test_case):
        \"\"\"Run a single test case.\"\"\"
        self.total_tests += 1
        
        test_id = test_case.get('id', 'unknown')
        method = test_case.get('method', 'GET')
        url = test_case.get('full_url', '')
        headers = test_case.get('headers', {})
        params = test_case.get('query_params', {})
        body = test_case.get('body')
        expected_status = test_case.get('expected_status_code', 200)
        
        print(f"\\n[TEST] {test_id}: {test_case.get('description', '')}")
        print(f"       {method} {url}")
        
        try:
            # Prepare request data
            request_kwargs = {
                'headers': headers,
                'params': params,
                'timeout': 30
            }
            
            if body is not None:
                if isinstance(body, (dict, list)):
                    request_kwargs['json'] = body
                else:
                    request_kwargs['data'] = body
            
            # Make the request
            response = requests.request(method, url, **request_kwargs)
            actual_status = response.status_code
            
            # Check result
            if actual_status == expected_status:
                print(f"       ✅ PASS (Status: {actual_status})")
                self.passed_tests += 1
                result = 'PASS'
            else:
                print(f"       ❌ FAIL (Expected: {expected_status}, Got: {actual_status})")
                self.failed_tests += 1
                result = 'FAIL'
            
            self.results.append({
                'test_id': test_id,
                'method': method,
                'url': url,
                'expected_status': expected_status,
                'actual_status': actual_status,
                'result': result,
                'response_time': response.elapsed.total_seconds(),
                'response_headers': dict(response.headers),
                'timestamp': datetime.now().isoformat()
            })
            
        except requests.exceptions.RequestException as e:
            print(f"       ❌ ERROR: {str(e)}")
            self.failed_tests += 1
            self.results.append({
                'test_id': test_id,
                'method': method,
                'url': url,
                'expected_status': expected_status,
                'actual_status': None,
                'result': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def print_summary(self):
        \"\"\"Print test execution summary.\"\"\"
        print("\\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        return self.failed_tests == 0
    
    def save_results(self, filename="test_results.json"):
        \"\"\"Save test results to JSON file.\"\"\"
        with open(filename, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': self.total_tests,
                    'passed_tests': self.passed_tests,
                    'failed_tests': self.failed_tests,
                    'execution_time': datetime.now().isoformat()
                },
                'results': self.results
            }, f, indent=2)
        print(f"\\nResults saved to: {filename}")


def main():
    \"\"\"Main test execution function.\"\"\"
    runner = APITestRunner()
    
    # Test cases
    test_cases = {{ test_cases | tojson }}
    
    print("Starting API Test Execution...")
    print(f"Total test cases: {len(test_cases)}")
    
    for test_case in test_cases:
        runner.run_test(test_case)
    
    # Print summary and save results
    success = runner.print_summary()
    runner.save_results()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
"""
        
        template = Template(python_template)
        script_content = template.render(
            generated_at=datetime.now().isoformat(),
            api_title=spec_info.get('title', 'Unknown API') if spec_info else 'Unknown API',
            api_version=spec_info.get('version', '1.0.0') if spec_info else '1.0.0',
            total_cases=len(test_cases),
            test_cases=test_cases,
            filename=filename
        )
        
        with open(filepath, 'w', encoding='utf-8') as pythonfile:
            pythonfile.write(script_content)
        
        # Make the script executable
        os.chmod(filepath, 0o755)
        
        logger.info(f"Exported Python test script with {len(test_cases)} test cases: {filepath}")
        return filepath
    
    def export_postman_collection(self, test_cases: List[Dict[str, Any]], 
                                 spec_info: Dict[str, Any] = None) -> str:
        """Export test cases as Postman collection."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_collection_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        collection = {
            "info": {
                "name": f"{spec_info.get('title', 'API')} Test Collection" if spec_info else "API Test Collection",
                "description": f"Generated test collection for {spec_info.get('title', 'API')}" if spec_info else "Generated API test collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # Group test cases by endpoint
        endpoint_groups = {}
        for test_case in test_cases:
            endpoint = test_case.get('endpoint', '/')
            if endpoint not in endpoint_groups:
                endpoint_groups[endpoint] = []
            endpoint_groups[endpoint].append(test_case)
        
        # Create Postman requests
        for endpoint, cases in endpoint_groups.items():
            folder = {
                "name": endpoint,
                "item": []
            }
            
            for test_case in cases:
                request = self._create_postman_request(test_case)
                folder["item"].append(request)
            
            collection["item"].append(folder)
        
        with open(filepath, 'w', encoding='utf-8') as postmanfile:
            json.dump(collection, postmanfile, indent=2)
        
        logger.info(f"Exported Postman collection with {len(test_cases)} test cases: {filepath}")
        return filepath
    
    def _create_postman_request(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Postman request from a test case."""
        
        # Build URL with path parameters
        url = test_case.get('full_url', '')
        if not url:
            base_url = test_case.get('base_url', 'http://localhost')
            path = test_case.get('endpoint', '/')
            # Replace path parameters
            for param_name, param_value in test_case.get('path_params', {}).items():
                path = path.replace(f"{{{param_name}}}", str(param_value))
            url = f"{base_url}{path}"
        
        # Prepare query parameters
        query_params = []
        for key, value in test_case.get('query_params', {}).items():
            query_params.append({
                "key": key,
                "value": str(value)
            })
        
        # Prepare headers
        headers = []
        for key, value in test_case.get('headers', {}).items():
            headers.append({
                "key": key,
                "value": str(value)
            })
        
        # Prepare body
        body = None
        if test_case.get('body') is not None:
            if isinstance(test_case['body'], (dict, list)):
                body = {
                    "mode": "raw",
                    "raw": json.dumps(test_case['body'], indent=2),
                    "options": {
                        "raw": {
                            "language": "json"
                        }
                    }
                }
            else:
                body = {
                    "mode": "raw",
                    "raw": str(test_case['body'])
                }
        
        request = {
            "name": test_case.get('description', test_case.get('id', 'Test')),
            "request": {
                "method": test_case.get('method', 'GET'),
                "header": headers,
                "url": {
                    "raw": url,
                    "query": query_params
                }
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            f"pm.test('Status code is {test_case.get('expected_status_code', 200)}', function () {{",
                            f"    pm.response.to.have.status({test_case.get('expected_status_code', 200)});",
                            "});"
                        ],
                        "type": "text/javascript"
                    }
                }
            ]
        }
        
        if body:
            request["request"]["body"] = body
        
        return request
    
    def export_html_report(self, test_cases: List[Dict[str, Any]], 
                          spec_info: Dict[str, Any] = None) -> str:
        """Export test cases as HTML report."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_report_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # Group test cases by type
        basic_cases = [tc for tc in test_cases if tc.get('test_type') == 'basic']
        ai_cases = [tc for tc in test_cases if tc.get('test_type') == 'ai_enhanced']
        edge_cases = [tc for tc in test_cases if tc.get('test_type') == 'edge_case']
        
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Test Report - {{ api_title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .stats { display: flex; justify-content: space-around; margin-bottom: 30px; }
        .stat-card { background: #007bff; color: white; padding: 20px; border-radius: 8px; text-align: center; min-width: 150px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .test-case { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; background: #fafafa; }
        .test-case h3 { margin: 0 0 10px 0; color: #007bff; }
        .method { padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; }
        .GET { background-color: #28a745; }
        .POST { background-color: #007bff; }
        .PUT { background-color: #ffc107; color: black; }
        .DELETE { background-color: #dc3545; }
        .PATCH { background-color: #6f42c1; }
        .curl-command { background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; overflow-x: auto; margin: 10px 0; }
        .badge { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold; }
        .badge-basic { background-color: #28a745; color: white; }
        .badge-ai { background-color: #007bff; color: white; }
        .badge-edge { background-color: #ffc107; color: black; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>API Test Report</h1>
            <h2>{{ api_title }} ({{ api_version }})</h2>
            <p>Generated on {{ generated_at }}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{{ total_cases }}</h3>
                <p>Total Test Cases</p>
            </div>
            <div class="stat-card">
                <h3>{{ basic_count }}</h3>
                <p>Basic Tests</p>
            </div>
            <div class="stat-card">
                <h3>{{ ai_count }}</h3>
                <p>AI Enhanced</p>
            </div>
            <div class="stat-card">
                <h3>{{ edge_count }}</h3>
                <p>Edge Cases</p>
            </div>
        </div>
        
        {% if basic_cases %}
        <div class="section">
            <h2>Basic Test Cases</h2>
            {% for test_case in basic_cases %}
            <div class="test-case">
                <h3>
                    <span class="method {{ test_case.method }}">{{ test_case.method }}</span>
                    {{ test_case.endpoint }}
                    <span class="badge badge-basic">BASIC</span>
                </h3>
                <p><strong>Description:</strong> {{ test_case.description }}</p>
                <p><strong>Expected Status:</strong> {{ test_case.expected_status_code }}</p>
                {% if test_case.tags %}
                <p><strong>Tags:</strong> {{ test_case.tags | join(', ') }}</p>
                {% endif %}
                <div class="curl-command">{{ test_case.curl_command }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if ai_cases %}
        <div class="section">
            <h2>AI Enhanced Test Cases</h2>
            {% for test_case in ai_cases %}
            <div class="test-case">
                <h3>
                    <span class="method {{ test_case.method }}">{{ test_case.method }}</span>
                    {{ test_case.endpoint }}
                    <span class="badge badge-ai">AI ENHANCED</span>
                </h3>
                <p><strong>Description:</strong> {{ test_case.description }}</p>
                <p><strong>Expected Status:</strong> {{ test_case.expected_status_code }}</p>
                {% if test_case.edge_cases %}
                <p><strong>Edge Cases:</strong> {{ test_case.edge_cases | join(', ') }}</p>
                {% endif %}
                {% if test_case.security_notes %}
                <p><strong>Security Notes:</strong> {{ test_case.security_notes }}</p>
                {% endif %}
                <div class="curl-command">{{ test_case.curl_command }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if edge_cases %}
        <div class="section">
            <h2>Edge Case Test Scenarios</h2>
            {% for test_case in edge_cases %}
            <div class="test-case">
                <h3>
                    <span class="method {{ test_case.method }}">{{ test_case.method }}</span>
                    {{ test_case.endpoint }}
                    <span class="badge badge-edge">EDGE CASE</span>
                </h3>
                <p><strong>Description:</strong> {{ test_case.description }}</p>
                <p><strong>Expected Status:</strong> {{ test_case.expected_status_code }}</p>
                <p><strong>Category:</strong> {{ test_case.edge_case_category }}</p>
                <div class="curl-command">{{ test_case.curl_command }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>"""
        
        template = Template(html_template)
        html_content = template.render(
            api_title=spec_info.get('title', 'Unknown API') if spec_info else 'Unknown API',
            api_version=spec_info.get('version', '1.0.0') if spec_info else '1.0.0',
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_cases=len(test_cases),
            basic_count=len(basic_cases),
            ai_count=len(ai_cases),
            edge_count=len(edge_cases),
            basic_cases=basic_cases,
            ai_cases=ai_cases,
            edge_cases=edge_cases
        )
        
        with open(filepath, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)
        
        logger.info(f"Exported HTML report with {len(test_cases)} test cases: {filepath}")
        return filepath