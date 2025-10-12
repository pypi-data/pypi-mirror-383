"""
CodeBox - Secure Python code execution container.

Provides a simple, secure environment for running untrusted Python code.
"""

from typing import Optional, Dict, Any, Union
from ..core.box import Box


class CodeBox(Box):
    """
    Secure container for executing Python code.

    CodeBox provides an isolated environment for running untrusted Python code
    with built-in safety and result formatting.

    Example:
        >>> with CodeBox() as codebox:
        ...     result = codebox.run("print('Hello, World!')")
        ...     print(result)
    """

    def __init__(
        self,
        image: str = "python:slim",
        memory_mib: Optional[int] = None,
        cpus: Optional[int] = None,
        **kwargs
    ):
        """
        Create a new CodeBox for Python code execution.

        Args:
            image: Container image with Python (default: python:slim)
            memory_mib: Memory limit in MiB (default: system default)
            cpus: Number of CPU cores (default: system default)
            **kwargs: Additional Box configuration options
        """
        # Set up Python-specific defaults
        config = {
            'engine': kwargs.get('engine', 'libkrun'),
            'memory_mib': memory_mib,
            'cpus': cpus,
        }

        # Filter out None values
        config = {k: v for k, v in config.items() if v is not None}

        # Merge with any additional kwargs
        config.update({k: v for k, v in kwargs.items() if k not in config})

        # Initialize the base Box with Python image
        super().__init__(image=image, **config)

    async def run(self, code: str, timeout: Optional[int] = None) -> Union[str, Dict[str, Any]]:
        """
        Execute Python code in the secure container.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds (not yet implemented)

        Returns:
            Execution output as a string

        Example:
            >>> async with CodeBox() as cb:
            ...     result = await cb.run("print('Hello, World!')")
            ...     print(result)
            [stdout] Hello, World!

        Note:
            Uses python3 from the container image.
            For custom Python paths, use execute() directly:
                await cb.execute("/path/to/python", "-c", code)
        """
        # Execute Python code using python3 -c
        return await self.execute("/usr/local/bin/python", "-c", code)

    async def run_script(self, script_path: str) -> str:
        """
        Execute a Python script file in the container.

        Args:
            script_path: Path to the Python script on the host

        Returns:
            Execution output as a string
        """
        with open(script_path, 'r') as f:
            code = f.read()
        return await self.run(code)

    async def install_package(self, package: str) -> str:
        """
        Install a Python package in the container using pip.

        Args:
            package: Package name (e.g., 'requests', 'numpy==1.24.0')

        Returns:
            Installation output

        Example:
            >>> async with CodeBox() as cb:
            ...     await cb.install_package("requests")
            ...     result = await cb.run("import requests; print(requests.__version__)")
        """
        return await self.execute("pip", "install", package)

    async def install_packages(self, *packages: str) -> str:
        """
        Install multiple Python packages.

        Args:
            *packages: Package names to install

        Returns:
            Installation output

        Example:
            >>> async with CodeBox() as cb:
            ...     await cb.install_packages("requests", "numpy", "pandas")
        """
        return await self.execute("pip", "install", *packages)
