"""
Functions to automatically change foreground colors of given object depending
on the background color of either the used colormap or the figure.
"""

from matplotlib import cm
from PIL import ImageColor


def auto_color(color: str, tolerance: int | float = 186) -> str:
    """Changes color of an object to black or white depending
    on the (background) color you pass to this function.

    Parameters
    ----------
    color: str
        Color value in hexadecimal format with leading number sign (#).
    tolerance: int or float
        Decides where to return black or white.

    Returns
    -------
    color: str
        Output color, either black or white, in hexadecimal format.
    """
    color = ImageColor.getcolor(color, "RGB")

    if (color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114) > tolerance:
        color = "#000000"
    else:
        color = "#ffffff"

    return color


def auto_color_cmap(
    data_value: float,
    cmap: str,
    tolerance: float = 0.45,
) -> str:
    """Changes color of an object to black or white depending
    on the colormap and the data_value you pass to this function.

    Parameters
    ----------
    data_value: float
        A data point.
    cmap: str
        The name of the colormap.
    tolerance: float
        Decides where to return black or white.

    Returns
    -------
    color: str
        Output color, either black or white, in hexadecimal format.
    """
    cmap = cm.get_cmap(cmap) or cmap
    rgba = cmap(data_value)

    if (rgba[0] * 0.299 + rgba[1] * 0.587 + rgba[2] * 0.114) > tolerance:
        color = "#000000"
    else:
        color = "#ffffff"

    return color
