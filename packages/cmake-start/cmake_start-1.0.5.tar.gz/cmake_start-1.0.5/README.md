# cmake-init

> 🚀 Generate modern CMake projects with best practices built-in

Powered by [UV](https://github.com/astral-sh/uv) - the fast Python package manager.

---

## Quick Start

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone & Setup
git clone https://github.com/Guo-astro/cmake-start.git
cd cmake-start
./tasks.sh setup

# 3. Create a project
uv run cmake-init my-project

# 4. Build it
cd my-project
cmake --preset=dev
cmake --build --preset=dev
```

---

## Usage

```bash
# C++ executable (default)
uv run cmake-init my-app

# C++ library
uv run cmake-init -s my-lib

# C++ header-only library
uv run cmake-init -h my-headers

# C project
uv run cmake-init --c my-c-app

# C++20 standard
uv run cmake-init --std 20 my-modern-app

# With Conan/vcpkg
uv run cmake-init -p conan my-app
```

**Important**: Project names must be lowercase (e.g., `my-project`, not `MyProject`)

---

## Code Quality Tools & OpenMP (Strongly Recommended)

**clang-tidy**, **cppcheck**, and **OpenMP** are **enabled by default** for better code quality and performance.

When you run `cmake --preset=dev`, the build system will:
1. Check if clang-tidy, cppcheck, and OpenMP are installed
2. Show detailed installation instructions if missing
3. Continue building (tools disabled if not found)

### Example Output (All Tools Found)

```
✅ Found clang-tidy: /opt/homebrew/bin/clang-tidy
✅ Found cppcheck: /opt/homebrew/bin/cppcheck
⏳ OpenMP check deferred (waiting for project() command)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Code Quality & Performance Tools Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ clang-tidy: ENABLED
     /opt/homebrew/bin/clang-tidy
  ✅ cppcheck: ENABLED
     /opt/homebrew/bin/cppcheck
  ❌ OpenMP: ENABLED but NOT FOUND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Found OpenMP (post-project check):
     C++ version: 4.5

📝 To use OpenMP in your code:
   1. Add to CMakeLists.txt:
      target_link_libraries(your_target PRIVATE OpenMP::OpenMP_CXX)
   2. In your C/C++ code:
      #include <omp.h>
      #pragma omp parallel for

🎉 All code quality and performance tools are active!
```

### Example Output (Tools Missing)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  clang-tidy not found - installation instructions:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 macOS (Homebrew):
   brew install llvm

❄️  Nix (declarative - recommended):
   Add to your configuration.nix or home.nix:
   home.packages = [ pkgs.clang-tools ];

❄️  Nix (imperative - quick test):
   nix-env -iA nixpkgs.clang-tools
   # OR with nix profile:
   nix profile install nixpkgs#clang-tools

💡 To disable this check:
   cmake --preset=dev -DENABLE_clang-tidy=OFF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Installation Guide

<details>
<summary><b>📦 macOS (Homebrew)</b></summary>

```bash
# Code quality tools
brew install llvm cppcheck

# OpenMP for parallel programming
brew install libomp

# Add to PATH if needed:
export PATH="/opt/homebrew/opt/llvm/bin:$PATH"
```
</details>

<details>
<summary><b>❄️ Nix (Declarative - Recommended)</b></summary>

Add to your `configuration.nix`, `home.nix`, or `flake.nix`:

```nix
# For system-wide (configuration.nix)
environment.systemPackages = with pkgs; [
  clang-tools       # clang-tidy
  cppcheck
  llvmPackages.openmp  # OpenMP
  # OR use gcc which includes OpenMP
  gcc
];

# For home-manager (home.nix)
home.packages = with pkgs; [
  clang-tools
  cppcheck
  llvmPackages.openmp
];

# For flake.nix devShell (recommended for project isolation)
devShells.default = pkgs.mkShell {
  buildInputs = with pkgs; [
    cmake
    clang-tools
    cppcheck
    llvmPackages.openmp
  ];
};
```

Then rebuild:
```bash
# NixOS
sudo nixos-rebuild switch

# home-manager
home-manager switch

# flake devShell
nix develop
```
</details>

<details>
<summary><b>❄️ Nix (Imperative - Quick Test)</b></summary>

```bash
# Traditional nix-env
nix-env -iA nixpkgs.clang-tools nixpkgs.cppcheck nixpkgs.llvmPackages.openmp

# Modern nix profile
nix profile install nixpkgs#clang-tools nixpkgs#cppcheck nixpkgs#llvmPackages.openmp

# Temporary shell (doesn't persist - great for testing)
nix-shell -p clang-tools cppcheck llvmPackages.openmp
```
</details>

<details>
<summary><b>📦 Ubuntu/Debian</b></summary>

```bash
sudo apt update
sudo apt install clang-tidy cppcheck libomp-dev

# OpenMP is also included with GCC:
sudo apt install build-essential
```
</details>

<details>
<summary><b>📦 Fedora</b></summary>

```bash
sudo dnf install clang-tools-extra cppcheck libomp-devel

# OpenMP is also included with GCC:
sudo dnf groupinstall 'Development Tools'
```
</details>

<details>
<summary><b>📦 Arch Linux</b></summary>

```bash
sudo pacman -S clang cppcheck openmp

# Note: OpenMP is included with GCC on Arch
```
</details>

<details>
<summary><b>📦 Windows</b></summary>

```powershell
choco install llvm cppcheck
```
</details>

### Using OpenMP in Your Code

Once OpenMP is detected, you can use it in your project:

```cmake
# In your CMakeLists.txt
target_link_libraries(your_target PRIVATE OpenMP::OpenMP_CXX)
```

```cpp
// In your C++ code
#include <omp.h>

int main() {
    #pragma omp parallel for
    for (int i = 0; i < 1000; i++) {
        // This loop runs in parallel!
        process(i);
    }
}
```

### Disabling (Not Recommended)

If you want to disable these features:
```bash
cmake --preset=dev -DENABLE_CLANG_TIDY=OFF -DENABLE_CPPCHECK=OFF -DENABLE_OPENMP=OFF
```

---

## Development

### Project Structure

```
cmake-start/
├── cmake-init/              ← Edit these files
│   ├── cmake_init.py       
│   ├── template.py         
│   └── templates/          
│
├── src/cmake_init_lib/     ← Auto-generated (don't edit)
│   ├── cmake_init.py       
│   ├── template.py         
│   └── cmake-init.zip      
│
└── build.py                ← Builds everything
```

### Making Changes

```bash
# 1. Edit source files
vim cmake-init/cmake_init.py
vim cmake-init/templates/common/cmake/code-quality.cmake

# 2. Rebuild (copies files + creates template ZIP)
python build.py

# 3. Test
uv run cmake-init test-project
```

**Single source of truth**: Always edit files in `cmake-init/`, then run `python build.py`

---

## Common Issues

### "Changes not working"
```bash
python build.py  # Run after editing cmake-init/
```

### "Invalid project name"
```bash
# Bad:  uv run cmake-init MyProject
# Good: uv run cmake-init my-project
```

### NixOS build errors
```bash
export CXX=clang++
cmake --preset=dev
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `uv run cmake-init my-app` | Create C++ executable |
| `uv run cmake-init -s my-lib` | Create C++ library |
| `uv run cmake-init -h my-headers` | Create header-only library |
| `uv run cmake-init --c my-c-app` | Create C project |
| `uv run cmake-init --std 20 my-app` | Use C++20 |
| `uv run cmake-init -p conan my-app` | Use Conan package manager |
| `uv run cmake-init --version` | Show version |
| `python build.py` | Build after editing templates |
| `python release.py patch` | Release new version to PyPI |
| `./tasks.sh setup` | Initial setup |

---

## Releasing to PyPI

**One command release:**

```bash
# Option 1: Automatic (commits everything first)
./quick-release.sh patch  # 1.0.1 → 1.0.2

# Option 2: Manual (requires clean git)
python release.py patch   # 1.0.1 → 1.0.2
```

The script automates:
- ✅ Version bump in pyproject.toml
- ✅ Template archive build (build.py)
- ✅ Wheel + source distribution build
- ✅ Git commit & tag
- ✅ PyPI upload
- ✅ GitHub push

**First time setup:**
```bash
# Get PyPI token: https://pypi.org/manage/account/token/
export PYPI_TOKEN='pypi-...'
# OR configure ~/.pypirc (see .pypirc.example)
```

See `RELEASE.md` for detailed documentation.

---

## What Makes This Different?

✅ **Smart code quality** - detects clang-tidy/cppcheck, shows clear install instructions
✅ **Nix-friendly** - proper support for declarative and imperative workflows
✅ **Latest vcpkg** - automatically fetches current baseline hash
✅ **Fast** - powered by UV (10-100x faster than pip)
✅ **Modern** - CMake presets, FetchContent-ready
✅ **Developer-friendly** - helpful error messages, not forced requirements
✅ **Cross-platform** - macOS, Linux, Windows, NixOS, Nix
✅ **Single source** - edit `cmake-init/`, run `build.py`  

---

## Links

- [CHANGELOG](CHANGELOG.md) - See what's new!
- [CMake Documentation](https://cmake.org/documentation/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [clang-tidy Docs](https://clang.llvm.org/extra/clang-tidy/)
- [cppcheck Manual](http://cppcheck.sourceforge.net/manual.pdf)
- [OpenMP Specification](https://www.openmp.org/)
- [Report Issues](https://github.com/Guo-astro/cmake-start/issues)
- [Original cmake-init](https://github.com/friendlyanon/cmake-init)

---

**Made with ❤️ for developers who hate boilerplate**
