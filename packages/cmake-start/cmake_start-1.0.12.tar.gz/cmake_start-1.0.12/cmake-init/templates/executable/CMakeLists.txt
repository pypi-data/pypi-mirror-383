cmake_minimum_required(VERSION 3.14)

include(cmake/prelude.cmake)

project(
    {= name =}
    VERSION {= version =}
    DESCRIPTION "{= description =}"
    HOMEPAGE_URL "{= homepage =}"
    LANGUAGES CXX
)

include(cmake/project-is-top-level.cmake)
include(cmake/variables.cmake)

# Find OpenMP after project() to ensure target is available
if(ENABLE_OPENMP)
  find_package(OpenMP QUIET)
  if(OpenMP_FOUND OR OpenMP_CXX_FOUND)
    set(OPENMP_AVAILABLE TRUE CACHE BOOL "OpenMP is available" FORCE)
    message(STATUS "")
    message(STATUS "✅ Found OpenMP (post-project check):")
    if(OpenMP_CXX_VERSION)
      message(STATUS "     C++ version: ${OpenMP_CXX_VERSION}")
    endif()
    message(STATUS "")
    message(STATUS "📝 To use OpenMP in your code:")
    message(STATUS "   1. Add to CMakeLists.txt:")
    message(STATUS "      target_link_libraries(your_target PRIVATE OpenMP::OpenMP_CXX)")
    message(STATUS "   2. In your C/C++ code:")
    message(STATUS "      #include <omp.h>")
    message(STATUS "      #pragma omp parallel for")
    message(STATUS "")
  endif()
endif()

# ---- Declare library ----

add_library(
    {= name =}_lib OBJECT
    source/lib.cpp
)

target_include_directories(
    {= name =}_lib ${warning_guard}
    PUBLIC
    "\$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source>"
)

target_compile_features({= name =}_lib PUBLIC cxx_std_{= std =}){% if pm %}

find_package(fmt REQUIRED)
target_link_libraries({= name =}_lib PRIVATE fmt::fmt){% end %}

# Link OpenMP if available
if(OPENMP_AVAILABLE)
  target_link_libraries({= name =}_lib PRIVATE OpenMP::OpenMP_CXX)
endif()

# ---- Declare executable ----

add_executable({= name =}_exe source/main.cpp)
add_executable({= name =}::exe ALIAS {= name =}_exe)

set_property(TARGET {= name =}_exe PROPERTY OUTPUT_NAME {= name =})

target_compile_features({= name =}_exe PRIVATE cxx_std_{= std =})

target_link_libraries({= name =}_exe PRIVATE {= name =}_lib)

# Link OpenMP to exe if available (for executables that use OpenMP functions directly)
if(OPENMP_AVAILABLE)
  target_link_libraries({= name =}_exe PRIVATE OpenMP::OpenMP_CXX)
endif()

# ---- Install rules ----

if(NOT CMAKE_SKIP_INSTALL_RULES)
  include(cmake/install-rules.cmake)
endif()

# ---- Developer mode ----

if(NOT {= name =}_DEVELOPER_MODE)
  return()
elseif(NOT PROJECT_IS_TOP_LEVEL)
  message(
      AUTHOR_WARNING
      "Developer mode is intended for developers of {= name =}"
  )
endif()

include(cmake/dev-mode.cmake)
