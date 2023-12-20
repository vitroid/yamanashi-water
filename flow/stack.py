import pandas as pd
import pickle

table = pd.DataFrame()
for year in range(2000, 2022):
    with open(f"{year}.pickle", "rb") as f:
        subtable = pickle.load(f)
    table = pd.concat([table, subtable], axis=0)

table.to_csv("stack.csv", encoding="UTF-8")
