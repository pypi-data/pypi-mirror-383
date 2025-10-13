import pandas as pd
from rich.console import Console
from rich.table import Table


def print_df(df: pd.DataFrame, index: bool = True, title: str = "") -> None:
    """
    Converts and prints a pd.DataFrame to a :class:`~rich.table.Table`.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to be converted to a rich table.
    index : bool
        If True, show the DataFrame index as the first column.
    title : str
        Optional title for the rich table.
    """
    console = Console()

    table = Table(title=title, box=None, header_style="bold magenta")

    if index:
        table.add_column("")

    for col in df.columns:
        table.add_column(col)

    for i in df.itertuples(index=index):
        table.add_row(*map(str, i))

    console.print(table)
