#!/usr/bin/env python3
"""
Command Line Interface for APITestGen.
Provides CLI access to all API test generation features.
"""

import click
import os
import sys
import json
from typing import Optional
import logging

from .openapi_parser import OpenAPIParser
from .test_generator import TestCaseGenerator
from .edge_case_generator import EdgeCaseGenerator
from .exporters import TestCaseExporter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """APITestGen - Generate API test cases from OpenAPI specifications."""
    pass


@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output', help='Output directory for generated files')
@click.option('--format', '-f', multiple=True, 
              type=click.Choice(['csv', 'json', 'shell', 'python', 'postman', 'html', 'all']),
              default=['all'], help='Export formats (can specify multiple)')
@click.option('--use-ai/--no-ai', default=False, help='Use OpenAI for enhanced test generation')
@click.option('--openai-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
@click.option('--edge-cases/--no-edge-cases', default=True, help='Generate edge case test scenarios')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def generate(spec_file: str, output_dir: str, format: tuple, use_ai: bool, 
             openai_key: Optional[str], edge_cases: bool, verbose: bool):
    """Generate test cases from an OpenAPI specification file."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        click.echo(f"🚀 APITestGen - Generating test cases from {spec_file}")
        click.echo()
        
        # Parse OpenAPI specification
        click.echo("📋 Parsing OpenAPI specification...")
        parser = OpenAPIParser()
        if not parser.load_from_file(spec_file):
            click.echo("❌ Error: Failed to parse OpenAPI specification", err=True)
            sys.exit(1)
        
        endpoints = parser.parse_endpoints()
        spec_info = parser.get_spec_info()
        
        click.echo(f"✅ Parsed {len(endpoints)} endpoints from {spec_info.get('title', 'API')}")
        click.echo()
        
        # Generate test cases
        click.echo("🧪 Generating test cases...")
        generator = TestCaseGenerator(openai_key)
        test_cases = generator.generate_test_cases(endpoints, use_ai=use_ai)
        
        basic_count = len([tc for tc in test_cases if tc.get('test_type') == 'basic'])
        ai_count = len([tc for tc in test_cases if tc.get('test_type') == 'ai_enhanced'])
        
        click.echo(f"✅ Generated {basic_count} basic test cases")
        if use_ai and openai_key:
            click.echo(f"✅ Generated {ai_count} AI-enhanced test cases")
        elif use_ai and not openai_key:
            click.echo("⚠️  AI features disabled: No OpenAI API key provided")
        
        # Generate edge cases
        if edge_cases:
            click.echo("🎯 Generating edge case scenarios...")
            edge_generator = EdgeCaseGenerator()
            edge_test_cases = edge_generator.generate_edge_cases(test_cases)
            test_cases.extend(edge_test_cases)
            click.echo(f"✅ Generated {len(edge_test_cases)} edge case scenarios")
        
        click.echo()
        click.echo(f"📊 Total test cases: {len(test_cases)}")
        click.echo()
        
        # Export test cases
        click.echo("💾 Exporting test cases...")
        exporter = TestCaseExporter(output_dir)
        
        exported_files = {}
        
        for fmt in format:
            if fmt == 'all':
                exported_files.update(exporter.export_all_formats(test_cases, spec_info))
            elif fmt == 'csv':
                exported_files['csv'] = exporter.export_csv(test_cases, spec_info)
            elif fmt == 'json':
                exported_files['json'] = exporter.export_json(test_cases, spec_info)
            elif fmt == 'shell':
                exported_files['shell'] = exporter.export_shell_script(test_cases, spec_info)
            elif fmt == 'python':
                exported_files['python'] = exporter.export_python_test_script(test_cases, spec_info)
            elif fmt == 'postman':
                exported_files['postman'] = exporter.export_postman_collection(test_cases, spec_info)
            elif fmt == 'html':
                exported_files['html'] = exporter.export_html_report(test_cases, spec_info)
        
        # Display exported files
        click.echo("✅ Exported files:")
        for file_format, filepath in exported_files.items():
            click.echo(f"   {file_format.upper()}: {filepath}")
        
        click.echo()
        click.echo("🎉 Test case generation completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
def validate(spec_file: str):
    """Validate an OpenAPI specification file."""
    
    try:
        click.echo(f"🔍 Validating OpenAPI specification: {spec_file}")
        
        parser = OpenAPIParser()
        if parser.load_from_file(spec_file):
            spec_info = parser.get_spec_info()
            endpoints = parser.parse_endpoints()
            
            click.echo("✅ OpenAPI specification is valid")
            click.echo()
            click.echo("📋 Specification Details:")
            click.echo(f"   Title: {spec_info.get('title', 'Unknown')}")
            click.echo(f"   Version: {spec_info.get('version', 'Unknown')}")
            click.echo(f"   OpenAPI Version: {spec_info.get('openapi_version', 'Unknown')}")
            click.echo(f"   Base URL: {spec_info.get('base_url', 'Unknown')}")
            click.echo(f"   Total Endpoints: {len(endpoints)}")
            
            # Show endpoint summary
            if endpoints:
                click.echo()
                click.echo("🔗 Endpoints Summary:")
                method_counts = {}
                for endpoint in endpoints:
                    method = endpoint['method']
                    method_counts[method] = method_counts.get(method, 0) + 1
                
                for method, count in sorted(method_counts.items()):
                    click.echo(f"   {method}: {count} endpoints")
        else:
            click.echo("❌ OpenAPI specification is invalid", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error validating specification: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['json', 'table']), default='table', 
              help='Output format')
def list_endpoints(spec_file: str, format: str):
    """List all endpoints in an OpenAPI specification."""
    
    try:
        parser = OpenAPIParser()
        if not parser.load_from_file(spec_file):
            click.echo("❌ Error: Failed to parse OpenAPI specification", err=True)
            sys.exit(1)
        
        endpoints = parser.parse_endpoints()
        
        if format == 'json':
            click.echo(json.dumps(endpoints, indent=2))
        else:
            click.echo(f"📋 Endpoints in {spec_file}:")
            click.echo()
            click.echo(f"{'Method':<8} {'Path':<40} {'Summary'}")
            click.echo("-" * 80)
            
            for endpoint in endpoints:
                method = endpoint['method']
                path = endpoint['path']
                summary = endpoint.get('summary', '')[:30]
                click.echo(f"{method:<8} {path:<40} {summary}")
            
            click.echo()
            click.echo(f"Total endpoints: {len(endpoints)}")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
def serve(host: str, port: int, debug: bool):
    """Start the web interface server."""
    
    try:
        click.echo("🌐 Starting APITestGen web server...")
        click.echo(f"   URL: http://{host}:{port}")
        click.echo("   Press Ctrl+C to stop")
        click.echo()
        
        from .app import app
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        click.echo("\n👋 Server stopped")
    except Exception as e:
        click.echo(f"❌ Error starting server: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('test_script', type=click.Path(exists=True))
@click.option('--timeout', default=30, help='Request timeout in seconds')
@click.option('--output', '-o', help='Output file for test results')
def run_tests(test_script: str, timeout: int, output: Optional[str]):
    """Run generated test scripts."""
    
    try:
        if test_script.endswith('.py'):
            click.echo(f"🐍 Running Python test script: {test_script}")
            import subprocess
            result = subprocess.run([sys.executable, test_script], 
                                  capture_output=True, text=True, timeout=timeout*10)
            
            click.echo(result.stdout)
            if result.stderr:
                click.echo(result.stderr, err=True)
            
            if result.returncode != 0:
                sys.exit(result.returncode)
                
        elif test_script.endswith('.sh'):
            click.echo(f"🐚 Running shell test script: {test_script}")
            import subprocess
            result = subprocess.run(['bash', test_script], 
                                  capture_output=True, text=True, timeout=timeout*10)
            
            click.echo(result.stdout)
            if result.stderr:
                click.echo(result.stderr, err=True)
            
            if result.returncode != 0:
                sys.exit(result.returncode)
        else:
            click.echo("❌ Error: Unsupported test script format", err=True)
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        click.echo("❌ Error: Test execution timed out", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error running tests: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def examples():
    """Show usage examples."""
    
    click.echo("📚 APITestGen Usage Examples:")
    click.echo()
    
    click.echo("1. Generate test cases from OpenAPI spec:")
    click.echo("   api-test-gen generate api-spec.yaml")
    click.echo()
    
    click.echo("2. Generate with AI enhancement:")
    click.echo("   api-test-gen generate api-spec.yaml --use-ai --openai-key YOUR_KEY")
    click.echo()
    
    click.echo("3. Export specific formats:")
    click.echo("   api-test-gen generate api-spec.yaml -f csv -f json -f shell")
    click.echo()
    
    click.echo("4. Validate OpenAPI specification:")
    click.echo("   api-test-gen validate api-spec.yaml")
    click.echo()
    
    click.echo("5. List endpoints:")
    click.echo("   api-test-gen list-endpoints api-spec.yaml")
    click.echo()
    
    click.echo("6. Start web interface:")
    click.echo("   api-test-gen serve --port 8080")
    click.echo()
    
    click.echo("7. Run generated test script:")
    click.echo("   api-test-gen run-tests output/api_test_script_*.py")
    click.echo()


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()