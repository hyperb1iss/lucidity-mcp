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


def get_changed_files(workspace_root: str) -> list[str]:
    """Get a list of all modified files (both staged and unstaged).

    Args:
        workspace_root: The root directory of the workspace/git repository

    Returns:
        List of modified file paths
    """
    logger.debug("Getting changed files in workspace %s", workspace_root)

    try:
        if not os.path.exists(os.path.join(workspace_root, ".git")):
            logger.error("No .git directory found in workspace root: %s", workspace_root)
            return []

        # Store current directory
        current_dir = os.getcwd()

        # Change to workspace root
        os.chdir(workspace_root)

        try:
            # Get unstaged modified files
            unstaged_files = (
                subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True)
                .stdout.strip()
                .split("\n")
            )

            # Get staged modified files
            staged_files = (
                subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
                .stdout.strip()
                .split("\n")
            )

            # Combine and remove empty entries
            all_files = list(set(filter(None, unstaged_files + staged_files)))
            logger.debug("Found %d changed files", len(all_files))

            return all_files

        finally:
            # Change back to the original directory
            os.chdir(current_dir)

    except subprocess.CalledProcessError as e:
        logger.error("Error getting changed files: %s (output: %s)", e, e.output)
        return []
    except Exception as e:
        logger.error("Unexpected error getting changed files: %s", e)
        return []


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
    current_header: list[str] = []

    lines = diff_content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for file header
        if line.startswith("diff --git "):
            # Save previous file content if any
            if current_file is not None:
                result[current_file]["content"] = "\n".join(current_content)
                result[current_file]["header"] = "\n".join(current_header)
                current_content = []
                current_header = []

            # Extract filename from diff header
            parts = line.split(" ")
            if len(parts) >= 4:
                # Extract the canonical filename (b/ version)
                file_path = parts[3][2:]  # Remove 'b/' prefix
                current_file = file_path
                result[current_file] = {
                    "status": "modified",
                    "content": "",
                    "original_content": "",
                    "header": line,
                    "raw_diff": line + "\n",
                }
                current_header.append(line)

            # Skip file metadata lines and collect headers
            while i + 1 < len(lines) and not lines[i + 1].startswith("@@"):
                i += 1
                if i < len(lines) and current_file is not None:
                    current_header.append(lines[i])
                    result[current_file]["raw_diff"] += lines[i] + "\n"

                    # Check for file status
                    if lines[i].startswith("new file"):
                        result[current_file]["status"] = "added"
                    elif lines[i].startswith("deleted file"):
                        result[current_file]["status"] = "deleted"
                    elif lines[i].startswith("rename from"):
                        result[current_file]["status"] = "renamed"

        # Collect diff hunk headers
        elif current_file is not None and line.startswith("@@"):
            current_header.append(line)
            result[current_file]["raw_diff"] += line + "\n"

        # Collect diff content
        elif current_file is not None and (line.startswith(("+", "-", " "))):
            current_content.append(line)
            result[current_file]["raw_diff"] += line + "\n"

        i += 1

    # Save the last file content
    if current_file is not None and current_content:
        result[current_file]["content"] = "\n".join(current_content)
        result[current_file]["header"] = "\n".join(current_header)

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


@mcp.tool("analyze_changes")
def analyze_changes(workspace_root: str = "", path: str = "") -> dict[str, Any]:
    """Prepare git changes for analysis through MCP.

    This tool examines the current git diff, extracts changed code,
    and prepares structured data with context for the AI to analyze.

    The tool doesn't perform analysis itself - it formats the git diff data
    and provides analysis instructions which get passed back to the AI model
    through the Model Context Protocol.

    Args:
        workspace_root: The root directory of the workspace/git repository
        path: Optional specific file path to analyze

    Returns:
        Structured git diff data with analysis instructions for the AI
    """
    logger.info("Starting git change analysis%s in workspace %s", f" for {path}" if path else "", workspace_root)

    if not workspace_root:
        return {"status": "error", "message": "workspace_root parameter is required"}

    # Get git diff
    logger.debug("Fetching git diff...")
    diff_content, staged_content = get_git_diff(workspace_root, path)

    # Get list of all changed files
    changed_files = get_changed_files(workspace_root)

    # Combine diff and staged content for complete changes
    combined_diff = diff_content
    if staged_content:
        combined_diff = combined_diff + "\n" + staged_content if combined_diff else staged_content

    logger.debug("Combined diff size: %d bytes", len(combined_diff))

    if not combined_diff:
        logger.warning("No changes detected in git diff")
        return {"status": "no_changes", "message": "No changes detected in the git diff", "file_list": []}

    # Parse the diff
    logger.debug("Parsing git diff...")
    parsed_diff = parse_git_diff(combined_diff)

    if not parsed_diff:
        logger.warning("No parseable changes in git diff")
        return {
            "status": "no_changes",
            "message": "No parseable changes detected in the git diff",
            "file_list": changed_files,
        }

    logger.info("Found %d files with changes to analyze", len(parsed_diff))

    # Process each changed file
    analysis_results = {}
    file_list = []

    for filename, diff_info in parsed_diff.items():
        logger.debug("Processing file: %s (status: %s)", filename, diff_info["status"])
        file_list.append(filename)

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
            from ..prompts import analyze_changes_prompt

            analysis_prompt = analyze_changes_prompt(
                code=modified_code, language=language, original_code=original_code if original_code else None
            )
            logger.debug("Generated analysis prompt of size: %d chars", len(analysis_prompt))

            # Store the analysis prompt to be returned
            analysis_results[filename] = {
                "status": diff_info["status"],
                "language": language,
                "analysis_prompt": analysis_prompt,
                "raw_diff": diff_info["raw_diff"],
                "original_code": original_code,
                "modified_code": modified_code,
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
        "file_list": file_list,
        "all_changed_files": changed_files,
        "results": analysis_results,
        "instructions": """
This data contains git changes that you should analyze for code quality issues.
As an AI model receiving this through MCP, your task is to:

1. Review each changed file:
   - Examine the raw diff showing the exact changes
   - Compare the original and modified code
   - Consider the language and file status (added, modified, deleted)

2. For each file, perform the analysis following the provided analysis prompt:
   - Analyze relevant quality dimensions
   - Assign severity levels to issues you identify
   - Provide line-specific explanations
   - Suggest concrete improvements

3. After analyzing all files, provide:
   - An overall assessment of the code changes
   - A prioritized list of improvements
   - Any patterns or systemic issues you've identified

Your analysis should be thorough yet focused on actionable improvements.
""",
    }
