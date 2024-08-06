import pandas as pd
import numpy as np


# read_csvが読み損じるので、自分で読む。
def read_csv(filename, sep=",", encoding="utf8"):
    rows = []
    with open(filename, encoding=encoding) as f:
        for line in f.readlines():
            cols = line.split(sep)[:143]
            rows.append(cols)
    df = pd.DataFrame(rows[1:])
    df.columns = rows[0][:143]
    print(rows[0][:143])
    return df


def read_NOX_ppb(datapath):

    cols = """月平均値(ppm)_４月
同左_５月.2
同左_６月.2
同左_７月.2
同左_８月.2
同左_９月.2
同左_10月.2
同左_11月.2
同左_12月.2
同左_１月.2
同左_２月.2
同左_３月.2
""".splitlines()

    # 2008年のデータはコラム名をつけまちがっている!!!信じられん。

    stations = ["19202030", "19204010", "19206010"]

    nox = []
    for year in range(2000, 2021):
        if year >= 2003:
            cols = "月平均値(ppm)_４月,月平均値(ppm)_５月,月平均値(ppm)_６月,月平均値(ppm)_７月,月平均値(ppm)_８月,月平均値(ppm)_９月,月平均値(ppm)_10月,月平均値(ppm)_11月,月平均値(ppm)_12月,月平均値(ppm)_１月,月平均値(ppm)_２月,月平均値(ppm)_３月".split(
                ","
            )
        filename = f"{datapath}/TD{year}0419.txt"
        cols_in_file = list(
            pd.read_csv(
                filename,
                sep=",",
                nrows=1,
                encoding="cp932",
            )
        )
        # print(len(cols_in_file))
        df = pd.read_csv(
            filename,
            encoding="cp932",
            sep=",",
            usecols=cols_in_file,
        )
        df = df.loc[:, ~df.columns.duplicated()]
        # print(year, df)
        for i, col in enumerate(cols):
            month = i + 4
            y = year
            if month > 12:
                y += 1
                month -= 12
            row = []
            for station in stations:
                rows = df[df["測定局コード"] == int(station)]
                if len(rows) > 0:
                    row.append(rows.iloc[0][col] * 1000)  # ppm to ppb
                else:
                    row.append(np.nan)
            # print(row)
            nox.append([float(x) for x in row])

    nox = pd.DataFrame(nox, columns=stations)

    # 日本時間を割りふる
    nox["datetime"] = pd.date_range(
        start="2000/04/01", freq="MS", periods=12 * 21
    ).tz_localize("Asia/Tokyo")

    # 1時間ごとの時間目盛りを準備する。
    dates = pd.date_range("2000/4/1", "2021/3/31", freq="H").tz_localize("Asia/Tokyo")
    ts = pd.DataFrame()
    ts["datetime"] = dates

    # 1月ごとのNOX値を、1時間ごとの時刻目盛りに変換し、不足部分をffillする。
    nox = pd.merge(ts, nox, on="datetime", how="outer").ffill()
    nox = nox.set_index("datetime")
    return nox
