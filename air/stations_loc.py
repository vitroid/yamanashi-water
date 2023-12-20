# stations_loc.pickleとブロック図を読みこみ、各ブロック内にある局を抽出する。

import pickle
import numpy as np
import pandas as pd
from shapely import Point
import geopandas as gpd
import shapely

with open("stations_loc.pickle", "rb") as f:
    stations_loc = pickle.load(f)

blocks = ["red", "lime", "yellow", "orange"]

stations = {}
for block in blocks:
    print(block)
    stations[block] = []
    gdf = gpd.read_file(f"../branches/{block}.geojson")
    # gdf = gpd.make_valid(pdf)
    # shape = shapely.ops.unary_union(gdf["geometry"])
    # shape = gpd.GeoSeries([shape]).make_valid()

    # マーカープロット
    for id, station in stations_loc.items():
        lon = station["longitude"]
        lat = station["latitude"]
        name = station["name"]
        # markerに情報をのせる
        p = Point(lon, lat)
        for i, row in gdf.iterrows():
            # print(i)
            if p.within(row["geometry"]):
                # if p.within(shape[0]):
                print(block, id, name)
                stations[block].append(id)
                break
