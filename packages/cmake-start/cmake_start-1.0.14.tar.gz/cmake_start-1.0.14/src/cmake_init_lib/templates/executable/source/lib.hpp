#pragma once

#include <string>

/**
 * @brief The core implementation of the executable
 *
 * This class makes up the library part of the executable, which means that the
 * main logic is implemented here. This kind of separation makes it easy to
 * test the implementation for the executable, because the logic is nicely
 * separated from the command-line logic implemented in the main function.
 */
struct library
{
  /**
   * @brief Simply initializes the name member to the name of the project
   */
  library();
{% if openmp %}
  /**
   * @brief Perform parallel computation using OpenMP
   * @param size Size of the array to process
   * @return Sum of computed values
   */
  auto parallel_sum(int size) const -> double;
{% end %}
  std::string name;
};
