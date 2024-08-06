import pandas as pd


def read_river_N(datapath, bridge):
    df = pd.read_csv(f"{datapath}/{bridge}.N.csv")
    # datetimeに変換し、分を省く
    df.datetime = pd.to_datetime(df.datetime).dt.floor("h")
    df = df.set_index("datetime")
    return df[["value"]]


def read_river_P(datapath, bridge):
    df = pd.read_csv(f"{datapath}/{bridge}.P.csv")
    # datetimeに変換し、分を省く
    df.datetime = pd.to_datetime(df.datetime).dt.floor("h")
    df = df.set_index("datetime")
    return df[["value"]]


def read_river_flow(datapath, bridge):
    df = pd.read_csv(f"{datapath}/{bridge}.flow.csv")
    # datetimeに変換し、分を省く
    df.datetime = pd.to_datetime(df.datetime).dt.floor("h")
    df = df.set_index("datetime")
    return df[["value"]]
