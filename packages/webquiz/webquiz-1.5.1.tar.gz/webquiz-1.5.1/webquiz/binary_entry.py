#!/usr/bin/env python3
"""
Entry point for PyInstaller binary.
Sets executable directory for relative path resolution.
"""

import sys
import os
import asyncio
from pathlib import Path
import webquiz.cli
from webquiz.version_check import check_and_notify_updates


def main():
    # Set executable directory for relative path resolution
    # For PyInstaller binaries, we need to detect the correct executable path
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running in a PyInstaller bundle
        exe_dir = Path(sys.argv[0]).parent.resolve()
    else:
        # Running normally (should not happen in binary_entry.py, but fallback)
        exe_dir = Path(sys.executable).parent

    os.environ["WEBQUIZ_BINARY_DIR"] = str(exe_dir)

    # Change working directory to binary location (important for macOS)
    os.chdir(exe_dir)

    # Mark this as binary execution for browser auto-opening
    os.environ["WEBQUIZ_IS_BINARY"] = "1"

    # Check for updates when binary starts (only for binary, not when running from source)
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(check_and_notify_updates())
        loop.close()
    except Exception:
        # Silently fail if update check fails - don't interrupt startup
        pass

    # Start the main application
    webquiz.cli.main()


if __name__ == "__main__":
    main()
