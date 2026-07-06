"""Path-traversal containment check for the read_file MCP tool."""

import os
from pathlib import Path
from typing import Optional

SANDBOX_DIR = (Path(__file__).resolve().parent.parent.parent / "mcp_sandbox").resolve()


def check_path(path: str) -> Optional[str]:
    """Return None if *path* resolves inside SANDBOX_DIR, else a block reason."""
    base = os.path.realpath(str(SANDBOX_DIR))
    candidate = os.path.realpath(os.path.join(base, path))
    try:
        if os.path.commonpath([candidate, base]) != base:
            return "path_escape"
    except ValueError:
        # e.g. different drives on Windows, or otherwise unrelated paths
        return "path_escape"
    return None
