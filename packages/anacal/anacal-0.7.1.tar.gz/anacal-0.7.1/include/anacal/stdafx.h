#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <memory>
#include <complex>
#include <tuple>
#include <cmath>
#include <random>
#include <iostream>
#include <algorithm>
#include <stdexcept>
#include <array>
#include <limits>
#include <optional>

namespace py = pybind11;

// Constatn for 1 / sqrt(2.0)
inline constexpr double one_over_sqrt2 = 0.7071067811865475;

struct BrightStar {
    float x;
    float y;
    float r;
};

struct Position {
    double y;
    double x;
};


