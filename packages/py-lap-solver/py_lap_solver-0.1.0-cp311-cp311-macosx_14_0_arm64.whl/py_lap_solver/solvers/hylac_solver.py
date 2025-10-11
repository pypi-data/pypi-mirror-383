import numpy as np

from ..base import LapSolver


class HyLACsolver(LapSolver):
    """HyLAC: Hybrid Linear Assignment solver in CUDA.

    This solver uses a hybrid approach combining classical and tree variants
    of the Hungarian algorithm, optimized for GPU execution. It is designed
    for solving the Linear Assignment Problem efficiently on NVIDIA GPUs.

    HyLAC is particularly effective for:
    - Single large LAPs (fine-grained solver)
    - Batches of small LAPs (stream solver, coarse-grained)
    - Both dense and sparse cost matrices

    Note: This solver requires CUDA support and will only be available on
    systems with NVIDIA GPUs and CUDA installed.

    Parameters
    ----------
    maximize : bool, optional
        If True, solve the maximization problem instead of minimization.
        Default is False (minimization).
    unassigned_value : int, optional
        Value to use for unassigned rows/columns in the output arrays.
        Default is -1.
    device_id : int, optional
        CUDA device ID to use for computation. Default is 0.
    use_stream_solver : bool, optional
        If True, use the stream solver for batch problems (solves each LAP
        with a single thread block). If False, each LAP uses multiple blocks.
        Default is True for batches.

    References
    ----------
    Samiran Kawtikwar and Rakesh Nagi. 2024. HyLAC: Hybrid linear assignment
    solver in CUDA. Journal of Parallel and Distributed Computing 187,
    (May 2024), 104838. https://doi.org/10.1016/j.jpdc.2024.104838
    """

    def __init__(
        self, maximize=False, unassigned_value=-1, device_id=0, use_stream_solver=True, **kwargs
    ):
        super().__init__()
        self.maximize = maximize
        self.unassigned_value = unassigned_value
        self.device_id = device_id
        self.use_stream_solver = use_stream_solver

        # Try to import the CUDA extension
        try:
            from py_lap_solver import _hylac

            self._backend = _hylac
            self._available = True
        except ImportError:
            self._backend = None
            self._available = False

    @staticmethod
    def is_available():
        """Check if the HyLAC solver is available."""
        try:
            from py_lap_solver import _hylac  # noqa: F401

            return True
        except ImportError:
            return False

    @staticmethod
    def has_cuda():
        """Check if CUDA support is available."""
        try:
            from py_lap_solver import _hylac

            return _hylac.HAS_CUDA
        except ImportError:
            return False

    def solve_single(self, cost_matrix, num_valid=None):
        """Solve a single linear assignment problem on GPU.

        Parameters
        ----------
        cost_matrix : np.ndarray
            Cost matrix of shape (N, M). Must be square (N == M) for HyLAC.
        num_valid : int, optional
            Number of valid rows/cols if matrix is padded.
            If None, uses the full matrix size.

        Returns
        -------
        row_to_col : np.ndarray
            Array of shape (N,) where row_to_col[i] gives the column assigned to row i.
            Unassigned rows have value `unassigned_value`.
        """
        if not self._available:
            raise RuntimeError(
                "HyLAC solver is not available. "
                "Please rebuild the package with CUDA support enabled."
            )

        cost_matrix = np.asarray(cost_matrix)
        n_rows, n_cols = cost_matrix.shape

        # HyLAC requires square matrices
        if n_rows != n_cols:
            raise ValueError(
                f"HyLAC requires square cost matrices, got shape {cost_matrix.shape}. "
                "Consider padding your matrix to make it square."
            )

        # Handle maximization by negating
        if self.maximize:
            cost_matrix = -cost_matrix.copy()

        # Determine num_valid
        num_valid_arg = n_rows if num_valid is None else num_valid

        # Choose precision based on input dtype
        if cost_matrix.dtype == np.float32:
            result = self._backend.solve_hylac_float(cost_matrix, num_valid=num_valid_arg)
        else:
            # Convert to float64 if not already
            if cost_matrix.dtype != np.float64:
                cost_matrix = cost_matrix.astype(np.float64)
            result = self._backend.solve_hylac_double(cost_matrix, num_valid=num_valid_arg)

        return result

    def batch_solve(self, batch_cost_matrices, num_valid=None):
        """Solve multiple linear assignment problems on GPU.

        Uses the HyLAC stream solver for efficient batch processing, where
        each LAP is solved by a single thread block in parallel.

        Parameters
        ----------
        batch_cost_matrices : np.ndarray
            Batch of cost matrices of shape (B, N, M). Each matrix must be
            square (N == M) for HyLAC.
        num_valid : np.ndarray or int, optional
            Number of valid rows/cols for each matrix.
            Can be a scalar (same for all) or array of shape (B,).

        Returns
        -------
        np.ndarray
            Array of shape (B, N) where element [b, i] gives the column assigned
            to row i in batch element b. Unassigned rows have value `unassigned_value`.
        """
        if not self._available:
            raise RuntimeError(
                "HyLAC solver is not available. "
                "Please rebuild the package with CUDA support enabled."
            )

        batch_cost_matrices = np.asarray(batch_cost_matrices)

        if batch_cost_matrices.ndim != 3:
            raise ValueError("batch_cost_matrices must be 3D array (B, N, M)")

        batch_size, n_rows, n_cols = batch_cost_matrices.shape

        # HyLAC requires square matrices
        if n_rows != n_cols:
            raise ValueError(
                f"HyLAC requires square cost matrices, got shape ({n_rows}, {n_cols}). "
                "Consider padding your matrices to make them square."
            )

        # Handle maximization by negating
        if self.maximize:
            batch_cost_matrices = -batch_cost_matrices.copy()

        # Handle num_valid parameter
        num_valid_arg = None
        if num_valid is not None:
            if isinstance(num_valid, (int, np.integer)):
                num_valid_arg = int(num_valid)
            else:
                num_valid_arg = np.asarray(num_valid, dtype=np.int64)

        # Choose precision based on input dtype
        if batch_cost_matrices.dtype == np.float32:
            return self._backend.batch_solve_hylac_float(
                batch_cost_matrices, num_valid=num_valid_arg
            )
        else:
            # Convert to float64 if not already
            if batch_cost_matrices.dtype != np.float64:
                batch_cost_matrices = batch_cost_matrices.astype(np.float64)
            return self._backend.batch_solve_hylac_double(
                batch_cost_matrices, num_valid=num_valid_arg
            )
