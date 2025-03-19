"""
Tests for prompts module.
"""

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
    assert "Git Change Analysis" in prompt_with_original  # Verify new prompt title
    assert "changes" in prompt_with_original  # Verify focus on changes
