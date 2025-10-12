# Python Coding Standards and Style Guide

## Overview

This document establishes coding standards and style guidelines for Python development within our organization. These standards ensure code consistency, maintainability, and readability across all Python projects.

## Code Style Standards

### PEP 8 Compliance

All Python code must adhere to PEP 8 guidelines with the following specific requirements:

**Line Length:**
- Maximum line length: 88 characters (Black formatter standard)
- Use implicit line continuation inside parentheses, brackets, and braces
- Use backslashes for line continuation only when necessary

**Indentation:**
- Use 4 spaces per indentation level
- Never mix tabs and spaces
- Continuation lines should align wrapped elements vertically

**Imports:**
```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import requests
import pandas as pd
from flask import Flask, request

# Local application imports
from myproject.models import User
from myproject.utils import helper_function
```

**Naming Conventions:**
- Variables and functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private attributes: `_leading_underscore`
- Modules: `lowercase` or `snake_case`

### Code Formatting

**Mandatory Tools:**
- **Black**: Code formatter (line length: 88)
- **isort**: Import sorting
- **flake8**: Linting with specific configuration
- **mypy**: Type checking

**Pre-commit Configuration:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

## Code Quality Standards

### Type Hints

**Mandatory for all new code:**
```python
from typing import List, Dict, Optional, Union
from pathlib import Path

def process_data(
    input_file: Path,
    output_format: str = "json",
    options: Optional[Dict[str, str]] = None
) -> Dict[str, Union[str, int]]:
    """Process data file and return results."""
    if options is None:
        options = {}
    
    # Implementation here
    return {"status": "success", "records": 100}
```

### Documentation Standards

**Docstring Format (Google Style):**
```python
def calculate_metrics(data: List[Dict[str, float]], metric_type: str) -> Dict[str, float]:
    """Calculate statistical metrics for the given data.
    
    Args:
        data: List of dictionaries containing numerical data points.
        metric_type: Type of metric to calculate ('mean', 'median', 'std').
        
    Returns:
        Dictionary containing calculated metrics with metric names as keys.
        
    Raises:
        ValueError: If metric_type is not supported.
        TypeError: If data contains non-numerical values.
        
    Example:
        >>> data = [{"value": 1.0}, {"value": 2.0}, {"value": 3.0}]
        >>> calculate_metrics(data, "mean")
        {"mean": 2.0}
    """
```

### Error Handling

**Exception Handling Standards:**
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DataProcessingError(Exception):
    """Custom exception for data processing errors."""
    pass

def process_file(file_path: Path) -> Optional[Dict[str, str]]:
    """Process file with proper error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return {"content": content, "status": "success"}
    
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        raise DataProcessingError(f"Cannot access file: {file_path}")
    
    except Exception as e:
        logger.exception(f"Unexpected error processing {file_path}")
        raise DataProcessingError(f"Processing failed: {e}") from e
```

## Testing Standards

### Test Structure

**Test Organization:**
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_services.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
├── fixtures/
│   ├── sample_data.json
│   └── test_config.yaml
└── conftest.py
```

**Test Naming Convention:**
```python
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    """Test cases for UserService class."""
    
    def test_create_user_with_valid_data_returns_user_id(self):
        """Test that creating a user with valid data returns user ID."""
        # Arrange
        user_data = {"name": "John Doe", "email": "john@example.com"}
        
        # Act
        result = UserService.create_user(user_data)
        
        # Assert
        assert result is not None
        assert isinstance(result, str)
    
    def test_create_user_with_invalid_email_raises_validation_error(self):
        """Test that invalid email raises ValidationError."""
        # Arrange
        user_data = {"name": "John Doe", "email": "invalid-email"}
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid email format"):
            UserService.create_user(user_data)
```

### Coverage Requirements

**Minimum Coverage Targets:**
- Unit tests: 90% line coverage
- Integration tests: 80% feature coverage
- Critical paths: 100% coverage

**Coverage Configuration (.coveragerc):**
```ini
[run]
source = src/
omit = 
    */tests/*
    */venv/*
    */migrations/*
    */settings/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Security Standards

### Input Validation

**Always validate and sanitize inputs:**
```python
import re
from typing import Union

def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    # Remove path separators and dangerous characters
    sanitized = re.sub(r'[<>:"|?*\\\/]', '_', filename)
    # Remove leading dots and spaces
    sanitized = sanitized.lstrip('. ')
    return sanitized[:255]  # Limit length
```

### Secrets Management

**Never hardcode secrets:**
```python
import os
from typing import Optional

def get_database_url() -> str:
    """Get database URL from environment variables."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return db_url

# Use environment variables or secret management services
API_KEY = os.getenv('API_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
```

## Performance Standards

### Code Optimization

**Use appropriate data structures:**
```python
# Use sets for membership testing
valid_statuses = {"active", "inactive", "pending"}
if user_status in valid_statuses:
    process_user()

# Use list comprehensions for simple transformations
squared_numbers = [x**2 for x in range(10)]

# Use generators for large datasets
def process_large_file(file_path: Path):
    """Process large file line by line using generator."""
    with open(file_path, 'r') as file:
        for line in file:
            yield process_line(line)
```

### Memory Management

**Efficient resource usage:**
```python
from contextlib import contextmanager
import sqlite3

@contextmanager
def database_connection(db_path: str):
    """Context manager for database connections."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

# Usage
with database_connection('app.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
```

## Project Structure Standards

### Standard Project Layout

```
project_name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       ├── models/
│       ├── services/
│       ├── utils/
│       └── config/
├── tests/
├── docs/
├── scripts/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .github/
│   └── workflows/
├── pyproject.toml
├── README.md
├── .gitignore
├── .pre-commit-config.yaml
└── Dockerfile
```

### Configuration Management

**Environment-based configuration:**
```python
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class Config:
    """Application configuration."""
    debug: bool = False
    database_url: str = ""
    api_key: str = ""
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables."""
        return cls(
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            database_url=os.getenv('DATABASE_URL', ''),
            api_key=os.getenv('API_KEY', ''),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
```

## Compliance and Enforcement

### Automated Checks

**CI/CD Pipeline Requirements:**
1. Code formatting check (Black, isort)
2. Linting (flake8, pylint)
3. Type checking (mypy)
4. Security scanning (bandit)
5. Test execution and coverage
6. Documentation generation

### Code Review Checklist

**Mandatory Review Items:**
- [ ] Code follows PEP 8 and style guidelines
- [ ] All functions have type hints and docstrings
- [ ] Tests cover new functionality
- [ ] No hardcoded secrets or credentials
- [ ] Error handling is appropriate
- [ ] Performance considerations addressed
- [ ] Security implications reviewed

### Exceptions and Waivers

**Process for exceptions:**
1. Document technical justification
2. Get approval from tech lead
3. Add TODO comment with timeline
4. Track in technical debt backlog

---

**Document Version**: 2.1  
**Last Updated**: October 2024  
**Next Review**: January 2025  
**Owner**: Development Standards Committee
