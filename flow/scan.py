import textract
import tabula
import sys
import pandas as pd
import pickle

year = sys.argv[1]

pdf_path = f"{year}.pdf"
text = textract.process(pdf_path).decode("utf-8")
pages = text.split("\f")

tabletitles = []
for page in pages:
    lines = page.splitlines()
    # skip empty strings
    words = [word for word in lines if "橋" in word or "川" in word]
    if len(words) >= 1:
        title = ".".join(words)
        tabletitles.append(title)
    # print(words[:10])
print(tabletitles)


tables = tabula.read_pdf(pdf_path, pages="all")

assert len(tables) == len(tabletitles)

bridges = ["昭和橋", "大月橋", "桂川橋", "富士見橋", "鶴川橋", "西方寺橋", "落合橋", "流川", "道志川", "秋山川"]

newtables = {}
for table, title in zip(tables, tabletitles):
    for bridge in bridges:
        if bridge in title:
            break
    else:
        continue
        # assert False, "No bridge."

    # カラム名の妙な空白を除去
    table.columns = table.columns.str.replace(" ", "")
    # 最初の列をインデックスとする
    table.set_index(table.columns[0], inplace=True)
    # インデックスの妙な空白を除去
    table.index = table.index.str.replace(" ", "")

    if int(year) in (2000, 2001):
        subtable = table.loc[["採取月日", "流量\r(年平均)", "全窒素"]]
    else:
        try:
            subtable = table.loc[["採取月日", "流量", "全窒素"]]
        except:
            subtable = table.loc[["採取月日", "3流量m/s", "全窒素mg/l"]]
            subtable.index = ["採取月日", "流量", "全窒素"]
    # print(table.index)

    if bridge in newtables:
        newtables[bridge] = pd.concat([newtables[bridge], subtable], axis=1)
    else:
        newtables[bridge] = subtable

fulltable = pd.DataFrame()
count = 13
for bridge, table in newtables.items():
    # 横長の表を縦長にする。
    table = table.T
    # 単位の行を落とす
    table = table.dropna(subset=["採取月日"])
    # 日付を月だけにしたカラムを追加する。
    table["month"] = table["採取月日"].str.replace("[月/].*", "", regex=True)
    ivals = []
    for val in table.loc[:, "month"]:
        try:
            ival = int(val)
        except:
            ival = count
            count += 1
        ivals.append(ival)
    table["month"] = ivals
    # 月番号を行見出しにする
    table = table.set_index("month")

    print(table)
    # 冗長なデータを削った表を新たに準備する。
    newtable = pd.DataFrame(columns=table.columns)
    # インデックス(月番号)ごとに
    for month in set(table.index):
        # もし複数行がマッチする場合は
        if len(table.loc[[month]]) > 1:
            # 行を融合してNaNを排除する
            subtable = table.loc[month].fillna(method="bfill").iloc[0]
        else:
            # その行を
            subtable = table.loc[month]
        # 新しい表に追加する。
        newtable.loc[month] = subtable
        print(subtable)
    # 年の列を追加する。
    newtable.loc[:, "year"] = int(year)
    # 1〜3月は年に1を足す
    newtable.loc[newtable.index < 4, "year"] = int(year) + 1
    # 年も行見出しにする
    newtable = newtable.set_index("year", append=True)
    # 列見出しを、二重にする。(あとで表を結合する時のために)
    newtable = newtable.set_axis(
        [(bridge, "採取月日"), (bridge, "流量"), (bridge, "全窒素")], axis=1
    )
    print(bridge, newtable)
    # 大表に追加する。
    fulltable = pd.concat([fulltable, newtable], axis=1)

print(fulltable)

with open(f"{year}.pickle", "wb") as f:
    pickle.dump(fulltable, f)
fulltable.to_csv(f"{year}.csv")
