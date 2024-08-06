# 共通利用関数

import os
import pandas as pd
import japanize_matplotlib
import re
from collections import defaultdict
import numpy as np


def assume_year(s: str) -> str:
    founds = set(re.findall(r"(20[012][0-9])", s))
    # 複数マッチする場合は、多数決する
    candids = defaultdict(int)
    for year in founds:
        candids[year] += 1
    return sorted(candids.keys(), key=lambda x: candids[x], reverse=True)[0]


def read_rain_hourly(datapath, column):
    dfs = []
    for root, _, files in os.walk(datapath):
        for file in files:
            if file[-4:] == ".csv":
                filename = root + "/" + file
                # 正時データ以外は読むな
                if not ("seiji" in filename or "正時" in filename):
                    continue
                year = assume_year(filename)
                df = None
                for enc in ("shift-jis", "utf8", "cp932"):
                    try:
                        df = pd.read_csv(filename, encoding=enc, header=0)
                    except:
                        # print(filename)
                        pass
                    if df is not None:
                        break

                if df is not None and column in df.columns:
                    df = df.rename({"Unnamed: 0": "datetime"}, axis="columns")
                    # 日付に変換する。
                    try:
                        df.datetime = pd.to_datetime(df.datetime)
                    except:
                        # 年が欠損している可能性がある
                        print(df.datetime[0])
                        df.datetime = f"{year}/" + df.datetime
                        df.datetime = pd.to_datetime(df.datetime)
                    df.datetime = df.datetime.dt.tz_localize("Asia/Tokyo")
                    dfs.append(df[["datetime", column]])

    if len(dfs) > 0:
        dfs = pd.concat(dfs, axis=0)
        dfs = dfs[dfs[column] != "***"]
        dfs = dfs[dfs[column] != "--"]
        dfs = dfs[dfs[column] != "**"]
        dfs = dfs[dfs[column] != "++"]
        dfs[column] = dfs[column].astype(float)
        dfs = dfs.sort_values(by="datetime")
        # 正時以外の情報を削る。
        dfs = dfs[dfs.datetime.dt.minute == 0]
        # 単純な重複データはここで落とす
        dfs = dfs.drop_duplicates()
        dfs = dfs.set_index("datetime", drop=True)
        return dfs

    return None


def delayed_data(rain_data, lookback=30):
    L = rain_data.shape[0]
    # 時間ずらしデータ。最初が一番古いデータになるはず。
    X_ = np.zeros([L, lookback]) / 0
    for i in range(lookback):
        X_[i:, lookback - i - 1] = rain_data[: L - i]

    return X_
