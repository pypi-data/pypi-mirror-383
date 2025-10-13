from pathlib import Path

import numpy as np
from uncertainties import ufloat, ufloat_fromstr

__all__ = ["QTYWriter"]


class QTYWriter:
    """
    A simple class to write quantities to a .tex
    file.

    Parameters
    ----------
    build_dir : str or Path
        Path to the base directory.
    """

    def __init__(self, build_dir: str or Path = "") -> None:
        """Initializes the QTYWriter class.

        Parameters
        ----------
        build_dir : str or Path
            Path to the base directory.
        """
        if not build_dir:
            raise ValueError("No base directory provided!")

        self.build_dir = build_dir

        if not Path(self.build_dir).is_dir():
            Path(self.build_dir).mkdir(parents=True, exist_ok=True)

    def write_value(
        self,
        filename: str | Path,
        val: ufloat,
        unit: str = "",
        prec: int = 3,
    ) -> None:
        """Writes given value/quantity to .tex file.

        Parameters
        ----------
        filename: str
            Name of the file to write to.
        val : ufloat
            Value/quantity to write to file.
        unit : str, optional
            Unit of the quantity. If left empty, a
            number ``\\num{}`` is written instead.
            Default: ``''``
        prec : int, optional
            Precision for rounding. Default: ``3``
        """
        val = str(val).split("e")

        exp = "" if len(val) < 2 else "e" + val[1]

        val = ufloat_fromstr(val[0])

        nom = np.round(val.n, prec)
        std = np.round(val.s, prec)

        if unit == "":
            value = rf"\num{{{nom} \pm {std}{exp}}}"
        else:
            value = rf"\qty{{{nom} \pm {std}{exp}}}{{{unit}}}"

        if self.build_dir[-1] == "/":
            self.build_dir = self.build_dir[:-1]
        if filename[0] == "/":
            filename = filename[1:]

        with open(self.build_dir + "/" + filename, "w") as f:
            f.write(value)
