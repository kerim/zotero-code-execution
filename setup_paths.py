"""
Setup script to add zotero_mcp to Python path.

Run this at the start of your script to make zotero_mcp importable:

    import setup_paths  # Must be first import
    from zotero_lib import SearchOrchestrator
"""

import sys
from pathlib import Path

# Add zotero_mcp to path
ZOTERO_MCP_PATH = Path.home() / ".local/pipx/venvs/zotero-mcp/lib/python3.13/site-packages"

if ZOTERO_MCP_PATH.exists():
    sys.path.insert(0, str(ZOTERO_MCP_PATH))
    print(f"✓ Added zotero_mcp to Python path: {ZOTERO_MCP_PATH}")
else:
    # Try to find it with different Python versions, across pipx and uv tool installs
    venv_lib_bases = [
        Path.home() / ".local/pipx/venvs/zotero-mcp/lib",
        Path.home() / ".local/pipx/venvs/zotero-mcp-server/lib",
        Path.home() / ".local/share/uv/tools/zotero-mcp-server/lib",
    ]

    found = False
    for lib_base in venv_lib_bases:
        if not lib_base.exists():
            continue
        # Find the actual python version directory
        for python_dir in sorted(lib_base.iterdir(), reverse=True):
            if python_dir.name.startswith("python"):
                site_packages = python_dir / "site-packages"
                if (site_packages / "zotero_mcp").exists():
                    sys.path.insert(0, str(site_packages))
                    print(f"✓ Added zotero_mcp to Python path: {site_packages}")
                    found = True
                    break
        if found:
            break

    if not found:
        print("⚠ Warning: Could not find zotero_mcp installation")
        print("  Make sure Zotero MCP is installed via pipx or uv tool")
