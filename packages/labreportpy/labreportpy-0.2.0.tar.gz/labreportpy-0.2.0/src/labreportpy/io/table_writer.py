from pathlib import Path

import pandas as pd

__all__ = ["TableWriter"]


class TableWriter:
    r"""Simple class to convert data from a DataFrame to
    a LaTeX tabularx/tabularray readable format. Either
    print out and copy the output of 'table_writer' or
    (better) save it to a .tex file and use
    begin{tflr}[evaluate=\filwith  thethe optiion
    ``\begin{tblr}[evaluate=\fileInput]``
    inside your tabularx
    ``\FileInput{your_table_file.tex}`` inside your tabularx
    or tabularray environment.


    Parameters
    ----------
    base_dir : str or Path
        Base directory to write to.
    """

    def __init__(self, base_dir: str or Path = "") -> None:
        """Initializes the table writer with a  base directory.

        Parameters
        ----------
        base_dir : str or Path
            Base directory to write to.
        """
        if not isinstance(base_dir, Path):
            base_dir = Path(base_dir)

        self.base_dir = base_dir

    def __call__(
        self,
        df: pd.DataFrame,
        output_file: str | Path,
        quantities: list = None,
        units: list = None,
        colspec: list = None,
        table_options: list = None,
        caption: str = "",
        label: str = "",
        header_math_mode: bool = True,
        booktabs: bool = True,
    ):
        """
        Writes data from a pandas.DataFrame to a full
        table environment compatible with tabularray.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame that will be converted to a LaTeX
            table.
        output_file : str or pathlib.Path
            Output file path. If `base_dir` is set when
            initializing the class, the path will be
            `<base_dir>/<output_file>`.
        quantities : list, optional
            Quantities set as the column names. If left
            empty, the column names of the DataFrame are
            used instead.
        units : list, optional
            Units for the quantities. If a quantity has
            no unit, make sure to parse an empty string
            at the respective list index. If left empty
            entirely, a list of the same length as
            `quantities` containing empty strings is used.
        colspec : list or str, optional
            The column specifiers. If empty, all columns
            are assumed to be of the `siunitx` `S` type.
        table_options : list, optional
            Additional table options. See the tabularray docs
            http://mirrors.ctan.org/macros/latex/contrib/tabularray/tabularray.pdf
            for more information.
        caption : str, optional
            Caption of the table.
        label : str
            Label of the table.
        header_math_mode : bool, optional, default=`True`
            If `True`, this sets the first row to math mode and
            also add the guard keyword to protect the column names.
        booktabs : bool, optional, default=`True`
            If `True`, use the `toprule`, `midrule`, and `bottomrule`
            macros, that are defined by the `booktabs` package. If
            `False`, the `hline` macro is used instead.
        """
        if quantities is None:
            quantities = []
        if units is None:
            units = []
        if colspec is None:
            colspec = []
        if table_options is None:
            table_options = []

        self.df = df

        return self._write_table(
            df,
            output_file,
            quantities,
            units,
            colspec,
            table_options,
            caption,
            label,
            header_math_mode,
            booktabs,
        )

    def write_inner(self, write_to_file: bool = True) -> str:
        """
        Writes a inner table to a .tex file.

        Parameters
        ----------
        write_to_file : bool, optional, default=`True`
            If `True`, writes inner table to `.tex` file.

        Returns
        -------
        table : str
            String representation of the table.
        """
        table = ""
        for _, series in self.df.iterrows():
            v = [str(s) for s in series.values]
            s = " & ".join(v) + r" \\" + "\n"
            table += s

        if write_to_file and self.output_file:
            with open(self.base_dir / self.output_file, "w") as f:
                f.write(table)

        return table

    def _write_table(
        self,
        df: pd.DataFrame,
        output_file: str or Path,
        quantities: list = None,
        units: list = None,
        colspec: list or str = None,
        table_options: list = None,
        caption: str = "",
        label: str = "",
        header_math_mode: bool = True,
        booktabs: bool = True,
    ) -> None:
        """
        Writes data from a pandas.DataFrame to a full
        table environment compatible with tabularray.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame that will be converted to a LaTeX
            table.
        output_file : str or pathlib.Path
            Output file path. If `base_dir` is set when
            initializing the class, the path will be
            `<base_dir>/<output_file>`.
        quantities : list, optional
            Quantities set as the column names. If left
            empty, the column names of the DataFrame are
            used instead.
        units : list, optional
            Units for the quantities. If a quantity has
            no unit, make sure to parse an empty string
            at the respective list index. If left empty
            entirely, a list of the same length as
            `quantities` containing empty strings is used.
        colspec : list or str, optional
            The column specifiers. If empty, all columns
            are assumed to be of the `siunitx` `S` type.
        table_options : list, optional
            Additional table options. See the tabularray docs
            http://mirrors.ctan.org/macros/latex/contrib/tabularray/tabularray.pdf
            for more information.
        caption : str, optional
            Caption of the table.
        label : str
            Label of the table.
        header_math_mode : bool, optional, default=`True`
            If `True`, this sets the first row to math mode and
            also add the guard keyword to protect the column names.
        booktabs : bool, optional, default=`True`
            If `True`, use the `toprule`, `midrule`, and `bottomrule`
            macros, that are defined by the `booktabs` package. If
            `False`, the `hline` macro is used instead.
        """
        if quantities is None:
            quantities = []
        if units is None:
            units = []
        if colspec is None:
            colspec = []
        if table_options is None:
            table_options = []

        if not output_file:
            raise ValueError("No output file specified.")

        output_file = Path(output_file)

        hrules = dict(
            {
                True: {
                    "header": "\n" + r"\toprule" + "\n",
                    "midrule": r"\midrule" + "\n",
                    "footer": r"\bottomrule" + "\n",
                },
                False: {
                    "header": r"\hline" + "\n",
                    "midrule": r"\hline" + "\n",
                    "footer": r"\hline" + "\n",
                },
            }
        )

        if quantities == []:
            quantities = self.df.columns.values.tolist()
        if units == []:
            units = [""] * len(quantities)
        if colspec == []:
            colspec = ["S"] * len(quantities)
        colspec = "".join(colspec)
        if header_math_mode:
            hmm = "row{1} = {guard, mode=math},"

        opts = table_options

        table = r"\begin{table}" + "\n" + r"\centering" + "\n"
        table += rf"\caption{{{caption}}}"
        table += "\n" + rf"\label{{{label}}}" + "\n"
        tblr = rf"\begin{{tblr}}{{colspec={{{colspec}}},{hmm}{','.join(opts)}}}"

        head_list = []
        for qty, unit in zip(quantities, units):
            s = str(qty) + r" \mathbin{/} " + r"\unit{unit}" if unit != "" else str(qty)

            head_list.append(s)

        header = hrules[booktabs]["header"]
        header += " & ".join(head_list) + r" \\" + "\n"

        header += hrules[booktabs]["midrule"]

        body = self.write_inner(write_to_file=False)

        footer = hrules[booktabs]["footer"]

        tblr += header + body + footer
        tblr += r"\end{tblr}" + "\n"

        table += tblr + r"\end{table}"

        with open(self.base_dir / output_file, "w") as f:
            f.write(table)

    def from_df(self, df: pd.DataFrame, output_file: str or Path) -> None:
        """
        Initializes the class with data from a DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to be converted to table format.
        output_file : str or Path
            Output file path for saving.
        """
        self.df = df
        self.output_file = output_file

    def from_file(
        self, input_file: str or Path, output_file: str or Path = None
    ) -> str:
        """
        Initializes the class with data from a file.

        Parameters
        ----------
        input_file : str or Path
            Input file containing the data.
        output_file : str or Path
            Output file to write to.

        Returns
        -------
        table: str
            A LaTeX (tabularx/tabularray) compatible string.
        """
        # check if input file is a .txt
        if input_file.split(".")[-1] != "txt":
            self.df = pd.read_csv(input_file)
        else:
            # read data from .txt, header is first row, use
            # whitespace as delimiter
            self.df = pd.read_csv(
                input_file, header=None, delim_whitespace=True, comment="#"
            )

        self.output_file = output_file
