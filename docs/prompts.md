# Lucidity Prompts

This document contains sample prompts used by Lucidity for code quality analysis.

## Base Analysis Prompt

```
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
```

## Quality Dimensions

Lucidity analyzes code across the following dimensions:

1. **Unnecessary Complexity**
   - Overly complex algorithms or functions
   - Unnecessary abstraction layers
   - Convoluted control flow
   - Functions/methods that are too long or have too many parameters
   - Nesting levels that are too deep

2. **Poor Abstractions**
   - Inappropriate use of design patterns
   - Missing abstractions where needed
   - Leaky abstractions that expose implementation details
   - Overly generic abstractions that add complexity
   - Unclear separation of concerns

3. **Unintended Code Deletion**
   - Critical functionality removed without replacement
   - Incomplete removal of deprecated code
   - Breaking changes to public APIs
   - Removed error handling or validation
   - Missing edge case handling present in original code

4. **Hallucinated Components**
   - References to non-existent functions, classes, or modules
   - Assumptions about available libraries or APIs
   - Inconsistent or impossible behavior expectations
   - References to frameworks or patterns not used in the project
   - Creation of interfaces that don't align with the codebase

5. **Style Inconsistencies**
   - Deviation from project coding standards
   - Inconsistent naming conventions
   - Inconsistent formatting or indentation
   - Inconsistent comment styles or documentation
   - Mixing of different programming paradigms

6. **Security Vulnerabilities**
   - Injection vulnerabilities (SQL, Command, etc.)
   - Insecure data handling or storage
   - Authentication or authorization flaws
   - Exposure of sensitive information
   - Unsafe dependencies or API usage

7. **Performance Issues**
   - Inefficient algorithms or data structures
   - Unnecessary computations or operations
   - Resource leaks (memory, file handles, etc.)
   - Excessive network or disk operations
   - Blocking operations in asynchronous code

8. **Code Duplication**
   - Repeated logic or functionality
   - Copy-pasted code with minor variations
   - Duplicate functionality across different modules
   - Redundant validation or error handling
   - Parallel hierarchies or structures

9. **Incomplete Error Handling**
   - Missing try-catch blocks for risky operations
   - Overly broad exception handling
   - Swallowed exceptions without proper logging
   - Unclear error messages or codes
   - Inconsistent error recovery strategies

10. **Test Coverage Gaps**
    - Missing unit tests for critical functionality
    - Uncovered edge cases or error paths
    - Brittle tests that make inappropriate assumptions
    - Missing integration or system tests
    - Tests that don't verify actual requirements

## Example Response

```
### Unnecessary Complexity

**Issues Found**: Yes

- **Issue**: Deeply nested conditional logic
- **Severity**: High
- **Location**: Lines 15-42
- **Explanation**: The function contains 5 levels of nested if-statements, making the code difficult to understand and maintain. The cognitive load to trace execution paths is very high.
- **Recommendation**: Extract conditional blocks into well-named helper functions and consider using early returns or the guard clause pattern to reduce nesting.

### Security Vulnerabilities

**Issues Found**: Yes

- **Issue**: SQL Injection vulnerability
- **Severity**: Critical
- **Location**: Line 78
- **Explanation**: User input is directly concatenated into an SQL query string, allowing potential attackers to inject malicious SQL commands.
- **Recommendation**: Use parameterized queries or prepared statements instead of string concatenation.

...

## Final Summary

The most critical issues to address are:
1. SQL Injection vulnerability (Critical)
2. Deeply nested conditional logic (High)
3. Missing error handling for network operations (High)

Overall, the code is moderately problematic with several high-severity issues that should be addressed before deployment. The main areas for improvement are security, complexity reduction, and error handling.

Key recommendations:
1. Implement proper SQL parameterization to prevent injection attacks
2. Refactor deeply nested conditional logic using helper functions and early returns
3. Add proper error handling for all network operations and external calls
