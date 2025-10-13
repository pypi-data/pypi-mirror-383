include(cmake/folders.cmake)

include(CTest)
if(BUILD_TESTING)
  add_subdirectory(test)
endif()
{% if exe %}
add_custom_target(
    run-exe
    COMMAND {= name =}_exe
    VERBATIM
)
add_dependencies(run-exe {= name =}_exe)
{% end %}
option(BUILD_MCSS_DOCS "Build documentation using Doxygen and m.css" OFF)
if(BUILD_MCSS_DOCS)
  include(cmake/docs.cmake)
endif()

option(ENABLE_COVERAGE "Enable coverage support separate from CTest's" OFF)
if(ENABLE_COVERAGE)
  include(cmake/coverage.cmake)
endif()

# Re-check OpenMP now that languages are enabled
if(ENABLE_OPENMP AND NOT OPENMP_AVAILABLE)
  find_package(OpenMP QUIET)

  if(OpenMP_FOUND OR OpenMP_C_FOUND OR OpenMP_CXX_FOUND)
    message(STATUS "")
    message(STATUS "✅ Found OpenMP (post-project check):")
    if(OpenMP_C_VERSION)
      message(STATUS "     C version: ${OpenMP_C_VERSION}")
    endif()
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
    set(OPENMP_AVAILABLE TRUE CACHE BOOL "OpenMP is available" FORCE)
  endif()
endif()

include(cmake/lint-targets.cmake)
include(cmake/spell-targets.cmake)

add_folders(Project)
