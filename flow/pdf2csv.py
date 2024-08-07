import textract
import tabula
import sys
import pandas as pd
import pickle

fiscal_year = int(sys.argv[1])

pdf_path = f"{fiscal_year}.pdf"
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

    if int(fiscal_year) in (2000, 2001):
        subtable = table.loc[["採取月日", "採取時刻", "流量\r(年平均)", "全窒素"]]
        subtable.index = ["採取月日", "採取時刻", "流量", "全窒素"]
    else:
        try:
            subtable = table.loc[["採取月日", "採取時刻", "流量", "全窒素"]]
        except:
            subtable = table.loc[["採取月日", "採取時刻", "3流量m/s", "全窒素mg/l"]]
            subtable.index = ["採取月日", "採取時刻", "流量", "全窒素"]
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
    table["bridge"] = bridge
    print(bridge)
    print(table)

    nitro = (
        pd.DataFrame(table, columns=["採取月日", "採取時刻", "bridge", "全窒素"])
        .dropna(subset=["全窒素"])
        .rename(columns={"全窒素": "value"})
    )
    nitro["item"] = "全窒素"
    flow = (
        pd.DataFrame(table, columns=["採取月日", "採取時刻", "bridge", "流量"])
        .dropna(subset=["流量"])
        .rename(columns={"流量": "value"})
    )
    flow["item"] = "流量"

    # 大表に追加する。
    fulltable = pd.concat([fulltable, nitro], axis=0)
    fulltable = pd.concat([fulltable, flow], axis=0)

print(fulltable)

fulltable.to_csv(f"{fiscal_year}.csv")
