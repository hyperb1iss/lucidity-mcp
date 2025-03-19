# Lucidity MCP

## Clarity in Code, Confidence in Creation

Lucidity is a Model Context Protocol (MCP) server designed to enhance the quality of AI-generated code through intelligent, prompt-based analysis. By providing structured guidance to AI coding assistants, Lucidity helps identify and address common quality issues, resulting in cleaner, more maintainable, and more robust code.

## The Problem

AI coding assistants are revolutionizing software development, but they come with unique challenges:

- AI often produces unnecessarily complex or overengineered solutions
- Generated code may reference non-existent APIs or libraries ("hallucinations")
- AI sometimes inadvertently removes or modifies important existing code
- Generated code can be inconsistent with project style or patterns
- Edge cases and error handling may be incomplete
- Security vulnerabilities might be introduced unintentionally

Developers spend significant time reviewing and correcting these issues, reducing the efficiency gains from using AI assistants.

## Solution

Lucidity bridges this gap by providing AI assistants with a specialized tool that guides them to perform thorough code quality analysis. Rather than implementing complex code analysis algorithms, Lucidity leverages the AI's own capabilities by generating comprehensive, structured prompts that focus the AI's attention on critical quality dimensions.

## Key Features

- **Comprehensive Issue Detection**: Covers 10 critical quality dimensions, from complexity to security vulnerabilities
- **Contextual Analysis**: Compares changes against original code to identify unintended modifications
- **Language Agnostic**: Works with any programming language the AI assistant understands
- **Focused Analysis**: Option to target specific issue types based on project needs
- **Structured Outputs**: Guides AI to provide actionable feedback with clear recommendations
- **MCP Integration**: Seamless integration with Claude and other MCP-compatible AI assistants
- **Lightweight Implementation**: Simple server design with minimal dependencies
- **Extensible Framework**: Easy to add new issue types or refine analysis criteria
- **Flexible Transport**: Supports both stdio for terminal-based interaction and SSE for network-based communication
- **Git-Aware Analysis**: Analyzes changes directly from git diff, making it ideal for pre-commit reviews

## Target Audience

- **Software Development Teams** using AI coding assistants for production work
- **Individual Developers** looking to improve AI-generated code quality
- **AI Tool Builders** seeking to enhance their coding assistants' capabilities
- **Code Reviewers** wanting structured guidelines for evaluating AI-generated code
- **Technical Educators** teaching best practices for working with AI assistants

## Use Cases

1. **Pre-commit Quality Check**: Before committing AI-generated code, run a Lucidity analysis to catch potential issues
2. **Code Review Assistance**: Use Lucidity to provide a structured framework for reviewing AI contributions
3. **Learning Tool**: Help developers understand common pitfalls in AI-generated code
4. **Continuous Improvement**: Track common issues to refine prompting strategies and workflows
5. **Cross-Language Standardization**: Apply consistent quality criteria across different programming languages
6. **CI/CD Integration**: Add Lucidity checks to your continuous integration pipeline to maintain code quality standards

## Technical Overview

Lucidity is built on the Model Context Protocol (MCP), allowing it to integrate with compatible AI assistants like Claude. When an assistant invokes Lucidity's analysis tool, it receives a structured prompt that guides its analysis process, resulting in consistent, high-quality feedback without requiring complex backend analysis algorithms.

### Architecture

- **FastMCP Core**: Built on the FastMCP SDK for robust MCP protocol implementation
- **Dual Transport Layer**:
  - **stdio transport** for terminal-based interaction
  - **SSE transport** for network-based communication
- **Git Integration**: Extracts and processes changes directly from git diffs
- **Language Detection**: Automatically detects programming languages for context-aware analysis
- **Prompt Engine**: Generates sophisticated analysis prompts tailored to specific code contexts

### Technical Requirements

- Python 3.10+
- Git repository access
- Compatible MCP client (Claude, etc.)
- Optional: Web server capability for SSE transport

## Benefits

- **Improved Code Quality**: Catch issues before they enter your codebase
- **Reduced Review Time**: Structured analysis makes reviews faster and more thorough
- **Educational Value**: Help developers learn to identify common AI coding pitfalls
- **Consistency**: Apply the same quality standards across all AI-assisted development
- **Adaptability**: Works with any programming language or framework
- **Integration**: Fits into existing development workflows with MCP-compatible assistants
- **Lightweight**: Minimal system requirements and dependencies

