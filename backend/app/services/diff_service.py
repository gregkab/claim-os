"""Diff computation service."""
import difflib
from typing import Tuple


def compute_unified_diff(old_content: str, new_content: str, old_name: str = "old", new_name: str = "new") -> str:
    """
    Compute unified diff between old and new content.
    
    Args:
        old_content: Old content string
        new_content: New content string
        old_name: Name for old content (for diff header)
        new_name: Name for new content (for diff header)
    
    Returns:
        Unified diff string
    """
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=old_name,
        tofile=new_name,
        lineterm=''
    )
    
    return ''.join(diff)


def compute_diff(old_content: str, new_content: str) -> Tuple[str, str, str]:
    """
    Compute diff and return old, new, and diff strings.
    
    Returns:
        Tuple of (old_content, new_content, diff_string)
    """
    diff = compute_unified_diff(old_content, new_content)
    return old_content, new_content, diff

