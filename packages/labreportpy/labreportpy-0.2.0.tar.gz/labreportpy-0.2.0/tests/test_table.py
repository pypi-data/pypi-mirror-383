import pandas as pd
from labreportpy.io import TableWriter

df = pd.read_csv("tests/test_data.csv", skiprows=1)

writer = TableWriter()

writer(df, output_file="tests/table.tex")
