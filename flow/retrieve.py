import pandas as pd
import os
import requests


def retrieve(url, filename):
    """
    関数「retrieve」は、指定された URL から PDF ファイルをダウンロードし、指定されたファイル名で保存します。

    Args:
      url: `url` パラメータは、取得するファイルの URL です。 PDF ファイル、画像、その他の種類のファイルが考えられます。
      filename: `filename` パラメータは、ダウンロードした PDF を保存するファイルの名前です。 「.pdf」などのファイル拡張子を含める必要があります。
    """
    response = requests.get(url)
    if response.status_code == 200:
        # File downloaded successfully
        print("PDF downloaded!")
    else:
        print(f"Error downloading PDF: {response.status_code}")
        exit(1)

    with open(filename, "wb") as f:
        f.write(response.content)


def to_seireki(wareki_year):
    """
    関数 `to_seireki` は、日本の元号システム (和暦) の年をグレゴリオ暦の対応する年 (正歴) に変換します。

    Args:
      wareki_year: `wareki_year` パラメータは、「和歴」元号としても知られる和暦体系の年を表します。これは、元号とその元号内の年の 2
    つの部分で構成される文字列です。たとえば、「平成30」は30年目を表します。

    Returns:
      the equivalent Gregorian year (西暦の年) for a given Japanese era year (和暦の年).
    """

    # 元号の開始年を取得する
    start_years = {
        "明治": 1867,
        "大正": 1911,
        "昭和": 1925,
        "平成": 1988,
        "令和": 2018,
    }
    start_year = start_years[wareki_year[:2]]

    num = wareki_year[2:]
    if num == "元":
        num = "1"

    # 西暦の年を計算する
    seireki_year = start_year + int(num)

    return seireki_year


yamanashi1 = pd.read_html(
    "https://www.pref.yamanashi.jp/taiki-sui/sokutei.html", extract_links="body"
)

公共用水域水質測定結果 = yamanashi1[4].values.ravel().tolist()


baseurl = "https://www.pref.yamanashi.jp"


for title, path in 公共用水域水質測定結果:
    seireki = to_seireki(title[:-2])
    if path is not None:
        subtables = pd.read_html(baseurl + path, extract_links="body")
        for subtitle, subpath in subtables[0].values.ravel().tolist():
            if subpath is not None:
                if "相模川" in subtitle:
                    print(title, subtitle, subpath)
                    retrieve(baseurl + subpath, f"{seireki}.pdf")
