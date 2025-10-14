"""
Unit tests for utility functions.
"""

import json
import pytest
from pydantic import BaseModel, ValidationError
from typing import List, Optional

from core.utils import ensure_json_format


class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""
    name: str
    age: int
    email: Optional[str] = None
    tags: List[str] = []


class TestEnsureJsonFormat:
    """Test cases for ensure_json_format function."""

    def test_valid_json_string(self):
        """Test with valid JSON string."""
        json_str = '{"name": "John", "age": 30, "email": "john@example.com"}'
        result = ensure_json_format(json_str, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "John"
        assert result.age == 30
        assert result.email == "john@example.com"

    def test_valid_json_with_arrays(self):
        """Test with valid JSON containing arrays."""
        json_str = '{"name": "Alice", "age": 25, "tags": ["python", "developer"]}'
        result = ensure_json_format(json_str, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "Alice"
        assert result.age == 25
        assert result.tags == ["python", "developer"]

    def test_minimal_valid_json(self):
        """Test with minimal required fields."""
        json_str = '{"name": "Bob", "age": 35}'
        result = ensure_json_format(json_str, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "Bob"
        assert result.age == 35
        assert result.email is None
        assert result.tags == []

    def test_json_embedded_in_text(self):
        """Test extraction of JSON from text."""
        text = 'Here is the result: {"name": "Charlie", "age": 40} and some more text'
        result = ensure_json_format(text, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "Charlie"
        assert result.age == 40

    def test_complex_json_embedded_in_text(self):
        """Test extraction of complex JSON from text."""
        text = '''
        The analysis shows the following data:
        {"name": "David", "age": 28, "email": "david@test.com", "tags": ["analysis", "data"]}
        This concludes our findings.
        '''
        result = ensure_json_format(text, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "David"
        assert result.age == 28
        assert result.email == "david@test.com"
        assert result.tags == ["analysis", "data"]

    def test_invalid_json_format(self):
        """Test with invalid JSON format."""
        invalid_json = '{"name": "John", "age": }'  # Missing value
        
        with pytest.raises(Exception):  # Should raise some parsing exception
            ensure_json_format(invalid_json, SampleModel)

    def test_json_with_validation_error(self):
        """Test with JSON that fails model validation."""
        # Missing required field 'name'
        json_str = '{"age": 30}'
        
        with pytest.raises(ValidationError):
            ensure_json_format(json_str, SampleModel)

    def test_json_with_wrong_data_types(self):
        """Test with JSON containing wrong data types."""
        # Age should be int, not string
        json_str = '{"name": "John", "age": "thirty"}'
        
        with pytest.raises(ValidationError):
            ensure_json_format(json_str, SampleModel)

    def test_nested_json_extraction(self):
        """Test extraction with nested JSON structures."""
        text = '''
        Some text with nested braces { and } chars.
        The actual data: {"name": "Eve", "age": 32}
        More text with { random } braces.
        '''
        result = ensure_json_format(text, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "Eve"
        assert result.age == 32

    def test_multiple_json_objects_takes_first(self):
        """Test that multiple JSON objects returns the first valid one."""
        text = '''
        First object: {"name": "First", "age": 25}
        Second object: {"name": "Second", "age": 30}
        '''
        result = ensure_json_format(text, SampleModel)
        
        # Should extract the first complete JSON object
        assert isinstance(result, SampleModel)
        assert result.name == "First"
        assert result.age == 25

    def test_malformed_embedded_json(self):
        """Test with malformed JSON embedded in text."""
        text = 'Here is bad JSON: {"name": "John", "age":} and more text'
        
        with pytest.raises(Exception):
            ensure_json_format(text, SampleModel)

    def test_no_json_in_text(self):
        """Test with text containing no JSON."""
        text = "This is just plain text with no JSON objects"
        
        with pytest.raises(Exception):
            ensure_json_format(text, SampleModel)