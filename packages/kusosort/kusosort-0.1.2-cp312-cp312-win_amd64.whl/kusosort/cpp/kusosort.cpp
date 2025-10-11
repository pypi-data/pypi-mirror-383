// src/kusosort/cpp/kusosort.cpp (Final Version)

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <vector>
#include <string> // For std::string support
#include <algorithm>
#include <random>
#include <iostream>
#include <utility>

namespace py = pybind11;

// --- Sorting Algorithm Implementations ---

// (Bogo, Bozo, Stalin, Miracle sorts are unchanged)
template<typename T>
void bogo_sort(std::vector<T>& data) {
    std::random_device rd;
    std::mt19937 g(rd());
    while (!std::is_sorted(data.begin(), data.end())) {
        std::shuffle(data.begin(), data.end(), g);
    }
}

template<typename T>
void bozo_sort(std::vector<T>& data) {
    std::random_device rd;
    std::mt19937 g(rd());
    std::uniform_int_distribution<size_t> dist(0, data.size() - 1);
    while (!std::is_sorted(data.begin(), data.end())) {
        std::swap(data[dist(g)], data[dist(g)]);
    }
}

template<typename T>
std::vector<T> stalin_sort(const std::vector<T>& data) {
    if (data.empty()) return {};
    std::vector<T> result;
    result.push_back(data[0]);
    for (size_t i = 1; i < data.size(); ++i) {
        if (data[i] >= result.back()) {
            result.push_back(data[i]);
        }
    }
    return result;
}

template<typename T>
bool miracle_sort(std::vector<T>& data, int max_attempts, const std::function<void()>& prey) {
    for (int i = 0; i < max_attempts; ++i) {
        prey();
        if (std::is_sorted(data.begin(), data.end())) {
            return true;
        }
    }
    return false;
}


// FIXED: Abe Sort now returns a new vector instead of modifying in-place.
template<typename T>
std::vector<T> abe_sort(const std::vector<T>& data) {
    if (data.empty()) {
        return {};
    }
    std::vector<T> result = data; 
    T running_max = result[0];

    for (size_t i = 1; i < result.size(); ++i) {
        if (result[i] < running_max) {
            result[i] = running_max;
        }
        else {
            running_max = result[i];
        }
    }
    return result; 
}

// FIXED: Quantum Bogo Sort now handles already-sorted lists correctly.
template<typename T>
std::vector<std::pair<int, std::vector<T>>> quantum_bogo_sort_multiverse(
    const std::vector<T>& data,
    int num_universes)
{
    std::vector<std::pair<int, std::vector<T>>> successful_universes;
    std::random_device rd;
    std::mt19937 g(rd());

    for (int i = 0; i < num_universes; ++i) {
        std::vector<T> universe_data = data;

        // FIX: Only shuffle if the list is not already sorted.
        if (!std::is_sorted(universe_data.begin(), universe_data.end())) {
            std::shuffle(universe_data.begin(), universe_data.end(), g);
        }

        if (std::is_sorted(universe_data.begin(), universe_data.end())) {
            successful_universes.push_back({ i + 1, universe_data });
        }
    }
    return successful_universes;
}

// --- Bindings for the Python Module ---
PYBIND11_MODULE(_kusosort_impl, m) {
    m.doc() = "C++ implementations of various joke sorting algorithms.";

    // Bogo Sort (int, float, and string)
    m.def("bogo_sort_int", &bogo_sort<int>);
    m.def("bogo_sort_float", &bogo_sort<double>);
    m.def("bogo_sort_string", &bogo_sort<std::string>); // ADDED

    // Bozo Sort (int, float, and string)
    m.def("bozo_sort_int", &bozo_sort<int>);
    m.def("bozo_sort_float", &bozo_sort<double>);
    m.def("bozo_sort_string", &bozo_sort<std::string>); // ADDED

    // Stalin Sort (int, float, and string)
    m.def("stalin_sort_int", &stalin_sort<int>);
    m.def("stalin_sort_float", &stalin_sort<double>);
    m.def("stalin_sort_string", &stalin_sort<std::string>); // ADDED

    // Miracle Sort (int, float, and string)
    m.def("miracle_sort_int", &miracle_sort<int>);
    m.def("miracle_sort_float", &miracle_sort<double>);
    m.def("miracle_sort_string", &miracle_sort<std::string>); // ADDED

    // Abe Sort (int, float, and string) - docstring removed for brevity
    m.def("abe_sort_int", &abe_sort<int>);
    m.def("abe_sort_float", &abe_sort<double>);
    m.def("abe_sort_string", &abe_sort<std::string>); // ADDED

    // Quantum Bogo Sort (int, float, and string)
    m.def("quantum_bogo_sort_multiverse_int", &quantum_bogo_sort_multiverse<int>);
    m.def("quantum_bogo_sort_multiverse_float", &quantum_bogo_sort_multiverse<double>);
    m.def("quantum_bogo_sort_multiverse_string", &quantum_bogo_sort_multiverse<std::string>); // ADDED
}