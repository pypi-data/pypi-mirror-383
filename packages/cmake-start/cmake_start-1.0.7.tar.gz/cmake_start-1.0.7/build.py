#!/usr/bin/env python3
"""
Build script for cmake-init package.
This script prepares the package by creating the necessary archive.
"""

import re
import shutil
from pathlib import Path

# Get the project root
PROJECT_ROOT = Path(__file__).parent

# Read version from source
with open(PROJECT_ROOT / "src" / "cmake_init_lib" / "__init__.py") as f:
    for line in f:
        match = re.match(r'^__version__ = "([^"]+)"$', line)
        if match is not None:
            version = match[1]
            break

print(f"Building cmake-init version {version}")

# Target directory for the templates archive
lib_dir = PROJECT_ROOT / "src" / "cmake_init_lib"

# Step 1: Copy Python source files from cmake-init/ to src/cmake_init_lib/
print("Copying Python source files...")
source_files = ["cmake_init.py", "template.py"]
for source_file in source_files:
    src = PROJECT_ROOT / "cmake-init" / source_file
    dst = lib_dir / source_file
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  Copied {source_file}")
    else:
        print(f"  Warning: {source_file} not found in cmake-init/")

# Step 2: Create the archive of templates
print("Creating template archive...")
archive_path = lib_dir / "cmake-init"
shutil.make_archive(
    str(archive_path),
    "zip",
    str(PROJECT_ROOT / "cmake-init"),
    "templates",
    True,
)

print("Build preparation complete!")
print(f"Template archive created: {archive_path}.zip")
print("\n✅ Single source of truth: cmake-init/ directory")
