from collections.abc import Callable

import numpy as np
from rich.console import Console
from rich.table import Table
from scipy.optimize import curve_fit

from labreportpy.utils import param_fmt

__all__ = ["fit"]


def fit(
    func: Callable,
    xdata: np.ndarray,
    ydata: np.ndarray,
    p0: np.ndarray | list | None = None,
    fmt: int = 3,
    title: str = "",
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, tuple]:
    """Calculates and prints fit params. Also prints
    the uncertainties for each parameter.
    This function utilizes scipy's curve_fit method.

    For more information, see :func:`scipy.optimize.curve_fit`.


    Parameters
    ----------
    func: callable
        The model function, f(x, …). It must take the
        independent variable as the first argument and
        the parameters to fit as separate remaining
        arguments.
    xdata: array_like
        The independent variable where the data is
        measured. Should usually be an M-length sequence
        or an (k,M)-shaped array for functions with k
        predictors, and each element should be float
        convertible if it is an array like object.
    ydata : array_like
        The dependent data, a length M array - nominally
        ``f(xdata, ...)``.
    p0 : array_like, optional
        Initial guess for the parameters (length N).
        If None, then the initial values will all be 1
        (if the number of parameters for the function
        can be determined using introspection, otherwise
        a ValueError is raised). Default: ``None``
    fmt: int, optional
        Number of decimal places to format. Default: ``3``
    title: str, optional
        Additional title for the table. Default: ``''``

    **kwargs
        Additional kwargs to :func:`scipy.optimize.curve_fit`

    Returns
    -------
    params: np.ndarray
        Optimal values for the parameters so that the sum
        of the squared residuals of ``f(xdata, *parameters) - ydata``
        is minimized.
    cov: np.ndarray
        The estimated approximate covariance of parameters. The
        diagonals provide the variance of the parameter estimate.
    errors: np.ndarray
        The uncertainties calculated from the estimated approximate
        covariance of the parameter.
    vars: tuple
        Variable names of ``func``.
    """
    vars = func.__code__.co_varnames

    params, cov = curve_fit(f=func, xdata=xdata, ydata=ydata, p0=p0, **kwargs)

    console = Console()
    table = Table(
        title="Fit Parameters" if title == "" else f"Fit Parameters: {title}",
        box=None,
        header_style="bold magenta",
    )

    for var in vars[1:]:
        table.add_column(var, justify="left")

    table.add_row(*param_fmt.fmt(params, cov, fmt=fmt))
    console.print(table)

    errors = np.sqrt(np.diag(cov))

    return params, cov, errors, vars[1:]
