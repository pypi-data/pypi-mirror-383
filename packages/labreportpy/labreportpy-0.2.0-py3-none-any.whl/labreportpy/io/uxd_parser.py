"""
A class to handle (i.e. read, write, and parse) .UXD files
from different scans written by a Bruker D8 XRD system.
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = ["UXDparser"]


class UXDparser:
    """
    A class to handle .UXD files from X, Z, theta and
    2theta-omega scans from a Bruker D8 XRD system.

    Access metadata through the ``UXDparser.meta``
    attribute.

    Parameters
    ----------
    base_dir : pathlib.Path or str
        The base data directory.
    """

    def __init__(self, base_dir: Path | str) -> None:
        """
        Initializes the UXDparser with a base data directory.

        Parameters
        ----------
        base_dir : pathlib.Path or str
            The base data directory.
        """
        if isinstance(base_dir, str):
            base_dir = Path(base_dir)
        if not base_dir.is_dir():
            raise IsADirectoryError(
                f"Please make sure '{base_dir}' is an existing directory!"
            )

        self.base_dir = base_dir

    def read_uxd(self, file: Path | str) -> pd.DataFrame:
        """
        Reads data from a .UXD file.

        Parameters
        ----------
        file : pathlib.Path or str
            The input data file.

        Returns
        -------
        data : pd.DataFrame
            Parsed data saved to a Pandas DataFrame.
        """
        if isinstance(file, str):
            file = Path(file)
        if not (self.base_dir / file).exists():
            raise FileNotFoundError(
                f"Please make sure the file '{self.base_dir / file}' exists!"
            )
        if file.suffix not in (".UXD", ".uxd"):
            raise ValueError("Expected a .UXD/.uxd file as input!")

        with open(self.base_dir / file) as f:
            lines = f.read().splitlines()
            self.data, self.meta = self._parse(lines)

        return self.data

    def _parse(self, lines: list or np.ndarray) -> tuple[pd.DataFrame, dict]:
        """
        Parses the contents of a .UXD file. Internal function,
        use ``read_uxd()`` to read .UXD files instead.

        Parameters
        ----------
        lines : list or np.ndarray
            Split lines of the input files.

        Result
        ------
        data: pd.DataFrame
            Parsed data saved to a Pandas DataFrame.
        meta : dict
            Metadata of the input file.
        """
        meta = dict()
        col1 = np.array([])
        col2 = np.array([])

        for line in lines:
            if not line.startswith(("_", ";")):
                line = line.split()

                col1 = np.append(col1, float(line[0]))
                col2 = np.append(col2, int(line[1]))
            else:
                tmp = line.split("=")
                if len(tmp) > 1:
                    meta[tmp[0]] = tmp[1].strip("'")

        col2 = col2.astype(int)

        match meta["_DRIVE"]:
            case "X":
                cols = {"X": col1, "COUNTS": col2}
            case "Z":
                cols = {"Z": col1, "COUNTS": col2}
            case "THETA":
                cols = {"THETA": col1, "COUNTS": col2}
            case "2THETA":
                cols = {"THETA": col1, "COUNTS": col2}
            case _:
                # Fallback, if no match
                warnings.warn(
                    "No match found for _DRIVE type, fallback to default\
                    columns 'A' and 'B'!",
                    stacklevel=2,
                )
                cols = {"A": col1, "B": col2}

        data = pd.DataFrame(data=cols)

        return data, meta

    def to_csv(self, file: Path | str, sep: str = ",", **kwargs) -> None:
        """
        Writes data to a .csv file.

        Parameters
        ----------
        file : Path or str
            Output file to save to.
        sep : str, optional
            String of length 1. Field delimiter for the output file.
            Default: ``','``
        **kwargs :
            Additional kwargs to :meth:`pandas.DataFrame.to_csv`.

        """
        if isinstance(file, str):
            file = Path(file)

        pd.to_csv(file, sep=sep, **kwargs)
