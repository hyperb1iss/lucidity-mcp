# Lucidity MCP

## Clarity in Code, Confidence in Creation

Lucidity is a Model Context Protocol (MCP) server designed to enhance the quality of AI-generated code through intelligent, prompt-based analysis. By providing structured guidance to AI coding assistants, Lucidity helps identify and address common quality issues, resulting in cleaner, more maintainable, and more robust code.

## Features

- **Comprehensive Issue Detection**: Covers 10 critical quality dimensions, from complexity to security vulnerabilities
- **Contextual Analysis**: Compares changes against original code to identify unintended modifications
- **Language Agnostic**: Works with any programming language the AI assistant understands
- **Focused Analysis**: Option to target specific issue types based on project needs
- **Structured Outputs**: Guides AI to provide actionable feedback with clear recommendations
- **MCP Integration**: Seamless integration with Claude and other MCP-compatible AI assistants

## Installation

### Prerequisites

- Python 3.13 or higher
- Git (for analyzing code changes)

### Install from source

```bash
# Clone the repository
git clone https://github.com/hyperbliss/lucidity-mcp.git
cd lucidity-mcp

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package and dependencies
pip install -e .
```

## Usage

### Running the server

```bash
# Run with stdio transport (for terminal use)
lucidity

# Run with SSE transport (for network use)
lucidity --transport sse --host 127.0.0.1 --port 6969

# Run with debug logging
lucidity --debug
```

### Command-line options

```
usage: lucidity [-h] [--debug] [--host HOST] [--port PORT] [--transport {stdio,sse}]
                [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--verbose]

Lucidity MCP Server

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  --host HOST           Host to bind the server to (use 0.0.0.0 for all interfaces)
  --port PORT           Port to listen on for network connections
  --transport {stdio,sse}
                        Transport type to use (stdio for terminal, sse for network)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level
  --verbose             Enable verbose logging for HTTP requests
```

## Integration with AI Assistants

Lucidity can be used with any MCP-compatible AI assistant, such as Claude. The assistant can invoke the `analyze_code_quality` tool to get detailed code quality feedback.

Example usage in a Claude conversation:

```
User: Can you help me improve the quality of this code?

Claude: I'd be happy to help! Let me analyze your code using the Lucidity tool to identify potential quality issues.

[Claude uses the analyze_code_quality tool]

Based on the Lucidity analysis, here are the key issues I've identified and my recommendations for improvement...
```

## Development

### Running tests

```bash
pytest
```

### Building the package

```bash
pip install build
python -m build
```

## License

Apache License 2.0
