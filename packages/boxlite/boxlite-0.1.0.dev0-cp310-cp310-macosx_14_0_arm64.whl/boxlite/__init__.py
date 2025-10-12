"""
BoxLite - Lightweight, secure containerization for any environment.

Following SQLite philosophy: "BoxLite" for branding, "boxlite" for code APIs.
"""

import os
from pathlib import Path

# Set BOXLITE_BIN_DIR if not already set, to help Rust find binaries
if "BOXLITE_BIN_DIR" not in os.environ:
    # Check if binaries are bundled with the package
    package_bin_dir = Path(__file__).parent / "bin"
    if package_bin_dir.exists():
        os.environ["BOXLITE_BIN_DIR"] = str(package_bin_dir)

from .core.box import Box
from .boxes import CodeBox

# Future specialized containers
# from .boxes.browser import BrowserBox
# from .boxes.claude_code import ClaudeCodeBox

__version__ = "0.1.0"
__all__ = ["Box", "CodeBox"]
