import numpy as np


def fmt(params: np.ndarray, cov: np.ndarray, fmt: int = 3) -> np.ndarray:
    """Calculates uncertainties and formats params and uncertainties
    to a string for printing. Result: param ± uncertainty

    Parameters
    ----------
    params: np.ndarray
        Array of parameters.
    cov: np.ndarray
        Covariance matrix.

    Returns
    -------
    formatted_strings: np.ndarray
        Array of formatted strings with params and uncertainties
        delimited by a ± sign.
    """
    par = [f"{p:.{fmt}f}" for p in params]
    uncert = [f" ± {np.sqrt(u):.{fmt}f}" for u in np.diag(cov)]

    return np.char.add(par, uncert)
