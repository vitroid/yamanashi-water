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
    flows = pd.DataFrame()
    nitros = pd.DataFrame()
    for fiscal_year in range(2000, 2022):
        table = pd.read_csv(f"{fiscal_year}.csv")
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
        table["datetime"] = pd.to_datetime(table["datetime"]).dt.tz_localize(
            "Asia/Tokyo"
        )
        table["unixtime"] = table["datetime"].astype(int) // 10**9
        table = table.set_index("unixtime")
        # print(table)
        # sys.exit(0)
        flows = pd.concat(
            [
                flows,
                pd.DataFrame(
                    table[table["item"] == "流量"], columns=["datetime", "value"]
                ),
            ]
        )
        nitros = pd.concat(
            [
                nitros,
                pd.DataFrame(
                    table[table["item"] == "全窒素"], columns=["datetime", "value"]
                ),
            ]
        )
    flows.to_csv(f"{bridge}.flow.csv")
    nitros.to_csv(f"{bridge}.N.csv")
#     ivals = []
#     for val in table.loc[:, "month"]:
#         try:
#             ival = int(val)
#         except:
#             ival = count
#             count += 1
#         ivals.append(ival)
#     table["month"] = ivals
#     # 月番号を行見出しにする
#     table = table.set_index("month")

#     print(table)
#     # 冗長なデータを削った表を新たに準備する。
#     newtable = pd.DataFrame(
#         columns=["year", "datetime", "流量", "全窒素"]
#     )  # "table.columns)
#     # インデックス(月番号)ごとに
#     for month in set(table.index):
#         # もし複数行がマッチする場合は
#         if len(table.loc[[month]]) > 1:
#             # 行を融合してNaNを排除する
#             subtable = table.loc[month].fillna(method="bfill").iloc[0]
#         else:
#             # その行を
#             subtable = table.loc[month]
#         # 新しい表に追加する。
#         newtable.loc[month] = subtable
#         print(subtable)
#     # 年も行見出しにする
#     newtable = newtable.set_index("year", append=True)
#     # 列見出しを、二重にする。(あとで表を結合する時のために)
#     newtable = newtable.set_axis(
#         [(bridge, "datetime"), (bridge, "流量"), (bridge, "全窒素")], axis=1
#     )
#     print(bridge, newtable)
#     # 大表に追加する。
#     fulltable = pd.concat([fulltable, newtable], axis=1)

# print(fulltable)

# with open(f"{fiscal_year}.pickle", "wb") as f:
#     pickle.dump(fulltable, f)
# fulltable.to_csv(f"{fiscal_year}.csv")
