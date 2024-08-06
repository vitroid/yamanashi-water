import pandas as pd


def read_NOX_ppb(datapath, station):
    dfs = []
    for year in range(2009, 2021):
        with open(f"{datapath}/19/{year}/j19{year}_{station}.csv") as f:
            df = pd.read_csv(f, parse_dates=[1])  # parse date time in column 1
            dfs.append(df)

    dfs = pd.concat(dfs)

    dfs["datetime"] = pd.to_datetime(dfs["date"]).dt.tz_localize("Asia/Tokyo")
    # dfs["unixtime"] = dfs["datetime"].astype(int) // 10**9
    dfs.index = dfs.datetime
    return dfs[["NOX"]].rename(columns={"NOX": station})
