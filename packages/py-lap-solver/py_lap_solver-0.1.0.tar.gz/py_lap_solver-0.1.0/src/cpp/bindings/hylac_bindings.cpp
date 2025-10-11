#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cstdint>

namespace py = pybind11;

// Placeholder for HyLAC solver - will be implemented when CUDA is enabled
// The HyLAC solver requires CUDA compilation and is currently disabled

py::array_t<int32_t> solve_hylac_float(
    py::array_t<float> cost_matrix,
    int num_valid
) {
    throw std::runtime_error(
        "HyLAC solver requires CUDA support which is not currently enabled. "
        "Please rebuild with CUDA enabled to use this solver."
    );
}

py::array_t<int32_t> solve_hylac_double(
    py::array_t<double> cost_matrix,
    int num_valid
) {
    throw std::runtime_error(
        "HyLAC solver requires CUDA support which is not currently enabled. "
        "Please rebuild with CUDA enabled to use this solver."
    );
}

py::array_t<int32_t> batch_solve_hylac_float(
    py::array_t<float> batch_cost_matrices,
    py::object num_valid
) {
    throw std::runtime_error(
        "HyLAC solver requires CUDA support which is not currently enabled. "
        "Please rebuild with CUDA enabled to use this solver."
    );
}

py::array_t<int32_t> batch_solve_hylac_double(
    py::array_t<double> batch_cost_matrices,
    py::object num_valid
) {
    throw std::runtime_error(
        "HyLAC solver requires CUDA support which is not currently enabled. "
        "Please rebuild with CUDA enabled to use this solver."
    );
}

PYBIND11_MODULE(_hylac, m) {
    m.doc() = "HyLAC: Hybrid Linear Assignment solver in CUDA";

    m.def("solve_hylac_float", &solve_hylac_float,
          "Solve single LAP with HyLAC (float32)",
          py::arg("cost_matrix"),
          py::arg("num_valid") = -1);

    m.def("solve_hylac_double", &solve_hylac_double,
          "Solve single LAP with HyLAC (float64)",
          py::arg("cost_matrix"),
          py::arg("num_valid") = -1);

    m.def("batch_solve_hylac_float", &batch_solve_hylac_float,
          "Solve batch of LAPs with HyLAC (float32)",
          py::arg("batch_cost_matrices"),
          py::arg("num_valid") = py::none());

    m.def("batch_solve_hylac_double", &batch_solve_hylac_double,
          "Solve batch of LAPs with HyLAC (float64)",
          py::arg("batch_cost_matrices"),
          py::arg("num_valid") = py::none());

    // Compile-time feature flags
    #ifdef LAP_CUDA
        m.attr("HAS_CUDA") = true;
    #else
        m.attr("HAS_CUDA") = false;
    #endif
}
