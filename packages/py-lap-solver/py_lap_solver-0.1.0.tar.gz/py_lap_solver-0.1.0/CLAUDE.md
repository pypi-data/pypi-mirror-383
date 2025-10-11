# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`py-lap-solver` is a unified Python framework for Linear Assignment Problem (LAP) solvers. It provides a common interface for multiple solver implementations, ranging from pure Python (scipy) to optimized C++ implementations with OpenMP and CUDA support.

The Linear Assignment Problem seeks to find an optimal assignment between two sets given a cost matrix, minimizing (or maximizing) the total cost of the assignment.

## Build and Installation

```bash
# Install the package in editable mode (without C++ extensions)
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Build with C++ extensions (requires CMake 3.24+, pybind11)
pip install -e . --no-build-isolation
```

The build system uses `scikit-build-core` to integrate CMake with Python packaging. The C++ extensions (`_batched_scipy_lap` and `_lap1015`) are optional - the package falls back to ScipySolver if not available.

### Optional Build Features

- **OpenMP**: Automatically detected on macOS (via Homebrew libomp at `/opt/homebrew/opt/libomp` or `/usr/local/opt/libomp`) and Linux. Enables parallel LAP solving in BatchedScipySolver.
- **CUDA**: Detected if CUDA compiler is available. Enables GPU-accelerated solving (LAP1015 has support, not yet fully exposed in Python bindings).

## Testing

```bash
# Run tests with pytest
pytest tests/

# Or use make
make test
```

The tests directory contains:
- Test files for validating solver correctness across single, batch, and rectangular test cases
- Common utilities for loading solvers and generating test matrices

## Code Formatting and Linting

The project uses `black` (line length 100) for formatting and `ruff` for linting. Use the Makefile for convenience:

```bash
make format      # Format code with black
make lint        # Lint code with ruff
make lint-fix    # Auto-fix linting issues
make check       # Run all checks
make all         # Format, lint-fix, check, and test
```

Ruff configuration enables common checks (pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear, flake8-comprehensions, flake8-simplify) but ignores:
- E501 (line too long) - handled by black
- N803/N806 (naming conventions) - conflicts with numpy conventions like `n_rows`, `dim_N`

## Code Architecture

### Three-Layer Design

1. **Base Interface** (`src/py_lap_solver/base.py`)
   - `LapSolver`: Abstract base class defining the solver interface
   - Key methods: `solve_single(cost_matrix, num_valid)` and `batch_solve(batch_cost_matrices, num_valid)`
   - All solvers must implement these methods and return assignments in the same format

2. **Solver Implementations** (`src/py_lap_solver/solvers/`)
   - `ScipySolver`: Pure Python wrapper around scipy.optimize.linear_sum_assignment (Hungarian algorithm). Always available.
   - `BatchedScipySolver`: C++ implementation of scipy's algorithm with optional OpenMP parallelization for batch processing
     - Uses pybind11 bindings in `src/cpp/bindings/batched_scipy_bindings.cpp`
     - Supports float32 and float64 precision
     - Runtime feature detection: `is_available()`, `has_openmp()`
   - `Lap1015Solver`: C++ implementation using the highly optimized LAP1015 algorithm (shortest augmenting path)
     - Uses pybind11 bindings in `src/cpp/bindings/lap1015_bindings.cpp`
     - Supports float32 and float64 precision
     - Runtime feature detection: `is_available()`, `has_openmp()`, `has_cuda()`
     - Note: Currently solves batches sequentially (no parallel batch support yet)

3. **C++ Core**
   - **Batched Scipy** (`src/cpp/batched_scipy/`): C++ port of scipy's rectangular_lsap algorithm with OpenMP batch parallelization
   - **LAP1015** (`src/cpp/lap1015/`): Highly optimized LAP solver implementation
     - Template-based architecture with multiple cost function and iterator types
     - Three execution modes: sequential, OpenMP (`lap::omp::`), CUDA (`lap::cuda::`)
     - Entry point: `lap.h` defines all templates and includes implementation headers
     - Compile-time flag `LAP_QUIET` suppresses debug output

### Key Design Patterns

- **Unified Solver Interface**: All solvers inherit from `LapSolver` and provide consistent `solve_single`/`batch_solve` methods
- **Return Format**: All solvers return a `row_to_col` array where `row_to_col[i]` gives the column assigned to row i. Unassigned rows have value -1 (or custom `unassigned_value`). This differs from scipy's `(row_ind, col_ind)` tuple format.
- **Optional Dependencies**: C++ solvers gracefully degrade if extensions are unavailable, using `is_available()` static methods
- **num_valid parameter**: Allows solving variable-sized problems with fixed-size padded matrices (only first `num_valid` rows/cols are used)
- **Rectangular Matrix Support**: All solvers handle non-square matrices. Lap1015Solver internally pads to square with high-cost padding values.

### C++ Binding Structure

Two pybind11 modules are built:

1. **_batched_scipy_lap**:
   - `solve_batched_lap_float(batch_cost, maximize, num_valid, unassigned_value)`
   - `solve_batched_lap_double(batch_cost, maximize, num_valid, unassigned_value)`
   - `HAS_OPENMP` flag (compile-time detection)

2. **_lap1015**:
   - `solve_lap_float(cost_matrix, num_valid)`
   - `solve_lap_double(cost_matrix, num_valid)`
   - `HAS_OPENMP`, `HAS_CUDA` flags (compile-time detection)

Python wrappers select the appropriate C++ function based on `dtype` and `use_openmp` parameters.

## Development Notes

### Adding a New Solver

1. Create new solver class in `src/py_lap_solver/solvers/`
2. Inherit from `LapSolver` and implement `solve_single` and `batch_solve`
3. Ensure return format is `row_to_col` array (not scipy's tuple format)
4. Export from `solvers/__init__.py` and update `get_available_solvers()`
5. Update `benchmarks/utils.py` to load the new solver

### CMake Configuration

- C++17 standard required
- Architecture-specific optimizations: `-march=native` (x86) or `-mcpu=native` (ARM)
- Release flags: `-O3 -fPIC`
- OpenMP detected via `find_package(OpenMP)` with special macOS Homebrew paths
- CUDA detected via `check_language(CUDA)`
- Compile definitions: `LAP_OPENMP`, `LAP_CUDA`, `LAP_QUIET`

### Correctness Validation

The `test_correctness.py` script validates that all solvers produce identical costs (within tolerance) for:
- Square matrices (various sizes: 10, 50, 100, 500)
- Rectangular matrices (non-square)
- Batch problems (multiple matrices)

All solvers should agree within 1e-6 (single) or 1e-5 (batch) tolerance.

### Important Implementation Details

- **Maximization**: Handled by negating the cost matrix before solving
- **Rectangular matrices**: Lap1015Solver pads to square with high-cost values (`max_cost * 1000 + 1e10`)
- **Batch solving**: BatchedScipySolver parallelizes across batch dimension with OpenMP. Lap1015Solver currently solves sequentially.
- **Precision**: All solvers support both float32 and float64, auto-detected from input dtype
