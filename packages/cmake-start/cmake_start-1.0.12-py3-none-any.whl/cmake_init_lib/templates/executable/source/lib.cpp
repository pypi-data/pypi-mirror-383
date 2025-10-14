#include "lib.hpp"{% if pm %}

#include <fmt/core.h>{% end %}{% if openmp %}

#ifdef _OPENMP
#  include <omp.h>
#endif
#include <cmath>
#include <vector>{% end %}

library::library()
    : name {{% if pm %}fmt::format("{}", "{= name =}"){% else %}"{= name =}"{% end %}}
{
}
{% if openmp %}
auto library::parallel_sum(int size) const -> double
{
  std::vector<double> data(static_cast<std::size_t>(size));
  double sum = 0.0;

#ifdef _OPENMP
  // Initialize data in parallel
  #pragma omp parallel for
  for (int i = 0; i < size; ++i) {
    data[static_cast<std::size_t>(i)] = std::sin(i * 0.001);
  }

  // Compute sum in parallel with reduction
  #pragma omp parallel for reduction(+:sum)
  for (int i = 0; i < size; ++i) {
    sum += data[static_cast<std::size_t>(i)];
  }
#else
  // Sequential fallback when OpenMP is not available
  for (int i = 0; i < size; ++i) {
    data[static_cast<std::size_t>(i)] = std::sin(i * 0.001);
  }
  for (int i = 0; i < size; ++i) {
    sum += data[static_cast<std::size_t>(i)];
  }
#endif

  return sum;
}
{% end %}
