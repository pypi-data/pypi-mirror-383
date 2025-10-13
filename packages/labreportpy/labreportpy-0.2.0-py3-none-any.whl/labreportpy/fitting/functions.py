# A collection of functions for fitting of data
import numpy as np


def lin_fit(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * x + b


def exp_fit(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * np.exp(-b * x) + c


def gauss_fit(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * np.exp(-((x - b) ** 2) / (2 * c**2))


def gauss_fit2(
    x: np.ndarray,
    a: float,
    b: float,
    c: float,
    d: float,
    e: float,
    f: float,
) -> np.ndarray:
    return a * np.exp(-((x - b) ** 2) / (2 * c**2)) + d * np.exp(
        -((x - e) ** 2) / (2 * f**2)
    )


def weibull(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * b * x ** (b - 1) * np.exp(-a * x**b)


def sigmoid(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    a / (1 + np.exp(-(x - b))) + c
