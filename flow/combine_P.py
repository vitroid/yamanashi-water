import textract
import tabula
import sys
import pandas as pd
import pickle

# もとはpdfから一気にpickleを生成していたのだが、酷くデータが壊れている部分があるので、
# csvを一旦生成し、手で修正した上でpickleにする。

# csv2pickleはstack.pyと統合すべき。
# このコードでは、全部まとめて大きな表にするのではなく、川ごとの表に分解する。

bridges = [
    "昭和橋",
    "大月橋",
    "桂川橋",
    "富士見橋",
    "鶴川橋",
    "西方寺橋",
    "落合橋",
    "流川",
    "道志川",
    "秋山川",
]

bridges = {bridge: dict() for bridge in bridges}

for bridge in bridges:
    phosphos = pd.DataFrame()
    for fiscal_year in range(2000, 2022):
        table = pd.read_csv(f"{fiscal_year}_P.csv")
        table = table[table["bridge"] == bridge]
        # 日付を月だけにしたカラムを追加する。
        table["month"] = table["採取月日"].str.replace("[月/].*", "", regex=True)
        table["day"] = (
            table["採取月日"]
            .str.replace(".*[月/]", "", regex=True)
            .replace("日", "", regex=True)
        )
        table["hour"] = table["採取時刻"].str.replace("[時:].*", "", regex=True)
        table["minute"] = (
            table["採取時刻"]
            .str.replace(".*[時:]", "", regex=True)
            .replace("分", "", regex=True)
        )
        # 年の列を追加する。
        table.loc[:, "fiscal_year"] = int(fiscal_year)
        # 1〜3月は年に1を足す
        table.loc[table["month"].astype(int) < 4, "year"] = f"{fiscal_year+1}"
        table.loc[table["month"].astype(int) >= 4, "year"] = f"{fiscal_year}"

        table["datetime"] = (
            table["year"]
            + "-"
            + table["month"].astype(int).map("{:02d}".format)
            + "-"
            + table["day"].astype(int).map("{:02d}".format)
            + " "
            + table["hour"].astype(int).map("{:02d}".format)
            + ":"
            + table["minute"].astype(int).map("{:02d}".format)
        )
        print(table.datetime)
        table["datetime"] = pd.to_datetime(table["datetime"]).dt.tz_localize(
            "Asia/Tokyo"
        )
        table["unixtime"] = table["datetime"].astype(int) // 10**9
        table = table.set_index("unixtime")
        # print(table)
        # sys.exit(0)
        phosphos = pd.concat(
            [
                phosphos,
                pd.DataFrame(
                    table[table["item"] == "全燐"], columns=["datetime", "value"]
                ),
            ]
        )
    phosphos.to_csv(f"{bridge}.P.csv")
