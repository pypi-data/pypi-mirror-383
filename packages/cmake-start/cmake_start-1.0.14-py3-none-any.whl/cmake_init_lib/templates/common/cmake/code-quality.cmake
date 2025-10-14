cmake_minimum_required(VERSION 3.{% if cmake_321 %}21{% else %}14{% end %})

# Code quality tools (clang-tidy, cppcheck) and performance libraries (OpenMP)
# These tools are optional and disabled by default to ensure compatibility
# They can be enabled with: cmake -DENABLE_CLANG_TIDY=ON -DENABLE_CPPCHECK=ON -DENABLE_OPENMP=ON

option(ENABLE_CLANG_TIDY "Enable clang-tidy checks" OFF)
option(ENABLE_CPPCHECK "Enable cppcheck checks" OFF)
option(ENABLE_OPENMP "Enable OpenMP parallel programming support (optional)" OFF)

# Function to show installation instructions
function(show_install_instructions TOOL_NAME)
  message(STATUS "")
  message(STATUS "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
  message(STATUS "⚠️  ${TOOL_NAME} not found - installation instructions:")
  message(STATUS "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
  message(STATUS "")

  if(APPLE)
    message(STATUS "📦 macOS (Homebrew):")
    if(TOOL_NAME STREQUAL "clang-tidy")
      message(STATUS "   brew install llvm")
      message(STATUS "   # Add to PATH: export PATH=\"/opt/homebrew/opt/llvm/bin:\$PATH\"")
    elseif(TOOL_NAME STREQUAL "cppcheck")
      message(STATUS "   brew install cppcheck")
    elseif(TOOL_NAME STREQUAL "OpenMP")
      message(STATUS "   brew install libomp")
      message(STATUS "   # OpenMP will be automatically detected by CMake")
    endif()
  endif()

  if(UNIX AND NOT APPLE)
    # Check for various package managers and nix
    set(HAS_NIX FALSE)
    execute_process(
      COMMAND which nix-env
      RESULT_VARIABLE NIX_CHECK
      OUTPUT_QUIET ERROR_QUIET
    )
    if(NIX_CHECK EQUAL 0)
      set(HAS_NIX TRUE)
    endif()

    if(HAS_NIX)
      message(STATUS "❄️  Nix (declarative - recommended):")
      message(STATUS "   Add to your configuration.nix or home.nix:")
      if(TOOL_NAME STREQUAL "clang-tidy")
        message(STATUS "   environment.systemPackages = [ pkgs.clang-tools ];")
        message(STATUS "   # OR for home-manager:")
        message(STATUS "   home.packages = [ pkgs.clang-tools ];")
      elseif(TOOL_NAME STREQUAL "cppcheck")
        message(STATUS "   environment.systemPackages = [ pkgs.cppcheck ];")
        message(STATUS "   # OR for home-manager:")
        message(STATUS "   home.packages = [ pkgs.cppcheck ];")
      elseif(TOOL_NAME STREQUAL "OpenMP")
        message(STATUS "   environment.systemPackages = [ pkgs.llvmPackages.openmp ];")
        message(STATUS "   # OR for home-manager:")
        message(STATUS "   home.packages = [ pkgs.llvmPackages.openmp ];")
        message(STATUS "   # OR use gcc which includes OpenMP:")
        message(STATUS "   home.packages = [ pkgs.gcc ];")
      endif()
      message(STATUS "")
      message(STATUS "❄️  Nix (imperative - quick test):")
      if(TOOL_NAME STREQUAL "clang-tidy")
        message(STATUS "   nix-env -iA nixpkgs.clang-tools")
        message(STATUS "   # OR with nix profile:")
        message(STATUS "   nix profile install nixpkgs#clang-tools")
      elseif(TOOL_NAME STREQUAL "cppcheck")
        message(STATUS "   nix-env -iA nixpkgs.cppcheck")
        message(STATUS "   # OR with nix profile:")
        message(STATUS "   nix profile install nixpkgs#cppcheck")
      elseif(TOOL_NAME STREQUAL "OpenMP")
        message(STATUS "   nix-env -iA nixpkgs.llvmPackages.openmp")
        message(STATUS "   # OR with nix profile:")
        message(STATUS "   nix profile install nixpkgs#llvmPackages.openmp")
        message(STATUS "   # OR in a nix-shell:")
        message(STATUS "   nix-shell -p llvmPackages.openmp")
      endif()
      message(STATUS "")
    endif()

    if(EXISTS "/etc/debian_version")
      message(STATUS "📦 Debian/Ubuntu:")
      if(TOOL_NAME STREQUAL "clang-tidy")
        message(STATUS "   sudo apt update && sudo apt install clang-tidy")
      elseif(TOOL_NAME STREQUAL "cppcheck")
        message(STATUS "   sudo apt update && sudo apt install cppcheck")
      elseif(TOOL_NAME STREQUAL "OpenMP")
        message(STATUS "   sudo apt update && sudo apt install libomp-dev")
        message(STATUS "   # OR install GCC (includes OpenMP):")
        message(STATUS "   sudo apt install build-essential")
      endif()
    endif()

    if(EXISTS "/etc/fedora-release")
      message(STATUS "📦 Fedora:")
      if(TOOL_NAME STREQUAL "clang-tidy")
        message(STATUS "   sudo dnf install clang-tools-extra")
      elseif(TOOL_NAME STREQUAL "cppcheck")
        message(STATUS "   sudo dnf install cppcheck")
      elseif(TOOL_NAME STREQUAL "OpenMP")
        message(STATUS "   sudo dnf install libomp-devel")
        message(STATUS "   # OR install GCC (includes OpenMP):")
        message(STATUS "   sudo dnf groupinstall 'Development Tools'")
      endif()
    endif()

    if(EXISTS "/etc/arch-release")
      message(STATUS "📦 Arch Linux:")
      if(TOOL_NAME STREQUAL "clang-tidy")
        message(STATUS "   sudo pacman -S clang")
      elseif(TOOL_NAME STREQUAL "cppcheck")
        message(STATUS "   sudo pacman -S cppcheck")
      elseif(TOOL_NAME STREQUAL "OpenMP")
        message(STATUS "   sudo pacman -S openmp")
        message(STATUS "   # OpenMP is included with GCC on Arch")
      endif()
    endif()
  endif()

  message(STATUS "")
  message(STATUS "💡 To disable this check:")
  message(STATUS "   cmake --preset=dev -DENABLE_${TOOL_NAME}=OFF")
  message(STATUS "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
  message(STATUS "")
endfunction()

# Detect clang-tidy
if(ENABLE_CLANG_TIDY)
  find_program(CLANG_TIDY_EXE NAMES clang-tidy)

  if(CLANG_TIDY_EXE)
    message(STATUS "✅ Found clang-tidy: ${CLANG_TIDY_EXE}")

    # Check toolchain consistency
    execute_process(
      COMMAND ${CLANG_TIDY_EXE} --version
      OUTPUT_VARIABLE CLANG_TIDY_VERSION
      ERROR_QUIET
    )

    # Detect potential toolchain mismatches
    set(TOOLCHAIN_WARNING FALSE)

    # Check if clang-tidy is from Nix but compiler is not (or vice versa)
    string(FIND "${CLANG_TIDY_EXE}" "/nix/store" TIDY_IN_NIX_STORE)
    string(FIND "${CLANG_TIDY_EXE}" "/run/current-system" TIDY_IN_NIX_SYSTEM)
    string(FIND "${CMAKE_CXX_COMPILER}" "/nix/store" COMPILER_IN_NIX_STORE)
    string(FIND "${CMAKE_CXX_COMPILER}" "/run/current-system" COMPILER_IN_NIX_SYSTEM)

    # Determine if each tool is from Nix
    set(TIDY_IS_NIX FALSE)
    set(COMPILER_IS_NIX FALSE)

    if(TIDY_IN_NIX_STORE GREATER -1 OR TIDY_IN_NIX_SYSTEM GREATER -1)
      set(TIDY_IS_NIX TRUE)
    endif()

    if(COMPILER_IN_NIX_STORE GREATER -1 OR COMPILER_IN_NIX_SYSTEM GREATER -1)
      set(COMPILER_IS_NIX TRUE)
    endif()

    # Check for mismatches
    if((TIDY_IS_NIX AND NOT COMPILER_IS_NIX) OR (NOT TIDY_IS_NIX AND COMPILER_IS_NIX))
      set(TOOLCHAIN_WARNING TRUE)

      # Determine toolchain sources
      if(TIDY_IS_NIX)
        set(TIDY_SOURCE "(Nix)")
      else()
        set(TIDY_SOURCE "(System)")
      endif()

      if(COMPILER_IS_NIX)
        set(COMPILER_SOURCE "(Nix)")
      else()
        set(COMPILER_SOURCE "(System)")
      endif()

      message(STATUS "")
      message(STATUS "⚠️  TOOLCHAIN MISMATCH DETECTED:")
      message(STATUS "   clang-tidy: ${CLANG_TIDY_EXE} ${TIDY_SOURCE}")
      if(CMAKE_CXX_COMPILER)
        message(STATUS "   compiler:   ${CMAKE_CXX_COMPILER} ${COMPILER_SOURCE}")
      else()
        message(STATUS "   compiler:   (will be detected later) ${COMPILER_SOURCE}")
      endif()
      message(STATUS "")
      message(STATUS "💡 Different toolchains may cause clang-tidy errors:")
      message(STATUS "   - System headers may not be compatible")
      message(STATUS "   - Standard library paths may differ")
      message(STATUS "")
      message(STATUS "   Recommendation: Use -DENABLE_CLANG_TIDY=OFF")
      message(STATUS "   Alternative:    Use -DENABLE_CPPCHECK=ON (more reliable)")
      message(STATUS "")
    endif()

    if(NOT TOOLCHAIN_WARNING)
      message(STATUS "   ✓ Toolchain appears consistent")
    endif()
  else()
    show_install_instructions("clang-tidy")
    message(WARNING "clang-tidy not found - static analysis disabled")
    message(WARNING "Install clang-tidy for better code quality checks")
    set(ENABLE_CLANG_TIDY OFF)
  endif()
else()
  message(STATUS "⚠️  clang-tidy checks DISABLED by user")
endif()

# Detect cppcheck
if(ENABLE_CPPCHECK)
  find_program(CPPCHECK_EXE NAMES cppcheck)

  if(CPPCHECK_EXE)
    message(STATUS "✅ Found cppcheck: ${CPPCHECK_EXE}")
  else()
    show_install_instructions("cppcheck")
    message(WARNING "cppcheck not found - static analysis disabled")
    message(WARNING "Install cppcheck for better code quality checks")
    set(ENABLE_CPPCHECK OFF)
  endif()
else()
  message(STATUS "⚠️  cppcheck checks DISABLED by user")
endif()

# Configure clang-tidy
if(ENABLE_CLANG_TIDY AND CLANG_TIDY_EXE)
  if(CMAKE_CXX_CLANG_TIDY)
    # Already configured via CMakePresets.json or command line
    message(STATUS "clang-tidy already configured: ${CMAKE_CXX_CLANG_TIDY}")
  else()
    set(CMAKE_CXX_CLANG_TIDY
        "${CLANG_TIDY_EXE};--header-filter=^${PROJECT_SOURCE_DIR}/;--system-headers=false;--warnings-as-errors=*;--quiet"
        CACHE STRING "clang-tidy command" FORCE)
    message(STATUS "Enabled clang-tidy checks (strict mode - warnings fail build)")
  endif()
endif()

# Configure cppcheck
if(ENABLE_CPPCHECK AND CPPCHECK_EXE)
  if(CMAKE_CXX_CPPCHECK)
    # Already configured via CMakePresets.json or command line
    message(STATUS "cppcheck already configured: ${CMAKE_CXX_CPPCHECK}")
  else()
    set(CMAKE_CXX_CPPCHECK
        "${CPPCHECK_EXE};--inline-suppr;--enable=warning,style,performance,portability;--error-exitcode=1;--suppress=missingIncludeSystem"
        CACHE STRING "cppcheck command" FORCE)
    message(STATUS "Enabled cppcheck checks (strict mode - errors fail build)")
  endif()
endif()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OpenMP Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Detect OpenMP (only if a language is enabled - happens after project() command)
if(ENABLE_OPENMP)
  # Check if any language is enabled (CXX, C, CUDA, Fortran)
  get_property(languages GLOBAL PROPERTY ENABLED_LANGUAGES)

  if(languages)
    find_package(OpenMP QUIET)

    if(OpenMP_FOUND OR OpenMP_C_FOUND OR OpenMP_CXX_FOUND)
      message(STATUS "✅ Found OpenMP:")
      if(OpenMP_C_VERSION)
        message(STATUS "     C version: ${OpenMP_C_VERSION}")
      endif()
      if(OpenMP_CXX_VERSION)
        message(STATUS "     C++ version: ${OpenMP_CXX_VERSION}")
      endif()

      # OpenMP will be linked to targets via target_link_libraries(target OpenMP::OpenMP_CXX)
      # This should be done in your CMakeLists.txt where targets are defined
      set(OPENMP_AVAILABLE TRUE CACHE BOOL "OpenMP is available" FORCE)
    else()
      show_install_instructions("OpenMP")
      message(WARNING "OpenMP not found - parallel programming support disabled")
      message(WARNING "Install OpenMP for multi-threaded performance")
      set(ENABLE_OPENMP OFF)
      set(OPENMP_AVAILABLE FALSE CACHE BOOL "OpenMP is available" FORCE)
    endif()
  else()
    # Languages not enabled yet - will check OpenMP later
    message(STATUS "⏳ OpenMP check deferred (waiting for project() command)")
    set(OPENMP_AVAILABLE FALSE CACHE BOOL "OpenMP is available" FORCE)
  endif()
else()
  message(STATUS "⚠️  OpenMP DISABLED by user")
  set(OPENMP_AVAILABLE FALSE CACHE BOOL "OpenMP is available" FORCE)
endif()

# Summary
message(STATUS "")
message(STATUS "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
message(STATUS "📊 Code Quality & Performance Tools Status:")
message(STATUS "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if(ENABLE_CLANG_TIDY AND CLANG_TIDY_EXE)
  message(STATUS "  ✅ clang-tidy: ENABLED")
  message(STATUS "     ${CLANG_TIDY_EXE}")
elseif(ENABLE_CLANG_TIDY)
  message(STATUS "  ❌ clang-tidy: ENABLED but NOT FOUND")
else()
  message(STATUS "  ⚠️  clang-tidy: DISABLED")
endif()

if(ENABLE_CPPCHECK AND CPPCHECK_EXE)
  message(STATUS "  ✅ cppcheck: ENABLED")
  message(STATUS "     ${CPPCHECK_EXE}")
elseif(ENABLE_CPPCHECK)
  message(STATUS "  ❌ cppcheck: ENABLED but NOT FOUND")
else()
  message(STATUS "  ⚠️  cppcheck: DISABLED")
endif()

if(OPENMP_AVAILABLE)
  message(STATUS "  ✅ OpenMP: ENABLED")
  if(OpenMP_C_VERSION)
    message(STATUS "     C ${OpenMP_C_VERSION}")
  endif()
  if(OpenMP_CXX_VERSION)
    message(STATUS "     C++ ${OpenMP_CXX_VERSION}")
  endif()
elseif(ENABLE_OPENMP)
  message(STATUS "  ❌ OpenMP: ENABLED but NOT FOUND")
else()
  message(STATUS "  ⚠️  OpenMP: DISABLED")
endif()

message(STATUS "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Show helpful tips
set(MISSING_TOOLS FALSE)
if((NOT CLANG_TIDY_EXE AND ENABLE_CLANG_TIDY) OR
   (NOT CPPCHECK_EXE AND ENABLE_CPPCHECK) OR
   (NOT OPENMP_AVAILABLE AND ENABLE_OPENMP))
  set(MISSING_TOOLS TRUE)
endif()

if(MISSING_TOOLS)
  message(STATUS "")
  message(STATUS "💡 Tip: Install missing tools above, then re-run CMake")
  message(STATUS "   Or disable with: cmake -DENABLE_CLANG_TIDY=OFF -DENABLE_CPPCHECK=OFF -DENABLE_OPENMP=OFF")
elseif(ENABLE_CLANG_TIDY AND ENABLE_CPPCHECK AND CLANG_TIDY_EXE AND CPPCHECK_EXE AND OPENMP_AVAILABLE)
  message(STATUS "")
  message(STATUS "🎉 All code quality and performance tools are active!")
endif()

if(OPENMP_AVAILABLE)
  message(STATUS "")
  message(STATUS "📝 To use OpenMP in your code:")
  message(STATUS "   1. Add to CMakeLists.txt:")
  message(STATUS "      target_link_libraries(your_target PRIVATE OpenMP::OpenMP_CXX)")
  message(STATUS "   2. In your C/C++ code:")
  message(STATUS "      #include <omp.h>")
  message(STATUS "      #pragma omp parallel for")
endif()
message(STATUS "")
