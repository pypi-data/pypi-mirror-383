"""cmake-init - The missing CMake project initializer."""

from pathlib import Path

from .cmake_init import main
from .template import compile_template

__version__ = "0.41.1"

__all__ = ["main", "compile_template", "pypi_main", "__version__"]


def pypi_main():
    """Entry point for the installed package."""
    # Get the templates directory from the package data
    package_dir = Path(__file__).parent
    templates_dir = package_dir / "templates"

    if not templates_dir.exists():
        raise FileNotFoundError(
            f"Templates directory not found at {templates_dir}. "
            "Please run 'python build.py' to build the package."
        )

    try:
        main(templates_dir, compile_template)
    except KeyboardInterrupt:
        pass
