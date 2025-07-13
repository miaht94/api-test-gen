from setuptools import setup, find_packages

setup(
    name="api-test-gen",
    version="1.0.0",
    description="Generate API Test Scripts from Swagger/OpenAPI specifications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="APITestGen Team",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0.0",
        "openapi-spec-validator>=0.7.1",
        "pyyaml>=6.0.1",
        "requests>=2.31.0",
        "openai>=1.12.0",
        "click>=8.1.7",
        "jsonschema>=4.21.1",
        "pandas>=2.2.0",
        "jinja2>=3.1.3",
        "pydantic>=2.5.3",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "api-test-gen=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)