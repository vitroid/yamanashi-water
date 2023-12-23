import pickle
import pandas as pd

BASEDIR = "./"
flows = pd.read_csv(f"{BASEDIR}山梨9地点流量と全窒素.tsv", sep="\t")
cols = list(flows.columns)
cols = {col: eval(col) for col in cols[2:]}
cols["Unnamed: 0"] = "month"
flows = flows.rename(columns=cols)

bridges = ["昭和橋", "大月橋", "桂川橋", "富士見橋", "鶴川橋", "西方寺橋", "落合橋", "流川", "道志川", "秋山川"]
columns = [(bridge, elem) for bridge in bridges for elem in ("流量", "全窒素")]
subdf = flows.iloc[0 * 12 : 21 * 12][columns]
subdf.to_csv("9bridges2000.csv")
