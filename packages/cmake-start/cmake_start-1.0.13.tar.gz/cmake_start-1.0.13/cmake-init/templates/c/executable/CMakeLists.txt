cmake_minimum_required(VERSION 3.{% if cmake_321 %}21{% else %}14{% end %})

include(cmake/prelude.cmake)

project(
    {= name =}
    VERSION {= version =}
    DESCRIPTION "{= description =}"
    HOMEPAGE_URL "{= homepage =}"
    LANGUAGES C
)
{% if not cmake_321 %}
include(cmake/project-is-top-level.cmake){% end %}
include(cmake/variables.cmake)

# Find OpenMP after project() to ensure target is available
if(ENABLE_OPENMP)
  find_package(OpenMP QUIET)
  if(OpenMP_FOUND OR OpenMP_C_FOUND)
    set(OPENMP_AVAILABLE TRUE CACHE BOOL "OpenMP is available" FORCE)
    message(STATUS "")
    message(STATUS "✅ Found OpenMP (post-project check):")
    if(OpenMP_C_VERSION)
      message(STATUS "     C version: ${OpenMP_C_VERSION}")
    endif()
    message(STATUS "")
    message(STATUS "📝 To use OpenMP in your code:")
    message(STATUS "   1. Add to CMakeLists.txt:")
    message(STATUS "      target_link_libraries(your_target PRIVATE OpenMP::OpenMP_C)")
    message(STATUS "   2. In your C code:")
    message(STATUS "      #include <omp.h>")
    message(STATUS "      #pragma omp parallel for")
    message(STATUS "")
  endif()
endif()

# ---- Declare library ----

add_library(
    {= name =}_lib OBJECT
    source/lib.c
)

target_include_directories(
    {= name =}_lib ${warning_guard}
    PUBLIC
    "\$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source>"
)

target_compile_features({= name =}_lib PUBLIC c_std_{= std =}){% if pm %}

find_package(json-c REQUIRED)
target_link_libraries({= name =}_lib PRIVATE json-c::json-c)

# Unfortunately, hedley provides no CMake package to be found trivially using
# find_package, so it has to be found manually
find_path(HEDLEY_INCLUDE_DIR hedley.h{% if cmake_321 %} REQUIRED){% else %})
if(NOT HEDLEY_INCLUDE_DIR)
  message(FATAL_ERROR "Couldn't find hedley.h (${HEDLEY_INCLUDE_DIR})")
endif(){% end %}
target_include_directories(
    {= name =}_lib SYSTEM
    PRIVATE "${HEDLEY_INCLUDE_DIR}"
){% end %}

# Link OpenMP if available
if(OPENMP_AVAILABLE)
  target_link_libraries({= name =}_lib PRIVATE OpenMP::OpenMP_C)
endif()

# ---- Declare executable ----

add_executable({= name =}_exe source/main.c)
add_executable({= name =}::exe ALIAS {= name =}_exe)

set_property(TARGET {= name =}_exe PROPERTY OUTPUT_NAME {= name =})

target_compile_features({= name =}_exe PRIVATE c_std_{= std =})

target_link_libraries({= name =}_exe PRIVATE {= name =}_lib)

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
