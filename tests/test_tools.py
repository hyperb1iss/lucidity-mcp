"""
Tests for tools module.
"""

from unittest.mock import patch

from lucidity.tools.code_analysis import detect_language, extract_code_from_diff, parse_git_diff


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
    assert '-    print("Hello")' in result["example.py"]["content"]
    assert '+    print("Hello, world!")' in result["example.py"]["content"]


def test_extract_code_from_diff():
    """Test extracting original and modified code from diff."""
    diff_info = {
        "status": "modified",
        "content": """@@ -1,5 +1,6 @@
 def hello():
-    print("Hello")
+    print("Hello, world!")
+    return True

 hello()""",
    }

    original_code, modified_code = extract_code_from_diff(diff_info)

    assert "def hello():" in original_code
    assert 'print("Hello")' in original_code
    assert "return True" not in original_code

    assert "def hello():" in modified_code
    assert 'print("Hello, world!")' in modified_code
    assert "return True" in modified_code


@patch("lucidity.tools.code_analysis.subprocess.run")
def test_get_git_diff(mock_run):
    """Test getting git diff from repository."""
    from lucidity.tools.code_analysis import get_git_diff

    # Mock subprocess.run to return some test diff output
    mock_run.return_value.stdout = "test diff output"
    mock_run.return_value.returncode = 0

    # Patch os functions and path checks
    with (
        patch("lucidity.tools.code_analysis.os.getcwd") as mock_getcwd,
        patch("lucidity.tools.code_analysis.os.chdir") as mock_chdir,
        patch("lucidity.tools.code_analysis.os.path.exists") as mock_exists,
    ):
        mock_getcwd.return_value = "/current/dir"
        mock_exists.return_value = True  # Simulate .git directory exists

        # Call the function
        diff_content, staged_content = get_git_diff("/path/to/repo")

        # Verify correct commands were run
        assert mock_run.call_count >= 2  # Should call git diff and git diff --cached

        # Verify directory changes
        mock_chdir.assert_any_call("/path/to/repo")
        mock_chdir.assert_any_call("/current/dir")

        # Verify git commands
        calls = mock_run.call_args_list
        assert any("diff" in str(call) for call in calls)
        assert any("--cached" in str(call) for call in calls)

        # Verify output
        assert diff_content == "test diff output" or staged_content == "test diff output"
