"""
Tests for prompts module.
"""

import pytest

from lucidity.prompts import format_dimensions, generate_analysis_prompt


def test_format_dimensions():
    """Test that format_dimensions correctly formats selected dimensions."""
    # Test with specified dimensions
    dimensions = ["complexity", "security"]
    formatted = format_dimensions(dimensions)
    assert "Unnecessary Complexity" in formatted
    assert "Security Vulnerabilities" in formatted
    assert "Test Coverage Gaps" not in formatted
    
    # Test with all dimensions
    all_formatted = format_dimensions()
    assert "Unnecessary Complexity" in all_formatted
    assert "Security Vulnerabilities" in all_formatted
    assert "Test Coverage Gaps" in all_formatted


def test_generate_analysis_prompt():
    """Test that generate_analysis_prompt creates a valid prompt."""
    code = "def hello():\n    print('Hello, world!')"
    language = "python"
    
    # Basic prompt generation
    prompt = generate_analysis_prompt(code, language)
    assert code in prompt
    assert language in prompt
    assert "Original Code" not in prompt
    
    # Prompt with original code
    original_code = "def hello():\n    pass"
    prompt_with_original = generate_analysis_prompt(code, language, original_code)
    assert original_code in prompt_with_original
    assert "Original Code" in prompt_with_original
    
    # Prompt with selected dimensions
    prompt_with_dimensions = generate_analysis_prompt(
        code, 
        language, 
        selected_dimensions=["complexity", "security"]
    )
    assert "Unnecessary Complexity" in prompt_with_dimensions
    assert "Security Vulnerabilities" in prompt_with_dimensions
    assert "Test Coverage Gaps" not in prompt_with_dimensions 