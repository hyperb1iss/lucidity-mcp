"""
Lucidity prompts module.

This module defines the prompt templates used for code quality analysis.
"""

from typing import Dict, List, Optional

from .context import mcp

# Define the base prompt for code analysis
BASE_ANALYSIS_PROMPT = """
# Code Quality Analysis

You are performing a comprehensive code quality analysis on the provided code. 
Your task is to identify potential quality issues across multiple dimensions and provide 
constructive feedback to improve the code.

## Code to Analyze

```{language}
{code}
```

{diff_section}

## Analysis Dimensions

Analyze the code for the following quality dimensions:
{dimensions}

## Instructions

1. For each applicable dimension, identify specific issues in the code
2. Provide a severity level for each issue (Critical, High, Medium, Low)
3. Explain why each issue is problematic, with reference to specific line numbers
4. Suggest concrete improvements to address each issue
5. If no issues are found in a dimension, explicitly state that

## Response Format

Organize your analysis by dimension as follows:

### [Dimension Name]

**Issues Found**: [Yes/No]

[If issues are found, list each one as follows]

- **Issue**: [Brief description]
- **Severity**: [Critical/High/Medium/Low]
- **Location**: [Line number(s)]
- **Explanation**: [Why this is a problem]
- **Recommendation**: [Specific improvement suggestion]

## Final Summary

After analyzing all dimensions, provide a concise summary of:
1. The most critical issues to address
2. Overall code quality assessment
3. Key recommendations for improvement
"""

# Define the code quality dimensions with descriptions
QUALITY_DIMENSIONS = {
    "complexity": """
    **Unnecessary Complexity**
    - Overly complex algorithms or functions
    - Unnecessary abstraction layers
    - Convoluted control flow
    - Functions/methods that are too long or have too many parameters
    - Nesting levels that are too deep
    """,
    
    "abstraction": """
    **Poor Abstractions**
    - Inappropriate use of design patterns
    - Missing abstractions where needed
    - Leaky abstractions that expose implementation details
    - Overly generic abstractions that add complexity
    - Unclear separation of concerns
    """,
    
    "deletion": """
    **Unintended Code Deletion**
    - Critical functionality removed without replacement
    - Incomplete removal of deprecated code
    - Breaking changes to public APIs
    - Removed error handling or validation
    - Missing edge case handling present in original code
    """,
    
    "hallucination": """
    **Hallucinated Components**
    - References to non-existent functions, classes, or modules
    - Assumptions about available libraries or APIs
    - Inconsistent or impossible behavior expectations
    - References to frameworks or patterns not used in the project
    - Creation of interfaces that don't align with the codebase
    """,
    
    "style": """
    **Style Inconsistencies**
    - Deviation from project coding standards
    - Inconsistent naming conventions
    - Inconsistent formatting or indentation
    - Inconsistent comment styles or documentation
    - Mixing of different programming paradigms
    """,
    
    "security": """
    **Security Vulnerabilities**
    - Injection vulnerabilities (SQL, Command, etc.)
    - Insecure data handling or storage
    - Authentication or authorization flaws
    - Exposure of sensitive information
    - Unsafe dependencies or API usage
    """,
    
    "performance": """
    **Performance Issues**
    - Inefficient algorithms or data structures
    - Unnecessary computations or operations
    - Resource leaks (memory, file handles, etc.)
    - Excessive network or disk operations
    - Blocking operations in asynchronous code
    """,
    
    "duplication": """
    **Code Duplication**
    - Repeated logic or functionality
    - Copy-pasted code with minor variations
    - Duplicate functionality across different modules
    - Redundant validation or error handling
    - Parallel hierarchies or structures
    """,
    
    "error_handling": """
    **Incomplete Error Handling**
    - Missing try-catch blocks for risky operations
    - Overly broad exception handling
    - Swallowed exceptions without proper logging
    - Unclear error messages or codes
    - Inconsistent error recovery strategies
    """,
    
    "testing": """
    **Test Coverage Gaps**
    - Missing unit tests for critical functionality
    - Uncovered edge cases or error paths
    - Brittle tests that make inappropriate assumptions
    - Missing integration or system tests
    - Tests that don't verify actual requirements
    """
}

# Format dimensions for inclusion in the prompt
def format_dimensions(selected_dimensions: Optional[List[str]] = None) -> str:
    """Format selected dimensions for inclusion in the prompt.
    
    Args:
        selected_dimensions: List of dimension keys to include, or None for all
        
    Returns:
        Formatted dimensions string for the prompt
    """
    dimensions = selected_dimensions or list(QUALITY_DIMENSIONS.keys())
    formatted = ""
    
    for dim in dimensions:
        if dim in QUALITY_DIMENSIONS:
            formatted += QUALITY_DIMENSIONS[dim] + "\n"
    
    return formatted


def generate_analysis_prompt(
    code: str,
    language: str,
    original_code: Optional[str] = None,
    selected_dimensions: Optional[List[str]] = None
) -> str:
    """Generate a complete analysis prompt for the given code.
    
    Args:
        code: The code to analyze
        language: The programming language of the code
        original_code: The original code (if performing diff analysis)
        selected_dimensions: Specific dimensions to analyze, or None for all
        
    Returns:
        Complete analysis prompt
    """
    # Format the dimensions section
    dimensions_text = format_dimensions(selected_dimensions)
    
    # Generate diff section if original code is provided
    diff_section = ""
    if original_code:
        diff_section = f"""
## Original Code (for comparison)

```{language}
{original_code}
```

When analyzing, pay particular attention to changes between the original and new code.
Identify any regressions, unintended modifications, or improvements.
"""
    
    # Build the complete prompt
    prompt = BASE_ANALYSIS_PROMPT.format(
        language=language,
        code=code,
        diff_section=diff_section,
        dimensions=dimensions_text
    )
    
    return prompt


@mcp.prompt("analyze_code")
def analyze_code_prompt(
    code: str,
    language: str,
    original_code: Optional[str] = None,
    focus_areas: Optional[List[str]] = None
) -> str:
    """Generate a prompt for analyzing code quality.
    
    Args:
        code: The code to analyze
        language: The programming language of the code
        original_code: The original code for comparison (optional)
        focus_areas: Specific quality dimensions to focus on (optional)
        
    Returns:
        A formatted prompt for code analysis
    """
    return generate_analysis_prompt(code, language, original_code, focus_areas) 