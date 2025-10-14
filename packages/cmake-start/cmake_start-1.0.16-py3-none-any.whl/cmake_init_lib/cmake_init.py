# cmake-init - The missing CMake project initializer
# Copyright (C) 2021  friendlyanon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Website: https://github.com/friendlyanon/cmake-init

"""\
Opinionated CMake project initializer to generate CMake projects that are
FetchContent ready, separate consumer and developer targets, provide install
rules with proper relocatable CMake packages and use modern CMake (3.14+)
"""

import argparse
import contextlib
import io
import json
import os
import platform
import re
import subprocess
import sys
import urllib.request
import zipfile

__version__ = "0.41.1"

compile_template = None


def fetch_vcpkg_baseline():
    """
    Fetch the latest vcpkg baseline commit hash from GitHub API.

    Returns:
        str: The latest commit SHA from vcpkg repository, or a fallback hash if fetch fails.
    """
    fallback_hash = "d7112d1a4fb50410d3639f5f586972591d848beb"

    try:
        url = "https://api.github.com/repos/microsoft/vcpkg/commits/master"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", f"cmake-init/{__version__}")

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest_hash = data["sha"]
            print(f"✅ Fetched latest vcpkg baseline: {latest_hash[:12]}...")
            return latest_hash
    except Exception as e:
        print(f"⚠️  Could not fetch latest vcpkg baseline: {e}")
        print(f"   Using fallback baseline: {fallback_hash[:12]}...")
        return fallback_hash


class Language:
    def __init__(self, name, types, options, default):
        self.name = name
        self.types = types
        self.options = options
        self.default = options[default]

    def __str__(self):
        return self.name


c_lang = Language("C", ["e", "s", "h"], ["90", "99", "11", "17", "23"], 1)

cpp_lang = Language("C++", ["e", "h", "s"], ["11", "14", "17", "20"], 2)


def not_empty(value):
    return len(value) != 0


class ArgumentError(Exception):
    pass


def prompt(
    msg,
    default,
    mapper=None,
    predicate=not_empty,
    header=None,
    no_prompt=False,
    validation_func=None,
):
    """
    Prompt user for input with validation.

    Args:
        msg: Message to display
        default: Default value
        mapper: Function to transform input
        predicate: Function to validate (returns bool)
        header: Header text to display before prompt
        no_prompt: If True, use default without prompting
        validation_func: Function that returns (is_valid, error_message) tuple
    """
    if header is not None:
        print(header)
    while True:
        # noinspection PyBroadException
        try:
            print(msg.format(default), end=": ")
            in_value = ("" if no_prompt else input()) or default
            value = mapper(in_value) if mapper is not None else in_value

            # Use validation_func if provided (gives detailed errors)
            if validation_func is not None:
                is_valid, error_msg = validation_func(value)
                if is_valid:
                    print()
                    return value
                else:
                    if no_prompt:
                        raise ArgumentError(
                            f"'{in_value}' is not an acceptable value: {error_msg}"
                        )
                    print(f"❌ {error_msg}")
                    continue

            # Fall back to predicate (simple bool check)
            if predicate(value):
                print()
                return value
        except Exception as e:
            if no_prompt:
                raise
        if no_prompt:
            raise ArgumentError(f"'{in_value}' is not an acceptable value")
        print("Invalid value, try again")


def validate_project_name(name):
    """
    Validate project name and return (is_valid, error_message).

    Rules:
    - Must start with a lowercase letter [a-z]
    - Can only contain lowercase letters, numbers, hyphens (-), and underscores (_)
    - Cannot contain uppercase letters
    - Cannot be named "test" or "lib" (reserved names)
    - Cannot have consecutive hyphens (--) or underscores (__)
    - Minimum length: 2 characters
    """
    # Check minimum length
    if len(name) < 2:
        return False, "Project name must be at least 2 characters long."

    # Check reserved names
    reserved = ["test", "lib"]
    if name in reserved:
        return False, f"'{name}' is a reserved name and cannot be used."

    # Check if starts with lowercase letter
    if not re.match("^[a-z]", name):
        if name[0].isupper():
            return (
                False,
                f"Project name must start with a lowercase letter, not '{name[0]}'.\n       Try: '{name.lower()}' instead.",
            )
        elif name[0].isdigit():
            return (
                False,
                "Project name cannot start with a number.\n       Try: 'my-{name}' or '{name}-project'.",
            )
        else:
            return (
                False,
                f"Project name must start with a lowercase letter (a-z), not '{name[0]}'.",
            )

    # Check for uppercase letters
    uppercase_chars = [c for c in name if c.isupper()]
    if uppercase_chars:
        return (
            False,
            f"Project name cannot contain uppercase letters: {', '.join(set(uppercase_chars))}\n       Try: '{name.lower()}' instead.",
        )

    # Check for invalid characters
    if not re.match("^[a-z][0-9a-z-_]*$", name):
        invalid_chars = [c for c in name if not re.match("[a-z0-9-_]", c)]
        if invalid_chars:
            return (
                False,
                f"Project name contains invalid characters: {', '.join(set(invalid_chars))}\n       Only lowercase letters, numbers, hyphens (-), and underscores (_) are allowed.",
            )

    # Check for consecutive hyphens or underscores
    if "--" in name:
        return (
            False,
            "Project name cannot contain consecutive hyphens (--).\n       Use single hyphens instead.",
        )
    if "__" in name:
        return (
            False,
            "Project name cannot contain consecutive underscores (__).\n       Use single underscores instead.",
        )

    # Check if ends with hyphen or underscore (good practice)
    if name[-1] in ["-", "_"]:
        return False, f"Project name should not end with '{name[-1]}'."

    return True, ""


def is_valid_name(name):
    """Legacy function that returns boolean only."""
    is_valid, _ = validate_project_name(name)
    return is_valid


def is_semver(version):
    return re.match(r"^\d+(\.\d+){0,3}", version) is not None


def get_substitutes(cli_args, name):
    no_prompt = cli_args.flags_used

    # Validate project name with detailed error message
    is_valid, error_msg = validate_project_name(name)
    if no_prompt and not is_valid:
        print(f"\n❌ Invalid project name: '{name}'", file=sys.stderr)
        print(f"   {error_msg}\n", file=sys.stderr)
        print("📋 Project name rules:", file=sys.stderr)
        print("   • Must start with a lowercase letter (a-z)", file=sys.stderr)
        print(
            "   • Can contain: lowercase letters, numbers, hyphens (-), underscores (_)",
            file=sys.stderr,
        )
        print(
            "   • Cannot contain: uppercase letters, spaces, or special characters",
            file=sys.stderr,
        )
        print("   • Cannot be: 'test' or 'lib' (reserved names)", file=sys.stderr)
        print(
            "   • Cannot have: consecutive hyphens (--) or underscores (__)",
            file=sys.stderr,
        )
        print(
            f"\n✅ Example valid names: my-project, awesome-lib, tool_v2\n",
            file=sys.stderr,
        )
        exit(1)

    def ask(*args, **kwargs):
        return prompt(*args, **kwargs, no_prompt=no_prompt)

    type_map = {
        "e": "[E]xecutable",
        "h": "[h]eader-only",
        "s": "[s]tatic/shared",
    }
    lang = c_lang if cli_args.c else cpp_lang
    os_map = {
        "Windows": "win64",
        "Linux": "linux",
        "Darwin": "darwin",
    }

    if not no_prompt:
        print(f"cmake-init is going to generate a {lang} project\n")

    d = {
        "name": ask(
            "Project name ({})",
            name,
            validation_func=validate_project_name,
            header="📋 Project name rules:\n"
            "   • Start with lowercase letter (a-z)\n"
            "   • Use: lowercase, numbers, hyphens (-), underscores (_)\n"
            "   • No uppercase letters, spaces, or special characters",
        ),
        "version": ask(
            "Project version ({})",
            "0.1.0",
            predicate=is_semver,
            header="""\
Use Semantic Versioning, because CMake naturally supports that. Visit
https://semver.org/ for more information.""",
        ),
        "description": ask(*(["Short description"] * 2)),
        "homepage": ask("Homepage URL ({})", "https://example.com/"),
        "std": ask(
            "{} standard ({})".format(lang, "/".join(lang.options)),
            cli_args.std or lang.default,
            predicate=lambda v: v in lang.options,
            header=f"{lang} standard to use. Defaults to {lang.default}.",
        ),
        "type_id": ask(
            "Target type ({})".format(" or ".join([type_map[t] for t in lang.types])),
            cli_args.type_id or "e",
            mapper=lambda v: v[0:1].lower(),
            predicate=lambda v: v in lang.types,
            header="""\
Type of the target this project provides. A static/shared library will be set
up to hide every symbol by default (as it should) and use an export header to
explicitly mark symbols for export/import, but only when built as a shared
library.""",
        ),
        "use_clang_tidy": False,  # Auto-detected by CMake
        "use_cppcheck": False,  # Auto-detected by CMake
        "examples": False,
        "c_examples": False,
        "cpp_examples": False,
        "os": os_map.get(platform.system(), "unknown"),
        "c": cli_args.c,
        "cpp": not cli_args.c,
        "c_header": False,
        "include_source": False,
        "has_source": True,
        "cpus": os.cpu_count(),
        "pm_name": "",
        "catch3": False,
        "cpp_std": "",
        "msvc_cpp_std": "",
        "c90": False,
        "c99": False,
        "cmake_321": False,
        "modules": False,
        "openmp": False,
    }
    package_manager = ask(
        "Package manager to use ([N]one/[c]onan/[v]cpkg)",
        cli_args.package_manager or "n",
        mapper=lambda v: v[0:1].lower(),
        predicate=lambda v: v in ["n", "c", "v"],
        header="""\
Choosing Conan requires it to be installed. Choosing vcpkg requires the
VCPKG_ROOT environment variable to be setup to vcpkg's root directory.""",
    )
    d["vcpkg"] = package_manager == "v"
    d["conan"] = package_manager == "c"
    d["pm"] = package_manager != "n"
    if d["pm"]:
        d["pm_name"] = "conan" if d["conan"] else "vcpkg"

    # Fetch latest vcpkg baseline if using vcpkg
    if d["vcpkg"]:
        d["vcpkg_baseline"] = fetch_vcpkg_baseline()
    else:
        d["vcpkg_baseline"] = ""  # Not used for non-vcpkg projects

    d["uc_name"] = d["name"].upper().replace("-", "_")
    if d["type_id"] != "e":
        key = "c_examples" if cli_args.c else "cpp_examples"
        value = "n" == ask(
            "Exclude examples ([Y]es/[n]o)",
            cli_args.examples or "y",
            mapper=lambda v: v[0:1].lower(),
            predicate=lambda v: v in ["y", "n"],
        )
        d[key] = value
        d["examples"] = value
    if d["type_id"] == "e":
        d["include_source"] = True
    if d["type_id"] == "h":
        d["has_source"] = False
    d["c_header"] = d["c"] and d["type_id"] == "h"
    d["exe"] = d["type_id"] == "e"
    d["lib"] = d["type_id"] == "s"
    d["header"] = d["type_id"] == "h"
    d["catch3"] = d["cpp"] and d["std"] != "11" and d["pm"]
    if d["conan"]:
        if d["c"]:
            d["cpp_std"] = "11"
            d["msvc_cpp_std"] = "14"
        else:
            d["cpp_std"] = d["std"]
            d["msvc_cpp_std"] = d["std"] if d["std"] != "11" else "14"
    if d["c"]:
        if d["std"] == "90":
            d["c90"] = True
        else:
            d["c99"] = True
    else:
        if d["std"] == "20":
            d["modules"] = True
    if d["c"] and int(d["std"]) >= 17:
        d["cmake_321"] = True

    # Enable OpenMP example code if requested
    d["openmp"] = cli_args.openmp == "y"

    return d


def mkdir(path):
    os.makedirs(path, exist_ok=True)


def write_file(path, d, overwrite, zip_path):
    if overwrite or not os.path.exists(path):
        renderer = compile_template(zip_path.read_text(encoding="UTF-8"), d)
        # noinspection PyBroadException
        try:
            contents = renderer()
        except Exception:
            print(f"Error while rendering {path}", file=sys.stderr)
            raise
        with open(path, "w", encoding="UTF-8", newline="\n") as f:
            f.write(contents)


def should_install_file(name, d):
    if name == "project-is-top-level.cmake":
        return not d["cmake_321"]
    if name == "vcpkg.json":
        return d["vcpkg"]
    if name == "conanfile.py":
        return d["conan"]
    if name == "conan-setup.sh":
        return d["conan"]
    if name == "install-config.cmake":
        return not d["exe"]
    if name == "windows-set-path.cmake":
        return not d["pm"]
    if name == "header_impl.c":
        return d["c_header"] and d["pm"]
    if name == "env.ps1" or name == "env.bat":
        return d["lib"] and not d["pm"]
    return True


def should_install_dir(at, d):
    if at.endswith("/example/"):
        if d["c"]:
            return d["c_examples"] if "/c/" in at else False
        else:
            return d["cpp_examples"]
    if at.endswith("/scripts/"):
        return d["conan"]
    return True


def transform_path(path, d):
    if d["c"] and d["pm"] and path.endswith("_test.c"):
        return f"{path}pp"
    return path


def write_dir(path, d, overwrite, template_path, base_path=None):
    # For pathlib.Path compatibility, track the base path for relative path calculation
    if base_path is None:
        base_path = template_path

    for entry in template_path.iterdir():
        name = entry.name.replace("__name__", d["name"])
        next_path = os.path.join(path, name)
        if entry.is_file():
            if should_install_file(name, d):
                write_file(transform_path(next_path, d), d, overwrite, entry)
        else:  # entry.is_dir()
            # Calculate relative path for should_install_dir check
            try:
                # For zipfile.Path
                rel_path = entry.at
            except AttributeError:
                # For pathlib.Path
                rel_path = str(entry.relative_to(base_path)) + "/"

            if should_install_dir(rel_path, d):
                mkdir(next_path)
                write_dir(next_path, d, overwrite, entry, base_path)


def determine_git_version():
    search_pattern = r"\d+(\.\d+)+"
    git_version_out = subprocess.run("git --version", shell=True, capture_output=True)
    if git_version_out.returncode != 0:
        return None
    git_version_out = str(git_version_out.stdout, sys.stdout.encoding)
    git_version_match = re.search(search_pattern, git_version_out)
    if not git_version_match:
        return None
    git_version_str = git_version_match.group(0)
    git_version = list(map(int, git_version_str.rstrip().split(".")))
    if len(git_version) < 3:
        git_version += [0] * (3 - len(git_version))
    return tuple(git_version)


def git_init(cwd):
    git_version = determine_git_version()
    if git_version is None:
        print("\nGit can't be found! Can't initialize git for the project.\n")
        return
    branch = ""
    if (2, 28, 0) <= git_version:
        branch = " -b master"
    subprocess.run(f"git init{branch}", shell=True, check=True, cwd=cwd)
    print(
        """
The project is ready to be used with git. If you are using GitHub, you may
push the project with the following commands from the project directory:

    git add .
    git commit -m "Initial commit"
    git remote add origin https://github.com/<your-account>/<repository>.git
    git push -u origin master
"""
    )


def conan_setup(cwd):
    """Automatically setup Conan dependencies after project generation

    Args:
        cwd: Project directory path
    """
    print("\n" + "=" * 60)
    print("🔧 Setting up Conan dependencies...")
    print("=" * 60)

    # Check if Conan is installed
    conan_check = subprocess.run(
        "conan --version", shell=True, capture_output=True, cwd=cwd
    )

    if conan_check.returncode != 0:
        print("\n❌ Conan is not installed!")
        print("\n📦 To install Conan, run:")
        print("   pip install conan")
        print("   # or")
        print("   pipx install conan")
        print("\nThen run the following command in your project directory:")
        print("   ./conan-setup.sh")
        print("\nOr manually run:")
        print("   conan profile detect")
        print("   conan install . -s build_type=Debug -b missing\n")
        return

    print("✅ Conan is installed")

    # Check if default profile exists, create if needed
    profile_check = subprocess.run(
        "conan profile show default", shell=True, capture_output=True, cwd=cwd
    )

    if profile_check.returncode != 0:
        print("📋 Creating default Conan profile...")
        profile_create = subprocess.run(
            "conan profile detect --force", shell=True, capture_output=True, cwd=cwd
        )

        if profile_create.returncode != 0:
            print("❌ Failed to create Conan profile")
            print("   Please run manually: conan profile detect")
            return

        print("✅ Default Conan profile created")
    else:
        print("✅ Conan profile exists")

    # Run conan install to generate toolchain
    # Install for both Debug and Release to support all development scenarios
    print("📦 Installing dependencies and generating CMake toolchain...")
    print("   This may take a few minutes on first run...\n")

    # Install Release dependencies first (used by most CI presets)
    print("   📦 Installing Release configuration...")
    conan_install_release = subprocess.run(
        "conan install . -s build_type=Release -b missing", shell=True, cwd=cwd
    )

    success = conan_install_release.returncode == 0

    if success:
        # Also install Debug dependencies for development
        print("\n   📦 Installing Debug configuration...")
        conan_install_debug = subprocess.run(
            "conan install . -s build_type=Debug -b missing", shell=True, cwd=cwd
        )
        if conan_install_debug.returncode != 0:
            print("   ⚠️  Debug installation had issues, but Release is available")
    else:
        print("\n   ⚠️  Release installation failed, trying Debug only...")
        conan_install_debug = subprocess.run(
            "conan install . -s build_type=Debug -b missing", shell=True, cwd=cwd
        )
        success = conan_install_debug.returncode == 0

    if success:
        print("\n" + "=" * 60)
        print("✅ Conan setup complete!")
        print("=" * 60)
        print("\n🎉 You can now build your project:")
        print("   cmake --preset=dev")
        print("   cmake --build --preset=dev")
        print("   ctest --preset=dev\n")
    else:
        print("\n" + "=" * 60)
        print("⚠️  Conan install encountered issues")
        print("=" * 60)
        print("\nYou can try running the setup script manually:")
        print("   ./conan-setup.sh")
        print("\nOr run Conan install manually:")
        print("   conan install . -s build_type=Release -b missing")
        print("   conan install . -s build_type=Debug -b missing\n")


def create(args, templates_root):
    """Create a CMake project according to the provided information

    Args:
        args: Parsed command line arguments
        templates_root: Path to templates directory (either zipfile.ZipFile or pathlib.Path)
    """
    from pathlib import Path as PathlibPath

    path = args.path
    if (
        not args.overwrite
        and os.path.exists(path)
        and os.path.isdir(path)
        and len(os.listdir(path)) != 0
    ):
        print(
            f"Error - directory exists and is not empty:\n{path}",
            file=sys.stderr,
        )
        exit(1)
    try:
        if args.flags_used:
            with contextlib.redirect_stdout(io.StringIO()):
                d = get_substitutes(args, os.path.basename(path))
        else:
            d = get_substitutes(args, os.path.basename(path))
    except ArgumentError as e:
        print(str(e), file=sys.stderr)
        exit(1)
    mkdir(path)
    mapping = {"e": "executable/", "h": "header/", "s": "shared/"}
    template_paths = [("c/" if d["c"] else "") + mapping[d["type_id"]], "common/"]
    if d["c"]:
        template_paths.insert(1, "c/common/")
    if args.overwrite:
        template_paths.reverse()

    # Support both zipfile and pathlib.Path
    if isinstance(templates_root, zipfile.ZipFile):
        # Legacy zipfile support
        for template_path in (f"templates/{p}" for p in template_paths):
            write_dir(
                path, d, args.overwrite, zipfile.Path(templates_root, template_path)
            )
    elif isinstance(templates_root, PathlibPath):
        # New pathlib.Path support
        for template_path in template_paths:
            write_dir(path, d, args.overwrite, templates_root / template_path)
    else:
        raise TypeError(
            f"templates_root must be zipfile.ZipFile or pathlib.Path, got {type(templates_root)}"
        )

    git_init(path)

    # Automatically setup Conan if selected
    if d["conan"]:
        conan_setup(path)

    cmake_version = "3.21" if d["cmake_321"] else "3.20"
    print(
        f"""\
To get started with developing the project, make sure you read the generated
HACKING.md and BUILDING.md files for how to build the project as a developer or
as a user respectively. There are also some details you may want to fill in in
the README.md, CONTRIBUTING.md and .github/workflows/ci.yml files.

Now make sure you have at least CMake {cmake_version} installed for local development, to
make use of all the nice Quality-of-Life improvements in newer releases:
https://cmake.org/download/

For more tips, like integration with package managers, please see the Wiki:
https://github.com/friendlyanon/cmake-init/wiki

You are all set. Have fun programming and create something awesome!"""
    )


def main(templates_root, template_compiler):
    """Main entry point for cmake-init

    Args:
        templates_root: Either a zipfile.ZipFile or pathlib.Path to templates directory
        template_compiler: Function to compile templates
    """
    global compile_template
    compile_template = template_compiler

    p = argparse.ArgumentParser(
        prog="cmake-init",
        description=__doc__,
        add_help=False,
    )
    p.add_argument(
        "--help",
        action="help",
        help="show this help message and exit",
    )
    p.add_argument("--version", action="version", version=__version__)
    p.set_defaults(overwrite=False, dummy=False, c=False)
    p.add_argument(
        "--c",
        action="store_true",
        help="generate a C project instead of a C++ one",
    )
    p.add_argument(
        "path",
        type=os.path.realpath,
        help="path to generate to, the name is also derived from this",
    )
    create_flags = [
        "type_id",
        "std",
        "use_clang_tidy",
        "use_cppcheck",
        "examples",
        "openmp",
    ]
    p.set_defaults(**{k: "" for k in create_flags})
    type_g = p.add_mutually_exclusive_group()
    mapping = {
        "e": "generate an executable (default)",
        "h": "generate a header-only library",
        "s": "generate a static/shared library",
    }
    for flag, help in mapping.items():
        type_g.add_argument(
            f"-{flag}",
            dest="type_id",
            action="store_const",
            const=flag,
            help=help,
        )
    defaults = ", ".join([f"{lang} - {lang.default}" for lang in [cpp_lang, c_lang]])
    p.add_argument(
        "--std",
        metavar="NN",
        help=f"set the language standard to use (defaults: {defaults})",
    )
    p.add_argument(
        "--no-clang-tidy",
        action="store_const",
        dest="use_clang_tidy",
        const="n",
        help="omit the clang-tidy preset from the dev preset",
    )
    p.add_argument(
        "--no-cppcheck",
        action="store_const",
        dest="use_cppcheck",
        const="n",
        help="omit the cppcheck preset from the dev preset",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="omit checks for existing files and non-empty project root",
    )
    p.add_argument(
        "--examples",
        action="store_const",
        const="n",
        help="generate examples for a library",
    )
    p.add_argument(
        "-p",
        metavar="pm",
        dest="package_manager",
        help="package manager to use (Options are: conan, vcpkg)",
    )
    p.add_argument(
        "--openmp",
        action="store_const",
        const="y",
        help="generate OpenMP parallel programming example code",
    )
    args = p.parse_args()
    if args.dummy:
        p.print_help()
        exit(1)
    flags_used = any(getattr(args, k) != "" for k in create_flags)
    setattr(args, "flags_used", flags_used)
    create(args, templates_root)
