cmake_minimum_required(VERSION 3.{% if cmake_321 %}21{% else %}14{% end %})

# Auto-detect and configure code quality tools (clang-tidy, cppcheck)
# These tools are optional and will only be enabled if found on the system

# Allow user to override detection
option(ENABLE_CLANG_TIDY "Enable clang-tidy checks (auto-detected if not specified)" AUTO)
option(ENABLE_CPPCHECK "Enable cppcheck checks (auto-detected if not specified)" AUTO)

# Detect clang-tidy
if(ENABLE_CLANG_TIDY STREQUAL "AUTO")
  find_program(CLANG_TIDY_EXE NAMES clang-tidy)
  if(CLANG_TIDY_EXE)
    message(STATUS "Found clang-tidy: ${CLANG_TIDY_EXE}")
    set(ENABLE_CLANG_TIDY ON)
  else()
    message(STATUS "clang-tidy not found - skipping clang-tidy checks")
    message(STATUS "To install clang-tidy:")
    if(APPLE)
      message(STATUS "  brew install llvm")
    elseif(UNIX)
      message(STATUS "  sudo apt install clang-tidy  # Ubuntu/Debian")
      message(STATUS "  sudo dnf install clang-tools-extra  # Fedora")
      message(STATUS "  nix-env -iA nixpkgs.clang-tools  # NixOS")
    endif()
    set(ENABLE_CLANG_TIDY OFF)
  endif()
endif()

# Detect cppcheck
if(ENABLE_CPPCHECK STREQUAL "AUTO")
  find_program(CPPCHECK_EXE NAMES cppcheck)
  if(CPPCHECK_EXE)
    message(STATUS "Found cppcheck: ${CPPCHECK_EXE}")
    set(ENABLE_CPPCHECK ON)
  else()
    message(STATUS "cppcheck not found - skipping cppcheck checks")
    message(STATUS "To install cppcheck:")
    if(APPLE)
      message(STATUS "  brew install cppcheck")
    elseif(UNIX)
      message(STATUS "  sudo apt install cppcheck  # Ubuntu/Debian")
      message(STATUS "  sudo dnf install cppcheck  # Fedora")
      message(STATUS "  nix-env -iA nixpkgs.cppcheck  # NixOS")
    endif()
    set(ENABLE_CPPCHECK OFF)
  endif()
endif()

# Configure clang-tidy if enabled
if(ENABLE_CLANG_TIDY AND CLANG_TIDY_EXE)
  if(CMAKE_CXX_CLANG_TIDY)
    # Already configured via CMakePresets.json or command line
    message(STATUS "clang-tidy already configured: ${CMAKE_CXX_CLANG_TIDY}")
  else()
    set(CMAKE_CXX_CLANG_TIDY 
        "${CLANG_TIDY_EXE};--header-filter=^${PROJECT_SOURCE_DIR}/"
        CACHE STRING "clang-tidy command" FORCE)
    message(STATUS "Enabled clang-tidy checks")
  endif()
else()
  # Explicitly disable if user set it but tool not found
  if(CMAKE_CXX_CLANG_TIDY)
    message(WARNING "clang-tidy configured but not found - disabling")
    unset(CMAKE_CXX_CLANG_TIDY CACHE)
  endif()
endif()

# Configure cppcheck if enabled
if(ENABLE_CPPCHECK AND CPPCHECK_EXE)
  if(CMAKE_CXX_CPPCHECK)
    # Already configured via CMakePresets.json or command line
    message(STATUS "cppcheck already configured: ${CMAKE_CXX_CPPCHECK}")
  else()
    set(CMAKE_CXX_CPPCHECK 
        "${CPPCHECK_EXE};--inline-suppr"
        CACHE STRING "cppcheck command" FORCE)
    message(STATUS "Enabled cppcheck checks")
  endif()
else()
  # Explicitly disable if user set it but tool not found
  if(CMAKE_CXX_CPPCHECK)
    message(WARNING "cppcheck configured but not found - disabling")
    unset(CMAKE_CXX_CPPCHECK CACHE)
  endif()
endif()

# Summary
message(STATUS "Code quality tools status:")
message(STATUS "  clang-tidy: ${ENABLE_CLANG_TIDY}")
message(STATUS "  cppcheck:   ${ENABLE_CPPCHECK}")

if(NOT ENABLE_CLANG_TIDY AND NOT ENABLE_CPPCHECK)
  message(STATUS "")
  message(STATUS "💡 Tip: Install clang-tidy and cppcheck for better code quality checks")
  message(STATUS "   Run 'cmake --build . --target help' to see available commands")
endif()
