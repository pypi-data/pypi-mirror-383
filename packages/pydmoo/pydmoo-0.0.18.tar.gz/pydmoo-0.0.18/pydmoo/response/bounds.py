import numpy as np


def matrix_conditional_update(x_curr, lb, ub, x_prev):
    """
    Vectorized conditional matrix update with bounded interpolation.

    Parameters
    ----------
    x_curr : ndarray, shape (N, n)
        Observation matrix.
    lb : ndarray, shape (1, n) or (n,)
        Lower bounds for each dimension.
    ub : ndarray, shape (1, n) or (n,)
        Upper bounds for each dimension.
    x_prev : ndarray, shape (N, n)
        Previous state matrix.

    Returns
    -------
    ndarray, shape (N, n)
        Updated matrix where:
        - Values within bounds remain unchanged
        - Values below bounds become 0.5*(a + x_prev)
        - Values above bounds become 0.5*(b + x_prev)

    Notes
    -----
    Uses NumPy broadcasting for efficient vectorized operations.
    """
    lb = np.reshape(lb, (1, -1))
    ub = np.reshape(ub, (1, -1))
    x_new = np.zeros_like(x_curr)

    mask = (x_curr >= lb) & (x_curr <= ub)
    x_new[mask] = x_curr[mask]

    mask = x_curr < lb
    x_new[mask] = 0.5 * (lb + x_prev)[mask]

    mask = x_curr > ub
    x_new[mask] = 0.5 * (ub + x_prev)[mask]

    return x_new


def clip_and_randomize(x, lb, ub):
    """
    Clip values to bounds with random replacement for out-of-bounds values.

    Parameters
    ----------
    x : ndarray, shape (N, n)
        Input matrix.
    lb : ndarray, shape (1, n) or (n,)
        Lower bounds.
    ub : ndarray, shape (1, n) or (n,)
        Upper bounds.

    Returns
    -------
    ndarray, shape (N, n)
        Matrix where out-of-bounds values are replaced with uniform random
        values within [lb, ub] for each dimension.

    See Also
    --------
    numpy.random.uniform : Used for random value generation.
    """
    out_of_bounds = (x < lb) | (x > ub)
    random_samples = np.random.uniform(low=lb, high=ub, size=x.shape)
    return np.where(out_of_bounds, random_samples, x)


def clip_by_numpy(x, lb, ub):
    """
    Clip values to interval [lb, ub].

    Parameters
    ----------
    x : ndarray
        Array containing elements to clip.
    lb : ndarray or scalar
        Minimum value.
    ub : ndarray or scalar
        Maximum value.

    Returns
    -------
    ndarray
        Clipped array where:
        x_clipped = max(lb, min(ub, x))

    Notes
    -----
    This is a wrapper around numpy.clip() with identical behavior.
    """
    return np.clip(x, lb, ub)
