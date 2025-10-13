"""
A simple function to create a colormap for a passed list of colors.
"""

import matplotlib.pyplot as plt
import numpy as np
from colour import Color
from matplotlib.colors import LinearSegmentedColormap


def custom_cmap(color_list: list, preview: bool = False) -> LinearSegmentedColormap:
    """Creates a colormap to a given list of colors.
    Also provides a preview of the colormap via plt.imshow().

    Parameters
    ----------
    color_list : list
        List of hexadecimal color codes with leading number sign (#).

    preview : bool, optional
        If ``True``, show a preview of the colormap. Default: ``False``

    Returns
    -------
    cmap : :class:`~matplotlib.colors.LinearSegmentedColormap`
        A colormap containing the given colors.

    Examples
    --------
    >>> from labreportpy.color import custom_cmap
    >>> cmap = custom_cmap(["#141515", "#342f98"])
    """

    cmap = LinearSegmentedColormap.from_list(
        "my_list", [Color(c1).rgb for c1 in color_list]
    )
    plt.figure(figsize=(15, 3))
    plt.imshow(
        [list(np.arange(0, len(color_list), 0.1))],
        interpolation="nearest",
        origin="lower",
        cmap=cmap,
    )
    plt.xticks([])
    plt.yticks([])

    return cmap
