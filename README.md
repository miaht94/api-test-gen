# 🚀 APITestGen

Generate comprehensive API test cases from OpenAPI/Swagger specifications automatically.

APITestGen is a powerful tool that automatically generates API test cases from existing API specifications such as OpenAPI (Swagger) or Postman collections. It reduces manual effort, increases test coverage (especially edge cases), and integrates easily with tools like Postman, Insomnia, and CI pipelines.

## ✨ Features

### 🎯 Core Features
- **OpenAPI/Swagger Parser**: Supports both JSON and YAML formats (OpenAPI 2.x & 3.x)
- **AI-Enhanced Generation**: Uses OpenAI GPT-4 for intelligent test case creation
- **Edge Case Generation**: Automatically generates edge cases for comprehensive testing
- **Multiple Export Formats**: CSV, JSON, Shell scripts, Python scripts, Postman collections, HTML reports
- **Web Interface**: User-friendly web UI for easy file upload and test generation
- **CLI Tool**: Command-line interface for automation and CI/CD integration

### 🧪 Test Case Types
- **Basic Test Cases**: Standard happy path scenarios
- **AI-Enhanced Cases**: Intelligent test scenarios with realistic data
- **Edge Cases**: Boundary testing, invalid inputs, security scenarios
- **Authentication Tests**: Missing, invalid, and expired authentication scenarios
- **HTTP Method Tests**: Wrong method usage scenarios

### 📤 Export Formats
- **CSV**: For manual testing and QA teams
- **JSON**: Structured test data for automation tools
- **Shell Scripts**: Executable bash scripts with cURL commands
- **Python Scripts**: Ready-to-run test scripts using requests library
- **Postman Collections**: Import directly into Postman
- **HTML Reports**: Beautiful, shareable test documentation

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/miaht94/api-test-gen.git
cd api-test-gen

# Install dependencies
pip install -r requirements.txt

# Optional: Install as a package
pip install -e .
```

### Web Interface

Start the web server:

```bash
python -m src.app
# or using CLI
api-test-gen serve
```

Then open http://localhost:5000 in your browser.

### Command Line Usage

```bash
# Generate test cases from OpenAPI spec
api-test-gen generate examples/petstore-api.json

# With AI enhancement (requires OpenAI API key)
export OPENAI_API_KEY="your-key-here"
api-test-gen generate examples/petstore-api.json --use-ai

# Specific export formats
api-test-gen generate examples/petstore-api.json -f csv -f python

# Validate OpenAPI specification
api-test-gen validate examples/petstore-api.json

# List endpoints
api-test-gen list-endpoints examples/petstore-api.json
```

## 📖 Usage Examples

### 1. Basic Test Generation

```bash
api-test-gen generate examples/petstore-api.json --output-dir ./output
```

This generates:
- Basic test cases for all endpoints
- Edge case scenarios
- All export formats in the output directory

### 2. AI-Enhanced Generation

```bash
export OPENAI_API_KEY="sk-your-openai-key"
api-test-gen generate examples/petstore-api.json --use-ai --output-dir ./output
```

AI enhancement provides:
- More realistic test data
- Better parameter combinations
- Security considerations
- Edge case suggestions

### 3. Custom Export Formats

```bash
# Export only specific formats
api-test-gen generate examples/petstore-api.json -f csv -f python -f postman

# Skip edge cases
api-test-gen generate examples/petstore-api.json --no-edge-cases
```

### 4. Running Generated Tests

```bash
# Run Python test script
api-test-gen run-tests output/api_test_script_*.py

# Run shell script
api-test-gen run-tests output/api_test_script_*.sh
```

## 🏗️ Project Structure

```
api-test-gen/
├── src/
│   ├── __init__.py
│   ├── openapi_parser.py      # OpenAPI specification parser
│   ├── test_generator.py      # Test case generation with AI
│   ├── edge_case_generator.py # Edge case scenario generation
│   ├── exporters.py          # Export functionality
│   ├── app.py                # Flask web application
│   ├── cli.py                # Command line interface
│   └── templates/            # HTML templates
│       ├── index.html
│       └── preview.html
├── examples/
│   ├── petstore-api.json     # Example OpenAPI specs
│   └── user-api.yaml
├── requirements.txt          # Python dependencies
├── setup.py                 # Package configuration
└── README.md                # This file
```

## 🛠️ Tech Stack

- **Backend**: Python with Flask
- **Parsing**: openapi-spec-validator, PyYAML
- **AI Integration**: OpenAI GPT-4
- **Export**: Pandas, Jinja2, JSON/CSV libraries
- **Frontend**: HTML/CSS/JavaScript (no frameworks)
- **CLI**: Click

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI API key for AI-enhanced generation
export OPENAI_API_KEY="sk-your-openai-key"

# Flask secret key (for web interface)
export SECRET_KEY="your-secret-key"
```

### OpenAPI Specification Requirements

APITestGen supports:
- OpenAPI 3.0.x and 3.1.x
- Swagger 2.0
- JSON and YAML formats
- File upload or direct text input

## 📊 Generated Test Case Structure

Each test case includes:

```json
{
  "id": "get_pets_basic",
  "method": "GET",
  "endpoint": "/pets",
  "description": "Test GET /pets - List all pets",
  "query_params": {"limit": 10, "category": "dog"},
  "path_params": {},
  "headers": {},
  "body": null,
  "expected_status_code": 200,
  "curl_command": "curl -X GET 'https://api.example.com/pets?limit=10&category=dog'",
  "test_type": "basic",
  "tags": ["pets"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🎯 Edge Case Coverage

APITestGen automatically generates edge cases for:

### Parameter Testing
- Null values
- Empty strings
- Very long strings (1000+ characters)
- Special characters and Unicode
- SQL injection attempts
- XSS injection attempts
- Path traversal attempts

### Data Type Testing
- Invalid data types (string instead of integer)
- Boundary values (min/max integers)
- Invalid enums
- Malformed arrays and objects

### Authentication Testing
- Missing authentication headers
- Invalid tokens
- Expired tokens (simulated)

### HTTP Method Testing
- Wrong HTTP methods for endpoints
- Method not allowed scenarios

## 🌐 Web Interface Features

### File Upload
- Drag and drop OpenAPI files
- Support for JSON and YAML
- Real-time validation
- File size limits (16MB)

### Text Input
- Paste OpenAPI specification directly
- Format selection (JSON/YAML)
- Syntax validation

### Generation Options
- AI enhancement toggle
- OpenAI API key input
- Edge case inclusion
- Real-time preview

### Results Preview
- Organized by test type
- Expandable test case details
- Copy cURL commands
- Download in multiple formats

## 🔌 API Endpoints

The web interface provides these REST endpoints:

```
POST /upload          # Upload OpenAPI file
POST /upload_text     # Upload OpenAPI text
GET  /generate/{id}   # Generate test cases
GET  /preview/{id}    # Preview test cases
GET  /export/{id}/{format}  # Export test cases
GET  /health          # Health check
```

## 🧪 Example Generated Files

### Shell Script Output
```bash
#!/bin/bash
# API Test Script - Generated by APITestGen

run_test() {
    local test_name="$1"
    local curl_command="$2"
    local expected_status="$3"
    
    echo "Running: $test_name"
    actual_status=$(eval "$curl_command -w '%{http_code}' -s -o /dev/null")
    
    if [ "$actual_status" = "$expected_status" ]; then
        echo "✅ PASS: $test_name"
    else
        echo "❌ FAIL: $test_name (Expected: $expected_status, Got: $actual_status)"
    fi
}

# Test cases
run_test "get_pets" "curl -X GET 'https://api.example.com/pets'" "200"
run_test "create_pet" "curl -X POST 'https://api.example.com/pets' -H 'Content-Type: application/json' -d '{\"name\":\"Fluffy\",\"category\":\"cat\"}'" "201"
```

### Python Script Output
```python
#!/usr/bin/env python3
import requests
import json

def test_get_pets():
    response = requests.get('https://api.example.com/pets')
    assert response.status_code == 200

def test_create_pet():
    data = {"name": "Fluffy", "category": "cat"}
    response = requests.post('https://api.example.com/pets', json=data)
    assert response.status_code == 201

if __name__ == "__main__":
    test_get_pets()
    test_create_pet()
    print("All tests passed!")
```

## 🔒 Security Considerations

APITestGen helps identify potential security issues by:
- Generating authentication bypass tests
- Testing for injection vulnerabilities
- Validating input sanitization
- Checking authorization boundaries

**Note**: Generated security tests are for legitimate testing purposes only. Use responsibly and only on systems you own or have permission to test.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: This README and inline code comments
- **Examples**: Check the `examples/` directory

## 🗺️ Roadmap

### Current (v1.0)
- [x] OpenAPI parsing and validation
- [x] Basic test case generation
- [x] AI-enhanced generation
- [x] Edge case scenarios
- [x] Multiple export formats
- [x] Web interface
- [x] CLI tool

### Future (v1.1+)
- [ ] Postman collection import
- [ ] Response validation
- [ ] Test result analysis
- [ ] Integration with CI/CD platforms
- [ ] Custom test templates
- [ ] Performance testing scenarios
- [ ] API versioning support
- [ ] Batch processing

## 🎉 Acknowledgments

Built for the 24-hour hackathon challenge. Thanks to:
- OpenAPI Initiative for the specification standard
- OpenAI for AI-powered test generation
- The open-source community for excellent libraries

---

**Happy API Testing! 🚀**
