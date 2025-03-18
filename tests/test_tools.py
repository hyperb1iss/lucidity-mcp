"""
Tests for tools module.
"""

import pytest
from unittest.mock import patch, MagicMock

from lucidity.tools.code_analysis import (
    detect_language,
    extract_code_from_diff,
    parse_git_diff
)


def test_detect_language():
    """Test language detection from file extensions."""
    assert detect_language("example.py") == "python"
    assert detect_language("styles.css") == "css"
    assert detect_language("app.js") == "javascript"
    assert detect_language("index.html") == "html"
    assert detect_language("unknown.xyz") == "text"


def test_parse_git_diff():
    """Test parsing git diff content."""
    diff_content = """diff --git a/example.py b/example.py
index abc123..def456 100644
--- a/example.py
+++ b/example.py
@@ -1,5 +1,6 @@
 def hello():
-    print("Hello")
+    print("Hello, world!")
+    return True
 
 hello()
"""
    
    result = parse_git_diff(diff_content)
    
    assert "example.py" in result
    assert result["example.py"]["status"] == "modified"
    assert "-    print(\"Hello\")" in result["example.py"]["content"]
    assert "+    print(\"Hello, world!\")" in result["example.py"]["content"]


def test_extract_code_from_diff():
    """Test extracting original and modified code from diff."""
    diff_info = {
        "status": "modified",
        "content": """@@ -1,5 +1,6 @@
 def hello():
-    print("Hello")
+    print("Hello, world!")
+    return True
 
 hello()"""
    }
    
    original_code, modified_code = extract_code_from_diff(diff_info)
    
    assert "def hello():" in original_code
    assert "print(\"Hello\")" in original_code
    assert "return True" not in original_code
    
    assert "def hello():" in modified_code
    assert "print(\"Hello, world!\")" in modified_code
    assert "return True" in modified_code


@patch("lucidity.tools.code_analysis.subprocess.run")
def test_get_git_diff(mock_run):
    """Test getting git diff from repository."""
    from lucidity.tools.code_analysis import get_git_diff
    
    # Mock the subprocess.run calls
    mock_process = MagicMock()
    mock_process.stdout = "/path/to/repo"
    mock_run.return_value = mock_process
    
    # Patch os functions
    with patch("lucidity.tools.code_analysis.os.getcwd") as mock_getcwd, \
         patch("lucidity.tools.code_analysis.os.chdir") as mock_chdir:
        
        mock_getcwd.return_value = "/current/dir"
        
        # Call the function
        get_git_diff("example.py")
        
        # Verify correct commands were run
        assert mock_run.call_count >= 3
        # Check that chdir was called to change to git root and back
        mock_chdir.assert_any_call("/path/to/repo")
        mock_chdir.assert_any_call("/current/dir") 