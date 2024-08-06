import pandas as pd


def read(datapath):
    dfs = []
    for year in range(2000, 2024):
        df = pd.read_csv(
            f"{datapath}/{year}.csv", skiprows=4, header=0, encoding="ShiftJIS"
        )
        dfs.append(df)

    dfs = pd.concat(dfs, axis=0)
    dfs.columns = ["datetime", "value", "QTY", "HOMO"]
    dfs["datetime"] = pd.to_datetime(dfs.datetime).dt.tz_localize("Asia/Tokyo")
    # dfs["unixtime"] = dfs["datetime"].astype(int) // 10**9
    dfs = dfs.set_index("datetime")
    return dfs
