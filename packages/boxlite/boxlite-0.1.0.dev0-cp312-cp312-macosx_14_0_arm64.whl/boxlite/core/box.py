"""
Base Box class for BoxLite containers.

This is the main user-facing API that wraps the Rust extension.
"""

from typing import Optional, Dict, Any, List, Tuple
import sys
import os
import fcntl


class Box:
    """
    Base class for all BoxLite containers.

    Provides secure, lightweight containerization using VM technology.
    """

    def __init__(self, image: str = "alpine:latest", **kwargs):
        """
        Create a new BoxLite container.

        Args:
            image: Container image to use (default: alpine:latest)
            **kwargs: Additional configuration options
                - engine: VM engine to use ('libkrun', 'firecracker')
                - memory_mib: Memory limit in MiB
                - cpus: Number of CPU cores
                - env: Environment variables as list of (key, value) tuples
        """
        # Import the Rust extension - the native Box class
        try:
            from ..boxlite import Box as NativeBox
            # Use the native implementation directly
            self._native_box = NativeBox({
                'engine': kwargs.get('engine', 'libkrun'),
                'image': image,
                **{k: v for k, v in kwargs.items() if k != 'engine'}
            })
            self._use_native = True
            return
        except ImportError as e:
            raise ImportError(
                f"BoxLite native extension not found: {e}. "
                "Please install with: pip install boxlite"
            )


    async def __aenter__(self):
        """Async context manager entry."""
        if self._use_native:
            self._native_box.__enter__()
            # Tokio runtime sets stdout/stderr to non-blocking mode
            # Restore blocking mode to prevent BlockingIOError when printing
            self._restore_blocking_mode()
        return self

    def _restore_blocking_mode(self):
        """Restore blocking mode on stdout/stderr after Tokio sets them to non-blocking."""
        for fd in [sys.stdout.fileno(), sys.stderr.fileno()]:
            try:
                flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                if flags & os.O_NONBLOCK:
                    fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
            except (OSError, AttributeError):
                # Ignore errors (e.g., when stdout/stderr is not a real file)
                pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._use_native:
            return self._native_box.__exit__(exc_type, exc_val, exc_tb)
        return None

    async def execute(self, command: str, *args) -> str:
        """
        Execute a command in the container.

        Args:
            command: Command to execute
            *args: Command arguments

        Returns:
            Command output as string
        """
        if self._use_native:
            result = await self._native_box.run_command(command, list(args) if args else None)
            if isinstance(result, list):
                return '\n'.join(f"[{stream}] {text}" for stream, text in result if text.strip())
            return str(result)

        raise RuntimeError("Container not initialized")
