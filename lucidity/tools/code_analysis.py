"""
Code analysis tools for Lucidity.

This module provides tools for analyzing code quality using MCP.
"""

import os
import subprocess
from typing import Any

from ..context import mcp
from ..log import logger


def get_git_diff(workspace_root: str, path: str | None = None) -> tuple[str, str]:
    """Get the current git diff and the staged files content.

    Args:
        workspace_root: The root directory of the workspace/git repository
        path: Optional specific file path to get diff for

    Returns:
        Tuple of (diff_content, staged_files_content)
    """
    logger.debug("Getting git diff%s in workspace %s", f" for path: {path}" if path else "", workspace_root)

    try:
        if not os.path.exists(os.path.join(workspace_root, ".git")):
            logger.error("No .git directory found in workspace root: %s", workspace_root)
            return "", ""

        # Store current directory
        current_dir = os.getcwd()
        logger.debug("Current directory before: %s", current_dir)

        # Change to workspace root
        os.chdir(workspace_root)
        logger.debug("Changed to workspace root: %s", os.getcwd())

        try:
            # Get the git repository root to verify we're in the right place
            git_root = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
            ).stdout.strip()
            logger.debug("Git root directory: %s", git_root)

            # Get the diff
            diff_command = ["git", "diff"]
            if path:
                # Normalize path for Windows/WSL
                normalized_path = path.replace("\\", "/")
                diff_command.append(normalized_path)

            logger.debug("Running diff command: %s", diff_command)
            diff = subprocess.run(diff_command, capture_output=True, text=True, check=True).stdout
            logger.debug("Git diff size: %d bytes", len(diff))

            # Get the staged files content
            staged_command = ["git", "diff", "--cached"]
            if path:
                staged_command.append(normalized_path)

            logger.debug("Running staged command: %s", staged_command)
            staged = subprocess.run(staged_command, capture_output=True, text=True, check=True).stdout
            logger.debug("Git staged diff size: %d bytes", len(staged))

            return diff, staged

        finally:
            # Change back to the original directory
            logger.debug("Changing back to original directory: %s", current_dir)
            os.chdir(current_dir)

    except subprocess.CalledProcessError as e:
        logger.error("Error getting git diff: %s (output: %s)", e, e.output)
        return "", ""
    except Exception as e:
        logger.error("Unexpected error getting git diff: %s", e)
        return "", ""


def parse_git_diff(diff_content: str) -> dict[str, dict[str, Any]]:
    """Parse git diff content into a structured format.

    Args:
        diff_content: Raw git diff content

    Returns:
        Dictionary mapping filenames to their diff info
    """
    result: dict[str, dict[str, Any]] = {}
    current_file: str | None = None
    current_content: list[str] = []

    lines = diff_content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for file header
        if line.startswith("diff --git "):
            # Save previous file content if any
            if current_file is not None:
                result[current_file]["content"] = "\n".join(current_content)
                current_content = []

            # Extract filename from diff header
            parts = line.split(" ")
            if len(parts) >= 3:
                file_path = parts[2][2:]  # Remove 'a/' prefix
                current_file = file_path
                result[current_file] = {"status": "modified", "content": "", "original_content": ""}

            # Skip file metadata lines
            while i + 1 < len(lines) and not lines[i + 1].startswith("@@"):
                i += 1

                # Check for file status
                if i < len(lines) and current_file is not None:
                    if lines[i].startswith("new file"):
                        result[current_file]["status"] = "added"
                    elif lines[i].startswith("deleted file"):
                        result[current_file]["status"] = "deleted"
                    elif lines[i].startswith("rename from"):
                        result[current_file]["status"] = "renamed"

        # Collect diff content
        elif current_file is not None and (line.startswith(("+", "-", " "))):
            current_content.append(line)

        i += 1

    # Save the last file content
    if current_file is not None and current_content:
        result[current_file]["content"] = "\n".join(current_content)

    return result


def extract_code_from_diff(diff_info: dict[str, Any]) -> tuple[str, str]:
    """Extract the original and modified code from diff info.

    Args:
        diff_info: Dictionary containing diff information

    Returns:
        Tuple of (original_code, modified_code)
    """
    original_lines = []
    modified_lines = []

    # Process the diff content
    for line in diff_info["content"].split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            # Line added
            modified_lines.append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            # Line removed
            original_lines.append(line[1:])
        elif line.startswith(" "):
            # Line unchanged
            original_lines.append(line[1:])
            modified_lines.append(line[1:])

    return "\n".join(original_lines), "\n".join(modified_lines)


def detect_language(filename: str) -> str:
    """Detect the programming language based on file extension.

    Args:
        filename: The name of the file

    Returns:
        The detected language or 'text' if unknown
    """
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "jsx",
        ".tsx": "tsx",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".kt": "kotlin",
        ".kts": "kotlin",
        ".sh": "bash",
        ".md": "markdown",
        ".json": "json",
        ".xml": "xml",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
    }

    _, ext = os.path.splitext(filename)
    return extension_map.get(ext.lower(), "text")


@mcp.tool("analyze_code_quality")
def analyze_code_quality(
    workspace_root: str = "", path: str = "", focus_areas: list[str] | None = None
) -> dict[str, Any]:
    """Analyze code quality using AI.

    This tool examines the current git diff, extracts changed code,
    and uses AI to analyze it for quality issues.

    Args:
        workspace_root: The root directory of the workspace/git repository
        path: Optional specific file path to analyze
        focus_areas: Optional list of quality dimensions to focus on

    Returns:
        Analysis results including issues found and recommendations
    """
    if focus_areas is None:
        focus_areas = []
    logger.info("Starting code quality analysis%s in workspace %s", f" for {path}" if path else "", workspace_root)
    if focus_areas:
        logger.info("Focus areas: %s", focus_areas)

    if not workspace_root:
        return {"status": "error", "message": "workspace_root parameter is required"}

    # Get git diff
    logger.debug("Fetching git diff...")
    diff_content, staged_content = get_git_diff(workspace_root, path)

    # Combine diff and staged content for complete changes
    combined_diff = diff_content
    if staged_content:
        combined_diff = combined_diff + "\n" + staged_content if combined_diff else staged_content

    logger.debug("Combined diff size: %d bytes", len(combined_diff))

    if not combined_diff:
        logger.warning("No changes detected in git diff")
        return {"status": "no_changes", "message": "No changes detected in the git diff"}

    # Parse the diff
    logger.debug("Parsing git diff...")
    parsed_diff = parse_git_diff(combined_diff)

    if not parsed_diff:
        logger.warning("No parseable changes in git diff")
        return {"status": "no_changes", "message": "No parseable changes detected in the git diff"}

    logger.info("Found %d files with changes to analyze", len(parsed_diff))

    # Process each changed file
    analysis_results = {}

    for filename, diff_info in parsed_diff.items():
        logger.debug("Processing file: %s (status: %s)", filename, diff_info["status"])

        # Skip certain files
        if filename.endswith((".lock", ".sum", ".mod", "package-lock.json", "yarn.lock", ".DS_Store")):
            logger.debug("Skipping excluded file: %s", filename)
            continue

        try:
            # Extract original and modified code
            logger.debug("Extracting code changes for %s", filename)
            original_code, modified_code = extract_code_from_diff(diff_info)

            # Skip if no significant code changes
            if len(modified_code.strip()) < 10:
                logger.debug("Skipping %s - insufficient code changes (< 10 chars)", filename)
                continue

            # Detect language
            language = detect_language(filename)
            logger.debug("Detected language for %s: %s", filename, language)

            # Create a prompt for analysis
            logger.debug("Generating analysis prompt for %s", filename)
            from ..prompts import analyze_code_prompt

            analysis_prompt = analyze_code_prompt(
                code=modified_code,
                language=language,
                original_code=original_code if original_code else None,
                focus_areas=focus_areas,
            )
            logger.debug("Generated analysis prompt of size: %d chars", len(analysis_prompt))

            # Store the analysis prompt to be returned
            analysis_results[filename] = {
                "status": diff_info["status"],
                "language": language,
                "analysis_prompt": analysis_prompt,
            }
            logger.info("Successfully analyzed %s", filename)

        except Exception as e:
            logger.error("Error analyzing %s: %s", filename, e)
            analysis_results[filename] = {"status": "error", "message": f"Error analyzing file: {e!s}"}

    logger.info("Code analysis complete - processed %d files", len(analysis_results))

    # Return results with instructions for AI analysis
    return {
        "status": "success",
        "file_count": len(analysis_results),
        "results": analysis_results,
        "instructions": """
Please analyze the code changes using the provided analysis prompt(s).
For each file in the results:

1. Read the analysis_prompt which contains:
   - The code to analyze
   - Original code (if available)
   - Analysis dimensions to consider
   - Detailed instructions for analysis

2. Follow the prompt's format to provide:
   - Analysis for each relevant dimension
   - Severity levels for issues found
   - Line-specific explanations
   - Concrete improvement recommendations
   - Final summary of critical issues

3. After analyzing all files, provide:
   - Overall assessment of code quality
   - Prioritized list of improvements
   - Any patterns or systemic issues found

Your analysis should be thorough but focused on actionable improvements.
""",
    }
